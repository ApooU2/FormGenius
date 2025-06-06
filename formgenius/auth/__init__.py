"""
FormGenius Authentication Module
Handles authentication for various platforms including Microsoft Office 365
"""

from .microsoft_auth import MicrosoftAuthenticator

__all__ = [
    'MicrosoftAuthenticator'
]
