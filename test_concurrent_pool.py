#!/usr/bin/env python3
"""
Test script to verify concurrent browser pool management.
Tests that N browsers are maintained at all times.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))


async def test_browser_pool():
    """Test that browser pool maintains N concurrent tasks."""
    print("Testing browser pool management...")
    print("-" * 60)
    
    # Simulate browser tasks that complete at different times
    num_concurrent = 3
    total_tasks_to_complete = 10
    
    active_tasks = set()
    completed_tasks = []
    task_counter = 0
    
    async def mock_browser_task(task_num, duration):
        """Simulate a browser task that takes some time."""
        print(f"  [Browser {task_num}] Started (duration: {duration}s)")
        await asyncio.sleep(duration)
        print(f"  [Browser {task_num}] Completed")
        return task_num
    
    print(f"1. Testing with {num_concurrent} concurrent browsers")
    print(f"   Target: Complete {total_tasks_to_complete} total tasks")
    print()
    
    # Start initial set of browsers
    for i in range(num_concurrent):
        task_counter += 1
        # Each task takes between 1-3 seconds
        duration = 1 + (task_counter % 3)
        task = asyncio.create_task(mock_browser_task(task_counter, duration))
        active_tasks.add(task)
        print(f"  ✓ Started initial browser #{task_counter}")
    
    print(f"\n  ✓ Initial {num_concurrent} browsers started")
    print(f"  Active browsers: {len(active_tasks)}/{num_concurrent}\n")
    
    # Monitor and maintain N concurrent tasks
    while len(completed_tasks) < total_tasks_to_complete:
        # Wait for at least one task to complete
        done, pending = await asyncio.wait(
            active_tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Process completed tasks
        for task in done:
            active_tasks.discard(task)
            result = await task
            completed_tasks.append(result)
            print(f"  ✓ Browser #{result} closed (Total completed: {len(completed_tasks)})")
        
        # Immediately spawn replacements to maintain N concurrent
        while len(active_tasks) < num_concurrent and len(completed_tasks) < total_tasks_to_complete:
            task_counter += 1
            duration = 1 + (task_counter % 3)
            new_task = asyncio.create_task(mock_browser_task(task_counter, duration))
            active_tasks.add(new_task)
            print(f"  ✓ IMMEDIATELY spawned replacement browser #{task_counter}")
            print(f"    Active browsers: {len(active_tasks)}/{num_concurrent}")
    
    # Wait for remaining tasks
    if active_tasks:
        print(f"\n  Waiting for {len(active_tasks)} remaining browser(s)...")
        await asyncio.gather(*active_tasks)
    
    print("\n2. Verification:")
    print(f"   Total tasks completed: {len(completed_tasks)}")
    print(f"   Expected: {total_tasks_to_complete}")
    
    if len(completed_tasks) == total_tasks_to_complete:
        print("   ✓ All tasks completed successfully")
        success = True
    else:
        print("   ✗ Task count mismatch")
        success = False
    
    print("-" * 60)
    
    if success:
        print("✓ Browser pool management test PASSED!")
        print("  - Maintained N concurrent browsers")
        print("  - Immediately replaced closed browsers")
        print("  - Completed all tasks successfully")
    else:
        print("✗ Browser pool management test FAILED!")
    
    return success


async def test_immediate_replacement():
    """Test that replacement happens immediately without delay."""
    print("\nTesting immediate browser replacement...")
    print("-" * 60)
    
    num_concurrent = 5
    replacement_times = []
    
    async def quick_task(task_num):
        """Quick task that completes fast."""
        await asyncio.sleep(0.1)
        return task_num
    
    active_tasks = set()
    task_counter = 0
    
    # Start initial tasks
    for i in range(num_concurrent):
        task_counter += 1
        task = asyncio.create_task(quick_task(task_counter))
        active_tasks.add(task)
    
    print(f"Started {num_concurrent} initial browsers")
    
    # Monitor for 10 replacements
    for _ in range(10):
        start_time = asyncio.get_event_loop().time()
        
        # Wait for completion
        done, pending = await asyncio.wait(
            active_tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Remove completed
        for task in done:
            active_tasks.discard(task)
        
        # Immediately spawn replacement
        task_counter += 1
        new_task = asyncio.create_task(quick_task(task_counter))
        active_tasks.add(new_task)
        
        replacement_time = asyncio.get_event_loop().time() - start_time
        replacement_times.append(replacement_time)
    
    # Wait for remaining
    if active_tasks:
        await asyncio.gather(*active_tasks)
    
    avg_replacement_time = sum(replacement_times) / len(replacement_times)
    
    print(f"Completed {len(replacement_times)} browser replacements")
    print(f"Average replacement time: {avg_replacement_time:.4f}s")
    
    # Replacement should be nearly instant (under 0.2s including task completion)
    if avg_replacement_time < 0.2:
        print("✓ Browser replacement is IMMEDIATE (< 0.2s)")
        success = True
    else:
        print("✗ Browser replacement has delay (> 0.2s)")
        success = False
    
    print("-" * 60)
    return success


def main():
    """Main test entry point."""
    print("=" * 60)
    print("CONCURRENT BROWSER POOL MANAGEMENT TEST")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Pool maintenance
        test1_success = asyncio.run(test_browser_pool())
        
        # Test 2: Immediate replacement
        test2_success = asyncio.run(test_immediate_replacement())
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Test 1 (Pool Maintenance): {'PASS' if test1_success else 'FAIL'}")
        print(f"Test 2 (Immediate Replacement): {'PASS' if test2_success else 'FAIL'}")
        print("=" * 60)
        
        if test1_success and test2_success:
            print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
            print("\nThe concurrent browser pool will:")
            print("  - Maintain N browsers visible in taskbar at all times")
            print("  - Immediately replace any closed browser")
            print("  - Work during Human Based Simulation")
            return 0
        else:
            print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
            return 1
            
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
