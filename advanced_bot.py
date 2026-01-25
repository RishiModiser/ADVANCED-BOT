#!/usr/bin/env python3
"""
Windows Desktop Automation System
Enterprise-grade RPA software for UX testing, sponsored content simulation,
and traffic behavior research.

⚠️ IMPORTANT: This system MUST NOT click real third-party ad networks.
"""

import sys
import json
import random
import time
import logging
import asyncio
import uuid
import subprocess
import shutil
import platform
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum

# Check for required dependencies before importing them
def check_dependencies():
    """Check if required packages are installed and provide helpful error messages."""
    missing_packages = []
    
    try:
        import PySide6
    except ImportError:
        missing_packages.append('PySide6')
    
    try:
        import playwright
    except ImportError:
        missing_packages.append('playwright')
    
    if missing_packages:
        print("\n" + "="*70)
        print("ERROR: Missing Required Dependencies")
        print("="*70)
        print(f"\nThe following packages are not installed: {', '.join(missing_packages)}")
        print("\nTo fix this issue, please run:")
        print("\n    pip install -r requirements.txt")
        print("\nThis will install all required dependencies including:")
        print("  - PySide6 (GUI framework)")
        print("  - playwright (browser automation)")
        print("  - python-dateutil (date utilities)")
        print("\nAfter installation, you also need to install Playwright browsers:")
        print("\n    playwright install chromium")
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
    QAbstractItemView, QRadioButton, QButtonGroup, QGridLayout, QStackedWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont, QColor, QPalette

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

AD_NETWORK_BLOCKLIST = [
    'googleads', 'doubleclick', 'adsense', 'adservice', 'googlesyndication',
    'ad.doubleclick', 'pagead2.googlesyndication', 'adnxs.com', 'facebook.com/tr',
    'ads-twitter.com', 'analytics.twitter.com', 'static.ads-twitter.com'
]

CONSENT_BUTTON_TEXTS = [
    'accept', 'accept all', 'agree', 'allow all', 'i agree',
    'agree and close', 'allow cookies', 'got it', 'ok', 'consent',
    'agree and continue', 'akzeptieren', 'accepter', 'aceptar'
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

USER_AGENTS = {
    'desktop': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ],
    'android': [
        'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    ]
}

# Referrer URLs for different sources
REFERRER_URLS = {
    'facebook': 'https://facebook.com',
    'google': 'https://google.com',
    'twitter': 'https://twitter.com',
    'telegram': 'https://t.me',
    'instagram': 'https://instagram.com'
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
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.file_logger = logging.getLogger(__name__)
    
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
    
    def __init__(self, platform: str = 'desktop'):
        self.platform = platform
        self.user_agent = None
        self.viewport = None
        self.timezone = None
        self.locale = None
        self.hardware_concurrency = None
    
    def generate_fingerprint(self) -> Dict[str, Any]:
        """Generate a realistic browser fingerprint."""
        self.user_agent = random.choice(USER_AGENTS.get(self.platform, USER_AGENTS['desktop']))
        
        if self.platform == 'android':
            self.viewport = {
                'width': random.choice([360, 375, 412, 414]),
                'height': random.choice([640, 667, 732, 896])
            }
        else:
            self.viewport = {
                'width': random.choice([1280, 1366, 1440, 1920]),
                'height': random.choice([720, 768, 900, 1080])
            }
        
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
    async def scroll_page(page: Page, depth_percent: int = None):
        """Scroll page with enhanced human-like behavior - viewport-based, random direction, pauses."""
        try:
            if depth_percent is None:
                depth_percent = random.randint(30, 100)
            
            # Get page and viewport info
            page_height = await page.evaluate('document.documentElement.scrollHeight')
            viewport_height = await page.evaluate('window.innerHeight')
            target_scroll = int(page_height * (depth_percent / 100))
            
            # Scroll in steps based on viewport height with variable speed
            current_position = 0
            scroll_direction = 1  # 1 for down, -1 for up
            
            while current_position < target_scroll:
                # Random step size based on viewport (more realistic)
                step = int(viewport_height * random.uniform(0.3, 0.8)) * scroll_direction
                next_position = current_position + step
                
                # Clamp to valid range
                next_position = max(0, min(next_position, target_scroll))
                
                # Use smooth scrolling behavior
                await page.evaluate(f'''
                    window.scrollTo({{
                        top: {next_position},
                        behavior: 'smooth'
                    }})
                ''')
                
                current_position = next_position
                
                # Variable pause between scrolls
                await asyncio.sleep(random.uniform(0.2, 0.6))
                
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
                    await asyncio.sleep(random.uniform(0.3, 0.7))
                
                # Random pause to simulate reading
                if random.random() < READING_PAUSE_CHANCE:
                    await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Final idle pause
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            logging.error(f'Scroll error: {e}')
    
    @staticmethod
    async def mouse_movement(page: Page, x: int, y: int):
        """Simulate natural mouse movement."""
        try:
            # Add slight randomness to coordinates
            x_offset = random.randint(-5, 5)
            y_offset = random.randint(-5, 5)
            
            await page.mouse.move(x + x_offset, y + y_offset)
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
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
        """Random idle pause to simulate reading/thinking."""
        await asyncio.sleep(random.uniform(2, 5))
    
    @staticmethod
    async def highlight_text(page: Page):
        """
        Randomly highlight text on page to simulate human reading behavior.
        Selects random text elements and highlights them briefly.
        """
        try:
            # Find text elements (paragraphs, divs with text)
            text_elements = await page.query_selector_all('p, div, span, article, section')
            
            if not text_elements or len(text_elements) == 0:
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
    async def time_based_browsing(page: Page, min_time: int, max_time: int, enable_highlight: bool = False):
        """
        Simulate advanced human browsing behavior for a specified time period.
        
        Args:
            page: Playwright page object
            min_time: Minimum time to spend in seconds (120-480)
            max_time: Maximum time to spend in seconds (120-480)
            enable_highlight: Enable random text highlighting
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
            
            while time.time() - start_time < time_to_spend:
                # Random scroll depth
                scroll_depth = random.randint(30, 100)
                
                # Scroll down with human-like behavior
                await HumanBehavior.scroll_page(page, scroll_depth)
                
                # Random reading pause
                await asyncio.sleep(random.uniform(2.0, 5.0))
                
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
# CONSENT MANAGER
# ============================================================================

class ConsentManager:
    """Automatically handles cookie banners and popups."""
    
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
    
    async def handle_consents(self, page: Page) -> bool:
        """Detect and handle consent dialogs."""
        try:
            self.log_manager.log('Checking for consent dialogs...')
            
            # Wait a bit for dialogs to appear
            await asyncio.sleep(1)
            
            # Try multiple detection strategies
            handled = False
            
            # Strategy 1: Text-based button detection
            for text in CONSENT_BUTTON_TEXTS:
                selectors = [
                    f'button:has-text("{text}")',
                    f'a:has-text("{text}")',
                    f'[role="button"]:has-text("{text}")'
                ]
                
                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            # Check if element is visible
                            is_visible = await element.is_visible()
                            if is_visible:
                                # Human-like delay before clicking
                                await HumanBehavior.random_delay(500, 1500)
                                await element.click()
                                self.log_manager.log(f'Clicked consent button: {text}')
                                handled = True
                                await asyncio.sleep(0.5)
                                break
                        if handled:
                            break
                    except Exception:
                        continue
                
                if handled:
                    break
            
            # Strategy 2: Role-based dialog detection
            if not handled:
                try:
                    dialogs = await page.query_selector_all('[role="dialog"]')
                    for dialog in dialogs:
                        is_visible = await dialog.is_visible()
                        if is_visible:
                            # Look for accept button within dialog
                            buttons = await dialog.query_selector_all('button')
                            for button in buttons:
                                text = await button.inner_text()
                                if any(consent_text in text.lower() for consent_text in CONSENT_BUTTON_TEXTS):
                                    await HumanBehavior.random_delay(500, 1500)
                                    await button.click()
                                    self.log_manager.log(f'Clicked dialog consent button')
                                    handled = True
                                    break
                        if handled:
                            break
                except Exception:
                    pass
            
            return handled
            
        except Exception as e:
            self.log_manager.log(f'Consent handler error: {e}', 'ERROR')
            return False


# ============================================================================
# SPONSORED CLICK ENGINE
# ============================================================================

class SponsoredClickEngine:
    """Safely handles sponsored content interactions with strict rules."""
    
    def __init__(self, log_manager: LogManager, confidence_threshold: float = 0.7):
        self.log_manager = log_manager
        self.confidence_threshold = confidence_threshold
        # Pre-compile blocklist check for better performance
        self._blocklist_lower = [item.lower() for item in AD_NETWORK_BLOCKLIST]
    
    async def is_safe_element(self, element, page: Page) -> bool:
        """Check if element is safe to click (not a real ad network)."""
        try:
            # Get element attributes
            href = await element.get_attribute('href')
            onclick = await element.get_attribute('onclick')
            
            # Check blocklist with optimized search
            href_lower = href.lower() if href else None
            onclick_lower = onclick.lower() if onclick else None
            
            for blocked in self._blocklist_lower:
                if href_lower and blocked in href_lower:
                    self.log_manager.log(f'BLOCKED: Element contains ad network URL: {blocked}', 'WARNING')
                    return False
                if onclick_lower and blocked in onclick_lower:
                    self.log_manager.log(f'BLOCKED: Element has ad network onclick: {blocked}', 'WARNING')
                    return False
            
            # Check iframe sources
            try:
                iframe_src = await element.get_attribute('src')
                if iframe_src:
                    iframe_src_lower = iframe_src.lower()
                    for blocked in self._blocklist_lower:
                        if blocked in iframe_src_lower:
                            self.log_manager.log(f'BLOCKED: Iframe from ad network: {blocked}', 'WARNING')
                            return False
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            self.log_manager.log(f'Safety check error: {e}', 'ERROR')
            return False
    
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
    
    async def find_sponsored_elements(self, page: Page) -> List:
        """Find safe sponsored/promo elements on page."""
        safe_elements = []
        
        try:
            for selector in SPONSORED_SELECTORS:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        # Safety check
                        is_safe = await self.is_safe_element(element, page)
                        if not is_safe:
                            continue
                        
                        # Confidence check
                        confidence = await self.calculate_confidence(element)
                        if confidence >= self.confidence_threshold:
                            safe_elements.append({
                                'element': element,
                                'selector': selector,
                                'confidence': confidence
                            })
                
                except Exception as e:
                    self.log_manager.log(f'Error finding elements for {selector}: {e}', 'ERROR')
                    continue
            
            self.log_manager.log(f'Found {len(safe_elements)} safe sponsored elements')
            return safe_elements
            
        except Exception as e:
            self.log_manager.log(f'Find sponsored elements error: {e}', 'ERROR')
            return []
    
    async def click_sponsored_content(self, page: Page, ratio: float):
        """Click sponsored content based on ratio."""
        try:
            # Random decision based on ratio
            if random.random() > ratio:
                self.log_manager.log('Skipping sponsored click (ratio check)')
                return False
            
            # Find safe sponsored elements
            sponsored = await self.find_sponsored_elements(page)
            
            if not sponsored:
                self.log_manager.log('No safe sponsored elements found')
                return False
            
            # Select random element
            selected = random.choice(sponsored)
            
            # Natural click
            self.log_manager.log(f'Clicking sponsored element (confidence: {selected["confidence"]:.2f})')
            success = await HumanBehavior.natural_click(page, selected['selector'])
            
            return success
            
        except Exception as e:
            self.log_manager.log(f'Sponsored click error: {e}', 'ERROR')
            return False


# ============================================================================
# SCRIPT EXECUTOR
# ============================================================================

class ScriptExecutor:
    """Executes RPA scripts with JSON-based steps."""
    
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
        self.current_page = None
    
    async def execute_script(self, script: Dict[str, Any], context: BrowserContext):
        """Execute a full RPA script with enhanced error handling and logging."""
        try:
            steps = script.get('steps', [])
            
            for idx, step in enumerate(steps):
                step_type = step.get('type')
                self.log_manager.log(f'▶ Starting step {idx + 1}/{len(steps)}: {step_type}')
                
                try:
                    if step_type == 'newPage':
                        self.current_page = await context.new_page()
                        self.log_manager.log(f'✓ Step {idx + 1}: New page opened')
                    
                    elif step_type == 'navigate':
                        url = step.get('url', '')
                        if self.current_page:
                            await self.current_page.goto(url, wait_until='domcontentloaded', timeout=30000)
                            self.log_manager.log(f'✓ Step {idx + 1}: Navigated to {url}')
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
                            depth = step.get('depth', None)
                            # Human-like scroll with natural behavior
                            await HumanBehavior.scroll_page(self.current_page, depth)
                            self.log_manager.log(f'✓ Step {idx + 1}: Scrolled to depth {depth}%')
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
                    
                    else:
                        self.log_manager.log(f'⚠ Step {idx + 1}: Unknown step type: {step_type}', 'WARNING')
                    
                except Exception as e:
                    self.log_manager.log(f'✗ Step {idx + 1} error: {e}', 'ERROR')
                    # Continue to next step even on error
                    continue
            
            self.log_manager.log('Script execution completed')
            return True
            
        except Exception as e:
            self.log_manager.log(f'Script execution error: {e}', 'ERROR')
            return False


# ============================================================================
# PROXY MANAGER
# ============================================================================

class ProxyManager:
    """Manages proxy configurations."""
    
    def __init__(self):
        self.proxy_enabled = False
        self.proxy_type = 'HTTP'
        self.proxy_list = []
        self.rotate_proxy = True
        self.current_proxy_index = 0
        self.failed_proxies = set()
    
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
                        # Check for host:port:username:password format
                        parts = line.split(':')
                        if len(parts) == 4:
                            # Assume host:port:username:password
                            host, port, username, password = parts
                            proxy_config['server'] = f"{proxy_type}://{host}:{port}"
                            proxy_config['username'] = username
                            proxy_config['password'] = password
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
                    
            except Exception as e:
                # Log parsing error but continue with other proxies
                print(f"Warning: Failed to parse proxy on line {line_num}: {line} - {e}")
                continue
        
        return proxies
    
    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration for Playwright."""
        if not self.proxy_enabled or not self.proxy_list:
            return None
        
        # Filter out failed proxies
        available_proxies = [p for i, p in enumerate(self.proxy_list) if i not in self.failed_proxies]
        
        if not available_proxies:
            # Reset failed proxies if all failed
            self.failed_proxies.clear()
            available_proxies = self.proxy_list
        
        if self.rotate_proxy:
            # Rotate through proxies
            proxy = available_proxies[self.current_proxy_index % len(available_proxies)]
            self.current_proxy_index += 1
        else:
            # Use first available proxy
            proxy = available_proxies[0]
        
        return proxy
    
    def mark_proxy_failed(self, proxy_config: Dict[str, str]):
        """Mark a proxy as failed."""
        try:
            idx = self.proxy_list.index(proxy_config)
            self.failed_proxies.add(idx)
        except ValueError:
            pass
    
    def get_proxy_count(self) -> int:
        """Get total number of loaded proxies."""
        return len(self.proxy_list)


# ============================================================================
# PROXY GEOLOCATION
# ============================================================================

class ProxyGeolocation:
    """Fetches proxy geolocation information."""
    
    def __init__(self):
        self.cache = {}
    
    def extract_ip_from_proxy(self, proxy_config: Dict[str, str]) -> Optional[str]:
        """Extract IP address from proxy configuration."""
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
    
    async def fetch_location(self, proxy_config: Dict[str, str]) -> Dict[str, str]:
        """
        Fetch geolocation for a proxy.
        Returns a dictionary with location info like country, city, timezone.
        
        Note: This uses a simple IP extraction and mock data for demo purposes.
        For production, integrate with ip-api.com, ipinfo.io, or similar services.
        """
        try:
            ip = self.extract_ip_from_proxy(proxy_config)
            if not ip:
                return {
                    'ip': 'unknown',
                    'country': 'Unknown',
                    'city': 'Unknown',
                    'timezone': 'UTC'
                }
            
            # Check cache
            if ip in self.cache:
                return self.cache[ip]
            
            # For demo: Parse IP and determine mock location
            # In production, make HTTP request to geolocation API
            location_info = {
                'ip': ip,
                'country': self._guess_country_from_ip(ip),
                'city': 'Unknown',
                'timezone': 'UTC'
            }
            
            # Cache the result
            self.cache[ip] = location_info
            return location_info
            
        except Exception as e:
            logging.error(f'Proxy geolocation error: {e}')
            return {
                'ip': 'error',
                'country': 'Unknown',
                'city': 'Unknown',
                'timezone': 'UTC'
            }
    
    def _guess_country_from_ip(self, ip: str) -> str:
        """Simple country guessing based on IP pattern (for demo purposes)."""
        # In production, this should use a real geolocation API
        if ip.startswith('192.168') or ip.startswith('10.') or ip.startswith('172.'):
            return 'Local Network'
        # Mock logic for demo
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
    """Manages Playwright browser instances."""
    
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.fingerprint_manager = FingerprintManager()
        self.proxy_manager = ProxyManager()
        self.headless = False
    
    async def initialize(self):
        """Initialize Playwright and browser."""
        try:
            self.log_manager.log('━━━ Browser Initialization Started ━━━')
            self.log_manager.log('Initializing Playwright...')
            self.playwright = await async_playwright().start()
            self.log_manager.log('✓ Playwright started successfully')
            
            launch_options = {
                'headless': self.headless,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            }
            
            # Note: Proxy is now set per-context, not per-browser
            
            self.log_manager.log(f'Launching Chromium browser (headless={self.headless})...')
            self.browser = await self.playwright.chromium.launch(**launch_options)
            self.log_manager.log('✓ Browser launched successfully')
            self.log_manager.log('━━━ Browser Initialization Complete ━━━')
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.log_manager.log(f'Browser initialization error: {error_msg}', 'ERROR')
            
            # Expanded error detection for browser installation issues
            browser_not_found_patterns = [
                "Executable doesn't exist",  # Use double quotes to avoid escaping
                'Browser was not found',
                'Failed to launch',
                'Could not find browser',
                'No such file or directory',
                'playwright.chromium.launch'
            ]
            
            # Check for system dependency issues (common on Linux)
            missing_deps_patterns = [
                'libgobject',
                'libnss',
                'libatk',
                'libdrm',
                'libgbm',
                'libasound',
                'error while loading shared libraries'
            ]
            
            is_browser_missing = any(pattern in error_msg for pattern in browser_not_found_patterns)
            is_deps_missing = any(pattern in error_msg for pattern in missing_deps_patterns)
            
            # Check if it's a browser not installed error or missing dependencies
            if is_browser_missing or is_deps_missing:
                self.log_manager.log('', 'ERROR')
                if is_browser_missing and is_deps_missing:
                    self.log_manager.log('Chromium browser and system dependencies are not installed!', 'ERROR')
                elif is_browser_missing:
                    self.log_manager.log('Chromium browser is not installed!', 'ERROR')
                else:
                    self.log_manager.log('System dependencies are missing!', 'ERROR')
                
                self.log_manager.log('Attempting automatic installation...', 'WARNING')
                
                # Attempt to install the browser automatically
                try:
                    # Verify playwright executable exists
                    playwright_path = shutil.which('playwright')
                    if not playwright_path:
                        self.log_manager.log('✗ Playwright executable not found in PATH', 'ERROR')
                        self.log_manager.log('Please ensure playwright is installed: pip install playwright', 'ERROR')
                        return False
                    
                    # Install browser if missing
                    if is_browser_missing:
                        self.log_manager.log('Installing Chromium browser...', 'INFO')
                        result = subprocess.run(
                            [playwright_path, 'install', 'chromium'],
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minute timeout
                        )
                        
                        if result.returncode != 0:
                            self.log_manager.log('✗ Browser installation failed', 'ERROR')
                            if result.stderr:
                                self.log_manager.log(f'Error: {result.stderr}', 'ERROR')
                            self.log_manager.log('Please run manually: playwright install chromium', 'ERROR')
                            return False
                        
                        self.log_manager.log('✓ Browser installed successfully!', 'INFO')
                    
                    # Install system dependencies on Linux
                    # Note: We install deps proactively when browser is missing because:
                    # 1. If deps were the issue, this fixes it
                    # 2. If browser was missing, deps are often also needed (fresh Linux systems)
                    # 3. Better to install now than fail on retry
                    if platform.system() == 'Linux' and (is_deps_missing or is_browser_missing):
                        self.log_manager.log('Installing system dependencies (Linux)...', 'INFO')
                        deps_result = subprocess.run(
                            [playwright_path, 'install-deps', 'chromium'],
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minute timeout
                        )
                        
                        if deps_result.returncode != 0:
                            self.log_manager.log('⚠ System dependencies installation failed', 'WARNING')
                            self.log_manager.log('This may require sudo privileges', 'WARNING')
                            self.log_manager.log('Try manually: sudo playwright install-deps chromium', 'WARNING')
                            # Don't return False - try to launch anyway
                        else:
                            self.log_manager.log('✓ System dependencies installed successfully!', 'INFO')
                    
                    # Retry initialization
                    self.log_manager.log('Retrying browser initialization...', 'INFO')
                    try:
                        # Ensure Playwright is initialized before launching browser
                        if not self.playwright:
                            self.log_manager.log('Initializing Playwright...', 'INFO')
                            self.playwright = await async_playwright().start()
                            self.log_manager.log('✓ Playwright started successfully', 'INFO')
                        
                        self.browser = await self.playwright.chromium.launch(**launch_options)
                        self.log_manager.log('✓ Browser launched successfully after auto-install')
                        self.log_manager.log('━━━ Browser Initialization Complete ━━━')
                        return True
                    except Exception as retry_error:
                        retry_msg = str(retry_error)
                        self.log_manager.log(f'Failed to launch browser after install: {retry_msg}', 'ERROR')
                        
                        # Check if still missing dependencies
                        if any(pattern in retry_msg for pattern in missing_deps_patterns):
                            self.log_manager.log('', 'ERROR')
                            self.log_manager.log('System dependencies are still missing.', 'ERROR')
                            self.log_manager.log('Please run: sudo playwright install-deps chromium', 'ERROR')
                            self.log_manager.log('Or install dependencies manually for your distribution', 'ERROR')
                        
                except subprocess.TimeoutExpired:
                    self.log_manager.log('✗ Installation timed out (>5 minutes)', 'ERROR')
                    self.log_manager.log('Check your internet connection and try again', 'ERROR')
                except Exception as install_error:
                    self.log_manager.log(f'✗ Installation error: {install_error}', 'ERROR')
                
                self.log_manager.log('', 'ERROR')
                self.log_manager.log('Manual installation steps:', 'ERROR')
                self.log_manager.log('  1. playwright install chromium', 'ERROR')
                if platform.system() == 'Linux':
                    self.log_manager.log('  2. sudo playwright install-deps chromium  (Linux only)', 'ERROR')
                self.log_manager.log('Or: python -m playwright install chromium', 'ERROR')
                self.log_manager.log('', 'ERROR')
            
            return False
    
    async def create_context(self, platform: str = 'desktop', use_proxy: bool = True) -> Optional[BrowserContext]:
        """Create a new browser context with fingerprinting and optional proxy."""
        try:
            if not self.browser:
                success = await self.initialize()
                if not success or not self.browser:
                    self.log_manager.log('Cannot create context: browser initialization failed', 'ERROR')
                    return None
            
            # Generate fingerprint
            self.fingerprint_manager.platform = platform
            fingerprint = self.fingerprint_manager.generate_fingerprint()
            
            self.log_manager.log(f'━━━ Creating Browser Context ━━━')
            self.log_manager.log(f'Platform: {platform}')
            self.log_manager.log(f'User Agent: {fingerprint["user_agent"][:60]}...')
            
            context_options = {
                'user_agent': fingerprint['user_agent'],
                'viewport': fingerprint['viewport'],
                'locale': fingerprint['locale'],
                'timezone_id': fingerprint['timezone'],
            }
            
            # Add proxy if enabled and configured
            proxy_config = None
            proxy_location = None
            if use_proxy:
                proxy_config = self.proxy_manager.get_proxy_config()
                if proxy_config:
                    # Fetch proxy geolocation
                    geo_manager = ProxyGeolocation()
                    proxy_location = await geo_manager.fetch_location(proxy_config)
                    
                    context_options['proxy'] = proxy_config
                    server = proxy_config.get('server', 'unknown')
                    self.log_manager.log(f'✓ Using proxy: {server}')
                    self.log_manager.log(f'✓ Proxy Location: {proxy_location["country"]}, IP: {proxy_location["ip"]}')
                else:
                    self.log_manager.log('No proxy configured, using direct connection')
            
            # Try to create context with proxy
            try:
                self.context = await self.browser.new_context(**context_options)
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
                    self.context = await self.browser.new_context(**context_options)
                    self.log_manager.log('✓ Browser context created with direct connection (proxy bypassed)')
                    proxy_location = None  # Clear proxy location since not using proxy
                else:
                    # Re-raise if not a proxy error
                    raise
            
            # Inject navigator properties
            await self.context.add_init_script(f"""
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint['hardware_concurrency']}
                }});
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined
                }});
            """)
            
            # Store proxy location for later use (e.g., displaying in browser)
            self.context._proxy_location = proxy_location
            
            self.log_manager.log('✓ Browser context created successfully')
            self.log_manager.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            return self.context
            
        except Exception as e:
            self.log_manager.log(f'Context creation error: {e}', 'ERROR')
            self.log_manager.log('This may be due to:', 'ERROR')
            self.log_manager.log('  - Invalid proxy configuration', 'ERROR')
            self.log_manager.log('  - Network connectivity issues', 'ERROR')
            self.log_manager.log('  - Browser crash or resource exhaustion', 'ERROR')
            return None
    
    async def close(self):
        """Close browser and cleanup."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.log_manager.log('Browser closed')
            
        except Exception as e:
            self.log_manager.log(f'Browser close error: {e}', 'ERROR')


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
    
    def emit_log(self, message: str, level: str = 'INFO'):
        """Emit log to GUI."""
        log_entry = self.log_manager.log(message, level)
        self.log_signal.emit(log_entry)
    
    def stop(self):
        """Stop the automation."""
        self.running = False
        self.emit_log('Stopping automation...')
    
    async def handle_referral_visit(self, page: Page, target_url: str, referral_sources: List[str]):
        """Handle referral visit - navigate from referrer to target."""
        # Randomly select one referral source
        referrer = random.choice(referral_sources)
        
        # Get referrer URL from constants
        referrer_url = REFERRER_URLS.get(referrer, 'https://google.com')
        
        self.emit_log(f'[INFO] Referral source selected: {referrer.capitalize()}')
        self.emit_log(f'Opening referrer: {referrer_url}')
        
        try:
            # Navigate to referrer
            await page.goto(referrer_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(random.uniform(2, 4))
            
            # Human-like idle and scroll on referrer
            await HumanBehavior.scroll_page(page, random.randint(20, 40))
            await asyncio.sleep(random.uniform(1, 3))
            
            # Navigate to target URL (simulate typing URL or clicking)
            self.emit_log(f'Navigating to target from {referrer.capitalize()}...')
            await page.goto(target_url, wait_until='domcontentloaded', timeout=30000)
            
        except Exception as e:
            self.emit_log(f'Error during referral visit: {e}', 'ERROR')
            raise
    
    async def handle_search_visit(self, page: Page, target_domain: str, keyword: str):
        """Handle search visit - search on Google, find target domain, and click it."""
        self.emit_log(f'[INFO] Search visit with keyword: "{keyword}" for domain: "{target_domain}"')
        
        try:
            # Navigate to Google
            self.emit_log('Opening Google...')
            await page.goto('https://www.google.com', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Focus search box
            search_selectors = ['input[name="q"]', 'textarea[name="q"]', '#APjFqb']
            search_box = None
            
            for selector in search_selectors:
                try:
                    search_box = await page.query_selector(selector)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                self.emit_log('Could not find Google search box, skipping search', 'WARNING')
                return False
            
            # Type keyword character by character with delays
            self.emit_log('Typing search keyword...')
            await search_box.click()
            await asyncio.sleep(random.uniform(0.3, 0.6))
            
            for char in keyword:
                await search_box.type(char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Press Enter
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await search_box.press('Enter')
            
            # Wait for results
            await asyncio.sleep(random.uniform(2, 4))
            
            # Scroll results page
            await HumanBehavior.scroll_page(page, random.randint(30, 60))
            await asyncio.sleep(random.uniform(1, 2))
            
            # Try to find and click target domain in top 10 results
            self.emit_log(f'Searching for target domain "{target_domain}" in top 10 results...')
            
            # Get all result links
            result_links = await page.query_selector_all('a[href]')
            
            found_link = None
            for link in result_links[:30]:  # Check first 30 links (covers top 10 results)
                try:
                    href = await link.get_attribute('href')
                    if href and target_domain in href:
                        found_link = link
                        self.emit_log(f'✓ Found target domain in results: {href[:80]}...')
                        break
                except:
                    continue
            
            if found_link:
                # Click the found link
                self.emit_log('Clicking on target domain link...')
                await found_link.click()
                await asyncio.sleep(random.uniform(2, 4))
                return True
            else:
                self.emit_log(f'⚠ Target domain "{target_domain}" not found in top results', 'WARNING')
                return False
            
        except Exception as e:
            self.emit_log(f'Error during search visit: {e}', 'ERROR')
            return False
    
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
                
                # Random mouse movements
                try:
                    viewport_size = page.viewport_size
                    if viewport_size:
                        x = random.randint(100, viewport_size['width'] - 100)
                        y = random.randint(100, viewport_size['height'] - 100)
                        await page.mouse.move(x, y)
                        await asyncio.sleep(random.uniform(0.5, 2))
                except:
                    pass
                
                # Try to click a link if extra pages enabled
                if enable_extra_pages and pages_visited < max_pages:
                    try:
                        # Find clickable article/content links
                        links = await page.query_selector_all('a[href^="http"], a[href^="/"]')
                        
                        if links and len(links) > 0:
                            # Filter out navigation/social links
                            content_link = random.choice(links[:min(20, len(links))])
                            
                            href = await content_link.get_attribute('href')
                            if href and not any(skip in href.lower() for skip in LINK_SKIP_PATTERNS):
                                
                                self.emit_log(f'[INFO] Clicking link to new page (page {pages_visited + 1}/{max_pages})')
                                await content_link.click()
                                await asyncio.sleep(random.uniform(3, 6))
                                pages_visited += 1
                                interactions_count += 1
                                
                                # Handle consents on new page
                                consent_manager = ConsentManager(self.log_manager)
                                await consent_manager.handle_consents(page)
                                
                    except Exception as e:
                        self.emit_log(f'Could not click link: {e}', 'WARNING')
                
                # Random idle pause (simulating reading)
                await asyncio.sleep(random.uniform(8, 25))
                
            self.emit_log(f'✓ Completed {interactions_count} interactions across {pages_visited} pages')
                
        except Exception as e:
            self.emit_log(f'Error during interaction: {e}', 'WARNING')
    
    async def handle_ad_detection_and_interaction(self, page: Page):
        """Detect ads and interact with them in a human-like manner."""
        try:
            self.emit_log('[INFO] Detecting ads on page...')
            ad_manager = AdDetectionManager(self.log_manager)
            
            # Detect ads
            ads = await ad_manager.detect_ads(page)
            
            if not ads or len(ads) == 0:
                self.emit_log('[INFO] No ads detected on page')
                return
            
            self.emit_log(f'[INFO] ✓ Found {len(ads)} ad(s) on page')
            
            # Select random ads to interact with (1-3 ads)
            num_ads_to_view = min(random.randint(1, 3), len(ads))
            selected_ads = random.sample(ads, num_ads_to_view)
            
            for i, ad in enumerate(selected_ads, 1):
                self.emit_log(f'[INFO] Interacting with ad {i}/{num_ads_to_view}...')
                
                # Scroll to ad
                scrolled = await ad_manager.scroll_to_ad(page, ad)
                if not scrolled:
                    continue
                
                self.emit_log('[INFO] Waiting for ad to load...')
                await ad_manager.wait_for_ad_load(page, ad)
                
                self.emit_log('[INFO] Viewing ad naturally...')
                await ad_manager.view_ad_naturally(page, ad)
                
                # Random pause between ads
                if i < num_ads_to_view:
                    await asyncio.sleep(random.uniform(2, 4))
            
            self.emit_log(f'✓ Completed interaction with {num_ads_to_view} ad(s)')
            
        except Exception as e:
            self.emit_log(f'Ad interaction error: {e}', 'WARNING')
    
    async def execute_single_visit(self, visit_num, url_list, platforms, visit_type, 
                                   search_keyword, target_domain, referral_sources,
                                   min_time_spend, max_time_spend, enable_consent, 
                                   enable_interaction, enable_extra_pages, max_pages,
                                   consent_manager, enable_highlight=False, enable_ad_interaction=False):
        """Execute a single visit/profile session."""
        try:
            # Select random URL and platform
            target_url = random.choice(url_list)
            platform = random.choice(platforms)
            
            self.emit_log(f'━━━ Profile {visit_num} | Platform: {platform} | URL: {target_url[:50]}... ━━━')
            
            # Create new context for this visit (session isolation)
            self.emit_log(f'Creating browser context for profile {visit_num}...')
            context = await self.browser_manager.create_context(platform)
            if not context:
                self.emit_log(f'Failed to create browser context for profile {visit_num}', 'ERROR')
                return False
            
            try:
                # Create new page
                page = await context.new_page()
                
                # Display proxy location in page title if available
                proxy_location = getattr(context, '_proxy_location', None)
                if proxy_location:
                    location_text = f"Proxy: {proxy_location['country']} | IP: {proxy_location['ip']}"
                    self.emit_log(f'[INFO] {location_text}')
                    # Inject location display into page
                    await page.add_init_script(f"""
                        window.addEventListener('load', () => {{
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
                            locationDiv.textContent = '{location_text}';
                            document.body.appendChild(locationDiv);
                        }});
                    """)
                
                # Navigate based on visit type
                if visit_type == 'referral':
                    await self.handle_referral_visit(page, target_url, referral_sources)
                elif visit_type == 'search':
                    # Search visit - find target domain in Google results
                    found = await self.handle_search_visit(page, target_domain, search_keyword)
                    if not found:
                        self.emit_log(f'Target domain not found in search for profile {visit_num}', 'WARNING')
                        return False
                else:
                    # Direct visit
                    self.emit_log(f'[INFO] Direct visit to {target_url}')
                    await page.goto(target_url, wait_until='domcontentloaded', timeout=30000)
                
                # Handle consents if enabled
                if consent_manager and enable_consent:
                    await consent_manager.handle_consents(page)
                
                # Detect and interact with ads if enabled
                if enable_ad_interaction:
                    await self.handle_ad_detection_and_interaction(page)
                
                # Time-based human scrolling behavior with highlighting
                self.emit_log(f'Starting time-based browsing ({min_time_spend}-{max_time_spend} seconds)...')
                await HumanBehavior.time_based_browsing(page, min_time_spend, max_time_spend, enable_highlight)
                
                # Handle interaction if enabled (legacy mode)
                if enable_interaction:
                    await self.handle_interaction(page, max_pages, enable_extra_pages)
                
                # Close page
                await page.close()
                
                self.emit_log(f'✓ Profile {visit_num} completed successfully')
                return True
                
            finally:
                # Always close context after visit (session isolation)
                await context.close()
                
        except Exception as e:
            self.emit_log(f'✗ Profile {visit_num} error: {e}', 'ERROR')
            return False
    
    async def run_automation(self):
        """Main automation loop with multi-threading, multiple URLs, and platform mixing support."""
        try:
            self.running = True
            self.emit_log('Starting automation...')
            
            # Get configuration
            url_list = self.config.get('url_list', [])
            num_visits = self.config.get('num_visits', 1)
            min_time_spend = self.config.get('min_time_spend', 120)  # 2 minutes default
            max_time_spend = self.config.get('max_time_spend', 240)  # 4 minutes default
            threads = self.config.get('threads', 1)
            total_threads_limit = self.config.get('total_threads', 0)
            platforms = self.config.get('platforms', ['desktop'])
            content_ratio = self.config.get('content_ratio', 85) / 100
            sponsored_ratio = self.config.get('sponsored_ratio', 15) / 100
            visit_type = self.config.get('visit_type', 'direct')
            search_keyword = self.config.get('search_keyword', '')
            target_domain = self.config.get('target_domain', '')
            referral_sources = self.config.get('referral_sources', [])
            enable_interaction = self.config.get('enable_interaction', False)
            enable_extra_pages = self.config.get('enable_extra_pages', False)
            max_pages = self.config.get('max_pages', 5)
            enable_consent = self.config.get('enable_consent', True)
            enable_popups = self.config.get('enable_popups', True)
            enable_text_highlight = self.config.get('enable_text_highlight', False)
            enable_ad_interaction = self.config.get('enable_ad_interaction', False)
            
            self.emit_log(f'Configuration: {len(url_list)} URLs, {num_visits} profiles, {threads} threads')
            self.emit_log(f'Time per profile: {min_time_spend}-{max_time_spend} seconds with human scrolling')
            if enable_text_highlight:
                self.emit_log('✓ Text highlighting enabled')
            if enable_ad_interaction:
                self.emit_log('✓ Ad detection & interaction enabled')
            if total_threads_limit > 0:
                self.emit_log(f'Total thread limit: {total_threads_limit}')
            
            # Check proxy configuration and log proxy status BEFORE browser initialization
            proxy_manager = self.browser_manager.proxy_manager
            if proxy_manager.proxy_enabled:
                proxy_count = proxy_manager.get_proxy_count()
                if proxy_count > 0:
                    self.emit_log(f'✓ Proxy configuration loaded: {proxy_count} proxies available')
                    if proxy_manager.rotate_proxy:
                        self.emit_log('✓ Proxy rotation enabled')
                else:
                    self.emit_log('⚠ Proxy enabled but no proxies loaded', 'WARNING')
            else:
                self.emit_log('Proxy disabled, using direct connection')
            
            # Initialize browser AFTER proxy validation
            self.browser_manager.headless = self.config.get('headless', False)
            
            self.emit_log('Initializing browser...')
            success = await self.browser_manager.initialize()
            if not success:
                self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'ERROR')
                self.emit_log('Failed to initialize browser', 'ERROR')
                self.emit_log('Please check the logs above for details', 'ERROR')
                self.emit_log('Common issues:', 'ERROR')
                self.emit_log('  1. Chromium not installed: Run "playwright install chromium"', 'ERROR')
                self.emit_log('  2. Port conflict or permission issues', 'ERROR')
                self.emit_log('  3. System resources (memory/disk) insufficient', 'ERROR')
                self.emit_log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'ERROR')
                return
            
            # Create consent manager
            consent_manager = ConsentManager(self.log_manager) if enable_consent else None
            
            # Track completed profiles
            total_profiles_completed = 0
            
            self.emit_log(f'Starting concurrent execution: {threads} browsers at a time')
            
            # Run visits in batches based on thread count
            for batch_start in range(0, num_visits, threads):
                if not self.running:
                    self.emit_log('Stop requested, exiting gracefully...')
                    break
                
                # Check total thread limit
                if total_threads_limit > 0 and total_profiles_completed >= total_threads_limit:
                    self.emit_log(f'✓ Total thread limit reached ({total_threads_limit}), stopping...')
                    break
                
                # Calculate how many visits in this batch
                batch_end = min(batch_start + threads, num_visits)
                batch_size = batch_end - batch_start
                
                if total_threads_limit > 0:
                    remaining = total_threads_limit - total_profiles_completed
                    batch_size = min(batch_size, remaining)
                
                self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                self.emit_log(f'Starting batch: {batch_size} browsers running simultaneously')
                self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
                
                # Create tasks for concurrent execution
                tasks = []
                for i in range(batch_size):
                    visit_num = batch_start + i + 1
                    task = self.execute_single_visit(
                        visit_num, url_list, platforms, visit_type,
                        search_keyword, target_domain, referral_sources,
                        min_time_spend, max_time_spend, enable_consent,
                        enable_interaction, enable_extra_pages, max_pages,
                        consent_manager, enable_text_highlight, enable_ad_interaction
                    )
                    tasks.append(task)
                
                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successes and log exceptions
                success_count = 0
                for i, result in enumerate(results):
                    if result is True:
                        success_count += 1
                    elif isinstance(result, Exception):
                        visit_num = batch_start + i + 1
                        self.emit_log(f'Profile {visit_num} exception: {result}', 'ERROR')
                
                total_profiles_completed += success_count
                
                self.emit_log(f'Batch completed: {success_count}/{batch_size} profiles successful')
                
                # Small delay between batches
                if batch_end < num_visits and self.running:
                    await asyncio.sleep(random.uniform(1, 3))
            
            self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            self.emit_log(f'✓ Automation completed: {total_profiles_completed} profiles processed')
            self.emit_log(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            
            # Cleanup
            await self.browser_manager.close()
            self.emit_log('Browser closed, automation finished')
            
        except Exception as e:
            self.emit_log(f'Automation error: {e}', 'ERROR')
        
        finally:
            self.running = False
            self.finished_signal.emit()
    
    def run(self):
        """Entry point for thread execution."""
        asyncio.run(self.run_automation())


# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class AppGUI(QMainWindow):
    """Main application GUI."""
    
    def __init__(self):
        super().__init__()
        self.log_manager = LogManager()
        self.automation_thread = None
        self.automation_worker = None
        # Initialize confidence_input with default value (since sponsored tab is removed)
        self.confidence_input = QDoubleSpinBox()
        self.confidence_input.setValue(0.7)
        # Create a reusable proxy manager for counting
        self._proxy_count_manager = ProxyManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Humanex Version 5 - Advanced Simulation Traffic')
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
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498db;
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
        
        # App title
        title = QLabel('🤖 Humanex v5')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('padding: 20px; background-color: #1a252f; color: white;')
        layout.addWidget(title)
        
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
        
        # Footer
        footer = QLabel('v5.0 • 2026')
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet('color: #7f8c8d; font-size: 11px; padding: 15px;')
        layout.addWidget(footer)
        
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
        url_group = QGroupBox('🌍 Website Configuration')
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
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Visit Type Section (NEW FEATURE)
        visit_type_group = QGroupBox('🔍 Visit Type')
        visit_type_layout = QVBoxLayout()
        visit_type_layout.setSpacing(10)
        
        # Radio buttons for visit type
        self.visit_type_group = QButtonGroup()
        self.visit_direct_radio = QRadioButton('Direct Visit')
        self.visit_referral_radio = QRadioButton('Referral Visit')
        self.visit_search_radio = QRadioButton('Search Visit')
        self.visit_direct_radio.setChecked(True)
        
        self.visit_type_group.addButton(self.visit_direct_radio, 0)
        self.visit_type_group.addButton(self.visit_referral_radio, 1)
        self.visit_type_group.addButton(self.visit_search_radio, 2)
        
        visit_type_layout.addWidget(self.visit_direct_radio)
        visit_type_layout.addWidget(self.visit_referral_radio)
        visit_type_layout.addWidget(self.visit_search_radio)
        
        # Connect signals to toggle visibility of sub-sections
        self.visit_referral_radio.toggled.connect(self.toggle_referral_section)
        self.visit_search_radio.toggled.connect(self.toggle_search_section)
        
        visit_type_group.setLayout(visit_type_layout)
        layout.addWidget(visit_type_group)
        
        # Referral Source Selector (NEW FEATURE)
        self.referral_group = QGroupBox('🔗 Referral Source Selector')
        referral_layout = QGridLayout()
        referral_layout.setSpacing(10)
        
        referral_label = QLabel('Select referral sources (multi-select allowed):')
        referral_layout.addWidget(referral_label, 0, 0, 1, 2)
        
        # Checkboxes in 2 columns
        self.referral_facebook = QCheckBox('✅ Facebook')
        self.referral_google = QCheckBox('✅ Google')
        self.referral_twitter = QCheckBox('✅ Twitter (X)')
        self.referral_telegram = QCheckBox('✅ Telegram')
        self.referral_instagram = QCheckBox('✅ Instagram')
        
        # Set default checked
        self.referral_facebook.setChecked(True)
        self.referral_google.setChecked(True)
        
        # Add to grid (2 columns)
        referral_layout.addWidget(self.referral_facebook, 1, 0)
        referral_layout.addWidget(self.referral_google, 1, 1)
        referral_layout.addWidget(self.referral_twitter, 2, 0)
        referral_layout.addWidget(self.referral_telegram, 2, 1)
        referral_layout.addWidget(self.referral_instagram, 3, 0)
        
        self.referral_group.setLayout(referral_layout)
        self.referral_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.referral_group)
        
        # Search Settings (NEW FEATURE)
        self.search_group = QGroupBox('🔎 Search Settings')
        search_layout = QVBoxLayout()
        search_layout.setSpacing(10)
        
        search_layout.addWidget(QLabel('Search Keyword:'))
        self.search_keyword_input = QLineEdit()
        self.search_keyword_input.setPlaceholderText('Enter keyword to search...')
        search_layout.addWidget(self.search_keyword_input)
        
        search_layout.addWidget(QLabel('Target Domain (e.g., example.com):'))
        self.target_domain_input = QLineEdit()
        self.target_domain_input.setPlaceholderText('Enter your target domain...')
        search_layout.addWidget(self.target_domain_input)
        
        info_label = QLabel('ℹ️ Bot will search keyword on Google, find target domain in top 10, and click it')
        info_label.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        info_label.setWordWrap(True)
        search_layout.addWidget(info_label)
        
        self.search_group.setLayout(search_layout)
        self.search_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.search_group)
        
        # Traffic Settings
        traffic_group = QGroupBox('📊 Traffic Settings')
        traffic_layout = QVBoxLayout()
        traffic_layout.setSpacing(10)
        
        # Time spend settings
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel('Time to Spend per Profile (seconds):'))
        traffic_layout.addLayout(time_layout)
        
        min_time_layout = QHBoxLayout()
        min_time_layout.addWidget(QLabel('  Minimum:'))
        self.min_time_input = QSpinBox()
        self.min_time_input.setRange(120, 480)  # 2 to 8 minutes
        self.min_time_input.setValue(120)  # 2 minutes default
        self.min_time_input.setSuffix(' sec')
        self.min_time_input.setToolTip('Minimum time to spend on each profile with human scrolling (2-8 minutes)')
        self.min_time_input.valueChanged.connect(self.validate_time_range)
        min_time_layout.addWidget(self.min_time_input)
        min_time_layout.addStretch()
        traffic_layout.addLayout(min_time_layout)
        
        max_time_layout = QHBoxLayout()
        max_time_layout.addWidget(QLabel('  Maximum:'))
        self.max_time_input = QSpinBox()
        self.max_time_input.setRange(120, 480)  # 2 to 8 minutes
        self.max_time_input.setValue(240)  # 4 minutes default
        self.max_time_input.setSuffix(' sec')
        self.max_time_input.setToolTip('Maximum time to spend on each profile with human scrolling (2-8 minutes)')
        self.max_time_input.valueChanged.connect(self.validate_time_range)
        max_time_layout.addWidget(self.max_time_input)
        max_time_layout.addStretch()
        traffic_layout.addLayout(max_time_layout)
        
        traffic_layout.addWidget(QLabel('Number of Profiles to Visit:'))
        self.num_visits_input = QSpinBox()
        self.num_visits_input.setRange(1, 10000)
        self.num_visits_input.setValue(10)
        self.num_visits_input.setToolTip('Number of profiles/pages to visit')
        traffic_layout.addWidget(self.num_visits_input)
        
        traffic_layout.addWidget(QLabel('Threads (concurrent browsers):'))
        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 100)
        self.threads_input.setValue(1)
        traffic_layout.addWidget(self.threads_input)
        
        traffic_layout.addWidget(QLabel('Total Threads to Run (0 = unlimited):'))
        self.total_threads_input = QSpinBox()
        self.total_threads_input.setRange(0, 100000)
        self.total_threads_input.setValue(0)
        self.total_threads_input.setSpecialValueText('Unlimited')
        traffic_layout.addWidget(self.total_threads_input)
        
        traffic_layout.addWidget(QLabel('Content Interaction % (0-100):'))
        self.content_ratio_input = QSpinBox()
        self.content_ratio_input.setRange(0, 100)
        self.content_ratio_input.setValue(85)
        traffic_layout.addWidget(self.content_ratio_input)
        
        traffic_layout.addWidget(QLabel('Sponsored Interaction % (0-100):'))
        self.sponsored_ratio_input = QSpinBox()
        self.sponsored_ratio_input.setRange(0, 100)
        self.sponsored_ratio_input.setValue(15)
        traffic_layout.addWidget(self.sponsored_ratio_input)
        
        traffic_group.setLayout(traffic_layout)
        layout.addWidget(traffic_group)
        
        # Platform Selection
        platform_group = QGroupBox('💻 Platform')
        platform_layout = QVBoxLayout()
        platform_layout.setSpacing(10)
        
        platform_layout.addWidget(QLabel('Select Platform(s):'))
        self.platform_desktop_check = QCheckBox('🖥 Desktop')
        self.platform_desktop_check.setChecked(True)
        platform_layout.addWidget(self.platform_desktop_check)
        
        self.platform_android_check = QCheckBox('📱 Android')
        platform_layout.addWidget(self.platform_android_check)
        
        info_label = QLabel('ℹ️ Select both to mix Desktop and Android browsers')
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
    
    def toggle_search_section(self, checked):
        """Toggle visibility of search settings."""
        self.search_group.setVisible(checked)
    
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
        
        self.enable_text_highlight = QCheckBox('✏️ Enable Text Highlighting')
        self.enable_text_highlight.setChecked(False)
        behavior_layout.addWidget(self.enable_text_highlight)
        
        highlight_info = QLabel('ℹ️ Randomly highlights text like human reading behavior')
        highlight_info.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        highlight_info.setWordWrap(True)
        behavior_layout.addWidget(highlight_info)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Ad Interaction Settings (NEW)
        ad_group = QGroupBox('📺 Ad Interaction (Demo/Test Only)')
        ad_layout = QVBoxLayout()
        ad_layout.setSpacing(10)
        
        self.enable_ad_interaction = QCheckBox('✅ Enable Ad Detection & Interaction')
        self.enable_ad_interaction.setChecked(False)
        ad_layout.addWidget(self.enable_ad_interaction)
        
        ad_info = QLabel('ℹ️ Detects demo/test ads, scrolls to them, waits for load, and views naturally')
        ad_info.setStyleSheet('color: #666; font-style: italic; font-size: 10px;')
        ad_info.setWordWrap(True)
        ad_layout.addWidget(ad_info)
        
        ad_warning = QLabel('⚠️ Only for demo ads - NOT real ad networks (blocked)')
        ad_warning.setStyleSheet('color: #d35400; font-weight: bold; font-size: 10px;')
        ad_warning.setWordWrap(True)
        ad_layout.addWidget(ad_warning)
        
        ad_group.setLayout(ad_layout)
        layout.addWidget(ad_group)
        
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
        
        layout.addStretch()
        
        scroll_area.setWidget(widget)
        return scroll_area
    
    def toggle_page_visit_settings(self, state):
        """Enable/disable page visit inputs based on checkbox state."""
        # PySide6 stateChanged emits int (0=unchecked, 2=checked), compare with enum or value
        enabled = state in (Qt.Checked, Qt.Checked.value)
        self.max_pages_input.setEnabled(enabled)
    
    def validate_time_range(self):
        """Ensure minimum time is not greater than maximum time."""
        min_time = self.min_time_input.value()
        max_time = self.max_time_input.value()
        
        if min_time > max_time:
            # Auto-adjust max to match min if min becomes greater
            self.max_time_input.setValue(min_time)
    
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
        toolbox_layout.addWidget(QLabel('Action Toolbox'))
        
        self.action_toolbox = QListWidget()
        self.action_toolbox.setDragEnabled(True)
        self.action_toolbox.setMaximumWidth(200)
        
        # Add action items with emojis - UPDATED NAMES
        actions = [
            '➕ New Tab',
            '🌐 Access Website',
            '⏱ Time',
            '📜 Scroll',
            '🖱 Click Element',
            '⌨ Input Text',
            '❌ Close Page'
        ]
        for action in actions:
            item = QListWidgetItem(action)
            self.action_toolbox.addItem(item)
        
        toolbox_layout.addWidget(self.action_toolbox)
        visual_layout.addWidget(toolbox_panel)
        
        # Center: Workflow List
        workflow_panel = QWidget()
        workflow_layout = QVBoxLayout(workflow_panel)
        workflow_layout.addWidget(QLabel('Workflow Steps'))
        
        self.workflow_list = QListWidget()
        self.workflow_list.setAcceptDrops(True)
        self.workflow_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.workflow_list.itemClicked.connect(self.on_workflow_item_clicked)
        self.workflow_list.model().rowsMoved.connect(self.sync_visual_to_json)
        
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
        config_layout.addWidget(QLabel('Step Configuration'))
        
        self.step_config_widget = QWidget()
        self.step_config_layout = QFormLayout(self.step_config_widget)
        
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
        
        json_layout.addWidget(QLabel('RPA Script Editor (JSON):'))
        
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
        
        return widget
    
    def start_automation(self):
        """Start the automation process."""
        try:
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
            
            # Get visit type
            visit_type = 'direct'
            if self.visit_referral_radio.isChecked():
                visit_type = 'referral'
            elif self.visit_search_radio.isChecked():
                visit_type = 'search'
            
            # Validate search keyword and target domain if search type is selected
            if visit_type == 'search':
                keyword = self.search_keyword_input.text().strip()
                target_domain = self.target_domain_input.text().strip()
                if not keyword:
                    QMessageBox.warning(self, 'Input Error', 'Please enter a search keyword for Search Visit type')
                    return
                if not target_domain:
                    QMessageBox.warning(self, 'Input Error', 'Please enter a target domain for Search Visit type')
                    return
            
            # Collect referral sources if referral type is selected
            referral_sources = []
            if visit_type == 'referral':
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
                
                if not referral_sources:
                    QMessageBox.warning(self, 'Input Error', 'Please select at least one referral source')
                    return
            
            # Get selected platforms
            selected_platforms = []
            if self.platform_desktop_check.isChecked():
                selected_platforms.append('desktop')
            if self.platform_android_check.isChecked():
                selected_platforms.append('android')
            
            if not selected_platforms:
                QMessageBox.warning(self, 'Input Error', 'Please select at least one platform (Desktop or Android)')
                return
            
            # Collect configuration
            config = {
                'url_list': url_list,
                'num_visits': self.num_visits_input.value(),
                'min_time_spend': self.min_time_input.value(),
                'max_time_spend': self.max_time_input.value(),
                'threads': self.threads_input.value(),
                'total_threads': self.total_threads_input.value(),
                'content_ratio': self.content_ratio_input.value(),
                'sponsored_ratio': self.sponsored_ratio_input.value(),
                'platforms': selected_platforms,
                'headless': False,  # Always False - browser must be visible
                'proxy_enabled': self.proxy_enabled_check.isChecked(),
                'proxy_type': self.proxy_type_combo.currentText(),
                'proxy_list': self.proxy_list_input.toPlainText(),
                'rotate_proxy': True,  # Always rotate for authenticity
                'visit_type': visit_type,
                'search_keyword': self.search_keyword_input.text().strip() if visit_type == 'search' else '',
                'target_domain': self.target_domain_input.text().strip() if visit_type == 'search' else '',
                'referral_sources': referral_sources,
                'enable_interaction': self.enable_interaction.isChecked(),
                'enable_extra_pages': self.enable_extra_pages.isChecked(),
                'max_pages': self.max_pages_input.value(),
                'scroll_depth': self.scroll_depth_input.value(),
                'enable_mouse_movement': self.enable_mouse_movement.isChecked(),
                'enable_idle_pauses': self.enable_idle_pauses.isChecked(),
                'enable_consent': self.enable_consent.isChecked(),
                'enable_popups': self.enable_popups.isChecked(),
                'enable_text_highlight': self.enable_text_highlight.isChecked(),
                'enable_ad_interaction': self.enable_ad_interaction.isChecked(),
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
                self.automation_worker.browser_manager.proxy_manager.rotate_proxy = config['rotate_proxy']
                self.automation_worker.browser_manager.proxy_manager.proxy_list = \
                    self.automation_worker.browser_manager.proxy_manager.parse_proxy_list(config['proxy_list'])
                
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
        """Load RPA script from file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 'Load Script', '', 'JSON Files (*.json)'
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    script_text = f.read()
                
                # Validate JSON
                json.loads(script_text)
                
                # Set the JSON text (this will trigger sync_json_to_visual via textChanged signal)
                self.script_editor.setPlainText(script_text)
                
                QMessageBox.information(self, 'Success', 'Script loaded and synced to Visual Builder successfully')
                
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
            # Scroll configuration with type and speed
            scroll_type_combo = QComboBox()
            scroll_type_combo.addItems(['Smooth', 'Auto'])
            scroll_type_combo.setCurrentText(config.get('scroll_type', 'Smooth'))
            scroll_type_combo.currentTextChanged.connect(lambda text: self.update_step_config(step, 'scroll_type', text))
            self.step_config_layout.addRow('Scroll Type:', scroll_type_combo)
            
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
        """Sync JSON editor to visual builder."""
        if self.syncing:
            return
        
        self.syncing = True
        
        try:
            json_text = self.script_editor.toPlainText().strip()
            if not json_text:
                return
            
            script = json.loads(json_text)
            steps = script.get('steps', [])
            
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
    
    # ========================================================================
    
    def closeEvent(self, event):
        """Handle application close."""
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
    try:
        result = subprocess.run(
            ['playwright', 'install', '--dry-run', 'chromium'],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Check if dry-run succeeded
        if result.returncode == 0:
            return True
    except Exception:
        pass
    
    # Fallback: check if browser exists in cache (any version)
    try:
        home_dir = Path.home()
        playwright_cache = home_dir / '.cache' / 'ms-playwright'
        if playwright_cache.exists():
            # Look for any chromium-* directory
            chromium_dirs = list(playwright_cache.glob('chromium-*'))
            if chromium_dirs:
                return True
    except Exception:
        pass
    
    return False


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Check browser installation
    if not check_browser_installation():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Browser Not Installed')
        msg.setText('Playwright Chromium browser is not installed!')
        msg.setInformativeText(
            'Please install it by running one of these commands in your terminal:\n\n'
            '  playwright install chromium\n'
            '  python -m playwright install chromium\n\n'
            'After installation, restart the application.'
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        return
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = AppGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
