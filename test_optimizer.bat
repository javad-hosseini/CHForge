@echo off
cd /d "%~dp0"

echo ============================================================
echo CHForge - Resource Optimizer Test
echo ============================================================
echo.

call venv\Scripts\activate.bat

echo.
echo Running optimizer test...
echo.

python test_optimizer.py

echo.
echo ============================================================
pause