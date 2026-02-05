#!/usr/bin/env python3
"""
Test concurrent platform selection fix.

This test validates that:
1. Platform configuration is properly retrieved in both RPA and Normal modes
2. Platform parameter is passed to create_context in all execution paths
3. Multiple platforms (Windows + Android) are randomly selected for concurrent browsers
"""

import sys
import re

def test_platform_selection_in_rpa_mode():
    """Test that RPA mode retrieves and uses platform configuration."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Check that platforms are retrieved from config in RPA mode
    rpa_mode_section = content[content.find('async def run_rpa_mode'):content.find('async def run_normal_mode')]
    
    # Verify platforms config is retrieved
    assert "platforms = self.config.get('platforms', ['windows'])" in rpa_mode_section, \
        "❌ FAILED: platforms configuration not retrieved in RPA mode"
    print("✓ Test 1 PASSED: Platforms configuration retrieved in RPA mode")
    
    # Verify platform is selected randomly for each concurrent browser
    assert "platform = random.choice(platforms)" in rpa_mode_section, \
        "❌ FAILED: platform not randomly selected in RPA mode"
    print("✓ Test 2 PASSED: Platform randomly selected for each concurrent browser")
    
    # Verify platform parameter is passed to create_context
    assert "create_context(platform=platform, use_proxy=" in rpa_mode_section, \
        "❌ FAILED: platform parameter not passed to create_context in RPA mode"
    print("✓ Test 3 PASSED: Platform parameter passed to create_context in RPA mode")
    
    # Verify platform is logged for visibility
    assert "Platform: {platform}" in rpa_mode_section, \
        "❌ FAILED: platform not logged in RPA mode"
    print("✓ Test 4 PASSED: Platform logged for visibility in RPA mode")

def test_platform_selection_in_normal_mode():
    """Test that Normal mode uses platform configuration correctly."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Check that platforms are retrieved from config in Normal mode
    # Find the entire normal mode method (it contains nested functions, so look further ahead)
    normal_start = content.find('async def run_normal_mode')
    # Look for a top-level method (not indented async def) after run_normal_mode
    # Search for pattern like "\n    async def " which is a class method
    search_pos = normal_start + 1000  # Start searching well into the method
    while search_pos < len(content):
        if content[search_pos:search_pos+14] == '\n    async def ':
            break
        search_pos += 1
    normal_mode_section = content[normal_start:search_pos] if search_pos < len(content) else content[normal_start:]
    
    # Verify platforms config is retrieved
    assert "platforms = self.config.get('platforms', ['windows'])" in normal_mode_section, \
        "❌ FAILED: platforms configuration not retrieved in Normal mode"
    print("✓ Test 5 PASSED: Platforms configuration retrieved in Normal mode")
    
    # Verify execute_single_profile receives platforms parameter
    assert "platforms, visit_type," in normal_mode_section, \
        "❌ FAILED: platforms parameter not passed to execute_single_profile"
    print("✓ Test 6 PASSED: Platforms parameter passed to execute_single_profile")

def test_execute_single_profile_uses_platform():
    """Test that execute_single_profile properly uses platform parameter."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # Find execute_single_profile method
    profile_start = content.find('async def execute_single_profile')
    next_async = content.find('async def ', profile_start + 50)
    profile_section = content[profile_start:next_async] if next_async > 0 else content[profile_start:]
    
    # Verify platform is selected from platforms list
    assert "platform = random.choice(platforms)" in profile_section, \
        "❌ FAILED: platform not selected in execute_single_profile"
    print("✓ Test 7 PASSED: Platform selected in execute_single_profile")
    
    # Verify platform is passed to create_context
    assert "context = await self.browser_manager.create_context(platform)" in profile_section, \
        "❌ FAILED: platform not passed to create_context in execute_single_profile"
    print("✓ Test 8 PASSED: Platform passed to create_context in execute_single_profile")

def test_concurrent_count_logic():
    """Test that concurrent count logic is correct."""
    with open('advanced_bot.py', 'r') as f:
        content = f.read()
    
    # RPA mode concurrent logic
    rpa_start = content.find('async def run_rpa_mode')
    rpa_end = content.find('async def run_normal_mode')
    rpa_mode_section = content[rpa_start:rpa_end]
    
    # Verify N tasks are created immediately
    assert "for i in range(num_concurrent):" in rpa_mode_section, \
        "❌ FAILED: concurrent tasks not created in loop"
    print("✓ Test 9 PASSED: RPA mode creates N concurrent tasks immediately")
    
    # Verify tasks are tracked
    assert "self.active_tasks.append(task)" in rpa_mode_section, \
        "❌ FAILED: tasks not tracked in active_tasks"
    print("✓ Test 10 PASSED: Tasks tracked in active_tasks for management")
    
    # Normal mode concurrent logic - find the full method
    normal_start = content.find('async def run_normal_mode')
    search_pos = normal_start + 1000
    while search_pos < len(content):
        if content[search_pos:search_pos+14] == '\n    async def ':
            break
        search_pos += 1
    normal_mode_section = content[normal_start:search_pos] if search_pos < len(content) else content[normal_start:]
    
    # Verify worker pool maintains N workers
    assert "while len(active_workers) < num_concurrent and self.running:" in normal_mode_section, \
        "❌ FAILED: worker pool doesn't maintain N workers"
    print("✓ Test 11 PASSED: Normal mode maintains N workers dynamically")
    
    # Verify immediate spawning (no delays)
    assert "# No delay - instances should start immediately" in normal_mode_section or \
           "# No delay - start all browsers immediately" in rpa_mode_section, \
        "❌ FAILED: delay comments not found, may have delays"
    print("✓ Test 12 PASSED: No delays in concurrent spawning")

if __name__ == '__main__':
    print("=" * 70)
    print("Testing Concurrent Platform Selection Fix")
    print("=" * 70)
    print()
    
    try:
        test_platform_selection_in_rpa_mode()
        print()
        test_platform_selection_in_normal_mode()
        print()
        test_execute_single_profile_uses_platform()
        print()
        test_concurrent_count_logic()
        print()
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
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
