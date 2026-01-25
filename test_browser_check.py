#!/usr/bin/env python3
"""
Test the browser check function to ensure it correctly detects browser installation.
"""

import sys
from pathlib import Path

# Import the check function
sys.path.insert(0, str(Path(__file__).parent))
from advanced_bot import check_browser_installation


def main():
    """Test browser installation check."""
    print("Testing browser installation check...")
    print("-" * 60)
    
    result = check_browser_installation()
    
    if result:
        print("✓ Browser installation detected successfully")
        print()
        print("The application should start without warnings.")
        return 0
    else:
        print("✗ Browser installation not detected")
        print()
        print("The application will show a warning dialog on startup.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
