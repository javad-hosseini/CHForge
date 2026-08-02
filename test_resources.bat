@echo off
cd /d "%~dp0"

echo ============================================================
echo CHForge - Resource Manager Test
echo ============================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running Resource Manager tests...
echo.

python test_resources.py

echo.
echo ============================================================
echo.
echo Press any key to exit...
pause > nul