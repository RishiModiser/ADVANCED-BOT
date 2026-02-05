#!/bin/bash
# Build script for creating standalone executable on Linux/Mac
# This script builds the ADVANCED-BOT into a single executable file

set -e  # Exit on error

echo "================================================"
echo "ADVANCED-BOT Standalone Build Script"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH!"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - Fedora: sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

echo "[1/5] Checking Python installation..."
python3 --version
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "ERROR: pip is not installed!"
    echo ""
    echo "Please install pip:"
    echo "  - macOS: python3 -m ensurepip --upgrade"
    echo "  - Ubuntu/Debian: sudo apt install python3-pip"
    echo "  - Fedora: sudo dnf install python3-pip"
    echo ""
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "[2/5] Installing/Upgrading dependencies..."
$PIP_CMD install --upgrade pip
$PIP_CMD install pyinstaller

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyInstaller!"
    exit 1
fi

$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install required dependencies!"
    echo "Please check requirements.txt and your internet connection."
    exit 1
fi
echo ""

echo "[3/5] Installing Playwright browsers..."
echo "This may take a few minutes on first run..."
playwright install chromium || {
    echo "WARNING: Playwright browser installation had issues."
    echo "The application will attempt to download browsers on first run."
}
echo ""

echo "[4/5] Cleaning previous builds..."
rm -rf build dist
echo ""

echo "[5/5] Building standalone executable..."
echo "This may take several minutes..."
pyinstaller advanced_bot.spec --clean --noconfirm

if [ $? -ne 0 ]; then
    echo ""
    echo "================================================"
    echo "BUILD FAILED!"
    echo "================================================"
    echo ""
    echo "PyInstaller encountered an error."
    echo "Please check the error messages above."
    echo ""
    exit 1
fi

# Check if build was successful
if [ -f "dist/ADVANCED-BOT" ]; then
    # Make executable
    chmod +x "dist/ADVANCED-BOT"
    
    echo ""
    echo "================================================"
    echo "BUILD SUCCESSFUL!"
    echo "================================================"
    echo ""
    echo "Your standalone executable is ready:"
    echo "  Location: dist/ADVANCED-BOT"
    echo "  Size: $(du -h dist/ADVANCED-BOT | cut -f1)"
    echo ""
    echo "================================================"
    echo "USAGE INSTRUCTIONS"
    echo "================================================"
    echo ""
    echo "To run the application:"
    echo "  1. Double-click: dist/ADVANCED-BOT (if configured in file manager)"
    echo "  2. Or run from terminal: ./dist/ADVANCED-BOT"
    echo ""
    echo "First Run Notes:"
    echo "  - The application will check for Playwright browsers"
    echo "  - If not found, it will download them automatically"
    echo "  - This one-time download takes 1-2 minutes"
    echo "  - After that, the app starts instantly!"
    echo ""
    echo "================================================"
    echo "DISTRIBUTION"
    echo "================================================"
    echo ""
    echo "You can distribute dist/ADVANCED-BOT to other computers."
    echo "No Python or dependencies required on target systems!"
    echo ""
    echo "For end users, include DISTRIBUTION_README.txt"
    echo ""
else
    echo ""
    echo "================================================"
    echo "BUILD FAILED!"
    echo "================================================"
    echo ""
    echo "The executable was not created."
    echo "Please check the error messages above."
    echo ""
    echo "Common issues:"
    echo "  - Missing dependencies"
    echo "  - Insufficient disk space"
    echo "  - Permission issues"
    echo ""
    exit 1
fi
