#!/usr/bin/env python3
"""
Form testing example for FormGenius.

This script demonstrates how to use FormGenius specifically for
comprehensive form testing across different types of forms.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.formgenius import FormGenius
from src.core.test_runner import TestRunner


async def comprehensive_form_testing():
    """Comprehensive form testing across different form types."""
    
    print("📝 FormGenius Comprehensive Form Testing")
    print("=" * 45)
    
    # Form-specific configuration
    form_config = {
        "analysis": {
            "deep_form_analysis": True,
            "analyze_validation_rules": True,
            "detect_field_types": True,
            "analyze_form_accessibility": True,
            "check_csrf_protection": True
        },
        "test_scenarios": {
            "include_validation_tests": True,
            "include_boundary_tests": True,
            "include_xss_tests": True,
            "include_sql_injection_tests": True,
            "include_accessibility_tests": True,
            "test_all_field_combinations": True
        },
        "data_generation": {
            "generate_invalid_data": True,
            "generate_edge_cases": True,
            "generate_malicious_inputs": True,
            "generate_accessibility_test_data": True
        }
    }
    
    formgenius = FormGenius(config=form_config)
    
    # Different types of forms for comprehensive testing
    form_test_sites = [
        {
            "name": "Basic Contact Form",
            "url": "https://httpbin.org/forms/post",
            "form_type": "contact",
            "expected_fields": ["custname", "custtel", "custemail", "size"]
        },
        {
            "name": "Registration Form",
            "url": "https://the-internet.herokuapp.com/signup",
            "form_type": "registration",
            "expected_fields": ["email", "password"]
        },
        {
            "name": "Login Form",
            "url": "https://the-internet.herokuapp.com/login",
            "form_type": "login",
            "expected_fields": ["username", "password"]
        },
        {
            "name": "Dynamic Controls",
            "url": "https://the-internet.herokuapp.com/dynamic_controls",
            "form_type": "dynamic",
            "expected_fields": ["checkbox", "input"]
        }
    ]
    
    print(f"Testing {len(form_test_sites)} different form types...\n")
    
    test_results = []
    
    for site in form_test_sites:
        print(f"📋 Testing: {site['name']}")
        print(f"   URL: {site['url']}")
        print(f"   Type: {site['form_type']}")
        
        try:
            # Step 1: Analyze form structure
            print("   🔍 Analyzing form structure...")
            analysis = await formgenius.analyze_website(
                site['url'],
                focus_on_forms=True
            )
            
            # Extract form information
            forms = analysis.get('forms', [])
            print(f"   📊 Found {len(forms)} forms")
            
            if forms:
                for i, form in enumerate(forms):
                    fields = form.get('fields', [])
                    print(f"      Form {i+1}: {len(fields)} fields")
                    for field in fields[:3]:  # Show first 3 fields
                        print(f"        - {field.get('name', 'unnamed')}: {field.get('type', 'unknown')}")
            
            # Step 2: Generate form-specific test scenarios
            print("   🧪 Generating form test scenarios...")
            scenarios = await formgenius.generate_form_test_scenarios(
                analysis,
                form_type=site['form_type'],
                include_security_tests=True
            )
            
            print(f"   ✅ Generated {len(scenarios)} form test scenarios")
            
            # Categorize scenarios
            scenario_categories = {}
            for scenario in scenarios:
                category = scenario.get('category', 'general')
                scenario_categories[category] = scenario_categories.get(category, 0) + 1
            
            for category, count in scenario_categories.items():
                print(f"      - {category}: {count} tests")
            
            # Step 3: Generate comprehensive test code
            print("   ⚡ Generating form test code...")
            site_name = site['name'].lower().replace(' ', '_')
            test_dir = f"./form_tests_{site_name}"
            
            await formgenius.generate_playwright_tests(
                scenarios,
                site['url'],
                output_dir=test_dir,
                test_type="form_testing",
                include_data_driven_tests=True
            )
            
            print(f"   ✅ Test code generated in: {test_dir}")
            
            # Step 4: Run validation tests
            print("   🔄 Running form validation tests...")
            
            runner = TestRunner(
                output_dir=Path(f"./form_results_{site_name}"),
                max_workers=1,  # Sequential for form testing
                timeout=30000,
                browser="chromium"
            )
            
            # Run validation-specific tests
            validation_pattern = "*validation*.py"
            result = await runner.run_test_suite(
                Path(test_dir),
                test_pattern=validation_pattern
            )
            
            print(f"   📈 Validation Results: {result.passed}/{result.total_tests} passed")
            
            test_results.append({
                'site': site['name'],
                'form_type': site['form_type'],
                'forms_found': len(forms),
                'scenarios': len(scenarios),
                'test_result': result
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {site['name']}: {e}")
            continue
        
        print()  # Empty line for readability
    
    # Generate comprehensive report
    print("📊 Form Testing Summary Report")
    print("=" * 35)
    
    total_forms = sum(r['forms_found'] for r in test_results)
    total_scenarios = sum(r['scenarios'] for r in test_results)
    total_tests = sum(r['test_result'].total_tests for r in test_results)
    total_passed = sum(r['test_result'].passed for r in test_results)
    
    print(f"Sites Tested: {len(test_results)}")
    print(f"Total Forms Analyzed: {total_forms}")
    print(f"Total Scenarios Generated: {total_scenarios}")
    print(f"Total Tests Executed: {total_tests}")
    print(f"Overall Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    print("\nDetailed Results by Form Type:")
    for result in test_results:
        print(f"  {result['site']} ({result['form_type']}):")
        print(f"    Forms: {result['forms_found']}")
        print(f"    Scenarios: {result['scenarios']}")
        print(f"    Tests: {result['test_result'].total_tests}")
        print(f"    Success: {result['test_result'].success_rate:.1f}%")
    
    print("\n🎉 Comprehensive form testing completed!")


async def single_form_deep_analysis():
    """Perform deep analysis on a single form."""
    
    print("🔬 Single Form Deep Analysis")
    print("=" * 30)
    
    # Get user input
    form_url = input("Enter the URL containing the form to analyze: ").strip()
    if not form_url:
        print("No URL provided. Exiting.")
        return
    
    print(f"\n🎯 Analyzing form at: {form_url}")
    
    # Deep analysis configuration
    deep_config = {
        "analysis": {
            "deep_form_analysis": True,
            "analyze_validation_rules": True,
            "detect_field_dependencies": True,
            "analyze_javascript_validation": True,
            "check_accessibility_compliance": True,
            "security_vulnerability_scan": True
        }
    }
    
    formgenius = FormGenius(config=deep_config)
    
    try:
        # Comprehensive analysis
        print("🔍 Performing deep form analysis...")
        analysis = await formgenius.analyze_website(form_url, deep_analysis=True)
        
        forms = analysis.get('forms', [])
        if not forms:
            print("❌ No forms found on the page.")
            return
        
        print(f"✅ Found {len(forms)} form(s)")
        
        # Detailed form information
        for i, form in enumerate(forms):
            print(f"\n📋 Form {i+1} Analysis:")
            print(f"   Method: {form.get('method', 'Unknown')}")
            print(f"   Action: {form.get('action', 'Unknown')}")
            print(f"   Fields: {len(form.get('fields', []))}")
            
            # Field details
            fields = form.get('fields', [])
            print(f"   \n   Field Details:")
            for field in fields:
                print(f"     - {field.get('name', 'unnamed')}:")
                print(f"       Type: {field.get('type', 'unknown')}")
                print(f"       Required: {field.get('required', False)}")
                print(f"       Validation: {field.get('validation_rules', 'None')}")
                if field.get('accessibility_issues'):
                    print(f"       Accessibility Issues: {len(field['accessibility_issues'])}")
        
        # Generate comprehensive test scenarios
        print(f"\n🧪 Generating comprehensive test scenarios...")
        scenarios = await formgenius.generate_form_test_scenarios(
            analysis,
            include_security_tests=True,
            include_accessibility_tests=True,
            include_performance_tests=True
        )
        
        print(f"✅ Generated {len(scenarios)} comprehensive scenarios")
        
        # Scenario breakdown
        scenario_types = {}
        for scenario in scenarios:
            category = scenario.get('category', 'general')
            scenario_types[category] = scenario_types.get(category, 0) + 1
        
        print("\nScenario Breakdown:")
        for category, count in scenario_types.items():
            print(f"  {category}: {count} scenarios")
        
        # Generate test code
        print(f"\n⚡ Generating comprehensive test suite...")
        await formgenius.generate_playwright_tests(
            scenarios,
            form_url,
            output_dir="./deep_form_analysis_tests",
            include_page_objects=True,
            include_data_fixtures=True,
            include_accessibility_tests=True
        )
        
        print("✅ Comprehensive test suite generated in: ./deep_form_analysis_tests")
        
        # Optional: Run immediate validation
        run_tests = input("\nRun immediate validation tests? (y/n): ").strip().lower()
        if run_tests == 'y':
            runner = TestRunner(
                output_dir=Path("./deep_analysis_results"),
                max_workers=1,
                headed=True  # Show browser for deep analysis
            )
            
            result = await runner.run_test_suite(Path("./deep_form_analysis_tests"))
            print(f"\n📈 Validation Results: {result.passed}/{result.total_tests} passed")
        
    except Exception as e:
        print(f"❌ Error during deep analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Select a form testing option:")
    print("1. Comprehensive form testing across multiple sites")
    print("2. Deep analysis of a single form")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        asyncio.run(comprehensive_form_testing())
    elif choice == "2":
        asyncio.run(single_form_deep_analysis())
    else:
        print("Invalid choice. Please run the script again.")
