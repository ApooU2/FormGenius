"""
Flow Analyzer for FormGenius

This module analyzes user flows and interaction patterns:
- Multi-page workflow detection
- Form submission flows
- Authentication flows
- E-commerce checkout flows
- Navigation pattern analysis
- State transition mapping
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from playwright.sync_api import Page, Response
import time
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

@dataclass
class FlowStep:
    """Represents a single step in a user flow"""
    step_id: str
    url: str
    page_title: str
    action_type: str  # 'navigate', 'click', 'fill', 'submit', 'wait'
    element_selector: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    expected_outcome: Optional[str] = None
    validation_selectors: List[str] = field(default_factory=list)
    wait_conditions: List[str] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class UserFlow:
    """Represents a complete user flow"""
    flow_id: str
    name: str
    description: str
    flow_type: str  # 'authentication', 'form_submission', 'checkout', 'navigation'
    priority: str  # 'critical', 'high', 'medium', 'low'
    steps: List[FlowStep] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    exit_points: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    complexity_score: int = 0
    dependencies: List[str] = field(default_factory=list)

@dataclass
class FlowAnalysisResult:
    """Complete flow analysis results"""
    discovered_flows: List[UserFlow]
    page_transitions: Dict[str, List[str]]
    form_flows: List[UserFlow]
    authentication_flows: List[UserFlow]
    commerce_flows: List[UserFlow]
    navigation_patterns: Dict[str, Any]
    flow_complexity_analysis: Dict[str, Any]
    recommended_test_flows: List[UserFlow]

class FlowAnalyzer:
    """Advanced user flow analyzer for web applications"""
    
    def __init__(self):
        self.discovered_pages = set()
        self.page_transitions = {}
        self.form_submissions = []
        self.navigation_patterns = {}
        
        # Flow pattern definitions
        self.flow_patterns = {
            'authentication': {
                'keywords': ['login', 'signin', 'signup', 'register', 'auth', 'password'],
                'form_fields': ['email', 'username', 'password', 'confirm'],
                'success_indicators': ['dashboard', 'profile', 'welcome', 'logout']
            },
            'checkout': {
                'keywords': ['cart', 'checkout', 'payment', 'billing', 'shipping'],
                'form_fields': ['address', 'card', 'cvv', 'expiry', 'name'],
                'success_indicators': ['confirmation', 'receipt', 'order', 'thank']
            },
            'contact': {
                'keywords': ['contact', 'support', 'feedback', 'inquiry'],
                'form_fields': ['name', 'email', 'message', 'subject'],
                'success_indicators': ['sent', 'submitted', 'received']
            },
            'registration': {
                'keywords': ['register', 'signup', 'join', 'create'],
                'form_fields': ['name', 'email', 'password', 'terms'],
                'success_indicators': ['verify', 'confirm', 'welcome']
            }
        }
    
    async def analyze_flows(self, page: Page, start_url: str, max_depth: int = 3) -> FlowAnalysisResult:
        """Analyze user flows starting from a given URL"""
        try:
            logger.info(f"Starting flow analysis from {start_url}")
            
            # Navigate to start URL
            await page.goto(start_url)
            await page.wait_for_load_state('networkidle')
            
            # Discover all flows
            discovered_flows = await self._discover_flows(page, start_url, max_depth)
            
            # Categorize flows
            form_flows = [f for f in discovered_flows if f.flow_type in ['form_submission', 'contact']]
            auth_flows = [f for f in discovered_flows if f.flow_type == 'authentication']
            commerce_flows = [f for f in discovered_flows if f.flow_type == 'checkout']
            
            # Analyze navigation patterns
            navigation_patterns = await self._analyze_navigation_patterns(page)
            
            # Calculate flow complexity
            complexity_analysis = self._analyze_flow_complexity(discovered_flows)
            
            # Recommend test flows
            recommended_flows = self._recommend_test_flows(discovered_flows)
            
            result = FlowAnalysisResult(
                discovered_flows=discovered_flows,
                page_transitions=self.page_transitions,
                form_flows=form_flows,
                authentication_flows=auth_flows,
                commerce_flows=commerce_flows,
                navigation_patterns=navigation_patterns,
                flow_complexity_analysis=complexity_analysis,
                recommended_test_flows=recommended_flows
            )
            
            logger.info(f"Flow analysis complete: {len(discovered_flows)} flows discovered")
            return result
            
        except Exception as e:
            logger.error(f"Flow analysis failed: {str(e)}")
            raise
    
    async def _discover_flows(self, page: Page, start_url: str, max_depth: int) -> List[UserFlow]:
        """Discover all user flows on the website"""
        flows = []
        
        try:
            # Analyze forms on current page
            form_flows = await self._analyze_form_flows(page)
            flows.extend(form_flows)
            
            # Discover navigation flows
            nav_flows = await self._analyze_navigation_flows(page, start_url, max_depth)
            flows.extend(nav_flows)
            
            # Look for authentication flows
            auth_flows = await self._discover_authentication_flows(page)
            flows.extend(auth_flows)
            
            # Look for e-commerce flows
            commerce_flows = await self._discover_commerce_flows(page)
            flows.extend(commerce_flows)
            
            return flows
            
        except Exception as e:
            logger.error(f"Flow discovery failed: {str(e)}")
            return []
    
    async def _analyze_form_flows(self, page: Page) -> List[UserFlow]:
        """Analyze form submission flows"""
        flows = []
        
        try:
            forms_data = await page.evaluate('''
                () => {
                    const forms = document.querySelectorAll('form');
                    return Array.from(forms).map((form, index) => {
                        const fields = Array.from(form.querySelectorAll('input, textarea, select'));
                        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]') || 
                                           form.querySelector('button:not([type])');
                        
                        return {
                            id: form.id || `form-${index}`,
                            action: form.action || window.location.href,
                            method: form.method || 'GET',
                            fields: fields.map(field => ({
                                name: field.name || field.id,
                                type: field.type || 'text',
                                required: field.required,
                                placeholder: field.placeholder
                            })),
                            submitSelector: submitButton ? this._getCSSSelector(submitButton) : null,
                            formSelector: this._getCSSSelector(form)
                        };
                    });
                }
            ''')
            
            for form_data in forms_data:
                flow_type = self._classify_form_flow(form_data)
                
                # Create flow steps
                steps = []
                step_id = 1
                
                # Fill form fields
                for field in form_data['fields']:
                    if field['name'] and field['type'] not in ['hidden', 'submit']:
                        steps.append(FlowStep(
                            step_id=f"step_{step_id}",
                            url=page.url,
                            page_title=await page.title(),
                            action_type='fill',
                            element_selector=f"[name='{field['name']}']",
                            input_data={'value': self._generate_test_data(field)},
                            expected_outcome=f"Field '{field['name']}' filled successfully"
                        ))
                        step_id += 1
                
                # Submit form
                if form_data['submitSelector']:
                    steps.append(FlowStep(
                        step_id=f"step_{step_id}",
                        url=page.url,
                        page_title=await page.title(),
                        action_type='submit',
                        element_selector=form_data['submitSelector'],
                        expected_outcome="Form submitted successfully",
                        wait_conditions=['networkidle', 'domcontentloaded']
                    ))
                
                flow = UserFlow(
                    flow_id=f"form_flow_{form_data['id']}",
                    name=f"{flow_type.title()} Form Flow",
                    description=f"Complete {flow_type} form submission workflow",
                    flow_type=flow_type,
                    priority='high' if flow_type == 'authentication' else 'medium',
                    steps=steps,
                    entry_points=[page.url],
                    complexity_score=len(steps)
                )
                flows.append(flow)
            
            return flows
            
        except Exception as e:
            logger.error(f"Form flow analysis failed: {str(e)}")
            return []
    
    async def _analyze_navigation_flows(self, page: Page, start_url: str, max_depth: int) -> List[UserFlow]:
        """Analyze navigation flows and page transitions"""
        flows = []
        
        try:
            # Get all navigation links
            nav_links = await page.evaluate('''
                () => {
                    const links = document.querySelectorAll('a[href], nav a, .nav a, .menu a');
                    return Array.from(links)
                        .filter(link => link.href && !link.href.startsWith('javascript:'))
                        .map(link => ({
                            href: link.href,
                            text: link.textContent?.trim(),
                            selector: this._getCSSSelector(link)
                        }));
                }
            ''')
            
            # Create navigation flows
            for link in nav_links[:10]:  # Limit to prevent excessive crawling
                if self._is_same_domain(link['href'], start_url):
                    flow = UserFlow(
                        flow_id=f"nav_flow_{hash(link['href'])}",
                        name=f"Navigate to {link['text'] or 'Page'}",
                        description=f"Navigation flow to {link['href']}",
                        flow_type='navigation',
                        priority='low',
                        steps=[
                            FlowStep(
                                step_id="step_1",
                                url=page.url,
                                page_title=await page.title(),
                                action_type='click',
                                element_selector=link['selector'],
                                expected_outcome=f"Navigate to {link['href']}",
                                wait_conditions=['networkidle']
                            )
                        ],
                        entry_points=[page.url],
                        exit_points=[link['href']]
                    )
                    flows.append(flow)
            
            return flows
            
        except Exception as e:
            logger.error(f"Navigation flow analysis failed: {str(e)}")
            return []
    
    async def _discover_authentication_flows(self, page: Page) -> List[UserFlow]:
        """Discover authentication-related flows"""
        flows = []
        
        try:
            # Look for login/signup forms
            auth_elements = await page.evaluate('''
                () => {
                    const authKeywords = ['login', 'signin', 'signup', 'register', 'log in', 'sign up'];
                    const elements = [];
                    
                    // Find forms with auth-related fields
                    document.querySelectorAll('form').forEach(form => {
                        const hasEmailOrUsername = form.querySelector('input[type="email"], input[name*="email"], input[name*="username"]');
                        const hasPassword = form.querySelector('input[type="password"]');
                        
                        if (hasEmailOrUsername && hasPassword) {
                            elements.push({
                                type: 'form',
                                element: form,
                                selector: this._getCSSSelector(form),
                                isLogin: !form.querySelector('input[name*="confirm"]'),
                                isSignup: !!form.querySelector('input[name*="confirm"]')
                            });
                        }
                    });
                    
                    // Find auth-related links
                    document.querySelectorAll('a').forEach(link => {
                        const text = link.textContent?.toLowerCase() || '';
                        const href = link.href?.toLowerCase() || '';
                        
                        if (authKeywords.some(keyword => text.includes(keyword) || href.includes(keyword))) {
                            elements.push({
                                type: 'link',
                                text: link.textContent?.trim(),
                                href: link.href,
                                selector: this._getCSSSelector(link)
                            });
                        }
                    });
                    
                    return elements;
                }
            ''')
            
            # Create authentication flows
            for element in auth_elements:
                if element['type'] == 'form':
                    flow_type = 'login' if element.get('isLogin') else 'signup'
                    
                    steps = [
                        FlowStep(
                            step_id="step_1",
                            url=page.url,
                            page_title=await page.title(),
                            action_type='fill',
                            element_selector=f"{element['selector']} input[type='email'], {element['selector']} input[name*='email'], {element['selector']} input[name*='username']",
                            input_data={'value': 'test@example.com'},
                            expected_outcome="Email/username filled"
                        ),
                        FlowStep(
                            step_id="step_2",
                            url=page.url,
                            page_title=await page.title(),
                            action_type='fill',
                            element_selector=f"{element['selector']} input[type='password']",
                            input_data={'value': 'password123'},
                            expected_outcome="Password filled"
                        ),
                        FlowStep(
                            step_id="step_3",
                            url=page.url,
                            page_title=await page.title(),
                            action_type='submit',
                            element_selector=f"{element['selector']} button[type='submit'], {element['selector']} input[type='submit']",
                            expected_outcome=f"{flow_type.title()} successful",
                            wait_conditions=['networkidle']
                        )
                    ]
                    
                    flow = UserFlow(
                        flow_id=f"auth_{flow_type}_flow",
                        name=f"{flow_type.title()} Flow",
                        description=f"User {flow_type} authentication flow",
                        flow_type='authentication',
                        priority='critical',
                        steps=steps,
                        entry_points=[page.url]
                    )
                    flows.append(flow)
            
            return flows
            
        except Exception as e:
            logger.error(f"Authentication flow discovery failed: {str(e)}")
            return []
    
    async def _discover_commerce_flows(self, page: Page) -> List[UserFlow]:
        """Discover e-commerce related flows"""
        flows = []
        
        try:
            commerce_elements = await page.evaluate('''
                () => {
                    const commerceKeywords = ['add to cart', 'buy now', 'checkout', 'purchase', 'add to bag'];
                    const elements = [];
                    
                    // Find add to cart buttons
                    document.querySelectorAll('button, a, input[type="submit"]').forEach(element => {
                        const text = element.textContent?.toLowerCase() || '';
                        const value = element.value?.toLowerCase() || '';
                        
                        if (commerceKeywords.some(keyword => text.includes(keyword) || value.includes(keyword))) {
                            elements.push({
                                type: 'action',
                                action: text || value,
                                selector: this._getCSSSelector(element)
                            });
                        }
                    });
                    
                    return elements;
                }
            ''')
            
            # Create commerce flows
            for element in commerce_elements:
                action_type = element['action']
                
                if 'cart' in action_type:
                    flow = UserFlow(
                        flow_id="add_to_cart_flow",
                        name="Add to Cart Flow",
                        description="Add product to shopping cart",
                        flow_type='checkout',
                        priority='high',
                        steps=[
                            FlowStep(
                                step_id="step_1",
                                url=page.url,
                                page_title=await page.title(),
                                action_type='click',
                                element_selector=element['selector'],
                                expected_outcome="Product added to cart",
                                validation_selectors=['.cart-count', '.cart-total', '.added-to-cart']
                            )
                        ],
                        entry_points=[page.url]
                    )
                    flows.append(flow)
            
            return flows
            
        except Exception as e:
            logger.error(f"Commerce flow discovery failed: {str(e)}")
            return []
    
    async def _analyze_navigation_patterns(self, page: Page) -> Dict[str, Any]:
        """Analyze navigation patterns and site structure"""
        try:
            navigation_data = await page.evaluate('''
                () => {
                    const patterns = {
                        mainNavigation: [],
                        breadcrumbs: [],
                        pagination: [],
                        footerLinks: [],
                        sidebarLinks: []
                    };
                    
                    // Main navigation
                    const mainNav = document.querySelector('nav, .nav, .navigation, .navbar');
                    if (mainNav) {
                        patterns.mainNavigation = Array.from(mainNav.querySelectorAll('a'))
                            .map(link => ({
                                text: link.textContent?.trim(),
                                href: link.href
                            }));
                    }
                    
                    // Breadcrumbs
                    const breadcrumbs = document.querySelector('.breadcrumb, .breadcrumbs, [aria-label*="breadcrumb"]');
                    if (breadcrumbs) {
                        patterns.breadcrumbs = Array.from(breadcrumbs.querySelectorAll('a'))
                            .map(link => ({
                                text: link.textContent?.trim(),
                                href: link.href
                            }));
                    }
                    
                    // Pagination
                    const pagination = document.querySelector('.pagination, .pager, .page-numbers');
                    if (pagination) {
                        patterns.pagination = Array.from(pagination.querySelectorAll('a, button'))
                            .map(element => ({
                                text: element.textContent?.trim(),
                                href: element.href || null
                            }));
                    }
                    
                    return patterns;
                }
            ''')
            
            return navigation_data
            
        except Exception as e:
            logger.error(f"Navigation pattern analysis failed: {str(e)}")
            return {}
    
    def _classify_form_flow(self, form_data: Dict[str, Any]) -> str:
        """Classify the type of form flow"""
        field_names = [field['name'].lower() for field in form_data['fields'] if field['name']]
        
        for flow_type, pattern in self.flow_patterns.items():
            field_matches = sum(1 for field in pattern['form_fields'] 
                              if any(field in name for name in field_names))
            
            if field_matches >= 2:  # At least 2 matching fields
                return flow_type
        
        return 'form_submission'
    
    def _generate_test_data(self, field: Dict[str, Any]) -> str:
        """Generate appropriate test data for form fields"""
        field_name = field.get('name', '').lower()
        field_type = field.get('type', 'text').lower()
        
        if 'email' in field_name or field_type == 'email':
            return 'test@example.com'
        elif 'password' in field_name or field_type == 'password':
            return 'TestPassword123!'
        elif 'phone' in field_name or field_type == 'tel':
            return '+1234567890'
        elif 'name' in field_name:
            return 'John Doe'
        elif field_type == 'number':
            return '123'
        elif field_type == 'date':
            return '2024-01-01'
        else:
            return 'Test input'
    
    def _is_same_domain(self, url: str, base_url: str) -> bool:
        """Check if URL is from the same domain"""
        try:
            url_domain = urlparse(url).netloc
            base_domain = urlparse(base_url).netloc
            return url_domain == base_domain or url_domain == ''
        except:
            return False
    
    def _analyze_flow_complexity(self, flows: List[UserFlow]) -> Dict[str, Any]:
        """Analyze the complexity of discovered flows"""
        if not flows:
            return {}
        
        total_steps = sum(len(flow.steps) for flow in flows)
        avg_steps = total_steps / len(flows)
        
        complexity_by_type = {}
        for flow in flows:
            flow_type = flow.flow_type
            if flow_type not in complexity_by_type:
                complexity_by_type[flow_type] = {'count': 0, 'total_steps': 0}
            
            complexity_by_type[flow_type]['count'] += 1
            complexity_by_type[flow_type]['total_steps'] += len(flow.steps)
        
        # Calculate average steps per flow type
        for flow_type in complexity_by_type:
            data = complexity_by_type[flow_type]
            data['avg_steps'] = data['total_steps'] / data['count']
        
        return {
            'total_flows': len(flows),
            'average_steps_per_flow': avg_steps,
            'complexity_by_type': complexity_by_type,
            'most_complex_flow': max(flows, key=lambda f: len(f.steps)).name if flows else None,
            'simplest_flow': min(flows, key=lambda f: len(f.steps)).name if flows else None
        }
    
    def _recommend_test_flows(self, flows: List[UserFlow]) -> List[UserFlow]:
        """Recommend the most important flows for testing"""
        # Priority order: critical > high > medium > low
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        
        # Sort by priority and complexity
        sorted_flows = sorted(flows, 
                            key=lambda f: (priority_order.get(f.priority, 0), len(f.steps)), 
                            reverse=True)
        
        # Return top flows for testing (up to 10)
        return sorted_flows[:10]
    
    def get_flow_summary(self, analysis_result: FlowAnalysisResult) -> Dict[str, Any]:
        """Get a summary of the flow analysis"""
        return {
            'overview': {
                'total_flows': len(analysis_result.discovered_flows),
                'form_flows': len(analysis_result.form_flows),
                'auth_flows': len(analysis_result.authentication_flows),
                'commerce_flows': len(analysis_result.commerce_flows)
            },
            'complexity': analysis_result.flow_complexity_analysis,
            'recommendations': {
                'priority_flows': [f.name for f in analysis_result.recommended_test_flows[:5]],
                'critical_flows': [f.name for f in analysis_result.discovered_flows if f.priority == 'critical']
            },
            'navigation': {
                'main_nav_items': len(analysis_result.navigation_patterns.get('mainNavigation', [])),
                'has_breadcrumbs': bool(analysis_result.navigation_patterns.get('breadcrumbs')),
                'has_pagination': bool(analysis_result.navigation_patterns.get('pagination'))
            }
        }
