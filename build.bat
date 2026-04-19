@echo off
REM ========================================================
REM ADVANCED-BOT - Build Script (Windows)
REM ========================================================
REM Builds a single executable from advanced_bot.py
REM Usage: build.bat
REM ========================================================

title ADVANCED-BOT - Build

echo.
echo  ========================================================
echo  ^|      ADVANCED-BOT - Build Script                    ^|
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

echo  ERROR: Python is not installed or not in PATH!
echo  Please install Python 3.8+ from https://www.python.org/downloads/
echo.
pause
exit /b 1

:python_found
echo  [1/3] Python found:
%PYTHON_CMD% --version
echo.

REM ── Install build dependencies ────────────────────────────────────────────
echo  [2/3] Installing dependencies...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install pyinstaller
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.

REM ── Build executable ──────────────────────────────────────────────────────
echo  [3/3] Building executable...
echo        This may take several minutes...
echo.
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
%PYTHON_CMD% -m PyInstaller --onefile --windowed advanced_bot.py

if errorlevel 1 (
    echo.
    echo  BUILD FAILED - Check the error messages above.
    echo.
    pause
    exit /b 1
)

if exist "dist\advanced_bot.exe" (
    echo.
    echo  ========================================================
    echo  ^|      BUILD SUCCESSFUL!                              ^|
    echo  ^|                                                      ^|
    echo  ^|      Executable: dist\advanced_bot.exe              ^|
    echo  ========================================================
    echo.
) else (
    echo.
    echo  BUILD FAILED - Executable not found.
    echo.
    pause
    exit /b 1
)

pause
