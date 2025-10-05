# Modern PDF Splitter

A comprehensive, user-friendly PDF splitting application built with Kivy, featuring modern UI design principles and robust functionality.

## Features

### Core Functionality
- **PDF Splitting**: Split PDFs by page ranges or individual pages
- **Flexible Page Selection**: Support for complex page range patterns (e.g., "1-5,8,10-15")
- **Batch Processing**: Process multiple page ranges in a single operation
- **File Validation**: Comprehensive input validation and error handling

### User Interface
- **Modern Design**: Clean, intuitive interface following HCI principles
- **Tabbed Interface**: Separate tabs for splitting and job history
- **Progress Tracking**: Real-time progress bars and status updates
- **Responsive Layout**: Adapts to different screen sizes
- **Visual Feedback**: Clear success/error messages and confirmations

### Job Management
- **Job History**: Complete history of all splitting operations
- **Job Details**: View detailed information about each job
- **Job Management**: Delete individual jobs or clear entire history
- **Persistent Storage**: Job history saved between sessions

### User Experience
- **Preview Function**: Preview split operations before execution
- **File Browsers**: Integrated file and directory selection dialogs
- **Form Validation**: Real-time input validation with helpful error messages
- **Reset Functionality**: Quick form reset for new operations
- **Keyboard Shortcuts**: Efficient workflow support

## Installation

1. **Install Python 3.7+** (if not already installed)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Basic Workflow

1. **Select PDF File**: Click "Browse" to select the PDF you want to split
2. **Define Page Ranges**: Enter page ranges in the format "1-5,8,10-15"
3. **Choose Output Directory**: Select where you want the split files saved
4. **Preview (Optional)**: Click "Preview Split" to see what will be created
5. **Split PDF**: Click "Split PDF" to perform the operation
6. **View History**: Check the "Job History" tab to see past operations

### Page Range Formats

- **Single pages**: `5` (page 5 only)
- **Page ranges**: `1-10` (pages 1 through 10)
- **Mixed ranges**: `1-5,8,10-15` (pages 1-5, page 8, pages 10-15)
- **Multiple ranges**: `1-3,7-9,12` (pages 1-3, 7-9, and 12)

### Output Files

Split files are automatically named based on the page ranges:
- `document_pages_1-5.pdf` (for pages 1-5)
- `document_page_8.pdf` (for single page 8)

## Technical Details

### Architecture
- **Framework**: Kivy 2.2.0 for cross-platform GUI
- **PDF Processing**: PyPDF2 for PDF manipulation
- **Data Storage**: JSON for job history persistence
- **Threading**: Background processing for non-blocking UI

### HCI Principles Applied

1. **Consistency**: Uniform button styles, colors, and layouts
2. **Feedback**: Clear status messages and progress indicators
3. **Error Prevention**: Input validation and confirmation dialogs
4. **Flexibility**: Multiple input methods and customization options
5. **Accessibility**: Clear labels, appropriate contrast, and logical flow
6. **Efficiency**: Keyboard shortcuts and streamlined workflows

### File Structure
```
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
└── job_history.json    # Job history storage (created on first run)
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid PDF files
- Non-existent directories
- Malformed page ranges
- File permission issues
- Disk space problems
- Corrupted PDF files

## Performance

- **Memory Efficient**: Processes PDFs without loading entire files into memory
- **Progress Tracking**: Real-time progress updates for long operations
- **Background Processing**: Non-blocking UI during PDF operations
- **Error Recovery**: Graceful handling of processing errors

## Requirements

- Python 3.7+
- Kivy 2.2.0
- PyPDF2 3.0.1
- Pillow 10.0.0
- kivy-garden.filebrowser 0.1.0

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Support

For support or questions, please open an issue in the project repository.