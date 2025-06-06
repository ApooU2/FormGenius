#!/usr/bin/env python3
"""
FormGenius - AI-powered web form automation tool
Main entry point for command-line usage
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from formgenius.core.agent import FormGeniusAgent
from formgenius.core.config import Config
from formgenius.core.reporter import TestReporter


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('formgenius.log')
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='FormGenius - AI-powered web form automation tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fill a single form
  python main.py fill --url https://example.com/form --config config.yaml

  # Fill multiple forms from a file
  python main.py batch --urls-file urls.txt --config config.yaml

  # Test form validation
  python main.py test --url https://example.com/form --config config.yaml

  # Fill Power Apps form
  python main.py power-apps --url https://apps.powerapps.com/... --config config.yaml
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='reports',
        help='Output directory for reports (default: reports)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fill single form command
    fill_parser = subparsers.add_parser('fill', help='Fill a single form')
    fill_parser.add_argument('--url', required=True, help='URL of the form to fill')
    fill_parser.add_argument('--submit', action='store_true', help='Submit the form after filling')
    fill_parser.add_argument('--scenario', choices=['valid', 'invalid', 'edge'], 
                           default='valid', help='Data generation scenario')
    
    # Batch fill command
    batch_parser = subparsers.add_parser('batch', help='Fill multiple forms')
    batch_parser.add_argument('--urls-file', required=True, help='File containing URLs (one per line)')
    batch_parser.add_argument('--submit', action='store_true', help='Submit forms after filling')
    batch_parser.add_argument('--scenario', choices=['valid', 'invalid', 'edge'], 
                            default='valid', help='Data generation scenario')
    
    # Test form validation command
    test_parser = subparsers.add_parser('test', help='Test form validation')
    test_parser.add_argument('--url', required=True, help='URL of the form to test')
    test_parser.add_argument('--scenarios', nargs='+', 
                           choices=['valid', 'invalid', 'edge'], 
                           default=['valid', 'invalid', 'edge'],
                           help='Test scenarios to run')
    
    # Power Apps command
    power_parser = subparsers.add_parser('power-apps', help='Fill Power Apps form')
    power_parser.add_argument('--url', required=True, help='URL of the Power Apps form')
    power_parser.add_argument('--submit', action='store_true', help='Submit the form after filling')
    power_parser.add_argument('--scenario', choices=['valid', 'invalid', 'edge'], 
                            default='valid', help='Data generation scenario')
    
    return parser.parse_args()


async def fill_single_form(agent: FormGeniusAgent, url: str, submit: bool, scenario: str) -> dict:
    """Fill a single form"""
    logging.info(f"Filling form at: {url}")
    
    # Convert old CLI parameters to new method signature
    test_scenarios = [scenario] if scenario else ["valid"]
    
    result = await agent.fill_form(
        url=url,
        test_scenarios=test_scenarios
    )
    
    logging.info(f"Form filling completed: {result.get('status', 'completed')}")
    return result


async def fill_multiple_forms(agent: FormGeniusAgent, urls_file: str, submit: bool, scenario: str) -> List[dict]:
    """Fill multiple forms from a file"""
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"URLs file not found: {urls_file}")
        return []
    
    logging.info(f"Filling {len(urls)} forms from {urls_file}")
    
    # Convert old CLI parameters to new method signature
    test_scenarios = [scenario] if scenario else ["valid"]
    
    result = await agent.batch_fill_forms(
        urls=urls,
        test_scenarios=test_scenarios
    )
    
    logging.info(f"Batch filling completed: {len(urls)} forms processed")
    return [result]  # Return as list for consistency


async def test_form_validation(agent: FormGeniusAgent, url: str, scenarios: List[str]) -> dict:
    """Test form validation with multiple scenarios"""
    logging.info(f"Testing form validation at: {url}")
    
    result = await agent.test_form_validation(
        url=url,
        validation_scenarios=scenarios
    )
    
    logging.info(f"Form validation testing completed")
    return result


async def fill_power_apps_form(agent: FormGeniusAgent, url: str, submit: bool, scenario: str) -> dict:
    """Fill a Power Apps form"""
    logging.info(f"Filling Power Apps form at: {url}")
    
    # Convert old CLI parameters to new method signature
    test_scenarios = [scenario] if scenario else ["valid"]
    
    result = await agent.fill_power_apps_form(
        app_url=url,
        test_scenarios=test_scenarios
    )
    
    logging.info(f"Power Apps form filling completed: {result.get('status', 'completed')}")
    return result


async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Load configuration
    try:
        config = Config.from_yaml(args.config)
        if args.headless:
            config.headless = True
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Initialize agent
    try:
        agent = FormGeniusAgent(config)
        # No initialization method needed
    except Exception as e:
        logging.error(f"Failed to create FormGenius agent: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        results = []
        
        if args.command == 'fill':
            result = await fill_single_form(agent, args.url, args.submit, args.scenario)
            results = [result]
            
        elif args.command == 'batch':
            results = await fill_multiple_forms(agent, args.urls_file, args.submit, args.scenario)
            
        elif args.command == 'test':
            result = await test_form_validation(agent, args.url, args.scenarios)
            results = [result]
            
        elif args.command == 'power-apps':
            result = await fill_power_apps_form(agent, args.url, args.submit, args.scenario)
            results = [result]
            
        else:
            logging.error("No command specified. Use --help for usage information.")
            sys.exit(1)
        
        # Generate reports
        reporter = TestReporter(config)
        
        if len(results) == 1:
            # Single form report
            report_data = await reporter.generate_report(results[0])
            logging.info(f"Report generated: {report_data.get('html_file', 'report.html')}")
        else:
            # Batch report - combine results
            combined_results = {
                'status': 'completed',
                'summary': {
                    'total_forms': len(results),
                    'successful': sum(1 for r in results if r.get('status') == 'completed'),
                    'failed': sum(1 for r in results if r.get('status') == 'failed'),
                },
                'results': results
            }
            report_data = await reporter.generate_report(combined_results)
            logging.info(f"Batch report generated: {report_data.get('html_file', 'report.html')}")
        
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Operation failed: {e}")
        sys.exit(1)
    # No cleanup needed - FormGeniusAgent doesn't have a close() method


if __name__ == '__main__':
    asyncio.run(main())
