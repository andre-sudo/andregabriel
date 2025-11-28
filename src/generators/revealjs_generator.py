"""
Reveal.js Generator - Generates HTML presentations from brand profiles

Creates beautiful, responsive HTML presentations using reveal.js
that follow the learned brand patterns.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from brand.schemas import BrandSchema
from .base import BaseGenerator


class RevealJSGenerator(BaseGenerator):
    """
    Generates reveal.js HTML presentations with brand styling.

    This is the "action" component of the world model for HTML output,
    translating brand knowledge into web-based presentations.
    """

    REVEAL_CDN = "https://cdn.jsdelivr.net/npm/reveal.js@5.0.4"

    def __init__(self, brand: BrandSchema):
        super().__init__(brand)
        self.slides_html: List[str] = []

    def generate(self, content: List[Dict[str, Any]], output_path: str) -> str:
        """
        Generate a complete reveal.js presentation from content list.

        Args:
            content: List of slide content dictionaries
            output_path: Path to save the HTML file

        Returns:
            Path to the generated HTML file
        """
        self.slides_html = []

        for slide_content in content:
            layout_type = slide_content.get('layout', 'content')
            self.add_slide(layout_type, slide_content)

        return self.save(output_path)

    def add_slide(self, layout_type: str, content: Dict[str, Any]) -> None:
        """Add a slide with the specified layout and content."""

        if layout_type == "title_slide":
            html = self._build_title_slide(content)
        elif layout_type == "section_header":
            html = self._build_section_slide(content)
        elif layout_type == "two_column":
            html = self._build_two_column_slide(content)
        elif layout_type == "image_left":
            html = self._build_image_left_slide(content)
        elif layout_type == "image_right":
            html = self._build_image_right_slide(content)
        elif layout_type == "quote":
            html = self._build_quote_slide(content)
        elif layout_type == "code":
            html = self._build_code_slide(content)
        else:
            html = self._build_content_slide(content)

        self.slides_html.append(html)

    def _build_title_slide(self, content: Dict[str, Any]) -> str:
        """Build a title slide layout"""
        title = self._escape_html(content.get('title', ''))
        subtitle = self._escape_html(content.get('subtitle', ''))

        return f'''<section class="title-slide">
    <h1>{title}</h1>
    {f'<p class="subtitle">{subtitle}</p>' if subtitle else ''}
</section>'''

    def _build_content_slide(self, content: Dict[str, Any]) -> str:
        """Build a standard content slide"""
        title = self._escape_html(content.get('title', ''))
        body = content.get('body', '')
        bullets = content.get('bullets', [])

        body_html = ''
        if bullets:
            items = '\n'.join(f'        <li>{self._escape_html(b)}</li>' for b in bullets)
            body_html = f'''<ul>
{items}
    </ul>'''
        elif body:
            body_html = f'<p>{self._escape_html(body)}</p>'

        return f'''<section>
    <h2>{title}</h2>
    {body_html}
</section>'''

    def _build_section_slide(self, content: Dict[str, Any]) -> str:
        """Build a section header slide"""
        title = self._escape_html(content.get('title', ''))

        return f'''<section class="section-header" data-background-color="{self.get_color('accent')}">
    <h2 style="color: white;">{title}</h2>
</section>'''

    def _build_two_column_slide(self, content: Dict[str, Any]) -> str:
        """Build a two-column slide"""
        title = self._escape_html(content.get('title', ''))
        left = content.get('left', content.get('body', ''))
        right = content.get('right', '')

        left_html = self._format_content(left)
        right_html = self._format_content(right)

        return f'''<section>
    <h2>{title}</h2>
    <div class="two-columns">
        <div class="column">{left_html}</div>
        <div class="column">{right_html}</div>
    </div>
</section>'''

    def _build_image_left_slide(self, content: Dict[str, Any]) -> str:
        """Build slide with image on left"""
        title = self._escape_html(content.get('title', ''))
        body = self._escape_html(content.get('body', ''))
        image = content.get('image', '')

        image_html = f'<img src="{image}" alt="" />' if image else '<div class="image-placeholder"></div>'

        return f'''<section>
    <div class="image-text-layout">
        <div class="image-side">{image_html}</div>
        <div class="text-side">
            <h2>{title}</h2>
            <p>{body}</p>
        </div>
    </div>
</section>'''

    def _build_image_right_slide(self, content: Dict[str, Any]) -> str:
        """Build slide with image on right"""
        title = self._escape_html(content.get('title', ''))
        body = self._escape_html(content.get('body', ''))
        image = content.get('image', '')

        image_html = f'<img src="{image}" alt="" />' if image else '<div class="image-placeholder"></div>'

        return f'''<section>
    <div class="image-text-layout reverse">
        <div class="text-side">
            <h2>{title}</h2>
            <p>{body}</p>
        </div>
        <div class="image-side">{image_html}</div>
    </div>
</section>'''

    def _build_quote_slide(self, content: Dict[str, Any]) -> str:
        """Build a quote slide"""
        quote = self._escape_html(content.get('body', content.get('quote', '')))
        attribution = self._escape_html(content.get('attribution', content.get('title', '')))

        return f'''<section class="quote-slide">
    <blockquote>
        <p>"{quote}"</p>
        {f'<cite>— {attribution}</cite>' if attribution else ''}
    </blockquote>
</section>'''

    def _build_code_slide(self, content: Dict[str, Any]) -> str:
        """Build a code slide with syntax highlighting"""
        title = self._escape_html(content.get('title', ''))
        code = content.get('code', content.get('body', ''))
        language = content.get('language', 'javascript')

        return f'''<section>
    <h2>{title}</h2>
    <pre><code class="language-{language}" data-trim data-noescape>
{code}
    </code></pre>
</section>'''

    def _format_content(self, content: Any) -> str:
        """Format content as HTML (handle strings, lists, etc.)"""
        if isinstance(content, list):
            items = '\n'.join(f'<li>{self._escape_html(item)}</li>' for item in content)
            return f'<ul>{items}</ul>'
        elif isinstance(content, str):
            return f'<p>{self._escape_html(content)}</p>'
        return ''

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not isinstance(text, str):
            text = str(text)
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def _generate_css(self) -> str:
        """Generate brand-specific CSS"""
        primary = self.get_color("primary")
        secondary = self.get_color("secondary")
        accent = self.get_color("accent")
        background = self.get_color("background")
        text = self.get_color("text")

        heading_font = self.get_font("heading")
        body_font = self.get_font("body")

        spacing_unit = self.brand.spacing.unit

        return f'''
:root {{
    --color-primary: {primary};
    --color-secondary: {secondary};
    --color-accent: {accent};
    --color-background: {background};
    --color-text: {text};
    --font-heading: '{heading_font["family"]}', sans-serif;
    --font-body: '{body_font["family"]}', sans-serif;
    --spacing-unit: {spacing_unit}px;
}}

.reveal {{
    font-family: var(--font-body);
    font-size: {body_font["size"]}px;
    color: var(--color-text);
}}

.reveal h1, .reveal h2, .reveal h3 {{
    font-family: var(--font-heading);
    color: var(--color-primary);
    font-weight: {heading_font["weight"]};
    text-transform: none;
    letter-spacing: -0.02em;
}}

.reveal h1 {{
    font-size: 2.5em;
    margin-bottom: 0.5em;
}}

.reveal h2 {{
    font-size: 1.8em;
    margin-bottom: 0.5em;
}}

.reveal .subtitle {{
    font-size: 1.2em;
    color: var(--color-secondary);
    margin-top: 0.5em;
}}

.reveal section {{
    padding: calc(var(--spacing-unit) * 4);
}}

/* Title slide */
.reveal .title-slide {{
    text-align: center;
}}

.reveal .title-slide h1 {{
    font-size: 3em;
}}

/* Section header */
.reveal .section-header h2 {{
    color: white;
    font-size: 2.5em;
}}

/* Two columns */
.reveal .two-columns {{
    display: flex;
    gap: calc(var(--spacing-unit) * 4);
    text-align: left;
}}

.reveal .two-columns .column {{
    flex: 1;
}}

/* Image + text layout */
.reveal .image-text-layout {{
    display: flex;
    gap: calc(var(--spacing-unit) * 4);
    align-items: center;
    text-align: left;
}}

.reveal .image-text-layout.reverse {{
    flex-direction: row-reverse;
}}

.reveal .image-text-layout .image-side {{
    flex: 1;
}}

.reveal .image-text-layout .text-side {{
    flex: 1;
}}

.reveal .image-text-layout img {{
    max-width: 100%;
    border-radius: 8px;
}}

.reveal .image-placeholder {{
    background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
    width: 100%;
    padding-bottom: 75%;
    border-radius: 8px;
}}

/* Quote slide */
.reveal .quote-slide {{
    text-align: center;
}}

.reveal .quote-slide blockquote {{
    background: none;
    border: none;
    box-shadow: none;
    font-style: italic;
    font-size: 1.5em;
    max-width: 80%;
    margin: 0 auto;
}}

.reveal .quote-slide cite {{
    display: block;
    margin-top: 1em;
    font-size: 0.7em;
    color: var(--color-accent);
    font-style: normal;
}}

/* Lists */
.reveal ul, .reveal ol {{
    text-align: left;
    margin-left: 1em;
}}

.reveal li {{
    margin-bottom: 0.5em;
    line-height: 1.4;
}}

/* Links */
.reveal a {{
    color: var(--color-accent);
}}

/* Code blocks */
.reveal pre {{
    font-size: 0.7em;
    box-shadow: none;
}}

.reveal code {{
    background: #1e1e1e;
    padding: 1em;
    border-radius: 8px;
}}
'''

    def _generate_html(self) -> str:
        """Generate the complete HTML document"""
        slides_content = '\n\n'.join(self.slides_html)
        custom_css = self._generate_css()
        brand_name = self.brand.name

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} Presentation</title>
    <link rel="stylesheet" href="{self.REVEAL_CDN}/dist/reset.css">
    <link rel="stylesheet" href="{self.REVEAL_CDN}/dist/reveal.css">
    <link rel="stylesheet" href="{self.REVEAL_CDN}/dist/theme/white.css">
    <link rel="stylesheet" href="{self.REVEAL_CDN}/plugin/highlight/monokai.css">
    <style>
{custom_css}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
{slides_content}
        </div>
    </div>

    <script src="{self.REVEAL_CDN}/dist/reveal.js"></script>
    <script src="{self.REVEAL_CDN}/plugin/notes/notes.js"></script>
    <script src="{self.REVEAL_CDN}/plugin/highlight/highlight.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            slideNumber: true,
            transition: 'slide',
            plugins: [ RevealNotes, RevealHighlight ]
        }});
    </script>
</body>
</html>'''

    def save(self, output_path: str) -> str:
        """Save the presentation to an HTML file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        html_content = self._generate_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def to_json(self) -> Dict[str, Any]:
        """Export presentation structure as JSON for API responses"""
        return {
            "brand": self.brand.name,
            "slide_count": len(self.slides_html),
            "css_variables": {
                "primary": self.get_color("primary"),
                "secondary": self.get_color("secondary"),
                "accent": self.get_color("accent"),
                "background": self.get_color("background"),
                "text": self.get_color("text")
            },
            "fonts": {
                "heading": self.get_font("heading"),
                "body": self.get_font("body")
            }
        }

    def reset(self) -> None:
        """Reset the generator for reuse."""
        self.slides_html = []
