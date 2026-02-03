# 🌐 Proxy Configuration Guide for ADVANCED-BOT

## Overview

ADVANCED-BOT supports **ALL types of proxies** including:
- ✅ HTTP Proxies
- ✅ HTTPS Proxies  
- ✅ SOCKS5 Proxies
- ✅ Authenticated Proxies (with username and password)
- ✅ IPv4 and IPv6 Proxies

## Quick Start

### For geo.g-w.info Users (and similar proxy providers)

If your proxies look like this:
```
geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg
geo.g-w.info:10800:FIFRlLg56bDDOhRy:EyIqa6s0H1koZieb
```

**IMPORTANT:** These proxies are likely **SOCKS5** proxies. You have two options:

#### Option 1: Select SOCKS5 in Proxy Type (Recommended)
1. Go to the **Proxy Settings** tab
2. Enable proxy by checking "✅ Enable Proxy"
3. In the **Proxy Type** dropdown, select **SOCKS5**
4. Paste your proxies in the text area
5. The bot will automatically parse them as SOCKS5 proxies

#### Option 2: Add Protocol Prefix
Add `socks5://` to each proxy:
```
socks5://geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg
socks5://geo.g-w.info:10800:FIFRlLg56bDDOhRy:EyIqa6s0H1koZieb
```

## Supported Proxy Formats

### 1. Simple Format (IP:Port)
```
192.168.1.1:8080
10.0.0.1:3128
proxy.example.com:8080
```
⚠️ Uses the protocol selected in "Proxy Type" dropdown (HTTP/HTTPS/SOCKS5)

### 2. Authenticated Format - Style 1 (user:pass@host:port)
```
username:password@192.168.1.1:8080
myuser:mypass@proxy.example.com:3128
```
⚠️ Uses the protocol selected in "Proxy Type" dropdown

### 3. Authenticated Format - Style 2 (host:port:username:password)
```
192.168.1.1:8080:username:password
proxy.example.com:3128:myuser:mypass
geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg
```
⭐ **This is the format used by geo.g-w.info and many premium proxy providers**

⚠️ Uses the protocol selected in "Proxy Type" dropdown

### 4. With Explicit Protocol (http://, https://, socks5://)

#### HTTP Protocol
```
http://192.168.1.1:8080
http://username:password@192.168.1.1:8080
http://192.168.1.1:8080:username:password
```

#### HTTPS Protocol
```
https://192.168.1.1:8080
https://username:password@192.168.1.1:8080
https://192.168.1.1:8080:username:password
```

#### SOCKS5 Protocol
```
socks5://192.168.1.1:1080
socks5://username:password@192.168.1.1:1080
socks5://geo.g-w.info:10800:username:password
```

✅ **When you specify the protocol explicitly, it overrides the "Proxy Type" dropdown setting**

### 5. IPv6 Support
```
[2001:db8::1]:8080
[2001:db8::1]:8080:username:password
user:pass@[2001:db8::1]:8080
socks5://[2001:db8::1]:1080
```

## How to Choose the Right Protocol

### When to use HTTP
- Most common proxy type
- Standard web proxies
- Default choice for general-purpose proxies

### When to use HTTPS
- Secure proxies with SSL/TLS encryption
- When you need encrypted proxy connections
- Some proxy providers require HTTPS

### When to use SOCKS5
- Premium proxy providers (like geo.g-w.info, luminati, oxylabs, etc.)
- Residential proxies
- Mobile proxies
- When you need better anonymity
- **Try SOCKS5 if HTTP doesn't work!**

## Common Issues and Solutions

### Issue: "Proxies not connecting" or "Connection refused"

**Solution 1: Try different proxy types**
Your proxies might be a different protocol than you think. Try this order:
1. First try **SOCKS5** (most common for premium proxies)
2. If that doesn't work, try **HTTP**
3. Finally, try **HTTPS**

**Solution 2: Check your proxy format**
Make sure your proxies are in one of the supported formats listed above.

**Solution 3: Add protocol prefix**
Instead of relying on the dropdown, explicitly specify the protocol:
```
socks5://your.proxy.com:10800:username:password
```

### Issue: "Proxy parsed but not working"

**Check:**
1. ✅ Is the proxy provider online?
2. ✅ Are your credentials correct?
3. ✅ Are you using the correct protocol (HTTP/HTTPS/SOCKS5)?
4. ✅ Is the proxy IP whitelisted (if required by your provider)?
5. ✅ Have you exceeded your proxy bandwidth/request limit?

## Visual Guide: Using the UI

### Step 1: Enable Proxy
1. Go to **Proxy Settings** tab
2. Check **✅ Enable Proxy**

### Step 2: Select Protocol Type
Choose from the dropdown:
- **HTTP** - for standard web proxies
- **HTTPS** - for secure proxies
- **SOCKS5** - for premium proxies (recommended for geo.g-w.info)

### Step 3: Add Your Proxies
Paste your proxies in the text area. The counter will show:
```
📊 Proxies loaded: 5
Protocol breakdown: SOCKS5: 5
```

This confirms:
- ✅ Number of proxies successfully parsed
- ✅ Which protocol will be used for each proxy

### Step 4: Verify
The protocol breakdown shows you exactly what protocol each proxy will use:
- If you see "HTTP: 5", all proxies will use HTTP
- If you see "SOCKS5: 5", all proxies will use SOCKS5
- If you see "HTTP: 3 | SOCKS5: 2", you have a mix

## Mixed Proxy Lists

You can mix different formats in the same list:

```
# Simple HTTP proxy
192.168.1.1:8080

# Authenticated HTTP proxy
user:pass@192.168.1.2:8080

# SOCKS5 proxy (explicit)
socks5://192.168.1.3:1080

# Premium proxy (will use selected Proxy Type)
geo.g-w.info:10800:username:password

# SOCKS5 premium proxy (explicit)
socks5://geo.g-w.info:10800:username2:password2
```

When you use mixed formats:
- Proxies **with** `protocol://` prefix will use that protocol
- Proxies **without** prefix will use the "Proxy Type" dropdown setting

## Example: Complete Setup for geo.g-w.info

1. ✅ Enable Proxy checkbox
2. ✅ Select **SOCKS5** in Proxy Type dropdown
3. ✅ Paste your proxies:
```
geo.g-w.info:10800:KWGBBxI0G8SSRwX0:g1GI0bd49JUi58Pg
geo.g-w.info:10800:FIFRlLg56bDDOhRy:EyIqa6s0H1koZieb
geo.g-w.info:10800:gyCqjgiqkXxUJ4yM:QXMXfhm6145DzQUv
```
4. ✅ Verify the counter shows: "Protocol breakdown: SOCKS5: 3"
5. ✅ Start the bot!

## Advanced Tips

### Tip 1: Protocol Auto-Detection
The bot doesn't auto-detect protocol based on port number because:
- Port 8080 could be HTTP, HTTPS, or SOCKS5
- Port 10800 could be any protocol
- It's better to be explicit than to guess wrong

**Always specify the protocol** if you're unsure.

### Tip 2: Test One Proxy First
If you're not sure which protocol to use:
1. Add just ONE proxy
2. Try it with SOCKS5 first
3. If it works, add the rest
4. If it doesn't work, try HTTP, then HTTPS

### Tip 3: Import from File
You can save your proxies in a `.txt` file and use the **📁 Import from File** button.

File example (`my_proxies.txt`):
```
# My SOCKS5 proxies from geo.g-w.info
socks5://geo.g-w.info:10800:user1:pass1
socks5://geo.g-w.info:10800:user2:pass2
socks5://geo.g-w.info:10800:user3:pass3
```

## Troubleshooting Checklist

- [ ] Proxies are in a supported format
- [ ] Correct protocol selected (try SOCKS5 for premium proxies)
- [ ] Credentials are correct (no typos)
- [ ] Proxy provider is online
- [ ] IP is whitelisted (if required)
- [ ] Not exceeding bandwidth/request limits
- [ ] Protocol breakdown shows expected protocol
- [ ] Tried adding explicit protocol prefix (socks5://)

## Summary

✅ **The bot supports ALL proxy types** (HTTP, HTTPS, SOCKS5)

✅ **All authentication formats are supported**

✅ **For geo.g-w.info proxies, use SOCKS5**

✅ **Always check the protocol breakdown** to verify which protocol will be used

✅ **When in doubt, add the protocol prefix explicitly** (socks5://, http://, https://)

---

**Still having issues?** Make sure you've selected the correct protocol type in the dropdown, or add the protocol prefix explicitly to your proxies.
