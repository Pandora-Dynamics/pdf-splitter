# Quick Start Guide - PDF Splitter Pro

## Installation (30 seconds)

### Option 1: Automated (Recommended)
```bash
# Linux/Mac
./run.sh

# Windows
run.bat
```
The launcher scripts will automatically:
- Create a virtual environment
- Install all dependencies
- Launch the application

### Option 2: Manual
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python main.py
```

## First Use (3 steps)

### 1️⃣ Select PDF File
Click **"Browse Files"** → Choose your PDF → See file info displayed

### 2️⃣ Choose How to Split
Select method from dropdown:
- **Extract Page Range**: Get specific pages (e.g., `1-5, 10-15`)
- **Split by Page Numbers**: Break at certain pages (e.g., `5, 10, 15`)
- **Split into Equal Parts**: Divide evenly (e.g., `3` parts)
- **Extract Single Pages**: Get individual pages (e.g., `1, 5, 10`)

### 3️⃣ Split!
Click **"Split PDF"** → Watch progress → Done! ✨

## Common Tasks

### Split a chapter (pages 10-25)
1. Select Method: **Extract Page Range**
2. Enter: `10-25`
3. Click **Split PDF**

### Divide 30-page document into 3 parts
1. Select Method: **Split into Equal Parts**
2. Enter: `3`
3. Click **Split PDF**
Result: 3 PDFs with 10 pages each

### Extract cover and last page
1. Select Method: **Extract Single Pages**
2. Enter: `1, 30` (adjust 30 to your last page)
3. Click **Split PDF**

### Split at chapter breaks (pages 10, 20, 30)
1. Select Method: **Split by Page Numbers**
2. Enter: `10, 20, 30`
3. Click **Split PDF**
Result: 4 PDFs (pages 1-10, 11-20, 21-30, 31-end)

## Tips & Tricks

✅ **Default Output**: Files save to same folder as source PDF  
✅ **Custom Location**: Click "Select Output Folder" before splitting  
✅ **View History**: Switch to "Job History" tab to see past operations  
✅ **File Naming**: Auto-generated based on split method  
✅ **Large Files**: Progress bar shows real-time status  

## Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Confirm in dialogs
- **Esc**: Close popups

## Troubleshooting

### "PyPDF2 not installed" error
```bash
pip install PyPDF2
```

### Application window too small
Drag corners to resize (minimum 900x600)

### Can't find output files
Check status message for output location or use "Select Output Folder"

### Invalid page range error
- Use format: `1-5, 8, 10-15`
- Separate with commas
- Use hyphens for ranges
- No spaces around numbers

## Features Overview

### 🎨 Modern UI
- Clean, professional design
- Rounded corners and smooth colors
- High contrast for readability

### 🔒 Error Prevention
- Input validation before processing
- Clear error messages
- Confirmation for destructive actions

### 📊 Job History
- Track all operations
- View source files and methods
- Clear history with confirmation

### 🚀 Performance
- Progress indicators
- Real-time status updates
- Efficient PDF processing

### ♿ Accessibility
- Clear labels and instructions
- Logical tab order
- Readable fonts and colors

## HCI Principles in Action

| Principle | Implementation |
|-----------|---------------|
| **Visibility** | Progress bar, status messages, file info |
| **Feedback** | Success/error popups, color coding |
| **Consistency** | Uniform buttons, predictable behavior |
| **Error Prevention** | Input validation, confirmations |
| **User Control** | Cancel buttons, undo-able actions |
| **Recognition** | Clear labels, visual hints |
| **Flexibility** | Multiple split methods, custom output |
| **Aesthetics** | Clean design, minimal clutter |

## Support

- **README.md**: Full documentation
- **verify_setup.py**: Check installation
- **GitHub Issues**: Report bugs or request features

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-05

Happy splitting! 📄✂️
