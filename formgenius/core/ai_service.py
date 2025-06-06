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
        self.api_call_count = 0
        self.batch_call_count = 0
        self.api_call_history = []
        self.last_call_time = None
    
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
    
    async def _call_gemini(self, prompt: str, is_batch: bool = False) -> Optional[str]:
        """
        Make an async call to Gemini API.
        
        Args:
            prompt: The prompt to send to Gemini
            is_batch: Whether this is a batched call
            
        Returns:
            Response text or None if failed
        """
        try:
            import time
            from datetime import datetime
            
            current_time = datetime.now()
            self.api_call_count += 1
            
            # Track call metrics
            call_info = {
                'timestamp': current_time,
                'is_batch': is_batch,
                'prompt_length': len(prompt)
            }
            self.api_call_history.append(call_info)
            
            # If this is a batch call, increment batch counter
            if is_batch:
                self.batch_call_count += 1
                logger.info(f"Making Gemini API BATCH call #{self.batch_call_count} (total API calls: {self.api_call_count})")
            else:
                logger.info(f"Making Gemini API call #{self.api_call_count}")
            
            # Run the synchronous Gemini call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            self.last_call_time = datetime.now()
            call_info['duration'] = (self.last_call_time - current_time).total_seconds()
            
            if response and response.text:
                return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
        
        return None
    
    async def batch_generate_field_values(self, fields: List[Dict[str, Any]], form_context: Dict[str, Any] = None, page_context: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Generate values for multiple fields in a single API call to reduce API usage.
        
        Args:
            fields: List of field information dictionaries
            form_context: Optional form context from previous analysis
            page_context: Optional page context with credentials/instructions
            
        Returns:
            Dictionary mapping field names to generated values
        """
        if not self.is_available() or not fields:
            return {}

        try:
            # Build batch context
            context_info = ""
            if form_context:
                context_info = f"FORM CONTEXT:\n"
                context_info += f"- Form Type: {form_context.get('form_type', 'unknown')}\n"
                context_info += f"- Form Purpose: {form_context.get('form_purpose', 'unknown')}\n"
                
                # Add any context notes
                if 'context_notes' in form_context and form_context['context_notes']:
                    context_info += f"- Notes: {form_context['context_notes']}\n"
                
                context_info += "\n"
            
            # Add page context information
            if page_context:
                if page_context.get('credentials'):
                    context_info += "AVAILABLE CREDENTIALS:\n"
                    for cred in page_context['credentials']:
                        if isinstance(cred, dict) and 'type' in cred and 'value' in cred:
                            context_info += f"- {cred['type']}: {cred['value']} (found: {cred.get('source', 'unknown')})\n"
                    context_info += "\n"
                
                if page_context.get('instructions'):
                    context_info += "PAGE INSTRUCTIONS:\n"
                    for instruction in page_context['instructions']:
                        context_info += f"- {instruction}\n"
                    context_info += "\n"
                
                # Add page title and URL if available
                if page_context.get('page_title'):
                    context_info += f"PAGE TITLE: {page_context.get('page_title')}\n"
                if page_context.get('url'):
                    context_info += f"PAGE URL: {page_context.get('url')}\n"
                    
                context_info += "\n"
            
            # Prepare field descriptions
            field_descriptions = []
            field_ids = []
            
            for i, field in enumerate(fields):
                if not isinstance(field, dict):
                    continue
                    
                field_type = field.get('type', 'text')
                field_name = field.get('name', '')
                field_id = field.get('id', '')
                field_label = field.get('label', '')
                field_placeholder = field.get('placeholder', '')
                
                # Generate a unique ID for this field
                field_id_for_mapping = field_name or field_id or f"field_{i}"
                field_ids.append(field_id_for_mapping)
                
                # Add field description
                field_desc = f"""
Field #{i+1}: {field_name} ({field_type})
ID: {field_id_for_mapping}
Label: {field_label}
Placeholder: {field_placeholder}
Type: {field_type}
Required: {field.get('required', False)}
"""
                
                # Add constraints if they exist
                constraints = field.get('constraints', {})
                if constraints:
                    try:
                        constraints_str = ', '.join([f"{k}: {v}" for k, v in constraints.items()])
                        field_desc += f"Constraints: {constraints_str}\n"
                    except Exception as e:
                        logger.warning(f"Could not convert constraints to string: {e}")
                
                # Safely add options if they exist
                options = field.get('options', [])
                if options:
                    try:
                        # Format options in a more readable way
                        options_str = []
                        for opt in options:
                            if isinstance(opt, dict):
                                opt_text = opt.get('text', '')
                                opt_value = opt.get('value', '')
                                if opt_text and opt_value:
                                    options_str.append(f"'{opt_text}' (value: '{opt_value}')")
                            else:
                                options_str.append(str(opt))
                        
                        field_desc += f"Options: [{', '.join(options_str)}]\n"
                    except Exception as e:
                        logger.warning(f"Could not convert options to string: {e}")
                        field_desc += "Options: []\n"
                
                field_descriptions.append(field_desc)
            
            # Build the consolidated prompt
            prompt = f"""
Generate realistic test data for multiple form fields in a single response.
{context_info}

FIELDS TO FILL:
{chr(10).join(field_descriptions)}

INSTRUCTIONS:
- Generate ONLY the data needed to fill the form - no explanations
- If credentials are provided in the page context, use them for matching fields
- For each field, generate appropriate data based on field type:
  - Email: Use test@example.com format
  - Password: Use "Test123!" or similar unless credentials provided
  - Text fields: Simple words or names appropriate to the field label
  - Textarea: Brief professional text (2-8 words)
  - Number: Realistic value within reasonable range
  - Phone: Standard format like (123) 456-7890
  - Date: YYYY-MM-DD format within reasonable range
  - Select/Radio: The value of the most appropriate option
  - Checkbox: "true" for agreements/consents, random for others

YOUR RESPONSE MUST BE VALID JSON ONLY with this structure:
{{
  "field_id_1": "generated_value_1",
  "field_id_2": "generated_value_2"
}}

DO NOT include any explanations, markdown formatting, or text outside the JSON.
"""

            response = await self._call_gemini(prompt, is_batch=True)
            if not response:
                return {}
                
            # Parse the JSON response
            try:
                import json
                import re
                
                logger.debug(f"Raw response from Gemini API: {response[:100]}...")
                
                # Try multiple approaches to extract valid JSON
                result = None
                
                # Approach 1: Direct JSON parsing
                try:
                    result = json.loads(response)
                    logger.debug("Successfully parsed full response as JSON")
                except json.JSONDecodeError:
                    logger.debug("Failed to parse full response as JSON, trying extraction")
                
                # Approach 2: Extract JSON with regex
                if result is None:
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            logger.debug("Successfully parsed extracted JSON with basic regex")
                        except json.JSONDecodeError:
                            logger.debug("Failed to parse extracted JSON with basic regex")
                
                # Approach 3: More careful JSON extraction
                if result is None:
                    # Look for patterns like {"field": "value"}
                    json_match = re.search(r'(\{(?:[^{}]|(?1))*\})', response, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            logger.debug("Successfully parsed extracted JSON with recursive regex")
                        except json.JSONDecodeError:
                            logger.debug("Failed to parse extracted JSON with recursive regex")
                
                # Approach 4: Final attempt - try to fix common JSON issues
                if result is None:
                    # Try to fix common JSON formatting issues
                    cleaned_response = response
                    # Replace single quotes with double quotes
                    cleaned_response = re.sub(r"'([^']*)':", r'"\1":', cleaned_response)
                    # Add quotes around unquoted keys
                    cleaned_response = re.sub(r'(\s+)(\w+)(:)', r'\1"\2"\3', cleaned_response)
                    
                    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            logger.debug("Successfully parsed JSON after cleanup")
                        except json.JSONDecodeError:
                            logger.error("All JSON parsing attempts failed")
                            return {}
                
                # If all parsing attempts failed
                if result is None:
                    logger.error("Failed to extract valid JSON from response")
                    return {}
                
                # Make sure we have valid data for fields
                field_values = {}
                for i, field_id in enumerate(field_ids):
                    if field_id in result:
                        field_values[field_id] = result[field_id]
                    else:
                        # Try to find the field by a different naming convention
                        field = fields[i]
                        field_name = field.get('name', '')
                        field_id_alt = field.get('id', '')
                        
                        # Check for alternative keys in the response
                        if field_name and field_name in result:
                            field_values[field_id] = result[field_name]
                        elif field_id_alt and field_id_alt in result:
                            field_values[field_id] = result[field_id_alt]
                
                logger.info(f"Successfully generated batch data for {len(field_values)}/{len(fields)} fields in a single API call")
                
                # If we didn't get values for all fields, log the missing ones
                if len(field_values) < len(fields):
                    missing_fields = [field_ids[i] for i in range(len(field_ids)) if field_ids[i] not in field_values]
                    logger.warning(f"Missing generated values for fields: {missing_fields}")
                
                return field_values
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse batch response as JSON: {e}")
                logger.debug(f"Response was: {response[:200]}...")
                return {}
                
        except Exception as e:
            logger.error(f"Error in batch field value generation: {e}")
            return {}
    
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
    
    def get_api_usage_metrics(self) -> Dict[str, Any]:
        """
        Get metrics on API usage.
        
        Returns:
            Dictionary with API usage metrics
        """
        from datetime import datetime, timedelta
        
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        five_minutes_ago = now - timedelta(minutes=5)
        
        # Calculate calls in recent time periods
        calls_last_minute = sum(1 for call in self.api_call_history if call['timestamp'] >= one_minute_ago)
        calls_last_five_minutes = sum(1 for call in self.api_call_history if call['timestamp'] >= five_minutes_ago)
        
        # Calculate batch efficiency
        batch_calls = sum(1 for call in self.api_call_history if call.get('is_batch', False))
        non_batch_calls = self.api_call_count - batch_calls
        
        # Calculate average duration
        durations = [call.get('duration', 0) for call in self.api_call_history if 'duration' in call]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_api_calls': self.api_call_count,
            'batch_calls': batch_calls,
            'non_batch_calls': non_batch_calls,
            'calls_last_minute': calls_last_minute,
            'calls_last_five_minutes': calls_last_five_minutes,
            'average_call_duration': avg_duration,
            'batch_efficiency': f"{batch_calls} batched calls replaced approximately {len(self.api_call_history) * 4} individual calls" if batch_calls else "N/A",
            'estimated_rate': f"{calls_last_minute} calls/minute"
        }
    
    def debug_api_status(self) -> Dict[str, Any]:
        """
        Get detailed debug information about the AI service status.
        
        Returns:
            Dictionary with debug information
        """
        debug_info = {
            'is_available': self.is_available(),
            'model_initialized': self.model is not None,
            'api_key_set': bool(self.config.gemini_api_key),
            'api_calls_made': self.api_call_count,
            'batch_calls_made': self.batch_call_count,
            'config_model': getattr(self.config, 'ai_model', 'gemini-2.0-flash-exp'),
        }
        
        if not self.is_available():
            if not self.config.gemini_api_key:
                debug_info['failure_reason'] = "API key not set"
            elif self.model is None:
                debug_info['failure_reason'] = "Model initialization failed"
        
        return debug_info
