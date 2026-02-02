# Quick Start Guide - RPA Script Creator

## How to Use (After Fix)

### Step 1: Open RPA Script Creator
1. Launch the application
2. Click on "🧩 RPA Script Creator" in the left sidebar

### Step 2: Build Your Workflow
Drag actions from **Action Toolbox** (left) to **Workflow Steps** (center):

**Available Actions:**
- ➕ **New Tab** - Opens a new browser tab
- 🌐 **Access Website** - Navigates to a URL
- ⏱ **Time** - Waits for a specified duration
- 📜 **Scroll** - Scrolls the page
- 🖱 **Click Element** - Clicks a page element
- ⌨ **Input Text** - Types text into a form field
- ❌ **Close Page** - Closes the current tab

### Step 3: Configure Each Action
Click on any step in **Workflow Steps** to configure it in **Step Configuration** (right):

**New Tab** - No configuration needed

**Access Website:**
- URL: Enter website URL (e.g., https://example.com)
- Timeout: Set wait time in milliseconds (default: 30000ms)

**Time:**
- Timeout Waiting: Fixed or Random
- Duration: Wait time in milliseconds (default: 2000ms)
- Max Duration: If Random mode, maximum wait time

**Scroll:**
- Scroll Type: Smooth (animated) or Auto (instant)
- Position: Top, Intermediate, or Bottom
- Depth: How far to scroll (0-100%)
- Min Scroll Speed: Minimum pause between scrolls (default: 100ms)
- Max Scroll Speed: Maximum pause between scrolls (default: 500ms)

**Click Element:**
- Selector: CSS selector of element to click (e.g., .button-class, #button-id)

**Input Text:**
- Selector: CSS selector of input field
- Text: Text to type into the field

**Close Page** - No configuration needed

### Step 4: Start Automation
1. Click "🎮 Control" in the left sidebar
2. Click "START AUTOMATION" button

**NEW: Auto-Enable Prompt**
If you have workflow steps but RPA Mode is not enabled, you'll see:

```
┌─────────────────────────────────────────────────┐
│             Enable RPA Mode?                     │
├─────────────────────────────────────────────────┤
│ You have workflow steps in the RPA Script       │
│ Creator but RPA Mode is not enabled.             │
│                                                   │
│ Would you like to enable RPA Mode to execute    │
│ your workflow steps?                             │
│                                                   │
│         [Yes]              [No]                  │
└─────────────────────────────────────────────────┘
```

Click **"Yes"** and the system will:
1. ✅ Enable RPA Mode automatically
2. ✅ Sync your workflow to JSON
3. ✅ Start automation
4. ✅ Execute all your actions with configured settings!

### Example Workflow

Here's a simple workflow to test a website:

1. **New Tab** → Opens a fresh browser tab
2. **Access Website** → https://example.com (Timeout: 30000ms)
3. **Time** → Wait 2000ms (2 seconds)
4. **Scroll** → Smooth scroll to 50% depth (Speed: 100-500ms)
5. **Time** → Wait 2000ms (2 seconds)
6. **Close Page** → Closes the tab

### Tips

✅ **All configuration parameters now work!**
- Set custom timeouts for slow websites
- Choose smooth or instant scrolling
- Control scroll speed for realistic behavior
- Configure wait times for page loading

✅ **Visual Builder and JSON are always synced**
- Changes in visual builder update JSON editor
- Changes in JSON editor update visual builder
- Use whichever you prefer!

✅ **No need to manually enable RPA mode**
- System prompts you automatically
- One click to enable and start

✅ **Clear error messages**
- If something is missing, you'll get helpful guidance
- Error messages tell you exactly what to do

### Troubleshooting

**Q: My workflow doesn't execute**
A: Make sure to click "START AUTOMATION" and confirm the RPA mode prompt

**Q: My configuration changes don't work**
A: This has been fixed! All configuration parameters now work properly

**Q: How do I know if RPA mode is enabled?**
A: Check the "Traffic Behaviour" tab - there's a "✅ Enable RPA Mode Only" checkbox

**Q: Can I edit the JSON directly?**
A: Yes! Switch to the "JSON Editor" tab in RPA Script Creator

**Q: My scroll speed setting is ignored**
A: This has been fixed! Min/Max speed settings now work correctly

### Advanced Features

**Save/Load Scripts:**
- Click "💾 Save Script" to save your workflow as JSON
- Click "📂 Load Script" to load a saved workflow
- Use "🔄 Sync Visual ↔ JSON" to manually sync

**Multiple Concurrent Browsers:**
- In Control tab, set "Concurrent Threads" to run multiple browsers
- Each browser runs the same workflow independently

**Proxy Support:**
- Enable proxy in "Proxy Settings" tab
- Each browser instance gets a different proxy

### What's New (This Fix)

✅ **Navigate/Access Website action now uses timeout configuration**
   - Before: Timeout was always 30 seconds
   - After: You can set any timeout you want

✅ **Scroll action now uses all configuration parameters**
   - Before: Scroll type and speed were ignored
   - After: Smooth/Auto, min/max speed all work

✅ **Auto-enable RPA mode prompt**
   - Before: Users didn't know they needed to enable RPA mode
   - After: System prompts automatically

✅ **Better error messages**
   - Before: Generic "no script provided" error
   - After: Clear guidance on adding actions or enabling RPA mode

✅ **Always sync workflow**
   - Before: Only synced if workflow_steps existed
   - After: Always syncs to ensure consistency

### Testing Your Fix

Run the test suite to verify everything works:

```bash
python test_rpa_functionality.py
```

You should see:
```
✓ All action mappings passed!
✓ All default configurations defined!
✓ Script structure is valid!
✓ All tests passed!
```

### Summary

The RPA Script Creator now works exactly as expected:
1. Drag and drop actions ✅
2. Configure parameters ✅
3. Click START AUTOMATION ✅
4. System prompts for RPA mode ✅
5. Actions execute with your settings ✅

**Problem solved!** 🎉
