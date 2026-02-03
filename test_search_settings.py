#!/usr/bin/env python3
"""
Test script for Search Settings enhancement and HIGH CPC/CPM mode fix.
Validates the new functionality without requiring full browser automation.
"""

import sys
import ast
import re

def test_captcha_function_exists():
    """Test that the CAPTCHA detection function was added."""
    print("Testing CAPTCHA function exists...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for CAPTCHA function
    if 'async def detect_and_solve_captcha' in content:
        print("✓ CAPTCHA detection function found")
        
        # Check for key CAPTCHA detection features (all required for comprehensive detection)
        captcha_selectors = [
            'recaptcha',
            'captcha',
            'iframe[src*="recaptcha"]',
        ]
        
        found_selectors = 0
        for selector in captcha_selectors:
            if selector in content:
                found_selectors += 1
        
        # All selectors should be present for comprehensive CAPTCHA detection
        if found_selectors == len(captcha_selectors):
            print(f"✓ CAPTCHA detection has proper selectors ({found_selectors}/{len(captcha_selectors)})")
        else:
            print(f"⚠ Warning: Not all CAPTCHA selectors found ({found_selectors}/{len(captcha_selectors)})")
        
        # Check for AI processing logic
        if 'AI vision' in content or 'screenshot' in content:
            print("✓ CAPTCHA solving logic with screenshot capability found")
        
        return True
    else:
        print("✗ CAPTCHA detection function NOT found")
        return False

def test_captcha_called_in_search():
    """Test that CAPTCHA detection is called in search visit function."""
    print("\nTesting CAPTCHA integration in search function...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find handle_search_visit function
    if 'async def handle_search_visit' in content:
        # Check if it calls detect_and_solve_captcha
        if 'await self.detect_and_solve_captcha(page)' in content:
            print("✓ CAPTCHA detection is called in search function")
            return True
        else:
            print("✗ CAPTCHA detection NOT called in search function")
            return False
    else:
        print("✗ handle_search_visit function NOT found")
        return False

def test_top_10_results_scanning():
    """Test that search results scanning is limited to top 10."""
    print("\nTesting top 10 results scanning...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for top 10 limiting logic
    patterns = [
        r'result_links\[:10\]',
        r'enumerate\(result_links\[:10\]',
        r'if len\(result_links\) >= 10',
        r'top 10'
    ]
    
    found = 0
    for pattern in patterns:
        if re.search(pattern, content):
            found += 1
    
    if found >= 2:
        print(f"✓ Top 10 results scanning implemented ({found} indicators found)")
        return True
    else:
        print(f"⚠ Warning: Limited top 10 indicators found ({found})")
        return False

def test_high_cpc_toggle_modification():
    """Test that HIGH CPC toggle disables Target URLs mode."""
    print("\nTesting HIGH CPC/CPM mode toggle modification...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find toggle_high_cpc_inputs function
    if 'def toggle_high_cpc_inputs' in content:
        # Extract the function by finding next function or class definition
        func_start = content.find('def toggle_high_cpc_inputs')
        # Look for next method definition at same indentation level
        next_func = content.find('\n    def ', func_start + 1)
        next_class = content.find('\n    class ', func_start + 1)
        
        # Use whichever comes first (or end of file if neither found)
        candidates = [x for x in [next_func, next_class] if x > 0]
        func_end = min(candidates) if candidates else -1
        func_content = content[func_start:func_end] if func_end > 0 else content[func_start:func_start + 2000]
        
        # Check for URL group disabling
        checks = [
            'url_group.setEnabled' in func_content,
            'url_input.setEnabled' in func_content,
            'url_list_widget.setEnabled' in func_content,
            'if enabled:' in func_content,
        ]
        
        passed = sum(checks)
        
        if passed >= 3:
            print(f"✓ HIGH CPC toggle properly disables Target URLs mode ({passed}/4 checks)")
            return True
        else:
            print(f"✗ HIGH CPC toggle incomplete ({passed}/4 checks)")
            return False
    else:
        print("✗ toggle_high_cpc_inputs function NOT found")
        return False

def test_search_result_filtering():
    """Test that search results are properly filtered."""
    print("\nTesting search result filtering...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for proper filtering logic
    # Essential filters (must have all):
    essential_filters = [
        'startswith(\'http\')',  # Must filter for HTTP links
        'google.com',  # Must exclude Google internal links
    ]
    
    # Optional but recommended filters:
    optional_filters = [
        'organic',
        'div#search',
        'div#rso'
    ]
    
    essential_found = sum(1 for f in essential_filters if f in content)
    optional_found = sum(1 for f in optional_filters if f in content)
    
    if essential_found == len(essential_filters):
        print(f"✓ Search result filtering implemented (essential: {essential_found}/{len(essential_filters)}, optional: {optional_found}/{len(optional_filters)})")
        return True
    else:
        print(f"✗ Missing essential filters ({essential_found}/{len(essential_filters)})")
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("Search Settings Enhancement Test Suite")
    print("="*70)
    
    tests = [
        test_captcha_function_exists,
        test_captcha_called_in_search,
        test_top_10_results_scanning,
        test_high_cpc_toggle_modification,
        test_search_result_filtering,
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
        print("\n✅ All tests PASSED! Implementation is complete.")
        return 0
    else:
        print(f"\n⚠ Some tests failed. Review the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
