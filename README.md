# Humanex Version 5 - Advanced Simulation Traffic

## 🎯 Overview

Humanex Version 5 is an enterprise-grade RPA (Robotic Process Automation) system designed for advanced traffic simulation and behavioral analysis. It provides sophisticated tools for:
- UX testing and user behavior simulation
- Sponsored content simulation
- Internal promotion testing
- Consent & popup automation
- Traffic behavior research
- Custom RPA script execution

## ⚠️ Important Safety Notice

**This system is designed ONLY for legitimate use cases:**
- Testing your own websites
- UX research on controlled environments
- Internal promotion testing
- Consent flow validation

**STRICTLY FORBIDDEN:**
- Clicking real third-party ad networks (Google Ads, AdSense, DoubleClick, etc.)
- Traffic fraud or click fraud
- Unauthorized automation
- Any illegal activities

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/RishiModiser/ADVANCED-BOT.git
cd ADVANCED-BOT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **⚠️ IMPORTANT: Install Playwright browsers** (Required!)
```bash
playwright install chromium
```

Or use the setup helper:
```bash
python setup_browser.py
```

### Troubleshooting

**Error: "Failed to initialize browser"**

This error occurs when Playwright browsers are not installed. To fix:

1. Run: `playwright install chromium`
2. Or: `python -m playwright install chromium`
3. Or: `python setup_browser.py`

If the issue persists, ensure you have installed the requirements:
```bash
pip install -r requirements.txt
playwright install chromium
```

## 🖥️ Usage

### Running the Application

```bash
python advanced_bot.py
```

**Note:** On first launch, the app will check if browsers are installed and show a warning if they're missing.

### GUI Features

The application provides a modern, fully responsive GUI with improved navigation. All features are accessible from the left sidebar:

#### Navigation Sections

1. **🔧 Website Traffic**
   - **Multiple Target URLs** - Add and manage multiple URLs in a list
   - **Visit Type Selection** - Direct, Referral, or Search visits
   - **Search Settings** - Keyword and target domain for Google search visits
   - **Traffic Settings** - Number of visits, concurrent threads, total thread limit
   - **Content vs Sponsored interaction ratios**
   - **Platform Mix** - Select Desktop, Android, or both for mixed traffic

2. **🧠 Traffic Behaviour**
   - Browser settings (Always visible mode)
   - Human behavior simulation with advanced interactions
   - Scroll depth configuration
   - Mouse movement and idle pauses
   - **Enable Interaction** - Advanced human behavior (click posts, explore pages, follow links)
   - **Page Visit Settings** - Enable extra pages and set maximum pages to visit
   - Consent & popup auto-handler

3. **🌐 Proxy Settings**
   - Enable/disable proxy
   - Auto-detect proxy type from protocol prefix or use default selection (HTTP, HTTPS, SOCKS5)
   - Multiple proxy format support:
     - Simple: `ip:port` or `host:port`
     - With auth: `user:pass@host:port`
     - Alternative auth: `host:port:username:password`
     - Protocol prefix: `http://host:port`, `https://host:port`, `socks5://host:port`
   - **Drag & Drop** - Drag and drop .txt files directly into the proxy list
   - **Import from File** - Import proxies from .txt file via file picker
   - **Proxy Counter** - Real-time display of loaded proxy count
   - Rotation settings (rotate per session/profile)
   - Automatic timezone/location handling based on proxy

4. **🧩 RPA Script Creator**
   - **Visual Builder** - Drag and drop interface for creating workflows
   - **Action Toolbox** - New Tab, Access Website, Time, Scroll, Click, Input, Close Page
   - **Enhanced Actions:**
     - **Access Website** - URL and timeout configuration
     - **Time** - Fixed or Random wait modes
     - **Scroll** - Smooth/Auto types with speed configuration
   - JSON-based script editor
   - Save/Load scripts
   - Custom automation workflows

5. **🎮 Control** (NEW in v5)
   - Start/Stop automation buttons
   - Real-time status display
   - Step-by-step usage instructions
   - Centralized control panel

6. **📋 Logs** (NEW in v5)
   - Dedicated full-screen log viewer
   - Real-time activity tracking
   - Thread-specific logging
   - Dark theme for better readability
   - Clear logs functionality

### Example RPA Script

```json
{
  "name": "Sample Automation",
  "steps": [
    {"type": "newPage"},
    {"type": "navigate", "url": "https://example.com", "timeout": 30000},
    {"type": "wait", "duration": 2000, "mode": "Fixed"},
    {"type": "scroll", "depth": 50, "scroll_type": "Smooth", "min_speed": 100, "max_speed": 500},
    {"type": "click", "selector": ".promo-button"},
    {"type": "closePage"}
  ]
}
```

## 🔧 Features

### 🆕 New Features (Latest Update)

#### Multiple URL Support
- Add multiple target URLs to a list
- Random URL selection per browser instance
- Each browser opens a different URL
- Easy URL management with add/remove buttons

#### Thread Management
- Configure concurrent browser threads (e.g., 20 chromes at once)
- Set total thread limit to control automation scale
- Real-time thread count tracking in logs
- Ideal for large-scale operations with proxies

#### Platform Mixing
- Select Desktop, Android, or both platforms
- Mixed traffic simulation with random platform selection
- Realistic user agent and viewport handling

#### Enhanced Search Visit
- Google search integration with keyword support
- Automatic target domain detection in top 10 results
- Human-like typing and interaction
- Continues with normal behavior after finding target

#### Advanced Human Behavior
- Click posts, links, and explore pages naturally
- Random mouse movements across viewport
- Variable interaction counts (5-15 per visit)
- Realistic reading pauses (8-25 seconds)

#### Improved Proxy Management
- Import proxies from .txt files or drag & drop
- Support for multiple proxy formats:
  - Simple format: `ip:port`
  - With authentication: `user:pass@ip:port` or `ip:port:username:password`
  - Protocol-specific: `http://ip:port`, `https://ip:port`, `socks5://ip:port`
  - Mixed formats in same list (auto-detection)
- Real-time proxy count display
- Automatic rotation per session/profile
- Support for HTTP, HTTPS, SOCKS5, and IP formats
- Ready for timezone/location/fingerprint customization

#### Enhanced RPA Script Creator
- Updated action names (New Tab, Access Website, Time)
- Configurable timeouts and wait modes
- Scroll type selection (Smooth/Auto)
- Scroll speed configuration (min/max range)

### Browser Automation
- Playwright-based Chromium automation
- Headful and headless modes
- Isolated browser contexts per profile
- Robust exception handling
- Auto-restart on crash

### Fingerprint & User Agent Engine
- Rotating user agents (Desktop/Android)
- Viewport randomization
- Timezone and locale spoofing
- Hardware concurrency variance
- Anti-detection measures

### Human Behavior Simulation
- Random scroll depth and speed
- Natural mouse movements
- Idle pauses and dwell time
- Focus/blur simulation
- Variable interaction timing

### Cookie & Popup Auto-Handler
- Automatic consent detection
- Cookie banner acceptance
- GDPR popup handling
- Notification prompts
- Modal overlay detection
- Multiple detection strategies:
  - Button text matching
  - ARIA labels
  - Role-based detection

### Sponsored Content Click Engine
- Ratio-based interaction logic
- Safe element detection
- Confidence scoring system
- Strict ad network blocklist
- Element visibility verification
- Size and position validation

### Safety Features
- **Ad Network Blocklist**: Automatically blocks interactions with known ad networks
- **Element Confidence System**: Only clicks elements meeting confidence threshold
- **URL Validation**: Checks all URLs before interaction
- **Safe Selectors**: Uses whitelisted selectors for sponsored content
- **Abort on Detection**: Immediately stops if ad network detected

## 🛡️ Security & Compliance

### Blocklist
The system blocks all interactions with:
- googleads
- doubleclick
- adsense
- adservice
- googlesyndication
- Other major ad networks

### Safe Sponsored Selectors
Only interacts with elements containing:
- `.promo`
- `.sponsored-demo`
- `.featured`
- `.recommended`
- `[data-sponsored="true"]`
- `[data-promo="true"]`

### Logging
- All actions are logged
- File-based logs in `logs/` directory
- Real-time GUI logs
- Timestamp and severity tracking

## 📁 Project Structure

The application is contained in a single file: `advanced_bot.py`

### Example Files:
- `example_script.json` - Sample RPA automation script
- `example_proxies.txt` - Example proxy list with all supported formats

### Internal Classes:
- `AppGUI` - Main GUI application
- `BrowserManager` - Playwright browser management
- `FingerprintManager` - User agent and fingerprint rotation
- `HumanBehavior` - Human-like interaction simulation
- `ConsentManager` - Cookie and popup handler
- `SponsoredClickEngine` - Safe sponsored content interaction
- `ScriptExecutor` - RPA script execution engine
- `ProxyManager` - Proxy configuration
- `LogManager` - Centralized logging
- `AutomationWorker` - Background automation thread

## 🔍 Configuration Options

### Traffic Settings
- **Content Interaction %**: Percentage of visits that interact with regular content (default: 85%)
- **Sponsored Interaction %**: Percentage of visits that interact with safe sponsored content (default: 15%)

### Behavior Settings
- **Scroll Depth**: How far to scroll on pages (30-100%)
- **Mouse Movement**: Enable/disable mouse movement simulation
- **Idle Pauses**: Enable/disable natural reading pauses

### Sponsored Content
- **Confidence Threshold**: Minimum confidence score for element interaction (0.0-1.0, default: 0.7)

## 📊 System Requirements

- Python 3.8+
- 4GB RAM minimum
- Internet connection
- Windows, macOS, or Linux

## 🧪 Testing

The system is designed for testing purposes only. Use it to:
- Test your own website's UX flows
- Validate consent mechanisms
- Research traffic patterns on your own sites
- Test internal promotional content

## ⚠️ Legal Disclaimer

This software is provided for legitimate testing and research purposes only. Users are solely responsible for ensuring their use complies with:
- Terms of service of websites being tested
- Local and international laws
- Ethical guidelines
- Platform policies

The developers assume no liability for misuse of this software.

## 📝 License

This project is provided as-is for educational and testing purposes.

## 🤝 Contributing

This is an enterprise-grade RPA tool. Contributions should maintain:
- Professional code quality
- Comprehensive error handling
- Security best practices
- Clear documentation

## 📧 Support

For issues or questions, please open an issue on the GitHub repository.

---

**Built with enterprise-grade standards for professional RPA automation.**
