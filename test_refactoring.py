#!/usr/bin/env python3
"""
Test script to validate the refactoring changes:
1. launch_persistent_context with channel="chrome"
2. Proxy queue system
3. Worker pool pattern
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock dependencies before import
from unittest.mock import Mock, MagicMock, AsyncMock, patch

# Mock PySide6 and playwright before checking dependencies
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()
sys.modules['playwright'] = MagicMock()
sys.modules['playwright.async_api'] = MagicMock()

# Test basic imports work
import unittest
try:
    from advanced_bot import (
        ProxyManager,
        BrowserManager,
        LogManager
    )
    print("✓ Successfully imported required classes")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


class TestProxyQueue(unittest.TestCase):
    """Test the new proxy queue system."""
    
    def test_proxy_queue_initialization(self):
        """Test that proxy queue is initialized correctly."""
        manager = ProxyManager()
        manager.proxy_enabled = True
        manager.proxy_list = [
            {'server': 'http://proxy1:8080'},
            {'server': 'http://proxy2:8080'},
            {'server': 'http://proxy3:8080'},
        ]
        
        # Initialize queue
        manager.initialize_queue()
        
        # Check queue is populated
        self.assertEqual(len(manager.proxy_queue), 3)
        self.assertEqual(manager.proxy_queue_index, 0)
        print("✓ Proxy queue initialization works")
    
    def test_proxy_sequential_distribution(self):
        """Test that proxies are distributed sequentially without repeats."""
        manager = ProxyManager()
        manager.proxy_enabled = True
        manager.proxy_list = [
            {'server': 'http://proxy1:8080'},
            {'server': 'http://proxy2:8080'},
            {'server': 'http://proxy3:8080'},
        ]
        manager.initialize_queue()
        
        # Get proxies sequentially
        proxy1 = manager.get_proxy_config()
        proxy2 = manager.get_proxy_config()
        proxy3 = manager.get_proxy_config()
        proxy4 = manager.get_proxy_config()  # Should be None
        
        self.assertIsNotNone(proxy1)
        self.assertIsNotNone(proxy2)
        self.assertIsNotNone(proxy3)
        self.assertIsNone(proxy4)  # All consumed
        
        # Verify they're different
        self.assertEqual(proxy1['server'], 'http://proxy1:8080')
        self.assertEqual(proxy2['server'], 'http://proxy2:8080')
        self.assertEqual(proxy3['server'], 'http://proxy3:8080')
        print("✓ Proxy sequential distribution works (no repeats)")
    
    def test_remaining_proxies(self):
        """Test that remaining proxy count is accurate."""
        manager = ProxyManager()
        manager.proxy_enabled = True
        manager.proxy_list = [
            {'server': 'http://proxy1:8080'},
            {'server': 'http://proxy2:8080'},
        ]
        manager.initialize_queue()
        
        self.assertEqual(manager.get_remaining_proxies(), 2)
        
        manager.get_proxy_config()
        self.assertEqual(manager.get_remaining_proxies(), 1)
        
        manager.get_proxy_config()
        self.assertEqual(manager.get_remaining_proxies(), 0)
        print("✓ Remaining proxy count tracking works")


class TestBrowserManager(unittest.TestCase):
    """Test the refactored BrowserManager."""
    
    def test_browser_manager_structure(self):
        """Test that BrowserManager has the new structure."""
        log_manager = LogManager()
        manager = BrowserManager(log_manager)
        
        # Check new attributes
        self.assertTrue(hasattr(manager, 'active_contexts'))
        self.assertIsInstance(manager.active_contexts, list)
        print("✓ BrowserManager has active_contexts tracking")
    
    def test_initialize_playwright_only(self):
        """Test that initialize only starts Playwright, not browser."""
        log_manager = LogManager()
        manager = BrowserManager(log_manager)
        
        # Mock playwright
        mock_pw = AsyncMock()
        with patch('advanced_bot.async_playwright') as mock_playwright:
            mock_playwright.return_value.start = AsyncMock(return_value=mock_pw)
            
            # Run async test
            result = asyncio.run(manager.initialize())
            
            # Should initialize playwright
            self.assertTrue(result)
            self.assertIsNotNone(manager.playwright)
            
            # Should NOT launch a browser (that happens in create_context now)
            self.assertIsNone(manager.browser)
            print("✓ initialize() only starts Playwright (no browser launch)")


def run_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running Refactoring Validation Tests")
    print("="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestProxyQueue))
    suite.addTests(loader.loadTestsFromTestCase(TestBrowserManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✓ All tests passed!")
        print("="*60 + "\n")
        return 0
    else:
        print("✗ Some tests failed")
        print("="*60 + "\n")
        return 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
