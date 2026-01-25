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
        # Verify playwright executable exists
        playwright_path = shutil.which('playwright')
        if not playwright_path:
            print("Note: Playwright executable not found in PATH")
            return True
        
        print("Installing system dependencies for Linux...")
        result = subprocess.run(
            [playwright_path, 'install-deps', 'chromium'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("Note: System dependencies installation may require sudo privileges")
            print("If browser fails to launch, run:")
            print("  sudo playwright install-deps chromium")
            print()
        return True
    except Exception as e:
        print(f"Note: Could not install system dependencies: {e}")
        print("If browser fails to launch, run:")
        print("  sudo playwright install-deps chromium")
        print()
        return True

def main():
    """Install Playwright Chromium browser."""
    print("=" * 60)
    print("Installing Playwright Chromium Browser")
    print("=" * 60)
    print()
    
    try:
        # Verify playwright executable exists
        playwright_path = shutil.which('playwright')
        if not playwright_path:
            print()
            print("=" * 60)
            print("✗ Playwright not found in PATH!")
            print("=" * 60)
            print()
            print("Please install the requirements first:")
            print("  pip install -r requirements.txt")
            print()
            return 1
        
        print(f"Using playwright from: {playwright_path}")
        print("Running: playwright install chromium")
        print()
        
        result = subprocess.run(
            [playwright_path, 'install', 'chromium'],
            check=True
        )
        
        print()
        
        # Try to install system dependencies
        install_system_deps()
        
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


if __name__ == '__main__':
    sys.exit(main())
