#!/usr/bin/env python3
"""
Setup and Run Script for Resume Analyzer Web Application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version check passed: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_required_files():
    """Check if all required files are present"""
    required_files = [
        'advanced_resume_analyzer.py',
        'app.py',
        'index.html',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'reports']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def run_server():
    """Start the Flask server"""
    print("\n🚀 Starting Resume Analyzer Web Application...")
    print("📊 Server will be available at: http://localhost:5000")
    print("💡 The browser will open automatically in 3 seconds")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:5000')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask server
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    """Main setup and run function"""
    print("🎯 Resume Analyzer Web Application Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check required files
    if not check_required_files():
        print("\n💡 Please ensure all required files are in the current directory:")
        print("   - advanced_resume_analyzer.py (your analyzer engine)")
        print("   - app.py (Flask backend)")
        print("   - index.html (frontend)")
        print("   - requirements.txt (dependencies)")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create directories
    create_directories()
    
    # Run server
    run_server()

if __name__ == "__main__":
    main()