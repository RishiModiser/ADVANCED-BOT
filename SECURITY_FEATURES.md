# Advanced Security Features

This document describes the advanced security features implemented in ADVANCED-BOT to protect against cracking, tampering, and unauthorized use.

## 🛡️ Security Overview

The bot now includes enterprise-grade security measures to prevent:
- Unauthorized access and usage
- Reverse engineering and code cracking
- Configuration and credential theft
- System tampering and integrity violations
- Rate limiting abuse
- Data exposure in logs

## 🔐 Security Features

### 1. Hardware ID Binding

**Purpose**: Generate unique hardware fingerprint for security features.

**Features**:
- Unique hardware fingerprint generation
- Multi-platform support (Windows, Linux, macOS)
- Persistent hardware ID storage
- Automatic fallback for different systems

**How it works**:
- Generates unique ID from system identifiers (UUID, machine ID, etc.)
- Stored securely in user's home directory

### 2. Configuration Encryption

**Purpose**: Protect sensitive data like API keys, proxies, and credentials.

**Features**:
- AES encryption using cryptography library
- Password-based key derivation (PBKDF2)
- Hardware-bound encryption (uses hardware ID as key)
- Optional custom password support

**How it works**:
- Sensitive configurations are encrypted before storage
- Decryption requires the same hardware or password
- Prevents credential theft if files are accessed

**Usage**:
```python
# Encrypt configuration
security.encrypt_config({
    "proxy": "192.168.1.1:8080:user:pass",
    "api_key": "secret_key_12345"
})

# Decrypt configuration
config = security.decrypt_config()
```

### 3. File Integrity Checking

**Purpose**: Detect tampering with bot files and prevent modified versions.

**Features**:
- SHA-256 checksums for critical files
- Automatic integrity verification
- Tamper detection and logging
- Baseline establishment on first run

**How it works**:
- Calculates checksums of important files
- Stores checksums securely
- Compares on each run to detect modifications
- Logs any detected changes

### 4. Rate Limiting

**Purpose**: Prevent abuse and ensure system stability.

**Features**:
- Configurable request limits (default: 100 starts per minute)
- Time-window based limiting
- Automatic cooldown calculation
- User-friendly error messages

**How it works**:
- Tracks automation start requests
- Blocks excessive requests within time window
- Shows remaining wait time to user

### 5. Secure Logging

**Purpose**: Protect sensitive information in logs.

**Features**:
- Automatic masking of sensitive data
- IP address masking
- Credential redaction
- Pattern-based filtering

**Masked data types**:
- IP addresses (shows only first and last octet)
- Email addresses
- API keys and tokens
- Passwords and authentication data
- Proxy credentials

**Example**:
```
Before: Proxy: http://192.168.1.100:8080 (user:secretpass)
After:  Proxy: http://192.*.*.100:8080 [AUTH]
```

### 6. Environment Validation

**Purpose**: Detect suspicious execution environments.

**Features**:
- VM/Sandbox detection
- Debugger detection
- Platform verification
- Security event logging

**Detected environments**:
- VirtualBox, VMware, QEMU
- Wine compatibility layer
- Common sandboxes
- Debugger presence

**Note**: Detection doesn't block execution but logs warnings for monitoring.

### 7. Session Security

**Purpose**: Track and secure individual bot sessions.

**Features**:
- Unique session tokens
- Session-based logging
- Secure session initialization
- Anti-replay measures

### 8. Cryptographic Security

**Purpose**: Ensure data integrity and authenticity.

**Features**:
- HMAC-based signatures
- SHA-256 hashing
- Secure random generation
- Base64 encoding for safe transport

**Libraries used**:
- `cryptography`: Industry-standard encryption
- `secrets`: Cryptographically secure random generation
- `hashlib`: SHA-256 and other hash functions
- `hmac`: Message authentication codes

## 📋 Security Manager API

### Initialization

```python
from security_manager import SecurityManager

# Initialize security manager
security = SecurityManager(app_name="ADVANCED-BOT")
```

### Configuration Encryption

```python
# Encrypt sensitive config
config_data = {
    "api_key": "secret_key",
    "proxy_credentials": "user:pass"
}
security.encrypt_config(config_data)

# Decrypt config
decrypted = security.decrypt_config()
```

### Integrity Checking

```python
# Verify file integrity
files_to_check = [
    'advanced_bot.py',
    'security_manager.py'
]
result = security.verify_integrity(files_to_check)

if result['verified']:
    print("All files verified")
else:
    print(f"Modified files: {result['modified_files']}")
```

### Secure Logging

```python
# Mask sensitive data
masked = security.mask_sensitive_data(
    "Connect to 192.168.1.100 with password: secret123"
)
# Output: "Connect to [REDACTED] with [REDACTED]"
```

### Rate Limiting

```python
from security_manager import RateLimiter

# Create rate limiter (100 requests per 60 seconds)
limiter = RateLimiter(max_requests=100, time_window=60)

# Check if request is allowed
if limiter.is_allowed():
    # Process request
    pass
else:
    wait_time = limiter.get_wait_time()
    print(f"Rate limited. Wait {wait_time} seconds")
```

## 🔧 Configuration

### Security Directory

All security files are stored in:
- **Windows**: `C:\Users\<username>\.advanced-bot_security\`
- **Linux/Mac**: `/home/<username>/.advanced-bot_security/`

### Security Files

| File | Purpose |
|------|---------|
| `hwid.dat` | Hardware ID |
| `config.enc` | Encrypted configuration |
| `integrity.json` | File checksums |
| `security.log` | Security event log |

### Environment Variables

No environment variables are required. All configuration is automatic.

## 🚀 Installation

The security features are automatically enabled when the required dependencies are installed:

```bash
pip install -r requirements.txt
```

Required dependencies:
- `cryptography>=41.0.0` - For encryption and key derivation

If the cryptography library is not installed, the bot will:
- Use base64 encoding as fallback (less secure)
- Show warnings about limited security
- Continue to function with basic protection

## 🎯 Best Practices

### For Developers

1. **Keep security_manager.py updated** with latest security patches
2. **Use encrypted config** for all sensitive data
3. **Enable integrity checking** for critical files
4. **Mask sensitive data** in all logs

### For Users

1. **Report suspicious activity** - check security.log regularly
2. **Update regularly** - security patches are important
3. **Use strong passwords** if using custom encryption

### For Administrators

1. **Set appropriate rate limits** based on usage patterns
2. **Monitor security logs** for unusual activity
3. **Verify file integrity** regularly

## 🔍 Security Event Logging

All security events are logged to `security.log`:

```json
{
  "type": "environment_check",
  "timestamp": "2026-02-05T10:30:00",
  "session": "a3f2c1d4",
  "data": {
    "platform": "Linux"
  }
}
```

### Event Types

- `environment_check` - Environment validation results
- `encryption_error` - Encryption operation failed
- `decryption_error` - Decryption operation failed
- `integrity_check_failed` - File integrity violation

## ⚠️ Security Warnings

### What Gets Logged

Security events are logged for:
- Configuration encryption/decryption
- File integrity checks
- Environment warnings
- Rate limit violations

### What Doesn't Get Logged

Sensitive data is NEVER logged:
- Passwords and credentials
- Full IP addresses
- API keys
- Session tokens (only partial)

## 🆘 Troubleshooting

### "Rate limit exceeded"

**Cause**: Too many automation starts in short time.

**Solution**: Wait for cooldown period (shown in error message).

### "Decryption error"

**Cause**: Wrong password or corrupted config file.

**Solution**: Re-enter password or delete config file to reset.

### "Cryptography library not installed"

**Cause**: Required security dependency missing.

**Solution**: Run `pip install cryptography>=41.0.0`

## 🎓 Technical Details

### Encryption Algorithm

- **Algorithm**: AES-256 (via Fernet)
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: Application name
- **Key Length**: 256 bits

### Hash Functions

- **File Integrity**: SHA-256
- **Hardware ID**: SHA-256

### Random Generation

- **Method**: `secrets` module (CSPRNG)
- **Entropy**: System-provided cryptographic quality

## 📚 Additional Resources

- [Python Cryptography Library](https://cryptography.io/)
- [OWASP Security Guidelines](https://owasp.org/)
- [NIST Cryptographic Standards](https://www.nist.gov/cryptography)

## 🔄 Version History

### Version 1.0 (Current)
- Initial security implementation
- Configuration encryption
- File integrity checking
- Rate limiting
- Secure logging
- Environment validation

---

**Built with security in mind to protect your automation bot from unauthorized access and cracking attempts.**
