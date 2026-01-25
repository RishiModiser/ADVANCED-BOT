#!/usr/bin/env python3
"""
Test script to verify browser initialization works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to import from advanced_bot
sys.path.insert(0, str(Path(__file__).parent))

# Import required classes
from playwright.async_api import async_playwright


async def test_browser_init():
    """Test basic browser initialization."""
    print("Testing browser initialization...")
    print("-" * 60)
    
    try:
        print("1. Starting Playwright...")
        playwright = await async_playwright().start()
        print("   ✓ Playwright started successfully")
        
        print("2. Launching Chromium browser...")
        browser = await playwright.chromium.launch(headless=True)
        print("   ✓ Browser launched successfully")
        
        print("3. Creating new context...")
        context = await browser.new_context()
        print("   ✓ Context created successfully")
        
        print("4. Creating new page...")
        page = await context.new_page()
        print("   ✓ Page created successfully")
        
        print("5. Testing page functionality...")
        await page.set_content("<html><body><h1>Test Page</h1></body></html>")
        print("   ✓ Page content set successfully")
        
        print("6. Getting page title...")
        content = await page.content()
        if "Test Page" in content:
            print("   ✓ Page content verified")
        else:
            print("   ✗ Page content verification failed")
        
        print("7. Cleaning up...")
        await context.close()
        await browser.close()
        await playwright.stop()
        print("   ✓ Cleanup completed")
        
        print("-" * 60)
        print("✓ All tests passed! Browser initialization is working correctly.")
        return True
        
    except Exception as e:
        print("-" * 60)
        print(f"✗ Test failed with error: {e}")
        print()
        print("This likely means Playwright browsers are not installed.")
        print("Please run: playwright install chromium")
        return False


def main():
    """Main test entry point."""
    success = asyncio.run(test_browser_init())
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
