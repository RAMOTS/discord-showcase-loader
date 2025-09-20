#!/usr/bin/env python3
"""
Check if all required dependencies are installed
"""

import sys
import subprocess


def check_dependency(package_name, import_name=None):
    """Check if a Python package is installed and importable."""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False


def main():
    """Check all dependencies."""
    print("Discord Showcase Loader - Dependency Check\n")
    
    dependencies = [
        ("discord.py", "discord"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("aiohttp", "aiohttp"),
    ]
    
    all_good = True
    
    print("Checking Python dependencies:")
    print("=" * 40)
    
    for package, import_name in dependencies:
        if not check_dependency(package, import_name):
            all_good = False
    
    print("\nPython version:")
    print("=" * 40)
    print(f"Python {sys.version}")
    
    if sys.version_info < (3, 8):
        print("⚠️  Python 3.8+ is recommended")
        all_good = False
    else:
        print("✅ Python version is compatible")
    
    if all_good:
        print("\n✅ All dependencies are installed and ready!")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r requirements.txt")
    else:
        print("\n❌ Some dependencies are missing.")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r requirements.txt")
        
        print("\nOr install individually:")
        for package, _ in dependencies:
            print(f"  pip install {package}")
    
    return all_good


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)