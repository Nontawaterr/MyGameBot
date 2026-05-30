# Rubitdd-Bot Workflows

## Add or Replace Image Templates

1. Identify the mode folder: `assets/` for soul, `sougenbi/` for sougenbi, `realm/` for realm, or `yonder/` for challenge assets.
2. Use short lowercase names that describe the visible target.
3. Search `main.py` for the old filename before renaming or removing an asset.
4. If adding a new top-level folder, update `build.bat` and `Rubitdd-Bot.spec` so PyInstaller bundles it.
5. Validate by running the app and exercising the affected mode against the real game window.

## Build and Release

1. Run `python -m compileall -q lib tests`.
2. Run `python -m pytest` and `python -m ruff check .` when dev dependencies are installed.
3. Run `build.bat`.
4. Start `dist\Rubitdd-Bot.exe` and confirm the UI opens.
5. Run `make_release.bat` to create `Rubitdd-Bot-Release.zip` and `release.json`.
6. Confirm `release.json` contains the expected version from `lib/version.py` and a non-empty lowercase SHA-256 hash.

## Refactor Safely

Prefer extracting pure logic from `main.py` before modifying behavior. Good candidates are config loading, button state transitions, mode definitions, path resolution, and updater decisions. Keep Win32 calls isolated in `lib/game_control.py` so pure functions can be tested without a game window.

## Manual Verification Checklist

- App starts with `python main.py`.
- Each changed tab can start and stop without leaving stale button state.
- The bot handles a missing target window with a clear error.
- Background screenshot still works when the game is covered but not minimized.
- Build output starts from `dist\Rubitdd-Bot.exe`.

