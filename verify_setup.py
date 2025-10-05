#!/usr/bin/env python3
"""
Verification script for PDF Splitter Pro
Checks if the application is properly set up
"""

import sys
import importlib.util

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", f"{version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_module(module_name):
    """Check if a Python module is installed"""
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {module_name} is not installed")
        return False
    print(f"✅ {module_name} is installed")
    return True

def check_file_structure():
    """Check if required files exist"""
    import os
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'run.sh',
        'run.bat'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            all_exist = False
    
    return all_exist

def check_main_structure():
    """Check if main.py has required components"""
    try:
        with open('main.py', 'r') as f:
            content = f.read()
        
        required_classes = [
            'PDFSplitterApp',
            'ModernButton',
            'ModernLabel',
            'InfoCard',
            'JobHistoryItem'
        ]
        
        required_methods = [
            'split_by_range',
            'split_by_pages',
            'split_equal_parts',
            'extract_single_pages',
            'load_history',
            'save_history'
        ]
        
        all_present = True
        
        print("\nChecking application structure:")
        for cls in required_classes:
            if f"class {cls}" in content:
                print(f"✅ {cls} class found")
            else:
                print(f"❌ {cls} class missing")
                all_present = False
        
        for method in required_methods:
            if f"def {method}" in content:
                print(f"✅ {method} method found")
            else:
                print(f"❌ {method} method missing")
                all_present = False
        
        return all_present
    
    except Exception as e:
        print(f"❌ Error checking main.py: {e}")
        return False

def check_hci_principles():
    """Check if HCI principles are implemented"""
    try:
        with open('main.py', 'r') as f:
            content = f.read()
        
        hci_features = {
            'Progress feedback': 'ProgressBar' in content,
            'Error handling': 'show_error' in content,
            'Success feedback': 'show_success' in content,
            'Confirmation dialogs': 'Popup' in content,
            'Modern styling': 'RoundedRectangle' in content,
            'Status updates': 'status_label' in content,
            'User guidance': 'hint_text' in content,
            'Job history': 'job_history' in content
        }
        
        print("\nChecking HCI principles implementation:")
        all_implemented = True
        for feature, implemented in hci_features.items():
            if implemented:
                print(f"✅ {feature}")
            else:
                print(f"❌ {feature}")
                all_implemented = False
        
        return all_implemented
    
    except Exception as e:
        print(f"❌ Error checking HCI principles: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("PDF Splitter Pro - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("File Structure", check_file_structure),
        ("Application Structure", check_main_structure),
        ("HCI Principles", check_hci_principles),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 40)
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("Checking Dependencies:")
    print("-" * 40)
    dep_kivy = check_module('kivy')
    dep_pypdf2 = check_module('PyPDF2')
    
    if not dep_kivy or not dep_pypdf2:
        print("\n⚠️  Some dependencies are missing.")
        print("Run: pip install -r requirements.txt")
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("✅ All checks passed! Application is ready.")
        print("\nTo run the application:")
        print("  Linux/Mac:  ./run.sh  or  python3 main.py")
        print("  Windows:    run.bat   or  python main.py")
    else:
        print("❌ Some checks failed. Please review the output above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
