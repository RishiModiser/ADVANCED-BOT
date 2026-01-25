# Windows Desktop Automation System - Usage Guide

## Quick Start Guide

### Installation

1. **Install Python 3.8+**
   ```bash
   python3 --version  # Should be 3.8 or higher
   ```

2. **Clone and Setup**
   ```bash
   git clone https://github.com/RishiModiser/ADVANCED-BOT.git
   cd ADVANCED-BOT
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Run the Application**
   ```bash
   python advanced_bot.py
   ```

## GUI Walkthrough

### Main Interface

The application window is divided into two main sections:
- **Left Panel**: Configuration tabs
- **Right Panel**: Control & Logs

### Configuration Tabs

#### 1. Website & Traffic Tab

Configure your automation target and traffic parameters:

- **Target URL**: The website you want to test (e.g., `https://your-website.com`)
- **Number of Visits**: How many times to visit the site (1-1000)
- **Content Interaction %**: Percentage of visits that interact with regular content (0-100)
  - Default: 85%
  - This means 85% of visits will just browse regular content
- **Sponsored Interaction %**: Percentage that interact with safe sponsored content (0-100)
  - Default: 15%
  - This means 15% will look for safe sponsored elements
- **Platform**: Choose between `desktop` or `android` user agents
  - Desktop: Uses typical desktop browser fingerprints
  - Android: Uses mobile device fingerprints

#### 2. Behavior Tab

Fine-tune the human-like behavior simulation:

- **Headless Mode**: Run browser without visible window
  - Unchecked (default): Browser window visible
  - Checked: Browser runs in background
  
- **Scroll Depth %**: How far to scroll down pages (30-100)
  - 30: Scroll only top of page
  - 70 (default): Scroll most of page
  - 100: Scroll to bottom

- **Enable Mouse Movement Simulation**: Add natural mouse movements
  - Checked (default): Simulates mouse movements
  - Creates more realistic traffic patterns

- **Enable Idle Pauses**: Add natural reading pauses
  - Checked (default): Pauses 2-5 seconds between actions
  - Simulates users reading content

- **Auto-handle Cookie Banners**: Automatically click consent buttons
  - Checked (default): Finds and clicks "Accept" buttons
  - Handles GDPR popups automatically

- **Auto-handle Popups**: Handle modal overlays
  - Checked (default): Closes unwanted popups
  - Keeps automation running smoothly

#### 3. Sponsored Content Tab

View and configure safety rules:

- **Ad Network Blocklist** (Read-only)
  - Shows all blocked ad networks
  - Includes: googleads, doubleclick, adsense, etc.
  - **System will NEVER click these**

- **Safe Selectors** (Read-only)
  - Shows CSS selectors for safe sponsored content
  - Only elements matching these patterns can be clicked
  - Examples: `.promo`, `.sponsored-demo`, `.featured`

- **Confidence Threshold** (0.0-1.0)
  - Minimum confidence score required to click
  - Default: 0.7
  - Higher = More selective (fewer clicks)
  - Lower = More permissive (more clicks)

#### 4. RPA Script Tab

Create and manage custom automation scripts:

- **Script Editor**: Write JSON-based automation workflows
- **Save Script**: Export script to JSON file
- **Load Script**: Import script from JSON file

**Script Format:**
```json
{
  "name": "My Automation",
  "steps": [
    {"type": "newPage"},
    {"type": "navigate", "url": "https://example.com"},
    {"type": "wait", "duration": 2000},
    {"type": "scroll", "depth": 50},
    {"type": "click", "selector": ".button"},
    {"type": "input", "selector": "#email", "text": "test@example.com"},
    {"type": "closePage"}
  ]
}
```

**Available Step Types:**
- `newPage`: Create a new browser tab
- `navigate`: Go to a URL
  - Parameters: `url` (string)
- `wait`: Pause for milliseconds
  - Parameters: `duration` (integer, milliseconds)
- `scroll`: Scroll page
  - Parameters: `depth` (integer, 0-100, optional)
- `click`: Click an element
  - Parameters: `selector` (CSS selector)
- `input`: Type into an input field
  - Parameters: `selector` (CSS selector), `text` (string)
- `closePage`: Close current tab

### Control Panel (Right Side)

#### Start Automation
1. Configure all settings in the left panel tabs
2. Click **Start Automation** button (green)
3. Watch real-time logs appear
4. Status changes to "Running..."

#### Stop Automation
- Click **Stop** button (red) to halt automation
- Graceful shutdown - finishes current action
- Browser closes automatically

#### Logs Section
- Real-time logging display
- Color-coded: Green text on dark background
- Shows all automation activities
- Timestamps included
- Click **Clear Logs** to reset display

## Common Use Cases

### Use Case 1: Basic UX Testing

**Goal**: Test if your website loads and scrolls properly

**Configuration:**
- Target URL: `https://your-website.com`
- Number of Visits: 5
- Platform: desktop
- Headless Mode: Unchecked (so you can watch)

**Steps:**
1. Enter your website URL
2. Set visits to 5
3. Leave other settings at defaults
4. Click Start Automation
5. Watch browser open and interact with site

### Use Case 2: Consent Flow Testing

**Goal**: Test cookie consent banners

**Configuration:**
- Target URL: `https://your-site-with-cookies.com`
- Number of Visits: 10
- Auto-handle Cookie Banners: Checked
- Headless Mode: Unchecked

**Steps:**
1. Configure as above
2. Click Start Automation
3. Watch logs for "Clicked consent button" messages
4. Verify banner is properly handled

### Use Case 3: Sponsored Content Testing

**Goal**: Test internal promotional content

**Configuration:**
- Target URL: `https://your-site.com/products`
- Content Interaction %: 70
- Sponsored Interaction %: 30
- Add `.your-promo-class` to sponsored selectors (in code)

**Important**: Ensure your sponsored content uses safe selectors like:
- Class: `promo`, `sponsored-demo`, `featured`
- Attribute: `data-promo="true"`

### Use Case 4: Mobile Traffic Simulation

**Goal**: Simulate mobile device traffic

**Configuration:**
- Platform: android
- Number of Visits: 20
- Headless Mode: Checked (for efficiency)

**Steps:**
1. Set platform to android
2. Configure visits and ratios
3. Enable headless mode
4. Click Start Automation

### Use Case 5: Custom RPA Workflow

**Goal**: Run specific test scenario

**Configuration:**
- Use RPA Script tab
- Create custom JSON script
- Save for reuse

**Example Script**: Login and navigate
```json
{
  "name": "Login Test",
  "steps": [
    {"type": "newPage"},
    {"type": "navigate", "url": "https://your-site.com/login"},
    {"type": "wait", "duration": 2000},
    {"type": "input", "selector": "#username", "text": "testuser"},
    {"type": "input", "selector": "#password", "text": "testpass"},
    {"type": "click", "selector": "#login-btn"},
    {"type": "wait", "duration": 3000},
    {"type": "closePage"}
  ]
}
```

## Safety Guidelines

### ✅ Allowed Use Cases
- Testing your own websites
- UX research on sites you control
- Internal promotion testing
- Consent mechanism validation
- Traffic pattern research (owned properties)

### ❌ Prohibited Use Cases
- Clicking real ad networks (Google Ads, etc.)
- Click fraud or traffic fraud
- Testing third-party sites without permission
- Generating fake engagement
- Any illegal activities

### Built-in Safety Features

1. **Ad Network Blocklist**
   - Automatically blocks known ad networks
   - Prevents accidental ad clicks
   - Cannot be disabled

2. **Element Confidence Scoring**
   - Validates element before clicking
   - Checks visibility, size, position
   - Only clicks high-confidence elements

3. **Safe Selector Whitelist**
   - Only clicks elements with safe classes
   - Must match predefined patterns
   - Protects against accidental ad clicks

4. **URL Validation**
   - Checks all URLs before interaction
   - Blocks ad network domains
   - Aborts on detection

## Troubleshooting

### Issue: "Browser initialization error"

**Solution:**
```bash
playwright install chromium
```

### Issue: GUI doesn't open

**Cause**: Missing display libraries

**Solution (Linux):**
```bash
sudo apt-get install libxcb-xinerama0 libxcb-cursor0
```

### Issue: "Import Error: libEGL.so.1"

**Cause**: Missing graphics libraries (Linux)

**Solution:**
```bash
sudo apt-get install libegl1 libxkbcommon-x11-0
```

### Issue: Consent buttons not being clicked

**Check:**
1. Website actually has consent buttons
2. Auto-handle Cookie Banners is enabled
3. Button text matches known patterns (check logs)

**Solution**: Add custom button text to `CONSENT_BUTTON_TEXTS` in code

### Issue: No sponsored elements found

**Check:**
1. Page actually has elements with safe selectors
2. Elements are visible (not hidden)
3. Confidence threshold isn't too high

**Solution**: 
- Lower confidence threshold
- Add your own selectors to `SPONSORED_SELECTORS`
- Check element classes match safe patterns

## Advanced Configuration

### Adding Custom Consent Button Text

Edit `advanced_bot.py`:
```python
CONSENT_BUTTON_TEXTS = [
    'accept', 'accept all', 'agree', 'allow all',
    'your custom text',  # Add here
]
```

### Adding Custom Sponsored Selectors

Edit `advanced_bot.py`:
```python
SPONSORED_SELECTORS = [
    '.promo', '.sponsored-demo', '.featured',
    '.your-custom-class',  # Add here
]
```

### Using a Proxy

Currently requires code modification. Edit `BrowserManager.__init__()`:
```python
self.proxy_manager.proxy_enabled = True
self.proxy_manager.proxy_server = 'http://proxy:8080'
self.proxy_manager.proxy_username = 'user'
self.proxy_manager.proxy_password = 'pass'
```

## Log Files

Logs are automatically saved to:
```
logs/automation_YYYYMMDD_HHMMSS.log
```

Each run creates a new log file with timestamp.

## Performance Tips

1. **Use Headless Mode** for large runs (faster, less resource-intensive)
2. **Lower visit count** during testing, increase for production runs
3. **Clear logs** periodically to keep GUI responsive
4. **Close application** between runs to free memory

## Best Practices

1. **Start Small**: Test with 1-5 visits first
2. **Watch First Run**: Run with headless off initially
3. **Check Logs**: Always review logs for errors
4. **Test Incrementally**: Add one feature at a time
5. **Use Scripts**: Save successful configurations as RPA scripts
6. **Respect Rate Limits**: Don't overwhelm servers
7. **Own Properties Only**: Only test sites you control

## Support

For issues or questions:
1. Check this guide
2. Review log files
3. Open GitHub issue with:
   - Error message
   - Configuration used
   - Log output
   - Steps to reproduce

---

**Remember**: This tool is for legitimate testing purposes only. Always ensure your use complies with applicable laws and terms of service.
