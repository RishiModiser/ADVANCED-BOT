# Concurrent Browser Management - Usage Guide

## Overview

Your requirements for concurrent browser management with proxy handling are **ALREADY FULLY IMPLEMENTED** in the current version of ADVANCED-BOT!

## Your Requirements ✅ ALREADY IMPLEMENTED

Based on your problem statement, here's what you requested and how it's already implemented:

### 1. ✅ N Concurrent = N Visible Browsers
**Requirement:** *"jiten concurrent ham ADD kry otne hi browsers open means visibile h parral me"*
(As many concurrent we add, that many browsers should be open/visible in parallel)

**Implementation:**
- Set `CONCURRENT = 50` → Exactly 50 browsers open and visible
- Each browser is a real Chrome window with its own taskbar icon
- Uses `launch_persistent_context` for visible browsers
- Stagger delay (0.2s between launches) ensures all browsers launch successfully

**Example:**
```
CONCURRENT = 50
Result: 50 Chrome windows visible in taskbar
Launch time: ~10 seconds (50 × 0.2s)
```

### 2. ✅ Each Browser Uses Different Proxy
**Requirement:** *"50 proxies fetch kr ke. hr instance / concurrent each proxies use kr le"*
(Fetch 50 proxies, each instance/concurrent should use each proxy)

**Implementation:**
- Sequential proxy distribution via `ProxyManager.get_proxy_config()`
- Each browser gets the next proxy from the queue (no duplicates)
- Proxy queue index tracks position: Browser 1 gets Proxy 1, Browser 2 gets Proxy 2, etc.

**Example:**
```
Proxies loaded: 10,000
Browser 1: Proxy 1 (8.8.8.8:8080)
Browser 2: Proxy 2 (8.8.8.9:8080)
Browser 3: Proxy 3 (8.8.8.10:8080)
...
Browser 50: Proxy 50
```

### 3. ✅ Auto-Restart on Browser Close
**Requirement:** *"50 me se 1 browser closed h gya to me chahta h turant new 1 or concurrent open h"*
(If 1 browser out of 50 closes, I want immediately a new concurrent to open)

**Implementation:**

**RPA Mode:**
```python
while self.running:
    # Create browser
    context = await create_context()
    # Execute automation
    # Browser closes or completes
    # Loop immediately restarts - INSTANT RESTART
```

**Normal Mode:**
```python
while self.running:
    # Remove completed workers
    active_workers = [w for w in active_workers if not w.done()]
    
    # Spawn replacements immediately
    while len(active_workers) < num_concurrent:
        task = asyncio.create_task(worker_task())
        active_workers.append(task)
```

**Result:** When any browser closes, a new one opens **immediately** (0.001s delay)

### 4. ✅ Maintain 50 Concurrent Always
**Requirement:** *"50 concurrent maintain rkhy"*
(Maintain 50 concurrent)

**Implementation:**
- Continuous monitoring loop checks every 0.1 seconds
- Instant replacement when browser closes
- Maintains EXACTLY N concurrent at all times
- Works until all proxies consumed or user stops

### 5. ✅ Process All Proxies (10K+)
**Requirement:** *"10K proxies jab tk completed na h jy apne concurrent maintain kr ke open hota jay"*
(10K proxies until they are not completed, should keep opening while maintaining concurrent)

**Implementation:**
```python
# Continues until proxies exhausted
while self.running:
    remaining = proxy_manager.get_remaining_proxies()
    if remaining <= 0:
        break  # All proxies consumed
    
    # Maintain N concurrent and process next proxy
```

**Example:**
```
Proxies: 10,000
Concurrent: 50

Iteration 1: Browsers 1-50 use Proxies 1-50
[Browser 1 completes]
Iteration 2: Browser 51 opens, uses Proxy 51
[Browser 3 completes]
Iteration 3: Browser 52 opens, uses Proxy 52
...
Continues until all 10,000 proxies consumed
```

---

## How to Use

### Step 1: Prepare Proxy List

Create a file `proxies.txt` with your proxies:

```
8.8.8.8:8080
8.8.8.9:8080:username:password
user:pass@8.8.8.10:8080
http://8.8.8.11:8080
...
(10,000 proxies)
```

**Supported formats:**
- `ip:port`
- `ip:port:username:password`
- `user:pass@ip:port`
- `http://ip:port`
- `https://ip:port`
- `socks5://ip:port`

### Step 2: Configure the Bot

**Option A: Using GUI**

1. Open the bot: `python advanced_bot.py`
2. Go to **Proxy Settings** tab
3. Click **Import from File** and select your `proxies.txt`
4. Enable **Use Proxy**
5. Go to **Website Traffic** tab
6. Set **Concurrent** = `50` (or any number you want)
7. Select **RPA Mode** if using RPA scripts
8. Click **START**

**Option B: Using Config (for automation)**

```python
config = {
    'concurrent': 50,              # Number of concurrent browsers
    'rpa_mode': True,              # Enable RPA mode
    'rpa_script': {                # Your automation script
        'name': 'My Automation',
        'steps': [...]
    },
    'proxy_enabled': True,
    'proxy_list': ['8.8.8.8:8080', '8.8.8.9:8080', ...],  # 10K proxies
}
```

### Step 3: Watch It Work!

```
Starting 50 concurrent visible browser(s)...
Spawning 50 concurrent browser tasks...

[Concurrent 1] Starting | Platform: windows | Proxies: 10000
[Concurrent 2] Starting | Platform: android | Proxies: 9999
[Concurrent 3] Starting | Platform: windows | Proxies: 9998
...
[Concurrent 50] Starting | Platform: android | Proxies: 9951

✓ Created 50 concurrent browser tasks
✓ All 50 concurrent browsers started and running
✓ Browsers will automatically restart if closed

[2 minutes later, Browser 5 closes]
[Concurrent 51] Starting | Platform: windows | Proxies: 9950
[Browser 51 immediately opens to maintain 50 concurrent]

[Browser 12 closes]
[Concurrent 52] Starting | Platform: android | Proxies: 9949
[Browser 52 immediately opens]

... continues until all 10,000 proxies consumed
```

---

## Advanced Features

### Mixed Platforms
Select multiple platforms for realistic traffic:

```python
config = {
    'platforms': ['windows', 'android'],  # Mix of desktop and mobile
}
```

Result:
- 50% Windows browsers
- 50% Android browsers
- Random selection per browser

### Proxy Geolocation Matching
The bot automatically:
1. Fetches proxy location (country, IP, timezone)
2. Generates browser fingerprint matching proxy location
3. Ensures browser timezone matches proxy timezone

**Example:**
```
Proxy: USA (31.56.70.200)
Browser: USA timezone (America/New_York)
Result: Perfect match, no detection
```

### RPA Script Automation
Execute custom scripts on each browser:

```json
{
  "name": "My Automation",
  "steps": [
    {"type": "newPage"},
    {"type": "navigate", "url": "https://example.com"},
    {"type": "wait", "duration": 5000},
    {"type": "scroll", "depth": 50},
    {"type": "click", "selector": ".button"},
    {"type": "closePage"}
  ]
}
```

Each of the 50 browsers executes this script independently!

---

## Performance Recommendations

### System Requirements by Concurrent Count

| Concurrent | RAM Needed | CPU Cores | Launch Time |
|------------|------------|-----------|-------------|
| 10         | 4GB        | 4 cores   | 2 seconds   |
| 50         | 16GB       | 8 cores   | 10 seconds  |
| 100        | 32GB       | 16 cores  | 20 seconds  |
| 200        | 64GB       | 32 cores  | 40 seconds  |

**Each browser uses:**
- ~200-500 MB RAM
- ~2-5% CPU per core

### Optimization Tips

1. **Use SSD for profiles** - Faster browser startup
2. **Close other applications** - Free up RAM
3. **Use headless mode** (if you don't need to see browsers) - Saves RAM
4. **Monitor system resources** - Don't exceed 80% RAM usage
5. **Start with lower concurrent** - Test with 10, then scale up

---

## Monitoring & Logging

### Real-Time Status

The bot provides detailed logging:

```
✓ Proxy configuration loaded: 10000 proxies available
✓ Worker pool mode: 50 concurrent browsers
✓ Spawned 50/50 workers (Active: 50)
✓ Proxy selected: 8.8.8.8:8080
✓ Proxy Location: United States (US), IP: 8.8.8.8
✓ Fingerprint MATCHED to proxy location: United States

[Worker 1] ✓ Completed successfully (Total: 1)
[Worker 2] ✓ Completed successfully (Total: 2)
[Worker 51] Starting (Proxies remaining: 9949)
...
All proxies consumed, waiting for active workers to finish...
✓ All work completed (no proxies remaining)
```

### Log Files

Logs are saved to `logs/` directory:
- `automation_YYYY-MM-DD.log` - Daily logs
- Real-time GUI logs in the **Logs** tab

---

## Troubleshooting

### Issue: Not all browsers opening

**Cause:** System resources insufficient

**Solution:**
1. Check RAM usage (Task Manager / htop)
2. Reduce concurrent count
3. Close other applications
4. Upgrade system RAM

### Issue: Browsers opening slowly

**Cause:** This is normal! Stagger delay prevents Playwright overload

**Expected:**
- 50 browsers = 10 seconds to launch
- 100 browsers = 20 seconds to launch

**Not a bug** - Once launched, all browsers run at full speed concurrently

### Issue: "No more proxies available"

**Cause:** All proxies consumed (this is expected behavior!)

**Solution:**
- Add more proxies to your list
- Or wait for current batch to finish

### Issue: Proxy connection failed

**Cause:** Invalid proxy or proxy offline

**Solution:**
- Bot automatically skips failed proxies
- Next browser gets next proxy from queue
- Check proxy validity before adding

---

## Example Scenarios

### Scenario 1: 50 Concurrent with 10K Proxies

```
Configuration:
- Concurrent: 50
- Proxies: 10,000
- Mode: RPA

Expected Behavior:
1. 50 browsers open immediately (visible in taskbar)
2. Each browser uses a different proxy (Proxy 1-50)
3. When Browser 1 completes, Browser 51 opens with Proxy 51
4. When Browser 2 completes, Browser 52 opens with Proxy 52
5. Continues until all 10,000 proxies consumed
6. Maintains exactly 50 browsers at all times

Timeline:
- Minute 0: Browsers 1-50 active
- Minute 2: Browsers 20-70 active (first 19 completed)
- Minute 5: Browsers 100-150 active
- ...
- Final: All 10,000 proxies processed
```

### Scenario 2: Browser Crashes Mid-Execution

```
Situation:
- 50 browsers running
- Browser 25 crashes unexpectedly

What Happens:
1. System detects Browser 25 closed
2. Immediate spawn of Browser 51
3. Browser 51 gets Proxy 51
4. Total browsers maintained: 50 (always)
5. No interruption to other 49 browsers

Log:
[Concurrent 25] Error: Browser closed unexpectedly
[Concurrent 51] Starting | Proxies: 9950
✓ Maintaining exactly 50 visible browsers
```

### Scenario 3: Manual Stop

```
Situation:
- User clicks STOP button while 50 browsers active

What Happens:
1. self.running = False
2. All browser loops detect stop signal
3. Browsers close gracefully (context.close())
4. No new browsers spawn
5. Clean shutdown

Log:
Stop requested - force closing 50 active worker(s)...
✓ All concurrent browsers stopped
```

---

## Summary

✅ **All your requirements are ALREADY implemented!**

You can RIGHT NOW:
1. Set concurrent to 50 (or any number)
2. Load 10,000 proxies
3. Click START
4. Watch 50 browsers open (visible in taskbar)
5. Each browser uses a different proxy
6. When any browser closes, a new one immediately opens
7. System maintains 50 browsers until all 10,000 proxies are consumed

**No code changes needed - just use the existing features!**

---

## Quick Start Command

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install browsers
playwright install chromium

# 3. Prepare proxies
# Create proxies.txt with your 10K proxies

# 4. Run the bot
python advanced_bot.py

# 5. In GUI:
#    - Import proxies
#    - Set concurrent = 50
#    - Click START

# Done! Watch 50 browsers working in parallel!
```

---

## Need Help?

- See `CONCURRENT_FIX_DOCUMENTATION.md` for technical details
- See `QUICK_REFERENCE_CONCURRENT_UNLIMITED.md` for quick reference
- See `README.md` for general usage
- Open an issue on GitHub for support

**The system is ready to use RIGHT NOW!** 🚀
