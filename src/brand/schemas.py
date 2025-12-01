"""
Brand World Model - Data Schemas

Pydantic schemas for validating and structuring brand data.
These schemas define the "language" of the brand world model.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ColorRole(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    BACKGROUND = "background"
    TEXT = "text"
    MUTED = "muted"


class FontWeight(str, Enum):
    LIGHT = "light"
    NORMAL = "normal"
    MEDIUM = "medium"
    SEMIBOLD = "semibold"
    BOLD = "bold"


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class LayoutType(str, Enum):
    TITLE = "title_slide"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    IMAGE_LEFT = "image_left"
    IMAGE_RIGHT = "image_right"
    FULL_IMAGE = "full_image"
    COMPARISON = "comparison"
    QUOTE = "quote"
    DATA = "data_heavy"
    SECTION = "section_header"
    BLANK = "blank"


class ColorSchema(BaseModel):
    """Schema for a single color definition"""
    hex: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    role: ColorRole
    name: Optional[str] = None
    usage: Optional[str] = None  # Description of when to use


class FontSchema(BaseModel):
    """Schema for font definition"""
    family: str
    fallback: List[str] = ["Arial", "sans-serif"]
    weight: FontWeight = FontWeight.NORMAL
    size_base: int = 16  # Base size in points
    line_height: float = 1.5


class TypographySchema(BaseModel):
    """Schema for typography system"""
    heading: FontSchema
    body: FontSchema
    caption: Optional[FontSchema] = None
    scale_ratio: float = 1.25  # Size ratio between heading levels


class SpacingSchema(BaseModel):
    """Schema for spacing system"""
    unit: int = 8  # Base spacing unit in pixels
    margin_x: int = 4  # Horizontal margin in units
    margin_y: int = 3  # Vertical margin in units
    element_gap: int = 2  # Gap between elements in units
    section_gap: int = 4  # Gap between sections in units


class LogoSchema(BaseModel):
    """Schema for logo usage rules"""
    primary_path: Optional[str] = None
    inverted_path: Optional[str] = None
    icon_path: Optional[str] = None
    min_width: int = 100  # Minimum width in pixels
    clear_space: int = 20  # Clear space around logo in pixels
    preferred_position: str = "top-left"


class ElementPositionSchema(BaseModel):
    """Schema for element positioning"""
    x: float = Field(..., ge=0, le=100)  # Percentage from left
    y: float = Field(..., ge=0, le=100)  # Percentage from top
    width: float = Field(..., ge=0, le=100)  # Percentage of slide width
    height: float = Field(..., ge=0, le=100)  # Percentage of slide height


class SlideElementSchema(BaseModel):
    """Schema for a slide element"""
    type: str  # title, subtitle, body, image, chart, logo, etc.
    position: ElementPositionSchema
    style: Dict[str, Any] = {}
    content_placeholder: Optional[str] = None


class SlideSchema(BaseModel):
    """Schema for a slide template"""
    layout_type: LayoutType
    elements: List[SlideElementSchema]
    background_color: Optional[str] = None
    background_image: Optional[str] = None
    notes: Optional[str] = None


class TemplateSchema(BaseModel):
    """Schema for a complete presentation template"""
    name: str
    description: Optional[str] = None
    slides: List[SlideSchema]
    default_transitions: Optional[str] = None
    aspect_ratio: str = "16:9"


class BrandRuleSchema(BaseModel):
    """Schema for a brand rule/guideline"""
    category: str  # color, typography, logo, layout, etc.
    rule: str  # The actual rule text
    severity: str = "recommended"  # required, recommended, optional
    examples: List[str] = []


class BrandSchema(BaseModel):
    """
    Complete brand schema - the structured representation
    of everything the world model knows about a brand.
    """
    id: str
    name: str
    description: Optional[str] = None

    # Visual Identity
    colors: List[ColorSchema]
    typography: TypographySchema
    logo: LogoSchema
    spacing: SpacingSchema

    # Patterns
    layout_patterns: List[SlideSchema] = []
    style_attributes: Dict[str, Any] = {}

    # Rules & Guidelines
    rules: List[BrandRuleSchema] = []

    # Metadata
    source_files: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    confidence_score: float = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "id": "acme-corp",
                "name": "Acme Corporation",
                "colors": [
                    {"hex": "#1E40AF", "role": "primary", "name": "Acme Blue"},
                    {"hex": "#F59E0B", "role": "accent", "name": "Highlight Orange"},
                    {"hex": "#1F2937", "role": "text", "name": "Dark Gray"},
                    {"hex": "#F9FAFB", "role": "background", "name": "Off White"}
                ],
                "typography": {
                    "heading": {
                        "family": "Inter",
                        "weight": "bold",
                        "size_base": 32
                    },
                    "body": {
                        "family": "Inter",
                        "weight": "normal",
                        "size_base": 16
                    }
                }
            }
        }


# Export convenient type aliases
ColorConfig = Dict[str, ColorSchema]
FontConfig = Dict[str, FontSchema]
