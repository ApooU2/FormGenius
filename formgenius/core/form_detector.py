"""
Form Detector - Intelligent form detection and analysis

This module provides advanced form detection capabilities for web pages,
including specialized handling for Power Apps and other dynamic forms.
"""

import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class FormDetector:
    """
    Intelligent form detector that can identify and analyze various types of forms.
    """
    
    def __init__(self, config):
        self.config = config
        self.form_selectors = [
            'form',
            '[data-testid*="form"]',
            '[class*="form"]',
            '[id*="form"]',
            '[role="form"]',
            '.powerapps-form',
            '.dynamics-form'
        ]
    
    async def detect_forms(self, page) -> List[Dict[str, Any]]:
        """
        Detect all forms on the current page.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected forms with their metadata
        """
        logger.info("Starting form detection on page")
        
        forms = []
        
        try:
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all form elements
            form_elements = soup.find_all('form')
            
            # Also look for dynamic forms (like Power Apps)
            dynamic_forms = self._detect_dynamic_forms(soup)
            
            # Process traditional forms
            for i, form_element in enumerate(form_elements):
                form_data = await self._analyze_form(form_element, page, f"form_{i}")
                if form_data:
                    forms.append(form_data)
            
            # Process dynamic forms
            for i, dynamic_form in enumerate(dynamic_forms):
                form_data = await self._analyze_dynamic_form(dynamic_form, page, f"dynamic_form_{i}")
                if form_data:
                    forms.append(form_data)
            
            logger.info(f"Detected {len(forms)} forms on the page")
            return forms
            
        except Exception as e:
            logger.error(f"Error detecting forms: {e}")
            return []
    
    def _detect_dynamic_forms(self, soup: BeautifulSoup) -> List[Any]:
        """Detect dynamic forms that don't use traditional <form> tags."""
        dynamic_forms = []
        
        # Look for Power Apps containers
        power_apps_containers = soup.find_all(['div', 'section'], {
            'class': lambda x: x and any(
                keyword in x.lower() for keyword in ['powerapps', 'powerapp', 'dynamics', 'msforms']
            )
        })
        dynamic_forms.extend(power_apps_containers)
        
        # Look for containers with form-like structure
        form_containers = soup.find_all(['div', 'section'], {
            'class': lambda x: x and any(
                keyword in x.lower() for keyword in ['form', 'input-group', 'field-group']
            )
        })
        
        # Filter containers that actually contain input fields
        for container in form_containers:
            inputs = container.find_all(['input', 'select', 'textarea', 'button'])
            if len(inputs) >= 2:  # At least 2 inputs to be considered a form
                dynamic_forms.append(container)
        
        return dynamic_forms
    
    async def _analyze_form(self, form_element, page, form_id: str) -> Optional[Dict[str, Any]]:
        """Analyze a traditional HTML form with enhanced radio group detection."""
        try:
            fields = []
            
            # Find all input fields
            input_elements = form_element.find_all(['input', 'select', 'textarea'])
            
            # Track radio groups to avoid duplicates
            processed_radio_groups = set()
            
            for input_elem in input_elements:
                field_data = self._analyze_field(input_elem)
                if field_data:
                    # Special handling for radio buttons
                    if field_data.get('type') == 'radio':
                        radio_name = field_data.get('name')
                        if radio_name and radio_name not in processed_radio_groups:
                            # Analyze the entire radio group
                            radio_group_data = self._analyze_radio_group(form_element, radio_name)
                            if radio_group_data:
                                fields.append(radio_group_data)
                                processed_radio_groups.add(radio_name)
                    else:
                        fields.append(field_data)
            
            # Find submit button
            submit_button = form_element.find(['input', 'button'], {
                'type': lambda x: x and x.lower() in ['submit', 'button']
            })
            
            if not submit_button:
                submit_button = form_element.find(['button'], string=lambda text: 
                    text and any(word in text.lower() for word in ['submit', 'send', 'save', 'continue'])
                )
            
            return {
                'id': form_id,
                'type': 'traditional',
                'action': form_element.get('action', ''),
                'method': form_element.get('method', 'get').lower(),
                'fields': fields,
                'submit_button': self._get_button_info(submit_button) if submit_button else None,
                'field_count': len(fields),
                'required_fields': len([f for f in fields if f.get('required')])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing form {form_id}: {e}")
            return None
    
    async def _analyze_dynamic_form(self, container, page, form_id: str) -> Optional[Dict[str, Any]]:
        """Analyze a dynamic form (like Power Apps)."""
        try:
            fields = []
            
            # Look for input elements within the container
            input_elements = container.find_all(['input', 'select', 'textarea'])
            
            # Also look for custom input components
            custom_inputs = container.find_all(['div', 'span'], {
                'class': lambda x: x and any(
                    keyword in x.lower() for keyword in ['input', 'field', 'control', 'textbox']
                ),
                'role': lambda x: x and x.lower() in ['textbox', 'combobox', 'listbox']
            })
            
            all_inputs = input_elements + custom_inputs
            
            for input_elem in all_inputs:
                field_data = self._analyze_field(input_elem)
                if field_data:
                    fields.append(field_data)
            
            # Find submit button
            submit_buttons = container.find_all(['button', 'div', 'span'], 
                string=lambda text: text and any(
                    word in text.lower() for word in ['submit', 'send', 'save', 'next', 'continue']
                )
            )
            
            submit_button = submit_buttons[0] if submit_buttons else None
            
            return {
                'id': form_id,
                'type': 'dynamic',
                'container_class': container.get('class', []),
                'fields': fields,
                'submit_button': self._get_button_info(submit_button) if submit_button else None,
                'field_count': len(fields),
                'required_fields': len([f for f in fields if f.get('required')])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing dynamic form {form_id}: {e}")
            return None
    
    def _analyze_field(self, field_element) -> Optional[Dict[str, Any]]:
        """Analyze an individual form field."""
        try:
            field_type = field_element.get('type', field_element.name).lower()
            
            # Skip hidden and submit fields
            if field_type in ['hidden', 'submit', 'button']:
                return None
            
            # Get field identifier
            field_id = field_element.get('id')
            field_name = field_element.get('name')
            field_label = self._get_field_label(field_element)
            
            # Determine field properties
            is_required = bool(field_element.get('required')) or 'required' in str(field_element.get('class', []))
            placeholder = field_element.get('placeholder', '')
            
            # Get field constraints
            constraints = {}
            if field_element.get('minlength'):
                constraints['minlength'] = int(field_element.get('minlength'))
            if field_element.get('maxlength'):
                constraints['maxlength'] = int(field_element.get('maxlength'))
            if field_element.get('min'):
                constraints['min'] = field_element.get('min')
            if field_element.get('max'):
                constraints['max'] = field_element.get('max')
            if field_element.get('pattern'):
                constraints['pattern'] = field_element.get('pattern')
            
            # Get options for select fields
            options = []
            if field_element.name == 'select':
                option_elements = field_element.find_all('option')
                options = [{'value': opt.get('value', ''), 'text': opt.get_text().strip()} 
                          for opt in option_elements if opt.get('value')]
            
            return {
                'id': field_id,
                'name': field_name,
                'type': field_type,
                'label': field_label,
                'required': is_required,
                'placeholder': placeholder,
                'constraints': constraints,
                'options': options,
                'selector': self._get_field_selector(field_element)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing field: {e}")
            return None
    
    def _get_field_label(self, field_element) -> str:
        """Get the label for a form field."""
        # Try to find associated label
        field_id = field_element.get('id')
        if field_id:
            # Look for label with 'for' attribute
            parent = field_element.parent
            while parent:
                label = parent.find('label', {'for': field_id})
                if label:
                    return label.get_text().strip()
                parent = parent.parent
        
        # Look for nearby label
        if field_element.parent:
            # Check previous sibling
            prev_sibling = field_element.find_previous_sibling('label')
            if prev_sibling:
                return prev_sibling.get_text().strip()
            
            # Check parent for label text
            parent_text = field_element.parent.get_text().strip()
            if parent_text and len(parent_text) < 100:
                return parent_text
        
        # Use placeholder or name as fallback
        return field_element.get('placeholder', '') or field_element.get('name', '')
    
    def _get_field_selector(self, field_element) -> str:
        """Generate a CSS selector for the field."""
        if field_element.get('id'):
            return f"#{field_element['id']}"
        elif field_element.get('name'):
            return f"[name='{field_element['name']}']"
        elif field_element.get('class'):
            classes = ' '.join(field_element['class'])
            return f".{classes.replace(' ', '.')}"
        else:
            return field_element.name
    
    def _get_button_info(self, button_element) -> Dict[str, Any]:
        """Get information about a button element."""
        return {
            'text': button_element.get_text().strip(),
            'type': button_element.get('type', 'button'),
            'id': button_element.get('id'),
            'class': button_element.get('class', []),
            'selector': self._get_field_selector(button_element)
        }
    
    def _analyze_radio_groups(self, form_element) -> Dict[str, Dict[str, Any]]:
        """Analyze radio button groups and their options."""
        radio_groups = {}
        
        # Find all radio buttons in the form
        radio_buttons = form_element.find_all('input', {'type': 'radio'})
        
        for radio in radio_buttons:
            name = radio.get('name')
            if not name:
                continue
                
            if name not in radio_groups:
                radio_groups[name] = {
                    'type': 'radio',
                    'name': name,
                    'options': [],
                    'label': self._get_radio_group_label(form_element, name),
                    'required': False,
                    'selector': f"input[name='{name}']"
                }
            
            # Get option details
            option_value = radio.get('value', '')
            option_label = self._get_radio_option_label(radio)
            
            radio_groups[name]['options'].append({
                'value': option_value,
                'text': option_label,
                'selector': f"input[name='{name}'][value='{option_value}']"
            })
            
            # Check if any radio in group is required
            if radio.get('required'):
                radio_groups[name]['required'] = True
        
        return radio_groups
    
    def _get_radio_group_label(self, form_element, group_name: str) -> str:
        """Get the label for a radio button group."""
        # Look for fieldset legend
        fieldsets = form_element.find_all('fieldset')
        for fieldset in fieldsets:
            radios_in_fieldset = fieldset.find_all('input', {'name': group_name, 'type': 'radio'})
            if radios_in_fieldset:
                legend = fieldset.find('legend')
                if legend:
                    return legend.get_text().strip()
        
        # Look for common label patterns
        first_radio = form_element.find('input', {'name': group_name, 'type': 'radio'})
        if first_radio:
            # Check for label before the radio group
            parent = first_radio.parent
            while parent and parent != form_element:
                # Look for label-like elements
                for tag in ['label', 'div', 'span', 'p']:
                    label_elem = parent.find_previous_sibling(tag)
                    if label_elem:
                        text = label_elem.get_text().strip()
                        if text and len(text) < 100 and ':' in text:
                            return text.replace(':', '').strip()
                parent = parent.parent
        
        return group_name.replace('_', ' ').title()
    
    def _get_radio_option_label(self, radio_element) -> str:
        """Get the label for a specific radio option."""
        # Check for associated label
        radio_id = radio_element.get('id')
        if radio_id:
            parent = radio_element.parent
            while parent:
                label = parent.find('label', {'for': radio_id})
                if label:
                    return label.get_text().strip()
                parent = parent.parent
        
        # Check next sibling for text
        next_sibling = radio_element.next_sibling
        if next_sibling and hasattr(next_sibling, 'strip'):
            text = next_sibling.strip()
            if text:
                return text
        
        # Check parent for text content
        if radio_element.parent:
            parent_text = radio_element.parent.get_text().strip()
            # Remove other radio button texts to isolate this one's label
            if parent_text and len(parent_text) < 50:
                return parent_text
        
        # Fallback to value
        return radio_element.get('value', 'Option')

    async def detect_power_apps_forms(self, page) -> List[Dict[str, Any]]:
        """
        Specialized detection for Power Apps forms.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of detected Power Apps forms
        """
        logger.info("Detecting Power Apps forms")
        
        try:
            # Wait for Power Apps to load
            await page.wait_for_timeout(3000)
            
            # Look for Power Apps specific selectors
            power_apps_selectors = [
                '[data-control-name]',
                '.appmagic-control',
                '[class*="powerapps"]',
                '[class*="powerapp"]'
            ]
            
            forms = []
            for selector in power_apps_selectors:
                elements = await page.query_selector_all(selector)
                
                for element in elements:
                    # Check if this looks like a form container
                    inner_html = await element.inner_html()
                    if 'input' in inner_html.lower() or 'textbox' in inner_html.lower():
                        form_data = await self._analyze_power_apps_form(element, page)
                        if form_data:
                            forms.append(form_data)
            
            return forms
            
        except Exception as e:
            logger.error(f"Error detecting Power Apps forms: {e}")
            return []
    
    async def _analyze_power_apps_form(self, container, page) -> Optional[Dict[str, Any]]:
        """Analyze a Power Apps form container."""
        try:
            # Get all interactive elements within the container
            interactive_elements = await container.query_selector_all(
                'input, select, textarea, [role="textbox"], [role="combobox"]'
            )
            
            fields = []
            for element in interactive_elements:
                field_info = await self._analyze_power_apps_field(element)
                if field_info:
                    fields.append(field_info)
            
            # Look for submit button
            submit_buttons = await container.query_selector_all(
                'button, [role="button"], [data-control-name*="submit"], [data-control-name*="save"]'
            )
            
            submit_button = None
            if submit_buttons:
                button_text = await submit_buttons[0].inner_text()
                submit_button = {
                    'text': button_text,
                    'element': submit_buttons[0]
                }
            
            return {
                'id': f"powerapps_form_{len(fields)}",
                'type': 'powerapps',
                'fields': fields,
                'submit_button': submit_button,
                'field_count': len(fields),
                'container': container
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Power Apps form: {e}")
            return None
    
    async def _analyze_power_apps_field(self, element) -> Optional[Dict[str, Any]]:
        """Analyze a Power Apps form field."""
        try:
            # Get field properties
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            field_type = await element.get_attribute('type') or tag_name
            
            # Get field identifiers
            control_name = await element.get_attribute('data-control-name')
            field_id = await element.get_attribute('id')
            
            # Try to get label
            label = ''
            try:
                # Look for associated label
                label_element = await element.query_selector('xpath=preceding::label[1]')
                if label_element:
                    label = await label_element.inner_text()
            except:
                pass
            
            # Check if required
            required = False
            try:
                aria_required = await element.get_attribute('aria-required')
                required = aria_required == 'true'
            except:
                pass
            
            return {
                'id': field_id or control_name,
                'name': control_name,
                'type': field_type,
                'label': label,
                'required': required,
                'element': element,
                'selector': f'[data-control-name="{control_name}"]' if control_name else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Power Apps field: {e}")
            return None
