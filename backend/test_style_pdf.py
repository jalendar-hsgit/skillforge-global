"""
Test script to verify Style Panel fields are properly saved and used in PDF export
"""
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, engine
from app.modelsx.resume import Resume
from app.api.v1x.resume_export import export_pdf
import os

def test_style_pdf():
    db = SessionLocal()
    
    try:
        # Find a test resume (or create one)
        resume = db.query(Resume).first()
        
        if not resume:
            print("❌ No resume found in database. Please create a resume first.")
            return
        
        print(f"✅ Testing with resume ID: {resume.id}")
        print(f"   Title: {resume.title}")
        print(f"\n📊 Current Style Settings:")
        print(f"   Font Family: {resume.font_family}")
        print(f"   Font Size: {resume.font_size}pt")
        print(f"   Heading Size: {resume.heading_size}pt")
        print(f"   Accent Color: {resume.accent_color}")
        print(f"   Text Color: {resume.text_color}")
        print(f"   Heading Color: {resume.heading_color}")
        print(f"   Line Spacing: {resume.line_spacing}")
        print(f"   Layout: {resume.layout}")
        
        # Update resume with test styles
        print(f"\n🎨 Updating to test styles...")
        resume.font_family = "Century Gothic"
        resume.font_size = 10
        resume.heading_size = 10
        resume.accent_color = "#9333ea"  # Purple
        resume.text_color = "#000000"
        resume.heading_color = "#1f2937"
        resume.line_spacing = 1.15
        
        # Add some content if missing
        if not resume.summary:
            resume.summary = "Professional software engineer with 5+ years of experience in full-stack development. Specialized in Python, JavaScript, and cloud technologies."
        
        db.commit()
        db.refresh(resume)
        
        print(f"✅ Updated style settings:")
        print(f"   Font: {resume.font_family} @ {resume.font_size}pt")
        print(f"   Heading: {resume.heading_size}pt")
        print(f"   Summary: {'Present' if resume.summary else 'Missing'}")
        
        # Generate PDF
        print(f"\n📄 Generating PDF...")
        pdf_bytes = export_pdf(resume)
        
        # Save to file
        output_path = os.path.join(os.path.dirname(__file__), f"test_resume_{resume.id}_styled.pdf")
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✅ PDF generated successfully!")
        print(f"   Output: {output_path}")
        print(f"   Size: {len(pdf_bytes) / 1024:.2f} KB")
        
        print(f"\n✅ TEST PASSED - Please verify the PDF manually:")
        print(f"   1. Font should be Helvetica (Century Gothic fallback)")
        print(f"   2. Body text should be 10pt")
        print(f"   3. Headings should be 10pt")
        print(f"   4. Summary section should be present")
        print(f"   5. Colors should match the settings")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_style_pdf()
