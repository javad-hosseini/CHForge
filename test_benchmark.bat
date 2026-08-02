@echo off
cd /d "%~dp0"

echo ============================================================
echo CHForge - Benchmark Test
echo ============================================================
echo.

call venv\Scripts\activate.bat

echo.
echo Running benchmark test...
echo.

python test_benchmark.py

echo.
echo ============================================================
pause