# Brand World Model

An AI-powered slide template generator that learns from your brand materials and existing presentations to generate new, on-brand slides.

## What is a "World Model"?

In this context, a **Brand World Model** is an AI system that:

1. **Perceives** - Analyzes slide images and brand materials using vision AI
2. **Learns** - Extracts design patterns, colors, typography, and layout rules
3. **Remembers** - Stores brand knowledge in a structured knowledge base
4. **Generates** - Creates new presentations that follow learned patterns

This approach goes beyond simple templates by understanding the *design DNA* of your brand.

## Features

- **Vision Analysis** - Upload slide images to automatically extract:
  - Color palettes with role detection (primary, secondary, accent)
  - Typography patterns and hierarchy
  - Layout structures and element positioning
  - Spacing and visual rhythm

- **Brand Knowledge Base** - Persistent storage of learned brand patterns

- **Multi-format Output**:
  - PowerPoint (.pptx) for Microsoft Office
  - HTML (reveal.js) for web presentations

- **Express API** - RESTful API for integration with other tools

- **Web Interface** - Simple UI for uploading, analyzing, and generating

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BRAND WORLD MODEL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Slide Image  │    │   Color      │    │   Brand      │      │
│  │   Analyzer   │    │  Analyzer    │    │  Extractor   │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             ▼                                   │
│               ┌─────────────────────────┐                       │
│               │   Brand Knowledge Base   │                      │
│               │   (Pydantic Schemas)     │                      │
│               └─────────────┬───────────┘                       │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  PowerPoint  │    │  Reveal.js   │    │   Express    │      │
│  │  Generator   │    │  Generator   │    │   API        │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Anthropic API key (for vision analysis)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd brand-world-model

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the Server

```bash
# Start the Express server
npm start

# Or in development mode with auto-reload
npm run dev
```

Open http://localhost:3000 in your browser.

## Usage

### 1. Analyze Your Brand

Upload existing slide images (PNG, JPG, etc.) to extract your brand's design patterns:

```bash
# Via API
curl -X POST http://localhost:3000/api/upload/slides \
  -F "slides=@slide1.png" \
  -F "slides=@slide2.png"

curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"slidePaths": ["/uploads/slide1.png"], "brandName": "My Brand"}'
```

### 2. Generate Presentations

Create new slides using your brand profile:

```bash
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "brandId": "my-brand",
    "content": [
      {"layout": "title_slide", "title": "Q4 Results", "subtitle": "Company Update"},
      {"layout": "content", "title": "Key Highlights", "bullets": ["Revenue up 20%", "New product launched"]}
    ],
    "format": "both"
  }'
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload/slides` | Upload slide images |
| POST | `/api/analyze` | Analyze slides and create brand profile |
| GET | `/api/brands` | List all brand profiles |
| GET | `/api/brands/:id` | Get specific brand profile |
| DELETE | `/api/brands/:id` | Delete brand profile |
| POST | `/api/generate` | Generate presentation |
| GET | `/api/brands/:id/css` | Export brand as CSS variables |

### Slide Layouts

| Layout | Description |
|--------|-------------|
| `title_slide` | Title and subtitle centered |
| `content` | Title with bullet points or body text |
| `section_header` | Section divider with accent background |
| `two_column` | Side-by-side content |
| `image_left` | Image on left, text on right |
| `image_right` | Text on left, image on right |
| `quote` | Centered quote with attribution |
| `code` | Code block with syntax highlighting (reveal.js only) |

## Project Structure

```
brand-world-model/
├── server/
│   └── index.js          # Express API server
├── src/
│   ├── analyzers/        # Vision analysis modules
│   │   ├── slide_analyzer.py
│   │   ├── color_analyzer.py
│   │   └── brand_extractor.py
│   ├── brand/            # Brand schemas and knowledge base
│   │   ├── schemas.py
│   │   └── knowledge_base.py
│   ├── generators/       # Template generators
│   │   ├── base.py
│   │   ├── pptx_generator.py
│   │   └── revealjs_generator.py
│   └── cli.py            # CLI interface
├── public/               # Web UI
│   ├── index.html
│   ├── css/
│   └── js/
├── data/brands/          # Stored brand profiles
├── uploads/              # Uploaded files
├── output/               # Generated presentations
├── package.json
├── requirements.txt
└── README.md
```

## Extending

### Adding New Generators

Create a new generator by extending `BaseGenerator`:

```python
from generators.base import BaseGenerator

class MyGenerator(BaseGenerator):
    def generate(self, content, output_path):
        # Implementation
        pass

    def add_slide(self, layout_type, content):
        # Implementation
        pass

    def save(self, output_path):
        # Implementation
        pass
```

### Custom Vision Analysis

To use a different vision model, modify `SlideAnalyzer` in `src/analyzers/slide_analyzer.py`.

## License

MIT
