#!/usr/bin/env python3
"""
Startup script for AutoDraw Flask API
Checks prerequisites and starts the API server
"""

import os
import sys
import subprocess
import time
import requests

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors', 
        'openai',
        'requests',
        'win32com'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'win32com':
                import win32com.client
            elif package == 'flask_cors':
                import flask_cors
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - not installed")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check environment variables"""
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY environment variable is not set")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        return False
    print("✅ OPENAI_API_KEY is set")
    return True

def check_autocad():
    """Check if AutoCAD is accessible"""
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        try:
            autocad = win32com.client.GetActiveObject("AutoCAD.Application")
            print(f"✅ AutoCAD connection: {autocad.Name}")
            return True
        except Exception as e:
            print(f"⚠️  AutoCAD not accessible: {e}")
            print("AutoCAD must be running for drawing functionality")
            return False
        finally:
            pythoncom.CoUninitialize()
    except ImportError:
        print("❌ pywin32 not installed - AutoCAD functionality will not work")
        return False

def install_dependencies():
    """Install missing dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_api():
    """Start the Flask API"""
    print("\nStarting AutoDraw API...")
    
    # Set default port if not specified
    if not os.getenv('PORT'):
        os.environ['PORT'] = '5000'
    
    port = os.getenv('PORT', '5000')
    
    try:
        # Import and run the Flask app
        from app import app
        
        print(f"🚀 AutoDraw API starting on http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        app.run(
            host='0.0.0.0',
            port=int(port),
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start API: {e}")
        return False
    
    return True

def wait_for_api():
    """Wait for API to be ready"""
    print("Waiting for API to be ready...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get('http://localhost:5000/health', timeout=2)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        attempt += 1
        time.sleep(1)
        if attempt % 5 == 0:
            print(f"   Still waiting... ({attempt}/{max_attempts})")
    
    print("❌ API failed to start within expected time")
    return False

def main():
    """Main startup function"""
    print("AutoDraw API Startup")
    print("=" * 50)
    
    # Check prerequisites
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("AutoCAD", check_autocad)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\nChecking {check_name}...")
        if not check_func():
            failed_checks.append(check_name)
    
    # Handle missing dependencies
    if "Dependencies" in failed_checks:
        print("\nAttempting to install missing dependencies...")
        if install_dependencies():
            # Re-check dependencies
            print("\nRe-checking dependencies...")
            if check_dependencies():
                failed_checks.remove("Dependencies")
    
    # Handle missing environment variables
    if "Environment" in failed_checks:
        print("\nPlease set the required environment variables:")
        print("export OPENAI_API_KEY='your-openai-api-key'")
        print("\nThen run this script again.")
        return False
    
    # Warn about AutoCAD but continue
    if "AutoCAD" in failed_checks:
        print("\n⚠️  Warning: AutoCAD is not accessible")
        print("The API will start but drawing functionality may not work")
        print("Make sure AutoCAD is running for full functionality")
    
    # Start the API
    if not start_api():
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 