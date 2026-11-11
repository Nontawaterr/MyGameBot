@echo off
echo Creating release package...

if not exist "dist\Rubitdd-Bot.exe" (
    echo Error: Rubitdd-Bot.exe not found in dist folder.
    echo Please run build.bat first.
    pause
    exit /b
)

for /f %%V in ('python -c "from lib.version import APP_VERSION; print(APP_VERSION)"') do set VERSION=%%V
if not defined VERSION (
    echo Error: Could not read APP_VERSION.
    exit /b 1
)

echo Zipping Rubitdd-Bot.exe as Rubitdd-Bot-update.exe...
REM The zip ships the exe under another name: the updater in 1.0.0-1.0.5 can't overwrite the
REM still-locked running Rubitdd-Bot.exe. The app renames itself back on first launch.
if exist "build\release" rmdir /s /q "build\release"
mkdir "build\release"
copy /y "dist\Rubitdd-Bot.exe" "build\release\Rubitdd-Bot-update.exe" >nul
if errorlevel 1 (
    echo Error: Could not prepare the update executable.
    exit /b 1
)
powershell -NoProfile -Command "Compress-Archive -Path build\release\* -DestinationPath Rubitdd-Bot-Release.zip -Force"
if errorlevel 1 (
    echo Error: Could not create Rubitdd-Bot-Release.zip.
    exit /b 1
)

echo Creating release manifest...
python -c "import hashlib,json,pathlib; p=pathlib.Path('Rubitdd-Bot-Release.zip'); manifest={'version':'%VERSION%','asset_name':p.name,'asset_url':'','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'notes':''}; pathlib.Path('release.json').write_text(json.dumps(manifest, indent=4), encoding='utf-8')"
if errorlevel 1 (
    echo Error: Could not create release.json.
    exit /b 1
)

echo.
echo ========================================================
echo  Package created successfully: Rubitdd-Bot-Release.zip
echo ========================================================
echo  Manifest file created: release.json
echo.
echo Upload both Rubitdd-Bot-Release.zip and release.json to the GitHub Release.
echo The app will use release.json to compare versions and verify the package hash.
echo.
echo You can also send this zip file to other computers.
echo They just need to extract it and run Rubitdd-Bot.exe
echo.
pause
