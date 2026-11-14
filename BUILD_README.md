# HumanexBot production build

## Windows prerequisites

- Windows 10/11 64-bit
- Python 3.11 or newer supported by the pinned dependencies
- Inno Setup 6
- Internet access for the first browser payload download
- Internet access while building to retrieve the Microsoft Visual C++ x64 runtime

## Build

Run `build_installer.bat` from a Developer Command Prompt or by double-clicking
it. The script creates an isolated `.build-venv`, installs pinned dependencies,
runs syntax/unit checks, downloads the Playwright-managed Chromium and Firefox
payloads, builds `HumanexBot.exe`, and creates the Inno Setup installer.

The final files are:

```
dist/
  HumanexBot.exe
  HumanexBot_Setup.exe
  README_INSTALLATION.txt
```

The installer is the customer deliverable. The executable is windowed and does
not open a console. Browser payloads are embedded in the packaged application;
user settings, activation data, logs, and profiles remain under the user's
application-data directory during upgrades and uninstall.

## Windows-only validation

On a clean Windows 10/11 VM, verify installation without Python, first launch,
activation, Chromium and Firefox startup, offline launch, retry/repair behavior,
desktop and Start Menu shortcuts, upgrade preservation, and uninstallation.
