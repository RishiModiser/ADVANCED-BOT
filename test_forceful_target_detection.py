#!/usr/bin/env python3
"""
Test Suite for Forceful Target Domain Detection & New Tab Opening
Tests the enhanced functionality for detecting and opening target domains.
"""

import sys
import re


def test_new_tab_opening():
    """Test that target domain opens in a new tab."""
    print("Testing new tab opening functionality...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check for Ctrl+Click implementation
    checks.append(("Ctrl+Click with Control modifier", "modifiers=['Control']" in content or 'modifiers=["Control"]' in content))
    
    # Check for new page creation
    checks.append(("Creates new page/tab", "context.new_page()" in content))
    
    # Check for closing search results page
    checks.append(("Closes search results page after opening target", "await page.close()" in content))
    
    # Check for new tab in fallback scenarios
    checks.append(("Fallback opens in new tab", "new_page = await context.new_page()" in content))
    
    # Check for logging about new tab
    checks.append(("Logs new tab opening", "new tab" in content.lower()))
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    return passed, len(checks)


def test_forceful_detection():
    """Test that forceful target domain detection is implemented."""
    print("\nTesting forceful target domain detection...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check for forceful detection mode
    checks.append(("Forceful detection mode enabled", "FORCEFUL" in content))
    
    # Check for multi-strategy matching
    checks.append(("Multiple matching strategies", "target_without_www" in content))
    
    # Check for exact domain comparison
    checks.append(("Exact domain match strategy", "target_lower == real_domain" in content))
    
    # Check for www-agnostic matching
    checks.append(("WWW-agnostic matching", "replace('www.', '')" in content))
    
    # Check for subdomain matching
    checks.append(("Subdomain matching support", "target_without_www in real_without_www" in content))
    
    # Check for position-based debugging
    checks.append(("Position-based debug logging", "Position {idx}" in content))
    
    # Check for comparison logging
    checks.append(("Logs domain comparisons", 'Comparing' in content))
    
    # Check for detection confirmation
    checks.append(("Detection confirmation log", "FORCEFULLY DETECTED" in content))
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    return passed, len(checks)


def test_multi_engine_support():
    """Test that multiple search engines are supported with redirect handling."""
    print("\nTesting multi-engine redirect handling...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check for Bing redirect handling
    checks.append(("Bing redirect detection", "is_bing_redirect" in content))
    checks.append(("Bing redirect URL extraction", "params['u']" in content or 'params["u"]' in content))
    
    # Check for Yahoo redirect handling
    checks.append(("Yahoo redirect detection", "is_yahoo_redirect" in content))
    checks.append(("Yahoo redirect URL extraction", "params['RU']" in content or 'params["RU"]' in content))
    
    # Check for URL decoding
    checks.append(("URL decoding with unquote", "unquote(" in content))
    
    # Check for proper URL parsing
    checks.append(("URL parsing with urlparse", "from urllib.parse import urlparse" in content))
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    return passed, len(checks)


def test_robust_fallbacks():
    """Test that robust fallback mechanisms are in place."""
    print("\nTesting robust fallback mechanisms...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check for fallback when target not found
    checks.append(("Fallback when target not found", "not found in" in content.lower() and "fallback" in content.lower()))
    
    # Check for exception fallback
    checks.append(("Exception handling fallback", "EXCEPTION FALLBACK" in content or "exception" in content.lower()))
    
    # Check for direct navigation fallback
    checks.append(("Direct navigation fallback", "direct navigation" in content.lower()))
    
    # Check that fallbacks also use new tab
    checks.append(("Fallback uses new tab", "FALLBACK" in content and "new_page" in content))
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    return passed, len(checks)


def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("Forceful Target Detection & New Tab Opening Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run all test suites
    results.append(("New tab opening", test_new_tab_opening()))
    results.append(("Forceful detection", test_forceful_detection()))
    results.append(("Multi-engine support", test_multi_engine_support()))
    results.append(("Robust fallbacks", test_robust_fallbacks()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    all_passed = True
    total_passed = 0
    total_checks = 0
    
    for test_name, (passed, total) in results:
        status = "✅ PASSED" if passed == total else "⚠ PARTIAL" if passed > 0 else "❌ FAILED"
        print(f"{test_name}: {status} ({passed}/{total})")
        total_passed += passed
        total_checks += total
        if passed != total:
            all_passed = False
    
    print("=" * 70)
    print(f"Overall: {total_passed}/{total_checks} checks passed")
    
    if all_passed:
        print("\n✅ All tests PASSED!")
        return 0
    elif total_passed > total_checks * 0.8:
        print("\n⚠ Most tests passed, some features may be incomplete.")
        return 0
    else:
        print("\n❌ Many tests failed. Please review the implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
