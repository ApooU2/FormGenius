"""
Scenario Generator for FormGenius

This module generates comprehensive test scenarios based on analysis results:
- Form testing scenarios
- User journey scenarios
- Edge case scenarios
- Accessibility testing scenarios
- Performance testing scenarios
"""

import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import uuid
import json

logger = logging.getLogger(__name__)

@dataclass
class TestScenario:
    """Represents a test scenario"""
    scenario_id: str
    name: str
    description: str
    category: str  # 'functional', 'validation', 'accessibility', 'performance', 'security'
    priority: str  # 'critical', 'high', 'medium', 'low'
    test_type: str  # 'positive', 'negative', 'boundary', 'edge_case'
    steps: List[Dict[str, Any]] = field(default_factory=list)
    expected_result: str = ""
    preconditions: List[str] = field(default_factory=list)
    test_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    estimated_duration: int = 60  # seconds
    complexity: str = "medium"  # 'simple', 'medium', 'complex'
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ScenarioSet:
    """Collection of related test scenarios"""
    set_id: str
    name: str
    description: str
    scenarios: List[TestScenario] = field(default_factory=list)
    coverage_areas: List[str] = field(default_factory=list)
    total_scenarios: int = 0
    estimated_duration: int = 0

class ScenarioGenerator:
    """Generates comprehensive test scenarios from analysis results"""
    
    def __init__(self):
        self.scenario_templates = self._load_scenario_templates()
        self.test_data_generators = self._setup_test_data_generators()
    
    def generate_scenarios(self, 
                         dom_analysis: Dict[str, Any],
                         flow_analysis: Dict[str, Any],
                         element_analysis: Dict[str, Any]) -> List[ScenarioSet]:
        """Generate comprehensive test scenarios"""
        try:
            logger.info("Starting scenario generation")
            
            scenario_sets = []
            
            # Generate form testing scenarios
            if element_analysis.get('form_elements'):
                form_scenarios = self._generate_form_scenarios(element_analysis)
                scenario_sets.append(form_scenarios)
            
            # Generate navigation scenarios
            if flow_analysis.get('navigation_patterns'):
                nav_scenarios = self._generate_navigation_scenarios(flow_analysis)
                scenario_sets.append(nav_scenarios)
            
            # Generate user journey scenarios
            if flow_analysis.get('discovered_flows'):
                journey_scenarios = self._generate_user_journey_scenarios(flow_analysis)
                scenario_sets.append(journey_scenarios)
            
            # Generate validation scenarios
            validation_scenarios = self._generate_validation_scenarios(element_analysis)
            scenario_sets.append(validation_scenarios)
            
            # Generate accessibility scenarios
            accessibility_scenarios = self._generate_accessibility_scenarios(dom_analysis)
            scenario_sets.append(accessibility_scenarios)
            
            # Generate security scenarios
            security_scenarios = self._generate_security_scenarios(element_analysis)
            scenario_sets.append(security_scenarios)
            
            # Generate performance scenarios
            performance_scenarios = self._generate_performance_scenarios(dom_analysis)
            scenario_sets.append(performance_scenarios)
            
            logger.info(f"Generated {len(scenario_sets)} scenario sets")
            return scenario_sets
            
        except Exception as e:
            logger.error(f"Scenario generation failed: {str(e)}")
            raise
    
    def _generate_form_scenarios(self, element_analysis: Dict[str, Any]) -> ScenarioSet:
        """Generate form-specific test scenarios"""
        scenarios = []
        form_elements = element_analysis.get('form_elements', [])
        
        for form_group in element_analysis.get('element_groups', []):
            if form_group.group_type == 'form':
                # Happy path scenario
                scenarios.append(self._create_form_happy_path_scenario(form_group))
                
                # Validation scenarios
                scenarios.extend(self._create_form_validation_scenarios(form_group))
                
                # Boundary testing scenarios
                scenarios.extend(self._create_form_boundary_scenarios(form_group))
                
                # Error handling scenarios
                scenarios.extend(self._create_form_error_scenarios(form_group))
        
        return ScenarioSet(
            set_id=str(uuid.uuid4()),
            name="Form Testing Scenarios",
            description="Comprehensive form testing including validation, submission, and error handling",
            scenarios=scenarios,
            coverage_areas=['form_validation', 'form_submission', 'error_handling', 'data_entry'],
            total_scenarios=len(scenarios),
            estimated_duration=sum(s.estimated_duration for s in scenarios)
        )
    
    def _generate_navigation_scenarios(self, flow_analysis: Dict[str, Any]) -> ScenarioSet:
        """Generate navigation test scenarios"""
        scenarios = []
        nav_patterns = flow_analysis.get('navigation_patterns', {})
        
        # Main navigation scenarios
        if nav_patterns.get('mainNavigation'):
            scenarios.append(self._create_main_navigation_scenario(nav_patterns))
        
        # Breadcrumb navigation scenarios
        if nav_patterns.get('breadcrumbs'):
            scenarios.append(self._create_breadcrumb_scenario(nav_patterns))
        
        # Page transitions scenarios
        if flow_analysis.get('page_transitions'):
            scenarios.extend(self._create_page_transition_scenarios(flow_analysis))
        
        # Mobile navigation scenarios
        scenarios.append(self._create_mobile_navigation_scenario(nav_patterns))
        
        return ScenarioSet(
            set_id=str(uuid.uuid4()),
            name="Navigation Testing Scenarios",
            description="Testing navigation patterns, menu functionality, and page transitions",
            scenarios=scenarios,
            coverage_areas=['navigation', 'menu_functionality', 'page_transitions', 'mobile_navigation'],
            total_scenarios=len(scenarios),
            estimated_duration=sum(s.estimated_duration for s in scenarios)
        )
    
    def _generate_user_journey_scenarios(self, flow_analysis: Dict[str, Any]) -> ScenarioSet:
        """Generate user journey test scenarios"""
        scenarios = []
        discovered_flows = flow_analysis.get('discovered_flows', [])
        
        for flow in discovered_flows:
            if flow.priority in ['critical', 'high']:
                scenarios.append(self._create_user_journey_scenario(flow))
        
        # Multi-step workflow scenarios
        scenarios.extend(self._create_workflow_scenarios(discovered_flows))
        
        # User registration/login journey
        auth_flows = flow_analysis.get('authentication_flows', [])
        for auth_flow in auth_flows:
            scenarios.append(self._create_auth_journey_scenario(auth_flow))
        
        return ScenarioSet(
            set_id=str(uuid.uuid4()),
            name="User Journey Scenarios",
            description="End-to-end user journey testing covering critical workflows",
            scenarios=scenarios,
            coverage_areas=['user_workflows', 'authentication', 'multi_step_processes'],
            total_scenarios=len(scenarios),
            estimated_duration=sum(s.estimated_duration for s in scenarios)
        )
    
    def _generate_validation_scenarios(self, element_analysis: Dict[str, Any]) -> ScenarioSet:
        """Generate input validation test scenarios"""
        scenarios = []
        input_elements = element_analysis.get('input_elements', [])
        
        # Field validation scenarios
        for element in input_elements:
            scenarios.extend(self._create_input_validation_scenarios(element))
        
        # Cross-field validation scenarios
        scenarios.extend(self._create_cross_field_validation_scenarios(input_elements))
        
        # Data format validation scenarios
        scenarios.extend(self._create_format_validation_scenarios(input_elements))
        
        return ScenarioSet(
            set_id=str(uuid.uuid4()),
            name="Validation Testing Scenarios",
            description="Input validation, data format checking, and constraint testing",
            scenarios=scenarios,
            coverage_areas=['input_validation', 'data_format', 'constraints', 'sanitization'],
            total_scenarios=len(scenarios),
            estimated_duration=sum(s.estimated_duration for s in scenarios)
        )
    
    def _generate_accessibility_scenarios(self, dom_analysis: Dict[str, Any]) -> ScenarioSet:
        """Generate accessibility test scenarios"""
        scenarios = []
        
        # Keyboard navigation scenarios
        scenarios.append(self._create_keyboard_navigation_scenario())
        
        # Screen reader scenarios
        scenarios.append(self._create_screen_reader_scenario())
        
        # Color contrast scenarios
        scenarios.append(self._create_color_contrast_scenario())
        
        # Focus management scenarios
        scenarios.append(self._create_focus_management_scenario())
        
        # ARIA attributes scenarios
        scenarios.append(self._create_aria_attributes_scenario())
        
        return ScenarioSet(
            set_id=str(uuid.uuid4()),
            name="Accessibility Testing Scenarios",
            description="Comprehensive accessibility testing including WCAG compliance",
            scenarios=scenarios,
            coverage_areas=['keyboard_navigation', 'screen_reader', 'color_contrast', 'aria_compliance'],
            total_scenarios=len(scenarios),
            estimated_duration=sum(s.estimated_duration for s in scenarios)
        )
    
    def _generate_security_scenarios(self, element_analysis: Dict[str, Any]) -> ScenarioSet:
        """Generate security test scenarios"""
        scenarios = []
        
        # XSS protection scenarios
        scenarios.extend(self._create_xss_scenarios(element_analysis))
        
        # SQL injection scenarios
        scenarios.extend(self._create_sql_injection_scenarios(element_analysis))
        
        # CSRF protection scenarios
        scenarios.append(self._create_csrf_scenario())
        
        # Input sanitization scenarios
        scenarios.extend(self._create_sanitization_scenarios(element_analysis))
        
        return ScenarioSet(
            set_id=str(uuid.uuid4()),
            name="Security Testing Scenarios",
            description="Security vulnerability testing including XSS, injection, and CSRF",
            scenarios=scenarios,
            coverage_areas=['xss_protection', 'injection_prevention', 'csrf_protection', 'sanitization'],
            total_scenarios=len(scenarios),
            estimated_duration=sum(s.estimated_duration for s in scenarios)
        )
    
    def _generate_performance_scenarios(self, dom_analysis: Dict[str, Any]) -> ScenarioSet:
        """Generate performance test scenarios"""
        scenarios = []
        
        # Page load performance scenarios
        scenarios.append(self._create_page_load_scenario())
        
        # Form submission performance scenarios
        scenarios.append(self._create_form_performance_scenario())
        
        # Resource loading scenarios
        scenarios.append(self._create_resource_loading_scenario())
        
        # Mobile performance scenarios
        scenarios.append(self._create_mobile_performance_scenario())
        
        return ScenarioSet(
            set_id=str(uuid.uuid4()),
            name="Performance Testing Scenarios",
            description="Performance testing including load times, responsiveness, and resource usage",
            scenarios=scenarios,
            coverage_areas=['page_load', 'form_performance', 'resource_loading', 'mobile_performance'],
            total_scenarios=len(scenarios),
            estimated_duration=sum(s.estimated_duration for s in scenarios)
        )
    
    # Helper methods for creating specific scenarios
    
    def _create_form_happy_path_scenario(self, form_group) -> TestScenario:
        """Create a happy path form submission scenario"""
        steps = []
        step_num = 1
        
        for element in form_group.elements:
            if element.element_type == 'input':
                test_data = self._generate_test_data_for_field(element)
                steps.append({
                    'step': step_num,
                    'action': 'fill',
                    'selector': element.selector,
                    'data': test_data,
                    'description': f"Fill {element.context.get('label', element.element_id)} field"
                })
                step_num += 1
        
        # Add submit step
        submit_element = next((e for e in form_group.elements if e.element_type == 'button'), None)
        if submit_element:
            steps.append({
                'step': step_num,
                'action': 'click',
                'selector': submit_element.selector,
                'description': "Submit the form"
            })
        
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            name=f"Form Happy Path - {form_group.group_id}",
            description="Successfully fill and submit form with valid data",
            category="functional",
            priority="high",
            test_type="positive",
            steps=steps,
            expected_result="Form submitted successfully with confirmation",
            tags=["form", "happy_path", "submission"],
            estimated_duration=120,
            complexity="medium"
        )
    
    def _create_form_validation_scenarios(self, form_group) -> List[TestScenario]:
        """Create form validation scenarios"""
        scenarios = []
        
        for element in form_group.elements:
            if element.is_required and element.element_type == 'input':
                # Required field validation
                scenarios.append(TestScenario(
                    scenario_id=str(uuid.uuid4()),
                    name=f"Required Field Validation - {element.element_id}",
                    description=f"Verify {element.element_id} field shows validation error when empty",
                    category="validation",
                    priority="high",
                    test_type="negative",
                    steps=[
                        {
                            'step': 1,
                            'action': 'focus',
                            'selector': element.selector,
                            'description': f"Focus on {element.element_id} field"
                        },
                        {
                            'step': 2,
                            'action': 'blur',
                            'selector': element.selector,
                            'description': "Leave field empty and move focus away"
                        }
                    ],
                    expected_result="Validation error message displayed for required field",
                    tags=["validation", "required", "negative"],
                    estimated_duration=60,
                    complexity="simple"
                ))
        
        return scenarios
    
    def _create_input_validation_scenarios(self, element) -> List[TestScenario]:
        """Create input validation scenarios for a specific element"""
        scenarios = []
        input_type = element.context.get('inputType', 'text')
        
        if input_type == 'email':
            scenarios.append(TestScenario(
                scenario_id=str(uuid.uuid4()),
                name=f"Email Format Validation - {element.element_id}",
                description="Test email field with invalid email formats",
                category="validation",
                priority="medium",
                test_type="negative",
                steps=[
                    {
                        'step': 1,
                        'action': 'fill',
                        'selector': element.selector,
                        'data': 'invalid-email',
                        'description': "Enter invalid email format"
                    },
                    {
                        'step': 2,
                        'action': 'blur',
                        'selector': element.selector,
                        'description': "Move focus away from field"
                    }
                ],
                expected_result="Email format validation error displayed",
                test_data={'invalid_emails': ['invalid-email', '@domain.com', 'user@', 'user..name@domain.com']},
                tags=["validation", "email", "format"],
                estimated_duration=90
            ))
        
        return scenarios
    
    def _create_keyboard_navigation_scenario(self) -> TestScenario:
        """Create keyboard navigation scenario"""
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            name="Keyboard Navigation Test",
            description="Test navigation using only keyboard (Tab, Enter, Arrow keys)",
            category="accessibility",
            priority="high",
            test_type="positive",
            steps=[
                {
                    'step': 1,
                    'action': 'keyboard',
                    'key': 'Tab',
                    'description': "Navigate through all interactive elements using Tab key"
                },
                {
                    'step': 2,
                    'action': 'keyboard',
                    'key': 'Enter',
                    'description': "Activate focused elements using Enter key"
                },
                {
                    'step': 3,
                    'action': 'verify',
                    'description': "Verify all interactive elements are reachable and operable"
                }
            ],
            expected_result="All interactive elements accessible via keyboard with visible focus indicators",
            tags=["accessibility", "keyboard", "navigation"],
            estimated_duration=180,
            complexity="medium"
        )
    
    def _create_xss_scenarios(self, element_analysis: Dict[str, Any]) -> List[TestScenario]:
        """Create XSS protection scenarios"""
        scenarios = []
        input_elements = element_analysis.get('input_elements', [])
        
        xss_payloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>'
        ]
        
        for element in input_elements[:3]:  # Limit to first 3 inputs
            scenarios.append(TestScenario(
                scenario_id=str(uuid.uuid4()),
                name=f"XSS Protection Test - {element.element_id}",
                description=f"Test XSS protection for {element.element_id} input field",
                category="security",
                priority="high",
                test_type="negative",
                steps=[
                    {
                        'step': 1,
                        'action': 'fill',
                        'selector': element.selector,
                        'data': xss_payloads[0],
                        'description': "Input XSS payload into field"
                    },
                    {
                        'step': 2,
                        'action': 'submit',
                        'description': "Submit form with XSS payload"
                    },
                    {
                        'step': 3,
                        'action': 'verify',
                        'description': "Verify XSS payload is properly sanitized"
                    }
                ],
                expected_result="XSS payload properly escaped/sanitized, no script execution",
                test_data={'xss_payloads': xss_payloads},
                tags=["security", "xss", "injection"],
                estimated_duration=120
            ))
        
        return scenarios
    
    def _load_scenario_templates(self) -> Dict[str, Any]:
        """Load scenario templates for different test types"""
        return {
            'form_templates': {
                'happy_path': {
                    'category': 'functional',
                    'priority': 'high',
                    'test_type': 'positive'
                },
                'validation': {
                    'category': 'validation',
                    'priority': 'medium',
                    'test_type': 'negative'
                }
            },
            'accessibility_templates': {
                'keyboard': {
                    'category': 'accessibility',
                    'priority': 'high',
                    'test_type': 'positive'
                }
            },
            'security_templates': {
                'xss': {
                    'category': 'security',
                    'priority': 'high',
                    'test_type': 'negative'
                }
            }
        }
    
    def _setup_test_data_generators(self) -> Dict[str, Any]:
        """Setup test data generators for different field types"""
        return {
            'email': ['test@example.com', 'user.name+tag@domain.co.uk'],
            'password': ['SecurePass123!', 'TestPassword456@'],
            'name': ['John Doe', 'Jane Smith', 'Test User'],
            'phone': ['+1234567890', '(555) 123-4567'],
            'address': ['123 Main St, City, State 12345'],
            'url': ['https://example.com', 'https://test.website.org'],
            'number': ['123', '456.78', '0'],
            'date': ['2024-01-01', '2023-12-31'],
            'text': ['Test input', 'Sample text data']
        }
    
    def _generate_test_data_for_field(self, element) -> str:
        """Generate appropriate test data for a form field"""
        input_type = element.context.get('inputType', 'text')
        field_name = element.context.get('label', '').lower()
        
        # Check field name patterns
        if 'email' in field_name:
            return self.test_data_generators['email'][0]
        elif 'password' in field_name:
            return self.test_data_generators['password'][0]
        elif 'name' in field_name:
            return self.test_data_generators['name'][0]
        elif 'phone' in field_name:
            return self.test_data_generators['phone'][0]
        
        # Check input type
        if input_type in self.test_data_generators:
            return self.test_data_generators[input_type][0]
        
        return 'Test input'
    
    def get_scenario_summary(self, scenario_sets: List[ScenarioSet]) -> Dict[str, Any]:
        """Get summary of generated scenarios"""
        total_scenarios = sum(s.total_scenarios for s in scenario_sets)
        total_duration = sum(s.estimated_duration for s in scenario_sets)
        
        categories = {}
        priorities = {}
        
        for scenario_set in scenario_sets:
            for scenario in scenario_set.scenarios:
                categories[scenario.category] = categories.get(scenario.category, 0) + 1
                priorities[scenario.priority] = priorities.get(scenario.priority, 0) + 1
        
        return {
            'total_scenario_sets': len(scenario_sets),
            'total_scenarios': total_scenarios,
            'estimated_total_duration': total_duration,
            'categories': categories,
            'priorities': priorities,
            'coverage_areas': list(set().union(*(s.coverage_areas for s in scenario_sets))),
            'scenario_sets': [
                {
                    'name': s.name,
                    'scenarios': s.total_scenarios,
                    'duration': s.estimated_duration,
                    'coverage': s.coverage_areas
                }
                for s in scenario_sets
            ]
        }
