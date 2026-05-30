@echo off
echo Running Python quality checks...

python -m ruff check .
if errorlevel 1 exit /b 1

python -m pytest
if errorlevel 1 exit /b 1

echo.
echo Checks passed.

