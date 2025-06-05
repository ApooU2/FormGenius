"""
Script Generator Agent for FormGenius.
Responsible for generating Playwright test scripts based on test scenarios and page analysis.
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Agent for generating Playwright test scripts."""
    
    def __init__(self):
        """Initialize the script generator."""
        self.script_templates = self._load_script_templates()
        self.selector_strategies = self._load_selector_strategies()
        self.assertion_patterns = self._load_assertion_patterns()
    
    def generate_test_script(self, scenario: Dict[str, Any], page_analysis: Dict[str, Any]) -> str:
        """
        Generate a complete Playwright test script for a scenario.
        
        Args:
            scenario: Test scenario details
            page_analysis: Page analysis results
            
        Returns:
            Complete Playwright test script
        """
        script_parts = []
        
        # Add imports and setup
        script_parts.append(self._generate_imports())
        script_parts.append(self._generate_test_class(scenario, page_analysis))
        
        # Generate test method
        test_method = self._generate_test_method(scenario, page_analysis)
        script_parts.append(test_method)
        
        # Add helper methods if needed
        helper_methods = self._generate_helper_methods(scenario, page_analysis)
        if helper_methods:
            script_parts.extend(helper_methods)
        
        return '\n\n'.join(script_parts)
    
    def generate_test_suite(self, scenarios: List[Dict[str, Any]], 
                          website_analysis: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate a complete test suite with multiple test files.
        
        Args:
            scenarios: List of test scenarios
            website_analysis: Website analysis results
            
        Returns:
            Dictionary mapping file names to script content
        """
        test_files = {}
        
        # Group scenarios by category and page
        grouped_scenarios = self._group_scenarios(scenarios)
        
        for group_name, group_scenarios in grouped_scenarios.items():
            # Generate test file for each group
            file_content = self._generate_test_file(group_scenarios, website_analysis)
            file_name = self._generate_file_name(group_name, group_scenarios)
            test_files[file_name] = file_content
        
        # Generate conftest.py for shared fixtures
        test_files['conftest.py'] = self._generate_conftest()
        
        # Generate pytest.ini configuration
        test_files['pytest.ini'] = self._generate_pytest_config()
        
        return test_files
    
    def generate_page_object(self, page_analysis: Dict[str, Any]) -> str:
        """
        Generate a Page Object Model class for a page.
        
        Args:
            page_analysis: Page analysis results
            
        Returns:
            Page Object Model class code
        """
        page_url = page_analysis.get('url', '')
        page_title = page_analysis.get('title', 'Page')
        class_name = self._generate_class_name(page_title, page_url)
        
        script_parts = []
        
        # Imports
        script_parts.append(self._generate_page_object_imports())
        
        # Class definition
        class_code = self._generate_page_object_class(class_name, page_analysis)
        script_parts.append(class_code)
        
        return '\n\n'.join(script_parts)
    
    def _generate_imports(self) -> str:
        """Generate necessary imports for test scripts."""
        return '''import pytest
import asyncio
from playwright.async_api import Page, Browser, BrowserContext, expect
from typing import Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)'''
    
    def _generate_test_class(self, scenario: Dict[str, Any], page_analysis: Dict[str, Any]) -> str:
        """Generate test class structure."""
        class_name = self._generate_test_class_name(scenario)
        page_url = page_analysis.get('url', '')
        
        return f'''class {class_name}:
    """
    Test class for: {scenario.get('description', 'Test scenario')}
    Page: {page_url}
    Category: {scenario.get('category', 'functional')}
    Priority: {scenario.get('priority', 'medium')}
    """
    
    @pytest.fixture(autouse=True)
    async def setup(self, page: Page):
        """Setup method run before each test."""
        self.page = page
        self.base_url = "{page_url}"
        
        # Set up page with reasonable defaults
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        await self.page.set_extra_http_headers({{"User-Agent": "FormGenius-TestBot/1.0"}})
        
        # Navigate to the test page
        await self.page.goto(self.base_url, wait_until="networkidle")
        
        # Wait for page to be ready
        await self.page.wait_for_load_state("domcontentloaded")'''
    
    def _generate_test_method(self, scenario: Dict[str, Any], page_analysis: Dict[str, Any]) -> str:
        """Generate the main test method."""
        method_name = self._generate_method_name(scenario.get('name', 'test'))
        steps = scenario.get('steps', [])
        expected_result = scenario.get('expected_result', 'Test passes')
        
        # Generate test steps
        test_steps = []
        for i, step in enumerate(steps):
            step_code = self._generate_step_code(step, page_analysis, i)
            if step_code:
                test_steps.append(step_code)
        
        # Generate assertions based on expected result
        assertions = self._generate_assertions(expected_result, scenario, page_analysis)
        
        test_code = f'''    async def {method_name}(self):
        """
        {scenario.get('description', 'Test method')}
        
        Steps:
        {chr(10).join(f"        {i+1}. {step}" for i, step in enumerate(steps))}
        
        Expected Result: {expected_result}
        """
        try:
            logger.info("Starting test: {scenario.get('name', 'Unknown test')}")
            
            # Test implementation
{chr(10).join(f"            {step}" for step in test_steps)}
            
            # Assertions
{chr(10).join(f"            {assertion}" for assertion in assertions)}
            
            logger.info("Test completed successfully: {scenario.get('name', 'Unknown test')}")
            
        except Exception as e:
            logger.error(f"Test failed: {scenario.get('name', 'Unknown test')} - {{e}}")
            await self._capture_failure_screenshot(f"{method_name}_failure")
            raise'''
        
        return test_code
    
    def _generate_step_code(self, step: str, page_analysis: Dict[str, Any], step_index: int) -> str:
        """Generate code for a specific test step."""
        step_lower = step.lower()
        
        # Navigation steps
        if 'navigate' in step_lower:
            return '# Navigation handled in setup'
        
        # Form filling steps
        if 'fill' in step_lower or 'enter' in step_lower:
            return self._generate_form_fill_code(step, page_analysis)
        
        # Click steps
        if 'click' in step_lower:
            return self._generate_click_code(step, page_analysis)
        
        # Verification steps
        if 'verify' in step_lower or 'check' in step_lower:
            return self._generate_verification_code(step, page_analysis)
        
        # Submit steps
        if 'submit' in step_lower:
            return self._generate_submit_code(step, page_analysis)
        
        # Wait steps
        if 'wait' in step_lower:
            return 'await self.page.wait_for_timeout(1000)  # Wait for page to stabilize'
        
        # Generic step
        return f'# Step {step_index + 1}: {step}'
    
    def _generate_form_fill_code(self, step: str, page_analysis: Dict[str, Any]) -> str:
        """Generate code for form filling steps."""
        forms = page_analysis.get('forms', [])
        if not forms:
            return '# No forms found on page'
        
        form_code_parts = []
        
        # Determine which form fields to fill based on step description
        for form in forms:
            fields = form.get('fields', [])
            
            for field in fields:
                field_type = field.get('type', 'text')
                field_name = field.get('name', '')
                field_id = field.get('id', '')
                
                # Generate selector
                selector = self._generate_field_selector(field)
                
                # Generate appropriate fill code based on field type
                if field_type == 'email':
                    form_code_parts.append(f'await self.page.fill("{selector}", "test@example.com")')
                elif field_type == 'password':
                    form_code_parts.append(f'await self.page.fill("{selector}", "TestPassword123!")')
                elif field_type == 'text':
                    if 'name' in field_name.lower() or 'name' in field_id.lower():
                        form_code_parts.append(f'await self.page.fill("{selector}", "Test User")')
                    else:
                        form_code_parts.append(f'await self.page.fill("{selector}", "Test Data")')
                elif field_type == 'tel':
                    form_code_parts.append(f'await self.page.fill("{selector}", "+1234567890")')
                elif field_type == 'url':
                    form_code_parts.append(f'await self.page.fill("{selector}", "https://example.com")')
                elif field_type == 'number':
                    form_code_parts.append(f'await self.page.fill("{selector}", "123")')
                elif field_type == 'date':
                    form_code_parts.append(f'await self.page.fill("{selector}", "2024-01-01")')
                elif field_type == 'checkbox':
                    form_code_parts.append(f'await self.page.check("{selector}")')
                elif field_type == 'radio':
                    form_code_parts.append(f'await self.page.check("{selector}")')
                elif field.get('tag') == 'select':
                    form_code_parts.append(f'await self.page.select_option("{selector}", index=0)')
                elif field.get('tag') == 'textarea':
                    form_code_parts.append(f'await self.page.fill("{selector}", "Test message content")')
        
        if form_code_parts:
            return '\n            '.join(form_code_parts)
        
        return '# Fill form fields with appropriate test data'
    
    def _generate_click_code(self, step: str, page_analysis: Dict[str, Any]) -> str:
        """Generate code for click actions."""
        interactive_elements = page_analysis.get('interactive_elements', [])
        
        # Look for buttons, links, or specific elements mentioned in the step
        step_lower = step.lower()
        
        if 'submit' in step_lower or 'button' in step_lower:
            # Find submit buttons
            submit_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Send")',
                '[data-testid*="submit"]'
            ]
            return f'await self.page.click("{submit_selectors[0]}")'
        
        elif 'login' in step_lower:
            login_selectors = [
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'input[value*="Login"]',
                '[data-testid*="login"]'
            ]
            return f'await self.page.click("{login_selectors[0]}")'
        
        elif 'register' in step_lower or 'signup' in step_lower:
            register_selectors = [
                'button:has-text("Register")',
                'button:has-text("Sign Up")',
                'input[value*="Register"]',
                '[data-testid*="register"]'
            ]
            return f'await self.page.click("{register_selectors[0]}")'
        
        elif 'link' in step_lower:
            # Generic link clicking
            return 'await self.page.click("a:first-child")'
        
        else:
            # Generic button clicking
            return 'await self.page.click("button:first-child")'
    
    def _generate_verification_code(self, step: str, page_analysis: Dict[str, Any]) -> str:
        """Generate code for verification steps."""
        step_lower = step.lower()
        
        if 'error' in step_lower or 'message' in step_lower:
            return '''# Verify error message is displayed
            error_message = await self.page.locator(".error, .alert-danger, [role='alert']").first
            await expect(error_message).to_be_visible()'''
        
        elif 'success' in step_lower:
            return '''# Verify success message or redirection
            # Check for success message
            success_elements = self.page.locator(".success, .alert-success, [role='status']")
            if await success_elements.count() > 0:
                await expect(success_elements.first).to_be_visible()
            else:
                # Check for URL change indicating success
                await self.page.wait_for_url("**/dashboard**", timeout=5000)'''
        
        elif 'visible' in step_lower or 'display' in step_lower:
            return '# Verify element visibility'
        
        elif 'redirect' in step_lower or 'navigation' in step_lower:
            return 'await self.page.wait_for_url("**/*", timeout=5000)'
        
        return '# Verification step'
    
    def _generate_submit_code(self, step: str, page_analysis: Dict[str, Any]) -> str:
        """Generate code for form submission."""
        return '''# Submit the form
        submit_button = self.page.locator('input[type="submit"], button[type="submit"], button:has-text("Submit")')
        await submit_button.click()
        
        # Wait for response
        await self.page.wait_for_load_state("networkidle")'''
    
    def _generate_assertions(self, expected_result: str, scenario: Dict[str, Any], 
                           page_analysis: Dict[str, Any]) -> List[str]:
        """Generate assertion code based on expected result."""
        assertions = []
        expected_lower = expected_result.lower()
        
        if 'success' in expected_lower:
            assertions.extend([
                '# Verify successful operation',
                'success_indicators = self.page.locator(".success, .alert-success, [data-testid*=\\"success\\"]")',
                'if await success_indicators.count() > 0:',
                '    await expect(success_indicators.first).to_be_visible()',
                'else:',
                '    # Alternative: Check for URL change or absence of error',
                '    error_indicators = self.page.locator(".error, .alert-danger, [data-testid*=\\"error\\"]")',
                '    await expect(error_indicators).to_have_count(0)'
            ])
        
        elif 'error' in expected_lower or 'fail' in expected_lower:
            assertions.extend([
                '# Verify error is displayed',
                'error_message = self.page.locator(".error, .alert-danger, [role=\\"alert\\"], [data-testid*=\\"error\\"]")',
                'await expect(error_message.first).to_be_visible()',
                'await expect(error_message.first).to_have_text(re.compile(r".+", re.IGNORECASE))'
            ])
        
        elif 'redirect' in expected_lower or 'navigate' in expected_lower:
            assertions.extend([
                '# Verify navigation occurred',
                'current_url = self.page.url',
                'assert current_url != self.base_url, "Page should have navigated to a different URL"'
            ])
        
        elif 'form' in expected_lower and 'submit' in expected_lower:
            assertions.extend([
                '# Verify form submission',
                '# Check for success message or URL change',
                'await asyncio.sleep(1)  # Allow time for submission processing',
                'current_url = self.page.url',
                'success_message = self.page.locator(".success, .alert-success")',
                'assert (await success_message.count() > 0) or (current_url != self.base_url), "Form submission should show success or redirect"'
            ])
        
        else:
            assertions.extend([
                '# Generic assertion - verify page is responsive',
                'await expect(self.page).to_have_title(re.compile(r".+", re.IGNORECASE))',
                'body = self.page.locator("body")',
                'await expect(body).to_be_visible()'
            ])
        
        return assertions
    
    def _generate_helper_methods(self, scenario: Dict[str, Any], 
                               page_analysis: Dict[str, Any]) -> List[str]:
        """Generate helper methods for the test class."""
        helpers = []
        
        # Screenshot capture helper
        helpers.append('''    async def _capture_failure_screenshot(self, test_name: str):
        """Capture screenshot on test failure."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{test_name}_{timestamp}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Failure screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Failed to capture screenshot: {e}")''')
        
        # Form validation helper
        if scenario.get('category') == 'functional' and 'form' in scenario.get('name', '').lower():
            helpers.append('''    async def _validate_form_errors(self, expected_errors: List[str]):
        """Validate that expected form errors are displayed."""
        for error_text in expected_errors:
            error_element = self.page.locator(f'text="{error_text}"')
            await expect(error_element).to_be_visible()''')
        
        # Wait for element helper
        helpers.append('''    async def _wait_for_element(self, selector: str, timeout: int = 5000):
        """Wait for element to be visible with custom timeout."""
        element = self.page.locator(selector)
        await expect(element).to_be_visible(timeout=timeout)
        return element''')
        
        return helpers
    
    def _generate_field_selector(self, field: Dict[str, Any]) -> str:
        """Generate the best selector for a form field."""
        # Priority order: data-testid, id, name, placeholder, type
        
        field_id = field.get('id', '')
        field_name = field.get('name', '')
        field_type = field.get('type', '')
        placeholder = field.get('placeholder', '')
        
        if field_id:
            return f'#{field_id}'
        elif field_name:
            return f'[name="{field_name}"]'
        elif placeholder:
            return f'[placeholder="{placeholder}"]'
        elif field_type:
            return f'input[type="{field_type}"]'
        else:
            return 'input'
    
    def _group_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group scenarios by category and page for organizing test files."""
        groups = {}
        
        for scenario in scenarios:
            # Group by category first
            category = scenario.get('category', 'functional')
            page_url = scenario.get('page_url', '')
            
            # Create a group key combining category and page
            if page_url:
                page_name = self._extract_page_name(page_url)
                group_key = f"{category}_{page_name}"
            else:
                group_key = category
            
            if group_key not in groups:
                groups[group_key] = []
            
            groups[group_key].append(scenario)
        
        return groups
    
    def _generate_test_file(self, scenarios: List[Dict[str, Any]], 
                          website_analysis: List[Dict[str, Any]]) -> str:
        """Generate a complete test file for a group of scenarios."""
        file_parts = []
        
        # File header with imports
        file_parts.append(self._generate_file_header(scenarios))
        
        # Generate test classes for each scenario
        for scenario in scenarios:
            # Find corresponding page analysis
            page_analysis = self._find_page_analysis(scenario, website_analysis)
            
            if page_analysis:
                test_class = self._generate_test_class(scenario, page_analysis)
                test_method = self._generate_test_method(scenario, page_analysis)
                helper_methods = self._generate_helper_methods(scenario, page_analysis)
                
                class_code = f"{test_class}\n\n{test_method}"
                if helper_methods:
                    class_code += "\n\n" + "\n\n".join(helper_methods)
                
                file_parts.append(class_code)
        
        return '\n\n'.join(file_parts)
    
    def _generate_file_header(self, scenarios: List[Dict[str, Any]]) -> str:
        """Generate file header with imports and metadata."""
        categories = list(set(scenario.get('category', 'functional') for scenario in scenarios))
        scenario_names = [scenario.get('name', 'Unknown') for scenario in scenarios]
        
        return f'''"""
FormGenius Test Suite - {", ".join(categories).title()} Tests

Generated test cases:
{chr(10).join(f"- {name}" for name in scenario_names)}

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import pytest
import asyncio
import re
from datetime import datetime
from playwright.async_api import Page, Browser, BrowserContext, expect
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)'''
    
    def _generate_conftest(self) -> str:
        """Generate conftest.py for shared fixtures."""
        return '''"""
Pytest configuration and shared fixtures for FormGenius test suite.
"""

import pytest
import asyncio
from playwright.async_api import Browser, BrowserContext, Page
from typing import Generator, AsyncGenerator
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def browser(playwright):
    """Launch browser for the test session."""
    browser = await playwright.chromium.launch(
        headless=os.getenv("HEADLESS", "true").lower() == "true",
        slow_mo=int(os.getenv("SLOWMO_MS", "100"))
    )
    yield browser
    await browser.close()

@pytest.fixture(scope="function")
async def context(browser: Browser):
    """Create a new browser context for each test."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="FormGenius-TestBot/1.0"
    )
    yield context
    await context.close()

@pytest.fixture(scope="function")
async def page(context: BrowserContext):
    """Create a new page for each test."""
    page = await context.new_page()
    
    # Set up default timeouts
    page.set_default_timeout(int(os.getenv("DEFAULT_TIMEOUT", "30000")))
    
    yield page
    await page.close()

@pytest.fixture(autouse=True)
def setup_test_artifacts():
    """Ensure test artifacts directory exists."""
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("videos", exist_ok=True)
    os.makedirs("traces", exist_ok=True)

def pytest_runtest_makereport(item, call):
    """Hook to capture test results for reporting."""
    if call.when == "call":
        if call.excinfo is not None:
            # Test failed, could trigger additional cleanup here
            pass
'''
    
    def _generate_pytest_config(self) -> str:
        """Generate pytest.ini configuration."""
        return '''[tool:pytest]
minversion = 6.0
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --asyncio-mode=auto
    -p no:warnings
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    functional: Functional test cases
    ui: User interface test cases
    accessibility: Accessibility test cases
    performance: Performance test cases
    security: Security test cases
    integration: Integration test cases
    critical: Critical priority tests
    high: High priority tests
    medium: Medium priority tests
    low: Low priority tests
    smoke: Smoke test cases
    regression: Regression test cases
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
'''
    
    def _generate_page_object_imports(self) -> str:
        """Generate imports for page object classes."""
        return '''from playwright.async_api import Page, Locator, expect
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)'''
    
    def _generate_page_object_class(self, class_name: str, page_analysis: Dict[str, Any]) -> str:
        """Generate a Page Object Model class."""
        page_url = page_analysis.get('url', '')
        forms = page_analysis.get('forms', [])
        interactive_elements = page_analysis.get('interactive_elements', [])
        
        # Generate locators for common elements
        locators = self._generate_page_locators(page_analysis)
        
        # Generate methods for interactions
        methods = self._generate_page_methods(page_analysis)
        
        return f'''class {class_name}:
    """
    Page Object Model for: {page_url}
    
    This class provides methods to interact with page elements
    and encapsulates the page structure for maintainable tests.
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.url = "{page_url}"
        
        # Element locators
{chr(10).join(f"        {locator}" for locator in locators)}
    
    async def navigate(self):
        """Navigate to this page."""
        await self.page.goto(self.url, wait_until="networkidle")
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def is_loaded(self) -> bool:
        """Check if page is fully loaded."""
        try:
            await self.page.wait_for_selector("body", timeout=5000)
            return True
        except:
            return False
    
{chr(10).join(methods)}'''
    
    def _generate_page_locators(self, page_analysis: Dict[str, Any]) -> List[str]:
        """Generate locator definitions for page elements."""
        locators = []
        
        # Common page elements
        locators.extend([
            'self.title = self.page.locator("title")',
            'self.body = self.page.locator("body")',
            'self.main = self.page.locator("main, [role=\\"main\\"]")'
        ])
        
        # Form elements
        forms = page_analysis.get('forms', [])
        for i, form in enumerate(forms):
            locators.append(f'self.form_{i} = self.page.locator("form").nth({i})')
            
            for field in form.get('fields', []):
                if field.get('id'):
                    field_name = field['id'].replace('-', '_').replace(' ', '_')
                    locators.append(f'self.{field_name} = self.page.locator("#{field["id"]}")')
                elif field.get('name'):
                    field_name = field['name'].replace('-', '_').replace(' ', '_')
                    locators.append(f'self.{field_name} = self.page.locator("[name=\\"{field["name"]}\\"]")')
        
        # Common interactive elements
        locators.extend([
            'self.submit_button = self.page.locator("input[type=\\"submit\\"], button[type=\\"submit\\"]")',
            'self.buttons = self.page.locator("button")',
            'self.links = self.page.locator("a[href]")',
            'self.inputs = self.page.locator("input, textarea, select")'
        ])
        
        return locators
    
    def _generate_page_methods(self, page_analysis: Dict[str, Any]) -> List[str]:
        """Generate interaction methods for the page."""
        methods = []
        
        # Form submission method
        if page_analysis.get('forms'):
            methods.append('''    async def submit_form(self, form_index: int = 0, data: Dict[str, Any] = None):
        """Submit a form with provided data."""
        if data:
            await self.fill_form(form_index, data)
        
        submit_button = self.page.locator(f"form:nth-child({form_index + 1}) input[type='submit'], form:nth-child({form_index + 1}) button[type='submit']")
        await submit_button.click()
        await self.page.wait_for_load_state("networkidle")''')
            
            methods.append('''    async def fill_form(self, form_index: int = 0, data: Dict[str, Any] = None):
        """Fill form fields with provided data."""
        if not data:
            return
        
        for field_name, value in data.items():
            try:
                field = self.page.locator(f"form:nth-child({form_index + 1}) [name='{field_name}'], form:nth-child({form_index + 1}) #{field_name}")
                await field.fill(str(value))
            except Exception as e:
                logger.warning(f"Could not fill field {field_name}: {e}")''')
        
        # Navigation methods
        navigation = page_analysis.get('navigation', {})
        if navigation.get('has_main_navigation'):
            methods.append('''    async def click_nav_item(self, item_text: str):
        """Click a navigation item by text."""
        nav_item = self.page.locator(f"nav a:has-text('{item_text}')")
        await nav_item.click()
        await self.page.wait_for_load_state("networkidle")''')
        
        # Generic interaction methods
        methods.extend([
            '''    async def click_button(self, button_text: str):
        """Click a button by its text."""
        button = self.page.locator(f"button:has-text('{button_text}')")
        await button.click()''',
            
            '''    async def get_error_messages(self) -> List[str]:
        """Get all error messages displayed on the page."""
        error_elements = self.page.locator(".error, .alert-danger, [role='alert']")
        count = await error_elements.count()
        messages = []
        for i in range(count):
            text = await error_elements.nth(i).text_content()
            if text:
                messages.append(text.strip())
        return messages''',
            
            '''    async def get_success_messages(self) -> List[str]:
        """Get all success messages displayed on the page."""
        success_elements = self.page.locator(".success, .alert-success, [role='status']")
        count = await success_elements.count()
        messages = []
        for i in range(count):
            text = await success_elements.nth(i).text_content()
            if text:
                messages.append(text.strip())
        return messages'''
        ])
        
        return methods
    
    def _find_page_analysis(self, scenario: Dict[str, Any], 
                          website_analysis: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the page analysis that matches a scenario."""
        scenario_url = scenario.get('page_url', '')
        
        for page_analysis in website_analysis:
            if page_analysis.get('url') == scenario_url:
                return page_analysis
        
        # If exact match not found, return first page as fallback
        return website_analysis[0] if website_analysis else None
    
    def _generate_test_class_name(self, scenario: Dict[str, Any]) -> str:
        """Generate a test class name from scenario."""
        name = scenario.get('name', 'Test')
        # Convert to PascalCase and remove special characters
        class_name = 'Test' + ''.join(word.capitalize() for word in re.findall(r'\w+', name))
        return class_name
    
    def _generate_method_name(self, test_name: str) -> str:
        """Generate a test method name from test name."""
        # Convert to snake_case
        method_name = 'test_' + re.sub(r'[^\w\s]', '', test_name.lower())
        method_name = re.sub(r'\s+', '_', method_name)
        return method_name
    
    def _generate_class_name(self, page_title: str, page_url: str) -> str:
        """Generate a class name for Page Object Model."""
        # Use page title if available, otherwise extract from URL
        if page_title and page_title != 'Page':
            name_source = page_title
        else:
            name_source = self._extract_page_name(page_url)
        
        # Convert to PascalCase
        class_name = ''.join(word.capitalize() for word in re.findall(r'\w+', name_source))
        return class_name + 'Page'
    
    def _extract_page_name(self, url: str) -> str:
        """Extract a meaningful name from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            if path:
                # Use the last part of the path
                return path.split('/')[-1].replace('-', '_').replace('.html', '')
            else:
                # Use domain name
                return parsed.netloc.replace('.', '_').replace('-', '_')
        except:
            return 'page'
    
    def _generate_file_name(self, group_name: str, scenarios: List[Dict[str, Any]]) -> str:
        """Generate a file name for a test group."""
        # Clean group name
        clean_name = re.sub(r'[^\w]', '_', group_name.lower())
        return f"test_{clean_name}.py"
    
    def _load_script_templates(self) -> Dict[str, str]:
        """Load reusable script templates."""
        return {
            'basic_test': '''async def test_{method_name}(self):
                """
                {description}
                """
                # Test implementation
                pass''',
            
            'form_test': '''async def test_form_submission(self):
                """Test form submission with valid data."""
                # Fill form fields
                await self.page.fill('[name="field1"]', 'test_value')
                
                # Submit form
                await self.page.click('input[type="submit"]')
                
                # Verify result
                await expect(self.page.locator('.success')).to_be_visible()''',
            
            'navigation_test': '''async def test_navigation(self):
                """Test page navigation."""
                # Click navigation link
                await self.page.click('nav a:first-child')
                
                # Verify navigation
                await self.page.wait_for_url('**/target-page')'''
        }
    
    def _load_selector_strategies(self) -> Dict[str, List[str]]:
        """Load selector strategies for different element types."""
        return {
            'submit_button': [
                'input[type="submit"]',
                'button[type="submit"]',
                'button:has-text("Submit")',
                '[data-testid*="submit"]'
            ],
            'login_button': [
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'input[value*="Login"]',
                '[data-testid*="login"]'
            ],
            'error_message': [
                '.error',
                '.alert-danger',
                '[role="alert"]',
                '.validation-error',
                '[data-testid*="error"]'
            ],
            'success_message': [
                '.success',
                '.alert-success',
                '[role="status"]',
                '.notification-success',
                '[data-testid*="success"]'
            ]
        }
    
    def _load_assertion_patterns(self) -> Dict[str, str]:
        """Load common assertion patterns."""
        return {
            'element_visible': 'await expect({element}).to_be_visible()',
            'element_hidden': 'await expect({element}).to_be_hidden()',
            'text_contains': 'await expect({element}).to_contain_text("{text}")',
            'url_matches': 'await expect(self.page).to_have_url(re.compile(r"{pattern}"))',
            'title_contains': 'await expect(self.page).to_have_title(re.compile(r"{title}"))'
        }
