"""
Test Executor Agent for FormGenius.
Responsible for running generated test scripts, managing test execution, and collecting results.
"""

import asyncio
import logging
import subprocess
import json
import os
import shutil
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class TestExecutor:
    """Agent for executing generated test scripts and managing test runs."""
    
    def __init__(self, test_directory: str = "generated_tests"):
        """
        Initialize the test executor.
        
        Args:
            test_directory: Directory where test files are stored
        """
        self.test_directory = Path(test_directory)
        self.results_directory = Path("test_results")
        self.artifacts_directory = Path("test_artifacts")
        
        # Create directories if they don't exist
        self.test_directory.mkdir(exist_ok=True)
        self.results_directory.mkdir(exist_ok=True)
        self.artifacts_directory.mkdir(exist_ok=True)
        
        self.execution_history = []
        self.current_run_id = None
    
    async def write_test_files(self, test_files: Dict[str, str]) -> bool:
        """
        Write generated test files to the test directory.
        
        Args:
            test_files: Dictionary mapping file names to content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear existing test files
            if self.test_directory.exists():
                for file_path in self.test_directory.glob("test_*.py"):
                    file_path.unlink()
                
                # Also remove conftest.py and pytest.ini if they exist
                conftest_path = self.test_directory / "conftest.py"
                if conftest_path.exists():
                    conftest_path.unlink()
                
                pytest_ini_path = self.test_directory / "pytest.ini"
                if pytest_ini_path.exists():
                    pytest_ini_path.unlink()
            
            # Write new test files
            for filename, content in test_files.items():
                file_path = self.test_directory / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Written test file: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error writing test files: {e}")
            return False
    
    async def execute_tests(self, test_filter: str = "", headless: bool = True, 
                          browser: str = "chromium", max_workers: int = 1) -> Dict[str, Any]:
        """
        Execute the generated tests using pytest.
        
        Args:
            test_filter: Pytest filter expression (e.g., "-k test_login")
            headless: Run tests in headless mode
            browser: Browser to use (chromium, firefox, webkit)
            max_workers: Number of parallel workers
            
        Returns:
            Test execution results
        """
        self.current_run_id = self._generate_run_id()
        run_directory = self.results_directory / self.current_run_id
        run_directory.mkdir(exist_ok=True)
        
        try:
            # Prepare environment variables
            env = os.environ.copy()
            env.update({
                'HEADLESS': str(headless).lower(),
                'BROWSER': browser,
                'SLOWMO_MS': '100',
                'DEFAULT_TIMEOUT': '30000'
            })
            
            # Prepare pytest command
            cmd = [
                'python', '-m', 'pytest',
                str(self.test_directory),
                '-v',
                '--tb=short',
                f'--junit-xml={run_directory}/results.xml',
                f'--html={run_directory}/report.html',
                '--self-contained-html'
            ]
            
            # Add test filter if provided
            if test_filter:
                cmd.extend(['-k', test_filter])
            
            # Add parallel execution if multiple workers
            if max_workers > 1:
                cmd.extend(['-n', str(max_workers)])
            
            logger.info(f"Executing tests with command: {' '.join(cmd)}")
            
            # Execute tests
            start_time = datetime.now()
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=os.getcwd(),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Parse results
            results = await self._parse_test_results(
                run_directory, stdout.decode(), stderr.decode(), 
                process.returncode, execution_time
            )
            
            # Save execution summary
            await self._save_execution_summary(run_directory, results)
            
            # Add to execution history
            self.execution_history.append({
                'run_id': self.current_run_id,
                'timestamp': start_time.isoformat(),
                'execution_time': execution_time,
                'results': results
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing tests: {e}")
            return {
                'success': False,
                'error': str(e),
                'run_id': self.current_run_id
            }
    
    async def execute_single_test(self, test_file: str, test_method: str = "", 
                                browser: str = "chromium", headless: bool = True) -> Dict[str, Any]:
        """
        Execute a single test file or test method.
        
        Args:
            test_file: Name of the test file to execute
            test_method: Specific test method to run (optional)
            browser: Browser to use
            headless: Run in headless mode
            
        Returns:
            Test execution results
        """
        test_path = self.test_directory / test_file
        if not test_path.exists():
            return {
                'success': False,
                'error': f'Test file not found: {test_file}'
            }
        
        # Build test specifier
        test_specifier = str(test_path)
        if test_method:
            test_specifier += f"::{test_method}"
        
        return await self.execute_tests(
            test_filter=f"--no-header {test_specifier}",
            headless=headless,
            browser=browser,
            max_workers=1
        )
    
    async def execute_by_category(self, category: str, priority: str = "", 
                                browser: str = "chromium", headless: bool = True) -> Dict[str, Any]:
        """
        Execute tests by category or priority.
        
        Args:
            category: Test category (functional, ui, accessibility, etc.)
            priority: Test priority (critical, high, medium, low)
            browser: Browser to use
            headless: Run in headless mode
            
        Returns:
            Test execution results
        """
        # Build pytest markers filter
        markers = []
        if category:
            markers.append(category)
        if priority:
            markers.append(priority)
        
        if markers:
            filter_expr = f"-m '{' and '.join(markers)}'"
        else:
            filter_expr = ""
        
        return await self.execute_tests(
            test_filter=filter_expr,
            headless=headless,
            browser=browser
        )
    
    async def get_test_status(self, run_id: str = None) -> Dict[str, Any]:
        """
        Get the status of a test run.
        
        Args:
            run_id: Specific run ID, or current run if None
            
        Returns:
            Test run status information
        """
        target_run_id = run_id or self.current_run_id
        if not target_run_id:
            return {'error': 'No test run available'}
        
        run_directory = self.results_directory / target_run_id
        if not run_directory.exists():
            return {'error': f'Run directory not found: {target_run_id}'}
        
        try:
            # Read execution summary
            summary_file = run_directory / "execution_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    return json.load(f)
            
            # If no summary, try to parse XML results
            xml_file = run_directory / "results.xml"
            if xml_file.exists():
                return await self._parse_junit_xml(xml_file)
            
            return {'error': 'No results available for this run'}
            
        except Exception as e:
            logger.error(f"Error getting test status: {e}")
            return {'error': str(e)}
    
    async def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get execution history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of execution history entries
        """
        return self.execution_history[-limit:] if self.execution_history else []
    
    async def get_test_artifacts(self, run_id: str = None) -> Dict[str, List[str]]:
        """
        Get test artifacts (screenshots, videos, traces) for a run.
        
        Args:
            run_id: Specific run ID, or current run if None
            
        Returns:
            Dictionary of artifact types and file paths
        """
        target_run_id = run_id or self.current_run_id
        if not target_run_id:
            return {}
        
        artifacts = {
            'screenshots': [],
            'videos': [],
            'traces': [],
            'reports': []
        }
        
        run_directory = self.results_directory / target_run_id
        if not run_directory.exists():
            return artifacts
        
        try:
            # Find screenshots
            for screenshot in run_directory.glob("**/*.png"):
                artifacts['screenshots'].append(str(screenshot))
            
            # Find videos
            for video in run_directory.glob("**/*.webm"):
                artifacts['videos'].append(str(video))
            
            # Find traces
            for trace in run_directory.glob("**/*.zip"):
                artifacts['traces'].append(str(trace))
            
            # Find reports
            for report in run_directory.glob("**/*.html"):
                artifacts['reports'].append(str(report))
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Error getting test artifacts: {e}")
            return artifacts
    
    async def cleanup_old_results(self, keep_last_n: int = 5):
        """
        Clean up old test results, keeping only the most recent ones.
        
        Args:
            keep_last_n: Number of recent results to keep
        """
        try:
            # Get all run directories sorted by creation time
            run_dirs = [d for d in self.results_directory.iterdir() if d.is_dir()]
            run_dirs.sort(key=lambda x: x.stat().st_ctime, reverse=True)
            
            # Remove old directories
            for run_dir in run_dirs[keep_last_n:]:
                shutil.rmtree(run_dir)
                logger.info(f"Removed old test results: {run_dir}")
            
        except Exception as e:
            logger.error(f"Error cleaning up old results: {e}")
    
    async def generate_test_report(self, run_id: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive test report.
        
        Args:
            run_id: Specific run ID, or current run if None
            
        Returns:
            Comprehensive test report
        """
        target_run_id = run_id or self.current_run_id
        if not target_run_id:
            return {'error': 'No test run available'}
        
        status = await self.get_test_status(target_run_id)
        if 'error' in status:
            return status
        
        artifacts = await self.get_test_artifacts(target_run_id)
        
        # Calculate additional metrics
        report = {
            'run_id': target_run_id,
            'execution_summary': status,
            'artifacts': artifacts,
            'metrics': self._calculate_test_metrics(status),
            'recommendations': self._generate_test_recommendations(status),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    async def _parse_test_results(self, run_directory: Path, stdout: str, stderr: str, 
                                return_code: int, execution_time: float) -> Dict[str, Any]:
        """Parse test execution results from various sources."""
        results = {
            'success': return_code == 0,
            'execution_time': execution_time,
            'return_code': return_code,
            'stdout': stdout,
            'stderr': stderr,
            'run_id': self.current_run_id
        }
        
        try:
            # Parse JUnit XML if available
            xml_file = run_directory / "results.xml"
            if xml_file.exists():
                junit_results = await self._parse_junit_xml(xml_file)
                results.update(junit_results)
            
            # Parse pytest output for additional information
            pytest_results = self._parse_pytest_output(stdout)
            results.update(pytest_results)
            
        except Exception as e:
            logger.error(f"Error parsing test results: {e}")
            results['parse_error'] = str(e)
        
        return results
    
    async def _parse_junit_xml(self, xml_file: Path) -> Dict[str, Any]:
        """Parse JUnit XML results file."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Extract test suite information
            testsuite = root if root.tag == 'testsuite' else root.find('testsuite')
            if testsuite is None:
                return {'error': 'Invalid JUnit XML format'}
            
            results = {
                'total_tests': int(testsuite.get('tests', 0)),
                'passed_tests': 0,
                'failed_tests': int(testsuite.get('failures', 0)),
                'error_tests': int(testsuite.get('errors', 0)),
                'skipped_tests': int(testsuite.get('skipped', 0)),
                'execution_time': float(testsuite.get('time', 0)),
                'test_cases': []
            }
            
            # Calculate passed tests
            results['passed_tests'] = (results['total_tests'] - 
                                     results['failed_tests'] - 
                                     results['error_tests'] - 
                                     results['skipped_tests'])
            
            # Extract individual test case information
            for testcase in testsuite.findall('testcase'):
                case_info = {
                    'name': testcase.get('name'),
                    'classname': testcase.get('classname'),
                    'time': float(testcase.get('time', 0)),
                    'status': 'passed'
                }
                
                # Check for failures or errors
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')
                
                if failure is not None:
                    case_info['status'] = 'failed'
                    case_info['failure_message'] = failure.get('message', '')
                    case_info['failure_text'] = failure.text or ''
                elif error is not None:
                    case_info['status'] = 'error'
                    case_info['error_message'] = error.get('message', '')
                    case_info['error_text'] = error.text or ''
                elif skipped is not None:
                    case_info['status'] = 'skipped'
                    case_info['skip_reason'] = skipped.get('message', '')
                
                results['test_cases'].append(case_info)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing JUnit XML: {e}")
            return {'error': f'Failed to parse JUnit XML: {e}'}
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest console output for additional information."""
        results = {}
        
        try:
            lines = output.split('\n')
            
            # Look for test session information
            for line in lines:
                if 'passed' in line and 'failed' in line:
                    # Parse summary line like "5 passed, 2 failed in 10.5s"
                    import re
                    match = re.search(r'(\d+)\s+passed.*?(\d+)\s+failed.*?in\s+([\d.]+)s', line)
                    if match:
                        results['summary_line'] = line.strip()
                        break
                elif line.startswith('=') and 'FAILURES' in line:
                    results['has_failures'] = True
                elif line.startswith('=') and 'ERRORS' in line:
                    results['has_errors'] = True
            
            # Extract failure details
            failure_section = False
            current_failure = None
            failure_details = []
            
            for line in lines:
                if line.startswith('=') and 'FAILURES' in line:
                    failure_section = True
                    continue
                elif line.startswith('=') and failure_section:
                    failure_section = False
                    break
                
                if failure_section:
                    if line.startswith('_'):
                        if current_failure:
                            failure_details.append(current_failure)
                        current_failure = {'test_name': line.strip('_ '), 'details': []}
                    elif current_failure and line.strip():
                        current_failure['details'].append(line)
            
            if current_failure:
                failure_details.append(current_failure)
            
            if failure_details:
                results['failure_details'] = failure_details
            
        except Exception as e:
            logger.debug(f"Error parsing pytest output: {e}")
        
        return results
    
    async def _save_execution_summary(self, run_directory: Path, results: Dict[str, Any]):
        """Save execution summary to JSON file."""
        try:
            summary_file = run_directory / "execution_summary.json"
            
            # Create a clean summary without large text fields
            summary = {
                'run_id': results.get('run_id'),
                'success': results.get('success'),
                'execution_time': results.get('execution_time'),
                'total_tests': results.get('total_tests', 0),
                'passed_tests': results.get('passed_tests', 0),
                'failed_tests': results.get('failed_tests', 0),
                'error_tests': results.get('error_tests', 0),
                'skipped_tests': results.get('skipped_tests', 0),
                'return_code': results.get('return_code'),
                'has_failures': results.get('has_failures', False),
                'has_errors': results.get('has_errors', False),
                'summary_line': results.get('summary_line', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving execution summary: {e}")
    
    def _generate_run_id(self) -> str:
        """Generate a unique run ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"run_{timestamp}"
    
    def _calculate_test_metrics(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional test metrics."""
        total = status.get('total_tests', 0)
        passed = status.get('passed_tests', 0)
        failed = status.get('failed_tests', 0)
        
        if total == 0:
            return {}
        
        return {
            'pass_rate': round((passed / total) * 100, 2),
            'fail_rate': round((failed / total) * 100, 2),
            'average_test_time': round(status.get('execution_time', 0) / total, 2),
            'tests_per_minute': round(total / (status.get('execution_time', 1) / 60), 2)
        }
    
    def _generate_test_recommendations(self, status: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        total = status.get('total_tests', 0)
        failed = status.get('failed_tests', 0)
        execution_time = status.get('execution_time', 0)
        
        # Performance recommendations
        if execution_time > 300:  # 5 minutes
            recommendations.append("Consider running tests in parallel to reduce execution time")
        
        if total > 0 and execution_time / total > 30:  # 30 seconds per test
            recommendations.append("Individual tests are running slowly, consider optimizing selectors and waits")
        
        # Reliability recommendations
        if failed > 0:
            recommendations.append("Review failed tests and improve test stability")
            
            if failed / total > 0.2:  # More than 20% failure rate
                recommendations.append("High failure rate detected, review test environment and application stability")
        
        # Coverage recommendations
        if total < 10:
            recommendations.append("Consider adding more test cases to improve coverage")
        
        # Success recommendations
        if failed == 0 and total > 0:
            recommendations.append("All tests passed! Consider adding more edge case testing")
        
        return recommendations
