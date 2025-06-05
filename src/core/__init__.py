"""
FormGenius Core Module

This module contains the core functionality of the FormGenius framework.
"""

from .formgenius import FormGenius
from .gemini_client import GeminiClient
from .test_runner import TestRunner, TestResult, TestSuiteResult

__all__ = [
    'FormGenius',
    'GeminiClient', 
    'TestRunner',
    'TestResult',
    'TestSuiteResult'
]

__version__ = "1.0.0"