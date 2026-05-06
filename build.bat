@echo off
echo Building Rubitdd-Bot (Bundled Version)...

REM Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build EXE with bundled assets
pyinstaller --noconsole --onefile --name "Rubitdd-Bot" --icon "app.ico" --add-data "assets;assets" --add-data "sougenbi;sougenbi" --add-data "realm;realm" --add-data "config.json;." --collect-all customtkinter main.py

echo.
echo Build complete!
echo The 'Rubitdd-Bot.exe' in 'dist' now contains all assets and config.
echo You can share just the .exe file.
pause

