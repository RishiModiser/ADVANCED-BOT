# Humanex Version 5 - Advanced Simulation Traffic

---

## 🎉 **NEW: TRUE 1-CLICK STANDALONE - NO INSTALLATION NEEDED!**

### 🚀 Quick Start (For End Users)

**Want to run the bot with just ONE CLICK? No Python, no installation, no setup?**

#### For Windows Users:
1. Double-click: **`ONE_CLICK_BUILD.bat`** (first time only - builds the executable)
2. Then double-click: **`dist/ADVANCED-BOT.exe`** (your standalone bot!)

#### For Linux/Mac Users:
1. Run: **`./ONE_CLICK_BUILD.sh`** (first time only - builds the executable)
2. Then run: **`./dist/ADVANCED-BOT`** (your standalone bot!)

**📖 Complete Guide:** See [QUICK_START_STANDALONE.md](QUICK_START_STANDALONE.md) for full instructions.

✅ **After building once, you can distribute the executable to ANY computer - no Python needed!**

---

## 🎯 Overview

Humanex Version 5 is an enterprise-grade RPA (Robotic Process Automation) system designed for advanced traffic simulation and behavioral analysis. It provides sophisticated tools for:
- UX testing and user behavior simulation
- Sponsored content simulation
- Internal promotion testing
- Consent & popup automation
- Traffic behavior research
- Custom RPA script execution

## 🔐 New: Advanced Security

**Enterprise-grade protection against cracking and unauthorized use!**

This bot now includes:
- 🔑 **License Key System** - Hardware-bound licenses prevent unauthorized distribution
- 🔒 **AES-256 Encryption** - Protects sensitive configs (proxies, API keys, credentials)
- 🛡️ **Integrity Checking** - Detects file tampering with SHA-256 checksums
- ⏱️ **Rate Limiting** - Prevents abuse and ensures stability
- 🎭 **Secure Logging** - Auto-masks IPs, passwords, and sensitive data
- 💻 **Hardware Binding** - Each license works only on authorized machine

**First run automatically creates a 30-day trial license!**

📖 See [SECURITY_FEATURES.md](SECURITY_FEATURES.md) for complete documentation.

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

### Option 1: Standalone Executable (Recommended for End Users)

**⚡ 1-Click Solution - No Python Required!**

If you want to run the bot with just one click without installing Python or any dependencies:

1. **Download or Build the Standalone Executable**
   
   **To build from source:**
   ```bash
   # Windows
   build_standalone.bat
   
   # Linux/Mac
   ./build_standalone.sh
   ```

2. **Run the Executable**
   - **Windows**: Double-click `dist/ADVANCED-BOT.exe`
   - **Linux/Mac**: Run `./dist/ADVANCED-BOT`

3. **First Run**: The application will automatically download Playwright browsers (takes 1-2 minutes)

✅ **That's it! Your bot is ready to use with just one click!**

📖 **For detailed instructions, see [STANDALONE_GUIDE.md](STANDALONE_GUIDE.md)**

---

### Option 2: Python Installation (For Developers)

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

This error occurs when Playwright browsers are not installed or system dependencies are missing. The bot now includes **enhanced automatic installation** that attempts to resolve this issue automatically.

**Automatic Installation (Enhanced!):**
When you run the bot and it detects a missing browser or system dependencies, it will:
1. Automatically download and install Chromium browser
2. Install required system dependencies (Linux only)
3. Retry the initialization process
4. Start working without manual intervention

The auto-install now detects more error types including:
- Missing browser binaries
- Missing system libraries (libgobject, libnss, libatk, etc.)
- Launch failures

**Manual Installation (if needed):**
If automatic installation fails, you can install manually:

1. Install browser: `playwright install chromium`
2. Install system dependencies (Linux only): `sudo playwright install-deps chromium`
3. Or use the helper: `python setup_browser.py`

If the issue persists, ensure you have installed the requirements:
```bash
pip install -r requirements.txt
playwright install chromium
# On Linux, also run:
sudo playwright install-deps chromium
```

**CI/CD Environments:**
For CI/CD pipelines, use the provided GitHub Actions workflow (`.github/workflows/test.yml`) which automatically installs browsers and system dependencies during the build process.

## 🖥️ Usage

### Running the Application

#### Standalone Executable (1-Click)
```bash
# Windows
dist\ADVANCED-BOT.exe

# Linux/Mac  
./dist/ADVANCED-BOT
```

#### Python Version
```bash
python advanced_bot.py
```

**Note:** On first launch, the app will check if browsers are installed and show a warning if they're missing.

### GUI Features

The application provides a modern, fully responsive GUI with improved navigation. All features are accessible from the left sidebar:

#### Navigation Sections

1. **🔧 Website Traffic**
   - **Multiple Target URLs** - Add and manage multiple URLs in a list
   - **Visit Type Selection** - Direct, Referral, Search, or HIGH CPC/CPM visits
   - **Search Settings** - Keyword and target domain for Google search visits
   - **HIGH CPC/CPM Mode Settings** - Advanced CPC/CPM optimization with multi-tab interaction
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
   - **📥 Import Settings** (NEW in v5.2)
     - **Import User Agents** - Load custom user agents from text file
     - **Import Cookies** - Load cookies from JSON file
     - Both work seamlessly with all instances and proxies

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

### 🆕 New Features (Latest Update - v5.2)

#### UI & Performance Improvements
- **Spinner Arrows** - Visible up/down arrows on all numeric inputs (QSpinBox) for better UX
- **Instant Instance Management** - Zero delays between thread starts (previously 0.5s delay removed)
- **Immediate Restart** - Instance restart time reduced from 1s to 0.001s for near-instant recovery
- **Stealth Mode** - Removed "Chrome is being controlled by automated test software" banner
- **Import User Agents** - Load custom user agents from text file, automatically rotated across instances
- **Import Cookies** - Load cookies from JSON file, automatically injected into all browser contexts

For detailed information, see [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md)

### Features from v5.1

#### Proxy Geolocation & Display
- **Automatic proxy location fetching** before browser launch
- **Real-time proxy location display** in browser window (top-right corner)
- Shows country and IP address: "Proxy: USA | IP: 31.56.70.200"
- Supports IP:PORT:USERNAME:PASSWORD format
- Location info logged for each browser session
- Seamless integration with proxy rotation

#### Ad Detection & Interaction (Demo/Test Only)
- **Intelligent ad detection** using multiple selectors
- **Human-like ad interaction**:
  - Smooth scrolling to ads
  - Proper wait time for ad content to load
  - Natural mouse movements over ad area
  - Realistic viewing duration (2-5 seconds)
- **Configurable via GUI** - Enable/disable in Traffic Behaviour tab
- **Safety first**: Only works with demo/test ads, real ad networks blocked
- Interacts with 1-3 ads per page randomly

#### Text Highlighting (Human Behavior)
- **Random text highlighting** while browsing
- Simulates natural reading behavior
- Features:
  - Selects 2-8 words at a time
  - Smooth mouse drag animation
  - Brief pause to "view" highlighted text
  - 20% chance during browsing sessions
- **Enable/disable option** in Traffic Behaviour tab
- Makes automation more human-like and natural

#### Enhanced Multi-Browser Management
- Proxy fetched **before** each browser opens
- Each thread gets unique proxy with location
- Real-time location display in each browser
- Proper thread management for 5, 10, or more browsers simultaneously

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

### 🔐 Advanced Security Features (NEW!)

The bot now includes enterprise-grade security to protect against cracking and unauthorized use:

#### Protection Features
- **License Key System** - Hardware-bound licenses with expiration dates
- **Configuration Encryption** - AES-256 encryption for sensitive data (proxies, API keys)
- **File Integrity Checking** - Detects tampering with SHA-256 checksums
- **Rate Limiting** - Prevents abuse with configurable request limits
- **Secure Logging** - Automatic masking of sensitive information (IPs, passwords, keys)
- **Environment Validation** - Detects suspicious execution environments
- **Hardware Binding** - Licenses tied to specific machines

#### Security Benefits
- ✅ Prevents unauthorized distribution and use
- ✅ Protects credentials and sensitive configuration
- ✅ Detects code tampering and modifications
- ✅ Ensures legitimate usage patterns
- ✅ Protects sensitive data in logs

📖 **For complete security documentation, see [SECURITY_FEATURES.md](SECURITY_FEATURES.md)**

#### Quick Security Setup
1. Install dependencies: `pip install -r requirements.txt` (includes cryptography)
2. First run automatically creates a 30-day trial license
3. Licensed users get hardware-bound licenses with custom expiration
4. All sensitive configs are automatically encrypted

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
- **NEW**: Automatic sensitive data masking

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
