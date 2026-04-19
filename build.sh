#!/bin/bash
# ========================================================
# ADVANCED-BOT - Build Script (Linux/macOS)
# ========================================================
# Builds a single executable from advanced_bot.py
# Usage: chmod +x build.sh && ./build.sh
# ========================================================

set -e

echo ""
echo "========================================================"
echo "|      ADVANCED-BOT - Build Script                    |"
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
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[1/3] Python found: $($PYTHON_CMD --version)"
echo ""

# ── Install build dependencies ─────────────────────────────────────────────
echo "[2/3] Installing dependencies..."
"$PYTHON_CMD" -m pip install --upgrade pip
"$PYTHON_CMD" -m pip install pyinstaller
"$PYTHON_CMD" -m pip install -r requirements.txt
echo ""

# ── Build executable ───────────────────────────────────────────────────────
echo "[3/3] Building executable..."
echo "      This may take several minutes..."
echo ""
rm -rf build dist
"$PYTHON_CMD" -m PyInstaller --onefile --windowed advanced_bot.py

if [ -f "dist/advanced_bot" ]; then
    chmod +x "dist/advanced_bot"
    echo ""
    echo "========================================================"
    echo "|      BUILD SUCCESSFUL!                              |"
    echo "|                                                      |"
    echo "|      Executable: dist/advanced_bot                  |"
    echo "========================================================"
    echo ""
else
    echo ""
    echo "BUILD FAILED - Executable not found."
    exit 1
fi
