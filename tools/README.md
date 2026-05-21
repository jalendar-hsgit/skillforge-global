# Template Preview Generation

This directory contains scripts for generating preview images for resume templates.

## Quick Start

Generate all template previews with one command:

```bash
npm run generate:templates
```

This will:
1. Generate PDF previews from templates
2. Convert PDFs to PNG thumbnails
3. Update database with PNG URLs

## Individual Scripts

### Generate PDF Previews
```bash
cd backend
python generate_template_pdfs.py
```
Creates actual resume PDFs using each template's styling in `public/templates/previews/`

### Convert PDFs to PNG
```bash
cd backend
python convert_pdfs_to_png.py
```
Converts PDF previews to optimized PNG thumbnails (~36KB each) in `public/templates/`

### Update Database
```bash
cd backend
python update_template_thumbnails.py
```
Updates `resume_templates` table with PNG thumbnail URLs

### Generate SVG Placeholders (Fallback)
```bash
npm run generate:template-svgs
```
Creates gradient SVG placeholders as fallback

## Dependencies

Backend (Python):
- `reportlab==4.4.4` - PDF generation
- `Pillow==12.0.0` - Image processing
- `PyMuPDF==1.26.6` - PDF to PNG conversion

All dependencies are in `backend/requirements.txt`

## Output

- **PDFs**: `public/templates/previews/*.pdf` (full page previews)
- **PNGs**: `public/templates/*.png` (400x520px thumbnails)
- **SVGs**: `public/templates/*.svg` (gradient fallbacks)

## Template Mapping

Templates are mapped by slug:
- `Modern Professional` → `modern-professional.png`
- `Software Engineer` → `software-engineer.png`
- etc.

See `backend/update_template_thumbnails.py` for full mapping.
