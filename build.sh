#!/bin/bash
# ========================================================
# HumanexBot Version 5.0 - Build Script (Linux/macOS)
# ========================================================
# Builds a single executable from humanexbot_v5.py
# Usage: chmod +x build.sh && ./build.sh
# ========================================================

set -e

echo ""
echo "========================================================"
echo "|      HumanexBot Version 5.0 - Build Script                    |"
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
"$PYTHON_CMD" -m PyInstaller --clean --noconfirm humanexbot_v5.spec

if [ -f "dist/humanexbot_v5" ]; then
    chmod +x "dist/humanexbot_v5"
    echo ""
    echo "========================================================"
    echo "|      BUILD SUCCESSFUL!                              |"
    echo "|                                                      |"
    echo "|      Executable: dist/humanexbot_v5                  |"
    echo "========================================================"
    echo ""
else
    echo ""
    echo "BUILD FAILED - Executable not found."
    exit 1
fi
