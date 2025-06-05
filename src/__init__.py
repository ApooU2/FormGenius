"""
FormGenius - AI-Powered Automated Web Testing Framework

FormGenius is a revolutionary AI-powered testing framework that automatically analyzes websites,
understands their structure and functionality, and generates comprehensive Playwright test suites
with minimal human intervention.

Example:
    ```python
    import asyncio
    from formgenius import FormGenius
    
    async def main():
        formgenius = FormGenius()
        analysis = await formgenius.analyze_website("https://example.com")
        scenarios = await formgenius.generate_test_scenarios(analysis)
        await formgenius.generate_playwright_tests(scenarios, "https://example.com")
    
    asyncio.run(main())
    ```
"""

from .core import FormGenius, GeminiClient, TestRunner
from .agents import WebExplorer, TestStrategist, ScriptGenerator, TestExecutor
from .analyzers import DOMAnalyzer, FlowAnalyzer, ElementDetector
from .generators import ScenarioGenerator, PlaywrightCodeGenerator

__version__ = "1.0.0"
__author__ = "FormGenius Team"
__email__ = "team@formgenius.dev"
__description__ = "AI-Powered Automated Web Testing Framework"

__all__ = [
    # Core components
    'FormGenius',
    'GeminiClient',
    'TestRunner',
    
    # AI Agents
    'WebExplorer',
    'TestStrategist', 
    'ScriptGenerator',
    'TestExecutor',
    
    # Analyzers
    'DOMAnalyzer',
    'FlowAnalyzer',
    'ElementDetector',
    
    # Generators
    'ScenarioGenerator',
    'PlaywrightCodeGenerator'
]


def get_version():
    """Get the current version of FormGenius."""
    return __version__


def get_info():
    """Get information about FormGenius."""
    return {
        'name': 'FormGenius',
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'email': __email__
    }


# Quick start function for convenience
async def quick_test(url: str, output_dir: str = "./generated_tests"):
    """
    Quick test generation for a URL.
    
    Args:
        url: The URL to test
        output_dir: Directory to output generated tests
        
    Returns:
        Dictionary with analysis and test generation results
    """
    formgenius = FormGenius()
    
    # Analyze website
    analysis = await formgenius.analyze_website(url)
    
    # Generate scenarios
    scenarios = await formgenius.generate_test_scenarios(analysis)
    
    # Generate tests
    await formgenius.generate_playwright_tests(scenarios, url, output_dir)
    
    return {
        'url': url,
        'output_dir': output_dir,
        'analysis': analysis,
        'scenarios_count': len(scenarios),
        'status': 'completed'
    }
