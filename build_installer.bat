@echo off
setlocal EnableExtensions
title HumanexBot Installer Build
cd /d "%~dp0"

call build.bat
if errorlevel 1 exit /b 1

if not exist "redist" mkdir redist
if not exist "redist\vc_redist.x64.exe" (
  echo [HumanexBot] Downloading Microsoft Visual C++ runtime...
  where curl.exe >nul 2>&1
  if errorlevel 1 (
    echo ERROR: curl.exe is required to download the VC++ runtime.
    exit /b 1
  )
  curl.exe -L --fail --silent --show-error ^
    -o "redist\vc_redist.x64.exe" ^
    "https://aka.ms/vs/17/release/vc_redist.x64.exe"
  if errorlevel 1 exit /b 1
)

set "ISCC="
where ISCC.exe >nul 2>&1
if not errorlevel 1 set "ISCC=ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
  echo ERROR: Inno Setup 6 was not found.
  exit /b 1
)

echo [HumanexBot] Building branded installer...
"%ISCC%" "installer\HumanexBot.iss"
if errorlevel 1 exit /b 1
if not exist "dist\HumanexBot_Setup.exe" (
  echo ERROR: dist\HumanexBot_Setup.exe was not generated.
  exit /b 1
)
copy /y "README_INSTALLATION.txt" "dist\README_INSTALLATION.txt" >nul
echo Production deliverables are in dist\.
exit /b 0
