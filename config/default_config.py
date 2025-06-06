"""
Default configuration for FormGenius framework.
"""

# Gemini AI Configuration
GEMINI_CONFIG = {
    "model": "gemini-2.0-flash-exp",
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 0.8,
    "top_k": 40
}

# Web Scraping Configuration
SCRAPING_CONFIG = {
    "timeout": 30000,  # 30 seconds
    "wait_for_load": 2000,  # 2 seconds
    "max_depth": 3,
    "max_pages": 50,
    "user_agent": "FormGenius/1.0 (+https://github.com/FormGenius/FormGenius)",
    "concurrent_requests": 5,
    "respect_robots_txt": True,
    "delay_between_requests": 1.0  # seconds
}

# Browser Configuration
BROWSER_CONFIG = {
    "headless": True,
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "ignore_https_errors": True,
    "accept_downloads": True,
    "locale": "en-US",
    "timezone": "America/New_York"
}

# Test Generation Configuration
TEST_CONFIG = {
    "test_timeout": 30000,  # 30 seconds per test
    "max_test_scenarios": 100,
    "page_load_timeout": 30000,
    "element_timeout": 10000,
    "screenshot_on_failure": True,
    "video_recording": True,
    "trace_recording": True,
    "retry_attempts": 2
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "max_elements_per_type": 50,
    "min_confidence_score": 0.7,
    "analyze_accessibility": True,
    "analyze_performance": True,
    "analyze_security": True,
    "deep_analysis": True
}

# Output Configuration
OUTPUT_CONFIG = {
    "test_output_dir": "generated_tests",
    "reports_dir": "test_reports",
    "screenshots_dir": "screenshots",
    "videos_dir": "videos",
    "traces_dir": "traces",
    "clean_old_results": True,
    "max_result_age_days": 30
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": True,
    "console_logging": True,
    "max_log_size": "10MB",
    "backup_count": 5
}

# Security Configuration
SECURITY_CONFIG = {
    "check_ssl_certificates": True,
    "check_csp_headers": True,
    "check_xss_protection": True,
    "check_clickjacking_protection": True,
    "scan_for_secrets": True,
    "check_auth_bypass": True
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "lighthouse_enabled": True,
    "performance_budget": {
        "first_contentful_paint": 2000,  # ms
        "largest_contentful_paint": 4000,  # ms
        "cumulative_layout_shift": 0.1,
        "first_input_delay": 100  # ms
    },
    "resource_monitoring": True,
    "memory_monitoring": True
}

# Accessibility Configuration
ACCESSIBILITY_CONFIG = {
    "axe_core_enabled": True,
    "wcag_level": "AA",  # A, AA, AAA
    "check_color_contrast": True,
    "check_keyboard_navigation": True,
    "check_screen_reader_support": True,
    "check_focus_management": True
}

# Data Generation Configuration
DATA_CONFIG = {
    "faker_locale": "en_US",
    "generate_realistic_data": True,
    "data_variation_count": 5,
    "use_boundary_values": True,
    "include_negative_tests": True,
    "custom_data_patterns": {}
}

# Reporting Configuration
REPORTING_CONFIG = {
    "generate_html_report": True,
    "generate_json_report": True,
    "generate_junit_xml": True,
    "generate_csv_report": True,
    "include_screenshots": True,
    "include_video_links": True,
    "include_trace_links": True,
    "email_notifications": False
}

# Advanced Features
ADVANCED_CONFIG = {
    "ai_enhanced_assertions": True,
    "smart_wait_strategies": True,
    "auto_healing_selectors": True,
    "visual_regression_testing": False,
    "api_testing_integration": False,
    "database_testing_integration": False
}
