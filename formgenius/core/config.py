"""
Configuration management for FormGenius
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # dotenv not installed, continue with system environment variables


@dataclass
class Config:
    """Configuration class for FormGenius."""
    
    # Browser settings
    headless: bool = True
    browser_type: str = "chromium"
    timeout: int = 30000
    slowmo: int = 100
    
    # AI settings
    ai_provider: str = "gemini"
    ai_model: str = "gemini-pro"
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    
    # Form filling settings
    retry_attempts: int = 3
    wait_between_fields: int = 500
    validate_before_submit: bool = True
    
    # Output settings
    output_directory: str = "test_results"
    save_screenshots: bool = True
    save_html: bool = True
    
    # MCP settings
    mcp_server_url: str = "http://localhost:8000"
    mcp_timeout: int = 30000
    
    # Power Apps settings
    power_apps_wait_time: int = 5000
    power_apps_selectors: Dict[str, str] = field(default_factory=lambda: {
        'app_container': '[data-control-name]',
        'form_container': '.powerapps-form',
        'input_field': '[role="textbox"]',
        'submit_button': '[data-control-name*="submit"]'
    })
    
    def __post_init__(self):
        """Initialize configuration after creation."""
        # Load from environment variables if not set
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        
        if not self.gemini_model:
            self.gemini_model = os.getenv('GEMINI_MODEL') or self.ai_model
        
        # Create output directory
        Path(self.output_directory).mkdir(exist_ok=True)
    
    @property 
    def browser_options(self) -> Dict[str, Any]:
        """Get browser options for Playwright."""
        return {
            'headless': self.headless,
            'timeout': self.timeout,
            'slow_mo': self.slowmo
        }
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file."""
        if not Path(config_path).exists():
            return cls()
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
        
        # Flatten nested configuration for dataclass
        flat_config = {}
        
        # Browser settings
        if 'browser' in config_data:
            browser_config = config_data['browser']
            flat_config['headless'] = browser_config.get('headless', True)
            flat_config['browser_type'] = browser_config.get('type', 'chromium')
            flat_config['timeout'] = browser_config.get('timeout', 30000)
            flat_config['slowmo'] = browser_config.get('slowmo', 100)
        
        # AI settings
        if 'ai' in config_data:
            ai_config = config_data['ai']
            flat_config['ai_provider'] = ai_config.get('provider', 'gemini')
            flat_config['ai_model'] = ai_config.get('model', 'gemini-pro')
            flat_config['gemini_api_key'] = ai_config.get('api_key')
        
        # Form filling settings
        if 'form_filling' in config_data:
            form_config = config_data['form_filling']
            flat_config['retry_attempts'] = form_config.get('retry_attempts', 3)
            flat_config['wait_between_fields'] = form_config.get('field_delay', 500)
            flat_config['validate_before_submit'] = form_config.get('validate_before_submit', True)
        
        # Output settings
        if 'output' in config_data:
            output_config = config_data['output']
            flat_config['output_directory'] = output_config.get('directory', 'test_results')
            flat_config['save_screenshots'] = output_config.get('save_screenshots', True)
            flat_config['save_html'] = output_config.get('save_html', True)
        
        # MCP settings
        if 'mcp_server' in config_data:
            mcp_config = config_data['mcp_server']
            flat_config['mcp_server_url'] = mcp_config.get('url', 'http://localhost:8000')
            flat_config['mcp_timeout'] = mcp_config.get('timeout', 30000)
        
        # Power Apps settings
        if 'power_apps' in config_data:
            pa_config = config_data['power_apps']
            flat_config['power_apps_wait_time'] = pa_config.get('wait_time', 5000)
            if 'selectors' in pa_config:
                flat_config['power_apps_selectors'] = pa_config['selectors']
        
        return cls(**flat_config)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file (alias for from_file)."""
        return cls.from_file(config_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'browser': {
                'headless': self.headless,
                'browser_type': self.browser_type,
                'timeout': self.timeout,
                'slowmo': self.slowmo
            },
            'ai': {
                'provider': self.ai_provider,
                'model': self.ai_model,
                'api_key': self.gemini_api_key
            },
            'form_filling': {
                'retry_attempts': self.retry_attempts,
                'wait_between_fields': self.wait_between_fields,
                'validate_before_submit': self.validate_before_submit
            },
            'output': {
                'directory': self.output_directory,
                'save_screenshots': self.save_screenshots,
                'save_html': self.save_html
            },
            'mcp': {
                'server_url': self.mcp_server_url,
                'timeout': self.mcp_timeout
            },
            'power_apps': {
                'wait_time': self.power_apps_wait_time,
                'selectors': self.power_apps_selectors
            }
        }
