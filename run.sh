#!/bin/bash
# Launcher script for PDF Splitter Pro

echo "==================================="
echo "  PDF Splitter Pro Launcher"
echo "==================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import kivy" &> /dev/null || ! python -c "import PyPDF2" &> /dev/null; then
    echo ""
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        exit 1
    fi
fi

echo ""
echo "Starting PDF Splitter Pro..."
echo ""

# Run the application
python main.py

# Deactivate virtual environment on exit
deactivate
