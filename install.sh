#!/bin/bash

# Modern PDF Splitter Installation Script

echo "Modern PDF Splitter - Installation Script"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.7 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python $python_version found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✓ pip3 found"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Make scripts executable
chmod +x run.py
chmod +x demo.py

echo "✓ Scripts made executable"

# Create desktop shortcut (optional)
if [ -d "$HOME/Desktop" ]; then
    cat > "$HOME/Desktop/Modern PDF Splitter.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Modern PDF Splitter
Comment=Split PDF files with ease
Exec=python3 $(pwd)/main.py
Icon=application-pdf
Terminal=false
Categories=Office;Graphics;
EOF
    chmod +x "$HOME/Desktop/Modern PDF Splitter.desktop"
    echo "✓ Desktop shortcut created"
fi

echo ""
echo "Installation completed successfully!"
echo ""
echo "To run the application:"
echo "  python3 main.py"
echo "  or"
echo "  python3 run.py"
echo ""
echo "To create demo files:"
echo "  python3 demo.py"
echo ""
echo "To run tests:"
echo "  python3 -m pytest test_app.py"
echo ""
echo "Enjoy using Modern PDF Splitter!"