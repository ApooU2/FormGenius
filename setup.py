#!/usr/bin/env python3
"""
FormGenius Setup Script

This script helps set up FormGenius for development and production use.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, description="", check=True):
    """Run a shell command with error handling."""
    print(f"📦 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("   FormGenius requires Python 3.8 or higher")
        return False


def check_node_version():
    """Check if Node.js is installed."""
    print("📦 Checking Node.js...")
    if shutil.which('node'):
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Node.js {result.stdout.strip()}")
            return True
    
    print("   ❌ Node.js not found")
    print("   Please install Node.js 14+ from https://nodejs.org/")
    return False


def setup_virtual_environment():
    """Setup Python virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("🔄 Virtual environment already exists")
        return True
    
    print("🔧 Creating virtual environment...")
    if run_command(f"{sys.executable} -m venv venv", "Creating venv"):
        print("   ✅ Virtual environment created")
        return True
    return False


def install_python_dependencies():
    """Install Python dependencies."""
    print("📚 Installing Python dependencies...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix-like
        pip_path = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_path} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing requirements"):
        return False
    
    print("   ✅ Python dependencies installed")
    return True


def install_playwright():
    """Install Playwright and browsers."""
    print("🎭 Installing Playwright browsers...")
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        python_path = "venv/bin/python"
    
    if not run_command(f"{python_path} -m playwright install", "Installing Playwright browsers"):
        return False
    
    print("   ✅ Playwright browsers installed")
    return True


def setup_environment_file():
    """Setup environment file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("🔧 Environment file already exists")
        return True
    
    if env_example.exists():
        print("🔧 Creating environment file from template...")
        shutil.copy(env_example, env_file)
        print("   ✅ .env file created from .env.example")
        print("   ⚠️  Please edit .env and add your GEMINI_API_KEY")
        return True
    else:
        print("🔧 Creating environment file...")
        with open(env_file, 'w') as f:
            f.write("# FormGenius Environment Configuration\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("FORMGENIUS_DEBUG=false\n")
            f.write("FORMGENIUS_MAX_WORKERS=4\n")
        
        print("   ✅ .env file created")
        print("   ⚠️  Please edit .env and add your GEMINI_API_KEY")
        return True


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = [
        "generated_tests",
        "test_results", 
        "logs",
        "temp"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True


def verify_installation():
    """Verify the installation."""
    print("🔍 Verifying installation...")
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix-like
        python_path = "venv/bin/python"
    
    # Test import
    test_cmd = f'{python_path} -c "from src.core.formgenius import FormGenius; print(\'✅ FormGenius import successful\')"'
    if not run_command(test_cmd, "Testing FormGenius import"):
        return False
    
    # Test Playwright
    test_cmd = f'{python_path} -c "import playwright; print(\'✅ Playwright import successful\')"'
    if not run_command(test_cmd, "Testing Playwright import"):
        return False
    
    print("   ✅ Installation verified")
    return True


def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 FormGenius setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your GEMINI_API_KEY")
    print("2. Activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix-like
        print("   source venv/bin/activate")
    
    print("3. Run a quick test:")
    print("   python main.py quick https://example.com")
    print("4. Or try the examples:")
    print("   python examples/basic_usage.py")
    
    print("\n📖 Documentation:")
    print("   - README.md for detailed usage")
    print("   - examples/ for sample scripts")
    print("   - config/ for configuration options")


def main():
    """Main setup function."""
    print("🚀 FormGenius Setup Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_node_version():
        return 1
    
    # Setup steps
    steps = [
        setup_virtual_environment,
        install_python_dependencies,
        install_playwright,
        setup_environment_file,
        create_directories,
        verify_installation
    ]
    
    for step in steps:
        if not step():
            print(f"\n❌ Setup failed at step: {step.__name__}")
            return 1
    
    print_next_steps()
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed with error: {e}")
        sys.exit(1)