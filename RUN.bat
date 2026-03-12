@echo off
REM ========================================================
REM ADVANCED-BOT - ONE-CLICK LAUNCHER
REM ========================================================
REM Double-click this file to start ADVANCED-BOT.
REM On first run, any missing dependencies are installed
REM automatically - no manual steps required!
REM ========================================================

title ADVANCED-BOT Launcher

color 0A
echo.
echo  ========================================================
echo  ^|                                                      ^|
echo  ^|      ADVANCED-BOT - One-Click Launcher              ^|
echo  ^|                                                      ^|
echo  ========================================================
echo.

REM ── Option 1: Run pre-built standalone executable if present ──────────────
if exist "dist\ADVANCED-BOT.exe" (
    echo  Launching pre-built ADVANCED-BOT executable...
    echo.
    start "" "dist\ADVANCED-BOT.exe"
    timeout /t 3 /nobreak >nul
    exit
)

REM ── Option 2: Run with Python (auto-installs deps on first run) ───────────
python --version >nul 2>&1
if not errorlevel 1 (
    echo  Python found. Starting ADVANCED-BOT...
    echo  ^(First run will auto-install any missing dependencies^)
    echo.
    python advanced_bot.py
    exit /b %errorlevel%
)

REM Try python3 as fallback
python3 --version >nul 2>&1
if not errorlevel 1 (
    echo  Python found. Starting ADVANCED-BOT...
    echo  ^(First run will auto-install any missing dependencies^)
    echo.
    python3 advanced_bot.py
    exit /b %errorlevel%
)

REM ── No Python found ───────────────────────────────────────────────────────
color 0C
echo.
echo  ========================================================
echo  ^|                                                      ^|
echo  ^|      Python is not installed!                       ^|
echo  ^|                                                      ^|
echo  ========================================================
echo.
echo  Python is required to run ADVANCED-BOT.
echo.
echo  Please download and install Python 3.8 or higher from:
echo.
echo      https://www.python.org/downloads/
echo.
echo  IMPORTANT: During installation, check the box:
echo      "Add Python to PATH"
echo.
echo  After installing Python, double-click this file again.
echo  Everything else will be set up automatically!
echo.
pause
exit /b 1
