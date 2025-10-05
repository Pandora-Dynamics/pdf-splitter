"""
Test suite for Modern PDF Splitter
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock

from utils import (
    validate_pdf_file, validate_output_directory, parse_page_ranges,
    get_pdf_page_count, validate_page_ranges, generate_output_filename,
    format_file_size, clean_filename, get_available_disk_space
)


class TestPDFSplitterUtils(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf_path = os.path.join(self.temp_dir, "test.pdf")
        self.create_test_pdf()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_pdf(self):
        """Create a test PDF file"""
        # Create a simple text file that looks like a PDF
        with open(self.test_pdf_path, 'w') as f:
            f.write("%PDF-1.4\n")
            f.write("1 0 obj\n")
            f.write("<<\n")
            f.write("/Type /Catalog\n")
            f.write("/Pages 2 0 R\n")
            f.write(">>\n")
            f.write("endobj\n")
            f.write("2 0 obj\n")
            f.write("<<\n")
            f.write("/Type /Pages\n")
            f.write("/Kids [3 0 R]\n")
            f.write("/Count 1\n")
            f.write(">>\n")
            f.write("endobj\n")
            f.write("3 0 obj\n")
            f.write("<<\n")
            f.write("/Type /Page\n")
            f.write("/Parent 2 0 R\n")
            f.write("/MediaBox [0 0 612 792]\n")
            f.write(">>\n")
            f.write("endobj\n")
            f.write("xref\n")
            f.write("0 4\n")
            f.write("0000000000 65535 f \n")
            f.write("0000000009 00000 n \n")
            f.write("0000000058 00000 n \n")
            f.write("0000000115 00000 n \n")
            f.write("trailer\n")
            f.write("<<\n")
            f.write("/Size 4\n")
            f.write("/Root 1 0 R\n")
            f.write(">>\n")
            f.write("startxref\n")
            f.write("200\n")
            f.write("%%EOF\n")
    
    def test_validate_pdf_file_valid(self):
        """Test PDF file validation with valid file"""
        is_valid, error = validate_pdf_file(self.test_pdf_path)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_pdf_file_nonexistent(self):
        """Test PDF file validation with nonexistent file"""
        is_valid, error = validate_pdf_file("nonexistent.pdf")
        self.assertFalse(is_valid)
        self.assertIn("not found", error)
    
    def test_validate_pdf_file_invalid_extension(self):
        """Test PDF file validation with invalid extension"""
        invalid_file = os.path.join(self.temp_dir, "test.txt")
        with open(invalid_file, 'w') as f:
            f.write("not a pdf")
        
        is_valid, error = validate_pdf_file(invalid_file)
        self.assertFalse(is_valid)
        self.assertIn("invalid", error.lower())
    
    def test_validate_output_directory_valid(self):
        """Test output directory validation with valid directory"""
        is_valid, error = validate_output_directory(self.temp_dir)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_output_directory_nonexistent(self):
        """Test output directory validation with nonexistent directory"""
        is_valid, error = validate_output_directory("nonexistent_dir")
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)
    
    def test_parse_page_ranges_single_pages(self):
        """Test parsing single page ranges"""
        ranges = parse_page_ranges("1,3,5")
        self.assertEqual(ranges, [1, 3, 5])
    
    def test_parse_page_ranges_page_ranges(self):
        """Test parsing page ranges"""
        ranges = parse_page_ranges("1-5,10-15")
        self.assertEqual(ranges, [(1, 5), (10, 15)])
    
    def test_parse_page_ranges_mixed(self):
        """Test parsing mixed page ranges"""
        ranges = parse_page_ranges("1-5,8,10-15")
        self.assertEqual(ranges, [(1, 5), 8, (10, 15)])
    
    def test_parse_page_ranges_with_spaces(self):
        """Test parsing page ranges with spaces"""
        ranges = parse_page_ranges("1 - 5, 8, 10 - 15")
        self.assertEqual(ranges, [(1, 5), 8, (10, 15)])
    
    def test_parse_page_ranges_empty(self):
        """Test parsing empty page ranges"""
        with self.assertRaises(ValueError):
            parse_page_ranges("")
    
    def test_parse_page_ranges_invalid_format(self):
        """Test parsing invalid page range format"""
        with self.assertRaises(ValueError):
            parse_page_ranges("1-5-10")
    
    def test_parse_page_ranges_negative_pages(self):
        """Test parsing negative page numbers"""
        with self.assertRaises(ValueError):
            parse_page_ranges("-1,5")
    
    def test_parse_page_ranges_invalid_range(self):
        """Test parsing invalid range (start > end)"""
        with self.assertRaises(ValueError):
            parse_page_ranges("5-1")
    
    def test_validate_page_ranges_valid(self):
        """Test page range validation with valid ranges"""
        page_ranges = [1, (3, 5), 10]
        total_pages = 15
        is_valid, error = validate_page_ranges(page_ranges, total_pages)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_page_ranges_invalid(self):
        """Test page range validation with invalid ranges"""
        page_ranges = [1, (3, 20), 10]  # Range 3-20 exceeds total pages
        total_pages = 15
        is_valid, error = validate_page_ranges(page_ranges, total_pages)
        self.assertFalse(is_valid)
        self.assertIn("exceeds", error)
    
    def test_generate_output_filename_single_page(self):
        """Test output filename generation for single page"""
        filename = generate_output_filename("document.pdf", 5)
        self.assertEqual(filename, "document_page_5.pdf")
    
    def test_generate_output_filename_page_range(self):
        """Test output filename generation for page range"""
        filename = generate_output_filename("document.pdf", (1, 5))
        self.assertEqual(filename, "document_pages_1-5.pdf")
    
    def test_generate_output_filename_same_start_end(self):
        """Test output filename generation for same start and end page"""
        filename = generate_output_filename("document.pdf", (5, 5))
        self.assertEqual(filename, "document_page_5.pdf")
    
    def test_generate_output_filename_with_index(self):
        """Test output filename generation with index"""
        filename = generate_output_filename("document.pdf", (1, 5), 2)
        self.assertEqual(filename, "document_pages_1-5_2.pdf")
    
    def test_format_file_size_bytes(self):
        """Test file size formatting for bytes"""
        self.assertEqual(format_file_size(512), "512.0 B")
    
    def test_format_file_size_kb(self):
        """Test file size formatting for KB"""
        self.assertEqual(format_file_size(1536), "1.5 KB")
    
    def test_format_file_size_mb(self):
        """Test file size formatting for MB"""
        self.assertEqual(format_file_size(2097152), "2.0 MB")
    
    def test_clean_filename(self):
        """Test filename cleaning"""
        dirty_filename = "test<>file.pdf"
        clean_name = clean_filename(dirty_filename)
        self.assertEqual(clean_name, "test__file.pdf")
    
    def test_clean_filename_multiple_underscores(self):
        """Test filename cleaning with multiple underscores"""
        dirty_filename = "test___file.pdf"
        clean_name = clean_filename(dirty_filename)
        self.assertEqual(clean_name, "test_file.pdf")
    
    def test_clean_filename_leading_trailing_underscores(self):
        """Test filename cleaning with leading/trailing underscores"""
        dirty_filename = "_test_file_.pdf"
        clean_name = clean_filename(dirty_filename)
        self.assertEqual(clean_name, "test_file.pdf")


class TestPDFSplitterIntegration(unittest.TestCase):
    """Integration tests for PDF splitter"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch('utils.get_pdf_page_count')
    def test_workflow_validation(self, mock_page_count):
        """Test complete workflow validation"""
        mock_page_count.return_value = 10
        
        # Test file validation
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("dummy pdf content")
        
        is_valid, error = validate_pdf_file(test_file)
        self.assertTrue(is_valid)
        
        # Test directory validation
        is_valid, error = validate_output_directory(self.temp_dir)
        self.assertTrue(is_valid)
        
        # Test page range parsing
        page_ranges = parse_page_ranges("1-5,8,10")
        self.assertEqual(page_ranges, [(1, 5), 8, 10])
        
        # Test page range validation
        is_valid, error = validate_page_ranges(page_ranges, 10)
        self.assertTrue(is_valid)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)