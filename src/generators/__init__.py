"""
Brand World Model - Template Generators

This module generates presentation templates in various formats
based on learned brand patterns.
"""

from .pptx_generator import PowerPointGenerator
from .revealjs_generator import RevealJSGenerator
from .base import BaseGenerator

__all__ = ['PowerPointGenerator', 'RevealJSGenerator', 'BaseGenerator']
