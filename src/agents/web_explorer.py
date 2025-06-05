"""
Web Explorer Agent for FormGenius.
Responsible for navigating websites, analyzing DOM structure, and collecting data for test generation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from playwright.async_api import Browser, BrowserContext, Page
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


class WebExplorer:
    """Agent for exploring and analyzing web applications."""
    
    def __init__(self, browser: Browser):
        """
        Initialize the web explorer.
        
        Args:
            browser: Playwright browser instance
        """
        self.browser = browser
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.visited_urls: Set[str] = set()
        self.discovered_pages: List[Dict[str, Any]] = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='FormGenius-TestBot/1.0'
        )
        self.page = await self.context.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.context:
            await self.context.close()
    
    async def explore_website(self, base_url: str, max_depth: int = 2, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Explore a website and analyze its structure.
        
        Args:
            base_url: Starting URL for exploration
            max_depth: Maximum depth for link following
            max_pages: Maximum number of pages to analyze
            
        Returns:
            List of analyzed pages with their structure and elements
        """
        self.visited_urls.clear()
        self.discovered_pages.clear()
        
        await self._explore_page(base_url, depth=0, max_depth=max_depth, max_pages=max_pages)
        return self.discovered_pages
    
    async def analyze_single_page(self, url: str) -> Dict[str, Any]:
        """
        Analyze a single webpage in detail.
        
        Args:
            url: URL to analyze
            
        Returns:
            Detailed analysis of the page
        """
        try:
            logger.info(f"Analyzing page: {url}")
            await self.page.goto(url, wait_until='networkidle')
            
            # Get page content and metadata
            content = await self.page.content()
            title = await self.page.title()
            
            # Analyze DOM structure
            dom_analysis = await self._analyze_dom_structure(content)
            
            # Detect interactive elements
            interactive_elements = await self._detect_interactive_elements()
            
            # Analyze forms
            forms_analysis = await self._analyze_forms()
            
            # Analyze navigation
            navigation_analysis = await self._analyze_navigation()
            
            # Check accessibility
            accessibility_analysis = await self._analyze_accessibility()
            
            # Analyze page performance
            performance_metrics = await self._analyze_performance()
            
            return {
                'url': url,
                'title': title,
                'dom_analysis': dom_analysis,
                'interactive_elements': interactive_elements,
                'forms': forms_analysis,
                'navigation': navigation_analysis,
                'accessibility': accessibility_analysis,
                'performance': performance_metrics,
                'page_type': self._determine_page_type(dom_analysis, forms_analysis),
                'test_opportunities': self._identify_test_opportunities(
                    interactive_elements, forms_analysis, navigation_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing page {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'analysis_failed': True
            }
    
    async def _explore_page(self, url: str, depth: int, max_depth: int, max_pages: int):
        """Recursively explore pages starting from the given URL."""
        if (len(self.discovered_pages) >= max_pages or 
            depth > max_depth or 
            url in self.visited_urls):
            return
        
        self.visited_urls.add(url)
        
        # Analyze current page
        page_analysis = await self.analyze_single_page(url)
        self.discovered_pages.append(page_analysis)
        
        # Find links to explore further
        if depth < max_depth:
            links = await self._extract_internal_links(url)
            for link in links[:5]:  # Limit to 5 links per page
                if len(self.discovered_pages) < max_pages:
                    await self._explore_page(link, depth + 1, max_depth, max_pages)
    
    async def _analyze_dom_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the DOM structure of the page."""
        soup = BeautifulSoup(content, 'html.parser')
        
        return {
            'total_elements': len(soup.find_all()),
            'headings': {
                f'h{i}': len(soup.find_all(f'h{i}')) 
                for i in range(1, 7)
            },
            'paragraphs': len(soup.find_all('p')),
            'images': len(soup.find_all('img')),
            'links': len(soup.find_all('a')),
            'forms': len(soup.find_all('form')),
            'inputs': len(soup.find_all(['input', 'textarea', 'select'])),
            'buttons': len(soup.find_all('button')) + len(soup.find_all('input', type='submit')),
            'tables': len(soup.find_all('table')),
            'lists': len(soup.find_all(['ul', 'ol'])),
            'divs': len(soup.find_all('div')),
            'spans': len(soup.find_all('span')),
            'has_semantic_html': bool(soup.find_all(['article', 'section', 'nav', 'header', 'footer', 'main', 'aside'])),
            'meta_tags': len(soup.find_all('meta')),
            'scripts': len(soup.find_all('script')),
            'stylesheets': len(soup.find_all('link', rel='stylesheet'))
        }
    
    async def _detect_interactive_elements(self) -> List[Dict[str, Any]]:
        """Detect all interactive elements on the page."""
        interactive_elements = []
        
        # Find all clickable elements
        clickable_selectors = [
            'button',
            'a[href]',
            'input[type="submit"]',
            'input[type="button"]',
            '[onclick]',
            '[role="button"]'
        ]
        
        for selector in clickable_selectors:
            elements = await self.page.query_selector_all(selector)
            for element in elements:
                try:
                    text = await element.text_content()
                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                    attributes = await element.evaluate('el => Array.from(el.attributes).reduce((acc, attr) => {acc[attr.name] = attr.value; return acc;}, {})')
                    bounding_box = await element.bounding_box()
                    
                    interactive_elements.append({
                        'type': 'clickable',
                        'tag': tag_name,
                        'text': text.strip() if text else '',
                        'attributes': attributes,
                        'selector': selector,
                        'bounding_box': bounding_box,
                        'visible': await element.is_visible(),
                        'enabled': await element.is_enabled()
                    })
                except Exception as e:
                    logger.debug(f"Error analyzing element: {e}")
        
        # Find input elements
        input_selectors = [
            'input',
            'textarea',
            'select'
        ]
        
        for selector in input_selectors:
            elements = await self.page.query_selector_all(selector)
            for element in elements:
                try:
                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                    attributes = await element.evaluate('el => Array.from(el.attributes).reduce((acc, attr) => {acc[attr.name] = attr.value; return acc;}, {})')
                    bounding_box = await element.bounding_box()
                    
                    interactive_elements.append({
                        'type': 'input',
                        'tag': tag_name,
                        'input_type': attributes.get('type', 'text'),
                        'name': attributes.get('name', ''),
                        'id': attributes.get('id', ''),
                        'placeholder': attributes.get('placeholder', ''),
                        'required': 'required' in attributes,
                        'attributes': attributes,
                        'bounding_box': bounding_box,
                        'visible': await element.is_visible(),
                        'enabled': await element.is_enabled()
                    })
                except Exception as e:
                    logger.debug(f"Error analyzing input element: {e}")
        
        return interactive_elements
    
    async def _analyze_forms(self) -> List[Dict[str, Any]]:
        """Analyze all forms on the page."""
        forms = []
        form_elements = await self.page.query_selector_all('form')
        
        for i, form in enumerate(form_elements):
            try:
                attributes = await form.evaluate('el => Array.from(el.attributes).reduce((acc, attr) => {acc[attr.name] = attr.value; return acc;}, {})')
                
                # Find all form fields
                fields = []
                field_selectors = ['input', 'textarea', 'select']
                
                for selector in field_selectors:
                    field_elements = await form.query_selector_all(selector)
                    for field in field_elements:
                        field_attrs = await field.evaluate('el => Array.from(el.attributes).reduce((acc, attr) => {acc[attr.name] = attr.value; return acc;}, {})')
                        tag_name = await field.evaluate('el => el.tagName.toLowerCase()')
                        
                        fields.append({
                            'tag': tag_name,
                            'type': field_attrs.get('type', 'text'),
                            'name': field_attrs.get('name', ''),
                            'id': field_attrs.get('id', ''),
                            'placeholder': field_attrs.get('placeholder', ''),
                            'required': 'required' in field_attrs,
                            'attributes': field_attrs
                        })
                
                forms.append({
                    'index': i,
                    'action': attributes.get('action', ''),
                    'method': attributes.get('method', 'GET').upper(),
                    'encoding': attributes.get('enctype', 'application/x-www-form-urlencoded'),
                    'fields': fields,
                    'field_count': len(fields),
                    'attributes': attributes
                })
                
            except Exception as e:
                logger.debug(f"Error analyzing form {i}: {e}")
        
        return forms
    
    async def _analyze_navigation(self) -> Dict[str, Any]:
        """Analyze navigation elements and structure."""
        nav_elements = await self.page.query_selector_all('nav, [role="navigation"]')
        nav_links = await self.page.query_selector_all('nav a, [role="navigation"] a')
        
        # Find breadcrumbs
        breadcrumb_selectors = [
            '[aria-label*="breadcrumb"]',
            '.breadcrumb',
            '.breadcrumbs',
            '[role="navigation"] ol',
            '[role="navigation"] ul'
        ]
        
        breadcrumbs = []
        for selector in breadcrumb_selectors:
            elements = await self.page.query_selector_all(selector)
            for element in elements:
                text = await element.text_content()
                if text and len(text.strip()) > 0:
                    breadcrumbs.append(text.strip())
        
        # Analyze menu structure
        menu_items = []
        for link in nav_links:
            try:
                text = await link.text_content()
                href = await link.get_attribute('href')
                if text and text.strip():
                    menu_items.append({
                        'text': text.strip(),
                        'href': href,
                        'external': href and (href.startswith('http') and not await self.page.url in href)
                    })
            except Exception as e:
                logger.debug(f"Error analyzing nav link: {e}")
        
        return {
            'nav_elements_count': len(nav_elements),
            'nav_links_count': len(nav_links),
            'menu_items': menu_items,
            'breadcrumbs': breadcrumbs,
            'has_main_navigation': len(nav_elements) > 0
        }
    
    async def _analyze_accessibility(self) -> Dict[str, Any]:
        """Analyze accessibility features of the page."""
        # Check for ARIA labels and roles
        aria_elements = await self.page.query_selector_all('[aria-label], [aria-labelledby], [role]')
        
        # Check for semantic HTML
        semantic_elements = await self.page.query_selector_all('main, header, footer, nav, section, article, aside')
        
        # Check for form labels
        labels = await self.page.query_selector_all('label')
        inputs_with_labels = await self.page.query_selector_all('input[id]:not([type="hidden"])')
        
        # Check for alt text on images
        images = await self.page.query_selector_all('img')
        images_with_alt = await self.page.query_selector_all('img[alt]')
        
        # Check for heading structure
        headings = []
        for level in range(1, 7):
            heading_elements = await self.page.query_selector_all(f'h{level}')
            for heading in heading_elements:
                text = await heading.text_content()
                headings.append({'level': level, 'text': text.strip() if text else ''})
        
        return {
            'aria_elements_count': len(aria_elements),
            'semantic_elements_count': len(semantic_elements),
            'has_semantic_structure': len(semantic_elements) > 0,
            'labels_count': len(labels),
            'inputs_count': len(inputs_with_labels),
            'labeled_inputs_ratio': len(labels) / max(len(inputs_with_labels), 1),
            'images_count': len(images),
            'images_with_alt_count': len(images_with_alt),
            'images_alt_ratio': len(images_with_alt) / max(len(images), 1),
            'heading_structure': headings,
            'heading_hierarchy_valid': self._validate_heading_hierarchy(headings)
        }
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze basic performance metrics."""
        try:
            # Get performance metrics
            metrics = await self.page.evaluate('''() => {
                const nav = performance.getEntriesByType('navigation')[0];
                return {
                    loadTime: nav ? nav.loadEventEnd - nav.loadEventStart : 0,
                    domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart : 0,
                    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
                    resources: performance.getEntriesByType('resource').length
                };
            }''')
            
            return metrics
        except Exception as e:
            logger.debug(f"Error getting performance metrics: {e}")
            return {}
    
    async def _extract_internal_links(self, base_url: str) -> List[str]:
        """Extract internal links from the current page."""
        try:
            links = await self.page.query_selector_all('a[href]')
            internal_links = []
            
            for link in links:
                href = await link.get_attribute('href')
                if href and not href.startswith('#'):
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = f"{base_url.rstrip('/')}{href}"
                    elif href.startswith('http'):
                        # Check if it's the same domain
                        if base_url in href:
                            full_url = href
                        else:
                            continue  # Skip external links
                    else:
                        # Relative path
                        full_url = f"{base_url.rstrip('/')}/{href}"
                    
                    if full_url not in self.visited_urls:
                        internal_links.append(full_url)
            
            return internal_links[:10]  # Limit to 10 links
        except Exception as e:
            logger.debug(f"Error extracting links: {e}")
            return []
    
    def _determine_page_type(self, dom_analysis: Dict[str, Any], forms_analysis: List[Dict[str, Any]]) -> str:
        """Determine the type of page based on its structure."""
        if forms_analysis:
            if any('login' in form.get('action', '').lower() or 
                   any(field.get('type') == 'password' for field in form.get('fields', []))
                   for form in forms_analysis):
                return 'login'
            elif any('register' in form.get('action', '').lower() or 
                     'signup' in form.get('action', '').lower()
                     for form in forms_analysis):
                return 'registration'
            elif any('contact' in form.get('action', '').lower() or 
                     'feedback' in form.get('action', '').lower()
                     for form in forms_analysis):
                return 'contact'
            else:
                return 'form'
        
        if dom_analysis.get('tables', 0) > 0:
            return 'data'
        
        if dom_analysis.get('links', 0) > dom_analysis.get('paragraphs', 0):
            return 'navigation'
        
        return 'content'
    
    def _identify_test_opportunities(self, interactive_elements: List[Dict[str, Any]], 
                                   forms_analysis: List[Dict[str, Any]], 
                                   navigation_analysis: Dict[str, Any]) -> List[str]:
        """Identify testing opportunities based on page analysis."""
        opportunities = []
        
        # Form testing opportunities
        if forms_analysis:
            opportunities.extend([
                'form_validation_testing',
                'form_submission_testing',
                'required_field_testing',
                'input_sanitization_testing'
            ])
        
        # Interactive element testing
        clickable_count = len([el for el in interactive_elements if el.get('type') == 'clickable'])
        if clickable_count > 0:
            opportunities.extend([
                'button_click_testing',
                'link_navigation_testing',
                'interactive_element_testing'
            ])
        
        # Navigation testing
        if navigation_analysis.get('has_main_navigation'):
            opportunities.append('navigation_testing')
        
        # Input testing
        input_count = len([el for el in interactive_elements if el.get('type') == 'input'])
        if input_count > 0:
            opportunities.extend([
                'input_field_testing',
                'data_entry_testing',
                'boundary_value_testing'
            ])
        
        return list(set(opportunities))  # Remove duplicates
    
    def _validate_heading_hierarchy(self, headings: List[Dict[str, str]]) -> bool:
        """Validate if heading hierarchy follows proper structure."""
        if not headings:
            return True
        
        levels = [h['level'] for h in headings]
        
        # Check if it starts with h1
        if levels[0] != 1:
            return False
        
        # Check for proper sequential order
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                return False
        
        return True
