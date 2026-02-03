@echo off
REM Simple run script for standalone executable on Windows

echo ================================================
echo ADVANCED-BOT Launcher
echo ================================================
echo.

REM Check if executable exists
if not exist "dist\ADVANCED-BOT.exe" (
    echo ERROR: Executable not found!
    echo.
    echo The standalone executable has not been built yet.
    echo Please run the build script first:
    echo.
    echo   build_standalone.bat
    echo.
    pause
    exit /b 1
)

REM Run the application
echo Starting ADVANCED-BOT...
echo.
start "" "dist\ADVANCED-BOT.exe"
