#!/usr/bin/env python3
"""
Validation script to check if the bot can run properly
Tests all critical dependencies and functionality
"""

import sys
import os

print("="*70)
print("ADVANCED-BOT - Pre-Build Validation")
print("="*70)
print()

# Track issues
issues = []
warnings = []
checks_passed = 0
checks_total = 0

def check(name, condition, error_msg=None, warning_msg=None):
    global checks_passed, checks_total
    checks_total += 1
    print(f"[{checks_total}] Checking {name}...", end=" ")
    if condition:
        print("✓ OK")
        checks_passed += 1
        return True
    else:
        if error_msg:
            print("✗ FAILED")
            issues.append(f"{name}: {error_msg}")
        elif warning_msg:
            print("⚠ WARNING")
            warnings.append(f"{name}: {warning_msg}")
        return False

# Check Python version
print("\n--- Python Environment ---")
py_version = sys.version_info
check("Python version", 
      py_version >= (3, 8),
      f"Python 3.8+ required, found {py_version.major}.{py_version.minor}")

# Check required modules
print("\n--- Required Dependencies ---")
try:
    import PySide6
    check("PySide6", True)
except ImportError:
    check("PySide6", False, "PySide6 not installed. Run: pip install PySide6")

try:
    import playwright
    check("Playwright", True)
except ImportError:
    check("Playwright", False, "Playwright not installed. Run: pip install playwright")

try:
    import aiohttp
    check("aiohttp", True)
except ImportError:
    check("aiohttp", False, "aiohttp not installed. Run: pip install aiohttp")

try:
    from dateutil import parser
    check("python-dateutil", True)
except ImportError:
    check("python-dateutil", False, "python-dateutil not installed. Run: pip install python-dateutil")

# Check PyInstaller for building
print("\n--- Build Tools ---")
try:
    import PyInstaller
    check("PyInstaller", True)
except ImportError:
    check("PyInstaller", False, None, "PyInstaller not installed. Run: pip install pyinstaller")

# Check required files
print("\n--- Project Files ---")
check("advanced_bot.py", os.path.exists("advanced_bot.py"), 
      "Main application file missing. Ensure you're in the project root directory.")
check("advanced_bot.spec", os.path.exists("advanced_bot.spec"),
      "PyInstaller spec file missing. Cannot build without advanced_bot.spec.")
check("requirements.txt", os.path.exists("requirements.txt"),
      "Requirements file missing. Cannot install dependencies.")
check("build_standalone.bat", os.path.exists("build_standalone.bat"),
      None, "Build script for Windows is missing.")
check("build_standalone.sh", os.path.exists("build_standalone.sh"),
      None, "Build script for Linux/Mac is missing.")

# Check example files
print("\n--- Example Files ---")
check("example_script.json", os.path.exists("example_script.json"), None, "Missing example file")
check("example_proxies.txt", os.path.exists("example_proxies.txt"), None, "Missing example file")

# Check if code compiles
print("\n--- Code Validation ---")
try:
    import py_compile
    py_compile.compile("advanced_bot.py", doraise=True)
    check("Syntax validation", True)
except py_compile.PyCompileError as e:
    check("Syntax validation", False, f"Syntax error: {e}")

# Check disk space (rough estimate)
print("\n--- System Resources ---")
try:
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024**3)
    check("Disk space", free_gb > 1.0, f"Insufficient space: {free_gb:.1f}GB free, need 1GB+")
except:
    check("Disk space", False, None, "Could not check disk space")

# Summary
print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)
print(f"Checks passed: {checks_passed}/{checks_total}")
print()

if issues:
    print("❌ CRITICAL ISSUES (must fix):")
    for issue in issues:
        print(f"   - {issue}")
    print()

if warnings:
    print("⚠ WARNINGS (recommended to fix):")
    for warning in warnings:
        print(f"   - {warning}")
    print()

if not issues:
    print("✅ All critical checks passed!")
    print()
    print("You can proceed with building the standalone executable:")
    print("  Windows: ONE_CLICK_BUILD.bat or build_standalone.bat")
    print("  Linux/Mac: ./ONE_CLICK_BUILD.sh or ./build_standalone.sh")
    print()
    sys.exit(0)
else:
    print("❌ Please fix the issues above before building.")
    print()
    print("Quick fix:")
    print("  pip install -r requirements.txt")
    print("  pip install pyinstaller")
    print()
    sys.exit(1)
