#!/bin/bash
# Simple run script for standalone executable on Linux/Mac

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "ADVANCED-BOT Launcher"
echo "================================================"
echo ""

# Check if executable exists
if [ ! -f "dist/ADVANCED-BOT" ]; then
    echo -e "${RED}ERROR: Executable not found!${NC}"
    echo ""
    echo "The standalone executable has not been built yet."
    echo "Please run the build script first:"
    echo ""
    echo "  ./build_standalone.sh"
    echo ""
    exit 1
fi

# Make sure it's executable
chmod +x dist/ADVANCED-BOT

# Run the application
echo -e "${GREEN}Starting ADVANCED-BOT...${NC}"
echo ""
./dist/ADVANCED-BOT
