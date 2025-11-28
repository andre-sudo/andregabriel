#!/usr/bin/env python3
"""
Brand World Model - CLI Interface

This script provides the command-line interface for analyzing slides
and generating presentations. It's called by the Express server.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from brand.schemas import (
    BrandSchema, ColorSchema, ColorRole, FontSchema, FontWeight,
    TypographySchema, SpacingSchema, LogoSchema, SlideSchema,
    LayoutType, SlideElementSchema, ElementPositionSchema
)
from brand.knowledge_base import BrandKnowledgeBase


def analyze_slides(data: dict) -> dict:
    """
    Analyze slide images and create a brand profile.

    Args:
        data: Dictionary containing:
            - slides: List of slide image paths
            - brand_name: Name for the brand profile
            - output_dir: Directory to save the brand profile

    Returns:
        Analysis results and brand profile
    """
    slides = data.get('slides', [])
    brand_name = data.get('brand_name', 'Extracted Brand')
    output_dir = data.get('output_dir', './data/brands')

    if not slides:
        return {"error": "No slides provided"}

    # For now, create a default brand profile
    # In production, this would use the SlideAnalyzer with vision AI
    brand_id = brand_name.lower().replace(' ', '-').replace('_', '-')
    brand_id = ''.join(c for c in brand_id if c.isalnum() or c == '-')

    # Try to analyze colors from images if PIL is available
    colors = []
    try:
        from analyzers.color_analyzer import ColorAnalyzer
        analyzer = ColorAnalyzer()

        all_colors = []
        for slide_path in slides[:5]:  # Analyze first 5 slides
            if os.path.exists(slide_path):
                palette = analyzer.extract_palette(slide_path, num_colors=4)
                all_colors.extend(palette)

        # Get most frequent colors by role
        role_colors = {}
        for color in all_colors:
            role = color.role or 'secondary'
            if role not in role_colors:
                role_colors[role] = []
            role_colors[role].append(color.hex)

        # Build color list
        for role, hex_list in role_colors.items():
            if hex_list:
                # Most frequent
                counts = {}
                for h in hex_list:
                    counts[h] = counts.get(h, 0) + 1
                best_hex = max(counts.items(), key=lambda x: x[1])[0]
                colors.append({
                    "hex": best_hex,
                    "role": role
                })
    except Exception as e:
        # Fallback to default colors
        colors = [
            {"hex": "#1E40AF", "role": "primary"},
            {"hex": "#6B7280", "role": "secondary"},
            {"hex": "#F59E0B", "role": "accent"},
            {"hex": "#FFFFFF", "role": "background"},
            {"hex": "#1F2937", "role": "text"}
        ]

    # Ensure we have all required colors
    required_roles = ["primary", "secondary", "accent", "background", "text"]
    existing_roles = [c["role"] for c in colors]

    defaults = {
        "primary": "#1E40AF",
        "secondary": "#6B7280",
        "accent": "#F59E0B",
        "background": "#FFFFFF",
        "text": "#1F2937"
    }

    for role in required_roles:
        if role not in existing_roles:
            colors.append({"hex": defaults[role], "role": role})

    # Create brand schema
    brand_data = {
        "id": brand_id,
        "name": brand_name,
        "description": f"Brand profile extracted from {len(slides)} slides",
        "colors": [
            ColorSchema(hex=c["hex"], role=ColorRole(c["role"]))
            for c in colors
        ],
        "typography": TypographySchema(
            heading=FontSchema(
                family="Inter",
                fallback=["Arial", "sans-serif"],
                weight=FontWeight.BOLD,
                size_base=36,
                line_height=1.2
            ),
            body=FontSchema(
                family="Inter",
                fallback=["Arial", "sans-serif"],
                weight=FontWeight.NORMAL,
                size_base=18,
                line_height=1.5
            )
        ),
        "logo": LogoSchema(
            preferred_position="bottom-right",
            min_width=80,
            clear_space=16
        ),
        "spacing": SpacingSchema(
            unit=8,
            margin_x=4,
            margin_y=3,
            element_gap=2,
            section_gap=4
        ),
        "layout_patterns": [
            SlideSchema(
                layout_type=LayoutType.TITLE,
                elements=[
                    SlideElementSchema(
                        type="title",
                        position=ElementPositionSchema(x=10, y=35, width=80, height=20),
                        style={"font_size": "xlarge", "alignment": "center"}
                    ),
                    SlideElementSchema(
                        type="subtitle",
                        position=ElementPositionSchema(x=10, y=55, width=80, height=10),
                        style={"font_size": "medium", "alignment": "center"}
                    )
                ]
            ),
            SlideSchema(
                layout_type=LayoutType.CONTENT,
                elements=[
                    SlideElementSchema(
                        type="title",
                        position=ElementPositionSchema(x=5, y=5, width=90, height=15),
                        style={"font_size": "large", "alignment": "left"}
                    ),
                    SlideElementSchema(
                        type="body",
                        position=ElementPositionSchema(x=5, y=22, width=90, height=73),
                        style={"font_size": "medium", "alignment": "left"}
                    )
                ]
            )
        ],
        "style_attributes": {
            "visual_style": "corporate",
            "density": "balanced"
        },
        "source_files": slides,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "confidence_score": 0.75
    }

    brand = BrandSchema(**brand_data)

    # Save to knowledge base
    kb = BrandKnowledgeBase(output_dir)
    kb.save_brand(brand)

    return {
        "success": True,
        "brand_id": brand_id,
        "brand_name": brand_name,
        "colors_extracted": len(colors),
        "slides_analyzed": len(slides),
        "confidence": 0.75
    }


def generate_presentation(data: dict) -> dict:
    """
    Generate a presentation from brand profile and content.

    Args:
        data: Dictionary containing:
            - brand: Brand profile data
            - content: List of slide content
            - format: Output format (pptx, html, both)
            - output_dir: Output directory
            - output_id: Filename without extension

    Returns:
        Generation results
    """
    brand_data = data.get('brand', {})
    content = data.get('content', [])
    output_format = data.get('format', 'both')
    output_dir = data.get('output_dir', './output')
    output_id = data.get('output_id', str(uuid.uuid4()))

    if not content:
        return {"error": "No content provided"}

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results = {"success": True, "files": []}

    # Convert brand data to BrandSchema
    try:
        # Handle colors
        colors = []
        for c in brand_data.get('colors', []):
            colors.append(ColorSchema(
                hex=c.get('hex', '#000000'),
                role=ColorRole(c.get('role', 'secondary'))
            ))

        if not colors:
            colors = [
                ColorSchema(hex="#1E40AF", role=ColorRole.PRIMARY),
                ColorSchema(hex="#6B7280", role=ColorRole.SECONDARY),
                ColorSchema(hex="#F59E0B", role=ColorRole.ACCENT),
                ColorSchema(hex="#FFFFFF", role=ColorRole.BACKGROUND),
                ColorSchema(hex="#1F2937", role=ColorRole.TEXT)
            ]

        # Handle typography
        typography_data = brand_data.get('typography', {})
        heading_data = typography_data.get('heading', {})
        body_data = typography_data.get('body', {})

        typography = TypographySchema(
            heading=FontSchema(
                family=heading_data.get('family', 'Inter'),
                fallback=heading_data.get('fallback', ['Arial', 'sans-serif']),
                weight=FontWeight(heading_data.get('weight', 'bold')),
                size_base=heading_data.get('size_base', 36),
                line_height=heading_data.get('line_height', 1.2)
            ),
            body=FontSchema(
                family=body_data.get('family', 'Inter'),
                fallback=body_data.get('fallback', ['Arial', 'sans-serif']),
                weight=FontWeight(body_data.get('weight', 'normal')),
                size_base=body_data.get('size_base', 18),
                line_height=body_data.get('line_height', 1.5)
            )
        )

        # Handle spacing
        spacing_data = brand_data.get('spacing', {})
        spacing = SpacingSchema(
            unit=spacing_data.get('unit', 8),
            margin_x=spacing_data.get('margin_x', 4),
            margin_y=spacing_data.get('margin_y', 3),
            element_gap=spacing_data.get('element_gap', 2),
            section_gap=spacing_data.get('section_gap', 4)
        )

        # Handle logo
        logo_data = brand_data.get('logo', {})
        logo = LogoSchema(
            primary_path=logo_data.get('primary_path'),
            preferred_position=logo_data.get('preferred_position', 'bottom-right'),
            min_width=logo_data.get('min_width', 80),
            clear_space=logo_data.get('clear_space', 16)
        )

        brand = BrandSchema(
            id=brand_data.get('id', 'generated-brand'),
            name=brand_data.get('name', 'Generated Brand'),
            colors=colors,
            typography=typography,
            logo=logo,
            spacing=spacing,
            layout_patterns=[],
            style_attributes=brand_data.get('style_attributes', {}),
            source_files=[],
            confidence_score=brand_data.get('confidence_score', 0.8)
        )

    except Exception as e:
        return {"error": f"Invalid brand data: {str(e)}"}

    # Generate PowerPoint
    if output_format in ['pptx', 'both']:
        try:
            from generators.pptx_generator import PowerPointGenerator

            pptx_gen = PowerPointGenerator(brand)
            pptx_path = os.path.join(output_dir, f"{output_id}.pptx")
            pptx_gen.generate(content, pptx_path)
            results["files"].append({"format": "pptx", "path": pptx_path})
        except ImportError:
            results["pptx_error"] = "python-pptx not installed"
        except Exception as e:
            results["pptx_error"] = str(e)

    # Generate reveal.js HTML
    if output_format in ['html', 'both']:
        try:
            from generators.revealjs_generator import RevealJSGenerator

            html_gen = RevealJSGenerator(brand)
            html_path = os.path.join(output_dir, f"{output_id}.html")
            html_gen.generate(content, html_path)
            results["files"].append({"format": "html", "path": html_path})
        except Exception as e:
            results["html_error"] = str(e)

    return results


def main():
    """Main entry point for CLI"""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: cli.py <action> <json_data>"}))
        sys.exit(1)

    action = sys.argv[1]
    try:
        data = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    if action == 'analyze':
        result = analyze_slides(data)
    elif action == 'generate':
        result = generate_presentation(data)
    else:
        result = {"error": f"Unknown action: {action}"}

    print(json.dumps(result))


if __name__ == '__main__':
    main()
