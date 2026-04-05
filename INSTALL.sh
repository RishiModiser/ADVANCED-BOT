#!/bin/bash
# ========================================================
# ADVANCED-BOT - ONE-TIME SETUP / INSTALLER
# ========================================================
# Run this file ONCE to install all dependencies.
# After setup, run ./RUN.sh to start the bot instantly!
#
# Usage:  chmod +x INSTALL.sh && ./INSTALL.sh
# ========================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "========================================================"
echo "|      ADVANCED-BOT - One-Time Setup                  |"
echo "|                                                      |"
echo "|  Run this once, then use RUN.sh for instant start   |"
echo "========================================================"
echo ""

# ── Find Python ────────────────────────────────────────────────────────────
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python is not installed!"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  macOS:          brew install python3"
    echo "                  OR https://www.python.org/downloads/"
    echo "  Ubuntu/Debian:  sudo apt install python3 python3-pip"
    echo "  Fedora:         sudo dnf install python3 python3-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[1/3] Python found: $($PYTHON_CMD --version)"
echo ""

# ── Install pip packages ───────────────────────────────────────────────────
echo "[2/3] Installing Python packages..."
echo "      (This is the slow part - only happens once!)"
echo ""
"$PYTHON_CMD" -m pip install --upgrade pip
"$PYTHON_CMD" -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install Python packages!"
    echo "Please check your internet connection and try again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
echo ""

# ── Install Playwright browser ─────────────────────────────────────────────
echo "[3/3] Installing Playwright browser (Chromium)..."
echo "      (This downloads ~150 MB - only happens once!)"
echo ""
"$PYTHON_CMD" -m playwright install chromium
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Playwright browser install had issues."
    echo "The bot will try to download it automatically on first run."
    echo ""
fi

# On Linux, also install system dependencies
if [ "$(uname -s)" = "Linux" ]; then
    echo ""
    echo "Installing Linux system dependencies for Chromium..."
    "$PYTHON_CMD" -m playwright install-deps chromium 2>/dev/null || true
fi

# ── Mark setup as complete ─────────────────────────────────────────────────
touch .bot_ready

echo ""
echo "========================================================"
echo "|   Setup Complete! Everything is installed.          |"
echo "|                                                      |"
echo "|   Now run:  ./RUN.sh                                |"
echo "|   Bot will start instantly - no more waiting!       |"
echo "========================================================"
echo ""
read -p "Press Enter to exit..."
