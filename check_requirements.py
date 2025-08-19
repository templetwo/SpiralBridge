#!/usr/bin/env python3
"""
SpiralBridge Requirements Checker
Checks if all requirements are met before starting the server
"""

import sys
import os

def check_chrome_installation():
    """Check if Chrome is installed."""
    chrome_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chrome.app/Contents/MacOS/Chrome',
        '/usr/bin/google-chrome',
        '/usr/local/bin/google-chrome'
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            return True
    
    print("❌ Chrome not found!")
    print("💡 Please install Google Chrome from: https://www.google.com/chrome/")
    print("   This is required for web scraping functionality.")
    return False

def check_python_imports():
    """Check if all required Python modules can be imported."""
    required_modules = [
        'flask',
        'selenium', 
        'undetected_chromedriver',
        'flask_cors',
        'flask_session'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} not found")
    
    if missing_modules:
        print(f"\n💡 Install missing modules with:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    return True

def check_file_permissions():
    """Check if we have write permissions in the current directory."""
    try:
        test_file = 'test_write_permission.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ File write permissions OK")
        return True
    except Exception as e:
        print(f"❌ File permission error: {e}")
        return False

def main():
    """Run all checks."""
    print("🔍 SpiralBridge Requirements Checker")
    print("=" * 50)
    
    checks = [
        ("Python imports", check_python_imports),
        ("Chrome browser", check_chrome_installation), 
        ("File permissions", check_file_permissions)
    ]
    
    all_passed = True
    
    for check_name, check_function in checks:
        print(f"\n📋 Checking {check_name}...")
        if not check_function():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! SpiralBridge is ready to run.")
        print("🚀 You can now start the server with: python3 app.py")
        return 0
    else:
        print("❌ Some requirements are missing. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
