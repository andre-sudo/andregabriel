/**
 * Brand World Model - Frontend Application
 */

// State
const state = {
    uploadedFiles: [],
    brands: [],
    selectedBrand: null,
    slides: [{ layout: 'content', title: '', body: '' }]
};

// DOM Elements
const slideUploadArea = document.getElementById('slide-upload-area');
const slideInput = document.getElementById('slide-input');
const uploadedFilesContainer = document.getElementById('uploaded-files');
const brandNameInput = document.getElementById('brand-name');
const analyzeBtn = document.getElementById('analyze-btn');
const analysisResult = document.getElementById('analysis-result');
const brandList = document.getElementById('brand-list');
const refreshBrandsBtn = document.getElementById('refresh-brands-btn');
const slidesEditor = document.getElementById('slides-editor');
const addSlideBtn = document.getElementById('add-slide-btn');
const generateBtn = document.getElementById('generate-btn');
const generateResult = document.getElementById('generate-result');

// ============================================
// File Upload
// ============================================

slideUploadArea.addEventListener('click', () => slideInput.click());

slideUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    slideUploadArea.classList.add('drag-over');
});

slideUploadArea.addEventListener('dragleave', () => {
    slideUploadArea.classList.remove('drag-over');
});

slideUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    slideUploadArea.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

slideInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

async function handleFiles(files) {
    const formData = new FormData();

    for (const file of files) {
        if (file.type.startsWith('image/')) {
            formData.append('slides', file);
        }
    }

    try {
        const response = await fetch('/api/upload/slides', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            state.uploadedFiles.push(...data.files);
            renderUploadedFiles();
            updateAnalyzeButton();
        } else {
            alert('Upload failed: ' + data.error);
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('Upload failed. Please try again.');
    }
}

function renderUploadedFiles() {
    uploadedFilesContainer.innerHTML = state.uploadedFiles.map((file, index) => `
        <div class="file-item">
            <span>📄 ${file.originalName}</span>
            <button class="remove-file" onclick="removeFile(${index})">×</button>
        </div>
    `).join('');
}

function removeFile(index) {
    state.uploadedFiles.splice(index, 1);
    renderUploadedFiles();
    updateAnalyzeButton();
}

function updateAnalyzeButton() {
    analyzeBtn.disabled = state.uploadedFiles.length === 0;
}

// ============================================
// Brand Analysis
// ============================================

analyzeBtn.addEventListener('click', async () => {
    const brandName = brandNameInput.value.trim() || 'My Brand';

    analyzeBtn.classList.add('loading');
    analyzeBtn.disabled = true;

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                slidePaths: state.uploadedFiles.map(f => f.path),
                brandName
            })
        });

        const data = await response.json();

        if (data.success) {
            analysisResult.hidden = false;
            analysisResult.className = 'result-box success';
            analysisResult.innerHTML = `
                <strong>✅ Brand profile created!</strong>
                <p>Analyzed ${data.analysis.slides_analyzed} slides and extracted ${data.analysis.colors_extracted} colors.</p>
                <p>Brand ID: <code>${data.analysis.brand_id}</code></p>
            `;

            // Refresh brand list
            loadBrands();
        } else {
            analysisResult.hidden = false;
            analysisResult.className = 'result-box error';
            analysisResult.innerHTML = `<strong>❌ Analysis failed:</strong> ${data.error}`;
        }
    } catch (error) {
        console.error('Analysis error:', error);
        analysisResult.hidden = false;
        analysisResult.className = 'result-box error';
        analysisResult.innerHTML = `<strong>❌ Analysis failed:</strong> ${error.message}`;
    } finally {
        analyzeBtn.classList.remove('loading');
        analyzeBtn.disabled = false;
    }
});

// ============================================
// Brand Selection
// ============================================

refreshBrandsBtn.addEventListener('click', loadBrands);

async function loadBrands() {
    try {
        const response = await fetch('/api/brands');
        const data = await response.json();

        state.brands = data.brands || [];
        renderBrandList();
    } catch (error) {
        console.error('Failed to load brands:', error);
    }
}

function renderBrandList() {
    if (state.brands.length === 0) {
        brandList.innerHTML = '<p class="empty-state">No brand profiles yet. Analyze some slides first!</p>';
        return;
    }

    brandList.innerHTML = state.brands.map(brand => `
        <div class="brand-card ${state.selectedBrand?.id === brand.id ? 'selected' : ''}"
             onclick="selectBrand('${brand.id}')">
            <h3>${brand.name}</h3>
            <div class="brand-colors" id="colors-${brand.id}"></div>
            <small>Confidence: ${Math.round((brand.confidence || 0) * 100)}%</small>
        </div>
    `).join('');

    // Load color swatches for each brand
    state.brands.forEach(loadBrandColors);
}

async function loadBrandColors(brand) {
    try {
        const response = await fetch(`/api/brands/${brand.id}`);
        const data = await response.json();

        const container = document.getElementById(`colors-${brand.id}`);
        if (container && data.colors) {
            container.innerHTML = data.colors.slice(0, 5).map(c =>
                `<div class="color-swatch" style="background-color: ${c.hex}"></div>`
            ).join('');
        }
    } catch (error) {
        console.error('Failed to load brand colors:', error);
    }
}

async function selectBrand(brandId) {
    try {
        const response = await fetch(`/api/brands/${brandId}`);
        state.selectedBrand = await response.json();
        renderBrandList();
        updateGenerateButton();
    } catch (error) {
        console.error('Failed to select brand:', error);
    }
}

// Make selectBrand available globally
window.selectBrand = selectBrand;

// ============================================
// Slide Editor
// ============================================

addSlideBtn.addEventListener('click', () => {
    state.slides.push({ layout: 'content', title: '', body: '' });
    renderSlides();
});

function renderSlides() {
    slidesEditor.innerHTML = state.slides.map((slide, index) => `
        <div class="slide-form" data-slide-index="${index}">
            <div class="slide-header">
                <span class="slide-number">Slide ${index + 1}</span>
                <select class="layout-select" onchange="updateSlideLayout(${index}, this.value)">
                    <option value="title_slide" ${slide.layout === 'title_slide' ? 'selected' : ''}>Title Slide</option>
                    <option value="content" ${slide.layout === 'content' ? 'selected' : ''}>Content</option>
                    <option value="section_header" ${slide.layout === 'section_header' ? 'selected' : ''}>Section Header</option>
                    <option value="two_column" ${slide.layout === 'two_column' ? 'selected' : ''}>Two Columns</option>
                    <option value="image_left" ${slide.layout === 'image_left' ? 'selected' : ''}>Image Left</option>
                    <option value="image_right" ${slide.layout === 'image_right' ? 'selected' : ''}>Image Right</option>
                    <option value="quote" ${slide.layout === 'quote' ? 'selected' : ''}>Quote</option>
                </select>
                ${state.slides.length > 1 ? `<button class="btn-icon delete-slide" onclick="deleteSlide(${index})" title="Delete slide">×</button>` : ''}
            </div>
            <div class="slide-fields">
                <input type="text" class="slide-title" placeholder="${getPlaceholder(slide.layout, 'title')}"
                       value="${escapeHtml(slide.title)}"
                       onchange="updateSlideField(${index}, 'title', this.value)">
                <textarea class="slide-body" placeholder="${getPlaceholder(slide.layout, 'body')}"
                          onchange="updateSlideField(${index}, 'body', this.value)">${escapeHtml(slide.body)}</textarea>
            </div>
        </div>
    `).join('');

    updateGenerateButton();
}

function getPlaceholder(layout, field) {
    const placeholders = {
        title_slide: { title: 'Presentation Title', body: 'Subtitle or tagline' },
        content: { title: 'Slide Title', body: 'Slide content (use new lines for bullet points)' },
        section_header: { title: 'Section Title', body: '' },
        two_column: { title: 'Slide Title', body: 'Left column | Right column (separate with |)' },
        image_left: { title: 'Slide Title', body: 'Text content for the right side' },
        image_right: { title: 'Slide Title', body: 'Text content for the left side' },
        quote: { title: 'Attribution (who said it)', body: 'The quote text' }
    };

    return placeholders[layout]?.[field] || (field === 'title' ? 'Title' : 'Content');
}

function updateSlideLayout(index, layout) {
    state.slides[index].layout = layout;
    renderSlides();
}

function updateSlideField(index, field, value) {
    state.slides[index][field] = value;
    updateGenerateButton();
}

function deleteSlide(index) {
    state.slides.splice(index, 1);
    renderSlides();
}

// Make functions available globally
window.updateSlideLayout = updateSlideLayout;
window.updateSlideField = updateSlideField;
window.deleteSlide = deleteSlide;
window.removeFile = removeFile;

function updateGenerateButton() {
    const hasContent = state.slides.some(s => s.title.trim() || s.body.trim());
    generateBtn.disabled = !state.selectedBrand || !hasContent;
}

// ============================================
// Generate Presentation
// ============================================

generateBtn.addEventListener('click', async () => {
    if (!state.selectedBrand) {
        alert('Please select a brand profile first.');
        return;
    }

    // Get selected formats
    const formatCheckboxes = document.querySelectorAll('input[name="format"]:checked');
    const formats = Array.from(formatCheckboxes).map(cb => cb.value);

    if (formats.length === 0) {
        alert('Please select at least one output format.');
        return;
    }

    let format = 'both';
    if (formats.length === 1) {
        format = formats[0];
    }

    // Prepare content
    const content = state.slides.map(slide => {
        const result = {
            layout: slide.layout,
            title: slide.title
        };

        // Handle different layouts
        if (slide.layout === 'two_column' && slide.body.includes('|')) {
            const [left, right] = slide.body.split('|').map(s => s.trim());
            result.left = left;
            result.right = right;
        } else if (slide.layout === 'quote') {
            result.body = slide.body;
            result.attribution = slide.title;
        } else if (slide.body.includes('\n')) {
            result.bullets = slide.body.split('\n').filter(l => l.trim());
        } else {
            result.body = slide.body;
        }

        // For title slide, use body as subtitle
        if (slide.layout === 'title_slide') {
            result.subtitle = slide.body;
        }

        return result;
    });

    generateBtn.classList.add('loading');
    generateBtn.disabled = true;

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                brandId: state.selectedBrand.id,
                content,
                format
            })
        });

        const data = await response.json();

        if (data.success) {
            generateResult.hidden = false;
            generateResult.className = 'result-box success';

            let links = '<div class="download-links">';
            if (data.files.pptx) {
                links += `<a href="${data.files.pptx}" class="download-link" download>📊 Download PowerPoint</a>`;
            }
            if (data.files.html) {
                links += `<a href="${data.files.html}" class="download-link" target="_blank">🌐 View HTML Presentation</a>`;
            }
            links += '</div>';

            generateResult.innerHTML = `
                <strong>✅ Presentation generated!</strong>
                <p>Your branded presentation is ready.</p>
                ${links}
            `;
        } else {
            generateResult.hidden = false;
            generateResult.className = 'result-box error';
            generateResult.innerHTML = `<strong>❌ Generation failed:</strong> ${data.error}`;
        }
    } catch (error) {
        console.error('Generation error:', error);
        generateResult.hidden = false;
        generateResult.className = 'result-box error';
        generateResult.innerHTML = `<strong>❌ Generation failed:</strong> ${error.message}`;
    } finally {
        generateBtn.classList.remove('loading');
        updateGenerateButton();
    }
});

// ============================================
// Utilities
// ============================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    loadBrands();
    renderSlides();
});
