#!/usr/bin/env python3
"""
Test Suite for Bing Search Engine Bug Fixes
- Bing search box detection with enhanced selectors
- Tab switching with bring_to_front() calls
- Scrolling on correct tab (target domain)
"""

import sys
import re


def test_bing_search_box_selectors():
    """Test that comprehensive Bing search box selectors are present."""
    print("Testing Bing search box selectors...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check for essential Bing selectors
    essential_selectors = [
        r'textarea\[name="q"\]',           # Textarea variant
        r'input\[name="q"\]',              # Input variant
        r'#sb_form_q',                     # Main ID
        r'input\[id="sb_form_q"\]',        # Input by ID
        r'textarea\[id="sb_form_q"\]',     # Textarea by ID
    ]
    
    for selector in essential_selectors:
        if re.search(selector, content):
            checks.append(f"✓ Selector found: {selector}")
        else:
            checks.append(f"✗ Selector missing: {selector}")
    
    # Check for additional Bing selectors
    additional_selectors = [
        r'aria-label.*Enter your search term',
        r'placeholder.*Search',
        r'#b_searchbox input',
        r'form#sb_form input',
    ]
    
    for selector in additional_selectors:
        if re.search(selector, content):
            checks.append(f"✓ Additional selector found: {selector[:40]}...")
        else:
            checks.append(f"✗ Additional selector missing: {selector[:40]}...")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def test_tab_switching_with_bring_to_front():
    """Test that bring_to_front() is called after opening new tabs."""
    print("\nTesting tab switching with bring_to_front()...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: bring_to_front() is used
    bring_to_front_matches = re.findall(r'await .*\.bring_to_front\(\)', content)
    if len(bring_to_front_matches) > 0:
        checks.append(f"✓ bring_to_front() is called {len(bring_to_front_matches)} times")
    else:
        checks.append("✗ bring_to_front() is not called")
    
    # Check 2: bring_to_front() after Ctrl+Click path
    # Find the section after "Get the last opened page (newly created tab)"
    ctrl_click_section = re.search(
        r'Get the last opened page.*?new_page = all_pages\[-1\].*?(await new_page\.bring_to_front\(\))',
        content,
        re.DOTALL
    )
    if ctrl_click_section:
        checks.append("✓ bring_to_front() called after Ctrl+Click success")
    else:
        checks.append("✗ bring_to_front() missing after Ctrl+Click success")
    
    # Check 3: bring_to_front() after direct new tab creation
    direct_tab_section = re.search(
        r'new_page = await context\.new_page\(\).*?await new_page\.goto.*?(await new_page\.bring_to_front\(\))',
        content,
        re.DOTALL
    )
    if direct_tab_section:
        checks.append("✓ bring_to_front() called after direct new tab creation")
    else:
        checks.append("✗ bring_to_front() missing after direct new tab creation")
    
    # Check 4: Logging for bring_to_front()
    if re.search(r"emit_log.*Brought.*tab.*front", content):
        checks.append("✓ Logging present for bring_to_front() calls")
    else:
        checks.append("✗ No logging for bring_to_front() calls")
    
    # Check 5: Error handling for bring_to_front()
    error_handling = re.search(
        r'try:.*?await .*\.bring_to_front\(\).*?except.*?focus_error',
        content,
        re.DOTALL
    )
    if error_handling:
        checks.append("✓ Error handling present for bring_to_front()")
    else:
        checks.append("✗ No error handling for bring_to_front()")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def test_proper_page_return():
    """Test that the correct page (target domain) is returned."""
    print("\nTesting proper page return from handle_search_visit...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Function returns new_page after closing search page
    return_pattern = re.search(
        r'await page\.close\(\).*?return new_page',
        content,
        re.DOTALL
    )
    if return_pattern:
        checks.append("✓ Returns new_page after closing search page")
    else:
        checks.append("✗ Does not properly return new_page")
    
    # Check 2: Search page is closed before returning
    close_before_return = len(re.findall(r'await page\.close\(\).*?return new_page', content, re.DOTALL))
    if close_before_return >= 3:  # Should be in multiple code paths
        checks.append(f"✓ Search page closed before return in {close_before_return} paths")
    else:
        checks.append(f"✗ Search page not consistently closed ({close_before_return} paths)")
    
    # Check 3: Caller uses returned page for further interactions
    caller_usage = re.search(
        r'search_page = await self\.handle_search_visit.*?page = search_page',
        content,
        re.DOTALL
    )
    if caller_usage:
        checks.append("✓ Caller properly uses returned page for interactions")
    else:
        checks.append("✗ Caller doesn't properly use returned page")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def test_bing_configuration():
    """Test that Bing configuration is properly structured."""
    print("\nTesting Bing search engine configuration...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Bing is in SEARCH_ENGINES
    if re.search(r"'Bing':\s*\{", content):
        checks.append("✓ Bing configuration exists in SEARCH_ENGINES")
    else:
        checks.append("✗ Bing configuration not found")
    
    # Check 2: Bing URL is correct
    if re.search(r"'url':\s*'https://www\.bing\.com'", content):
        checks.append("✓ Bing URL is correct")
    else:
        checks.append("✗ Bing URL is incorrect or missing")
    
    # Check 3: search_box_selectors is a list
    bing_config = re.search(r"'Bing':\s*\{.*?'search_box_selectors':\s*\[(.*?)\]", content, re.DOTALL)
    if bing_config:
        selectors = bing_config.group(1)
        # Count actual selector strings (look for quoted strings)
        selector_count = len(re.findall(r"['\"]([^'\"]+)['\"]", selectors))
        if selector_count >= 5:
            checks.append(f"✓ Bing has {selector_count} search box selectors")
        else:
            checks.append(f"✗ Bing has only {selector_count} search box selectors (need at least 5)")
    else:
        checks.append("✗ search_box_selectors not found for Bing")
    
    # Check 4: Results selectors present
    if re.search(r"'results_selector':\s*\['#b_results'", content):
        checks.append("✓ Bing results selector configured")
    else:
        checks.append("✗ Bing results selector missing")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("✗")]
    return len(failed) == 0, len(checks) - len(failed), len(checks)


def main():
    print("=" * 70)
    print("Bing Search Engine Bug Fixes Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run tests
    passed, score, total = test_bing_search_box_selectors()
    results.append(("Bing search box selectors", passed, score, total))
    
    passed, score, total = test_tab_switching_with_bring_to_front()
    results.append(("Tab switching with bring_to_front()", passed, score, total))
    
    passed, score, total = test_proper_page_return()
    results.append(("Proper page return", passed, score, total))
    
    passed, score, total = test_bing_configuration()
    results.append(("Bing configuration", passed, score, total))
    
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
    print(f"Overall Score: {total_score}/{total_checks}")
    print("=" * 70)
    
    if all_passed:
        print("\n✅ All tests PASSED! Bing search fixes are complete.")
        return 0
    else:
        print("\n❌ Some tests FAILED. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
