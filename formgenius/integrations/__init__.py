"""
FormGenius Integrations Module
Contains integrations with external services and platforms
"""

from .playwright_mcp import PlaywrightMCPClient
from .power_apps import PowerAppsHandler

__all__ = [
    'PlaywrightMCPClient',
    'PowerAppsHandler'
]
