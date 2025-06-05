#!/usr/bin/env python3
"""
Basic usage example for FormGenius framework.

This script demonstrates how to use FormGenius to analyze a website
and generate comprehensive test suites.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.formgenius import FormGenius
from src.core.test_runner import TestRunner


async def basic_example():
    """Basic example of using FormGenius."""
    
    print("🚀 FormGenius Basic Example")
    print("=" * 50)
    
    # Initialize FormGenius
    # Make sure you have GEMINI_API_KEY in your environment
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        return
    
    formgenius = FormGenius()
    
    # Target website
    target_url = "https://example.com"
    print(f"🎯 Target URL: {target_url}")
    
    try:
        # Step 1: Analyze the website
        print("\n📊 Step 1: Analyzing website...")
        analysis_result = await formgenius.analyze_website(target_url)
        
        print(f"✅ Analysis complete!")
        print(f"   - Found {len(analysis_result.get('forms', []))} forms")
        print(f"   - Found {len(analysis_result.get('interactive_elements', []))} interactive elements")
        print(f"   - Identified {len(analysis_result.get('user_flows', []))} user flows")
        
        # Step 2: Generate test scenarios
        print("\n🧪 Step 2: Generating test scenarios...")
        scenarios = await formgenius.generate_test_scenarios(analysis_result)
        
        print(f"✅ Generated {len(scenarios)} test scenarios")
        for i, scenario in enumerate(scenarios[:3], 1):  # Show first 3
            print(f"   {i}. {scenario.get('name', 'Unnamed scenario')}")
        
        # Step 3: Generate Playwright tests
        print("\n⚡ Step 3: Generating Playwright test code...")
        test_code = await formgenius.generate_playwright_tests(
            scenarios, 
            target_url,
            output_dir="./generated_tests"
        )
        
        print(f"✅ Generated test files:")
        output_dir = Path("./generated_tests")
        if output_dir.exists():
            for test_file in output_dir.glob("*.py"):
                print(f"   - {test_file.name}")
        
        # Step 4: Run the tests (optional)
        run_tests = input("\n🏃 Would you like to run the generated tests? (y/n): ").strip().lower()
        
        if run_tests == 'y':
            print("\n🔄 Running generated tests...")
            
            runner = TestRunner(
                output_dir=Path("./test_results"),
                max_workers=2,
                headed=False  # Set to True to see tests run in browser
            )
            
            test_result = await runner.run_test_suite(Path("./generated_tests"))
            
            print(f"\n📈 Test Results:")
            print(f"   Total: {test_result.total_tests}")
            print(f"   Passed: {test_result.passed}")
            print(f"   Failed: {test_result.failed}")
            print(f"   Success Rate: {test_result.success_rate:.1f}%")
            
            print(f"\n📊 Reports generated in: ./test_results/")
        
        print("\n🎉 Example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def advanced_example():
    """Advanced example with custom configuration."""
    
    print("🚀 FormGenius Advanced Example")
    print("=" * 50)
    
    # Custom configuration
    config = {
        "analysis": {
            "deep_analysis": True,
            "analyze_accessibility": True,
            "analyze_security": True,
            "max_pages": 10
        },
        "test_generation": {
            "include_negative_tests": True,
            "include_edge_cases": True,
            "generate_data_driven_tests": True
        },
        "execution": {
            "browsers": ["chromium", "firefox"],
            "parallel_workers": 4,
            "screenshot_on_failure": True,
            "video_recording": True
        }
    }
    
    formgenius = FormGenius(config=config)
    
    # Multiple URLs for comprehensive testing
    target_urls = [
        "https://example.com",
        "https://httpbin.org/forms/post",  # Form testing
        "https://the-internet.herokuapp.com/login"  # Login testing
    ]
    
    for url in target_urls:
        print(f"\n🎯 Processing: {url}")
        
        try:
            # Analyze
            analysis = await formgenius.analyze_website(url)
            
            # Generate scenarios
            scenarios = await formgenius.generate_test_scenarios(analysis)
            
            # Generate tests with custom naming
            domain = url.split("//")[1].split("/")[0].replace(".", "_")
            test_dir = f"./tests_{domain}"
            
            await formgenius.generate_playwright_tests(
                scenarios,
                url,
                output_dir=test_dir
            )
            
            print(f"✅ Generated tests in: {test_dir}")
            
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
    
    print("\n🎉 Advanced example completed!")


def interactive_example():
    """Interactive example where user provides URLs."""
    
    print("🚀 FormGenius Interactive Example")
    print("=" * 50)
    
    print("This example will help you test your own websites!")
    print("Enter URLs you want to analyze and test.")
    print("Type 'quit' to exit.\n")
    
    urls = []
    while True:
        url = input("Enter a URL to test: ").strip()
        if url.lower() == 'quit':
            break
        if url:
            urls.append(url)
            print(f"Added: {url}")
    
    if not urls:
        print("No URLs provided. Exiting.")
        return
    
    async def process_urls():
        formgenius = FormGenius()
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            try:
                # Quick analysis and test generation
                analysis = await formgenius.analyze_website(url)
                scenarios = await formgenius.generate_test_scenarios(analysis)
                
                domain = url.split("//")[1].split("/")[0].replace(".", "_")
                await formgenius.generate_playwright_tests(
                    scenarios,
                    url,
                    output_dir=f"./tests_{domain}"
                )
                
                print(f"✅ Tests generated for {url}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    asyncio.run(process_urls())


if __name__ == "__main__":
    print("Select an example to run:")
    print("1. Basic Example")
    print("2. Advanced Example")
    print("3. Interactive Example")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(basic_example())
    elif choice == "2":
        asyncio.run(advanced_example())
    elif choice == "3":
        interactive_example()
    else:
        print("Invalid choice. Please run the script again.")
