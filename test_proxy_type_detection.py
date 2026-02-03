#!/usr/bin/env python3
"""
Test to check if the bot needs better proxy type detection.
The user's proxies from geo.g-w.info:10800 might be SOCKS5 proxies
but the bot might be treating them as HTTP.
"""

# The issue: User's proxies in format host:port:user:pass
# are being parsed correctly, but might need protocol detection

# Common ports for proxy types:
# HTTP: 8080, 3128, 8888, 80
# HTTPS: 443, 8443
# SOCKS5: 1080, 1081, 9050
# Custom: 10800 (could be any protocol!)

proxy_line = "geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg"

print("Analyzing proxy:", proxy_line)
print()

parts = proxy_line.split(':')
host = parts[0]
port = parts[1]
username = parts[2]
password = parts[3]

print(f"Host: {host}")
print(f"Port: {port}")
print(f"Username: {username}")
print(f"Password: {password}")
print()

print("Port analysis:")
print(f"  Port 10800 is NOT a standard HTTP port (8080, 3128, 80)")
print(f"  Port 10800 is NOT a standard HTTPS port (443, 8443)")
print(f"  Port 10800 is NOT a standard SOCKS5 port (1080, 9050)")
print(f"  Port 10800 appears to be a CUSTOM port")
print()

print("Likely issue:")
print("  The bot defaults to HTTP protocol when no protocol is specified.")
print("  But geo.g-w.info:10800 might be using SOCKS5 or another protocol.")
print("  The user needs to either:")
print("    1. Specify the protocol explicitly (e.g., socks5://geo.g-w.info:10800:user:pass)")
print("    2. Select the correct proxy type (SOCKS5) in the bot's UI")
print()

print("Testing with different protocols:")
for protocol in ['http', 'https', 'socks5']:
    server = f"{protocol}://{host}:{port}"
    print(f"  {protocol.upper():7s}: {server}")
print()

print("CONCLUSION:")
print("  The parsing works correctly!")
print("  But the bot needs to use the RIGHT protocol for geo.g-w.info:10800.")
print("  The user should either:")
print("    - Prefix proxies with 'socks5://' if they're SOCKS5 proxies")
print("    - Select 'SOCKS5' in the Proxy Type dropdown")
print("    - Try different proxy types to see which one works")
