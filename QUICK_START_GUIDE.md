# Quick Start Guide - New Features

## 🚀 How to Use New Features

### 1. Proxy with Location Display

**Setup:**
1. Go to **Proxy Settings** tab
2. Enable "✅ Enable Proxy"
3. Add your proxies in format:
   ```
   31.56.70.200:8080:l89g6-ttl-0:TywlutsUqvIMSy1
   ```
4. Each line is one proxy

**What happens:**
- Bot fetches proxy location automatically
- Browser shows: "Proxy: USA | IP: 31.56.70.200" in top-right corner
- Location logged for each browser

---

### 2. Multi-threaded Browsers

**Setup:**
1. Go to **Website Traffic** tab
2. Set "Threads" to desired number (e.g., 5, 10)
3. If you have 5 threads and 5 proxies → 5 browsers open at once

**What happens:**
- Thread 1: Opens with proxy 1 → Shows location → Browses
- Thread 2: Opens with proxy 2 → Shows location → Browses
- (All run simultaneously in real-time)

---

### 3. Ad Detection & Interaction

**Setup:**
1. Go to **Traffic Behaviour** tab
2. Enable "✅ Enable Ad Detection & Interaction"
3. ⚠️ Only works with demo/test ads (not real ad networks)

**What happens:**
- Bot scans page for ads
- Scrolls smoothly to each ad
- Waits 1-2 seconds for ad to load
- Moves mouse over ad naturally
- Views for 2-5 seconds
- Logs: "Found 3 ad(s), interacting with 2..."

---

### 4. Text Highlighting

**Setup:**
1. Go to **Traffic Behaviour** tab
2. Enable "✏️ Enable Text Highlighting"

**What happens:**
- While browsing, randomly highlights text
- Selects 2-8 words
- Smooth mouse drag animation
- Brief pause, then deselects
- Makes behavior look more human

---

## 📋 Complete Workflow Example

### Scenario: Run 5 browsers with proxies

**Step 1: Add Proxies**
```
Proxy Settings → Enable Proxy
Add 5 proxies (one per line):
31.56.70.200:8080:user1:pass1
45.123.45.67:8080:user2:pass2
192.168.1.1:8080:user3:pass3
10.0.0.1:8080:user4:pass4
172.16.0.1:8080:user5:pass5
```

**Step 2: Configure Behavior**
```
Traffic Behaviour → Enable Text Highlighting
Traffic Behaviour → Enable Ad Detection
```

**Step 3: Set Traffic**
```
Website Traffic → Add URLs
Website Traffic → Threads: 5
Website Traffic → Visits: 5
```

**Step 4: Start**
```
Control → Click Start
Watch in Logs tab
```

**Expected Output:**
```
Profile 1 | Platform: desktop | URL: example.com
Creating browser context...
✓ Using proxy: http://31.56.70.200:8080
✓ Proxy Location: USA, IP: 31.56.70.200
Browser context created successfully
Opening example.com...
[INFO] Detecting ads on page...
[INFO] ✓ Found 3 ad(s) on page
[INFO] Interacting with ad 1/2...
[INFO] Viewing ad naturally...
Starting time-based browsing (120-240 seconds)...
✓ Profile 1 completed successfully

(Same for profiles 2-5, running simultaneously)
```

---

## 🎯 Tips

### For Best Results:

1. **Proxies:**
   - Use working proxies only
   - Mix geographic locations
   - Enable rotation for authenticity

2. **Threads:**
   - Start with 5 to test
   - Increase to 10-20 for scale
   - Watch RAM usage

3. **Ad Interaction:**
   - Only enable for pages with demo ads
   - Not for real advertising networks
   - Check logs to verify detection

4. **Text Highlighting:**
   - Works best on text-heavy pages
   - Natural pause after highlight
   - 20% chance per scroll action

---

## 🔍 Monitoring

**Watch Logs for:**
- ✓ "Proxy Location: ..." - Confirms location fetched
- ✓ "Found X ad(s)" - Confirms ad detection
- ✓ "Interacting with ad..." - Confirms ad interaction
- ⚠️ Warnings - Non-critical issues
- ✗ Errors - Issues requiring attention

---

## 📱 Visual Indicators

**In Browser Window:**
```
┌─────────────────────────────────────────┐
│                      [Proxy: USA | IP: 31.56.70.200] │
│                                         │
│  Your Website Content Here              │
│                                         │
└─────────────────────────────────────────┘
```
- Fixed position (top-right)
- Dark background
- Green text
- Always visible
- Doesn't interfere with page

---

## ⚠️ Important Notes

### Safety:
- Ad interaction works ONLY with demo/test ads
- Real ad networks (Google, Facebook) are BLOCKED
- Use on your own websites for testing

### Performance:
- Each browser: ~200-300 MB RAM
- 5 browsers: ~1-1.5 GB RAM
- Monitor system resources

### Proxy Format:
- Primary: `IP:PORT:USERNAME:PASSWORD`
- Also supports: `IP:PORT`, `USER:PASS@IP:PORT`
- Mix formats in same list

---

## 🆘 Troubleshooting

**Issue:** Proxy location not showing
- Check proxy format is correct
- View logs for connection status
- Verify proxy is working

**Issue:** No ads detected
- Page may not have demo ads
- Check if ads use standard selectors
- Enable debug logging

**Issue:** Text highlighting not working
- Ensure feature is enabled
- Page needs text content
- Check logs for errors

**Issue:** Browsers not opening
- Check thread count vs available RAM
- Verify Playwright is installed
- Review initialization logs

---

## 📞 Support

For issues or questions:
1. Check logs for error messages
2. Review FEATURE_DEMO.md for details
3. Run test_new_features.py for validation
4. Open issue on GitHub

---

**Version:** 5.1
**Last Updated:** 2026-01-25
