import json
import time
import os
import sys
import threading
from lib.game_control import GameControl
from lib.updater import maybe_run_update
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
import customtkinter as ctk

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
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
        self.root.geometry("650x350")
        self.root.resizable(False, False)
        
        self.is_running = False
        self.is_sougenbi_running = False
        self.is_realm_running = False
        self.is_yonder_running = False
        self.bot_thread = None
        self.sougenbi_thread = None
        self.realm_thread = None
        self.yonder_thread = None
        self.config = None
        self.bot = None
        
        self.setup_ui()
        self.load_configuration()
        
    def setup_ui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self.root, height=70, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(header_frame, 
                                   text=f"🐇 Rubitdd-Bot-v{APP_VERSION} 🐇", 
                                   font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Tab Control
        self.tab_control = ctk.CTkTabview(self.root, height=200)
        self.tab_control.pack(fill="x", padx=20, pady=10)
        self.tab_control.add("soul")
        self.tab_control.add("sougenbi")
        self.tab_control.add("realm")
        self.tab_control.add("yonder")
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.tab_control.tab("soul"), 
                                        text="● สถานะ: ปิด", 
                                        font=("Arial", 14, "bold"),
                                        text_color="#ff6b6b")
        self.status_label.pack(pady=20)
        
        # Button Frame
        button_frame = ctk.CTkFrame(self.tab_control.tab("soul"), fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Start Button
        self.start_button = ctk.CTkButton(button_frame, 
                                         text="▶ เริ่มทำงาน", 
                                         font=("Arial", 13, "bold"),
                                         fg_color="#51cf66",
                                         hover_color="#40c057",
                                         width=160,
                                         height=40,
                                         corner_radius=8,
                                         command=self.start_bot)
        self.start_button.pack(side="left", padx=10)
        
        # Stop Button
        self.stop_button = ctk.CTkButton(button_frame, 
                                        text="■ หยุดทำงาน", 
                                        font=("Arial", 13, "bold"),
                                        text_color="white",
                                        fg_color="#000000",
                                        hover_color="#131313",
                                        width=160,
                                        height=40,
                                        corner_radius=8,
                                        state="disabled",
                                        command=self.stop_bot)
        self.stop_button.pack(side="left", padx=10)

        # --- Sougenbi Tab UI ---
        # Status Label
        self.sougenbi_status_label = ctk.CTkLabel(self.tab_control.tab("sougenbi"), 
                                        text="● สถานะ: ปิด", 
                                        font=("Arial", 14, "bold"),
                                        text_color="#ff6b6b")
        self.sougenbi_status_label.pack(pady=20)
        
        # Button Frame
        sougenbi_button_frame = ctk.CTkFrame(self.tab_control.tab("sougenbi"), fg_color="transparent")
        sougenbi_button_frame.pack(pady=10)
        
        # Start Button
        self.sougenbi_start_button = ctk.CTkButton(sougenbi_button_frame, 
                                         text="▶ เริ่มทำงาน", 
                                         font=("Arial", 13, "bold"),
                                         fg_color="#51cf66",
                                         hover_color="#40c057",
                                         width=160,
                                         height=40,
                                         corner_radius=8,
                                         command=self.start_sougenbi)
        self.sougenbi_start_button.pack(side="left", padx=10)
        
        # Stop Button
        self.sougenbi_stop_button = ctk.CTkButton(sougenbi_button_frame, 
                                        text="■ หยุดทำงาน", 
                                        font=("Arial", 13, "bold"),
                                        text_color="white",
                                        fg_color="#000000",
                                        hover_color="#131313",
                                        width=160,
                                        height=40,
                                        corner_radius=8,
                                        state="disabled",
                                        command=self.stop_sougenbi)
        self.sougenbi_stop_button.pack(side="left", padx=10)

        # --- Realm Tab UI ---
        # Status Label
        self.realm_status_label = ctk.CTkLabel(self.tab_control.tab("realm"), 
                                        text="● สถานะ: ปิด", 
                                        font=("Arial", 14, "bold"),
                                        text_color="#ff6b6b")
        self.realm_status_label.pack(pady=20)
        
        # Button Frame
        realm_button_frame = ctk.CTkFrame(self.tab_control.tab("realm"), fg_color="transparent")
        realm_button_frame.pack(pady=10)
        
        # Start Button
        self.realm_start_button = ctk.CTkButton(realm_button_frame, 
                                         text="▶ เริ่มทำงาน", 
                                         font=("Arial", 13, "bold"),
                                         fg_color="#51cf66",
                                         hover_color="#40c057",
                                         width=160,
                                         height=40,
                                         corner_radius=8,
                                         command=self.start_realm)
        self.realm_start_button.pack(side="left", padx=10)
        
        # Stop Button
        self.realm_stop_button = ctk.CTkButton(realm_button_frame, 
                                        text="■ หยุดทำงาน", 
                                        font=("Arial", 13, "bold"),
                                        text_color="white",
                                        fg_color="#000000",
                                        hover_color="#131313",
                                        width=160,
                                        height=40,
                                        corner_radius=8,
                                        state="disabled",
                                        command=self.stop_realm)
        self.realm_stop_button.pack(side="left", padx=10)
 
        # --- Yonder Tab UI ---
        self.yonder_status_label = ctk.CTkLabel(
            self.tab_control.tab("yonder"),
            text="● สถานะ: ปิด",
            font=("Arial", 14, "bold"),
            text_color="#ff6b6b",
        )
        self.yonder_status_label.pack(pady=20)

        yonder_button_frame = ctk.CTkFrame(self.tab_control.tab("yonder"), fg_color="transparent")
        yonder_button_frame.pack(pady=10)

        self.yonder_start_button = ctk.CTkButton(
            yonder_button_frame,
            text="▶ เริ่มทำงาน",
            font=("Arial", 13, "bold"),
            fg_color="#51cf66",
            hover_color="#40c057",
            width=160,
            height=40,
            corner_radius=8,
            command=self.start_yonder,
        )
        self.yonder_start_button.pack(side="left", padx=10)

        self.yonder_stop_button = ctk.CTkButton(
            yonder_button_frame,
            text="■ หยุดทำงาน",
            font=("Arial", 13, "bold"),
            text_color="white",
            fg_color="#000000",
            hover_color="#131313",
            width=160,
            height=40,
            corner_radius=8,
            state="disabled",
            command=self.stop_yonder,
        )
        self.yonder_stop_button.pack(side="left", padx=10)

        
    def log_message(self, message):
        print(f"{time.strftime('%H:%M:%S')} - {message}")
        
    def load_configuration(self):
        try:
            config_path = resource_path('config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Resolve image paths
            for key, path in self.config['templates'].items():
                self.config['templates'][key] = resource_path(path)
            
            if 'sougenbi_templates' in self.config:
                for key, path in self.config['sougenbi_templates'].items():
                    self.config['sougenbi_templates'][key] = resource_path(path)

            if 'realm_templates' in self.config:
                for key, path in self.config['realm_templates'].items():
                    self.config['realm_templates'][key] = resource_path(path)

            if 'yonder_templates' in self.config:
                for key, path in self.config['yonder_templates'].items():
                    self.config['yonder_templates'][key] = resource_path(path)

            self.log_message("✓ โหลด config.json สำเร็จ")
            self.log_message(f"  หน้าต่างเป้าหมาย: {self.config['window_title']}")
        except FileNotFoundError:
            self.log_message("✗ ไม่พบไฟล์ config.json")
        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {str(e)}")
            
    def start_bot(self):
        if self.is_running:
            return
            
        if not self.config:
            self.log_message("✗ กรุณาตรวจสอบไฟล์ config.json")
            return
            
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="● สถานะ: กำลังทำงาน", text_color="#51cf66")
        
        self.log_message("=== เริ่มทำงานบอท ===")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
        
    def stop_bot(self):
        if not self.is_running:
            return
            
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="● สถานะ: ปิด", text_color="#ff6b6b")
        
        self.log_message("=== หยุดทำงานบอท ===")
        
    def run_bot(self):
        try:
            # Initialize Game Control
            self.bot = GameControl(self.config['window_title'])
            self.log_message("✓ เชื่อมต่อหน้าต่างเกมสำเร็จ")
            
            # Main Loop
            while self.is_running:
                self.log_message("กำลังสแกน...")
                
                # Check for start button
                start_pos = self.bot.find_image(
                    self.config['templates']['start_button'], 
                    self.config['confidence_threshold']
                )
                
                if start_pos:
                    self.log_message(f"✓ พบปุ่ม Start ที่ตำแหน่ง {start_pos}")
                    self.bot.background_click(start_pos[0], start_pos[1])
                    time.sleep(0.5)

                # Check for accept button
                accept_pos = self.bot.find_image(
                    self.config['templates']['accept_button'], 
                    self.config['confidence_threshold']
                )
                
                if accept_pos:
                    self.log_message(f"✓ พบปุ่ม Accept ที่ตำแหน่ง {accept_pos}")
                    self.bot.background_click(accept_pos[0], accept_pos[1])
                    time.sleep(0.5)

                # Check for dismiss button
                dismiss_pos = self.bot.find_image(
                    self.config['templates']['dismiss_button'], 
                    self.config['confidence_threshold']
                )
                
                if dismiss_pos:
                    self.log_message(f"✓ พบปุ่ม Dismiss ที่ตำแหน่ง {dismiss_pos}")
                    # Use background_click to allow user to use mouse simultaneously
                    self.bot.background_click(dismiss_pos[0], dismiss_pos[1])
                    time.sleep(0.5)

                # Check for continue button
                continue_pos = self.bot.find_image(
                    self.config['templates']['continue_button'], 
                    self.config['confidence_threshold']
                )
                
                if continue_pos:
                    self.log_message(f"✓ พบปุ่ม Continue ที่ตำแหน่ง {continue_pos}")
                    self.bot.background_click(continue_pos[0], continue_pos[1])
                    time.sleep(0.5)

                # Check for clear button
                clear_pos = self.bot.find_image(
                    self.config['templates']['clear_button'], 
                    self.config['confidence_threshold']
                )
                
                if clear_pos:
                    self.log_message(f"✓ พบปุ่ม Clear ที่ตำแหน่ง {clear_pos}")
                    self.bot.background_click(clear_pos[0], clear_pos[1])
                    time.sleep(0.5)

                # Check for donee button
                donee_pos = self.bot.find_image(
                    self.config['templates']['donee_button'], 
                    self.config['confidence_threshold']
                )
                
                if donee_pos:
                    self.log_message(f"✓ พบปุ่ม Donee ที่ตำแหน่ง {donee_pos}")
                    self.bot.background_click(donee_pos[0], donee_pos[1])
                    time.sleep(0.5)

                # Check for done1 button
                done1_pos = self.bot.find_image(
                    self.config['templates']['done1_button'], 
                    self.config['confidence_threshold']
                )
                
                if done1_pos:
                    self.log_message(f"✓ พบปุ่ม Done1 ที่ตำแหน่ง {done1_pos}")
                    self.bot.background_click(done1_pos[0], done1_pos[1])
                    time.sleep(0.5)
                
                time.sleep(self.config['loop_delay'])
                
        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {str(e)}")
            self.root.after(0, self.stop_bot)

    def start_sougenbi(self):
        if self.is_sougenbi_running:
            return
            
        if not self.config:
            self.log_message("✗ กรุณาตรวจสอบไฟล์ config.json")
            return
            
        self.is_sougenbi_running = True
        self.sougenbi_start_button.configure(state="disabled")
        self.sougenbi_stop_button.configure(state="normal")
        self.sougenbi_status_label.configure(text="● สถานะ: กำลังทำงาน", text_color="#51cf66")
        
        self.log_message("=== เริ่มทำงานบอท Sougenbi ===")
        
        # Start bot in separate thread
        self.sougenbi_thread = threading.Thread(target=self.run_sougenbi, daemon=True)
        self.sougenbi_thread.start()
        
    def stop_sougenbi(self):
        if not self.is_sougenbi_running:
            return
            
        self.is_sougenbi_running = False
        self.sougenbi_start_button.configure(state="normal")
        self.sougenbi_stop_button.configure(state="disabled")
        self.sougenbi_status_label.configure(text="● สถานะ: ปิด", text_color="#ff6b6b")
        
        self.log_message("=== หยุดทำงานบอท Sougenbi ===")
        
    def run_sougenbi(self):
        try:
            # Initialize Game Control if not already
            if not self.bot:
                self.bot = GameControl(self.config['window_title'])
                self.log_message("✓ เชื่อมต่อหน้าต่างเกมสำเร็จ")
            
            # Main Loop
            while self.is_sougenbi_running:
                self.log_message("กำลังสแกน Sougenbi...")
                
                templates = self.config.get('sougenbi_templates', {})
                
                # Check for start button
                if 'start' in templates:
                    start_pos = self.bot.find_image(
                        templates['start'], 
                        self.config['confidence_threshold']
                    )
                    
                    if start_pos:
                        self.log_message(f"✓ พบปุ่ม Start ที่ตำแหน่ง {start_pos}")
                        self.bot.background_click(start_pos[0], start_pos[1])
                        time.sleep(0.5)

                # Check for accept button
                if 'accept' in templates:
                    accept_pos = self.bot.find_image(
                        templates['accept'], 
                        self.config['confidence_threshold']
                    )
                    
                    if accept_pos:
                        self.log_message(f"✓ พบปุ่ม Accept ที่ตำแหน่ง {accept_pos}")
                        self.bot.background_click(accept_pos[0], accept_pos[1])
                        time.sleep(0.5)

                # Check for dismiss button
                if 'dismiss' in templates:
                    dismiss_pos = self.bot.find_image(
                        templates['dismiss'], 
                        self.config['confidence_threshold']
                    )
                    
                    if dismiss_pos:
                        self.log_message(f"✓ พบปุ่ม Dismiss ที่ตำแหน่ง {dismiss_pos}")
                        self.bot.background_click(dismiss_pos[0], dismiss_pos[1])
                        time.sleep(0.5)

                # Check for donee button
                if 'donee' in templates:
                    donee_pos = self.bot.find_image(
                        templates['donee'], 
                        self.config['confidence_threshold']
                    )
                    
                    if donee_pos:
                        self.log_message(f"✓ พบปุ่ม Donee ที่ตำแหน่ง {donee_pos}")
                        self.bot.background_click(donee_pos[0], donee_pos[1])
                        time.sleep(0.5)

                # Check for done1 button
                if 'done1' in templates:
                    done1_pos = self.bot.find_image(
                        templates['done1'], 
                        self.config['confidence_threshold']
                    )
                    
                    if done1_pos:
                        self.log_message(f"✓ พบปุ่ม Done1 ที่ตำแหน่ง {done1_pos}")
                        self.bot.background_click(done1_pos[0], done1_pos[1])
                        time.sleep(0.5)

                # Check for donee1 button
                if 'donee1' in templates:
                    donee1_pos = self.bot.find_image(
                        templates['donee1'], 
                        self.config['confidence_threshold']
                    )
                    
                    if donee1_pos:
                        self.log_message(f"✓ พบปุ่ม Donee1 ที่ตำแหน่ง {donee1_pos}")
                        self.bot.background_click(donee1_pos[0], donee1_pos[1])
                        time.sleep(0.5)
                
                time.sleep(self.config['loop_delay'])
                
        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {str(e)}")
            self.root.after(0, self.stop_sougenbi)

    def start_realm(self):
        if self.is_realm_running:
            return
            
        if not self.config:
            self.log_message("✗ กรุณาตรวจสอบไฟล์ config.json")
            return
            
        self.is_realm_running = True
        self.realm_start_button.configure(state="disabled")
        self.realm_stop_button.configure(state="normal")
        self.realm_status_label.configure(text="● สถานะ: กำลังทำงาน", text_color="#51cf66")
        
        self.log_message("=== เริ่มทำงานบอท Realm ===")
        
        # Start bot in separate thread
        self.realm_thread = threading.Thread(target=self.run_realm, daemon=True)
        self.realm_thread.start()
        
    def stop_realm(self):
        if not self.is_realm_running:
            return
            
        self.is_realm_running = False
        self.realm_start_button.configure(state="normal")
        self.realm_stop_button.configure(state="disabled")
        self.realm_status_label.configure(text="● สถานะ: ปิด", text_color="#ff6b6b")
        
        self.log_message("=== หยุดทำงานบอท Realm ===")
        
    def run_realm(self):
        try:
            # Initialize Game Control if not already
            if not self.bot:
                self.bot = GameControl(self.config['window_title'])
                self.log_message("✓ เชื่อมต่อหน้าต่างเกมสำเร็จ")
            
            hogan_blocked = False

            # Main Loop
            while self.is_realm_running:
                self.log_message("กำลังสแกน Realm...")
                
                templates = self.config.get('realm_templates', {})
                
                # Check for done1 button
                if 'done1' in templates:
                    done1_pos = self.bot.find_image(
                        templates['done1'], 
                        self.config['confidence_threshold']
                    )
                    
                    if done1_pos:
                        self.log_message(f"✓ พบปุ่ม Done1 ที่ตำแหน่ง {done1_pos}")
                        self.bot.background_click(done1_pos[0], done1_pos[1])
                        time.sleep(0.5)

                # Check for mark to block hogan - check every loop
                if 'mark' in templates:
                    mark_pos = self.bot.find_image(
                        templates['mark'],
                        self.config['confidence_threshold']
                    )
                    if mark_pos:
                        if not hogan_blocked:
                            self.log_message(f"✓ พบ Mark ที่ตำแหน่ง {mark_pos} - หยุดกด Hogan ชั่วคราว")
                        hogan_blocked = True

                # Check for hogan button - only if not blocked
                if 'hogan' in templates and not hogan_blocked:
                    hogan_pos = self.bot.find_image(
                        templates['hogan'], 
                        self.config['confidence_threshold']
                    )
                    
                    if hogan_pos:
                        self.log_message(f"✓ พบปุ่ม Hogan ที่ตำแหน่ง {hogan_pos}")
                        # Click 40px below the found image
                        self.bot.background_click(hogan_pos[0], hogan_pos[1] + 40)
                        time.sleep(0.5)

                # Check for next button
                if 'next' in templates:
                    next_pos = self.bot.find_image(
                        templates['next'], 
                        self.config['confidence_threshold']
                    )
                    
                    if next_pos:
                        self.log_message(f"✓ พบปุ่ม Next ที่ตำแหน่ง {next_pos}")
                        self.bot.background_click(next_pos[0], next_pos[1])
                        time.sleep(0.5)

                # Check for attack button
                if 'attack' in templates:
                    attack_pos = self.bot.find_image(
                        templates['attack'], 
                        self.config['confidence_threshold']
                    )
                    
                    if attack_pos:
                        self.log_message(f"✓ พบปุ่ม Attack ที่ตำแหน่ง {attack_pos}")
                        self.bot.background_click(attack_pos[0], attack_pos[1])
                        if hogan_blocked:
                            self.log_message("✓ เริ่มทำงาน Hogan อีกครั้ง")
                            hogan_blocked = False
                        time.sleep(0.5)

                # Check for lose button
                if 'lose' in templates:
                    lose_pos = self.bot.find_image(
                        templates['lose'], 
                        self.config['confidence_threshold']
                    )
                    
                    if lose_pos:
                        self.log_message(f"✓ พบปุ่ม Lose ที่ตำแหน่ง {lose_pos}")
                        self.bot.background_click(lose_pos[0], lose_pos[1])
                        time.sleep(1.5)

                # Check for lose1 button
                if 'lose1' in templates:
                    lose1_pos = self.bot.find_image(
                        templates['lose1'], 
                        self.config['confidence_threshold']
                    )
                    
                    if lose1_pos:
                        self.log_message(f"✓ พบปุ่ม Lose1 ที่ตำแหน่ง {lose1_pos}")
                        self.bot.background_click(lose1_pos[0], lose1_pos[1])
                        time.sleep(0.5)
                
                time.sleep(self.config['loop_delay'])
                
        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {str(e)}")
            self.root.after(0, self.stop_realm)

    def start_yonder(self):
        if self.is_yonder_running:
            return

        if not self.config:
            self.log_message("✗ กรุณาตรวจสอบไฟล์ config.json")
            return

        self.is_yonder_running = True
        self.yonder_start_button.configure(state="disabled")
        self.yonder_stop_button.configure(state="normal")
        self.yonder_status_label.configure(text="● สถานะ: กำลังทำงาน", text_color="#51cf66")

        self.log_message("=== เริ่มทำงานบอท Yonder ===")

        self.yonder_thread = threading.Thread(target=self.run_yonder, daemon=True)
        self.yonder_thread.start()

    def stop_yonder(self):
        if not self.is_yonder_running:
            return

        self.is_yonder_running = False
        self.yonder_start_button.configure(state="normal")
        self.yonder_stop_button.configure(state="disabled")
        self.yonder_status_label.configure(text="● สถานะ: ปิด", text_color="#ff6b6b")

        self.log_message("=== หยุดทำงานบอท Yonder ===")

    def run_yonder(self):
        try:
            if not self.bot:
                self.bot = GameControl(self.config['window_title'])
                self.log_message("✓ เชื่อมต่อหน้าต่างเกมสำเร็จ")

            templates = self.config.get('yonder_templates', {})
            challenge_template = templates.get('challenge')
            if not challenge_template:
                self.log_message("✗ ไม่พบ yonder_templates.challenge ใน config.json")
                self.root.after(0, self.stop_yonder)
                return

            while self.is_yonder_running:
                self.log_message("กำลังสแกน Yonder...")

                challenge_pos = self.bot.find_image(
                    challenge_template,
                    self.config['confidence_threshold']
                )

                if challenge_pos:
                    self.log_message(f"✓ พบ Challenge ที่ตำแหน่ง {challenge_pos}")
                    self.bot.background_click(challenge_pos[0], challenge_pos[1])
                    time.sleep(0.5)

                accept_template = templates.get('accept')
                if accept_template:
                    accept_pos = self.bot.find_image(
                        accept_template,
                        self.config['confidence_threshold']
                    )
                    if accept_pos:
                        self.log_message(f"✓ พบปุ่ม Accept ที่ตำแหน่ง {accept_pos}")
                        self.bot.background_click(accept_pos[0], accept_pos[1])
                        time.sleep(0.5)

                dismiss_template = templates.get('dismiss')
                if dismiss_template:
                    dismiss_pos = self.bot.find_image(
                        dismiss_template,
                        self.config['confidence_threshold']
                    )
                    if dismiss_pos:
                        self.log_message(f"✓ พบปุ่ม Dismiss ที่ตำแหน่ง {dismiss_pos}")
                        self.bot.background_click(dismiss_pos[0], dismiss_pos[1])
                        time.sleep(0.5)

                continue_template = templates.get('continue')
                if continue_template:
                    continue_pos = self.bot.find_image(
                        continue_template,
                        self.config['confidence_threshold']
                    )
                    if continue_pos:
                        self.log_message(f"✓ พบปุ่ม Continue ที่ตำแหน่ง {continue_pos}")
                        self.bot.background_click(continue_pos[0], continue_pos[1])
                        time.sleep(0.5)

                clear_template = templates.get('clear')
                if clear_template:
                    clear_pos = self.bot.find_image(
                        clear_template,
                        self.config['confidence_threshold']
                    )
                    if clear_pos:
                        self.log_message(f"✓ พบปุ่ม Clear ที่ตำแหน่ง {clear_pos}")
                        self.bot.background_click(clear_pos[0], clear_pos[1])
                        time.sleep(0.5)

                done1_template = templates.get('done1')
                if done1_template:
                    done1_pos = self.bot.find_image(
                        done1_template,
                        self.config['confidence_threshold']
                    )
                    if done1_pos:
                        self.log_message(f"✓ พบปุ่ม Done1 ที่ตำแหน่ง {done1_pos}")
                        self.bot.background_click(done1_pos[0], done1_pos[1])
                        time.sleep(0.5)

                time.sleep(self.config['loop_delay'])

        except Exception as e:
            self.log_message(f"✗ ข้อผิดพลาด: {str(e)}")
            self.root.after(0, self.stop_yonder)

def load_config():
    config_path = resource_path('config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    root = ctk.CTk()

    config = None
    try:
        config = load_config()
    except Exception:
        pass

    # Show the GUI immediately so the window always appears, even if the
    # update check is slow or fails.
    app = BotGUI(root)

    def run_update_check():
        try:
            if config and maybe_run_update(root, config):
                # Update accepted: close so the restart helper can replace files.
                root.destroy()
        except Exception:
            pass

    if config:
        root.after(500, run_update_check)

    root.mainloop()

if __name__ == "__main__":
    main()
