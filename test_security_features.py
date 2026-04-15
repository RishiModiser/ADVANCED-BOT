#!/usr/bin/env python3
"""
Security Manager Test Suite
Tests for advanced security features in ADVANCED-BOT
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security_manager import (
    SecurityManager,
    RateLimiter,
    create_security_manager
)


class TestSecurityManager:
    """Test suite for SecurityManager class."""
    
    def __init__(self):
        self.test_count = 0
        self.passed = 0
        self.failed = 0
        self.temp_dir = None
        
    def setup(self):
        """Setup test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="security_test_")
        print(f"Test directory: {self.temp_dir}")
        
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up: {self.temp_dir}")
    
    def assert_true(self, condition, message):
        """Assert that condition is true."""
        self.test_count += 1
        if condition:
            self.passed += 1
            print(f"  ✓ {message}")
            return True
        else:
            self.failed += 1
            print(f"  ✗ {message}")
            return False
    
    def assert_false(self, condition, message):
        """Assert that condition is false."""
        return self.assert_true(not condition, message)
    
    def assert_equal(self, actual, expected, message):
        """Assert that actual equals expected."""
        condition = actual == expected
        if not condition:
            print(f"    Expected: {expected}")
            print(f"    Got: {actual}")
        return self.assert_true(condition, message)
    
    def test_hardware_id_generation(self):
        """Test hardware ID generation."""
        print("\n[TEST] Hardware ID Generation")
        
        security = SecurityManager(app_name="TEST_BOT")
        
        # Test that hardware ID is generated
        hwid = security.get_hardware_id()
        self.assert_true(len(hwid) > 0, "Hardware ID is generated")
        self.assert_true(len(hwid) == 64, "Hardware ID is 64 characters (SHA-256)")
        
        # Test that hardware ID is consistent
        hwid2 = security.get_hardware_id()
        self.assert_equal(hwid, hwid2, "Hardware ID is consistent")
    
    def test_config_encryption(self):
        """Test configuration encryption and decryption."""
        print("\n[TEST] Configuration Encryption")
        
        security = SecurityManager(app_name="TEST_BOT")
        
        # Test config data
        test_config = {
            "api_key": "secret_key_12345",
            "proxy": "192.168.1.100:8080:user:pass",
            "nested": {
                "value": "test"
            }
        }
        
        # Encrypt
        result = security.encrypt_config(test_config)
        self.assert_true(result, "Config encryption succeeds")
        
        # Decrypt
        decrypted = security.decrypt_config()
        self.assert_equal(
            decrypted,
            test_config,
            "Decrypted config matches original"
        )
    
    def test_config_encryption_with_password(self):
        """Test configuration encryption with custom password."""
        print("\n[TEST] Configuration Encryption with Password")
        
        security = SecurityManager(app_name="TEST_BOT")
        
        test_config = {"secret": "value123"}
        password = "my_secure_password"
        
        # Encrypt with password
        result = security.encrypt_config(test_config, password=password)
        self.assert_true(result, "Config encryption with password succeeds")
        
        # Decrypt with correct password
        decrypted = security.decrypt_config(password=password)
        self.assert_equal(
            decrypted,
            test_config,
            "Decryption with correct password works"
        )
        
        # Decrypt with wrong password should fail
        decrypted_wrong = security.decrypt_config(password="wrong_password")
        self.assert_true(
            decrypted_wrong is None,
            "Decryption with wrong password fails"
        )
    
    def test_file_integrity_checking(self):
        """Test file integrity verification."""
        print("\n[TEST] File Integrity Checking")
        
        security = SecurityManager(app_name="TEST_BOT")
        
        # Create test files in temp directory
        test_file1 = os.path.join(self.temp_dir, "test1.txt")
        test_file2 = os.path.join(self.temp_dir, "test2.txt")
        
        with open(test_file1, 'w') as f:
            f.write("Test content 1")
        with open(test_file2, 'w') as f:
            f.write("Test content 2")
        
        # First integrity check (establish baseline)
        result1 = security.verify_integrity([test_file1, test_file2])
        self.assert_true(result1['verified'], "Initial integrity check passes")
        self.assert_equal(
            result1['checked_files'],
            2,
            "Two files checked"
        )
        
        # Second check without changes
        result2 = security.verify_integrity([test_file1, test_file2])
        self.assert_true(result2['verified'], "Integrity check passes with no changes")
        
        # Modify a file
        with open(test_file1, 'w') as f:
            f.write("Modified content")
        
        # Check should detect modification
        result3 = security.verify_integrity([test_file1, test_file2])
        self.assert_false(
            result3['verified'],
            "Integrity check detects modification"
        )
        self.assert_true(
            test_file1 in result3['modified_files'],
            "Modified file is identified"
        )
    
    def test_sensitive_data_masking(self):
        """Test sensitive data masking in logs."""
        print("\n[TEST] Sensitive Data Masking")
        
        security = SecurityManager(app_name="TEST_BOT")
        
        # Test IP address masking
        text1 = "Connect to 192.168.1.100 server"
        masked1 = security.mask_sensitive_data(text1)
        self.assert_true(
            "[REDACTED]" in masked1,
            "IP address is masked"
        )
        self.assert_false(
            "192.168.1.100" in masked1,
            "Original IP is not in masked text"
        )
        
        # Test password masking
        text2 = "password: secret123"
        masked2 = security.mask_sensitive_data(text2)
        self.assert_true(
            "[REDACTED]" in masked2,
            "Password is masked"
        )
        
        # Test API key masking
        text3 = "api_key: abcdef1234567890abcdef1234567890"
        masked3 = security.mask_sensitive_data(text3)
        self.assert_true(
            "[REDACTED]" in masked3,
            "API key is masked"
        )
    
    def test_security_status(self):
        """Test security status reporting."""
        print("\n[TEST] Security Status")
        
        security = SecurityManager(app_name="TEST_BOT")
        
        status = security.get_security_status()
        
        self.assert_true('timestamp' in status, "Status has timestamp")
        self.assert_true('hardware_id' in status, "Status has hardware ID")
        self.assert_true('platform' in status, "Status has platform info")
        self.assert_true(
            isinstance(status['crypto_available'], bool),
            "Status has crypto availability flag"
        )
    
    def test_rate_limiter(self):
        """Test rate limiting functionality."""
        print("\n[TEST] Rate Limiter")
        
        # Create limiter allowing 3 requests per 2 seconds
        limiter = RateLimiter(max_requests=3, time_window=2)
        
        # First 3 requests should be allowed
        self.assert_true(limiter.is_allowed(), "Request 1 allowed")
        self.assert_true(limiter.is_allowed(), "Request 2 allowed")
        self.assert_true(limiter.is_allowed(), "Request 3 allowed")
        
        # 4th request should be blocked
        self.assert_false(limiter.is_allowed(), "Request 4 blocked")
        
        # Check wait time
        wait_time = limiter.get_wait_time()
        self.assert_true(
            wait_time > 0 and wait_time <= 2,
            f"Wait time is reasonable: {wait_time}s"
        )
        
        # Wait and try again
        import time
        time.sleep(2.1)
        
        # Should be allowed again
        self.assert_true(limiter.is_allowed(), "Request allowed after wait")
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("SECURITY MANAGER TEST SUITE")
        print("="*70)
        
        self.setup()
        
        try:
            # Run all tests
            self.test_hardware_id_generation()
            self.test_config_encryption()
            self.test_config_encryption_with_password()
            self.test_file_integrity_checking()
            self.test_sensitive_data_masking()
            self.test_security_status()
            self.test_rate_limiter()
            
        finally:
            self.teardown()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed} ✓")
        print(f"Failed: {self.failed} ✗")
        print(f"Success Rate: {(self.passed/self.test_count*100):.1f}%")
        print("="*70)
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestSecurityManager()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
