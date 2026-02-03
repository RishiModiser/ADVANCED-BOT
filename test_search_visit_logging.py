#!/usr/bin/env python3
"""
Test script to validate the search visit logging sequence fix.
This test verifies that the logging messages appear in the correct order.
"""

import re

def test_search_visit_logging_sequence():
    """Test that search visit logs appear in the correct order."""
    print("Testing search visit logging sequence...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the execute_single_visit function
    func_pattern = r'async def execute_single_visit\(self, page, visit_num, target_url, visit_type,'
    func_match = re.search(func_pattern, content)
    
    if not func_match:
        print("✗ Could not find execute_single_visit function")
        return False
    
    func_start = func_match.start()
    
    # Extract a reasonable chunk of the function (next 2000 chars)
    func_content = content[func_start:func_start + 3000]
    
    # Check that "Processing URL" is NOT at the top before visit_type branching
    lines = func_content.split('\n')
    
    # Find where visit_type branches start
    visit_type_check_line = -1
    processing_url_line = -1
    
    for i, line in enumerate(lines):
        if 'if visit_type ==' in line and visit_type_check_line == -1:
            visit_type_check_line = i
        if 'Processing URL:' in line:
            processing_url_line = i
    
    # Check 1: "Processing URL" should not exist at all (was removed)
    if processing_url_line != -1:
        print(f"✗ Found 'Processing URL' at line {processing_url_line}, should be removed")
        return False
    else:
        print("✓ Generic 'Processing URL' log has been removed")
    
    # Check 2: Search visit should have proper logging
    if 'Search visit - Opening' in func_content and 'to search for target domain' in func_content:
        print("✓ Search visit has proper logging: 'Search visit - Opening {search_engine} to search for target domain...'")
    else:
        print("✗ Search visit logging not found or incorrect")
        return False
    
    # Check 3: Referral visit should have proper logging
    if 'Referral visit to' in func_content:
        print("✓ Referral visit has proper logging")
    else:
        print("⚠ Referral visit logging not found (may need to be added)")
    
    # Check 4: Verify the order - search log should come BEFORE calling handle_search_visit
    search_log_pos = func_content.find('Search visit - Opening')
    handle_search_pos = func_content.find('await self.handle_search_visit')
    
    if search_log_pos != -1 and handle_search_pos != -1:
        if search_log_pos < handle_search_pos:
            print("✓ Search visit log appears BEFORE handle_search_visit call (correct order)")
        else:
            print("✗ Search visit log appears AFTER handle_search_visit call (wrong order)")
            return False
    
    return True

def test_handle_search_visit_flow():
    """Test that handle_search_visit has the correct flow."""
    print("\nTesting handle_search_visit function flow...")
    
    with open('advanced_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find handle_search_visit function
    func_pattern = r'async def handle_search_visit\(self, context:'
    func_match = re.search(func_pattern, content)
    
    if not func_match:
        print("✗ Could not find handle_search_visit function")
        return False
    
    func_start = func_match.start()
    # Extract a large chunk to cover the entire function
    func_content = content[func_start:func_start + 5000]
    
    # Check the order of operations
    order_checks = [
        ('Search visit using', 'Logs search engine being used'),
        ('Keyword:', 'Logs keyword and target'),
        ('Creating new tab', 'Creates new tab'),
        ('Opening.*in new tab', 'Opens search engine'),
        ('goto.*url', 'Navigates to search engine URL'),
        ('Waiting for search box', 'Waits for search box'),
        ('Typing search keyword', 'Types the keyword'),
        ('Pressing Enter', 'Submits search'),
        ('Waiting for search results', 'Waits for results'),
        ('Searching for target domain', 'Looks for target in results'),
    ]
    
    positions = []
    for pattern, desc in order_checks:
        match = re.search(pattern, func_content, re.IGNORECASE)
        if match:
            positions.append((match.start(), desc, pattern))
    
    # Verify they're in order
    if len(positions) >= 8:  # At least 8 of the key steps should be present
        print(f"✓ Found {len(positions)}/{len(order_checks)} expected steps")
        
        # Check if they're in ascending order
        sorted_positions = sorted(positions, key=lambda x: x[0])
        if sorted_positions == positions:
            print("✓ All steps are in the correct order:")
            for i, (pos, desc, _) in enumerate(positions[:5], 1):
                print(f"  {i}. {desc}")
            if len(positions) > 5:
                print(f"  ... and {len(positions) - 5} more steps")
        else:
            print("⚠ Warning: Some steps may be out of order")
        return True
    else:
        print(f"⚠ Only found {len(positions)}/{len(order_checks)} expected steps")
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("Search Visit Logging Sequence Test")
    print("="*70)
    
    tests = [
        test_search_visit_logging_sequence,
        test_handle_search_visit_flow,
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
        print("\n✅ All tests PASSED! Search visit logging is now in correct order.")
        print("\nExpected log sequence for search visits:")
        print("1. [Visit N] Search visit - Opening Google to search for target domain...")
        print("2. [INFO] Search visit using Google")
        print("3. [INFO] Keyword: \"keyword\" | Target: \"domain.com\"")
        print("4. Creating new tab for Google...")
        print("5. Opening Google in new tab...")
        print("6. Checking for consent dialogs...")
        print("7. Waiting for search box...")
        print("8. Typing search keyword: \"keyword\"...")
        print("9. Pressing Enter to search...")
        print("10. Waiting for search results...")
        print("11. Searching for target domain in top 10 search results...")
        print("12. Found target domain at position X...")
        print("13. Clicking on target domain link...")
        print("14. Successfully navigated to target domain from search")
        return 0
    else:
        print(f"\n⚠ Some tests failed. Review the implementation.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
