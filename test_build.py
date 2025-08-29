#!/usr/bin/env python3
"""
Test script to verify the AQI Calculator app works correctly
before building the APK with GitHub Actions.
"""

import os
import sys
import subprocess

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")

    required_modules = [
        'kivy',
        'matplotlib',
        'numpy',
        'pandas',
        'openpyxl',
        'plyer'
    ]

    failed_imports = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n⚠️  Missing modules: {', '.join(failed_imports)}")
        print("Install with: pip install " + " ".join(failed_imports))
        return False

    print("✅ All imports successful!")
    return True

def test_app_structure():
    """Test that all required files exist."""
    print("\n🔍 Testing app structure...")

    required_files = [
        'main.py',
        'aqi_calculator.py',
        'database_manager.py',
        'report_generator.py',
        'excel_manager.py',
        'buildozer.spec'
    ]

    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (missing)")
            missing_files.append(file)

    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False

    print("✅ All required files present!")
    return True

def test_buildozer_config():
    """Test buildozer.spec configuration."""
    print("\n🔍 Testing buildozer configuration...")

    if not os.path.exists('buildozer.spec'):
        print("❌ buildozer.spec not found")
        return False

    try:
        with open('buildozer.spec', 'r') as f:
            content = f.read()

        # Check for required settings
        checks = [
            ('title', 'title ='),
            ('package.name', 'package.name ='),
            ('requirements', 'requirements ='),
            ('orientation', 'orientation ='),
            ('android.permissions', 'android.permissions =')
        ]

        for check_name, check_string in checks:
            if check_string in content:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name} (missing)")

        print("✅ Buildozer configuration looks good!")
        return True

    except Exception as e:
        print(f"❌ Error reading buildozer.spec: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 AQI Calculator - Pre-Build Test Suite")
    print("=" * 50)

    tests = [
        test_app_structure,
        test_imports,
        test_buildozer_config
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print("📊 Test Results:")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🎉 Your app is ready for APK building!")
        print("\nNext steps:")
        print("1. Create a GitHub repository")
        print("2. Upload all your files")
        print("3. Push to trigger GitHub Actions")
        print("4. Download APK from Actions artifacts")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\nPlease fix the issues above before building the APK.")

    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)