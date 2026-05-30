@echo off
REM ========================================================
REM ADVANCED-BOT - ONE-CLICK LAUNCHER
REM ========================================================
REM Double-click this file to start ADVANCED-BOT instantly.
REM
REM FIRST TIME? Run INSTALL.bat once to set everything up,
REM then use this file for instant 1-click launch!
REM ========================================================

title ADVANCED-BOT

color 0A
echo.
echo  ========================================================
echo  ^|      ADVANCED-BOT - Starting...                     ^|
echo  ========================================================
echo.

REM ── Find Python ───────────────────────────────────────────────────────────
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :run_bot
)
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :run_bot
)

REM ── No Python found ───────────────────────────────────────────────────────
color 0C
echo  ERROR: Python is not installed!
echo.
echo  Please download Python 3.8+ from:
echo      https://www.python.org/downloads/
echo  Check "Add Python to PATH" during install.
echo.
pause
exit /b 1

:run_bot
REM ── Check if setup was done (show hint if not) ────────────────────────────
if not exist ".bot_ready" (
    echo  First launch detected. Running one-time setup automatically...
    echo.
    call INSTALL.bat --no-pause
    if errorlevel 1 (
        color 0C
        echo  ERROR: One-time setup failed. Please run INSTALL.bat manually.
        echo.
        pause
        exit /b 1
    )
    echo  Setup complete. Starting bot...
    echo.
)

%PYTHON_CMD% advanced_bot.py
exit /b %errorlevel%
