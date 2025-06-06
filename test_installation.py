#!/usr/bin/env python3
"""
FormGenius Installation Test
Quick test to verify that FormGenius is properly installed and configured
"""

import sys
import asyncio
from pathlib import Path


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from formgenius.core.agent import FormGeniusAgent
        print("✓ FormGeniusAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FormGeniusAgent: {e}")
        return False
    
    try:
        from formgenius.core.config import Config
        print("✓ Config imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Config: {e}")
        return False
    
    try:
        from formgenius.core.data_generator import DataGenerator
        print("✓ DataGenerator imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import DataGenerator: {e}")
        return False
    
    try:
        from formgenius.core.form_detector import FormDetector
        print("✓ FormDetector imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FormDetector: {e}")
        return False
    
    try:
        from formgenius.core.reporter import TestReporter
        print("✓ TestReporter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import TestReporter: {e}")
        return False
    
    try:
        from formgenius.integrations.playwright_mcp import PlaywrightMCPClient
        print("✓ PlaywrightMCPClient imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PlaywrightMCPClient: {e}")
        return False
    
    try:
        from formgenius.integrations.power_apps import PowerAppsHandler
        print("✓ PowerAppsHandler imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PowerAppsHandler: {e}")
        return False
    
    return True


def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from formgenius.core.config import Config
        
        # Test loading from YAML
        if Path('config.yaml').exists():
            config = Config.from_yaml('config.yaml')
            print("✓ Configuration loaded from config.yaml")
        else:
            print("✗ config.yaml not found")
            return False
        
        # Test basic config structure
        if hasattr(config, 'browser_options'):
            print("✓ Browser options configured")
        else:
            print("✗ Browser options missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_data_generation():
    """Test data generation functionality"""
    print("\nTesting data generation...")
    
    try:
        from formgenius.core.config import Config
        from formgenius.core.data_generator import DataGenerator
        
        config = Config.from_yaml('config.yaml')
        generator = DataGenerator(config)
        
        # Test basic data generation
        email = generator.generate_email()
        if email and '@' in email:
            print(f"✓ Email generation: {email}")
        else:
            print("✗ Email generation failed")
            return False
        
        name = generator.generate_name()
        if name and len(name) > 0:
            print(f"✓ Name generation: {name}")
        else:
            print("✗ Name generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Data generation test failed: {e}")
        return False


async def test_agent_initialization():
    """Test agent initialization"""
    print("\nTesting agent initialization...")
    
    try:
        from formgenius.core.config import Config
        from formgenius.core.agent import FormGeniusAgent
        
        config = Config.from_yaml('config.yaml')
        # Set headless mode for testing
        config.browser_options['headless'] = True
        
        agent = FormGeniusAgent(config)
        print("✓ Agent created successfully")
        
        # Note: We're not actually initializing the browser here
        # as it requires Playwright to be installed and configured
        print("✓ Agent initialization test passed (browser not started)")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent initialization test failed: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\nChecking dependencies...")
    
    # Map package names to their import names
    required_packages = {
        'playwright': 'playwright',
        'beautifulsoup4': 'bs4',
        'faker': 'faker',
        'pyyaml': 'yaml',
        'google-generativeai': 'google.generativeai',
        'aiohttp': 'aiohttp',
        'jinja2': 'jinja2'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} (missing)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run all tests"""
    print("FormGenius Installation Test")
    print("=" * 50)
    
    all_passed = True
    
    # Check dependencies first
    if not check_dependencies():
        print("\n⚠️  Some dependencies are missing. Install them before proceeding.")
        all_passed = False
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test configuration
    if not test_config():
        all_passed = False
    
    # Test data generation
    if not test_data_generation():
        all_passed = False
    
    # Test agent initialization
    if not asyncio.run(test_agent_initialization()):
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! FormGenius is ready to use.")
        print("\nNext steps:")
        print("1. Install Playwright browsers: playwright install")
        print("2. Set up your API keys in config.yaml or environment variables")
        print("3. Run examples: python examples.py")
        print("4. Use CLI: python main.py --help")
    else:
        print("❌ Some tests failed. Please fix the issues before using FormGenius.")
        sys.exit(1)


if __name__ == '__main__':
    main()
