#!/bin/bash
# ========================================================
# ADVANCED-BOT - ONE-CLICK LAUNCHER
# ========================================================
# Run this file to start ADVANCED-BOT.
# On first run, any missing dependencies are installed
# automatically - no manual steps required!
#
# Usage:  ./RUN.sh   OR   double-click in file manager
# ========================================================

# Change to the directory containing this script so relative
# paths (dist/ADVANCED-BOT, advanced_bot.py, etc.) always work.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "========================================================"
echo "|      ADVANCED-BOT - One-Click Launcher              |"
echo "========================================================"
echo ""

# ── Option 1: Run pre-built standalone executable if present ─────────────
if [ -f "dist/ADVANCED-BOT" ]; then
    chmod +x "dist/ADVANCED-BOT"
    echo "Launching pre-built ADVANCED-BOT executable..."
    echo ""
    ./dist/ADVANCED-BOT
    exit $?
fi

# ── Option 2: Run with Python (auto-installs deps on first run) ──────────
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -n "$PYTHON_CMD" ]; then
    echo "Python found. Starting ADVANCED-BOT..."
    echo "(First run will auto-install any missing dependencies)"
    echo ""
    "$PYTHON_CMD" advanced_bot.py
    exit $?
fi

# ── No Python found ──────────────────────────────────────────────────────
echo "ERROR: Python is not installed!"
echo ""
echo "Please install Python 3.8 or higher:"
echo "  macOS:          brew install python3"
echo "                  OR https://www.python.org/downloads/"
echo "  Ubuntu/Debian:  sudo apt install python3 python3-pip"
echo "  Fedora:         sudo dnf install python3 python3-pip"
echo ""
echo "After installing Python, run this script again."
echo "Everything else will be set up automatically!"
echo ""
read -p "Press Enter to exit..."
exit 1
