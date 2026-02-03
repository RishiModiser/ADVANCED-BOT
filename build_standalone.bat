@echo off
REM Build script for creating standalone executable on Windows
REM This script builds the ADVANCED-BOT into a single executable file

echo ================================================
echo ADVANCED-BOT Standalone Build Script
echo ================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers (this may take a few minutes)...
playwright install chromium

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo Building standalone executable...
pyinstaller advanced_bot.spec --clean --noconfirm

REM Check if build was successful
if exist "dist\ADVANCED-BOT.exe" (
    echo.
    echo ================================================
    echo BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Your standalone executable is ready:
    echo   Location: dist\ADVANCED-BOT.exe
    echo.
    echo To run the application:
    echo   Double-click dist\ADVANCED-BOT.exe
    echo   OR
    echo   Run from command line: dist\ADVANCED-BOT.exe
    echo.
    echo Note: On first run, the application will download
    echo       Playwright browsers automatically if needed.
    echo.
) else (
    echo.
    echo ================================================
    echo BUILD FAILED!
    echo ================================================
    echo Please check the error messages above.
    exit /b 1
)
