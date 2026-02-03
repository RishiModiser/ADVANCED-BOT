#!/bin/bash
# Build script for creating standalone executable on Linux/Mac
# This script builds the ADVANCED-BOT into a single executable file

echo "================================================"
echo "ADVANCED-BOT Standalone Build Script"
echo "================================================"
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers (this may take a few minutes)..."
playwright install chromium

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the executable
echo "Building standalone executable..."
pyinstaller advanced_bot.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/ADVANCED-BOT" ]; then
    echo ""
    echo "================================================"
    echo "BUILD SUCCESSFUL!"
    echo "================================================"
    echo ""
    echo "Your standalone executable is ready:"
    echo "  Location: dist/ADVANCED-BOT"
    echo ""
    echo "To run the application:"
    echo "  ./dist/ADVANCED-BOT"
    echo ""
    echo "Note: On first run, the application will download"
    echo "      Playwright browsers automatically if needed."
    echo ""
else
    echo ""
    echo "================================================"
    echo "BUILD FAILED!"
    echo "================================================"
    echo "Please check the error messages above."
    exit 1
fi
