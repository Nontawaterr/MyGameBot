---
name: rubitdd-bot-maintainer
description: Maintain this Rubitdd-Bot repository, a Windows Python CustomTkinter and OpenCV game automation app. Use when changing bot modes, image template assets, Win32 automation behavior, updater/version logic, PyInstaller build files, release packaging, or project quality checks.
---

# Rubitdd Bot Maintainer

## Core Workflow

Start by reading the relevant files instead of assuming structure:

- UI and mode orchestration: `main.py`
- Window capture and background clicks: `lib/game_control.py`
- Update and release manifest logic: `lib/updater.py`
- Current app version: `lib/version.py`
- Runtime settings: `config.json`
- Image templates: `assets/`, `sougenbi/`, `realm/`, `yonder/`
- Build and release scripts: `build.bat`, `make_release.bat`, `Rubitdd-Bot.spec`

Before editing, check `git status --short` and preserve unrelated user changes.

## Task Guidance

For UI changes, keep CustomTkinter code in `main.py` unless extracting a clearly reusable helper. Do not block the UI thread; keep long-running bot loops in worker threads and update button/status state consistently.

For automation changes, treat `GameControl` as Windows-only code. Validate assumptions about window title matching, minimized windows, screenshot dimensions, and OpenCV image matching before changing click behavior.

For asset updates, keep files in the mode-specific folder and use descriptive lowercase names such as `accept.png`, `start.png`, or `lose.png`. Update PyInstaller data includes if adding a new top-level asset folder.

For updater or release work, update `lib/version.py`, verify manifest fields, preserve SHA-256 verification, and run the release package workflow only after a successful build.

## Validation

Use the project-local helper first:

```powershell
python .codex\skills\rubitdd-bot-maintainer\scripts\project_check.py
```

Then run available checks:

```powershell
python -m compileall -q lib tests
python -m pytest
python -m ruff check .
```

If `pytest` or `ruff` is missing, ask to install `requirements-dev.txt` or continue with `compileall` plus focused manual verification.

For GUI and bot behavior, manual verification is required: run `python main.py`, test affected tabs, and confirm the target game window can be found in foreground and background conditions. For packaging, run `build.bat`, start `dist\Rubitdd-Bot.exe`, then run `make_release.bat` only if the executable works.

## Additional Reference

Read `references/workflows.md` when the task involves a full build/release, asset addition, or deeper refactor.

