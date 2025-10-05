# Installation Guide - PDF Splitter Pro

## 🚀 Quick Installation (Recommended)

### For Linux/Mac Users
```bash
# Make launcher executable (if needed)
chmod +x run.sh

# Run the application
./run.sh
```

### For Windows Users
```cmd
# Double-click run.bat or run from command prompt
run.bat
```

**The launcher will automatically:**
1. Create a virtual environment
2. Install all dependencies (Kivy, PyPDF2)
3. Launch the application

---

## 📋 Manual Installation

If you prefer manual installation or the launcher doesn't work:

### Step 1: Check Python Version
```bash
python3 --version
# or on Windows:
python --version

# Required: Python 3.8 or higher
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

This will install:
- **Kivy 2.3.0**: UI framework
- **PyPDF2 3.0.1**: PDF processing

### Step 4: Run Application
```bash
python main.py
```

---

## 🔧 Platform-Specific Setup

### Linux (Ubuntu/Debian)

#### Install System Dependencies
```bash
# Update package list
sudo apt-get update

# Install Python and pip
sudo apt-get install python3 python3-pip python3-venv

# Install Kivy system dependencies
sudo apt-get install build-essential git python3-dev
sudo apt-get install libgl1-mesa-dev libgles2-mesa-dev
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt-get install libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good
```

#### Run Application
```bash
./run.sh
# or
python3 main.py
```

### macOS

#### Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Install Python and SDL2
```bash
# Install Python 3
brew install python3

# Install SDL2 (if needed)
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
```

#### Run Application
```bash
./run.sh
# or
python3 main.py
```

### Windows

#### Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Important**: Check "Add Python to PATH"
4. Click "Install Now"

#### Run Application
```cmd
# Double-click run.bat or run:
run.bat

# Or manually:
python main.py
```

---

## ✅ Verify Installation

Run the verification script to check everything is set up correctly:

```bash
python3 verify_setup.py
# or on Windows:
python verify_setup.py
```

**Expected Output:**
```
============================================================
PDF Splitter Pro - Setup Verification
============================================================

Python Version:
----------------------------------------
✅ Python version: 3.x.x

File Structure:
----------------------------------------
✅ main.py exists
✅ requirements.txt exists
✅ README.md exists
✅ run.sh exists
✅ run.bat exists

Application Structure:
----------------------------------------
✅ PDFSplitterApp class found
✅ ModernButton class found
✅ ModernLabel class found
✅ InfoCard class found
✅ JobHistoryItem class found
[... all checks ...]

Checking Dependencies:
----------------------------------------
✅ kivy is installed
✅ PyPDF2 is installed

============================================================
VERIFICATION SUMMARY
============================================================
✅ All checks passed! Application is ready.
```

---

## 🐛 Troubleshooting

### Issue: "python: command not found"
**Solution:**
- Linux/Mac: Use `python3` instead of `python`
- Windows: Reinstall Python and check "Add to PATH"

### Issue: "pip: command not found"
**Solution:**
```bash
# Linux/Mac
sudo apt-get install python3-pip
# or
brew install python3

# Windows: Reinstall Python with pip option checked
```

### Issue: "kivy not found" or "PyPDF2 not found"
**Solution:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Permission denied" when running run.sh
**Solution:**
```bash
chmod +x run.sh
./run.sh
```

### Issue: Kivy installation fails on Linux
**Solution:**
```bash
# Install system dependencies first
sudo apt-get install build-essential git python3-dev
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Try again
pip install -r requirements.txt
```

### Issue: Application window is blank/black
**Solution:**
```bash
# Try different graphics backend
export KIVY_GL_BACKEND=angle_sdl2  # Linux/Mac
set KIVY_GL_BACKEND=angle_sdl2     # Windows

# Then run
python main.py
```

### Issue: "ModuleNotFoundError: No module named 'kivy'"
**Solution:**
This means Kivy isn't installed. Make sure you:
1. Activated the virtual environment
2. Ran `pip install -r requirements.txt`
3. Are running from the correct directory

### Issue: Application runs but can't load PDFs
**Solution:**
```bash
# Check PyPDF2 installation
python -c "import PyPDF2; print(PyPDF2.__version__)"

# Reinstall if needed
pip install --force-reinstall PyPDF2
```

---

## 📦 Dependencies Details

### Required Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| kivy | 2.3.0 | GUI framework |
| PyPDF2 | 3.0.1 | PDF processing |
| Python | 3.8+ | Runtime |

### Dependency Tree
```
pdf-splitter
├── kivy 2.3.0
│   ├── Kivy-Garden >= 0.1.4
│   ├── docutils
│   ├── pygments
│   └── [platform-specific graphics libraries]
└── PyPDF2 3.0.1
    └── [standard library only]
```

---

## 🔄 Updating

### Update Dependencies
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Update packages
pip install --upgrade kivy PyPDF2
```

### Reinstall Everything
```bash
# Remove virtual environment
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Run launcher again
./run.sh  # Linux/Mac
run.bat   # Windows
```

---

## 🧹 Uninstallation

### Remove Application
```bash
# Navigate to parent directory
cd ..

# Remove entire folder
rm -rf pdf-splitter  # Linux/Mac
rmdir /s pdf-splitter  # Windows
```

### Remove Job History
```bash
# Linux/Mac
rm ~/.pdf_splitter_history.json

# Windows
del %USERPROFILE%\.pdf_splitter_history.json
```

---

## 🌐 Network Requirements

**Good News:** This application works **100% offline**!

- ❌ No internet connection required
- ❌ No external API calls
- ❌ No cloud services
- ✅ All processing done locally
- ✅ Complete privacy

**Exception:** Internet needed only during initial installation to download dependencies.

---

## 💾 Disk Space Requirements

- **Application Files:** ~50 KB
- **Dependencies (Kivy + PyPDF2):** ~50-100 MB
- **Virtual Environment:** ~100-200 MB
- **Total:** ~150-300 MB

---

## 🎯 System Requirements

### Minimum Requirements
- **OS:** Windows 7+, macOS 10.12+, Linux (any modern distro)
- **Python:** 3.8 or higher
- **RAM:** 512 MB
- **Disk Space:** 300 MB
- **Display:** 900x600 pixels minimum

### Recommended Requirements
- **OS:** Windows 10+, macOS 11+, Ubuntu 20.04+
- **Python:** 3.10 or higher
- **RAM:** 1 GB
- **Disk Space:** 500 MB
- **Display:** 1280x720 pixels or higher

---

## ✨ Post-Installation

### First Run Checklist
1. ✅ Application launches without errors
2. ✅ Window displays correctly
3. ✅ "Browse Files" button works
4. ✅ Can select a PDF file
5. ✅ File information displays correctly
6. ✅ Can switch between tabs
7. ✅ Job History tab is accessible

### Test Split Operation
1. Download or use an existing PDF
2. Click "Browse Files" and select it
3. Choose "Extract Page Range"
4. Enter "1" (to extract first page)
5. Click "Split PDF"
6. Check output folder for result

If all steps work, installation is successful! 🎉

---

## 📞 Support

### Getting Help
1. **Check README.md** for detailed documentation
2. **Run verify_setup.py** to diagnose issues
3. **Check QUICKSTART.md** for common questions
4. **Review this guide** for installation-specific issues

### Reporting Issues
When reporting problems, include:
- Operating system and version
- Python version (`python --version`)
- Output of `verify_setup.py`
- Full error message
- Steps to reproduce

---

**Installation Guide Version:** 1.0.0  
**Last Updated:** 2025-10-05  
**Status:** Production Ready ✅
