#!/bin/bash
# ========================================================
# ADVANCED-BOT - ONE-CLICK LAUNCHER
# ========================================================
# Run this file to start ADVANCED-BOT instantly.
#
# FIRST TIME? Run INSTALL.sh once to set everything up,
# then use this file for instant 1-click launch!
#
# Usage:  ./RUN.sh   OR   double-click in file manager
# ========================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "========================================================"
echo "|      ADVANCED-BOT - Starting...                     |"
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
    echo "  Ubuntu/Debian:  sudo apt install python3 python3-pip"
    echo "  Fedora:         sudo dnf install python3 python3-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# ── Check if setup was done (show hint if not) ─────────────────────────────
if [ ! -f ".bot_ready" ]; then
    echo "NOTE: First time? Run ./INSTALL.sh once for faster startup."
    echo "      Starting anyway (may take a moment to install packages)..."
    echo ""
fi

"$PYTHON_CMD" advanced_bot.py
exit $?
