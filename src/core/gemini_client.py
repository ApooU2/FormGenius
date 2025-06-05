"""
Gemini AI client for FormGenius automated testing framework.
Handles communication with Google's Gemini API for web analysis and test generation.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.text_model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-pro")
        )
        self.vision_model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_VISION_MODEL", "gemini-pro-vision")
        )
        
        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.1")),
            max_output_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "4096")),
            top_p=float(os.getenv("GEMINI_TOP_P", "0.8")),
            top_k=int(os.getenv("GEMINI_TOP_K", "40"))
        )
        
        # Safety settings for web content analysis
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    
    async def analyze_webpage_structure(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Analyze webpage structure and identify testable elements.
        
        Args:
            html_content: HTML content of the webpage
            url: URL of the webpage
            
        Returns:
            Dictionary containing analysis results
        """
        prompt = f"""
        Analyze this webpage HTML and identify all testable elements and user interactions.
        
        URL: {url}
        
        HTML Content:
        {html_content[:10000]}  # Limit to first 10k chars to avoid token limits
        
        Please provide a structured analysis including:
        1. Page type and purpose
        2. Interactive elements (forms, buttons, links, inputs)
        3. Navigation elements
        4. Content areas that should be validated
        5. Potential user workflows
        6. Accessibility considerations
        7. Performance testing opportunities
        
        Return the response in JSON format with clear categorization.
        """
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error analyzing webpage structure: {e}")
            return {"error": str(e)}
    
    async def generate_test_scenarios(self, page_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate comprehensive test scenarios based on page analysis.
        
        Args:
            page_analysis: Results from webpage structure analysis
            
        Returns:
            List of test scenarios
        """
        prompt = f"""
        Based on this webpage analysis, generate comprehensive test scenarios for automated testing.
        
        Page Analysis:
        {page_analysis}
        
        Generate test scenarios for:
        1. Functional testing (form submissions, navigation, user workflows)
        2. UI testing (element visibility, layout, responsive design)
        3. Accessibility testing (ARIA labels, keyboard navigation, screen reader compatibility)
        4. Performance testing (page load times, resource loading)
        5. Error handling (invalid inputs, network failures, edge cases)
        6. Cross-browser compatibility
        7. Security testing (XSS prevention, input validation)
        
        For each scenario, provide:
        - Test name and description
        - Prerequisites
        - Step-by-step actions
        - Expected results
        - Priority level (High/Medium/Low)
        - Test type category
        
        Return the response in JSON format with an array of test scenarios.
        """
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_scenarios_response(response)
        except Exception as e:
            logger.error(f"Error generating test scenarios: {e}")
            return [{"error": str(e)}]
    
    async def generate_playwright_code(self, test_scenario: Dict[str, Any], page_analysis: Dict[str, Any]) -> str:
        """
        Generate Playwright test code for a specific test scenario.
        
        Args:
            test_scenario: Test scenario details
            page_analysis: Page analysis results
            
        Returns:
            Playwright test code as string
        """
        prompt = f"""
        Generate Playwright test code for this test scenario.
        
        Test Scenario:
        {test_scenario}
        
        Page Analysis:
        {page_analysis}
        
        Requirements:
        1. Use modern Playwright Python async syntax
        2. Include proper error handling and assertions
        3. Use robust selectors (prefer data-testid, then semantic selectors)
        4. Add meaningful comments
        5. Include setup and teardown if needed
        6. Handle timeouts and waits appropriately
        7. Follow Playwright best practices
        
        Generate a complete, runnable test function that can be imported into a test suite.
        """
        
        try:
            response = await self._generate_content(prompt)
            return self._extract_code_from_response(response)
        except Exception as e:
            logger.error(f"Error generating Playwright code: {e}")
            return f"# Error generating code: {e}"
    
    async def analyze_test_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test execution results and provide insights.
        
        Args:
            test_results: Test execution results
            
        Returns:
            Analysis and recommendations
        """
        prompt = f"""
        Analyze these test execution results and provide insights and recommendations.
        
        Test Results:
        {test_results}
        
        Please provide:
        1. Summary of test execution
        2. Failure analysis and root causes
        3. Recommendations for fixing failures
        4. Suggestions for improving test coverage
        5. Performance insights
        6. Reliability improvements
        
        Return the response in JSON format.
        """
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error analyzing test results: {e}")
            return {"error": str(e)}
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API."""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.text_model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure analysis response."""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON found, return structured text
                return {"analysis": response, "structured": False}
        except json.JSONDecodeError:
            return {"analysis": response, "structured": False}
    
    def _parse_scenarios_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse and structure scenarios response."""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON array found, try to find object
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response[start_idx:end_idx]
                    parsed = json.loads(json_str)
                    # If it's an object with scenarios key, return that
                    if 'scenarios' in parsed:
                        return parsed['scenarios']
                    return [parsed]
                return [{"scenario": response, "structured": False}]
        except json.JSONDecodeError:
            return [{"scenario": response, "structured": False}]
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from response, handling markdown code blocks."""
        # Look for code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            return response.strip()
