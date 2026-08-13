@echo off
REM ========================================================
REM HumanexBot Version 5.0 - Windows Installer Builder
REM ========================================================
REM Builds dist\humanexbot_v5.exe and packages it with Inno Setup.
REM Usage: build_installer.bat
REM ========================================================

title HumanexBot Version 5.0 - Installer Build

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo  ========================================================
echo  ^|      HumanexBot Version 5.0 - Installer Build               ^|
echo  ========================================================
echo.

if not exist "dist\humanexbot_v5.exe" (
    echo  [1/3] Executable not found. Building app first...
    call build.bat
    if errorlevel 1 (
        echo.
        echo  ERROR: build.bat failed.
        pause
        exit /b 1
    )
) else (
    echo  [1/3] Found existing executable: dist\humanexbot_v5.exe
)
echo.

echo  [2/3] Detecting Inno Setup compiler...
set "ISCC_CMD="
where iscc >nul 2>&1
if not errorlevel 1 (
    set "ISCC_CMD=iscc"
    goto :iscc_found
)
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_CMD=%ProgramFiles%\Inno Setup 6\ISCC.exe"

:iscc_found
if "%ISCC_CMD%"=="" (
    echo.
    echo  ERROR: Inno Setup not found.
    echo  Install Inno Setup 6 from:
    echo      https://jrsoftware.org/isinfo.php
    echo.
    pause
    exit /b 1
)
echo  Inno Setup compiler: %ISCC_CMD%
echo.

echo  [3/3] Building installer...
"%ISCC_CMD%" "installer\HumanexBot.iss"
if errorlevel 1 (
    echo.
    echo  ERROR: Installer build failed.
    pause
    exit /b 1
)

echo.
echo  ========================================================
echo  ^|  SUCCESS! Installer created in:                          ^|
echo  ^|  installer\output\HumanexBot-Setup-v5.0.exe             ^|
echo  ========================================================
echo.
pause
