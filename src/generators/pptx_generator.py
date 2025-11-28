"""
PowerPoint Generator - Generates PPTX presentations from brand profiles

Uses python-pptx to create branded PowerPoint presentations
that follow the learned brand patterns.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from brand.schemas import BrandSchema
from .base import BaseGenerator


class PowerPointGenerator(BaseGenerator):
    """
    Generates PowerPoint presentations with brand styling.

    This is the "action" component of the world model for PPTX output,
    translating brand knowledge into actual presentation files.
    """

    # Slide dimensions (16:9 aspect ratio)
    SLIDE_WIDTH = Inches(13.333)
    SLIDE_HEIGHT = Inches(7.5)

    def __init__(self, brand: BrandSchema):
        super().__init__(brand)
        self.prs = Presentation()
        self.prs.slide_width = self.SLIDE_WIDTH
        self.prs.slide_height = self.SLIDE_HEIGHT

    def generate(self, content: List[Dict[str, Any]], output_path: str) -> str:
        """
        Generate a complete presentation from content list.

        Args:
            content: List of slide content dictionaries, each with:
                - layout: Layout type (title_slide, content, two_column, etc.)
                - title: Slide title
                - body: Body text or bullet points
                - image: Optional image path
                - notes: Optional speaker notes

        Returns:
            Path to the generated PPTX file
        """
        for slide_content in content:
            layout_type = slide_content.get('layout', 'content')
            self.add_slide(layout_type, slide_content)

        return self.save(output_path)

    def add_slide(self, layout_type: str, content: Dict[str, Any]) -> None:
        """Add a slide with the specified layout and content."""

        # Use blank layout and build custom
        blank_layout = self.prs.slide_layouts[6]  # Blank layout
        slide = self.prs.slides.add_slide(blank_layout)

        # Set background color
        background = slide.background
        fill = background.fill
        fill.solid()
        bg_color = self.get_color("background")
        fill.fore_color.rgb = RgbColor(*self.hex_to_rgb(bg_color))

        # Build slide based on layout type
        if layout_type == "title_slide":
            self._build_title_slide(slide, content)
        elif layout_type == "section_header":
            self._build_section_slide(slide, content)
        elif layout_type == "two_column":
            self._build_two_column_slide(slide, content)
        elif layout_type == "image_left":
            self._build_image_left_slide(slide, content)
        elif layout_type == "image_right":
            self._build_image_right_slide(slide, content)
        elif layout_type == "quote":
            self._build_quote_slide(slide, content)
        else:
            self._build_content_slide(slide, content)

        # Add logo if specified in brand
        if self.brand.logo.primary_path and os.path.exists(self.brand.logo.primary_path):
            self._add_logo(slide)

        # Add speaker notes
        if content.get('notes'):
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = content['notes']

    def _build_title_slide(self, slide, content: Dict[str, Any]) -> None:
        """Build a title slide layout"""
        # Title - centered, large
        title = content.get('title', '')
        subtitle = content.get('subtitle', '')

        # Title text box
        title_box = slide.shapes.add_textbox(
            Inches(1), Inches(2.5),
            Inches(11.333), Inches(1.5)
        )
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(54)
        title_para.font.bold = True
        title_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("primary")))
        title_para.alignment = PP_ALIGN.CENTER
        title_font = self.get_font("heading")
        title_para.font.name = title_font["family"]

        # Subtitle
        if subtitle:
            sub_box = slide.shapes.add_textbox(
                Inches(1), Inches(4.2),
                Inches(11.333), Inches(1)
            )
            sub_frame = sub_box.text_frame
            sub_para = sub_frame.paragraphs[0]
            sub_para.text = subtitle
            sub_para.font.size = Pt(24)
            sub_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("text")))
            sub_para.alignment = PP_ALIGN.CENTER

    def _build_content_slide(self, slide, content: Dict[str, Any]) -> None:
        """Build a standard content slide"""
        title = content.get('title', '')
        body = content.get('body', '')
        bullets = content.get('bullets', [])

        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.75), Inches(0.5),
            Inches(11.833), Inches(1)
        )
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(36)
        title_para.font.bold = True
        title_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("primary")))
        title_font = self.get_font("heading")
        title_para.font.name = title_font["family"]

        # Body content
        body_box = slide.shapes.add_textbox(
            Inches(0.75), Inches(1.7),
            Inches(11.833), Inches(5.3)
        )
        body_frame = body_box.text_frame
        body_frame.word_wrap = True

        text_color = RgbColor(*self.hex_to_rgb(self.get_color("text")))
        body_font = self.get_font("body")

        if bullets:
            for i, bullet in enumerate(bullets):
                if i == 0:
                    para = body_frame.paragraphs[0]
                else:
                    para = body_frame.add_paragraph()
                para.text = f"• {bullet}"
                para.font.size = Pt(20)
                para.font.color.rgb = text_color
                para.font.name = body_font["family"]
                para.space_after = Pt(12)
        elif body:
            body_para = body_frame.paragraphs[0]
            body_para.text = body
            body_para.font.size = Pt(20)
            body_para.font.color.rgb = text_color
            body_para.font.name = body_font["family"]

    def _build_section_slide(self, slide, content: Dict[str, Any]) -> None:
        """Build a section header slide"""
        title = content.get('title', '')

        # Accent bar
        accent_color = self.get_color("accent")
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(3),
            Inches(13.333), Inches(1.5)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RgbColor(*self.hex_to_rgb(accent_color))
        shape.line.fill.background()

        # Title centered on accent bar
        title_box = slide.shapes.add_textbox(
            Inches(1), Inches(3.2),
            Inches(11.333), Inches(1.1)
        )
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(44)
        title_para.font.bold = True
        title_para.font.color.rgb = RgbColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER

    def _build_two_column_slide(self, slide, content: Dict[str, Any]) -> None:
        """Build a two-column slide"""
        title = content.get('title', '')
        left_content = content.get('left', content.get('body', ''))
        right_content = content.get('right', '')

        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.75), Inches(0.5),
            Inches(11.833), Inches(1)
        )
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(36)
        title_para.font.bold = True
        title_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("primary")))

        # Left column
        left_box = slide.shapes.add_textbox(
            Inches(0.75), Inches(1.7),
            Inches(5.5), Inches(5.3)
        )
        left_frame = left_box.text_frame
        left_frame.word_wrap = True
        left_para = left_frame.paragraphs[0]
        left_para.text = left_content if isinstance(left_content, str) else '\n'.join(left_content)
        left_para.font.size = Pt(18)
        left_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("text")))

        # Right column
        right_box = slide.shapes.add_textbox(
            Inches(6.75), Inches(1.7),
            Inches(5.5), Inches(5.3)
        )
        right_frame = right_box.text_frame
        right_frame.word_wrap = True
        right_para = right_frame.paragraphs[0]
        right_para.text = right_content if isinstance(right_content, str) else '\n'.join(right_content)
        right_para.font.size = Pt(18)
        right_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("text")))

    def _build_image_left_slide(self, slide, content: Dict[str, Any]) -> None:
        """Build slide with image on left, content on right"""
        title = content.get('title', '')
        body = content.get('body', '')
        image_path = content.get('image', '')

        # Title
        title_box = slide.shapes.add_textbox(
            Inches(6.75), Inches(0.5),
            Inches(5.833), Inches(1)
        )
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(32)
        title_para.font.bold = True
        title_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("primary")))

        # Image placeholder on left
        if image_path and os.path.exists(image_path):
            slide.shapes.add_picture(
                image_path,
                Inches(0.5), Inches(0.75),
                Inches(5.5), Inches(6)
            )
        else:
            # Add placeholder shape
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0.5), Inches(0.75),
                Inches(5.5), Inches(6)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = RgbColor(229, 231, 235)

        # Body on right
        body_box = slide.shapes.add_textbox(
            Inches(6.75), Inches(1.7),
            Inches(5.833), Inches(5.3)
        )
        body_frame = body_box.text_frame
        body_frame.word_wrap = True
        body_para = body_frame.paragraphs[0]
        body_para.text = body
        body_para.font.size = Pt(18)
        body_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("text")))

    def _build_image_right_slide(self, slide, content: Dict[str, Any]) -> None:
        """Build slide with content on left, image on right"""
        title = content.get('title', '')
        body = content.get('body', '')
        image_path = content.get('image', '')

        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.75), Inches(0.5),
            Inches(5.833), Inches(1)
        )
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(32)
        title_para.font.bold = True
        title_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("primary")))

        # Body on left
        body_box = slide.shapes.add_textbox(
            Inches(0.75), Inches(1.7),
            Inches(5.833), Inches(5.3)
        )
        body_frame = body_box.text_frame
        body_frame.word_wrap = True
        body_para = body_frame.paragraphs[0]
        body_para.text = body
        body_para.font.size = Pt(18)
        body_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("text")))

        # Image on right
        if image_path and os.path.exists(image_path):
            slide.shapes.add_picture(
                image_path,
                Inches(7.333), Inches(0.75),
                Inches(5.5), Inches(6)
            )
        else:
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(7.333), Inches(0.75),
                Inches(5.5), Inches(6)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = RgbColor(229, 231, 235)

    def _build_quote_slide(self, slide, content: Dict[str, Any]) -> None:
        """Build a quote slide"""
        quote = content.get('body', content.get('quote', ''))
        attribution = content.get('attribution', content.get('title', ''))

        # Large quote marks
        accent_color = self.get_color("accent")

        # Quote text
        quote_box = slide.shapes.add_textbox(
            Inches(1.5), Inches(2),
            Inches(10.333), Inches(3)
        )
        quote_frame = quote_box.text_frame
        quote_frame.word_wrap = True
        quote_para = quote_frame.paragraphs[0]
        quote_para.text = f'"{quote}"'
        quote_para.font.size = Pt(32)
        quote_para.font.italic = True
        quote_para.font.color.rgb = RgbColor(*self.hex_to_rgb(self.get_color("text")))
        quote_para.alignment = PP_ALIGN.CENTER

        # Attribution
        if attribution:
            attr_box = slide.shapes.add_textbox(
                Inches(1.5), Inches(5.2),
                Inches(10.333), Inches(0.8)
            )
            attr_frame = attr_box.text_frame
            attr_para = attr_frame.paragraphs[0]
            attr_para.text = f"— {attribution}"
            attr_para.font.size = Pt(20)
            attr_para.font.color.rgb = RgbColor(*self.hex_to_rgb(accent_color))
            attr_para.alignment = PP_ALIGN.CENTER

    def _add_logo(self, slide) -> None:
        """Add brand logo to slide"""
        logo_path = self.brand.logo.primary_path
        if not logo_path or not os.path.exists(logo_path):
            return

        position = self.brand.logo.preferred_position
        logo_width = Inches(1.2)

        # Position mapping
        positions = {
            "top-left": (Inches(0.3), Inches(0.2)),
            "top-right": (Inches(11.833), Inches(0.2)),
            "bottom-left": (Inches(0.3), Inches(7)),
            "bottom-right": (Inches(11.833), Inches(7)),
            "top-center": (Inches(6), Inches(0.2)),
        }

        left, top = positions.get(position, positions["bottom-right"])

        try:
            slide.shapes.add_picture(logo_path, left, top, width=logo_width)
        except Exception:
            pass  # Skip if logo can't be added

    def save(self, output_path: str) -> str:
        """Save the presentation to a PPTX file."""
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        self.prs.save(output_path)
        return output_path

    def reset(self) -> None:
        """Reset the presentation for reuse."""
        self.prs = Presentation()
        self.prs.slide_width = self.SLIDE_WIDTH
        self.prs.slide_height = self.SLIDE_HEIGHT
        self.slides = []
