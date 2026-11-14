@echo off
REM ========================================================
REM HumanexBot Version 5.0 - ONE-TIME SETUP / INSTALLER
REM ========================================================
REM Run this file ONCE to install all dependencies.
REM After setup, double-click RUN.bat to start the bot instantly!
REM ========================================================

title HumanexBot Version 5.0 - Setup
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
set NO_PAUSE=
if /I "%~1"=="--no-pause" set NO_PAUSE=1

color 0A
echo.
echo  ========================================================
echo  ^|                                                      ^|
echo  ^|      HumanexBot Version 5.0 - One-Time Setup                  ^|
echo  ^|                                                      ^|
echo  ^|  Run this once, then use RUN.bat for instant start  ^|
echo  ^|                                                      ^|
echo  ========================================================
echo.

REM ── Check Python ─────────────────────────────────────────────────────────
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

color 0C
echo  ERROR: Python is not installed!
echo.
echo  Please download and install Python 3.8 or higher from:
echo      https://www.python.org/downloads/
echo.
echo  IMPORTANT: During installation, check "Add Python to PATH"
echo.
if not defined NO_PAUSE pause
exit /b 1

:python_found
echo  [1/3] Python found:
%PYTHON_CMD% --version
echo.

REM ── Install pip packages ──────────────────────────────────────────────────
echo  [2/3] Installing Python packages...
echo        (This is the slow part - only happens once!)
echo.
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Failed to install Python packages!
    echo  Please check your internet connection and try again.
    echo.
    if not defined NO_PAUSE pause
    exit /b 1
)
echo.

REM ── Install Playwright browser ────────────────────────────────────────────
echo [3/3] Installing Playwright browsers (Chromium + Firefox)...
echo        (This downloads the managed browser payloads once!)
echo.
%PYTHON_CMD% -m playwright install chromium firefox
if errorlevel 1 (
    echo.
    echo  WARNING: Playwright browser install had issues.
    echo  The bot will try to download it automatically on first run.
    echo.
)

REM ── Mark setup as complete ────────────────────────────────────────────────
echo. > .bot_ready

echo.
color 0A
echo  ========================================================
echo  ^|                                                      ^|
echo  ^|   Setup Complete! Everything is installed.          ^|
echo  ^|                                                      ^|
echo  ^|   Now double-click RUN.bat to start the bot         ^|
echo  ^|   instantly - no more waiting!                      ^|
echo  ^|                                                      ^|
echo  ========================================================
echo.
if not defined NO_PAUSE pause