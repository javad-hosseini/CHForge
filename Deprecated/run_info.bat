@echo off
echo ============================================================
echo CHForge - System Information
echo ============================================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running system information collector...
echo.

python -m chforge.system.info

echo.
echo ============================================================
echo Done!
pause