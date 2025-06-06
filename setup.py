#!/usr/bin/env python3
"""
FormGenius Setup Script
Helps users set up FormGenius for first-time use
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def create_virtual_environment():
    """Create a virtual environment"""
    print("\nSetting up virtual environment...")
    
    if Path("venv").exists():
        print("✓ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # macOS/Linux
        pip_path = Path("venv/bin/pip")
    
    if not pip_path.exists():
        print("❌ Virtual environment not found. Please run setup again.")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        print("✓ pip upgraded")
        
        # Install requirements
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def install_playwright_browsers():
    """Install Playwright browsers"""
    print("\nInstalling Playwright browsers...")
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python")
    else:  # macOS/Linux
        python_path = Path("venv/bin/python")
    
    try:
        subprocess.run([str(python_path), "-m", "playwright", "install"], check=True)
        print("✓ Playwright browsers installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        print("You can install them manually later with: playwright install")
        return False


def setup_environment_file():
    """Set up environment variables file"""
    print("\nSetting up environment configuration...")
    
    if Path(".env").exists():
        print("✓ .env file already exists")
        return True
    
    if Path(".env.example").exists():
        try:
            shutil.copy(".env.example", ".env")
            print("✓ .env file created from template")
            print("📝 Please edit .env file and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  .env.example not found, creating basic .env file")
        try:
            with open(".env", "w") as f:
                f.write("# FormGenius Environment Variables\n")
                f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
                f.write("LOG_LEVEL=INFO\n")
            print("✓ Basic .env file created")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False


def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = ["reports", "screenshots", "logs", "templates"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ {directory}/ directory ready")
    
    return True


def run_installation_test():
    """Run the installation test"""
    print("\nRunning installation test...")
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = Path("venv/Scripts/python")
    else:  # macOS/Linux
        python_path = Path("venv/bin/python")
    
    try:
        result = subprocess.run([str(python_path), "test_installation.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Installation test passed")
            return True
        else:
            print("❌ Installation test failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run installation test: {e}")
        return False


def show_next_steps():
    """Show next steps to the user"""
    print("\n" + "=" * 60)
    print("🎉 FormGenius Setup Complete!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - GOOGLE_API_KEY for Gemini AI")
    print("   - Other API keys as needed")
    
    print("\n2. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    
    print("\n3. Test with examples:")
    print("   python examples.py")
    
    print("\n4. Use the command line interface:")
    print("   python main.py --help")
    print("   python main.py fill --url https://example.com/form")
    
    print("\n5. Check the documentation:")
    print("   See README.md for detailed usage instructions")
    
    print(f"\n📁 Project directory: {Path.cwd()}")
    print("📧 Need help? Check the documentation or create an issue")


def main():
    """Main setup function"""
    print("FormGenius Setup Script")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Create virtual environment
    if success and not create_virtual_environment():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Install Playwright browsers
    if success:
        install_playwright_browsers()  # Don't fail if this doesn't work
    
    # Set up environment file
    if success and not setup_environment_file():
        success = False
    
    # Create directories
    if success and not create_directories():
        success = False
    
    # Run installation test
    if success:
        run_installation_test()  # Don't fail if this doesn't work
    
    if success:
        show_next_steps()
    else:
        print("\n❌ Setup encountered some issues. Please check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
