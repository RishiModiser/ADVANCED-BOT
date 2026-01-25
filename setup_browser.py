#!/usr/bin/env python3
"""
Browser Setup Helper Script
Installs Playwright Chromium browser required for the bot to function.
"""

import subprocess
import sys

def main():
    """Install Playwright Chromium browser."""
    print("=" * 60)
    print("Installing Playwright Chromium Browser")
    print("=" * 60)
    print()
    
    try:
        print("Running: playwright install chromium")
        print()
        
        result = subprocess.run(
            ['playwright', 'install', 'chromium'],
            check=True
        )
        
        print()
        print("=" * 60)
        print("✓ Browser installation completed successfully!")
        print("=" * 60)
        print()
        print("You can now run the bot with: python advanced_bot.py")
        print()
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ Installation failed!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Please ensure you have installed the requirements first:")
        print("  pip install -r requirements.txt")
        print()
        return 1
        
    except FileNotFoundError:
        print()
        print("=" * 60)
        print("✗ Playwright not found!")
        print("=" * 60)
        print()
        print("Please install the requirements first:")
        print("  pip install -r requirements.txt")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
