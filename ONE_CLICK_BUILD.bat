@echo off
REM ========================================================
REM ONE-CLICK BUILD - ADVANCED-BOT
REM ========================================================
REM This script will build a standalone executable that
REM requires NO Python installation to run!
REM
REM Just double-click this file and wait for the build!
REM ========================================================

title ADVANCED-BOT - One-Click Builder

color 0A
echo.
echo  ========================================================
echo  ^|                                                      ^|
echo  ^|      ADVANCED-BOT - ONE-CLICK BUILD SCRIPT          ^|
echo  ^|                                                      ^|
echo  ^|      Building a standalone executable...            ^|
echo  ^|      No Python needed on target computers!          ^|
echo  ^|                                                      ^|
echo  ========================================================
echo.
echo  Please wait while we:
echo    - Check Python installation
echo    - Install build tools
echo    - Download dependencies
echo    - Build the executable
echo.
echo  This may take 5-10 minutes on first run...
echo.
echo  ========================================================
echo.
pause
echo.

REM Call the main build script
call build_standalone.bat

REM Check result
if errorlevel 1 (
    color 0C
    echo.
    echo  ========================================================
    echo  ^|                                                      ^|
    echo  ^|      BUILD FAILED - Please check errors above       ^|
    echo  ^|                                                      ^|
    echo  ========================================================
    echo.
    pause
    exit /b 1
) else (
    color 0A
    echo.
    echo  ========================================================
    echo  ^|                                                      ^|
    echo  ^|      SUCCESS! Your standalone executable is ready!  ^|
    echo  ^|                                                      ^|
    echo  ^|      Location: dist\ADVANCED-BOT.exe                ^|
    echo  ^|                                                      ^|
    echo  ^|      You can now distribute this file to any        ^|
    echo  ^|      Windows computer - no installation needed!     ^|
    echo  ^|                                                      ^|
    echo  ========================================================
    echo.
    echo  Press any key to exit...
    pause >nul
)
