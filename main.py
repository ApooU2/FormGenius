#!/usr/bin/env python3
"""
FormGenius CLI - Command Line Interface

Main entry point for running FormGenius from the command line.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.formgenius import FormGenius
from src.core.test_runner import TestRunner


def setup_argparser():
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="FormGenius - AI-Powered Web Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze and generate tests for a website
  python main.py analyze https://example.com --output ./tests

  # Run generated tests
  python main.py run ./tests --workers 4

  # Quick test (analyze + generate + run)
  python main.py quick https://example.com

  # Generate tests with specific focus areas
  python main.py analyze https://shop.com --focus forms,checkout --security
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze website and generate tests')
    analyze_parser.add_argument('url', help='URL to analyze')
    analyze_parser.add_argument('--output', '-o', default='./generated_tests', 
                               help='Output directory for generated tests')
    analyze_parser.add_argument('--focus', help='Focus areas (comma-separated): forms,navigation,checkout,etc')
    analyze_parser.add_argument('--deep', action='store_true', help='Enable deep analysis')
    analyze_parser.add_argument('--security', action='store_true', help='Include security tests')
    analyze_parser.add_argument('--accessibility', action='store_true', help='Include accessibility tests')
    analyze_parser.add_argument('--performance', action='store_true', help='Include performance tests')
    analyze_parser.add_argument('--max-pages', type=int, default=10, help='Maximum pages to analyze')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run generated tests')
    run_parser.add_argument('test_dir', help='Directory containing tests')
    run_parser.add_argument('--output', '-o', default='./test_results', 
                           help='Output directory for test results')
    run_parser.add_argument('--workers', '-w', type=int, default=4, 
                           help='Number of parallel workers')
    run_parser.add_argument('--browser', '-b', default='chromium', 
                           choices=['chromium', 'firefox', 'webkit'],
                           help='Browser to use for testing')
    run_parser.add_argument('--headed', action='store_true', help='Run tests in headed mode')
    run_parser.add_argument('--timeout', '-t', type=int, default=30000, 
                           help='Test timeout in milliseconds')
    
    # Quick command
    quick_parser = subparsers.add_parser('quick', help='Quick test (analyze + generate + run)')
    quick_parser.add_argument('url', help='URL to test')
    quick_parser.add_argument('--output', '-o', default='./quick_tests', 
                             help='Output directory')
    quick_parser.add_argument('--workers', '-w', type=int, default=2, 
                             help='Number of parallel workers')
    quick_parser.add_argument('--browser', '-b', default='chromium', 
                             help='Browser to use')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('action', choices=['show', 'validate'], 
                              help='Configuration action')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    return parser


async def cmd_analyze(args):
    """Handle analyze command."""
    print(f"🔍 Analyzing website: {args.url}")
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        return 1
    
    # Setup configuration
    config = {
        "analysis": {
            "deep_analysis": args.deep,
            "max_pages": args.max_pages,
            "analyze_security": args.security,
            "analyze_accessibility": args.accessibility,
            "analyze_performance": args.performance
        }
    }
    
    if args.focus:
        focus_areas = [area.strip() for area in args.focus.split(',')]
        config["analysis"]["focus_areas"] = focus_areas
        print(f"📍 Focus areas: {', '.join(focus_areas)}")
    
    try:
        formgenius = FormGenius(config=config)
        
        # Analyze website
        print("📊 Analyzing website structure...")
        analysis = await formgenius.analyze_website(args.url)
        
        print("✅ Analysis completed")
        print(f"   Forms found: {len(analysis.get('forms', []))}")
        print(f"   Interactive elements: {len(analysis.get('interactive_elements', []))}")
        print(f"   User flows: {len(analysis.get('user_flows', []))}")
        
        # Generate scenarios
        print("🧪 Generating test scenarios...")
        scenarios = await formgenius.generate_test_scenarios(analysis)
        print(f"✅ Generated {len(scenarios)} test scenarios")
        
        # Generate tests
        print("⚡ Generating Playwright tests...")
        await formgenius.generate_playwright_tests(
            scenarios,
            args.url,
            output_dir=args.output
        )
        
        print(f"✅ Tests generated in: {args.output}")
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save analysis results
        analysis_file = output_path / "analysis_results.json"
        with open(analysis_file, 'w') as f:
            json.dump({
                'url': args.url,
                'analysis': analysis,
                'scenarios_count': len(scenarios)
            }, f, indent=2)
        
        print(f"📊 Analysis results saved to: {analysis_file}")
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1


async def cmd_run(args):
    """Handle run command."""
    test_dir = Path(args.test_dir)
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return 1
    
    print(f"🏃 Running tests from: {test_dir}")
    print(f"   Browser: {args.browser}")
    print(f"   Workers: {args.workers}")
    print(f"   Headed: {args.headed}")
    
    try:
        runner = TestRunner(
            output_dir=Path(args.output),
            max_workers=args.workers,
            timeout=args.timeout,
            headed=args.headed,
            browser=args.browser
        )
        
        result = await runner.run_test_suite(test_dir)
        
        print(f"\n📊 Test Results:")
        print(f"   Total: {result.total_tests}")
        print(f"   Passed: {result.passed}")
        print(f"   Failed: {result.failed}")
        print(f"   Skipped: {result.skipped}")
        print(f"   Success Rate: {result.success_rate:.1f}%")
        print(f"   Duration: {result.duration:.2f} seconds")
        
        print(f"\n📈 Reports generated in: {args.output}")
        
        return 0 if result.failed == 0 else 1
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


async def cmd_quick(args):
    """Handle quick command."""
    print(f"⚡ Quick test for: {args.url}")
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        return 1
    
    try:
        # Step 1: Analyze and generate
        formgenius = FormGenius()
        
        print("1️⃣ Analyzing website...")
        analysis = await formgenius.analyze_website(args.url)
        
        print("2️⃣ Generating scenarios...")  
        scenarios = await formgenius.generate_test_scenarios(analysis)
        
        print("3️⃣ Generating tests...")
        await formgenius.generate_playwright_tests(
            scenarios,
            args.url,
            output_dir=args.output
        )
        
        print(f"✅ Generated {len(scenarios)} test scenarios")
        
        # Step 2: Run tests
        print("4️⃣ Running tests...")
        runner = TestRunner(
            output_dir=Path(f"{args.output}_results"),
            max_workers=args.workers,
            browser=args.browser
        )
        
        result = await runner.run_test_suite(Path(args.output))
        
        print(f"\n🎉 Quick test completed!")
        print(f"   Success Rate: {result.success_rate:.1f}%")
        print(f"   Tests: {result.passed}/{result.total_tests} passed")
        
        return 0 if result.failed == 0 else 1
        
    except Exception as e:
        print(f"❌ Error in quick test: {e}")
        return 1


def cmd_config(args):
    """Handle config command."""
    if args.action == 'show':
        print("📋 FormGenius Configuration:")
        print(f"   Config file: ./config/formgenius.conf")
        print(f"   Python config: ./config/default_config.py")
        print(f"   Playwright config: ./config/playwright.config.js")
        
        # Check environment
        api_key = os.getenv('GEMINI_API_KEY')
        print(f"   Gemini API Key: {'✅ Set' if api_key else '❌ Not set'}")
        
    elif args.action == 'validate':
        print("🔍 Validating configuration...")
        
        # Check required files
        config_files = [
            './config/formgenius.conf',
            './config/default_config.py',
            './config/playwright.config.js'
        ]
        
        all_valid = True
        for config_file in config_files:
            if Path(config_file).exists():
                print(f"   ✅ {config_file}")
            else:
                print(f"   ❌ {config_file} (missing)")
                all_valid = False
        
        # Check API key
        if os.getenv('GEMINI_API_KEY'):
            print("   ✅ GEMINI_API_KEY environment variable")
        else:
            print("   ❌ GEMINI_API_KEY environment variable (missing)")
            all_valid = False
        
        print(f"\n{'✅ Configuration valid' if all_valid else '❌ Configuration issues found'}")
        return 0 if all_valid else 1
    
    return 0


def cmd_version(args):
    """Handle version command."""
    from src import get_info
    
    info = get_info()
    print(f"FormGenius {info['version']}")
    print(f"{info['description']}")
    print(f"Author: {info['author']}")
    return 0


async def main():
    """Main CLI entry point."""
    parser = setup_argparser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle commands
    if args.command == 'analyze':
        return await cmd_analyze(args)
    elif args.command == 'run':
        return await cmd_run(args)
    elif args.command == 'quick':
        return await cmd_quick(args)
    elif args.command == 'config':
        return cmd_config(args)
    elif args.command == 'version':
        return cmd_version(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)
