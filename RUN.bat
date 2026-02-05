@echo off
REM ========================================================
REM ADVANCED-BOT LAUNCHER
REM ========================================================
REM Simple launcher for the standalone executable
REM ========================================================

title ADVANCED-BOT Launcher

REM Check if executable exists
if not exist "dist\ADVANCED-BOT.exe" (
    color 0C
    echo.
    echo  ========================================================
    echo  ^|                                                      ^|
    echo  ^|      EXECUTABLE NOT FOUND!                          ^|
    echo  ^|                                                      ^|
    echo  ========================================================
    echo.
    echo  The standalone executable has not been built yet.
    echo.
    echo  Please build it first by running:
    echo    ONE_CLICK_BUILD.bat
    echo.
    echo  Or use the manual build script:
    echo    build_standalone.bat
    echo.
    pause
    exit /b 1
)

REM Run the application
color 0A
echo.
echo  ========================================================
echo  ^|                                                      ^|
echo  ^|      ADVANCED-BOT - Starting...                     ^|
echo  ^|                                                      ^|
echo  ========================================================
echo.
echo  Launching ADVANCED-BOT...
echo.
echo  Note: On first run, the application will download
echo        Playwright browsers (takes 1-2 minutes).
echo.
echo  This window can be closed once the app starts.
echo.

start "" "dist\ADVANCED-BOT.exe"

timeout /t 3 /nobreak >nul
exit
