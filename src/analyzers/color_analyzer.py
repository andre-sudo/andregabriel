"""
Color Analyzer - Extracts and analyzes color palettes from images
"""

import io
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from PIL import Image
import colorsys


@dataclass
class ColorInfo:
    """Represents a color with its properties"""
    hex: str
    rgb: Tuple[int, int, int]
    hsl: Tuple[float, float, float]
    name: Optional[str] = None
    frequency: float = 0.0
    role: Optional[str] = None  # primary, secondary, accent, background, text


class ColorAnalyzer:
    """Analyzes images to extract color palettes and relationships"""

    # Common color name mappings
    COLOR_NAMES = {
        '#FFFFFF': 'white',
        '#000000': 'black',
        '#FF0000': 'red',
        '#00FF00': 'green',
        '#0000FF': 'blue',
        '#FFFF00': 'yellow',
        '#FF00FF': 'magenta',
        '#00FFFF': 'cyan',
    }

    def __init__(self):
        self.palette_cache = {}

    def extract_palette(self, image_path: str, num_colors: int = 6) -> List[ColorInfo]:
        """
        Extract dominant colors from an image using color quantization
        """
        img = Image.open(image_path)
        img = img.convert('RGB')

        # Resize for faster processing
        img.thumbnail((200, 200))

        # Get all pixels
        pixels = list(img.getdata())

        # Simple color quantization using binning
        color_counts = {}
        for pixel in pixels:
            # Quantize to reduce color space
            quantized = self._quantize_color(pixel)
            color_counts[quantized] = color_counts.get(quantized, 0) + 1

        # Sort by frequency
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

        # Get top colors
        total_pixels = len(pixels)
        palette = []

        for rgb, count in sorted_colors[:num_colors]:
            hex_color = self._rgb_to_hex(rgb)
            hsl = self._rgb_to_hsl(rgb)

            color_info = ColorInfo(
                hex=hex_color,
                rgb=rgb,
                hsl=hsl,
                frequency=count / total_pixels,
                name=self._get_color_name(hex_color)
            )
            palette.append(color_info)

        # Assign roles based on analysis
        self._assign_color_roles(palette)

        return palette

    def _quantize_color(self, rgb: Tuple[int, int, int], levels: int = 32) -> Tuple[int, int, int]:
        """Reduce color precision for grouping similar colors"""
        factor = 256 // levels
        return (
            (rgb[0] // factor) * factor,
            (rgb[1] // factor) * factor,
            (rgb[2] // factor) * factor
        )

    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    def _rgb_to_hsl(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSL"""
        r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)

    def _get_color_name(self, hex_color: str) -> Optional[str]:
        """Get a descriptive name for a color"""
        # Check exact matches first
        if hex_color.upper() in self.COLOR_NAMES:
            return self.COLOR_NAMES[hex_color.upper()]

        # Analyze HSL for descriptive name
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        h, s, l = self._rgb_to_hsl(rgb)

        # Determine lightness descriptor
        if l < 20:
            lightness = "dark"
        elif l > 80:
            lightness = "light"
        else:
            lightness = ""

        # Determine hue name
        if s < 10:
            if l < 20:
                return "black"
            elif l > 80:
                return "white"
            else:
                return "gray"

        hue_names = [
            (15, "red"),
            (45, "orange"),
            (75, "yellow"),
            (150, "green"),
            (210, "cyan"),
            (270, "blue"),
            (330, "purple"),
            (360, "red"),
        ]

        hue_name = "red"
        for threshold, name in hue_names:
            if h < threshold:
                hue_name = name
                break

        return f"{lightness} {hue_name}".strip()

    def _assign_color_roles(self, palette: List[ColorInfo]) -> None:
        """Assign semantic roles to colors based on their properties"""
        if not palette:
            return

        for color in palette:
            h, s, l = color.hsl

            # Background colors are usually very light or very dark
            if l > 90 or l < 10:
                if color.role is None:
                    color.role = 'background'
            # Text colors are usually very dark or very light with low saturation
            elif (l < 25 or l > 85) and s < 20:
                if color.role is None:
                    color.role = 'text'
            # High saturation colors with medium lightness are accents
            elif s > 50 and 30 < l < 70:
                if color.role is None:
                    color.role = 'accent'

        # Assign primary to the most frequent non-background color
        for color in palette:
            if color.role is None:
                color.role = 'primary'
                break

        # Assign secondary to remaining
        for color in palette:
            if color.role is None:
                color.role = 'secondary'

    def analyze_contrast(self, color1: ColorInfo, color2: ColorInfo) -> float:
        """Calculate contrast ratio between two colors (WCAG)"""
        def get_luminance(rgb):
            def channel(c):
                c = c / 255
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            r, g, b = rgb
            return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

        l1 = get_luminance(color1.rgb)
        l2 = get_luminance(color2.rgb)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def to_dict(self, palette: List[ColorInfo]) -> Dict:
        """Convert palette to dictionary for JSON serialization"""
        return {
            'colors': [
                {
                    'hex': c.hex,
                    'rgb': list(c.rgb),
                    'hsl': list(c.hsl),
                    'name': c.name,
                    'frequency': round(c.frequency, 4),
                    'role': c.role
                }
                for c in palette
            ]
        }
