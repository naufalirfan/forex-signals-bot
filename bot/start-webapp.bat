@echo off
echo ========================================
echo   Forex Signals Webapp Server
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python tidak ditemukan! Install Python terlebih dahulu.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

echo.
echo Memulai webapp server...
echo Akses di http://localhost:8080
echo Tekan Ctrl+C untuk berhenti.
echo.
python server.py
pause
