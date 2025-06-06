#!/usr/bin/env python3
"""
Microsoft Authentication Setup Script
One-time setup to authenticate with Microsoft Office 365 for Power Apps testing
"""

import asyncio
import logging
import getpass
import sys
from pathlib import Path

# Add parent directory to path to import formgenius modules
sys.path.insert(0, str(Path(__file__).parent))

from formgenius.core.config import Config
from formgenius.integrations.playwright_mcp import PlaywrightMCPClient
from formgenius.auth.microsoft_auth import MicrosoftAuthenticator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_microsoft_auth():
    """
    Setup Microsoft authentication for Power Apps testing
    """
    print("\n" + "="*70)
    print("🔐 MICROSOFT AUTHENTICATION SETUP FOR FORMGENIUS")
    print("="*70)
    print("This setup will authenticate with your Microsoft Office 365 account")
    print("to enable Power Apps form testing with FormGenius.")
    print("\nIMPORTANT:")
    print("• Have your Microsoft account credentials ready")
    print("• Be prepared to complete 2FA authentication")
    print("• Keep your authenticator app/phone nearby")
    print("• This process will open a browser window")
    print("="*70)
    
    # Get user credentials
    email = input("\nEnter your Microsoft email address: ").strip()
    if not email:
        print("❌ Email is required")
        return False
    
    password = getpass.getpass("Enter your Microsoft password: ").strip()
    if not password:
        print("❌ Password is required")
        return False
    
    print(f"\n📧 Email: {email}")
    print("🔑 Password: [HIDDEN]")
    
    confirm = input("\nProceed with authentication? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Authentication cancelled")
        return False
    
    try:
        # Load configuration
        print("\n🔧 Loading configuration...")
        config = Config.from_yaml('config.yaml')
        
        # Initialize Playwright client
        print("🌐 Initializing browser...")
        playwright_client = PlaywrightMCPClient(config)
        await playwright_client.initialize()
        
        # Initialize Microsoft authenticator
        print("🔐 Setting up Microsoft authenticator...")
        authenticator = MicrosoftAuthenticator(config, playwright_client)
        
        # Perform authentication
        print(f"🚀 Starting authentication for {email}...")
        print("📱 Browser window will open - DO NOT CLOSE IT during authentication")
        
        result = await authenticator.authenticate(email, password)
        
        if result['success']:
            print("\n" + "="*50)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("="*50)
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Message: {result.get('message', 'Authentication completed')}")
            print("\n📝 Authentication state has been saved.")
            print("🎯 You can now run FormGenius tests on Power Apps forms.")
            print("\n💡 Next steps:")
            print("1. Use 'python main.py power-apps --url <YOUR_POWER_APP_URL>' to test forms")
            print("2. Authentication will persist for 30 days")
            print("3. Re-run this setup if authentication expires")
            
            # Display authentication status
            status = await authenticator.get_auth_status()
            print(f"\n📊 Auth Status: {status}")
            
        else:
            print("\n" + "="*50)
            print("❌ AUTHENTICATION FAILED!")
            print("="*50)
            print(f"Error: {result.get('error', 'Unknown error')}")
            print("\n🔧 Troubleshooting:")
            print("1. Verify your email and password are correct")
            print("2. Ensure 2FA was completed successfully")
            print("3. Check your internet connection")
            print("4. Try running the setup again")
            return False
        
        # Cleanup
        await playwright_client.cleanup()
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        logger.error(f"Authentication setup failed: {e}")
        return False


async def check_auth_status():
    """
    Check current authentication status
    """
    try:
        config = Config.from_yaml('config.yaml')
        playwright_client = PlaywrightMCPClient(config)
        await playwright_client.initialize()
        
        authenticator = MicrosoftAuthenticator(config, playwright_client)
        status = await authenticator.get_auth_status()
        
        print("\n📊 AUTHENTICATION STATUS")
        print("="*40)
        print(f"Authenticated: {'✅ Yes' if status['authenticated'] else '❌ No'}")
        print(f"Auth file exists: {'✅ Yes' if status['auth_file_exists'] else '❌ No'}")
        print(f"Cache file exists: {'✅ Yes' if status['cache_file_exists'] else '❌ No'}")
        
        if status.get('cached_expiry'):
            print(f"Cache expires: {status['cached_expiry']}")
        if status.get('cached_timestamp'):
            print(f"Last authenticated: {status['cached_timestamp']}")
        
        await playwright_client.cleanup()
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")


async def clear_auth():
    """
    Clear authentication cache
    """
    try:
        config = Config.from_yaml('config.yaml')
        playwright_client = PlaywrightMCPClient(config)
        await playwright_client.initialize()
        
        authenticator = MicrosoftAuthenticator(config, playwright_client)
        await authenticator.logout()
        
        print("✅ Authentication cache cleared successfully")
        
        await playwright_client.cleanup()
        
    except Exception as e:
        print(f"❌ Error clearing auth: {e}")


def print_help():
    """
    Print help information
    """
    print("\n🔐 MICROSOFT AUTHENTICATION SETUP")
    print("="*50)
    print("Available commands:")
    print("  python setup_auth.py           - Setup Microsoft authentication")
    print("  python setup_auth.py status    - Check authentication status")
    print("  python setup_auth.py clear     - Clear authentication cache")
    print("  python setup_auth.py help      - Show this help")
    print("\nExample usage:")
    print("  python setup_auth.py")
    print("  python main.py power-apps --url https://apps.powerapps.com/play/your-app-id")


async def main():
    """
    Main entry point
    """
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            await check_auth_status()
        elif command == "clear":
            await clear_auth()
        elif command == "help":
            print_help()
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
    else:
        # Default action: setup authentication
        success = await setup_microsoft_auth()
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
