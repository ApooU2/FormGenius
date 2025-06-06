"""
FormGenius Agent - Main orchestrator for AI-powered form automation

This module contains the main FormGeniusAgent class that coordinates all 
form detection, data generation, and filling operations.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from ..integrations.playwright_mcp import PlaywrightMCPClient
from ..integrations.power_apps import PowerAppsHandler
from .form_detector import FormDetector
from .data_generator import DataGenerator
from .config import Config
from .reporter import TestReporter

logger = logging.getLogger(__name__)


class FormGeniusAgent:
    """
    Main FormGenius agent for automated form filling and testing.
    
    This agent can automatically:
    - Detect forms on web pages
    - Generate realistic test data
    - Fill out forms intelligently
    - Submit forms and validate responses
    - Generate comprehensive test reports
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the FormGenius agent.
        
        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()
        self.playwright_client = PlaywrightMCPClient(self.config)
        self.power_apps_handler = PowerAppsHandler(self.config)
        self.form_detector = FormDetector(self.config)
        self.data_generator = DataGenerator(self.config)
        self.reporter = TestReporter(self.config)
        
        self.session_data = {
            'session_id': self._generate_session_id(),
            'start_time': datetime.now(),
            'forms_processed': [],
            'results': [],
            'errors': []
        }
    
    async def fill_form(self, url: str, form_data: Optional[Dict[str, Any]] = None,
                       test_scenarios: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fill out a single form on a webpage.
        
        Args:
            url: URL of the page containing the form
            form_data: Optional pre-defined form data to use
            test_scenarios: List of test scenarios to execute
            
        Returns:
            Results of the form filling operation
        """
        logger.info(f"Starting form filling for URL: {url}")
        
        try:
            # Initialize browser session
            await self.playwright_client.initialize()
            
            # Navigate to the page
            navigation_result = await self.playwright_client.navigate_to(url)
            if not navigation_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to navigate to {url}: {navigation_result.get('error')}"
                }
            
            # First analyze the full page context for any credentials or instructions
            # This is important for test sites that display login credentials on the page
            page_context = await self.form_detector.analyze_page_context(self.playwright_client.page)
            logger.info(f"Page context analyzed. Found credentials: {page_context['has_test_credentials']}")
            
            # If test credentials were found on the page, use them
            predefined_credentials = {}
            if page_context['has_test_credentials'] and page_context['credentials']:
                predefined_credentials = page_context['credentials']
                logger.info(f"Using credentials found on page: {list(predefined_credentials.keys())}")
            
            # Detect forms on the page
            forms = await self.form_detector.detect_forms(self.playwright_client.page)
            if not forms:
                return {
                    'success': False,
                    'error': 'No forms detected on the page'
                }
            
            # Process each form found
            results = []
            for i, form in enumerate(forms):
                logger.info(f"Processing form {i+1}/{len(forms)}")
                
                # Generate test data if not provided, incorporating page credentials if found
                if not form_data:
                    generated_form_data = await self.data_generator.generate_form_data(form, page_context)
                    
                    # If we found credentials on the page, override the generated ones
                    if predefined_credentials:
                        for field_name, field_value in predefined_credentials.items():
                            # Map common credential field names
                            if field_name == 'username':
                                for potential_name in ['username', 'user', 'email', 'login', 'user_id']:
                                    if potential_name in generated_form_data:
                                        generated_form_data[potential_name] = field_value
                                        
                            elif field_name == 'password':
                                for potential_name in ['password', 'pass', 'pwd']:
                                    if potential_name in generated_form_data:
                                        generated_form_data[potential_name] = field_value
                            
                            # Also try direct field name mapping
                            if field_name in generated_form_data:
                                generated_form_data[field_name] = field_value
                    
                    form_data = generated_form_data
                
                # Execute test scenarios
                scenarios = test_scenarios or ['happy_path']
                for scenario in scenarios:
                    scenario_result = await self._execute_form_scenario(
                        form, form_data, scenario, page_context
                    )
                    results.append(scenario_result)
            
            # Generate final result
            final_result = {
                'success': True,
                'url': url,
                'forms_found': len(forms),
                'scenarios_executed': len(results),
                'results': results,
                'session_id': self.session_data['session_id'],
                'page_context': {
                    'credentials_found': page_context['has_test_credentials'],
                    'instructions_found': len(page_context['instructions']) > 0
                },
                'api_usage': self.data_generator.ai_service.get_api_usage_metrics() if self.data_generator.ai_service.is_available() else {}
            }
            
            self.session_data['forms_processed'].append(url)
            self.session_data['results'].append(final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error filling form at {url}: {e}")
            error_result = {
                'success': False,
                'url': url,
                'error': str(e),
                'session_id': self.session_data['session_id']
            }
            self.session_data['errors'].append(error_result)
            return error_result
        
        finally:
            await self.playwright_client.cleanup()
    
    async def fill_power_apps_form(self, app_url: str, form_data: Optional[Dict[str, Any]] = None,
                                  test_scenarios: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fill out a Power Apps form with specialized handling.
        
        Args:
            app_url: URL of the Power Apps application
            form_data: Optional pre-defined form data
            test_scenarios: List of test scenarios to execute
            
        Returns:
            Results of the Power Apps form filling operation
        """
        logger.info(f"Starting Power Apps form filling for: {app_url}")
        
        try:
            # Initialize Power Apps handler
            await self.power_apps_handler.initialize(self.playwright_client)
            
            # Navigate to Power Apps
            navigation_result = await self.power_apps_handler.navigate_to_app(app_url)
            if not navigation_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to load Power App: {navigation_result.get('error')}"
                }
            
            # Wait for app to load and detect forms
            await self.power_apps_handler.wait_for_app_load()
            
            # First analyze the full page context for any credentials or instructions
            page_context = await self.form_detector.analyze_page_context(self.playwright_client.page)
            logger.info(f"Power Apps page context analyzed. Found credentials: {page_context['has_test_credentials']}")
            
            forms = await self.power_apps_handler.detect_power_apps_forms()
            
            if not forms:
                return {
                    'success': False,
                    'error': 'No Power Apps forms detected'
                }
            
            # Process Power Apps forms
            results = []
            for form in forms:
                if not form_data:
                    form_data = await self.data_generator.generate_power_apps_data(form, page_context)
                
                scenarios = test_scenarios or ['happy_path', 'validation_test']
                for scenario in scenarios:
                    scenario_result = await self.power_apps_handler.fill_form(
                        form, form_data, scenario
                    )
                    results.append(scenario_result)
            
            return {
                'success': True,
                'app_url': app_url,
                'forms_found': len(forms),
                'scenarios_executed': len(results),
                'results': results,
                'session_id': self.session_data['session_id']
            }
            
        except Exception as e:
            logger.error(f"Error filling Power Apps form: {e}")
            return {
                'success': False,
                'app_url': app_url,
                'error': str(e),
                'session_id': self.session_data['session_id']
            }
    
    async def batch_fill_forms(self, urls: List[str], 
                              form_data_map: Optional[Dict[str, Dict[str, Any]]] = None,
                              test_scenarios: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fill out multiple forms in batch.
        
        Args:
            urls: List of URLs containing forms to fill
            form_data_map: Optional mapping of URL to form data
            test_scenarios: List of test scenarios to execute
            
        Returns:
            Batch processing results
        """
        logger.info(f"Starting batch form filling for {len(urls)} URLs")
        
        batch_results = {
            'success': True,
            'total_urls': len(urls),
            'processed_urls': 0,
            'successful_fills': 0,
            'failed_fills': 0,
            'results': [],
            'session_id': self.session_data['session_id']
        }
        
        for url in urls:
            try:
                # Get form data for this URL
                form_data = form_data_map.get(url) if form_data_map else None
                
                # Fill the form
                result = await self.fill_form(url, form_data, test_scenarios)
                
                batch_results['results'].append(result)
                batch_results['processed_urls'] += 1
                
                if result['success']:
                    batch_results['successful_fills'] += 1
                else:
                    batch_results['failed_fills'] += 1
                    
                # Small delay between forms to be respectful
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                batch_results['results'].append({
                    'success': False,
                    'url': url,
                    'error': str(e)
                })
                batch_results['failed_fills'] += 1
                batch_results['processed_urls'] += 1
        
        # Update overall success status
        batch_results['success'] = batch_results['failed_fills'] == 0
        
        # Add API usage metrics
        if self.data_generator.ai_service.is_available():
            batch_results['api_usage'] = self.data_generator.ai_service.get_api_usage_metrics()
        
        return batch_results
    
    async def test_form_validation(self, url: str, validation_scenarios: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Test form validation by submitting invalid data.
        
        Args:
            url: URL of the page containing the form
            validation_scenarios: List of validation scenarios to test
            
        Returns:
            Validation test results
        """
        logger.info(f"Starting form validation testing for: {url}")
        
        scenarios = validation_scenarios or [
            'empty_required_fields',
            'invalid_email',
            'invalid_phone',
            'sql_injection_attempt',
            'xss_attempt',
            'boundary_values'
        ]
        
        try:
            await self.playwright_client.initialize()
            await self.playwright_client.navigate_to(url)
            
            forms = await self.form_detector.detect_forms(self.playwright_client.page)
            if not forms:
                return {
                    'success': False,
                    'error': 'No forms detected for validation testing'
                }
            
            validation_results = []
            for form in forms:
                for scenario in scenarios:
                    # Generate invalid data for this scenario
                    invalid_data = await self.data_generator.generate_invalid_data(form, scenario)
                    
                    # Execute validation test
                    result = await self._execute_validation_test(form, invalid_data, scenario)
                    validation_results.append(result)
            
            return {
                'success': True,
                'url': url,
                'validation_scenarios': len(scenarios),
                'forms_tested': len(forms),
                'results': validation_results,
                'session_id': self.session_data['session_id']
            }
            
        except Exception as e:
            logger.error(f"Error during validation testing: {e}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'session_id': self.session_data['session_id']
            }
        
        finally:
            await self.playwright_client.cleanup()
    
    async def generate_test_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive test report for the current session.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            Generated report data
        """
        return await self.reporter.generate_report(self.session_data, output_path)
    
    async def _execute_form_scenario(self, form: Dict[str, Any], 
                                   form_data: Dict[str, Any], 
                                   scenario: str,
                                   page_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific test scenario for a form."""
        logger.info(f"Executing scenario: {scenario}")
        
        try:
            # Use any page instructions or context for improved form filling
            if page_context and page_context.get('instructions'):
                logger.info(f"Using {len(page_context['instructions'])} page instructions to guide form filling")
            
            # Fill out the form fields
            fill_result = await self._fill_form_fields(form, form_data)
            if not fill_result['success']:
                return {
                    'success': False,
                    'scenario': scenario,
                    'error': f"Failed to fill form: {fill_result.get('error')}"
                }
            
            # Submit the form
            submit_result = await self._submit_form(form)
            
            # Validate the response
            validation_result = await self._validate_form_response(scenario)
            
            return {
                'success': True,
                'scenario': scenario,
                'fill_result': fill_result,
                'submit_result': submit_result,
                'validation_result': validation_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'scenario': scenario,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fill_form_fields(self, form: Dict[str, Any], 
                              form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill out form fields with the provided data."""
        filled_fields = []
        errors = []
        
        for field in form.get('fields', []):
            try:
                field_name = field.get('name') or field.get('id')
                field_value = form_data.get(field_name)
                
                if field_value is not None:
                    fill_success = await self.playwright_client.fill_field(
                        field, field_value
                    )
                    
                    if fill_success:
                        filled_fields.append({
                            'field': field_name,
                            'value': field_value,
                            'success': True
                        })
                    else:
                        errors.append(f"Failed to fill field: {field_name}")
                        
            except Exception as e:
                errors.append(f"Error filling field {field_name}: {str(e)}")
        
        return {
            'success': len(errors) == 0,
            'filled_fields': len(filled_fields),
            'total_fields': len(form.get('fields', [])),
            'errors': errors
        }
    
    async def _submit_form(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """Submit the form and capture the response."""
        try:
            submit_button = form.get('submit_button')
            if not submit_button:
                return {
                    'success': False,
                    'error': 'No submit button found'
                }
            
            # Click submit button
            await self.playwright_client.click_element(submit_button)
            
            # Wait for response
            await self.playwright_client.wait_for_response()
            
            return {
                'success': True,
                'submitted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _validate_form_response(self, scenario: str) -> Dict[str, Any]:
        """Validate the form submission response."""
        try:
            # Check for success/error messages
            page_content = await self.playwright_client.get_page_content()
            
            # Look for common success indicators
            success_indicators = [
                'success', 'submitted', 'thank you', 'received',
                'confirmation', 'complete'
            ]
            
            # Look for common error indicators  
            error_indicators = [
                'error', 'failed', 'invalid', 'required',
                'missing', 'incorrect'
            ]
            
            has_success = any(indicator in page_content.lower() 
                            for indicator in success_indicators)
            has_error = any(indicator in page_content.lower() 
                          for indicator in error_indicators)
            
            return {
                'success': has_success and not has_error,
                'has_success_message': has_success,
                'has_error_message': has_error,
                'scenario': scenario,
                'page_title': await self.playwright_client.get_page_title()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_validation_test(self, form: Dict[str, Any], 
                                     invalid_data: Dict[str, Any], 
                                     scenario: str) -> Dict[str, Any]:
        """Execute a validation test with invalid data."""
        try:
            # Fill form with invalid data
            fill_result = await self._fill_form_fields(form, invalid_data)
            
            # Attempt to submit
            submit_result = await self._submit_form(form)
            
            # Check if validation errors are properly displayed
            validation_check = await self._check_validation_errors()
            
            return {
                'success': True,
                'scenario': scenario,
                'fill_result': fill_result,
                'submit_result': submit_result,
                'validation_working': validation_check['has_validation_errors'],
                'validation_details': validation_check
            }
            
        except Exception as e:
            return {
                'success': False,
                'scenario': scenario,
                'error': str(e)
            }
    
    async def _check_validation_errors(self) -> Dict[str, Any]:
        """Check if validation errors are properly displayed."""
        try:
            page_content = await self.playwright_client.get_page_content()
            
            validation_indicators = [
                'required', 'invalid', 'error', 'please enter',
                'must be', 'cannot be empty', 'field is required'
            ]
            
            has_validation_errors = any(indicator in page_content.lower() 
                                      for indicator in validation_indicators)
            
            return {
                'has_validation_errors': has_validation_errors,
                'page_content_length': len(page_content)
            }
            
        except Exception as e:
            return {
                'has_validation_errors': False,
                'error': str(e)
            }
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"formgenius_{timestamp}"
