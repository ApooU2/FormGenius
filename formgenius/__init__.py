"""
FormGenius - AI-Powered Form Automation Agent

A sophisticated AI agent that automatically fills out and submits web forms,
including Power Apps forms, using Playwright MCP for comprehensive user testing.
"""

__version__ = "1.0.0"
__author__ = "FormGenius Team"

from .core.agent import FormGeniusAgent
from .core.form_detector import FormDetector
from .core.data_generator import DataGenerator
from .integrations.playwright_mcp import PlaywrightMCPClient
from .integrations.power_apps import PowerAppsHandler

__all__ = [
    "FormGeniusAgent",
    "FormDetector", 
    "DataGenerator",
    "PlaywrightMCPClient",
    "PowerAppsHandler"
]
