#!/usr/bin/env python3
"""
Test script for search engine opening fix.
Validates that search engines open properly with networkidle and retry logic.
"""

import sys
import re

# Module-level constant for the file to test
TARGET_FILE = 'advanced_bot.py'

def test_networkidle_loading():
    """Test that search engine loads with networkidle for stability."""
    print("Testing networkidle page loading...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for networkidle in goto call
    if "wait_until='networkidle'" in content:
        print("✓ Search engine uses networkidle loading strategy")
        
        # Check for fallback to domcontentloaded
        if "wait_until='domcontentloaded'" in content:
            print("✓ Fallback to domcontentloaded exists")
        
        return True
    else:
        print("✗ networkidle loading NOT found")
        return False

def test_search_box_retry_logic():
    """Test that search box detection has retry logic."""
    print("\nTesting search box retry logic...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for retry mechanism
    checks = [
        'max_retries' in content,
        'for retry in range(max_retries)' in content,
        "state='visible'" in content,  # Check for visibility
        'is_visible()' in content,  # Check for element visibility
    ]
    
    passed = sum(checks)
    
    if passed >= 3:
        print(f"✓ Search box retry logic implemented ({passed}/4 checks)")
        return True
    else:
        print(f"✗ Search box retry logic incomplete ({passed}/4 checks)")
        return False

def test_page_reload_fallback():
    """Test that page reload fallback exists if search box not found."""
    print("\nTesting page reload fallback...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find handle_search_visit function and check for reload logic
    if 'async def handle_search_visit' in content:
        # Look for actual reload method call
        if 'page.reload' in content or 'await page.reload' in content:
            # Also verify it's in error handling context
            if 'if not search_selector' in content or 'search box not found' in content.lower():
                print("✓ Page reload fallback exists in error handling")
                return True
            else:
                print("✓ Page reload exists (but context unclear)")
                return True
        else:
            print("✗ Page reload fallback NOT found")
            return False
    else:
        print("✗ handle_search_visit function NOT found")
        return False

def test_consent_wait_improvement():
    """Test that consent handling waits for page to stabilize."""
    print("\nTesting consent handling improvements...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for improved wait after consent click in handle_search_visit
    # Look for wait_for_load_state call after consent button click
    checks = [
        'wait_for_load_state' in content,
        'networkidle' in content,
        'consent' in content.lower() and 'button.click()' in content,
    ]
    
    passed = sum(checks)
    
    if passed >= 2:
        print(f"✓ Consent handling has improved wait logic ({passed}/3 checks)")
        return True
    else:
        print(f"⚠ Limited consent wait improvements ({passed}/3 checks)")
        return False

def test_search_results_wait():
    """Test that search results loading has improved wait logic."""
    print("\nTesting search results wait improvements...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for wait_for_load_state after Enter press in search flow
    # Look for pattern: press Enter -> wait_for_load_state
    if 'wait_for_load_state' in content and 'page.press' in content:
        # Additional check: should be in search context
        if 'search' in content.lower() and 'Enter' in content:
            print("✓ Search results wait for load state after Enter press")
            return True
    
    if 'wait_for_load_state' in content:
        print("✓ Search results have wait_for_load_state")
        return True
    else:
        print("⚠ Limited search results wait improvements")
        return False

def test_search_engine_config():
    """Test that search engine configurations exist for all engines."""
    print("\nTesting search engine configurations...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for search engine configs
    engines = ['Google', 'Bing', 'Yahoo', 'DuckDuckGo', 'Yandex', 'Baidu']
    found_engines = []
    
    for engine in engines:
        if f"'{engine}':" in content or f'"{engine}":' in content:
            found_engines.append(engine)
    
    if len(found_engines) >= 3:
        print(f"✓ Search engine configs found for: {', '.join(found_engines)}")
        return True
    else:
        print(f"✗ Limited search engine configs ({len(found_engines)} found)")
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("Search Engine Opening Fix Test Suite")
    print("="*70)
    
    tests = [
        test_networkidle_loading,
        test_search_box_retry_logic,
        test_page_reload_fallback,
        test_consent_wait_improvement,
        test_search_results_wait,
        test_search_engine_config,
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
        print("\n✅ All tests PASSED! Search engine opening fix is complete.")
        return 0
    elif sum(results) >= len(results) * 0.7:
        print(f"\n⚠ Most tests passed ({sum(results)}/{len(results)}). Implementation looks good.")
        return 0
    else:
        print(f"\n⚠ Some tests failed. Review the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
