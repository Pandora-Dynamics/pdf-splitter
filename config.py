"""
Configuration settings for Modern PDF Splitter
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "Modern PDF Splitter"
APP_VERSION = "1.0.0"
APP_AUTHOR = "PDF Splitter Team"

# File paths
HISTORY_FILE = "job_history.json"
CONFIG_FILE = "app_config.json"
LOG_FILE = "app.log"

# UI Settings
WINDOW_SIZE = (1000, 700)
MIN_WINDOW_SIZE = (800, 600)
DEFAULT_THEME = {
    'primary_color': (0.2, 0.6, 0.9, 1),
    'secondary_color': (0.7, 0.7, 0.7, 1),
    'success_color': (0.2, 0.7, 0.3, 1),
    'error_color': (0.8, 0.2, 0.2, 1),
    'text_color': (0.2, 0.2, 0.2, 1),
    'text_secondary_color': (0.5, 0.5, 0.5, 1),
    'background_color': (1, 1, 1, 1),
    'border_radius': 8
}

# PDF Settings
MAX_FILE_SIZE_MB = 100  # Maximum PDF file size in MB
SUPPORTED_EXTENSIONS = ['.pdf']
DEFAULT_OUTPUT_PREFIX = "split_"

# Job History Settings
MAX_HISTORY_ITEMS = 1000  # Maximum number of history items to keep
AUTO_SAVE_HISTORY = True

# Progress Settings
PROGRESS_UPDATE_INTERVAL = 0.1  # Seconds between progress updates
SHOW_PROGRESS_DETAILS = True

# Validation Settings
VALIDATE_PDF_INTEGRITY = True
CHECK_FILE_PERMISSIONS = True
WARN_ON_LARGE_FILES = True
LARGE_FILE_THRESHOLD_MB = 50

# Error Messages
ERROR_MESSAGES = {
    'no_file_selected': "Please select a valid PDF file",
    'no_output_dir': "Please select a valid output directory",
    'invalid_page_range': "Invalid page range format",
    'file_not_found': "Selected file not found",
    'permission_denied': "Permission denied accessing file or directory",
    'invalid_pdf': "Selected file is not a valid PDF",
    'pdf_corrupted': "PDF file appears to be corrupted",
    'disk_full': "Not enough disk space for output files",
    'page_out_of_range': "Page number exceeds PDF page count",
    'empty_page_range': "Please enter page ranges"
}

# Success Messages
SUCCESS_MESSAGES = {
    'split_complete': "PDF split completed successfully!",
    'files_created': "Successfully created {} files in {}",
    'history_cleared': "Job history cleared successfully",
    'job_deleted': "Job deleted from history"
}

# UI Text
UI_TEXT = {
    'app_title': "Modern PDF Splitter",
    'split_tab': "Split PDF",
    'history_tab': "Job History",
    'select_file': "1. Select PDF File",
    'define_pages': "2. Define Page Ranges",
    'select_output': "3. Select Output Directory",
    'browse': "Browse",
    'preview': "Preview Split",
    'split': "Split PDF",
    'reset': "Reset",
    'clear_all': "Clear All",
    'view': "View",
    'delete': "Delete",
    'close': "Close",
    'ok': "OK",
    'cancel': "Cancel",
    'select': "Select"
}

# Page Range Help
PAGE_RANGE_HELP = """
Page Range Formats:
• Single pages: 5
• Page ranges: 1-10
• Mixed ranges: 1-5,8,10-15
• Multiple ranges: 1-3,7-9,12

Examples:
• 1-5,8,10-15 (pages 1-5, page 8, pages 10-15)
• 1,3,5-7 (pages 1, 3, and 5-7)
• 1-10 (pages 1 through 10)
"""

def get_config_path():
    """Get the configuration file path"""
    return os.path.join(os.path.dirname(__file__), CONFIG_FILE)

def get_history_path():
    """Get the history file path"""
    return os.path.join(os.path.dirname(__file__), HISTORY_FILE)

def get_log_path():
    """Get the log file path"""
    return os.path.join(os.path.dirname(__file__), LOG_FILE)

def ensure_data_directory():
    """Ensure data directory exists"""
    data_dir = os.path.dirname(__file__)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir