"""
Playwright MCP Client - Interface with Microsoft's Playwright MCP server

This module provides a client for communicating with the Playwright MCP server
to perform browser automation tasks.
"""

import asyncio
import logging
import aiohttp
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logger = logging.getLogger(__name__)


class PlaywrightMCPClient:
    """
    Client for interfacing with Playwright MCP server and direct Playwright operations.
    """
    
    def __init__(self, config):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # MCP server settings
        self.mcp_server_url = config.mcp_server_url
        self.session = None
    
    async def initialize(self):
        """Initialize the Playwright browser and MCP connection."""
        logger.info("Initializing Playwright MCP client")
        
        try:
            # Initialize direct Playwright instance
            self.playwright = await async_playwright().start()
            
            # Launch browser
            browser_type = getattr(self.playwright, self.config.browser_type)
            self.browser = await browser_type.launch(
                headless=self.config.headless,
                slow_mo=self.config.slowmo
            )
            
            # Create context
            self.context = await self.browser.new_context()
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(self.config.timeout)
            
            # Initialize HTTP session for MCP communication
            self.session = aiohttp.ClientSession()
            
            logger.info("Playwright MCP client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright MCP client: {e}")
            raise
    
    async def cleanup(self):
        """Clean up browser and MCP connections."""
        try:
            if self.session:
                await self.session.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
                
            logger.info("Playwright MCP client cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def navigate_to(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            Navigation result
        """
        try:
            logger.info(f"Navigating to: {url}")
            
            try:
                # First try with 'networkidle', but with a shorter timeout
                response = await self.page.goto(url, wait_until='networkidle', timeout=10000)
            except Exception as navigation_error:
                logger.warning(f"Navigation with 'networkidle' failed, trying with 'load': {navigation_error}")
                # If networkidle fails, try with 'load' which is less strict
                response = await self.page.goto(url, wait_until='load')
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state('domcontentloaded')
            
            return {
                'success': True,
                'url': url,
                'status': response.status if response else None,
                'title': await self.page.title()
            }
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    async def fill_field(self, field: Dict[str, Any], value: Any) -> bool:
        """
        Fill a form field with a value using enhanced field detection.
        
        Args:
            field: Field information from FormDetector
            value: Value to fill
            
        Returns:
            Success status
        """
        try:
            selector = field.get('selector')
            field_type = field.get('type', 'text').lower()
            field_name = field.get('name') or field.get('id')
            
            if not selector:
                logger.error(f"No selector found for field: {field}")
                return False
            
            logger.debug(f"Attempting to fill field {field_name} ({field_type}) with value: {value}")
            
            # Wait for element to be available
            await self.page.wait_for_selector(selector, timeout=10000)
            
            # Handle different field types with enhanced logic
            if field_type in ['text', 'email', 'password', 'tel', 'url', 'number', 'search']:
                await self._fill_text_field(selector, str(value))
                
            elif field_type == 'textarea':
                await self._fill_text_field(selector, str(value))
                
            elif field_type == 'select':
                return await self._fill_select_field(selector, value, field)
                
            elif field_type == 'checkbox':
                return await self._fill_checkbox_field(selector, value)
                    
            elif field_type == 'radio':
                return await self._fill_radio_field(selector, value, field)
                
            elif field_type == 'file':
                return await self._fill_file_field(selector, value)
                
            elif field_type == 'date':
                return await self._fill_date_field(selector, value)
                
            elif field_type == 'time':
                return await self._fill_time_field(selector, value)
                
            else:
                # Fallback for unknown field types
                logger.warning(f"Unknown field type {field_type}, trying text input")
                await self._fill_text_field(selector, str(value))
            
            # Add small delay between field fills
            await asyncio.sleep(self.config.wait_between_fields / 1000)
            
            logger.debug(f"Successfully filled field {field_name} with value: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fill field {field_name}: {e}")
            return False
    
    async def _fill_text_field(self, selector: str, value: str) -> None:
        """Fill a text-based input field."""
        # Clear existing content and type new value
        await self.page.fill(selector, "")
        await self.page.type(selector, value, delay=50)
    
    async def _fill_select_field(self, selector: str, value: Any, field: Dict[str, Any]) -> bool:
        """Fill a select dropdown field with enhanced option matching."""
        try:
            # Get available options
            options = field.get('options', [])
            
            # Try different matching strategies
            value_str = str(value).lower().strip()
            
            # Strategy 1: Exact value match
            for option in options:
                if option.get('value') == str(value):
                    await self.page.select_option(selector, value=option['value'])
                    logger.debug(f"Selected option by exact value: {option['value']}")
                    return True
            
            # Strategy 2: Exact text match
            for option in options:
                if option.get('text', '').lower().strip() == value_str:
                    if option.get('value'):
                        await self.page.select_option(selector, value=option['value'])
                    else:
                        await self.page.select_option(selector, label=option['text'])
                    logger.debug(f"Selected option by exact text: {option['text']}")
                    return True
            
            # Strategy 3: Partial text match
            for option in options:
                option_text = option.get('text', '').lower().strip()
                if value_str in option_text or option_text in value_str:
                    if option.get('value'):
                        await self.page.select_option(selector, value=option['value'])
                    else:
                        await self.page.select_option(selector, label=option['text'])
                    logger.debug(f"Selected option by partial text match: {option['text']}")
                    return True
            
            # Strategy 4: Select first non-empty option if no match found
            for option in options:
                if option.get('value') and option['value'] not in ['', 'select', 'choose']:
                    await self.page.select_option(selector, value=option['value'])
                    logger.debug(f"Selected first available option: {option['text']}")
                    return True
            
            logger.warning(f"No suitable option found for value '{value}' in select field")
            return False
            
        except Exception as e:
            logger.error(f"Error selecting option in dropdown: {e}")
            return False
    
    async def _fill_checkbox_field(self, selector: str, value: Any) -> bool:
        """Fill a checkbox field."""
        try:
            should_check = bool(value) and str(value).lower() not in ['false', '0', 'no', 'off']
            
            if should_check:
                await self.page.check(selector)
                logger.debug(f"Checked checkbox: {selector}")
            else:
                await self.page.uncheck(selector)
                logger.debug(f"Unchecked checkbox: {selector}")
            
            return True
        except Exception as e:
            logger.error(f"Error handling checkbox: {e}")
            return False
    
    async def _fill_radio_field(self, selector: str, value: Any, field: Dict[str, Any]) -> bool:
        """Fill a radio button field with enhanced option matching."""
        try:
            field_name = field.get('name')
            value_str = str(value).lower().strip()
            
            # Strategy 1: Try exact value match
            radio_selector = f"input[name='{field_name}'][value='{value}']"
            try:
                await self.page.check(radio_selector)
                logger.debug(f"Selected radio by exact value: {value}")
                return True
            except:
                pass
            
            # Strategy 2: Find all radio buttons with this name and match by value/label
            radio_buttons = await self.page.query_selector_all(f"input[name='{field_name}']")
            
            for radio in radio_buttons:
                # Try to match by value attribute
                radio_value = await radio.get_attribute('value')
                if radio_value and radio_value.lower().strip() == value_str:
                    await radio.check()
                    logger.debug(f"Selected radio by matching value: {radio_value}")
                    return True
                
                # Try to match by associated label text
                radio_id = await radio.get_attribute('id')
                if radio_id:
                    try:
                        label = await self.page.query_selector(f"label[for='{radio_id}']")
                        if label:
                            label_text = await label.inner_text()
                            if label_text.lower().strip() == value_str:
                                await radio.check()
                                logger.debug(f"Selected radio by matching label: {label_text}")
                                return True
                    except:
                        pass
            
            # Strategy 3: Partial text matching with labels
            for radio in radio_buttons:
                radio_id = await radio.get_attribute('id')
                if radio_id:
                    try:
                        label = await self.page.query_selector(f"label[for='{radio_id}']")
                        if label:
                            label_text = await label.inner_text()
                            if value_str in label_text.lower() or label_text.lower() in value_str:
                                await radio.check()
                                logger.debug(f"Selected radio by partial label match: {label_text}")
                                return True
                    except:
                        pass
            
            # Strategy 4: Select first radio button if no match found
            if radio_buttons:
                await radio_buttons[0].check()
                first_value = await radio_buttons[0].get_attribute('value')
                logger.debug(f"Selected first radio button with value: {first_value}")
                return True
            
            logger.warning(f"No suitable radio option found for value '{value}'")
            return False
            
        except Exception as e:
            logger.error(f"Error handling radio button: {e}")
            return False
    
    async def _fill_file_field(self, selector: str, value: Any) -> bool:
        """Fill a file upload field."""
        try:
            if value and str(value) != "test_file.txt":
                await self.page.set_input_files(selector, str(value))
                logger.debug(f"Uploaded file: {value}")
                return True
            else:
                logger.debug("Skipped file upload (placeholder value)")
                return True
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False
    
    async def _fill_date_field(self, selector: str, value: Any) -> bool:
        """Fill a date input field."""
        try:
            # Convert various date formats to YYYY-MM-DD
            date_str = str(value)
            if len(date_str.split('/')) == 3:
                # Convert MM/DD/YYYY to YYYY-MM-DD
                parts = date_str.split('/')
                if len(parts[2]) == 4:  # Full year
                    date_str = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            
            await self.page.fill(selector, date_str)
            logger.debug(f"Filled date field with: {date_str}")
            return True
        except Exception as e:
            logger.error(f"Error filling date field: {e}")
            return False
    
    async def _fill_time_field(self, selector: str, value: Any) -> bool:
        """Fill a time input field."""
        try:
            time_str = str(value)
            # Ensure HH:MM format
            if ':' not in time_str and len(time_str) >= 3:
                # Convert HHMM to HH:MM
                time_str = f"{time_str[:2]}:{time_str[2:4]}"
            
            await self.page.fill(selector, time_str)
            logger.debug(f"Filled time field with: {time_str}")
            return True
        except Exception as e:
            logger.error(f"Error filling time field: {e}")
            return False
    
    async def click_element(self, element_info: Dict[str, Any]) -> bool:
        """
        Click an element.
        
        Args:
            element_info: Element information
            
        Returns:
            Success status
        """
        try:
            selector = element_info.get('selector')
            if not selector:
                logger.error("No selector provided for click")
                return False
            
            # Wait for element to be available and clickable
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.click(selector)
            
            logger.debug(f"Successfully clicked element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return False
    
    async def wait_for_response(self, timeout: int = None) -> Dict[str, Any]:
        """
        Wait for page response after form submission.
        
        Args:
            timeout: Optional timeout override
            
        Returns:
            Response information
        """
        try:
            timeout = timeout or self.config.timeout
            
            # Wait for navigation or network idle
            try:
                await self.page.wait_for_load_state('networkidle', timeout=timeout)
            except:
                # If networkidle times out, try domcontentloaded
                await self.page.wait_for_load_state('domcontentloaded', timeout=5000)
            
            return {
                'success': True,
                'url': self.page.url,
                'title': await self.page.title()
            }
            
        except Exception as e:
            logger.error(f"Error waiting for response: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_page_content(self) -> str:
        """Get the current page content."""
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return ""
    
    async def get_page_title(self) -> str:
        """Get the current page title."""
        try:
            return await self.page.title()
        except Exception as e:
            logger.error(f"Failed to get page title: {e}")
            return ""
    
    async def take_screenshot(self, path: str) -> bool:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Path to save screenshot
            
        Returns:
            Success status
        """
        try:
            await self.page.screenshot(path=path, full_page=True)
            logger.debug(f"Screenshot saved to: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    async def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript on the page.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Execution result
        """
        try:
            result = await self.page.evaluate(script)
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            return None
    
    async def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector
            timeout: Optional timeout override
            
        Returns:
            Success status
        """
        try:
            timeout = timeout or self.config.timeout
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
            
        except Exception as e:
            logger.error(f"Element {selector} not found within timeout: {e}")
            return False
    
    async def get_element_text(self, selector: str) -> Optional[str]:
        """
        Get text content of an element.
        
        Args:
            selector: CSS selector
            
        Returns:
            Element text or None
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.inner_text()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get text for {selector}: {e}")
            return None
    
    async def is_element_visible(self, selector: str) -> bool:
        """
        Check if an element is visible.
        
        Args:
            selector: CSS selector
            
        Returns:
            Visibility status
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.is_visible()
            return False
            
        except Exception as e:
            logger.error(f"Failed to check visibility for {selector}: {e}")
            return False
    
    # MCP Server Communication Methods
    
    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool via the MCP server.
        
        Args:
            tool_name: Name of the MCP tool to call
            parameters: Tool parameters
            
        Returns:
            Tool result
        """
        try:
            if not self.session:
                raise Exception("MCP session not initialized")
            
            payload = {
                'tool': tool_name,
                'parameters': parameters
            }
            
            async with self.session.post(
                f"{self.mcp_server_url}/tools/{tool_name}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.mcp_timeout/1000)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'result': result
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"MCP server error {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
