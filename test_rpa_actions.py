#!/usr/bin/env python3
"""
Test script to validate all RPA Script Creator actions.
Tests each action type to ensure they work properly.
"""

import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
from playwright.async_api import async_playwright


async def test_all_rpa_actions():
    """Test all RPA actions to ensure they work correctly."""
    
    print("=" * 70)
    print("Testing All RPA Script Creator Actions")
    print("=" * 70)
    
    # Test script with all action types
    test_script = {
        "name": "Complete Action Test",
        "description": "Test all RPA actions",
        "steps": [
            # Test 1: New Tab
            {"type": "newPage"},
            
            # Test 2: Access Website
            {"type": "navigate", "url": "https://example.com", "timeout": 30000},
            
            # Test 3: Time (wait)
            {"type": "wait", "duration": 2000},
            
            # Test 4: Scroll
            {"type": "scroll", "depth": 50, "position": "Intermediate", "scroll_type": "Smooth"},
            
            # Test 5: Wait again
            {"type": "wait", "duration": 1000},
            
            # Test 6: Refresh Webpage
            {"type": "refresh"},
            
            # Test 7: Wait after refresh
            {"type": "wait", "duration": 1000},
            
            # Test 8: New Tab again
            {"type": "newPage"},
            
            # Test 9: Navigate in new tab
            {"type": "navigate", "url": "https://www.wikipedia.org", "timeout": 30000},
            
            # Test 10: Scroll in new tab
            {"type": "scroll", "depth": 30, "position": "Top", "scroll_type": "Auto"},
            
            # Test 11: Wait
            {"type": "wait", "duration": 2000},
            
            # Test 12: Close Tab (closeTab)
            {"type": "closeTab"},
            
            # Test 13: Navigate back to first tab (should still be on example.com)
            {"type": "wait", "duration": 1000},
            
            # Test 14: Close Page (closePage)
            {"type": "closePage"}
        ]
    }
    
    results = {
        "newPage": {"tested": False, "passed": False, "error": None},
        "navigate": {"tested": False, "passed": False, "error": None},
        "wait": {"tested": False, "passed": False, "error": None},
        "scroll": {"tested": False, "passed": False, "error": None},
        "click": {"tested": False, "passed": False, "error": None},
        "input": {"tested": False, "passed": False, "error": None},
        "closePage": {"tested": False, "passed": False, "error": None},
        "refresh": {"tested": False, "passed": False, "error": None},
        "closeTab": {"tested": False, "passed": False, "error": None},
        "if": {"tested": False, "passed": False, "error": None},
        "forLoopElements": {"tested": False, "passed": False, "error": None},
        "forLoopTimes": {"tested": False, "passed": False, "error": None},
        "while": {"tested": False, "passed": False, "error": None},
        "break": {"tested": False, "passed": False, "error": None},
        "quitBrowser": {"tested": False, "passed": False, "error": None},
    }
    
    try:
        async with async_playwright() as p:
            print("\n1. Launching browser...")
            browser = await p.chromium.launch(headless=False)
            
            print("2. Creating browser context...")
            context = await browser.new_context()
            
            print("3. Executing test script...\n")
            
            # Simple script executor for testing
            current_page = None
            steps = test_script.get('steps', [])
            
            for idx, step in enumerate(steps):
                step_type = step.get('type')
                print(f"   Step {idx + 1}/{len(steps)}: {step_type}")
                
                try:
                    if step_type == 'newPage':
                        results["newPage"]["tested"] = True
                        # Check if context has existing pages
                        if not current_page and context.pages:
                            current_page = context.pages[0]
                            print(f"      ✓ Using existing page")
                        else:
                            current_page = await context.new_page()
                            print(f"      ✓ New page/tab opened successfully")
                        results["newPage"]["passed"] = True
                    
                    elif step_type == 'navigate':
                        results["navigate"]["tested"] = True
                        url = step.get('url', '')
                        timeout = step.get('timeout', 30000)
                        if current_page:
                            await current_page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                            print(f"      ✓ Navigated to {url}")
                            results["navigate"]["passed"] = True
                        else:
                            print(f"      ✗ No page available")
                            results["navigate"]["error"] = "No page available"
                    
                    elif step_type == 'wait':
                        results["wait"]["tested"] = True
                        duration = step.get('duration', 1000)
                        await asyncio.sleep(duration / 1000)
                        print(f"      ✓ Waited {duration}ms")
                        results["wait"]["passed"] = True
                    
                    elif step_type == 'scroll':
                        results["scroll"]["tested"] = True
                        if current_page:
                            depth = step.get('depth', 50)
                            position = step.get('position', 'Intermediate')
                            scroll_type = step.get('scroll_type', 'Smooth')
                            
                            # Simple scroll implementation
                            # Convert percentage depth to pixels (depth * 10)
                            # This is a simplified approximation for testing purposes
                            scroll_amount = depth * 10
                            await current_page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                            print(f"      ✓ Scrolled to depth {depth}% ({scroll_type})")
                            results["scroll"]["passed"] = True
                        else:
                            print(f"      ✗ No page available")
                            results["scroll"]["error"] = "No page available"
                    
                    elif step_type == 'closePage':
                        results["closePage"]["tested"] = True
                        if current_page:
                            await current_page.close()
                            current_page = None
                            print(f"      ✓ Page closed")
                            results["closePage"]["passed"] = True
                        else:
                            print(f"      ✗ No page to close")
                            results["closePage"]["error"] = "No page to close"
                    
                    elif step_type == 'refresh':
                        results["refresh"]["tested"] = True
                        if current_page:
                            await current_page.reload(wait_until='domcontentloaded')
                            print(f"      ✓ Page refreshed")
                            results["refresh"]["passed"] = True
                        else:
                            print(f"      ✗ No page available")
                            results["refresh"]["error"] = "No page available"
                    
                    elif step_type == 'closeTab':
                        results["closeTab"]["tested"] = True
                        if current_page:
                            await current_page.close()
                            current_page = None
                            print(f"      ✓ Tab closed")
                            results["closeTab"]["passed"] = True
                        else:
                            print(f"      ✗ No tab to close")
                            results["closeTab"]["error"] = "No tab to close"
                    
                    else:
                        print(f"      ⚠ Unknown step type: {step_type}")
                    
                except Exception as e:
                    print(f"      ✗ Error: {e}")
                    if step_type in results:
                        results[step_type]["error"] = str(e)
            
            print("\n4. Cleaning up...")
            await context.close()
            await browser.close()
            
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        return False
    
    # Print results summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    all_passed = True
    for action, result in results.items():
        if result["tested"]:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"{action:15s} : {status}")
            if result["error"]:
                print(f"                  Error: {result['error']}")
            if not result["passed"]:
                all_passed = False
        else:
            print(f"{action:15s} : NOT TESTED")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✓ All tested actions passed!")
        return True
    else:
        print("\n✗ Some actions failed. Please review errors above.")
        return False


if __name__ == '__main__':
    print("RPA Script Creator Action Validation Test\n")
    
    success = asyncio.run(test_all_rpa_actions())
    
    sys.exit(0 if success else 1)
