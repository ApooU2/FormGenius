"""
FormGenius - AI-Powered Automated Testing Framework

Main application that orchestrates web exploration, test generation, and execution
using Google Gemini AI and Playwright for comprehensive web application testing.
"""

import asyncio
import logging
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from playwright.async_api import async_playwright, Browser

from .gemini_client import GeminiClient
from ..agents.web_explorer import WebExplorer
from ..agents.test_strategist import TestStrategist
from ..agents.script_generator import ScriptGenerator
from ..agents.test_executor import TestExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('formgenius.log')
    ]
)

logger = logging.getLogger(__name__)


class FormGenius:
    """
    Main FormGenius application class.
    
    Coordinates the entire testing workflow from web exploration to test execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize FormGenius with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._load_default_config()
        
        # Initialize components
        self.gemini_client = GeminiClient()
        self.test_strategist = TestStrategist()
        self.script_generator = ScriptGenerator()
        self.test_executor = TestExecutor(
            test_directory=self.config.get('test_directory', 'generated_tests')
        )
        
        self.browser: Optional[Browser] = None
        self.session_data = {
            'session_id': self._generate_session_id(),
            'start_time': datetime.now(),
            'website_analysis': [],
            'test_strategy': {},
            'generated_scenarios': [],
            'test_files': {},
            'execution_results': {}
        }
    
    async def analyze_website(self, base_url: str, max_depth: int = 2, 
                            max_pages: int = 10) -> Dict[str, Any]:
        """
        Analyze a website structure and identify testing opportunities.
        
        Args:
            base_url: Starting URL for analysis
            max_depth: Maximum depth for link following
            max_pages: Maximum number of pages to analyze
            
        Returns:
            Website analysis results
        """
        logger.info(f"Starting website analysis for: {base_url}")
        
        try:
            # Launch browser for exploration
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.config.get('headless', True)
                )
                
                # Explore website structure
                async with WebExplorer(browser) as explorer:
                    website_analysis = await explorer.explore_website(
                        base_url, max_depth, max_pages
                    )
                
                await browser.close()
            
            # Enhance analysis with AI insights
            enhanced_analysis = []
            for page_analysis in website_analysis:
                if 'error' not in page_analysis:
                    # Get AI analysis of the page
                    ai_analysis = await self.gemini_client.analyze_webpage_structure(
                        page_analysis.get('dom_analysis', {}),
                        page_analysis.get('url', '')
                    )
                    
                    # Merge AI insights with page analysis
                    page_analysis['ai_insights'] = ai_analysis
                
                enhanced_analysis.append(page_analysis)
            
            self.session_data['website_analysis'] = enhanced_analysis
            
            logger.info(f"Website analysis completed. Analyzed {len(enhanced_analysis)} pages.")
            
            return {
                'success': True,
                'analysis': enhanced_analysis,
                'summary': self._create_analysis_summary(enhanced_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error during website analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_test_strategy(self, website_analysis: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive test strategy based on website analysis.
        
        Args:
            website_analysis: Website analysis results (uses session data if None)
            
        Returns:
            Test strategy
        """
        analysis = website_analysis or self.session_data['website_analysis']
        if not analysis:
            return {
                'success': False,
                'error': 'No website analysis available. Run analyze_website first.'
            }
        
        logger.info("Generating test strategy...")
        
        try:
            # Generate strategy using test strategist
            strategy = self.test_strategist.generate_test_strategy(analysis)
            
            # Enhance strategy with AI recommendations
            ai_recommendations = await self.gemini_client.analyze_test_results({
                'website_analysis': analysis,
                'initial_strategy': strategy
            })
            
            strategy['ai_recommendations'] = ai_recommendations
            
            self.session_data['test_strategy'] = strategy
            
            logger.info("Test strategy generation completed.")
            
            return {
                'success': True,
                'strategy': strategy
            }
            
        except Exception as e:
            logger.error(f"Error generating test strategy: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_test_scenarios(self, website_analysis: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate detailed test scenarios for all analyzed pages.
        
        Args:
            website_analysis: Website analysis results (uses session data if None)
            
        Returns:
            Generated test scenarios
        """
        analysis = website_analysis or self.session_data['website_analysis']
        if not analysis:
            return {
                'success': False,
                'error': 'No website analysis available. Run analyze_website first.'
            }
        
        logger.info("Generating test scenarios...")
        
        try:
            all_scenarios = []
            
            # Generate scenarios for each page
            for page_analysis in analysis:
                if 'error' in page_analysis:
                    continue
                
                # Generate scenarios using test strategist
                page_scenarios = self.test_strategist.generate_test_scenarios(page_analysis)
                
                # Enhance scenarios with AI-generated ones
                ai_scenarios = await self.gemini_client.generate_test_scenarios(page_analysis)
                
                # Merge and deduplicate scenarios
                combined_scenarios = page_scenarios + ai_scenarios
                all_scenarios.extend(combined_scenarios)
            
            # Prioritize scenarios
            prioritized_scenarios = self.test_strategist.prioritize_test_scenarios(
                all_scenarios, analysis
            )
            
            self.session_data['generated_scenarios'] = prioritized_scenarios
            
            logger.info(f"Generated {len(prioritized_scenarios)} test scenarios.")
            
            return {
                'success': True,
                'scenarios': prioritized_scenarios,
                'summary': self._create_scenarios_summary(prioritized_scenarios)
            }
            
        except Exception as e:
            logger.error(f"Error generating test scenarios: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_playwright_tests(self, scenarios: List[Dict[str, Any]], 
                                      base_url: str, output_dir: str = "./generated_tests") -> Dict[str, Any]:
        """
        Generate Playwright test files from test scenarios.
        
        Args:
            scenarios: Test scenarios to convert to Playwright tests
            base_url: Base URL for the website being tested
            output_dir: Directory to save generated test files
            
        Returns:
            Results of test generation including file paths and summary
        """
        if not scenarios:
            return {
                'success': False,
                'error': 'No test scenarios provided for Playwright test generation.'
            }
        
        logger.info(f"Generating Playwright tests for {len(scenarios)} scenarios...")
        
        try:
            # Import the PlaywrightCodeGenerator
            from ..generators.playwright_codegen import PlaywrightCodeGenerator
            
            # Create code generator
            code_generator = PlaywrightCodeGenerator(output_dir=output_dir)
            
            # Get website analysis from session data or create basic analysis
            analysis = self.session_data.get('website_analysis', [])
            
            # Convert dictionary scenarios to objects expected by PlaywrightCodeGenerator
            scenario_objects = []
            for scenario_dict in scenarios:
                scenario_obj = type('Scenario', (), {})()
                scenario_obj.name = scenario_dict.get('name', 'unnamed_test')
                scenario_obj.description = scenario_dict.get('description', 'Generated test scenario')
                scenario_obj.steps = scenario_dict.get('steps', [])
                scenario_obj.priority = scenario_dict.get('priority', 'medium')
                scenario_obj.category = scenario_dict.get('category', 'functional')
                scenario_obj.test_type = scenario_dict.get('type', 'functional')
                scenario_obj.expected_result = scenario_dict.get('expected_result', 'Test should pass')
                scenario_objects.append(scenario_obj)
            
            # Create scenario sets for the code generator
            scenario_sets = [
                type('ScenarioSet', (), {
                    'name': 'FormGenius Generated Tests',
                    'description': 'Comprehensive test scenarios generated by FormGenius AI',
                    'scenarios': scenario_objects
                })()
            ]
            
            # Create basic DOM and element analysis for the code generator
            dom_analysis = {
                'url': base_url,
                'title': 'Test Target Website',
                'forms': [],
                'interactive_elements': [],
                'navigation_elements': []
            }
            
            element_analysis = {
                'element_groups': [],
                'interactive_elements': []
            }
            
            # If we have analysis data, use it
            if analysis:
                for page_data in analysis:
                    if 'forms' in page_data:
                        dom_analysis['forms'].extend(page_data['forms'])
                    if 'interactive_elements' in page_data:
                        dom_analysis['interactive_elements'].extend(page_data['interactive_elements'])
                        element_analysis['interactive_elements'].extend(page_data['interactive_elements'])
            
            # Generate the test suite
            test_suite = code_generator.generate_test_suite(
                scenario_sets=scenario_sets,
                dom_analysis=dom_analysis,
                element_analysis=element_analysis,
                base_url=base_url
            )
            
            # Get generation summary
            summary = code_generator.get_generation_summary(test_suite)
            
            self.session_data['test_files'] = {
                tf.file_path: tf.content for tf in test_suite.test_files
            }
            
            logger.info(f"Successfully generated Playwright test suite: {summary['total_test_files']} files, {summary['total_tests']} tests")
            
            return {
                'success': True,
                'test_suite': test_suite,
                'summary': summary,
                'output_directory': output_dir,
                'files_generated': summary['files_generated']
            }
            
        except Exception as e:
            logger.error(f"Error generating Playwright tests: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_test_scripts(self, scenarios: List[Dict[str, Any]] = None,
                                  website_analysis: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate Playwright test scripts from test scenarios.
        
        Args:
            scenarios: Test scenarios (uses session data if None)
            website_analysis: Website analysis results (uses session data if None)
            
        Returns:
            Generated test scripts
        """
        test_scenarios = scenarios or self.session_data['generated_scenarios']
        analysis = website_analysis or self.session_data['website_analysis']
        
        if not test_scenarios:
            return {
                'success': False,
                'error': 'No test scenarios available. Run generate_test_scenarios first.'
            }
        
        if not analysis:
            return {
                'success': False,
                'error': 'No website analysis available. Run analyze_website first.'
            }
        
        logger.info("Generating test scripts...")
        
        try:
            # Generate test suite
            test_files = self.script_generator.generate_test_suite(test_scenarios, analysis)
            
            # Enhance scripts with AI-generated code
            enhanced_files = {}
            for filename, content in test_files.items():
                if filename.startswith('test_') and filename.endswith('.py'):
                    # Get AI-enhanced version
                    enhanced_content = await self._enhance_test_script_with_ai(
                        content, test_scenarios, analysis
                    )
                    enhanced_files[filename] = enhanced_content
                else:
                    enhanced_files[filename] = content
            
            self.session_data['test_files'] = enhanced_files
            
            logger.info(f"Generated {len(enhanced_files)} test files.")
            
            return {
                'success': True,
                'test_files': enhanced_files,
                'file_count': len(enhanced_files)
            }
            
        except Exception as e:
            logger.error(f"Error generating test scripts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_tests(self, test_filter: str = "", headless: bool = True,
                          browser: str = "chromium", max_workers: int = 1) -> Dict[str, Any]:
        """
        Execute the generated test scripts.
        
        Args:
            test_filter: Pytest filter expression
            headless: Run tests in headless mode
            browser: Browser to use
            max_workers: Number of parallel workers
            
        Returns:
            Test execution results
        """
        test_files = self.session_data.get('test_files', {})
        if not test_files:
            return {
                'success': False,
                'error': 'No test files available. Run generate_test_scripts first.'
            }
        
        logger.info("Executing tests...")
        
        try:
            # Write test files to disk
            write_success = await self.test_executor.write_test_files(test_files)
            if not write_success:
                return {
                    'success': False,
                    'error': 'Failed to write test files to disk'
                }
            
            # Execute tests
            execution_results = await self.test_executor.execute_tests(
                test_filter=test_filter,
                headless=headless,
                browser=browser,
                max_workers=max_workers
            )
            
            # Analyze results with AI
            if execution_results.get('success'):
                ai_analysis = await self.gemini_client.analyze_test_results(execution_results)
                execution_results['ai_analysis'] = ai_analysis
            
            self.session_data['execution_results'] = execution_results
            
            logger.info("Test execution completed.")
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Error executing tests: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def full_analysis_and_testing(self, base_url: str, **kwargs) -> Dict[str, Any]:
        """
        Run the complete analysis and testing workflow.
        
        Args:
            base_url: URL to analyze and test
            **kwargs: Additional configuration options
            
        Returns:
            Complete workflow results
        """
        logger.info(f"Starting full analysis and testing workflow for: {base_url}")
        
        workflow_results = {
            'session_id': self.session_data['session_id'],
            'base_url': base_url,
            'start_time': self.session_data['start_time'].isoformat(),
            'steps': {}
        }
        
        try:
            # Step 1: Analyze website
            analysis_result = await self.analyze_website(
                base_url,
                max_depth=kwargs.get('max_depth', 2),
                max_pages=kwargs.get('max_pages', 10)
            )
            workflow_results['steps']['analysis'] = analysis_result
            
            if not analysis_result['success']:
                return workflow_results
            
            # Step 2: Generate test strategy
            strategy_result = await self.generate_test_strategy()
            workflow_results['steps']['strategy'] = strategy_result
            
            if not strategy_result['success']:
                return workflow_results
            
            # Step 3: Generate test scenarios
            scenarios_result = await self.generate_test_scenarios()
            workflow_results['steps']['scenarios'] = scenarios_result
            
            if not scenarios_result['success']:
                return workflow_results
            
            # Step 4: Generate test scripts
            scripts_result = await self.generate_test_scripts()
            workflow_results['steps']['scripts'] = scripts_result
            
            if not scripts_result['success']:
                return workflow_results
            
            # Step 5: Execute tests
            execution_result = await self.execute_tests(
                headless=kwargs.get('headless', True),
                browser=kwargs.get('browser', 'chromium'),
                max_workers=kwargs.get('max_workers', 1)
            )
            workflow_results['steps']['execution'] = execution_result
            
            # Generate final report
            workflow_results['final_report'] = await self.generate_session_report()
            workflow_results['end_time'] = datetime.now().isoformat()
            workflow_results['success'] = True
            
            logger.info("Full workflow completed successfully.")
            
            return workflow_results
            
        except Exception as e:
            logger.error(f"Error in full workflow: {e}")
            workflow_results['error'] = str(e)
            workflow_results['success'] = False
            workflow_results['end_time'] = datetime.now().isoformat()
            return workflow_results
    
    async def generate_session_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report for the current session.
        
        Returns:
            Session report
        """
        report = {
            'session_id': self.session_data['session_id'],
            'session_duration': (datetime.now() - self.session_data['start_time']).total_seconds(),
            'website_analysis_summary': self._create_analysis_summary(
                self.session_data.get('website_analysis', [])
            ),
            'test_strategy_summary': self._create_strategy_summary(
                self.session_data.get('test_strategy', {})
            ),
            'scenarios_summary': self._create_scenarios_summary(
                self.session_data.get('generated_scenarios', [])
            ),
            'execution_summary': self._create_execution_summary(
                self.session_data.get('execution_results', {})
            ),
            'recommendations': self._generate_session_recommendations(),
            'artifacts': await self.test_executor.get_test_artifacts()
        }
        
        return report
    
    async def _enhance_test_script_with_ai(self, content: str, scenarios: List[Dict[str, Any]],
                                         analysis: List[Dict[str, Any]]) -> str:
        """Enhance test script content with AI improvements."""
        try:
            # Find relevant scenarios for this script
            relevant_scenarios = []
            for scenario in scenarios[:3]:  # Limit to avoid token limits
                relevant_scenarios.append({
                    'name': scenario.get('name'),
                    'description': scenario.get('description'),
                    'category': scenario.get('category')
                })
            
            # Get AI enhancement
            enhanced_script = await self.gemini_client.generate_playwright_code(
                {'scenarios': relevant_scenarios}, 
                {'analysis_summary': 'Multi-page web application'}
            )
            
            # If AI enhancement is valid, merge with original
            if enhanced_script and 'error' not in enhanced_script.lower():
                return content  # For now, return original content
                # TODO: Implement smart merging of AI enhancements
            
            return content
            
        except Exception as e:
            logger.debug(f"Error enhancing script with AI: {e}")
            return content
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            'headless': True,
            'browser': 'chromium',
            'max_depth': 2,
            'max_pages': 10,
            'test_directory': 'generated_tests',
            'results_directory': 'test_results',
            'default_timeout': 30000,
            'slowmo_ms': 100
        }
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def _create_analysis_summary(self, analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of website analysis."""
        if not analysis:
            return {}
        
        total_pages = len(analysis)
        successful_analysis = len([p for p in analysis if 'error' not in p])
        total_forms = sum(len(p.get('forms', [])) for p in analysis if 'error' not in p)
        total_interactive = sum(len(p.get('interactive_elements', [])) for p in analysis if 'error' not in p)
        
        page_types = {}
        for page in analysis:
            if 'error' not in page:
                page_type = page.get('page_type', 'unknown')
                page_types[page_type] = page_types.get(page_type, 0) + 1
        
        return {
            'total_pages': total_pages,
            'successful_analysis': successful_analysis,
            'total_forms': total_forms,
            'total_interactive_elements': total_interactive,
            'page_types': page_types
        }
    
    def _create_strategy_summary(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of test strategy."""
        if not strategy:
            return {}
        
        return {
            'test_categories': strategy.get('test_categories', []),
            'complexity_score': strategy.get('overview', {}).get('complexity_score', 0),
            'estimated_duration': strategy.get('overview', {}).get('recommended_test_duration', {}),
            'risk_assessment': strategy.get('risk_assessment', {})
        }
    
    def _create_scenarios_summary(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of test scenarios."""
        if not scenarios:
            return {}
        
        total_scenarios = len(scenarios)
        categories = {}
        priorities = {}
        
        for scenario in scenarios:
            category = scenario.get('category', 'unknown')
            priority = scenario.get('priority', 'unknown')
            
            categories[category] = categories.get(category, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return {
            'total_scenarios': total_scenarios,
            'by_category': categories,
            'by_priority': priorities
        }
    
    def _create_execution_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of test execution."""
        if not results:
            return {}
        
        return {
            'success': results.get('success', False),
            'total_tests': results.get('total_tests', 0),
            'passed_tests': results.get('passed_tests', 0),
            'failed_tests': results.get('failed_tests', 0),
            'execution_time': results.get('execution_time', 0),
            'pass_rate': results.get('passed_tests', 0) / max(results.get('total_tests', 1), 1) * 100
        }
    
    def _generate_session_recommendations(self) -> List[str]:
        """Generate recommendations based on session data."""
        recommendations = []
        
        analysis = self.session_data.get('website_analysis', [])
        scenarios = self.session_data.get('generated_scenarios', [])
        results = self.session_data.get('execution_results', {})
        
        # Analysis recommendations
        if len(analysis) < 5:
            recommendations.append("Consider analyzing more pages for comprehensive test coverage")
        
        # Scenario recommendations
        if len(scenarios) < 10:
            recommendations.append("Generate more test scenarios to improve coverage")
        
        # Execution recommendations
        if results.get('failed_tests', 0) > 0:
            recommendations.append("Review and fix failed tests to improve reliability")
        
        if results.get('execution_time', 0) > 600:  # 10 minutes
            recommendations.append("Consider optimizing tests or running in parallel to reduce execution time")
        
        return recommendations


# CLI Interface
async def main():
    """Main CLI interface for FormGenius."""
    import argparse
    
    parser = argparse.ArgumentParser(description='FormGenius - AI-Powered Automated Testing Framework')
    parser.add_argument('url', help='URL to analyze and test')
    parser.add_argument('--max-depth', type=int, default=2, help='Maximum depth for link following')
    parser.add_argument('--max-pages', type=int, default=10, help='Maximum number of pages to analyze')
    parser.add_argument('--headless', action='store_true', default=True, help='Run tests in headless mode')
    parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], default='chromium', help='Browser to use')
    parser.add_argument('--workers', type=int, default=1, help='Number of parallel test workers')
    parser.add_argument('--output', default='report.json', help='Output file for results')
    
    args = parser.parse_args()
    
    # Initialize FormGenius
    formgenius = FormGenius()
    
    try:
        # Run full workflow
        results = await formgenius.full_analysis_and_testing(
            args.url,
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            headless=args.headless,
            browser=args.browser,
            max_workers=args.workers
        )
        
        # Save results to file
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"FormGenius analysis and testing completed!")
        print(f"Results saved to: {args.output}")
        
        # Print summary
        if results.get('success'):
            execution = results.get('steps', {}).get('execution', {})
            print(f"Tests executed: {execution.get('total_tests', 0)}")
            print(f"Tests passed: {execution.get('passed_tests', 0)}")
            print(f"Tests failed: {execution.get('failed_tests', 0)}")
        else:
            print(f"Workflow failed: {results.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
