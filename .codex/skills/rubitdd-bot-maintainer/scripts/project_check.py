from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REQUIRED_FILES = [
    "main.py",
    "config.json",
    "requirements.txt",
    "build.bat",
    "make_release.bat",
    "Rubitdd-Bot.spec",
    "lib/game_control.py",
    "lib/updater.py",
    "lib/version.py",
]
ASSET_DIRS = ["assets", "sougenbi", "realm"]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))
    print("OK: required files exist")


def check_config_json() -> None:
    try:
        json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"config.json is invalid: {exc}")
    print("OK: config.json parses")


def check_assets() -> None:
    for folder in ASSET_DIRS:
        asset_dir = ROOT / folder
        if not asset_dir.exists():
            fail(f"Missing asset directory: {folder}")
        png_count = len(list(asset_dir.glob("*.png")))
        if png_count == 0:
            fail(f"No PNG templates found in {folder}")
        print(f"OK: {folder} has {png_count} PNG templates")


def check_python_syntax() -> None:
    py_files = [ROOT / "main.py", *sorted((ROOT / "lib").glob("*.py"))]
    test_dir = ROOT / "tests"
    if test_dir.exists():
        py_files.extend(sorted(test_dir.glob("test_*.py")))

    for file_path in py_files:
        source = file_path.read_text(encoding="utf-8")
        compile(source, str(file_path), "exec")
    print(f"OK: {len(py_files)} Python files pass syntax check")


def main() -> int:
    check_required_files()
    check_config_json()
    check_assets()
    check_python_syntax()
    print("Project check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
