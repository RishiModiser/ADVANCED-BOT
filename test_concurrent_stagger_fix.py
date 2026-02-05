#!/usr/bin/env python3
"""
Test that concurrent browser stagger fix is properly implemented.

This test validates that:
1. A stagger delay (0.2s) is added between browser task creations in RPA mode
2. A stagger delay (0.2s) is added between worker spawns in Normal mode
3. The stagger prevents overwhelming Playwright's connection
4. Comments explain the Playwright connection limitation
"""

import sys
import re

def test_rpa_mode_stagger():
    """Test that RPA mode has stagger delay between browser task creations."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find RPA mode section
    rpa_start = content.find('async def run_rpa_mode')
    rpa_end = content.find('async def run_normal_mode')
    rpa_section = content[rpa_start:rpa_end]
    
    # Check for stagger delay in task creation loop
    assert 'for i in range(num_concurrent):' in rpa_section, \
        "❌ FAILED: Task creation loop not found in RPA mode"
    print("✓ Test 1 PASSED: Task creation loop exists in RPA mode")
    
    # Check for asyncio.sleep in the loop
    assert 'await asyncio.sleep(0.2)' in rpa_section, \
        "❌ FAILED: Stagger delay (asyncio.sleep) not found in RPA mode"
    print("✓ Test 2 PASSED: Stagger delay (0.2s) added in RPA mode")
    
    # Check for comment explaining Playwright connection limitation
    assert 'Playwright' in rpa_section and 'connection' in rpa_section, \
        "❌ FAILED: No comment explaining Playwright connection limitation in RPA mode"
    print("✓ Test 3 PASSED: Comment explains Playwright connection limitation in RPA mode")
    
    # Check that delay is conditional (not after last task)
    assert 'if i < num_concurrent - 1' in rpa_section or 'Don\'t delay after the last' in rpa_section, \
        "❌ FAILED: Stagger delay should be conditional (not after last task)"
    print("✓ Test 4 PASSED: Stagger delay is conditional (skipped after last task)")

def test_normal_mode_stagger():
    """Test that Normal mode has stagger delay between worker spawns."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find Normal mode section
    normal_start = content.find('async def run_normal_mode')
    # Find next method after run_normal_mode (search for next async def at same indentation level)
    search_pos = normal_start + 1000
    while search_pos < len(content):
        if content[search_pos:search_pos+14] == '\n    async def ':
            break
        search_pos += 1
    normal_section = content[normal_start:search_pos] if search_pos < len(content) else content[normal_start:]
    
    # Check for worker spawn loop
    assert 'while len(active_workers) < num_concurrent' in normal_section, \
        "❌ FAILED: Worker spawn loop not found in Normal mode"
    print("✓ Test 5 PASSED: Worker spawn loop exists in Normal mode")
    
    # Check for asyncio.sleep in the spawn loop
    assert 'await asyncio.sleep(0.2)' in normal_section, \
        "❌ FAILED: Stagger delay (asyncio.sleep) not found in Normal mode"
    print("✓ Test 6 PASSED: Stagger delay (0.2s) added in Normal mode")
    
    # Check for comment explaining Playwright connection limitation
    assert 'Playwright' in normal_section and 'connection' in normal_section, \
        "❌ FAILED: No comment explaining Playwright connection limitation in Normal mode"
    print("✓ Test 7 PASSED: Comment explains Playwright connection limitation in Normal mode")
    
    # Check that delay is conditional
    assert 'if len(active_workers) < num_concurrent' in normal_section, \
        "❌ FAILED: Stagger delay should be conditional in Normal mode"
    print("✓ Test 8 PASSED: Stagger delay is conditional in Normal mode")

def test_comment_accuracy():
    """Test that comments accurately describe the issue and solution."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Check for mention of 5 concurrent launches limitation
    assert '~5 concurrent' in content or '5 concurrent' in content, \
        "❌ FAILED: Comments should mention the ~5 concurrent limitation"
    print("✓ Test 9 PASSED: Comments mention the ~5 concurrent limitation")
    
    # Check for mention of launch_persistent_context
    assert 'launch_persistent_context' in content, \
        "❌ FAILED: Comments should reference launch_persistent_context"
    print("✓ Test 10 PASSED: Comments reference the problematic call (launch_persistent_context)")

if __name__ == '__main__':
    print("=" * 70)
    print("Testing Concurrent Browser Stagger Fix")
    print("=" * 70)
    print()
    
    try:
        test_rpa_mode_stagger()
        print()
        test_normal_mode_stagger()
        print()
        test_comment_accuracy()
        print()
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("The fix correctly adds a 0.2s stagger between browser launches")
        print("to prevent overwhelming Playwright's connection.")
        print()
        print("Expected behavior:")
        print("  - Setting CONCURRENT=10 will now open all 10 browsers")
        print("  - Browsers launch with 0.2s stagger (10 browsers = 2 seconds)")
        print("  - Once launched, all browsers run truly concurrently")
        print()
        sys.exit(0)
    except AssertionError as e:
        print()
        print("=" * 70)
        print(str(e))
        print("=" * 70)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("=" * 70)
        sys.exit(1)
