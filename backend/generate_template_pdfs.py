"""
Generate PDF preview thumbnails for resume templates
Creates actual resume PDFs using the template styling
"""
import sys
import os
from pathlib import Path
from io import BytesIO

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas

# Sample resume data for previews
SAMPLE_DATA = {
    "full_name": "John Doe",
    "title": "Software Engineer",
    "email": "john.doe@email.com",
    "phone": "(555) 123-4567",
    "location": "San Francisco, CA",
    "summary": "Experienced software engineer with 5+ years of expertise in full-stack development, cloud architecture, and agile methodologies.",
    "experience": [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "duration": "2020 - Present",
            "description": "Led development of microservices architecture"
        },
        {
            "title": "Software Engineer",
            "company": "StartupXYZ",
            "duration": "2018 - 2020",
            "description": "Developed features for SaaS platform"
        }
    ],
    "education": [
        {
            "degree": "B.S. Computer Science",
            "school": "University of Technology",
            "year": "2018"
        }
    ],
    "skills": ["Python", "JavaScript", "React", "AWS", "Docker", "SQL"]
}

# Template configurations matching the database
TEMPLATES = [
    {"name": "Modern Professional", "slug": "modern-professional", "accent": "#2563eb", "font": "Helvetica"},
    {"name": "Software Engineer", "slug": "software-engineer", "accent": "#0ea5e9", "font": "Helvetica"},
    {"name": "Corporate Standard", "slug": "corporate-standard", "accent": "#1e40af", "font": "Helvetica"},
    {"name": "Tech Stack", "slug": "tech-stack", "accent": "#6366f1", "font": "Helvetica"},
    {"name": "Sleek Professional", "slug": "sleek-professional", "accent": "#8b5cf6", "font": "Helvetica"},
    {"name": "Data Scientist", "slug": "data-scientist", "accent": "#06b6d4", "font": "Helvetica"},
    {"name": "Minimalist Blue", "slug": "minimalist-blue", "accent": "#3b82f6", "font": "Helvetica"},
    {"name": "Executive Black", "slug": "executive-black", "accent": "#000000", "font": "Helvetica-Bold"},
    {"name": "Healthcare Professional", "slug": "healthcare-professional", "accent": "#059669", "font": "Helvetica"},
    {"name": "C-Suite Executive", "slug": "c-suite-executive", "accent": "#dc2626", "font": "Helvetica-Bold"},
    {"name": "Professional Gray", "slug": "professional-gray", "accent": "#6b7280", "font": "Helvetica"},
    {"name": "DevOps Specialist", "slug": "devops-specialist", "accent": "#10b981", "font": "Courier"},
    {"name": "Traditional Serif", "slug": "traditional-serif", "accent": "#854d0e", "font": "Times-Roman"},
    {"name": "Senior Leader", "slug": "senior-leader", "accent": "#7c2d12", "font": "Helvetica-Bold"},
    {"name": "Nursing Excellence", "slug": "nursing-excellence", "accent": "#0891b2", "font": "Helvetica"},
    {"name": "Marketing Maven", "slug": "marketing-maven", "accent": "#ec4899", "font": "Helvetica"},
    {"name": "VP Level", "slug": "vp-level", "accent": "#991b1b", "font": "Helvetica-Bold"},
    {"name": "Gradient Modern", "slug": "gradient-modern", "accent": "#8b5cf6", "font": "Helvetica"},
    {"name": "Banking Professional", "slug": "banking-professional", "accent": "#065f46", "font": "Helvetica"},
    {"name": "Clinical Researcher", "slug": "clinical-researcher", "accent": "#0369a1", "font": "Helvetica"},
    {"name": "Cybersecurity Pro", "slug": "cybersecurity-pro", "accent": "#dc2626", "font": "Courier-Bold"},
    {"name": "Startup Hustle", "slug": "startup-hustle", "accent": "#f59e0b", "font": "Helvetica"},
    {"name": "Innovative Thinker", "slug": "innovative-thinker", "accent": "#a855f7", "font": "Helvetica"},
    {"name": "Board Member", "slug": "board-member", "accent": "#1e3a8a", "font": "Helvetica-Bold"},
    {"name": "Dark Mode Pro", "slug": "dark-mode-pro", "accent": "#3b82f6", "font": "Helvetica-Bold"},
    {"name": "Academic Scholar", "slug": "academic-scholar", "accent": "#92400e", "font": "Times-Roman"},
    {"name": "Content Creator", "slug": "content-creator", "accent": "#db2777", "font": "Helvetica"},
    {"name": "Creative Bold", "slug": "creative-bold", "accent": "#ea580c", "font": "Helvetica-Bold"},
    {"name": "Designer Portfolio", "slug": "designer-portfolio", "accent": "#c026d3", "font": "Helvetica"},
    {"name": "Artistic Flair", "slug": "artistic-flair", "accent": "#e11d48", "font": "Helvetica-Bold"},
]

def create_pdf_preview(template, output_path):
    """Create a single PDF preview for a template"""
    buffer = BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    accent_color = HexColor(template["accent"])
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.black,
        spaceAfter=6,
        fontName=template["font"]
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=accent_color,
        spaceAfter=12,
        fontName=template["font"]
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=accent_color,
        spaceAfter=6,
        spaceBefore=12,
        fontName=template["font"],
        borderWidth=2,
        borderColor=accent_color,
        borderPadding=4
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName=template["font"].replace("-Bold", "")
    )
    
    # Build content
    story = []
    
    # Header
    story.append(Paragraph(SAMPLE_DATA["full_name"], title_style))
    story.append(Paragraph(SAMPLE_DATA["title"], subtitle_style))
    story.append(Paragraph(
        f"{SAMPLE_DATA['email']} | {SAMPLE_DATA['phone']} | {SAMPLE_DATA['location']}", 
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    story.append(Paragraph(SAMPLE_DATA["summary"], body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Experience
    story.append(Paragraph("EXPERIENCE", heading_style))
    for exp in SAMPLE_DATA["experience"]:
        story.append(Paragraph(f"<b>{exp['title']}</b> - {exp['company']}", body_style))
        story.append(Paragraph(f"<i>{exp['duration']}</i>", body_style))
        story.append(Paragraph(exp['description'], body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Education
    story.append(Paragraph("EDUCATION", heading_style))
    for edu in SAMPLE_DATA["education"]:
        story.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['school']}", body_style))
        story.append(Paragraph(edu['year'], body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Skills
    story.append(Paragraph("SKILLS", heading_style))
    story.append(Paragraph(" • ".join(SAMPLE_DATA["skills"]), body_style))
    
    # Build PDF
    doc.build(story)
    
    # Save to file
    with open(output_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    return output_path

def main():
    # Create output directory
    output_dir = Path(__file__).parent.parent / "public" / "templates" / "previews"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating PDF previews in {output_dir}")
    
    for template in TEMPLATES:
        try:
            output_path = output_dir / f"{template['slug']}.pdf"
            create_pdf_preview(template, output_path)
            print(f"✓ Generated {template['name']} -> {output_path.name}")
        except Exception as e:
            print(f"✗ Failed to generate {template['name']}: {e}")
    
    print(f"\n✅ Generated {len(TEMPLATES)} PDF previews")

if __name__ == "__main__":
    main()
