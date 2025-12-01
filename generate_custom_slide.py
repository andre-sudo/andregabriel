#!/usr/bin/env python3
"""
Generate a custom slide based on exact specifications
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Slide dimensions (16:9)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

def pct_to_inches_x(pct):
    """Convert percentage X to inches"""
    return Inches(13.333 * pct / 100)

def pct_to_inches_y(pct):
    """Convert percentage Y to inches"""
    return Inches(7.5 * pct / 100)

def create_slide():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    # Use blank layout
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Set white background
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(255, 255, 255)

    # Colors
    DARK_BLUE = RGBColor(0, 32, 96)
    MEDIUM_BLUE = RGBColor(0, 112, 192)
    LIGHT_GREY = RGBColor(242, 242, 242)
    WHITE = RGBColor(255, 255, 255)

    # ========================================
    # 1. MAIN TITLE
    # ========================================
    title_box = slide.shapes.add_textbox(
        pct_to_inches_x(5), pct_to_inches_y(5),
        pct_to_inches_x(90), pct_to_inches_y(10)
    )
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    title_para = title_frame.paragraphs[0]
    title_para.text = "Accelerating Growth in the Digital Age: Strategic Imperatives"
    title_para.font.size = Pt(32)
    title_para.font.color.rgb = DARK_BLUE
    title_para.font.name = "Calibri Light"
    title_para.alignment = PP_ALIGN.LEFT

    # ========================================
    # 2. COLUMN 1: Customer-Centricity (Left)
    # ========================================
    # Header Box
    header1 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        pct_to_inches_x(5), pct_to_inches_y(20),
        pct_to_inches_x(30), pct_to_inches_y(25)
    )
    header1.fill.solid()
    header1.fill.fore_color.rgb = MEDIUM_BLUE
    header1.line.fill.background()

    # Header Icon placeholder (person with arrows - using a simple circle as placeholder)
    icon1 = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        pct_to_inches_x(17), pct_to_inches_y(24),
        pct_to_inches_x(6), pct_to_inches_y(8)
    )
    icon1.fill.solid()
    icon1.fill.fore_color.rgb = WHITE
    icon1.line.color.rgb = WHITE

    # Header Title
    header1_title = slide.shapes.add_textbox(
        pct_to_inches_x(5), pct_to_inches_y(35),
        pct_to_inches_x(30), pct_to_inches_y(8)
    )
    h1_frame = header1_title.text_frame
    h1_para = h1_frame.paragraphs[0]
    h1_para.text = "Customer-Centricity"
    h1_para.font.size = Pt(20)
    h1_para.font.bold = True
    h1_para.font.color.rgb = WHITE
    h1_para.font.name = "Arial"
    h1_para.alignment = PP_ALIGN.CENTER

    # Content Box
    content1 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        pct_to_inches_x(5), pct_to_inches_y(45),
        pct_to_inches_x(30), pct_to_inches_y(40)
    )
    content1.fill.solid()
    content1.fill.fore_color.rgb = LIGHT_GREY
    content1.line.fill.background()

    # Content List
    content1_text = slide.shapes.add_textbox(
        pct_to_inches_x(7), pct_to_inches_y(48),
        pct_to_inches_x(26), pct_to_inches_y(35)
    )
    c1_frame = content1_text.text_frame
    c1_frame.word_wrap = True

    bullets1 = [
        "Customer-centricity and specifications",
        "Provide lowoperated digital and omivasion",
        "Innovate digitad property noaz customer-centricity"
    ]

    for i, bullet in enumerate(bullets1):
        if i == 0:
            para = c1_frame.paragraphs[0]
        else:
            para = c1_frame.add_paragraph()
        para.text = f"• {bullet}"
        para.font.size = Pt(16)
        para.font.color.rgb = DARK_BLUE
        para.font.name = "Arial"
        para.space_after = Pt(8)

    # ========================================
    # 3. COLUMN 2: Operational Agility (Middle)
    # ========================================
    # Header Box
    header2 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        pct_to_inches_x(35.5), pct_to_inches_y(20),
        pct_to_inches_x(30), pct_to_inches_y(25)
    )
    header2.fill.solid()
    header2.fill.fore_color.rgb = MEDIUM_BLUE
    header2.line.fill.background()

    # Header Icon placeholder (speedometer - using diamond as placeholder)
    icon2 = slide.shapes.add_shape(
        MSO_SHAPE.DIAMOND,
        pct_to_inches_x(47.5), pct_to_inches_y(24),
        pct_to_inches_x(6), pct_to_inches_y(8)
    )
    icon2.fill.solid()
    icon2.fill.fore_color.rgb = WHITE
    icon2.line.color.rgb = WHITE

    # Header Title
    header2_title = slide.shapes.add_textbox(
        pct_to_inches_x(35.5), pct_to_inches_y(35),
        pct_to_inches_x(30), pct_to_inches_y(8)
    )
    h2_frame = header2_title.text_frame
    h2_para = h2_frame.paragraphs[0]
    h2_para.text = "Operational Agility"
    h2_para.font.size = Pt(20)
    h2_para.font.bold = True
    h2_para.font.color.rgb = WHITE
    h2_para.font.name = "Arial"
    h2_para.alignment = PP_ALIGN.CENTER

    # Content Box
    content2 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        pct_to_inches_x(35.5), pct_to_inches_y(45),
        pct_to_inches_x(30), pct_to_inches_y(40)
    )
    content2.fill.solid()
    content2.fill.fore_color.rgb = LIGHT_GREY
    content2.line.fill.background()

    # Content List
    content2_text = slide.shapes.add_textbox(
        pct_to_inches_x(37.5), pct_to_inches_y(48),
        pct_to_inches_x(26), pct_to_inches_y(35)
    )
    c2_frame = content2_text.text_frame
    c2_frame.word_wrap = True

    bullets2 = [
        "Agility offer in operational agility",
        "L.ost comprehensivind in operational agility",
        "Soll-collection and innovation and development agility"
    ]

    for i, bullet in enumerate(bullets2):
        if i == 0:
            para = c2_frame.paragraphs[0]
        else:
            para = c2_frame.add_paragraph()
        para.text = f"• {bullet}"
        para.font.size = Pt(16)
        para.font.color.rgb = DARK_BLUE
        para.font.name = "Arial"
        para.space_after = Pt(8)

    # ========================================
    # 4. COLUMN 3: Ecosystem Partnerships (Right)
    # ========================================
    # Header Box
    header3 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        pct_to_inches_x(66), pct_to_inches_y(20),
        pct_to_inches_x(30), pct_to_inches_y(25)
    )
    header3.fill.solid()
    header3.fill.fore_color.rgb = MEDIUM_BLUE
    header3.line.fill.background()

    # Header Icon placeholder (three connected people - using hexagon as placeholder)
    icon3 = slide.shapes.add_shape(
        MSO_SHAPE.HEXAGON,
        pct_to_inches_x(78), pct_to_inches_y(24),
        pct_to_inches_x(6), pct_to_inches_y(8)
    )
    icon3.fill.solid()
    icon3.fill.fore_color.rgb = WHITE
    icon3.line.color.rgb = WHITE

    # Header Title
    header3_title = slide.shapes.add_textbox(
        pct_to_inches_x(66), pct_to_inches_y(35),
        pct_to_inches_x(30), pct_to_inches_y(8)
    )
    h3_frame = header3_title.text_frame
    h3_para = h3_frame.paragraphs[0]
    h3_para.text = "Ecosystem Partnerships"
    h3_para.font.size = Pt(20)
    h3_para.font.bold = True
    h3_para.font.color.rgb = WHITE
    h3_para.font.name = "Arial"
    h3_para.alignment = PP_ALIGN.CENTER

    # Content Box
    content3 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        pct_to_inches_x(66), pct_to_inches_y(45),
        pct_to_inches_x(30), pct_to_inches_y(40)
    )
    content3.fill.solid()
    content3.fill.fore_color.rgb = LIGHT_GREY
    content3.line.fill.background()

    # Content List
    content3_text = slide.shapes.add_textbox(
        pct_to_inches_x(68), pct_to_inches_y(48),
        pct_to_inches_x(26), pct_to_inches_y(35)
    )
    c3_frame = content3_text.text_frame
    c3_frame.word_wrap = True

    bullets3 = [
        "Ecosystem partnerships or global platform",
        "Develop cosacanotomy of ecosystem partnerships",
        "Enhance transprark of scas and potent onricating partnerships"
    ]

    for i, bullet in enumerate(bullets3):
        if i == 0:
            para = c3_frame.paragraphs[0]
        else:
            para = c3_frame.add_paragraph()
        para.text = f"• {bullet}"
        para.font.size = Pt(16)
        para.font.color.rgb = DARK_BLUE
        para.font.name = "Arial"
        para.space_after = Pt(8)

    # ========================================
    # 5. FOOTER / SOURCE
    # ========================================
    footer = slide.shapes.add_textbox(
        pct_to_inches_x(5), pct_to_inches_y(95),
        pct_to_inches_x(45), pct_to_inches_y(4)
    )
    footer_frame = footer.text_frame
    footer_para = footer_frame.paragraphs[0]
    footer_para.text = "Source: McKinsey Global Institute Analysis, 2024"
    footer_para.font.size = Pt(10)
    footer_para.font.color.rgb = DARK_BLUE
    footer_para.font.name = "Arial"
    footer_para.alignment = PP_ALIGN.LEFT

    # Save
    output_path = "/home/user/andregabriel/output/strategic-imperatives.pptx"
    prs.save(output_path)
    print(f"Saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_slide()
