#!/usr/bin/env python3
"""
Comprehensive test for all the changes made to advanced_bot.py
Tests user agents, platform changes, time units, and code structure.
"""

import ast
import sys

def test_user_agents():
    """Test USER_AGENTS dictionary changes."""
    print("\n=== Testing USER_AGENTS Changes ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Parse the USER_AGENTS section
    start_idx = content.find('USER_AGENTS = {')
    end_idx = content.find('\n}\n', start_idx) + 2
    user_agents_section = content[start_idx:end_idx]
    
    # Test 1: 'windows' key exists
    assert "'windows'" in user_agents_section, "windows key not found"
    print("✓ 'windows' key found in USER_AGENTS")
    
    # Test 2: 'android' key exists
    assert "'android'" in user_agents_section, "android key not found"
    print("✓ 'android' key found in USER_AGENTS")
    
    # Test 3: Old 'desktop' key removed
    assert "'desktop':" not in user_agents_section, "Old desktop key still present"
    print("✓ Old 'desktop' key removed")
    
    # Test 4: At least 5000 Windows user agents
    windows_agents_count = user_agents_section.count("'Mozilla/5.0 (Windows")
    assert windows_agents_count >= 5000, f"Not enough Windows user agents: {windows_agents_count}"
    print(f"✓ Windows user agents count: {windows_agents_count} (>= 5000)")
    
    return True

def test_platform_references():
    """Test platform references throughout code."""
    print("\n=== Testing Platform References ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Count 'windows' references (should be multiple)
    windows_count = content.count("'windows'")
    assert windows_count >= 5, f"Not enough 'windows' references: {windows_count}"
    print(f"✓ Found {windows_count} 'windows' platform references")
    
    # Verify 'Windows' in checkbox label
    assert '🖥 Windows' in content, "Windows checkbox label not found"
    print("✓ Windows checkbox label updated")
    
    return True

def test_time_units():
    """Test time unit changes from minutes to seconds."""
    print("\n=== Testing Time Unit Changes ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Test 1: Seconds labels present
    assert 'Stay Time (seconds)' in content, "Stay Time (seconds) label not found"
    print("✓ Stay Time (seconds) label found")
    
    assert 'Random Minimum (seconds)' in content, "Random Minimum (seconds) label not found"
    print("✓ Random Minimum (seconds) label found")
    
    assert 'Random Maximum (seconds)' in content, "Random Maximum (seconds) label not found"
    print("✓ Random Maximum (seconds) label found")
    
    # Test 2: No minute labels remaining in time inputs
    lines = content.split('\n')
    minute_labels = [i for i, line in enumerate(lines, 1) 
                     if '(minutes)' in line and 'stay' in line.lower()]
    assert len(minute_labels) == 0, f"Found minute labels at lines: {minute_labels}"
    print("✓ No minute labels found in stay time inputs")
    
    # Test 3: Verify range changes
    assert '.setRange(10, 3600)' in content, "Time range not updated to seconds"
    print("✓ Time ranges updated to (10, 3600) seconds")
    
    # Test 4: Verify suffix changes
    assert "' sec'" in content, "Seconds suffix not found"
    print("✓ Seconds suffix found")
    
    return True

def test_thread_concurrent_label():
    """Test THREAD/CONCURRENT label."""
    print("\n=== Testing THREAD/CONCURRENT Label ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    assert 'THREAD/CONCURRENT' in content, "THREAD/CONCURRENT label not found"
    print("✓ THREAD/CONCURRENT label found")
    
    # Should not have old label
    assert 'Number of Profiles to Open:' not in content, "Old label still present"
    print("✓ Old 'Number of Profiles to Open' label removed")
    
    return True

def test_ad_interaction_removed():
    """Test that ad interaction feature is completely removed."""
    print("\n=== Testing Ad Interaction Removal ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Should have no ad_interaction references
    ad_count = content.count('ad_interaction')
    assert ad_count == 0, f"Found {ad_count} ad_interaction references"
    print("✓ All ad_interaction references removed")
    
    # Should not have Ad Interaction group box
    assert 'Ad Interaction (Demo/Test Only)' not in content, "Ad Interaction group box still present"
    print("✓ Ad Interaction UI group removed")
    
    return True

def test_rpa_mode_enhancements():
    """Test RPA mode enhancements."""
    print("\n=== Testing RPA Mode Enhancements ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Test for thread maintenance
    assert 'thread maintenance' in content.lower(), "Thread maintenance not found"
    print("✓ Thread maintenance logic added")
    
    # Test for proxy fallback
    assert 'proxy failure' in content.lower() or 'proxy failed' in content.lower(), "Proxy fallback not found"
    print("✓ Proxy fallback logic added")
    
    # Test for visible browser forcing
    assert 'Always visible for RPA mode' in content or 'visible browser' in content.lower(), "Visible browser forcing not clear"
    print("✓ Visible browser support added")
    
    return True

def test_search_visit_improvements():
    """Test Search Visit improvements."""
    print("\n=== Testing Search Visit Improvements ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find handle_search_visit function
    assert 'async def handle_search_visit' in content, "handle_search_visit function not found"
    
    # Check for longer timeout
    assert 'timeout=60000' in content, "60 second timeout not found"
    print("✓ Extended timeout to 60 seconds")
    
    # Check for improved waiting
    search_visit_start = content.find('async def handle_search_visit')
    search_visit_section = content[search_visit_start:search_visit_start + 5000]
    assert 'wait_for_selector' in search_visit_section, "wait_for_selector not found"
    print("✓ Added better element waiting")
    
    return True

def test_syntax():
    """Test Python syntax is valid."""
    print("\n=== Testing Python Syntax ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    try:
        ast.parse(content)
        print("✓ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("COMPREHENSIVE TEST SUITE FOR ADVANCED-BOT CHANGES")
    print("="*60)
    
    tests = [
        test_syntax,
        test_user_agents,
        test_platform_references,
        test_time_units,
        test_thread_concurrent_label,
        test_ad_interaction_removed,
        test_rpa_mode_enhancements,
        test_search_visit_improvements,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} FAILED")
        except AssertionError as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} ERROR: {e}")
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
