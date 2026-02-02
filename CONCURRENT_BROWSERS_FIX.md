# Concurrent Visible Browsers and Imported Useragents Fix

## Problem Statement

The user reported the following issues with RPA mode:

1. **Concurrent Visible Browsers Not Working**: When setting concurrent browsers to 2, only 1 visible browser was opening
2. **Imported Useragents Not Loading**: Imported useragents were not being used in RPA mode
3. **No Auto-Restart**: When a visible browser was closed manually, it was not being replaced
4. **Terminology**: The label "THREAD" should be renamed to "Concurrent"

## Changes Made

### 1. UI Label Change (Line 20220)
**Before:**
```python
traffic_layout.addWidget(QLabel('THREAD:'))
```

**After:**
```python
traffic_layout.addWidget(QLabel('Concurrent:'))
```

- Changed the label from "THREAD:" to "Concurrent:" to better reflect what the setting does
- Updated tooltip text to be more descriptive

### 2. RPA Mode Concurrent Browser Logic (Lines 19353-19477)

#### Key Changes:

**A. Removed Retry Limit**
- **Before**: Browsers would stop after `max_retries = 3` failures
- **After**: Browsers run continuously in an infinite loop `while self.running:`
- This ensures that N concurrent browsers are always maintained

**B. Improved Logging**
- Added logging to show when imported useragents are loaded:
  ```python
  if self.browser_manager.imported_useragents:
      self.emit_log(f'✓ Imported useragents loaded: {len(self.browser_manager.imported_useragents)} user agents available')
  ```

**C. Changed Terminology**
- All log messages now use "Concurrent" instead of "Thread"
- Examples:
  - `[Thread X]` → `[Concurrent X]`
  - `num_threads` → `num_concurrent` (variable name)
  - "threads" → "concurrent browsers" (in messages)

**D. Auto-Restart Feature**
- Each concurrent browser now runs in a continuous loop
- When a browser closes (normally or due to user action), it immediately restarts
- Only stops when:
  1. User clicks STOP button (`self.running = False`)
  2. No more proxies available (if proxy mode is enabled)

**E. Small Delay Between Starts**
- Added `await asyncio.sleep(0.5)` between starting each concurrent browser
- Prevents resource contention when opening multiple browsers simultaneously

### 3. Imported Useragents Already Working

The imported useragents functionality was already implemented correctly:
- `BrowserManager.__init__` initializes `self.imported_useragents = []` (Line 18329)
- `AutomationTask.__init__` passes imported useragents to browser manager (Line 18562)
- `BrowserManager.create_context` uses imported useragents if available (Lines 18394-18396)

**Added Enhancement**: Now logs when imported useragents are loaded, so users can confirm they're being used

## How It Works Now

### Normal Operation (e.g., 5 Concurrent Browsers)

1. User sets "Concurrent: 5" in the UI
2. User clicks START with RPA mode enabled
3. System starts 5 concurrent browser processes
4. Each browser:
   - Creates a visible browser context
   - Executes the RPA script
   - When finished (or closed), immediately restarts
   - Continues indefinitely until user clicks STOP

### With Imported Useragents

1. User imports useragents via "Import User Agents" button
2. System loads and stores them in `self.imported_useragents`
3. When RPA mode starts, logs: "✓ Imported useragents loaded: X user agents available"
4. Each browser randomly selects from imported useragents instead of generating new ones
5. Confirmation appears in logs: "✓ Using imported user agent"

### Auto-Restart Behavior

**Scenario**: User has 5 concurrent browsers running and manually closes 2 of them

**Result**: 
- System detects the browsers closed
- Immediately logs: "[Concurrent X] Browser closed, immediately restarting..."
- Two new browsers open automatically
- Total concurrent browsers maintained: 5

## Testing

Two test suites verify the changes:

### test_comprehensive_changes.py
- Verifies all existing functionality still works
- Updated to check for "Concurrent" label
- ✅ All 8 tests pass

### test_concurrent_browsers.py (NEW)
- Specifically tests the new concurrent browser features
- Verifies:
  - Label changed from "THREAD" to "Concurrent"
  - Continuous loop implementation
  - Auto-restart functionality
  - Imported useragents logging
  - Terminology updates
- ✅ All 6 tests pass

## Code Quality

- ✅ Python syntax validated
- ✅ All existing tests pass
- ✅ New test coverage for concurrent browser features
- ✅ Backward compatible (config keys remain the same)

## User Benefits

1. **Predictable Behavior**: Setting concurrent browsers to N actually opens N browsers
2. **True Concurrency**: All N browsers run simultaneously, not sequentially
3. **Continuous Operation**: Browsers auto-restart indefinitely until stopped
4. **Visibility**: Clear logging shows when imported useragents are loaded and used
5. **Better UX**: "Concurrent" label is more intuitive than "THREAD"
6. **Resilience**: If a browser crashes or is closed, it's immediately replaced
