# Windows Desktop Automation System

## 🎯 Overview

Enterprise-grade RPA (Robotic Process Automation) software for:
- UX testing
- Sponsored content simulation
- Internal promotion testing
- Consent & popup automation
- Traffic behavior research

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

3. Install Playwright browsers:
```bash
playwright install chromium
```

## 🖥️ Usage

### Running the Application

```bash
python advanced_bot.py
```

### GUI Features

The application provides a fully responsive GUI with the following sections:

1. **Website & Traffic Tab**
   - **Multiple Target URLs** - Add and manage multiple URLs in a list
   - **Visit Type Selection** - Direct, Referral, or Search visits
   - **Search Settings** - Keyword and target domain for Google search visits
   - **Traffic Settings** - Number of visits, concurrent threads, total thread limit
   - **Content vs Sponsored interaction ratios**
   - **Platform Mix** - Select Desktop, Android, or both for mixed traffic

2. **Traffic Behaviour Tab** (formerly "Behavior")
   - Browser settings (Always visible mode)
   - Human behavior simulation with advanced interactions
   - Scroll depth configuration
   - Mouse movement and idle pauses
   - **Enable Interaction** - Advanced human behavior (click posts, explore pages, follow links)
   - **Page Visit Settings** - Enable extra pages and set maximum pages to visit
   - Consent & popup auto-handler

3. **Proxy Settings Tab**
   - Enable/disable proxy
   - Proxy type selection (HTTP, HTTPS, SOCKS5)
   - Proxy list management (manual entry or import from file)
   - **Import from File** - Import proxies from .txt file
   - Rotation settings (rotate per session/profile)
   - Automatic timezone/location handling based on proxy

4. **RPA Script Tab**
   - **Visual Builder** - Drag and drop interface for creating workflows
   - **Action Toolbox** - New Tab, Access Website, Time, Scroll, Click, Input, Close Page
   - **Enhanced Actions:**
     - **Access Website** - URL and timeout configuration
     - **Time** - Fixed or Random wait modes
     - **Scroll** - Smooth/Auto types with speed configuration
   - JSON-based script editor
   - Save/Load scripts
   - Custom automation workflows

5. **Control & Logs Panel**
   - Start/Stop automation
   - Real-time logging with thread tracking
   - Status monitoring

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
- Import proxies from .txt files
- Support for HTTP, HTTPS, SOCKS5, and IP formats
- Automatic rotation per session/profile
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
