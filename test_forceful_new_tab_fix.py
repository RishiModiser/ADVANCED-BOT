#!/usr/bin/env python3
"""
Test script for forceful new tab fix for DuckDuckGo, Yandex, and Baidu.
Validates that these search engines forcefully create new tabs instead of relying on Ctrl+Click.
"""

import sys
import re


def test_forceful_new_tab_for_problematic_engines():
    """Test that DuckDuckGo, Yandex, and Baidu use forceful new tab creation."""
    print("Testing forceful new tab fix for DuckDuckGo, Yandex, and Baidu...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: force_direct_method variable exists
    if 'force_direct_method' in content:
        checks.append("✓ force_direct_method variable exists")
    else:
        checks.append("✗ force_direct_method variable not found")
    
    # Check 2: DuckDuckGo is in the force list
    if re.search(r"search_engine in \[.*['\"]DuckDuckGo['\"]", content):
        checks.append("✓ DuckDuckGo is in forceful new tab list")
    else:
        checks.append("✗ DuckDuckGo not in force list")
    
    # Check 3: Yandex is in the force list
    if re.search(r"search_engine in \[.*['\"]Yandex['\"]", content):
        checks.append("✓ Yandex is in forceful new tab list")
    else:
        checks.append("✗ Yandex not in force list")
    
    # Check 4: Baidu is in the force list
    if re.search(r"search_engine in \[.*['\"]Baidu['\"]", content):
        checks.append("✓ Baidu is in forceful new tab list")
    else:
        checks.append("✗ Baidu not in force list")
    
    # Check 5: Forced method creates new page directly
    if re.search(r"if force_direct_method:.*new_page = await context\.new_page\(\)", content, re.DOTALL):
        checks.append("✓ Forced method creates new page directly")
    else:
        checks.append("✗ Forced method doesn't create new page")
    
    # Check 6: Forced method logs FORCEFUL message
    if re.search(r"\[FORCEFUL\].*Using direct new tab method", content):
        checks.append("✓ Logs FORCEFUL new tab creation")
    else:
        checks.append("✗ No FORCEFUL logging")
    
    # Check 7: Forced method closes old search page
    if re.search(r"if force_direct_method:.*await page\.close\(\)", content, re.DOTALL):
        checks.append("✓ Forced method closes old search page")
    else:
        checks.append("✗ Forced method doesn't close old page")
    
    # Check 8: Forced method returns new page (not old page)
    if re.search(r"if force_direct_method:.*return new_page", content, re.DOTALL):
        checks.append("✓ Forced method returns new page")
    else:
        checks.append("✗ Forced method doesn't return new page")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def test_fallback_for_failed_ctrl_click():
    """Test that even for other engines, if Ctrl+Click fails to create tab, force new tab."""
    print("\nTesting fallback when Ctrl+Click doesn't create new tab...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Check if len(all_pages) condition exists
    if re.search(r"if len\(all_pages\) > 1:", content):
        checks.append("✓ Checks if new tab was created")
    else:
        checks.append("✗ Doesn't check for new tab creation")
    
    # Check 2: In the else block (when tab NOT created), should force create new tab
    # Look for pattern: else: ... new_page = await context.new_page()
    if re.search(r"else:.*\[FORCEFUL\].*Ctrl\+Click did not create new tab", content, re.DOTALL):
        checks.append("✓ Detects when Ctrl+Click fails to create tab")
    else:
        checks.append("✗ Doesn't detect Ctrl+Click failure")
    
    # Check 3: Should create new page in fallback
    if re.search(r"else:.*new_page = await context\.new_page\(\).*await new_page\.goto", content, re.DOTALL):
        checks.append("✓ Fallback creates new page when Ctrl+Click fails")
    else:
        checks.append("✗ Fallback doesn't create new page")
    
    # Check 4: Should close old search page in fallback
    if re.search(r"else:.*await page\.close\(\)", content, re.DOTALL):
        checks.append("✓ Fallback closes old search page")
    else:
        checks.append("✗ Fallback doesn't close old page")
    
    # Check 5: Should return new_page (not old page) in fallback
    if re.search(r"else:.*return new_page", content, re.DOTALL):
        checks.append("✓ Fallback returns new page (not old search page)")
    else:
        checks.append("✗ Fallback returns old page")
    
    # Check 6: OLD BUG - should NOT return old 'page' object when tab not created
    # This was the bug: else: ... return page (returning old search results page)
    if re.search(r"else:.*# If new tab didn't open, treat it as same-tab navigation.*return page", content, re.DOTALL):
        checks.append("✗ BUG STILL EXISTS: Returns old search page when tab not created")
    else:
        checks.append("✓ BUG FIXED: Does not return old search page")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def test_no_removed_functionality():
    """Test that existing functionality is preserved."""
    print("\nTesting that existing functionality is preserved...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Ctrl+Click still exists for engines that need it
    if re.search(r"await found_link\.click\(modifiers=\['Control'\]\)", content):
        checks.append("✓ Ctrl+Click method still exists for compatible engines")
    else:
        checks.append("✗ Ctrl+Click method removed")
    
    # Check 2: Consent handling still exists
    if re.search(r"ConsentManager.*handle_consents", content, re.DOTALL):
        checks.append("✓ Consent handling preserved")
    else:
        checks.append("✗ Consent handling removed")
    
    # Check 3: New page closing old page still happens
    if re.search(r"await page\.close\(\).*return new_page", content, re.DOTALL):
        checks.append("✓ Old search page is closed before returning new page")
    else:
        checks.append("✗ Old search page not closed properly")
    
    # Check 4: handle_search_visit function still exists
    if 'async def handle_search_visit' in content:
        checks.append("✓ handle_search_visit function exists")
    else:
        checks.append("✗ handle_search_visit function missing")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def main():
    print("=" * 70)
    print("Forceful New Tab Fix Test Suite")
    print("For DuckDuckGo, Yandex, and Baidu Search Engines")
    print("=" * 70)
    
    results = []
    
    # Run tests
    passed, score, total = test_forceful_new_tab_for_problematic_engines()
    results.append(("Forceful new tab for DuckDuckGo/Yandex/Baidu", passed, score, total))
    
    passed, score, total = test_fallback_for_failed_ctrl_click()
    results.append(("Fallback when Ctrl+Click fails", passed, score, total))
    
    passed, score, total = test_no_removed_functionality()
    results.append(("Existing functionality preserved", passed, score, total))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    all_passed = True
    total_score = 0
    total_checks = 0
    for name, passed, score, total in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status} ({score}/{total})")
        total_score += score
        total_checks += total
        if not passed:
            all_passed = False
    
    print("=" * 70)
    print(f"Overall Score: {total_score}/{total_checks} checks passed")
    print("=" * 70)
    
    if all_passed:
        print("\n✅ All tests PASSED! Forceful new tab fix is complete.")
        print("DuckDuckGo, Yandex, and Baidu will now properly open target domains in new tabs.")
        return 0
    else:
        print(f"\n❌ Some tests FAILED ({total_score}/{total_checks} passed). Please review the implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
