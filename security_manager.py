#!/usr/bin/env python3
"""
Advanced Security Manager for HUMANEX BOT v5.0
Provides enterprise-grade protection against cracking, tampering, and unauthorized use.
"""

import os
import sys
import json
import hashlib
import base64
import time
import uuid
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import hmac
import secrets

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False



class SecurityManager:
    """
    Comprehensive security manager for bot protection.
    
    Features:
    - Hardware ID binding
    - File integrity checking
    - Configuration encryption
    - Anti-tampering measures
    - Rate limiting
    - Secure logging
    """
    
    def __init__(self, app_name: str = "HUMANEX BOT v5.0"):
        self.app_name = app_name
        self.security_dir = Path.home() / f".{app_name.lower()}_security"
        self.security_dir.mkdir(exist_ok=True, parents=True)
        
        self.hwid_file = self.security_dir / "hwid.dat"
        self.config_file = self.security_dir / "config.enc"
        self.integrity_file = self.security_dir / "integrity.json"
        
        self._master_key = None
        self._session_token = None
        self._init_session()
        
    def _init_session(self):
        """Initialize security session."""
        self._session_token = secrets.token_hex(32)
        self._check_environment()
        
    def _check_environment(self):
        """Check if running in a safe environment (not VM, debugger, etc.)."""
        checks = []
        
        # Check for common VM/sandbox indicators
        vm_indicators = [
            'vmware', 'virtualbox', 'qemu', 'xen', 'parallels',
            'virtual', 'sandbox', 'wine'
        ]
        
        system_info = platform.platform().lower()
        for indicator in vm_indicators:
            if indicator in system_info:
                checks.append(f"VM indicator detected: {indicator}")
        
        # Check for debugger (basic check)
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            checks.append("Debugger detected")
        
        # Log checks (but don't block - some users may run in VMs legitimately)
        if checks:
            self._log_security_event("environment_check", {
                "warnings": checks,
                "timestamp": datetime.now().isoformat()
            })
    
    def _log_security_event(self, event_type: str, data: Dict[str, Any]):
        """Log security events securely."""
        log_file = self.security_dir / "security.log"
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "session": self._session_token[:8],  # Only log partial token
            "data": data
        }
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass  # Silent fail for logging
    
    def generate_hardware_id(self) -> str:
        """
        Generate unique hardware ID for this machine.
        Uses multiple system identifiers for uniqueness.
        """
        identifiers = []
        
        # System UUID (best identifier on most systems)
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.check_output("wmic csproduct get uuid", shell=True)
                uuid_line = result.decode().split('\n')[1].strip()
                if uuid_line and uuid_line != "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF":
                    identifiers.append(uuid_line)
            elif platform.system() == "Linux":
                machine_id_files = ['/etc/machine-id', '/var/lib/dbus/machine-id']
                for file_path in machine_id_files:
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            identifiers.append(f.read().strip())
                        break
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                result = subprocess.check_output(
                    ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                    stderr=subprocess.DEVNULL
                )
                for line in result.decode().split('\n'):
                    if 'IOPlatformUUID' in line:
                        uuid_val = line.split('"')[3]
                        identifiers.append(uuid_val)
                        break
        except Exception:
            pass
        
        # Fallback: Use platform info
        if not identifiers:
            identifiers.extend([
                platform.node(),
                platform.machine(),
                platform.processor()
            ])
        
        # Create hash from all identifiers
        combined = "|".join(str(i) for i in identifiers if i)
        hwid = hashlib.sha256(combined.encode()).hexdigest()
        
        # Save HWID
        try:
            with open(self.hwid_file, 'w') as f:
                f.write(hwid)
        except Exception:
            pass
        
        return hwid
    
    def get_hardware_id(self) -> str:
        """Get cached or generate new hardware ID."""
        if self.hwid_file.exists():
            try:
                with open(self.hwid_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        return self.generate_hardware_id()
    
    def encrypt_config(self, config_data: Dict[str, Any], 
                      password: Optional[str] = None) -> bool:
        """
        Encrypt configuration data.
        
        Args:
            config_data: Configuration dictionary to encrypt
            password: Optional password (uses hardware ID if not provided)
            
        Returns:
            True if successful
        """
        if not CRYPTO_AVAILABLE:
            # Fallback: Save as base64 encoded JSON (not secure but better than plain)
            try:
                json_data = json.dumps(config_data)
                encoded = base64.b64encode(json_data.encode()).decode()
                with open(self.config_file, 'w') as f:
                    f.write(encoded)
                return True
            except Exception:
                return False
        
        try:
            # Use password or hardware ID as key source
            key_source = password or self.get_hardware_id()
            
            # Derive encryption key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.app_name.encode(),
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(key_source.encode())
            )
            
            # Encrypt data
            fernet = Fernet(key)
            json_data = json.dumps(config_data)
            encrypted = fernet.encrypt(json_data.encode())
            
            # Save encrypted config
            with open(self.config_file, 'wb') as f:
                f.write(encrypted)
            
            return True
            
        except Exception as e:
            self._log_security_event("encryption_error", {"error": str(e)})
            return False
    
    def decrypt_config(self, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Decrypt configuration data.
        
        Args:
            password: Optional password (uses hardware ID if not provided)
            
        Returns:
            Decrypted configuration dict or None
        """
        if not self.config_file.exists():
            return None
        
        if not CRYPTO_AVAILABLE:
            # Fallback: Decode base64 JSON
            try:
                with open(self.config_file, 'r') as f:
                    encoded = f.read()
                json_data = base64.b64decode(encoded.encode()).decode()
                return json.loads(json_data)
            except Exception:
                return None
        
        try:
            # Use password or hardware ID as key source
            key_source = password or self.get_hardware_id()
            
            # Derive decryption key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.app_name.encode(),
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(key_source.encode())
            )
            
            # Decrypt data
            fernet = Fernet(key)
            with open(self.config_file, 'rb') as f:
                encrypted = f.read()
            
            decrypted = fernet.decrypt(encrypted)
            json_data = decrypted.decode()
            return json.loads(json_data)
            
        except Exception as e:
            self._log_security_event("decryption_error", {"error": str(e)})
            return None
    
    def calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""
    
    def verify_integrity(self, files_to_check: List[str]) -> Dict[str, Any]:
        """
        Verify integrity of critical files.
        
        Args:
            files_to_check: List of file paths to verify
            
        Returns:
            Dict with verification results
        """
        current_checksums = {}
        modified_files = []
        
        # Calculate current checksums
        for file_path in files_to_check:
            if os.path.exists(file_path):
                current_checksums[file_path] = self.calculate_file_checksum(file_path)
        
        # Load stored checksums
        stored_checksums = {}
        if self.integrity_file.exists():
            try:
                with open(self.integrity_file, 'r') as f:
                    stored_checksums = json.load(f)
            except Exception:
                pass
        
        # Compare checksums
        for file_path, checksum in current_checksums.items():
            if file_path in stored_checksums:
                if stored_checksums[file_path] != checksum:
                    modified_files.append(file_path)
        
        # Save current checksums
        try:
            with open(self.integrity_file, 'w') as f:
                json.dump(current_checksums, f, indent=2)
        except Exception:
            pass
        
        if modified_files:
            self._log_security_event("integrity_check_failed", {
                "modified_files": modified_files
            })
        
        return {
            "verified": len(modified_files) == 0,
            "modified_files": modified_files,
            "checked_files": len(current_checksums)
        }
    
    def mask_sensitive_data(self, text: str, 
                           patterns: Optional[List[str]] = None) -> str:
        """
        Mask sensitive data in logs and output.
        
        Args:
            text: Text to mask
            patterns: List of regex patterns to mask (default: common patterns)
            
        Returns:
            Masked text
        """
        import re
        
        if patterns is None:
            patterns = [
                r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
                r'\b[A-Za-z0-9]{32,}\b',  # API keys/tokens (32+ chars)
                r'password["\s:=]+[^\s"]+',  # Passwords
                r'api[_-]?key["\s:=]+[^\s"]+',  # API keys
                r'token["\s:=]+[^\s"]+',  # Tokens
            ]
        
        masked_text = text
        for pattern in patterns:
            masked_text = re.sub(pattern, '[REDACTED]', masked_text, flags=re.IGNORECASE)
        
        return masked_text
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "hardware_id": self.get_hardware_id()[:16] + "...",  # Partial HWID
            "crypto_available": CRYPTO_AVAILABLE,
            "session_active": self._session_token is not None,
            "platform": platform.system(),
            "security_dir": str(self.security_dir.exists())
        }
        
        return status


class RateLimiter:
    """
    Rate limiter to prevent abuse.
    """
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        now = time.time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        # Check if under limit
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def get_wait_time(self) -> float:
        """Get time to wait before next request is allowed."""
        if not self.requests:
            return 0.0
        
        oldest_request = min(self.requests)
        elapsed = time.time() - oldest_request
        
        if elapsed >= self.time_window:
            return 0.0
        
        return self.time_window - elapsed


# Convenience functions for easy integration
def create_security_manager(app_name: str = "HUMANEX BOT v5.0") -> SecurityManager:
    """Create and initialize security manager."""
    return SecurityManager(app_name)


if __name__ == "__main__":
    # Demo usage
    print("=== Advanced Security Manager Demo ===\n")
    
    security = SecurityManager()
    
    # Generate hardware ID
    hwid = security.get_hardware_id()
    print(f"Hardware ID: {hwid[:32]}...")
    
    # Test encryption
    test_config = {
        "proxy": "192.168.1.1:8080",
        "api_key": "secret_key_12345",
        "user": "admin"
    }
    
    print(f"\nEncryption Test:")
    if security.encrypt_config(test_config):
        print("  Config encrypted successfully")
        decrypted = security.decrypt_config()
        if decrypted == test_config:
            print("  Config decrypted successfully")
        else:
            print("  Decryption failed!")
    
    # Security status
    status = security.get_security_status()
    print(f"\nSecurity Status:")
    print(f"  Platform: {status['platform']}")
    print(f"  Crypto Available: {status['crypto_available']}")
    
    print("\n=== Demo Complete ===")
