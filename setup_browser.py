#!/usr/bin/env python3
"""
Browser Setup Helper Script
Installs Playwright Chromium browser required for the bot to function.
"""

import subprocess
import sys
import platform
import shutil

def install_system_deps():
    """Install system dependencies on Linux if needed."""
    if platform.system() != 'Linux':
        return True

    try:
        # Prefer python -m playwright so it uses the correct installation
        result = subprocess.run(
            [sys.executable, '-m', 'playwright', 'install-deps', 'chromium'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            # Fall back to bare executable if module invocation failed
            playwright_path = shutil.which('playwright')
            if playwright_path:
                subprocess.run(
                    [playwright_path, 'install-deps', 'chromium'],
                    capture_output=True,
                    text=True
                )
            else:
                print("Note: System dependencies installation may require sudo privileges")
                print("If browser fails to launch, run:")
                print("  sudo python -m playwright install-deps chromium")
                print()
        return True
    except Exception as e:
        print(f"Note: Could not install system dependencies: {e}")
        print("If browser fails to launch, run:")
        print("  sudo python -m playwright install-deps chromium")
        print()
        return True

def main():
    """Install Playwright Chromium browser."""
    print("=" * 60)
    print("Installing Playwright Chromium Browser")
    print("=" * 60)
    print()

    # Try python -m playwright first (works even when 'playwright' isn't on PATH)
    install_cmds = [
        [sys.executable, '-m', 'playwright', 'install', 'chromium'],
    ]
    playwright_path = shutil.which('playwright')
    if playwright_path:
        install_cmds.append([playwright_path, 'install', 'chromium'])

    last_error = None
    for cmd in install_cmds:
        print(f"Running: {' '.join(cmd)}")
        print()
        try:
            subprocess.run(cmd, check=True)
            last_error = None
            break
        except subprocess.CalledProcessError as e:
            last_error = e
        except FileNotFoundError as e:
            last_error = e

    if last_error is not None:
        print()
        print("=" * 60)
        print("✗ Installation failed!")
        print("=" * 60)
        print()
        print(f"Error: {last_error}")
        print()
        print("Please ensure you have installed the requirements first:")
        print("  pip install -r requirements.txt")
        print()
        return 1

    print()

    # Try to install system dependencies
    install_system_deps()

    print("=" * 60)
    print("✓ Browser installation completed successfully!")
    print("=" * 60)
    print()
    print("You can now run the bot with: python humanexbot_v5.py")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
