"""
Utility functions for Modern PDF Splitter
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import List, Tuple, Union, Dict, Any
from pathlib import Path

from config import (
    ERROR_MESSAGES, SUCCESS_MESSAGES, MAX_FILE_SIZE_MB,
    SUPPORTED_EXTENSIONS, VALIDATE_PDF_INTEGRITY
)


def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, ERROR_MESSAGES['file_not_found']
    
    if not os.access(file_path, os.R_OK):
        return False, ERROR_MESSAGES['permission_denied']
    
    # Check file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        return False, ERROR_MESSAGES['invalid_pdf']
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large ({file_size_mb:.1f}MB). Maximum size: {MAX_FILE_SIZE_MB}MB"
    
    # Check if file is readable
    try:
        with open(file_path, 'rb') as f:
            f.read(1024)  # Read first 1KB to check if file is readable
    except Exception as e:
        return False, f"File read error: {str(e)}"
    
    return True, ""


def validate_output_directory(dir_path: str) -> Tuple[bool, str]:
    """
    Validate output directory
    
    Args:
        dir_path: Path to the output directory
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(dir_path):
        return False, "Output directory does not exist"
    
    if not os.path.isdir(dir_path):
        return False, "Output path is not a directory"
    
    if not os.access(dir_path, os.W_OK):
        return False, ERROR_MESSAGES['permission_denied']
    
    return True, ""


def parse_page_ranges(page_text: str) -> List[Union[int, Tuple[int, int]]]:
    """
    Parse page range text into list of ranges
    
    Args:
        page_text: Text containing page ranges (e.g., "1-5,8,10-15")
        
    Returns:
        List of page ranges (single pages as int, ranges as tuples)
        
    Raises:
        ValueError: If page range format is invalid
    """
    if not page_text.strip():
        raise ValueError(ERROR_MESSAGES['empty_page_range'])
    
    ranges = []
    parts = page_text.replace(' ', '').split(',')
    
    for part in parts:
        if not part:
            continue
            
        if '-' in part:
            # Handle range (e.g., "1-5")
            try:
                start, end = map(int, part.split('-'))
                if start <= 0 or end <= 0:
                    raise ValueError("Page numbers must be positive")
                if start > end:
                    raise ValueError("Start page must be less than or equal to end page")
                ranges.append((start, end))
            except ValueError as e:
                raise ValueError(f"Invalid range format '{part}': {str(e)}")
        else:
            # Handle single page (e.g., "5")
            try:
                page_num = int(part)
                if page_num <= 0:
                    raise ValueError("Page numbers must be positive")
                ranges.append(page_num)
            except ValueError as e:
                raise ValueError(f"Invalid page number '{part}': {str(e)}")
    
    if not ranges:
        raise ValueError(ERROR_MESSAGES['empty_page_range'])
    
    return ranges


def get_pdf_page_count(file_path: str) -> int:
    """
    Get total number of pages in PDF
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Number of pages in the PDF
        
    Raises:
        Exception: If PDF cannot be read
    """
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def validate_page_ranges(page_ranges: List[Union[int, Tuple[int, int]]], total_pages: int) -> Tuple[bool, str]:
    """
    Validate page ranges against PDF page count
    
    Args:
        page_ranges: List of page ranges
        total_pages: Total number of pages in PDF
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    for page_range in page_ranges:
        if isinstance(page_range, tuple):
            start, end = page_range
            if start > total_pages or end > total_pages:
                return False, f"Page range {start}-{end} exceeds PDF page count ({total_pages})"
        else:
            if page_range > total_pages:
                return False, f"Page {page_range} exceeds PDF page count ({total_pages})"
    
    return True, ""


def generate_output_filename(input_file: str, page_range: Union[int, Tuple[int, int]], index: int = 0) -> str:
    """
    Generate output filename for split PDF
    
    Args:
        input_file: Path to input PDF file
        page_range: Page range (single page or tuple)
        index: Index for multiple files with same range
        
    Returns:
        Generated filename
    """
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    if isinstance(page_range, tuple):
        start, end = page_range
        if start == end:
            filename = f"{base_name}_page_{start}.pdf"
        else:
            filename = f"{base_name}_pages_{start}-{end}.pdf"
    else:
        filename = f"{base_name}_page_{page_range}.pdf"
    
    # Add index if multiple files with same range
    if index > 0:
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{index}{ext}"
    
    return filename


def save_job_history(history: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Save job history to file
    
    Args:
        history: List of job history items
        file_path: Path to history file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(history, f, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving job history: {e}")
        return False


def load_job_history(file_path: str) -> List[Dict[str, Any]]:
    """
    Load job history from file
    
    Args:
        file_path: Path to history file
        
    Returns:
        List of job history items
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading job history: {e}")
    
    return []


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_timestamp(timestamp: str) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Timestamp string
        
    Returns:
        Formatted timestamp
    """
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return timestamp


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove invalid characters for filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    return filename


def get_available_disk_space(path: str) -> int:
    """
    Get available disk space in bytes
    
    Args:
        path: Path to check
        
    Returns:
        Available space in bytes
    """
    try:
        statvfs = os.statvfs(path)
        return statvfs.f_frsize * statvfs.f_bavail
    except:
        return 0


def estimate_output_size(input_file: str, page_ranges: List[Union[int, Tuple[int, int]]]) -> int:
    """
    Estimate output file sizes
    
    Args:
        input_file: Path to input PDF
        page_ranges: List of page ranges
        
    Returns:
        Estimated total size in bytes
    """
    try:
        input_size = os.path.getsize(input_file)
        total_pages = get_pdf_page_count(input_file)
        
        # Rough estimation: assume proportional size
        estimated_size_per_file = input_size // total_pages
        total_estimated_size = 0
        
        for page_range in page_ranges:
            if isinstance(page_range, tuple):
                page_count = page_range[1] - page_range[0] + 1
            else:
                page_count = 1
            
            total_estimated_size += estimated_size_per_file * page_count
        
        return total_estimated_size
    except:
        return 0


def create_backup_filename(original_path: str) -> str:
    """
    Create backup filename for original file
    
    Args:
        original_path: Path to original file
        
    Returns:
        Backup filename
    """
    base_name = os.path.splitext(original_path)[0]
    ext = os.path.splitext(original_path)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_backup_{timestamp}{ext}"