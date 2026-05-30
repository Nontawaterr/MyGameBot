# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Rubitdd-Bot is a Windows desktop automation bot for the game Onmyoji (陰陽師). It captures screenshots of the game window via Win32 APIs, matches UI element images using OpenCV template matching, and sends background clicks (without moving the physical mouse) so the user can continue using their computer.

## Commands

```
pip install -r requirements.txt          # install runtime deps
pip install -r requirements-dev.txt      # install runtime + dev deps (pytest, ruff)
python main.py                           # run the app
dev_check.bat                            # lint (ruff) + test (pytest) in one step
python -m ruff check .                   # lint only
python -m pytest                         # test only
python -m pytest tests/test_updater.py::test_normalize_version  # single test
build.bat                                # PyInstaller → dist\Rubitdd-Bot.exe
make_release.bat                         # package dist\ into zip + release.json
```

All commands run from the repo root on Windows. The app requires `pywin32` and only works on Windows.

## Architecture

**Entry point**: `main.py` — CustomTkinter GUI with four tabs (soul, sougenbi, realm, yonder), each a "mode" that runs its own scan-and-click loop in a daemon thread.

**`lib/game_control.py`** — `GameControl` class: finds the game window by title via `win32gui.FindWindow`, captures background screenshots using `PrintWindow`/`BitBlt`, runs `cv2.matchTemplate` to locate UI elements, and sends `WM_LBUTTONDOWN`/`WM_LBUTTONUP` via `PostMessage` for background clicks.

**`lib/updater.py`** — Self-update system: fetches `release.json` manifest from GitHub Releases, compares versions, downloads zip, verifies SHA-256, extracts, and spawns a PowerShell restart helper. Only runs when `sys.frozen` is True (PyInstaller builds).

**`lib/version.py`** — Single `APP_VERSION` string; bump this before building a release.

**`config.json`** — Runtime config: `window_title`, `confidence_threshold`, `loop_delay`, template image paths per mode (`templates`, `sougenbi_templates`, `realm_templates`, `yonder_templates`), and update settings. Template paths are resolved via `resource_path()` at load time (handles both dev and PyInstaller `_MEIPASS`).

**Image template folders**: `assets/` (soul mode), `sougenbi/`, `realm/`, `yonder/` — each contains PNG/JPG screenshots of game buttons used for template matching. Keep mode-specific images in their matching folder.

## Domain Language

- **Mode**: a self-contained automation flow mapped to one UI tab and one template group.
- **Template**: an image file used for OpenCV matching to find a clickable element.
- **Background click**: a click sent via `PostMessage` without moving the physical cursor.
- **Confidence threshold**: minimum `matchTemplate` score (0–1) to count a template as found.

## Coding Conventions

- `snake_case` for functions/variables/modules, `PascalCase` for classes, `UPPER_CASE` for constants.
- UI wiring stays in `main.py`; reusable Win32/OpenCV logic lives in `lib/`.
- Ruff config: line length 120, target Python 3.8+, rules E/F/I/UP/B (E501 ignored).
- Pytest config: tests in `tests/`, files named `test_*.py`, functions named `test_*`.

## Build & Release

PyInstaller bundles assets, sougenbi, realm, yonder folders and config.json into a single .exe. The `build.bat` uses `--onefile --noconsole`. After building, `make_release.bat` creates `Rubitdd-Bot-Release.zip` + `release.json` (with SHA-256 hash) for GitHub Releases upload.
