@echo off
setlocal EnableExtensions
title HumanexBot Production Build
cd /d "%~dp0"

echo [HumanexBot] Validating Python...
where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python launcher was not found.
  exit /b 1
)

if not exist ".build-venv\Scripts\python.exe" (
  py -3 -m venv .build-venv
  if errorlevel 1 exit /b 1
)
set "PYTHON=%CD%\.build-venv\Scripts\python.exe"

echo [HumanexBot] Installing pinned build dependencies...
"%PYTHON%" -m pip install --upgrade pip
"%PYTHON%" -m pip install -r requirements.txt pyinstaller==6.11.1
if errorlevel 1 exit /b 1

echo [HumanexBot] Running syntax and unit checks...
"%PYTHON%" -m compileall -q .
"%PYTHON%" -m unittest discover -s tests -v
if errorlevel 1 exit /b 1

echo [HumanexBot] Provisioning managed Chromium and Firefox...
set "PLAYWRIGHT_BROWSERS_PATH=%CD%\playwright-browsers"
"%PYTHON%" -m playwright install chromium firefox
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo [HumanexBot] Building HumanexBot.exe...
"%PYTHON%" -m PyInstaller --clean --noconfirm humanexbot_v5.spec
if errorlevel 1 exit /b 1

if not exist "dist\HumanexBot.exe" (
  echo ERROR: dist\HumanexBot.exe was not generated.
  exit /b 1
)
echo HumanexBot executable created successfully.
exit /b 0
