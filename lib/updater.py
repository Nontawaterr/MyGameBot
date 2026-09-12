import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

try:
    from tkinter import messagebox
except Exception:
    messagebox = None

from lib.version import APP_VERSION

USER_AGENT = "Rubitdd-Bot-Updater/1.0"
DEFAULT_TIMEOUT = 15
DEFAULT_MANIFEST_ASSET = "release.json"
DEFAULT_PACKAGE_ASSET = "Rubitdd-Bot-Release.zip"

# Releases ship the exe as UPDATE_EXE_NAME. The restart script in 1.0.0-1.0.5 copies the new exe
# over the running one right after the app exits, while the PyInstaller bootloader still locks it,
# so that copy fails; a different file name avoids the clash. The app renames itself back on launch.
CANONICAL_EXE_NAME = "Rubitdd-Bot.exe"
UPDATE_EXE_NAME = "Rubitdd-Bot-update.exe"

STAGE_DIR_PREFIX = "rubitdd_update_stage_"
HELPER_DIR_PREFIX = "rubitdd_update_helper_"
STALE_UPDATE_DIR_SECONDS = 60 * 60


class UpdateError(RuntimeError):
    pass


@dataclass(frozen=True)
class ReleaseManifest:
    version: str
    asset_name: str
    asset_url: str
    sha256: str
    notes: str = ""


def normalize_version(value):
    value = str(value).strip()
    if not value:
        return (0,)

    if value.lower().startswith("v"):
        value = value[1:]

    parts = []
    for token in value.replace("-", ".").split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        if not digits:
            break
        parts.append(int(digits))

    while parts and parts[-1] == 0:
        parts.pop()

    return tuple(parts) or (0,)


def is_newer_version(latest, current=APP_VERSION):
    return normalize_version(latest) > normalize_version(current)


def _build_request(url):
    return urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json, application/json;q=0.9, */*;q=0.8",
        },
    )


def fetch_json(url, timeout=DEFAULT_TIMEOUT):
    with urllib.request.urlopen(_build_request(url), timeout=timeout) as response:
        payload = response.read().decode("utf-8-sig")
    return json.loads(payload)


class DownloadProgress:
    """Byte counters a download worker updates and the Tk thread reads to draw progress."""

    def __init__(self):
        self.done = 0
        self.total = 0


def download_file(url, destination_path, timeout=DEFAULT_TIMEOUT, progress=None):
    destination_path = Path(destination_path)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(_build_request(url), timeout=timeout) as response:
        if progress is not None:
            progress.total = int(response.headers.get("Content-Length") or 0)
        with destination_path.open("wb") as output_file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output_file.write(chunk)
                if progress is not None:
                    progress.done += len(chunk)


def sha256_file(file_path):
    digest = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _get_update_settings(config):
    update = config.get("update") or {}
    release_api_url = str(update.get("release_api_url", "")).strip()
    manifest_asset_name = str(update.get("manifest_asset_name", DEFAULT_MANIFEST_ASSET)).strip() or DEFAULT_MANIFEST_ASSET
    package_asset_name = str(update.get("asset_name", DEFAULT_PACKAGE_ASSET)).strip() or DEFAULT_PACKAGE_ASSET
    enabled = bool(update.get("enabled", True))

    return {
        "enabled": enabled,
        "release_api_url": release_api_url,
        "manifest_asset_name": manifest_asset_name,
        "package_asset_name": package_asset_name,
    }


def _get_asset_by_name(release_data, asset_name):
    for asset in release_data.get("assets", []):
        if str(asset.get("name", "")).lower() == asset_name.lower():
            return asset
    return None


def _load_manifest_from_release(release_data, manifest_asset_name):
    manifest_asset = _get_asset_by_name(release_data, manifest_asset_name)
    if not manifest_asset:
        raise UpdateError(f"Manifest asset not found: {manifest_asset_name}")

    manifest_url = manifest_asset.get("browser_download_url")
    if not manifest_url:
        raise UpdateError("Manifest asset is missing browser_download_url")

    raw_manifest = fetch_json(manifest_url)

    version = str(raw_manifest.get("version", "")).strip()
    asset_name = str(raw_manifest.get("asset_name", "")).strip() or DEFAULT_PACKAGE_ASSET
    asset_url = str(raw_manifest.get("asset_url", "")).strip()
    sha256 = str(raw_manifest.get("sha256", "")).strip().lower()
    notes = str(raw_manifest.get("notes", "")).strip()

    if not version:
        raise UpdateError("Manifest is missing version")

    if not asset_url and not asset_name:
        raise UpdateError("Manifest is missing asset information")

    return ReleaseManifest(
        version=version,
        asset_name=asset_name,
        asset_url=asset_url,
        sha256=sha256,
        notes=notes,
    )


def _find_download_url(release_data, manifest):
    if manifest.asset_url:
        return manifest.asset_url

    asset = _get_asset_by_name(release_data, manifest.asset_name)
    if not asset:
        raise UpdateError(f"Package asset not found: {manifest.asset_name}")

    asset_url = asset.get("browser_download_url")
    if not asset_url:
        raise UpdateError("Package asset is missing browser_download_url")

    return asset_url


def _extract_zip(zip_path, extract_dir):
    extract_dir = Path(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(extract_dir)


def _find_launch_executable(extract_dir, preferred_name):
    extract_dir = Path(extract_dir)
    exe_candidates = list(extract_dir.rglob("*.exe"))

    if preferred_name:
        preferred_name = preferred_name.lower()
        for candidate in exe_candidates:
            if candidate.name.lower() == preferred_name:
                return candidate

    if len(exe_candidates) == 1:
        return exe_candidates[0]

    if exe_candidates:
        return sorted(exe_candidates, key=lambda item: (len(item.parts), item.name.lower()))[0]

    raise UpdateError("No executable was found inside the downloaded package")


def _write_restart_script(script_path):
    script = r"""param(
    [int]$ParentPid,
    [string]$SourceDir,
    [string]$TargetDir,
    [string]$LaunchExeName
)

$ErrorActionPreference = 'Stop'

try {
    while (Get-Process -Id $ParentPid -ErrorAction SilentlyContinue) {
        Start-Sleep -Milliseconds 250
    }

    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    # A one-file exe stays locked for a moment after the app exits (its bootloader process
    # cleans up first, antivirus may scan it), so keep retrying the copy for a while.
    $deadline = (Get-Date).AddSeconds(60)
    while ($true) {
        try {
            Get-ChildItem -LiteralPath $SourceDir -Force | ForEach-Object {
                Copy-Item -LiteralPath $_.FullName -Destination $TargetDir -Recurse -Force
            }
            break
        } catch {
            if ((Get-Date) -gt $deadline) { throw }
            Start-Sleep -Milliseconds 500
        }
    }

    $launchPath = Join-Path $TargetDir $LaunchExeName
    Start-Process -FilePath $launchPath -WorkingDirectory $TargetDir
} catch {
    Add-Type -AssemblyName System.Windows.Forms
    $message = "Update failed: $($_.Exception.Message)`n`nDownload Rubitdd-Bot-Release.zip from the GitHub Releases page and extract it over the old files."
    [System.Windows.Forms.MessageBox]::Show($message, 'Rubitdd-Bot update failed') | Out-Null
} finally {
    $stageRoot = Split-Path -Parent $SourceDir
    $helperRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (Test-Path -LiteralPath $stageRoot) {
        Remove-Item -LiteralPath $stageRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $helperRoot) {
        Remove-Item -LiteralPath $helperRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
"""
    Path(script_path).write_text(script, encoding="utf-8")


def _launch_restart_helper(parent_pid, source_dir, target_dir, launch_exe_name):
    helper_dir = Path(tempfile.mkdtemp(prefix=HELPER_DIR_PREFIX))
    try:
        script_path = helper_dir / "restart.ps1"
        _write_restart_script(script_path)

        subprocess.Popen(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                "-ParentPid",
                str(parent_pid),
                "-SourceDir",
                str(source_dir),
                "-TargetDir",
                str(target_dir),
                "-LaunchExeName",
                launch_exe_name,
            ],
            creationflags=subprocess.CREATE_NO_WINDOW,
            cwd=str(target_dir),
            env=_fresh_app_env(),
        )
    except BaseException:
        shutil.rmtree(helper_dir, ignore_errors=True)
        raise


def _fresh_app_env():
    """Environment for starting a frozen exe as its own app instead of a child of this process."""
    env = dict(os.environ)
    env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return env


def _copy_with_retry(source, destination, attempts=20, delay=0.5):
    for attempt in range(attempts):
        try:
            shutil.copyfile(source, destination)
            return True
        except OSError:
            if attempt < attempts - 1:
                time.sleep(delay)
    return False


def _remove_with_retry(path, attempts=60, delay=0.5):
    for _ in range(attempts):
        try:
            Path(path).unlink()
            return
        except FileNotFoundError:
            return
        except OSError:
            time.sleep(delay)


def migrate_update_exe_name():
    """Move a freshly installed UPDATE_EXE_NAME back to CANONICAL_EXE_NAME.

    Running as the update name: copy this exe over CANONICAL_EXE_NAME, start that copy and
    return True so the caller exits. Running as the canonical name: delete a leftover update
    exe in the background, since it stays locked for a moment while that process exits.
    """
    if not getattr(sys, "frozen", False):
        return False

    exe = Path(sys.executable)
    canonical = exe.with_name(CANONICAL_EXE_NAME)

    if exe.name.lower() == UPDATE_EXE_NAME.lower():
        if not _copy_with_retry(exe, canonical):
            return False  # e.g. the old exe is still open; keep running under the update name
        subprocess.Popen([str(canonical)], cwd=str(exe.parent), env=_fresh_app_env())
        return True

    leftover = exe.with_name(UPDATE_EXE_NAME)
    if exe.name.lower() == CANONICAL_EXE_NAME.lower() and leftover.exists():
        threading.Thread(target=_remove_with_retry, args=(leftover,), daemon=True).start()
    return False


def _show_error(title, message, parent=None):
    if messagebox is None:
        return

    try:
        messagebox.showerror(title, message, parent=parent)
    except Exception:
        pass


def _show_info(title, message, parent=None):
    if messagebox is None:
        return

    try:
        messagebox.showinfo(title, message, parent=parent)
    except Exception:
        pass


def _update_prompt(release_data, manifest):
    notes = manifest.notes or str(release_data.get("body", "")).strip()
    lines = [f"New version {manifest.version} is available."]
    if notes:
        lines += ["", notes]
    lines += ["", "Download and install the update now?"]
    return "\n".join(lines)


def _remove_stale_update_dirs(temp_root=None, max_age=STALE_UPDATE_DIR_SECONDS, now=None):
    """Delete staging folders left by an update that never finished, e.g. the app was closed mid-download."""
    temp_root = Path(temp_root or tempfile.gettempdir())
    now = time.time() if now is None else now
    for prefix in (STAGE_DIR_PREFIX, HELPER_DIR_PREFIX):
        for path in temp_root.glob(prefix + "*"):
            try:
                if path.is_dir() and now - path.stat().st_mtime > max_age:
                    shutil.rmtree(path, ignore_errors=True)
            except OSError:
                pass


def _fetch_available_update(settings):
    """Return (release_data, manifest) when a newer release is published, else None."""
    _remove_stale_update_dirs()
    try:
        release_data = fetch_json(settings["release_api_url"])
        manifest = _load_manifest_from_release(release_data, settings["manifest_asset_name"])
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None  # no release published yet — not an error
        raise
    if not is_newer_version(manifest.version, APP_VERSION):
        return None
    return release_data, manifest


def _stage_and_launch_update(release_data, manifest, settings, progress=None):
    """Download, verify and extract the package, then start the restart helper that installs it.

    If anything fails, the staging folder is deleted before the error propagates. Once the
    helper is running it owns the folder and deletes it after copying.
    """
    package_url = _find_download_url(release_data, manifest)
    current_exe = Path(sys.executable)
    stage_root = Path(tempfile.mkdtemp(prefix=STAGE_DIR_PREFIX))
    try:
        zip_path = stage_root / settings["package_asset_name"]
        extract_dir = stage_root / "extracted"

        download_file(package_url, zip_path, progress=progress)
        if manifest.sha256 and sha256_file(zip_path).lower() != manifest.sha256.lower():
            raise UpdateError("Checksum mismatch for the downloaded package")

        _extract_zip(zip_path, extract_dir)
        launch_exe = _find_launch_executable(extract_dir, current_exe.name)
        _launch_restart_helper(os.getpid(), extract_dir, current_exe.parent, launch_exe.name)
    except BaseException:
        shutil.rmtree(stage_root, ignore_errors=True)
        raise


def _run_in_background(root, work, on_success, on_error, poll_ms=100):
    """Run work() on a daemon thread, then call on_success(result) or on_error(exc) on the Tk thread."""
    outcome = {}

    def target():
        try:
            outcome["result"] = work()
        except BaseException as exc:
            outcome["error"] = exc

    worker = threading.Thread(target=target, daemon=True)
    worker.start()

    def poll():
        if worker.is_alive():
            root.after(poll_ms, poll)
        elif "error" in outcome:
            on_error(outcome["error"])
        else:
            on_success(outcome.get("result"))

    root.after(poll_ms, poll)


class _ProgressWindow:
    """Small window that follows DownloadProgress while the download worker runs."""

    def __init__(self, root, version, progress):
        import tkinter as tk
        from tkinter import ttk

        self.progress = progress
        self.version = version
        self.closed = False
        self.window = tk.Toplevel(root)
        self.window.title("Updating Rubitdd-Bot")
        self.window.resizable(False, False)
        self.window.transient(root)
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)  # closing it would not stop the download
        self.label = ttk.Label(self.window, text=f"Downloading version {version}...", width=-50)
        self.label.pack(padx=20, pady=(16, 8))
        self.bar = ttk.Progressbar(self.window, length=320, maximum=100)
        self.bar.pack(padx=20, pady=(0, 16))
        self._refresh()

    def _refresh(self):
        if self.closed:
            return
        done, total = self.progress.done, self.progress.total
        mb = 1024 * 1024
        if total and done >= total:
            self.label.configure(text=f"Installing version {self.version}...")
            self.bar.configure(value=100)
        elif total:
            percent = done * 100 // total
            self.label.configure(text=f"Downloading version {self.version}... {percent}% ({done // mb} / {total // mb} MB)")
            self.bar.configure(value=percent)
        else:
            self.label.configure(text=f"Downloading version {self.version}... {done // mb} MB")
        self.window.after(200, self._refresh)

    def close(self):
        self.closed = True
        try:
            self.window.destroy()
        except Exception:
            pass


def start_update_check(root, config):
    """Check for a newer release and offer to install it without blocking the Tk main loop.

    Network and file work run on worker threads; dialogs and windows stay on the Tk thread.
    When the user accepts, a progress window follows the download, and the app closes once
    the restart helper that installs the update is running.
    """
    settings = _get_update_settings(config)
    release_api_url = settings["release_api_url"]
    if (
        not settings["enabled"]
        or not release_api_url
        or "<OWNER>" in release_api_url
        or "<REPO>" in release_api_url
        or not getattr(sys, "frozen", False)
        or messagebox is None
    ):
        return

    def on_checked(found):
        if not found:
            return
        release_data, manifest = found
        if not messagebox.askyesno("Update available", _update_prompt(release_data, manifest), parent=root):
            return

        progress = DownloadProgress()
        window = _ProgressWindow(root, manifest.version, progress)

        def on_installed(_result):
            window.close()
            root.destroy()  # the restart helper waits for this process to exit

        def on_install_failed(exc):
            window.close()
            _show_error("Update failed", str(exc), parent=root)

        _run_in_background(
            root,
            lambda: _stage_and_launch_update(release_data, manifest, settings, progress),
            on_installed,
            on_install_failed,
        )

    def on_check_failed(exc):
        _show_error("Update failed", str(exc), parent=root)

    _run_in_background(root, lambda: _fetch_available_update(settings), on_checked, on_check_failed)
