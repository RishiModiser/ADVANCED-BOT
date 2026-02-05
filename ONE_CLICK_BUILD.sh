#!/bin/bash
# ========================================================
# ONE-CLICK BUILD - ADVANCED-BOT
# ========================================================
# This script will build a standalone executable that
# requires NO Python installation to run!
#
# Just run this file and wait for the build!
# Usage: ./ONE_CLICK_BUILD.sh
# ========================================================

clear

echo "========================================================"
echo "|                                                      |"
echo "|      ADVANCED-BOT - ONE-CLICK BUILD SCRIPT          |"
echo "|                                                      |"
echo "|      Building a standalone executable...            |"
echo "|      No Python needed on target computers!          |"
echo "|                                                      |"
echo "========================================================"
echo ""
echo "  Please wait while we:"
echo "    - Check Python installation"
echo "    - Install build tools"
echo "    - Download dependencies"
echo "    - Build the executable"
echo ""
echo "  This may take 5-10 minutes on first run..."
echo ""
echo "========================================================"
echo ""
read -p "Press Enter to start the build process..."
echo ""

# Make the build script executable
chmod +x build_standalone.sh

# Call the main build script
./build_standalone.sh

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================"
    echo "|                                                      |"
    echo "|      SUCCESS! Your standalone executable is ready!  |"
    echo "|                                                      |"
    echo "|      Location: dist/ADVANCED-BOT                    |"
    echo "|                                                      |"
    echo "|      You can now distribute this file to any        |"
    echo "|      Linux/Mac computer - no installation needed!   |"
    echo "|                                                      |"
    echo "========================================================"
    echo ""
    read -p "Press Enter to exit..."
else
    echo ""
    echo "========================================================"
    echo "|                                                      |"
    echo "|      BUILD FAILED - Please check errors above       |"
    echo "|                                                      |"
    echo "========================================================"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
