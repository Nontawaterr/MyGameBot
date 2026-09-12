@echo off
echo Creating release package...

if not exist "dist\Rubitdd-Bot.exe" (
    echo Error: Rubitdd-Bot.exe not found in dist folder.
    echo Please run build.bat first.
    pause
    exit /b
)

for /f %%V in ('python -c "from lib.version import APP_VERSION; print(APP_VERSION)"') do set VERSION=%%V

echo Zipping Rubitdd-Bot.exe as Rubitdd-Bot-update.exe...
REM The zip ships the exe under another name: the updater in 1.0.0-1.0.5 can't overwrite the
REM still-locked running Rubitdd-Bot.exe. The app renames itself back on first launch.
if exist "build\release" rmdir /s /q "build\release"
mkdir "build\release"
copy /y "dist\Rubitdd-Bot.exe" "build\release\Rubitdd-Bot-update.exe" >nul
powershell -NoProfile -Command "Compress-Archive -Path build\release\* -DestinationPath Rubitdd-Bot-Release.zip -Force"

echo Creating release manifest...
powershell -NoProfile -Command ^
  "$version = '%VERSION%';" ^
  "$zipName = 'Rubitdd-Bot-Release.zip';" ^
  "$hash = (Get-FileHash -Algorithm SHA256 -Path $zipName).Hash.ToLower();" ^
  "$manifest = [ordered]@{ version = $version; asset_name = $zipName; asset_url = ''; sha256 = $hash; notes = '' };" ^
  "$manifest | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 'release.json'"

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
