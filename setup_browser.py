#!/usr/bin/env python3
"""Developer helper for installing HumanexBot's managed browsers."""

import sys
from app_runtime import install_missing_browsers

def main():
    """Install Playwright Chromium and Firefox browsers."""
    print("=" * 60)
    print("Installing Playwright Chromium Browser")
    print("=" * 60)
    print()

    # Try python -m playwright first (works even when 'playwright' isn't on PATH)
    result = install_missing_browsers()
    if result.returncode != 0:
        print()
        print("=" * 60)
        print("✗ Installation failed!")
        print("=" * 60)
        print()
        print(result.stderr or result.stdout)
        print()
        print("Please ensure you have installed the requirements first:")
        print("  pip install -r requirements.txt")
        print()
        return 1

    print()

    print("=" * 60)
    print("✓ Chromium and Firefox installation completed successfully!")
    print("=" * 60)
    print()
    print("You can now run the bot with: python humanexbot_v5.py")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
