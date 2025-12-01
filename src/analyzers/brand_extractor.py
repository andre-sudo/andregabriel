"""
Brand Extractor - Analyzes brand materials to build a comprehensive brand profile

This component processes logos, style guides, and existing materials
to extract the "brand DNA" that can be applied to new templates.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from PIL import Image

from .color_analyzer import ColorAnalyzer
from .slide_analyzer import SlideAnalyzer


@dataclass
class BrandProfile:
    """Complete brand identity profile extracted from materials"""
    name: str
    colors: Dict[str, Any]  # primary, secondary, accent, etc.
    typography: Dict[str, Any]  # fonts, sizes, weights
    logo: Dict[str, Any]  # logo info and placement rules
    layouts: List[Dict[str, Any]]  # common layout patterns
    style: Dict[str, Any]  # overall style attributes
    spacing: Dict[str, Any]  # margin and padding patterns
    rules: List[str] = field(default_factory=list)  # extracted brand rules


class BrandExtractor:
    """
    Extracts comprehensive brand identity from various materials.

    This is the "memory" component of the Brand World Model,
    storing learned brand patterns for template generation.
    """

    BRAND_ANALYSIS_PROMPT = """Analyze these brand materials and extract a comprehensive brand guide.

Focus on identifying:
1. Primary, secondary, and accent colors
2. Typography choices and hierarchy
3. Logo usage patterns and safe zones
4. Overall visual style and mood
5. Common design patterns and motifs
6. Spacing and layout preferences

Return a JSON object with:
{
    "brand_personality": ["list of personality traits"],
    "visual_style": "minimal|corporate|creative|playful|elegant|bold|technical",
    "color_usage": {
        "primary_use": "how primary color is typically used",
        "accent_use": "how accent colors are used",
        "background_preference": "light|dark|varied"
    },
    "typography_rules": {
        "heading_treatment": "description of heading style",
        "body_treatment": "description of body text style",
        "emphasis_method": "bold|italic|color|underline"
    },
    "logo_rules": {
        "preferred_placement": "top-left|top-center|bottom-right|etc",
        "minimum_size": "small|medium|large",
        "clear_space": "tight|normal|generous"
    },
    "layout_preferences": {
        "alignment": "left|center|mixed",
        "density": "sparse|balanced|dense",
        "whitespace": "minimal|moderate|generous"
    },
    "design_motifs": ["recurring design elements"],
    "restrictions": ["things to avoid"]
}"""

    def __init__(self, api_key: Optional[str] = None, provider: str = "anthropic"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.provider = provider
        self.color_analyzer = ColorAnalyzer()
        self.slide_analyzer = SlideAnalyzer(api_key, provider)

    def extract_from_slides(self, slide_paths: List[str]) -> BrandProfile:
        """
        Extract brand profile from existing presentation slides.

        Args:
            slide_paths: List of paths to slide images

        Returns:
            BrandProfile with extracted brand identity
        """
        if not slide_paths:
            raise ValueError("At least one slide image is required")

        # Analyze all slides
        analyses = []
        all_colors = []

        for path in slide_paths:
            try:
                # Get slide analysis
                analysis = self.slide_analyzer.analyze_slide(path)
                analyses.append(analysis)

                # Collect colors
                colors = self.color_analyzer.extract_palette(path)
                all_colors.extend(colors)
            except Exception as e:
                print(f"Warning: Failed to process {path}: {e}")

        if not analyses:
            raise ValueError("Could not analyze any slides")

        # Synthesize brand profile
        return self._build_profile_from_analyses(analyses, all_colors)

    def extract_from_assets(
        self,
        logo_path: Optional[str] = None,
        slide_paths: Optional[List[str]] = None,
        style_guide_path: Optional[str] = None,
        additional_assets: Optional[List[str]] = None
    ) -> BrandProfile:
        """
        Extract brand profile from multiple asset types.

        Args:
            logo_path: Path to logo image
            slide_paths: List of slide image paths
            style_guide_path: Path to style guide (PDF or image)
            additional_assets: Other brand materials

        Returns:
            Comprehensive BrandProfile
        """
        profile_data = {
            "name": "Extracted Brand",
            "colors": {},
            "typography": {},
            "logo": {},
            "layouts": [],
            "style": {},
            "spacing": {},
            "rules": []
        }

        # Process logo
        if logo_path and os.path.exists(logo_path):
            logo_colors = self.color_analyzer.extract_palette(logo_path, num_colors=4)
            profile_data["logo"] = {
                "path": logo_path,
                "colors": [c.hex for c in logo_colors],
                "dimensions": self._get_image_dimensions(logo_path)
            }
            # Logo colors often indicate primary brand colors
            for color in logo_colors:
                if color.role == 'primary' or color.frequency > 0.2:
                    if 'primary' not in profile_data["colors"]:
                        profile_data["colors"]["primary"] = color.hex

        # Process slides
        if slide_paths:
            slide_profile = self.extract_from_slides(slide_paths)
            profile_data["colors"].update(slide_profile.colors)
            profile_data["typography"] = slide_profile.typography
            profile_data["layouts"] = slide_profile.layouts
            profile_data["spacing"] = slide_profile.spacing
            profile_data["style"] = slide_profile.style

        # Process additional assets for color extraction
        if additional_assets:
            for asset_path in additional_assets:
                if os.path.exists(asset_path):
                    try:
                        colors = self.color_analyzer.extract_palette(asset_path, num_colors=3)
                        # Add any new accent colors
                        for color in colors:
                            if color.role == 'accent' and 'accent' not in profile_data["colors"]:
                                profile_data["colors"]["accent"] = color.hex
                    except Exception:
                        pass

        return BrandProfile(**profile_data)

    def _build_profile_from_analyses(
        self,
        analyses: List[Any],
        colors: List[Any]
    ) -> BrandProfile:
        """Build a BrandProfile from slide analyses and colors"""

        # Aggregate colors by role
        color_roles = {"primary": [], "secondary": [], "accent": [], "background": [], "text": []}
        for color in colors:
            role = color.role or "secondary"
            if role in color_roles:
                color_roles[role].append(color.hex)

        # Pick most common color for each role
        final_colors = {}
        for role, hex_list in color_roles.items():
            if hex_list:
                # Count occurrences
                counts = {}
                for h in hex_list:
                    counts[h] = counts.get(h, 0) + 1
                final_colors[role] = max(counts.items(), key=lambda x: x[1])[0]

        # Aggregate typography
        typography = {}
        for analysis in analyses:
            if analysis.typography:
                for key, value in analysis.typography.items():
                    if key not in typography:
                        typography[key] = value

        # Aggregate spacing
        spacing_values = {"margins": [], "element_spacing": [], "grid_columns": []}
        for analysis in analyses:
            if analysis.spacing:
                for key in spacing_values:
                    if key in analysis.spacing:
                        spacing_values[key].append(analysis.spacing[key])

        # Most common spacing values
        spacing = {}
        for key, values in spacing_values.items():
            if values:
                counts = {}
                for v in values:
                    counts[str(v)] = counts.get(str(v), 0) + 1
                spacing[key] = max(counts.items(), key=lambda x: x[1])[0]

        # Extract layout patterns
        layouts = []
        layout_counts = {}
        for analysis in analyses:
            lt = analysis.layout_type
            layout_counts[lt] = layout_counts.get(lt, 0) + 1

        for layout_type, count in sorted(layout_counts.items(), key=lambda x: x[1], reverse=True):
            layouts.append({
                "type": layout_type,
                "frequency": count / len(analyses),
                "example_elements": self._get_layout_elements(analyses, layout_type)
            })

        # Determine overall style
        style = {
            "visual_style": self._determine_visual_style(analyses),
            "density": spacing.get("element_spacing", "balanced"),
            "formality": "corporate" if typography.get("heading_style") == "sans-serif" else "traditional"
        }

        return BrandProfile(
            name="Extracted Brand",
            colors=final_colors,
            typography=typography,
            logo={},
            layouts=layouts[:5],  # Top 5 layout patterns
            style=style,
            spacing=spacing,
            rules=self._extract_rules(analyses)
        )

    def _get_image_dimensions(self, image_path: str) -> Dict[str, int]:
        """Get image dimensions"""
        img = Image.open(image_path)
        return {"width": img.width, "height": img.height}

    def _get_layout_elements(self, analyses: List[Any], layout_type: str) -> List[Dict]:
        """Get common elements for a layout type"""
        elements = []
        for analysis in analyses:
            if analysis.layout_type == layout_type:
                for el in analysis.elements[:5]:  # First 5 elements
                    elements.append({
                        "type": el.type,
                        "position": el.position
                    })
                break
        return elements

    def _determine_visual_style(self, analyses: List[Any]) -> str:
        """Determine the overall visual style from analyses"""
        style_hints = []
        for analysis in analyses:
            if analysis.raw_description:
                desc = analysis.raw_description.lower()
                if "minimal" in desc:
                    style_hints.append("minimal")
                elif "bold" in desc:
                    style_hints.append("bold")
                elif "elegant" in desc:
                    style_hints.append("elegant")
                elif "playful" in desc:
                    style_hints.append("playful")
                else:
                    style_hints.append("corporate")

        if style_hints:
            counts = {}
            for s in style_hints:
                counts[s] = counts.get(s, 0) + 1
            return max(counts.items(), key=lambda x: x[1])[0]
        return "corporate"

    def _extract_rules(self, analyses: List[Any]) -> List[str]:
        """Extract brand rules from analyses"""
        rules = []

        # Check for consistent patterns
        all_have_logo = all(
            any(el.type == "logo" for el in a.elements)
            for a in analyses
        )
        if all_have_logo:
            rules.append("Logo should be present on all slides")

        # Check for footer consistency
        all_have_footer = all(
            any(el.type == "footer" for el in a.elements)
            for a in analyses
        )
        if all_have_footer:
            rules.append("Include footer on all slides")

        return rules

    def save_profile(self, profile: BrandProfile, output_path: str) -> None:
        """Save brand profile to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(asdict(profile), f, indent=2)

    def load_profile(self, profile_path: str) -> BrandProfile:
        """Load brand profile from JSON file"""
        with open(profile_path, 'r') as f:
            data = json.load(f)
        return BrandProfile(**data)

    def to_dict(self, profile: BrandProfile) -> Dict:
        """Convert BrandProfile to dictionary"""
        return asdict(profile)
