# FormGenius - AI-Powered Form Automation Agent

FormGenius is an intelligent AI agent that automatically fills out and submits web forms, including Power Apps forms, using Playwright MCP (Model Context Protocol) for comprehensive user testing.

## Features

- **Smart Form Detection**: Automatically identifies and analyzes web forms
- **AI-Powered Data Generation**: Generates realistic test data using Faker and AI models
- **Power Apps Support**: Specialized support for Microsoft Power Apps forms
- **Playwright MCP Integration**: Uses Microsoft's Playwright MCP server for robust browser automation
- **Multiple Test Scenarios**: Valid, invalid, and edge case testing
- **Batch Processing**: Fill multiple forms simultaneously
- **Comprehensive Reporting**: HTML and JSON reports with screenshots
- **CLI Interface**: Easy-to-use command-line interface
- **Configurable**: YAML-based configuration with environment variable support

## Quick Start

### 1. Automated Setup
```bash
python setup.py
```
This will create a virtual environment, install dependencies, and set up the project.

### 2. Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Copy environment template
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Test Installation
```bash
python test_installation.py
```

## Usage

### Command Line Interface

#### Fill a Single Form
```bash
python main.py fill --url https://example.com/form --config config.yaml
```

#### Fill Multiple Forms (Batch)
```bash
python main.py batch --urls-file sample_urls.txt --config config.yaml
```

#### Test Form Validation
```bash
python main.py test --url https://example.com/form --scenarios valid invalid edge
```

#### Fill Power Apps Form
```bash
python main.py power-apps --url https://apps.powerapps.com/play/abc123
```

### Python API

#### Basic Form Filling
```python
from formgenius.core.agent import FormGeniusAgent
from formgenius.core.config import Config

config = Config.from_yaml('config.yaml')
agent = FormGeniusAgent(config)

result = await agent.fill_form(
    url="https://example.com/contact-form",
    test_scenarios=["valid"]
)
```

#### Power Apps Form Testing
```python
result = await agent.fill_power_apps_form(
    app_url="https://apps.powerapps.com/play/abc123",
    test_scenarios=["valid"]
)
```

#### Batch Form Testing
```python
result = await agent.batch_fill_forms(
    urls=[
        "https://example.com/form1",
        "https://example.com/form2", 
        "https://example.com/form3"
    ],
    test_scenarios=["valid"]
)
```

#### Form Validation Testing
```python
result = await agent.test_form_validation(
    url="https://example.com/form",
    validation_scenarios=["valid", "invalid", "edge"]
)
```

## Configuration

FormGenius uses YAML configuration files. See `config.yaml` for all available options:

```yaml
# Browser settings
browser:
  type: "chromium"
  headless: false
  viewport:
    width: 1920
    height: 1080

# AI configuration  
ai:
  provider: "google"
  model: "gemini-pro"
  temperature: 0.7

# Form filling behavior
form_filling:
  field_delay: 500
  typing_delay: 50
  form_load_timeout: 15
  take_screenshots: true

# Test scenarios
test_scenarios:
  valid:
    description: "Fill form with valid data"
    data_quality: "valid"
  invalid:
    description: "Test form validation"
    data_quality: "invalid"
  edge:
    description: "Test edge cases"
    data_quality: "edge"
```

### Environment Variables

Set these in your `.env` file:

```bash
GOOGLE_API_KEY=your_google_api_key_here
MCP_SERVER_URL=http://localhost:3000
LOG_LEVEL=INFO
BROWSER_HEADLESS=false
```

## Examples

Run the examples to see FormGenius in action:

```bash
python examples.py
```

This will demonstrate:
- Single form filling
- Batch processing
- Form validation testing
- Power Apps form handling
- Custom data generation
- Error handling

## Project Structure

```
FormGenius/
├── main.py                 # CLI entry point
├── setup.py               # Setup script
├── examples.py            # Usage examples
├── test_installation.py   # Installation test
├── config.yaml           # Configuration file
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── sample_urls.txt      # Sample URLs for batch testing
├── formgenius/
│   ├── __init__.py
│   ├── core/            # Core modules
│   │   ├── __init__.py
│   │   ├── agent.py     # Main FormGenius agent
│   │   ├── config.py    # Configuration management
│   │   ├── data_generator.py  # AI-powered data generation
│   │   ├── form_detector.py   # Form detection logic
│   │   └── reporter.py  # Test reporting
│   └── integrations/    # External integrations
│       ├── __init__.py
│       ├── playwright_mcp.py  # Playwright MCP client
│       └── power_apps.py      # Power Apps handler
├── reports/             # Generated reports
├── screenshots/         # Screenshots during testing
└── logs/               # Log files
```

## Architecture

FormGenius follows a modular architecture:

1. **FormGeniusAgent**: Main orchestrator that coordinates all components
2. **FormDetector**: Analyzes web pages to identify forms and their fields
3. **DataGenerator**: Uses AI and Faker library to generate realistic test data
4. **PlaywrightMCPClient**: Handles browser automation via Playwright MCP
5. **PowerAppsHandler**: Specialized handler for Power Apps forms
6. **TestReporter**: Generates comprehensive HTML and JSON reports
7. **Config**: Manages configuration from YAML files and environment variables

## Supported Form Types

- **Standard HTML Forms**: Basic HTML `<form>` elements
- **Dynamic Forms**: JavaScript-rendered forms
- **Power Apps Forms**: Microsoft Power Apps applications
- **Multi-step Forms**: Forms with multiple pages/steps
- **File Upload Forms**: Forms with file input fields
- **Validation-heavy Forms**: Forms with complex client-side validation

## Data Generation

FormGenius generates realistic test data using:

- **Faker Library**: Generates names, addresses, emails, phone numbers
- **AI Models**: Context-aware data generation for specific fields
- **Custom Patterns**: Configurable data patterns for specific use cases
- **Validation Scenarios**: Invalid and edge case data for testing

### Supported Data Types

- Personal information (names, emails, phones)
- Addresses and geographical data
- Dates and times
- Numbers and quantities
- Text content (descriptions, comments)
- File uploads (generates test files)
- Boolean values (checkboxes, radio buttons)

## Reporting

FormGenius generates comprehensive reports:

### HTML Reports
- Visual form screenshots
- Field-by-field filling results
- Error messages and validation failures
- Performance metrics and timing

### JSON Reports
- Machine-readable test results
- Detailed field mappings
- Error logs and stack traces
- Metadata and configuration used

## CLI Commands

```bash
# Get help
python main.py --help

# Fill single form
python main.py fill --url URL [--submit] [--scenario SCENARIO]

# Batch fill forms  
python main.py batch --urls-file FILE [--submit] [--scenario SCENARIO]

# Test form validation
python main.py test --url URL [--scenarios SCENARIOS]

# Fill Power Apps form
python main.py power-apps --url URL [--submit] [--scenario SCENARIO]

# Global options
--config CONFIG_FILE    # Configuration file path
--verbose              # Enable verbose logging  
--headless            # Run browser in headless mode
--output DIR          # Output directory for reports
```

## Requirements

- Python 3.8+
- Node.js 14+ (for Playwright MCP server)
- Chrome/Chromium browser
- Internet connection for AI services

## Dependencies

See `requirements.txt` for the complete list:

- **playwright**: Browser automation
- **beautifulsoup4**: HTML parsing and form detection
- **faker**: Realistic test data generation
- **google-generativeai**: Google AI integration
- **pyyaml**: YAML configuration parsing
- **aiohttp**: Async HTTP client
- **jinja2**: Report template rendering

## Troubleshooting

### Common Issues

1. **Playwright Installation Issues**
   ```bash
   playwright install
   ```

2. **API Key Not Found**
   - Check your `.env` file
   - Ensure `GOOGLE_API_KEY` is set correctly

3. **Form Not Detected**
   - Check if the page loads completely
   - Verify the URL is accessible
   - Try increasing `form_load_timeout` in config

4. **Power Apps Forms Not Working**
   - Ensure you have proper authentication
   - Check Power Apps specific selectors in config
   - Try increasing `load_timeout` for Power Apps

### Debug Mode

Enable debug logging:
```bash
python main.py --verbose [command]
```

Or set in configuration:
```yaml
logging:
  level: "DEBUG"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📚 Documentation: See this README and code comments
- 🐛 Bug Reports: Create an issue on GitHub
- 💡 Feature Requests: Create an issue on GitHub
- 🤝 Contributions: Pull requests welcome

## Roadmap

- [ ] Support for more AI providers (OpenAI, Anthropic)
- [ ] Advanced form field type detection
- [ ] Multi-language support
- [ ] Integration with test frameworks (pytest, unittest)
- [ ] GUI interface for non-technical users
- [ ] Docker containerization
- [ ] Cloud deployment options

---

**FormGenius** - Making web form testing intelligent and automated! 🤖✨
