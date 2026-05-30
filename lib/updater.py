import hashlib
import json
import os
import subprocess
import sys
import tempfile
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


def download_file(url, destination_path, timeout=DEFAULT_TIMEOUT):
    destination_path = Path(destination_path)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(_build_request(url), timeout=timeout) as response:
        with destination_path.open("wb") as output_file:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output_file.write(chunk)


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

try {
    while (Get-Process -Id $ParentPid -ErrorAction SilentlyContinue) {
        Start-Sleep -Seconds 1
    }

    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    Get-ChildItem -LiteralPath $SourceDir -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $TargetDir -Recurse -Force
    }

    $launchPath = Join-Path $TargetDir $LaunchExeName
    Start-Process -FilePath $launchPath -WorkingDirectory $TargetDir
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
    helper_dir = Path(tempfile.mkdtemp(prefix="rubitdd_update_helper_"))
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
    )


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


def maybe_run_update(root, config):
    settings = _get_update_settings(config)

    if not settings["enabled"]:
        return False

    release_api_url = settings["release_api_url"]
    if not release_api_url or "<OWNER>" in release_api_url or "<REPO>" in release_api_url:
        return False

    if not getattr(sys, "frozen", False):
        return False

    try:
        release_data = fetch_json(release_api_url)
        manifest = _load_manifest_from_release(release_data, settings["manifest_asset_name"])

        if not is_newer_version(manifest.version, APP_VERSION):
            return False

        notes = manifest.notes or str(release_data.get("body", "")).strip()
        prompt = [f"New version {manifest.version} is available."]
        if notes:
            prompt.append("")
            prompt.append(notes)
        prompt.append("")
        prompt.append("Download and install the update now?")

        if messagebox is None:
            return False

        if not messagebox.askyesno("Update available", "\n".join(prompt), parent=root):
            return False

        package_url = _find_download_url(release_data, manifest)
        current_exe = Path(sys.executable)
        target_dir = current_exe.parent
        launch_exe_name = current_exe.name

        stage_root = Path(tempfile.mkdtemp(prefix="rubitdd_update_stage_"))
        zip_path = stage_root / settings["package_asset_name"]
        extract_dir = stage_root / "extracted"

        download_file(package_url, zip_path)

        if manifest.sha256:
            downloaded_hash = sha256_file(zip_path)
            if downloaded_hash.lower() != manifest.sha256.lower():
                raise UpdateError("Checksum mismatch for the downloaded package")

        _extract_zip(zip_path, extract_dir)
        launch_exe = _find_launch_executable(extract_dir, launch_exe_name)
        launch_exe_name = launch_exe.name

        _launch_restart_helper(
            os.getpid(),
            extract_dir,
            target_dir,
            launch_exe_name,
        )
        return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            # No release published yet — not an error
            return False
        _show_error("Update failed", str(exc), parent=root)
        return False
    except Exception as exc:
        _show_error("Update failed", str(exc), parent=root)
        return False
