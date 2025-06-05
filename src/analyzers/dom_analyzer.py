"""
DOM Analyzer for FormGenius

This module provides comprehensive DOM structure analysis capabilities:
- HTML element hierarchy analysis
- Form field detection and categorization
- Interactive element identification
- Accessibility attribute extraction
- Semantic structure mapping
"""

import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from playwright.sync_api import Page, ElementHandle
import re

logger = logging.getLogger(__name__)

@dataclass
class DOMElement:
    """Represents a DOM element with analysis metadata"""
    tag_name: str
    element_id: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    text_content: Optional[str] = None
    xpath: Optional[str] = None
    css_selector: Optional[str] = None
    is_interactive: bool = False
    is_form_element: bool = False
    accessibility_info: Dict[str, Any] = field(default_factory=dict)
    children_count: int = 0
    depth: int = 0

@dataclass
class FormField:
    """Represents a form field with detailed analysis"""
    name: str
    field_type: str
    label: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    validation_pattern: Optional[str] = None
    options: List[str] = field(default_factory=list)
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    selector: Optional[str] = None
    description: Optional[str] = None

@dataclass
class DOMAnalysisResult:
    """Complete DOM analysis results"""
    total_elements: int
    interactive_elements: List[DOMElement]
    form_fields: List[FormField]
    forms: List[Dict[str, Any]]
    navigation_elements: List[DOMElement]
    semantic_structure: Dict[str, Any]
    accessibility_issues: List[Dict[str, str]]
    page_metadata: Dict[str, Any]

class DOMAnalyzer:
    """Advanced DOM structure analyzer using Playwright"""
    
    def __init__(self):
        self.interactive_tags = {
            'a', 'button', 'input', 'textarea', 'select', 'option',
            'details', 'summary', 'dialog', 'menu', 'menuitem'
        }
        self.form_tags = {
            'form', 'input', 'textarea', 'select', 'button', 'fieldset', 'legend'
        }
        self.semantic_tags = {
            'header', 'nav', 'main', 'section', 'article', 'aside', 'footer',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        }
    
    async def analyze_page(self, page: Page) -> DOMAnalysisResult:
        """Perform comprehensive DOM analysis of a page"""
        try:
            logger.info("Starting DOM analysis")
            
            # Get page metadata
            page_metadata = await self._extract_page_metadata(page)
            
            # Analyze all elements
            all_elements = await self._analyze_all_elements(page)
            
            # Identify interactive elements
            interactive_elements = await self._identify_interactive_elements(page)
            
            # Analyze forms
            forms, form_fields = await self._analyze_forms(page)
            
            # Identify navigation elements
            navigation_elements = await self._identify_navigation_elements(page)
            
            # Build semantic structure
            semantic_structure = await self._build_semantic_structure(page)
            
            # Check accessibility
            accessibility_issues = await self._check_accessibility(page)
            
            result = DOMAnalysisResult(
                total_elements=len(all_elements),
                interactive_elements=interactive_elements,
                form_fields=form_fields,
                forms=forms,
                navigation_elements=navigation_elements,
                semantic_structure=semantic_structure,
                accessibility_issues=accessibility_issues,
                page_metadata=page_metadata
            )
            
            logger.info(f"DOM analysis complete: {result.total_elements} elements analyzed")
            return result
            
        except Exception as e:
            logger.error(f"DOM analysis failed: {str(e)}")
            raise
    
    async def _extract_page_metadata(self, page: Page) -> Dict[str, Any]:
        """Extract page metadata and head information"""
        try:
            metadata = {
                'title': await page.title(),
                'url': page.url,
                'viewport': await page.viewport_size(),
            }
            
            # Extract meta tags
            meta_tags = await page.evaluate('''
                () => {
                    const metas = document.querySelectorAll('meta');
                    const result = {};
                    metas.forEach(meta => {
                        const name = meta.getAttribute('name') || meta.getAttribute('property');
                        const content = meta.getAttribute('content');
                        if (name && content) {
                            result[name] = content;
                        }
                    });
                    return result;
                }
            ''')
            metadata['meta_tags'] = meta_tags
            
            # Extract stylesheets and scripts
            metadata['stylesheets'] = await page.evaluate('''
                () => Array.from(document.querySelectorAll('link[rel="stylesheet"]'))
                    .map(link => link.href)
            ''')
            
            metadata['scripts'] = await page.evaluate('''
                () => Array.from(document.querySelectorAll('script[src]'))
                    .map(script => script.src)
            ''')
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract page metadata: {str(e)}")
            return {}
    
    async def _analyze_all_elements(self, page: Page) -> List[DOMElement]:
        """Analyze all DOM elements"""
        try:
            elements_data = await page.evaluate('''
                () => {
                    const elements = document.querySelectorAll('*');
                    return Array.from(elements).map((el, index) => {
                        const rect = el.getBoundingClientRect();
                        return {
                            tagName: el.tagName.toLowerCase(),
                            id: el.id || null,
                            classes: Array.from(el.classList),
                            attributes: Object.fromEntries(
                                Array.from(el.attributes).map(attr => [attr.name, attr.value])
                            ),
                            textContent: el.textContent?.trim()?.substring(0, 200) || null,
                            childrenCount: el.children.length,
                            depth: el.closest('*') ? 
                                el.parentElement ? this._getDepth(el) : 0 : 0,
                            isVisible: rect.width > 0 && rect.height > 0,
                            xpath: this._getXPath(el)
                        };
                    });
                }
            ''')
            
            return [self._create_dom_element(data) for data in elements_data]
            
        except Exception as e:
            logger.error(f"Failed to analyze all elements: {str(e)}")
            return []
    
    async def _identify_interactive_elements(self, page: Page) -> List[DOMElement]:
        """Identify interactive elements on the page"""
        try:
            interactive_data = await page.evaluate('''
                () => {
                    const interactiveTags = new Set(['a', 'button', 'input', 'textarea', 'select', 'details', 'summary']);
                    const elements = document.querySelectorAll('*');
                    
                    return Array.from(elements)
                        .filter(el => {
                            return interactiveTags.has(el.tagName.toLowerCase()) ||
                                   el.hasAttribute('onclick') ||
                                   el.hasAttribute('onsubmit') ||
                                   el.hasAttribute('tabindex') ||
                                   el.style.cursor === 'pointer' ||
                                   el.getAttribute('role') === 'button';
                        })
                        .map(el => {
                            const rect = el.getBoundingClientRect();
                            return {
                                tagName: el.tagName.toLowerCase(),
                                id: el.id || null,
                                classes: Array.from(el.classList),
                                attributes: Object.fromEntries(
                                    Array.from(el.attributes).map(attr => [attr.name, attr.value])
                                ),
                                textContent: el.textContent?.trim()?.substring(0, 100) || null,
                                isVisible: rect.width > 0 && rect.height > 0,
                                cssSelector: this._getCSSSelector(el),
                                accessibilityInfo: {
                                    role: el.getAttribute('role'),
                                    ariaLabel: el.getAttribute('aria-label'),
                                    ariaDescribedBy: el.getAttribute('aria-describedby'),
                                    tabIndex: el.getAttribute('tabindex')
                                }
                            };
                        });
                }
            ''')
            
            elements = []
            for data in interactive_data:
                element = self._create_dom_element(data)
                element.is_interactive = True
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to identify interactive elements: {str(e)}")
            return []
    
    async def _analyze_forms(self, page: Page) -> tuple[List[Dict[str, Any]], List[FormField]]:
        """Analyze all forms and form fields on the page"""
        try:
            forms_data = await page.evaluate('''
                () => {
                    const forms = document.querySelectorAll('form');
                    return Array.from(forms).map((form, index) => {
                        const formFields = Array.from(form.querySelectorAll('input, textarea, select'));
                        
                        return {
                            id: form.id || `form-${index}`,
                            action: form.action || null,
                            method: form.method || 'GET',
                            name: form.name || null,
                            enctype: form.enctype || null,
                            cssSelector: this._getCSSSelector(form),
                            fieldCount: formFields.length,
                            fields: formFields.map(field => ({
                                name: field.name || field.id || `field-${Math.random().toString(36).substr(2, 9)}`,
                                type: field.type || field.tagName.toLowerCase(),
                                id: field.id || null,
                                label: this._getFieldLabel(field),
                                placeholder: field.placeholder || null,
                                required: field.required || false,
                                pattern: field.pattern || null,
                                minLength: field.minLength || null,
                                maxLength: field.maxLength || null,
                                options: field.tagName.toLowerCase() === 'select' ? 
                                    Array.from(field.options).map(opt => opt.value) : [],
                                cssSelector: this._getCSSSelector(field)
                            }))
                        };
                    });
                }
            ''')
            
            forms = []
            all_form_fields = []
            
            for form_data in forms_data:
                forms.append(form_data)
                
                # Convert form fields to FormField objects
                for field_data in form_data.get('fields', []):
                    form_field = FormField(
                        name=field_data['name'],
                        field_type=field_data['type'],
                        label=field_data.get('label'),
                        placeholder=field_data.get('placeholder'),
                        required=field_data.get('required', False),
                        validation_pattern=field_data.get('pattern'),
                        options=field_data.get('options', []),
                        min_length=field_data.get('minLength'),
                        max_length=field_data.get('maxLength'),
                        selector=field_data.get('cssSelector')
                    )
                    all_form_fields.append(form_field)
            
            return forms, all_form_fields
            
        except Exception as e:
            logger.error(f"Failed to analyze forms: {str(e)}")
            return [], []
    
    async def _identify_navigation_elements(self, page: Page) -> List[DOMElement]:
        """Identify navigation elements"""
        try:
            nav_data = await page.evaluate('''
                () => {
                    const navSelectors = [
                        'nav', 'nav a', 'nav button',
                        '[role="navigation"]', '[role="navigation"] a',
                        '.nav', '.nav a', '.navigation', '.navigation a',
                        '.menu', '.menu a', '.navbar', '.navbar a',
                        'header a', 'footer a'
                    ];
                    
                    const navElements = new Set();
                    navSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => navElements.add(el));
                    });
                    
                    return Array.from(navElements).map(el => ({
                        tagName: el.tagName.toLowerCase(),
                        id: el.id || null,
                        classes: Array.from(el.classList),
                        textContent: el.textContent?.trim()?.substring(0, 100) || null,
                        href: el.href || null,
                        cssSelector: this._getCSSSelector(el)
                    }));
                }
            ''')
            
            return [self._create_dom_element(data) for data in nav_data]
            
        except Exception as e:
            logger.error(f"Failed to identify navigation elements: {str(e)}")
            return []
    
    async def _build_semantic_structure(self, page: Page) -> Dict[str, Any]:
        """Build semantic structure map of the page"""
        try:
            structure = await page.evaluate('''
                () => {
                    const structure = {
                        headings: [],
                        landmarks: [],
                        lists: [],
                        tables: [],
                        media: []
                    };
                    
                    // Headings
                    document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
                        structure.headings.push({
                            level: parseInt(h.tagName.substring(1)),
                            text: h.textContent?.trim(),
                            id: h.id || null
                        });
                    });
                    
                    // Landmarks
                    document.querySelectorAll('header, nav, main, section, article, aside, footer').forEach(landmark => {
                        structure.landmarks.push({
                            type: landmark.tagName.toLowerCase(),
                            id: landmark.id || null,
                            classes: Array.from(landmark.classList)
                        });
                    });
                    
                    // Lists
                    document.querySelectorAll('ul, ol').forEach(list => {
                        structure.lists.push({
                            type: list.tagName.toLowerCase(),
                            itemCount: list.querySelectorAll('li').length
                        });
                    });
                    
                    // Tables
                    document.querySelectorAll('table').forEach(table => {
                        structure.tables.push({
                            rows: table.querySelectorAll('tr').length,
                            headers: table.querySelectorAll('th').length
                        });
                    });
                    
                    // Media
                    document.querySelectorAll('img, video, audio').forEach(media => {
                        structure.media.push({
                            type: media.tagName.toLowerCase(),
                            src: media.src || null,
                            alt: media.alt || null
                        });
                    });
                    
                    return structure;
                }
            ''')
            
            return structure
            
        except Exception as e:
            logger.error(f"Failed to build semantic structure: {str(e)}")
            return {}
    
    async def _check_accessibility(self, page: Page) -> List[Dict[str, str]]:
        """Check for common accessibility issues"""
        try:
            issues = await page.evaluate('''
                () => {
                    const issues = [];
                    
                    // Missing alt text on images
                    document.querySelectorAll('img').forEach(img => {
                        if (!img.alt) {
                            issues.push({
                                type: 'missing_alt_text',
                                element: img.tagName.toLowerCase(),
                                message: 'Image missing alt text',
                                selector: this._getCSSSelector(img)
                            });
                        }
                    });
                    
                    // Form fields without labels
                    document.querySelectorAll('input, textarea, select').forEach(field => {
                        if (!field.labels || field.labels.length === 0) {
                            if (!field.getAttribute('aria-label') && !field.getAttribute('aria-labelledby')) {
                                issues.push({
                                    type: 'missing_label',
                                    element: field.tagName.toLowerCase(),
                                    message: 'Form field missing label',
                                    selector: this._getCSSSelector(field)
                                });
                            }
                        }
                    });
                    
                    // Links without text
                    document.querySelectorAll('a').forEach(link => {
                        if (!link.textContent?.trim() && !link.getAttribute('aria-label')) {
                            issues.push({
                                type: 'empty_link',
                                element: 'a',
                                message: 'Link without text or aria-label',
                                selector: this._getCSSSelector(link)
                            });
                        }
                    });
                    
                    return issues;
                }
            ''')
            
            return issues
            
        except Exception as e:
            logger.error(f"Failed to check accessibility: {str(e)}")
            return []
    
    def _create_dom_element(self, data: Dict[str, Any]) -> DOMElement:
        """Create DOMElement from data dictionary"""
        return DOMElement(
            tag_name=data.get('tagName', ''),
            element_id=data.get('id'),
            classes=data.get('classes', []),
            attributes=data.get('attributes', {}),
            text_content=data.get('textContent'),
            xpath=data.get('xpath'),
            css_selector=data.get('cssSelector'),
            is_interactive=data.get('tagName', '').lower() in self.interactive_tags,
            is_form_element=data.get('tagName', '').lower() in self.form_tags,
            accessibility_info=data.get('accessibilityInfo', {}),
            children_count=data.get('childrenCount', 0),
            depth=data.get('depth', 0)
        )
    
    def get_element_summary(self, analysis_result: DOMAnalysisResult) -> Dict[str, Any]:
        """Get a summary of the DOM analysis"""
        return {
            'page_info': {
                'title': analysis_result.page_metadata.get('title'),
                'url': analysis_result.page_metadata.get('url'),
                'total_elements': analysis_result.total_elements
            },
            'interactivity': {
                'interactive_elements': len(analysis_result.interactive_elements),
                'forms': len(analysis_result.forms),
                'form_fields': len(analysis_result.form_fields),
                'navigation_elements': len(analysis_result.navigation_elements)
            },
            'structure': {
                'headings': len(analysis_result.semantic_structure.get('headings', [])),
                'landmarks': len(analysis_result.semantic_structure.get('landmarks', [])),
                'lists': len(analysis_result.semantic_structure.get('lists', [])),
                'tables': len(analysis_result.semantic_structure.get('tables', []))
            },
            'accessibility': {
                'issues_found': len(analysis_result.accessibility_issues),
                'issue_types': list(set(issue['type'] for issue in analysis_result.accessibility_issues))
            }
        }
