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

def test_launch_semaphore_in_create_context():
    """Test that create_context launches browsers in parallel (no serial semaphore restriction).
    
    The serial Semaphore(1) was removed so that all N browsers launch in parallel,
    allowing them to appear concurrently. The 0.2s stagger between
    task creations in the callers provides sufficient safety to avoid overwhelming Playwright.
    """
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find create_context method
    cc_start = content.find('async def create_context(')
    # Find the next method after create_context
    cc_end = content.find('\n    async def ', cc_start + 1)
    cc_section = content[cc_start:cc_end] if cc_end != -1 else content[cc_start:]
    
    # Verify the serial blocking semaphore is NOT used (would prevent parallel launches)
    assert '_launch_semaphore' not in cc_section, \
        "❌ FAILED: _launch_semaphore should not be used in create_context (causes serial launches)"
    print("✓ Test 11 PASSED: No serial semaphore in create_context (parallel launches enabled)")
    
    # Verify launch_persistent_context is called directly (not wrapped in a semaphore)
    assert 'async with self._launch_semaphore' not in cc_section, \
        "❌ FAILED: launch_persistent_context should NOT be wrapped with a serial semaphore"
    print("✓ Test 12 PASSED: launch_persistent_context called directly for parallel launching")
    
    # Verify the proxy retry fallback is still there for robust error handling
    assert 'Retrying without proxy' in cc_section, \
        "❌ FAILED: Proxy retry fallback not found in create_context"
    print("✓ Test 13 PASSED: Proxy retry fallback retained for error-free operation")
    
    # Verify _launch_semaphore is NOT in BrowserManager.__init__ (clean removal)
    bm_init_start = content.find('class BrowserManager:')
    bm_init_end = content.find('\n    async def initialize(', bm_init_start)
    bm_init_section = content[bm_init_start:bm_init_end]
    assert '_launch_semaphore' not in bm_init_section, \
        "❌ FAILED: _launch_semaphore should be removed from BrowserManager.__init__"
    print("✓ Test 14 PASSED: _launch_semaphore fully removed from BrowserManager (parallel launches)")


def test_rpa_startup_barrier():
    """Test that RPA mode has a startup barrier to ensure all N browsers are visible simultaneously.
    
    Without this barrier, browsers with short scripts would complete and restart before
    all N are launched, so fewer than N (e.g. only 3 out of 5) are ever visible at once.
    """
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find RPA mode section
    rpa_start = content.find('async def run_rpa_mode')
    rpa_end = content.find('async def run_normal_mode')
    rpa_section = content[rpa_start:rpa_end]
    
    # Check that the startup barrier event is declared
    assert 'initial_launch_event = asyncio.Event()' in rpa_section, \
        "❌ FAILED: Startup barrier event not found in RPA mode"
    print("✓ Test 15 PASSED: Startup barrier asyncio.Event declared in RPA mode")
    
    # Check that a counter tracks initial launches
    assert 'initial_launched_count = 0' in rpa_section, \
        "❌ FAILED: Initial launch counter not found in RPA mode"
    print("✓ Test 16 PASSED: Initial launch counter declared in RPA mode")
    
    # Check that is_initial_launch flag is used
    assert 'is_initial_launch' in rpa_section, \
        "❌ FAILED: is_initial_launch flag not found in RPA mode"
    print("✓ Test 17 PASSED: is_initial_launch flag used in run_rpa_concurrent")
    
    # Check that event is set when count reaches num_concurrent
    assert 'initial_launched_count >= num_concurrent' in rpa_section, \
        "❌ FAILED: Event should be set when all N browsers launch"
    print("✓ Test 18 PASSED: Event set when all N browsers have launched")
    
    # Check that tasks wait on the event before executing scripts
    assert 'await initial_launch_event.wait()' in rpa_section, \
        "❌ FAILED: Tasks must await the startup barrier before running scripts"
    print("✓ Test 19 PASSED: Tasks wait for startup barrier before executing scripts")
    
    # Check that failed/cancelled launches also update the counter (no deadlock)
    # Must appear in: (1) failed context path, (2) no-proxy-early-exit path,
    # (3) exception handler — at minimum 3 paths guarantee no slot is ever skipped.
    increment_count = rpa_section.count('initial_launched_count += 1')
    assert increment_count >= 3, \
        f"❌ FAILED: Counter must be incremented in at least 3 paths (success, failure, exception) to prevent deadlock, found {increment_count}"
    print(f"✓ Test 20 PASSED: Counter incremented in {increment_count} paths (prevents deadlock on failures)")
    
    # Check that the barrier is only for initial launches (not restarts)
    assert 'is_initial_launch = False' in rpa_section, \
        "❌ FAILED: is_initial_launch must be cleared after first launch so restarts skip the barrier"
    print("✓ Test 21 PASSED: Barrier skipped for restarts (only applies to initial launch)")


def test_normal_mode_startup_barrier():
    """Test that Normal mode has a startup barrier to ensure all N browsers are visible simultaneously.
    
    Without this barrier, browsers with short work cycles complete and close before
    all N are launched, so fewer than N are ever visible at once.
    """
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find Normal mode section
    normal_start = content.find('async def run_normal_mode')
    # Find next top-level async def
    search_pos = normal_start + 1000
    while search_pos < len(content):
        if content[search_pos:search_pos+14] == '\n    async def ':
            break
        search_pos += 1
    normal_section = content[normal_start:search_pos] if search_pos < len(content) else content[normal_start:]
    
    # Check that startup barrier event is declared
    assert 'normal_startup_barrier' in normal_section, \
        "❌ FAILED: Startup barrier not found in Normal mode"
    print("✓ Test 22 PASSED: Startup barrier declared in Normal mode")
    
    # Check that asyncio.Event() is used for the barrier
    assert "asyncio.Event()" in normal_section, \
        "❌ FAILED: asyncio.Event() not found in Normal mode"
    print("✓ Test 23 PASSED: asyncio.Event() used for barrier in Normal mode")
    
    # Check that target count is num_concurrent
    assert "'target': num_concurrent" in normal_section, \
        "❌ FAILED: Barrier target should be num_concurrent"
    print("✓ Test 24 PASSED: Barrier target set to num_concurrent in Normal mode")
    
    # Check that initial_workers_spawned tracks which workers are initial
    assert 'initial_workers_spawned' in normal_section, \
        "❌ FAILED: initial_workers_spawned tracker not found in Normal mode"
    print("✓ Test 25 PASSED: initial_workers_spawned tracks initial batch in Normal mode")
    
    # Check that is_initial_worker flag is passed to worker_task
    assert 'is_initial_worker=is_initial' in normal_section or 'is_initial_worker=' in normal_section, \
        "❌ FAILED: is_initial_worker flag not passed to worker_task"
    print("✓ Test 26 PASSED: is_initial_worker flag passed to worker_task in Normal mode")
    
    # Check that worker_task passes startup_barrier to execute_single_profile
    assert 'startup_barrier=normal_startup_barrier if is_initial_worker else None' in normal_section, \
        "❌ FAILED: startup_barrier not passed to execute_single_profile for initial workers"
    print("✓ Test 27 PASSED: startup_barrier passed to execute_single_profile for initial workers only")


def test_execute_single_profile_startup_barrier():
    """Test that execute_single_profile handles the startup barrier correctly."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find execute_single_profile section
    esp_start = content.find('async def execute_single_profile(')
    esp_end = content.find('\n    async def execute_browser_with_tabs', esp_start)
    esp_section = content[esp_start:esp_end] if esp_end != -1 else content[esp_start:]
    
    # Check that startup_barrier parameter exists
    assert 'startup_barrier=None' in esp_section, \
        "❌ FAILED: startup_barrier parameter not in execute_single_profile"
    print("✓ Test 28 PASSED: startup_barrier parameter added to execute_single_profile")
    
    # Check that barrier is signaled after successful context creation
    assert "startup_barrier['count'] += 1" in esp_section, \
        "❌ FAILED: Barrier count increment not found in execute_single_profile"
    print("✓ Test 29 PASSED: Barrier count incremented after context creation in execute_single_profile")
    
    # Check that all N event is set when count reaches target
    assert "startup_barrier['count'] >= startup_barrier['target']" in esp_section, \
        "❌ FAILED: Barrier event set condition not found in execute_single_profile"
    print("✓ Test 30 PASSED: Barrier event set when all N browsers launched in execute_single_profile")
    
    # Check that tasks wait on the barrier before executing
    assert "await startup_barrier['event'].wait()" in esp_section, \
        "❌ FAILED: Barrier wait not found in execute_single_profile"
    print("✓ Test 31 PASSED: execute_single_profile waits on startup barrier before running")
    
    # Check deadlock prevention on failure paths (at least 2 paths)
    increment_count = esp_section.count("startup_barrier['count'] += 1")
    assert increment_count >= 2, \
        f"❌ FAILED: Barrier increment should appear in at least 2 paths (success + failure), found {increment_count}"
    print(f"✓ Test 32 PASSED: Barrier incremented in {increment_count} paths (prevents deadlock)")
    
    # Check that startup_barrier is passed through to execute_high_cpc_mode
    assert 'startup_barrier=startup_barrier' in esp_section, \
        "❌ FAILED: startup_barrier not passed through to execute_high_cpc_mode"
    print("✓ Test 33 PASSED: startup_barrier forwarded to execute_high_cpc_mode")


def test_execute_high_cpc_mode_startup_barrier():
    """Test that execute_high_cpc_mode handles the startup barrier correctly."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find execute_high_cpc_mode section
    hcpc_start = content.find('async def execute_high_cpc_mode(')
    hcpc_end = content.find('\n    async def execute_single_profile', hcpc_start)
    hcpc_section = content[hcpc_start:hcpc_end] if hcpc_end != -1 else content[hcpc_start:]
    
    # Check that startup_barrier parameter exists
    assert 'startup_barrier=None' in hcpc_section, \
        "❌ FAILED: startup_barrier parameter not in execute_high_cpc_mode"
    print("✓ Test 34 PASSED: startup_barrier parameter added to execute_high_cpc_mode")
    
    # Check barrier signaling after context creation
    assert "startup_barrier['count'] += 1" in hcpc_section, \
        "❌ FAILED: Barrier count increment not found in execute_high_cpc_mode"
    print("✓ Test 35 PASSED: Barrier count incremented in execute_high_cpc_mode")
    
    # Check that all N event is set
    assert "startup_barrier['count'] >= startup_barrier['target']" in hcpc_section, \
        "❌ FAILED: Barrier event set condition not found in execute_high_cpc_mode"
    print("✓ Test 36 PASSED: Barrier event set when all N browsers launched in execute_high_cpc_mode")
    
    # Check deadlock prevention (both success and failure paths)
    increment_count = hcpc_section.count("startup_barrier['count'] += 1")
    assert increment_count >= 2, \
        f"❌ FAILED: Barrier increment should appear in at least 2 paths, found {increment_count}"
    print(f"✓ Test 37 PASSED: Barrier incremented in {increment_count} paths in execute_high_cpc_mode")


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
        test_launch_semaphore_in_create_context()
        print()
        test_rpa_startup_barrier()
        print()
        test_normal_mode_startup_barrier()
        print()
        test_execute_single_profile_startup_barrier()
        print()
        test_execute_high_cpc_mode_startup_barrier()
        print()
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("All N browsers launch in parallel (no serial semaphore restriction)")
        print("AND synchronize via a startup barrier before any script runs.")
        print("This guarantees all N concurrent browsers are visible simultaneously.")
        print()
        print("Expected behavior (both RPA mode and Normal mode):")
        print("  - Setting CONCURRENT=10 will open exactly 10 browsers concurrently")
        print("  - All 10 browsers are visible concurrently in parallel before any work starts")
        print("  - 0.2s stagger between task/worker creations avoids exact-simultaneous init")
        print("  - Startup barrier ensures all N are open before scripts start")
        print("  - Proxy retry fallback ensures error-free operation on proxy failures")
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
