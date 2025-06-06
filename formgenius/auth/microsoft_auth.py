"""
Microsoft Authentication Handler for Power Apps
Handles Microsoft Office 365 authentication with 2FA support
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class MicrosoftAuthenticator:
    """
    Handles Microsoft Office 365 authentication including 2FA
    """
    
    def __init__(self, config, playwright_client):
        self.config = config
        self.playwright_client = playwright_client
        self.auth_state_file = "auth_state.json"
        self.auth_cache_file = "auth_cache.json"
        
        # Microsoft login URLs
        self.login_url = "https://login.microsoftonline.com"
        self.powerapps_url = "https://make.powerapps.com"
        
        # Authentication state
        self.is_authenticated = False
        self.auth_expiry = None
        
    async def authenticate(self, email: str, password: str, force_reauth: bool = False) -> Dict[str, Any]:
        """
        Authenticate with Microsoft Office 365
        
        Args:
            email: Microsoft account email
            password: Microsoft account password
            force_reauth: Force re-authentication even if cached state exists
            
        Returns:
            Authentication result
        """
        logger.info(f"Starting Microsoft authentication for: {email}")
        
        try:
            # Check if we have valid cached authentication
            if not force_reauth and await self._load_cached_auth():
                logger.info("Using cached authentication state")
                return {
                    'success': True,
                    'method': 'cached',
                    'message': 'Authentication loaded from cache'
                }
            
            # Perform fresh authentication
            return await self._perform_authentication(email, password)
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _perform_authentication(self, email: str, password: str) -> Dict[str, Any]:
        """
        Perform fresh authentication with 2FA support
        """
        logger.info("Performing fresh Microsoft authentication")
        
        page = self.playwright_client.page
        
        try:
            # Navigate to Microsoft login
            await page.goto(self.login_url)
            
            # Enter email
            await page.fill("input[type='email']", email)
            await page.click("input[type='submit']")
            
            # Wait for password field or potential redirect
            await page.wait_for_timeout(2000)
            
            # Check if we need to enter password
            password_field = await page.query_selector("input[type='password']")
            if password_field:
                await page.fill("input[type='password']", password)
                await page.click("input[type='submit']")
                await page.wait_for_timeout(1000)
            
            # Handle 2FA if required
            await self._handle_2fa()
            
            # Navigate to Power Apps to verify authentication
            await page.goto(self.powerapps_url)
            
            # Wait for successful load
            await page.wait_for_url("**/make.powerapps.com/**", timeout=30000)
            
            # Save authentication state
            await self._save_auth_state()
            
            self.is_authenticated = True
            
            return {
                'success': True,
                'method': 'fresh',
                'message': 'Authentication completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Authentication process failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _handle_2fa(self):
        """
        Handle 2FA authentication flow
        """
        page = self.playwright_client.page
        
        # Common 2FA selectors
        two_fa_selectors = [
            "input[type='tel']",  # Phone verification
            "input[data-se-id='code']",  # Authentication code
            "[data-testid='authenticator-app-code']",  # Authenticator app
            "input[placeholder*='code']",  # Generic code input
            "[aria-label*='verification']"  # ARIA label for verification
        ]
        
        logger.info("Checking for 2FA requirements...")
        
        # Check if 2FA is required
        two_fa_detected = False
        for selector in two_fa_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    two_fa_detected = True
                    logger.info(f"2FA detected: {selector}")
                    break
            except:
                continue
        
        if two_fa_detected:
            logger.info("2FA required - waiting for manual completion")
            print("\n" + "="*60)
            print("🔐 TWO-FACTOR AUTHENTICATION REQUIRED")
            print("="*60)
            print("Please complete the 2FA process in the browser:")
            print("1. Check your phone/authenticator app for the code")
            print("2. Enter the verification code in the browser")
            print("3. Click 'Verify' or 'Sign in'")
            print("4. Wait for successful login")
            print("\nFormGenius will continue automatically once authentication is complete...")
            print("="*60)
            
            # Wait for successful authentication (redirect to intended page or dashboard)
            success_indicators = [
                "**/make.powerapps.com/**",
                "**/portal.office.com/**",
                "**/admin.microsoft.com/**",
                "**/outlook.office.com/**"
            ]
            
            # Wait up to 5 minutes for manual 2FA completion
            authenticated = False
            for _ in range(60):  # 60 * 5 seconds = 5 minutes
                current_url = page.url
                
                # Check if we've been redirected to a success page
                for indicator in success_indicators:
                    if any(part in current_url for part in indicator.split("*")):
                        authenticated = True
                        break
                
                if authenticated:
                    break
                    
                # Check if 2FA elements are gone (another success indicator)
                still_on_2fa = False
                for selector in two_fa_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element and await element.is_visible():
                            still_on_2fa = True
                            break
                    except:
                        continue
                
                if not still_on_2fa:
                    # Double-check by looking for success indicators in DOM
                    success_elements = await page.query_selector_all('[data-testid*="success"], [aria-label*="success"], .success-message')
                    if success_elements:
                        authenticated = True
                        break
                
                await asyncio.sleep(5)
            
            if authenticated:
                logger.info("2FA authentication completed successfully")
                print("✅ 2FA authentication completed successfully!")
            else:
                logger.warning("2FA authentication timeout - manual verification may be needed")
                print("⚠️  2FA timeout - please ensure authentication was completed")
    
    async def _save_auth_state(self):
        """
        Save authentication state for future use
        """
        try:
            page = self.playwright_client.page
            context = self.playwright_client.context
            
            # Save browser context state
            await context.storage_state(path=self.auth_state_file)
            
            # Save additional metadata
            auth_metadata = {
                'timestamp': datetime.now().isoformat(),
                'expiry': (datetime.now() + timedelta(days=30)).isoformat(),
                'url': page.url,
                'user_agent': await page.evaluate('navigator.userAgent')
            }
            
            with open(self.auth_cache_file, 'w') as f:
                json.dump(auth_metadata, f, indent=2)
            
            logger.info("Authentication state saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save authentication state: {e}")
    
    async def _load_cached_auth(self) -> bool:
        """
        Load cached authentication state
        
        Returns:
            True if valid cached state was loaded
        """
        try:
            # Check if auth files exist
            if not os.path.exists(self.auth_state_file) or not os.path.exists(self.auth_cache_file):
                logger.debug("No cached authentication found")
                return False
            
            # Load and validate metadata
            with open(self.auth_cache_file, 'r') as f:
                metadata = json.load(f)
            
            expiry = datetime.fromisoformat(metadata['expiry'])
            if datetime.now() > expiry:
                logger.info("Cached authentication expired")
                return False
            
            # Load browser context state
            context = self.playwright_client.context
            await context.close()
            
            # Create new context with saved state
            browser = self.playwright_client.browser
            self.playwright_client.context = await browser.new_context(storage_state=self.auth_state_file)
            self.playwright_client.page = await self.playwright_client.context.new_page()
            
            # Set default timeout
            self.playwright_client.page.set_default_timeout(self.playwright_client.config.timeout)
            
            # Verify authentication by navigating to Power Apps
            await self.playwright_client.page.goto(self.powerapps_url)
            
            # Check if we're actually logged in
            await asyncio.sleep(3)
            current_url = self.playwright_client.page.url
            
            if "login" in current_url.lower() or "signin" in current_url.lower():
                logger.info("Cached authentication invalid - redirected to login")
                return False
            
            logger.info("Cached authentication validated successfully")
            self.is_authenticated = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load cached authentication: {e}")
            return False
    
    async def logout(self):
        """
        Log out and clear authentication state
        """
        try:
            if self.is_authenticated:
                page = self.playwright_client.page
                
                # Navigate to logout URL
                await page.goto("https://login.microsoftonline.com/logout")
                await page.wait_for_timeout(2000)
            
            # Clear cached files
            for file_path in [self.auth_state_file, self.auth_cache_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            self.is_authenticated = False
            logger.info("Logout completed and cache cleared")
            
        except Exception as e:
            logger.error(f"Error during logout: {e}")
    
    def is_auth_required(self, url: str) -> bool:
        """
        Check if authentication is required for a given URL
        
        Args:
            url: URL to check
            
        Returns:
            True if authentication is required
        """
        auth_required_domains = [
            'powerapps.com',
            'make.powerapps.com',
            'apps.powerapps.com',
            'portal.office.com',
            'outlook.office.com',
            'teams.microsoft.com'
        ]
        
        return any(domain in url.lower() for domain in auth_required_domains)
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """
        Get current authentication status
        
        Returns:
            Authentication status information
        """
        status = {
            'authenticated': self.is_authenticated,
            'auth_file_exists': os.path.exists(self.auth_state_file),
            'cache_file_exists': os.path.exists(self.auth_cache_file)
        }
        
        if os.path.exists(self.auth_cache_file):
            try:
                with open(self.auth_cache_file, 'r') as f:
                    metadata = json.load(f)
                status['cached_expiry'] = metadata.get('expiry')
                status['cached_timestamp'] = metadata.get('timestamp')
            except:
                pass
        
        return status
