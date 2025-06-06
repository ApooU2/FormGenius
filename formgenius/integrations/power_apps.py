"""
Power Apps Handler - Specialized handling for Microsoft Power Apps forms

This module provides specialized functionality for detecting, analyzing,
and filling Power Apps forms which use custom controls and dynamic loading.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class PowerAppsHandler:
    """
    Specialized handler for Microsoft Power Apps forms.
    """
    
    def __init__(self, config):
        self.config = config
        self.playwright_client = None
        
        # Power Apps specific selectors
        self.selectors = config.power_apps_selectors
        
        # Common Power Apps field types and their selectors
        self.field_selectors = {
            'textbox': '[role="textbox"]',
            'combobox': '[role="combobox"]',
            'checkbox': '[role="checkbox"]',
            'button': '[role="button"]',
            'datepicker': '[data-control-name*="date"]',
            'dropdown': '[data-control-name*="dropdown"]'
        }
    
    async def initialize(self, playwright_client):
        """
        Initialize the Power Apps handler.
        
        Args:
            playwright_client: PlaywrightMCPClient instance
        """
        self.playwright_client = playwright_client
        logger.info("Power Apps handler initialized")
    
    async def navigate_to_app(self, app_url: str) -> Dict[str, Any]:
        """
        Navigate to a Power Apps application.
        
        Args:
            app_url: URL of the Power Apps application
            
        Returns:
            Navigation result
        """
        logger.info(f"Navigating to Power Apps: {app_url}")
        
        try:
            # Navigate to the app
            nav_result = await self.playwright_client.navigate_to(app_url)
            if not nav_result['success']:
                return nav_result
            
            # Wait for Power Apps to initialize
            await self.wait_for_app_load()
            
            return {
                'success': True,
                'app_url': app_url,
                'message': 'Power Apps loaded successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to navigate to Power Apps: {e}")
            return {
                'success': False,
                'app_url': app_url,
                'error': str(e)
            }
    
    async def wait_for_app_load(self):
        """Wait for Power Apps application to fully load."""
        logger.info("Waiting for Power Apps to load...")
        
        try:
            page = self.playwright_client.page
            
            # Wait for initial load
            await asyncio.sleep(2)
            
            # Wait for app container to appear
            app_selectors = [
                self.selectors['app_container'],
                '[data-control-name]',
                '.appmagic-control',
                '[class*="powerapps"]'
            ]
            
            for selector in app_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    logger.debug(f"Found Power Apps element: {selector}")
                    break
                except:
                    continue
            
            # Additional wait for dynamic content
            await asyncio.sleep(self.config.power_apps_wait_time / 1000)
            
            # Wait for any loading indicators to disappear
            loading_selectors = [
                '[data-control-name*="loading"]',
                '.loading',
                '.spinner',
                '[aria-label*="loading"]'
            ]
            
            for selector in loading_selectors:
                try:
                    await page.wait_for_selector(selector, state='hidden', timeout=2000)
                except:
                    continue
            
            logger.info("Power Apps application loaded")
            
        except Exception as e:
            logger.warning(f"Error waiting for Power Apps load: {e}")
    
    async def detect_power_apps_forms(self) -> List[Dict[str, Any]]:
        """
        Detect forms within a Power Apps application.
        
        Returns:
            List of detected Power Apps forms
        """
        logger.info("Detecting Power Apps forms")
        
        try:
            page = self.playwright_client.page
            forms = []
            
            # Look for form containers
            form_containers = await page.query_selector_all(
                f"{self.selectors['app_container']}, [data-control-name*='form'], [data-control-name*='screen']"
            )
            
            for i, container in enumerate(form_containers):
                form_data = await self._analyze_power_apps_container(container, i)
                if form_data and form_data.get('fields'):
                    forms.append(form_data)
            
            # If no forms found in containers, scan the entire page
            if not forms:
                logger.info("No forms found in containers, scanning entire page")
                form_data = await self._analyze_entire_page()
                if form_data and form_data.get('fields'):
                    forms.append(form_data)
            
            logger.info(f"Detected {len(forms)} Power Apps forms")
            return forms
            
        except Exception as e:
            logger.error(f"Error detecting Power Apps forms: {e}")
            return []
    
    async def _analyze_power_apps_container(self, container, container_index: int) -> Optional[Dict[str, Any]]:
        """Analyze a Power Apps container for form fields."""
        try:
            fields = []
            
            # Find all interactive elements
            interactive_selectors = [
                '[role="textbox"]',
                '[role="combobox"]', 
                '[role="checkbox"]',
                'input',
                'select',
                'textarea',
                '[data-control-name*="text"]',
                '[data-control-name*="input"]',
                '[data-control-name*="dropdown"]',
                '[data-control-name*="date"]'
            ]
            
            for selector in interactive_selectors:
                elements = await container.query_selector_all(selector)
                
                for element in elements:
                    field_data = await self._analyze_power_apps_element(element)
                    if field_data:
                        fields.append(field_data)
            
            # Look for submit buttons
            submit_buttons = await container.query_selector_all(
                '[role="button"], button, [data-control-name*="submit"], [data-control-name*="save"], [data-control-name*="send"]'
            )
            
            submit_button = None
            for button in submit_buttons:
                button_text = await button.inner_text() if button else ""
                if any(keyword in button_text.lower() for keyword in ['submit', 'save', 'send', 'next', 'continue']):
                    submit_button = {
                        'text': button_text,
                        'element': button,
                        'selector': f'text="{button_text}"'
                    }
                    break
            
            if fields:
                return {
                    'id': f'powerapps_form_{container_index}',
                    'type': 'powerapps',
                    'fields': fields,
                    'submit_button': submit_button,
                    'field_count': len(fields),
                    'container': container
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing Power Apps container: {e}")
            return None
    
    async def _analyze_entire_page(self) -> Optional[Dict[str, Any]]:
        """Analyze the entire page for Power Apps form elements."""
        try:
            page = self.playwright_client.page
            fields = []
            
            # Get all interactive elements on the page
            all_elements = await page.query_selector_all(
                '[role="textbox"], [role="combobox"], [role="checkbox"], input, select, textarea, [data-control-name]'
            )
            
            for element in all_elements:
                field_data = await self._analyze_power_apps_element(element)
                if field_data:
                    fields.append(field_data)
            
            # Look for submit buttons
            submit_buttons = await page.query_selector_all('[role="button"], button')
            submit_button = None
            
            for button in submit_buttons:
                button_text = await button.inner_text() if button else ""
                if any(keyword in button_text.lower() for keyword in ['submit', 'save', 'send']):
                    submit_button = {
                        'text': button_text,
                        'element': button,
                        'selector': f'text="{button_text}"'
                    }
                    break
            
            if fields:
                return {
                    'id': 'powerapps_page_form',
                    'type': 'powerapps',
                    'fields': fields,
                    'submit_button': submit_button,
                    'field_count': len(fields)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing entire page: {e}")
            return None
    
    async def _analyze_power_apps_element(self, element) -> Optional[Dict[str, Any]]:
        """Analyze a single Power Apps element."""
        try:
            # Get element properties
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            role = await element.get_attribute('role')
            control_name = await element.get_attribute('data-control-name')
            element_id = await element.get_attribute('id')
            aria_label = await element.get_attribute('aria-label')
            placeholder = await element.get_attribute('placeholder')
            
            # Determine field type
            field_type = 'text'  # default
            if role == 'textbox':
                field_type = 'text'
            elif role == 'combobox':
                field_type = 'select'
            elif role == 'checkbox':
                field_type = 'checkbox'
            elif tag_name == 'select':
                field_type = 'select'
            elif tag_name == 'textarea':
                field_type = 'textarea'
            elif control_name and 'date' in control_name.lower():
                field_type = 'date'
            
            # Get field label
            label = await self._get_power_apps_field_label(element)
            
            # Check if required
            required = await element.get_attribute('aria-required') == 'true'
            
            # Generate selector
            selector = await self._generate_power_apps_selector(element)
            
            return {
                'id': element_id or control_name,
                'name': control_name or element_id,
                'type': field_type,
                'label': label,
                'required': required,
                'placeholder': placeholder,
                'element': element,
                'selector': selector,
                'role': role,
                'control_name': control_name
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Power Apps element: {e}")
            return None
    
    async def _get_power_apps_field_label(self, element) -> str:
        """Get the label for a Power Apps field."""
        try:
            # Try aria-label first
            aria_label = await element.get_attribute('aria-label')
            if aria_label:
                return aria_label
            
            # Try placeholder
            placeholder = await element.get_attribute('placeholder')
            if placeholder:
                return placeholder
            
            # Look for nearby text elements
            parent = await element.evaluate('el => el.parentElement')
            if parent:
                parent_text = await parent.inner_text() if parent else ""
                if parent_text and len(parent_text) < 100:
                    return parent_text.strip()
            
            # Try control name
            control_name = await element.get_attribute('data-control-name')
            if control_name:
                return control_name.replace('_', ' ').title()
            
            return "Unnamed Field"
            
        except Exception as e:
            logger.error(f"Error getting Power Apps field label: {e}")
            return "Unknown Field"
    
    async def _generate_power_apps_selector(self, element) -> str:
        """Generate a selector for a Power Apps element."""
        try:
            # Try data-control-name first (most reliable for Power Apps)
            control_name = await element.get_attribute('data-control-name')
            if control_name:
                return f'[data-control-name="{control_name}"]'
            
            # Try ID
            element_id = await element.get_attribute('id')
            if element_id:
                return f'#{element_id}'
            
            # Try role and aria-label combination
            role = await element.get_attribute('role')
            aria_label = await element.get_attribute('aria-label')
            if role and aria_label:
                return f'[role="{role}"][aria-label="{aria_label}"]'
            
            # Fallback to role only
            if role:
                return f'[role="{role}"]'
            
            # Final fallback to tag name
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            return tag_name
            
        except Exception as e:
            logger.error(f"Error generating Power Apps selector: {e}")
            return 'input'
    
    async def fill_form(self, form: Dict[str, Any], form_data: Dict[str, Any], 
                       scenario: str) -> Dict[str, Any]:
        """
        Fill a Power Apps form with the provided data.
        
        Args:
            form: Power Apps form structure
            form_data: Data to fill in the form
            scenario: Test scenario being executed
            
        Returns:
            Form filling result
        """
        logger.info(f"Filling Power Apps form for scenario: {scenario}")
        
        try:
            filled_fields = []
            errors = []
            
            for field in form.get('fields', []):
                field_name = field.get('name') or field.get('id')
                field_value = form_data.get(field_name)
                
                if field_value is not None:
                    success = await self._fill_power_apps_field(field, field_value)
                    
                    if success:
                        filled_fields.append({
                            'field': field_name,
                            'value': field_value,
                            'success': True
                        })
                    else:
                        errors.append(f"Failed to fill field: {field_name}")
                        
                    # Small delay between fields
                    await asyncio.sleep(0.5)
            
            # Submit the form if requested
            submit_result = None
            if scenario != 'fill_only':
                submit_result = await self._submit_power_apps_form(form)
            
            return {
                'success': len(errors) == 0,
                'scenario': scenario,
                'filled_fields': len(filled_fields),
                'total_fields': len(form.get('fields', [])),
                'errors': errors,
                'submit_result': submit_result
            }
            
        except Exception as e:
            logger.error(f"Error filling Power Apps form: {e}")
            return {
                'success': False,
                'scenario': scenario,
                'error': str(e)
            }
    
    async def _fill_power_apps_field(self, field: Dict[str, Any], value: Any) -> bool:
        """Fill a single Power Apps field."""
        try:
            page = self.playwright_client.page
            selector = field.get('selector')
            field_type = field.get('type', 'text')
            
            if not selector:
                logger.error(f"No selector for Power Apps field: {field}")
                return False
            
            # Wait for element to be available
            await page.wait_for_selector(selector, timeout=5000)
            
            # Handle different Power Apps field types
            if field_type in ['text', 'email', 'password', 'number']:
                # For Power Apps text fields, we might need to click first
                await page.click(selector)
                await page.fill(selector, str(value))
                
            elif field_type == 'select':
                # Power Apps dropdowns might need special handling
                await page.click(selector)
                await asyncio.sleep(0.5)
                
                # Try to find and click the option
                option_selector = f'[data-value="{value}"], [title="{value}"], text="{value}"'
                try:
                    await page.click(option_selector, timeout=3000)
                except:
                    # Fallback: type the value
                    await page.type(selector, str(value))
                    
            elif field_type == 'checkbox':
                if value:
                    await page.check(selector)
                else:
                    await page.uncheck(selector)
                    
            elif field_type == 'date':
                # Power Apps date fields might need special handling
                await page.click(selector)
                await page.fill(selector, str(value))
                
            else:
                # Default: try to fill as text
                await page.click(selector)
                await page.fill(selector, str(value))
            
            logger.debug(f"Successfully filled Power Apps field {selector} with: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fill Power Apps field {selector}: {e}")
            return False
    
    async def _submit_power_apps_form(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a Power Apps form."""
        try:
            submit_button = form.get('submit_button')
            if not submit_button:
                return {
                    'success': False,
                    'error': 'No submit button found'
                }
            
            page = self.playwright_client.page
            
            # Click the submit button
            if 'element' in submit_button:
                await submit_button['element'].click()
            else:
                selector = submit_button.get('selector', submit_button.get('text', ''))
                await page.click(selector)
            
            # Wait for submission to complete
            await asyncio.sleep(2)
            
            # Check for success/error messages
            success_selectors = [
                '[data-control-name*="success"]',
                '[aria-label*="success"]',
                'text="Success"',
                'text="Submitted"',
                'text="Thank you"'
            ]
            
            error_selectors = [
                '[data-control-name*="error"]',
                '[aria-label*="error"]',
                'text="Error"',
                'text="Failed"'
            ]
            
            has_success = False
            has_error = False
            
            for selector in success_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    has_success = True
                    break
                except:
                    continue
            
            for selector in error_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=1000)
                    has_error = True
                    break
                except:
                    continue
            
            return {
                'success': has_success and not has_error,
                'has_success_message': has_success,
                'has_error_message': has_error,
                'submitted_at': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error submitting Power Apps form: {e}")
            return {
                'success': False,
                'error': str(e)
            }
