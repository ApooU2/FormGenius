# FormGenius 🤖

**AI-Powered Automated Web Testing Framework**

> **Transform any website into comprehensive automated tests in seconds with the power of AI** 🚀

FormGenius is a revolutionary AI-powered testing framework that automatically analyzes websites, understands their structure and functionality, and generates comprehensive Playwright test suites with minimal human intervention. Whether you're a QA engineer, developer, or testing beginner, FormGenius makes advanced web testing accessible to everyone.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Playwright](https://img.shields.io/badge/playwright-latest-orange.svg)](https://playwright.dev)
[![AI Powered](https://img.shields.io/badge/AI-Gemini%20Pro-purple.svg)](https://ai.google.dev)

---

## 🎯 What is FormGenius?

**FormGenius is like having an expert QA engineer that never sleeps, working 24/7 to test your websites automatically.**

Imagine you have a website - maybe an online store, a blog, or a business application. Normally, testing this website would require:
- 👨‍💻 A skilled QA engineer to write test scripts
- ⏰ Days or weeks to create comprehensive tests
- 🧠 Deep knowledge of testing frameworks like Playwright
- 🔄 Constant maintenance as your website changes

**FormGenius eliminates all of this.** Just give it your website URL, and it will:

1. **🕵️ Analyze your website** - It intelligently crawls through your pages, understanding forms, buttons, navigation, and user workflows
2. **🧠 Generate test scenarios** - Using AI, it creates comprehensive test cases covering functional, security, accessibility, and edge cases
3. **⚡ Create production-ready test code** - It writes professional Playwright test suites with best practices, ready to run
4. **🚀 Execute and report** - It runs the tests across multiple browsers and generates detailed reports

**Result**: Complete automated testing for your website in under 60 seconds, with zero coding required from you.

---

## 🌟 Key Features That Make FormGenius Special

### 🤖 **AI-Powered Intelligence**
- **Smart Website Understanding**: Uses Google Gemini AI to understand your website like a human would
- **Intelligent Element Detection**: Automatically identifies forms, buttons, links, and interactive elements
- **Context-Aware Testing**: Understands business workflows and user journeys
- **Adaptive Learning**: Gets smarter with each website it analyzes

### 🧪 **Comprehensive Test Coverage**
- **Functional Testing**: Tests all features work as expected (form submissions, navigation, user flows)
- **Validation Testing**: Ensures proper input validation and error handling
- **Security Testing**: Automatically tests for common vulnerabilities (XSS, CSRF, SQL injection)
- **Accessibility Testing**: Verifies WCAG compliance and screen reader compatibility
- **Performance Testing**: Monitors page load times and resource usage
- **Cross-Browser Testing**: Tests across Chrome, Firefox, and Safari automatically

### ⚡ **Zero-Effort Test Generation**
- **No Coding Required**: Just provide a URL and get professional test suites
- **Production-Ready Code**: Generates clean, maintainable Playwright tests
- **Page Object Model**: Follows testing best practices out of the box
- **Complete Test Infrastructure**: Includes configuration files, test data, and setup instructions

### 🛡️ **Enterprise-Grade Quality**
- **Parallel Execution**: Runs tests simultaneously for faster results
- **Rich Reporting**: HTML, JSON, and JUnit XML reports with screenshots and videos
- **CI/CD Integration**: Works seamlessly with GitHub Actions, Jenkins, and other CI systems
- **Error Recovery**: Smart retry mechanisms and detailed failure analysis

---

## 🎬 How FormGenius Works - Step by Step

### Step 1: 🕵️ **Website Exploration**
```
You provide: https://mystore.com
FormGenius thinks: "Let me explore this website..."

🔍 Discovers:
  ├── Login form with username/password fields
  ├── Product search functionality  
  ├── Shopping cart system
  ├── Checkout process with payment forms
  └── User registration workflow
```

### Step 2: 🧠 **AI Analysis & Strategy**
```
FormGenius's AI brain analyzes:
📊 "This is an e-commerce site with these critical paths:
    - User authentication (high priority)
    - Product search and filtering (medium priority)  
    - Shopping cart operations (high priority)
    - Payment processing (critical priority)
    - User account management (medium priority)"

🎯 Test Strategy Generated:
    ✅ 15 functional test scenarios
    ✅ 8 security test cases
    ✅ 5 accessibility checks
    ✅ 12 edge case validations
```

### Step 3: ⚡ **Test Code Generation**
```
FormGenius writes professional code:

📁 Generated Test Suite:
├── tests/
│   ├── test_login_functionality.py          # User authentication tests
│   ├── test_product_search.py               # Search and filtering tests  
│   ├── test_shopping_cart.py                # Cart operations
│   ├── test_checkout_process.py             # Payment workflow
│   └── test_security_validations.py         # Security checks
├── pages/
│   ├── login_page.py                        # Page object for login
│   ├── product_page.py                      # Page object for products
│   └── checkout_page.py                     # Page object for checkout
├── requirements.txt                         # All dependencies
├── pytest.ini                              # Test configuration
└── README.md                               # Setup instructions
```

### Step 4: 🚀 **Execution & Reporting**
```
FormGenius runs your tests:

🏃‍♂️ Executing tests in parallel across:
   ├── Chrome (Desktop)
   ├── Firefox (Desktop)  
   └── Safari (Desktop)

📊 Results:
   ✅ 32/35 tests passed (91% success rate)
   ❌ 3 tests failed (accessibility issues found)
   📸 Screenshots captured for all failures
   📹 Videos recorded for debugging
   📄 Detailed HTML report generated
```

---

## 🏁 Getting Started (Complete Beginner Guide)

### Prerequisites
Don't worry if you're new to programming! FormGenius is designed to be beginner-friendly.

**What you need:**
- 💻 A computer (Windows, Mac, or Linux)
- 🐍 Python 3.8 or higher ([Download here](https://python.org))
- 🔑 A free Google Gemini API key ([Get one here](https://ai.google.dev))

### Step-by-Step Installation

#### 1. **Download FormGenius**
```bash
# Open your terminal/command prompt and run:
git clone https://github.com/FormGenius/FormGenius.git
cd FormGenius
```

#### 2. **Set Up Python Environment**
```bash
# Create a virtual environment (recommended)
python -m venv formgenius-env

# Activate it:
# On Mac/Linux:
source formgenius-env/bin/activate
# On Windows:
formgenius-env\Scripts\activate
```

#### 3. **Install FormGenius**
```bash
# Install all required packages
pip install -r requirements.txt

# Install browser engines for testing
playwright install
```

#### 4. **Configure Your API Key**
```bash
# Create your configuration file
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env

# Replace 'your_actual_api_key_here' with your real API key
```

#### 5. **Test Your Installation**
```bash
# Run the demo to make sure everything works
python demo.py
```

If you see the FormGenius demo running successfully, congratulations! 🎉 You're ready to start testing websites.

---

## 🚀 Your First Test in 60 Seconds

### Method 1: One-Command Testing (Easiest)
```bash
# Test any website with a single command
python main.py quick https://example.com

# That's it! FormGenius will:
# ✅ Analyze the website
# ✅ Generate test scenarios  
# ✅ Create test code
# ✅ Run the tests
# ✅ Show you the results
```

### Method 2: Step-by-Step Control
```bash
# 1. Analyze a website first
python main.py analyze https://mystore.com --output ./my-tests

# 2. Run the generated tests
python main.py run ./my-tests --workers 4

# 3. View your results in the generated HTML report
```

### Method 3: Using Python Code
```python
# If you want to use FormGenius in your own Python scripts
import asyncio
from src.core.formgenius import FormGenius

async def test_my_website():
    # Initialize FormGenius
    formgenius = FormGenius()
    
    # Analyze a website
    analysis = await formgenius.analyze_website("https://mywebsite.com")
    
    # Generate test scenarios
    scenarios = await formgenius.generate_test_scenarios(analysis)
    
    # Generate Playwright test code
    await formgenius.generate_playwright_tests(
        scenarios, 
        "https://mywebsite.com",
        output_dir="./my_tests"
    )
    
    print("✅ Tests generated! Check the ./my_tests folder")

# Run it
asyncio.run(test_my_website())
```

---

## 🎯 Real-World Examples

### Example 1: Testing an Online Store
```bash
# Test an e-commerce website
python main.py quick https://shop.example.com

# FormGenius automatically finds and tests:
✅ Product browsing and search
✅ Add to cart functionality  
✅ User registration and login
✅ Checkout process
✅ Payment form validation
✅ Order confirmation
✅ Security vulnerabilities
✅ Mobile responsiveness
```

### Example 2: Testing a Blog/News Site
```bash
# Test a content website
python main.py quick https://myblog.com

# FormGenius automatically tests:
✅ Article reading experience
✅ Comment system functionality
✅ Search functionality
✅ Newsletter signup forms
✅ Social media sharing
✅ Contact forms
✅ Accessibility compliance
```

### Example 3: Testing a Business Application
```bash
# Test a SaaS application
python main.py quick https://myapp.com

# FormGenius automatically tests:
✅ User authentication flows
✅ Dashboard functionality
✅ Form submissions and data handling
✅ User settings and preferences
✅ Data export/import features
✅ Security and authorization
✅ API integrations
```

---

## 📊 Understanding Your Test Results

When FormGenius finishes testing, you get comprehensive reports:

### 📄 **HTML Report** (Most Important)
- **Visual Overview**: See all test results at a glance
- **Screenshots**: Visual proof of what happened during tests
- **Failure Details**: Exactly what went wrong and where
- **Performance Metrics**: How fast your website loads
- **Browser Compatibility**: Results across different browsers

### 📋 **Test Categories Explained**

| Test Type | What It Checks | Why It Matters |
|-----------|----------------|----------------|
| **Smoke Tests** | Basic functionality works | Ensures your site doesn't crash |
| **Functional Tests** | Features work as intended | Verifies user can complete tasks |
| **Validation Tests** | Forms handle bad input properly | Prevents user frustration |
| **Security Tests** | No common vulnerabilities | Protects your users' data |
| **Accessibility Tests** | Site works for disabled users | Legal compliance & inclusivity |
| **Performance Tests** | Site loads quickly | Better user experience & SEO |

### 🚨 **What to Do When Tests Fail**

**Don't panic!** Failed tests are valuable feedback. Here's what to do:

1. **Check the HTML report** - It shows exactly what went wrong
2. **Look at screenshots** - Visual evidence of the issue
3. **Read the error message** - FormGenius explains what happened
4. **Fix the issue on your website** - Address the underlying problem
5. **Re-run the tests** - Verify your fix worked

---

## 🛠️ Advanced Configuration

### Custom Test Focus
```python
# Focus on specific areas of your website
config = {
    "analysis": {
        "focus_areas": ["forms", "navigation", "checkout"],
        "deep_analysis": True,
        "security_testing": True
    },
    "scenarios": {
        "include_security_tests": True,
        "include_accessibility_tests": True,
        "generate_negative_tests": True,
        "test_mobile_compatibility": True
    },
    "execution": {
        "parallel_workers": 4,
        "browser_types": ["chromium", "firefox", "webkit"],
        "screenshot_on_failure": True,
        "video_recording": True
    }
}

formgenius = FormGenius(config=config)
```

### Environment Variables
```bash
# Customize FormGenius behavior
export GEMINI_API_KEY="your-api-key"
export FORMGENIUS_DEBUG=true
export FORMGENIUS_MAX_WORKERS=4
export FORMGENIUS_TIMEOUT=30000
export FORMGENIUS_BROWSER=chromium
```

### Configuration Files
```ini
# formgenius.conf - Main configuration
[analysis]
deep_analysis = true
max_pages = 20
focus_areas = forms,navigation,security

[testing]
parallel_workers = 4
timeout = 30000
browsers = chromium,firefox,webkit

[reporting]
include_screenshots = true
include_videos = true
generate_html_report = true
```

---

## 🔍 Understanding FormGenius Components

### Core Architecture
```
FormGenius Framework
│
├── 🧠 AI Agents
│   ├── WebExplorer      # Crawls and analyzes websites
│   ├── TestStrategist   # Creates testing strategies  
│   ├── ScriptGenerator  # Writes test code
│   └── TestExecutor     # Runs tests and collects results
│
├── 🔬 Analyzers
│   ├── DOMAnalyzer      # Understands HTML structure
│   ├── FlowAnalyzer     # Maps user workflows
│   └── ElementDetector # Identifies interactive elements
│
├── ⚙️ Generators  
│   ├── ScenarioGenerator      # Creates test scenarios
│   └── PlaywrightCodeGenerator # Writes Playwright code
│
└── 🎯 Core System
    ├── FormGenius       # Main orchestrator
    ├── GeminiClient     # AI integration
    └── TestRunner       # Test execution engine
```

### How Components Work Together

1. **WebExplorer** visits your website and maps all pages and functionality
2. **DOMAnalyzer** & **ElementDetector** understand the structure and find testable elements  
3. **FlowAnalyzer** identifies user workflows and business processes
4. **TestStrategist** uses AI to create comprehensive testing strategies
5. **ScenarioGenerator** creates detailed test scenarios for each identified workflow
6. **PlaywrightCodeGenerator** writes professional test code following best practices
7. **TestExecutor** runs all tests in parallel across multiple browsers
8. **TestRunner** coordinates everything and generates detailed reports

---

## 🚀 Production Usage

### CI/CD Integration

#### GitHub Actions
```yaml
# .github/workflows/formgenius-tests.yml
name: FormGenius Automated Testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install FormGenius
      run: |
        pip install -r requirements.txt
        playwright install
    - name: Run FormGenius Tests
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: |
        python main.py quick https://mywebsite.com --output results.json
    - name: Upload Test Results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: |
          results.json
          test-results/
```

#### Jenkins Pipeline
```groovy
pipeline {
    agent any
    
    environment {
        GEMINI_API_KEY = credentials('gemini-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'playwright install'
            }
        }
        
        stage('Run FormGenius Tests') {
            steps {
                sh 'python main.py quick ${WEBSITE_URL} --workers 4'
            }
        }
        
        stage('Publish Results') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-results/html-report',
                    reportFiles: 'index.html',
                    reportName: 'FormGenius Test Report'
                ])
            }
        }
    }
}
```

### Monitoring & Alerts
```python
# Monitor your website continuously
import schedule
import time
from src.core.formgenius import FormGenius

async def daily_website_check():
    """Run FormGenius tests daily and alert on failures"""
    formgenius = FormGenius()
    
    results = await formgenius.full_analysis_and_testing(
        "https://mywebsite.com",
        max_workers=4
    )
    
    success_rate = results.get('success_rate', 0)
    
    if success_rate < 95:  # Alert if success rate drops below 95%
        send_alert(f"Website test success rate: {success_rate}%")
    
    return results

# Schedule daily checks
schedule.every().day.at("06:00").do(lambda: asyncio.run(daily_website_check()))

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

---

## 🛠️ Troubleshooting Common Issues

### Issue 1: "API Key Not Found"
```
❌ Error: GEMINI_API_KEY environment variable not set

✅ Solution:
1. Get a free API key from https://ai.google.dev
2. Create a .env file: echo "GEMINI_API_KEY=your_key" > .env
3. Make sure the .env file is in your FormGenius directory
```

### Issue 2: "Playwright Browsers Not Installed"
```
❌ Error: Browser 'chromium' is not installed

✅ Solution:
Run: playwright install
This downloads the browser engines needed for testing
```

### Issue 3: "Tests Are Failing"
```
❌ Some tests are failing unexpectedly

✅ Troubleshooting Steps:
1. Check if your website is accessible
2. Look at the HTML report for detailed error messages
3. Run tests in headed mode: python main.py quick https://site.com --headed
4. Check network connectivity and firewall settings
```

### Issue 4: "Slow Test Execution"
```
❌ Tests are taking too long to run

✅ Optimization Tips:
1. Reduce the number of workers: --workers 2
2. Limit analysis depth: --max-depth 1 --max-pages 5
3. Focus on specific areas: --focus forms,navigation
4. Use headless mode (default): --headless
```

### Issue 5: "Out of Memory Errors"
```
❌ FormGenius crashes with memory errors

✅ Solutions:
1. Reduce parallel workers: --workers 1
2. Limit analysis scope: --max-pages 10
3. Close other applications using memory
4. Use a more powerful machine for large websites
```

---

## 🤝 Getting Help & Contributing

### 📚 **Learning Resources**
- **📖 [Complete Documentation](https://github.com/FormGenius/FormGenius/wiki)** - Detailed guides and tutorials
- **🎥 [Video Tutorials](https://youtube.com/FormGenius)** - Step-by-step video guides  
- **💬 [Community Forum](https://github.com/FormGenius/FormGenius/discussions)** - Ask questions and share tips
- **📰 [Blog](https://blog.formgenius.dev)** - Testing tips and best practices

### 🆘 **Getting Support**
- **🐛 [Report Bugs](https://github.com/FormGenius/FormGenius/issues)** - Found an issue? Let us know!
- **💡 [Request Features](https://github.com/FormGenius/FormGenius/issues)** - Suggest improvements
- **✉️ [Email Support](mailto:support@formgenius.dev)** - Direct help from our team
- **💬 [Discord Community](https://discord.gg/formgenius)** - Real-time chat with users

### 🚀 **Contributing to FormGenius**
We welcome contributions from beginners to experts!

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/yourusername/FormGenius.git

# 3. Create a feature branch
git checkout -b my-new-feature

# 4. Make your changes and test them
python -m pytest tests/

# 5. Submit a pull request
```

**Areas where you can contribute:**
- 📝 **Documentation**: Help improve our guides and examples
- 🐛 **Bug Fixes**: Fix issues and improve stability  
- ✨ **New Features**: Add new testing capabilities
- 🌍 **Translations**: Help make FormGenius available in other languages
- 📚 **Examples**: Create tutorials for specific use cases

---

## 🗺️ Roadmap & Future Features

### Version 1.1 (Coming Soon)
- [ ] 📱 **Mobile App Testing** - Test mobile applications with Appium integration
- [ ] 🔌 **API Testing** - Automatically test REST APIs and GraphQL endpoints  
- [ ] 🗄️ **Database Testing** - Validate data integrity and database operations
- [ ] 🎨 **Visual Testing** - Detect visual regressions and UI changes
- [ ] 🌐 **Multi-language Support** - Test websites in different languages

### Version 1.2 (Future)
- [ ] 🤖 **Custom AI Models** - Train FormGenius on your specific domain
- [ ] 📊 **Advanced Analytics** - Deeper insights into test results and trends
- [ ] 🔄 **Self-Healing Tests** - Automatically fix broken tests when websites change
- [ ] 🏢 **Enterprise Features** - Team collaboration, advanced reporting, SSO
- [ ] ☁️ **Cloud Platform** - Run FormGenius tests in the cloud

### Long-term Vision
- [ ] 🧠 **AGI Testing Assistant** - AI that understands complex business logic
- [ ] 🔮 **Predictive Testing** - Predict issues before they happen
- [ ] 🌍 **Global Test Network** - Distributed testing across continents
- [ ] 📱 **No-Code Interface** - Visual test creation for non-technical users

---

## 📄 License & Legal

FormGenius is open source software licensed under the **MIT License**. This means:

✅ **You can use it freely** for personal and commercial projects  
✅ **You can modify it** to fit your needs  
✅ **You can distribute it** with your own projects  
✅ **No warranty or liability** - use at your own risk  

See the [LICENSE](LICENSE) file for complete details.

### Third-Party Acknowledgments
FormGenius is built on the shoulders of giants:

- **🎭 [Playwright](https://playwright.dev)** - Microsoft's excellent browser automation framework
- **🧠 [Google Gemini](https://ai.google.dev)** - Advanced AI capabilities for intelligent testing
- **🧪 [Pytest](https://pytest.org)** - Python's premier testing framework  
- **🎲 [Faker](https://faker.readthedocs.io)** - Realistic test data generation
- **♿ [Axe Core](https://github.com/dequelabs/axe-core)** - Accessibility testing engine

---

## 🎉 Final Words

**Congratulations!** 🎊 You now understand how FormGenius can revolutionize your web testing process. 

### What You've Learned:
✅ What FormGenius is and why it's powerful  
✅ How to install and set it up  
✅ How to run your first tests  
✅ How to understand and act on test results  
✅ How to integrate it into your development workflow  
✅ How to get help when you need it  

### Your Next Steps:
1. **🚀 Try it out** - Test your first website with FormGenius
2. **📚 Explore** - Check out the examples and advanced features  
3. **🤝 Join the community** - Connect with other FormGenius users
4. **📈 Scale up** - Integrate FormGenius into your CI/CD pipeline
5. **🌟 Share** - Tell others about your experience with FormGenius

### Remember:
> **"The best test is the one that runs automatically"** - FormGenius Team

FormGenius transforms website testing from a complex, time-consuming task into a simple, one-command operation. Whether you're testing a personal blog or a complex enterprise application, FormGenius has you covered.

**Happy Testing!** 🧪✨

---

**FormGenius** - *Making AI-Powered Web Testing Accessible to Everyone* 🤖🌐

Made with ❤️ by the FormGenius team | [Website](https://formgenius.dev) | [GitHub](https://github.com/FormGenius/FormGenius) | [Documentation](https://docs.formgenius.dev)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for Playwright)
- Gemini API key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/FormGenius/FormGenius.git
cd FormGenius
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers:**
```bash
playwright install
```

5. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Basic Usage

```python
import asyncio
from src.core.formgenius import FormGenius

async def main():
    # Initialize FormGenius
    formgenius = FormGenius()
    
    # Analyze a website
    analysis = await formgenius.analyze_website("https://example.com")
    
    # Generate test scenarios
    scenarios = await formgenius.generate_test_scenarios(analysis)
    
    # Generate Playwright tests
    await formgenius.generate_playwright_tests(
        scenarios, 
        "https://example.com",
        output_dir="./generated_tests"
    )

asyncio.run(main())
```

## 📖 Documentation

### Core Components

#### 🔍 Web Explorer Agent
Intelligently crawls and explores websites to understand structure and functionality.

```python
from src.agents.web_explorer import WebExplorer

explorer = WebExplorer()
page_data = await explorer.explore_page("https://example.com")
```

#### 🧠 Test Strategist Agent
AI-powered test strategy generation based on website analysis.

```python
from src.agents.test_strategist import TestStrategist

strategist = TestStrategist()
strategy = await strategist.create_test_strategy(analysis_data)
```

#### ⚡ Script Generator Agent
Generates high-quality Playwright test code with best practices.

```python
from src.agents.script_generator import ScriptGenerator

generator = ScriptGenerator()
test_code = await generator.generate_test_scripts(scenarios)
```

#### 🏃 Test Executor Agent
Manages test execution, monitoring, and result collection.

```python
from src.agents.test_executor import TestExecutor

executor = TestExecutor()
results = await executor.execute_tests("./generated_tests")
```

### Analyzers

#### 📊 DOM Analyzer
Deep analysis of HTML structure, semantics, and accessibility.

```python
from src.analyzers.dom_analyzer import DOMAnalyzer

analyzer = DOMAnalyzer()
dom_data = await analyzer.analyze_page(page_content)
```

#### 🔄 Flow Analyzer
Identifies user flows, navigation patterns, and business workflows.

```python
from src.analyzers.flow_analyzer import FlowAnalyzer

flow_analyzer = FlowAnalyzer()
flows = await flow_analyzer.analyze_user_flows(page_data)
```

#### 🎯 Element Detector
Intelligent detection and categorization of web elements.

```python
from src.analyzers.element_detector import ElementDetector

detector = ElementDetector()
elements = await detector.detect_elements(page_content)
```

### Generators

#### 🧪 Scenario Generator
Creates comprehensive test scenarios covering all aspects of functionality.

```python
from src.generators.scenario_generator import ScenarioGenerator

scenario_gen = ScenarioGenerator()
scenarios = await scenario_gen.generate_scenarios(analysis_data)
```

#### 🎭 Playwright Code Generator
Generates production-ready Playwright test code with Page Object Model.

```python
from src.generators.playwright_codegen import PlaywrightCodeGenerator

codegen = PlaywrightCodeGenerator()
test_files = await codegen.generate_test_suite(scenarios, base_url)
```

## 🛠️ Configuration

FormGenius supports extensive configuration through multiple methods:

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key
FORMGENIUS_DEBUG=true
FORMGENIUS_MAX_WORKERS=4
```

### Configuration Files
- `config/formgenius.conf` - Main configuration
- `config/playwright.config.js` - Playwright settings
- `config/default_config.py` - Python configuration

### Programmatic Configuration
```python
config = {
    "analysis": {
        "deep_analysis": True,
        "max_pages": 10
    },
    "testing": {
        "parallel_workers": 4,
        "timeout": 30000
    }
}

formgenius = FormGenius(config=config)
```

## 📝 Examples

### Basic Website Testing
```bash
python examples/basic_usage.py
```

### E-commerce Testing
```bash
python examples/ecommerce_testing.py
```

### Form Testing
```bash
python examples/form_testing.py
```

### Custom Testing Scenarios
```python
# Custom configuration for specific needs
config = {
    "analysis": {
        "focus_areas": ["forms", "navigation", "checkout"],
        "deep_analysis": True
    },
    "scenarios": {
        "include_security_tests": True,
        "include_accessibility_tests": True,
        "generate_negative_tests": True
    }
}

formgenius = FormGenius(config=config)
result = await formgenius.analyze_and_test("https://mysite.com")
```

## 🧪 Running Tests

### Command Line Interface
```bash
# Run generated tests
python -m src.core.test_runner ./generated_tests --workers 4

# Run with specific browser
python -m src.core.test_runner ./generated_tests --browser firefox

# Run in headed mode
python -m src.core.test_runner ./generated_tests --headed
```

### Programmatic Execution
```python
from src.core.test_runner import TestRunner

runner = TestRunner(
    output_dir="./test_results",
    max_workers=4,
    browser="chromium"
)

result = await runner.run_test_suite("./generated_tests")
print(f"Success rate: {result.success_rate:.1f}%")
```

## 📊 Reports and Monitoring

FormGenius generates comprehensive reports in multiple formats:

- **HTML Report**: Rich interactive report with charts and detailed results
- **JSON Report**: Machine-readable results for CI/CD integration
- **JUnit XML**: Standard format for most CI/CD platforms
- **Screenshots**: Captured on test failures
- **Videos**: Full test execution recordings
- **Traces**: Detailed execution traces for debugging

### Report Location
```
test_results/
├── test_report.html      # Main HTML report
├── test_report.json      # JSON results
├── junit_report.xml      # JUnit XML
├── screenshots/          # Failure screenshots
├── videos/              # Test execution videos
└── traces/              # Playwright traces
```

## 🔧 Advanced Features

### AI-Enhanced Assertions
FormGenius uses AI to generate intelligent assertions based on page context:

```python
# AI generates contextually appropriate assertions
await formgenius.generate_smart_assertions(page_element, context)
```

### Auto-Healing Selectors
Selectors that automatically adapt to page changes:

```python
# Self-healing selectors that adapt to DOM changes
smart_selector = await formgenius.create_resilient_selector(element)
```

### Visual Regression Testing
Automated visual comparison and change detection:

```python
config = {
    "visual_testing": {
        "enabled": True,
        "threshold": 0.1,
        "ignore_regions": ["#dynamic-content"]
    }
}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run linting
flake8 src/
black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev) for the excellent testing framework
- [Google Gemini](https://ai.google.dev) for AI capabilities
- [Faker](https://faker.readthedocs.io) for test data generation
- [Axe Core](https://github.com/dequelabs/axe-core) for accessibility testing

## 📞 Support

- 📖 [Documentation](https://github.com/FormGenius/FormGenius/wiki)
- 🐛 [Issue Tracker](https://github.com/FormGenius/FormGenius/issues)
- 💬 [Discussions](https://github.com/FormGenius/FormGenius/discussions)
- ✉️ [Email Support](mailto:support@formgenius.dev)

## 🗺️ Roadmap

### Version 1.1 (Coming Soon)
- [ ] API testing integration
- [ ] Database testing capabilities
- [ ] Mobile app testing support
- [ ] Advanced AI models integration

### Version 1.2 (Future)
- [ ] Real-time test monitoring
- [ ] Test optimization recommendations
- [ ] Custom AI model training
- [ ] Enterprise features

---

**FormGenius** - Revolutionizing web testing with AI 🚀

Made with ❤️ by the FormGenius team