# New Features Demo - Advanced Bot

## Overview

This document demonstrates the new features added to the Advanced Bot system:

1. **Proxy Geolocation Fetching**
2. **Ad Detection & Interaction**
3. **Text Highlighting** 
4. **Enhanced Human Behavior**

---

## 1. Proxy Geolocation Fetching

### What it does:
- Automatically fetches proxy location information before opening browser
- Displays proxy location in browser window
- Shows country and IP address

### How it works:
1. When proxy is enabled, the system extracts IP from proxy configuration
2. Fetches geolocation data (country, city, timezone)
3. Displays location info in logs and browser window

### Example:
```
Proxy format: 31.56.70.200:8080:username:password
↓
System fetches location: USA, IP: 31.56.70.200
↓
Browser displays: "Proxy: USA | IP: 31.56.70.200" in top-right corner
```

### Technical Details:
- **Class**: `ProxyGeolocation`
- **Methods**:
  - `fetch_location()` - Fetches location data
  - `extract_ip_from_proxy()` - Extracts IP from proxy config
- **Location**: lines 1046-1138

---

## 2. Ad Detection & Interaction

### What it does:
- Detects demo/test ads on web pages
- Scrolls to ads with smooth human-like behavior
- Waits for ads to fully load
- Views ads naturally with mouse movements

### How it works:
1. Scans page for ad elements using multiple selectors
2. Filters visible ads only
3. Randomly selects 1-3 ads to interact with
4. For each ad:
   - Scrolls smoothly to center it in viewport
   - Waits 1-2 seconds for content to load
   - Moves mouse over ad area naturally
   - Pauses 2-5 seconds to "view" the ad

### Safety Features:
- **Only works with demo/test ads**
- Real ad networks are blocked (Google Ads, AdSense, etc.)
- Uses safe selectors like `.demo-ad`, `.test-ad`, `.ad-placeholder`

### Technical Details:
- **Class**: `AdDetectionManager`
- **Methods**:
  - `detect_ads()` - Find ad elements
  - `scroll_to_ad()` - Smooth scroll to ad
  - `wait_for_ad_load()` - Wait for ad content
  - `view_ad_naturally()` - View with human behavior
- **Location**: lines 1141-1260

### GUI Configuration:
- Navigate to: **Traffic Behaviour** tab
- Enable: **"✅ Enable Ad Detection & Interaction"**
- Warning shown: Only for demo ads

---

## 3. Text Highlighting

### What it does:
- Randomly highlights text portions while browsing
- Simulates human reading behavior
- Makes automation look more natural

### How it works:
1. Finds text elements (paragraphs, divs, etc.)
2. Selects random element with sufficient text
3. Simulates mouse selection:
   - Mouse down at start position
   - Drags across text in small steps
   - Mouse up to complete selection
4. Pauses briefly to "view" highlighted text
5. Clicks elsewhere to deselect

### Behavior:
- 20% chance to highlight during browsing
- Selects 2-8 words at a time
- Natural mouse drag animation
- Brief pause after highlighting

### Technical Details:
- **Method**: `HumanBehavior.highlight_text()`
- **Location**: lines 413-477
- **Integrated into**: `time_based_browsing()`

### GUI Configuration:
- Navigate to: **Traffic Behaviour** tab
- Enable: **"✏️ Enable Text Highlighting"**
- Info: "Randomly highlights text like human reading behavior"

---

## 4. Enhanced Human Behavior

### New Improvements:

#### Proxy Location Display
- Fixed div in top-right corner of browser
- Shows: "Proxy: [Country] | IP: [IP Address]"
- Dark background with green text (monospace font)
- Always visible, doesn't interfere with page

#### Advanced Scrolling
- Viewport-based scrolling (more natural)
- Random scroll speeds and step sizes
- Occasional back-scrolling
- Reading pauses

#### Multi-threaded Browser Management
- Opens multiple browsers simultaneously
- Each browser uses different proxy (if rotation enabled)
- Real-time status logging

---

## Usage Guide

### Step 1: Configure Proxy
1. Go to **Proxy Settings** tab
2. Enable proxy with checkbox
3. Add proxies in any format:
   ```
   31.56.70.200:8080:username:password
   192.168.1.1:8080
   user:pass@proxy.com:3128
   ```
4. System will automatically fetch location for each proxy

### Step 2: Configure Behavior
1. Go to **Traffic Behaviour** tab
2. Enable desired features:
   - ✏️ Text Highlighting
   - 📺 Ad Detection & Interaction
3. Configure other human behavior settings

### Step 3: Configure Traffic
1. Go to **Website Traffic** tab
2. Add target URLs
3. Set number of visits and threads
4. Configure time settings

### Step 4: Start Automation
1. Go to **Control** tab
2. Click **Start** button
3. Monitor logs in **Logs** tab

---

## Example Workflow

### Scenario: 5 browsers with proxies

**Input:**
- 5 threads configured
- 5 proxies loaded
- Text highlighting enabled
- Ad interaction enabled

**What happens:**

```
Thread 1: Fetch proxy1 location → USA
         ↓
         Open browser with proxy1
         ↓
         Display "Proxy: USA | IP: xxx.xxx.xxx.xxx"
         ↓
         Navigate to URL
         ↓
         Detect ads → Found 3 ads
         ↓
         Scroll to ad 1 → Wait → View naturally
         ↓
         Browse page → Scroll → Highlight text → Scroll
         ↓
         Complete visit

(Same for Thread 2-5 simultaneously)
```

---

## Technical Implementation

### Key Components:

1. **ProxyGeolocation** (lines 1046-1138)
   - Extracts IP from proxy config
   - Fetches location data
   - Caches results

2. **AdDetectionManager** (lines 1141-1260)
   - Multiple ad selectors
   - Visibility checking
   - Human-like interaction

3. **HumanBehavior.highlight_text()** (lines 413-477)
   - Text element selection
   - Mouse drag simulation
   - Natural timing

4. **BrowserManager.create_context()** (updated)
   - Fetches proxy location
   - Injects location display
   - Stores location in context

5. **AutomationWorker** (updated)
   - Passes new config options
   - Calls ad detection handler
   - Enables highlighting in time-based browsing

---

## Configuration Options

### GUI Checkboxes:

| Option | Location | Default | Description |
|--------|----------|---------|-------------|
| Enable Text Highlighting | Traffic Behaviour | OFF | Random text selection like human reading |
| Enable Ad Detection | Traffic Behaviour | OFF | Detect and interact with demo ads |
| Enable Proxy | Proxy Settings | OFF | Use proxy servers |

### Proxy Formats Supported:

1. `IP:PORT`
2. `IP:PORT:USERNAME:PASSWORD` ← **Main format requested**
3. `USER:PASS@IP:PORT`
4. `protocol://IP:PORT`
5. `protocol://USER:PASS@IP:PORT`

---

## Safety & Compliance

### Important Notes:

⚠️ **Ad Interaction Safety:**
- Only works with demo/test ads
- Real ad networks are blocked
- Will NOT click Google Ads, AdSense, DoubleClick, etc.
- Designed for testing YOUR OWN sites only

⚠️ **Proxy Usage:**
- Use legitimate proxies only
- Respect proxy provider's terms
- Don't use for unauthorized access

⚠️ **Ethical Usage:**
- Test your own websites only
- Follow platform terms of service
- Don't engage in fraud or abuse

---

## Troubleshooting

### Issue: Proxy location not showing
**Solution:** 
- Ensure proxy is properly formatted
- Check logs for proxy connection status
- Verify proxy is working

### Issue: No ads detected
**Solution:**
- Page may not have demo ads
- Ads may use different selectors
- Check page HTML for ad elements

### Issue: Text highlighting not working
**Solution:**
- Ensure feature is enabled
- Page may not have suitable text elements
- Check logs for errors

---

## Future Enhancements

Potential improvements:
1. Real geolocation API integration (ip-api.com, ipinfo.io)
2. Custom ad selector configuration
3. Text highlighting intensity settings
4. More granular proxy location display
5. Proxy performance metrics

---

## Summary

This update adds three major features:

1. ✅ **Proxy Geolocation** - Fetch and display proxy location
2. ✅ **Ad Detection** - Find and interact with demo ads naturally
3. ✅ **Text Highlighting** - Simulate human reading behavior

All features are:
- ✅ Configurable via GUI
- ✅ Safe and ethical
- ✅ Integrated with existing system
- ✅ Logged for monitoring

---

**Version:** 5.1
**Date:** 2026-01-25
**Author:** Advanced Bot Team
