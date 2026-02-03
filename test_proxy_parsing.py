#!/usr/bin/env python3
"""
Test script to verify proxy parsing for all formats, including authenticated proxies.
This test specifically validates the host:port:username:password format.
"""

import sys
from typing import List, Dict

class ProxyManager:
    """Simplified ProxyManager for testing."""
    
    def __init__(self):
        self.proxy_type = 'HTTP'
    
    def parse_proxy_list(self, proxy_text: str) -> List[Dict[str, str]]:
        """Parse proxy list from text input.
        
        Supported formats:
        - ip:port or host:port
        - user:pass@ip:port or user:pass@host:port
        - ip:port:username:password or host:port:username:password
        - protocol://ip:port or protocol://host:port (http, https, socks5)
        - protocol://user:pass@ip:port or protocol://user:pass@host:port
        - IPv6: [ipv6]:port or protocol://[ipv6]:port
        
        Returns:
            List of parsed proxy configurations
        """
        proxies = []
        lines = proxy_text.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                proxy_config = {}
                proxy_type = self.proxy_type.lower()  # Default to selected type
                
                # Check if protocol is specified in the line
                if '://' in line:
                    protocol, rest = line.split('://', 1)
                    proxy_type = protocol.lower()
                    if proxy_type not in ['http', 'https', 'socks5']:
                        proxy_type = self.proxy_type.lower()
                    line = rest
                
                # Check for user:pass@host:port format
                if '@' in line:
                    auth_part, server_part = line.split('@', 1)
                    if ':' in auth_part:
                        username, password = auth_part.split(':', 1)
                        proxy_config['username'] = username
                        proxy_config['password'] = password
                    
                    # Build server URL from host:port
                    if ':' in server_part:
                        # Handle IPv6 addresses [ipv6]:port
                        if server_part.startswith('['):
                            # IPv6 format
                            bracket_end = server_part.find(']')
                            if bracket_end != -1:
                                host = server_part[:bracket_end+1]
                                port_part = server_part[bracket_end+1:]
                                if port_part.startswith(':'):
                                    port = port_part[1:]
                                    proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                        else:
                            host, port = server_part.rsplit(':', 1)
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                else:
                    # Parse without @ symbol
                    # Check for IPv6 addresses first
                    if line.startswith('['):
                        # IPv6 format: [ipv6]:port or [ipv6]:port:username:password
                        bracket_end = line.find(']')
                        if bracket_end != -1:
                            host = line[:bracket_end+1]
                            rest_parts = line[bracket_end+1:].lstrip(':').split(':')
                            if len(rest_parts) >= 1:
                                port = rest_parts[0]
                                proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                                if len(rest_parts) == 3:
                                    # [ipv6]:port:username:password
                                    proxy_config['username'] = rest_parts[1]
                                    proxy_config['password'] = rest_parts[2]
                    else:
                        # Check for host:port:username:password format
                        parts = line.split(':')
                        if len(parts) == 4:
                            # Assume host:port:username:password
                            host, port, username, password = parts
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                            proxy_config['username'] = username
                            proxy_config['password'] = password
                        elif len(parts) == 2:
                            # Simple host:port format
                            host, port = parts
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                        elif len(parts) > 2:
                            # Assume last part is port, rest is hostname
                            # This could be hostname:with:colons:port
                            port = parts[-1]
                            host = ':'.join(parts[:-1])
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                
                if proxy_config.get('server'):
                    proxies.append(proxy_config)
                    
            except Exception as e:
                # Log parsing error but continue with other proxies
                print(f"Warning: Failed to parse proxy on line {line_num}: {line} - {e}")
                continue
        
        return proxies


def test_proxy_formats():
    """Test various proxy formats."""
    manager = ProxyManager()
    
    # Test 1: Simple format
    print("=" * 80)
    print("TEST 1: Simple host:port format")
    print("=" * 80)
    proxy_text = "192.168.1.1:8080"
    proxies = manager.parse_proxy_list(proxy_text)
    print(f"Input: {proxy_text}")
    print(f"Parsed: {proxies}")
    assert len(proxies) == 1
    assert proxies[0]['server'] == 'http://192.168.1.1:8080'
    assert 'username' not in proxies[0]
    print("✓ PASSED\n")
    
    # Test 2: user:pass@host:port format
    print("=" * 80)
    print("TEST 2: user:pass@host:port format")
    print("=" * 80)
    proxy_text = "user:password@192.168.1.2:8080"
    proxies = manager.parse_proxy_list(proxy_text)
    print(f"Input: {proxy_text}")
    print(f"Parsed: {proxies}")
    assert len(proxies) == 1
    assert proxies[0]['server'] == 'http://192.168.1.2:8080'
    assert proxies[0]['username'] == 'user'
    assert proxies[0]['password'] == 'password'
    print("✓ PASSED\n")
    
    # Test 3: host:port:username:password format (THE KEY TEST!)
    print("=" * 80)
    print("TEST 3: host:port:username:password format (USER'S FORMAT)")
    print("=" * 80)
    proxy_text = """geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg
geo.g-w.info:10800:FIFRlLg56bDDOhRy:EyIqa6s0H1koZieb"""
    proxies = manager.parse_proxy_list(proxy_text)
    print(f"Input:\n{proxy_text}")
    print(f"\nParsed {len(proxies)} proxies:")
    for i, proxy in enumerate(proxies, 1):
        print(f"  Proxy {i}:")
        print(f"    Server: {proxy['server']}")
        print(f"    Username: {proxy['username']}")
        print(f"    Password: {proxy['password']}")
    
    assert len(proxies) == 2
    assert proxies[0]['server'] == 'http://geo.g-w.info:10800'
    assert proxies[0]['username'] == 'KWGBBxI0G8SSRwX0'
    assert proxies[0]['password'] == 'g1GI0bd49JUi58Pg'
    assert proxies[1]['server'] == 'http://geo.g-w.info:10800'
    assert proxies[1]['username'] == 'FIFRlLg56bDDOhRy'
    assert proxies[1]['password'] == 'EyIqa6s0H1koZieb'
    print("✓ PASSED\n")
    
    # Test 4: Protocol specified
    print("=" * 80)
    print("TEST 4: Protocol specified (socks5)")
    print("=" * 80)
    proxy_text = "socks5://geo.g-w.info:10800:testuser:testpass"
    proxies = manager.parse_proxy_list(proxy_text)
    print(f"Input: {proxy_text}")
    print(f"Parsed: {proxies}")
    assert len(proxies) == 1
    assert proxies[0]['server'] == 'socks5://geo.g-w.info:10800'
    assert proxies[0]['username'] == 'testuser'
    assert proxies[0]['password'] == 'testpass'
    print("✓ PASSED\n")
    
    # Test 5: Mixed formats
    print("=" * 80)
    print("TEST 5: Mixed formats in one list")
    print("=" * 80)
    proxy_text = """192.168.1.1:8080
user:pass@192.168.1.2:8080
geo.g-w.info:10800:username:password
http://192.168.1.3:8080
socks5://user:pass@192.168.1.4:1080"""
    proxies = manager.parse_proxy_list(proxy_text)
    print(f"Input:\n{proxy_text}")
    print(f"\nParsed {len(proxies)} proxies:")
    for i, proxy in enumerate(proxies, 1):
        print(f"  Proxy {i}: {proxy}")
    assert len(proxies) == 5
    print("✓ PASSED\n")
    
    # Test 6: All user's proxies
    print("=" * 80)
    print("TEST 6: All user's proxies from issue")
    print("=" * 80)
    proxy_text = """geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg
geo.g-w.info:10800:FIFRlLg56bDDOhRy:EyIqa6s0H1koZieb
geo.g-w.info:10800:gyCqjgiqkXxUJ4yM:QXMXfhm6145DzQUv
geo.g-w.info:10800:iPtM2e7dbRIv0k3A:cgXMBHvy4Mrvrvba
geo.g-w.info:10800:i7Op6wbV9m1sH6gw:CD7LQdkTLsAYwACv"""
    proxies = manager.parse_proxy_list(proxy_text)
    print(f"Parsed {len(proxies)} proxies")
    for i, proxy in enumerate(proxies, 1):
        print(f"  Proxy {i}: server={proxy['server']}, user={proxy['username'][:5]}..., pass={proxy['password'][:5]}...")
    assert len(proxies) == 5
    print("✓ PASSED\n")
    
    print("=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("=" * 80)
    print("\nThe proxy parsing logic correctly handles all formats, including:")
    print("  ✓ Simple host:port")
    print("  ✓ user:pass@host:port")
    print("  ✓ host:port:username:password (USER'S FORMAT)")
    print("  ✓ Protocol-specified proxies (http://, https://, socks5://)")
    print("  ✓ Mixed formats in the same list")
    print("\nThe parsing works correctly! The issue may be elsewhere in the code.")


if __name__ == '__main__':
    try:
        test_proxy_formats()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
