@echo off
REM Build script for creating standalone executable on Windows
REM This script builds the ADVANCED-BOT into a single executable file

setlocal enabledelayedexpansion

echo ================================================
echo ADVANCED-BOT Standalone Build Script
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed or not in PATH!
    echo.
    echo Please reinstall Python with pip included.
    echo.
    pause
    exit /b 1
)

echo [2/5] Installing/Upgrading dependencies...
pip install --upgrade pip
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller!
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install required dependencies!
    echo Please check requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo.

echo [3/5] Installing Playwright browsers...
echo This may take a few minutes on first run...
playwright install chromium
if errorlevel 1 (
    echo WARNING: Playwright browser installation had issues.
    echo The application will attempt to download browsers on first run.
)
echo.

echo [4/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

echo [5/5] Building standalone executable...
echo This may take several minutes...
pyinstaller advanced_bot.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ================================================
    echo BUILD FAILED!
    echo ================================================
    echo.
    echo PyInstaller encountered an error.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

REM Check if build was successful
if exist "dist\ADVANCED-BOT.exe" (
    echo.
    echo ================================================
    echo BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Your standalone executable is ready:
    echo   Location: dist\ADVANCED-BOT.exe
    echo   Size: 
    dir "dist\ADVANCED-BOT.exe" | find "ADVANCED-BOT.exe"
    echo.
    echo ================================================
    echo USAGE INSTRUCTIONS
    echo ================================================
    echo.
    echo To run the application:
    echo   1. Double-click: dist\ADVANCED-BOT.exe
    echo   2. Or run from command line: dist\ADVANCED-BOT.exe
    echo.
    echo First Run Notes:
    echo   - The application will check for Playwright browsers
    echo   - If not found, it will download them automatically
    echo   - This one-time download takes 1-2 minutes
    echo   - After that, the app starts instantly!
    echo.
    echo ================================================
    echo DISTRIBUTION
    echo ================================================
    echo.
    echo You can distribute dist\ADVANCED-BOT.exe to other computers.
    echo No Python or dependencies required on target systems!
    echo.
    echo For end users, include DISTRIBUTION_README.txt
    echo.
    pause
) else (
    echo.
    echo ================================================
    echo BUILD FAILED!
    echo ================================================
    echo.
    echo The executable was not created.
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo   - Missing dependencies
    echo   - Insufficient disk space
    echo   - Antivirus blocking PyInstaller
    echo.
    pause
    exit /b 1
)
