"""
FormGenius Test Runner

This module provides the test execution engine for FormGenius, handling the orchestration
of test execution, result collection, and reporting.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import shutil

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Represents the result of a single test."""
    test_name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshots: List[str] = None
    
    def __post_init__(self):
        if self.screenshots is None:
            self.screenshots = []


@dataclass
class TestSuiteResult:
    """Represents the result of a test suite execution."""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    timestamp: str
    test_results: List[TestResult]
    coverage_report: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100


class TestRunner:
    """
    Advanced test runner for FormGenius framework.
    
    Handles execution of Playwright tests with comprehensive reporting,
    parallel execution, and result aggregation.
    """
    
    def __init__(self, 
                 output_dir: Path = None,
                 max_workers: int = 4,
                 timeout: int = 30000,
                 headed: bool = False,
                 browser: str = "chromium"):
        """
        Initialize the test runner.
        
        Args:
            output_dir: Directory for test outputs and reports
            max_workers: Maximum number of parallel test workers
            timeout: Test timeout in milliseconds
            headed: Whether to run tests in headed mode
            browser: Browser to use for testing
        """
        self.output_dir = output_dir or Path("test_results")
        self.max_workers = max_workers
        self.timeout = timeout
        self.headed = headed
        self.browser = browser
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration for test execution."""
        log_file = self.output_dir / "test_execution.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Configure logger
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    async def run_test_suite(self, 
                           test_dir: Path,
                           test_pattern: str = "test_*.py",
                           config_file: Optional[Path] = None) -> TestSuiteResult:
        """
        Run a complete test suite.
        
        Args:
            test_dir: Directory containing test files
            test_pattern: Pattern to match test files
            config_file: Optional Playwright config file
            
        Returns:
            TestSuiteResult with execution results
        """
        start_time = time.time()
        suite_name = test_dir.name
        
        logger.info(f"Starting test suite execution: {suite_name}")
        logger.info(f"Test directory: {test_dir}")
        logger.info(f"Test pattern: {test_pattern}")
        
        # Find test files
        test_files = list(test_dir.glob(test_pattern))
        if not test_files:
            logger.warning(f"No test files found matching pattern: {test_pattern}")
            return TestSuiteResult(
                suite_name=suite_name,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0.0,
                timestamp=datetime.now().isoformat(),
                test_results=[]
            )
        
        logger.info(f"Found {len(test_files)} test files")
        
        # Prepare test execution
        test_results = []
        
        # Run tests
        if self.max_workers == 1:
            # Sequential execution
            for test_file in test_files:
                result = await self._run_single_test_file(test_file, config_file)
                test_results.extend(result)
        else:
            # Parallel execution
            semaphore = asyncio.Semaphore(self.max_workers)
            tasks = [
                self._run_test_with_semaphore(semaphore, test_file, config_file)
                for test_file in test_files
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Test execution failed: {result}")
                    # Create a failed test result
                    test_results.append(TestResult(
                        test_name="failed_execution",
                        status="failed",
                        duration=0.0,
                        error_message=str(result)
                    ))
                else:
                    test_results.extend(result)
        
        # Calculate metrics
        duration = time.time() - start_time
        passed = sum(1 for r in test_results if r.status == "passed")
        failed = sum(1 for r in test_results if r.status == "failed")
        skipped = sum(1 for r in test_results if r.status == "skipped")
        
        # Create suite result
        suite_result = TestSuiteResult(
            suite_name=suite_name,
            total_tests=len(test_results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            timestamp=datetime.now().isoformat(),
            test_results=test_results
        )
        
        # Generate reports
        await self._generate_reports(suite_result)
        
        logger.info(f"Test suite completed: {suite_name}")
        logger.info(f"Total: {suite_result.total_tests}, "
                   f"Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
        logger.info(f"Success rate: {suite_result.success_rate:.1f}%")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        return suite_result
    
    async def _run_test_with_semaphore(self, 
                                     semaphore: asyncio.Semaphore,
                                     test_file: Path,
                                     config_file: Optional[Path]) -> List[TestResult]:
        """Run a test file with semaphore for parallel execution."""
        async with semaphore:
            return await self._run_single_test_file(test_file, config_file)
    
    async def _run_single_test_file(self, 
                                  test_file: Path,
                                  config_file: Optional[Path] = None) -> List[TestResult]:
        """
        Run a single test file and return results.
        
        Args:
            test_file: Path to the test file
            config_file: Optional Playwright config file
            
        Returns:
            List of TestResult objects
        """
        logger.info(f"Running test file: {test_file}")
        
        # Prepare command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "--json-report",
            f"--json-report-file={self.output_dir / f'{test_file.stem}_report.json'}",
            "-v"
        ]
        
        # Add browser configuration
        cmd.extend([
            f"--browser={self.browser}",
            f"--timeout={self.timeout}"
        ])
        
        if self.headed:
            cmd.append("--headed")
        
        if config_file:
            cmd.extend(["--config", str(config_file)])
        
        start_time = time.time()
        
        try:
            # Run the test
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=test_file.parent
            )
            
            stdout, stderr = await process.communicate()
            duration = time.time() - start_time
            
            # Parse results
            report_file = self.output_dir / f'{test_file.stem}_report.json'
            if report_file.exists():
                results = self._parse_pytest_json_report(report_file)
            else:
                # Fallback parsing
                results = self._parse_pytest_output(stdout.decode(), stderr.decode(), duration)
            
            logger.info(f"Completed test file: {test_file} ({len(results)} tests)")
            return results
            
        except Exception as e:
            logger.error(f"Failed to run test file {test_file}: {e}")
            return [TestResult(
                test_name=f"{test_file.stem}_execution_error",
                status="failed",
                duration=time.time() - start_time,
                error_message=str(e)
            )]
    
    def _parse_pytest_json_report(self, report_file: Path) -> List[TestResult]:
        """Parse pytest JSON report to extract test results."""
        try:
            with open(report_file, 'r') as f:
                data = json.load(f)
            
            results = []
            for test in data.get('tests', []):
                status = test.get('outcome', 'unknown')
                if status == 'passed':
                    status = 'passed'
                elif status == 'failed':
                    status = 'failed'
                elif status == 'skipped':
                    status = 'skipped'
                
                result = TestResult(
                    test_name=test.get('nodeid', 'unknown'),
                    status=status,
                    duration=test.get('duration', 0.0),
                    error_message=test.get('call', {}).get('longrepr') if status == 'failed' else None
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to parse JSON report {report_file}: {e}")
            return []
    
    def _parse_pytest_output(self, stdout: str, stderr: str, duration: float) -> List[TestResult]:
        """Fallback method to parse pytest output."""
        results = []
        
        # Simple parsing - this is a basic implementation
        lines = stdout.split('\n')
        for line in lines:
            if '::' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                parts = line.split()
                if len(parts) >= 2:
                    test_name = parts[0]
                    status = parts[1].lower()
                    
                    result = TestResult(
                        test_name=test_name,
                        status=status,
                        duration=duration / max(1, len([l for l in lines if '::' in l])),  # Estimate
                        error_message=stderr if status == 'failed' and stderr else None
                    )
                    results.append(result)
        
        return results
    
    async def _generate_reports(self, suite_result: TestSuiteResult):
        """Generate comprehensive test reports."""
        # JSON Report
        json_report_path = self.output_dir / "test_report.json"
        with open(json_report_path, 'w') as f:
            json.dump(asdict(suite_result), f, indent=2)
        
        # HTML Report
        html_report_path = self.output_dir / "test_report.html"
        await self._generate_html_report(suite_result, html_report_path)
        
        # JUnit XML Report
        junit_report_path = self.output_dir / "junit_report.xml"
        self._generate_junit_report(suite_result, junit_report_path)
        
        logger.info(f"Reports generated:")
        logger.info(f"  JSON: {json_report_path}")
        logger.info(f"  HTML: {html_report_path}")
        logger.info(f"  JUnit: {junit_report_path}")
    
    async def _generate_html_report(self, suite_result: TestSuiteResult, output_path: Path):
        """Generate an HTML test report."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>FormGenius Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
                .summary { display: flex; gap: 20px; margin: 20px 0; }
                .metric { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
                .passed { background: #d4edda; color: #155724; }
                .failed { background: #f8d7da; color: #721c24; }
                .skipped { background: #fff3cd; color: #856404; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #f8f9fa; }
                .status-passed { color: #28a745; font-weight: bold; }
                .status-failed { color: #dc3545; font-weight: bold; }
                .status-skipped { color: #ffc107; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FormGenius Test Report</h1>
                <p><strong>Suite:</strong> {suite_name}</p>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p><strong>Duration:</strong> {duration:.2f} seconds</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <div style="font-size: 24px; font-weight: bold;">{total_tests}</div>
                </div>
                <div class="metric passed">
                    <h3>Passed</h3>
                    <div style="font-size: 24px; font-weight: bold;">{passed}</div>
                </div>
                <div class="metric failed">
                    <h3>Failed</h3>
                    <div style="font-size: 24px; font-weight: bold;">{failed}</div>
                </div>
                <div class="metric skipped">
                    <h3>Skipped</h3>
                    <div style="font-size: 24px; font-weight: bold;">{skipped}</div>
                </div>
                <div class="metric">
                    <h3>Success Rate</h3>
                    <div style="font-size: 24px; font-weight: bold;">{success_rate:.1f}%</div>
                </div>
            </div>
            
            <h2>Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Error Message</th>
                    </tr>
                </thead>
                <tbody>
                    {test_rows}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Generate test rows
        test_rows = ""
        for test in suite_result.test_results:
            status_class = f"status-{test.status}"
            error_msg = test.error_message[:100] + "..." if test.error_message and len(test.error_message) > 100 else (test.error_message or "")
            
            test_rows += f"""
                <tr>
                    <td>{test.test_name}</td>
                    <td class="{status_class}">{test.status.upper()}</td>
                    <td>{test.duration:.2f}s</td>
                    <td>{error_msg}</td>
                </tr>
            """
        
        # Format the HTML
        html_content = html_template.format(
            suite_name=suite_result.suite_name,
            timestamp=suite_result.timestamp,
            duration=suite_result.duration,
            total_tests=suite_result.total_tests,
            passed=suite_result.passed,
            failed=suite_result.failed,
            skipped=suite_result.skipped,
            success_rate=suite_result.success_rate,
            test_rows=test_rows
        )
        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _generate_junit_report(self, suite_result: TestSuiteResult, output_path: Path):
        """Generate a JUnit XML report."""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        # Create root element
        testsuites = Element('testsuites')
        testsuite = SubElement(testsuites, 'testsuite')
        testsuite.set('name', suite_result.suite_name)
        testsuite.set('tests', str(suite_result.total_tests))
        testsuite.set('failures', str(suite_result.failed))
        testsuite.set('skipped', str(suite_result.skipped))
        testsuite.set('time', str(suite_result.duration))
        testsuite.set('timestamp', suite_result.timestamp)
        
        # Add test cases
        for test in suite_result.test_results:
            testcase = SubElement(testsuite, 'testcase')
            testcase.set('name', test.test_name)
            testcase.set('time', str(test.duration))
            
            if test.status == 'failed':
                failure = SubElement(testcase, 'failure')
                failure.set('message', test.error_message or 'Test failed')
                if test.stack_trace:
                    failure.text = test.stack_trace
            elif test.status == 'skipped':
                SubElement(testcase, 'skipped')
        
        # Write to file
        rough_string = tostring(testsuites, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        with open(output_path, 'w') as f:
            f.write(reparsed.toprettyxml(indent="  "))
    
    async def run_single_test(self, 
                            test_file: Path,
                            test_name: Optional[str] = None) -> TestResult:
        """
        Run a single test and return the result.
        
        Args:
            test_file: Path to the test file
            test_name: Specific test name to run (optional)
            
        Returns:
            TestResult object
        """
        if test_name:
            test_spec = f"{test_file}::{test_name}"
        else:
            test_spec = str(test_file)
        
        results = await self._run_single_test_file(Path(test_spec))
        return results[0] if results else TestResult(
            test_name=test_spec,
            status="failed",
            duration=0.0,
            error_message="No results returned"
        )
    
    def get_test_history(self, days: int = 30) -> List[TestSuiteResult]:
        """
        Get test execution history from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of TestSuiteResult objects
        """
        history = []
        
        # Look for JSON reports in the output directory
        for report_file in self.output_dir.glob("test_report_*.json"):
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                
                # Convert back to TestSuiteResult
                test_results = [
                    TestResult(**test_data) 
                    for test_data in data.get('test_results', [])
                ]
                
                suite_result = TestSuiteResult(
                    suite_name=data['suite_name'],
                    total_tests=data['total_tests'],
                    passed=data['passed'],
                    failed=data['failed'],
                    skipped=data['skipped'],
                    duration=data['duration'],
                    timestamp=data['timestamp'],
                    test_results=test_results,
                    coverage_report=data.get('coverage_report'),
                    performance_metrics=data.get('performance_metrics')
                )
                
                history.append(suite_result)
                
            except Exception as e:
                logger.warning(f"Failed to load test history from {report_file}: {e}")
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x.timestamp, reverse=True)
        
        return history


# Utility functions for external use
async def run_tests(test_directory: Union[str, Path], 
                   output_directory: Union[str, Path] = None,
                   **kwargs) -> TestSuiteResult:
    """
    Convenience function to run tests with default configuration.
    
    Args:
        test_directory: Directory containing test files
        output_directory: Directory for test outputs
        **kwargs: Additional arguments for TestRunner
        
    Returns:
        TestSuiteResult object
    """
    test_dir = Path(test_directory)
    output_dir = Path(output_directory) if output_directory else Path("test_results")
    
    runner = TestRunner(output_dir=output_dir, **kwargs)
    return await runner.run_test_suite(test_dir)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FormGenius Test Runner")
    parser.add_argument("test_dir", help="Directory containing test files")
    parser.add_argument("--output", "-o", help="Output directory for reports")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--timeout", "-t", type=int, default=30000, help="Test timeout in milliseconds")
    parser.add_argument("--headed", action="store_true", help="Run tests in headed mode")
    parser.add_argument("--browser", "-b", default="chromium", help="Browser to use")
    
    args = parser.parse_args()
    
    async def main():
        test_dir = Path(args.test_dir)
        output_dir = Path(args.output) if args.output else Path("test_results")
        
        runner = TestRunner(
            output_dir=output_dir,
            max_workers=args.workers,
            timeout=args.timeout,
            headed=args.headed,
            browser=args.browser
        )
        
        result = await runner.run_test_suite(test_dir)
        
        print(f"\nTest Suite Complete: {result.suite_name}")
        print(f"Total: {result.total_tests}, Passed: {result.passed}, "
              f"Failed: {result.failed}, Skipped: {result.skipped}")
        print(f"Success Rate: {result.success_rate:.1f}%")
        print(f"Duration: {result.duration:.2f} seconds")
        
        if result.failed > 0:
            print("\nFailed Tests:")
            for test in result.test_results:
                if test.status == "failed":
                    print(f"  - {test.test_name}: {test.error_message}")
        
        return 0 if result.failed == 0 else 1
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
