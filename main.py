import json
import os
import sys
import threading
import time

from lib.game_control import GameControl
from lib.updater import migrate_update_exe_name, start_update_check
from lib.version import APP_VERSION


def ensure_tk_environment():
    """
    Ensure Tk can find Tcl/Tk runtime files when running from virtual environments.
    """
    base_dirs = []
    for candidate in (sys.base_prefix, sys.base_exec_prefix, sys.prefix):
        if candidate and candidate not in base_dirs:
            base_dirs.append(candidate)

    if not os.environ.get("TCL_LIBRARY"):
        for base in base_dirs:
            tcl_path = os.path.join(base, "tcl", "tcl8.6")
            if os.path.isfile(os.path.join(tcl_path, "init.tcl")):
                os.environ["TCL_LIBRARY"] = tcl_path
                break

    if not os.environ.get("TK_LIBRARY"):
        for base in base_dirs:
            tk_path = os.path.join(base, "tcl", "tk8.6")
            if os.path.isfile(os.path.join(tk_path, "tk.tcl")):
                os.environ["TK_LIBRARY"] = tk_path
                break


ensure_tk_environment()
import customtkinter as ctk  # noqa: E402

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Mode names in display order
MODE_NAMES = ("soul", "sougenbi", "realm", "yonder", "even", "draft", "bondling")

# Bondling sub-modes (key -> button label); UI only for now, no scan loop yet
BONDLING_SUB_MODES = {"farm": "ฟาม", "catch": "จับ"}

# Even sub-modes (key -> button label) and the templates each one clicks
EVEN_SUB_MODES = {"farm": "Farm", "activity": "Activity"}
EVEN_SUB_TEMPLATES = {
    "farm": ("farm-1",),
    "activity": ("activity-1", "activity-2", "activity-3"),
}
EVEN_CONTINUE_KEYS = ("continue-1", "continue-2")

# Tabs that pick a sub-mode with a segmented button above the status line
MODE_SUB_MODES = {"even": EVEN_SUB_MODES, "bondling": BONDLING_SUB_MODES}

# Config key for each mode's templates section
MODE_TEMPLATE_KEYS = {
    "soul": "templates",
    "sougenbi": "sougenbi_templates",
    "realm": "realm_templates",
    "yonder": "yonder_templates",
    "even": "even_templates",
    "draft": "draft_templates",
}

# Draft mode: templates the loop needs
DRAFT_REQUIRED_KEYS = ("accept", "draft-fight", "draft-best", "draft-victory", "continue")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Rubitdd-Bot-v{APP_VERSION}")
        self.root.geometry("720x350")
        self.root.resizable(False, False)

        self.bot = None
        self.config = None

        # Per-mode state: running flag, thread, and UI widgets
        self.modes = {}
        for name in MODE_NAMES:
            self.modes[name] = {
                "running": False,
                "thread": None,
                "status": None,
                "start_btn": None,
                "stop_btn": None,
                "templates": {},
            }

        self.setup_ui()
        self.load_configuration()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _create_mode_tab(self, mode_name):
        """Create the standard status + start/stop buttons inside a tab."""
        tab = self.tab_control.tab(mode_name)

        # even and bondling pick a sub-mode above the status line
        sub_mode = None
        sub_modes = MODE_SUB_MODES.get(mode_name)
        if sub_modes:
            sub_mode = ctk.CTkSegmentedButton(
                tab,
                values=list(sub_modes.values()),
                font=("Arial", 13, "bold"),
                width=240,
                height=30,
                dynamic_resizing=False,
            )
            sub_mode.set(next(iter(sub_modes.values())))
            sub_mode.pack(pady=(8, 0))

        status = ctk.CTkLabel(
            tab,
            text="● สถานะ: ปิด",
            font=("Arial", 14, "bold"),
            text_color="#ff6b6b",
        )
        status.pack(pady=10 if sub_mode else 20)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(pady=10)

        start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ เริ่มทำงาน",
            font=("Arial", 13, "bold"),
            fg_color="#51cf66",
            hover_color="#40c057",
            width=160,
            height=40,
            corner_radius=8,
            command=lambda m=mode_name: self.start_mode(m),
        )
        start_btn.pack(side="left", padx=10)

        stop_btn = ctk.CTkButton(
            btn_frame,
            text="■ หยุดทำงาน",
            font=("Arial", 13, "bold"),
            text_color="white",
            fg_color="#000000",
            hover_color="#131313",
            width=160,
            height=40,
            corner_radius=8,
            state="disabled",
            command=lambda m=mode_name: self.stop_mode(m),
        )
        stop_btn.pack(side="left", padx=10)

        mode = self.modes[mode_name]
        mode["status"] = status
        mode["start_btn"] = start_btn
        mode["stop_btn"] = stop_btn
        mode["sub_mode"] = sub_mode

    def setup_ui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self.root, height=70, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text=f"🐇 Rubitdd-Bot-v{APP_VERSION} 🐇",
            font=("Arial", 24, "bold"),
        )
        title_label.pack(pady=20)

        # Tab Control
        self.tab_control = ctk.CTkTabview(self.root, height=200)
        self.tab_control.pack(fill="x", padx=20, pady=10)
        for name in MODE_NAMES:
            self.tab_control.add(name)

        # Create identical UI for each tab
        for name in MODE_NAMES:
            self._create_mode_tab(name)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _resolve_mode_templates(self, mode_key):
        """Merge shared_templates with mode-specific templates, resolve paths.

        Mode-specific entries override shared entries with the same key.
        """
        shared = dict(self.config.get("shared_templates", {}))
        mode_specific = dict(self.config.get(mode_key, {}))
        merged = {**shared, **mode_specific}
        return {k: resource_path(v) for k, v in merged.items()}

    def log_message(self, message):
        print(f"{time.strftime('%H:%M:%S')} - {message}")

    def load_configuration(self):
        try:
            config_path = resource_path("config.json")
            with open(config_path, encoding="utf-8") as f:
                self.config = json.load(f)

            # Resolve templates for every mode
            for mode_name, tpl_key in MODE_TEMPLATE_KEYS.items():
                self.modes[mode_name]["templates"] = self._resolve_mode_templates(tpl_key)

            self.log_message("✓ โหลด config.json สำเร็จ")
            self.log_message(f"  หน้าต่างเป้าหมาย: {self.config['window_title']}")
        except FileNotFoundError:
            self.log_message("✗ ไม่พบไฟล์ config.json")
        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {e!s}")

    # ------------------------------------------------------------------
    # Start / Stop (generic)
    # ------------------------------------------------------------------

    def start_mode(self, mode_name):
        mode = self.modes[mode_name]
        if mode["running"]:
            return
        if not self.config:
            self.log_message("✗ กรุณาตรวจสอบไฟล์ config.json")
            return

        mode["running"] = True
        mode["start_btn"].configure(state="disabled")
        mode["stop_btn"].configure(state="normal")
        mode["status"].configure(text="● สถานะ: กำลังทำงาน", text_color="#51cf66")

        self.log_message(f"=== เริ่มทำงานบอท {mode_name.capitalize()} ===")

        target = self._get_run_target(mode_name)
        mode["thread"] = threading.Thread(target=target, daemon=True)
        mode["thread"].start()

    def stop_mode(self, mode_name):
        mode = self.modes[mode_name]
        if not mode["running"]:
            return

        mode["running"] = False
        mode["start_btn"].configure(state="normal")
        mode["stop_btn"].configure(state="disabled")
        mode["status"].configure(text="● สถานะ: ปิด", text_color="#ff6b6b")

        self.log_message(f"=== หยุดทำงานบอท {mode_name.capitalize()} ===")

    def _selected_sub_mode(self, mode_name):
        """Key of the sub-mode picked in the tab's segmented button (read on the Tk thread)."""
        label = self.modes[mode_name]["sub_mode"].get()
        for key, text in MODE_SUB_MODES[mode_name].items():
            if text == label:
                return key
        return next(iter(MODE_SUB_MODES[mode_name]))

    def _get_run_target(self, mode_name):
        """Return the callable for the mode's worker thread."""
        if mode_name == "realm":
            return self._run_realm
        if mode_name == "yonder":
            return self._run_yonder
        if mode_name == "even":
            # read the sub-mode widget here on the Tk thread, not inside the worker
            sub_key = self._selected_sub_mode(mode_name)
            return lambda: self._run_even(sub_key)
        if mode_name == "draft":
            return self._run_draft
        if mode_name == "bondling":
            sub_label = self.modes[mode_name]["sub_mode"].get()
            return lambda: self._run_bondling(sub_label)
        # soul and sougenbi use the generic scan loop
        return lambda: self._run_generic(mode_name)

    # ------------------------------------------------------------------
    # Scan loops
    # ------------------------------------------------------------------

    def _ensure_bot(self):
        """Initialise the GameControl singleton on first use."""
        if not self.bot:
            self.bot = GameControl(self.config["window_title"])
            self.log_message("✓ เชื่อมต่อหน้าต่างเกมสำเร็จ")

    def _run_generic(self, mode_name):
        """Generic scan-and-click loop used by soul and sougenbi."""
        try:
            self._ensure_bot()
            mode = self.modes[mode_name]
            templates = mode["templates"]
            threshold = self.config["confidence_threshold"]

            while mode["running"]:
                self.log_message(f"กำลังสแกน {mode_name.capitalize()}...")
                for key, path in templates.items():
                    pos = self.bot.find_image(path, threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม {key.capitalize()} ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)
                time.sleep(self.config["loop_delay"])

        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {e!s}")
            self.root.after(0, lambda: self.stop_mode(mode_name))

    def _run_realm(self):
        """Realm mode — special hogan-blocking logic."""
        mode_name = "realm"
        try:
            self._ensure_bot()
            mode = self.modes[mode_name]
            templates = mode["templates"]
            threshold = self.config.get("realm_confidence", self.config["confidence_threshold"])
            hogan_blocked = False

            while mode["running"]:
                self.log_message("กำลังสแกน Realm...")

                # done1
                if "done1" in templates:
                    pos = self.bot.find_image(templates["done1"], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม Done1 ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)

                # mark — blocks hogan when visible
                if "mark" in templates:
                    mark_pos = self.bot.find_image(templates["mark"], threshold)
                    if mark_pos:
                        if not hogan_blocked:
                            self.log_message(f"✓ พบ Mark ที่ตำแหน่ง {mark_pos} - หยุดกด Hogan ชั่วคราว")
                        hogan_blocked = True

                # hogan — only click if not blocked, click 40px below
                if "hogan" in templates and not hogan_blocked:
                    pos = self.bot.find_image(templates["hogan"], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม Hogan ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1] + 40)
                        time.sleep(0.5)

                # next
                if "next" in templates:
                    pos = self.bot.find_image(templates["next"], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม Next ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)

                # attack — also unblocks hogan
                if "attack" in templates:
                    pos = self.bot.find_image(templates["attack"], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม Attack ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        if hogan_blocked:
                            self.log_message("✓ เริ่มทำงาน Hogan อีกครั้ง")
                            hogan_blocked = False
                        time.sleep(0.5)

                # lose
                if "lose" in templates:
                    pos = self.bot.find_image(templates["lose"], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม Lose ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(1.5)

                # lose1
                if "lose1" in templates:
                    pos = self.bot.find_image(templates["lose1"], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม Lose1 ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)

                time.sleep(self.config["loop_delay"])

        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {e!s}")
            self.root.after(0, lambda: self.stop_mode(mode_name))

    def _run_yonder(self):
        """Yonder mode — requires challenge template to exist."""
        mode_name = "yonder"
        try:
            self._ensure_bot()
            mode = self.modes[mode_name]
            templates = mode["templates"]
            threshold = self.config["confidence_threshold"]

            if "challenge" not in templates:
                self.log_message("✗ ไม่พบ yonder_templates.challenge ใน config.json")
                self.root.after(0, lambda: self.stop_mode(mode_name))
                return

            while mode["running"]:
                self.log_message("กำลังสแกน Yonder...")
                for key, path in templates.items():
                    pos = self.bot.find_image(path, threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม {key.capitalize()} ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)
                time.sleep(self.config["loop_delay"])

        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {e!s}")
            self.root.after(0, lambda: self.stop_mode(mode_name))

    def _click_shared(self, templates, threshold):
        """Click every visible shared template (accept, dismiss, done1, donee)."""
        for key in self.config.get("shared_templates", {}):
            path = templates.get(key)
            if not path:
                continue
            pos = self.bot.find_image(path, threshold)
            if pos:
                self.log_message(f"✓ พบปุ่ม {key.capitalize()} ที่ตำแหน่ง {pos}")
                self.bot.background_click(pos[0], pos[1])
                time.sleep(0.5)

    def _run_even(self, sub_key):
        """Even mode — stateless: every tick click the shared popups, then the templates of the
        selected sub-mode (Farm: farm-1; Activity: activity-1/2/3), then continue.

        Stateless on purpose: nothing is remembered between ticks, so a click the game missed
        is found again and retried on the next tick instead of leaving the bot stuck.
        """
        mode_name = "even"
        try:
            self._ensure_bot()
            mode = self.modes[mode_name]
            templates = mode["templates"]
            threshold = self.config["confidence_threshold"]
            sub_keys = EVEN_SUB_TEMPLATES[sub_key]
            sub_label = EVEN_SUB_MODES[sub_key]

            missing = [key for key in sub_keys + EVEN_CONTINUE_KEYS if key not in templates]
            if missing:
                self.log_message(f"✗ ไม่พบ even_templates: {', '.join(missing)} ใน config.json")
                self.root.after(0, lambda: self.stop_mode(mode_name))
                return

            while mode["running"]:
                self.log_message(f"กำลังสแกน Even ({sub_label})...")

                # shared popups can show up at any point
                self._click_shared(templates, threshold)

                for key in sub_keys:
                    pos = self.bot.find_image(templates[key], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม {key.capitalize()} ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)

                for key in EVEN_CONTINUE_KEYS:
                    pos = self.bot.find_image(templates[key], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม {key.capitalize()} ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)
                        break

                time.sleep(self.config["loop_delay"])

        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {e!s}")
            self.root.after(0, lambda: self.stop_mode(mode_name))

    def _run_draft(self):
        """Draft mode — stateless: every tick, click whatever is on screen.

        accept, draft-fight and draft-best are clicked on their center; draft-victory is only
        logged, because continue is checked right after it.
        """
        mode_name = "draft"
        try:
            self._ensure_bot()
            mode = self.modes[mode_name]
            templates = mode["templates"]
            threshold = self.config["confidence_threshold"]

            missing = [key for key in DRAFT_REQUIRED_KEYS if key not in templates]
            if missing:
                self.log_message(f"✗ ไม่พบ draft_templates: {', '.join(missing)} ใน config.json")
                self.root.after(0, lambda: self.stop_mode(mode_name))
                return

            while mode["running"]:
                self.log_message("กำลังสแกน Draft...")

                for key in ("accept", "draft-fight", "draft-best"):
                    pos = self.bot.find_image(templates[key], threshold)
                    if pos:
                        self.log_message(f"✓ พบปุ่ม {key.capitalize()} ที่ตำแหน่ง {pos}")
                        self.bot.background_click(pos[0], pos[1])
                        time.sleep(0.5)

                if self.bot.find_image(templates["draft-victory"], threshold):
                    self.log_message("✓ พบ Draft-victory - เช็คปุ่ม Continue")

                pos = self.bot.find_image(templates["continue"], threshold)
                if pos:
                    self.log_message(f"✓ พบปุ่ม Continue ที่ตำแหน่ง {pos}")
                    self.bot.background_click(pos[0], pos[1])
                    time.sleep(0.5)

                time.sleep(self.config["loop_delay"])

        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {e!s}")
            self.root.after(0, lambda: self.stop_mode(mode_name))

    def _run_bondling(self, sub_label):
        """Bondling mode — UI only for now: farm and catch have no scan loop yet."""
        mode_name = "bondling"
        self.log_message(f"✗ Bondling ({sub_label}) ยังไม่มีการทำงาน")
        self.root.after(0, lambda: self.stop_mode(mode_name))


def load_config():
    config_path = resource_path("config.json")
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def main():
    # Releases install as Rubitdd-Bot-update.exe; move back to Rubitdd-Bot.exe and restart under that name
    if migrate_update_exe_name():
        return

    root = ctk.CTk()

    config = None
    try:
        config = load_config()
    except Exception:
        pass

    # Show the GUI immediately so the window always appears, even if the
    # update check is slow or fails.
    BotGUI(root)

    def run_update_check():
        try:
            # Runs in the background and closes the app itself once an accepted update is ready to install
            start_update_check(root, config)
        except Exception:
            pass

    if config:
        root.after(500, run_update_check)

    root.mainloop()


if __name__ == "__main__":
    main()
