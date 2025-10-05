#!/usr/bin/env python3
"""
Demo script for Modern PDF Splitter
This script creates sample PDFs and demonstrates the application features
"""

import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def create_sample_pdf(filename, num_pages=10):
    """Create a sample PDF with specified number of pages"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    for i in range(1, num_pages + 1):
        c.drawString(100, height - 100, f"This is page {i} of {num_pages}")
        c.drawString(100, height - 150, f"Sample content for page {i}")
        c.drawString(100, height - 200, f"Created by Modern PDF Splitter Demo")
        
        # Add some visual elements
        c.rect(50, height - 250, width - 100, 100)
        c.drawString(60, height - 240, f"Page {i} Content Box")
        
        if i < num_pages:
            c.showPage()
    
    c.save()
    print(f"Created sample PDF: {filename} ({num_pages} pages)")

def create_demo_files():
    """Create demo PDF files for testing"""
    demo_dir = "demo_files"
    os.makedirs(demo_dir, exist_ok=True)
    
    # Create sample PDFs
    sample_files = [
        ("small_document.pdf", 5),
        ("medium_document.pdf", 15),
        ("large_document.pdf", 25),
        ("single_page.pdf", 1)
    ]
    
    for filename, pages in sample_files:
        filepath = os.path.join(demo_dir, filename)
        create_sample_pdf(filepath, pages)
    
    print(f"\nDemo files created in '{demo_dir}' directory:")
    for filename, pages in sample_files:
        filepath = os.path.join(demo_dir, filename)
        size = os.path.getsize(filepath)
        print(f"  - {filename} ({pages} pages, {size} bytes)")
    
    return demo_dir

def print_demo_instructions():
    """Print demo instructions"""
    print("\n" + "="*60)
    print("MODERN PDF SPLITTER - DEMO INSTRUCTIONS")
    print("="*60)
    print("\n1. START THE APPLICATION:")
    print("   python main.py")
    print("   or")
    print("   python run.py")
    
    print("\n2. TRY THESE DEMO SCENARIOS:")
    print("   a) Split small_document.pdf by pages 1-3,5")
    print("   b) Split medium_document.pdf by ranges 1-5,10-15")
    print("   c) Split large_document.pdf by individual pages 1,5,10,15,20")
    print("   d) Split single_page.pdf by page 1")
    
    print("\n3. FEATURES TO TEST:")
    print("   - File browsing and selection")
    print("   - Page range input validation")
    print("   - Preview functionality")
    print("   - Progress tracking")
    print("   - Job history management")
    print("   - Error handling")
    
    print("\n4. PAGE RANGE FORMATS TO TRY:")
    print("   - Single pages: 1,3,5")
    print("   - Page ranges: 1-5,10-15")
    print("   - Mixed: 1-3,5,7-9,12")
    print("   - With spaces: 1 - 5, 8, 10 - 15")
    
    print("\n5. ERROR SCENARIOS TO TEST:")
    print("   - Invalid page ranges (e.g., 5-1, -1, 100)")
    print("   - Non-existent files")
    print("   - Read-only directories")
    print("   - Empty page ranges")
    
    print("\n6. UI FEATURES TO EXPLORE:")
    print("   - Tab switching between Split and History")
    print("   - Progress bar during operations")
    print("   - Success/error popups")
    print("   - Job history viewing and deletion")
    print("   - Form reset functionality")
    
    print("\n" + "="*60)

def main():
    """Main demo function"""
    print("Modern PDF Splitter - Demo Setup")
    print("="*40)
    
    try:
        # Check if reportlab is available
        import reportlab
        print("✓ ReportLab available for PDF generation")
    except ImportError:
        print("⚠ ReportLab not available. Installing...")
        os.system("pip install reportlab")
        import reportlab
        print("✓ ReportLab installed successfully")
    
    # Create demo files
    demo_dir = create_demo_files()
    
    # Print instructions
    print_demo_instructions()
    
    print(f"\nDemo setup complete! Demo files are in '{demo_dir}' directory.")
    print("You can now run the application and test with these files.")

if __name__ == '__main__':
    main()