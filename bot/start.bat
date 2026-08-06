@echo off
echo ========================================
echo   Forex Signals Trading Bot
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

REM Check .env
if not exist .env (
    echo .env tidak ditemukan!
    echo Copy .env.example ke .env dan isi konfigurasi.
    copy .env.example .env
    echo Silakan edit .env terlebih dahulu!
    pause
    exit /b 1
)

echo.
echo Memulai bot...
echo Tekan Ctrl+C untuk berhenti.
echo.
python bot.py
pause
