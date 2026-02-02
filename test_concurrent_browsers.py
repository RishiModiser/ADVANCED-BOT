#!/usr/bin/env python3
"""
Test for concurrent browser and imported useragents features.
Tests the specific changes requested for RPA mode.
"""

import sys

def test_concurrent_label_changed():
    """Test that THREAD label has been changed to Concurrent."""
    print("\n=== Testing THREAD → Concurrent Label Change ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Should have Concurrent label
    assert "QLabel('Concurrent:')" in content, "Concurrent label not found"
    print("✓ Label changed from 'THREAD:' to 'Concurrent:'")
    
    # Should not have old THREAD label
    assert "QLabel('THREAD:')" not in content, "Old THREAD label still present"
    print("✓ Old 'THREAD:' label removed")
    
    return True

def test_concurrent_browser_loop():
    """Test that concurrent browsers run in continuous loop."""
    print("\n=== Testing Concurrent Browser Continuous Loop ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find the run_rpa_mode function
    rpa_mode_start = content.find('async def run_rpa_mode(self):')
    rpa_mode_end = content.find('async def run_normal_mode(self):', rpa_mode_start)
    rpa_mode_section = content[rpa_mode_start:rpa_mode_end]
    
    # Test 1: Should have continuous loop (while self.running)
    assert 'while self.running:' in rpa_mode_section, "Continuous loop not found"
    print("✓ Continuous loop implemented (while self.running)")
    
    # Test 2: Should NOT have max_retries limiting the loop
    assert 'while self.running and retry_count < max_retries:' not in rpa_mode_section, "Old retry-limited loop still present"
    print("✓ Removed retry-limited loop")
    
    # Test 3: Should have auto-restart message
    assert 'auto-restart' in rpa_mode_section.lower() or 'automatically restart' in rpa_mode_section.lower(), "Auto-restart message not found"
    print("✓ Auto-restart message present")
    
    # Test 4: Should create all N concurrent browsers
    assert 'for i in range(num_concurrent)' in rpa_mode_section, "Loop to create N concurrent browsers not found"
    print("✓ Creates N concurrent browsers based on configuration")
    
    return True

def test_imported_useragents_logging():
    """Test that imported useragents are logged when loaded."""
    print("\n=== Testing Imported Useragents Logging ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find the run_rpa_mode function
    rpa_mode_start = content.find('async def run_rpa_mode(self):')
    rpa_mode_end = content.find('async def run_normal_mode(self):', rpa_mode_start)
    rpa_mode_section = content[rpa_mode_start:rpa_mode_end]
    
    # Should check and log imported useragents
    assert 'imported_useragents' in rpa_mode_section, "Imported useragents check not found"
    print("✓ Imported useragents check present")
    
    assert 'useragents loaded' in rpa_mode_section.lower() or 'user agents available' in rpa_mode_section.lower(), "Useragents logging not found"
    print("✓ Imported useragents logging message present")
    
    return True

def test_browser_manager_useragents():
    """Test that BrowserManager has imported_useragents attribute."""
    print("\n=== Testing BrowserManager Imported Useragents ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find the BrowserManager class
    browser_manager_start = content.find('class BrowserManager:')
    browser_manager_section = content[browser_manager_start:browser_manager_start + 5000]
    
    # Should have imported_useragents attribute
    assert 'self.imported_useragents = []' in browser_manager_section, "imported_useragents attribute not found"
    print("✓ BrowserManager has imported_useragents attribute")
    
    # Find create_context method
    create_context_start = content.find('async def create_context', browser_manager_start)
    create_context_section = content[create_context_start:create_context_start + 3000]
    
    # Should use imported useragents if available
    assert 'if self.imported_useragents' in create_context_section, "Imported useragents usage not found"
    print("✓ create_context uses imported useragents when available")
    
    return True

def test_concurrent_terminology():
    """Test that 'Thread' is replaced with 'Concurrent' in logs."""
    print("\n=== Testing Concurrent Terminology ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find the run_rpa_mode function
    rpa_mode_start = content.find('async def run_rpa_mode(self):')
    rpa_mode_end = content.find('async def run_normal_mode(self):', rpa_mode_start)
    rpa_mode_section = content[rpa_mode_start:rpa_mode_end]
    
    # Should use 'Concurrent' in log messages
    # We expect at least 3 different log messages using 'Concurrent' terminology
    MIN_EXPECTED_CONCURRENT_LOGS = 3
    concurrent_count = rpa_mode_section.count('[Concurrent ')
    assert concurrent_count >= MIN_EXPECTED_CONCURRENT_LOGS, f"Not enough 'Concurrent' log messages: {concurrent_count}"
    print(f"✓ Found {concurrent_count} log messages using 'Concurrent' terminology")
    
    # Should not use old '[Thread ' terminology in RPA mode
    old_thread_count = rpa_mode_section.count('[Thread ')
    assert old_thread_count == 0, f"Old '[Thread ' terminology still present: {old_thread_count}"
    print("✓ Old '[Thread ' terminology removed from RPA mode")
    
    return True

def test_small_delay_between_starts():
    """Test that there's a small delay between browser starts to avoid resource contention."""
    print("\n=== Testing Browser Start Delays ===")
    
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find the run_rpa_mode function
    rpa_mode_start = content.find('async def run_rpa_mode(self):')
    rpa_mode_end = content.find('async def run_normal_mode(self):', rpa_mode_start)
    rpa_mode_section = content[rpa_mode_start:rpa_mode_end]
    
    # Should have delay between browser starts
    assert 'await asyncio.sleep(0.5)' in rpa_mode_section or 'await asyncio.sleep(1)' in rpa_mode_section, "Delay between starts not found"
    print("✓ Small delay added between browser starts")
    
    return True

def main():
    """Run all tests."""
    print("="*60)
    print("TEST SUITE FOR CONCURRENT BROWSERS & USERAGENTS")
    print("="*60)
    
    tests = [
        test_concurrent_label_changed,
        test_concurrent_browser_loop,
        test_imported_useragents_logging,
        test_browser_manager_useragents,
        test_concurrent_terminology,
        test_small_delay_between_starts,
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
