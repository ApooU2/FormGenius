"""
Element Detector for FormGenius

This module provides intelligent element detection and categorization:
- Interactive element identification
- Form element analysis
- Button and link detection
- Input field categorization
- Dynamic content detection
- Element state analysis
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from playwright.sync_api import Page, ElementHandle, Locator
import re
import time

logger = logging.getLogger(__name__)

@dataclass
class DetectedElement:
    """Represents a detected web element with metadata"""
    element_id: str
    tag_name: str
    element_type: str
    selector: str
    xpath: Optional[str] = None
    text_content: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    is_visible: bool = True
    is_enabled: bool = True
    is_required: bool = False
    bounding_box: Optional[Dict[str, float]] = None
    validation_rules: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FormElementGroup:
    """Represents a group of related form elements"""
    group_id: str
    group_type: str  # 'form', 'fieldset', 'address', 'payment', 'personal_info'
    elements: List[DetectedElement] = field(default_factory=list)
    container_selector: Optional[str] = None
    validation_dependencies: List[str] = field(default_factory=list)
    completion_order: List[str] = field(default_factory=list)

@dataclass
class ElementDetectionResult:
    """Complete element detection results"""
    all_elements: List[DetectedElement]
    interactive_elements: List[DetectedElement]
    form_elements: List[DetectedElement]
    button_elements: List[DetectedElement]
    input_elements: List[DetectedElement]
    link_elements: List[DetectedElement]
    element_groups: List[FormElementGroup]
    dynamic_elements: List[DetectedElement]
    validation_elements: List[DetectedElement]
    accessibility_elements: List[DetectedElement]

class ElementDetector:
    """Advanced element detector with intelligent categorization"""
    
    def __init__(self):
        self.element_types = {
            'input': ['input', 'textarea'],
            'button': ['button', 'input[type="submit"]', 'input[type="button"]'],
            'link': ['a'],
            'select': ['select'],
            'form': ['form'],
            'interactive': ['button', 'a', 'input', 'textarea', 'select', 'details', 'summary']
        }
        
        self.input_field_patterns = {
            'email': ['email', 'e-mail', 'mail'],
            'password': ['password', 'pass', 'pwd'],
            'name': ['name', 'firstname', 'lastname', 'fullname'],
            'phone': ['phone', 'tel', 'mobile', 'number'],
            'address': ['address', 'street', 'city', 'state', 'zip', 'postal'],
            'date': ['date', 'birth', 'dob'],
            'number': ['number', 'amount', 'quantity', 'price'],
            'search': ['search', 'query', 'find'],
            'url': ['url', 'website', 'link'],
            'file': ['file', 'upload', 'attachment']
        }
        
        self.validation_patterns = {
            'required': r'required|mandatory|\*',
            'email': r'email|@|mail',
            'phone': r'phone|tel|\+?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            'url': r'url|http|www',
            'number': r'number|\d+',
            'date': r'date|\d{2}[\/\-]\d{2}[\/\-]\d{4}'
        }
    
    async def detect_elements(self, page: Page) -> ElementDetectionResult:
        """Perform comprehensive element detection on a page"""
        try:
            logger.info("Starting element detection")
            
            # Detect all elements
            all_elements = await self._detect_all_elements(page)
            
            # Categorize elements
            interactive_elements = await self._detect_interactive_elements(page)
            form_elements = await self._detect_form_elements(page)
            button_elements = await self._detect_button_elements(page)
            input_elements = await self._detect_input_elements(page)
            link_elements = await self._detect_link_elements(page)
            
            # Group related elements
            element_groups = await self._group_form_elements(page, form_elements)
            
            # Detect dynamic elements
            dynamic_elements = await self._detect_dynamic_elements(page)
            
            # Detect validation elements
            validation_elements = await self._detect_validation_elements(page)
            
            # Detect accessibility elements
            accessibility_elements = await self._detect_accessibility_elements(page)
            
            result = ElementDetectionResult(
                all_elements=all_elements,
                interactive_elements=interactive_elements,
                form_elements=form_elements,
                button_elements=button_elements,
                input_elements=input_elements,
                link_elements=link_elements,
                element_groups=element_groups,
                dynamic_elements=dynamic_elements,
                validation_elements=validation_elements,
                accessibility_elements=accessibility_elements
            )
            
            logger.info(f"Element detection complete: {len(all_elements)} total elements")
            return result
            
        except Exception as e:
            logger.error(f"Element detection failed: {str(e)}")
            raise
    
    async def _detect_all_elements(self, page: Page) -> List[DetectedElement]:
        """Detect all elements on the page"""
        try:
            elements_data = await page.evaluate('''
                () => {
                    const elements = document.querySelectorAll('*');
                    const results = [];
                    
                    elements.forEach((element, index) => {
                        const rect = element.getBoundingClientRect();
                        const isVisible = rect.width > 0 && rect.height > 0 && 
                                         window.getComputedStyle(element).display !== 'none' &&
                                         window.getComputedStyle(element).visibility !== 'hidden';
                        
                        if (isVisible || ['input', 'button', 'a', 'form'].includes(element.tagName.toLowerCase())) {
                            results.push({
                                elementId: element.id || `element-${index}`,
                                tagName: element.tagName.toLowerCase(),
                                selector: this._getCSSSelector(element),
                                xpath: this._getXPath(element),
                                textContent: element.textContent?.trim()?.substring(0, 200) || null,
                                attributes: Object.fromEntries(
                                    Array.from(element.attributes).map(attr => [attr.name, attr.value])
                                ),
                                isVisible: isVisible,
                                isEnabled: !element.disabled,
                                boundingBox: {
                                    x: rect.x,
                                    y: rect.y,
                                    width: rect.width,
                                    height: rect.height
                                }
                            });
                        }
                    });
                    
                    return results;
                }
            ''')
            
            elements = []
            for data in elements_data:
                element = self._create_detected_element(data)
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect all elements: {str(e)}")
            return []
    
    async def _detect_interactive_elements(self, page: Page) -> List[DetectedElement]:
        """Detect interactive elements"""
        try:
            interactive_data = await page.evaluate('''
                () => {
                    const interactiveSelectors = [
                        'button', 'a[href]', 'input', 'textarea', 'select',
                        '[onclick]', '[tabindex]', '[role="button"]',
                        'details', 'summary', '[contenteditable]'
                    ];
                    
                    const elements = new Set();
                    interactiveSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => elements.add(el));
                    });
                    
                    return Array.from(elements).map((element, index) => {
                        const rect = element.getBoundingClientRect();
                        return {
                            elementId: element.id || `interactive-${index}`,
                            tagName: element.tagName.toLowerCase(),
                            selector: this._getCSSSelector(element),
                            textContent: element.textContent?.trim()?.substring(0, 100) || null,
                            attributes: Object.fromEntries(
                                Array.from(element.attributes).map(attr => [attr.name, attr.value])
                            ),
                            isVisible: rect.width > 0 && rect.height > 0,
                            isEnabled: !element.disabled,
                            suggestedActions: this._getSuggestedActions(element),
                            context: {
                                hasClickHandler: !!element.onclick || element.hasAttribute('onclick'),
                                isFormControl: ['input', 'textarea', 'select', 'button'].includes(element.tagName.toLowerCase()),
                                role: element.getAttribute('role')
                            }
                        };
                    });
                }
            ''')
            
            elements = []
            for data in interactive_data:
                element = self._create_detected_element(data)
                element.element_type = 'interactive'
                element.suggested_actions = data.get('suggestedActions', [])
                element.context = data.get('context', {})
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect interactive elements: {str(e)}")
            return []
    
    async def _detect_form_elements(self, page: Page) -> List[DetectedElement]:
        """Detect form-related elements"""
        try:
            form_data = await page.evaluate('''
                () => {
                    const formElements = document.querySelectorAll(
                        'form, input, textarea, select, button[type="submit"], fieldset, legend, label'
                    );
                    
                    return Array.from(formElements).map((element, index) => {
                        const rect = element.getBoundingClientRect();
                        const label = this._getElementLabel(element);
                        
                        return {
                            elementId: element.id || element.name || `form-element-${index}`,
                            tagName: element.tagName.toLowerCase(),
                            selector: this._getCSSSelector(element),
                            textContent: element.textContent?.trim()?.substring(0, 100) || null,
                            attributes: Object.fromEntries(
                                Array.from(element.attributes).map(attr => [attr.name, attr.value])
                            ),
                            isVisible: rect.width > 0 && rect.height > 0,
                            isEnabled: !element.disabled,
                            isRequired: element.required || element.hasAttribute('required'),
                            validationRules: this._getValidationRules(element),
                            context: {
                                label: label,
                                placeholder: element.placeholder,
                                formOwner: element.form ? this._getCSSSelector(element.form) : null,
                                fieldType: this._getFieldType(element)
                            }
                        };
                    });
                }
            ''')
            
            elements = []
            for data in form_data:
                element = self._create_detected_element(data)
                element.element_type = 'form'
                element.is_required = data.get('isRequired', False)
                element.validation_rules = data.get('validationRules', [])
                element.context = data.get('context', {})
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect form elements: {str(e)}")
            return []
    
    async def _detect_button_elements(self, page: Page) -> List[DetectedElement]:
        """Detect button elements"""
        try:
            button_data = await page.evaluate('''
                () => {
                    const buttons = document.querySelectorAll(
                        'button, input[type="submit"], input[type="button"], input[type="reset"], [role="button"]'
                    );
                    
                    return Array.from(buttons).map((button, index) => {
                        const rect = button.getBoundingClientRect();
                        return {
                            elementId: button.id || `button-${index}`,
                            tagName: button.tagName.toLowerCase(),
                            selector: this._getCSSSelector(button),
                            textContent: button.textContent?.trim() || button.value || null,
                            attributes: Object.fromEntries(
                                Array.from(button.attributes).map(attr => [attr.name, attr.value])
                            ),
                            isVisible: rect.width > 0 && rect.height > 0,
                            isEnabled: !button.disabled,
                            context: {
                                buttonType: button.type || 'button',
                                isPrimary: this._isPrimaryButton(button),
                                isDestructive: this._isDestructiveButton(button),
                                formOwner: button.form ? this._getCSSSelector(button.form) : null
                            }
                        };
                    });
                }
            ''')
            
            elements = []
            for data in button_data:
                element = self._create_detected_element(data)
                element.element_type = 'button'
                element.suggested_actions = ['click']
                element.context = data.get('context', {})
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect button elements: {str(e)}")
            return []
    
    async def _detect_input_elements(self, page: Page) -> List[DetectedElement]:
        """Detect input elements with field type classification"""
        try:
            input_data = await page.evaluate('''
                () => {
                    const inputs = document.querySelectorAll('input, textarea');
                    
                    return Array.from(inputs).map((input, index) => {
                        const rect = input.getBoundingClientRect();
                        const label = this._getElementLabel(input);
                        
                        return {
                            elementId: input.id || input.name || `input-${index}`,
                            tagName: input.tagName.toLowerCase(),
                            selector: this._getCSSSelector(input),
                            attributes: Object.fromEntries(
                                Array.from(input.attributes).map(attr => [attr.name, attr.value])
                            ),
                            isVisible: rect.width > 0 && rect.height > 0,
                            isEnabled: !input.disabled,
                            isRequired: input.required,
                            context: {
                                inputType: input.type || 'text',
                                label: label,
                                placeholder: input.placeholder,
                                value: input.value,
                                pattern: input.pattern,
                                minLength: input.minLength,
                                maxLength: input.maxLength,
                                min: input.min,
                                max: input.max,
                                step: input.step,
                                autocomplete: input.autocomplete,
                                fieldCategory: this._categorizeInputField(input)
                            }
                        };
                    });
                }
            ''')
            
            elements = []
            for data in input_data:
                element = self._create_detected_element(data)
                element.element_type = 'input'
                element.is_required = data.get('isRequired', False)
                element.suggested_actions = ['fill', 'clear']
                element.context = data.get('context', {})
                
                # Add validation rules based on input type
                element.validation_rules = self._generate_validation_rules(element.context)
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect input elements: {str(e)}")
            return []
    
    async def _detect_link_elements(self, page: Page) -> List[DetectedElement]:
        """Detect link elements"""
        try:
            link_data = await page.evaluate('''
                () => {
                    const links = document.querySelectorAll('a[href]');
                    
                    return Array.from(links).map((link, index) => {
                        const rect = link.getBoundingClientRect();
                        return {
                            elementId: link.id || `link-${index}`,
                            tagName: 'a',
                            selector: this._getCSSSelector(link),
                            textContent: link.textContent?.trim() || null,
                            attributes: Object.fromEntries(
                                Array.from(link.attributes).map(attr => [attr.name, attr.value])
                            ),
                            isVisible: rect.width > 0 && rect.height > 0,
                            context: {
                                href: link.href,
                                target: link.target,
                                isExternal: link.hostname !== window.location.hostname,
                                isDownload: link.hasAttribute('download'),
                                linkType: this._getLinkType(link)
                            }
                        };
                    });
                }
            ''')
            
            elements = []
            for data in link_data:
                element = self._create_detected_element(data)
                element.element_type = 'link'
                element.suggested_actions = ['click']
                element.context = data.get('context', {})
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect link elements: {str(e)}")
            return []
    
    async def _group_form_elements(self, page: Page, form_elements: List[DetectedElement]) -> List[FormElementGroup]:
        """Group related form elements"""
        try:
            groups_data = await page.evaluate('''
                () => {
                    const groups = [];
                    
                    // Group by forms
                    document.querySelectorAll('form').forEach((form, index) => {
                        const formElements = Array.from(form.querySelectorAll('input, textarea, select, button'));
                        if (formElements.length > 0) {
                            groups.push({
                                groupId: form.id || `form-group-${index}`,
                                groupType: 'form',
                                containerSelector: this._getCSSSelector(form),
                                elements: formElements.map(el => this._getCSSSelector(el))
                            });
                        }
                    });
                    
                    // Group by fieldsets
                    document.querySelectorAll('fieldset').forEach((fieldset, index) => {
                        const fieldsetElements = Array.from(fieldset.querySelectorAll('input, textarea, select'));
                        if (fieldsetElements.length > 0) {
                            const legend = fieldset.querySelector('legend');
                            groups.push({
                                groupId: fieldset.id || `fieldset-group-${index}`,
                                groupType: legend ? legend.textContent?.trim()?.toLowerCase() || 'fieldset' : 'fieldset',
                                containerSelector: this._getCSSSelector(fieldset),
                                elements: fieldsetElements.map(el => this._getCSSSelector(el))
                            });
                        }
                    });
                    
                    return groups;
                }
            ''')
            
            groups = []
            for group_data in groups_data:
                # Find matching elements
                group_elements = []
                for selector in group_data.get('elements', []):
                    for element in form_elements:
                        if element.selector == selector:
                            group_elements.append(element)
                            break
                
                if group_elements:
                    group = FormElementGroup(
                        group_id=group_data['groupId'],
                        group_type=group_data['groupType'],
                        container_selector=group_data['containerSelector'],
                        elements=group_elements,
                        completion_order=[el.element_id for el in group_elements]
                    )
                    groups.append(group)
            
            return groups
            
        except Exception as e:
            logger.error(f"Failed to group form elements: {str(e)}")
            return []
    
    async def _detect_dynamic_elements(self, page: Page) -> List[DetectedElement]:
        """Detect elements that might change dynamically"""
        try:
            dynamic_data = await page.evaluate('''
                () => {
                    const dynamicSelectors = [
                        '[data-testid]', '[data-cy]', '[data-qa]',
                        '.loading', '.spinner', '.progress',
                        '[role="alert"]', '[role="status"]',
                        '.modal', '.popup', '.tooltip',
                        '[aria-live]', '[aria-expanded]'
                    ];
                    
                    const elements = new Set();
                    dynamicSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => elements.add(el));
                    });
                    
                    return Array.from(elements).map((element, index) => ({
                        elementId: element.id || `dynamic-${index}`,
                        tagName: element.tagName.toLowerCase(),
                        selector: this._getCSSSelector(element),
                        textContent: element.textContent?.trim()?.substring(0, 100) || null,
                        attributes: Object.fromEntries(
                            Array.from(element.attributes).map(attr => [attr.name, attr.value])
                        ),
                        context: {
                            isDynamic: true,
                            hasTestId: !!(element.getAttribute('data-testid') || 
                                        element.getAttribute('data-cy') || 
                                        element.getAttribute('data-qa')),
                            ariaLive: element.getAttribute('aria-live'),
                            role: element.getAttribute('role')
                        }
                    }));
                }
            ''')
            
            elements = []
            for data in dynamic_data:
                element = self._create_detected_element(data)
                element.element_type = 'dynamic'
                element.context = data.get('context', {})
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect dynamic elements: {str(e)}")
            return []
    
    async def _detect_validation_elements(self, page: Page) -> List[DetectedElement]:
        """Detect validation-related elements"""
        try:
            validation_data = await page.evaluate('''
                () => {
                    const validationSelectors = [
                        '.error', '.invalid', '.validation-error',
                        '[role="alert"]', '.alert-danger',
                        '.help-text', '.field-help', '.hint'
                    ];
                    
                    const elements = new Set();
                    validationSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => elements.add(el));
                    });
                    
                    return Array.from(elements).map((element, index) => ({
                        elementId: element.id || `validation-${index}`,
                        tagName: element.tagName.toLowerCase(),
                        selector: this._getCSSSelector(element),
                        textContent: element.textContent?.trim() || null,
                        attributes: Object.fromEntries(
                            Array.from(element.attributes).map(attr => [attr.name, attr.value])
                        ),
                        context: {
                            validationType: this._getValidationType(element),
                            isVisible: window.getComputedStyle(element).display !== 'none'
                        }
                    }));
                }
            ''')
            
            elements = []
            for data in validation_data:
                element = self._create_detected_element(data)
                element.element_type = 'validation'
                element.context = data.get('context', {})
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect validation elements: {str(e)}")
            return []
    
    async def _detect_accessibility_elements(self, page: Page) -> List[DetectedElement]:
        """Detect accessibility-related elements"""
        try:
            a11y_data = await page.evaluate('''
                () => {
                    const a11ySelectors = [
                        '[aria-label]', '[aria-labelledby]', '[aria-describedby]',
                        '[role]', '[tabindex]', 'label'
                    ];
                    
                    const elements = new Set();
                    a11ySelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => elements.add(el));
                    });
                    
                    return Array.from(elements).map((element, index) => ({
                        elementId: element.id || `a11y-${index}`,
                        tagName: element.tagName.toLowerCase(),
                        selector: this._getCSSSelector(element),
                        textContent: element.textContent?.trim()?.substring(0, 100) || null,
                        attributes: Object.fromEntries(
                            Array.from(element.attributes).map(attr => [attr.name, attr.value])
                        ),
                        context: {
                            ariaLabel: element.getAttribute('aria-label'),
                            ariaLabelledBy: element.getAttribute('aria-labelledby'),
                            ariaDescribedBy: element.getAttribute('aria-describedby'),
                            role: element.getAttribute('role'),
                            tabIndex: element.getAttribute('tabindex')
                        }
                    }));
                }
            ''')
            
            elements = []
            for data in a11y_data:
                element = self._create_detected_element(data)
                element.element_type = 'accessibility'
                element.context = data.get('context', {})
                elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Failed to detect accessibility elements: {str(e)}")
            return []
    
    def _create_detected_element(self, data: Dict[str, Any]) -> DetectedElement:
        """Create DetectedElement from data dictionary"""
        return DetectedElement(
            element_id=data.get('elementId', ''),
            tag_name=data.get('tagName', ''),
            element_type=data.get('elementType', 'unknown'),
            selector=data.get('selector', ''),
            xpath=data.get('xpath'),
            text_content=data.get('textContent'),
            attributes=data.get('attributes', {}),
            is_visible=data.get('isVisible', True),
            is_enabled=data.get('isEnabled', True),
            is_required=data.get('isRequired', False),
            bounding_box=data.get('boundingBox'),
            validation_rules=data.get('validationRules', []),
            suggested_actions=data.get('suggestedActions', []),
            context=data.get('context', {})
        )
    
    def _generate_validation_rules(self, context: Dict[str, Any]) -> List[str]:
        """Generate validation rules based on element context"""
        rules = []
        
        input_type = context.get('inputType', '').lower()
        pattern = context.get('pattern')
        min_length = context.get('minLength')
        max_length = context.get('maxLength')
        
        if input_type == 'email':
            rules.append('valid_email_format')
        elif input_type == 'url':
            rules.append('valid_url_format')
        elif input_type == 'tel':
            rules.append('valid_phone_format')
        elif input_type == 'number':
            rules.append('numeric_input_only')
        
        if pattern:
            rules.append(f'matches_pattern: {pattern}')
        
        if min_length:
            rules.append(f'min_length: {min_length}')
        
        if max_length:
            rules.append(f'max_length: {max_length}')
        
        return rules
    
    def get_detection_summary(self, result: ElementDetectionResult) -> Dict[str, Any]:
        """Get a summary of element detection results"""
        return {
            'totals': {
                'all_elements': len(result.all_elements),
                'interactive_elements': len(result.interactive_elements),
                'form_elements': len(result.form_elements),
                'button_elements': len(result.button_elements),
                'input_elements': len(result.input_elements),
                'link_elements': len(result.link_elements)
            },
            'groups': {
                'element_groups': len(result.element_groups),
                'form_groups': len([g for g in result.element_groups if g.group_type == 'form'])
            },
            'specialized': {
                'dynamic_elements': len(result.dynamic_elements),
                'validation_elements': len(result.validation_elements),
                'accessibility_elements': len(result.accessibility_elements)
            },
            'input_types': self._get_input_type_distribution(result.input_elements),
            'button_types': self._get_button_type_distribution(result.button_elements)
        }
    
    def _get_input_type_distribution(self, input_elements: List[DetectedElement]) -> Dict[str, int]:
        """Get distribution of input types"""
        distribution = {}
        for element in input_elements:
            input_type = element.context.get('inputType', 'text')
            distribution[input_type] = distribution.get(input_type, 0) + 1
        return distribution
    
    def _get_button_type_distribution(self, button_elements: List[DetectedElement]) -> Dict[str, int]:
        """Get distribution of button types"""
        distribution = {}
        for element in button_elements:
            button_type = element.context.get('buttonType', 'button')
            distribution[button_type] = distribution.get(button_type, 0) + 1
        return distribution
