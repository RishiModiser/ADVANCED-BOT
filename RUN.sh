#!/bin/bash
# ========================================================
# ADVANCED-BOT LAUNCHER
# ========================================================
# Simple launcher for the standalone executable
# ========================================================

clear

# Check if executable exists
if [ ! -f "dist/ADVANCED-BOT" ]; then
    echo ""
    echo "========================================================"
    echo "|                                                      |"
    echo "|      EXECUTABLE NOT FOUND!                          |"
    echo "|                                                      |"
    echo "========================================================"
    echo ""
    echo "The standalone executable has not been built yet."
    echo ""
    echo "Please build it first by running:"
    echo "  ./ONE_CLICK_BUILD.sh"
    echo ""
    echo "Or use the manual build script:"
    echo "  ./build_standalone.sh"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Make sure it's executable
chmod +x "dist/ADVANCED-BOT"

# Run the application
echo ""
echo "========================================================"
echo "|                                                      |"
echo "|      ADVANCED-BOT - Starting...                     |"
echo "|                                                      |"
echo "========================================================"
echo ""
echo "Launching ADVANCED-BOT..."
echo ""
echo "Note: On first run, the application will download"
echo "      Playwright browsers (takes 1-2 minutes)."
echo ""

./dist/ADVANCED-BOT

exit 0
