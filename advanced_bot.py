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
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTabWidget, QGroupBox, QListWidget,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QScrollArea, QListWidgetItem, QFormLayout,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont, QColor

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
        """Scroll page with human-like behavior."""
        try:
            if depth_percent is None:
                depth_percent = random.randint(30, 100)
            
            # Get page height
            page_height = await page.evaluate('document.documentElement.scrollHeight')
            target_scroll = int(page_height * (depth_percent / 100))
            
            # Scroll in steps with variable speed using smooth scrolling
            current_position = 0
            while current_position < target_scroll:
                step = random.randint(100, 300)
                current_position = min(current_position + step, target_scroll)
                
                # Use smooth scrolling behavior
                await page.evaluate(f'''
                    window.scrollTo({{
                        top: {current_position},
                        behavior: 'smooth'
                    }})
                ''')
                await asyncio.sleep(random.uniform(0.1, 0.4))
            
            # Random idle pause
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
        """Parse proxy list from text input."""
        proxies = []
        lines = proxy_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            proxy_config = {}
            
            # Check for user:pass@ip:port format
            if '@' in line:
                auth_part, server_part = line.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                    proxy_config['username'] = username
                    proxy_config['password'] = password
                
                # Build server URL
                if ':' in server_part:
                    ip, port = server_part.rsplit(':', 1)
                    proxy_config['server'] = f"{self.proxy_type.lower()}://{ip}:{port}"
            else:
                # Simple ip:port format
                if ':' in line:
                    ip, port = line.rsplit(':', 1)
                    proxy_config['server'] = f"{self.proxy_type.lower()}://{ip}:{port}"
            
            if proxy_config.get('server'):
                proxies.append(proxy_config)
        
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
            self.log_manager.log('Initializing Playwright...')
            self.playwright = await async_playwright().start()
            
            launch_options = {
                'headless': self.headless,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            }
            
            # Note: Proxy is now set per-context, not per-browser
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            self.log_manager.log('Browser launched successfully')
            
            return True
            
        except Exception as e:
            self.log_manager.log(f'Browser initialization error: {e}', 'ERROR')
            return False
    
    async def create_context(self, platform: str = 'desktop', use_proxy: bool = True) -> Optional[BrowserContext]:
        """Create a new browser context with fingerprinting and optional proxy."""
        try:
            if not self.browser:
                await self.initialize()
            
            # Generate fingerprint
            self.fingerprint_manager.platform = platform
            fingerprint = self.fingerprint_manager.generate_fingerprint()
            
            self.log_manager.log(f'Creating context with {platform} fingerprint')
            
            context_options = {
                'user_agent': fingerprint['user_agent'],
                'viewport': fingerprint['viewport'],
                'locale': fingerprint['locale'],
                'timezone_id': fingerprint['timezone'],
            }
            
            # Add proxy if enabled and configured
            if use_proxy:
                proxy_config = self.proxy_manager.get_proxy_config()
                if proxy_config:
                    context_options['proxy'] = proxy_config
                    server = proxy_config.get('server', 'unknown')
                    self.log_manager.log(f'Using proxy: {server}')
            
            self.context = await self.browser.new_context(**context_options)
            
            # Inject navigator properties
            await self.context.add_init_script(f"""
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint['hardware_concurrency']}
                }});
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined
                }});
            """)
            
            self.log_manager.log('Browser context created')
            return self.context
            
        except Exception as e:
            self.log_manager.log(f'Context creation error: {e}', 'ERROR')
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
    
    async def run_automation(self):
        """Main automation loop with session isolation and stability improvements."""
        try:
            self.running = True
            self.emit_log('Starting automation...')
            
            # Initialize browser
            platform = self.config.get('platform', 'desktop')
            self.browser_manager.headless = self.config.get('headless', False)
            
            success = await self.browser_manager.initialize()
            if not success:
                self.emit_log('Failed to initialize browser', 'ERROR')
                return
            
            # Create managers
            consent_manager = ConsentManager(self.log_manager)
            sponsored_engine = SponsoredClickEngine(self.log_manager)
            
            # Get configuration
            target_url = self.config.get('url', '')
            num_visits = self.config.get('num_visits', 1)
            content_ratio = self.config.get('content_ratio', 85) / 100
            sponsored_ratio = self.config.get('sponsored_ratio', 15) / 100
            
            # Failure tracking for browser restart
            consecutive_failures = 0
            max_failures_before_restart = 3
            
            # Run visits with session isolation
            for visit in range(num_visits):
                if not self.running:
                    self.emit_log('Stop requested, exiting gracefully...')
                    break
                
                self.emit_log(f'━━━ Visit {visit + 1}/{num_visits} ━━━')
                
                context = None
                page = None
                
                try:
                    # Create new context for this visit (session isolation)
                    context = await self.browser_manager.create_context(platform)
                    if not context:
                        self.emit_log('Failed to create browser context', 'ERROR')
                        consecutive_failures += 1
                        
                        # Restart browser if too many failures
                        if consecutive_failures >= max_failures_before_restart:
                            self.emit_log(f'Too many failures ({consecutive_failures}), restarting browser...')
                            await self.browser_manager.close()
                            await asyncio.sleep(2)
                            success = await self.browser_manager.initialize()
                            if not success:
                                self.emit_log('Browser restart failed', 'ERROR')
                                break
                            consecutive_failures = 0
                        
                        continue
                    
                    # Create new page
                    page = await context.new_page()
                    
                    # Navigate
                    self.emit_log(f'Navigating to {target_url}')
                    await page.goto(target_url, wait_until='domcontentloaded', timeout=30000)
                    
                    # Handle consents
                    await consent_manager.handle_consents(page)
                    
                    # Random scroll
                    await HumanBehavior.scroll_page(page)
                    
                    # Idle pause
                    await HumanBehavior.idle_pause()
                    
                    # Decide on interaction type based on ratio
                    if random.random() < sponsored_ratio:
                        # Try sponsored click
                        await sponsored_engine.click_sponsored_content(page, 1.0)
                    else:
                        # Regular content interaction
                        self.emit_log('Performing content interaction')
                        await HumanBehavior.scroll_page(page, random.randint(50, 100))
                    
                    # Idle before closing
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    # Close page
                    if page:
                        await page.close()
                    
                    self.emit_log(f'✓ Visit {visit + 1} completed successfully')
                    
                    # Reset failure counter on success
                    consecutive_failures = 0
                    
                    # Delay between visits
                    if visit < num_visits - 1 and self.running:
                        delay = random.uniform(2, 5)
                        await asyncio.sleep(delay)
                
                except Exception as e:
                    self.emit_log(f'✗ Visit {visit + 1} error: {e}', 'ERROR')
                    consecutive_failures += 1
                    
                    # Restart browser if too many failures
                    if consecutive_failures >= max_failures_before_restart:
                        self.emit_log(f'Too many failures ({consecutive_failures}), restarting browser...')
                        await self.browser_manager.close()
                        await asyncio.sleep(2)
                        success = await self.browser_manager.initialize()
                        if not success:
                            self.emit_log('Browser restart failed', 'ERROR')
                            break
                        consecutive_failures = 0
                
                finally:
                    # Always close context after visit (session isolation)
                    if context:
                        try:
                            await context.close()
                            self.emit_log(f'Context closed for visit {visit + 1}')
                        except Exception as e:
                            self.emit_log(f'Error closing context: {e}', 'ERROR')
            
            # Cleanup
            await self.browser_manager.close()
            self.emit_log('Automation completed')
            
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
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Windows Desktop Automation System')
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Navigation + Settings
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Logs + Control
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
    
    def create_left_panel(self) -> QWidget:
        """Create left settings panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel('Configuration')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Website & Traffic
        tabs.addTab(self.create_website_tab(), 'Website & Traffic')
        
        # Tab 2: Behavior Settings
        tabs.addTab(self.create_behavior_tab(), 'Behavior')
        
        # Tab 3: Proxy Settings
        tabs.addTab(self.create_proxy_tab(), 'Proxy Settings')
        
        # Tab 4: Sponsored Content
        tabs.addTab(self.create_sponsored_tab(), 'Sponsored Content')
        
        # Tab 5: RPA Script
        tabs.addTab(self.create_script_tab(), 'RPA Script')
        
        layout.addWidget(tabs)
        
        return panel
    
    def create_website_tab(self) -> QWidget:
        """Create website configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Website URL
        url_group = QGroupBox('Website Configuration')
        url_layout = QVBoxLayout()
        
        url_layout.addWidget(QLabel('Target URL:'))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://example.com')
        url_layout.addWidget(self.url_input)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Traffic Settings
        traffic_group = QGroupBox('Traffic Settings')
        traffic_layout = QVBoxLayout()
        
        traffic_layout.addWidget(QLabel('Number of Visits:'))
        self.num_visits_input = QSpinBox()
        self.num_visits_input.setRange(1, 1000)
        self.num_visits_input.setValue(10)
        traffic_layout.addWidget(self.num_visits_input)
        
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
        platform_group = QGroupBox('Platform')
        platform_layout = QVBoxLayout()
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(['desktop', 'android'])
        platform_layout.addWidget(self.platform_combo)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)
        
        layout.addStretch()
        
        return widget
    
    def create_behavior_tab(self) -> QWidget:
        """Create behavior settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Browser Settings
        browser_group = QGroupBox('Browser Settings')
        browser_layout = QVBoxLayout()
        
        # Note: Browser always runs in visible mode (headless=False)
        info_label = QLabel('ℹ️ Browser always runs in visible mode for monitoring')
        info_label.setStyleSheet('color: #666; font-style: italic;')
        browser_layout.addWidget(info_label)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Human Behavior
        behavior_group = QGroupBox('Human Behavior')
        behavior_layout = QVBoxLayout()
        
        behavior_layout.addWidget(QLabel('Scroll Depth % (30-100):'))
        self.scroll_depth_input = QSpinBox()
        self.scroll_depth_input.setRange(30, 100)
        self.scroll_depth_input.setValue(70)
        behavior_layout.addWidget(self.scroll_depth_input)
        
        self.enable_mouse_movement = QCheckBox('Enable Mouse Movement Simulation')
        self.enable_mouse_movement.setChecked(True)
        behavior_layout.addWidget(self.enable_mouse_movement)
        
        self.enable_idle_pauses = QCheckBox('Enable Idle Pauses')
        self.enable_idle_pauses.setChecked(True)
        behavior_layout.addWidget(self.enable_idle_pauses)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Consent Manager
        consent_group = QGroupBox('Consent & Popup Handler')
        consent_layout = QVBoxLayout()
        
        self.enable_consent = QCheckBox('Auto-handle Cookie Banners')
        self.enable_consent.setChecked(True)
        consent_layout.addWidget(self.enable_consent)
        
        self.enable_popups = QCheckBox('Auto-handle Popups')
        self.enable_popups.setChecked(True)
        consent_layout.addWidget(self.enable_popups)
        
        consent_group.setLayout(consent_layout)
        layout.addWidget(consent_group)
        
        layout.addStretch()
        
        return widget
    
    def create_proxy_tab(self) -> QWidget:
        """Create proxy settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Enable Proxy
        proxy_enable_group = QGroupBox('Proxy Configuration')
        proxy_enable_layout = QVBoxLayout()
        
        self.proxy_enabled_check = QCheckBox('Enable Proxy')
        self.proxy_enabled_check.setChecked(False)
        self.proxy_enabled_check.stateChanged.connect(self.toggle_proxy_inputs)
        proxy_enable_layout.addWidget(self.proxy_enabled_check)
        
        proxy_enable_group.setLayout(proxy_enable_layout)
        layout.addWidget(proxy_enable_group)
        
        # Proxy Type
        proxy_type_group = QGroupBox('Proxy Type')
        proxy_type_layout = QVBoxLayout()
        
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(['HTTP', 'HTTPS', 'SOCKS5'])
        self.proxy_type_combo.setEnabled(False)
        proxy_type_layout.addWidget(self.proxy_type_combo)
        
        proxy_type_group.setLayout(proxy_type_layout)
        layout.addWidget(proxy_type_group)
        
        # Proxy List
        proxy_list_group = QGroupBox('Proxy List')
        proxy_list_layout = QVBoxLayout()
        
        proxy_list_layout.addWidget(QLabel('Enter proxies (one per line):'))
        proxy_list_layout.addWidget(QLabel('Formats: ip:port or user:pass@ip:port'))
        
        self.proxy_list_input = QTextEdit()
        self.proxy_list_input.setPlaceholderText('127.0.0.1:8080\nuser:pass@192.168.1.1:3128\n10.0.0.1:1080')
        self.proxy_list_input.setMaximumHeight(150)
        self.proxy_list_input.setEnabled(False)
        proxy_list_layout.addWidget(self.proxy_list_input)
        
        proxy_list_group.setLayout(proxy_list_layout)
        layout.addWidget(proxy_list_group)
        
        # Rotation Settings
        rotation_group = QGroupBox('Rotation Settings')
        rotation_layout = QVBoxLayout()
        
        self.rotate_proxy_check = QCheckBox('Rotate proxy per session')
        self.rotate_proxy_check.setChecked(True)
        self.rotate_proxy_check.setEnabled(False)
        rotation_layout.addWidget(self.rotate_proxy_check)
        
        rotation_group.setLayout(rotation_layout)
        layout.addWidget(rotation_group)
        
        layout.addStretch()
        
        return widget
    
    def toggle_proxy_inputs(self, state):
        """Enable/disable proxy inputs based on checkbox state."""
        enabled = state == Qt.Checked
        self.proxy_type_combo.setEnabled(enabled)
        self.proxy_list_input.setEnabled(enabled)
        self.rotate_proxy_check.setEnabled(enabled)
    
    def create_sponsored_tab(self) -> QWidget:
        """Create sponsored content tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Safety Rules
        safety_group = QGroupBox('Safety Rules')
        safety_layout = QVBoxLayout()
        
        safety_layout.addWidget(QLabel('⚠️ Ad Network Blocklist:'))
        
        self.blocklist_display = QTextEdit()
        self.blocklist_display.setReadOnly(True)
        self.blocklist_display.setMaximumHeight(150)
        self.blocklist_display.setText('\n'.join(AD_NETWORK_BLOCKLIST))
        safety_layout.addWidget(self.blocklist_display)
        
        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)
        
        # Detection Rules
        detection_group = QGroupBox('Sponsored Element Detection')
        detection_layout = QVBoxLayout()
        
        detection_layout.addWidget(QLabel('Safe Selectors:'))
        self.selectors_display = QTextEdit()
        self.selectors_display.setReadOnly(True)
        self.selectors_display.setMaximumHeight(150)
        self.selectors_display.setText('\n'.join(SPONSORED_SELECTORS))
        detection_layout.addWidget(self.selectors_display)
        
        detection_layout.addWidget(QLabel('Confidence Threshold (0.0-1.0):'))
        self.confidence_input = QDoubleSpinBox()
        self.confidence_input.setRange(0.0, 1.0)
        self.confidence_input.setSingleStep(0.1)
        self.confidence_input.setValue(0.7)
        detection_layout.addWidget(self.confidence_input)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        layout.addStretch()
        
        return widget
    
    def create_script_tab(self) -> QWidget:
        """Create RPA script tab with visual builder and JSON editor."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        
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
        
        # Add action items
        actions = [
            'Open Page',
            'Navigate',
            'Wait',
            'Scroll',
            'Click Element',
            'Input Text',
            'Close Page'
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
        
        add_step_btn = QPushButton('Add Step')
        add_step_btn.clicked.connect(self.add_workflow_step)
        workflow_btn_layout.addWidget(add_step_btn)
        
        remove_step_btn = QPushButton('Remove Step')
        remove_step_btn.clicked.connect(self.remove_workflow_step)
        workflow_btn_layout.addWidget(remove_step_btn)
        
        clear_workflow_btn = QPushButton('Clear All')
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
        
        save_btn = QPushButton('Save Script')
        save_btn.clicked.connect(self.save_script)
        btn_layout.addWidget(save_btn)
        
        load_btn = QPushButton('Load Script')
        load_btn.clicked.connect(self.load_script)
        btn_layout.addWidget(load_btn)
        
        sync_btn = QPushButton('Sync Visual ↔ JSON')
        sync_btn.clicked.connect(self.force_sync)
        btn_layout.addWidget(sync_btn)
        
        main_layout.addLayout(btn_layout)
        
        # Initialize workflow data storage
        self.workflow_steps = []
        self.syncing = False  # Prevent recursive syncing
        
        return widget
    
    def create_right_panel(self) -> QWidget:
        """Create right control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel('Control & Logs')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('Start Automation')
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px;')
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('Stop')
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet('background-color: #f44336; color: white; padding: 10px;')
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # Status
        self.status_label = QLabel('Status: Ready')
        self.status_label.setStyleSheet('padding: 5px; background-color: #e0e0e0;')
        layout.addWidget(self.status_label)
        
        # Logs
        layout.addWidget(QLabel('Live Logs:'))
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet('background-color: #1e1e1e; color: #00ff00; font-family: monospace;')
        layout.addWidget(self.log_display)
        
        # Clear logs button
        clear_btn = QPushButton('Clear Logs')
        clear_btn.clicked.connect(self.clear_logs)
        layout.addWidget(clear_btn)
        
        return panel
    
    def start_automation(self):
        """Start the automation process."""
        try:
            # Validate inputs
            url = self.url_input.text().strip()
            if not url:
                QMessageBox.warning(self, 'Input Error', 'Please enter a target URL')
                return
            
            # Collect configuration
            config = {
                'url': url,
                'num_visits': self.num_visits_input.value(),
                'content_ratio': self.content_ratio_input.value(),
                'sponsored_ratio': self.sponsored_ratio_input.value(),
                'platform': self.platform_combo.currentText(),
                'headless': False,  # Always False - browser must be visible
                'proxy_enabled': self.proxy_enabled_check.isChecked(),
                'proxy_type': self.proxy_type_combo.currentText(),
                'proxy_list': self.proxy_list_input.toPlainText(),
                'rotate_proxy': self.rotate_proxy_check.isChecked(),
            }
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText('Status: Running...')
            self.status_label.setStyleSheet('padding: 5px; background-color: #4CAF50; color: white;')
            
            # Create and start worker thread
            self.automation_thread = QThread()
            self.automation_worker = AutomationWorker(config, self.log_manager)
            
            # Configure proxy manager
            if config['proxy_enabled'] and config['proxy_list'].strip():
                self.automation_worker.browser_manager.proxy_manager.proxy_enabled = True
                self.automation_worker.browser_manager.proxy_manager.proxy_type = config['proxy_type']
                self.automation_worker.browser_manager.proxy_manager.rotate_proxy = config['rotate_proxy']
                self.automation_worker.browser_manager.proxy_manager.proxy_list = \
                    self.automation_worker.browser_manager.proxy_manager.parse_proxy_list(config['proxy_list'])
            
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
        self.status_label.setText('Status: Ready')
        self.status_label.setStyleSheet('padding: 5px; background-color: #e0e0e0;')
        
        if self.automation_thread:
            self.automation_thread.quit()
            self.automation_thread.wait()
            self.automation_thread = None
        
        self.automation_worker = None
    
    def append_log(self, log_entry: str):
        """Append log to display."""
        self.log_display.append(log_entry)
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
                
                self.script_editor.setPlainText(script_text)
                QMessageBox.information(self, 'Success', 'Script loaded successfully')
                
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
            url_input = QLineEdit(config.get('url', ''))
            url_input.textChanged.connect(lambda text: self.update_step_config(step, 'url', text))
            self.step_config_layout.addRow('URL:', url_input)
        
        elif step_type == 'wait':
            duration_input = QSpinBox()
            duration_input.setRange(100, 60000)
            duration_input.setValue(config.get('duration', 2000))
            duration_input.valueChanged.connect(lambda val: self.update_step_config(step, 'duration', val))
            self.step_config_layout.addRow('Duration (ms):', duration_input)
        
        elif step_type == 'scroll':
            depth_input = QSpinBox()
            depth_input.setRange(0, 100)
            depth_input.setValue(config.get('depth', 50))
            depth_input.valueChanged.connect(lambda val: self.update_step_config(step, 'depth', val))
            self.step_config_layout.addRow('Depth (%):', depth_input)
        
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
        """Force synchronization between visual and JSON."""
        self.sync_visual_to_json()
        QMessageBox.information(self, 'Sync', 'Visual builder synced to JSON')
    
    def action_to_step_type(self, action_name: str) -> str:
        """Convert action name to step type."""
        mapping = {
            'Open Page': 'newPage',
            'Navigate': 'navigate',
            'Wait': 'wait',
            'Scroll': 'scroll',
            'Click Element': 'click',
            'Input Text': 'input',
            'Close Page': 'closePage'
        }
        return mapping.get(action_name, 'unknown')
    
    def step_type_to_action(self, step_type: str) -> str:
        """Convert step type to action name."""
        mapping = {
            'newPage': 'Open Page',
            'navigate': 'Navigate',
            'wait': 'Wait',
            'scroll': 'Scroll',
            'click': 'Click Element',
            'input': 'Input Text',
            'closePage': 'Close Page'
        }
        return mapping.get(step_type, step_type)
    
    def get_default_config(self, step_type: str) -> Dict[str, Any]:
        """Get default configuration for step type."""
        defaults = {
            'navigate': {'url': 'https://example.com'},
            'wait': {'duration': 2000},
            'scroll': {'depth': 50},
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

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = AppGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
