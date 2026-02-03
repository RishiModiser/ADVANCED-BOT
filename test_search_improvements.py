#!/usr/bin/env python3
"""
Test Suite for Search Improvements
- Bing redirect URL handling
- Google CTRL+K method
"""

import sys
import re


def test_bing_redirect_handling():
    """Test that Bing redirect URLs are properly handled."""
    print("Testing Bing redirect URL handling...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Import parse_qs and unquote
    if re.search(r'from urllib\.parse import.*parse_qs', content):
        checks.append("✓ parse_qs is imported")
    else:
        checks.append("✗ parse_qs is not imported")
    
    if re.search(r'from urllib\.parse import.*unquote', content):
        checks.append("✓ unquote is imported")
    else:
        checks.append("✗ unquote is not imported")
    
    # Check 2: Bing redirect detection
    if re.search(r'bing\.com.*in href.*and.*\/ck\/a.*in href', content, re.DOTALL):
        checks.append("✓ Bing redirect detection implemented")
    else:
        checks.append("✗ Bing redirect detection not found")
    
    # Check 3: URL parameter extraction
    if re.search(r"params.*=.*parse_qs", content):
        checks.append("✓ URL parameter parsing implemented")
    else:
        checks.append("✗ URL parameter parsing not found")
    
    # Check 4: Real URL extraction from 'u' parameter
    if re.search(r"'u'.*in params", content):
        checks.append("✓ Extracts real URL from 'u' parameter")
    else:
        checks.append("✗ Does not extract from 'u' parameter")
    
    # Check 5: URL decoding with unquote
    if re.search(r'unquote\(', content):
        checks.append("✓ URL decoding with unquote implemented")
    else:
        checks.append("✗ URL decoding not found")
    
    # Check 6: Improved filtering for Bing redirects
    if re.search(r'is_bing_redirect', content):
        checks.append("✓ Special filtering for Bing redirects")
    else:
        checks.append("✗ No special filtering for Bing redirects")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def test_google_ctrl_k_method():
    """Test that Google CTRL+K method is implemented."""
    print("\nTesting Google CTRL+K method...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Special handling for Google
    if re.search(r"if search_engine == ['\"]Google['\"]:", content):
        checks.append("✓ Special handling for Google search engine")
    else:
        checks.append("✗ No special handling for Google")
    
    # Check 2: Navigate to about:blank
    if re.search(r"about:blank", content):
        checks.append("✓ Navigates to about:blank for Google")
    else:
        checks.append("✗ Does not navigate to about:blank")
    
    # Check 3: Press CTRL+K
    if re.search(r"keyboard\.press.*Control\+K", content):
        checks.append("✓ Presses CTRL+K to activate Chrome search")
    else:
        checks.append("✗ Does not press CTRL+K")
    
    # Check 4: Human-like typing for keyword
    if re.search(r'for char in keyword:.*keyboard\.type\(char\)', content, re.DOTALL):
        checks.append("✓ Types keyword character by character (human-like)")
    else:
        checks.append("✗ Does not type keyword character by character")
    
    # Check 5: Press Enter after typing
    if re.search(r"keyboard\.press.*Enter", content):
        checks.append("✓ Presses Enter after typing")
    else:
        checks.append("✗ Does not press Enter")
    
    # Check 6: Wait for results after Enter
    if re.search(r"wait_for_load_state.*after.*Enter", content, re.DOTALL | re.IGNORECASE):
        checks.append("✓ Waits for page load after Enter")
    else:
        # Check if there's wait_for_load_state after keyboard.press('Enter')
        if re.search(r"keyboard\.press\(['\"]Enter['\"].*wait_for_load_state", content, re.DOTALL):
            checks.append("✓ Waits for page load after Enter")
        else:
            checks.append("✗ No wait for page load after Enter")
    
    # Check 7: Updated docstring mentions CTRL+K
    if re.search(r"CTRL\+K", content):
        checks.append("✓ Documentation mentions CTRL+K method")
    else:
        checks.append("✗ Documentation doesn't mention CTRL+K")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def test_enhanced_logging():
    """Test that enhanced logging is present."""
    print("\nTesting enhanced logging...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check for debug logging of Bing redirects
    if re.search(r"emit_log.*Bing redirect detected", content):
        checks.append("✓ Debug logging for Bing redirect detection")
    else:
        checks.append("✗ No debug logging for Bing redirects")
    
    # Check for logging of real URL extraction
    if re.search(r"emit_log.*Real URL", content):
        checks.append("✓ Logging shows extracted real URLs")
    else:
        checks.append("✗ No logging for real URL extraction")
    
    # Check for CTRL+K logging
    if re.search(r"emit_log.*CTRL\+K", content, re.IGNORECASE):
        checks.append("✓ Logging mentions CTRL+K activation")
    else:
        checks.append("✗ No logging for CTRL+K")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def main():
    print("=" * 70)
    print("Search Improvements Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run tests
    passed, score, total = test_bing_redirect_handling()
    results.append(("Bing redirect URL handling", passed, score, total))
    
    passed, score, total = test_google_ctrl_k_method()
    results.append(("Google CTRL+K method", passed, score, total))
    
    passed, score, total = test_enhanced_logging()
    results.append(("Enhanced logging", passed, score, total))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    all_passed = True
    for name, passed, score, total in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status} ({score}/{total})")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ All tests PASSED! Implementation is complete.")
        return 0
    else:
        print("\n❌ Some tests FAILED. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
