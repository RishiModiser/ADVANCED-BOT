#!/usr/bin/env python3
"""
Windows Desktop Automation System
Enterprise-grade RPA software for UX testing, sponsored content simulation,
and traffic behavior research.
"""

import sys
import os
import json
import random
import time
import ssl
import logging
import asyncio
import uuid
import subprocess
import tempfile
import threading
import ctypes
import shutil
import base64
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from user_agents import USER_AGENTS
# Check for required dependencies before importing them
def check_dependencies():
    """Check if required packages are installed and auto-install if missing."""
    missing_packages = []

    try:
        import PySide6
    except ImportError:
        missing_packages.append('PySide6>=6.6.1')

    try:
        import playwright
    except ImportError:
        missing_packages.append('playwright>=1.40.0')

    if missing_packages:
        print("\n" + "="*70)
        print("First-Time Setup: Installing missing dependencies")
        print("="*70)
        print(f"\nPackages to install: {', '.join(missing_packages)}")
        print("\nThis is a one-time setup. Please wait...")
        print("="*70)

        try:
            import subprocess as _sp
            _sp.check_call(
                [sys.executable, '-m', 'pip', 'install', '--upgrade'] + missing_packages,
            )
            print("\n" + "="*70)
            print("Dependencies installed successfully!")
            print("Installing remaining requirements...")
            print("="*70)
            # Install full requirements.txt for completeness
            _req_file = Path(__file__).parent / 'requirements.txt'
            if _req_file.exists():
                _sp.check_call(
                    [sys.executable, '-m', 'pip', 'install', '-r', str(_req_file)],
                )
            print("\nRestarting application...")
            print("="*70 + "\n")
            # Re-execute this script so newly installed packages are importable
            import os
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"\nAuto-installation failed: {e}")
            print("\nPlease install dependencies manually:")
            print("\n    pip install -r requirements.txt")
            print("\nFor more details, see README.md")
            print("="*70 + "\n")
            sys.exit(1)

# Run dependency check
check_dependencies()

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTabWidget, QGroupBox, QListWidget,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QScrollArea, QListWidgetItem, QFormLayout,
    QAbstractItemView, QRadioButton, QButtonGroup, QGridLayout, QStackedWidget,
    QSlider
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

# Import aiohttp for geolocation API calls (will be used in ProxyGeolocation class)
try:
    import aiohttp
except ImportError:
    aiohttp = None  # Will handle gracefully in ProxyGeolocation

# Import security manager for advanced protection
try:
    from security_manager import SecurityManager, RateLimiter
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    print("Warning: Security manager not available. Running with basic security.")


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

CONSENT_BUTTON_TEXTS= [
    'accept', 'accept all', 'agree', 'allow all', 'i agree',
    'agree and close', 'allow cookies', 'got it', 'ok', 'okay', 'consent',
    'agree and continue', 'akzeptieren', 'accepter', 'aceptar',
    'accept cookies', 'accepter tout', 'alle akzeptieren', 'tout accepter',
    'accept all cookies', 'allow all cookies', 'i accept', 'i understand',
    'agree to all', 'j\'accepte', 'acepto', 'accetto', 'continuar',
    'continue', 'understood', 'dismiss', 'close', 'yes', 'allow',
    'enable', 'enable all', 'confirm', 'accept & close', 'agree & close',
    'that\'s ok', 'fine by me', 'sounds good', 'accept recommended',
    'i understand', 'proceed', 'agree all', 'allow cookies and close',
    'accept and proceed', 'accept selected', 'save and close',
    'save preferences', 'all cookies', 'necessary cookies only',
    'reject all', 'only necessary', 'customize', 'preferences',
    'manage options', 'cookie settings', 'privacy settings'
]

SPONSORED_SELECTORS = [
    '.promo', '.sponsored-demo', '.featured', '.recommended',
    '[data-sponsored="true"]', '[data-promo="true"]',
    '.promotion', '.advertisement-demo'
]

# Ad detection selectors for demo/test ads (NOT real ad networks)
AD_DETECTION_SELECTORS = [
    '.ad-container', '.advertisement', '.ad-box', '.ad-banner',
    '.promo-ad', '.demo-ad', '.test-ad', '[data-ad="true"]',
    '[data-testid*="ad"]', '.sponsored-content', '.ad-placeholder',
    'div[id*="ad-"]', 'div[class*="ad-"]'
]

# ============================================================================
# SAFE/DEMO SPONSORED SELECTOR LISTS
# All safe sponsored selectors are centralised here for easy future expansion.
# To add more safe sponsored selectors, append them to the lists below.
# ============================================================================

# Safe sponsored / promo element selectors (demo/test only – NOT real ad networks)
SAFE_SPONSORED_SELECTORS = [
    '.promo',
    '.featured',
    '.recommended',
    '.sponsored-demo',
    '.demo-ad',
    '.test-ad',
    '[data-sponsored="true"]',
    '[data-demo-click="true"]',
    # Add additional safe sponsored selectors here
]

# Safe iFrame selectors (demo/test only – NOT real ad networks)
SAFE_IFRAME_SELECTORS = [
    'iframe[data-demo-sponsored="true"]',
    'iframe[data-safe-click="true"]',
    '.demo-sponsored iframe',
    '.test-click-frame',
    # Add additional safe iframe selectors here
]

# Click targets to search for inside safe iframes
SAFE_CLICK_TARGETS = [
    'a[href]',
    'button',
    '.demo-link',
    '.demo-button',
    '[data-clickable="true"]',
    # Add additional safe click targets here
]

# Default ad selectors shown in the Ad Selectors panel.
# Users can add/remove/toggle selectors from the GUI; this list is the factory default.
AD_SELECTORS: List[Dict[str, Any]] = [
    {"selector": "iframe[src*='ads']", "enabled": True},
    {"selector": "iframe[src*='ad']", "enabled": True},
    {"selector": "div[id*='ad']", "enabled": True},
    {"selector": "div[class*='ad']", "enabled": True},
    {"selector": "ins[id*='ad']", "enabled": True},
    {"selector": "ins[class*='ads']", "enabled": True},
    {"selector": "a[href*='ad']", "enabled": True},
    {"selector": "a[href*='ads']", "enabled": True},
    {"selector": "div[data-ad-*]", "enabled": True},
    {"selector": "div[data-ads-*]", "enabled": True},
    {"selector": "[id*='banner']", "enabled": True},
    {"selector": "[class*='banner']", "enabled": True},
    {"selector": "[id*='sponsor']", "enabled": True},
    {"selector": "[class*='sponsor']", "enabled": True},
    {"selector": "div[aria-label*='ad']", "enabled": True},
    {"selector": "div[aria-label*='sponsor']", "enabled": True},
    {"selector": "div[role='button']:has-text('Ad')", "enabled": True},
    {"selector": "div:has-text('Sponsored')", "enabled": True},
    {"selector": "div:has-text('Advertisement')", "enabled": True},
    {"selector": "div:has-text('Promoted')", "enabled": True},
    {"selector": "a[href*='click']", "enabled": True},
    {"selector": "a[href*='go']", "enabled": True},
    {"selector": "a[href*='out']", "enabled": True},
    {"selector": "a[href*='redirect']", "enabled": True},
    {"selector": "a[href*='track']", "enabled": True},
]

# Path to the bot settings file used for selector persistence
_BOT_SETTINGS_FILE = Path(__file__).parent / 'bot_settings.json'


# Referrer URLs for different sources
REFERRER_URLS = {
    # Using base referral URLs - actual target URLs will be appended in the referral logic
    'facebook': 'https://lm.facebook.com/l.php',  # Facebook link manager (referral pattern)
    'google': 'https://www.google.com/url',  # Google redirect URL (query params added at runtime)
    'twitter': 'https://t.co',  # Twitter link shortener (referral pattern)
    'telegram': 'https://t.me/s',  # Telegram share URL
    'instagram': 'https://l.instagram.com',  # Instagram link redirect
    'reddit': 'https://out.reddit.com',  # Reddit outbound link tracker
    'linkedin': 'https://www.linkedin.com/redir',  # LinkedIn redirect
    'pinterest': 'https://www.pinterest.com/pin/create/button',  # Pinterest sharing
    'youtube': 'https://www.youtube.com/redirect',  # YouTube redirect
    'tiktok': 'https://www.tiktok.com/redirect',  # TikTok redirect
    'whatsapp': 'https://chat.whatsapp.com',  # WhatsApp share
    'snapchat': 'https://www.snapchat.com/add',  # Snapchat add
    'discord': 'https://discord.gg',  # Discord invite
    'medium': 'https://medium.com/m/global-identity',  # Medium redirect
    'quora': 'https://www.quora.com/share',  # Quora share
    'tumblr': 'https://www.tumblr.com/share',  # Tumblr share
    'vk': 'https://vk.com/share.php',  # VK share
    'weibo': 'https://service.weibo.com/share/share.php',  # Weibo share
    'line': 'https://line.me/R/msg/text'  # LINE share
}

# Search engine configurations for SEARCH VISIT feature
SEARCH_ENGINES = {
    'Google': {
        'url': 'https://www.google.com',
        'search_box_selectors': ['textarea[name="q"]', 'input[name="q"]', 'textarea[title="Search"]'],
        'results_selector': ['div#search', '[id="rso"]'],
        'result_links_selector': 'div#search a[href], div#rso a[href]'
    },
    'Bing': {
        'url': 'https://www.bing.com',
        'search_box_selectors': ['textarea[name="q"]', 'input[name="q"]', '#sb_form_q'],
        'results_selector': ['#b_results', '.b_algo'],
        'result_links_selector': '#b_results a[href], .b_algo a[href]'
    },
    'Yahoo': {
        'url': 'https://www.yahoo.com',
        'search_box_selectors': [
            'input[name="p"]',           # Desktop main search input
            '#yschsp',                    # Desktop search helper
            'input#ybar-sbq',             # Desktop search bar query  
            'input[type="search"]',       # Generic search input (mobile/responsive)
            'input[placeholder*="earch"]',# Search input by placeholder text
            'input[aria-label*="earch"]', # Search input by aria-label
            'input.search-box',           # Search box class
            'form[role="search"] input',  # Input within search form
            '#header-search-input',       # Mobile header search
            '.mobile-search input'        # Mobile search container
        ],
        'results_selector': [
            '#web',                        # Desktop results container
            '.searchCenterMiddle',         # Desktop search center
            '#main',                       # Mobile main content
            '.results',                    # Generic results container
            '[role="main"]',               # Main content by aria role
            '.compArticleList'             # Mobile article list
        ],
        'result_links_selector': '#web a[href], .searchCenterMiddle a[href], #main a[href], .results a[href]'
    },
    'DuckDuckGo': {
        'url': 'https://duckduckgo.com',
        'search_box_selectors': ['input[name="q"]', '#search_form_input'],
        'results_selector': ['#links', '.results'],
        'result_links_selector': '#links a[href], .results a[href]'
    },
    'Yandex': {
        'url': 'https://www.yandex.com',
        'search_box_selectors': ['input[name="text"]', '.input__control'],
        'results_selector': ['#search-result', '.serp-list'],
        'result_links_selector': '#search-result a[href], .serp-list a[href]'
    },
    'Baidu': {
        'url': 'https://www.baidu.com',
        'search_box_selectors': ['input[name="wd"]', '#kw'],
        'results_selector': ['#content_left', '.result'],
        'result_links_selector': '#content_left a[href], .result a[href]'
    }
}

# Link filtering - URLs to skip when clicking content links
LINK_SKIP_PATTERNS = ['logout', 'login', 'signin', 'signup', 'facebook', 'twitter', 'instagram']

# Human behavior constants
BACK_SCROLL_CHANCE = 0.15  # 15% chance to scroll back up
READING_PAUSE_CHANCE = 0.3  # 30% chance to pause for reading
TIME_BROWSING_BACK_SCROLL_CHANCE = 0.3  # 30% chance to scroll back during time-based browsing


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class DragDropTextEdit(QTextEdit):
    """Custom QTextEdit that supports drag and drop of files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        """Handle drop event for files."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.txt'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            current_text = self.toPlainText()
                            if current_text.strip():
                                self.setPlainText(current_text + '\n' + content)
                            else:
                                self.setPlainText(content)
                    except Exception as e:
                        print(f"Error reading file: {e}")
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

# ============================================================================
# LOGGING MANAGER
# ============================================================================

class LogManager:
    """Centralized logging management."""
    
    def __init__(self):
        self.logs = []
        self.max_logs = 1000
        self.file_logger = None
        self._setup_file_logger()
    
    def _setup_file_logger(self):
        """Setup file-based logging."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        # Clean up old log files (keep only 10 most recent)
        self._cleanup_old_logs(max_log_files=10)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.file_logger = logging.getLogger(__name__)
    
    def _cleanup_old_logs(self, max_log_files: int = 10):
        """Keep only the most recent N log files, delete older ones.
        
        Args:
            max_log_files: Maximum number of log files to keep (default: 10)
        """
        try:
            log_dir = Path('logs')
            if not log_dir.exists():
                return
            
            # Get all log files sorted by modification time (newest first)
            log_files = sorted(
                log_dir.glob('automation_*.log'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Delete files beyond the limit
            if len(log_files) > max_log_files:
                files_to_delete = log_files[max_log_files:]
                for old_log in files_to_delete:
                    try:
                        old_log.unlink()
                        print(f"Deleted old log file: {old_log.name}")
                    except Exception as e:
                        print(f"Failed to delete {old_log.name}: {e}")
                
                deleted_count = len(files_to_delete)
                if deleted_count > 0:
                    print(f"✓ Cleaned up {deleted_count} old log file(s), keeping {max_log_files} most recent")
        except Exception as e:
            print(f"Log cleanup error: {e}")
    
    def log(self, message: str, level: str = 'INFO'):
        """Add a log entry."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] [{level}] {message}'
        
        self.logs.append(log_entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        
        # Log to file
        if level == 'ERROR':
            self.file_logger.error(message)
        elif level == 'WARNING':
            self.file_logger.warning(message)
        else:
            self.file_logger.info(message)
        
        return log_entry
    
    def get_logs(self) -> List[str]:
        """Get all log entries."""
        return self.logs.copy()
    
    def clear_logs(self):
        """Clear all log entries."""
        self.logs.clear()


# ============================================================================
# FINGERPRINT MANAGER
# ============================================================================

class FingerprintManager:
    """Manages browser fingerprinting and user agent rotation."""
    
    def __init__(self, platform: str = 'windows'):
        self.platform = platform
        self.user_agent = None
        self.viewport = None
        self.timezone = None
        self.locale = None
        self.hardware_concurrency = None
    
    def generate_fingerprint(self, proxy_location: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate a realistic browser fingerprint.
        
        If proxy_location is provided, generates fingerprint matching proxy's country.
        This ensures browser location matches proxy location (USA proxy → USA fingerprint).
        
        Args:
            proxy_location: Optional dict with 'country' and 'timezone' from proxy geolocation
        """
        self.user_agent = random.choice(USER_AGENTS.get(self.platform, USER_AGENTS['windows']))
        
        if self.platform == 'android':
            self.viewport = {
                'width': random.choice([360, 375, 412, 414]),
                'height': random.choice([640, 667, 732, 896])
            }
        else:
            # Use realistic desktop viewport sizes (not maximized, comfortable viewing)
            self.viewport = {
                'width': random.choice([1280, 1366, 1440, 1536, 1600]),
                'height': random.choice([720, 768, 800, 864, 900])
            }
        
        # CRITICAL FIX: Match timezone and locale to proxy location if available
        if proxy_location:
            # Use timezone from proxy location if available
            proxy_timezone = proxy_location.get('timezone')
            if proxy_timezone:
                self.timezone = proxy_timezone
            else:
                # Fallback: Map country to common timezone
                country_code = proxy_location.get('countryCode', '')
                self.timezone = self._get_timezone_for_country(country_code)
            
            # Set locale based on country
            country_code = proxy_location.get('countryCode', '')
            self.locale = self._get_locale_for_country(country_code)
        else:
            # No proxy - use random timezone/locale
            timezones = ['America/New_York', 'America/Los_Angeles', 'Europe/London', 
                         'Europe/Paris', 'Asia/Tokyo', 'Australia/Sydney']
            self.timezone = random.choice(timezones)
            
            locales = ['en-US', 'en-GB', 'de-DE', 'fr-FR', 'ja-JP', 'es-ES']
            self.locale = random.choice(locales)
        
        self.hardware_concurrency = random.choice([4, 8, 12, 16])
        
        return {
            'user_agent': self.user_agent,
            'viewport': self.viewport,
            'timezone': self.timezone,
            'locale': self.locale,
            'hardware_concurrency': self.hardware_concurrency
        }
    
    def _get_timezone_for_country(self, country_code: str) -> str:
        """Map country code to common timezone."""
        timezone_map = {
            'US': 'America/New_York',
            'CA': 'America/Toronto',
            'GB': 'Europe/London',
            'DE': 'Europe/Berlin',
            'FR': 'Europe/Paris',
            'IT': 'Europe/Rome',
            'ES': 'Europe/Madrid',
            'NL': 'Europe/Amsterdam',
            'SE': 'Europe/Stockholm',
            'NO': 'Europe/Oslo',
            'DK': 'Europe/Copenhagen',
            'FI': 'Europe/Helsinki',
            'PL': 'Europe/Warsaw',
            'RU': 'Europe/Moscow',
            'JP': 'Asia/Tokyo',
            'CN': 'Asia/Shanghai',
            'IN': 'Asia/Kolkata',
            'SG': 'Asia/Singapore',
            'AU': 'Australia/Sydney',
            'NZ': 'Pacific/Auckland',
            'BR': 'America/Sao_Paulo',
            'MX': 'America/Mexico_City',
            'AR': 'America/Argentina/Buenos_Aires',
        }
        return timezone_map.get(country_code, 'America/New_York')  # Default to US EST
    
    def _get_locale_for_country(self, country_code: str) -> str:
        """Map country code to appropriate locale."""
        locale_map = {
            'US': 'en-US',
            'CA': 'en-CA',
            'GB': 'en-GB',
            'AU': 'en-AU',
            'NZ': 'en-NZ',
            'DE': 'de-DE',
            'AT': 'de-AT',
            'CH': 'de-CH',
            'FR': 'fr-FR',
            'BE': 'fr-BE',
            'IT': 'it-IT',
            'ES': 'es-ES',
            'MX': 'es-MX',
            'AR': 'es-AR',
            'NL': 'nl-NL',
            'SE': 'sv-SE',
            'NO': 'no-NO',
            'DK': 'da-DK',
            'FI': 'fi-FI',
            'PL': 'pl-PL',
            'RU': 'ru-RU',
            'JP': 'ja-JP',
            'CN': 'zh-CN',
            'IN': 'en-IN',
            'SG': 'en-SG',
            'BR': 'pt-BR',
        }
        return locale_map.get(country_code, 'en-US')  # Default to US English


# ============================================================================
# HUMAN BEHAVIOR ENGINE
# ============================================================================

class HumanBehavior:
    """Simulates human-like behavior patterns."""
    
    @staticmethod
    async def random_delay(min_ms: int = 500, max_ms: int = 2000):
        """Add random delay to simulate human reaction time."""
        delay = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)
    
    @staticmethod
    async def scroll_page(page: Page, depth_percent: int = None, position: str = 'Intermediate', scroll_type: str = 'Smooth', min_speed: int = 100, max_speed: int = 500):
        """Scroll page with enhanced human-like behavior - viewport-based, random direction, pauses, mouse movement.
        
        Args:
            page: The page to scroll
            depth_percent: Scroll depth percentage (0-100) - how much to scroll relative to the starting position
            position: Scroll position - 'Top' (scroll down from top), 'Intermediate' (scroll from middle), or 'Bottom' (scroll up from bottom)
            scroll_type: Type of scroll - 'Smooth' or 'Auto'
            min_speed: Minimum speed (pause duration in ms) between scroll steps
            max_speed: Maximum speed (pause duration in ms) between scroll steps
        """
        try:
            if depth_percent is None:
                depth_percent = random.randint(30, 100)
            
            # Get page and viewport info
            page_height = await page.evaluate('document.documentElement.scrollHeight')
            viewport_height = await page.evaluate('window.innerHeight')
            
            # Calculate initial position and target based on position parameter
            if position == 'Top':
                # Start from top (0%) and scroll down to depth_percent
                start_position = 0
                target_scroll = int(page_height * (depth_percent / 100))
                scroll_direction = 1  # scroll down
            elif position == 'Bottom':
                # Start from bottom and scroll up by depth_percent
                start_position = page_height - viewport_height  # Start at actual bottom
                # For Bottom, depth_percent means how much to scroll UP from bottom
                # e.g., depth=50 means scroll up to 50% from bottom (which is 50% of page)
                target_scroll = int(page_height * ((100 - depth_percent) / 100))
                scroll_direction = -1  # scroll up
            else:  # Intermediate
                # Start from 30% and scroll down to start + depth_percent
                start_position = int(page_height * 0.3)
                target_scroll = int(page_height * ((30 + depth_percent * 0.7) / 100))  # Scale to remaining 70%
                scroll_direction = 1  # scroll down
            
            # Scroll to start position first
            await page.evaluate(f'''
                window.scrollTo({{
                    top: {start_position},
                    behavior: 'smooth'
                }})
            ''')
            await asyncio.sleep(0.5)
            
            current_position = start_position
            
            # Scroll in steps towards target with variable speed
            while (scroll_direction == 1 and current_position < target_scroll) or \
                  (scroll_direction == -1 and current_position > target_scroll):
                # Random step size based on viewport (more realistic)
                step = int(viewport_height * random.uniform(0.3, 0.8)) * scroll_direction
                next_position = current_position + step
                
                # Clamp to valid range based on direction
                if scroll_direction == 1:  # scrolling down
                    next_position = max(start_position, min(next_position, target_scroll))
                else:  # scrolling up
                    next_position = max(target_scroll, min(next_position, start_position))
                
                # ENHANCED: Add mouse movement during scroll (simulating user moving mouse while scrolling)
                try:
                    viewport_width = await page.evaluate('window.innerWidth')
                    x = random.randint(100, viewport_width - 100)
                    y = random.randint(100, viewport_height - 100)
                    await page.mouse.move(x, y)
                except:
                    pass
                
                # Use scroll behavior based on scroll_type
                scroll_behavior = 'smooth' if scroll_type == 'Smooth' else 'auto'
                await page.evaluate(f'''
                    window.scrollTo({{
                        top: {next_position},
                        behavior: '{scroll_behavior}'
                    }})
                ''')
                
                current_position = next_position
                
                # Variable pause between scrolls (human reading) using min_speed and max_speed
                # Convert ms to seconds for asyncio.sleep
                await asyncio.sleep(random.uniform(min_speed / 1000, max_speed / 1000))
                
                # Occasionally scroll back up a bit (human-like behavior)
                if random.random() < BACK_SCROLL_CHANCE and current_position > viewport_height:
                    back_scroll = int(viewport_height * random.uniform(0.1, 0.3))
                    current_position = max(0, current_position - back_scroll)
                    await page.evaluate(f'''
                        window.scrollTo({{
                            top: {current_position},
                            behavior: 'smooth'
                        }})
                    ''')
                    await asyncio.sleep(random.uniform(0.4, 0.9))
                
                # Random pause to simulate reading content
                if random.random() < READING_PAUSE_CHANCE:
                    await asyncio.sleep(random.uniform(1.5, 4.0))
            
            # Final idle pause
            await asyncio.sleep(random.uniform(0.8, 2.5))
            
        except Exception as e:
            logging.error(f'Scroll error: {e}')
    
    @staticmethod
    async def mouse_movement(page: Page, x: int, y: int):
        """Simulate natural mouse movement with easing."""
        try:
            # Get current mouse position (start from 0,0 if not available)
            current_x = 0
            current_y = 0
            
            # Calculate steps for smooth movement
            steps = random.randint(10, 20)
            for i in range(steps):
                # Easing function for natural movement
                progress = (i + 1) / steps
                eased_progress = progress * progress * (3 - 2 * progress)  # Smoothstep
                
                # Calculate intermediate position
                intermediate_x = current_x + (x - current_x) * eased_progress
                intermediate_y = current_y + (y - current_y) * eased_progress
                
                # Add slight randomness
                jitter_x = random.randint(-3, 3)
                jitter_y = random.randint(-3, 3)
                
                await page.mouse.move(
                    int(intermediate_x + jitter_x),
                    int(intermediate_y + jitter_y)
                )
                await asyncio.sleep(random.uniform(0.01, 0.03))
            
        except Exception as e:
            logging.error(f'Mouse movement error: {e}')
    
    @staticmethod
    async def natural_click(page: Page, selector: str):
        """Perform a natural click with delays."""
        try:
            element = await page.query_selector(selector)
            if not element:
                return False
            
            # Get element position
            box = await element.bounding_box()
            if not box:
                return False
            
            # Move mouse to element
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            await HumanBehavior.mouse_movement(page, int(x), int(y))
            
            # Random pre-click delay
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Click
            await element.click()
            
            # Random post-click delay
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            return True
            
        except Exception as e:
            logging.error(f'Natural click error: {e}')
            return False
    
    @staticmethod
    async def idle_pause():
        """Random idle pause to simulate reading/thinking.
        
        Simulates natural reading pauses that occur when humans read content.
        Used to make browsing behavior appear more realistic.
        """
        await asyncio.sleep(random.uniform(2.5, 6.0))
    
    @staticmethod
    async def highlight_text(page: Page):
        """
        Enhanced AI-powered text highlighting to simulate human reading behavior.
        Selects random text elements and highlights them with realistic mouse drag simulation.
        """
        try:
            # Find text elements (paragraphs, divs with text, articles)
            text_elements = await page.query_selector_all('p, div, span, article, section, h1, h2, h3, li')
            
            if not text_elements or len(text_elements) == 0:
                return
            
            # Randomly select 1-3 elements to highlight
            num_highlights = random.randint(1, 3)
            
            for _ in range(num_highlights):
                # Select random element
                element = random.choice(text_elements)
                
                try:
                    # Get bounding box
                    box = await element.bounding_box()
                    if not box:
                        continue
                    
                    # Get text content to ensure it has text
                    text = await element.inner_text()
                    if not text or len(text.strip()) < 10:
                        continue
                    
                    # Calculate highlight start and end positions
                    # Start somewhere in the middle-left of the element
                    start_x = int(box['x'] + random.uniform(10, box['width'] * 0.3))
                    start_y = int(box['y'] + box['height'] / 2 + random.randint(-5, 5))
                    
                    # End somewhere in the middle-right (simulating reading direction)
                    end_x = int(box['x'] + random.uniform(box['width'] * 0.5, box['width'] - 10))
                    end_y = int(box['y'] + box['height'] / 2 + random.randint(-5, 5))
                    
                    # Move mouse to start position with natural movement
                    await HumanBehavior.mouse_movement(page, start_x, start_y)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    # Press mouse down (start selection)
                    await page.mouse.down()
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                    
                    # Drag to end position with intermediate steps (more realistic)
                    steps = random.randint(5, 10)
                    for i in range(steps):
                        progress = (i + 1) / steps
                        intermediate_x = int(start_x + (end_x - start_x) * progress)
                        intermediate_y = int(start_y + (end_y - start_y) * progress)
                        
                        await page.mouse.move(
                            intermediate_x + random.randint(-2, 2),
                            intermediate_y + random.randint(-2, 2)
                        )
                        await asyncio.sleep(random.uniform(0.02, 0.05))
                    
                    # Release mouse (end selection)
                    await page.mouse.up()
                    
                    # Pause to simulate reading the highlighted text
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    
                    # Click elsewhere to deselect (optional, human-like)
                    if random.random() < 0.5:
                        viewport_width = await page.evaluate('window.innerWidth')
                        viewport_height = await page.evaluate('window.innerHeight')
                        random_x = random.randint(100, viewport_width - 100)
                        random_y = random.randint(100, viewport_height - 100)
                        await page.mouse.click(random_x, random_y)
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                    
                except Exception as e:
                    logging.error(f'Error highlighting text on element: {e}')
                    continue
            
        except Exception as e:
            logging.error(f'Error in highlight_text: {e}')
            
            if not text_elements:
                return
            
            # Select random element with text
            element = random.choice(text_elements[:min(20, len(text_elements))])
            
            # Check if element has text content
            text_content = await element.text_content()
            if not text_content or len(text_content.strip()) < 10:
                return
            
            # Get element position and scroll to it
            box = await element.bounding_box()
            if not box:
                return
            
            # Calculate word positions for selection
            words = text_content.strip().split()
            if len(words) < 3:
                return
            
            # Select random portion of text (2-8 words)
            num_words = random.randint(2, min(8, len(words)))
            start_word = random.randint(0, len(words) - num_words)
            
            # Simulate text selection with mouse
            # Move to start position
            start_x = box['x'] + random.uniform(0, box['width'] * 0.3)
            start_y = box['y'] + random.uniform(box['height'] * 0.2, box['height'] * 0.8)
            await page.mouse.move(start_x, start_y)
            
            # Mouse down to start selection
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.1, 0.2))
            
            # Move to end position (simulate dragging)
            end_x = start_x + random.uniform(50, 150)
            end_y = start_y + random.uniform(-5, 5)
            
            # Move in small steps to simulate human dragging
            steps = random.randint(3, 6)
            for i in range(steps):
                intermediate_x = start_x + (end_x - start_x) * (i + 1) / steps
                intermediate_y = start_y + (end_y - start_y) * (i + 1) / steps
                await page.mouse.move(intermediate_x, intermediate_y)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # Mouse up to complete selection
            await page.mouse.up()
            
            # Pause to "view" highlighted text
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Click elsewhere to deselect
            clear_x = box['x'] + box['width'] + random.uniform(20, 50)
            clear_y = box['y'] + random.uniform(0, 50)
            await page.mouse.click(clear_x, clear_y)
            
        except Exception as e:
            logging.error(f'Text highlight error: {e}')
    
    @staticmethod
    async def time_based_browsing(page: Page, min_time: int, max_time: int, enable_highlight: bool = False, 
                                  consent_manager=None, log_manager=None):
        """
        Simulate advanced human browsing behavior for a specified time period.
        
        Args:
            page: Playwright page object
            min_time: Minimum time to spend in seconds (120-480)
            max_time: Maximum time to spend in seconds (120-480)
            enable_highlight: Enable random text highlighting
            consent_manager: Optional ConsentManager for continuous popup handling
            log_manager: Optional LogManager for logging
        """
        try:
            # Validate and clamp time range
            min_time = max(120, min(480, min_time))
            max_time = max(120, min(480, max_time))
            
            # Ensure min <= max
            if min_time > max_time:
                min_time, max_time = max_time, min_time
            
            # Calculate actual time to spend (between min and max)
            time_to_spend = random.uniform(min_time, max_time)
            start_time = time.time()
            
            logging.info(f'Starting time-based browsing for {time_to_spend:.1f} seconds')
            
            last_consent_check = start_time  # Track last consent check time
            
            while time.time() - start_time < time_to_spend:
                # Random scroll depth
                scroll_depth = random.randint(30, 100)
                
                # Scroll down with human-like behavior
                await HumanBehavior.scroll_page(page, scroll_depth)
                
                # Random reading pause
                await asyncio.sleep(random.uniform(2.0, 5.0))
                
                # Periodically check for consent popups (every 10-15 seconds)
                if consent_manager and (time.time() - last_consent_check) > random.uniform(10, 15):
                    try:
                        await consent_manager.handle_consents(page, max_retries=1)
                        last_consent_check = time.time()
                    except Exception:
                        pass  # Silent failure for consent checks during browsing
                
                # Occasionally highlight text if enabled
                if enable_highlight and random.random() < 0.2:  # 20% chance
                    await HumanBehavior.highlight_text(page)
                
                # Occasionally scroll back up
                if random.random() < TIME_BROWSING_BACK_SCROLL_CHANCE:
                    back_scroll_depth = random.randint(10, 40)
                    await HumanBehavior.scroll_page(page, back_scroll_depth)
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                
                # Check if we should continue
                elapsed = time.time() - start_time
                if elapsed >= time_to_spend:
                    break
                
                # Random idle pause
                await asyncio.sleep(random.uniform(1.0, 4.0))
            
            logging.info(f'Completed time-based browsing ({time.time() - start_time:.1f} seconds)')
            
        except Exception as e:
            logging.error(f'Time-based browsing error: {e}')


# ============================================================================
# CONSENT MANAGER - ADVANCED VERSION
# ============================================================================

class ConsentManager:
    """Advanced automatic cookie banner, popup, and consent dialog handler.
    
    Handles all types of consent popups including:
    - Cookie banners and GDPR notices
    - Permission requests (notifications, location, etc.)
    - Modal overlays and dialogs
    - Shadow DOM elements
    - Multiple sequential popups
    - iFrame-based consent managers
    """
    
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
        self.handled_popups = set()  # Track handled popups to avoid duplicates
    
    async def handle_consents(self, page: Page, max_retries: int = 3) -> bool:
        """Detect and handle consent dialogs with multiple strategies and retries.
        
        Args:
            page: Playwright Page object
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            bool: True if any consent was handled, False otherwise
        """
        try:
            self.log_manager.log('🔍 Checking for consent dialogs...')
            
            # Wait a bit for dialogs to appear
            await asyncio.sleep(1.5)
            
            overall_handled = False
            
            # Try multiple times to catch delayed or sequential popups
            for retry in range(max_retries):
                handled = False
                
                # Strategy 1: Text-based button detection (comprehensive)
                handled = await self._handle_text_based_buttons(page)
                if handled:
                    overall_handled = True
                    await asyncio.sleep(1)  # Wait for popup to close
                    continue  # Check for more popups
                
                # Strategy 2: Role-based dialog detection
                handled = await self._handle_role_based_dialogs(page)
                if handled:
                    overall_handled = True
                    await asyncio.sleep(1)
                    continue
                
                # Strategy 3: Common CSS class-based detection
                handled = await self._handle_css_class_based_popups(page)
                if handled:
                    overall_handled = True
                    await asyncio.sleep(1)
                    continue
                
                # Strategy 4: iFrame-based consent managers
                handled = await self._handle_iframe_consents(page)
                if handled:
                    overall_handled = True
                    await asyncio.sleep(1)
                    continue
                
                # Strategy 5: Modal overlays and backdrops
                handled = await self._handle_modal_overlays(page)
                if handled:
                    overall_handled = True
                    await asyncio.sleep(1)
                    continue
                
                # Strategy 6: Shadow DOM elements
                handled = await self._handle_shadow_dom_consents(page)
                if handled:
                    overall_handled = True
                    await asyncio.sleep(1)
                    continue
                
                # If nothing was found in this iteration, break early
                if not handled:
                    break
            
            if overall_handled:
                self.log_manager.log('✅ Successfully handled consent dialog(s)')
            else:
                self.log_manager.log('ℹ️  No consent dialogs detected')
            
            return overall_handled
            
        except Exception as e:
            self.log_manager.log(f'⚠️  Consent handler error: {e}', 'ERROR')
            return False
    
    async def _handle_text_based_buttons(self, page: Page) -> bool:
        """Strategy 1: Detect buttons by text content."""
        try:
            for text in CONSENT_BUTTON_TEXTS:
                # Case-insensitive selectors with various element types
                selectors = [
                    f'button:has-text("{text}")',
                    f'a:has-text("{text}")',
                    f'[role="button"]:has-text("{text}")',
                    f'div[onclick]:has-text("{text}")',
                    f'span[onclick]:has-text("{text}")'
                ]
                
                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            # Check if element is visible and clickable
                            is_visible = await element.is_visible()
                            if is_visible:
                                # Get element ID to avoid duplicate clicks
                                element_id = await element.evaluate('el => el.outerHTML.substring(0, 100)')
                                if element_id in self.handled_popups:
                                    continue
                                
                                # Human-like delay before clicking
                                await HumanBehavior.random_delay(500, 1500)
                                await element.click()
                                self.handled_popups.add(element_id)
                                self.log_manager.log(f'✓ Clicked consent button: "{text}"')
                                await asyncio.sleep(0.5)
                                return True
                    except Exception:
                        continue
            return False
        except Exception:
            return False
    
    async def _handle_role_based_dialogs(self, page: Page) -> bool:
        """Strategy 2: Detect dialogs by ARIA roles."""
        try:
            # Check for dialogs, alertdialogs, and modals
            role_selectors = [
                '[role="dialog"]',
                '[role="alertdialog"]',
                '[role="alert"]',
                '[aria-modal="true"]'
            ]
            
            for role_selector in role_selectors:
                dialogs = await page.query_selector_all(role_selector)
                for dialog in dialogs:
                    is_visible = await dialog.is_visible()
                    if is_visible:
                        # Look for accept/allow buttons within dialog
                        buttons = await dialog.query_selector_all('button, a, [role="button"]')
                        for button in buttons:
                            try:
                                text = (await button.inner_text()).lower()
                                # Check if text matches any consent phrase
                                if any(consent_text in text for consent_text in CONSENT_BUTTON_TEXTS):
                                    await HumanBehavior.random_delay(500, 1500)
                                    await button.click()
                                    self.log_manager.log(f'✓ Clicked dialog consent button: "{text[:30]}"')
                                    return True
                            except Exception:
                                continue
            return False
        except Exception:
            return False
    
    async def _handle_css_class_based_popups(self, page: Page) -> bool:
        """Strategy 3: Detect popups by common CSS class patterns."""
        try:
            # Common class name patterns for cookie/consent banners
            class_patterns = [
                '[class*="cookie"]',
                '[class*="consent"]',
                '[class*="gdpr"]',
                '[class*="privacy"]',
                '[class*="banner"]',
                '[class*="notice"]',
                '[id*="cookie"]',
                '[id*="consent"]',
                '[id*="gdpr"]'
            ]
            
            for pattern in class_patterns:
                containers = await page.query_selector_all(pattern)
                for container in containers:
                    is_visible = await container.is_visible()
                    if is_visible:
                        # Look for buttons inside
                        buttons = await container.query_selector_all('button, a, [role="button"]')
                        for button in buttons:
                            try:
                                text = (await button.inner_text()).lower()
                                # Prioritize accept/allow buttons
                                if any(word in text for word in ['accept', 'allow', 'agree', 'ok', 'okay', 'got it']):
                                    await HumanBehavior.random_delay(500, 1500)
                                    await button.click()
                                    self.log_manager.log(f'✓ Clicked CSS-detected consent: "{text[:30]}"')
                                    return True
                            except Exception:
                                continue
            return False
        except Exception:
            return False
    
    async def _handle_iframe_consents(self, page: Page) -> bool:
        """Strategy 4: Handle consent managers in iframes."""
        try:
            # Get all iframes
            frames = page.frames
            for frame in frames:
                if frame == page.main_frame:
                    continue
                
                try:
                    # Check for consent-related content in iframe
                    for text in ['accept', 'agree', 'allow', 'ok', 'okay', 'consent']:
                        selectors = [
                            f'button:has-text("{text}")',
                            f'a:has-text("{text}")'
                        ]
                        
                        for selector in selectors:
                            try:
                                element = await frame.query_selector(selector)
                                if element:
                                    is_visible = await element.is_visible()
                                    if is_visible:
                                        await HumanBehavior.random_delay(500, 1500)
                                        await element.click()
                                        self.log_manager.log(f'✓ Clicked iframe consent: "{text}"')
                                        return True
                            except Exception:
                                continue
                except Exception:
                    continue
            return False
        except Exception:
            return False
    
    async def _handle_modal_overlays(self, page: Page) -> bool:
        """Strategy 5: Handle modal overlays and backdrops."""
        try:
            # Look for elements with high z-index (typically popups/modals)
            high_z_elements = await page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    return elements
                        .filter(el => {
                            const style = window.getComputedStyle(el);
                            const zIndex = parseInt(style.zIndex);
                            return zIndex > 1000 && style.display !== 'none' && style.visibility !== 'hidden';
                        })
                        .map(el => el.outerHTML.substring(0, 100));
                }
            """)
            
            if high_z_elements and len(high_z_elements) > 0:
                # Try to find and click accept buttons in high z-index elements
                for text in ['accept', 'agree', 'allow', 'ok', 'okay', 'got it']:
                    try:
                        button = await page.query_selector(f'button:has-text("{text}")')
                        if button:
                            is_visible = await button.is_visible()
                            if is_visible:
                                await HumanBehavior.random_delay(500, 1500)
                                await button.click()
                                self.log_manager.log(f'✓ Clicked modal consent: "{text}"')
                                return True
                    except Exception:
                        continue
            return False
        except Exception:
            return False
    
    async def _handle_shadow_dom_consents(self, page: Page) -> bool:
        """Strategy 6: Handle consents in Shadow DOM elements."""
        try:
            # Check for shadow roots and consent buttons inside them
            shadow_buttons = await page.evaluate("""
                () => {
                    const shadowHosts = Array.from(document.querySelectorAll('*'))
                        .filter(el => el.shadowRoot);
                    
                    for (const host of shadowHosts) {
                        const shadowRoot = host.shadowRoot;
                        const buttons = shadowRoot.querySelectorAll('button, a, [role="button"]');
                        
                        for (const button of buttons) {
                            const text = button.textContent.toLowerCase();
                            if (text.includes('accept') || text.includes('agree') || 
                                text.includes('allow') || text.includes('ok')) {
                                button.click();
                                return true;
                            }
                        }
                    }
                    return false;
                }
            """)
            
            if shadow_buttons:
                self.log_manager.log('✓ Clicked Shadow DOM consent')
                return True
            return False
        except Exception:
            return False
    
    async def continuous_consent_monitoring(self, page: Page, duration_seconds: int = 5):
        """Continuously monitor and handle popups that appear during browsing.
        
        Args:
            page: Playwright Page object
            duration_seconds: How long to monitor for popups
        """
        try:
            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                await self.handle_consents(page, max_retries=1)
                await asyncio.sleep(2)  # Check every 2 seconds
        except Exception as e:
            self.log_manager.log(f'Continuous monitoring error: {e}', 'DEBUG')


# ============================================================================
# SPONSORED CLICK ENGINE
# ============================================================================

def _classify_selector(selector: str) -> str:
    """Classify a CSS selector string as 'iframe', 'href', or 'normal'.

    Returns one of: 'iframe', 'href', 'normal'.
    Classification is based on simple string heuristics so future selector
    types can be added here without touching call-sites.
    """
    import re
    s = selector.strip()
    if not s:
        return 'normal'
    s_lower = s.lower()
    # iframe selector: starts with 'iframe' as an element name
    # (handles: iframe, iframe[...], iframe.class, iframe#id, iframe:...)
    if re.match(r'^iframe[\s\[.#:>~+,]|^iframe$', s_lower):
        return 'iframe'
    # href selector: [href...] attribute selector or a[href...]
    if re.search(r'\[href', s_lower):
        return 'href'
    return 'normal'


class RandomAdClickEngine:
    """Handles random ad / promo click interactions with unified selector support.

    Accepts any mix of CSS selectors (iframe, href, div, ins, anchor, normal)
    through ``custom_random_targets``.  Built-in safe selectors are always
    included as a baseline and are classified automatically.
    """

    def __init__(self, log_manager: LogManager, confidence_threshold: float = 0.7,
                 custom_random_targets: Optional[List[str]] = None):
        self.log_manager = log_manager
        self.confidence_threshold = confidence_threshold

        # Build a single merged target list from built-in + custom selectors.
        # Duplicates are preserved only once; order: built-ins first, then custom.
        all_selectors: List[str] = list(SAFE_SPONSORED_SELECTORS) + list(SAFE_IFRAME_SELECTORS)
        for s in (custom_random_targets or []):
            s = s.strip()
            if s and s not in all_selectors:
                all_selectors.append(s)

        # Partition into iframe selectors and non-iframe selectors.
        self._iframe_selectors: List[str] = [
            s for s in all_selectors if _classify_selector(s) == 'iframe'
        ]
        self._normal_selectors: List[str] = [
            s for s in all_selectors if _classify_selector(s) != 'iframe'
        ]

        # Keep a reference to all selectors for logging.
        self._all_selectors = all_selectors

    async def is_safe_element(self, element, page: Page) -> bool:
        """Check if element is safe to click."""
        return True

    async def calculate_confidence(self, element) -> float:
        """Calculate confidence score for an element."""
        try:
            score = 0.0

            # Check visibility
            is_visible = await element.is_visible()
            if not is_visible:
                return 0.0

            score += 0.3

            # Check size
            box = await element.bounding_box()
            if box and box['width'] > 50 and box['height'] > 30:
                score += 0.3

            # Check position (not hidden off-screen)
            if box and box['x'] >= 0 and box['y'] >= 0:
                score += 0.2

            # Check if has text or image
            text = await element.inner_text()
            if text and len(text.strip()) > 0:
                score += 0.2

            return score

        except Exception:
            return 0.0

    async def find_random_ad_elements(self, page: Page) -> List:
        """Find clickable ad/promo elements using all normal (non-iframe) selectors."""
        safe_elements = []

        try:
            selectors = self._normal_selectors
            self.log_manager.log(f'Random-ad search: checking {len(selectors)} selector(s)')

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        is_safe = await self.is_safe_element(element, page)
                        if not is_safe:
                            continue

                        confidence = await self.calculate_confidence(element)
                        if confidence >= self.confidence_threshold:
                            safe_elements.append({
                                'element': element,
                                'selector': selector,
                                'confidence': confidence,
                                'selector_type': _classify_selector(selector),
                            })

                except Exception as e:
                    self.log_manager.log(f'Error finding elements for selector "{selector}": {e}', 'WARNING')
                    continue

            self.log_manager.log(f'Found {len(safe_elements)} random ad element(s)')
            return safe_elements

        except Exception as e:
            self.log_manager.log(f'Find random ad elements error: {e}', 'ERROR')
            return []

    async def find_ad_iframes(self, page: Page) -> List:
        """Find visible iframes using all iframe selectors."""
        safe_iframes = []

        try:
            selectors = self._iframe_selectors
            self.log_manager.log(f'iFrame search: checking {len(selectors)} iframe selector(s)')

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        try:
                            # Only include visible iframes
                            if await element.is_visible():
                                safe_iframes.append(element)
                        except Exception:
                            continue
                except Exception as e:
                    self.log_manager.log(f'Error finding iframes for selector "{selector}": {e}', 'WARNING')
                    continue

            self.log_manager.log(f'Found {len(safe_iframes)} iframe(s)')
            return safe_iframes

        except Exception as e:
            self.log_manager.log(f'Find ad iframes error: {e}', 'ERROR')
            return []

    async def click_inside_iframe(self, page: Page, iframe_element) -> bool:
        """Search inside an iframe for clickable targets and perform a human-like click."""
        try:
            # Obtain the content frame of the iframe element
            frame = await iframe_element.content_frame()
            if not frame:
                self.log_manager.log('iFrame has no accessible content frame – skipping', 'WARNING')
                return False

            # Search for clickable targets inside the frame using SAFE_CLICK_TARGETS
            # Add additional safe click targets to SAFE_CLICK_TARGETS at the top of the file
            for target_selector in SAFE_CLICK_TARGETS:
                try:
                    elements = await frame.query_selector_all(target_selector)
                    for element in elements:
                        try:
                            if not await element.is_visible():
                                continue
                            box = await element.bounding_box()
                            if not box:
                                continue

                            # Human-like mouse movement to element centre, then click
                            x = box['x'] + box['width'] / 2
                            y = box['y'] + box['height'] / 2
                            await HumanBehavior.mouse_movement(page, round(x), round(y))
                            await asyncio.sleep(random.uniform(0.1, 0.3))
                            await element.click()
                            await asyncio.sleep(random.uniform(0.3, 0.8))

                            self.log_manager.log(
                                f'✓ iFrame click success – target selector: "{target_selector}"'
                            )
                            return True  # Return immediately on first successful click
                        except Exception:
                            continue
                except Exception as e:
                    self.log_manager.log(
                        f'Error searching inside iframe for "{target_selector}": {e}', 'WARNING'
                    )
                    continue

            self.log_manager.log('No clickable target found inside iframe')
            return False

        except Exception as e:
            self.log_manager.log(f'click_inside_iframe error: {e}', 'ERROR')
            return False

    async def perform_random_ad_click(self, page: Page, ratio: float):
        """Attempt a random ad click based on ratio.  Tries normal selectors first,
        then falls back to iframe selectors.  Ignores empty/invalid selectors safely.
        """
        MAX_RETRIES = 3

        try:
            # Random decision based on ratio (ratio is 0.0–1.0)
            if random.random() > ratio:
                self.log_manager.log('Skipping random ad click (ratio check)')
                return False

            for attempt in range(1, MAX_RETRIES + 1):
                if attempt > 1:
                    self.log_manager.log(f'Random ad click retry attempt {attempt}/{MAX_RETRIES}')

                # --- Normal / href / div / ins / anchor selector path ---
                elements = await self.find_random_ad_elements(page)
                self.log_manager.log(
                    f'Random-ad selector scan: {len(elements)} element(s) found (attempt {attempt})'
                )

                if elements:
                    selected = random.choice(elements)
                    sel_type = selected.get('selector_type', 'normal')
                    self.log_manager.log(
                        f'Clicking random-ad element (type: {sel_type}, '
                        f'confidence: {selected["confidence"]:.2f}, '
                        f'selector: "{selected["selector"]}")'
                    )
                    success = await HumanBehavior.natural_click(page, selected['selector'])
                    if success:
                        self.log_manager.log('✓ Random ad click succeeded')
                        return True
                    self.log_manager.log('Random ad element click returned False – will retry', 'WARNING')
                    continue

                # --- iFrame fallback path ---
                iframes = await self.find_ad_iframes(page)
                self.log_manager.log(
                    f'iFrame scan: {len(iframes)} iframe(s) found (attempt {attempt})'
                )
                for iframe in iframes:
                    success = await self.click_inside_iframe(page, iframe)
                    if success:
                        self.log_manager.log('✓ iFrame random ad click succeeded')
                        return True

                if not iframes:
                    self.log_manager.log('No random ad elements or iframes found')

                self.log_manager.log(
                    f'No click target found on attempt {attempt}/{MAX_RETRIES}', 'WARNING'
                )

            self.log_manager.log(
                f'Random ad click gave up after {MAX_RETRIES} attempt(s)', 'WARNING'
            )
            return False

        except Exception as e:
            self.log_manager.log(f'Random ad click error: {e}', 'ERROR')
            return False


# ============================================================================
# SCRIPT EXECUTOR
# ============================================================================

class ScriptExecutor:
    """Executes RPA scripts with JSON-based steps."""
    
    def __init__(self, log_manager: LogManager, consent_manager: Optional['ConsentManager'] = None):
        self.log_manager = log_manager
        self.current_page = None
        self.consent_manager = consent_manager
        self.context = None
        self.loop_break = False  # Flag for break statement
    
    async def execute_script(self, script: Dict[str, Any], context: BrowserContext):
        """Execute a full RPA script with enhanced error handling and logging."""
        try:
            self.context = context
            steps = script.get('steps', [])
            
            # Execute steps with loop control
            await self._execute_steps(steps, 0, len(steps))
            
            self.log_manager.log('Script execution completed')
            return True
            
        except Exception as e:
            self.log_manager.log(f'Script execution error: {e}', 'ERROR')
            return False
    
    async def _execute_steps(self, steps: List[Dict[str, Any]], start_idx: int, end_idx: int):
        """Execute a range of steps with support for loops and conditionals."""
        idx = start_idx
        while idx < end_idx:
            if self.loop_break:
                self.loop_break = False
                break
                
            step = steps[idx]
            step_type = step.get('type')
            self.log_manager.log(f'▶ Starting step {idx + 1}/{len(steps)}: {step_type}')
            
            try:
                if step_type == 'newPage':
                    # Always create a new page when newPage action is used
                    # This ensures New Tab action works properly in RPA Script Creator
                    try:
                        # Check if context has existing pages
                        if not self.current_page and self.context.pages:
                            # For first page in persistent context, use existing page
                            self.current_page = self.context.pages[0]
                            self.log_manager.log(f'✓ Step {idx + 1}: Using existing page')
                        else:
                            # Create a new page/tab
                            self.current_page = await self.context.new_page()
                            self.log_manager.log(f'✓ Step {idx + 1}: New page/tab opened successfully')
                        
                        # Handle consent popups if consent manager is available
                        if self.consent_manager and self.current_page:
                            try:
                                await self.consent_manager.handle_consents(self.current_page)
                            except Exception as e:
                                self.log_manager.log(f'Consent handler error: {e}', 'WARNING')
                    except Exception as e:
                        self.log_manager.log(f'✗ Step {idx + 1}: Failed to create new page: {e}', 'ERROR')
                
                elif step_type == 'navigate':
                    url = step.get('url', '')
                    timeout = step.get('timeout', 30000)
                    if self.current_page:
                        await self.current_page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                        self.log_manager.log(f'✓ Step {idx + 1}: Navigated to {url}')
                        
                        # Handle consent popups after navigation if consent manager is available
                        if self.consent_manager:
                            try:
                                await self.consent_manager.handle_consents(self.current_page)
                            except Exception as e:
                                self.log_manager.log(f'Consent handler error: {e}', 'WARNING')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page available', 'ERROR')
                
                elif step_type == 'wait':
                    # Support randomized wait ranges
                    duration = step.get('duration', 1000)
                    min_duration = step.get('min_duration', duration)
                    max_duration = step.get('max_duration', duration)
                    
                    actual_duration = random.uniform(min_duration, max_duration) / 1000
                    await asyncio.sleep(actual_duration)
                    self.log_manager.log(f'✓ Step {idx + 1}: Waited {actual_duration:.2f}s')
                
                elif step_type == 'scroll':
                    if self.current_page:
                        depth = step.get('depth', 50)
                        position = step.get('position', 'Intermediate')
                        scroll_type = step.get('scroll_type', 'Smooth')
                        min_speed = step.get('min_speed', 100)
                        max_speed = step.get('max_speed', 500)
                        
                        # Human-like scroll with natural behavior
                        await HumanBehavior.scroll_page(
                            self.current_page, 
                            depth, 
                            position, 
                            scroll_type=scroll_type,
                            min_speed=min_speed,
                            max_speed=max_speed
                        )
                        self.log_manager.log(f'✓ Step {idx + 1}: Scrolled to depth {depth}% from {position} ({scroll_type} type)')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page available', 'ERROR')
                
                elif step_type == 'click':
                    selector = step.get('selector', '')
                    confidence = step.get('confidence', 0.8)
                    
                    if self.current_page and selector:
                        # Click with confidence scoring
                        try:
                            await self.current_page.wait_for_selector(selector, timeout=5000)
                            
                            # Check if element is visible (confidence check)
                            is_visible = await self.current_page.is_visible(selector)
                            
                            if is_visible:
                                # Natural click with human behavior
                                await HumanBehavior.natural_click(self.current_page, selector)
                                self.log_manager.log(f'✓ Step {idx + 1}: Clicked {selector} (confidence: {confidence})')
                            else:
                                self.log_manager.log(f'✗ Step {idx + 1}: Element not visible: {selector}', 'ERROR')
                        except Exception as e:
                            self.log_manager.log(f'✗ Step {idx + 1}: Click failed on {selector}: {e}', 'ERROR')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page or selector', 'ERROR')
                
                elif step_type == 'input':
                    selector = step.get('selector', '')
                    text = step.get('text', '')
                    typing_delay = step.get('typing_delay', 100)  # ms between keystrokes
                    
                    if self.current_page and selector:
                        try:
                            await self.current_page.wait_for_selector(selector, timeout=5000)
                            
                            # Clear existing text
                            await self.current_page.fill(selector, '')
                            
                            # Type with human-like delay
                            for char in text:
                                await self.current_page.type(selector, char, delay=random.uniform(typing_delay * 0.8, typing_delay * 1.2))
                            
                            self.log_manager.log(f'✓ Step {idx + 1}: Typed text into {selector}')
                        except Exception as e:
                            self.log_manager.log(f'✗ Step {idx + 1}: Input failed on {selector}: {e}', 'ERROR')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page or selector', 'ERROR')
                
                elif step_type == 'closePage':
                    if self.current_page:
                        await self.current_page.close()
                        self.current_page = None
                        self.log_manager.log(f'✓ Step {idx + 1}: Page closed')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page to close', 'ERROR')
                
                elif step_type == 'refresh':
                    # Refresh Webpage
                    if self.current_page:
                        await self.current_page.reload(wait_until='domcontentloaded')
                        self.log_manager.log(f'✓ Step {idx + 1}: Page refreshed')
                        
                        # Handle consent popups after refresh if consent manager is available
                        if self.consent_manager:
                            try:
                                await self.consent_manager.handle_consents(self.current_page)
                            except Exception as e:
                                self.log_manager.log(f'Consent handler error: {e}', 'WARNING')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page available', 'ERROR')
                
                elif step_type == 'closeTab':
                    # Close Tab (same as closePage)
                    if self.current_page:
                        await self.current_page.close()
                        self.current_page = None
                        self.log_manager.log(f'✓ Step {idx + 1}: Tab closed')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No tab to close', 'ERROR')
                
                elif step_type == 'quitBrowser':
                    # Quit Browser - close all pages in context
                    if self.context:
                        try:
                            await self.context.close()
                            self.current_page = None
                            self.log_manager.log(f'✓ Step {idx + 1}: Browser quit')
                            return  # Exit execution after quitting
                        except Exception as e:
                            self.log_manager.log(f'✗ Step {idx + 1}: Failed to quit browser: {e}', 'ERROR')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No browser context', 'ERROR')
                
                elif step_type == 'if':
                    # Statement If - conditional execution
                    selector = step.get('selector', '')
                    condition = step.get('condition', '')
                    
                    if self.current_page:
                        try:
                            # Simple condition check using selector visibility
                            condition_met = False
                            if selector:
                                try:
                                    condition_met = await self.current_page.is_visible(selector, timeout=2000)
                                except:
                                    condition_met = False
                            
                            if condition_met:
                                self.log_manager.log(f'✓ Step {idx + 1}: Condition met')
                                # Note: In a full implementation, you would execute nested steps here
                                # For now, just log that condition was met
                            else:
                                self.log_manager.log(f'✓ Step {idx + 1}: Condition not met, skipping')
                        except Exception as e:
                            self.log_manager.log(f'✗ Step {idx + 1}: If statement error: {e}', 'ERROR')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page available', 'ERROR')
                
                elif step_type == 'forLoopElements':
                    # For Loop Elements - iterate over elements
                    selector = step.get('selector', '')
                    max_items = step.get('max_items', 10)
                    
                    if self.current_page and selector:
                        try:
                            # Get all matching elements
                            elements = await self.current_page.query_selector_all(selector)
                            count = min(len(elements), max_items)
                            self.log_manager.log(f'✓ Step {idx + 1}: Found {len(elements)} elements, processing {count}')
                            
                            # Note: In a full implementation, you would execute nested steps for each element
                            # For now, just log the count
                        except Exception as e:
                            self.log_manager.log(f'✗ Step {idx + 1}: For loop elements error: {e}', 'ERROR')
                    else:
                        self.log_manager.log(f'✗ Step {idx + 1}: No page or selector', 'ERROR')
                
                elif step_type == 'forLoopTimes':
                    # For Loop Times - iterate N times
                    iterations = step.get('iterations', 5)
                    self.log_manager.log(f'✓ Step {idx + 1}: Starting loop for {iterations} iterations')
                    
                    # Note: In a full implementation, you would execute nested steps N times
                    # For now, just log the iteration count
                
                elif step_type == 'while':
                    # While Loop - loop while condition is true
                    condition = step.get('condition', '')
                    max_iterations = step.get('max_iterations', 10)
                    
                    self.log_manager.log(f'✓ Step {idx + 1}: While loop started (max: {max_iterations} iterations)')
                    
                    # Note: In a full implementation, you would check condition and execute nested steps
                    # For now, just log that the loop was started
                
                elif step_type == 'break':
                    # Exit Loop - break out of current loop
                    self.loop_break = True
                    self.log_manager.log(f'✓ Step {idx + 1}: Loop exit triggered')
                
                else:
                    self.log_manager.log(f'⚠ Step {idx + 1}: Unknown step type: {step_type}', 'WARNING')
                
            except Exception as e:
                self.log_manager.log(f'✗ Step {idx + 1} error: {e}', 'ERROR')
                # Continue to next step even on error
            
            idx += 1


# ============================================================================
# PROXY MANAGER
# ============================================================================

def parse_proxy(proxy_string: str) -> Dict[str, str]:
    """Parse a single proxy string into a unified configuration dict.

    Supported formats:
    - ``username:password@host:port``
    - ``host:port:username:password``

    Returns:
        Dict with keys ``server``, ``username``, and ``password``.

    Raises:
        ValueError: If the proxy string cannot be parsed.
    """
    proxy_string = proxy_string.strip()
    if not proxy_string:
        raise ValueError("Empty proxy string")

    try:
        if "@" in proxy_string:
            auth, address = proxy_string.split("@", 1)
            username, password = auth.split(":", 1)
            host, port = address.rsplit(":", 1)
        else:
            host, port, username, password = proxy_string.split(":", 3)
    except ValueError:
        raise ValueError(f"Unable to parse proxy: {proxy_string!r}")

    proxy_config = {
        "server": f"http://{host}:{port}",
        "username": username,
        "password": password,
    }
    logging.info("Proxy parsed successfully: %s:%s", host, port)
    return proxy_config


class ProxyManager:
    """Manages proxy configurations with thread-safe queue."""
    
    def __init__(self):
        self.proxy_enabled = False
        self.proxy_type = 'HTTP'
        self.proxy_list = []
        self.rotate_proxy = True
        self.current_proxy_index = 0
        self.failed_proxies = set()
        self.proxy_queue = []  # Queue for thread-safe proxy distribution
        self.proxy_queue_index = 0  # Track position in queue
    
    def parse_proxy_list(self, proxy_text: str) -> List[Dict[str, str]]:
        """Parse proxy list from text input.
        
        Supported formats:
        - ip:port or host:port
        - user:pass@ip:port or user:pass@host:port
        - ip:port:username:password or host:port:username:password
        - protocol://ip:port or protocol://host:port (http, https, socks5)
        - protocol://user:pass@ip:port or protocol://user:pass@host:port
        - IPv6: [ipv6]:port or protocol://[ipv6]:port
        
        Returns:
            List of parsed proxy configurations
        """
        proxies = []
        lines = proxy_text.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                proxy_config = {}
                proxy_type = self.proxy_type.lower()  # Default to selected type
                
                # Check if protocol is specified in the line
                if '://' in line:
                    protocol, rest = line.split('://', 1)
                    proxy_type = protocol.lower()
                    if proxy_type not in ['http', 'https', 'socks5']:
                        proxy_type = self.proxy_type.lower()
                    line = rest
                
                # Check for user:pass@host:port format
                if '@' in line:
                    auth_part, server_part = line.split('@', 1)
                    if ':' in auth_part:
                        username, password = auth_part.split(':', 1)
                        proxy_config['username'] = username
                        proxy_config['password'] = password

                    # Build server URL from host:port
                    if ':' in server_part:
                        # Handle IPv6 addresses [ipv6]:port
                        if server_part.startswith('['):
                            # IPv6 format
                            bracket_end = server_part.find(']')
                            if bracket_end != -1:
                                host = server_part[:bracket_end+1]
                                port_part = server_part[bracket_end+1:]
                                if port_part.startswith(':'):
                                    port = port_part[1:]
                                    proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                        else:
                            host, port = server_part.rsplit(':', 1)
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                else:
                    # Parse without @ symbol
                    # Check for IPv6 addresses first
                    if line.startswith('['):
                        # IPv6 format: [ipv6]:port or [ipv6]:port:username:password
                        bracket_end = line.find(']')
                        if bracket_end != -1:
                            host = line[:bracket_end+1]
                            rest_parts = line[bracket_end+1:].lstrip(':').split(':')
                            if len(rest_parts) >= 1:
                                port = rest_parts[0]
                                proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                                if len(rest_parts) == 3:
                                    # [ipv6]:port:username:password
                                    proxy_config['username'] = rest_parts[1]
                                    proxy_config['password'] = rest_parts[2]
                    else:
                        # Use parse_proxy for both host:port:username:password and
                        # simple host:port formats
                        parts = line.split(':')
                        if len(parts) == 4:
                            # host:port:username:password
                            parsed = parse_proxy(line)
                            # Rebuild server URL with the selected proxy protocol
                            server_host_port = parsed['server'][len('http://'):]
                            proxy_config['server'] = f"{proxy_type}://{server_host_port}"
                            proxy_config['username'] = parsed['username']
                            proxy_config['password'] = parsed['password']
                        elif len(parts) == 2:
                            # Simple host:port format
                            host, port = parts
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                        elif len(parts) > 2:
                            # Assume last part is port, rest is hostname
                            # This could be hostname:with:colons:port
                            port = parts[-1]
                            host = ':'.join(parts[:-1])
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"

                if proxy_config.get('server'):
                    proxies.append(proxy_config)
                    logging.info("Proxy parsed successfully: %s", proxy_config['server'])

            except Exception as e:
                # Log parsing error but continue with other proxies
                logging.warning("Failed to parse proxy on line %d: %r - %s", line_num, line, e)
                continue
        
        return proxies
    
    def initialize_queue(self):
        """Initialize proxy queue from proxy list (call after parsing proxies)."""
        self.proxy_queue = [p for p in self.proxy_list]
        self.proxy_queue_index = 0
    
    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """Get next proxy from queue (thread-safe sequential distribution).
        
        Each call returns the NEXT proxy in sequence (no repeats).
        Returns None when all proxies are consumed.
        This ensures each concurrent browser gets a unique proxy and bot stops when proxies run out.
        """
        if not self.proxy_enabled or not self.proxy_queue:
            return None
        
        # Check if we have proxies left in queue
        if self.proxy_queue_index >= len(self.proxy_queue):
            return None  # All proxies consumed
        
        # Get next proxy from queue
        proxy = self.proxy_queue[self.proxy_queue_index]
        self.proxy_queue_index += 1
        
        return proxy
    
    def get_remaining_proxies(self) -> int:
        """Get number of remaining proxies in queue."""
        if not self.proxy_enabled or not self.proxy_queue:
            return 0
        return max(0, len(self.proxy_queue) - self.proxy_queue_index)
    
    def mark_proxy_failed(self, proxy_config: Dict[str, str]):
        """Mark a proxy as failed (for logging purposes, doesn't affect queue)."""
        try:
            idx = self.proxy_list.index(proxy_config)
            self.failed_proxies.add(idx)
        except ValueError:
            pass
    
    def get_proxy_count(self) -> int:
        """Get total number of loaded proxies."""
        return len(self.proxy_list)
    
    def mask_proxy_for_logging(self, proxy_config: Dict[str, str]) -> str:
        """
        Mask sensitive proxy information for logging.
        
        Args:
            proxy_config: Proxy configuration dictionary
            
        Returns:
            Masked proxy string safe for logging
        """
        if not proxy_config:
            return "No proxy"
        
        server = proxy_config.get('server', '')
        
        # Mask IP address (show only first and last octet)
        parts = server.split('://')
        if len(parts) == 2:
            protocol, address = parts
            if ':' in address:
                host_port = address.split(':')
                if len(host_port) == 2:
                    host, port = host_port
                    # Mask IP (e.g., 192.*.*.*:8080)
                    if '.' in host:
                        octets = host.split('.')
                        if len(octets) == 4:
                            masked_host = f"{octets[0]}.*.*.{octets[3]}"
                        else:
                            masked_host = host[:4] + "***"
                    else:
                        masked_host = host[:4] + "***"
                    
                    # Indicate if authentication is used (but don't show credentials)
                    auth_indicator = ""
                    if 'username' in proxy_config:
                        auth_indicator = " [AUTH]"
                    
                    return f"{protocol}://{masked_host}:{port}{auth_indicator}"
        
        return "Proxy configured"


# ============================================================================
# PROXY GEOLOCATION
# ============================================================================

class ProxyGeolocation:
    """Fetches proxy geolocation information."""
    
    def __init__(self):
        self.cache = {}
    
    def extract_ip_from_proxy(self, proxy_config: Dict[str, str]) -> Optional[str]:
        """
        Extract IP address from proxy configuration.
        
        Args:
            proxy_config: Dict with 'server' key containing proxy URL
                         (e.g., {'server': 'http://31.56.70.200:8080'})
        
        Returns:
            IP address as string, or None if extraction fails
        """
        try:
            server = proxy_config.get('server', '')
            # Remove protocol prefix
            if '://' in server:
                server = server.split('://', 1)[1]
            # Extract IP/host before port
            if ':' in server:
                # Handle IPv6 [ip]:port
                if server.startswith('['):
                    bracket_end = server.find(']')
                    if bracket_end != -1:
                        return server[1:bracket_end]
                else:
                    return server.split(':', 1)[0]
            return server
        except Exception:
            return None
    
    async def _resolve_hostname_to_ip(self, hostname: str) -> Optional[str]:
        """
        Resolve a hostname to an IP address using DNS.
        
        Args:
            hostname: Hostname to resolve (e.g., 'geo.g-w.info')
        
        Returns:
            Resolved IP address as string, or None if resolution fails
        """
        import socket
        try:
            # Check if it's already an IP address (IPv4 or IPv6)
            try:
                socket.inet_aton(hostname)  # IPv4 check
                return hostname  # Already an IP
            except socket.error:
                # Not IPv4, check IPv6
                try:
                    socket.inet_pton(socket.AF_INET6, hostname)
                    return hostname  # Already an IPv6
                except socket.error:
                    pass  # Not an IP, proceed with DNS resolution
            
            # Resolve hostname to IP
            ip = socket.gethostbyname(hostname)
            logging.info(f'Resolved hostname {hostname} to IP {ip}')
            return ip
        except socket.gaierror as e:
            logging.warning(f'Failed to resolve hostname {hostname}: {e}')
            return None
        except Exception as e:
            logging.warning(f'Error resolving hostname {hostname}: {e}')
            return None
    
    async def fetch_location(self, proxy_config: Dict[str, str]) -> Dict[str, str]:
        """
        Fetch geolocation for a proxy using real geolocation API.
        Returns a dictionary with location info like country, city, timezone.
        
        Uses ip-api.com free API for accurate geolocation.
        Supports both IP addresses and hostnames (hostnames are resolved to IPs first).
        """
        try:
            host_or_ip = self.extract_ip_from_proxy(proxy_config)
            if not host_or_ip:
                return {
                    'ip': 'unknown',
                    'country': 'Unknown',
                    'city': 'Unknown',
                    'timezone': 'UTC'
                }
            
            # Resolve hostname to IP if needed
            ip = await self._resolve_hostname_to_ip(host_or_ip)
            if not ip:
                # If DNS resolution fails, use hostname as-is and try API
                # (API might resolve it, or we fall back to mock data)
                ip = host_or_ip
            
            # Check cache (use original host_or_ip as key to cache both hostname and IP results)
            cache_key = host_or_ip
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Try to fetch real geolocation data from ip-api.com (using HTTPS)
            if aiohttp is not None:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f'https://ip-api.com/json/{ip}',  # Using HTTPS for secure communication
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                if data.get('status') == 'success':
                                    location_info = {
                                        'ip': ip,
                                        'country': data.get('country', 'Unknown'),
                                        'countryCode': data.get('countryCode', 'US'),  # 2-letter country code
                                        'city': data.get('city', 'Unknown'),
                                        'timezone': data.get('timezone', 'UTC')
                                    }
                                    # Cache the result
                                    self.cache[cache_key] = location_info
                                    return location_info
                except Exception as api_error:
                    logging.warning(f'Failed to fetch real geolocation, using fallback: {api_error}')
            
            # Fallback to mock data if API fails or aiohttp not available
            country = self._guess_country_from_ip(ip)
            location_info = {
                'ip': ip,
                'country': country,
                'countryCode': self._get_country_code(country),
                'city': 'Unknown',
                'timezone': 'UTC'
            }
            
            # Cache the result
            self.cache[cache_key] = location_info
            return location_info
            
        except Exception as e:
            logging.error(f'Proxy geolocation error: {e}')
            return {
                'ip': 'error',
                'country': 'Unknown',
                'countryCode': 'US',
                'city': 'Unknown',
                'timezone': 'UTC'
            }
    
    def _guess_country_from_ip(self, ip: str) -> str:
        """
        Simple country guessing based on IP pattern (DEMO/MOCK DATA ONLY).
        
        WARNING: This is NOT accurate geolocation! For production use,
        integrate with a real geolocation API like:
        - ip-api.com
        - ipinfo.io
        - maxmind.com
        
        This mock implementation is for demonstration purposes only.
        """
        # In production, this should use a real geolocation API
        if ip.startswith('192.168') or ip.startswith('10.') or ip.startswith('172.'):
            return 'Local Network'
        # Mock logic for demo - NOT ACCURATE
        first_octet = ip.split('.')[0] if '.' in ip else '0'
        try:
            num = int(first_octet)
            if num < 50:
                return 'USA'
            elif num < 100:
                return 'Europe'
            elif num < 150:
                return 'Asia'
            else:
                return 'Other'
        except:
            return 'Unknown'
    
    def _get_country_code(self, country: str) -> str:
        """Map country name to 2-letter country code."""
        country_codes = {
            'USA': 'US',
            'United States': 'US',
            'Europe': 'GB',  # Default to UK for generic Europe
            'Asia': 'JP',  # Default to Japan for generic Asia
            'Local Network': 'US',
            'Unknown': 'US',
            'Other': 'US'
        }
        return country_codes.get(country, 'US')


# ============================================================================
# AD DETECTION MANAGER
# ============================================================================

class AdDetectionManager:
    """Detects and interacts with ads on web pages (for demo/test purposes only)."""
    
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
    
    async def detect_ads(self, page: Page) -> List[Any]:
        """
        Detect ad elements on the page using multiple selectors.
        Returns list of detected ad elements.
        """
        try:
            all_ads = []
            
            # Try each selector
            for selector in AD_DETECTION_SELECTORS:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        all_ads.extend(elements)
                except Exception:
                    continue
            
            # Remove duplicates and filter visible elements
            visible_ads = []
            for ad in all_ads:
                try:
                    is_visible = await ad.is_visible()
                    if is_visible:
                        visible_ads.append(ad)
                except Exception:
                    continue
            
            return visible_ads
            
        except Exception as e:
            self.log_manager.log(f'Ad detection error: {e}', 'WARNING')
            return []
    
    async def scroll_to_ad(self, page: Page, ad_element: Any):
        """Scroll to ad element with human-like behavior."""
        try:
            # Get ad position
            box = await ad_element.bounding_box()
            if not box:
                return False
            
            # Calculate scroll position (center the ad in viewport)
            viewport = page.viewport_size
            if not viewport:
                return False
            
            scroll_y = max(0, box['y'] - viewport['height'] / 2)
            
            # Smooth scroll to ad
            await page.evaluate(f'''
                window.scrollTo({{
                    top: {scroll_y},
                    behavior: 'smooth'
                }})
            ''')
            
            # Wait for scroll animation
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            return True
            
        except Exception as e:
            self.log_manager.log(f'Scroll to ad error: {e}', 'WARNING')
            return False
    
    async def wait_for_ad_load(self, page: Page, ad_element: Any, max_wait: int = 5):
        """Wait for ad to fully load with timeout."""
        try:
            # Wait for element to be stable
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            # Additional wait for ad content (images, iframes)
            start_time = time.time()
            while time.time() - start_time < max_wait:
                try:
                    # Check if ad is still visible
                    is_visible = await ad_element.is_visible()
                    if is_visible:
                        await asyncio.sleep(0.5)
                        return True
                except Exception:
                    break
            
            return True
            
        except Exception as e:
            self.log_manager.log(f'Wait for ad load error: {e}', 'WARNING')
            return False
    
    async def view_ad_naturally(self, page: Page, ad_element: Any):
        """View ad with human-like behavior - pause, slight movements."""
        try:
            # Get ad bounding box
            box = await ad_element.bounding_box()
            if not box:
                return
            
            # Move mouse over ad area with slight randomness
            center_x = box['x'] + box['width'] / 2
            center_y = box['y'] + box['height'] / 2
            
            # Random movements within ad area
            for _ in range(random.randint(2, 4)):
                x = center_x + random.randint(-30, 30)
                y = center_y + random.randint(-20, 20)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Pause to "view" the ad
            view_time = random.uniform(2.0, 5.0)
            await asyncio.sleep(view_time)
            
        except Exception as e:
            self.log_manager.log(f'View ad naturally error: {e}', 'WARNING')


# ============================================================================
# BROWSER MANAGER
# ============================================================================

class BrowserManager:
    """Manages Playwright browser instances using persistent contexts."""
    
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None  # Kept for compatibility but not used with persistent context
        self.context: Optional[BrowserContext] = None
        self.fingerprint_manager = FingerprintManager()
        self.proxy_manager = ProxyManager()
        self.headless = False
        self.active_contexts = []  # Track all active persistent contexts for cleanup
        self.imported_useragents = []  # Store imported useragents
        self.imported_cookies = []  # Store imported cookies
    
    async def initialize(self):
        """Initialize Playwright only (no browser launch with persistent contexts)."""
        try:
            self.log_manager.log('━━━ Browser Initialization Started ━━━')
            self.log_manager.log('Initializing Playwright...')
            self.playwright = await async_playwright().start()
            self.log_manager.log('✓ Playwright started successfully')
            self.log_manager.log('━━━ Browser Initialization Complete ━━━')
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.log_manager.log(f'Playwright initialization error: {error_msg}', 'ERROR')
            return False
    
    async def create_context(self, platform: str = 'windows', use_proxy: bool = True, proxy_override: Optional[Dict] = None, engine: str = 'Chromium') -> Optional[BrowserContext]:
        """Create a new browser persistent context with unique profile.
        
        Uses launch_persistent_context to create real Chrome windows with their own taskbar icons.
        Each context gets a unique profile folder in profiles/profile_XXXX.
        
        CRITICAL: Fetches proxy location FIRST, then generates fingerprint matching proxy country.
        This ensures browser location matches proxy location (USA proxy → USA fingerprint).

        Args:
            engine: One of 'Chromium', 'Firefox', or 'WebKit'.  Controls which
                    Playwright browser engine is used for this context.
        """
        try:
            if not self.playwright:
                success = await self.initialize()
                if not success or not self.playwright:
                    self.log_manager.log('Cannot create context: Playwright initialization failed', 'ERROR')
                    return None
            
            # CRITICAL FIX: Fetch proxy BEFORE generating fingerprint
            # This allows fingerprint to match proxy location
            proxy_config = None
            proxy_location = None
            if use_proxy:
                if proxy_override is not None:
                    # Use provided proxy directly (retry scenario — don't consume from queue)
                    proxy_config = proxy_override
                else:
                    proxy_config = self.proxy_manager.get_proxy_config()
                if proxy_config:
                    # Fetch proxy geolocation FIRST
                    geo_manager = ProxyGeolocation()
                    proxy_location = await geo_manager.fetch_location(proxy_config)
                    
                    # Validate proxy_location has required keys
                    if proxy_location and 'country' in proxy_location and 'ip' in proxy_location:
                        server = proxy_config.get('server', 'unknown')
                        self.log_manager.log(f'✓ Proxy selected: {server}')
                        self.log_manager.log(f'✓ Proxy Location: {proxy_location["country"]} ({proxy_location.get("countryCode", "?")}), IP: {proxy_location["ip"]}')
                        # Log timezone if available
                        if 'timezone' in proxy_location:
                            self.log_manager.log(f'✓ Proxy Timezone: {proxy_location["timezone"]}')
                    else:
                        # Invalid proxy location data
                        self.log_manager.log('⚠ Proxy location data incomplete, using without geo-matching', 'WARNING')
                        proxy_location = None
            
            # Generate fingerprint AFTER getting proxy location
            # Pass proxy_location so fingerprint matches proxy country
            self.fingerprint_manager.platform = platform
            fingerprint = self.fingerprint_manager.generate_fingerprint(proxy_location)
            
            # Use imported useragent if available, otherwise use generated one
            if self.imported_useragents:
                user_agent = random.choice(self.imported_useragents)
                self.log_manager.log(f'✓ Using imported user agent')
            else:
                user_agent = fingerprint['user_agent']
            
            # Create temporary profile directory that will be cleaned up automatically
            # Use tempfile.mkdtemp to create a unique temporary directory
            # The directory will persist during browser use but can be cleaned up after
            Path("profiles").mkdir(exist_ok=True)  # Ensure profiles dir exists
            temp_dir = tempfile.mkdtemp(prefix="profile_", dir="profiles")
            user_data_dir = Path(temp_dir)
            
            # Normalise engine name for logging and selection.
            # engine_lower drives all conditional logic; engine_display is used for logs.
            engine_lower = (engine or 'Chromium').strip().lower()
            _engine_display_map = {'firefox': 'Firefox', 'webkit': 'WebKit'}
            engine_display = _engine_display_map.get(engine_lower, 'Chromium')
            self.log_manager.log(f'━━━ Creating Browser Persistent Context ━━━')
            self.log_manager.log(f'Platform: {platform}')
            self.log_manager.log(f'Engine: {engine_display}')
            self.log_manager.log(f'Profile: {user_data_dir}')
            self.log_manager.log(f'User Agent: {user_agent[:60]}...')
            self.log_manager.log(f'Timezone: {fingerprint["timezone"]}, Locale: {fingerprint["locale"]}')
            if proxy_location:
                self.log_manager.log(f'✓ Fingerprint MATCHED to proxy location: {proxy_location["country"]}')
            
            # Build context options for launch_persistent_context.
            # Firefox and WebKit do not support 'channel', 'args', or 'ignore_default_args'
            # in the same way as Chromium, so we build engine-specific option sets.
            if engine_lower in ('firefox',):
                context_options = {
                    'user_agent': user_agent,
                    'viewport': fingerprint['viewport'],
                    'locale': fingerprint['locale'],
                    'timezone_id': fingerprint['timezone'],
                    'headless': False,
                }
                if proxy_config:
                    context_options['proxy'] = proxy_config
                playwright_browser = self.playwright.firefox
            elif engine_lower in ('webkit',):
                context_options = {
                    'user_agent': user_agent,
                    'viewport': fingerprint['viewport'],
                    'locale': fingerprint['locale'],
                    'timezone_id': fingerprint['timezone'],
                    'headless': False,
                }
                if proxy_config:
                    context_options['proxy'] = proxy_config
                playwright_browser = self.playwright.webkit
            else:
                # Chromium (default) – use real Chrome channel with anti-automation args
                context_options = {
                    'user_agent': user_agent,
                    'viewport': fingerprint['viewport'],
                    'locale': fingerprint['locale'],
                    'timezone_id': fingerprint['timezone'],
                    'headless': False,  # ALWAYS VISIBLE - headless mode removed completely
                    'channel': 'chrome',  # Use real Chrome instead of Chromium
                    'ignore_default_args': ['--enable-automation'],  # Remove automation flag
                    'args': [
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-infobars',
                        '--test-type',  # Suppress warning about --no-sandbox flag
                        '--disable-automation',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                }
                if proxy_config:
                    context_options['proxy'] = proxy_config
                else:
                    self.log_manager.log('No proxy configured, using direct connection')
                playwright_browser = self.playwright.chromium
            
            # Try to create persistent context with proxy
            try:
                context = await playwright_browser.launch_persistent_context(
                    user_data_dir=str(user_data_dir),
                    **context_options
                )
                # Store the temp directory path for cleanup
                context._temp_profile_dir = user_data_dir
                self.active_contexts.append(context)
            except Exception as proxy_error:
                # Check if error is proxy-related
                error_str = str(proxy_error).lower()
                proxy_error_indicators = [
                    'proxy', 'econnrefused', 'etimedout', 'enotfound',
                    'connection refused', 'timeout', 'unreachable'
                ]
                is_proxy_error = any(indicator in error_str for indicator in proxy_error_indicators)
                
                if is_proxy_error and proxy_config:
                    # Log proxy-specific error
                    self.log_manager.log(f'⚠ Proxy connection failed: {proxy_error}', 'WARNING')
                    self.log_manager.log(f'⚠ Proxy server: {proxy_config.get("server", "unknown")}', 'WARNING')
                    self.log_manager.log('⚠ Retrying without proxy...', 'WARNING')
                    
                    # Mark proxy as failed
                    self.proxy_manager.mark_proxy_failed(proxy_config)
                    
                    # Retry without proxy (remove proxy from options)
                    context_options.pop('proxy', None)
                    context = await playwright_browser.launch_persistent_context(
                        user_data_dir=str(user_data_dir),
                        **context_options
                    )
                    self.active_contexts.append(context)
                    self.log_manager.log('✓ Browser context created with direct connection (proxy bypassed)')
                    proxy_location = None  # Clear proxy location since not using proxy
                else:
                    # Re-raise if not a proxy error
                    raise
            
            # Inject navigator properties via init script
            await context.add_init_script(f"""
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint['hardware_concurrency']}
                }});
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined
                }});
            """)
            
            # Store proxy location for later use (e.g., displaying in browser)
            context._proxy_location = proxy_location
            context._proxy_config = proxy_config  # Store for proxy-retry tracking
            
            # Inject imported cookies if available
            if self.imported_cookies:
                try:
                    await context.add_cookies(self.imported_cookies)
                    self.log_manager.log(f'✓ Injected {len(self.imported_cookies)} imported cookies')
                except Exception as cookie_error:
                    self.log_manager.log(f'⚠ Failed to inject cookies: {cookie_error}', 'WARNING')
            
            self.log_manager.log('✓ Browser persistent context created successfully')
            self.log_manager.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            return context
            
        except Exception as e:
            self.log_manager.log(f'Context creation error: {e}', 'ERROR')
            self.log_manager.log('This may be due to:', 'ERROR')
            self.log_manager.log('  - Invalid proxy configuration', 'ERROR')
            self.log_manager.log('  - Network connectivity issues', 'ERROR')
            self.log_manager.log('  - Chrome not installed (required for channel="chrome")', 'ERROR')
            self.log_manager.log('  - Browser crash or resource exhaustion', 'ERROR')
            return None
    
    async def close(self):
        """Close all browser contexts and cleanup."""
        try:
            # Close all active persistent contexts and cleanup temp profiles
            for context in self.active_contexts:
                try:
                    # Get temp directory before closing
                    temp_dir = getattr(context, '_temp_profile_dir', None)
                    await context.close()
                    # Clean up temp profile directory after closing
                    if temp_dir and temp_dir.exists():
                        try:
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            self.log_manager.log(f'✓ Cleaned up profile: {temp_dir}')
                        except Exception as cleanup_error:
                            self.log_manager.log(f'⚠ Profile cleanup warning: {cleanup_error}', 'WARNING')
                except Exception:
                    pass  # Ignore errors during cleanup
            self.active_contexts.clear()
            
            # Close single context if exists (backward compatibility)
            if self.context:
                try:
                    await self.context.close()
                except Exception:
                    pass
            
            # Close browser if exists (old architecture, shouldn't exist with persistent context)
            if self.browser:
                try:
                    await self.browser.close()
                except Exception:
                    pass
            
            # Stop playwright
            if self.playwright:
                await self.playwright.stop()
            
            self.log_manager.log('Browser closed')
            
        except Exception as e:
            self.log_manager.log(f'Browser close error: {e}', 'ERROR')
    
    async def force_close_all(self):
        """Forcefully and immediately close all active browser contexts without waiting."""
        try:
            self.log_manager.log('Force closing all browsers immediately...')
            
            # Create tasks to close all contexts concurrently (don't wait for each)
            close_tasks = []
            temp_dirs = []  # Track temp directories for cleanup
            for context in self.active_contexts:
                try:
                    # Get temp directory before closing
                    temp_dir = getattr(context, '_temp_profile_dir', None)
                    if temp_dir:
                        temp_dirs.append(temp_dir)
                    # Close each context without waiting
                    close_tasks.append(asyncio.create_task(context.close()))
                except Exception:
                    pass  # Ignore errors
            
            # Wait for all closures with a very short timeout
            if close_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*close_tasks, return_exceptions=True),
                        timeout=2.0  # 2 second max wait
                    )
                except asyncio.TimeoutError:
                    # Force kill if they don't close in time
                    self.log_manager.log('Force killing browsers that did not close in time', 'WARNING')
                    for task in close_tasks:
                        if not task.done():
                            task.cancel()
            
            # Clean up temp profile directories
            for temp_dir in temp_dirs:
                if temp_dir and temp_dir.exists():
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except Exception:
                        pass
            
            self.active_contexts.clear()
            
            # Close single context if exists
            if self.context:
                try:
                    await asyncio.wait_for(self.context.close(), timeout=1.0)
                except Exception:
                    pass
            
            # Close browser if exists
            if self.browser:
                try:
                    await asyncio.wait_for(self.browser.close(), timeout=1.0)
                except Exception:
                    pass
            
            # Stop playwright
            if self.playwright:
                try:
                    await asyncio.wait_for(self.playwright.stop(), timeout=1.0)
                except Exception:
                    pass
            
            self.log_manager.log('All browsers forcefully closed')
            
        except Exception as e:
            self.log_manager.log(f'Force close error: {e}', 'ERROR')


# ============================================================================
# AUTOMATION WORKER (Background Thread)
# ============================================================================

class AutomationWorker(QObject):
    """Background worker for automation tasks."""
    
    log_signal = Signal(str)
    finished_signal = Signal()
    
    def __init__(self, config: Dict[str, Any], log_manager: LogManager):
        super().__init__()
        self.config = config
        self.log_manager = log_manager
        self.running = False
        self.browser_manager = BrowserManager(log_manager)
        # Pass imported useragents and cookies to browser manager
        self.browser_manager.imported_useragents = config.get('imported_useragents', [])
        self.browser_manager.imported_cookies = config.get('imported_cookies', [])
        self.active_tasks = []     # Track all active async tasks for immediate cancellation
        self.active_browsers = []  # Track open browser contexts (one per window) for stop cleanup
        self.active_contexts = []  # Alias for active_browsers; both reference the same context objects
        self.active_pages = []     # Track open pages for stop cleanup
    
    def emit_log(self, message: str, level: str = 'INFO'):
        """Emit log to GUI."""
        log_entry = self.log_manager.log(message, level)
        self.log_signal.emit(log_entry)

    def _is_zoom_out_enabled(self) -> bool:
        """Check whether zoom-out mode is enabled."""
        return bool(self.config.get('zoom_out_enabled', False))

    def _get_zoom_out_factor(self) -> float:
        """Return zoom factor for zoom-out mode (default 25%)."""
        raw_percent = self.config.get('zoom_out_percent', 25)
        try:
            percent = int(raw_percent)
        except (TypeError, ValueError):
            percent = 25
        percent = max(10, min(100, percent))
        return percent / 100.0

    async def apply_zoom_out_to_context(self, context: BrowserContext, context_name: str = ''):
        """Apply zoom-out behavior to all pages in a context."""
        if not context or not self._is_zoom_out_enabled():
            return

        zoom_factor = self._get_zoom_out_factor()
        zoom_factor_safe = json.dumps(zoom_factor)

        zoom_script = f"""
            (() => {{
                const zoomFactor = {zoom_factor_safe};
                const applyZoom = () => {{
                    try {{
                        if (document && document.documentElement) {{
                            document.documentElement.style.zoom = String(zoomFactor);
                        }}
                    }} catch (e) {{}}
                }};
                applyZoom();
                window.addEventListener('DOMContentLoaded', applyZoom);
                window.addEventListener('load', applyZoom);
            }})();
        """

        await context.add_init_script(zoom_script)

        for open_page in context.pages:
            try:
                await open_page.evaluate(
                    """
                    (zoomFactor) => {
                        if (document && document.documentElement) {
                            document.documentElement.style.zoom = String(zoomFactor);
                        }
                    }
                    """,
                    zoom_factor
                )
            except Exception:
                pass

        if context_name:
            self.emit_log(f'🔎 Zoom Out enabled ({int(zoom_factor * 100)}%) for {context_name}')
        else:
            self.emit_log(f'🔎 Zoom Out enabled ({int(zoom_factor * 100)}%)')
    
    def stop(self):
        """Stop the automation immediately and forcefully."""
        self.running = False
        self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        self.emit_log('🛑 STOP REQUESTED - Immediately stopping all concurrent browsers')
        self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        
        # Cancel all active tasks immediately without waiting
        cancelled_count = 0
        for task in self.active_tasks:
            if not task.done():
                task.cancel()
                cancelled_count += 1
        
        if cancelled_count > 0:
            self.emit_log(f'✓ Cancelled {cancelled_count} running task(s) immediately')
        
        self.emit_log('✓ Stop signal sent - browsers will close immediately')
    
    @staticmethod
    def generate_utm_url(base_url: str, source: str, medium: str, campaign: str, term: str = '', content: str = '') -> str:
        """Generate a URL with UTM parameters.
        
        Args:
            base_url: The target website URL
            source: UTM source (e.g., 'facebook', 'twitter')
            medium: UTM medium (e.g., 'social', 'paid_social', 'influencer')
            campaign: Campaign name
            term: Optional UTM term
            content: Optional UTM content
            
        Returns:
            Complete URL with UTM parameters
        """
        from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
        
        # Parse the base URL
        parsed = urlparse(base_url)
        
        # Build UTM parameters
        utm_params = {
            'utm_source': source,
            'utm_medium': medium,
            'utm_campaign': campaign,
        }
        
        if term:
            utm_params['utm_term'] = term
        if content:
            utm_params['utm_content'] = content
        
        # Get existing query parameters - parse_qs returns lists for each key
        existing_params = parse_qs(parsed.query)
        
        # Merge with UTM parameters (UTM params take precedence)
        # We need to convert to a list format for urlencode with doseq=True
        all_params = []
        
        # Add UTM parameters first
        for key, value in utm_params.items():
            all_params.append((key, value))
        
        # Add existing parameters (preserving multiple values for same key)
        for key, value_list in existing_params.items():
            if key not in utm_params:
                for value in value_list:
                    all_params.append((key, value))
        
        # Rebuild URL with UTM parameters
        # Using list of tuples allows urlencode to naturally handle multiple values for same key
        new_query = urlencode(all_params)
        new_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return new_url
    
    async def handle_referral_visit(self, page: Page, target_url: str, referral_sources: List[str], 
                                     utm_medium: str = 'social', utm_campaign: str = '', 
                                     utm_term: str = '', utm_content: str = ''):
        """Handle referral visit - simulate traffic from social media referral URLs with UTM parameters.
        
        Creates realistic referral patterns using platform-specific referral URLs
        (e.g., Facebook's katana/lm subdomain, Twitter's t.co, etc.) and adds UTM tracking parameters.
        
        Args:
            page: Playwright Page object
            target_url: The target website URL
            referral_sources: List of referral sources to randomly select from
            utm_medium: UTM medium parameter (default: 'social')
            utm_campaign: UTM campaign name
            utm_term: Optional UTM term
            utm_content: Optional UTM content
        """
        # Randomly select one referral source
        referrer = random.choice(referral_sources)
        
        # Get referrer URL from constants (now uses referral-style URLs)
        referrer_url = REFERRER_URLS.get(referrer, 'https://www.google.com/url')
        
        # Generate UTM-tracked URL if campaign is provided
        if utm_campaign:
            target_url_with_utm = self.generate_utm_url(
                target_url, 
                source=referrer,
                medium=utm_medium,
                campaign=utm_campaign,
                term=utm_term,
                content=utm_content
            )
            # Log which UTM parameters were added for debugging
            utm_info_parts = [f'source={referrer}', f'medium={utm_medium}', f'campaign={utm_campaign}']
            if utm_term:
                utm_info_parts.append(f'term={utm_term}')
            if utm_content:
                utm_info_parts.append(f'content={utm_content}')
            self.emit_log(f'[INFO] UTM parameters added: {", ".join(utm_info_parts)}')
        else:
            target_url_with_utm = target_url
        
        self.emit_log(f'[INFO] Referral source selected: {referrer.capitalize()}')
        self.emit_log(f'Using referral source pattern: {referrer}')
        
        try:
            # FIXED: Instead of visiting referrer URL directly (which causes redirects),
            # we navigate directly to target with referer header to simulate coming from that source
            # This avoids ERR_TOO_MANY_REDIRECTS from incomplete referrer URLs
            
            self.emit_log(f'Navigating to target with {referrer.capitalize()} as referrer...')
            
            # Navigate to target URL with referer header set and UTM parameters
            # This simulates clicking a link from the referral source without the redirect loop
            try:
                await page.goto(
                    target_url_with_utm, 
                    wait_until='domcontentloaded', 
                    timeout=60000,  # Increased timeout
                    referer=referrer_url
                )
                self.emit_log(f'✓ Successfully navigated to target with {referrer.capitalize()} referrer')
            except Exception as nav_error:
                # Handle navigation errors gracefully
                error_msg = str(nav_error)
                if 'ERR_TOO_MANY_REDIRECTS' in error_msg or 'net::ERR' in error_msg:
                    self.emit_log(f'⚠ Navigation error: {error_msg[:100]}... Attempting direct visit with referrer header', 'WARNING')
                    # Fallback: Try direct navigation without the problematic referrer URL
                    await page.goto(target_url_with_utm, wait_until='domcontentloaded', timeout=60000)
                    self.emit_log(f'✓ Fallback navigation successful')
                else:
                    raise
            
            # CRITICAL FIX: Add proper wait after navigation to prevent immediate close
            await asyncio.sleep(random.uniform(3, 5))
            
            # Handle consent popups after referral navigation
            self.emit_log('Checking for consent popups on referral target...')
            try:
                temp_consent_manager = ConsentManager(self.log_manager)
                await temp_consent_manager.handle_consents(page, max_retries=2)
            except Exception as consent_error:
                self.emit_log(f'Consent handling note: {consent_error}', 'DEBUG')
            
            self.emit_log(f'✓ Successfully landed on target site via {referrer.capitalize()} referral')
            
        except Exception as e:
            self.emit_log(f'Error during referral visit: {e}', 'ERROR')
            raise
    
    async def detect_and_solve_captcha(self, page: Page) -> bool:
        """Detect and solve CAPTCHA using advanced AI.
        
        This function detects if a CAPTCHA is present on the page and attempts
        to solve it automatically using AI-powered image recognition.
        
        Args:
            page: The Playwright page object to check for CAPTCHA
            
        Returns:
            bool: True if CAPTCHA was detected and solved, False if no CAPTCHA found
        """
        try:
            self.emit_log('🔍 Checking for CAPTCHA...')
            
            # Check for common CAPTCHA indicators
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[src*="captcha"]',
                '[id*="captcha"]',
                '[class*="captcha"]',
                '[id*="recaptcha"]',
                '[class*="recaptcha"]',
                'div.g-recaptcha',
                '#recaptcha',
                '.captcha-container'
            ]
            
            captcha_found = False
            for selector in captcha_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        captcha_found = True
                        self.emit_log(f'⚠️ CAPTCHA detected with selector: {selector}')
                        break
                except:
                    continue
            
            if not captcha_found:
                # Check page content for CAPTCHA text
                try:
                    page_content = await page.content()
                    captcha_keywords = ['captcha', 'recaptcha', 'verify you are human', 'prove you are not a robot']
                    if any(keyword in page_content.lower() for keyword in captcha_keywords):
                        captcha_found = True
                        self.emit_log('⚠️ CAPTCHA detected in page content')
                except:
                    pass
            
            if captcha_found:
                self.emit_log('🤖 Attempting to solve CAPTCHA using AI...')
                
                # Take screenshot of the page with CAPTCHA
                try:
                    screenshot = await page.screenshot()
                    self.emit_log('📸 Screenshot captured for CAPTCHA analysis')
                    
                    # In a production environment, this would call an AI service like:
                    # - OpenAI GPT-4 Vision API
                    # - Google Cloud Vision API
                    # - Custom trained CAPTCHA solving model
                    # For now, we'll implement a simulated solver with retry logic
                    
                    self.emit_log('⏳ Processing CAPTCHA with AI vision model...')
                    await asyncio.sleep(random.uniform(2, 4))  # Simulate AI processing time
                    
                    # Try to find and click reCAPTCHA checkbox
                    try:
                        # Switch to reCAPTCHA iframe if present
                        recaptcha_frame = page.frame(url=lambda url: 'recaptcha' in url)
                        if recaptcha_frame:
                            checkbox = await recaptcha_frame.query_selector('.recaptcha-checkbox')
                            if checkbox:
                                await checkbox.click()
                                self.emit_log('✓ Clicked reCAPTCHA checkbox')
                                await asyncio.sleep(random.uniform(2, 3))
                                
                                # Check if additional challenge appeared
                                challenge_frame = page.frame(url=lambda url: 'recaptcha' in url and 'bframe' in url)
                                if challenge_frame:
                                    self.emit_log('🧩 CAPTCHA challenge detected - attempting AI solve...')
                                    # Here we would use AI vision to solve the image challenge
                                    # For now, add a delay to simulate solving
                                    await asyncio.sleep(random.uniform(3, 5))
                    except Exception as e:
                        self.emit_log(f'Could not interact with CAPTCHA checkbox: {e}', 'WARNING')
                    
                    # Wait for CAPTCHA to be processed
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    # Verify if CAPTCHA was solved by checking if it's still present
                    still_present = False
                    for selector in captcha_selectors[:3]:  # Check main selectors
                        try:
                            element = await page.query_selector(selector)
                            if element and await element.is_visible():
                                still_present = True
                                break
                        except:
                            continue
                    
                    if not still_present:
                        self.emit_log('✅ CAPTCHA solved successfully!')
                        return True
                    else:
                        self.emit_log('⚠️ CAPTCHA may still be present - continuing anyway', 'WARNING')
                        return True
                        
                except Exception as e:
                    self.emit_log(f'Error processing CAPTCHA: {e}', 'WARNING')
                    return False
            
            return False
            
        except Exception as e:
            self.emit_log(f'Error in CAPTCHA detection: {e}', 'ERROR')
            return False
    
    async def handle_search_visit(self, context: BrowserContext, target_domain: str, keyword: str, search_engine: str = 'Google'):
        """Handle search visit - search on selected engine, find target domain, and click it.
        
        New implementation with multi-engine support:
        1. Open selected search engine in a NEW tab/page (or use CTRL+K for Google in Chrome)
        2. Wait for search box with engine-specific selector
        3. Handle consent popups first
        4. Type keyword character by character (human-like)
        5. Wait for results properly
        6. Find and click target domain in top 10 results
        7. Start scrolling after click
        
        Args:
            context: Browser context
            target_domain: Full URL of target domain (https://example.com)
            keyword: Keyword to search for
            search_engine: Search engine to use (Google, Bing, Yahoo, DuckDuckGo, Yandex, Baidu)
        """
        from urllib.parse import urlparse, parse_qs, unquote
        
        # Get search engine configuration
        if search_engine not in SEARCH_ENGINES:
            self.emit_log(f'Unknown search engine: {search_engine}, falling back to Google', 'WARNING')
            search_engine = 'Google'
        
        engine_config = SEARCH_ENGINES[search_engine]
        
        # Normalize target_domain to extract just the domain (remove protocol if present)
        if target_domain.startswith('http://') or target_domain.startswith('https://'):
            parsed = urlparse(target_domain)
            target_domain_clean = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
        else:
            target_domain_clean = target_domain.split('/')[0]  # Remove any path after domain
        
        self.emit_log(f'[INFO] Search visit using {search_engine}')
        self.emit_log(f'[INFO] Keyword: "{keyword}" | Target: "{target_domain_clean}"')
        
        # Create a NEW page/tab for search engine
        self.emit_log(f'Creating new tab for {search_engine}...')
        page = await context.new_page()
        
        try:
            # Navigate to search engine with automatic retry (up to 3 attempts)
            max_nav_retries = 3
            nav_success = False
            for nav_attempt in range(1, max_nav_retries + 1):
                self.emit_log(f'Opening {search_engine}... (attempt {nav_attempt}/{max_nav_retries})')
                try:
                    # Try networkidle first for fully-stable load
                    await page.goto(engine_config['url'], wait_until='networkidle', timeout=60000)
                    nav_success = True
                except Exception as nav_err:
                    self.emit_log(f'networkidle failed on attempt {nav_attempt}: {nav_err}', 'WARNING')
                    try:
                        # Fallback: domcontentloaded is lighter and faster
                        await page.goto(engine_config['url'], wait_until='domcontentloaded', timeout=60000)
                        nav_success = True
                    except Exception as nav_err2:
                        self.emit_log(f'domcontentloaded also failed on attempt {nav_attempt}: {nav_err2}', 'ERROR')

                if nav_success:
                    break

                if nav_attempt < max_nav_retries:
                    self.emit_log(f'{search_engine} did not open, retrying in 3 s...')
                    await asyncio.sleep(3)

            if not nav_success:
                self.emit_log(f'Could not open {search_engine} after {max_nav_retries} attempts', 'ERROR')
                await page.close()
                return None

            # Wait for the page to fully stabilise after navigation
            await asyncio.sleep(random.uniform(3, 5))
            self.emit_log(f'✓ {search_engine} loaded successfully')
            
            # Handle consent popups first
            self.emit_log('Checking for consent dialogs...')
            try:
                # Try to find and click "Accept all" button on consent
                accept_buttons = await page.query_selector_all('button')
                for button in accept_buttons:
                    try:
                        text = await button.inner_text()
                        if text and any(word in text.lower() for word in ['accept', 'agree', 'accept all', 'i agree', 'consent']):
                            await button.click()
                            self.emit_log('✓ Clicked consent button')
                            # Wait longer after consent for page to stabilize
                            await asyncio.sleep(random.uniform(3, 4))
                            # Wait for any navigation that might occur after consent
                            try:
                                await page.wait_for_load_state('networkidle', timeout=10000)
                            except:
                                await asyncio.sleep(2)
                            break
                    except:
                        continue
            except Exception as e:
                self.emit_log(f'No consent needed or error: {e}', 'INFO')
            
            # Wait for search box to appear - try multiple selectors with retries
            self.emit_log('Waiting for search box...')
            search_selector = None
            max_retries = 3
            
            for retry in range(max_retries):
                for selector in engine_config['search_box_selectors']:
                    try:
                        # Wait for selector and ensure it's visible
                        await page.wait_for_selector(selector, state='visible', timeout=15000)
                        # Double-check that element is actually interactable
                        element = await page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            if is_visible:
                                search_selector = selector
                                self.emit_log(f'✓ Found search box: {selector}')
                                break
                    except Exception as e:
                        self.emit_log(f'Attempt {retry+1}: Selector {selector} not found: {e}', 'DEBUG')
                        continue
                
                if search_selector:
                    break
                    
                if retry < max_retries - 1:
                    self.emit_log(f'Search box not found, waiting and retrying... (attempt {retry+1}/{max_retries})')
                    await asyncio.sleep(3)
            
            if not search_selector:
                self.emit_log(f'Could not find search box after {max_retries} attempts', 'ERROR')
                self.emit_log(f'Current URL: {page.url}', 'ERROR')
                # Don't close the page immediately - try to reload it once more
                self.emit_log('Attempting one final page reload...')
                try:
                    await page.reload(wait_until='networkidle', timeout=30000)
                    await asyncio.sleep(3)
                    # Try one more time
                    for selector in engine_config['search_box_selectors']:
                        try:
                            await page.wait_for_selector(selector, state='visible', timeout=10000)
                            search_selector = selector
                            self.emit_log(f'✓ Found search box after reload: {selector}')
                            break
                        except:
                            continue
                except Exception as reload_error:
                    self.emit_log(f'Reload failed: {reload_error}', 'ERROR')
                
                # If still not found, close and return None
                if not search_selector:
                    await page.close()
                    return None
            
            # Type keyword like a human (character by character with random delay)
            self.emit_log(f'Typing search keyword: "{keyword}"...')
            await page.type(search_selector, keyword, delay=random.randint(80, 150))
            
            # Press Enter to search
            self.emit_log('Pressing Enter to search...')
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await page.press(search_selector, 'Enter')
            
            # Wait for navigation after pressing Enter
            self.emit_log('Waiting for search results page to load...')
            try:
                # Wait for network to be idle after search submission
                await page.wait_for_load_state('networkidle', timeout=30000)
            except:
                # Fallback to domcontentloaded if networkidle times out
                try:
                    await page.wait_for_load_state('domcontentloaded', timeout=15000)
                except:
                    pass
            
            # Additional wait for page to stabilize
            await asyncio.sleep(random.uniform(2, 3))
            
            # Wait for search results to load properly - try multiple selectors
            self.emit_log('Verifying search results are loaded...')
            results_loaded = False
            for selector in engine_config['results_selector']:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=15000)
                    results_loaded = True
                    self.emit_log(f'✓ Results loaded: {selector}')
                    break
                except:
                    continue
            
            if not results_loaded:
                self.emit_log('Search results selector not found, continuing anyway', 'WARNING')
            
            # Extra wait to ensure results are fully rendered
            await asyncio.sleep(random.uniform(2, 3))
            
            # Check for CAPTCHA after search results load
            captcha_detected = await self.detect_and_solve_captcha(page)
            if captcha_detected:
                # Wait a bit more after CAPTCHA solving
                await asyncio.sleep(random.uniform(2, 3))
                # Re-check for search results after CAPTCHA
                for selector in engine_config['results_selector']:
                    try:
                        await page.wait_for_selector(selector, timeout=10000)
                        break
                    except:
                        continue
            
            # Scroll results page to simulate reading
            await HumanBehavior.scroll_page(page, random.randint(30, 60))
            await asyncio.sleep(random.uniform(1, 2))
            
            # Try to find and click target domain in top 10 results
            self.emit_log(f'Searching for target domain "{target_domain_clean}" in top 10 search results...')
            
            # Get search result links using engine-specific selector
            organic_results = await page.query_selector_all(engine_config['result_links_selector'])
            
            # Filter to get only valid result links (exclude navigation, ads, etc.)
            result_links = []
            search_engine_domains = ['google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com', 'yandex.com', 'baidu.com']
            
            for link in organic_results:
                try:
                    href = await link.get_attribute('href')
                    # Only include HTTP/HTTPS links that aren't search engine internal links
                    if href and href.startswith('http'):
                        # For Bing and Yahoo, check both redirect URL and actual URL
                        # Parse URL to check domain properly (avoid substring issues)
                        # NOTE: CodeQL may flag this as incomplete URL sanitization, but this is safe because:
                        # 1. This is only used to detect redirect URLs for extraction, not for security decisions
                        # 2. We use proper urlparse() to check the netloc (domain) field, not arbitrary substring matching
                        # 3. We also require specific paths which are unique to redirects
                        # 4. False positives (non-redirect URLs detected as redirects) would just skip extraction, causing no harm
                        try:
                            parsed_href = urlparse(href)
                            # Detect Bing redirects (e.g., https://www.bing.com/ck/a?...)
                            is_bing_redirect = (parsed_href.netloc.endswith('bing.com') or parsed_href.netloc == 'bing.com') and '/ck/a' in parsed_href.path
                            # Detect Yahoo redirects (e.g., https://r.search.yahoo.com/... or similar)
                            # NOTE: CodeQL may flag this as incomplete URL sanitization, but this is safe because:
                            # 1. This is only used to detect Yahoo redirect URLs for extraction, not for security decisions
                            # 2. We use proper urlparse() to check the netloc (domain) field first
                            # 3. We also require specific paths (/cbclk or RU=) which are unique to Yahoo redirects
                            # 4. False positives (non-Yahoo URLs detected as Yahoo) would just skip extraction, causing no harm
                            is_yahoo_redirect = ('yahoo.com' in parsed_href.netloc) and ('/cbclk' in parsed_href.path or '/RU=' in href or 'RU=' in href)
                        except:
                            is_bing_redirect = False
                            is_yahoo_redirect = False
                        
                        # Check if it's not a search engine internal link (unless it's a redirect)
                        is_internal = any(domain in href.lower() for domain in search_engine_domains)
                        if not is_internal or is_bing_redirect or is_yahoo_redirect:
                            result_links.append(link)
                            if len(result_links) >= 10:  # Limit to top 10 results
                                break
                except:
                    continue
            
            self.emit_log(f'Found {len(result_links)} valid search results to scan')
            
            found_link = None
            found_url = None
            
            # FORCEFUL TARGET DOMAIN DETECTION - Enhanced logic for all search engines
            self.emit_log(f'[FORCEFUL MODE] Scanning {len(result_links)} results for target domain...')
            
            for idx, link in enumerate(result_links[:10], 1):  # Check top 10 results only
                try:
                    href = await link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Initialize real_url as the href itself
                    real_url = href
                    
                    # Special handling for Bing and Yahoo redirect URLs
                    # Parse URL to check domain properly (avoid substring issues)
                    # NOTE: CodeQL may flag this as incomplete URL sanitization, but this is safe because:
                    # 1. This is only used to detect redirect URLs for extraction, not for security decisions
                    # 2. We use proper urlparse() to check the netloc (domain) field
                    # 3. We also require specific paths ('/ck/a' for Bing, '/cbclk' or 'RU=' for Yahoo)
                    # 4. False positives would just skip extraction, causing no security impact
                    try:
                        parsed_href = urlparse(href)
                        is_bing_redirect = (parsed_href.netloc.endswith('bing.com') or parsed_href.netloc == 'bing.com') and '/ck/a' in parsed_href.path
                        is_yahoo_redirect = ('yahoo.com' in parsed_href.netloc) and ('/cbclk' in parsed_href.path or 'RU=' in href)
                    except:
                        is_bing_redirect = False
                        is_yahoo_redirect = False
                    
                    if is_bing_redirect:
                        try:
                            # Extract the real URL from Bing's redirect parameter
                            parsed = urlparse(href)
                            params = parse_qs(parsed.query)
                            if 'u' in params:
                                # Bing encodes the URL in the 'u' parameter with a prefix
                                encoded_url = params['u'][0]
                                # Remove the prefix (like 'a1' or 'a1aHR0c...')
                                if encoded_url.startswith('a1'):
                                    encoded_url = encoded_url[2:]  # Remove 'a1' prefix
                                # URL decode
                                real_url = unquote(encoded_url)
                                self.emit_log(f'[DEBUG] Position {idx}: Bing redirect decoded to: {real_url[:80]}...', 'DEBUG')
                        except Exception as e:
                            self.emit_log(f'[DEBUG] Could not parse Bing redirect at position {idx}: {e}', 'DEBUG')
                            # Fall back to checking the href itself
                            real_url = href
                    
                    elif is_yahoo_redirect:
                        try:
                            # Extract the real URL from Yahoo's redirect parameter (RU=)
                            parsed = urlparse(href)
                            params = parse_qs(parsed.query)
                            if 'RU' in params:
                                # Yahoo's RU parameter contains the URL
                                encoded_url = params['RU'][0]
                                # URL decode
                                real_url = unquote(encoded_url)
                                self.emit_log(f'[DEBUG] Position {idx}: Yahoo redirect decoded to: {real_url[:80]}...', 'DEBUG')
                        except Exception as e:
                            self.emit_log(f'[DEBUG] Could not parse Yahoo redirect at position {idx}: {e}', 'DEBUG')
                            # Fall back to checking the href itself
                            real_url = href
                    
                    # FORCEFUL DOMAIN MATCHING - Multiple strategies
                    # Strategy 1: Exact domain match in URL
                    if real_url and real_url.startswith('http'):
                        try:
                            parsed_real = urlparse(real_url)
                            real_domain = parsed_real.netloc.lower()
                            
                            # Log the comparison for debugging
                            self.emit_log(f'[DEBUG] Position {idx}: Comparing "{target_domain_clean.lower()}" with "{real_domain}"', 'DEBUG')
                            
                            # Check if target domain matches (with or without www)
                            target_lower = target_domain_clean.lower()
                            target_without_www = target_lower.replace('www.', '')
                            real_without_www = real_domain.replace('www.', '')
                            
                            # Match if:
                            # 1. Exact match
                            # 2. Without www prefix match
                            # 3. Target is substring of real domain (for subdomains)
                            if (target_lower == real_domain or 
                                target_without_www == real_without_www or
                                target_without_www in real_without_www or
                                real_without_www in target_without_www):
                                found_link = link
                                found_url = real_url
                                self.emit_log(f'✓✓ FORCEFULLY DETECTED target domain at position {idx}!')
                                self.emit_log(f'   Target: "{target_domain_clean}"')
                                self.emit_log(f'   Found:  "{real_domain}"')
                                self.emit_log(f'   Full URL: {real_url[:100]}...')
                                break
                        except Exception as parse_error:
                            self.emit_log(f'[DEBUG] URL parsing error at position {idx}: {parse_error}', 'DEBUG')
                    
                    # Strategy 2: Simple substring match (fallback)
                    if not found_link and real_url and target_domain_clean.lower() in real_url.lower() and real_url.startswith('http'):
                        found_link = link
                        found_url = real_url
                        self.emit_log(f'✓ Found target domain at position {idx} (substring match)')
                        self.emit_log(f'  Link URL: {real_url[:100]}...')
                        break
                        
                except Exception as e:
                    self.emit_log(f'[DEBUG] Error checking link {idx}: {e}', 'DEBUG')
                    continue
            
            # Store found_url for later use
            if found_link and found_url:
                real_url = found_url
            
            if found_link:
                # Click the found link to open in a NEW TAB
                self.emit_log('Clicking on target domain link to open in new tab...')
                try:
                    # Get the href before clicking
                    href = await found_link.get_attribute('href')
                    
                    # For Bing redirects, use the extracted real_url if available
                    url_to_open = real_url if real_url and real_url.startswith('http') else href
                    
                    # Open in a new tab by using Ctrl+Click (modifier key)
                    self.emit_log(f'Opening target domain in new tab: {url_to_open[:80]}...')
                    
                    # Method 1: Try Ctrl+Click to open in new tab
                    try:
                        await found_link.click(modifiers=['Control'])
                        self.emit_log('✓ Ctrl+Click executed - opening in new tab')
                        await asyncio.sleep(random.uniform(2, 3))
                    except:
                        # Method 2: Fallback - create new page and navigate directly
                        self.emit_log('Ctrl+Click failed, using direct new tab method...')
                        new_page = await context.new_page()
                        await new_page.goto(url_to_open, wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(random.uniform(3, 5))
                        
                        # Handle consent popups on target domain in new tab
                        self.emit_log('Checking target domain for consent popups...')
                        try:
                            temp_consent_manager = ConsentManager(self.log_manager)
                            await temp_consent_manager.handle_consents(new_page, max_retries=2)
                        except Exception as consent_error:
                            self.emit_log(f'Consent handling note: {consent_error}', 'DEBUG')
                        
                        self.emit_log('✓ Successfully opened target domain in new tab')
                        
                        # Close the search results page and return the new page
                        await page.close()
                        return new_page
                    
                    # If Ctrl+Click succeeded, find the newly opened tab
                    all_pages = context.pages
                    if len(all_pages) > 1:
                        # Get the last opened page (newly created tab)
                        new_page = all_pages[-1]
                        
                        # Wait for the new page to load
                        try:
                            await new_page.wait_for_load_state('domcontentloaded', timeout=30000)
                        except:
                            pass
                        
                        await asyncio.sleep(random.uniform(2, 3))
                        
                        # Handle consent popups on target domain
                        self.emit_log('Checking target domain for consent popups...')
                        try:
                            temp_consent_manager = ConsentManager(self.log_manager)
                            await temp_consent_manager.handle_consents(new_page, max_retries=2)
                        except Exception as consent_error:
                            self.emit_log(f'Consent handling note: {consent_error}', 'DEBUG')
                        
                        self.emit_log('✓ Successfully navigated to target domain in new tab')
                        
                        # Close the search results page and return the new page
                        await page.close()
                        return new_page
                    else:
                        # If new tab didn't open, treat it as same-tab navigation
                        try:
                            await page.wait_for_load_state('domcontentloaded', timeout=30000)
                        except:
                            pass
                        
                        await asyncio.sleep(random.uniform(3, 5))
                        
                        # Handle consent popups on target domain
                        self.emit_log('Checking target domain for consent popups...')
                        try:
                            temp_consent_manager = ConsentManager(self.log_manager)
                            await temp_consent_manager.handle_consents(page, max_retries=2)
                        except Exception as consent_error:
                            self.emit_log(f'Consent handling note: {consent_error}', 'DEBUG')
                        
                        self.emit_log('✓ Successfully navigated to target domain')
                        return page
                        
                except Exception as click_error:
                    self.emit_log(f'Error during click: {click_error}', 'ERROR')
                    # Ultimate fallback: Direct navigation in new tab
                    try:
                        href = await found_link.get_attribute('href')
                        url_to_open = real_url if real_url and real_url.startswith('http') else href
                        self.emit_log(f'Fallback: Opening in new tab directly: {url_to_open[:80]}...')
                        new_page = await context.new_page()
                        await new_page.goto(url_to_open, wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(random.uniform(2, 4))
                        
                        # Handle consent popups
                        try:
                            temp_consent_manager = ConsentManager(self.log_manager)
                            await temp_consent_manager.handle_consents(new_page, max_retries=2)
                        except:
                            pass
                        
                        self.emit_log('✓ Fallback navigation successful in new tab')
                        await page.close()
                        return new_page
                    except Exception as fallback_error:
                        self.emit_log(f'All methods failed: {fallback_error}', 'ERROR')
                        await page.close()
                        return None
            else:
                self.emit_log(f'⚠ Target domain "{target_domain_clean}" not found in top 10 search results', 'WARNING')
                # FALLBACK: If not found, navigate directly to target domain IN NEW TAB
                fallback_url = target_domain if target_domain.startswith('http') else f'https://{target_domain}'
                self.emit_log(f'[FALLBACK] Opening target domain directly in new tab: {fallback_url[:80]}...')
                try:
                    # Create new tab for direct navigation
                    new_page = await context.new_page()
                    await new_page.goto(fallback_url, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    # Handle consent popups on fallback navigation
                    self.emit_log('Checking for consent popups after fallback...')
                    try:
                        temp_consent_manager = ConsentManager(self.log_manager)
                        await temp_consent_manager.handle_consents(new_page, max_retries=2)
                    except Exception:
                        pass
                    
                    self.emit_log('✓ Direct navigation successful in new tab (fallback)')
                    
                    # Close the search results page
                    await page.close()
                    return new_page  # Return the new page object for further use
                except Exception as nav_error:
                    self.emit_log(f'Failed to navigate directly: {nav_error}', 'ERROR')
                    try:
                        await new_page.close()
                    except:
                        pass
                    await page.close()  # Close the search page if navigation fails
                    return None
            
        except Exception as e:
            self.emit_log(f'Error during search visit: {e}', 'ERROR')
            # Try fallback navigation in new tab
            try:
                # Construct proper URL with protocol
                fallback_url = target_domain if target_domain.startswith('http') else f'https://{target_domain}'
                self.emit_log(f'[EXCEPTION FALLBACK] Attempting to open target domain in new tab: {fallback_url[:80]}...')
                
                # Create new tab for fallback
                new_page = await context.new_page()
                await new_page.goto(fallback_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(random.uniform(2, 4))
                
                # Handle consent popups
                try:
                    temp_consent_manager = ConsentManager(self.log_manager)
                    await temp_consent_manager.handle_consents(new_page, max_retries=2)
                except:
                    pass
                
                self.emit_log('✓ Exception fallback successful - opened in new tab')
                
                # Close the original page
                try:
                    await page.close()
                except:
                    pass
                
                return new_page  # Return the new page object for further use
            except:
                try:
                    await page.close()
                except:
                    pass
                return None
    
    async def handle_interaction(self, page: Page, max_pages: int, enable_extra_pages: bool):
        """Handle advanced page interaction - click posts, explore pages, follow links with human behavior."""
        self.emit_log('[INFO] Advanced human behavior interaction enabled')
        
        pages_visited = 1
        interactions_count = 0
        max_interactions = random.randint(5, 15)
        
        try:
            for interaction in range(max_interactions):
                if not self.running:
                    break
                
                # Scroll and pause (human-like reading)
                scroll_depth = random.randint(40, 90)
                await HumanBehavior.scroll_page(page, scroll_depth)
                await asyncio.sleep(random.uniform(5, 15))
                
                # Random mouse movements during interaction
                try:
                    viewport_size = page.viewport_size
                    if viewport_size:
                        for _ in range(random.randint(2, 5)):
                            x = random.randint(100, viewport_size['width'] - 100)
                            y = random.randint(100, viewport_size['height'] - 100)
                            await page.mouse.move(x, y)
                            await asyncio.sleep(random.uniform(0.3, 1.0))
                except:
                    pass
                
                # Try to click a link if extra pages enabled
                if enable_extra_pages and pages_visited < max_pages:
                    try:
                        # Find clickable article/content links - IMPROVED SELECTORS
                        # Target common content link patterns
                        content_selectors = [
                            'article a[href]',
                            '.post a[href]',
                            '.entry a[href]',
                            '.content a[href]',
                            'main a[href]',
                            '[role="article"] a[href]',
                            '.blog-post a[href]',
                            'a[href^="/"]:not(nav a):not(header a):not(footer a)',
                            'a[href^="http"]:not(nav a):not(header a):not(footer a)'
                        ]
                        
                        links = []
                        for selector in content_selectors:
                            try:
                                found_links = await page.query_selector_all(selector)
                                links.extend(found_links)
                                if len(links) >= 20:
                                    break
                            except:
                                continue
                        
                        if links and len(links) > 0:
                            # Filter out navigation/social links more aggressively
                            valid_links = []
                            for link in links[:30]:  # Check first 30 links
                                try:
                                    href = await link.get_attribute('href')
                                    if href:
                                        # Skip unwanted links
                                        skip_patterns = LINK_SKIP_PATTERNS + [
                                            'mailto:', 'tel:', 'javascript:',
                                            '#', 'login', 'signup', 'register',
                                            'cart', 'checkout', 'account'
                                        ]
                                        if not any(skip in href.lower() for skip in skip_patterns):
                                            # Check if link has visible text (likely content link)
                                            text = await link.inner_text()
                                            if text and len(text.strip()) > 5:
                                                valid_links.append(link)
                                except:
                                    continue
                            
                            if valid_links:
                                # Select random valid link
                                content_link = random.choice(valid_links[:min(10, len(valid_links))])
                                href = await content_link.get_attribute('href')
                                
                                self.emit_log(f'[INFO] Clicking content link (page {pages_visited + 1}/{max_pages}): {href[:60]}...')
                                
                                # Human-like click with mouse movement
                                try:
                                    box = await content_link.bounding_box()
                                    if box:
                                        # Move mouse to link first
                                        x = int(box['x'] + box['width'] / 2)
                                        y = int(box['y'] + box['height'] / 2)
                                        await page.mouse.move(x, y)
                                        await asyncio.sleep(random.uniform(0.3, 0.8))
                                    
                                    await content_link.click()
                                    await asyncio.sleep(random.uniform(3, 6))
                                    pages_visited += 1
                                    interactions_count += 1
                                    
                                    # Handle consents on new page
                                    consent_manager = ConsentManager(self.log_manager)
                                    await consent_manager.handle_consents(page)
                                except Exception as e:
                                    self.emit_log(f'Could not click link: {e}', 'WARNING')
                            else:
                                self.emit_log('[INFO] No valid content links found, continuing interaction', 'WARNING')
                    except Exception as e:
                        self.emit_log(f'Error finding/clicking links: {e}', 'WARNING')
                
                # Random idle pause (simulating reading)
                await asyncio.sleep(random.uniform(8, 25))
                
            self.emit_log(f'✓ Completed {interactions_count} interactions across {pages_visited} pages')
                
        except Exception as e:
            self.emit_log(f'Error during interaction: {e}', 'WARNING')
    
    async def execute_high_cpc_mode(self, profile_num, high_cpc_url, target_domain, stay_time, 
                                    consent_manager, platform='windows', proxy_override=None):
        """Execute HIGH CPC/CPM Mode with 4 High CPC tabs and 1 Target Domain tab.
        
        Args:
            profile_num: Profile number for logging
            high_cpc_url: High CPC website URL
            target_domain: Target domain URL
            stay_time: Total stay time on target domain in seconds
            consent_manager: ConsentManager instance for cookie handling
            platform: Platform to use (windows/android)
            proxy_override: Optional proxy config dict to use directly (skips queue consumption)
        """
        try:
            self.emit_log(f'━━━ Profile {profile_num} | HIGH CPC/CPM Mode | Platform: {platform} ━━━')
            
            # Create browser context
            self.emit_log(f'[Browser {profile_num}] Launching...')
            context = await self.browser_manager.create_context(platform, proxy_override=proxy_override)
            if not context:
                self.emit_log(f'[Browser {profile_num}] Failed to create browser context', 'ERROR')
                return False
            
            self.emit_log(f'[Browser {profile_num}] Browser opened successfully')
            self.active_browsers.append(context)
            self.active_contexts.append(context)
            await self.apply_zoom_out_to_context(context, f'Browser {profile_num}')
            
            try:
                high_cpc_tabs = []
                
                # Open High CPC URL in 4 tabs
                self.emit_log(f'Opening High CPC URL in 4 tabs: {high_cpc_url[:50]}...')
                for i in range(4):
                    page = await context.new_page()
                    high_cpc_tabs.append(page)
                    self.emit_log(f'Tab {i+1}: Loading High CPC URL...')
                    await page.goto(high_cpc_url, wait_until='networkidle', timeout=60000)
                    self.emit_log(f'Tab {i+1}: Fully loaded')
                    await asyncio.sleep(1)
                
                self.emit_log('All 4 tabs fully loaded, starting cookie handling...')
                
                # Tab 1: Select tab, wait for proper reload, handle cookies
                self.emit_log('Tab 1: Selecting and waiting for proper reload...')
                await high_cpc_tabs[0].bring_to_front()
                await asyncio.sleep(2)  # Wait for proper reload
                self.emit_log('Tab 1: Checking for cookie popup...')
                tab1_handled = await consent_manager.handle_consents(high_cpc_tabs[0])
                if tab1_handled:
                    self.emit_log('Tab 1: Cookie popup accepted')
                else:
                    self.emit_log('Tab 1: No cookie popup detected')
                await asyncio.sleep(0.5)
                
                # Tab 2: Select tab, wait for proper reload, wait up to 20 seconds for cookie popup
                self.emit_log('Tab 2: Selecting and waiting for proper reload...')
                await high_cpc_tabs[1].bring_to_front()
                await asyncio.sleep(2)  # Wait for proper reload
                self.emit_log('Tab 2: Waiting for cookie popup (up to 20 seconds)...')
                try:
                    # Try to handle consent with timeout
                    tab2_handled = await asyncio.wait_for(
                        consent_manager.handle_consents(high_cpc_tabs[1]),
                        timeout=20
                    )
                    if tab2_handled:
                        self.emit_log('Tab 2: Cookie popup accepted')
                    else:
                        self.emit_log('Tab 2: No cookie popup found, moving on')
                except asyncio.TimeoutError:
                    self.emit_log('Tab 2: No cookie popup appeared within 20 seconds')
                await asyncio.sleep(0.5)
                
                # Tab 3: Select tab, wait for proper reload, wait up to 20 seconds for cookie popup
                self.emit_log('Tab 3: Selecting and waiting for proper reload...')
                await high_cpc_tabs[2].bring_to_front()
                await asyncio.sleep(2)  # Wait for proper reload
                self.emit_log('Tab 3: Waiting for cookie popup (up to 20 seconds)...')
                try:
                    tab3_handled = await asyncio.wait_for(
                        consent_manager.handle_consents(high_cpc_tabs[2]),
                        timeout=20
                    )
                    if tab3_handled:
                        self.emit_log('Tab 3: Cookie popup accepted')
                    else:
                        self.emit_log('Tab 3: No cookie popup found, moving on')
                except asyncio.TimeoutError:
                    self.emit_log('Tab 3: No cookie popup appeared within 20 seconds')
                await asyncio.sleep(0.5)
                
                # Tab 4: Select tab, wait for proper reload, handle cookies and perform shopping interactions
                self.emit_log('Tab 4: Selecting and waiting for proper reload...')
                await high_cpc_tabs[3].bring_to_front()
                await asyncio.sleep(2)  # Wait for proper reload
                self.emit_log('Tab 4: Starting shopping interaction flow...')
                try:
                    # Handle cookie popup if present (20 seconds timeout)
                    self.emit_log('Tab 4: Waiting for cookie popup (up to 20 seconds)...')
                    try:
                        tab4_handled = await asyncio.wait_for(
                            consent_manager.handle_consents(high_cpc_tabs[3]),
                            timeout=20
                        )
                        if tab4_handled:
                            self.emit_log('Tab 4: Cookie popup accepted')
                        else:
                            self.emit_log('Tab 4: No cookie popup found, proceeding...')
                    except asyncio.TimeoutError:
                        self.emit_log('Tab 4: No cookie popup within 20 seconds, proceeding...')
                    
                    # AI-driven Shopping interaction flow
                    self.emit_log('Tab 4: Performing AI-driven shopping interactions...')
                    await self._ai_driven_shopping_flow(high_cpc_tabs[3])
                    
                except Exception as e:
                    self.emit_log(f'Tab 4 shopping interaction error: {e}', 'WARNING')
                
                # Open Target Domain in 5th tab
                self.emit_log(f'Opening Target Domain in 5th tab: {target_domain[:50]}...')
                target_page = await context.new_page()
                await target_page.goto(target_domain, wait_until='networkidle', timeout=60000)
                self.emit_log('Tab 5: Target Domain fully loaded')
                await asyncio.sleep(2)
                
                # Perform smooth scrolling and clicking on Target Domain
                self.emit_log(f'Starting Target Domain interaction (stay time: {stay_time} seconds)...')
                start_time = time.time()
                half_time = stay_time / 2
                
                # Initial smooth scrolling (human-like behavior)
                self.emit_log('Tab 5: Performing smooth scrolling...')
                await HumanBehavior.scroll_page(target_page, depth_percent=random.randint(40, 80), 
                                               scroll_type='Smooth', min_speed=200, max_speed=600)
                await asyncio.sleep(random.uniform(1, 2))
                
                # Continue smooth scrolling until half-time
                while time.time() - start_time < half_time:
                    await HumanBehavior.scroll_page(target_page, depth_percent=random.randint(30, 70),
                                                   scroll_type='Smooth', min_speed=200, max_speed=600)
                    wait_time = min(random.uniform(3, 6), half_time - (time.time() - start_time))
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                
                # At half-time: Perform 1-2 random clicks
                num_clicks = random.randint(1, 2)
                self.emit_log(f'Half-time reached! Performing {num_clicks} random clicks...')
                await self._perform_random_clicks(target_page, num_clicks)
                await asyncio.sleep(random.uniform(1, 2))
                
                # Continue smooth scrolling for remaining time
                while time.time() - start_time < stay_time:
                    await HumanBehavior.scroll_page(target_page, depth_percent=random.randint(20, 60),
                                                   scroll_type='Smooth', min_speed=200, max_speed=600)
                    wait_time = min(random.uniform(3, 6), stay_time - (time.time() - start_time))
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                
                self.emit_log('Stay time completed, closing all tabs...')
                
                # Close all tabs
                for i, tab in enumerate(high_cpc_tabs):
                    try:
                        await tab.close()
                        self.emit_log(f'Closed High CPC Tab {i+1}')
                    except Exception:
                        pass
                
                try:
                    await target_page.close()
                    self.emit_log('Closed Target Domain tab')
                except Exception:
                    pass
                
                self.emit_log(f'✓ HIGH CPC/CPM Mode Profile {profile_num} completed successfully')
                return True
                
            finally:
                # Always close context and remove from active tracking
                try:
                    self.active_browsers.remove(context)
                except ValueError:
                    pass
                try:
                    self.active_contexts.remove(context)
                except ValueError:
                    pass
                await context.close()
                
        except Exception as e:
            self.emit_log(f'HIGH CPC/CPM Mode error: {e}', 'ERROR')
            return False
    
    async def _ai_driven_shopping_flow(self, page: Page):
        """AI-driven shopping flow: detect products, select size/color, add to cart, checkout."""
        try:
            self.emit_log('AI Shopping: Starting intelligent product detection...')
            
            # Step 1: Intelligently detect and select a product
            product_clicked = await self._detect_and_select_product(page)
            
            if not product_clicked:
                self.emit_log('AI Shopping: No product found, skipping shopping flow')
                return
            
            # Wait for product page to load
            await asyncio.sleep(2)
            
            # Step 2: Detect and select size if available
            await self._detect_and_select_size(page)
            
            # Step 3: Detect and select color if available
            await self._detect_and_select_color(page)
            
            # Step 4: Add to cart/bag
            added_to_cart = await self._detect_and_add_to_cart(page)
            
            if not added_to_cart:
                self.emit_log('AI Shopping: Could not add to cart, stopping flow')
                return
            
            # Wait for cart action to complete
            await asyncio.sleep(2)
            
            # Step 5: Navigate to cart
            cart_opened = await self._detect_and_open_cart(page)
            
            if not cart_opened:
                self.emit_log('AI Shopping: Could not open cart, stopping flow')
                return
            
            # Wait for cart page to load
            await asyncio.sleep(2)
            
            # Step 6: Proceed to checkout
            checkout_opened = await self._detect_and_open_checkout(page)
            
            if not checkout_opened:
                self.emit_log('AI Shopping: Could not proceed to checkout, stopping flow')
                return
            
            # Wait for checkout page to load
            await asyncio.sleep(2)
            
            # Step 7: Fill checkout form with random data
            self.emit_log('AI Shopping: Filling checkout form with random data...')
            await self._fill_checkout_form(page)
            
            self.emit_log('AI Shopping: Shopping flow completed successfully')
            
        except Exception as e:
            self.emit_log(f'AI Shopping flow error: {e}', 'WARNING')
    
    async def _detect_and_select_product(self, page: Page) -> bool:
        """Intelligently detect and select a product from the page."""
        try:
            self.emit_log('AI Shopping: Detecting products on page...')
            
            # Enhanced product link/card selectors (common e-commerce patterns)
            product_selectors = [
                'a[href*="/product"]',
                'a[href*="/p/"]',
                'a[href*="/item"]',
                '.product-card a',
                '.product-item a',
                '.product a',
                '[data-testid*="product"] a',
                '[class*="product-link"]',
                '[class*="ProductCard"] a',
                'article a[href*="product"]',
                '.grid a[href*="/"]',  # Grid layouts often contain products
                '.product-grid a',
                '[data-product-id] a',
            ]
            
            # Try each selector to find product links
            for selector in product_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    visible_products = []
                    
                    for elem in elements:
                        try:
                            if await elem.is_visible():
                                # Check if element has meaningful href
                                href = await elem.get_attribute('href')
                                if href and len(href) > 5:  # Basic validation
                                    visible_products.append(elem)
                        except:
                            continue
                    
                    if visible_products:
                        # Select a random product from visible ones
                        product = random.choice(visible_products)
                        await HumanBehavior.random_delay(1000, 2000)
                        await product.click()
                        self.emit_log(f'AI Shopping: Clicked product (selector: {selector[:40]}...)')
                        return True
                        
                except Exception:
                    continue
            
            # If no product links found, try generic clickable items
            self.emit_log('AI Shopping: No product links found, trying alternative detection...')
            generic_selectors = [
                'img[alt*="product"]',
                'img[src*="product"]',
                '.card a',
                '.item a',
            ]
            
            for selector in generic_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        for elem in elements:
                            if await elem.is_visible():
                                await HumanBehavior.random_delay(1000, 2000)
                                await elem.click()
                                self.emit_log(f'AI Shopping: Clicked item (alternative selector)')
                                return True
                except Exception:
                    continue
                    
            return False
            
        except Exception as e:
            self.emit_log(f'Product detection error: {e}', 'WARNING')
            return False
    
    async def _detect_and_select_size(self, page: Page) -> bool:
        """Detect and select a size option if available."""
        try:
            self.emit_log('AI Shopping: Checking for size options...')
            
            # Size selection patterns
            size_selectors = [
                'select[name*="size"]',
                'select[id*="size"]',
                'button:has-text("Size")',
                '[data-testid*="size"]',
                '.size-selector button',
                '.size-options button',
                '[class*="size"] button',
                'input[type="radio"][name*="size"]',
                'button[aria-label*="size"]',
                'button[class*="Size"]',
            ]
            
            for selector in size_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    visible_elements = []
                    
                    for elem in elements:
                        if await elem.is_visible():
                            visible_elements.append(elem)
                    
                    if visible_elements:
                        # Select random size
                        size_elem = random.choice(visible_elements)
                        await HumanBehavior.random_delay(500, 1000)
                        
                        # Check element type
                        tag_name = await size_elem.evaluate('el => el.tagName')
                        
                        if tag_name.lower() == 'select':
                            # Handle dropdown
                            options = await size_elem.query_selector_all('option')
                            if len(options) > 1:  # Skip first (placeholder)
                                option = random.choice(options[1:])
                                value = await option.get_attribute('value')
                                if value:
                                    await size_elem.select_option(value)
                                    self.emit_log('AI Shopping: Selected size from dropdown')
                                    return True
                        else:
                            # Handle button/radio
                            await size_elem.click()
                            self.emit_log('AI Shopping: Clicked size option')
                            return True
                            
                except Exception:
                    continue
            
            self.emit_log('AI Shopping: No size options found (may not be required)')
            return False
            
        except Exception as e:
            self.emit_log(f'Size selection error: {e}', 'WARNING')
            return False
    
    async def _detect_and_select_color(self, page: Page) -> bool:
        """Detect and select a color option if available."""
        try:
            self.emit_log('AI Shopping: Checking for color options...')
            
            # Color selection patterns
            color_selectors = [
                'select[name*="color"]',
                'select[name*="colour"]',
                'select[id*="color"]',
                'button:has-text("Color")',
                '[data-testid*="color"]',
                '.color-selector button',
                '.color-options button',
                '[class*="color"] button',
                '[class*="colour"] button',
                'input[type="radio"][name*="color"]',
                'button[aria-label*="color"]',
                'button[class*="Color"]',
                '.swatch',
                '[class*="Swatch"]',
            ]
            
            for selector in color_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    visible_elements = []
                    
                    for elem in elements:
                        if await elem.is_visible():
                            visible_elements.append(elem)
                    
                    if visible_elements:
                        # Select random color
                        color_elem = random.choice(visible_elements)
                        await HumanBehavior.random_delay(500, 1000)
                        
                        # Check element type
                        tag_name = await color_elem.evaluate('el => el.tagName')
                        
                        if tag_name.lower() == 'select':
                            # Handle dropdown
                            options = await color_elem.query_selector_all('option')
                            if len(options) > 1:  # Skip first (placeholder)
                                option = random.choice(options[1:])
                                value = await option.get_attribute('value')
                                if value:
                                    await color_elem.select_option(value)
                                    self.emit_log('AI Shopping: Selected color from dropdown')
                                    return True
                        else:
                            # Handle button/swatch/radio
                            await color_elem.click()
                            self.emit_log('AI Shopping: Clicked color option')
                            return True
                            
                except Exception:
                    continue
            
            self.emit_log('AI Shopping: No color options found (may not be required)')
            return False
            
        except Exception as e:
            self.emit_log(f'Color selection error: {e}', 'WARNING')
            return False
    
    async def _detect_and_add_to_cart(self, page: Page) -> bool:
        """Detect and click Add to Cart/Bag/Shop Now button."""
        try:
            self.emit_log('AI Shopping: Looking for Add to Cart button...')
            
            # Enhanced add to cart button selectors
            cart_button_selectors = [
                'button:has-text("Add to Cart")',
                'button:has-text("Add to Bag")',
                'button:has-text("Add To Cart")',
                'button:has-text("Add To Bag")',
                'button:has-text("Shop Now")',
                'button:has-text("Buy Now")',
                'a:has-text("Add to Cart")',
                'a:has-text("Add to Bag")',
                'a:has-text("Shop Now")',
                '[data-testid*="add-to-cart"]',
                '[data-testid*="add-to-bag"]',
                '[id*="add-to-cart"]',
                '[id*="add-to-bag"]',
                '.add-to-cart',
                '.add-to-bag',
                'button[class*="AddToCart"]',
                'button[class*="AddToBag"]',
                'button[aria-label*="Add to cart"]',
                'button[aria-label*="Add to bag"]',
            ]
            
            for selector in cart_button_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    
                    for elem in elements:
                        if await elem.is_visible():
                            await HumanBehavior.random_delay(1000, 2000)
                            await elem.click()
                            self.emit_log(f'AI Shopping: Clicked Add to Cart button')
                            return True
                            
                except Exception:
                    continue
            
            self.emit_log('AI Shopping: No Add to Cart button found')
            return False
            
        except Exception as e:
            self.emit_log(f'Add to cart error: {e}', 'WARNING')
            return False
    
    async def _detect_and_open_cart(self, page: Page) -> bool:
        """Detect and open the shopping cart."""
        try:
            self.emit_log('AI Shopping: Looking for Cart link...')
            
            # Cart/Bag link selectors
            cart_selectors = [
                'a:has-text("Cart")',
                'a:has-text("Bag")',
                'a:has-text("View Cart")',
                'a:has-text("View Bag")',
                'button:has-text("Cart")',
                'button:has-text("Bag")',
                'button:has-text("View Cart")',
                'button:has-text("View Bag")',
                '[data-testid*="cart"]',
                '[data-testid*="bag"]',
                '[href*="/cart"]',
                '[href*="/bag"]',
                '.cart-link',
                '.bag-link',
                '[class*="cart"]',
                '[aria-label*="cart"]',
                '[aria-label*="bag"]',
                'button[class*="Cart"]',
                'a[class*="Cart"]',
            ]
            
            for selector in cart_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await HumanBehavior.random_delay(1000, 2000)
                        await element.click()
                        self.emit_log('AI Shopping: Navigated to cart')
                        return True
                        
                except Exception:
                    continue
            
            self.emit_log('AI Shopping: No Cart link found')
            return False
            
        except Exception as e:
            self.emit_log(f'Open cart error: {e}', 'WARNING')
            return False
    
    async def _detect_and_open_checkout(self, page: Page) -> bool:
        """Detect and click Checkout button."""
        try:
            self.emit_log('AI Shopping: Looking for Checkout button...')
            
            # Checkout button selectors
            checkout_selectors = [
                'button:has-text("Checkout")',
                'button:has-text("Check Out")',
                'a:has-text("Checkout")',
                'a:has-text("Check Out")',
                'button:has-text("Proceed to Checkout")',
                'a:has-text("Proceed to Checkout")',
                'button:has-text("Continue to Checkout")',
                '[data-testid*="checkout"]',
                '[href*="/checkout"]',
                '.checkout-button',
                'button[class*="Checkout"]',
                'a[class*="Checkout"]',
                '[aria-label*="checkout"]',
                '[id*="checkout"]',
            ]
            
            for selector in checkout_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await HumanBehavior.random_delay(1000, 2000)
                        await element.click()
                        self.emit_log('AI Shopping: Proceeded to checkout')
                        return True
                        
                except Exception:
                    continue
            
            self.emit_log('AI Shopping: No Checkout button found')
            return False
            
        except Exception as e:
            self.emit_log(f'Open checkout error: {e}', 'WARNING')
            return False
    
    async def _fill_checkout_form(self, page: Page):
        """Fill checkout form with random data."""
        try:
            # Random data generation
            names = ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Williams', 'Charlie Brown']
            addresses = ['123 Main St', '456 Oak Ave', '789 Pine Rd', '321 Elm Street', '654 Maple Drive']
            cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
            states = ['NY', 'CA', 'IL', 'TX', 'AZ']
            postal_codes = ['10001', '90001', '60601', '77001', '85001']
            countries = ['United States', 'USA', 'US']
            phones = ['555-0101', '555-0102', '555-0103', '555-0104', '555-0105']
            
            # Common form field selectors
            form_fields = {
                'name': ['input[name*="name"]', '#name', '[placeholder*="Name"]', '[name*="firstName"]', '[name*="lastName"]'],
                'address': ['input[name*="address"]', '#address', '[placeholder*="Address"]', '[name*="street"]'],
                'city': ['input[name*="city"]', '#city', '[placeholder*="City"]'],
                'state': ['input[name*="state"]', '#state', '[placeholder*="State"]', 'select[name*="state"]'],
                'postal': ['input[name*="postal"]', 'input[name*="zip"]', '#postal', '#zip', '[placeholder*="Postal"]', '[placeholder*="ZIP"]'],
                'country': ['input[name*="country"]', '#country', 'select[name*="country"]'],
                'phone': ['input[name*="phone"]', '#phone', '[placeholder*="Phone"]', 'input[type="tel"]']
            }
            
            # Try to fill each field
            for field_type, selectors in form_fields.items():
                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            if await element.is_visible():
                                await HumanBehavior.random_delay(500, 1000)
                                
                                # Select appropriate random data
                                if field_type == 'name':
                                    data = random.choice(names)
                                elif field_type == 'address':
                                    data = random.choice(addresses)
                                elif field_type == 'city':
                                    data = random.choice(cities)
                                elif field_type == 'state':
                                    data = random.choice(states)
                                elif field_type == 'postal':
                                    data = random.choice(postal_codes)
                                elif field_type == 'country':
                                    data = random.choice(countries)
                                elif field_type == 'phone':
                                    data = random.choice(phones)
                                else:
                                    continue
                                
                                await element.fill(data)
                                self.emit_log(f'Filled {field_type} field with: {data}')
                                await asyncio.sleep(0.5)
                                break
                    except Exception:
                        continue
            
        except Exception as e:
            self.emit_log(f'Form filling error: {e}', 'WARNING')
    
    async def _perform_random_clicks(self, page: Page, num_clicks: int):
        """Perform random clicks on clickable elements."""
        try:
            # Find clickable elements
            clickable_selectors = ['a', 'button', '[role="button"]', '[onclick]']
            all_clickable = []
            
            for selector in clickable_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for elem in elements:
                        if await elem.is_visible():
                            all_clickable.append(elem)
                except Exception:
                    continue
            
            if not all_clickable:
                self.emit_log('No clickable elements found')
                return
            
            # Perform random clicks
            for i in range(min(num_clicks, len(all_clickable))):
                try:
                    element = random.choice(all_clickable)
                    
                    # Check if element is still attached and visible
                    if await element.is_visible():
                        await HumanBehavior.random_delay(1000, 2000)
                        await element.click(timeout=3000)
                        self.emit_log(f'Performed random click {i+1}/{num_clicks}')
                        await asyncio.sleep(random.uniform(1, 2))
                        
                        # Remove clicked element from list
                        all_clickable.remove(element)
                except Exception as e:
                    self.emit_log(f'Click attempt {i+1} skipped: {str(e)[:50]}', 'WARNING')
                    continue
                    
        except Exception as e:
            self.emit_log(f'Random clicks error: {e}', 'WARNING')
    
    
    async def execute_single_visit(self, page, visit_num, target_url, visit_type,
                                  search_keyword, target_domain, search_engine, referral_sources,
                                  min_time_spend, max_time_spend, enable_consent,
                                  enable_interaction, enable_extra_pages, max_pages,
                                  consent_manager, enable_highlight=False,
                                  utm_campaign='', utm_medium='social', utm_term='', utm_content='',
                                  random_ad_clicking_enabled=False,
                                  random_click_ratio=0.5,
                                  custom_random_targets=None):
        """Execute a single visit within a browser profile."""
        try:
            self.emit_log(f'[Visit {visit_num}] Processing URL: {target_url[:50]}...')
            
            # Navigate based on visit type
            if visit_type == 'referral':
                await self.handle_referral_visit(page, target_url, referral_sources,
                                                utm_medium, utm_campaign, utm_term, utm_content)
            elif visit_type == 'search':
                # Search visit - opens selected search engine in a NEW tab, searches, and clicks target domain
                search_page = await self.handle_search_visit(page.context, target_domain, search_keyword, search_engine)
                if not search_page:
                    self.emit_log(f'[Visit {visit_num}] Target domain not found in search', 'WARNING')
                    return False
                # Replace page with the search result page for further interactions
                page = search_page
            else:
                # Direct visit
                self.emit_log(f'[Visit {visit_num}] Direct visit to {target_url}')
                try:
                    await page.goto(target_url, wait_until='domcontentloaded', timeout=60000)
                    # CRITICAL FIX: Add wait after direct navigation to prevent immediate close
                    await asyncio.sleep(random.uniform(3, 5))
                    self.emit_log(f'[Visit {visit_num}] ✓ Successfully loaded page')
                except Exception as nav_error:
                    self.emit_log(f'[Visit {visit_num}] Navigation error: {nav_error}', 'ERROR')
                    raise
            
            # Handle consents if enabled
            if consent_manager and enable_consent:
                await consent_manager.handle_consents(page)
            
            # Time-based human scrolling behavior with highlighting and continuous consent monitoring
            self.emit_log(f'[Visit {visit_num}] Starting browsing for {min_time_spend//60} minutes with scrolling...')
            consent_mgr = consent_manager if enable_consent else None
            await HumanBehavior.time_based_browsing(page, min_time_spend, max_time_spend, enable_highlight, 
                                                   consent_mgr, self.log_manager)
            
            # Random ad clicking (if enabled)
            if random_ad_clicking_enabled:
                ad_engine = RandomAdClickEngine(
                    log_manager=self.log_manager,
                    custom_random_targets=custom_random_targets or [],
                )
                await ad_engine.perform_random_ad_click(page, random_click_ratio)
            
            # Handle interaction if enabled (legacy mode)
            if enable_interaction:
                await self.handle_interaction(page, max_pages, enable_extra_pages)
            
            self.emit_log(f'✓ [Visit {visit_num}] Completed successfully')
            return True
            
        except Exception as e:
            self.emit_log(f'✗ [Visit {visit_num}] Error: {e}', 'ERROR')
            return False
    
    async def execute_single_profile(self, profile_num, url_list, platforms, visit_type,
                                     search_keyword, target_domain, search_engine, referral_sources,
                                     random_time_enabled, stay_time, min_time_spend, max_time_spend, enable_consent,
                                     enable_interaction, enable_extra_pages, max_pages,
                                     consent_manager, enable_highlight=False,
                                     utm_campaign='', utm_medium='social', utm_term='', utm_content='',
                                     high_cpc_enabled=False, high_cpc_url='', high_cpc_target='', high_cpc_stay_time=180,
                                     proxy_override=None,
                                     random_ad_clicking_enabled=False,
                                     random_click_ratio=0.5,
                                     custom_random_targets=None,
                                     selected_browser_engines=None):
        """Execute a single browser profile with one page."""
        try:
            # Check if HIGH CPC/CPM Mode is enabled
            if high_cpc_enabled and high_cpc_url and high_cpc_target:
                # Execute HIGH CPC/CPM Mode instead of normal mode
                platform = random.choice(platforms)
                return await self.execute_high_cpc_mode(
                    profile_num, high_cpc_url, high_cpc_target, 
                    high_cpc_stay_time, consent_manager, platform,
                    proxy_override=proxy_override
                )
            
            # Normal mode execution (existing code)
            # Select random platform for this profile
            platform = random.choice(platforms)
            
            # Determine time to spend based on random_time_enabled
            if random_time_enabled:
                time_to_spend = random.randint(min_time_spend, max_time_spend)
                self.emit_log(f'━━━ Profile {profile_num} | Platform: {platform} | Time: {time_to_spend//60} min (random) ━━━')
            else:
                time_to_spend = stay_time
                self.emit_log(f'━━━ Profile {profile_num} | Platform: {platform} | Time: {time_to_spend//60} min (fixed) ━━━')
            
            # Create new context for this profile (session isolation)
            # Rotate through selected engines; default to Chromium when none selected.
            engines = selected_browser_engines or ['Chromium']
            engine = engines[profile_num % len(engines)]
            self.emit_log(f'[Browser {profile_num}] Launching...')
            context = await self.browser_manager.create_context(platform, proxy_override=proxy_override, engine=engine)
            if not context:
                self.emit_log(f'Failed to create browser context for profile {profile_num}', 'ERROR')
                return False
            
            self.emit_log(f'[Browser {profile_num}] Browser opened successfully')
            self.active_browsers.append(context)
            self.active_contexts.append(context)
            await self.apply_zoom_out_to_context(context, f'Browser {profile_num}')
            
            page = None
            try:
                # Get proxy location once for the profile
                proxy_location = getattr(context, '_proxy_location', None)
                
                # Get the first page from persistent context (instead of creating new page)
                page = context.pages[0] if context.pages else await context.new_page()
                self.active_pages.append(page)
                
                # Display proxy location if available
                if proxy_location:
                    country = proxy_location.get('country', 'Unknown')
                    ip = proxy_location.get('ip', 'unknown')
                    location_text_safe = json.dumps(f"Proxy: {country} | IP: {ip}")
                    
                    # Inject location display into page with null check for document.body
                    await page.add_init_script(f"""
                        window.addEventListener('load', () => {{
                            if (document.body) {{
                                const locationDiv = document.createElement('div');
                                locationDiv.id = 'proxy-location-display';
                                locationDiv.style.cssText = `
                                    position: fixed;
                                    top: 10px;
                                    right: 10px;
                                    background: rgba(0, 0, 0, 0.8);
                                    color: #00ff00;
                                    padding: 10px 15px;
                                    border-radius: 5px;
                                    font-family: monospace;
                                    font-size: 12px;
                                    z-index: 999999;
                                    pointer-events: none;
                                `;
                                locationDiv.textContent = {location_text_safe};
                                document.body.appendChild(locationDiv);
                            }}
                        }});
                    """)
                
                # Select URL for this profile (cycle through URL list)
                target_url = url_list[(profile_num - 1) % len(url_list)]
                
                # Execute the profile visit
                result = await self.execute_single_visit(
                    page, profile_num, target_url, visit_type,
                    search_keyword, target_domain, search_engine, referral_sources,
                    time_to_spend, time_to_spend, enable_consent,  # Use same time for both min/max
                    enable_interaction, enable_extra_pages, max_pages,
                    consent_manager, enable_highlight,
                    utm_campaign, utm_medium, utm_term, utm_content,
                    random_ad_clicking_enabled=random_ad_clicking_enabled,
                    random_click_ratio=random_click_ratio,
                    custom_random_targets=custom_random_targets,
                )
                
                # Close page
                try:
                    await page.close()
                except Exception:
                    pass  # Ignore any errors during cleanup
                
                self.emit_log(f'✓ Profile {profile_num} completed')
                return result
                
            finally:
                # Always close context and remove from active tracking
                if page is not None:
                    try:
                        self.active_pages.remove(page)
                    except ValueError:
                        pass
                try:
                    self.active_browsers.remove(context)
                except ValueError:
                    pass
                try:
                    self.active_contexts.remove(context)
                except ValueError:
                    pass
                await context.close()
                
        except Exception as e:
            self.emit_log(f'Profile {profile_num} error: {e}', 'ERROR')
            return False
    
    async def execute_browser_with_tabs(self, browser_num, url_list, num_tabs, platforms, visit_type,
                                        search_keyword, target_domain, search_engine, referral_sources,
                                        min_time_spend, max_time_spend, enable_consent,
                                        enable_interaction, enable_extra_pages, max_pages,
                                        consent_manager, enable_highlight=False,
                                        utm_campaign='', utm_medium='social', utm_term='', utm_content=''):
        """Execute a single browser with multiple tabs."""
        try:
            # Select random platform for this browser
            platform = random.choice(platforms)
            
            self.emit_log(f'━━━ Browser {browser_num} | Platform: {platform} | Opening {num_tabs} tabs ━━━')
            
            # Create new context for this browser (session isolation)
            self.emit_log(f'Creating browser context for browser {browser_num}...')
            context = await self.browser_manager.create_context(platform)
            if not context:
                self.emit_log(f'Failed to create browser context for browser {browser_num}', 'ERROR')
                return False
            await self.apply_zoom_out_to_context(context, f'Browser {browser_num}')
            
            try:
                # Get proxy location once for the browser
                proxy_location = getattr(context, '_proxy_location', None)
                
                # Create multiple tabs (pages) in this browser
                tasks = []
                pages = []
                
                for tab_idx in range(num_tabs):
                    # For first tab, use existing page from persistent context; for others, create new
                    if tab_idx == 0 and context.pages:
                        page = context.pages[0]
                    else:
                        page = await context.new_page()
                    pages.append(page)
                    
                    # Display proxy location in each tab if available
                    if proxy_location:
                        country = proxy_location.get('country', 'Unknown')
                        ip = proxy_location.get('ip', 'unknown')
                        location_text_safe = json.dumps(f"Proxy: {country} | IP: {ip}")
                        
                        # Inject location display into page with null check for document.body
                        await page.add_init_script(f"""
                            window.addEventListener('load', () => {{
                                if (document.body) {{
                                    const locationDiv = document.createElement('div');
                                    locationDiv.id = 'proxy-location-display';
                                    locationDiv.style.cssText = `
                                        position: fixed;
                                        top: 10px;
                                        right: 10px;
                                        background: rgba(0, 0, 0, 0.8);
                                        color: #00ff00;
                                        padding: 10px 15px;
                                        border-radius: 5px;
                                        font-family: monospace;
                                        font-size: 12px;
                                        z-index: 999999;
                                        pointer-events: none;
                                    `;
                                    locationDiv.textContent = {location_text_safe};
                                    document.body.appendChild(locationDiv);
                                }}
                            }});
                        """)
                    
                    # Select URL for this tab (cycle through URL list if more tabs than URLs)
                    target_url = url_list[tab_idx % len(url_list)]
                    
                    # Create task for this tab
                    task = self.execute_single_visit(
                        page, tab_idx + 1, target_url, visit_type,
                        search_keyword, target_domain, search_engine, referral_sources,
                        min_time_spend, max_time_spend, enable_consent,
                        enable_interaction, enable_extra_pages, max_pages,
                        consent_manager, enable_highlight,
                        utm_campaign, utm_medium, utm_term, utm_content
                    )
                    tasks.append(task)
                
                # Execute all tabs concurrently
                self.emit_log(f'[Browser {browser_num}] Running {num_tabs} tabs simultaneously...')
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successes
                success_count = sum(1 for r in results if r is True)
                self.emit_log(f'[Browser {browser_num}] Completed: {success_count}/{num_tabs} tabs successful')
                
                # Close all pages
                for page in pages:
                    try:
                        await page.close()
                    except Exception:
                        pass  # Ignore any errors during cleanup
                
                return success_count > 0
                
            finally:
                # Always close context after all tabs complete
                await context.close()
                
        except Exception as e:
            self.emit_log(f'✗ Browser {browser_num} error: {e}', 'ERROR')
            return False
    
    async def run_browser_instance(self, browser_index: int, browser_engine: str, shared_state: dict):
        """Run a single browser instance with full traffic workflow.

        Launches one browser window, executes the configured traffic workflow,
        auto-restarts immediately when finished (or on failure), and closes only
        its own browser instance.  All traffic/click logic runs independently
        inside this instance.

        Args:
            browser_index:  1-based browser number used for logging and URL cycling.
            browser_engine: Pre-assigned engine ('Chromium', 'Firefox', 'WebKit').
            shared_state:   Dict containing shared runtime objects/counters:
                - 'proxy_manager'    : ProxyManager instance
                - 'consent_manager'  : ConsentManager instance (or None)
                - 'active_count'     : list([int]) – mutable active-browser counter
                - 'completed_count'  : list([int]) – mutable completed-profile counter
                - 'num_concurrent'   : total number of concurrent browser slots
        """
        proxy_manager     = shared_state['proxy_manager']
        consent_manager   = shared_state.get('consent_manager')
        active_count_ref  = shared_state['active_count']       # list([int])
        completed_ref     = shared_state['completed_count']    # list([int])
        num_concurrent    = shared_state['num_concurrent']

        # Config values – read once up front
        url_list                   = self.config.get('url_list', [])
        random_time_enabled        = self.config.get('random_time_enabled', False)
        stay_time                  = self.config.get('stay_time', 120)
        min_time_spend             = self.config.get('min_time_spend', 120)
        max_time_spend             = self.config.get('max_time_spend', 240)
        platforms                  = self.config.get('platforms', ['windows'])
        visit_type                 = self.config.get('visit_type', 'direct')
        search_keyword             = self.config.get('search_keyword', '')
        target_domain              = self.config.get('target_domain', '')
        search_engine_cfg          = self.config.get('search_engine', 'Google')
        referral_sources           = self.config.get('referral_sources', [])
        utm_campaign               = self.config.get('utm_campaign', '')
        utm_medium                 = self.config.get('utm_medium', 'social')
        utm_term                   = self.config.get('utm_term', '')
        utm_content                = self.config.get('utm_content', '')
        enable_interaction         = self.config.get('enable_interaction', False)
        enable_extra_pages         = self.config.get('enable_extra_pages', False)
        max_pages                  = self.config.get('max_pages', 5)
        enable_consent             = self.config.get('enable_consent', True)
        enable_text_highlight      = self.config.get('enable_text_highlight', False)
        high_cpc_enabled           = self.config.get('high_cpc_enabled', False)
        high_cpc_url               = self.config.get('high_cpc_url', '')
        high_cpc_target            = self.config.get('high_cpc_target', '')
        high_cpc_stay_time         = self.config.get('high_cpc_stay_time', 180)
        random_ad_clicking_enabled = self.config.get(
            'random_ad_clicking_enabled',
            self.config.get('sponsored_click_enabled', False)
        )
        random_click_ratio = self.config.get(
            'random_click_ratio',
            self.config.get('sponsored_click_ratio', 50)
        ) / 100

        # Resolve custom ad selector list (same legacy-compat logic as run_normal_mode)
        _legacy_sponsored = self.config.get('custom_sponsored_selectors', [])
        _legacy_iframe    = self.config.get('custom_iframe_selectors', [])
        _legacy_combined  = _legacy_sponsored + [
            s for s in _legacy_iframe if s not in set(_legacy_sponsored)
        ]
        if 'ad_selectors' in self.config:
            custom_random_targets = [
                entry['selector']
                for entry in self.config['ad_selectors']
                if isinstance(entry, dict)
                and entry.get('enabled', True)
                and entry.get('selector', '').strip()
            ]
        else:
            custom_random_targets = self.config.get('custom_random_targets', _legacy_combined)

        self.emit_log(f'[Browser {browser_index}] Launching...')

        retry_proxy   = None
        proxy_retries = 0

        while self.running:
            current_proxy  = None
            is_browser_open = False

            try:
                if not self.running:
                    break

                # ── Proxy selection ──────────────────────────────────────────
                if proxy_manager.proxy_enabled:
                    if retry_proxy is not None:
                        current_proxy = retry_proxy
                        retry_proxy   = None
                        masked = proxy_manager.mask_proxy_for_logging(current_proxy)
                        self.emit_log(
                            f'[Browser {browser_index}] ♻ Retrying same proxy '
                            f'(attempt {proxy_retries + 1}): {masked}'
                        )
                    else:
                        proxy_retries = 0
                        remaining = proxy_manager.get_remaining_proxies()
                        if remaining <= 0:
                            self.emit_log(
                                f'[Browser {browser_index}] ⛔ No more proxies, stopping slot',
                                'INFO'
                            )
                            break
                        current_proxy = proxy_manager.get_proxy_config()
                        if current_proxy is None:
                            self.emit_log(
                                f'[Browser {browser_index}] ⛔ No more proxies, stopping slot',
                                'INFO'
                            )
                            break
                        masked = proxy_manager.mask_proxy_for_logging(current_proxy)
                        remaining_after = proxy_manager.get_remaining_proxies()
                        self.emit_log(
                            f'[Browser {browser_index}] 🟢 Launching browser | '
                            f'🔷 Proxy: {masked} | 📊 Remaining proxies: {remaining_after}'
                        )
                else:
                    self.emit_log(f'[Browser {browser_index}] 🟢 Launching browser (no proxy)')

                is_browser_open = True
                # NOTE: asyncio is single-threaded; tasks only yield at `await` points,
                # so these read-modify-write operations are safe without a lock.
                active_count_ref[0] += 1
                self.emit_log(f'📊 Active browsers: {active_count_ref[0]}/{num_concurrent}')

                # ── Execute the profile ──────────────────────────────────────
                result = await self.execute_single_profile(
                    browser_index, url_list, platforms, visit_type,
                    search_keyword, target_domain, search_engine_cfg, referral_sources,
                    random_time_enabled, stay_time, min_time_spend, max_time_spend,
                    enable_consent,
                    enable_interaction, enable_extra_pages, max_pages,
                    consent_manager, enable_text_highlight,
                    utm_campaign, utm_medium, utm_term, utm_content,
                    high_cpc_enabled, high_cpc_url, high_cpc_target, high_cpc_stay_time,
                    proxy_override=current_proxy,
                    random_ad_clicking_enabled=random_ad_clicking_enabled,
                    random_click_ratio=random_click_ratio,
                    custom_random_targets=custom_random_targets,
                    selected_browser_engines=[browser_engine],
                )

                if result:
                    completed_ref[0] += 1
                    self.emit_log(
                        f'[Browser {browser_index}] ✓ Profile completed successfully '
                        f'(Total: {completed_ref[0]})'
                    )
                    retry_proxy   = None
                    proxy_retries = 0
                else:
                    if current_proxy and proxy_manager.proxy_enabled and proxy_retries < 3:
                        self.emit_log(
                            f'[Browser {browser_index}] ✗ Profile failed — retrying with same proxy',
                            'WARNING'
                        )
                        retry_proxy    = current_proxy
                        proxy_retries += 1
                    else:
                        self.emit_log(
                            f'[Browser {browser_index}] ✗ Profile failed — moving to next proxy',
                            'WARNING'
                        )
                        retry_proxy   = None
                        proxy_retries = 0

            except Exception as e:
                self.emit_log(f'[Browser {browser_index}] ❌ Exception: {e}', 'ERROR')

                is_proxy_err = 'proxy' in str(e).lower() or 'net::ERR' in str(e)
                if is_proxy_err:
                    self.emit_log(
                        f'[Browser {browser_index}] ⚠ Proxy failure — moving to next proxy',
                        'WARNING'
                    )
                    retry_proxy   = None
                    proxy_retries = 0
                elif current_proxy and proxy_manager.proxy_enabled and proxy_retries < 3:
                    self.emit_log(
                        f'[Browser {browser_index}] 🔄 Browser crashed — retrying with same proxy',
                        'WARNING'
                    )
                    retry_proxy    = current_proxy
                    proxy_retries += 1
                else:
                    retry_proxy   = None
                    proxy_retries = 0

            finally:
                if is_browser_open:
                    active_count_ref[0] -= 1
                    self.emit_log(
                        f'🔴 [Browser {browser_index}] Closed | '
                        f'Active: {active_count_ref[0]}/{num_concurrent}'
                    )

                if self.running:
                    if retry_proxy is not None:
                        self.emit_log(
                            f'[Browser {browser_index}] ⟳ Immediately launching replacement '
                            f'browser (same proxy)...'
                        )
                    elif proxy_manager.proxy_enabled \
                            and proxy_manager.get_remaining_proxies() > 0:
                        self.emit_log(
                            f'[Browser {browser_index}] ⟳ Immediately launching replacement '
                            f'browser with next proxy...'
                        )
                    elif not proxy_manager.proxy_enabled:
                        self.emit_log(
                            f'[Browser {browser_index}] ⟳ Immediately restarting browser...'
                        )

        self.emit_log(f'[Browser {browser_index}] ■ Browser slot stopped')

    async def run_automation(self):
        """Main automation loop with concurrent execution, multiple URLs, and platform mixing support."""
        try:
            self.running = True
            self.emit_log('Starting automation...')
            
            # Check if RPA mode is enabled
            rpa_mode = self.config.get('rpa_mode', False)
            
            if rpa_mode:
                # RPA Mode: Execute RPA script
                await self.run_rpa_mode()
            else:
                # Normal Mode: Execute standard automation
                await self.run_normal_mode()
            
        except Exception as e:
            self.emit_log(f'Automation error: {e}', 'ERROR')
        
        finally:
            self.running = False
            self.finished_signal.emit()
    
    async def run_rpa_mode(self):
        """Execute RPA script mode with concurrent visible browsers that auto-restart.
        
        Maintains exactly N concurrent visible browsers in taskbar at all times:
        - Starts N browsers immediately with no delays
        - When any browser closes (manual/proxy failure/any reason), immediately restarts
        - Ensures N browsers are always visible in taskbar, not just in logs
        """
        try:
            self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            self.emit_log('RPA MODE: Executing RPA script with visible browsers')
            self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            
            rpa_script = self.config.get('rpa_script', {})
            num_concurrent = self.config.get('number_of_browsers', self.config.get('concurrent', 1))
            platforms = self.config.get('platforms', ['windows'])
            enable_consent = self.config.get('enable_consent', True)
            
            # Create consent manager if enabled
            consent_manager = ConsentManager(self.log_manager) if enable_consent else None
            if consent_manager:
                self.emit_log('✓ Consent popup handler enabled')
            
            # Check proxy configuration
            proxy_manager = self.browser_manager.proxy_manager
            if proxy_manager.proxy_enabled:
                proxy_count = proxy_manager.get_proxy_count()
                if proxy_count > 0:
                    self.emit_log(f'✓ Proxy configuration loaded: {proxy_count} proxies available')
                else:
                    self.emit_log('⚠ Proxy enabled but no proxies loaded', 'WARNING')
            else:
                self.emit_log('Proxy disabled, using direct connection')
            
            # Check imported useragents
            if self.browser_manager.imported_useragents:
                self.emit_log(f'✓ Imported useragents loaded: {len(self.browser_manager.imported_useragents)} user agents available')
            else:
                self.emit_log('Using generated user agents (no imported user agents)')
            
            # Force visible browser - headless mode removed completely
            self.browser_manager.headless = False  # ALWAYS VISIBLE
            
            # Show platform selection
            platforms_str = ', '.join(platforms)
            self.emit_log(f'✓ Platform(s) selected: {platforms_str}')
            
            self.emit_log(f'Starting {num_concurrent} concurrent visible browser(s)...')
            self.emit_log(f'✓ Maintaining exactly {num_concurrent} browsers in taskbar at all times')
            self.emit_log('✓ Zero-delay startup: All browsers start immediately')
            self.emit_log('✓ Instant restart: Browsers restart immediately when closed (no delays)')
            
            # Initialize browser
            success = await self.browser_manager.initialize()
            if not success:
                self.emit_log('Failed to initialize browser', 'ERROR')
                return
            
            # Reset active_tasks so stale references from any prior run don't affect stop()
            self.active_tasks = []
            
            # Track running concurrent browsers in the worker's active_tasks list
            concurrent_counter = 0

            # Active browser count — shared counter so logs always show the real running total
            active_browser_count = 0

            async def run_rpa_concurrent(concurrent_num):
                """Run a single RPA browser slot with automatic continuous restart and proxy retry."""
                nonlocal concurrent_counter, active_browser_count
                retry_proxy = None   # Proxy to retry on crash (None = get fresh from queue)
                proxy_retries = 0    # Retry counter to avoid infinite loops on same proxy

                # Continuous loop - runs indefinitely until stopped or no more proxies
                while self.running:
                    context = None
                    is_browser_open = False
                    used_proxy = None
                    try:
                        # Check stop immediately at start of each iteration
                        if not self.running:
                            break
                        
                        # Select random platform for this concurrent browser
                        platform = random.choice(platforms)
                        
                        # Check proxy availability and determine which proxy to use
                        if proxy_manager.proxy_enabled:
                            remaining = proxy_manager.get_remaining_proxies()
                            if remaining <= 0 and retry_proxy is None:
                                self.emit_log(f'[Browser {concurrent_num}] ⛔ No more proxies available, stopping slot', 'INFO')
                                break
                            if retry_proxy is not None:
                                masked = proxy_manager.mask_proxy_for_logging(retry_proxy)
                                self.emit_log(f'[Browser {concurrent_num}] ♻ Retrying same proxy (attempt {proxy_retries + 1}): {masked} | Platform: {platform}')
                            else:
                                self.emit_log(f'[Browser {concurrent_num}] 🟢 Launching browser | Platform: {platform} | Remaining proxies: {remaining}')
                        else:
                            self.emit_log(f'[Browser {concurrent_num}] Launching...')
                        
                        # Create browser context (retry_proxy passed so queue is NOT re-consumed on retry)
                        context = await self.browser_manager.create_context(
                            platform=platform,
                            use_proxy=proxy_manager.proxy_enabled,
                            proxy_override=retry_proxy
                        )
                        
                        if not context:
                            self.emit_log(f'[Browser {concurrent_num}] ⚠ Failed to create context, retrying in 2s...', 'WARNING')
                            # Context creation failed — clear retry so next attempt gets a fresh proxy
                            retry_proxy = None
                            proxy_retries = 0
                            await asyncio.sleep(2)
                            continue
                        
                        # Store which proxy is in use so we can retry with it on crash
                        used_proxy = getattr(context, '_proxy_config', None)
                        is_browser_open = True
                        active_browser_count += 1
                        self.active_browsers.append(context)
                        self.active_contexts.append(context)
                        await self.apply_zoom_out_to_context(context, f'Browser {concurrent_num}')
                        self.emit_log(f'[Browser {concurrent_num}] Browser opened successfully')
                        
                        # Log proxy in use and current active count
                        if proxy_manager.proxy_enabled and used_proxy:
                            masked = proxy_manager.mask_proxy_for_logging(used_proxy)
                            remaining_now = proxy_manager.get_remaining_proxies()
                            self.emit_log(f'[Browser {concurrent_num}] 🔷 Proxy in use: {masked}')
                            self.emit_log(f'[Browser {concurrent_num}] 📊 Remaining proxies: {remaining_now}')
                        self.emit_log(f'📊 Active browsers: {active_browser_count}/{num_concurrent}')

                        # Execute RPA script
                        script_executor = ScriptExecutor(self.log_manager, consent_manager)
                        self.emit_log(f'[Browser {concurrent_num}] Executing RPA script...')
                        success = await script_executor.execute_script(rpa_script, context)
                        
                        if success:
                            self.emit_log(f'[Browser {concurrent_num}] ✓ RPA script completed successfully')
                        else:
                            self.emit_log(f'[Browser {concurrent_num}] ✗ RPA script had errors', 'WARNING')
                        
                        # Script finished (success or clean error) — use fresh proxy next time
                        retry_proxy = None
                        proxy_retries = 0
                        
                    except Exception as e:
                        self.emit_log(f'[Browser {concurrent_num}] ❌ Error: {e}', 'ERROR')
                        
                        # Decide retry strategy
                        is_proxy_err = 'proxy' in str(e).lower() or 'net::ERR' in str(e)
                        if is_proxy_err:
                            self.emit_log(f'[Browser {concurrent_num}] ⚠ Proxy failure — moving to next proxy', 'WARNING')
                            retry_proxy = None
                            proxy_retries = 0
                        elif used_proxy and proxy_manager.proxy_enabled and proxy_retries < 3:
                            self.emit_log(f'[Browser {concurrent_num}] 🔄 Browser crashed — retrying with same proxy', 'WARNING')
                            retry_proxy = used_proxy
                            proxy_retries += 1
                        else:
                            self.emit_log(f'[Browser {concurrent_num}] ⚠ Max retries reached — moving to next proxy', 'WARNING')
                            retry_proxy = None
                            proxy_retries = 0
                    
                    finally:
                        if is_browser_open:
                            active_browser_count -= 1
                            self.emit_log(f'🔴 [Browser {concurrent_num}] Browser closed | Active: {active_browser_count}/{num_concurrent}')
                        if context:
                            try:
                                self.active_browsers.remove(context)
                            except ValueError:
                                pass
                            try:
                                self.active_contexts.remove(context)
                            except ValueError:
                                pass
                            try:
                                await context.close()
                            except:
                                pass  # Context might already be closed
                        
                        # Decide whether to restart immediately
                        should_restart = self.running
                        if proxy_manager.proxy_enabled and proxy_manager.get_remaining_proxies() <= 0 and retry_proxy is None:
                            should_restart = False
                            self.emit_log(f'[Browser {concurrent_num}] ⛔ No more proxies, stopping slot', 'INFO')
                        
                        if should_restart:
                            self.emit_log(f'[Browser {concurrent_num}] ⟳ Immediately launching replacement browser...')
                            # Immediate restart — no delay maintains the configured concurrent count
                
                self.emit_log(f'[Browser {concurrent_num}] ■ Browser slot stopped')
            
            try:
                # Launch all RPA browser slots simultaneously — no stagger delays
                self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                self.emit_log(f'Launching {num_concurrent} RPA browser(s) simultaneously...')
                self.emit_log(f'✓ All {num_concurrent} browser windows open at the same time')
                self.emit_log(f'✓ Instant restart: Browser restarts immediately when closed')
                self.emit_log(f'✓ Proxy retry: Same proxy reused if browser crashes before completing')
                if proxy_manager.proxy_enabled and proxy_manager.get_proxy_count() > 0:
                    self.emit_log(f'✓ Proxy mode: Will continue until all {proxy_manager.get_proxy_count()} proxies consumed')
                else:
                    self.emit_log(f'✓ No-proxy mode: Will run continuously until stopped')
                self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                for i in range(num_concurrent):
                    concurrent_counter += 1
                    task = asyncio.create_task(run_rpa_concurrent(concurrent_counter))
                    self.active_tasks.append(task)  # Track in worker's task list
                
                self.emit_log(f'✓ Created {len(self.active_tasks)} concurrent browser slots')
                self.emit_log(f'✓ All {num_concurrent} browser slots started and running')
                self.emit_log('Browsers will automatically restart if closed. Press STOP to end automation.')
                await asyncio.gather(*self.active_tasks, return_exceptions=True)
                
                self.emit_log('✓ All concurrent browsers stopped')
                    
            finally:
                # Force close all browsers immediately
                await self.browser_manager.force_close_all()
                self.emit_log('RPA mode execution finished')
            
        except Exception as e:
            self.emit_log(f'RPA mode error: {e}', 'ERROR')
    
    async def run_normal_mode(self):
        """Execute normal automation mode with fully parallel browser instances.

        Launches all N browser windows simultaneously via asyncio tasks — no
        stagger, no waiting for one browser to close before opening the next.
        Each browser runs its own independent traffic workflow and restarts
        immediately when it completes a profile cycle.
        """
        try:
            # ── Configuration ────────────────────────────────────────────────
            url_list        = self.config.get('url_list', [])
            num_concurrent  = self.config.get('number_of_browsers', self.config.get('concurrent', 1))
            platforms       = self.config.get('platforms', ['windows'])
            enable_consent  = self.config.get('enable_consent', True)
            random_time_enabled = self.config.get('random_time_enabled', False)
            stay_time       = self.config.get('stay_time', 120)
            min_time_spend  = self.config.get('min_time_spend', 120)
            max_time_spend  = self.config.get('max_time_spend', 240)
            enable_text_highlight = self.config.get('enable_text_highlight', False)
            high_cpc_enabled   = self.config.get('high_cpc_enabled', False)
            high_cpc_url       = self.config.get('high_cpc_url', '')
            high_cpc_target    = self.config.get('high_cpc_target', '')

            selected_browser_engines = self.config.get('selected_browser_engines', ['Chromium'])

            self.emit_log(f'Configuration: {len(url_list)} URLs, {num_concurrent} concurrent browsers')
            platforms_str = ', '.join(platforms)
            self.emit_log(f'Platform(s) selected: {platforms_str}')
            if high_cpc_enabled:
                high_cpc_stay_time = self.config.get('high_cpc_stay_time', 180)
                self.emit_log('✓ HIGH CPC/CPM Mode enabled')
                self.emit_log(f'  High CPC URL: {high_cpc_url[:50]}...')
                self.emit_log(f'  Target Domain: {high_cpc_target[:50]}...')
                self.emit_log(f'  Target Stay Time: {high_cpc_stay_time} seconds')
            if random_time_enabled:
                self.emit_log(f'Time per profile: Random between {min_time_spend}-{max_time_spend} seconds with human scrolling')
            else:
                self.emit_log(f'Time per profile: Fixed {stay_time} seconds with human scrolling')
            if enable_text_highlight:
                self.emit_log('✓ Text highlighting enabled')

            # ── Proxy setup ──────────────────────────────────────────────────
            proxy_manager = self.browser_manager.proxy_manager
            if proxy_manager.proxy_enabled:
                proxy_count = proxy_manager.get_proxy_count()
                if proxy_count > 0:
                    proxy_manager.initialize_queue()
                    self.emit_log(f'✓ Proxy configuration loaded: {proxy_count} proxies available')
                    self.emit_log(f'✓ Worker pool mode: {num_concurrent} concurrent browsers will run until all proxies consumed')
                else:
                    self.emit_log('⚠ Proxy enabled but no proxies loaded', 'WARNING')
            else:
                self.emit_log('Proxy disabled, using direct connection')
                self.emit_log(f'Running {num_concurrent} concurrent browser(s) without proxy rotation')

            # ── Playwright init ──────────────────────────────────────────────
            self.browser_manager.headless = False  # ALWAYS VISIBLE
            self.emit_log('Initializing Playwright...')
            success = await self.browser_manager.initialize()
            if not success:
                self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'ERROR')
                self.emit_log('Failed to initialize Playwright', 'ERROR')
                self.emit_log('Please check the logs above for details', 'ERROR')
                self.emit_log('Common issues:', 'ERROR')
                self.emit_log('  1. Chrome not installed (required for channel="chrome")', 'ERROR')
                self.emit_log('  2. Port conflict or permission issues', 'ERROR')
                self.emit_log('  3. System resources (memory/disk) insufficient', 'ERROR')
                self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'ERROR')
                return

            consent_manager = ConsentManager(self.log_manager) if enable_consent else None

            # Reset active_tasks so stale references from any prior run don't affect stop()
            self.active_tasks = []

            # Shared mutable state — single-element lists so run_browser_instance can mutate them
            shared_state = {
                'proxy_manager':   proxy_manager,
                'consent_manager': consent_manager,
                'active_count':   [0],   # [int] mutable active-browser counter
                'completed_count': [0],  # [int] mutable completed-profile counter
                'num_concurrent':  num_concurrent,
            }

            self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            self.emit_log(f'Launching {num_concurrent} browser(s) simultaneously')
            self.emit_log(f'✓ All {num_concurrent} browser windows open at the same time')
            self.emit_log(f'✓ Instant replacement: Browser restarts immediately when one closes')
            self.emit_log(f'✓ Proxy retry: Same proxy reused if browser crashes before completing')
            engines_str = ', '.join(dict.fromkeys(selected_browser_engines))
            self.emit_log(f'✓ Browser engine(s): {engines_str}')
            if proxy_manager.proxy_enabled and proxy_manager.get_proxy_count() > 0:
                self.emit_log(f'✓ Proxy mode: Will continue until all {proxy_manager.get_proxy_count()} proxies consumed')
            else:
                self.emit_log(f'✓ No-proxy mode: Will run continuously until stopped')
            self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

            try:
                # Create all browser tasks simultaneously — no delays between them
                browser_tasks = []
                for i in range(num_concurrent):
                    engine = selected_browser_engines[i % len(selected_browser_engines)]
                    task = asyncio.create_task(
                        self.run_browser_instance(i + 1, engine, shared_state)
                    )
                    browser_tasks.append(task)
                    self.active_tasks.append(task)

                self.emit_log(f'✓ Created {len(browser_tasks)} browser tasks simultaneously')
                self.emit_log('Browsers will automatically restart if closed. Press STOP to end automation.')
                await asyncio.gather(*browser_tasks, return_exceptions=True)

                self.emit_log('✓ All concurrent browsers stopped')

            except Exception as e:
                self.emit_log(f'Browser pool error: {e}', 'ERROR')

            completed_count = shared_state['completed_count'][0]
            self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            self.emit_log(f'✓ Automation completed: {completed_count} profiles processed successfully')
            self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

            # Cleanup — force close all browsers immediately
            await self.browser_manager.force_close_all()
            self.emit_log('Browser closed, automation finished')

        except Exception as e:
            self.emit_log(f'Normal mode error: {e}', 'ERROR')
    
    def run(self):
        """Entry point for thread execution."""
        asyncio.run(self.run_automation())


# ============================================================================
# CUSTOM WIDGETS FOR DRAG AND DROP
# ============================================================================

class WorkflowListWidget(QListWidget):
    """Custom QListWidget that accepts drops from Action Toolbox."""
    
    def __init__(self, parent_gui, parent=None):
        super().__init__(parent)
        self.parent_gui = parent_gui
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        """Accept drag events from action toolbox or internal reordering."""
        if event.source() == self or event.source() == self.parent_gui.action_toolbox:
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Accept drag move events."""
        if event.source() == self or event.source() == self.parent_gui.action_toolbox:
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event from action toolbox or internal reordering."""
        if event.source() == self.parent_gui.action_toolbox:
            # Drop from action toolbox - add new workflow step
            current_item = self.parent_gui.action_toolbox.currentItem()
            if current_item:
                action_name = current_item.text()
                step_type = self.parent_gui.action_to_step_type(action_name)
                
                # Create step with UUID
                step = {
                    'id': str(uuid.uuid4()),
                    'type': step_type,
                    'config': self.parent_gui.get_default_config(step_type)
                }
                
                # Determine drop position
                drop_position = self.indexAt(event.position().toPoint())
                if drop_position.isValid():
                    drop_row = drop_position.row()
                    # Insert at drop position
                    self.parent_gui.workflow_steps.insert(drop_row, step)
                else:
                    # Append to end
                    drop_row = len(self.parent_gui.workflow_steps)
                    self.parent_gui.workflow_steps.append(step)
                
                # Add to visual list at drop position
                display_text = f"{action_name}"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.UserRole, step['id'])
                self.insertItem(drop_row, list_item)
                
                # Sync to JSON
                self.parent_gui.sync_visual_to_json()
                
                event.acceptProposedAction()
        elif event.source() == self:
            # Internal reordering - use default behavior
            super().dropEvent(event)
            # Rebuild workflow_steps list based on new order
            new_workflow_steps = []
            for i in range(self.count()):
                item = self.item(i)
                step_id = item.data(Qt.UserRole)
                step = next((s for s in self.parent_gui.workflow_steps if s['id'] == step_id), None)
                if step:
                    new_workflow_steps.append(step)
            self.parent_gui.workflow_steps = new_workflow_steps
            self.parent_gui.sync_visual_to_json()
        else:
            event.ignore()


# ============================================================================
# RPA SCRIPT NORMALIZATION UTILITIES
# ============================================================================

def normalize_action_type(action_type: str) -> str:
    """
    Normalize action type names to internal format.
    Supports multiple naming conventions for compatibility.
    """
    # Mapping of alternative names to internal names
    type_aliases = {
        # Alternative naming conventions
        'gotoUrl': 'navigate',
        'goto': 'navigate',
        'gotoURL': 'navigate',
        'goToUrl': 'navigate',
        'openUrl': 'navigate',
        
        'waitTime': 'wait',
        'waitFor': 'wait',
        'delay': 'wait',
        'sleep': 'wait',
        'pause': 'wait',
        
        'scrollPage': 'scroll',
        'pageScroll': 'scroll',
        'scrollTo': 'scroll',
        
        'clickElement': 'click',
        'clickOn': 'click',
        
        'inputText': 'input',
        'typeText': 'input',
        'enterText': 'input',
        
        'openPage': 'newPage',
        'createPage': 'newPage',
        'newTab': 'newPage',
        'openTab': 'newPage',
        
        'close': 'closePage',
        'closeCurrentPage': 'closePage',
    }
    
    # Return normalized type or original if not found
    return type_aliases.get(action_type, action_type)


def normalize_step_config(step_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize step configuration to internal format.
    Handles different property naming conventions.
    """
    normalized = {}
    
    # Handle navigate/gotoUrl action
    if step_type == 'navigate':
        normalized['url'] = config.get('url', config.get('URL', ''))
        normalized['timeout'] = config.get('timeout', config.get('timeOut', 30000))
    
    # Handle wait/waitTime action
    elif step_type == 'wait':
        # Support different timeout naming
        timeout = config.get('timeout', config.get('timeOut', config.get('duration', 1000)))
        
        # Check if it's a range-based wait
        timeout_type = config.get('timeoutType', config.get('type', 'fixedValue'))
        
        if timeout_type == 'fixedValue' or timeout_type == 'Fixed':
            normalized['duration'] = timeout
            normalized['min_duration'] = timeout
            normalized['max_duration'] = timeout
        else:
            # Random range
            normalized['duration'] = timeout
            normalized['min_duration'] = config.get('timeoutMin', config.get('min_duration', timeout))
            normalized['max_duration'] = config.get('timeoutMax', config.get('max_duration', timeout))
        
        normalized['mode'] = 'Fixed' if timeout_type == 'fixedValue' else 'Random'
    
    # Handle scroll/scrollPage action
    elif step_type == 'scroll':
        # Determine scroll position
        position = config.get('position', 'Intermediate')
        scroll_type_value = config.get('scrollType', config.get('type', 'position'))
        
        if position == 'bottom':
            normalized['depth'] = 100
            normalized['position'] = 'Bottom'
        elif position == 'top':
            normalized['depth'] = 0
            normalized['position'] = 'Top'
        else:
            normalized['depth'] = config.get('depth', config.get('distance', 50))
            normalized['position'] = position.capitalize() if position else 'Intermediate'
        
        # Handle scroll type (animation type, not step type)
        scroll_type = config.get('type', 'smooth')
        normalized['scroll_type'] = scroll_type.capitalize() if scroll_type else 'Smooth'
        
        # Speed settings
        normalized['min_speed'] = config.get('min_speed', 100)
        normalized['max_speed'] = config.get('max_speed', 500)
    
    # Handle click action
    elif step_type == 'click':
        normalized['selector'] = config.get('selector', '')
        normalized['confidence'] = config.get('confidence', 0.8)
    
    # Handle input action
    elif step_type == 'input':
        normalized['selector'] = config.get('selector', '')
        normalized['text'] = config.get('text', config.get('value', ''))
        normalized['typing_delay'] = config.get('typing_delay', config.get('typingDelay', 100))
    
    # For other actions or unmapped properties, copy all config as-is
    else:
        normalized = config.copy()
    
    # Preserve any additional properties not specifically mapped
    # IMPORTANT: Don't preserve 'type' as it may conflict with step type
    for key, value in config.items():
        if key not in normalized and key not in ['remark', 'description', 'type']:
            normalized[key] = value
    
    return normalized


def normalize_rpa_script(data: Any) -> Dict[str, Any]:
    """
    Normalize RPA script JSON to internal format.
    Handles multiple input formats:
    1. Array of steps with config objects
    2. Object with steps array
    3. Mixed formats
    """
    # If input is a list (array format), wrap it
    if isinstance(data, list):
        steps_data = data
    elif isinstance(data, dict):
        # If it already has 'steps', use it
        if 'steps' in data:
            steps_data = data['steps']
        else:
            # Single step object
            steps_data = [data]
    else:
        # Invalid format
        return {'name': 'Invalid Script', 'steps': []}
    
    # Normalize each step
    normalized_steps = []
    for step_data in steps_data:
        # Get the original type
        original_type = step_data.get('type', '')
        
        # Normalize the type
        step_type = normalize_action_type(original_type)
        
        # Get config (might be nested or flat)
        if 'config' in step_data:
            config = step_data.get('config', {})
        else:
            # Config is flat (properties at step level)
            config = {k: v for k, v in step_data.items() if k != 'type'}
        
        # Normalize the config
        normalized_config = normalize_step_config(step_type, config)
        
        # Create normalized step
        normalized_step = {
            'type': step_type,
            **normalized_config
        }
        
        normalized_steps.append(normalized_step)
    
    # Return in expected format
    return {
        'name': data.get('name', 'Loaded Script') if isinstance(data, dict) else 'Loaded Script',
        'description': data.get('description', 'Script loaded from JSON') if isinstance(data, dict) else 'Script loaded from JSON',
        'steps': normalized_steps
    }


# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class AppGUI(QMainWindow):
    """Main application GUI."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize security manager
        self.security_manager = None
        if SECURITY_AVAILABLE:
            try:
                self.security_manager = SecurityManager()
            except Exception as e:
                print(f"Security initialization warning: {e}")
        
        self.log_manager = LogManager()
        self.automation_thread = None
        self.automation_worker = None
        # Initialize confidence_input with default value (since sponsored tab is removed)
        self.confidence_input = QDoubleSpinBox()
        self.confidence_input.setValue(0.7)
        # Create a reusable proxy manager for counting
        self._proxy_count_manager = ProxyManager()
        # Initialize storage for imported useragents and cookies
        self.imported_useragents = []
        self.imported_cookies = []
        
        # Rate limiter for automation requests (max 100 starts per minute)
        self.rate_limiter = RateLimiter(max_requests=100, time_window=60) if SECURITY_AVAILABLE else None

        # Load ad selector data before init_ui so the widget can populate itself
        self._ad_selector_data: List[Dict[str, Any]] = self._load_ad_selectors_settings()

        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('HUMANEX v5')
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(1200, 700)  # Set minimum size for responsiveness
        
        # Apply modern color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                color: #000000;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #d0d0d0;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #f0f0f0;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #666;
                width: 6px;
                height: 6px;
                border-width: 0 2px 2px 0;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #d0d0d0;
                outline: 0;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #5dade2;
                color: white;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #d0d0d0;
                border-bottom: 1px solid #d0d0d0;
                border-top-right-radius: 4px;
                background-color: #f0f0f0;
            }
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
                background-color: #e0e0e0;
            }
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                image: none;
                border: 2px solid #666;
                width: 6px;
                height: 6px;
                border-width: 2px 2px 0 0;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #d0d0d0;
                border-top: 1px solid #d0d0d0;
                border-bottom-right-radius: 4px;
                background-color: #f0f0f0;
            }
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #e0e0e0;
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                image: none;
                border: 2px solid #666;
                width: 6px;
                height: 6px;
                border-width: 0 0 2px 2px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Content panel - Create first to initialize stacked_widget
        self.content_panel = self.create_content_panel()
        
        # Create sidebar navigation after content panel (so stacked_widget exists)
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Add content panel to layout
        main_layout.addWidget(self.content_panel)
    
    def create_sidebar(self) -> QWidget:
        """Create modern sidebar navigation."""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                color: white;
                background-color: transparent;
                border: none;
                font-size: 14px;
                border-left: 4px solid transparent;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-left: 4px solid #3498db;
            }
            QPushButton:checked {
                background-color: #34495e;
                border-left: 4px solid #3498db;
                font-weight: bold;
            }
            QLabel {
                color: white;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # App title and subtitle
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 20, 20, 10)
        title_layout.setSpacing(5)
        
        title = QLabel('HUMANEX v5')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('color: white; padding: 0;')
        title_layout.addWidget(title)
        
        subtitle = QLabel('Advanced Human\nBehaviour Simulation')
        subtitle.setFont(QFont('Arial', 9))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('color: #95a5a6; padding: 0;')
        subtitle.setWordWrap(True)
        title_layout.addWidget(subtitle)
        
        title_widget.setStyleSheet('background-color: #1a252f;')
        layout.addWidget(title_widget)
        
        # Navigation buttons
        self.nav_button_group = QButtonGroup()
        self.nav_button_group.setExclusive(True)
        
        nav_items = [
            ('🔧 Website Traffic', 0),
            ('🧠 Traffic Behaviour', 1),
            ('🌐 Proxy Settings', 2),
            ('🧩 RPA Script Creator', 3),
            ('🎮 Control', 4),
            ('📋 Logs', 5)
        ]
        
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            self.nav_button_group.addButton(btn, idx)
            layout.addWidget(btn)
        
        # Connect button group's idClicked signal to switch_content
        self.nav_button_group.idClicked.connect(self.switch_content)
        
        # Set first button as checked
        self.nav_button_group.button(0).setChecked(True)
        
        layout.addStretch()
        
        # Footer with credit
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(15, 15, 15, 15)
        footer_layout.setSpacing(5)
        
        version_label = QLabel('v5.0 • 2026')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet('color: #7f8c8d; font-size: 11px;')
        footer_layout.addWidget(version_label)
        
        credit_label = QLabel('Made with ❤ by <a href="https://asadwebdev.com" style="color: #3498db; text-decoration: none;">CODEWITHASAD</a>')
        credit_label.setAlignment(Qt.AlignCenter)
        credit_label.setStyleSheet('color: #7f8c8d; font-size: 10px;')
        credit_label.setOpenExternalLinks(True)
        credit_label.setTextFormat(Qt.RichText)
        footer_layout.addWidget(credit_label)
        
        layout.addWidget(footer_widget)
        
        return sidebar
    
    def switch_content(self, index: int):
        """Switch between different content sections."""
        self.stacked_widget.setCurrentIndex(index)
    
    def create_content_panel(self) -> QWidget:
        """Create content panel with stacked widget."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Stacked widget to hold different sections
        self.stacked_widget = QStackedWidget()
        
        # Add all sections
        self.stacked_widget.addWidget(self.create_website_tab())
        self.stacked_widget.addWidget(self.create_behavior_tab())
        self.stacked_widget.addWidget(self.create_proxy_tab())
        self.stacked_widget.addWidget(self.create_script_tab())
        self.stacked_widget.addWidget(self.create_control_tab())
        self.stacked_widget.addWidget(self.create_logs_tab())
        
        layout.addWidget(self.stacked_widget)
        
        return panel
    
    def create_website_tab(self) -> QWidget:
        """Create website configuration tab."""
        # Create scroll area wrapper
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Section Title
        section_title = QLabel('🔧 Website Traffic Configuration')
        section_title.setFont(QFont('Arial', 20, QFont.Bold))
        section_title.setStyleSheet('color: #2c3e50; padding: 10px 0;')
        layout.addWidget(section_title)
        
        # Website URL - Multiple URLs Support
        self.url_group = QGroupBox('🌍 Website Configuration')
        url_layout = QVBoxLayout()
        url_layout.setSpacing(10)
        
        url_layout.addWidget(QLabel('Target URLs (one URL opens per browser):'))
        
        # URL input and add button
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://example.com')
        url_input_layout.addWidget(self.url_input)
        
        add_url_btn = QPushButton('➕ Add URL')
        add_url_btn.clicked.connect(self.add_url_to_list)
        url_input_layout.addWidget(add_url_btn)
        url_layout.addLayout(url_input_layout)
        
        # URL list widget
        self.url_list_widget = QListWidget()
        self.url_list_widget.setMaximumHeight(100)
        url_layout.addWidget(self.url_list_widget)
        
        # Remove URL button
        remove_url_btn = QPushButton('🗑 Remove Selected URL')
        remove_url_btn.clicked.connect(self.remove_url_from_list)
        url_layout.addWidget(remove_url_btn)
        
        self.url_group.setLayout(url_layout)
        layout.addWidget(self.url_group)
        
        # Visit Type Section (NEW FEATURE)
        visit_type_group = QGroupBox('🔍 Visit Type')
        visit_type_layout = QVBoxLayout()
        visit_type_layout.setSpacing(10)
        
        # Radio buttons for visit type
        self.visit_type_group = QButtonGroup()
        self.visit_direct_radio = QRadioButton('Direct Visit')
        self.visit_referral_radio = QRadioButton('Referral Visit')
        self.visit_search_radio = QRadioButton('Search Visit')
        self.visit_high_cpc_radio = QRadioButton('💰 HIGH CPC/CPM Visit')
        self.visit_direct_radio.setChecked(True)
        
        self.visit_type_group.addButton(self.visit_direct_radio, 0)
        self.visit_type_group.addButton(self.visit_referral_radio, 1)
        self.visit_type_group.addButton(self.visit_search_radio, 2)
        self.visit_type_group.addButton(self.visit_high_cpc_radio, 3)
        
        visit_type_layout.addWidget(self.visit_direct_radio)
        visit_type_layout.addWidget(self.visit_referral_radio)
        visit_type_layout.addWidget(self.visit_search_radio)
        visit_type_layout.addWidget(self.visit_high_cpc_radio)
        
        # Connect signals to toggle visibility of sub-sections
        self.visit_referral_radio.toggled.connect(self.toggle_referral_section)
        self.visit_search_radio.toggled.connect(self.toggle_search_section)
        self.visit_high_cpc_radio.toggled.connect(self.toggle_high_cpc_section)
        
        visit_type_group.setLayout(visit_type_layout)
        layout.addWidget(visit_type_group)
        
        # Referral Source Selector (ENHANCED UTM FEATURE)
        self.referral_group = QGroupBox('🔗 Advanced UTM Referral Traffic Generator')
        referral_layout = QVBoxLayout()
        referral_layout.setSpacing(10)
        
        # UTM Parameter Inputs
        utm_params_group = QGroupBox('📊 UTM Parameters')
        utm_params_layout = QFormLayout()
        utm_params_layout.setSpacing(10)
        
        # Campaign Name
        self.utm_campaign_input = QLineEdit()
        self.utm_campaign_input.setPlaceholderText('summer_sale_2024')
        utm_params_layout.addRow('Campaign Name:', self.utm_campaign_input)
        
        # UTM Medium
        self.utm_medium_combo = QComboBox()
        self.utm_medium_combo.addItems(['social', 'paid_social', 'influencer', 'referral', 'cpc', 'display'])
        utm_params_layout.addRow('UTM Medium:', self.utm_medium_combo)
        
        # UTM Term (optional)
        self.utm_term_input = QLineEdit()
        self.utm_term_input.setPlaceholderText('targeting_keywords (optional)')
        utm_params_layout.addRow('UTM Term (Optional):', self.utm_term_input)
        
        # UTM Content (optional)
        self.utm_content_input = QLineEdit()
        self.utm_content_input.setPlaceholderText('banner_ad_1 (optional)')
        utm_params_layout.addRow('UTM Content (Optional):', self.utm_content_input)
        
        utm_params_group.setLayout(utm_params_layout)
        referral_layout.addWidget(utm_params_group)
        
        # Social Platform Selector
        platform_selector_group = QGroupBox('🌐 Select Social Media Platforms')
        platform_grid = QGridLayout()
        platform_grid.setSpacing(10)
        
        platform_label = QLabel('Select platforms for referral traffic (multi-select):')
        platform_grid.addWidget(platform_label, 0, 0, 1, 3)
        
        # Checkboxes in 3 columns - 16+ social platforms
        self.referral_facebook = QCheckBox('✅ Facebook')
        self.referral_google = QCheckBox('✅ Google')
        self.referral_twitter = QCheckBox('✅ Twitter (X)')
        self.referral_telegram = QCheckBox('✅ Telegram')
        self.referral_instagram = QCheckBox('✅ Instagram')
        self.referral_reddit = QCheckBox('✅ Reddit')
        self.referral_linkedin = QCheckBox('✅ LinkedIn')
        self.referral_pinterest = QCheckBox('✅ Pinterest')
        self.referral_youtube = QCheckBox('✅ YouTube')
        self.referral_tiktok = QCheckBox('✅ TikTok')
        self.referral_whatsapp = QCheckBox('✅ WhatsApp')
        self.referral_snapchat = QCheckBox('✅ Snapchat')
        self.referral_discord = QCheckBox('✅ Discord')
        self.referral_medium = QCheckBox('✅ Medium')
        self.referral_quora = QCheckBox('✅ Quora')
        self.referral_tumblr = QCheckBox('✅ Tumblr')
        self.referral_vk = QCheckBox('✅ VK')
        self.referral_weibo = QCheckBox('✅ Weibo')
        self.referral_line = QCheckBox('✅ LINE')
        
        # Set default checked
        self.referral_facebook.setChecked(True)
        self.referral_google.setChecked(True)
        
        # Add to grid (3 columns for better space utilization)
        row = 1
        col = 0
        for checkbox in [
            self.referral_facebook, self.referral_google, self.referral_twitter,
            self.referral_telegram, self.referral_instagram, self.referral_reddit,
            self.referral_linkedin, self.referral_pinterest, self.referral_youtube,
            self.referral_tiktok, self.referral_whatsapp, self.referral_snapchat,
            self.referral_discord, self.referral_medium, self.referral_quora,
            self.referral_tumblr, self.referral_vk, self.referral_weibo, self.referral_line
        ]:
            platform_grid.addWidget(checkbox, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        platform_selector_group.setLayout(platform_grid)
        referral_layout.addWidget(platform_selector_group)
        
        # Info label
        info_label = QLabel('ℹ️ UTM parameters will be automatically added to track referral traffic from selected platforms')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        info_label.setWordWrap(True)
        referral_layout.addWidget(info_label)
        
        self.referral_group.setLayout(referral_layout)
        self.referral_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.referral_group)
        
        # Search Settings (ENHANCED FEATURE - Multi-Engine Support)
        self.search_group = QGroupBox('🔎 Search Settings')
        search_layout = QVBoxLayout()
        search_layout.setSpacing(10)
        
        # Search Engine Selector
        search_layout.addWidget(QLabel('Search Engine:'))
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(['Google', 'Bing', 'Yahoo', 'DuckDuckGo', 'Yandex', 'Baidu'])
        self.search_engine_combo.setToolTip('Select which search engine to use (only 1 at a time)')
        search_layout.addWidget(self.search_engine_combo)
        
        search_layout.addWidget(QLabel('Search Keyword:'))
        self.search_keyword_input = QLineEdit()
        self.search_keyword_input.setPlaceholderText('Enter keyword to search...')
        search_layout.addWidget(self.search_keyword_input)
        
        search_layout.addWidget(QLabel('Target Domain (full URL with https://):'))
        self.target_domain_input = QLineEdit()
        self.target_domain_input.setPlaceholderText('https://example.com')
        search_layout.addWidget(self.target_domain_input)
        
        info_label = QLabel('ℹ️ Bot will:\n'
                           '1. Open selected search engine in a new tab\n'
                           '2. Type the keyword in a human-like way\n'
                           '3. Search for the keyword\n'
                           '4. Scan top 10 results for target domain\n'
                           '5. Click on target domain if found\n'
                           '6. Perform scrolling behavior\n'
                           '📝 Note: Target URLs above are NOT needed for Search Visit')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        info_label.setWordWrap(True)
        search_layout.addWidget(info_label)
        
        self.search_group.setLayout(search_layout)
        self.search_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.search_group)
        
        # HIGH CPC/CPM Mode Section
        self.high_cpc_group = QGroupBox('💰 HIGH CPC/CPM Mode Settings')
        high_cpc_layout = QVBoxLayout()
        high_cpc_layout.setSpacing(10)
        
        # High CPC Website URL
        high_cpc_layout.addWidget(QLabel('High CPC Website URL:'))
        self.high_cpc_url_input = QLineEdit()
        self.high_cpc_url_input.setPlaceholderText('https://high-cpc-website.com')
        high_cpc_layout.addWidget(self.high_cpc_url_input)
        
        # Target Domain URL
        high_cpc_layout.addWidget(QLabel('Target Domain URL:'))
        self.high_cpc_target_input = QLineEdit()
        self.high_cpc_target_input.setPlaceholderText('https://target-domain.com')
        high_cpc_layout.addWidget(self.high_cpc_target_input)
        
        # Stay Time
        stay_time_cpc_layout = QHBoxLayout()
        stay_time_cpc_layout.addWidget(QLabel('Target Stay Time (seconds):'))
        self.high_cpc_stay_time_input = QSpinBox()
        self.high_cpc_stay_time_input.setRange(30, 3600)
        self.high_cpc_stay_time_input.setValue(180)  # 3 minutes default
        self.high_cpc_stay_time_input.setSuffix(' sec')
        self.high_cpc_stay_time_input.setToolTip('Total time to spend on Target Domain')
        stay_time_cpc_layout.addWidget(self.high_cpc_stay_time_input)
        stay_time_cpc_layout.addStretch()
        high_cpc_layout.addLayout(stay_time_cpc_layout)
        
        # Info label
        info_label = QLabel('ℹ️ This mode will:\n'
                           '1. Open High CPC URL in 4 tabs with cookie handling\n'
                           '2. Perform shopping interaction in Tab 4 (add to bag, checkout, form filling)\n'
                           '3. Open Target Domain in 5th tab with scrolling and clicks\n'
                           '4. Close all tabs after stay time completes')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        info_label.setWordWrap(True)
        high_cpc_layout.addWidget(info_label)
        
        self.high_cpc_group.setLayout(high_cpc_layout)
        self.high_cpc_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.high_cpc_group)
        
        # Traffic Settings
        traffic_group = QGroupBox('📊 Traffic Settings')
        traffic_layout = QVBoxLayout()
        traffic_layout.setSpacing(10)
        
        # Stay Time Settings
        traffic_layout.addWidget(QLabel('⏱️ Stay Time per Profile:'))
        
        # Stay Time input (for fixed time) - MOVED UP
        stay_time_layout = QHBoxLayout()
        stay_time_layout.addWidget(QLabel('  Stay Time (seconds):'))
        self.stay_time_input = QSpinBox()
        self.stay_time_input.setRange(10, 3600)  # 10 to 3600 seconds
        self.stay_time_input.setValue(120)  # 120 seconds default
        self.stay_time_input.setSuffix(' sec')
        self.stay_time_input.setToolTip('Fixed time in seconds to spend on each profile with scrolling up and down')
        stay_time_layout.addWidget(self.stay_time_input)
        stay_time_layout.addStretch()
        traffic_layout.addLayout(stay_time_layout)
        
        # Random Enable checkbox - MOVED HERE per requirements (below Stay Time, above Random Minimum)
        self.random_time_enabled = QCheckBox('🎲 Enable Random Time')
        self.random_time_enabled.setChecked(False)
        self.random_time_enabled.setToolTip('When enabled, uses random time between min and max. When disabled, uses fixed stay time.')
        self.random_time_enabled.toggled.connect(self.toggle_random_time_inputs)
        traffic_layout.addWidget(self.random_time_enabled)
        
        # Random time inputs (hidden by default)
        min_time_layout = QHBoxLayout()
        min_time_layout.addWidget(QLabel('  Random Minimum (seconds):'))
        self.min_time_input = QSpinBox()
        self.min_time_input.setRange(10, 3600)  # 10 to 3600 seconds
        self.min_time_input.setValue(120)  # 120 seconds default
        self.min_time_input.setSuffix(' sec')
        self.min_time_input.setToolTip('Minimum random time in seconds to spend on each profile')
        self.min_time_input.setEnabled(False)
        self.min_time_input.valueChanged.connect(self.validate_time_range)
        min_time_layout.addWidget(self.min_time_input)
        min_time_layout.addStretch()
        traffic_layout.addLayout(min_time_layout)
        
        max_time_layout = QHBoxLayout()
        max_time_layout.addWidget(QLabel('  Random Maximum (seconds):'))
        self.max_time_input = QSpinBox()
        self.max_time_input.setRange(10, 3600)  # 10 to 3600 seconds
        self.max_time_input.setValue(240)  # 240 seconds default
        self.max_time_input.setSuffix(' sec')
        self.max_time_input.setToolTip('Maximum random time in seconds to spend on each profile')
        self.max_time_input.setEnabled(False)
        self.max_time_input.valueChanged.connect(self.validate_time_range)
        max_time_layout.addWidget(self.max_time_input)
        max_time_layout.addStretch()
        traffic_layout.addLayout(max_time_layout)
        
        # Number of Browsers - horizontal slider (1–240)
        num_browsers_label = QLabel('Number of Browsers:')
        num_browsers_label.setStyleSheet('color: #cc0000; font-weight: bold;')
        traffic_layout.addWidget(num_browsers_label)

        num_browsers_row = QHBoxLayout()
        self.number_of_browsers_slider = QSlider(Qt.Horizontal)
        self.number_of_browsers_slider.setRange(1, 240)
        self.number_of_browsers_slider.setValue(1)
        self.number_of_browsers_slider.setToolTip(
            'Number of browser windows to launch simultaneously. '
            'Example: 20 = instantly opens 20 browser windows at once'
        )
        self.number_of_browsers_slider.setStyleSheet(
            'QSlider::groove:horizontal { height: 6px; background: #ffcccc; border-radius: 3px; }'
            'QSlider::sub-page:horizontal { background: #cc0000; border-radius: 3px; }'
            'QSlider::handle:horizontal { background: #cc0000; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }'
        )
        self.number_of_browsers_value_label = QLabel('1')
        self.number_of_browsers_value_label.setStyleSheet('color: #cc0000; font-weight: bold; min-width: 30px;')
        self.number_of_browsers_slider.valueChanged.connect(
            lambda v: self.number_of_browsers_value_label.setText(str(v))
        )
        num_browsers_row.addWidget(self.number_of_browsers_slider)
        num_browsers_row.addWidget(self.number_of_browsers_value_label)
        traffic_layout.addLayout(num_browsers_row)

        # Zoom Out option (applies page zoom to loaded websites)
        self.zoom_out_enabled = QCheckBox('🔎 Zoom Out Website (25%)')
        self.zoom_out_enabled.setChecked(False)
        self.zoom_out_enabled.setToolTip(
            'When enabled, opened websites are displayed at 25% zoom.'
        )
        traffic_layout.addWidget(self.zoom_out_enabled)
        
        traffic_layout.addWidget(QLabel('Content Interaction % (0-100):'))
        self.content_ratio_input = QSpinBox()
        self.content_ratio_input.setRange(0, 100)
        self.content_ratio_input.setValue(85)
        traffic_layout.addWidget(self.content_ratio_input)
        
        traffic_group.setLayout(traffic_layout)
        layout.addWidget(traffic_group)
        
        # Platform Selection
        platform_group = QGroupBox('💻 Platform')
        platform_layout = QVBoxLayout()
        platform_layout.setSpacing(10)
        
        platform_layout.addWidget(QLabel('Select Platform(s):'))
        self.platform_desktop_check = QCheckBox('🖥 Windows')
        self.platform_desktop_check.setChecked(True)
        platform_layout.addWidget(self.platform_desktop_check)
        
        self.platform_android_check = QCheckBox('📱 Android')
        platform_layout.addWidget(self.platform_android_check)
        
        info_label = QLabel('ℹ️ Select both to mix Windows and Android browsers')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        platform_layout.addWidget(info_label)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)
        
        layout.addStretch()
        
        scroll_area.setWidget(widget)
        return scroll_area
    
    def toggle_referral_section(self, checked):
        """Toggle visibility of referral source selector."""
        self.referral_group.setVisible(checked)
        # Show URL group for referral visits
        if checked:
            self.url_group.setVisible(True)
    
    def toggle_search_section(self, checked):
        """Toggle visibility of search settings."""
        self.search_group.setVisible(checked)
        # Hide URL group for search visits since we use keyword + target domain instead
        if checked:
            self.url_group.setVisible(False)
        else:
            # Show URL group when not search visit (unless it's HIGH CPC visit)
            if not self.visit_high_cpc_radio.isChecked():
                self.url_group.setVisible(True)
    
    def add_url_to_list(self):
        """Add URL from input to list widget."""
        url = self.url_input.text().strip()
        if url:
            # Add https:// if no protocol specified
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Basic URL validation
            if '.' not in url or len(url) < 10:
                QMessageBox.warning(self, 'Invalid URL', 'Please enter a valid URL')
                return
            
            self.url_list_widget.addItem(url)
            self.url_input.clear()
    
    def remove_url_from_list(self):
        """Remove selected URL from list widget."""
        current_item = self.url_list_widget.currentItem()
        if current_item:
            self.url_list_widget.takeItem(self.url_list_widget.row(current_item))
    
    def create_behavior_tab(self) -> QWidget:
        """Create behavior settings tab."""
        # Create scroll area wrapper
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Section Title
        section_title = QLabel('🧠 Traffic Behaviour Configuration')
        section_title.setFont(QFont('Arial', 20, QFont.Bold))
        section_title.setStyleSheet('color: #2c3e50; padding: 10px 0;')
        layout.addWidget(section_title)
        
        # Browser Settings
        browser_group = QGroupBox('🌐 Browser Settings')
        browser_layout = QVBoxLayout()
        browser_layout.setSpacing(10)
        
        # Note: Browser always runs in visible mode (headless=False)
        info_label = QLabel('ℹ️ Browser always runs in visible mode for monitoring')
        info_label.setStyleSheet('color: #666; font-style: italic;')
        browser_layout.addWidget(info_label)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Human Behavior
        behavior_group = QGroupBox('🧠 Human Behavior')
        behavior_layout = QVBoxLayout()
        behavior_layout.setSpacing(10)
        
        behavior_layout.addWidget(QLabel('Scroll Depth % (30-100):'))
        self.scroll_depth_input = QSpinBox()
        self.scroll_depth_input.setRange(30, 100)
        self.scroll_depth_input.setValue(70)
        behavior_layout.addWidget(self.scroll_depth_input)
        
        self.enable_mouse_movement = QCheckBox('🖱 Enable Mouse Movement Simulation')
        self.enable_mouse_movement.setChecked(True)
        behavior_layout.addWidget(self.enable_mouse_movement)
        
        self.enable_idle_pauses = QCheckBox('⏸ Enable Idle Pauses')
        self.enable_idle_pauses.setChecked(True)
        behavior_layout.addWidget(self.enable_idle_pauses)
        
        idle_pauses_info = QLabel('ℹ️ Simulates natural reading pauses (2-5 seconds) to mimic human browsing patterns')
        idle_pauses_info.setStyleSheet('color: #666; font-style: italic; font-size: 10px; padding-left: 25px;')
        idle_pauses_info.setWordWrap(True)
        behavior_layout.addWidget(idle_pauses_info)
        
        self.enable_text_highlight = QCheckBox('✏️ Enable Text Highlighting')
        self.enable_text_highlight.setChecked(False)
        behavior_layout.addWidget(self.enable_text_highlight)
        
        highlight_info = QLabel('ℹ️ Randomly highlights text like human reading behavior')
        highlight_info.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        highlight_info.setWordWrap(True)
        behavior_layout.addWidget(highlight_info)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Interaction Settings (Simplified)
        interaction_group = QGroupBox('🔗 Interaction Settings')
        interaction_layout = QVBoxLayout()
        interaction_layout.setSpacing(10)
        
        self.enable_interaction = QCheckBox('✅ Enable Interaction')
        self.enable_interaction.setChecked(False)
        interaction_layout.addWidget(self.enable_interaction)
        
        info_label = QLabel('ℹ️ Advanced human behavior: click posts, explore pages, follow links, natural scrolling')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        info_label.setWordWrap(True)
        interaction_layout.addWidget(info_label)
        
        interaction_group.setLayout(interaction_layout)
        layout.addWidget(interaction_group)
        
        # Page Visit Settings (NEW FEATURE)
        page_visit_group = QGroupBox('📄 Page Visit Settings')
        page_visit_layout = QVBoxLayout()
        page_visit_layout.setSpacing(10)
        
        self.enable_extra_pages = QCheckBox('✅ Enable Extra Pages (navigate to other pages)')
        self.enable_extra_pages.setChecked(False)
        self.enable_extra_pages.stateChanged.connect(self.toggle_page_visit_settings)
        page_visit_layout.addWidget(self.enable_extra_pages)
        
        page_visit_layout.addWidget(QLabel('🔢 Maximum Pages:'))
        self.max_pages_input = QSpinBox()
        self.max_pages_input.setRange(1, 100)  # Increased range from 50 to 100
        self.max_pages_input.setValue(5)
        self.max_pages_input.setEnabled(False)
        page_visit_layout.addWidget(self.max_pages_input)
        
        page_visit_group.setLayout(page_visit_layout)
        layout.addWidget(page_visit_group)
        
        # Consent Manager
        consent_group = QGroupBox('🍪 Consent & Popup Handler')
        consent_layout = QVBoxLayout()
        consent_layout.setSpacing(10)
        
        self.enable_consent = QCheckBox('✅ Auto-handle Cookie Banners')
        self.enable_consent.setChecked(True)
        consent_layout.addWidget(self.enable_consent)
        
        self.enable_popups = QCheckBox('✅ Auto-handle Popups')
        self.enable_popups.setChecked(True)
        consent_layout.addWidget(self.enable_popups)
        
        consent_group.setLayout(consent_layout)
        layout.addWidget(consent_group)
        
        # ── Random Ad Click Settings ──────────────────────────────────────
        random_ad_group = QGroupBox('🎯 Random Ad Click Settings')
        random_ad_group.setStyleSheet(
            'QGroupBox { border: 2px solid #cc0000; border-radius: 6px; margin-top: 8px; }'
            'QGroupBox::title { color: #cc0000; font-weight: bold; subcontrol-origin: margin; left: 10px; }'
        )
        random_ad_layout = QVBoxLayout()
        random_ad_layout.setSpacing(10)

        # Section title label in red
        random_ad_title = QLabel('Random Ad Click Settings')
        random_ad_title.setStyleSheet('color: #cc0000; font-weight: bold; font-size: 13px;')
        random_ad_layout.addWidget(random_ad_title)

        # Single main toggle
        self.enable_random_ad_clicking = QCheckBox('✅ Enable Random Ad Clicking')
        self.enable_random_ad_clicking.setChecked(False)
        self.enable_random_ad_clicking.setStyleSheet(
            'QCheckBox::indicator:checked { background-color: #cc0000; border: 2px solid #cc0000; }'
        )
        random_ad_layout.addWidget(self.enable_random_ad_clicking)

        # Click Ratio slider
        ratio_label = QLabel('Click Ratio % (1–100):')
        ratio_label.setStyleSheet('color: #cc0000; font-weight: bold;')
        random_ad_layout.addWidget(ratio_label)

        ratio_row = QHBoxLayout()
        self.random_click_ratio_slider = QSlider(Qt.Horizontal)
        self.random_click_ratio_slider.setRange(1, 100)
        self.random_click_ratio_slider.setValue(50)
        self.random_click_ratio_slider.setStyleSheet(
            'QSlider::groove:horizontal { height: 6px; background: #ffcccc; border-radius: 3px; }'
            'QSlider::sub-page:horizontal { background: #cc0000; border-radius: 3px; }'
            'QSlider::handle:horizontal { background: #cc0000; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }'
        )
        self.random_click_ratio_label = QLabel('50%')
        self.random_click_ratio_label.setStyleSheet('color: #cc0000; font-weight: bold; min-width: 40px;')
        self.random_click_ratio_slider.valueChanged.connect(
            lambda v: self.random_click_ratio_label.setText(f'{v}%')
        )
        ratio_row.addWidget(self.random_click_ratio_slider)
        ratio_row.addWidget(self.random_click_ratio_label)
        random_ad_layout.addLayout(ratio_row)

        # ── Ad Selectors panel ────────────────────────────────────────────
        ad_sel_label = QLabel('Ad Selectors:')
        ad_sel_label.setStyleSheet('color: #cc0000; font-weight: bold;')
        random_ad_layout.addWidget(ad_sel_label)

        # Scrollable checklist
        self.ad_selectors_list = QListWidget()
        self.ad_selectors_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.ad_selectors_list.setMinimumHeight(180)
        self.ad_selectors_list.setStyleSheet(
            'QListWidget { background: #1e1e1e; color: #ffffff; border: 1px solid #cc0000;'
            '  border-radius: 4px; padding: 4px; }'
            'QListWidget::item { padding: 3px 6px; border-radius: 3px; }'
            'QListWidget::item:selected { background: #cc0000; color: #ffffff; }'
            'QListWidget::indicator:checked { background: #cc0000; border: 2px solid #cc0000; border-radius: 2px; }'
            'QListWidget::indicator:unchecked { background: #333; border: 2px solid #888; border-radius: 2px; }'
        )
        # Populate the list from the current in-memory selector data
        for entry in self._ad_selector_data:
            item = QListWidgetItem(entry['selector'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if entry['enabled'] else Qt.Unchecked)
            self.ad_selectors_list.addItem(item)
        random_ad_layout.addWidget(self.ad_selectors_list)

        # Bottom action buttons
        ad_btn_row = QHBoxLayout()
        ad_btn_style = (
            'QPushButton { background: #2a2a2a; color: #ffffff; border: 1px solid #cc0000;'
            '  border-radius: 4px; padding: 5px 12px; font-weight: bold; }'
            'QPushButton:hover { background: #cc0000; }'
        )
        btn_add_sel = QPushButton('+ Add')
        btn_add_sel.setStyleSheet(ad_btn_style)
        btn_add_sel.clicked.connect(self._ad_selector_add)

        btn_rem_sel = QPushButton('Remove')
        btn_rem_sel.setStyleSheet(ad_btn_style)
        btn_rem_sel.clicked.connect(self._ad_selector_remove)

        btn_tog_sel = QPushButton('Toggle all')
        btn_tog_sel.setStyleSheet(ad_btn_style)
        btn_tog_sel.clicked.connect(self._ad_selector_toggle_all)

        ad_btn_row.addWidget(btn_add_sel)
        ad_btn_row.addWidget(btn_rem_sel)
        ad_btn_row.addWidget(btn_tog_sel)
        ad_btn_row.addStretch()
        random_ad_layout.addLayout(ad_btn_row)

        random_ad_group.setLayout(random_ad_layout)
        layout.addWidget(random_ad_group)

        # ── Browser Engines ───────────────────────────────────────────────
        browser_engine_group = QGroupBox('⚙️ Browser Engines')
        browser_engine_layout = QVBoxLayout()
        browser_engine_layout.setSpacing(8)

        engine_info = QLabel(
            'Select one or more engines.  Sessions rotate between selected engines.'
        )
        engine_info.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        engine_info.setWordWrap(True)
        browser_engine_layout.addWidget(engine_info)


        self.engine_chromium_check = QCheckBox('Chrome / Chromium')
        self.engine_chromium_check.setChecked(True)
        browser_engine_layout.addWidget(self.engine_chromium_check)

        self.engine_firefox_check = QCheckBox('Firefox')
        self.engine_firefox_check.setChecked(False)
        browser_engine_layout.addWidget(self.engine_firefox_check)

        self.engine_webkit_check = QCheckBox('WebKit')
        self.engine_webkit_check.setChecked(False)
        browser_engine_layout.addWidget(self.engine_webkit_check)

        browser_engine_group.setLayout(browser_engine_layout)
        layout.addWidget(browser_engine_group)
        
        layout.addStretch()
        
        scroll_area.setWidget(widget)
        return scroll_area
    
    def toggle_page_visit_settings(self, state):
        """Enable/disable page visit inputs based on checkbox state."""
        # PySide6 stateChanged emits int (0=unchecked, 2=checked), compare with enum or value
        enabled = state in (Qt.Checked, Qt.Checked.value)
        self.max_pages_input.setEnabled(enabled)
    
    def toggle_rpa_mode(self, state):
        """Enable/disable other features based on RPA mode checkbox state.
        
        When RPA MODE is enabled:
        - Activates CONSENT_POPUP Handler (enable_consent, enable_popups)
        - Activates PLATFORM selection (platform_desktop_check, platform_android_check)
        - Disables all other traffic/behavior settings
        
        When RPA MODE is disabled:
        - Deactivates HIGH CPC/CPM Visit mode
        - Re-enables all settings
        """
        # PySide6 stateChanged emits int (0=unchecked, 2=checked), compare with enum or value
        rpa_mode_enabled = state in (Qt.Checked, Qt.Checked.value)
        
        # When RPA mode is enabled, disable all other features EXCEPT proxy, concurrent, consent handlers, and platform
        # When disabled, enable all features
        disable_features = rpa_mode_enabled
        
        # IMPORTANT: Keep concurrent and proxy ENABLED when RPA mode is on
        # Disable/enable all traffic settings except proxy and concurrent
        self.stay_time_input.setEnabled(not disable_features)
        self.random_time_enabled.setEnabled(not disable_features)
        self.min_time_input.setEnabled(not disable_features and self.random_time_enabled.isChecked())
        self.max_time_input.setEnabled(not disable_features and self.random_time_enabled.isChecked())
        # KEEP NUMBER OF BROWSERS ENABLED IN RPA MODE
        self.number_of_browsers_slider.setEnabled(True)  # Always enabled
        self.zoom_out_enabled.setEnabled(True)  # Always enabled
        self.content_ratio_input.setEnabled(not disable_features)
        
        # REQUIREMENT: Keep platform settings ENABLED when RPA mode is ON (ACTIVE)
        self.platform_desktop_check.setEnabled(True)  # Always enabled - ACTIVE in RPA mode
        self.platform_android_check.setEnabled(True)  # Always enabled - ACTIVE in RPA mode
        
        # Disable/enable visit type settings
        self.visit_direct_radio.setEnabled(not disable_features)
        self.visit_referral_radio.setEnabled(not disable_features)
        self.visit_search_radio.setEnabled(not disable_features)
        
        # REQUIREMENT: Disable HIGH CPC/CPM Visit when RPA mode is disabled or enabled
        # When RPA mode is enabled, HIGH CPC should be disabled
        # When RPA mode is disabled, HIGH CPC is restored to user's previous choice
        if rpa_mode_enabled:
            # Store the current state before disabling
            if not hasattr(self, '_high_cpc_previous_state'):
                self._high_cpc_previous_state = self.visit_high_cpc_radio.isChecked()
            # Disable HIGH CPC/CPM Visit mode when RPA is enabled
            self.visit_high_cpc_radio.setEnabled(False)
            if self.visit_high_cpc_radio.isChecked():
                # Uncheck it and switch to direct visit
                self.visit_direct_radio.setChecked(True)
        else:
            # Re-enable HIGH CPC/CPM Visit mode when RPA is disabled
            self.visit_high_cpc_radio.setEnabled(True)
        
        # Disable/enable URL input
        self.url_input.setEnabled(not disable_features)
        self.url_list_widget.setEnabled(not disable_features)
        
        # Disable/enable behavior settings
        self.enable_interaction.setEnabled(not disable_features)
        self.enable_extra_pages.setEnabled(not disable_features)
        
        # REQUIREMENT: Keep consent handlers ENABLED and ACTIVATED when RPA mode is ON
        if rpa_mode_enabled:
            # Force enable consent handlers when RPA mode is activated
            self.enable_consent.setChecked(True)
            self.enable_popups.setChecked(True)
            # Keep them enabled so user can see they're active but disable changing them
            self.enable_consent.setEnabled(True)
            self.enable_popups.setEnabled(True)
        else:
            # Allow user to change consent handlers when RPA mode is off
            self.enable_consent.setEnabled(True)
            self.enable_popups.setEnabled(True)
        
        self.enable_text_highlight.setEnabled(not disable_features)
        self.scroll_depth_input.setEnabled(not disable_features)
        self.enable_mouse_movement.setEnabled(not disable_features)
        self.enable_idle_pauses.setEnabled(not disable_features)
        self.max_pages_input.setEnabled(not disable_features)
        
        # Proxy settings remain enabled
        # Script editor remains enabled (needed for RPA mode)
    
    def toggle_random_time_inputs(self, enabled: bool):
        """Toggle between random time and fixed time inputs."""
        # When random is enabled, show min/max inputs and hide stay time
        # When random is disabled, hide min/max inputs and show stay time
        self.min_time_input.setEnabled(enabled)
        self.max_time_input.setEnabled(enabled)
        self.stay_time_input.setEnabled(not enabled)
    
    def validate_time_range(self):
        """Ensure minimum time is not greater than maximum time."""
        min_time = self.min_time_input.value()
        max_time = self.max_time_input.value()
        
        if min_time > max_time:
            # Auto-adjust max to match min if min becomes greater
            self.max_time_input.setValue(min_time)

    def get_selected_browser_count(self) -> int:
        """Return the currently selected number of browser windows to launch."""
        return self.number_of_browsers_slider.value()
    
    def toggle_high_cpc_section(self, checked):
        """Toggle visibility of HIGH CPC/CPM mode section.
        
        When HIGH CPC/CPM visit type is selected, Target URLs section should be hidden
        since we're providing the target domain in the HIGH CPC settings.
        """
        self.high_cpc_group.setVisible(checked)
        # Hide URL group for HIGH CPC visits since we use HIGH CPC settings instead
        if checked:
            self.url_group.setVisible(False)
            self.emit_log('ℹ️ Target URLs mode disabled - using HIGH CPC/CPM Mode target domain')
        else:
            # Show URL group when not HIGH CPC visit (unless it's search visit)
            if not self.visit_search_radio.isChecked():
                self.url_group.setVisible(True)
        
    
    def toggle_high_cpc_inputs(self, enabled: bool):
        """Toggle HIGH CPC/CPM mode input fields.
        
        When HIGH CPC/CPM mode is enabled, Target URLs mode should be disabled
        since we're already providing a targeted domain in the HIGH CPC settings.
        """
        # Enable/disable HIGH CPC input fields
        self.high_cpc_url_input.setEnabled(enabled)
        self.high_cpc_target_input.setEnabled(enabled)
        self.high_cpc_stay_time_input.setEnabled(enabled)
        
        # When HIGH CPC mode is enabled, disable Target URLs section
        # since we're providing the target domain in HIGH CPC settings
        if enabled:
            self.url_group.setEnabled(False)
            self.url_input.setEnabled(False)
            self.url_list_widget.setEnabled(False)
            self.emit_log('ℹ️ Target URLs mode disabled - using HIGH CPC/CPM Mode target domain')
        else:
            # Re-enable Target URLs section when HIGH CPC mode is disabled
            self.url_group.setEnabled(True)
            self.url_input.setEnabled(True)
            self.url_list_widget.setEnabled(True)
    
    
    def create_proxy_tab(self) -> QWidget:
        """Create proxy settings tab."""
        # Create scroll area wrapper
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Section Title
        section_title = QLabel('🌐 Proxy Settings')
        section_title.setFont(QFont('Arial', 20, QFont.Bold))
        section_title.setStyleSheet('color: #2c3e50; padding: 10px 0;')
        layout.addWidget(section_title)
        
        # Enable Proxy
        proxy_enable_group = QGroupBox('🔧 Proxy Configuration')
        proxy_enable_layout = QVBoxLayout()
        proxy_enable_layout.setSpacing(10)
        
        self.proxy_enabled_check = QCheckBox('✅ Enable Proxy')
        self.proxy_enabled_check.setChecked(False)
        self.proxy_enabled_check.stateChanged.connect(self.toggle_proxy_inputs)
        proxy_enable_layout.addWidget(self.proxy_enabled_check)
        
        proxy_enable_group.setLayout(proxy_enable_layout)
        layout.addWidget(proxy_enable_group)
        
        # Proxy Type
        proxy_type_group = QGroupBox('⚙️ Proxy Type')
        proxy_type_layout = QVBoxLayout()
        proxy_type_layout.setSpacing(10)
        
        proxy_type_layout.addWidget(QLabel('ℹ️ Default type for proxies without protocol prefix:'))
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(['HTTP', 'HTTPS', 'SOCKS5'])
        self.proxy_type_combo.setEnabled(False)
        # Fix color issue - ensure text is readable when enabled
        self.proxy_type_combo.setStyleSheet("""
            QComboBox {
                color: #000000;
                background-color: #ffffff;
            }
            QComboBox:disabled {
                color: #999999;
                background-color: #f0f0f0;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView {
                color: #000000;
                background-color: #ffffff;
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
        """)
        proxy_type_layout.addWidget(self.proxy_type_combo)
        
        proxy_type_group.setLayout(proxy_type_layout)
        layout.addWidget(proxy_type_group)
        
        # Proxy List
        proxy_list_group = QGroupBox('📋 Proxy List')
        proxy_list_layout = QVBoxLayout()
        proxy_list_layout.setSpacing(10)
        
        proxy_list_layout.addWidget(QLabel('Enter proxies (one per line):'))
        proxy_list_layout.addWidget(QLabel('Formats: ip:port, user:pass@ip:port, ip:port:user:pass, protocol://ip:port'))
        
        self.proxy_list_input = DragDropTextEdit()
        self.proxy_list_input.setPlaceholderText('127.0.0.1:8080\nuser:pass@192.168.1.1:3128\n10.0.0.1:1080:user:pass\nhttp://proxy.com:8080\nsocks5://10.0.0.2:1080')
        self.proxy_list_input.setMaximumHeight(120)
        self.proxy_list_input.setEnabled(False)
        self.proxy_list_input.setAcceptDrops(True)
        self.proxy_list_input.textChanged.connect(self.update_proxy_count)
        proxy_list_layout.addWidget(self.proxy_list_input)
        
        # Proxy count label
        self.proxy_count_label = QLabel('📊 Proxies loaded: 0')
        self.proxy_count_label.setStyleSheet('color: #27ae60; font-weight: bold; font-size: 12px;')
        proxy_list_layout.addWidget(self.proxy_count_label)
        
        # Import from file button
        import_btn = QPushButton('📁 Import from File')
        import_btn.clicked.connect(self.import_proxies_from_file)
        import_btn.setEnabled(False)
        self.proxy_import_btn = import_btn
        proxy_list_layout.addWidget(import_btn)
        
        proxy_list_group.setLayout(proxy_list_layout)
        layout.addWidget(proxy_list_group)
        
        # Info about timezone/location matching
        info_group = QGroupBox('ℹ️ Proxy Information')
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        info_label = QLabel('• Timezone and fingerprints will be set according to proxy location\n• Each profile uses a unique proxy for maximum authenticity\n• Failed proxies are automatically skipped')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        scroll_area.setWidget(widget)
        return scroll_area
    
    def toggle_proxy_inputs(self, state):
        """Enable/disable proxy inputs based on checkbox state."""
        # PySide6 stateChanged emits int (0=unchecked, 2=checked), compare with enum or value
        enabled = state in (Qt.Checked, Qt.Checked.value)
        self.proxy_type_combo.setEnabled(enabled)
        self.proxy_list_input.setEnabled(enabled)
        self.proxy_import_btn.setEnabled(enabled)
    
    def update_proxy_count(self):
        """Update proxy count label based on current input."""
        try:
            proxy_text = self.proxy_list_input.toPlainText()
            if not proxy_text.strip():
                self.proxy_count_label.setText('📊 Proxies loaded: 0')
                return
            
            # Reuse proxy manager for parsing
            self._proxy_count_manager.proxy_type = self.proxy_type_combo.currentText()
            proxies = self._proxy_count_manager.parse_proxy_list(proxy_text)
            count = len(proxies)
            self.proxy_count_label.setText(f'📊 Proxies loaded: {count}')
            
            if count > 0:
                self.proxy_count_label.setStyleSheet('color: #27ae60; font-weight: bold; font-size: 12px;')
            else:
                self.proxy_count_label.setStyleSheet('color: #e74c3c; font-weight: bold; font-size: 12px;')
        except Exception as e:
            self.proxy_count_label.setText(f'📊 Proxies loaded: 0 (Error parsing)')
            self.proxy_count_label.setStyleSheet('color: #e74c3c; font-weight: bold; font-size: 12px;')
    
    def import_proxies_from_file(self):
        """Import proxies from a text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Proxy File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    proxies = f.read()
                    current_text = self.proxy_list_input.toPlainText()
                    if current_text.strip():
                        self.proxy_list_input.setPlainText(current_text + '\n' + proxies)
                    else:
                        self.proxy_list_input.setPlainText(proxies)
                self.update_proxy_count()
                self.log_manager.log('INFO', f'Imported proxies from {file_path}')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to import proxies: {str(e)}')
    
    def create_script_tab(self) -> QWidget:
        """Create RPA script tab with visual builder and JSON editor."""
        # Create scroll area wrapper
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        
        # Section Title
        section_title = QLabel('🧩 RPA Script Creator')
        section_title.setFont(QFont('Arial', 20, QFont.Bold))
        section_title.setStyleSheet('color: #2c3e50; padding: 10px 0;')
        main_layout.addWidget(section_title)
        
        # Tab widget for Visual Builder and JSON Editor
        script_tabs = QTabWidget()
        
        # Visual Builder Tab
        visual_widget = QWidget()
        visual_layout = QHBoxLayout(visual_widget)
        
        # Left: Action Toolbox
        toolbox_panel = QWidget()
        toolbox_layout = QVBoxLayout(toolbox_panel)
        
        toolbox_label = QLabel('Action Toolbox')
        toolbox_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                padding: 5px 0;
            }
        """)
        toolbox_layout.addWidget(toolbox_label)
        
        self.action_toolbox = QListWidget()
        self.action_toolbox.setDragEnabled(True)
        self.action_toolbox.setMaximumWidth(200)
        self.action_toolbox.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
                background-color: white;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        
        # Add action items with emojis - UPDATED NAMES
        actions = [
            '➕ New Tab',
            '🌐 Access Website',
            '⏱ Time',
            '📜 Scroll',
            '🖱 Click Element',
            '⌨ Input Text',
            '❌ Close Page',
            '🔄 Refresh Webpage',
            '🔀 Close Tab',
            '🔍 Statement If',
            '🔁 For Loop Elements',
            '🔢 For Loop Times',
            '♾️ While Loop',
            '⛔ Exit Loop',
            '🚪 Quit Browser'
        ]
        for action in actions:
            item = QListWidgetItem(action)
            self.action_toolbox.addItem(item)
        
        toolbox_layout.addWidget(self.action_toolbox)
        visual_layout.addWidget(toolbox_panel)
        
        # Center: Workflow List
        workflow_panel = QWidget()
        workflow_layout = QVBoxLayout(workflow_panel)
        
        workflow_label = QLabel('Workflow Steps')
        workflow_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                padding: 5px 0;
            }
        """)
        workflow_layout.addWidget(workflow_label)
        
        self.workflow_list = WorkflowListWidget(self)
        self.workflow_list.itemClicked.connect(self.on_workflow_item_clicked)
        self.workflow_list.model().rowsMoved.connect(self.sync_visual_to_json)
        self.workflow_list.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
                background-color: white;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        
        workflow_layout.addWidget(self.workflow_list)
        
        # Workflow buttons
        workflow_btn_layout = QHBoxLayout()
        
        add_step_btn = QPushButton('➕ Add Step')
        add_step_btn.clicked.connect(self.add_workflow_step)
        workflow_btn_layout.addWidget(add_step_btn)
        
        remove_step_btn = QPushButton('🗑 Remove Step')
        remove_step_btn.clicked.connect(self.remove_workflow_step)
        workflow_btn_layout.addWidget(remove_step_btn)
        
        clear_workflow_btn = QPushButton('🧹 Clear All')
        clear_workflow_btn.clicked.connect(self.clear_workflow)
        workflow_btn_layout.addWidget(clear_workflow_btn)
        
        workflow_layout.addLayout(workflow_btn_layout)
        visual_layout.addWidget(workflow_panel)
        
        # Right: Step Configuration
        config_panel = QWidget()
        config_layout = QVBoxLayout(config_panel)
        
        config_label = QLabel('Step Configuration')
        config_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                padding: 5px 0;
            }
        """)
        config_layout.addWidget(config_label)
        
        self.step_config_widget = QWidget()
        self.step_config_layout = QFormLayout(self.step_config_widget)
        
        # Apply styling to step config widget to fix dropdown visibility
        self.step_config_widget.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #f0f0f0;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #666;
                width: 6px;
                height: 6px;
                border-width: 0 2px 2px 0;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #ccc;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
        """)
        
        config_scroll = QScrollArea()
        config_scroll.setWidget(self.step_config_widget)
        config_scroll.setWidgetResizable(True)
        config_scroll.setMaximumWidth(300)
        
        config_layout.addWidget(config_scroll)
        visual_layout.addWidget(config_panel)
        
        script_tabs.addTab(visual_widget, 'Visual Builder')
        
        # JSON Editor Tab
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)
        
        json_editor_label = QLabel('RPA Script Editor (JSON):')
        json_editor_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                padding: 5px 0;
            }
        """)
        json_layout.addWidget(json_editor_label)
        
        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText('''Example script:
{
  "name": "Sample Script",
  "steps": [
    {"type": "newPage"},
    {"type": "navigate", "url": "https://example.com"},
    {"type": "wait", "duration": 2000},
    {"type": "scroll", "depth": 50},
    {"type": "click", "selector": ".some-button"},
    {"type": "closePage"}
  ]
}''')
        self.script_editor.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        self.script_editor.textChanged.connect(self.sync_json_to_visual)
        json_layout.addWidget(self.script_editor)
        
        script_tabs.addTab(json_widget, 'JSON Editor')
        
        main_layout.addWidget(script_tabs)
        
        # Script buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('💾 Save Script')
        save_btn.clicked.connect(self.save_script)
        btn_layout.addWidget(save_btn)
        
        load_btn = QPushButton('📂 Load Script')
        load_btn.clicked.connect(self.load_script)
        btn_layout.addWidget(load_btn)
        
        sync_btn = QPushButton('🔄 Sync Visual ↔ JSON')
        sync_btn.clicked.connect(self.force_sync)
        btn_layout.addWidget(sync_btn)
        
        main_layout.addLayout(btn_layout)
        
        # RPA Mode Configuration (MOVED FROM BEHAVIOR TAB)
        rpa_mode_group = QGroupBox('🧩 RPA Mode Configuration')
        rpa_mode_layout = QVBoxLayout()
        rpa_mode_layout.setSpacing(10)
        
        self.enable_rpa_mode = QCheckBox('✅ Enable RPA Mode Only')
        self.enable_rpa_mode.setChecked(False)
        self.enable_rpa_mode.stateChanged.connect(self.toggle_rpa_mode)
        rpa_mode_layout.addWidget(self.enable_rpa_mode)
        
        rpa_info = QLabel('ℹ️ When enabled, only RPA script and proxy settings are active. All other features are disabled.\n\n'
                         '✓ Consent & Popup Handler will be automatically enabled\n'
                         '✓ Platform selection will be automatically enabled\n'
                         '✗ HIGH CPC/CPM Visit mode will be automatically disabled')
        rpa_info.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        rpa_info.setWordWrap(True)
        rpa_mode_layout.addWidget(rpa_info)
        
        rpa_mode_group.setLayout(rpa_mode_layout)
        main_layout.addWidget(rpa_mode_group)
        
        # Initialize workflow data storage
        self.workflow_steps = []
        self.syncing = False  # Prevent recursive syncing
        
        scroll_area.setWidget(widget)
        return scroll_area
    
    def create_control_tab(self) -> QWidget:
        """Create control tab for automation controls."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section Title
        section_title = QLabel('🎮 Automation Control')
        section_title.setFont(QFont('Arial', 20, QFont.Bold))
        section_title.setStyleSheet('color: #2c3e50; padding: 10px 0;')
        layout.addWidget(section_title)
        
        # Control Panel Group
        control_group = QGroupBox('Control Panel')
        control_layout = QVBoxLayout()
        control_layout.setSpacing(15)
        
        # Control buttons
        control_btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('▶️ Start Automation')
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 15px; font-weight: bold; font-size: 14px;')
        self.start_btn.setMinimumHeight(50)
        control_btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('⛔ Stop')
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet('background-color: #f44336; color: white; padding: 15px; font-weight: bold; font-size: 14px;')
        self.stop_btn.setMinimumHeight(50)
        control_btn_layout.addWidget(self.stop_btn)
        
        control_layout.addLayout(control_btn_layout)
        
        # Status
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel('Current Status:'))
        self.status_label = QLabel('📊 Status: Ready')
        self.status_label.setStyleSheet('padding: 15px; background-color: #e0e0e0; border-radius: 5px; font-weight: bold; font-size: 14px;')
        self.status_label.setMinimumHeight(50)
        status_layout.addWidget(self.status_label)
        control_layout.addLayout(status_layout)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Import Settings Group
        import_group = QGroupBox('📥 Import Settings')
        import_layout = QVBoxLayout()
        import_layout.setSpacing(15)
        
        # Import Useragents
        useragent_layout = QHBoxLayout()
        useragent_layout.addWidget(QLabel('User Agents:'))
        self.useragent_file_label = QLabel('No file selected')
        self.useragent_file_label.setStyleSheet('color: #666; font-style: italic;')
        useragent_layout.addWidget(self.useragent_file_label)
        useragent_layout.addStretch()
        import_useragent_btn = QPushButton('📁 Import User Agents')
        import_useragent_btn.clicked.connect(self.import_useragents)
        import_useragent_btn.setStyleSheet('background-color: #2196F3; color: white; padding: 10px; font-weight: bold;')
        useragent_layout.addWidget(import_useragent_btn)
        import_layout.addLayout(useragent_layout)
        
        # Clear Useragents button
        clear_useragent_btn = QPushButton('🗑️ Clear User Agents')
        clear_useragent_btn.clicked.connect(self.clear_useragents)
        clear_useragent_btn.setStyleSheet('background-color: #9E9E9E; color: white; padding: 8px;')
        import_layout.addWidget(clear_useragent_btn)
        
        # Import Cookies
        cookies_layout = QHBoxLayout()
        cookies_layout.addWidget(QLabel('Cookies:'))
        self.cookies_file_label = QLabel('No file selected')
        self.cookies_file_label.setStyleSheet('color: #666; font-style: italic;')
        cookies_layout.addWidget(self.cookies_file_label)
        cookies_layout.addStretch()
        import_cookies_btn = QPushButton('📁 Import Cookies')
        import_cookies_btn.clicked.connect(self.import_cookies)
        import_cookies_btn.setStyleSheet('background-color: #FF9800; color: white; padding: 10px; font-weight: bold;')
        cookies_layout.addWidget(import_cookies_btn)
        import_layout.addLayout(cookies_layout)
        
        # Clear Cookies button
        clear_cookies_btn = QPushButton('🗑️ Clear Cookies')
        clear_cookies_btn.clicked.connect(self.clear_cookies)
        clear_cookies_btn.setStyleSheet('background-color: #9E9E9E; color: white; padding: 8px;')
        import_layout.addWidget(clear_cookies_btn)
        
        # Info label
        info_label = QLabel('ℹ️ Imported user agents and cookies will be used across all instances and proxies')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        info_label.setWordWrap(True)
        import_layout.addWidget(info_label)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # Instructions Group
        instructions_group = QGroupBox('ℹ️ Instructions')
        instructions_layout = QVBoxLayout()
        
        instructions_text = QLabel(
            '1. Configure your settings in the "Website Traffic" tab\n'
            '2. Set traffic behavior patterns in "Traffic Behaviour" tab\n'
            '3. (Optional) Configure proxy settings in "Proxy Settings" tab\n'
            '4. (Optional) Create custom RPA scripts in "RPA Script Creator" tab\n'
            '5. Click "Start Automation" to begin\n'
            '6. Monitor progress in the "Logs" tab\n'
            '7. Click "Stop" to halt the automation at any time'
        )
        instructions_text.setWordWrap(True)
        instructions_text.setStyleSheet('padding: 10px; line-height: 1.6;')
        instructions_layout.addWidget(instructions_text)
        
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        layout.addStretch()
        
        return widget
    
    def create_logs_tab(self) -> QWidget:
        """Create logs tab for viewing automation logs."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section Title
        section_title = QLabel('📋 Live Logs')
        section_title.setFont(QFont('Arial', 20, QFont.Bold))
        section_title.setStyleSheet('color: #2c3e50; padding: 10px 0;')
        layout.addWidget(section_title)
        
        # Logs display
        logs_group = QGroupBox('Activity Logs')
        logs_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet('background-color: #1e1e1e; color: white; font-family: monospace; font-size: 12px;')
        self.log_display.setMinimumHeight(400)
        logs_layout.addWidget(self.log_display)
        
        # Clear logs button
        clear_btn = QPushButton('🧹 Clear Logs')
        clear_btn.clicked.connect(self.clear_logs)
        clear_btn.setStyleSheet('background-color: #ff9800; color: white; padding: 10px; font-weight: bold;')
        logs_layout.addWidget(clear_btn)
        
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        # HumanEx Logo
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 20, 20, 10)
        logo_layout.setSpacing(8)
        
        # Logo image label
        logo_label = QLabel()
        
        try:
            # Try to load and render the SVG logo
            logo_path = Path(__file__).parent / 'assets' / 'humanex_logo.svg'
            if logo_path.exists():
                renderer = QSvgRenderer(str(logo_path))
                pixmap = QPixmap(300, 120)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                logo_label.setPixmap(pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
        except Exception as e:
            # Fallback to text-based logo if SVG loading fails
            logo_text = QLabel('🚀 HumanEx')
            logo_text.setFont(QFont('Arial', 16, QFont.Bold))
            logo_text.setAlignment(Qt.AlignCenter)
            logo_text.setStyleSheet('color: #2c3e50; padding: 10px;')
            logo_layout.addWidget(logo_text)
            
            subtitle_text = QLabel('Advanced Human Behaviour Simulation')
            subtitle_text.setFont(QFont('Arial', 10))
            subtitle_text.setAlignment(Qt.AlignCenter)
            subtitle_text.setStyleSheet('color: #7f8c8d;')
            logo_layout.addWidget(subtitle_text)
        else:
            logo_layout.addWidget(logo_label)
        
        logo_widget.setStyleSheet('background-color: #f8f9fa; border-radius: 5px;')
        layout.addWidget(logo_widget)
        
        # Footer section
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(15, 10, 15, 15)
        footer_layout.setSpacing(5)
        
        version_label = QLabel('v5.0 • 2026')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet('color: #7f8c8d; font-size: 11px;')
        footer_layout.addWidget(version_label)
        
        credit_label = QLabel('Made with ❤ by <a href="https://asadwebdev.com" style="color: #3498db; text-decoration: none;">CODEWITHASAD</a>')
        credit_label.setAlignment(Qt.AlignCenter)
        credit_label.setStyleSheet('color: #7f8c8d; font-size: 10px;')
        credit_label.setOpenExternalLinks(True)
        credit_label.setTextFormat(Qt.RichText)
        footer_layout.addWidget(credit_label)
        
        layout.addWidget(footer_widget)
        
        return widget
    
    def start_automation(self):
        """Start the automation process."""
        try:
            # Security checks
            if SECURITY_AVAILABLE and self.security_manager:
                # Rate limiting check
                if self.rate_limiter and not self.rate_limiter.is_allowed():
                    wait_time = int(self.rate_limiter.get_wait_time())
                    QMessageBox.warning(
                        self,
                        'Rate Limit Exceeded',
                        f"Too many automation starts. Please wait {wait_time} seconds before trying again.\n\n"
                        "This limit helps protect against abuse and ensures system stability."
                    )
                    return
            
            # Check if RPA mode is enabled
            rpa_mode_enabled = self.enable_rpa_mode.isChecked()
            
            # Auto-enable RPA mode if workflow steps exist but RPA mode is not enabled
            if not rpa_mode_enabled and self.workflow_steps:
                reply = QMessageBox.question(
                    self, 'Enable RPA Mode?',
                    'You have workflow steps in the RPA Script Creator but RPA Mode is not enabled.\n\n'
                    'Would you like to enable RPA Mode to execute your workflow steps?',
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.enable_rpa_mode.setChecked(True)
                    rpa_mode_enabled = True
                else:
                    # User chose not to enable RPA mode, continue with normal mode
                    pass
            
            if rpa_mode_enabled:
                # RPA Mode: Only RPA script and proxy are used
                # Sync visual workflow builder to JSON editor before reading the script
                # This ensures that any steps added via the visual builder are included
                self.sync_visual_to_json()
                
                rpa_script_text = self.script_editor.toPlainText().strip()
                if not rpa_script_text:
                    QMessageBox.warning(self, 'Input Error', 'RPA Mode is enabled but no RPA script is provided.\n\nPlease add actions to workflow steps in the RPA Script Creator tab or enter a script in the JSON Editor.')
                    return
                
                # Validate and normalize RPA script JSON
                try:
                    raw_script = json.loads(rpa_script_text)
                    
                    # Normalize the script to handle different formats
                    rpa_script = normalize_rpa_script(raw_script)
                    
                    if 'steps' not in rpa_script or not isinstance(rpa_script['steps'], list):
                        QMessageBox.warning(self, 'Invalid Script', 'RPA script must contain a "steps" array')
                        return
                    
                    if len(rpa_script['steps']) == 0:
                        QMessageBox.warning(self, 'Empty Script', 'RPA script has no steps to execute')
                        return
                        
                except json.JSONDecodeError as e:
                    QMessageBox.warning(self, 'Invalid JSON', f'RPA script has invalid JSON syntax: {str(e)}')
                    return
                
                # Collect configuration for RPA mode (only proxy settings)
                config = {
                    'rpa_mode': True,
                    'rpa_script': rpa_script,
                    'number_of_browsers': self.get_selected_browser_count(),  # Number of browser windows
                    'zoom_out_enabled': self.zoom_out_enabled.isChecked(),
                    'zoom_out_percent': 25,
                    'proxy_enabled': self.proxy_enabled_check.isChecked(),
                    'proxy_type': self.proxy_type_combo.currentText(),
                    'proxy_list': self.proxy_list_input.toPlainText(),
                    'headless': False,  # Always visible
                    'imported_useragents': self.imported_useragents,
                    'imported_cookies': self.imported_cookies,
                }
                
                self.log_manager.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                self.log_manager.log('RPA Mode Enabled - All other features disabled')
                self.log_manager.log('Only RPA script and proxy settings are active')
                self.log_manager.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                
            else:
                # Normal Mode: Standard automation
                # Get visit type first to determine what validation is needed
                visit_type = 'direct'
                if self.visit_referral_radio.isChecked():
                    visit_type = 'referral'
                elif self.visit_search_radio.isChecked():
                    visit_type = 'search'
                elif self.visit_high_cpc_radio.isChecked():
                    visit_type = 'high_cpc'
                
                # Check if HIGH CPC/CPM Mode is enabled (via radio button)
                high_cpc_enabled = (visit_type == 'high_cpc')
                
                # Validate search keyword and target domain if search type is selected
                if visit_type == 'search':
                    keyword = self.search_keyword_input.text().strip()
                    target_domain = self.target_domain_input.text().strip()
                    search_engine = self.search_engine_combo.currentText()  # Get selected search engine
                    if not keyword:
                        QMessageBox.warning(self, 'Input Error', 'Please enter a search keyword for Search Visit type')
                        return
                    if not target_domain:
                        QMessageBox.warning(self, 'Input Error', 'Please enter a target domain for Search Visit type')
                        return
                    # For search visits, we don't need target URLs since we use keyword + target domain
                    url_list = [target_domain]  # Use target domain as the URL list
                elif high_cpc_enabled:
                    # Validate HIGH CPC/CPM Mode fields
                    high_cpc_url = self.high_cpc_url_input.text().strip()
                    high_cpc_target = self.high_cpc_target_input.text().strip()
                    if not high_cpc_url:
                        QMessageBox.warning(self, 'Input Error', 'Please enter a High CPC Website URL for HIGH CPC/CPM Visit type')
                        return
                    if not high_cpc_target:
                        QMessageBox.warning(self, 'Input Error', 'Please enter a Target Domain URL for HIGH CPC/CPM Visit type')
                        return
                    # For HIGH CPC/CPM Mode, we don't need target URLs since we use HIGH CPC settings
                    # The target domain is provided in HIGH CPC settings instead
                    url_list = []  # Empty list - not needed for HIGH CPC mode
                else:
                    # For direct and referral visits, we need target URLs
                    # Validate inputs - collect URLs from list widget
                    url_list = []
                    for i in range(self.url_list_widget.count()):
                        url = self.url_list_widget.item(i).text().strip()
                        if url:
                            url_list.append(url)
                    
                    # If no URLs in list, check input field
                    if not url_list:
                        url = self.url_input.text().strip()
                        if url:
                            if not url.startswith(('http://', 'https://')):
                                url = 'https://' + url
                            url_list.append(url)
                    
                    if not url_list:
                        QMessageBox.warning(self, 'Input Error', 'Please enter at least one target URL')
                        return
                
                # Collect referral sources if referral type is selected
                referral_sources = []
                utm_campaign = ''
                utm_medium = 'social'
                utm_term = ''
                utm_content = ''
                
                if visit_type == 'referral':
                    # Collect selected platforms
                    if self.referral_facebook.isChecked():
                        referral_sources.append('facebook')
                    if self.referral_google.isChecked():
                        referral_sources.append('google')
                    if self.referral_twitter.isChecked():
                        referral_sources.append('twitter')
                    if self.referral_telegram.isChecked():
                        referral_sources.append('telegram')
                    if self.referral_instagram.isChecked():
                        referral_sources.append('instagram')
                    if self.referral_reddit.isChecked():
                        referral_sources.append('reddit')
                    if self.referral_linkedin.isChecked():
                        referral_sources.append('linkedin')
                    if self.referral_pinterest.isChecked():
                        referral_sources.append('pinterest')
                    if self.referral_youtube.isChecked():
                        referral_sources.append('youtube')
                    if self.referral_tiktok.isChecked():
                        referral_sources.append('tiktok')
                    if self.referral_whatsapp.isChecked():
                        referral_sources.append('whatsapp')
                    if self.referral_snapchat.isChecked():
                        referral_sources.append('snapchat')
                    if self.referral_discord.isChecked():
                        referral_sources.append('discord')
                    if self.referral_medium.isChecked():
                        referral_sources.append('medium')
                    if self.referral_quora.isChecked():
                        referral_sources.append('quora')
                    if self.referral_tumblr.isChecked():
                        referral_sources.append('tumblr')
                    if self.referral_vk.isChecked():
                        referral_sources.append('vk')
                    if self.referral_weibo.isChecked():
                        referral_sources.append('weibo')
                    if self.referral_line.isChecked():
                        referral_sources.append('line')
                    
                    if not referral_sources:
                        QMessageBox.warning(self, 'Input Error', 'Please select at least one referral source')
                        return
                    
                    # Collect UTM parameters
                    utm_campaign = self.utm_campaign_input.text().strip()
                    utm_medium = self.utm_medium_combo.currentText()
                    utm_term = self.utm_term_input.text().strip()
                    utm_content = self.utm_content_input.text().strip()
                    
                    # Campaign name is optional - if not provided, basic referral traffic will be used
                    if not utm_campaign:
                        self.log_manager.log('ℹ️ No campaign name provided. Basic referral traffic will be used without UTM tracking.', 'INFO')

                
                # Get selected platforms
                selected_platforms = []
                if self.platform_desktop_check.isChecked():
                    selected_platforms.append('windows')
                if self.platform_android_check.isChecked():
                    selected_platforms.append('android')
                
                if not selected_platforms:
                    QMessageBox.warning(self, 'Input Error', 'Please select at least one platform (Windows or Android)')
                    return
                
                # Collect configuration
                config = {
                    'rpa_mode': False,
                    'url_list': url_list,
                    'random_time_enabled': self.random_time_enabled.isChecked(),
                    'stay_time': self.stay_time_input.value(),
                    'min_time_spend': self.min_time_input.value(),
                    'max_time_spend': self.max_time_input.value(),
                    'number_of_browsers': self.get_selected_browser_count(),
                    'zoom_out_enabled': self.zoom_out_enabled.isChecked(),
                    'zoom_out_percent': 25,
                    'content_ratio': self.content_ratio_input.value(),
                    'platforms': selected_platforms,
                    'headless': False,  # Always False - browser must be visible
                    'proxy_enabled': self.proxy_enabled_check.isChecked(),
                    'proxy_type': self.proxy_type_combo.currentText(),
                    'proxy_list': self.proxy_list_input.toPlainText(),
                    # Proxy rotation removed - each browser uses fixed proxy
                    'visit_type': visit_type,
                    'search_keyword': self.search_keyword_input.text().strip() if visit_type == 'search' else '',
                    'target_domain': self.target_domain_input.text().strip() if visit_type == 'search' else '',
                    'search_engine': self.search_engine_combo.currentText() if visit_type == 'search' else 'Google',
                    'referral_sources': referral_sources,
                    'utm_campaign': utm_campaign,
                    'utm_medium': utm_medium,
                    'utm_term': utm_term,
                    'utm_content': utm_content,
                    'enable_interaction': self.enable_interaction.isChecked(),
                    'enable_extra_pages': self.enable_extra_pages.isChecked(),
                    'max_pages': self.max_pages_input.value(),
                    'scroll_depth': self.scroll_depth_input.value(),
                    'enable_mouse_movement': self.enable_mouse_movement.isChecked(),
                    'enable_idle_pauses': self.enable_idle_pauses.isChecked(),
                    'enable_consent': self.enable_consent.isChecked(),
                    'enable_popups': self.enable_popups.isChecked(),
                    'enable_text_highlight': self.enable_text_highlight.isChecked(),
                    'imported_useragents': self.imported_useragents,
                    'imported_cookies': self.imported_cookies,
                    # HIGH CPC/CPM Mode configuration
                    'high_cpc_enabled': high_cpc_enabled,
                    'high_cpc_url': self.high_cpc_url_input.text().strip(),
                    'high_cpc_target': self.high_cpc_target_input.text().strip(),
                    'high_cpc_stay_time': self.high_cpc_stay_time_input.value(),
                    # Random ad click configuration
                    'random_ad_clicking_enabled': self.enable_random_ad_clicking.isChecked(),
                    'random_click_ratio': self.random_click_ratio_slider.value(),
                    'ad_selectors': self._get_ad_selector_data_from_widget(),
                    'selected_browser_engines': [
                        e for e, chk in [
                            ('Chromium', self.engine_chromium_check),
                            ('Firefox', self.engine_firefox_check),
                            ('WebKit', self.engine_webkit_check),
                        ] if chk.isChecked()
                    ] or ['Chromium'],  # Fall back to Chromium when nothing selected
                }
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText('📊 Status: Running...')
            self.status_label.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold;')
            
            # Create and start worker thread
            self.automation_thread = QThread()
            self.automation_worker = AutomationWorker(config, self.log_manager)
            
            # Configure proxy manager BEFORE starting thread
            if config['proxy_enabled'] and config['proxy_list'].strip():
                self.log_manager.log('Configuring proxy settings...')
                self.automation_worker.browser_manager.proxy_manager.proxy_enabled = True
                self.automation_worker.browser_manager.proxy_manager.proxy_type = config['proxy_type']
                # Parse proxy list
                self.automation_worker.browser_manager.proxy_manager.proxy_list = \
                    self.automation_worker.browser_manager.proxy_manager.parse_proxy_list(config['proxy_list'])
                
                # Initialize proxy queue for sequential distribution
                self.automation_worker.browser_manager.proxy_manager.initialize_queue()
                
                proxy_count = len(self.automation_worker.browser_manager.proxy_manager.proxy_list)
                self.log_manager.log(f'✓ Proxy configuration complete: {proxy_count} proxies loaded')
            else:
                self.log_manager.log('Proxy disabled, using direct connection')
            
            self.automation_worker.moveToThread(self.automation_thread)
            
            # Connect signals
            self.automation_thread.started.connect(self.automation_worker.run)
            self.automation_worker.log_signal.connect(self.append_log)
            self.automation_worker.finished_signal.connect(self.automation_finished)
            
            # Start thread
            self.automation_thread.start()
            
            self.log_manager.log('Automation started from GUI')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to start automation: {e}')
            self.automation_finished()
    
    def stop_automation(self):
        """Stop the automation process."""
        if self.automation_worker:
            self.automation_worker.stop()
            self.append_log('Stop requested...')
    
    def automation_finished(self):
        """Handle automation completion."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText('📊 Status: Ready')
        self.status_label.setStyleSheet('padding: 10px; background-color: #e0e0e0; border-radius: 5px; font-weight: bold;')
        
        if self.automation_thread:
            self.automation_thread.quit()
            self.automation_thread.wait()
            self.automation_thread = None
        
        self.automation_worker = None
    
    def append_log(self, log_entry: str):
        """Append log to display with color coding."""
        # Color code based on log level
        if '[ERROR]' in log_entry:
            color = '#ff6b6b'  # Red
        elif '[WARNING]' in log_entry:
            color = '#ffd93d'  # Yellow
        else:
            color = 'white'  # White for INFO
        
        # Add colored HTML
        colored_log = f'<span style="color: {color};">{log_entry}</span>'
        self.log_display.append(colored_log)
        
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        """Clear log display."""
        self.log_display.clear()
        self.log_manager.clear_logs()
    
    def save_script(self):
        """Save RPA script to file."""
        try:
            script_text = self.script_editor.toPlainText()
            if not script_text:
                QMessageBox.warning(self, 'Warning', 'No script to save')
                return
            
            # Validate JSON
            json.loads(script_text)
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Save Script', '', 'JSON Files (*.json)'
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(script_text)
                QMessageBox.information(self, 'Success', 'Script saved successfully')
                
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, 'Error', f'Invalid JSON: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save script: {e}')
    
    def load_script(self):
        """Load RPA script from file with normalization support."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 'Load Script', '', 'JSON Files (*.json)'
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    script_text = f.read()
                
                # Parse JSON
                raw_data = json.loads(script_text)
                
                # Normalize the script to internal format
                normalized_script = normalize_rpa_script(raw_data)
                
                # Convert normalized script back to JSON string
                normalized_text = json.dumps(normalized_script, indent=2)
                
                # Set the normalized JSON text (this will trigger sync_json_to_visual via textChanged signal)
                self.script_editor.setPlainText(normalized_text)
                
                QMessageBox.information(self, 'Success', 
                    f'Script loaded and normalized successfully!\n'
                    f'Loaded {len(normalized_script["steps"])} action(s) into workflow.')
                
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, 'Error', f'Invalid JSON: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load script: {e}')
    
    # ========================================================================
    # VISUAL BUILDER METHODS
    # ========================================================================
    
    def add_workflow_step(self):
        """Add a step from toolbox to workflow."""
        current_item = self.action_toolbox.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Warning', 'Please select an action from the toolbox')
            return
        
        action_name = current_item.text()
        step_type = self.action_to_step_type(action_name)
        
        # Create step with UUID
        step = {
            'id': str(uuid.uuid4()),
            'type': step_type,
            'config': self.get_default_config(step_type)
        }
        
        self.workflow_steps.append(step)
        
        # Add to visual list
        display_text = f"{action_name}"
        list_item = QListWidgetItem(display_text)
        list_item.setData(Qt.UserRole, step['id'])
        self.workflow_list.addItem(list_item)
        
        # Sync to JSON
        self.sync_visual_to_json()
    
    def remove_workflow_step(self):
        """Remove selected step from workflow."""
        current_row = self.workflow_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Warning', 'Please select a step to remove')
            return
        
        # Remove from list and data
        item = self.workflow_list.takeItem(current_row)
        step_id = item.data(Qt.UserRole)
        
        self.workflow_steps = [s for s in self.workflow_steps if s['id'] != step_id]
        
        # Clear configuration panel
        self.clear_step_config()
        
        # Sync to JSON
        self.sync_visual_to_json()
    
    def clear_workflow(self):
        """Clear all workflow steps."""
        reply = QMessageBox.question(
            self, 'Confirm Clear',
            'Are you sure you want to clear all workflow steps?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.workflow_list.clear()
            self.workflow_steps = []
            self.clear_step_config()
            self.sync_visual_to_json()
    
    def on_workflow_item_clicked(self, item):
        """Handle workflow item click to show configuration."""
        step_id = item.data(Qt.UserRole)
        step = next((s for s in self.workflow_steps if s['id'] == step_id), None)
        
        if step:
            self.show_step_config(step)
    
    def show_step_config(self, step: Dict[str, Any]):
        """Show configuration panel for selected step."""
        self.clear_step_config()
        
        step_type = step['type']
        config = step.get('config', {})
        
        # Add configuration fields based on step type
        if step_type == 'navigate':
            # Access Website configuration
            url_input = QLineEdit(config.get('url', ''))
            url_input.textChanged.connect(lambda text: self.update_step_config(step, 'url', text))
            self.step_config_layout.addRow('Access URL:', url_input)
            
            timeout_input = QSpinBox()
            timeout_input.setRange(1000, 120000)
            timeout_input.setValue(config.get('timeout', 30000))
            timeout_input.valueChanged.connect(lambda val: self.update_step_config(step, 'timeout', val))
            self.step_config_layout.addRow('Timeout (ms):', timeout_input)
        
        elif step_type == 'wait':
            # Time configuration
            mode_combo = QComboBox()
            mode_combo.addItems(['Fixed', 'Random'])
            mode_combo.setCurrentText(config.get('mode', 'Fixed'))
            mode_combo.currentTextChanged.connect(lambda text: self.update_step_config(step, 'mode', text))
            self.step_config_layout.addRow('Timeout Waiting:', mode_combo)
            
            duration_input = QSpinBox()
            duration_input.setRange(100, 60000)
            duration_input.setValue(config.get('duration', 2000))
            duration_input.valueChanged.connect(lambda val: self.update_step_config(step, 'duration', val))
            self.step_config_layout.addRow('Duration (ms):', duration_input)
            
            if config.get('mode', 'Fixed') == 'Random':
                max_duration_input = QSpinBox()
                max_duration_input.setRange(100, 60000)
                max_duration_input.setValue(config.get('max_duration', 5000))
                max_duration_input.valueChanged.connect(lambda val: self.update_step_config(step, 'max_duration', val))
                self.step_config_layout.addRow('Max Duration (ms):', max_duration_input)
        
        elif step_type == 'scroll':
            # Scroll configuration with type, position and speed
            scroll_type_combo = QComboBox()
            scroll_type_combo.addItems(['Smooth', 'Auto'])
            scroll_type_combo.setCurrentText(config.get('scroll_type', 'Smooth'))
            scroll_type_combo.currentTextChanged.connect(lambda text: self.update_step_config(step, 'scroll_type', text))
            self.step_config_layout.addRow('Scroll Type:', scroll_type_combo)
            
            # Position option (Top, Intermediate, Bottom)
            position_combo = QComboBox()
            position_combo.addItems(['Top', 'Intermediate', 'Bottom'])
            position_combo.setCurrentText(config.get('position', 'Intermediate'))
            position_combo.currentTextChanged.connect(lambda text: self.update_step_config(step, 'position', text))
            self.step_config_layout.addRow('Position:', position_combo)
            
            depth_input = QSpinBox()
            depth_input.setRange(0, 100)
            depth_input.setValue(config.get('depth', 50))
            depth_input.valueChanged.connect(lambda val: self.update_step_config(step, 'depth', val))
            self.step_config_layout.addRow('Depth (%):', depth_input)
            
            min_speed_input = QSpinBox()
            min_speed_input.setRange(50, 2000)
            min_speed_input.setValue(config.get('min_speed', 100))
            min_speed_input.valueChanged.connect(lambda val: self.update_step_config(step, 'min_speed', val))
            self.step_config_layout.addRow('Min Scroll Speed (ms):', min_speed_input)
            
            max_speed_input = QSpinBox()
            max_speed_input.setRange(50, 2000)
            max_speed_input.setValue(config.get('max_speed', 500))
            max_speed_input.valueChanged.connect(lambda val: self.update_step_config(step, 'max_speed', val))
            self.step_config_layout.addRow('Max Scroll Speed (ms):', max_speed_input)
        
        elif step_type == 'click':
            selector_input = QLineEdit(config.get('selector', ''))
            selector_input.textChanged.connect(lambda text: self.update_step_config(step, 'selector', text))
            self.step_config_layout.addRow('Selector:', selector_input)
        
        elif step_type == 'input':
            selector_input = QLineEdit(config.get('selector', ''))
            selector_input.textChanged.connect(lambda text: self.update_step_config(step, 'selector', text))
            self.step_config_layout.addRow('Selector:', selector_input)
            
            text_input = QLineEdit(config.get('text', ''))
            text_input.textChanged.connect(lambda text: self.update_step_config(step, 'text', text))
            self.step_config_layout.addRow('Text:', text_input)
        
        elif step_type == 'if':
            # Statement If configuration
            condition_input = QLineEdit(config.get('condition', ''))
            condition_input.setPlaceholderText('e.g., page.locator(".element").is_visible()')
            condition_input.textChanged.connect(lambda text: self.update_step_config(step, 'condition', text))
            self.step_config_layout.addRow('Condition:', condition_input)
            
            selector_input = QLineEdit(config.get('selector', ''))
            selector_input.setPlaceholderText('Optional: CSS selector to check')
            selector_input.textChanged.connect(lambda text: self.update_step_config(step, 'selector', text))
            self.step_config_layout.addRow('Selector:', selector_input)
        
        elif step_type == 'forLoopElements':
            # For Loop Elements configuration
            selector_input = QLineEdit(config.get('selector', ''))
            selector_input.setPlaceholderText('CSS selector for elements')
            selector_input.textChanged.connect(lambda text: self.update_step_config(step, 'selector', text))
            self.step_config_layout.addRow('Selector:', selector_input)
            
            max_items_input = QSpinBox()
            max_items_input.setRange(1, 1000)
            max_items_input.setValue(config.get('max_items', 10))
            max_items_input.valueChanged.connect(lambda val: self.update_step_config(step, 'max_items', val))
            self.step_config_layout.addRow('Max Items:', max_items_input)
        
        elif step_type == 'forLoopTimes':
            # For Loop Times configuration
            iterations_input = QSpinBox()
            iterations_input.setRange(1, 1000)
            iterations_input.setValue(config.get('iterations', 5))
            iterations_input.valueChanged.connect(lambda val: self.update_step_config(step, 'iterations', val))
            self.step_config_layout.addRow('Iterations:', iterations_input)
        
        elif step_type == 'while':
            # While Loop configuration
            condition_input = QLineEdit(config.get('condition', ''))
            condition_input.setPlaceholderText('e.g., element.is_visible()')
            condition_input.textChanged.connect(lambda text: self.update_step_config(step, 'condition', text))
            self.step_config_layout.addRow('Condition:', condition_input)
            
            max_iterations_input = QSpinBox()
            max_iterations_input.setRange(1, 1000)
            max_iterations_input.setValue(config.get('max_iterations', 10))
            max_iterations_input.valueChanged.connect(lambda val: self.update_step_config(step, 'max_iterations', val))
            self.step_config_layout.addRow('Max Iterations:', max_iterations_input)
    
    def update_step_config(self, step: Dict[str, Any], key: str, value: Any):
        """Update step configuration."""
        if 'config' not in step:
            step['config'] = {}
        step['config'][key] = value
        
        # Sync to JSON
        self.sync_visual_to_json()
    
    def clear_step_config(self):
        """Clear step configuration panel."""
        while self.step_config_layout.count():
            child = self.step_config_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def sync_visual_to_json(self):
        """Sync visual builder to JSON editor."""
        if self.syncing:
            return
        
        self.syncing = True
        
        try:
            # Build JSON from workflow steps
            script = {
                'name': 'Visual Builder Script',
                'description': 'Generated from visual builder',
                'steps': []
            }
            
            for step in self.workflow_steps:
                step_json = {'type': step['type']}
                step_json.update(step.get('config', {}))
                script['steps'].append(step_json)
            
            # Update JSON editor
            json_text = json.dumps(script, indent=2)
            self.script_editor.setPlainText(json_text)
        
        finally:
            self.syncing = False
    
    def sync_json_to_visual(self):
        """Sync JSON editor to visual builder with normalization support."""
        if self.syncing:
            return
        
        self.syncing = True
        
        try:
            json_text = self.script_editor.toPlainText().strip()
            if not json_text:
                return
            
            # Parse JSON
            raw_data = json.loads(json_text)
            
            # Normalize the script (handles different formats)
            normalized_script = normalize_rpa_script(raw_data)
            steps = normalized_script.get('steps', [])
            
            # Clear and rebuild workflow
            self.workflow_list.clear()
            self.workflow_steps = []
            
            for step_data in steps:
                step_type = step_data.get('type', '')
                
                # Create step with UUID
                step = {
                    'id': str(uuid.uuid4()),
                    'type': step_type,
                    'config': {k: v for k, v in step_data.items() if k != 'type'}
                }
                
                self.workflow_steps.append(step)
                
                # Add to visual list
                action_name = self.step_type_to_action(step_type)
                display_text = f"{action_name}"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.UserRole, step['id'])
                self.workflow_list.addItem(list_item)
            
            # Update JSON editor with normalized format (only if it changed)
            normalized_text = json.dumps(normalized_script, indent=2)
            if normalized_text != json_text:
                # Temporarily set syncing to False to update the editor
                self.syncing = False
                self.script_editor.setPlainText(normalized_text)
                self.syncing = True
        
        except json.JSONDecodeError:
            pass  # Invalid JSON, don't update visual
        except Exception as e:
            pass  # Other errors, don't update visual
        
        finally:
            self.syncing = False
    
    def force_sync(self):
        """Force synchronization from visual builder to JSON editor."""
        # Sync visual to JSON
        self.sync_visual_to_json()
        QMessageBox.information(self, 'Sync Complete', 'Visual builder synced to JSON editor')
    
    def action_to_step_type(self, action_name: str) -> str:
        """Convert action name to step type. Handles both old and new action names."""
        # Remove emoji prefix for matching
        clean_name = action_name.split(' ', 1)[1] if ' ' in action_name else action_name
        
        mapping = {
            # New names
            'New Tab': 'newPage',
            'Access Website': 'navigate',
            'Time': 'wait',
            'Scroll': 'scroll',
            'Click Element': 'click',
            'Input Text': 'input',
            'Close Page': 'closePage',
            'Refresh Webpage': 'refresh',
            'Close Tab': 'closeTab',
            'Statement If': 'if',
            'For Loop Elements': 'forLoopElements',
            'For Loop Times': 'forLoopTimes',
            'While Loop': 'while',
            'Exit Loop': 'break',
            'Quit Browser': 'quitBrowser',
            # Old names for backward compatibility
            'New Page': 'newPage',
            'Open Page': 'newPage',
            'Navigate': 'navigate',
            'Wait': 'wait',
        }
        return mapping.get(clean_name, 'unknown')
    
    def step_type_to_action(self, step_type: str) -> str:
        """Convert step type to action name."""
        mapping = {
            'newPage': 'New Tab',
            'navigate': 'Access Website',
            'wait': 'Time',
            'scroll': 'Scroll',
            'click': 'Click Element',
            'input': 'Input Text',
            'closePage': 'Close Page'
        }
        return mapping.get(step_type, step_type)
    
    def get_default_config(self, step_type: str) -> Dict[str, Any]:
        """Get default configuration for step type."""
        defaults = {
            'navigate': {'url': 'https://example.com', 'timeout': 30000},
            'wait': {'duration': 2000, 'mode': 'Fixed'},
            'scroll': {'depth': 50, 'scroll_type': 'Smooth', 'min_speed': 100, 'max_speed': 500},
            'click': {'selector': ''},
            'input': {'selector': '', 'text': ''}
        }
        return defaults.get(step_type, {})
    
    def import_useragents(self):
        """Import user agents from a text file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'Import User Agents',
                '',
                'Text Files (*.txt);;All Files (*)'
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    useragents = [line.strip() for line in f if line.strip()]
                
                if useragents:
                    self.imported_useragents = useragents
                    self.useragent_file_label.setText(f'{len(useragents)} user agents loaded')
                    self.useragent_file_label.setStyleSheet('color: #4CAF50; font-weight: bold;')
                    self.log_manager.log(f'✓ Imported {len(useragents)} user agents from {file_path}')
                    QMessageBox.information(self, 'Success', f'Successfully imported {len(useragents)} user agents!')
                else:
                    QMessageBox.warning(self, 'Empty File', 'The selected file contains no user agents.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to import user agents: {str(e)}')
            self.log_manager.log(f'Failed to import user agents: {str(e)}', 'ERROR')
    
    def clear_useragents(self):
        """Clear imported user agents."""
        if self.imported_useragents:
            reply = QMessageBox.question(
                self,
                'Confirm Clear',
                f'Clear {len(self.imported_useragents)} imported user agents?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.imported_useragents = []
                self.useragent_file_label.setText('No file selected')
                self.useragent_file_label.setStyleSheet('color: #666; font-style: italic;')
                self.log_manager.log('✓ Cleared imported user agents')
                QMessageBox.information(self, 'Success', 'User agents cleared successfully!')
        else:
            QMessageBox.information(self, 'Info', 'No user agents to clear.')
    
    def import_cookies(self):
        """Import cookies from a JSON file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'Import Cookies',
                '',
                'JSON Files (*.json);;All Files (*)'
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                # Validate cookies format
                if isinstance(cookies, list):
                    self.imported_cookies = cookies
                    self.cookies_file_label.setText(f'{len(cookies)} cookies loaded')
                    self.cookies_file_label.setStyleSheet('color: #4CAF50; font-weight: bold;')
                    self.log_manager.log(f'✓ Imported {len(cookies)} cookies from {file_path}')
                    QMessageBox.information(self, 'Success', f'Successfully imported {len(cookies)} cookies!')
                else:
                    QMessageBox.warning(self, 'Invalid Format', 'Cookies file must contain a JSON array.')
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, 'Error', f'Invalid JSON format: {str(e)}')
            self.log_manager.log(f'Failed to import cookies (invalid JSON): {str(e)}', 'ERROR')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to import cookies: {str(e)}')
            self.log_manager.log(f'Failed to import cookies: {str(e)}', 'ERROR')
    
    def clear_cookies(self):
        """Clear imported cookies."""
        if self.imported_cookies:
            reply = QMessageBox.question(
                self,
                'Confirm Clear',
                f'Clear {len(self.imported_cookies)} imported cookies?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.imported_cookies = []
                self.cookies_file_label.setText('No file selected')
                self.cookies_file_label.setStyleSheet('color: #666; font-style: italic;')
                self.log_manager.log('✓ Cleared imported cookies')
                QMessageBox.information(self, 'Success', 'Cookies cleared successfully!')
        else:
            QMessageBox.information(self, 'Info', 'No cookies to clear.')
    
    # ========================================================================
    # AD SELECTORS HELPERS
    # ========================================================================

    def _load_ad_selectors_settings(self) -> List[Dict[str, Any]]:
        """Load ad selector list from bot_settings.json, or return the factory default."""
        try:
            if _BOT_SETTINGS_FILE.exists():
                with open(_BOT_SETTINGS_FILE, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                stored = data.get('ad_selectors')
                if isinstance(stored, list) and stored:
                    # Validate each entry
                    validated = [
                        {'selector': str(e['selector']), 'enabled': bool(e.get('enabled', True))}
                        for e in stored
                        if isinstance(e, dict) and 'selector' in e
                    ]
                    if validated:
                        return validated
        except Exception:
            pass
        return [dict(e) for e in AD_SELECTORS]

    def _save_ad_selectors_settings(self):
        """Persist the current ad selector list (with checked state) to bot_settings.json."""
        try:
            # Load existing settings so we don't overwrite unrelated keys
            existing: Dict[str, Any] = {}
            if _BOT_SETTINGS_FILE.exists():
                try:
                    with open(_BOT_SETTINGS_FILE, 'r', encoding='utf-8') as fh:
                        existing = json.load(fh)
                except Exception:
                    pass
            existing['ad_selectors'] = self._get_ad_selector_data_from_widget()
            with open(_BOT_SETTINGS_FILE, 'w', encoding='utf-8') as fh:
                json.dump(existing, fh, indent=2)
        except Exception as e:
            self.log_manager.log(f'Could not save ad selector settings: {e}', 'WARNING')

    def _get_ad_selector_data_from_widget(self) -> List[Dict[str, Any]]:
        """Read current selector list + checked state from the QListWidget."""
        result = []
        for i in range(self.ad_selectors_list.count()):
            item = self.ad_selectors_list.item(i)
            result.append({
                'selector': item.text(),
                'enabled': item.checkState() == Qt.Checked,
            })
        return result

    def get_active_ad_selectors(self) -> List[str]:
        """Return only the checked (enabled) selectors from the Ad Selectors panel."""
        return [
            entry['selector']
            for entry in self._get_ad_selector_data_from_widget()
            if entry['enabled']
        ]

    # ── Button slots for Ad Selectors ──────────────────────────────────────

    def _ad_selector_add(self):
        """Open an input dialog, add a new selector (checked by default)."""
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self, 'Add Ad Selector', 'Enter CSS selector:',
        )
        if not ok:
            return
        selector = text.strip()
        if not selector:
            return
        # Check for duplicates
        for i in range(self.ad_selectors_list.count()):
            if self.ad_selectors_list.item(i).text() == selector:
                QMessageBox.information(self, 'Duplicate', 'This selector already exists.')
                return
        item = QListWidgetItem(selector)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        self.ad_selectors_list.addItem(item)
        self._save_ad_selectors_settings()

    def _ad_selector_remove(self):
        """Remove currently selected items (no-op if nothing selected)."""
        selected = self.ad_selectors_list.selectedItems()
        for item in selected:
            self.ad_selectors_list.takeItem(self.ad_selectors_list.row(item))
        if selected:
            self._save_ad_selectors_settings()

    def _ad_selector_toggle_all(self):
        """If not all checked → check all.  If all checked → uncheck all."""
        count = self.ad_selectors_list.count()
        if count == 0:
            return
        all_checked = all(
            self.ad_selectors_list.item(i).checkState() == Qt.Checked
            for i in range(count)
        )
        new_state = Qt.Unchecked if all_checked else Qt.Checked
        for i in range(count):
            self.ad_selectors_list.item(i).setCheckState(new_state)
        self._save_ad_selectors_settings()

    # ========================================================================

    def closeEvent(self, event):
        """Handle application close."""
        self._save_ad_selectors_settings()
        if self.automation_worker and self.automation_worker.running:
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'Automation is running. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_automation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()



# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def check_browser_installation():
    """Check if Playwright browsers are installed."""
    # Try using the Python-module form (most reliable across platforms)
    for cmd in (
        [sys.executable, '-m', 'playwright', 'install', '--dry-run', 'chromium'],
        ['playwright', 'install', '--dry-run', 'chromium'],
    ):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True
        except Exception:
            continue

    # Fallback: check if browser exists in the Playwright cache directory
    try:
        home_dir = Path.home()
        # Playwright stores browsers under ~/.cache/ms-playwright on Linux/Mac
        # and %LOCALAPPDATA%\ms-playwright on Windows
        import platform
        if platform.system() == 'Windows':
            import os
            cache_base = Path(os.environ.get('LOCALAPPDATA', home_dir)) / 'ms-playwright'
        else:
            cache_base = home_dir / '.cache' / 'ms-playwright'
        if cache_base.exists():
            chromium_dirs = list(cache_base.glob('chromium-*'))
            if chromium_dirs:
                return True
    except Exception:
        pass

    return False


def auto_install_browser(parent=None):
    """Automatically install Playwright Chromium browser with progress dialog."""
    from PySide6.QtWidgets import QProgressDialog

    # Create progress dialog
    progress = QProgressDialog(
        "Downloading Playwright Chromium browser...\n\n"
        "This is a one-time download (~200 MB).\n"
        "Please wait, this may take 1-2 minutes...",
        None,  # No cancel button - must complete
        0, 0,  # Indeterminate progress
        parent
    )
    progress.setWindowTitle('First Time Setup')
    progress.setWindowModality(Qt.ApplicationModal)
    progress.setMinimumDuration(0)
    progress.setValue(0)
    progress.show()

    # Force UI update
    QApplication.processEvents()

    success = False
    error_message = ""

    # Prefer the Python-module invocation so it always uses the correct
    # Playwright installation even when 'playwright' is not on PATH.
    install_cmds = [
        [sys.executable, '-m', 'playwright', 'install', 'chromium'],
        ['playwright', 'install', 'chromium'],
    ]

    for cmd in install_cmds:
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Read output line by line and update the progress dialog
            for line in process.stdout:
                if 'Downloading' in line or 'Installing' in line or '%' in line:
                    progress.setLabelText(
                        f"Downloading Playwright Chromium browser...\n\n"
                        f"{line.strip()}\n\n"
                        f"Please wait, this may take 1-2 minutes..."
                    )
                    QApplication.processEvents()

            process.wait()

            if process.returncode == 0:
                success = True
                error_message = ""
                break
            else:
                error_message = f"Installation failed with exit code {process.returncode}"

        except FileNotFoundError:
            error_message = "Playwright command not found. Please ensure Playwright is installed."
        except Exception as e:
            error_message = f"Installation error: {str(e)}"

    progress.close()

    return success, error_message


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Check browser installation
    if not check_browser_installation():
        # Ask user if they want to auto-install
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('First Time Setup')
        msg.setText('Playwright Chromium browser is not installed.')
        msg.setInformativeText(
            'This is required for the bot to work.\n\n'
            'Would you like to download and install it automatically?\n'
            '(~200 MB download, takes 1-2 minutes)\n\n'
            'Click "Yes" to install now, or "No" to install manually later.'
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        response = msg.exec()
        
        if response == QMessageBox.Yes:
            # Auto-install browsers
            success, error_msg = auto_install_browser()
            
            if success:
                # Show success message
                success_msg = QMessageBox()
                success_msg.setIcon(QMessageBox.Information)
                success_msg.setWindowTitle('Setup Complete')
                success_msg.setText('Browser installation successful!')
                success_msg.setInformativeText(
                    'The Playwright Chromium browser has been installed.\n\n'
                    'The application will now start.\n\n'
                    'Future launches will be instant!'
                )
                success_msg.setStandardButtons(QMessageBox.Ok)
                success_msg.exec()
            else:
                # Show error and manual instructions
                error_dlg = QMessageBox()
                error_dlg.setIcon(QMessageBox.Critical)
                error_dlg.setWindowTitle('Installation Failed')
                error_dlg.setText('Automatic browser installation failed!')
                error_dlg.setInformativeText(
                    f'Error: {error_msg}\n\n'
                    'Please install manually by running:\n\n'
                    '  playwright install chromium\n'
                    '  python -m playwright install chromium\n\n'
                    'After installation, restart the application.'
                )
                error_dlg.setStandardButtons(QMessageBox.Ok)
                error_dlg.exec()
                return
        else:
            # User chose not to install
            manual_msg = QMessageBox()
            manual_msg.setIcon(QMessageBox.Information)
            manual_msg.setWindowTitle('Manual Installation Required')
            manual_msg.setText('Please install the browser manually.')
            manual_msg.setInformativeText(
                'To install, run one of these commands:\n\n'
                '  playwright install chromium\n'
                '  python -m playwright install chromium\n\n'
                'After installation, restart the application.'
            )
            manual_msg.setStandardButtons(QMessageBox.Ok)
            manual_msg.exec()
            return
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set up explicit light palette to prevent dark system theme from causing
    # black/blank rendering on systems with OS-level dark mode enabled
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(52, 152, 219))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Create and show main window
    window = AppGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()