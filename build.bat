@echo off
echo Building Rubitdd-Bot (Bundled Version)...

REM Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

if exist "dist" (
    echo Error: Could not remove the dist folder. Close Rubitdd-Bot.exe and try again.
    exit /b 1
)
if exist "build" (
    echo Error: Could not remove the build folder.
    exit /b 1
)

REM Build EXE with bundled assets
pyinstaller --noconsole --onefile --name "Rubitdd-Bot" --icon "app.ico" --add-data "assets;assets" --add-data "sougenbi;sougenbi" --add-data "realm;realm" --add-data "yonder;yonder" --add-data "even;even" --add-data "draft;draft" --add-data "config.json;." --collect-all customtkinter main.py
if errorlevel 1 (
    echo Error: PyInstaller build failed.
    exit /b 1
)

if not exist "dist\Rubitdd-Bot.exe" (
    echo Error: dist\Rubitdd-Bot.exe was not created.
    exit /b 1
)

echo.
echo Build complete!
echo The 'Rubitdd-Bot.exe' in 'dist' now contains all assets and config.
echo You can share just the .exe file.
pause

