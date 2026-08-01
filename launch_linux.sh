#!/bin/bash
# HintSpark — Linux Launch Script
# ================================

echo "=========================================="
echo " HintSpark — AI Math Tutor & Helper (Linux)"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 using your package manager (e.g. sudo apt install python3 python3-pip python3-venv)"
    exit 1
fi

# Set up virtual environment if not present
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing required Python dependencies..."
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
    ./venv/bin/pip install pywebview
fi

# Launch application
echo "Starting HintSpark..."
./venv/bin/python3 desktop_app.py
