"""
Convert PDF previews to PNG thumbnails for web display
Uses pdf2image library to convert first page of each PDF
"""
import sys
import os
from pathlib import Path

# Check for pdf2image
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    print("⚠️  pdf2image not installed. Trying PIL-based conversion...")

from PIL import Image

def convert_pdf_to_png_pil(pdf_path, png_path, dpi=150):
    """Fallback: Extract first page using PyMuPDF if available"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Resize to thumbnail
        img.thumbnail((400, 520), Image.Resampling.LANCZOS)
        img.save(png_path, "PNG", optimize=True)
        doc.close()
        return True
    except ImportError:
        print("❌ PyMuPDF not installed. Install with: pip install PyMuPDF")
        return False
    except Exception as e:
        print(f"✗ Failed to convert {pdf_path.name}: {e}")
        return False

def convert_pdf_to_png(pdf_path, png_path, dpi=150):
    """Convert PDF to PNG using pdf2image"""
    try:
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
        if images:
            # Resize to thumbnail
            img = images[0]
            img.thumbnail((400, 520), Image.Resampling.LANCZOS)
            img.save(png_path, "PNG", optimize=True)
            return True
        return False
    except Exception as e:
        print(f"✗ Failed to convert {pdf_path.name}: {e}")
        return False

def main():
    pdf_dir = Path(__file__).parent.parent / "public" / "templates" / "previews"
    output_dir = Path(__file__).parent.parent / "public" / "templates"
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        return
    
    print(f"Converting {len(pdf_files)} PDFs to PNG thumbnails...\n")
    
    success_count = 0
    for pdf_path in pdf_files:
        png_path = output_dir / f"{pdf_path.stem}.png"
        
        if HAS_PDF2IMAGE:
            if convert_pdf_to_png(pdf_path, png_path):
                print(f"✓ Converted {pdf_path.name} -> {png_path.name}")
                success_count += 1
        else:
            if convert_pdf_to_png_pil(pdf_path, png_path):
                print(f"✓ Converted {pdf_path.name} -> {png_path.name}")
                success_count += 1
    
    print(f"\n✅ Converted {success_count}/{len(pdf_files)} PDFs to PNG")

if __name__ == "__main__":
    main()
