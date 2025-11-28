"""
Brand World Model - Brand Knowledge Base

This module manages the storage and retrieval of brand profiles
and learned design patterns.
"""

from .knowledge_base import BrandKnowledgeBase
from .schemas import BrandSchema, TemplateSchema, SlideSchema

__all__ = ['BrandKnowledgeBase', 'BrandSchema', 'TemplateSchema', 'SlideSchema']
