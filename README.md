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
   - Target URL configuration
   - Number of visits
   - Content vs Sponsored interaction ratios
   - Platform selection (Desktop/Android)

2. **Behavior Tab**
   - Browser settings (Headless mode)
   - Human behavior simulation
   - Scroll depth configuration
   - Mouse movement and idle pauses
   - Consent & popup auto-handler

3. **Sponsored Content Tab**
   - Ad network blocklist (read-only)
   - Safe sponsored element selectors
   - Confidence threshold adjustment

4. **RPA Script Tab**
   - JSON-based script editor
   - Save/Load scripts
   - Custom automation workflows

5. **Control & Logs Panel**
   - Start/Stop automation
   - Real-time logging
   - Status monitoring

### Example RPA Script

```json
{
  "name": "Sample Automation",
  "steps": [
    {"type": "newPage"},
    {"type": "navigate", "url": "https://example.com"},
    {"type": "wait", "duration": 2000},
    {"type": "scroll", "depth": 50},
    {"type": "click", "selector": ".promo-button"},
    {"type": "closePage"}
  ]
}
```

## 🔧 Features

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
