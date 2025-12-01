/**
 * Brand World Model - Express API Server
 *
 * This server provides the REST API for:
 * - Uploading and analyzing slide images
 * - Managing brand profiles
 * - Generating presentations in multiple formats
 */

import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
import fs from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(ROOT_DIR, 'public')));
app.use('/output', express.static(path.join(ROOT_DIR, 'output')));
app.use('/uploads', express.static(path.join(ROOT_DIR, 'uploads')));

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(ROOT_DIR, 'uploads');
    await fs.mkdir(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only images are allowed.'));
    }
  }
});

// ============================================
// API Routes
// ============================================

/**
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * Upload slide images for analysis
 * POST /api/upload/slides
 */
app.post('/api/upload/slides', upload.array('slides', 20), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files uploaded' });
    }

    const uploadedFiles = req.files.map(f => ({
      filename: f.filename,
      originalName: f.originalname,
      path: `/uploads/${f.filename}`,
      size: f.size
    }));

    res.json({
      success: true,
      message: `${uploadedFiles.length} file(s) uploaded successfully`,
      files: uploadedFiles
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Upload brand assets (logo, style guides, etc.)
 * POST /api/upload/assets
 */
app.post('/api/upload/assets', upload.array('assets', 10), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files uploaded' });
    }

    const uploadedFiles = req.files.map(f => ({
      filename: f.filename,
      originalName: f.originalname,
      path: `/uploads/${f.filename}`,
      type: f.mimetype
    }));

    res.json({
      success: true,
      files: uploadedFiles
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Analyze uploaded slides to extract brand patterns
 * POST /api/analyze
 */
app.post('/api/analyze', async (req, res) => {
  try {
    const { slidePaths, brandName } = req.body;

    if (!slidePaths || slidePaths.length === 0) {
      return res.status(400).json({ error: 'No slide paths provided' });
    }

    // Convert relative paths to absolute
    const absolutePaths = slidePaths.map(p =>
      path.join(ROOT_DIR, p.startsWith('/') ? p.slice(1) : p)
    );

    // Run Python analyzer
    const result = await runPythonScript('analyze', {
      slides: absolutePaths,
      brand_name: brandName || 'Extracted Brand',
      output_dir: path.join(ROOT_DIR, 'data', 'brands')
    });

    res.json({
      success: true,
      analysis: result
    });
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * List all stored brand profiles
 * GET /api/brands
 */
app.get('/api/brands', async (req, res) => {
  try {
    const brandsDir = path.join(ROOT_DIR, 'data', 'brands');
    await fs.mkdir(brandsDir, { recursive: true });

    const files = await fs.readdir(brandsDir);
    const brands = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        const content = await fs.readFile(path.join(brandsDir, file), 'utf-8');
        const brand = JSON.parse(content);
        brands.push({
          id: brand.id || file.replace('.json', ''),
          name: brand.name,
          updated_at: brand.updated_at,
          confidence: brand.confidence_score || 0
        });
      }
    }

    res.json({ brands });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get a specific brand profile
 * GET /api/brands/:id
 */
app.get('/api/brands/:id', async (req, res) => {
  try {
    const brandPath = path.join(ROOT_DIR, 'data', 'brands', `${req.params.id}.json`);
    const content = await fs.readFile(brandPath, 'utf-8');
    res.json(JSON.parse(content));
  } catch (error) {
    if (error.code === 'ENOENT') {
      res.status(404).json({ error: 'Brand not found' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

/**
 * Delete a brand profile
 * DELETE /api/brands/:id
 */
app.delete('/api/brands/:id', async (req, res) => {
  try {
    const brandPath = path.join(ROOT_DIR, 'data', 'brands', `${req.params.id}.json`);
    await fs.unlink(brandPath);
    res.json({ success: true, message: 'Brand deleted' });
  } catch (error) {
    if (error.code === 'ENOENT') {
      res.status(404).json({ error: 'Brand not found' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

/**
 * Generate presentation from brand and content
 * POST /api/generate
 */
app.post('/api/generate', async (req, res) => {
  try {
    const { brandId, content, format = 'both', filename } = req.body;

    if (!brandId) {
      return res.status(400).json({ error: 'Brand ID is required' });
    }

    if (!content || content.length === 0) {
      return res.status(400).json({ error: 'Slide content is required' });
    }

    // Load brand profile
    const brandPath = path.join(ROOT_DIR, 'data', 'brands', `${brandId}.json`);
    let brandData;
    try {
      const brandContent = await fs.readFile(brandPath, 'utf-8');
      brandData = JSON.parse(brandContent);
    } catch {
      return res.status(404).json({ error: 'Brand not found' });
    }

    const outputId = filename || uuidv4();
    const outputDir = path.join(ROOT_DIR, 'output');
    await fs.mkdir(outputDir, { recursive: true });

    const results = {};

    // Run Python generator
    const result = await runPythonScript('generate', {
      brand: brandData,
      content: content,
      format: format,
      output_dir: outputDir,
      output_id: outputId
    });

    if (format === 'pptx' || format === 'both') {
      results.pptx = `/output/${outputId}.pptx`;
    }

    if (format === 'html' || format === 'both') {
      results.html = `/output/${outputId}.html`;
    }

    res.json({
      success: true,
      files: results,
      details: result
    });
  } catch (error) {
    console.error('Generation error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Preview a brand's styling as CSS
 * GET /api/brands/:id/css
 */
app.get('/api/brands/:id/css', async (req, res) => {
  try {
    const brandPath = path.join(ROOT_DIR, 'data', 'brands', `${req.params.id}.json`);
    const content = await fs.readFile(brandPath, 'utf-8');
    const brand = JSON.parse(content);

    // Generate CSS from brand
    const css = generateBrandCSS(brand);
    res.type('text/css').send(css);
  } catch (error) {
    if (error.code === 'ENOENT') {
      res.status(404).json({ error: 'Brand not found' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

// ============================================
// Helper Functions
// ============================================

/**
 * Run a Python script and return the result
 */
function runPythonScript(action, data) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(ROOT_DIR, 'src', 'cli.py');

    const process = spawn('python3', [scriptPath, action, JSON.stringify(data)]);

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(stdout));
        } catch {
          resolve({ output: stdout });
        }
      } else {
        reject(new Error(stderr || `Process exited with code ${code}`));
      }
    });

    process.on('error', (err) => {
      reject(err);
    });
  });
}

/**
 * Generate CSS from brand profile
 */
function generateBrandCSS(brand) {
  const colors = {};
  if (brand.colors) {
    for (const color of brand.colors) {
      colors[color.role] = color.hex;
    }
  }

  const typography = brand.typography || {};
  const heading = typography.heading || {};
  const body = typography.body || {};
  const spacing = brand.spacing || {};

  return `:root {
  /* Colors */
  --color-primary: ${colors.primary || '#1E40AF'};
  --color-secondary: ${colors.secondary || '#6B7280'};
  --color-accent: ${colors.accent || '#F59E0B'};
  --color-background: ${colors.background || '#FFFFFF'};
  --color-text: ${colors.text || '#1F2937'};

  /* Typography */
  --font-heading: '${heading.family || 'Inter'}', sans-serif;
  --font-body: '${body.family || 'Inter'}', sans-serif;
  --font-size-base: ${body.size_base || 16}px;
  --line-height: ${body.line_height || 1.5};

  /* Spacing */
  --spacing-unit: ${spacing.unit || 8}px;
  --margin-x: ${(spacing.margin_x || 4) * (spacing.unit || 8)}px;
  --margin-y: ${(spacing.margin_y || 3) * (spacing.unit || 8)}px;
}`;
}

// ============================================
// Serve Frontend
// ============================================

// Serve index.html for root route
app.get('/', (req, res) => {
  res.sendFile(path.join(ROOT_DIR, 'public', 'index.html'));
});

// ============================================
// Start Server
// ============================================

app.listen(PORT, () => {
  console.log(`🎨 Brand World Model server running at http://localhost:${PORT}`);
  console.log(`📁 Uploads directory: ${path.join(ROOT_DIR, 'uploads')}`);
  console.log(`📤 Output directory: ${path.join(ROOT_DIR, 'output')}`);
});

export default app;
