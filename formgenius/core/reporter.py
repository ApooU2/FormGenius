"""
Test Reporter - Generate comprehensive test reports
"""

import json
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class TestReporter:
    """Generate comprehensive test reports for FormGenius sessions."""
    
    def __init__(self, config):
        self.config = config
    
    async def generate_report(self, session_data: Dict[str, Any], 
                            output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive test report.
        
        Args:
            session_data: Session data from FormGeniusAgent
            output_path: Optional custom output path
            
        Returns:
            Report data
        """
        report_data = self._create_report_data(session_data)
        
        # Generate HTML report
        html_report = self._generate_html_report(report_data)
        
        # Generate JSON report
        json_report = self._generate_json_report(report_data)
        
        # Save reports
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(self.config.output_directory) / f"formgenius_report_{timestamp}"
        
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)
        
        # Save HTML report
        html_file = output_path / "report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Save JSON report
        json_file = output_path / "report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, default=str)
        
        report_data['output_files'] = {
            'html': str(html_file),
            'json': str(json_file)
        }
        
        return report_data
    
    def _create_report_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured report data."""
        results = session_data.get('results', [])
        errors = session_data.get('errors', [])
        
        # Calculate summary statistics
        total_forms = len(session_data.get('forms_processed', []))
        successful_forms = len([r for r in results if r.get('success')])
        failed_forms = len([r for r in results if not r.get('success')]) + len(errors)
        
        total_scenarios = sum(r.get('scenarios_executed', 0) for r in results)
        
        start_time = session_data.get('start_time')
        end_time = datetime.now()
        duration = 0
        if start_time:
            duration = (end_time - start_time).total_seconds()
        
        return {
            'session_info': {
                'session_id': session_data.get('session_id'),
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration
            },
            'summary': {
                'total_forms': total_forms,
                'successful_forms': successful_forms,
                'failed_forms': failed_forms,
                'success_rate': (successful_forms / max(total_forms, 1)) * 100,
                'total_scenarios': total_scenarios
            },
            'results': results,
            'errors': errors,
            'forms_processed': session_data.get('forms_processed', [])
        }
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FormGenius Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.5em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #007acc;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #007acc;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .result-item {{
            background: #f8f9fa;
            margin-bottom: 15px;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .result-item.failed {{
            border-left-color: #dc3545;
        }}
        .result-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .status {{
            padding: 4px 12px;
            border-radius: 20px;
            color: white;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status.success {{
            background-color: #28a745;
        }}
        .status.failed {{
            background-color: #dc3545;
        }}
        .details {{
            margin-top: 15px;
        }}
        .details pre {{
            background: #f1f3f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9em;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 FormGenius Test Report</h1>
            <p>AI-Powered Form Automation Results</p>
            <div class="timestamp">
                Generated: {report_data['session_info']['end_time'].strftime('%Y-%m-%d %H:%M:%S') if report_data['session_info']['end_time'] else 'N/A'}
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Forms</h3>
                <div class="value">{report_data['summary']['total_forms']}</div>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <div class="value">{report_data['summary']['success_rate']:.1f}%</div>
            </div>
            <div class="summary-card">
                <h3>Scenarios Executed</h3>
                <div class="value">{report_data['summary']['total_scenarios']}</div>
            </div>
            <div class="summary-card">
                <h3>Duration</h3>
                <div class="value">{report_data['session_info']['duration']:.1f}s</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Test Results</h2>
            {self._generate_results_html(report_data['results'])}
        </div>
        
        {self._generate_errors_html(report_data['errors']) if report_data['errors'] else ''}
        
        <div class="section">
            <h2>ℹ️ Session Information</h2>
            <div class="details">
                <p><strong>Session ID:</strong> {report_data['session_info']['session_id']}</p>
                <p><strong>Start Time:</strong> {report_data['session_info']['start_time'].strftime('%Y-%m-%d %H:%M:%S') if report_data['session_info']['start_time'] else 'N/A'}</p>
                <p><strong>End Time:</strong> {report_data['session_info']['end_time'].strftime('%Y-%m-%d %H:%M:%S') if report_data['session_info']['end_time'] else 'N/A'}</p>
                <p><strong>Total Duration:</strong> {report_data['session_info']['duration']:.2f} seconds</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_results_html(self, results):
        """Generate HTML for test results."""
        if not results:
            return "<p>No test results available.</p>"
        
        html_parts = []
        for i, result in enumerate(results):
            success = result.get('success', False)
            status_class = 'success' if success else 'failed'
            
            html_parts.append(f"""
            <div class="result-item {'' if success else 'failed'}">
                <div class="result-header">
                    <h4>Form {i+1}: {html.escape(result.get('url', 'Unknown URL'))}</h4>
                    <span class="status {status_class}">
                        {'✅ SUCCESS' if success else '❌ FAILED'}
                    </span>
                </div>
                <div class="details">
                    <p><strong>Forms Found:</strong> {result.get('forms_found', 0)}</p>
                    <p><strong>Scenarios Executed:</strong> {result.get('scenarios_executed', 0)}</p>
                    {f"<p><strong>Error:</strong> {html.escape(str(result.get('error', '')))}</p>" if result.get('error') else ''}
                </div>
            </div>
            """)
        
        return ''.join(html_parts)
    
    def _generate_errors_html(self, errors):
        """Generate HTML for errors section."""
        if not errors:
            return ""
        
        error_items = []
        for error in errors:
            error_items.append(f"""
            <div class="result-item failed">
                <div class="result-header">
                    <h4>Error: {html.escape(error.get('url', 'Unknown URL'))}</h4>
                    <span class="status failed">❌ ERROR</span>
                </div>
                <div class="details">
                    <pre>{html.escape(str(error.get('error', 'Unknown error')))}</pre>
                </div>
            </div>
            """)
        
        return f"""
        <div class="section">
            <h2>⚠️ Errors</h2>
            {''.join(error_items)}
        </div>
        """
    
    def _generate_json_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON report."""
        return {
            'report_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            **report_data
        }
