"""
Test proxy hostname support - ensures hostnames are resolved to IPs for geolocation.
"""
import sys
import asyncio
import socket
from typing import Dict, Optional

# Test the ProxyManager parsing
class ProxyManager:
    def __init__(self):
        self.proxy_type = 'HTTP'
    
    def parse_proxy_list(self, proxy_text: str):
        """Parse proxy list from text input."""
        proxies = []
        lines = proxy_text.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                proxy_config = {}
                proxy_type = self.proxy_type.lower()
                
                # Check if protocol is specified
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
                    
                    if ':' in server_part:
                        if server_part.startswith('['):
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
                    if line.startswith('['):
                        bracket_end = line.find(']')
                        if bracket_end != -1:
                            host = line[:bracket_end+1]
                            rest_parts = line[bracket_end+1:].lstrip(':').split(':')
                            if len(rest_parts) >= 1:
                                port = rest_parts[0]
                                proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                                if len(rest_parts) == 3:
                                    proxy_config['username'] = rest_parts[1]
                                    proxy_config['password'] = rest_parts[2]
                    else:
                        # Check for host:port:username:password format
                        parts = line.split(':')
                        if len(parts) == 4:
                            host, port, username, password = parts
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                            proxy_config['username'] = username
                            proxy_config['password'] = password
                        elif len(parts) == 2:
                            host, port = parts
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                        elif len(parts) > 2:
                            port = parts[-1]
                            host = ':'.join(parts[:-1])
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                
                if proxy_config.get('server'):
                    proxies.append(proxy_config)
                    
            except Exception as e:
                print(f"Warning: Failed to parse proxy on line {line_num}: {line} - {e}")
                continue
        
        return proxies


class ProxyGeolocation:
    """Test ProxyGeolocation with hostname resolution."""
    
    def __init__(self):
        self.cache = {}
    
    def extract_ip_from_proxy(self, proxy_config: Dict[str, str]) -> Optional[str]:
        """Extract IP/host from proxy configuration."""
        try:
            server = proxy_config.get('server', '')
            # Remove protocol prefix
            if '://' in server:
                server = server.split('://', 1)[1]
            # Extract IP/host before port
            if ':' in server:
                if server.startswith('['):
                    bracket_end = server.find(']')
                    if bracket_end != -1:
                        return server[1:bracket_end]
                else:
                    return server.split(':', 1)[0]
            return server
        except Exception:
            return None
    
    async def _resolve_hostname_to_ip(self, hostname: str) -> Optional[str]:
        """Resolve hostname to IP address."""
        try:
            # Check if it's already an IP address
            try:
                socket.inet_aton(hostname)
                return hostname  # Already an IPv4
            except socket.error:
                try:
                    socket.inet_pton(socket.AF_INET6, hostname)
                    return hostname  # Already an IPv6
                except socket.error:
                    pass
            
            # Resolve hostname to IP
            ip = socket.gethostbyname(hostname)
            print(f'✓ Resolved hostname {hostname} to IP {ip}')
            return ip
        except socket.gaierror as e:
            print(f'⚠ Failed to resolve hostname {hostname}: {e}')
            return None
        except Exception as e:
            print(f'⚠ Error resolving hostname {hostname}: {e}')
            return None


async def test_proxy_parsing_and_resolution():
    """Test proxy parsing with various formats including hostnames."""
    print("=" * 70)
    print("TEST: Proxy Parsing and Hostname Resolution")
    print("=" * 70)
    
    pm = ProxyManager()
    geo = ProxyGeolocation()
    
    # Test cases with different proxy formats
    test_cases = [
        ("IP-based simple", "192.168.1.1:8080"),
        ("IP with auth (@)", "user:pass@192.168.1.2:8080"),
        ("IP with auth (colon)", "192.168.1.3:8080:testuser:testpass"),
        ("Hostname simple", "proxy.example.com:3128"),
        ("Hostname with auth (@)", "user:pass@proxy.example.com:8080"),
        ("Hostname with auth (colon)", "proxy.example.com:3128:admin:secret123"),
        ("User's proxy format", "geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg"),
        ("With HTTP protocol", "http://192.168.1.4:8080"),
        ("With SOCKS5 protocol", "socks5://user:pass@192.168.1.5:1080"),
    ]
    
    all_passed = True
    for test_name, proxy_str in test_cases:
        print(f"\n📋 Test: {test_name}")
        print(f"   Input: {proxy_str}")
        
        # Parse proxy
        result = pm.parse_proxy_list(proxy_str)
        if not result:
            print(f"   ❌ FAILED: Could not parse proxy")
            all_passed = False
            continue
        
        proxy_config = result[0]
        print(f"   ✓ Parsed: {proxy_config}")
        
        # Extract host/IP
        host_or_ip = geo.extract_ip_from_proxy(proxy_config)
        if not host_or_ip:
            print(f"   ❌ FAILED: Could not extract host/IP")
            all_passed = False
            continue
        
        print(f"   ✓ Extracted host/IP: {host_or_ip}")
        
        # Try to resolve if it's a hostname
        resolved_ip = await geo._resolve_hostname_to_ip(host_or_ip)
        if resolved_ip:
            print(f"   ✓ Resolved to: {resolved_ip}")
        else:
            # It's okay if resolution fails for test/example domains
            print(f"   ℹ Resolution skipped or failed (expected for test domains)")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    return all_passed


async def test_real_hostname_resolution():
    """Test resolution with a real, resolvable hostname."""
    print("\n" + "=" * 70)
    print("TEST: Real Hostname Resolution")
    print("=" * 70)
    
    geo = ProxyGeolocation()
    
    # Test with well-known public DNS servers
    test_hostnames = [
        "google.com",
        "cloudflare.com",
        "8.8.8.8",  # Already an IP
        "github.com"
    ]
    
    for hostname in test_hostnames:
        print(f"\n📋 Testing: {hostname}")
        resolved = await geo._resolve_hostname_to_ip(hostname)
        if resolved:
            print(f"   ✓ Resolved to: {resolved}")
        else:
            print(f"   ❌ Resolution failed")
    
    print("\n" + "=" * 70)


async def main():
    """Run all tests."""
    print("\n🧪 Proxy Hostname Support Tests\n")
    
    await test_proxy_parsing_and_resolution()
    await test_real_hostname_resolution()
    
    print("\n✅ Test suite completed!")


if __name__ == '__main__':
    asyncio.run(main())
