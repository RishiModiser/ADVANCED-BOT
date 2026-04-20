# Humanex Version 5 - Advanced Simulation Traffic

## 🎯 Overview

Humanex Version 5 is an enterprise-grade RPA (Robotic Process Automation) system designed for advanced traffic simulation and behavioral analysis. It provides sophisticated tools for:
- UX testing and user behavior simulation
- Sponsored content simulation
- Internal promotion testing
- Consent & popup automation
- Traffic behavior research
- Custom RPA script execution

## 🔐 Security

**Enterprise-grade protection against cracking and unauthorized use!**

This bot includes:
- 🔒 **AES-256 Encryption** - Protects sensitive configs (proxies, API keys, credentials)
- 🛡️ **Integrity Checking** - Detects file tampering with SHA-256 checksums
- ⏱️ **Rate Limiting** - Prevents abuse and ensures stability
- 🎭 **Secure Logging** - Auto-masks IPs, passwords, and sensitive data

📖 See [SECURITY_FEATURES.md](SECURITY_FEATURES.md) for complete documentation.

## ⚠️ Important Safety Notice

**This system is designed ONLY for legitimate use cases:**
- Testing your own websites
- UX research on controlled environments
- Internal promotion testing
- Consent flow validation

**STRICTLY FORBIDDEN:**
- Clicking real third-party ad networks
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

2. Create a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

Or use the setup helper:
```bash
python setup_browser.py
```

### Run the Application

```bash
python advanced_bot.py
```

### Build an Executable

To build a single portable executable:

**Windows:**
```bat
build.bat
```

**Linux/macOS:**
```bash
chmod +x build.sh && ./build.sh
```

Or run PyInstaller directly:
```bash
pyinstaller --clean --noconfirm advanced_bot.spec
```

The resulting executable will be at `dist/advanced_bot` (or `dist/advanced_bot.exe` on Windows).

### Troubleshooting

**Error: "Failed to initialize browser"**

This error occurs when Playwright browsers are not installed. Run:

```bash
playwright install chromium
# On Linux, also run:
sudo playwright install-deps chromium
```

Or use the setup helper:
```bash
python setup_browser.py
```

## 🖥️ Usage

### GUI Features

The application provides a modern, fully responsive GUI with improved navigation. All features are accessible from the left sidebar:

#### Navigation Sections

1. **🔧 Website Traffic**
   - Multiple Target URLs - Add and manage multiple URLs in a list
   - Visit Type Selection - Direct, Referral, Search, or HIGH CPC/CPM visits
   - Search Settings - Keyword and target domain for Google search visits
   - HIGH CPC/CPM Mode Settings - Advanced CPC/CPM optimization with multi-tab interaction
   - Traffic Settings - Number of visits, concurrent threads, total thread limit
   - Content vs Sponsored interaction ratios
   - Platform Mix - Select Desktop, Android, or both for mixed traffic

2. **🧠 Traffic Behaviour**
   - Browser settings (Always visible mode)
   - Human behavior simulation with advanced interactions
   - Scroll depth configuration
   - Mouse movement and idle pauses
   - Enable Interaction - Advanced human behavior (click posts, explore pages, follow links)
   - Page Visit Settings - Enable extra pages and set maximum pages to visit
   - Consent & popup auto-handler

3. **🌐 Proxy Settings**
   - Enable/disable proxy
   - Auto-detect proxy type from protocol prefix or use default selection (HTTP, HTTPS, SOCKS5)
   - Multiple proxy format support:
     - Simple: `ip:port` or `host:port`
     - With auth: `user:pass@host:port`
     - Alternative auth: `host:port:username:password`
     - Protocol prefix: `http://host:port`, `https://host:port`, `socks5://host:port`
   - Drag & Drop - Drag and drop .txt files directly into the proxy list
   - Import from File - Import proxies from .txt file via file picker
   - Proxy Counter - Real-time display of loaded proxy count
   - Rotation settings (rotate per session/profile)
   - Automatic timezone/location handling based on proxy

4. **🧩 RPA Script Creator**
   - Visual Builder - Drag and drop interface for creating workflows
   - Action Toolbox - New Tab, Access Website, Time, Scroll, Click, Input, Close Page
   - JSON-based script editor
   - Save/Load scripts
   - Custom automation workflows

5. **🎮 Control** (NEW in v5)
   - Start/Stop automation buttons
   - Real-time status display
   - Step-by-step usage instructions
   - Centralized control panel
   - **Import Settings** (NEW in v5.2)
     - Import User Agents - Load custom user agents from text file
     - Import Cookies - Load cookies from JSON file

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
- **Instant Instance Management** - Zero delays between thread starts
- **Immediate Restart** - Instance restart time reduced for near-instant recovery
- **Stealth Mode** - Removed "Chrome is being controlled by automated test software" banner
- **Import User Agents** - Load custom user agents from text file, automatically rotated across instances
- **Import Cookies** - Load cookies from JSON file, automatically injected into all browser contexts

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

### Sponsored Content Click Engine
- Ratio-based interaction logic
- Safe element detection
- Confidence scoring system
- Element visibility verification

## 🛡️ Security & Compliance

### Protection Features
- **Configuration Encryption** - AES-256 encryption for sensitive data (proxies, API keys)
- **File Integrity Checking** - Detects tampering with SHA-256 checksums
- **Rate Limiting** - Prevents abuse with configurable request limits
- **Secure Logging** - Automatic masking of sensitive information (IPs, passwords, keys)
- **Environment Validation** - Detects suspicious execution environments

### Logging
- All actions are logged
- File-based logs in `logs/` directory
- Real-time GUI logs
- Timestamp and severity tracking
- Automatic sensitive data masking

## 📁 Project Structure

```
advanced_bot.py        # Main application
security_manager.py    # Security utilities
setup_browser.py       # Browser setup helper
user_agents.py         # User agent rotation
requirements.txt       # Python dependencies
build.bat              # Windows build script
build.sh               # Linux/macOS build script
example_script.json    # Sample RPA script
example_proxies.txt    # Example proxy list
```

## 📊 System Requirements

- Python 3.8+
- 4GB RAM minimum
- Internet connection
- Windows, macOS, or Linux

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

Contributions should maintain:
- Professional code quality
- Comprehensive error handling
- Security best practices
- Clear documentation

## 📧 Support

For issues or questions, please open an issue on the GitHub repository.

---

**Built with enterprise-grade standards for professional RPA automation.**
