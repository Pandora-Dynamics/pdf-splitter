# PDF Splitter Pro

A modern, robust, and user-friendly PDF splitting application built with Kivy, following Human-Computer Interaction (HCI) principles for optimal user experience.

## Features

### Core PDF Splitting Functionalities
- **Extract Page Range**: Extract specific page ranges (e.g., 1-5, 8, 10-12)
- **Split by Page Numbers**: Split PDF at specified page numbers into multiple parts
- **Split into Equal Parts**: Divide PDF into N equal parts automatically
- **Extract Single Pages**: Extract individual pages as separate PDF files

### Job History Tracking
- View complete history of all split operations
- Track source files, split methods, and output locations
- Timestamp for each operation
- Persistent storage of history (saved to `~/.pdf_splitter_history.json`)
- Clear history with confirmation dialog

### User Interface (Following HCI Principles)
- **Visual Hierarchy**: Clear step-by-step workflow (Select → Configure → Execute)
- **Immediate Feedback**: Real-time status updates and progress indicators
- **Error Prevention**: Input validation and clear error messages
- **Consistency**: Uniform design language throughout the application
- **User Control**: Confirmation dialogs for destructive actions
- **Accessibility**: High contrast colors, readable fonts, clear labels
- **Visibility**: System status always visible to users
- **Aesthetic Design**: Modern, clean interface with rounded corners and professional color scheme

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Platform-Specific Setup

#### Linux
```bash
# Install system dependencies for Kivy
sudo apt-get install python3-pip build-essential git python3-dev
sudo apt-get install libgl1-mesa-dev libgles2-mesa-dev
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

#### macOS
```bash
# Kivy should work out of the box after installing requirements
# If you encounter issues, install SDL2 via Homebrew:
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
```

#### Windows
```bash
# Requirements.txt includes Windows-compatible versions
# No additional system dependencies needed
```

## Usage

### Running the Application

```bash
python main.py
```

### Step-by-Step Guide

1. **Select PDF File**
   - Click "Browse Files" button
   - Navigate to your PDF file
   - Select the file to load it
   - File information (name and page count) will be displayed

2. **Choose Split Method**
   - Select from the dropdown menu:
     - **Extract Page Range**: Enter ranges like "1-5, 8, 10-12"
     - **Split by Page Numbers**: Enter split points like "3, 6, 9"
     - **Split into Equal Parts**: Enter number of parts (e.g., "3")
     - **Extract Single Pages**: Enter page numbers like "1, 3, 5"

3. **Configure Parameters**
   - Input field will appear based on selected method
   - Enter the required parameters following the hints

4. **Select Output Location** (Optional)
   - Click "Select Output Folder" to choose destination
   - If not specified, files will be saved in the same folder as source PDF

5. **Execute Split**
   - Click "Split PDF" button
   - Progress bar shows operation status
   - Success message appears when complete

### Viewing Job History

1. Click on the "Job History" tab
2. View all previous split operations with:
   - Timestamp
   - Source file name
   - Split method used
   - Number of output files created
3. Clear history using "Clear History" button (requires confirmation)

## Examples

### Extract Specific Pages
- Method: Extract Page Range
- Input: `1-5, 10, 15-20`
- Result: Creates PDF with pages 1-5, 10, and 15-20

### Split Document into Sections
- Method: Split by Page Numbers
- Input: `5, 10, 15`
- Result: Creates 4 PDFs:
  - Part 1: Pages 1-5
  - Part 2: Pages 6-10
  - Part 3: Pages 11-15
  - Part 4: Pages 16-end

### Divide into Equal Parts
- Method: Split into Equal Parts
- Input: `3`
- Result: Creates 3 PDFs with approximately equal number of pages

### Extract Individual Pages
- Method: Extract Single Pages
- Input: `1, 5, 10`
- Result: Creates 3 separate PDF files, each containing one page

## HCI Principles Implemented

### 1. **Visibility of System Status**
- Real-time progress bar during operations
- Status messages for current operation
- Clear indication of loaded file and page count

### 2. **Match Between System and Real World**
- Natural language labels and instructions
- Familiar file browser interface
- Intuitive step-by-step workflow

### 3. **User Control and Freedom**
- Cancel buttons in all dialogs
- Confirmation for destructive actions (clear history)
- No forced workflows - users can change selections anytime

### 4. **Consistency and Standards**
- Uniform button styling throughout
- Consistent color coding (blue for primary, red for destructive, green for success)
- Standard file picker dialogs

### 5. **Error Prevention**
- Input validation before processing
- Clear hint text in input fields
- Disabled/hidden options when not applicable

### 6. **Recognition Rather Than Recall**
- Clear labels for all functions
- Visual hints and examples in input fields
- Job history for reference

### 7. **Flexibility and Efficiency**
- Multiple split methods for different use cases
- Optional output folder selection
- Quick access to recent operations

### 8. **Aesthetic and Minimalist Design**
- Clean, modern interface
- Focused on essential functions
- Minimal cognitive load

### 9. **Help Users Recognize and Recover from Errors**
- Clear error messages
- Specific guidance on what went wrong
- Non-technical language

### 10. **Help and Documentation**
- Hint text in all input fields
- Clear step-by-step layout
- This README for comprehensive guidance

## Technical Details

### Architecture
- **Framework**: Kivy 2.3.0
- **PDF Processing**: PyPDF2 3.0.1
- **Data Storage**: JSON for job history
- **UI Components**: Custom widgets following Material Design principles

### File Structure
```
pdf-splitter/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── ~/.pdf_splitter_history.json  # Job history (auto-created)
```

### Custom Components
- **ModernButton**: Styled buttons with rounded corners
- **ModernLabel**: Consistent label styling
- **InfoCard**: Card-based layout for sections
- **JobHistoryItem**: Custom widget for history entries

## Troubleshooting

### Application won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### PDF not loading
- Verify file is a valid PDF
- Check file permissions
- Ensure PyPDF2 is installed correctly

### Split operation fails
- Verify page numbers/ranges are valid
- Ensure sufficient disk space
- Check write permissions for output folder

### Display issues
- Update graphics drivers
- Try different SDL2 backends (set environment variable: `KIVY_GL_BACKEND=angle_sdl2`)

## License

See LICENSE file for details.

## Contributing

This is a standalone application. For feature requests or bug reports, please refer to the project documentation.

## Version History

### v1.0.0 (2025-10-05)
- Initial release
- Four split methods implemented
- Job history tracking
- Modern UI with HCI principles
- Cross-platform support (Windows, macOS, Linux)
