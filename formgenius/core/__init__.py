"""
FormGenius Core Module
Contains the main components for form detection, data generation, and automation
"""

from .agent import FormGeniusAgent
from .config import Config
from .data_generator import DataGenerator
from .form_detector import FormDetector
from .reporter import TestReporter

__all__ = [
    'FormGeniusAgent',
    'Config',
    'DataGenerator', 
    'FormDetector',
    'TestReporter'
]
