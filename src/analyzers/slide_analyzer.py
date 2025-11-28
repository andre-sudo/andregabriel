"""
Slide Analyzer - Uses Vision AI to extract design patterns from slide images

This is the core "world model" component that learns to understand
slide layouts, design patterns, and visual hierarchy.
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from PIL import Image

from .color_analyzer import ColorAnalyzer, ColorInfo


@dataclass
class LayoutElement:
    """Represents a detected element in a slide layout"""
    type: str  # title, subtitle, body, image, chart, logo, footer, etc.
    position: Dict[str, float]  # x, y, width, height as percentages
    style: Dict[str, Any]  # font_size, alignment, etc.
    confidence: float


@dataclass
class SlideAnalysis:
    """Complete analysis of a slide image"""
    layout_type: str  # title_slide, content, two_column, image_heavy, etc.
    elements: List[LayoutElement]
    colors: List[Dict]
    typography: Dict[str, Any]
    spacing: Dict[str, Any]
    visual_hierarchy: List[str]
    raw_description: str
    confidence: float


class SlideAnalyzer:
    """
    Analyzes slide images using Vision AI to extract design patterns.

    This forms the "perception" component of the Brand World Model,
    converting visual input into structured design knowledge.
    """

    ANALYSIS_PROMPT = """Analyze this presentation slide image and extract detailed design information.

Return a JSON object with the following structure:
{
    "layout_type": "title_slide|content|two_column|image_left|image_right|full_image|comparison|quote|data_heavy",
    "elements": [
        {
            "type": "title|subtitle|body|bullet_list|image|chart|logo|icon|footer|header|shape|divider",
            "position": {
                "x": 0-100 (percentage from left),
                "y": 0-100 (percentage from top),
                "width": 0-100 (percentage of slide width),
                "height": 0-100 (percentage of slide height)
            },
            "style": {
                "font_size": "large|medium|small|xlarge",
                "font_weight": "bold|normal|light",
                "alignment": "left|center|right",
                "color_role": "primary|secondary|accent|text|background"
            },
            "content_summary": "brief description of the content"
        }
    ],
    "typography": {
        "heading_style": "sans-serif|serif|display|monospace",
        "body_style": "sans-serif|serif|monospace",
        "hierarchy_levels": 1-4,
        "estimated_fonts": ["font name guesses"]
    },
    "spacing": {
        "margins": "tight|normal|generous",
        "element_spacing": "compact|balanced|airy",
        "grid_columns": 1-4
    },
    "visual_hierarchy": ["ordered list of elements by visual prominence"],
    "design_notes": "any notable design patterns, techniques, or brand elements observed",
    "overall_style": "minimal|corporate|creative|playful|elegant|technical|bold"
}

Be precise with position estimates. Analyze the visual weight and hierarchy carefully."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "anthropic"):
        """
        Initialize the analyzer with an AI provider.

        Args:
            api_key: API key for the vision model
            provider: "anthropic" or "openai"
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.provider = provider
        self.color_analyzer = ColorAnalyzer()

        if not self.api_key:
            raise ValueError("API key required. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")

    def analyze_slide(self, image_path: str) -> SlideAnalysis:
        """
        Analyze a single slide image and extract design patterns.

        Args:
            image_path: Path to the slide image

        Returns:
            SlideAnalysis object with extracted design information
        """
        # Validate image
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Extract colors using local analysis
        color_palette = self.color_analyzer.extract_palette(image_path)
        color_data = self.color_analyzer.to_dict(color_palette)

        # Get vision AI analysis
        vision_result = self._call_vision_api(image_path)

        # Parse and combine results
        try:
            parsed = json.loads(vision_result)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            parsed = self._extract_json(vision_result)

        # Build SlideAnalysis object
        elements = [
            LayoutElement(
                type=el.get('type', 'unknown'),
                position=el.get('position', {}),
                style=el.get('style', {}),
                confidence=0.8
            )
            for el in parsed.get('elements', [])
        ]

        return SlideAnalysis(
            layout_type=parsed.get('layout_type', 'unknown'),
            elements=elements,
            colors=color_data['colors'],
            typography=parsed.get('typography', {}),
            spacing=parsed.get('spacing', {}),
            visual_hierarchy=parsed.get('visual_hierarchy', []),
            raw_description=parsed.get('design_notes', ''),
            confidence=0.85
        )

    def analyze_multiple(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple slides and synthesize common patterns.

        Args:
            image_paths: List of paths to slide images

        Returns:
            Synthesized design patterns across all slides
        """
        analyses = []
        for path in image_paths:
            try:
                analysis = self.analyze_slide(path)
                analyses.append(analysis)
            except Exception as e:
                print(f"Warning: Failed to analyze {path}: {e}")

        if not analyses:
            raise ValueError("No slides could be analyzed")

        # Synthesize common patterns
        return self._synthesize_patterns(analyses)

    def _call_vision_api(self, image_path: str) -> str:
        """Call the vision API to analyze the image"""
        # Encode image to base64
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Detect image type
        img = Image.open(image_path)
        media_type = f"image/{img.format.lower()}" if img.format else "image/png"

        if self.provider == "anthropic":
            return self._call_anthropic(image_data, media_type)
        else:
            return self._call_openai(image_data, media_type)

    def _call_anthropic(self, image_data: str, media_type: str) -> str:
        """Call Anthropic's Claude Vision API"""
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": self.ANALYSIS_PROMPT
                        }
                    ]
                }
            ]
        )

        return message.content[0].text

    def _call_openai(self, image_data: str, media_type: str) -> str:
        """Call OpenAI's GPT-4 Vision API"""
        import openai

        client = openai.OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": self.ANALYSIS_PROMPT
                        }
                    ]
                }
            ],
            max_tokens=2048
        )

        return response.choices[0].message.content

    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from a text response that might have extra content"""
        import re

        # Try to find JSON block
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Return empty structure if parsing fails
        return {
            "layout_type": "unknown",
            "elements": [],
            "typography": {},
            "spacing": {},
            "visual_hierarchy": [],
            "design_notes": text
        }

    def _synthesize_patterns(self, analyses: List[SlideAnalysis]) -> Dict[str, Any]:
        """Synthesize common patterns from multiple slide analyses"""
        # Aggregate layout types
        layout_counts = {}
        for a in analyses:
            layout_counts[a.layout_type] = layout_counts.get(a.layout_type, 0) + 1

        # Aggregate colors
        all_colors = []
        for a in analyses:
            all_colors.extend(a.colors)

        # Find most common colors
        color_counts = {}
        for c in all_colors:
            hex_val = c.get('hex', '')
            if hex_val:
                color_counts[hex_val] = color_counts.get(hex_val, 0) + 1

        common_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:6]

        # Aggregate typography
        typography_styles = []
        for a in analyses:
            if a.typography:
                typography_styles.append(a.typography)

        return {
            "slide_count": len(analyses),
            "layout_distribution": layout_counts,
            "common_colors": [{"hex": c[0], "frequency": c[1]} for c in common_colors],
            "typography_patterns": typography_styles[:3] if typography_styles else [],
            "element_patterns": self._extract_element_patterns(analyses),
            "confidence": sum(a.confidence for a in analyses) / len(analyses)
        }

    def _extract_element_patterns(self, analyses: List[SlideAnalysis]) -> Dict:
        """Extract common element positioning patterns"""
        element_positions = {}

        for analysis in analyses:
            for element in analysis.elements:
                el_type = element.type
                if el_type not in element_positions:
                    element_positions[el_type] = []
                element_positions[el_type].append(element.position)

        # Average positions for each element type
        averaged = {}
        for el_type, positions in element_positions.items():
            if positions:
                averaged[el_type] = {
                    "avg_x": sum(p.get('x', 0) for p in positions) / len(positions),
                    "avg_y": sum(p.get('y', 0) for p in positions) / len(positions),
                    "avg_width": sum(p.get('width', 0) for p in positions) / len(positions),
                    "avg_height": sum(p.get('height', 0) for p in positions) / len(positions),
                    "occurrences": len(positions)
                }

        return averaged

    def to_dict(self, analysis: SlideAnalysis) -> Dict:
        """Convert SlideAnalysis to dictionary for JSON serialization"""
        return {
            "layout_type": analysis.layout_type,
            "elements": [asdict(el) for el in analysis.elements],
            "colors": analysis.colors,
            "typography": analysis.typography,
            "spacing": analysis.spacing,
            "visual_hierarchy": analysis.visual_hierarchy,
            "raw_description": analysis.raw_description,
            "confidence": analysis.confidence
        }
