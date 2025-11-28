"""
Base Generator - Abstract base class for template generators

This defines the interface that all generators must implement,
ensuring consistency across output formats.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from brand.schemas import BrandSchema, SlideSchema, TemplateSchema


class BaseGenerator(ABC):
    """
    Abstract base class for presentation generators.

    All generators (PowerPoint, reveal.js, etc.) inherit from this
    to ensure a consistent interface for the world model.
    """

    def __init__(self, brand: BrandSchema):
        """
        Initialize generator with a brand profile.

        Args:
            brand: BrandSchema containing brand identity information
        """
        self.brand = brand
        self.slides: List[Dict[str, Any]] = []

    @abstractmethod
    def generate(self, content: List[Dict[str, Any]], output_path: str) -> str:
        """
        Generate a presentation from content.

        Args:
            content: List of slide content dictionaries
            output_path: Path to save the generated file

        Returns:
            Path to the generated file
        """
        pass

    @abstractmethod
    def add_slide(
        self,
        layout_type: str,
        content: Dict[str, Any]
    ) -> None:
        """
        Add a slide to the presentation.

        Args:
            layout_type: Type of slide layout
            content: Slide content (title, body, images, etc.)
        """
        pass

    @abstractmethod
    def save(self, output_path: str) -> str:
        """
        Save the presentation to a file.

        Args:
            output_path: Path to save the file

        Returns:
            Path to the saved file
        """
        pass

    def get_color(self, role: str) -> str:
        """
        Get a color by its role from the brand.

        Args:
            role: Color role (primary, secondary, accent, etc.)

        Returns:
            Hex color code
        """
        for color in self.brand.colors:
            if color.role.value == role:
                return color.hex
        # Default fallbacks
        defaults = {
            "primary": "#1E40AF",
            "secondary": "#6B7280",
            "accent": "#F59E0B",
            "background": "#FFFFFF",
            "text": "#1F2937"
        }
        return defaults.get(role, "#000000")

    def get_font(self, type: str) -> Dict[str, Any]:
        """
        Get font settings by type.

        Args:
            type: Font type (heading, body, caption)

        Returns:
            Font configuration dictionary
        """
        if type == "heading":
            font = self.brand.typography.heading
        elif type == "caption" and self.brand.typography.caption:
            font = self.brand.typography.caption
        else:
            font = self.brand.typography.body

        return {
            "family": font.family,
            "size": font.size_base,
            "weight": font.weight.value,
            "line_height": font.line_height
        }

    def get_layout(self, layout_type: str) -> Optional[SlideSchema]:
        """
        Get a layout pattern from the brand.

        Args:
            layout_type: Type of layout to retrieve

        Returns:
            SlideSchema or None if not found
        """
        for layout in self.brand.layout_patterns:
            if layout.layout_type.value == layout_type:
                return layout
        return None

    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def generate_from_template(
        self,
        template: TemplateSchema,
        content_map: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Generate presentation from a template with content mapping.

        Args:
            template: TemplateSchema defining slide structure
            content_map: Dictionary mapping placeholders to content
            output_path: Path to save the file

        Returns:
            Path to generated file
        """
        for slide in template.slides:
            slide_content = {}
            for element in slide.elements:
                if element.content_placeholder and element.content_placeholder in content_map:
                    slide_content[element.type] = content_map[element.content_placeholder]

            self.add_slide(slide.layout_type.value, slide_content)

        return self.save(output_path)
