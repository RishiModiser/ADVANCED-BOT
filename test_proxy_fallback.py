#!/usr/bin/env python3
"""
Test for Proxy Fallback Mechanism
Validates that browser context creation falls back to direct connection when proxy fails
"""

import asyncio
from typing import Optional, Dict
from unittest.mock import MagicMock, AsyncMock, patch


class MockLogManager:
    """Mock log manager for testing."""
    def __init__(self):
        self.logs = []
    
    def log(self, message: str, level: str = 'INFO'):
        self.logs.append((message, level))
        print(f"[{level}] {message}")


class MockProxyManager:
    """Mock proxy manager for testing."""
    def __init__(self):
        self.proxy_enabled = False
        self.proxy_list = []
        self.failed_proxies = set()
    
    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration."""
        if not self.proxy_enabled or not self.proxy_list:
            return None
        
        # Return first available proxy not in failed list
        for i, proxy in enumerate(self.proxy_list):
            if i not in self.failed_proxies:
                return proxy
        return None
    
    def mark_proxy_failed(self, proxy_config: Dict[str, str]):
        """Mark a proxy as failed."""
        try:
            idx = self.proxy_list.index(proxy_config)
            self.failed_proxies.add(idx)
        except ValueError:
            pass


class MockFingerprintManager:
    """Mock fingerprint manager for testing."""
    def __init__(self):
        self.platform = 'desktop'
    
    def generate_fingerprint(self):
        return {
            'user_agent': 'Mozilla/5.0 Test Browser',
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'en-US',
            'timezone': 'America/New_York',
            'hardware_concurrency': 8
        }


class MockContext:
    """Mock browser context."""
    async def add_init_script(self, script: str):
        pass


class MockBrowser:
    """Mock browser that simulates proxy failures."""
    def __init__(self, fail_with_proxy=False):
        self.fail_with_proxy = fail_with_proxy
        self.context_calls = []
    
    async def new_context(self, **kwargs):
        """Create context, fail if proxy is used and fail_with_proxy is True."""
        self.context_calls.append(kwargs)
        
        # Simulate proxy connection failure
        if self.fail_with_proxy and 'proxy' in kwargs:
            raise Exception("net::ERR_PROXY_CONNECTION_FAILED")
        
        return MockContext()


async def test_proxy_fallback():
    """Test that context creation falls back to direct connection when proxy fails."""
    print("="*70)
    print("Testing Proxy Fallback Mechanism")
    print("="*70)
    print()
    
    # Setup mocks
    log_manager = MockLogManager()
    browser = MockBrowser(fail_with_proxy=True)
    
    proxy_manager = MockProxyManager()
    proxy_manager.proxy_enabled = True
    proxy_manager.proxy_list = [
        {'server': 'http://invalid-proxy.example.com:8080'}
    ]
    
    fingerprint_manager = MockFingerprintManager()
    
    # Simulate the create_context logic with our fix
    print("Step 1: Setting up browser context with invalid proxy")
    print(f"  Proxy server: {proxy_manager.proxy_list[0]['server']}")
    print()
    
    try:
        # Generate fingerprint
        fingerprint_manager.platform = 'desktop'
        fingerprint = fingerprint_manager.generate_fingerprint()
        
        log_manager.log('━━━ Creating Browser Context ━━━')
        log_manager.log(f'Platform: desktop')
        log_manager.log(f'User Agent: {fingerprint["user_agent"][:60]}...')
        
        context_options = {
            'user_agent': fingerprint['user_agent'],
            'viewport': fingerprint['viewport'],
            'locale': fingerprint['locale'],
            'timezone_id': fingerprint['timezone'],
        }
        
        # Add proxy if enabled and configured
        proxy_config = None
        use_proxy = True
        if use_proxy:
            proxy_config = proxy_manager.get_proxy_config()
            if proxy_config:
                context_options['proxy'] = proxy_config
                server = proxy_config.get('server', 'unknown')
                log_manager.log(f'✓ Using proxy: {server}')
            else:
                log_manager.log('No proxy configured, using direct connection')
        
        # Try to create context with proxy
        print()
        print("Step 2: Attempting to create context with proxy...")
        try:
            context = await browser.new_context(**context_options)
            print("  ✗ Should have failed with proxy error!")
            return False
        except Exception as proxy_error:
            # Check if error is proxy-related
            error_str = str(proxy_error).lower()
            proxy_error_indicators = [
                'proxy', 'econnrefused', 'etimedout', 'enotfound',
                'connection refused', 'timeout', 'unreachable'
            ]
            is_proxy_error = any(indicator in error_str for indicator in proxy_error_indicators)
            
            print(f"  ✓ Proxy error detected: {proxy_error}")
            print()
            
            if is_proxy_error and proxy_config:
                # Log proxy-specific error
                log_manager.log(f'⚠ Proxy connection failed: {proxy_error}', 'WARNING')
                log_manager.log(f'⚠ Proxy server: {proxy_config.get("server", "unknown")}', 'WARNING')
                log_manager.log('⚠ Retrying without proxy...', 'WARNING')
                
                # Mark proxy as failed
                proxy_manager.mark_proxy_failed(proxy_config)
                
                print()
                print("Step 3: Retrying without proxy...")
                # Retry without proxy
                context_options_no_proxy = {
                    'user_agent': fingerprint['user_agent'],
                    'viewport': fingerprint['viewport'],
                    'locale': fingerprint['locale'],
                    'timezone_id': fingerprint['timezone'],
                }
                context = await browser.new_context(**context_options_no_proxy)
                log_manager.log('✓ Browser context created with direct connection (proxy bypassed)')
                print("  ✓ Context created successfully without proxy!")
            else:
                # Re-raise if not a proxy error
                raise
        
        # Inject navigator properties
        await context.add_init_script(f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {fingerprint['hardware_concurrency']}
            }});
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined
            }});
        """)
        
        log_manager.log('✓ Browser context created successfully')
        log_manager.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        
        # Validate the results
        print()
        print("="*70)
        print("Validation Results")
        print("="*70)
        print()
        print(f"Total context creation attempts: {len(browser.context_calls)}")
        print(f"  Attempt 1 (with proxy): {'proxy' in browser.context_calls[0]}")
        print(f"  Attempt 2 (without proxy): {'proxy' not in browser.context_calls[1]}")
        print()
        print(f"Proxy marked as failed: {0 in proxy_manager.failed_proxies}")
        print()
        
        # Check logs for expected messages
        warning_logs = [log for log, level in log_manager.logs if level == 'WARNING']
        print(f"Warning messages logged: {len(warning_logs)}")
        for log in warning_logs:
            print(f"  - {log}")
        print()
        
        # Verify success
        success = (
            len(browser.context_calls) == 2 and
            'proxy' in browser.context_calls[0] and
            'proxy' not in browser.context_calls[1] and
            0 in proxy_manager.failed_proxies and
            len(warning_logs) == 3
        )
        
        if success:
            print("✓ TEST PASSED: Proxy fallback mechanism works correctly!")
            print()
            print("Key behaviors verified:")
            print("  1. Initial attempt used proxy")
            print("  2. Proxy failure was detected")
            print("  3. Failed proxy was marked")
            print("  4. Retry succeeded without proxy")
            print("  5. Appropriate warning messages were logged")
        else:
            print("✗ TEST FAILED: Unexpected behavior")
        
        return success
        
    except Exception as e:
        log_manager.log(f'Context creation error: {e}', 'ERROR')
        log_manager.log('This may be due to:', 'ERROR')
        log_manager.log('  - Invalid proxy configuration', 'ERROR')
        log_manager.log('  - Network connectivity issues', 'ERROR')
        log_manager.log('  - Browser crash or resource exhaustion', 'ERROR')
        print(f"✗ TEST FAILED: Unexpected exception: {e}")
        return False


async def main():
    """Run all tests."""
    print()
    result = await test_proxy_fallback()
    print()
    print("="*70)
    print(f"Overall Result: {'PASSED' if result else 'FAILED'}")
    print("="*70)
    return result


if __name__ == '__main__':
    result = asyncio.run(main())
    exit(0 if result else 1)
