"""
Data Generator - AI-powered test data generation

This module generates realistic and contextually appropriate test data
for form fields using AI and various data generation strategies.
"""

import logging
import random
import string
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from faker import Faker

logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Intelligent data generator that creates realistic test data for forms.
    """
    
    def __init__(self, config):
        self.config = config
        self.fake = Faker()
        
        # Data generation strategies
        self.field_strategies = {
            'email': self._generate_email,
            'password': self._generate_password,
            'text': self._generate_text,
            'name': self._generate_name,
            'phone': self._generate_phone,
            'date': self._generate_date,
            'number': self._generate_number,
            'select': self._generate_select_value,
            'checkbox': self._generate_checkbox_value,
            'radio': self._generate_radio_value,
            'textarea': self._generate_textarea,
            'url': self._generate_url,
            'file': self._generate_file_path
        }
    
    async def generate_form_data(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete test data for a form.
        
        Args:
            form: Form structure from FormDetector
            
        Returns:
            Dictionary mapping field names to generated values
        """
        logger.info(f"Generating test data for form with {len(form.get('fields', []))} fields")
        
        form_data = {}
        
        for field in form.get('fields', []):
            field_name = field.get('name') or field.get('id')
            if not field_name:
                continue
            
            # Generate value based on field type and context
            value = await self._generate_field_value(field)
            if value is not None:
                form_data[field_name] = value
        
        return form_data
    
    async def generate_power_apps_data(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate test data specifically for Power Apps forms.
        
        Args:
            form: Power Apps form structure
            
        Returns:
            Dictionary mapping field names to generated values
        """
        logger.info("Generating Power Apps test data")
        
        # Use the same logic as regular forms but with Power Apps specific handling
        return await self.generate_form_data(form)
    
    async def generate_invalid_data(self, form: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """
        Generate invalid test data for validation testing.
        
        Args:
            form: Form structure
            scenario: Type of invalid data to generate
            
        Returns:
            Dictionary with invalid test data
        """
        logger.info(f"Generating invalid test data for scenario: {scenario}")
        
        invalid_data = {}
        
        for field in form.get('fields', []):
            field_name = field.get('name') or field.get('id')
            if not field_name:
                continue
            
            # Generate invalid value based on scenario
            invalid_value = await self._generate_invalid_field_value(field, scenario)
            if invalid_value is not None:
                invalid_data[field_name] = invalid_value
        
        return invalid_data
    
    async def _generate_field_value(self, field: Dict[str, Any]) -> Any:
        """Generate a value for a specific field."""
        field_type = field.get('type', 'text').lower()
        field_label = field.get('label', '').lower()
        field_name = field.get('name', '').lower()
        
        # Determine the most appropriate data type based on field info
        data_type = self._determine_data_type(field_type, field_label, field_name)
        
        # Get the generation strategy
        strategy = self.field_strategies.get(data_type, self.field_strategies['text'])
        
        # Generate the value
        try:
            return await strategy(field)
        except Exception as e:
            logger.error(f"Error generating value for field {field_name}: {e}")
            return None
    
    def _determine_data_type(self, field_type: str, field_label: str, field_name: str) -> str:
        """Determine the appropriate data type for a field."""
        # Check field type first
        if field_type in ['email']:
            return 'email'
        elif field_type in ['password']:
            return 'password'
        elif field_type in ['tel', 'phone']:
            return 'phone'
        elif field_type in ['date', 'datetime-local']:
            return 'date'
        elif field_type in ['number', 'range']:
            return 'number'
        elif field_type in ['url']:
            return 'url'
        elif field_type in ['file']:
            return 'file'
        elif field_type in ['select', 'select-one']:
            return 'select'
        elif field_type in ['checkbox']:
            return 'checkbox'
        elif field_type in ['radio']:
            return 'radio'
        elif field_type in ['textarea']:
            return 'textarea'
        
        # Check field label and name for context
        combined_text = f"{field_label} {field_name}".lower()
        
        if any(keyword in combined_text for keyword in ['email', 'e-mail']):
            return 'email'
        elif any(keyword in combined_text for keyword in ['password', 'pwd']):
            return 'password'
        elif any(keyword in combined_text for keyword in ['phone', 'tel', 'mobile']):
            return 'phone'
        elif any(keyword in combined_text for keyword in ['name', 'first', 'last', 'full']):
            return 'name'
        elif any(keyword in combined_text for keyword in ['date', 'birth', 'dob']):
            return 'date'
        elif any(keyword in combined_text for keyword in ['age', 'year', 'number', 'amount']):
            return 'number'
        elif any(keyword in combined_text for keyword in ['website', 'url', 'link']):
            return 'url'
        elif any(keyword in combined_text for keyword in ['message', 'comment', 'description']):
            return 'textarea'
        
        return 'text'
    
    async def _generate_email(self, field: Dict[str, Any]) -> str:
        """Generate a realistic email address."""
        return self.fake.email()
    
    async def _generate_password(self, field: Dict[str, Any]) -> str:
        """Generate a password meeting common requirements."""
        # Check for any constraints
        constraints = field.get('constraints', {})
        min_length = constraints.get('minlength', 8)
        max_length = constraints.get('maxlength', 20)
        
        # Generate password with mix of characters
        length = random.randint(max(min_length, 8), min(max_length, 20))
        
        password = (
            ''.join(random.choices(string.ascii_uppercase, k=2)) +
            ''.join(random.choices(string.ascii_lowercase, k=length-6)) +
            ''.join(random.choices(string.digits, k=2)) +
            ''.join(random.choices('!@#$%^&*', k=2))
        )
        
        # Shuffle the password
        password_list = list(password)
        random.shuffle(password_list)
        return ''.join(password_list)
    
    async def _generate_name(self, field: Dict[str, Any]) -> str:
        """Generate a realistic name."""
        field_label = field.get('label', '').lower()
        
        if 'first' in field_label:
            return self.fake.first_name()
        elif 'last' in field_label:
            return self.fake.last_name()
        else:
            return self.fake.name()
    
    async def _generate_phone(self, field: Dict[str, Any]) -> str:
        """Generate a realistic phone number."""
        return self.fake.phone_number()
    
    async def _generate_date(self, field: Dict[str, Any]) -> str:
        """Generate a realistic date."""
        field_label = field.get('label', '').lower()
        
        if any(keyword in field_label for keyword in ['birth', 'dob']):
            # Generate birth date (18-80 years ago)
            start_date = datetime.now() - timedelta(days=80*365)
            end_date = datetime.now() - timedelta(days=18*365)
            fake_date = self.fake.date_between(start_date=start_date, end_date=end_date)
        else:
            # Generate recent date
            fake_date = self.fake.date_between(start_date='-1y', end_date='today')
        
        return fake_date.strftime('%Y-%m-%d')
    
    async def _generate_number(self, field: Dict[str, Any]) -> str:
        """Generate a realistic number."""
        constraints = field.get('constraints', {})
        min_val = int(constraints.get('min', 1))
        max_val = int(constraints.get('max', 100))
        
        return str(random.randint(min_val, max_val))
    
    async def _generate_text(self, field: Dict[str, Any]) -> str:
        """Generate realistic text content."""
        constraints = field.get('constraints', {})
        max_length = constraints.get('maxlength', 50)
        
        field_label = field.get('label', '').lower()
        
        if any(keyword in field_label for keyword in ['company', 'organization']):
            text = self.fake.company()
        elif any(keyword in field_label for keyword in ['address', 'street']):
            text = self.fake.address()
        elif any(keyword in field_label for keyword in ['city']):
            text = self.fake.city()
        elif any(keyword in field_label for keyword in ['country']):
            text = self.fake.country()
        elif any(keyword in field_label for keyword in ['title', 'subject']):
            text = self.fake.sentence(nb_words=3)
        else:
            text = self.fake.word()
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + '...'
        
        return text
    
    async def _generate_textarea(self, field: Dict[str, Any]) -> str:
        """Generate text for textarea fields."""
        return self.fake.paragraph(nb_sentences=3)
    
    async def _generate_url(self, field: Dict[str, Any]) -> str:
        """Generate a realistic URL."""
        return self.fake.url()
    
    async def _generate_file_path(self, field: Dict[str, Any]) -> str:
        """Generate a file path for file upload fields."""
        # For testing purposes, we'll return a placeholder
        return "test_file.txt"
    
    async def _generate_select_value(self, field: Dict[str, Any]) -> str:
        """Generate a value for select fields with smart option selection."""
        options = field.get('options', [])
        field_label = field.get('label', '').lower()
        field_name = field.get('name', '').lower()
        
        if not options:
            logger.warning(f"No options found for select field: {field_name}")
            return ""
        
        # Filter out empty/placeholder options
        valid_options = []
        placeholder_keywords = ['select', 'choose', 'pick', 'please', '---', '--']
        
        for opt in options:
            opt_value = opt.get('value', '').strip()
            opt_text = opt.get('text', '').strip().lower()
            
            # Skip empty values or placeholder options
            if not opt_value or any(keyword in opt_text for keyword in placeholder_keywords):
                continue
                
            valid_options.append(opt)
        
        if not valid_options:
            logger.warning(f"No valid options found for select field: {field_name}")
            return ""
        
        # Smart selection based on field context
        selected_option = self._smart_option_selection(valid_options, field_label, field_name)
        return selected_option.get('value', '')
    
    def _smart_option_selection(self, options: List[Dict], field_label: str, field_name: str) -> Dict:
        """Intelligently select an option based on field context."""
        field_context = f"{field_label} {field_name}".lower()
        
        # Priority matching for common field types
        if any(keyword in field_context for keyword in ['country']):
            # Prefer common countries
            preferred = ['us', 'usa', 'united states', 'uk', 'canada', 'australia']
            for opt in options:
                opt_text = opt.get('text', '').lower()
                if any(country in opt_text for country in preferred):
                    return opt
        
        elif any(keyword in field_context for keyword in ['state', 'province']):
            # Prefer common states
            preferred = ['california', 'new york', 'texas', 'florida', 'ontario', 'quebec']
            for opt in options:
                opt_text = opt.get('text', '').lower()
                if any(state in opt_text for state in preferred):
                    return opt
        
        elif any(keyword in field_context for keyword in ['title', 'prefix']):
            # Prefer common titles
            preferred = ['mr', 'ms', 'mrs', 'dr']
            for opt in options:
                opt_text = opt.get('text', '').lower()
                if any(title in opt_text for title in preferred):
                    return opt
        
        elif any(keyword in field_context for keyword in ['gender', 'sex']):
            # Prefer male/female over other options
            preferred = ['male', 'female', 'm', 'f']
            for opt in options:
                opt_text = opt.get('text', '').lower()
                if any(gender in opt_text for gender in preferred):
                    return opt
        
        elif any(keyword in field_context for keyword in ['age', 'year']):
            # Prefer reasonable age ranges
            for opt in options:
                opt_text = opt.get('text', '').lower()
                if any(age in opt_text for age in ['25-34', '30-39', '35-44', 'adult']):
                    return opt
        
        # Default: select a random option (avoid first/last as they might be placeholders)
        if len(options) > 2:
            return random.choice(options[1:-1])
        else:
            return random.choice(options)
    
    async def _generate_checkbox_value(self, field: Dict[str, Any]) -> bool:
        """Generate a value for checkbox fields with context awareness."""
        field_label = field.get('label', '').lower()
        field_name = field.get('name', '').lower()
        field_context = f"{field_label} {field_name}".lower()
        
        # Context-based checkbox selection
        if any(keyword in field_context for keyword in ['agree', 'accept', 'terms', 'privacy', 'policy']):
            # Usually check agreement checkboxes
            return True
        elif any(keyword in field_context for keyword in ['newsletter', 'email', 'marketing', 'promotional']):
            # Randomly decide on marketing/newsletter checkboxes
            return random.choice([True, False])
        elif any(keyword in field_context for keyword in ['required', 'mandatory']):
            # Always check required checkboxes
            return True
        else:
            # Random with slight bias toward checking
            return random.choice([True, True, False])
    
    async def _generate_radio_value(self, field: Dict[str, Any]) -> str:
        """Generate a value for radio button fields with smart selection."""
        field_label = field.get('label', '').lower()
        field_name = field.get('name', '').lower()
        field_context = f"{field_label} {field_name}".lower()
        
        # For radio buttons, we need to determine what options might be available
        # Since radio buttons are grouped by name, we'll generate contextually appropriate values
        
        if any(keyword in field_context for keyword in ['gender', 'sex']):
            return random.choice(['Male', 'Female', 'male', 'female', 'M', 'F'])
        elif any(keyword in field_context for keyword in ['yes', 'no', 'boolean']):
            return random.choice(['Yes', 'No', 'yes', 'no', 'Y', 'N'])
        elif any(keyword in field_context for keyword in ['rating', 'satisfaction']):
            return random.choice(['5', '4', 'Excellent', 'Good', 'Very Good'])
        elif any(keyword in field_context for keyword in ['frequency', 'often']):
            return random.choice(['Daily', 'Weekly', 'Monthly', 'Rarely'])
        elif any(keyword in field_context for keyword in ['size']):
            return random.choice(['Small', 'Medium', 'Large', 'S', 'M', 'L'])
        elif any(keyword in field_context for keyword in ['priority']):
            return random.choice(['High', 'Medium', 'Low', '1', '2', '3'])
        else:
            # Generic options that might work for many radio groups
            return random.choice(['Option1', 'Option2', 'A', 'B', '1', '2', 'Yes'])
    
    async def _generate_enhanced_data(self, field: Dict[str, Any]) -> Any:
        """Enhanced data generation with better context awareness."""
        field_type = field.get('type', 'text').lower()
        field_label = field.get('label', '').lower()
        field_name = field.get('name', '').lower()
        field_context = f"{field_label} {field_name}".lower()
        
        # Enhanced generation for specific field contexts
        if 'first' in field_context and 'name' in field_context:
            return self.fake.first_name()
        elif 'last' in field_context and 'name' in field_context:
            return self.fake.last_name()
        elif 'full' in field_context and 'name' in field_context:
            return self.fake.name()
        elif 'company' in field_context:
            return self.fake.company()
        elif 'job' in field_context or 'title' in field_context:
            return self.fake.job()
        elif 'address' in field_context:
            if 'line1' in field_context or '1' in field_context:
                return self.fake.street_address()
            elif 'line2' in field_context or '2' in field_context:
                return self.fake.secondary_address() if random.choice([True, False]) else ""
            else:
                return self.fake.address()
        elif 'city' in field_context:
            return self.fake.city()
        elif 'state' in field_context or 'province' in field_context:
            return self.fake.state()
        elif 'zip' in field_context or 'postal' in field_context:
            return self.fake.zipcode()
        elif 'country' in field_context:
            return self.fake.country()
        
        # Fall back to original generation method
        return await self._generate_field_value(field)
        return await self._generate_select_value(field)
    
    async def _generate_invalid_field_value(self, field: Dict[str, Any], scenario: str) -> Any:
        """Generate invalid data for validation testing."""
        field_type = field.get('type', 'text').lower()
        
        if scenario == 'empty_required_fields':
            if field.get('required'):
                return ''  # Empty value for required field
            else:
                return await self._generate_field_value(field)  # Valid value for non-required
        
        elif scenario == 'invalid_email':
            if field_type == 'email' or 'email' in field.get('label', '').lower():
                return 'invalid-email-format'
            else:
                return await self._generate_field_value(field)
        
        elif scenario == 'invalid_phone':
            if field_type in ['tel', 'phone'] or 'phone' in field.get('label', '').lower():
                return 'not-a-phone-number'
            else:
                return await self._generate_field_value(field)
        
        elif scenario == 'sql_injection_attempt':
            return "'; DROP TABLE users; --"
        
        elif scenario == 'xss_attempt':
            return "<script>alert('XSS')</script>"
        
        elif scenario == 'boundary_values':
            constraints = field.get('constraints', {})
            if 'maxlength' in constraints:
                # Generate text that's too long
                max_length = constraints['maxlength']
                return 'x' * (max_length + 10)
            elif field_type == 'number':
                if 'max' in constraints:
                    return str(int(constraints['max']) + 1)
                else:
                    return '999999999'
            else:
                return await self._generate_field_value(field)
        
        else:
            # Default to generating normal test data
            return await self._generate_field_value(field)
    
    # Public synchronous methods for testing and simple usage
    def generate_email(self) -> str:
        """Generate a test email address."""
        return self.fake.email()
    
    def generate_name(self) -> str:
        """Generate a test full name."""
        return self.fake.name()
    
    def generate_phone(self) -> str:
        """Generate a test phone number."""
        return self.fake.phone_number()
    
    def generate_text(self, length: int = 50) -> str:
        """Generate test text."""
        return self.fake.text(max_nb_chars=length)
    
    def generate_password(self) -> str:
        """Generate a test password."""
        return self.fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
