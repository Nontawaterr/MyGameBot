# Repository Guidelines

## Project Structure & Module Organization

This repository contains a Windows Python automation app for Rubitdd-Bot.

- `main.py` defines the CustomTkinter UI, mode tabs, configuration loading, and worker-thread control.
- `lib/` contains reusable logic: `game_control.py` for Win32/OpenCV screen capture and clicking, `updater.py` for release updates, and `version.py` for `APP_VERSION`.
- `assets/`, `sougenbi/`, `realm/`, and `yonder/` hold image templates used by the bot modes. Keep mode-specific images in their matching folder.
- `config.json` stores runtime settings. Avoid committing local-only secrets or machine-specific values.
- `build.bat`, `make_release.bat`, and `Rubitdd-Bot.spec` support PyInstaller builds and release packaging.

## Build, Test, and Development Commands

- `pip install -r requirements.txt` installs Python dependencies.
- `pip install -r requirements-dev.txt` installs runtime plus developer tools.
- `python main.py` runs the app locally for development.
- `dev_check.bat` runs Ruff lint checks and the pytest suite.
- `build.bat` creates `dist\Rubitdd-Bot.exe` with bundled assets and config.
- `make_release.bat` packages `dist\*` into `Rubitdd-Bot-Release.zip` and writes `release.json`.

Run commands from the repository root on Windows. The app depends on `pywin32`, so Linux/macOS behavior is not expected to work.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Follow the existing style: `snake_case` for functions, methods, variables, and module names; `PascalCase` for classes such as `BotGUI` and `GameControl`; uppercase constants such as `APP_VERSION`.

Keep UI wiring in `main.py` and reusable platform/game automation code in `lib/`. Prefer small helper methods over expanding long event handlers. When adding image-driven actions, name files by their visible purpose, for example `accept.png`, `start.png`, or `lose.png`.

## Testing Guidelines

Run automated tests with `python -m pytest` or `dev_check.bat`. Current tests focus on pure updater/version logic that does not require the GUI or game window. Before committing UI or automation changes, also run `python main.py` and manually verify each affected mode. For automation changes, test against the target game window in normal and background-window conditions. For release changes, run `build.bat` and confirm the generated executable starts.

If adding tests, place them under `tests/`, name files `test_*.py`, and prefer `pytest` for pure logic such as config parsing, version comparison, or updater behavior.

## Agent-Specific Instructions

Use the repo-local skill at `.codex/skills/rubitdd-bot-maintainer/` for repeated maintenance workflows. Its `project_check.py` helper validates required files, config JSON, mode asset folders, and Python syntax without needing external packages.

## Commit & Pull Request Guidelines

Git history is minimal, so use clear imperative commit messages such as `Update realm image matching` or `Fix release manifest hash`. Keep each commit focused on one behavior or asset set.

Pull requests should include a short summary, changed modes or assets, manual test steps, and screenshots or recordings for UI changes. Link related issues when available and note any config or release-package impact.
