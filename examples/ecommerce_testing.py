#!/usr/bin/env python3
"""
E-commerce testing example for FormGenius.

This script demonstrates how to use FormGenius specifically for
e-commerce websites with complex user flows.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.formgenius import FormGenius
from src.core.test_runner import TestRunner


async def ecommerce_testing_example():
    """Comprehensive e-commerce testing example."""
    
    print("🛒 FormGenius E-commerce Testing Example")
    print("=" * 50)
    
    # E-commerce specific configuration
    ecommerce_config = {
        "analysis": {
            "deep_analysis": True,
            "analyze_accessibility": True,
            "analyze_security": True,
            "analyze_performance": True,
            "max_pages": 20,  # More pages for e-commerce
            "focus_on_forms": True,
            "analyze_checkout_flow": True
        },
        "test_scenarios": {
            "include_cart_scenarios": True,
            "include_checkout_scenarios": True,
            "include_payment_scenarios": True,
            "include_user_account_scenarios": True,
            "include_product_search_scenarios": True,
            "include_negative_scenarios": True
        },
        "data_generation": {
            "generate_user_profiles": True,
            "generate_product_data": True,
            "generate_payment_data": True,
            "include_international_data": True
        }
    }
    
    formgenius = FormGenius(config=ecommerce_config)
    
    # Popular e-commerce demo sites for testing
    ecommerce_sites = [
        {
            "name": "Demo Online Shop",
            "url": "https://demo.opencart.com/",
            "focus": ["product_catalog", "cart", "checkout"]
        },
        {
            "name": "Automation Practice",
            "url": "http://automationpractice.com/",
            "focus": ["user_registration", "product_search", "checkout"]
        },
        {
            "name": "The Internet - E-commerce",
            "url": "https://the-internet.herokuapp.com/",
            "focus": ["basic_auth", "forms", "dynamic_content"]
        }
    ]
    
    print(f"Testing {len(ecommerce_sites)} e-commerce sites...\n")
    
    all_results = []
    
    for site in ecommerce_sites:
        print(f"🎯 Testing: {site['name']}")
        print(f"   URL: {site['url']}")
        print(f"   Focus Areas: {', '.join(site['focus'])}")
        
        try:
            # Step 1: Deep analysis
            print("   📊 Analyzing website structure...")
            analysis = await formgenius.analyze_website(
                site['url'],
                focus_areas=site['focus']
            )
            
            # Step 2: Generate e-commerce specific scenarios
            print("   🧪 Generating e-commerce test scenarios...")
            scenarios = await formgenius.generate_ecommerce_scenarios(
                analysis,
                focus_areas=site['focus']
            )
            
            print(f"   ✅ Generated {len(scenarios)} scenarios")
            
            # Display scenario categories
            scenario_types = {}
            for scenario in scenarios:
                category = scenario.get('category', 'general')
                scenario_types[category] = scenario_types.get(category, 0) + 1
            
            for category, count in scenario_types.items():
                print(f"      - {category}: {count} scenarios")
            
            # Step 3: Generate comprehensive test suite
            print("   ⚡ Generating Playwright test suite...")
            site_name = site['name'].lower().replace(' ', '_')
            test_dir = f"./ecommerce_tests_{site_name}"
            
            test_files = await formgenius.generate_playwright_tests(
                scenarios,
                site['url'],
                output_dir=test_dir,
                include_page_objects=True,
                include_data_fixtures=True
            )
            
            print(f"   ✅ Test suite generated in: {test_dir}")
            
            # Step 4: Run a subset of tests for demonstration
            print("   🔄 Running sample tests...")
            
            runner = TestRunner(
                output_dir=Path(f"./results_{site_name}"),
                max_workers=2,
                timeout=60000,  # Longer timeout for e-commerce
                browser="chromium"
            )
            
            # Run only smoke tests to avoid long execution
            smoke_test_pattern = "*smoke*.py"
            result = await runner.run_test_suite(
                Path(test_dir),
                test_pattern=smoke_test_pattern
            )
            
            print(f"   📈 Sample Results: {result.passed}/{result.total_tests} passed")
            
            all_results.append({
                'site': site['name'],
                'url': site['url'],
                'scenarios': len(scenarios),
                'test_result': result
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {site['name']}: {e}")
            continue
        
        print()  # Empty line for readability
    
    # Summary report
    print("📊 E-commerce Testing Summary")
    print("=" * 30)
    
    total_scenarios = sum(r['scenarios'] for r in all_results)
    total_tests = sum(r['test_result'].total_tests for r in all_results)
    total_passed = sum(r['test_result'].passed for r in all_results)
    
    print(f"Sites Tested: {len(all_results)}")
    print(f"Total Scenarios Generated: {total_scenarios}")
    print(f"Total Tests Executed: {total_tests}")
    print(f"Overall Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    print("\nDetailed Results:")
    for result in all_results:
        print(f"  {result['site']}:")
        print(f"    Scenarios: {result['scenarios']}")
        print(f"    Tests: {result['test_result'].total_tests}")
        print(f"    Success: {result['test_result'].success_rate:.1f}%")
    
    print("\n🎉 E-commerce testing example completed!")


async def generate_custom_ecommerce_scenarios():
    """Generate custom e-commerce scenarios based on user input."""
    
    print("🛍️ Custom E-commerce Scenario Generator")
    print("=" * 40)
    
    # Get user input
    site_url = input("Enter e-commerce site URL: ").strip()
    if not site_url:
        print("No URL provided. Exiting.")
        return
    
    print("\nSelect focus areas (enter numbers separated by commas):")
    focus_options = [
        "Product Search",
        "Shopping Cart",
        "Checkout Process",
        "User Registration",
        "User Login",
        "Payment Processing",
        "Order Management",
        "Product Reviews",
        "Wishlist",
        "Mobile Responsiveness"
    ]
    
    for i, option in enumerate(focus_options, 1):
        print(f"{i}. {option}")
    
    selected = input("\nYour selection: ").strip()
    if not selected:
        focus_areas = ["general"]
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selected.split(",")]
            focus_areas = [focus_options[i].lower().replace(" ", "_") for i in indices if 0 <= i < len(focus_options)]
        except:
            focus_areas = ["general"]
    
    print(f"\nSelected focus areas: {', '.join(focus_areas)}")
    
    # Generate scenarios
    formgenius = FormGenius()
    
    try:
        print("\n📊 Analyzing website...")
        analysis = await formgenius.analyze_website(site_url)
        
        print("🧪 Generating custom scenarios...")
        scenarios = await formgenius.generate_test_scenarios(
            analysis,
            focus_areas=focus_areas,
            include_edge_cases=True
        )
        
        print(f"✅ Generated {len(scenarios)} custom scenarios")
        
        # Save scenarios to file
        import json
        output_file = "custom_ecommerce_scenarios.json"
        with open(output_file, 'w') as f:
            json.dump(scenarios, f, indent=2)
        
        print(f"💾 Scenarios saved to: {output_file}")
        
        # Optionally generate tests
        generate_tests = input("\nGenerate Playwright tests? (y/n): ").strip().lower()
        if generate_tests == 'y':
            await formgenius.generate_playwright_tests(
                scenarios,
                site_url,
                output_dir="./custom_ecommerce_tests"
            )
            print("✅ Tests generated in: ./custom_ecommerce_tests")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Select an e-commerce testing option:")
    print("1. Run comprehensive e-commerce testing")
    print("2. Generate custom scenarios for your site")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        asyncio.run(ecommerce_testing_example())
    elif choice == "2":
        asyncio.run(generate_custom_ecommerce_scenarios())
    else:
        print("Invalid choice. Please run the script again.")
