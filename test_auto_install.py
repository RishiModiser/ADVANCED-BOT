#!/usr/bin/env python3
"""
Test auto-install logic and error detection patterns.
"""

import sys

def test_error_patterns():
    """Test that error patterns are correctly detected."""
    print("Testing error pattern detection...")
    print("=" * 60)
    
    # Test error patterns (must match those in advanced_bot.py)
    browser_not_found_patterns = [
        "Executable doesn't exist",  # Use double quotes to avoid escaping
        'Browser was not found',
        'Failed to launch',
        'Could not find browser',
        'No such file or directory',
        'playwright.chromium.launch'
    ]
    
    missing_deps_patterns = [
        'libgobject',
        'libnss',
        'libatk',
        'libdrm',
        'libgbm',
        'libasound',
        'error while loading shared libraries'
    ]
    
    test_cases = [
        ("Executable doesn't exist at /path/to/chromium", True, False),
        ("Browser was not found in cache", True, False),
        ("Failed to launch chromium browser", True, False),
        ("error while loading shared libraries: libgobject-2.0.so.0", False, True),
        ("error while loading shared libraries: libnss3.so", False, True),
        ("Connection refused", False, False),
        ("Some random error", False, False),
    ]
    
    passed = 0
    failed = 0
    
    for error_msg, should_be_browser_missing, should_be_deps_missing in test_cases:
        is_browser_missing = any(pattern in error_msg for pattern in browser_not_found_patterns)
        is_deps_missing = any(pattern in error_msg for pattern in missing_deps_patterns)
        
        if is_browser_missing == should_be_browser_missing and is_deps_missing == should_be_deps_missing:
            print(f"✓ PASS: '{error_msg[:50]}...'")
            passed += 1
        else:
            print(f"✗ FAIL: '{error_msg[:50]}...'")
            print(f"  Expected: browser_missing={should_be_browser_missing}, deps_missing={should_be_deps_missing}")
            print(f"  Got: browser_missing={is_browser_missing}, deps_missing={is_deps_missing}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print()
    
    return failed == 0


def main():
    """Run tests."""
    print()
    print("=" * 60)
    print("Auto-Install Logic Test")
    print("=" * 60)
    print()
    
    success = test_error_patterns()
    
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
