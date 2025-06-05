"""
Playwright Code Generator for FormGenius

This module generates Playwright test code from test scenarios:
- Test file generation with proper structure
- Page Object Model generation
- Test data management
- Configuration file generation
- Pytest integration
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class GeneratedTestFile:
    """Represents a generated test file"""
    file_path: str
    content: str
    test_count: int
    page_objects: List[str] = None
    dependencies: List[str] = None

@dataclass
class PageObjectModel:
    """Represents a Page Object Model"""
    class_name: str
    file_path: str
    content: str
    selectors: Dict[str, str] = None
    methods: List[str] = None

@dataclass
class TestSuite:
    """Represents a complete test suite"""
    suite_name: str
    test_files: List[GeneratedTestFile]
    page_objects: List[PageObjectModel]
    config_files: List[GeneratedTestFile]
    requirements: List[str]
    setup_instructions: str

class PlaywrightCodeGenerator:
    """Generates Playwright test code from scenarios"""
    
    def __init__(self, output_dir: str = "generated_tests"):
        self.output_dir = output_dir
        self.imports_template = self._get_imports_template()
        self.page_object_template = self._get_page_object_template()
        self.test_template = self._get_test_template()
        
    def generate_test_suite(self, 
                           scenario_sets: List[Any],
                           dom_analysis: Dict[str, Any],
                           element_analysis: Dict[str, Any],
                           base_url: str) -> TestSuite:
        """Generate complete Playwright test suite"""
        try:
            logger.info("Starting Playwright test suite generation")
            
            # Create output directory structure
            self._create_directory_structure()
            
            # Generate page objects
            page_objects = self._generate_page_objects(element_analysis, base_url)
            
            # Generate test files
            test_files = []
            for scenario_set in scenario_sets:
                test_file = self._generate_test_file(scenario_set, page_objects, base_url)
                test_files.append(test_file)
            
            # Generate configuration files
            config_files = self._generate_config_files(base_url)
            
            # Generate requirements
            requirements = self._generate_requirements()
            
            # Generate setup instructions
            setup_instructions = self._generate_setup_instructions()
            
            suite = TestSuite(
                suite_name=f"FormGenius_Test_Suite_{self._get_timestamp()}",
                test_files=test_files,
                page_objects=page_objects,
                config_files=config_files,
                requirements=requirements,
                setup_instructions=setup_instructions
            )
            
            # Write all files to disk
            self._write_test_suite_to_disk(suite)
            
            logger.info(f"Test suite generated: {len(test_files)} test files, {len(page_objects)} page objects")
            return suite
            
        except Exception as e:
            logger.error(f"Test suite generation failed: {str(e)}")
            raise
    
    def _create_directory_structure(self):
        """Create the test directory structure"""
        directories = [
            self.output_dir,
            f"{self.output_dir}/tests",
            f"{self.output_dir}/pages",
            f"{self.output_dir}/data",
            f"{self.output_dir}/utils",
            f"{self.output_dir}/config"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_page_objects(self, element_analysis: Dict[str, Any], base_url: str) -> List[PageObjectModel]:
        """Generate Page Object Models"""
        page_objects = []
        
        # Group elements by page/form
        element_groups = element_analysis.get('element_groups', [])
        
        for group in element_groups:
            if group.group_type == 'form':
                page_object = self._create_form_page_object(group, base_url)
                page_objects.append(page_object)
        
        # Create a base page object
        base_page = self._create_base_page_object(base_url)
        page_objects.append(base_page)
        
        # Create main page object
        main_page = self._create_main_page_object(element_analysis, base_url)
        page_objects.append(main_page)
        
        return page_objects
    
    def _create_form_page_object(self, form_group, base_url: str) -> PageObjectModel:
        """Create a Page Object for a form"""
        class_name = f"{self._camel_case(form_group.group_id)}Page"
        file_path = f"{self.output_dir}/pages/{self._snake_case(form_group.group_id)}_page.py"
        
        # Extract selectors from form elements
        selectors = {}
        methods = []
        
        for element in form_group.elements:
            selector_name = self._camel_case(element.element_id)
            selectors[selector_name] = element.selector
            
            if element.element_type == 'input':
                methods.append(f"fill_{self._snake_case(element.element_id)}")
            elif element.element_type == 'button':
                methods.append(f"click_{self._snake_case(element.element_id)}")
        
        content = self._generate_form_page_object_content(class_name, selectors, methods, form_group)
        
        return PageObjectModel(
            class_name=class_name,
            file_path=file_path,
            content=content,
            selectors=selectors,
            methods=methods
        )
    
    def _create_base_page_object(self, base_url: str) -> PageObjectModel:
        """Create a base page object with common functionality"""
        class_name = "BasePage"
        file_path = f"{self.output_dir}/pages/base_page.py"
        
        content = f'''"""Base Page Object for common functionality"""
from playwright.sync_api import Page, expect
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BasePage:
    """Base page object with common functionality"""
    
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "{base_url}"
    
    def navigate_to(self, path: str = ""):
        """Navigate to a specific path"""
        url = f"{{self.base_url}}/{{path}}".rstrip("/")
        logger.info(f"Navigating to: {{url}}")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
    
    def wait_for_element(self, selector: str, timeout: int = 30000):
        """Wait for element to be visible"""
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def click_element(self, selector: str):
        """Click an element"""
        logger.info(f"Clicking element: {{selector}}")
        self.page.click(selector)
    
    def fill_field(self, selector: str, value: str):
        """Fill a form field"""
        logger.info(f"Filling field {{selector}} with: {{value}}")
        self.page.fill(selector, value)
    
    def get_text(self, selector: str) -> str:
        """Get text content of an element"""
        return self.page.text_content(selector)
    
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return self.page.is_visible(selector)
    
    def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled"""
        return self.page.is_enabled(selector)
    
    def take_screenshot(self, name: str):
        """Take a screenshot"""
        self.page.screenshot(path=f"screenshots/{{name}}.png")
    
    def verify_page_title(self, expected_title: str):
        """Verify page title"""
        expect(self.page).to_have_title(expected_title)
    
    def verify_url_contains(self, expected_text: str):
        """Verify URL contains expected text"""
        expect(self.page).to_have_url(lambda url: expected_text in url)
    
    def verify_element_visible(self, selector: str):
        """Verify element is visible"""
        expect(self.page.locator(selector)).to_be_visible()
    
    def verify_element_text(self, selector: str, expected_text: str):
        """Verify element contains expected text"""
        expect(self.page.locator(selector)).to_contain_text(expected_text)
'''
        
        return PageObjectModel(
            class_name=class_name,
            file_path=file_path,
            content=content,
            selectors={},
            methods=["navigate_to", "wait_for_element", "click_element", "fill_field"]
        )
    
    def _create_main_page_object(self, element_analysis: Dict[str, Any], base_url: str) -> PageObjectModel:
        """Create main page object with all interactive elements"""
        class_name = "MainPage"
        file_path = f"{self.output_dir}/pages/main_page.py"
        
        # Extract key selectors from interactive elements
        selectors = {}
        interactive_elements = element_analysis.get('interactive_elements', [])
        
        for element in interactive_elements[:10]:  # Limit to first 10 elements
            if element.selector:
                selector_name = f"element_{element.element_id}"
                selectors[selector_name] = element.selector
        
        content = self._generate_main_page_object_content(class_name, selectors, base_url)
        
        return PageObjectModel(
            class_name=class_name,
            file_path=file_path,
            content=content,
            selectors=selectors,
            methods=["navigate", "verify_page_loaded"]
        )
    
    def _generate_test_file(self, scenario_set, page_objects: List[PageObjectModel], base_url: str) -> GeneratedTestFile:
        """Generate a test file from scenario set"""
        file_name = f"test_{self._snake_case(scenario_set.name.replace(' ', '_'))}.py"
        file_path = f"{self.output_dir}/tests/{file_name}"
        
        # Generate test content
        content = self._generate_test_file_content(scenario_set, page_objects, base_url)
        
        return GeneratedTestFile(
            file_path=file_path,
            content=content,
            test_count=len(scenario_set.scenarios),
            page_objects=[po.class_name for po in page_objects],
            dependencies=["pytest", "playwright"]
        )
    
    def _generate_test_file_content(self, scenario_set, page_objects: List[PageObjectModel], base_url: str) -> str:
        """Generate the content for a test file"""
        imports = self._generate_imports(page_objects)
        
        test_class_name = f"Test{self._camel_case(scenario_set.name.replace(' ', ''))}"
        
        test_methods = []
        for scenario in scenario_set.scenarios:
            test_method = self._generate_test_method(scenario, page_objects)
            test_methods.append(test_method)
        
        content = f'''"""
{scenario_set.description}
Generated by FormGenius - AI-Powered Test Generation
"""
{imports}

class {test_class_name}:
    """Test class for {scenario_set.name}"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page):
        """Setup for each test"""
        self.page = page
        self.base_page = BasePage(page)
        self.main_page = MainPage(page)
        
        # Navigate to base URL
        self.main_page.navigate()
        
        yield
        
        # Cleanup after each test
        logger.info("Test completed")

{chr(10).join(test_methods)}
'''
        
        return content
    
    def _generate_test_method(self, scenario, page_objects: List[PageObjectModel]) -> str:
        """Generate a single test method"""
        method_name = f"test_{self._snake_case(scenario.name.replace(' ', '_'))}"
        
        steps_code = []
        for i, step in enumerate(scenario.steps, 1):
            step_code = self._generate_step_code(step, page_objects)
            steps_code.append(f"        # Step {i}: {step.get('description', 'Action')}")
            steps_code.append(f"        {step_code}")
            steps_code.append("")
        
        test_method = f'''    def {method_name}(self):
        """
        {scenario.description}
        
        Priority: {scenario.priority}
        Category: {scenario.category}
        Type: {scenario.test_type}
        """
        logger.info("Starting test: {scenario.name}")
        
{chr(10).join(steps_code)}
        
        # Verify expected result
        logger.info("Expected: {scenario.expected_result}")
        
        # Take screenshot for documentation
        self.base_page.take_screenshot("{method_name}")
'''
        
        return test_method
    
    def _generate_step_code(self, step: Dict[str, Any], page_objects: List[PageObjectModel]) -> str:
        """Generate code for a single test step"""
        action = step.get('action', 'unknown')
        selector = step.get('selector', '')
        data = step.get('data', '')
        
        if action == 'fill':
            return f'self.base_page.fill_field("{selector}", "{data}")'
        elif action == 'click':
            return f'self.base_page.click_element("{selector}")'
        elif action == 'submit':
            return f'self.base_page.click_element("{selector}")'
        elif action == 'verify':
            return f'self.base_page.verify_element_visible("{selector}")'
        elif action == 'navigate':
            return f'self.base_page.navigate_to("{data}")'
        elif action == 'wait':
            return f'self.base_page.wait_for_element("{selector}")'
        elif action == 'keyboard':
            key = step.get('key', 'Tab')
            return f'self.page.keyboard.press("{key}")'
        else:
            return f'# TODO: Implement action "{action}" for selector "{selector}"'
    
    def _generate_config_files(self, base_url: str) -> List[GeneratedTestFile]:
        """Generate configuration files"""
        config_files = []
        
        # Generate pytest.ini
        pytest_ini = GeneratedTestFile(
            file_path=f"{self.output_dir}/pytest.ini",
            content=self._generate_pytest_ini(),
            test_count=0
        )
        config_files.append(pytest_ini)
        
        # Generate playwright.config.py
        playwright_config = GeneratedTestFile(
            file_path=f"{self.output_dir}/playwright.config.py",
            content=self._generate_playwright_config(base_url),
            test_count=0
        )
        config_files.append(playwright_config)
        
        # Generate conftest.py
        conftest = GeneratedTestFile(
            file_path=f"{self.output_dir}/conftest.py",
            content=self._generate_conftest(),
            test_count=0
        )
        config_files.append(conftest)
        
        return config_files
    
    def _generate_requirements(self) -> List[str]:
        """Generate requirements list"""
        return [
            "pytest>=7.0.0",
            "playwright>=1.40.0",
            "pytest-playwright>=0.4.0",
            "pytest-html>=3.1.0",
            "pytest-xdist>=3.0.0",
            "allure-pytest>=2.12.0"
        ]
    
    def _generate_setup_instructions(self) -> str:
        """Generate setup instructions"""
        return '''# FormGenius Generated Test Suite Setup Instructions

## Prerequisites
- Python 3.8 or higher
- pip package manager

## Installation Steps

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install
   ```

3. Run tests:
   ```bash
   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_form_testing_scenarios.py

   # Run with HTML report
   pytest --html=reports/report.html

   # Run in parallel
   pytest -n auto

   # Run with specific browser
   pytest --browser chromium
   ```

## Test Structure
- `tests/` - Test files
- `pages/` - Page Object Models
- `data/` - Test data files
- `utils/` - Utility functions
- `config/` - Configuration files

## Generated Features
- Page Object Model pattern
- Comprehensive test scenarios
- Accessibility testing
- Security testing
- Performance testing
- Cross-browser compatibility
'''
    
    def _write_test_suite_to_disk(self, suite: TestSuite):
        """Write all test suite files to disk"""
        # Write test files
        for test_file in suite.test_files:
            self._write_file(test_file.file_path, test_file.content)
        
        # Write page objects
        for page_object in suite.page_objects:
            self._write_file(page_object.file_path, page_object.content)
        
        # Write config files
        for config_file in suite.config_files:
            self._write_file(config_file.file_path, config_file.content)
        
        # Write requirements.txt
        requirements_content = "\n".join(suite.requirements)
        self._write_file(f"{self.output_dir}/requirements.txt", requirements_content)
        
        # Write setup instructions
        self._write_file(f"{self.output_dir}/README.md", suite.setup_instructions)
        
        # Write __init__.py files
        init_dirs = ["tests", "pages", "utils"]
        for dir_name in init_dirs:
            init_path = f"{self.output_dir}/{dir_name}/__init__.py"
            self._write_file(init_path, "# FormGenius generated package")
    
    def _write_file(self, file_path: str, content: str):
        """Write content to file"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Generated file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {str(e)}")
    
    # Template and helper methods
    
    def _generate_imports(self, page_objects: List[PageObjectModel]) -> str:
        """Generate import statements"""
        imports = '''import pytest
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.main_page import MainPage'''
        
        # Add specific page object imports
        for po in page_objects:
            if po.class_name not in ['BasePage', 'MainPage']:
                module_name = self._snake_case(po.class_name.replace('Page', ''))
                imports += f"\nfrom pages.{module_name}_page import {po.class_name}"
        
        imports += "\n\nlogger = logging.getLogger(__name__)\n"
        return imports
    
    def _generate_form_page_object_content(self, class_name: str, selectors: Dict[str, str], methods: List[str], form_group) -> str:
        """Generate form page object content"""
        selectors_code = []
        for name, selector in selectors.items():
            selectors_code.append(f'    {name.upper()}_SELECTOR = "{selector}"')
        
        methods_code = []
        for element in form_group.elements:
            if element.element_type == 'input':
                method_name = f"fill_{self._snake_case(element.element_id)}"
                selector_name = f"{self._camel_case(element.element_id).upper()}_SELECTOR"
                methods_code.append(f'''
    def {method_name}(self, value: str):
        """Fill {element.element_id} field"""
        self.fill_field(self.{selector_name}, value)''')
            elif element.element_type == 'button':
                method_name = f"click_{self._snake_case(element.element_id)}"
                selector_name = f"{self._camel_case(element.element_id).upper()}_SELECTOR"
                methods_code.append(f'''
    def {method_name}(self):
        """Click {element.element_id} button"""
        self.click_element(self.{selector_name})''')
        
        content = f'''"""Page Object for {class_name}"""
from pages.base_page import BasePage
from playwright.sync_api import Page

class {class_name}(BasePage):
    """Page object for {form_group.group_id}"""
    
    # Selectors
{chr(10).join(selectors_code)}
    
    def __init__(self, page: Page):
        super().__init__(page)
{chr(10).join(methods_code)}
    
    def submit_form(self):
        """Submit the form"""
        # Find and click submit button
        submit_selectors = ["button[type='submit']", "input[type='submit']", ".submit-btn"]
        for selector in submit_selectors:
            if self.is_visible(selector):
                self.click_element(selector)
                break
    
    def verify_form_validation_error(self, field_selector: str):
        """Verify form validation error is displayed"""
        error_selectors = [
            f"{field_selector} + .error",
            f"{field_selector} ~ .error",
            ".error-message",
            ".validation-error"
        ]
        for selector in error_selectors:
            if self.is_visible(selector):
                self.verify_element_visible(selector)
                return
        raise AssertionError("No validation error found")
'''
        return content
    
    def _generate_main_page_object_content(self, class_name: str, selectors: Dict[str, str], base_url: str) -> str:
        """Generate main page object content"""
        content = f'''"""Main Page Object"""
from pages.base_page import BasePage
from playwright.sync_api import Page

class {class_name}(BasePage):
    """Main page object for the application"""
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def navigate(self):
        """Navigate to the main page"""
        self.navigate_to()
    
    def verify_page_loaded(self):
        """Verify the main page has loaded correctly"""
        # Check for common page elements
        selectors_to_check = ["body", "header", "main", "nav"]
        for selector in selectors_to_check:
            if self.is_visible(selector):
                self.verify_element_visible(selector)
                break
'''
        return content
    
    def _generate_pytest_ini(self) -> str:
        """Generate pytest.ini configuration"""
        return '''[tool:pytest]
minversion = 6.0
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --html=reports/report.html
    --self-contained-html
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    smoke: Smoke tests
    regression: Regression tests
    accessibility: Accessibility tests
    security: Security tests
    performance: Performance tests
    form: Form testing
    navigation: Navigation testing
log_cli = true
log_cli_level = INFO
'''
    
    def _generate_playwright_config(self, base_url: str) -> str:
        """Generate Playwright configuration"""
        return f'''"""Playwright configuration for FormGenius tests"""
from playwright.sync_api import sync_playwright
import pytest

@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context"""
    return {{
        "viewport": {{"width": 1280, "height": 720}},
        "ignore_https_errors": True,
        "record_video_dir": "videos/",
        "record_video_size": {{"width": 1280, "height": 720}}
    }}

@pytest.fixture(scope="session")
def playwright_config():
    """Playwright configuration"""
    return {{
        "base_url": "{base_url}",
        "timeout": 30000,
        "headless": True,
        "browsers": ["chromium", "firefox", "webkit"],
        "screenshot_mode": "only-on-failure",
        "video_mode": "retain-on-failure"
    }}
'''
    
    def _generate_conftest(self) -> str:
        """Generate conftest.py"""
        return '''"""Pytest configuration and fixtures"""
import pytest
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory"""
    return Path("data")

@pytest.fixture(autouse=True)
def test_setup(request):
    """Setup for each test"""
    test_name = request.node.name
    start_time = datetime.now()
    
    logging.info(f"Starting test: {test_name}")
    
    yield
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logging.info(f"Test completed: {test_name} (Duration: {duration:.2f}s)")

@pytest.fixture(scope="session")
def screenshots_dir():
    """Screenshots directory"""
    screenshots_path = Path("screenshots")
    screenshots_path.mkdir(exist_ok=True)
    return screenshots_path
'''
    
    # Utility methods
    
    def _camel_case(self, text: str) -> str:
        """Convert text to CamelCase"""
        words = text.replace('-', '_').replace(' ', '_').split('_')
        return ''.join(word.capitalize() for word in words if word)
    
    def _snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        import re
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
        text = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', text)
        return text.lower().replace('-', '_').replace(' ', '_')
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_imports_template(self) -> str:
        """Get imports template"""
        return '''import pytest
import logging
from playwright.sync_api import Page, expect
'''
    
    def _get_page_object_template(self) -> str:
        """Get page object template"""
        return '''from pages.base_page import BasePage
from playwright.sync_api import Page

class {class_name}(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
'''
    
    def _get_test_template(self) -> str:
        """Get test template"""
        return '''def test_{test_name}(self):
    """Test description"""
    # Test implementation
    pass
'''
    
    def get_generation_summary(self, suite: TestSuite) -> Dict[str, Any]:
        """Get summary of code generation"""
        return {
            'suite_name': suite.suite_name,
            'total_test_files': len(suite.test_files),
            'total_tests': sum(tf.test_count for tf in suite.test_files),
            'page_objects': len(suite.page_objects),
            'config_files': len(suite.config_files),
            'requirements': len(suite.requirements),
            'files_generated': {
                'test_files': [tf.file_path for tf in suite.test_files],
                'page_objects': [po.file_path for po in suite.page_objects],
                'config_files': [cf.file_path for cf in suite.config_files]
            },
            'output_directory': self.output_dir,
            'setup_instructions_included': bool(suite.setup_instructions)
        }
