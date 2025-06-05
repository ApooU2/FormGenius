"""
Test Strategist Agent for FormGenius.
Responsible for analyzing web application structure and generating comprehensive test strategies.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TestPriority(Enum):
    """Test priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCategory(Enum):
    """Test category types."""
    FUNCTIONAL = "functional"
    UI = "ui"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SECURITY = "security"
    INTEGRATION = "integration"
    REGRESSION = "regression"
    CROSS_BROWSER = "cross_browser"


class TestStrategist:
    """Agent for generating comprehensive test strategies and scenarios."""
    
    def __init__(self):
        """Initialize the test strategist."""
        self.test_patterns = self._load_test_patterns()
        self.risk_factors = self._load_risk_factors()
    
    def generate_test_strategy(self, website_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive test strategy based on website analysis.
        
        Args:
            website_analysis: List of analyzed pages from web explorer
            
        Returns:
            Comprehensive test strategy
        """
        strategy = {
            'overview': self._create_strategy_overview(website_analysis),
            'test_categories': self._identify_test_categories(website_analysis),
            'priority_matrix': self._create_priority_matrix(website_analysis),
            'test_scenarios': self._generate_test_scenarios(website_analysis),
            'coverage_areas': self._identify_coverage_areas(website_analysis),
            'risk_assessment': self._assess_risks(website_analysis),
            'recommendations': self._generate_recommendations(website_analysis)
        }
        
        return strategy
    
    def prioritize_test_scenarios(self, test_scenarios: List[Dict[str, Any]], 
                                 website_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize test scenarios based on risk, impact, and business value.
        
        Args:
            test_scenarios: List of test scenarios
            website_analysis: Website analysis data
            
        Returns:
            Prioritized test scenarios
        """
        prioritized_scenarios = []
        
        for scenario in test_scenarios:
            priority_score = self._calculate_priority_score(scenario, website_analysis)
            scenario['priority_score'] = priority_score
            scenario['priority_level'] = self._determine_priority_level(priority_score)
            prioritized_scenarios.append(scenario)
        
        # Sort by priority score (highest first)
        prioritized_scenarios.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized_scenarios
    
    def generate_test_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate specific test scenarios for a single page.
        
        Args:
            page_analysis: Analysis of a single page
            
        Returns:
            List of test scenarios for the page
        """
        scenarios = []
        
        # Generate scenarios based on page type
        page_type = page_analysis.get('page_type', 'content')
        scenarios.extend(self._generate_page_type_scenarios(page_type, page_analysis))
        
        # Generate scenarios for interactive elements
        scenarios.extend(self._generate_interactive_scenarios(page_analysis))
        
        # Generate scenarios for forms
        scenarios.extend(self._generate_form_scenarios(page_analysis))
        
        # Generate scenarios for navigation
        scenarios.extend(self._generate_navigation_scenarios(page_analysis))
        
        # Generate accessibility scenarios
        scenarios.extend(self._generate_accessibility_scenarios(page_analysis))
        
        # Generate performance scenarios
        scenarios.extend(self._generate_performance_scenarios(page_analysis))
        
        # Generate security scenarios
        scenarios.extend(self._generate_security_scenarios(page_analysis))
        
        return scenarios
    
    def generate_comprehensive_scenarios(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate comprehensive test scenarios based on website analysis.
        
        Args:
            analysis: Website analysis results
            
        Returns:
            List of detailed test scenarios
        """
        try:
            scenarios = []
            
            # Basic page load scenarios
            scenarios.extend(self._create_basic_scenarios(analysis))
            
            # Form-specific scenarios
            if analysis.get("forms"):
                scenarios.extend(self._create_form_scenarios(analysis["forms"]))
            
            # Navigation scenarios
            if analysis.get("navigation_elements"):
                scenarios.extend(self._create_navigation_scenarios(analysis["navigation_elements"]))
            
            # Interactive element scenarios
            if analysis.get("interactive_elements"):
                scenarios.extend(self._create_interaction_scenarios(analysis["interactive_elements"]))
            
            logger.info(f"Generated {len(scenarios)} comprehensive test scenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"Error generating comprehensive scenarios: {e}")
            raise

    def _create_basic_scenarios(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create basic page load and accessibility scenarios."""
        return [
            {
                "name": "page_load_test",
                "description": "Verify page loads successfully",
                "type": "functional",
                "priority": "high",
                "steps": [
                    {"action": "navigate", "data": analysis.get("url", "")},
                    {"action": "wait", "selector": "body"},
                    {"action": "verify", "selector": "title"},
                    {"action": "verify", "selector": "body"}
                ],
                "expected_result": "Page loads without errors and displays content",
                "category": "smoke"
            },
            {
                "name": "responsive_design_test",
                "description": "Test responsive design across different viewports",
                "type": "visual",
                "priority": "medium",
                "steps": [
                    {"action": "navigate", "data": analysis.get("url", "")},
                    {"action": "verify", "selector": "body"},
                ],
                "expected_result": "Page displays correctly on different screen sizes",
                "category": "ui"
            }
        ]

    def _create_form_scenarios(self, forms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create form-specific test scenarios."""
        scenarios = []
        
        for form in forms:
            form_id = form.get("id", "unknown_form")
            scenarios.extend([
                {
                    "name": f"form_{form_id}_valid_submission",
                    "description": f"Test valid form submission for {form_id}",
                    "type": "functional",
                    "priority": "high",
                    "steps": [
                        {"action": "navigate", "data": ""},
                        {"action": "fill", "selector": "input[name='email']", "data": "test@example.com"},
                        {"action": "fill", "selector": "input[name='password']", "data": "password123"},
                        {"action": "click", "selector": "button[type='submit']"},
                        {"action": "verify", "selector": ".success-message"}
                    ],
                    "expected_result": "Form submits successfully with valid data",
                    "category": "functional"
                },
                {
                    "name": f"form_{form_id}_validation",
                    "description": f"Test form validation for {form_id}",
                    "type": "validation",
                    "priority": "high",
                    "steps": [
                        {"action": "navigate", "data": ""},
                        {"action": "click", "selector": "button[type='submit']"},
                        {"action": "verify", "selector": ".error-message"}
                    ],
                    "expected_result": "Form displays validation errors for empty required fields",
                    "category": "validation"
                }
            ])
        
        return scenarios

    def _create_navigation_scenarios(self, nav_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create navigation test scenarios."""
        return [
            {
                "name": "navigation_menu_test",
                "description": "Test all navigation menu items",
                "type": "functional",
                "priority": "medium",
                "steps": [
                    {"action": "navigate", "data": ""},
                    {"action": "click", "selector": "nav a:first-child"},
                    {"action": "verify", "selector": "body"},
                    {"action": "keyboard", "key": "ArrowDown"}
                ],
                "expected_result": "Navigation works correctly and pages load",
                "category": "navigation"
            }
        ]

    def _create_interaction_scenarios(self, interactive_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create interactive element test scenarios."""
        return [
            {
                "name": "interactive_elements_test",
                "description": "Test interactive UI elements",
                "type": "functional",
                "priority": "medium",
                "steps": [
                    {"action": "navigate", "data": ""},
                    {"action": "click", "selector": "button:first"},
                    {"action": "verify", "selector": "body"}
                ],
                "expected_result": "Interactive elements respond correctly to user actions",
                "category": "interaction"
            }
        ]
    
    def _create_strategy_overview(self, website_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create high-level strategy overview."""
        total_pages = len(website_analysis)
        page_types = {}
        total_forms = 0
        total_interactive_elements = 0
        
        for page in website_analysis:
            if 'error' in page:
                continue
                
            page_type = page.get('page_type', 'unknown')
            page_types[page_type] = page_types.get(page_type, 0) + 1
            
            forms = page.get('forms', [])
            total_forms += len(forms)
            
            interactive_elements = page.get('interactive_elements', [])
            total_interactive_elements += len(interactive_elements)
        
        return {
            'total_pages_analyzed': total_pages,
            'page_type_distribution': page_types,
            'total_forms': total_forms,
            'total_interactive_elements': total_interactive_elements,
            'complexity_score': self._calculate_complexity_score(website_analysis),
            'recommended_test_duration': self._estimate_test_duration(website_analysis)
        }
    
    def _identify_test_categories(self, website_analysis: List[Dict[str, Any]]) -> List[str]:
        """Identify relevant test categories based on website analysis."""
        categories = set()
        
        for page in website_analysis:
            if 'error' in page:
                continue
            
            # Always include basic categories
            categories.update([
                TestCategory.FUNCTIONAL.value,
                TestCategory.UI.value,
                TestCategory.CROSS_BROWSER.value
            ])
            
            # Add accessibility if semantic HTML is present
            if page.get('accessibility', {}).get('has_semantic_structure'):
                categories.add(TestCategory.ACCESSIBILITY.value)
            
            # Add performance for all pages
            categories.add(TestCategory.PERFORMANCE.value)
            
            # Add security if forms are present
            if page.get('forms'):
                categories.add(TestCategory.SECURITY.value)
            
            # Add integration if multiple pages exist
            if len(website_analysis) > 1:
                categories.add(TestCategory.INTEGRATION.value)
        
        return list(categories)
    
    def _create_priority_matrix(self, website_analysis: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Create priority matrix for different test types."""
        priority_matrix = {
            TestPriority.CRITICAL.value: [],
            TestPriority.HIGH.value: [],
            TestPriority.MEDIUM.value: [],
            TestPriority.LOW.value: []
        }
        
        # Critical: Form validation, security, core functionality
        priority_matrix[TestPriority.CRITICAL.value].extend([
            'form_submission_testing',
            'authentication_testing',
            'data_validation_testing',
            'core_functionality_testing'
        ])
        
        # High: Navigation, user workflows, error handling
        priority_matrix[TestPriority.HIGH.value].extend([
            'navigation_testing',
            'user_workflow_testing',
            'error_handling_testing',
            'responsive_design_testing'
        ])
        
        # Medium: UI consistency, accessibility, performance
        priority_matrix[TestPriority.MEDIUM.value].extend([
            'ui_consistency_testing',
            'accessibility_testing',
            'performance_testing',
            'browser_compatibility_testing'
        ])
        
        # Low: Visual regression, edge cases
        priority_matrix[TestPriority.LOW.value].extend([
            'visual_regression_testing',
            'edge_case_testing',
            'localization_testing'
        ])
        
        return priority_matrix
    
    def _generate_test_scenarios(self, website_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate test scenarios for all analyzed pages."""
        all_scenarios = []
        
        for page in website_analysis:
            if 'error' in page:
                continue
            
            page_scenarios = self.generate_test_scenarios(page)
            all_scenarios.extend(page_scenarios)
        
        # Remove duplicates and merge similar scenarios
        return self._deduplicate_scenarios(all_scenarios)
    
    def _generate_page_type_scenarios(self, page_type: str, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate scenarios based on page type."""
        scenarios = []
        url = page_analysis.get('url', '')
        
        if page_type == 'login':
            scenarios.extend([
                {
                    'name': 'Valid Login Test',
                    'description': 'Test login with valid credentials',
                    'category': TestCategory.FUNCTIONAL.value,
                    'priority': TestPriority.CRITICAL.value,
                    'page_url': url,
                    'steps': [
                        'Navigate to login page',
                        'Enter valid username',
                        'Enter valid password',
                        'Click login button',
                        'Verify successful login'
                    ],
                    'expected_result': 'User is logged in and redirected to dashboard',
                    'test_data': {'username': 'valid_user', 'password': 'valid_password'}
                },
                {
                    'name': 'Invalid Login Test',
                    'description': 'Test login with invalid credentials',
                    'category': TestCategory.FUNCTIONAL.value,
                    'priority': TestPriority.HIGH.value,
                    'page_url': url,
                    'steps': [
                        'Navigate to login page',
                        'Enter invalid username',
                        'Enter invalid password',
                        'Click login button',
                        'Verify error message'
                    ],
                    'expected_result': 'Error message is displayed',
                    'test_data': {'username': 'invalid_user', 'password': 'invalid_password'}
                }
            ])
        
        elif page_type == 'registration':
            scenarios.extend([
                {
                    'name': 'Valid Registration Test',
                    'description': 'Test registration with valid data',
                    'category': TestCategory.FUNCTIONAL.value,
                    'priority': TestPriority.CRITICAL.value,
                    'page_url': url,
                    'steps': [
                        'Navigate to registration page',
                        'Fill all required fields with valid data',
                        'Submit form',
                        'Verify successful registration'
                    ],
                    'expected_result': 'User is registered successfully'
                }
            ])
        
        elif page_type == 'form':
            scenarios.extend([
                {
                    'name': 'Form Submission Test',
                    'description': 'Test form submission with valid data',
                    'category': TestCategory.FUNCTIONAL.value,
                    'priority': TestPriority.HIGH.value,
                    'page_url': url,
                    'steps': [
                        'Navigate to form page',
                        'Fill form with valid data',
                        'Submit form',
                        'Verify submission success'
                    ],
                    'expected_result': 'Form is submitted successfully'
                }
            ])
        
        return scenarios
    
    def _generate_interactive_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate scenarios for interactive elements."""
        scenarios = []
        interactive_elements = page_analysis.get('interactive_elements', [])
        url = page_analysis.get('url', '')
        
        # Count different types of interactive elements
        buttons = [el for el in interactive_elements if el.get('tag') == 'button']
        links = [el for el in interactive_elements if el.get('tag') == 'a']
        inputs = [el for el in interactive_elements if el.get('type') == 'input']
        
        if buttons:
            scenarios.append({
                'name': 'Button Interaction Test',
                'description': f'Test all {len(buttons)} buttons on the page',
                'category': TestCategory.FUNCTIONAL.value,
                'priority': TestPriority.HIGH.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Identify all clickable buttons',
                    'Click each button and verify response',
                    'Check for proper visual feedback'
                ],
                'expected_result': 'All buttons respond appropriately when clicked',
                'element_count': len(buttons)
            })
        
        if links:
            scenarios.append({
                'name': 'Link Navigation Test',
                'description': f'Test navigation through {len(links)} links',
                'category': TestCategory.FUNCTIONAL.value,
                'priority': TestPriority.MEDIUM.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Identify all navigation links',
                    'Click each link and verify destination',
                    'Verify back navigation works'
                ],
                'expected_result': 'All links navigate to correct destinations',
                'element_count': len(links)
            })
        
        if inputs:
            scenarios.append({
                'name': 'Input Field Test',
                'description': f'Test all {len(inputs)} input fields',
                'category': TestCategory.FUNCTIONAL.value,
                'priority': TestPriority.HIGH.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Test each input field with valid data',
                    'Test each input field with invalid data',
                    'Verify validation messages'
                ],
                'expected_result': 'All input fields accept valid data and reject invalid data',
                'element_count': len(inputs)
            })
        
        return scenarios
    
    def _generate_form_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate scenarios for forms."""
        scenarios = []
        forms = page_analysis.get('forms', [])
        url = page_analysis.get('url', '')
        
        for i, form in enumerate(forms):
            form_name = f"Form {i + 1}"
            field_count = len(form.get('fields', []))
            required_fields = [field for field in form.get('fields', []) if field.get('required')]
            
            scenarios.extend([
                {
                    'name': f'{form_name} - Valid Data Submission',
                    'description': f'Test {form_name} with valid data in all {field_count} fields',
                    'category': TestCategory.FUNCTIONAL.value,
                    'priority': TestPriority.CRITICAL.value,
                    'page_url': url,
                    'form_index': i,
                    'steps': [
                        'Navigate to page',
                        f'Fill all {field_count} form fields with valid data',
                        'Submit form',
                        'Verify successful submission'
                    ],
                    'expected_result': 'Form submits successfully with valid data'
                },
                {
                    'name': f'{form_name} - Required Field Validation',
                    'description': f'Test required field validation for {len(required_fields)} required fields',
                    'category': TestCategory.FUNCTIONAL.value,
                    'priority': TestPriority.HIGH.value,
                    'page_url': url,
                    'form_index': i,
                    'steps': [
                        'Navigate to page',
                        'Leave required fields empty',
                        'Attempt to submit form',
                        'Verify validation messages appear'
                    ],
                    'expected_result': 'Validation messages appear for required fields'
                }
            ])
            
            if form.get('method', '').upper() == 'POST':
                scenarios.append({
                    'name': f'{form_name} - Security Testing',
                    'description': f'Test {form_name} for security vulnerabilities',
                    'category': TestCategory.SECURITY.value,
                    'priority': TestPriority.HIGH.value,
                    'page_url': url,
                    'form_index': i,
                    'steps': [
                        'Navigate to page',
                        'Test for XSS vulnerabilities',
                        'Test for SQL injection',
                        'Test CSRF protection',
                        'Verify input sanitization'
                    ],
                    'expected_result': 'Form is protected against common security vulnerabilities'
                })
        
        return scenarios
    
    def _generate_navigation_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate scenarios for navigation."""
        scenarios = []
        navigation = page_analysis.get('navigation', {})
        url = page_analysis.get('url', '')
        
        if navigation.get('has_main_navigation'):
            scenarios.append({
                'name': 'Main Navigation Test',
                'description': 'Test main navigation functionality',
                'category': TestCategory.FUNCTIONAL.value,
                'priority': TestPriority.HIGH.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Identify main navigation menu',
                    'Test each navigation item',
                    'Verify proper page loading'
                ],
                'expected_result': 'All navigation items work correctly'
            })
        
        if navigation.get('breadcrumbs'):
            scenarios.append({
                'name': 'Breadcrumb Navigation Test',
                'description': 'Test breadcrumb navigation',
                'category': TestCategory.UI.value,
                'priority': TestPriority.MEDIUM.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Verify breadcrumb visibility',
                    'Test breadcrumb links',
                    'Verify current page indication'
                ],
                'expected_result': 'Breadcrumbs show correct navigation path'
            })
        
        return scenarios
    
    def _generate_accessibility_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate accessibility test scenarios."""
        scenarios = []
        accessibility = page_analysis.get('accessibility', {})
        url = page_analysis.get('url', '')
        
        scenarios.extend([
            {
                'name': 'Keyboard Navigation Test',
                'description': 'Test keyboard-only navigation',
                'category': TestCategory.ACCESSIBILITY.value,
                'priority': TestPriority.HIGH.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Use only Tab key to navigate',
                    'Verify all interactive elements are reachable',
                    'Test Enter and Space key interactions'
                ],
                'expected_result': 'All interactive elements are keyboard accessible'
            },
            {
                'name': 'Screen Reader Compatibility Test',
                'description': 'Test screen reader compatibility',
                'category': TestCategory.ACCESSIBILITY.value,
                'priority': TestPriority.MEDIUM.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Check for proper heading structure',
                    'Verify ARIA labels and roles',
                    'Test with screen reader'
                ],
                'expected_result': 'Page is compatible with screen readers'
            }
        ])
        
        if accessibility.get('images_count', 0) > 0:
            scenarios.append({
                'name': 'Image Alt Text Test',
                'description': 'Verify all images have appropriate alt text',
                'category': TestCategory.ACCESSIBILITY.value,
                'priority': TestPriority.MEDIUM.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Identify all images',
                    'Verify alt text presence',
                    'Check alt text quality'
                ],
                'expected_result': 'All images have meaningful alt text'
            })
        
        return scenarios
    
    def _generate_performance_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance test scenarios."""
        scenarios = []
        url = page_analysis.get('url', '')
        
        scenarios.extend([
            {
                'name': 'Page Load Performance Test',
                'description': 'Test page loading performance',
                'category': TestCategory.PERFORMANCE.value,
                'priority': TestPriority.MEDIUM.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Measure page load time',
                    'Check for performance bottlenecks',
                    'Verify acceptable load times'
                ],
                'expected_result': 'Page loads within acceptable time limits'
            },
            {
                'name': 'Responsive Design Test',
                'description': 'Test responsive design across different screen sizes',
                'category': TestCategory.UI.value,
                'priority': TestPriority.HIGH.value,
                'page_url': url,
                'steps': [
                    'Navigate to page',
                    'Test on mobile viewport',
                    'Test on tablet viewport',
                    'Test on desktop viewport',
                    'Verify layout adapts properly'
                ],
                'expected_result': 'Page layout adapts correctly to different screen sizes'
            }
        ])
        
        return scenarios
    
    def _generate_security_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security test scenarios."""
        scenarios = []
        url = page_analysis.get('url', '')
        forms = page_analysis.get('forms', [])
        
        if forms:
            scenarios.extend([
                {
                    'name': 'XSS Protection Test',
                    'description': 'Test protection against Cross-Site Scripting',
                    'category': TestCategory.SECURITY.value,
                    'priority': TestPriority.HIGH.value,
                    'page_url': url,
                    'steps': [
                        'Navigate to page',
                        'Attempt XSS injection in form fields',
                        'Submit form',
                        'Verify script is not executed'
                    ],
                    'expected_result': 'XSS attempts are blocked or sanitized'
                },
                {
                    'name': 'Input Validation Test',
                    'description': 'Test server-side input validation',
                    'category': TestCategory.SECURITY.value,
                    'priority': TestPriority.HIGH.value,
                    'page_url': url,
                    'steps': [
                        'Navigate to page',
                        'Submit malicious input data',
                        'Verify proper validation',
                        'Check error handling'
                    ],
                    'expected_result': 'Invalid input is rejected with proper error messages'
                }
            ])
        
        return scenarios
    
    def _calculate_priority_score(self, scenario: Dict[str, Any], website_analysis: List[Dict[str, Any]]) -> float:
        """Calculate priority score for a test scenario."""
        base_score = 0.0
        
        # Category weights
        category_weights = {
            TestCategory.FUNCTIONAL.value: 1.0,
            TestCategory.SECURITY.value: 0.9,
            TestCategory.ACCESSIBILITY.value: 0.7,
            TestCategory.UI.value: 0.6,
            TestCategory.PERFORMANCE.value: 0.5,
            TestCategory.INTEGRATION.value: 0.4,
            TestCategory.CROSS_BROWSER.value: 0.3
        }
        
        category = scenario.get('category', TestCategory.FUNCTIONAL.value)
        base_score += category_weights.get(category, 0.5)
        
        # Form-related scenarios get higher priority
        if 'form' in scenario.get('name', '').lower():
            base_score += 0.3
        
        # Login/authentication scenarios get highest priority
        if 'login' in scenario.get('name', '').lower() or 'auth' in scenario.get('name', '').lower():
            base_score += 0.5
        
        # Security scenarios get higher priority
        if scenario.get('category') == TestCategory.SECURITY.value:
            base_score += 0.4
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def _determine_priority_level(self, priority_score: float) -> str:
        """Determine priority level based on score."""
        if priority_score >= 0.8:
            return TestPriority.CRITICAL.value
        elif priority_score >= 0.6:
            return TestPriority.HIGH.value
        elif priority_score >= 0.4:
            return TestPriority.MEDIUM.value
        else:
            return TestPriority.LOW.value
    
    def _deduplicate_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate scenarios and merge similar ones."""
        unique_scenarios = []
        seen_names = set()
        
        for scenario in scenarios:
            name = scenario.get('name', '')
            if name not in seen_names:
                unique_scenarios.append(scenario)
                seen_names.add(name)
        
        return unique_scenarios
    
    def _identify_coverage_areas(self, website_analysis: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify test coverage areas."""
        coverage_areas = {
            'functional': [],
            'ui': [],
            'accessibility': [],
            'performance': [],
            'security': [],
            'integration': []
        }
        
        for page in website_analysis:
            if 'error' in page:
                continue
            
            page_type = page.get('page_type', 'content')
            url = page.get('url', '')
            
            # Functional coverage
            if page.get('forms') or page.get('interactive_elements'):
                coverage_areas['functional'].append(f"Interactive elements on {url}")
            
            # UI coverage
            coverage_areas['ui'].append(f"User interface of {url}")
            
            # Accessibility coverage
            if page.get('accessibility', {}).get('has_semantic_structure'):
                coverage_areas['accessibility'].append(f"Accessibility features on {url}")
            
            # Performance coverage
            coverage_areas['performance'].append(f"Performance metrics for {url}")
            
            # Security coverage
            if page.get('forms'):
                coverage_areas['security'].append(f"Form security on {url}")
        
        # Integration coverage
        if len(website_analysis) > 1:
            coverage_areas['integration'].append("Cross-page navigation and workflows")
        
        return coverage_areas
    
    def _assess_risks(self, website_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess testing risks based on website complexity."""
        risks = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        total_forms = sum(len(page.get('forms', [])) for page in website_analysis if 'error' not in page)
        total_interactive = sum(len(page.get('interactive_elements', [])) for page in website_analysis if 'error' not in page)
        
        # High risks
        if total_forms > 5:
            risks['high'].append("High number of forms increases validation complexity")
        
        if any(page.get('page_type') == 'login' for page in website_analysis):
            risks['high'].append("Authentication functionality requires thorough security testing")
        
        # Medium risks
        if total_interactive > 20:
            risks['medium'].append("Large number of interactive elements increases test coverage requirements")
        
        if len(website_analysis) > 10:
            risks['medium'].append("Multiple pages require comprehensive integration testing")
        
        # Low risks
        if any(page.get('accessibility', {}).get('images_alt_ratio', 1) < 0.8 for page in website_analysis):
            risks['low'].append("Some images missing alt text may affect accessibility compliance")
        
        return risks
    
    def _generate_recommendations(self, website_analysis: List[Dict[str, Any]]) -> List[str]:
        """Generate testing recommendations."""
        recommendations = []
        
        total_forms = sum(len(page.get('forms', [])) for page in website_analysis if 'error' not in page)
        has_login = any(page.get('page_type') == 'login' for page in website_analysis)
        
        # Always recommend basic testing
        recommendations.extend([
            "Implement automated regression testing for critical user paths",
            "Set up continuous integration with automated test execution",
            "Include cross-browser testing for major browsers (Chrome, Firefox, Safari, Edge)"
        ])
        
        # Form-specific recommendations
        if total_forms > 0:
            recommendations.extend([
                "Implement comprehensive form validation testing",
                "Test form security against XSS and injection attacks",
                "Verify proper error handling and user feedback"
            ])
        
        # Authentication recommendations
        if has_login:
            recommendations.extend([
                "Implement security testing for authentication flows",
                "Test session management and timeout handling",
                "Verify password policies and account lockout mechanisms"
            ])
        
        # Accessibility recommendations
        if any(page.get('accessibility', {}).get('has_semantic_structure') for page in website_analysis):
            recommendations.append("Include accessibility testing with automated tools and manual verification")
        
        # Performance recommendations
        recommendations.extend([
            "Set up performance monitoring and testing",
            "Test application under various load conditions",
            "Monitor and test page load times regularly"
        ])
        
        return recommendations
    
    def _calculate_complexity_score(self, website_analysis: List[Dict[str, Any]]) -> float:
        """Calculate overall complexity score for the website."""
        if not website_analysis:
            return 0.0
        
        complexity_factors = {
            'page_count': len(website_analysis),
            'total_forms': sum(len(page.get('forms', [])) for page in website_analysis if 'error' not in page),
            'total_interactive': sum(len(page.get('interactive_elements', [])) for page in website_analysis if 'error' not in page),
            'unique_page_types': len(set(page.get('page_type') for page in website_analysis if 'error' not in page))
        }
        
        # Normalize and weight factors
        normalized_score = (
            min(complexity_factors['page_count'] / 10.0, 1.0) * 0.3 +
            min(complexity_factors['total_forms'] / 20.0, 1.0) * 0.4 +
            min(complexity_factors['total_interactive'] / 50.0, 1.0) * 0.2 +
            min(complexity_factors['unique_page_types'] / 5.0, 1.0) * 0.1
        )
        
        return round(normalized_score, 2)
    
    def _estimate_test_duration(self, website_analysis: List[Dict[str, Any]]) -> Dict[str, str]:
        """Estimate test execution duration."""
        complexity_score = self._calculate_complexity_score(website_analysis)
        
        if complexity_score < 0.3:
            return {
                'automated_tests': '30 minutes',
                'manual_testing': '2 hours',
                'total_estimate': '2.5 hours'
            }
        elif complexity_score < 0.6:
            return {
                'automated_tests': '1 hour',
                'manual_testing': '4 hours',
                'total_estimate': '5 hours'
            }
        else:
            return {
                'automated_tests': '2 hours',
                'manual_testing': '8 hours',
                'total_estimate': '10 hours'
            }
    
    def _load_test_patterns(self) -> Dict[str, Any]:
        """Load common test patterns and templates."""
        return {
            'form_patterns': {
                'validation': ['required_fields', 'format_validation', 'length_validation'],
                'security': ['xss_protection', 'sql_injection', 'csrf_protection'],
                'usability': ['error_messages', 'field_labeling', 'submit_feedback']
            },
            'navigation_patterns': {
                'menu_testing': ['main_navigation', 'breadcrumbs', 'footer_links'],
                'page_transitions': ['loading_states', 'error_pages', 'redirects']
            },
            'interaction_patterns': {
                'click_events': ['buttons', 'links', 'interactive_elements'],
                'input_events': ['text_input', 'selection', 'file_upload']
            }
        }
    
    def _load_risk_factors(self) -> Dict[str, List[str]]:
        """Load risk factors for different application types."""
        return {
            'high_risk_elements': [
                'authentication_forms',
                'payment_processing',
                'file_uploads',
                'data_export',
                'user_management'
            ],
            'medium_risk_elements': [
                'search_functionality',
                'content_management',
                'notifications',
                'user_preferences'
            ],
            'low_risk_elements': [
                'static_content',
                'basic_navigation',
                'read_only_data'
            ]
        }
