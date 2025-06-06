#!/usr/bin/env python3
"""
FormGenius Example Usage Scripts
Demonstrates various ways to use the FormGenius agent
"""

import asyncio
import logging
from pathlib import Path

from formgenius.core.agent import FormGeniusAgent
from formgenius.core.config import Config


async def example_single_form():
    """Example: Fill a single form with valid data"""
    print("=== Example: Single Form Filling ===")
    
    # Load configuration
    config = Config.from_yaml('config.yaml')
    
    # Initialize agent (no initialization method needed)
    agent = FormGeniusAgent(config)
    
    try:
        # Fill a form (replace with actual URL)
        result = await agent.fill_form(
            url="https://example.com/contact-form",
            test_scenarios=["valid"]  # Use test_scenarios instead of submit and scenario
        )
        
        print(f"Form filling result: {result['status']}")
        print(f"Fields filled: {len(result.get('filled_fields', []))}")
        
    except Exception as e:
        print(f"Error: {e}")
        # No cleanup needed for FormGeniusAgent


async def example_batch_forms():
    """Example: Fill multiple forms in batch"""
    print("\n=== Example: Batch Form Filling ===")
    
    # Sample URLs (replace with actual URLs)
    urls = [
        "https://example.com/form1",
        "https://example.com/form2", 
        "https://example.com/form3"
    ]
    
    config = Config.from_yaml('config.yaml')
    agent = FormGeniusAgent(config)
    
    try:
        results = await agent.batch_fill_forms(
            urls=urls,
            test_scenarios=["valid"]  # Use test_scenarios instead of submit and scenario
        )
        
        print(f"Processed {len(results)} forms")
        for i, result in enumerate(results):
            print(f"Form {i+1}: {result['status']}")
            
    except Exception as e:
        print(f"Error: {e}")
        # No cleanup needed for FormGeniusAgent


async def example_form_validation_testing():
    """Example: Test form validation with different scenarios"""
    print("\n=== Example: Form Validation Testing ===")
    
    config = Config.from_yaml('config.yaml')
    agent = FormGeniusAgent(config)
    
    try:
        # Test form with multiple scenarios
        result = await agent.test_form_validation(
            url="https://example.com/signup-form",
            validation_scenarios=["valid", "invalid", "edge"]  # Use validation_scenarios instead of scenarios
        )
        
        print(f"Validation testing completed")
        print(f"Test scenarios run: {len(result.get('scenarios', []))}")
        
        for scenario in result.get('scenarios', []):
            print(f"- {scenario['name']}: {scenario['status']}")
            
    except Exception as e:
        print(f"Error: {e}")
        # No cleanup needed for FormGeniusAgent


async def example_power_apps_form():
    """Example: Fill a Power Apps form"""
    print("\n=== Example: Power Apps Form Filling ===")
    
    config = Config.from_yaml('config.yaml')
    agent = FormGeniusAgent(config)
    
    try:
        # Fill Power Apps form (replace with actual Power Apps URL)
        result = await agent.fill_power_apps_form(
            app_url="https://apps.powerapps.com/play/...",  # Use app_url instead of url
            test_scenarios=["valid"]  # Use test_scenarios instead of submit and scenario
        )
        
        print(f"Power Apps form result: {result['status']}")
        print(f"Power Apps fields detected: {len(result.get('power_apps_fields', []))}")
        
    except Exception as e:
        print(f"Error: {e}")
        # No cleanup needed for FormGeniusAgent


async def example_custom_data_generation():
    """Example: Use custom data generation"""
    print("\n=== Example: Custom Data Generation ===")
    
    from formgenius.core.data_generator import DataGenerator
    
    config = Config.from_yaml('config.yaml')
    generator = DataGenerator(config)
    
    # Generate data for specific field types
    data = {
        'email': generator.generate_email(),
        'name': generator.generate_name(),
        'phone': generator.generate_phone(),
        'text': generator.generate_text(100),
        'password': generator.generate_password()
    }
    
    print("Generated test data:")
    for field, value in data.items():
        print(f"- {field}: {value}")


async def example_with_custom_config():
    """Example: Use custom configuration"""
    print("\n=== Example: Custom Configuration ===")
    
    # Create custom config
    config = Config(
        headless=True,
        browser_type='chromium',
        timeout=45000,
        ai_provider='gemini',
        ai_model='gemini-pro',
        retry_attempts=2,
        wait_between_fields=200,
        save_screenshots=True
    )
    
    agent = FormGeniusAgent(config)
    
    try:
        # Use agent with custom config
        print("Agent initialized with custom configuration")
        print(f"Headless mode: {config.headless}")
        print(f"AI provider: {config.ai_provider}")
        
    except Exception as e:
        print(f"Error: {e}")
        # No cleanup needed for FormGeniusAgent


async def example_error_handling():
    """Example: Proper error handling"""
    print("\n=== Example: Error Handling ===")
    
    config = Config.from_yaml('config.yaml')
    agent = FormGeniusAgent(config)
    
    try:
        # Try to fill a non-existent form
        result = await agent.fill_form(
            url="https://nonexistent-domain-12345.com/form",
            test_scenarios=["valid"]  # Use test_scenarios instead of submit and scenario
        )
        
        if result['status'] == 'error':
            print(f"Expected error occurred: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"Exception caught: {e}")
        # No special cleanup needed


def main():
    """Run all examples"""
    print("FormGenius Usage Examples")
    print("=" * 50)
    
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Run examples
    asyncio.run(example_single_form())
    asyncio.run(example_batch_forms())
    asyncio.run(example_form_validation_testing())
    asyncio.run(example_power_apps_form())
    asyncio.run(example_custom_data_generation())
    asyncio.run(example_with_custom_config())
    asyncio.run(example_error_handling())
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nTo run FormGenius from command line:")
    print("python main.py fill --url https://example.com/form")
    print("python main.py batch --urls-file urls.txt")
    print("python main.py test --url https://example.com/form")
    print("python main.py power-apps --url https://apps.powerapps.com/...")


if __name__ == '__main__':
    main()
