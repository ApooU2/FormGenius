"""
AI Service - Integration with Gemini AI for intelligent data generation

This module provides AI-powered form analysis and data generation using
Google's Gemini API for contextually appropriate test data.
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AIService:
    """
    AI service for intelligent form analysis and data generation using Gemini.
    """
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self._setup_gemini()
    
    def _setup_gemini(self):
        """Initialize Gemini AI client."""
        try:
            api_key = self.config.gemini_api_key
            if not api_key:
                logger.warning("Gemini API key not found. AI features will be disabled.")
                return
            
            genai.configure(api_key=api_key)
            
            # Initialize the model with the configured model name
            model_name = getattr(self.config, 'ai_model', 'gemini-2.0-flash-exp')
            if hasattr(self.config, 'gemini_model'):
                model_name = self.config.gemini_model
            
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Gemini AI initialized with model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.model is not None
    
    async def analyze_form_context(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze form structure and context using AI to better understand field requirements.
        
        Args:
            form: Form structure from FormDetector
            
        Returns:
            AI analysis with context and suggestions
        """
        if not self.is_available():
            return {}
        
        try:
            # Prepare form context for AI analysis
            form_context = {
                'form_action': form.get('action', ''),
                'form_method': form.get('method', ''),
                'fields': []
            }
            
            for field in form.get('fields', []):
                field_info = {
                    'name': field.get('name'),
                    'type': field.get('type'),
                    'label': field.get('label'),
                    'placeholder': field.get('placeholder'),
                    'required': field.get('required', False),
                    'options': field.get('options', [])
                }
                form_context['fields'].append(field_info)
            
            prompt = f"""
Analyze this web form and provide context-aware insights for generating realistic test data:

Form Details:
{json.dumps(form_context, indent=2)}

Please provide:
1. Form purpose/type (contact form, registration, survey, etc.)
2. Field-specific data generation suggestions
3. Realistic option selections for dropdowns/radio buttons
4. Any business context that would help generate appropriate test data

Respond in JSON format with this structure:
{{
    "form_type": "string",
    "form_purpose": "string", 
    "field_suggestions": {{
        "field_name": {{
            "data_type": "string",
            "suggestions": ["suggestion1", "suggestion2"],
            "preferred_value": "string"
        }}
    }},
    "context_notes": "string"
}}
"""

            response = await self._call_gemini(prompt)
            if response:
                try:
                    # Try to parse as JSON first
                    return json.loads(response)
                except json.JSONDecodeError:
                    # If not JSON, try to extract JSON from the response
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass
                    
                    logger.warning(f"AI response was not valid JSON: {response[:200]}...")
                    # Return a basic analysis based on form structure
                    return {
                        "form_type": "contact_form",
                        "form_purpose": "user_contact",
                        "field_suggestions": {},
                        "context_notes": "Basic analysis fallback"
                    }
            
        except Exception as e:
            logger.error(f"Error analyzing form context with AI: {e}")
        
        return {}
    
    async def generate_field_value(self, field: Dict[str, Any], form_context: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate a contextually appropriate value for a specific field using AI.
        
        Args:
            field: Field information
            form_context: Optional form context from previous analysis
            
        Returns:
            Generated field value or None if AI unavailable
        """
        if not self.is_available():
            return None
        
        try:
            field_type = field.get('type', 'text')
            field_name = field.get('name', '')
            field_label = field.get('label', '')
            field_placeholder = field.get('placeholder', '')
            
            # Build context string
            context_info = ""
            if form_context:
                context_info = f"Form Type: {form_context.get('form_type', 'unknown')}\n"
                context_info += f"Form Purpose: {form_context.get('form_purpose', 'unknown')}\n"
                
                field_suggestions = form_context.get('field_suggestions', {}).get(field_name, {})
                if field_suggestions:
                    context_info += f"AI Suggestions: {field_suggestions}\n"
            
            prompt = f"""
Generate simple, realistic test data for this form field:

Field: {field_name} ({field_type})
Label: {field_label}
Placeholder: {field_placeholder}

Rules:
- Generate SIMPLE, SHORT test data
- For text fields: use simple words or realistic names/values
- For comments/textarea: use brief, professional text (max 10 words)
- For usernames: use format like "testuser123" or "user" + numbers
- For passwords: use simple format like "test123" or "password123"
- NO conversational responses or questions
- NO business-specific context unless clearly indicated by field name
- Keep responses generic and suitable for automated testing

Examples:
- username: "testuser123"
- email: "test@example.com" 
- comments: "This is a test comment"
- description: "Test description"
- message: "Test message"

For select/radio with options: {field.get('options', [])}

Respond with ONLY the simple test value, nothing else.
"""

            return await self._call_gemini(prompt)
            
        except Exception as e:
            logger.error(f"Error generating field value with AI: {e}")
            return None
    
    async def generate_intelligent_option_selection(self, field: Dict[str, Any], options: List[Dict], form_context: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Intelligently select an option from dropdown/radio button choices using AI.
        
        Args:
            field: Field information
            options: Available options
            form_context: Optional form context
            
        Returns:
            Selected option or None
        """
        if not self.is_available() or not options:
            return None
        
        try:
            field_name = field.get('name', '')
            field_label = field.get('label', '')
            
            options_text = []
            for i, opt in enumerate(options):
                opt_value = opt.get('value', '')
                opt_text = opt.get('text', opt_value)
                options_text.append(f"{i}: {opt_text} (value: {opt_value})")
            
            context_info = ""
            if form_context:
                context_info = f"Form Context: {form_context.get('form_type', '')} - {form_context.get('form_purpose', '')}\n"
            
            prompt = f"""
Select the most appropriate option from this list for a realistic form fill:

Field: {field_name} ({field_label})
{context_info}

Available Options:
{chr(10).join(options_text)}

Consider:
- Most common/realistic choice for this field type
- Professional/appropriate selection for testing
- Avoid placeholder options like "Select..." or "Choose..."

Respond with ONLY the index number (0, 1, 2, etc.) of your selected option.
"""

            response = await self._call_gemini(prompt)
            if response and response.strip().isdigit():
                index = int(response.strip())
                if 0 <= index < len(options):
                    return options[index]
            
        except Exception as e:
            logger.error(f"Error with AI option selection: {e}")
        
        return None
    
    async def _call_gemini(self, prompt: str) -> Optional[str]:
        """
        Make an async call to Gemini API.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Response text or None if failed
        """
        try:
            # Run the synchronous Gemini call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            if response and response.text:
                return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
        
        return None
    
    async def generate_validation_test_data(self, field: Dict[str, Any], scenario: str) -> Optional[str]:
        """
        Generate specific invalid/edge case data for validation testing.
        
        Args:
            field: Field information
            scenario: Type of validation test (empty, invalid_format, boundary, etc.)
            
        Returns:
            Invalid test data or None
        """
        if not self.is_available():
            return None
        
        try:
            field_type = field.get('type', 'text')
            field_name = field.get('name', '')
            constraints = field.get('constraints', {})
            
            prompt = f"""
Generate invalid test data for form validation testing:

Field: {field_name}
Type: {field_type}
Constraints: {constraints}
Test Scenario: {scenario}

Generate appropriate invalid data for testing this specific validation scenario:
- empty: return empty string
- invalid_format: wrong format for the field type
- boundary: exceed field limits/constraints  
- injection: test for security vulnerabilities
- special_chars: problematic special characters

Respond with ONLY the invalid value, no explanation.
"""

            return await self._call_gemini(prompt)
            
        except Exception as e:
            logger.error(f"Error generating validation test data: {e}")
            return None
