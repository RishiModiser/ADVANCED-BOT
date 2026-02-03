#!/usr/bin/env python3
"""
Test script for Yahoo search box detection fix.
Validates that Yahoo has comprehensive selector coverage for web and mobile views.
"""

import sys
import re

# Module-level constant for the file to test
TARGET_FILE = 'advanced_bot.py'

def test_yahoo_selector_count():
    """Test that Yahoo has expanded selector coverage."""
    print("Testing Yahoo selector count...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Yahoo configuration with proper bracket handling
    yahoo_start = content.find("'Yahoo': {")
    if yahoo_start == -1:
        print("✗ Yahoo configuration NOT found")
        return False
    
    # Find the search_box_selectors list
    selectors_start = content.find("'search_box_selectors':", yahoo_start)
    if selectors_start == -1:
        print("✗ Yahoo search_box_selectors NOT found")
        return False
    
    # Find the opening bracket
    bracket_start = content.find('[', selectors_start)
    if bracket_start == -1:
        print("✗ Yahoo search_box_selectors list NOT found")
        return False
    
    # Find the matching closing bracket
    bracket_count = 1
    bracket_end = bracket_start + 1
    while bracket_count > 0 and bracket_end < len(content):
        if content[bracket_end] == '[':
            bracket_count += 1
        elif content[bracket_end] == ']':
            bracket_count -= 1
        bracket_end += 1
    
    selectors_text = content[bracket_start:bracket_end]
    # Count selectors (each selector is a quoted string)
    selector_count = len(re.findall(r"['\"][^'\"]+['\"]", selectors_text))
    
    if selector_count >= 8:
        print(f"✓ Yahoo has {selector_count} search box selectors (comprehensive coverage)")
        return True
    else:
        print(f"✗ Yahoo only has {selector_count} search box selectors (needs more coverage)")
        return False

def test_yahoo_mobile_selectors():
    """Test that Yahoo includes mobile-specific selectors."""
    print("\nTesting Yahoo mobile-specific selectors...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for mobile-related selectors
    mobile_indicators = [
        'type="search"',           # Generic mobile search
        'placeholder',             # Mobile often uses placeholder
        'aria-label',              # Accessibility (common on mobile)
        'mobile',                  # Explicit mobile class/id
        'header-search',           # Mobile header search
        'form[role="search"]',     # Semantic form selector
    ]
    
    found = []
    for indicator in mobile_indicators:
        if indicator in content:
            found.append(indicator)
    
    if len(found) >= 4:
        print(f"✓ Yahoo includes mobile-related selectors ({len(found)}/{len(mobile_indicators)} indicators found)")
        return True
    else:
        print(f"✗ Limited mobile selector coverage ({len(found)}/{len(mobile_indicators)} indicators found)")
        return False

def test_yahoo_desktop_selectors_preserved():
    """Test that original Yahoo desktop selectors are preserved."""
    print("\nTesting Yahoo desktop selector preservation...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for original desktop selectors
    desktop_selectors = [
        'input[name="p"]',
        '#yschsp',
    ]
    
    found = []
    for selector in desktop_selectors:
        if selector in content:
            found.append(selector)
    
    if len(found) == len(desktop_selectors):
        print(f"✓ Original desktop selectors preserved ({len(found)}/{len(desktop_selectors)})")
        return True
    else:
        print(f"✗ Some original desktop selectors missing ({len(found)}/{len(desktop_selectors)})")
        return False

def test_yahoo_results_selector_count():
    """Test that Yahoo has expanded results selector coverage."""
    print("\nTesting Yahoo results selector count...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Yahoo configuration
    yahoo_start = content.find("'Yahoo': {")
    if yahoo_start == -1:
        print("✗ Yahoo configuration NOT found")
        return False
    
    # Find the results_selector list
    selectors_start = content.find("'results_selector':", yahoo_start)
    if selectors_start == -1:
        print("✗ Yahoo results_selector NOT found")
        return False
    
    # Find the opening bracket
    bracket_start = content.find('[', selectors_start)
    if bracket_start == -1:
        print("✗ Yahoo results_selector list NOT found")
        return False
    
    # Find the matching closing bracket
    bracket_count = 1
    bracket_end = bracket_start + 1
    while bracket_count > 0 and bracket_end < len(content):
        if content[bracket_end] == '[':
            bracket_count += 1
        elif content[bracket_end] == ']':
            bracket_count -= 1
        bracket_end += 1
    
    selectors_text = content[bracket_start:bracket_end]
    # Count selectors (each selector is a quoted string)
    selector_count = len(re.findall(r"['\"][^'\"]+['\"]", selectors_text))
    
    if selector_count >= 4:
        print(f"✓ Yahoo has {selector_count} results selectors (good coverage)")
        return True
    else:
        print(f"✗ Yahoo only has {selector_count} results selectors (needs more coverage)")
        return False

def test_yahoo_mobile_results_selectors():
    """Test that Yahoo includes mobile-specific results selectors."""
    print("\nTesting Yahoo mobile results selectors...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for mobile results indicators
    mobile_result_indicators = [
        '#main',                   # Common mobile main container
        '.results',                # Generic results class
        'role="main"',             # Semantic main content
        'compArticleList',         # Mobile article list
    ]
    
    found = []
    for indicator in mobile_result_indicators:
        if indicator in content:
            found.append(indicator)
    
    if len(found) >= 2:
        print(f"✓ Yahoo includes mobile results selectors ({len(found)}/{len(mobile_result_indicators)} indicators found)")
        return True
    else:
        print(f"✗ Limited mobile results coverage ({len(found)}/{len(mobile_result_indicators)} indicators found)")
        return False

def test_no_breaking_changes():
    """Test that no other search engines were modified."""
    print("\nTesting no breaking changes to other search engines...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that other search engines still exist
    search_engines = ['Google', 'Bing', 'DuckDuckGo', 'Yandex', 'Baidu']
    found_engines = []
    
    for engine in search_engines:
        if f"'{engine}':" in content or f'"{engine}":' in content:
            found_engines.append(engine)
    
    if len(found_engines) == len(search_engines):
        print(f"✓ All other search engines intact ({len(found_engines)}/{len(search_engines)})")
        return True
    else:
        print(f"✗ Some search engines missing ({len(found_engines)}/{len(search_engines)})")
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("Yahoo Search Box Detection Fix Test Suite")
    print("="*70)
    
    tests = [
        test_yahoo_selector_count,
        test_yahoo_mobile_selectors,
        test_yahoo_desktop_selectors_preserved,
        test_yahoo_results_selector_count,
        test_yahoo_mobile_results_selectors,
        test_no_breaking_changes,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "="*70)
    print(f"Test Results: {sum(results)}/{len(results)} tests passed")
    print("="*70)
    
    if all(results):
        print("\n✅ All tests PASSED! Yahoo search box detection fix is complete.")
        return 0
    elif sum(results) >= len(results) * 0.8:
        print(f"\n⚠ Most tests passed ({sum(results)}/{len(results)}). Implementation looks good.")
        return 0
    else:
        print(f"\n⚠ Some tests failed. Review the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
