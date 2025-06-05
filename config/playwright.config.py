"""
Playwright Configuration for FormGenius
This file configures Playwright test execution settings for Python/pytest
"""
import pytest
from playwright.sync_api import Browser, BrowserContext, Page

# Browser configuration
BROWSER_CONFIG = {
    "headless": True,
    "viewport": {"width": 1920, "height": 1080},
    "ignore_https_errors": True,
    "accept_downloads": True,
    "locale": "en-US",
    "timezone_id": "America/New_York",
    "screen": {"width": 1920, "height": 1080},
}

# Test configuration
TEST_CONFIG = {
    "timeout": 30000,  # 30 seconds
    "expect_timeout": 10000,  # 10 seconds
    "base_url": None,  # Set this for your specific application
    "test_dir": "./generated_tests",
    "output_dir": "./test-results",
}

# Retry configuration
RETRY_CONFIG = {
    "retries": 2,
    "workers": 4,
}

# Artifact configuration
ARTIFACT_CONFIG = {
    "screenshot_mode": "only-on-failure",
    "video_mode": "retain-on-failure",
    "trace_mode": "retain-on-failure",
    "video_dir": "./test-results/videos",
    "screenshot_dir": "./test-results/screenshots",
    "trace_dir": "./test-results/traces",
}

# Browser types to test against
BROWSERS = ["chromium", "firefox", "webkit"]

@pytest.fixture(scope="session")
def browser_config():
    """Returns browser configuration settings"""
    return BROWSER_CONFIG

@pytest.fixture(scope="session")
def test_config():
    """Returns test configuration settings"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def artifact_config():
    """Returns artifact configuration settings"""
    return ARTIFACT_CONFIG

@pytest.fixture(scope="session")
def browser_context_args(artifact_config):
    """Configure browser context with recording settings"""
    return {
        **BROWSER_CONFIG,
        "record_video_dir": artifact_config["video_dir"] if artifact_config["video_mode"] != "off" else None,
        "record_video_size": {"width": 1920, "height": 1080},
    }

def configure_page(page: Page, test_config: dict) -> None:
    """Configure page with timeout and other settings"""
    page.set_default_timeout(test_config["timeout"])
    page.set_default_navigation_timeout(test_config["timeout"])

def take_screenshot_on_failure(page: Page, request, artifact_config: dict) -> None:
    """Take screenshot on test failure"""
    if request.node.rep_call.failed and artifact_config["screenshot_mode"] in ["always", "only-on-failure"]:
        screenshot_path = f"{artifact_config['screenshot_dir']}/{request.node.name}.png"
        page.screenshot(path=screenshot_path, full_page=True)
