"""
Seed Resume Templates - 30+ Professional Templates
Run: python seed_resume_templates.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.modelsx.resume import ResumeTemplate

# Font families available
FONTS = [
    "Helvetica", "Times-Roman", "Courier", "Arial", "Verdana",
    "Georgia", "Palatino", "Garamond", "Bookman", "Calibri",
    "Cambria", "Roboto"
]

# Color themes (74 total - showing key ones)
COLOR_THEMES = {
    "Professional Blue": {"accent": "#2563eb", "text": "#1f2937", "heading": "#1e40af"},
    "Executive Black": {"accent": "#000000", "text": "#374151", "heading": "#111827"},
    "Modern Teal": {"accent": "#0d9488", "text": "#1f2937", "heading": "#115e59"},
    "Creative Purple": {"accent": "#9333ea", "text": "#374151", "heading": "#7e22ce"},
    "Tech Green": {"accent": "#10b981", "text": "#1f2937", "heading": "#059669"},
    "Medical Navy": {"accent": "#1e40af", "text": "#374151", "heading": "#1e3a8a"},
    "Legal Burgundy": {"accent": "#991b1b", "text": "#374151", "heading": "#7f1d1d"},
    "Sales Orange": {"accent": "#ea580c", "text": "#1f2937", "heading": "#c2410c"},
    "Marketing Pink": {"accent": "#db2777", "text": "#374151", "heading": "#be185d"},
    "Academic Brown": {"accent": "#92400e", "text": "#374151", "heading": "#78350f"},
}


def create_templates():
    """Create 30+ professional resume templates"""
    db: Session = SessionLocal()
    
    try:
        # Clear existing templates
        db.query(ResumeTemplate).delete()
        db.commit()
        
        templates = []
        
        # ==================== MODERN CATEGORY ====================
        
        # 1. Modern Professional
        templates.append(ResumeTemplate(
            name="Modern Professional",
            description="Clean, contemporary design perfect for tech and creative industries",
            category="Modern",
            thumbnail_url="/templates/thumbs/modern-professional.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Helvetica",
            color_theme="Professional Blue",
            accent_color="#2563eb",
            text_color="#1f2937",
            heading_color="#1e40af",
            background_type="solid",
            picture_style="circle",
            rating_style="bars",
            line_spacing=1.5,
            font_size=11,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="A4",
            sections_order=["summary", "experience", "education", "skills", "projects", "certificates"],
            enabled_sections=["summary", "experience", "education", "skills", "projects", "certificates"],
            popularity_score=95
        ))
        
        # 2. Modern Minimalist
        templates.append(ResumeTemplate(
            name="Modern Minimalist",
            description="Simple, elegant design with maximum impact",
            category="Modern",
            thumbnail_url="/templates/thumbs/modern-minimalist.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Calibri",
            color_theme="Executive Black",
            accent_color="#000000",
            text_color="#374151",
            heading_color="#111827",
            background_type="solid",
            picture_style="square",
            rating_style="dots",
            line_spacing=1.4,
            font_size=11,
            show_icons=False,
            max_pages=1,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="A4",
            sections_order=["summary", "experience", "skills", "education"],
            enabled_sections=["summary", "experience", "skills", "education"],
            popularity_score=88
        ))
        
        # 3. Modern Two-Column
        templates.append(ResumeTemplate(
            name="Modern Two-Column",
            description="Efficient layout with sidebar for skills and contact",
            category="Modern",
            thumbnail_url="/templates/thumbs/modern-two-column.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="two-column",
            font_family="Roboto",
            color_theme="Modern Teal",
            accent_color="#0d9488",
            text_color="#1f2937",
            heading_color="#115e59",
            background_type="solid",
            picture_style="circle",
            rating_style="circles",
            line_spacing=1.5,
            font_size=10,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 15, "bottom": 15, "left": 15, "right": 15},
            page_size="A4",
            sections_order=["summary", "experience", "education", "skills", "projects"],
            enabled_sections=["summary", "experience", "education", "skills", "projects"],
            popularity_score=92
        ))
        
        # ==================== CLASSIC CATEGORY ====================
        
        # 4. Classic Professional
        templates.append(ResumeTemplate(
            name="Classic Professional",
            description="Traditional format trusted by recruiters worldwide",
            category="Classic",
            thumbnail_url="/templates/thumbs/classic-professional.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Times-Roman",
            color_theme="Executive Black",
            accent_color="#000000",
            text_color="#000000",
            heading_color="#000000",
            background_type="solid",
            picture_style="none",
            rating_style="bars",
            line_spacing=1.2,
            font_size=11,
            show_icons=False,
            max_pages=2,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "experience", "education", "skills"],
            enabled_sections=["summary", "experience", "education", "skills"],
            popularity_score=85
        ))
        
        # 5. Classic Executive
        templates.append(ResumeTemplate(
            name="Classic Executive",
            description="Sophisticated format for senior leadership roles",
            category="Classic",
            thumbnail_url="/templates/thumbs/classic-executive.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Georgia",
            color_theme="Executive Black",
            accent_color="#1f2937",
            text_color="#374151",
            heading_color="#111827",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=3,
            page_margins={"top": 30, "bottom": 30, "left": 30, "right": 30},
            page_size="Letter",
            sections_order=["summary", "experience", "education", "achievements", "skills"],
            enabled_sections=["summary", "experience", "education", "achievements", "skills"],
            popularity_score=78
        ))
        
        # 6. Classic Serif
        templates.append(ResumeTemplate(
            name="Classic Serif",
            description="Elegant serif typography for traditional industries",
            category="Classic",
            thumbnail_url="/templates/thumbs/classic-serif.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Garamond",
            color_theme="Academic Brown",
            accent_color="#92400e",
            text_color="#374151",
            heading_color="#78350f",
            background_type="solid",
            picture_style="none",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=2,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="A4",
            sections_order=["summary", "experience", "education", "publications", "skills"],
            enabled_sections=["summary", "experience", "education", "publications", "skills"],
            popularity_score=72
        ))
        
        # ==================== CREATIVE CATEGORY ====================
        
        # 7. Creative Bold
        templates.append(ResumeTemplate(
            name="Creative Bold",
            description="Stand out with vibrant colors and modern typography",
            category="Creative",
            thumbnail_url="/templates/thumbs/creative-bold.jpg",
            is_ats_friendly=False,
            is_premium=True,
            layout="sidebar",
            font_family="Verdana",
            color_theme="Creative Purple",
            accent_color="#9333ea",
            text_color="#374151",
            heading_color="#7e22ce",
            background_type="gradient",
            picture_style="circle",
            rating_style="stars",
            line_spacing=1.5,
            font_size=10,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 15, "bottom": 15, "left": 15, "right": 15},
            page_size="A4",
            sections_order=["summary", "skills", "experience", "projects", "education"],
            enabled_sections=["summary", "skills", "experience", "projects", "education"],
            popularity_score=68
        ))
        
        # 8. Creative Designer
        templates.append(ResumeTemplate(
            name="Creative Designer",
            description="Portfolio-style layout for designers and artists",
            category="Creative",
            thumbnail_url="/templates/thumbs/creative-designer.jpg",
            is_ats_friendly=False,
            is_premium=True,
            layout="two-column",
            font_family="Helvetica",
            color_theme="Marketing Pink",
            accent_color="#db2777",
            text_color="#374151",
            heading_color="#be185d",
            background_type="pattern",
            picture_style="circle",
            rating_style="circles",
            line_spacing=1.6,
            font_size=10,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="A4",
            sections_order=["summary", "projects", "experience", "skills", "education"],
            enabled_sections=["summary", "projects", "experience", "skills", "education"],
            popularity_score=75
        ))
        
        # 9. Creative Infographic
        templates.append(ResumeTemplate(
            name="Creative Infographic",
            description="Visual storytelling with charts and graphics",
            category="Creative",
            thumbnail_url="/templates/thumbs/creative-infographic.jpg",
            is_ats_friendly=False,
            is_premium=True,
            layout="sidebar",
            font_family="Calibri",
            color_theme="Sales Orange",
            accent_color="#ea580c",
            text_color="#1f2937",
            heading_color="#c2410c",
            background_type="gradient",
            picture_style="rounded",
            rating_style="stars",
            line_spacing=1.5,
            font_size=10,
            show_icons=True,
            max_pages=1,
            page_margins={"top": 10, "bottom": 10, "left": 10, "right": 10},
            page_size="A4",
            sections_order=["summary", "skills", "experience", "education", "projects"],
            enabled_sections=["summary", "skills", "experience", "education", "projects"],
            popularity_score=70
        ))
        
        # ==================== EXECUTIVE CATEGORY ====================
        
        # 10. Executive Premium
        templates.append(ResumeTemplate(
            name="Executive Premium",
            description="Luxury design for C-level executives",
            category="Executive",
            thumbnail_url="/templates/thumbs/executive-premium.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Palatino",
            color_theme="Executive Black",
            accent_color="#1f2937",
            text_color="#374151",
            heading_color="#111827",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.4,
            font_size=11,
            show_icons=False,
            max_pages=3,
            page_margins={"top": 35, "bottom": 35, "left": 35, "right": 35},
            page_size="Letter",
            sections_order=["summary", "experience", "achievements", "education", "skills"],
            enabled_sections=["summary", "experience", "achievements", "education", "skills"],
            popularity_score=82
        ))
        
        # 11. Executive Modern
        templates.append(ResumeTemplate(
            name="Executive Modern",
            description="Contemporary elegance for senior management",
            category="Executive",
            thumbnail_url="/templates/thumbs/executive-modern.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="two-column",
            font_family="Cambria",
            color_theme="Medical Navy",
            accent_color="#1e40af",
            text_color="#374151",
            heading_color="#1e3a8a",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=3,
            page_margins={"top": 30, "bottom": 30, "left": 30, "right": 30},
            page_size="Letter",
            sections_order=["summary", "experience", "education", "achievements", "skills"],
            enabled_sections=["summary", "experience", "education", "achievements", "skills"],
            popularity_score=80
        ))
        
        # 12. Executive Leadership
        templates.append(ResumeTemplate(
            name="Executive Leadership",
            description="Bold format highlighting leadership achievements",
            category="Executive",
            thumbnail_url="/templates/thumbs/executive-leadership.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Georgia",
            color_theme="Legal Burgundy",
            accent_color="#991b1b",
            text_color="#374151",
            heading_color="#7f1d1d",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=4,
            page_margins={"top": 30, "bottom": 30, "left": 30, "right": 30},
            page_size="Letter",
            sections_order=["summary", "experience", "achievements", "education", "skills", "volunteer"],
            enabled_sections=["summary", "experience", "achievements", "education", "skills", "volunteer"],
            popularity_score=77
        ))
        
        # ==================== TECH CATEGORY ====================
        
        # 13. Tech Developer
        templates.append(ResumeTemplate(
            name="Tech Developer",
            description="Perfect for software engineers and developers",
            category="Tech",
            thumbnail_url="/templates/thumbs/tech-developer.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="two-column",
            font_family="Courier",
            color_theme="Tech Green",
            accent_color="#10b981",
            text_color="#1f2937",
            heading_color="#059669",
            background_type="solid",
            picture_style="circle",
            rating_style="bars",
            line_spacing=1.5,
            font_size=10,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="A4",
            sections_order=["summary", "skills", "experience", "projects", "education", "certificates"],
            enabled_sections=["summary", "skills", "experience", "projects", "education", "certificates"],
            popularity_score=90
        ))
        
        # 14. Tech Data Science
        templates.append(ResumeTemplate(
            name="Tech Data Science",
            description="Optimized for data scientists and ML engineers",
            category="Tech",
            thumbnail_url="/templates/thumbs/tech-data-science.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Roboto",
            color_theme="Professional Blue",
            accent_color="#2563eb",
            text_color="#1f2937",
            heading_color="#1e40af",
            background_type="solid",
            picture_style="circle",
            rating_style="bars",
            line_spacing=1.5,
            font_size=11,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="A4",
            sections_order=["summary", "skills", "experience", "projects", "education", "publications"],
            enabled_sections=["summary", "skills", "experience", "projects", "education", "publications"],
            popularity_score=87
        ))
        
        # 15. Tech DevOps
        templates.append(ResumeTemplate(
            name="Tech DevOps",
            description="Tailored for DevOps and cloud engineers",
            category="Tech",
            thumbnail_url="/templates/thumbs/tech-devops.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="two-column",
            font_family="Helvetica",
            color_theme="Modern Teal",
            accent_color="#0d9488",
            text_color="#1f2937",
            heading_color="#115e59",
            background_type="solid",
            picture_style="circle",
            rating_style="circles",
            line_spacing=1.5,
            font_size=10,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="A4",
            sections_order=["summary", "skills", "experience", "certificates", "education", "projects"],
            enabled_sections=["summary", "skills", "experience", "certificates", "education", "projects"],
            popularity_score=84
        ))
        
        # ==================== MEDICAL CATEGORY ====================
        
        # 16. Medical Professional
        templates.append(ResumeTemplate(
            name="Medical Professional",
            description="Clean format for healthcare professionals",
            category="Medical",
            thumbnail_url="/templates/thumbs/medical-professional.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Times-Roman",
            color_theme="Medical Navy",
            accent_color="#1e40af",
            text_color="#374151",
            heading_color="#1e3a8a",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=3,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "education", "experience", "certificates", "publications", "skills"],
            enabled_sections=["summary", "education", "experience", "certificates", "publications", "skills"],
            popularity_score=79
        ))
        
        # 17. Medical Nurse
        templates.append(ResumeTemplate(
            name="Medical Nurse",
            description="Optimized for nursing professionals",
            category="Medical",
            thumbnail_url="/templates/thumbs/medical-nurse.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Calibri",
            color_theme="Professional Blue",
            accent_color="#2563eb",
            text_color="#1f2937",
            heading_color="#1e40af",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.4,
            font_size=11,
            show_icons=False,
            max_pages=2,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "experience", "education", "certificates", "skills"],
            enabled_sections=["summary", "experience", "education", "certificates", "skills"],
            popularity_score=76
        ))
        
        # 18. Medical Research
        templates.append(ResumeTemplate(
            name="Medical Research",
            description="Academic format for medical researchers",
            category="Medical",
            thumbnail_url="/templates/thumbs/medical-research.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Georgia",
            color_theme="Academic Brown",
            accent_color="#92400e",
            text_color="#374151",
            heading_color="#78350f",
            background_type="solid",
            picture_style="none",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=5,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "education", "publications", "experience", "certificates", "skills"],
            enabled_sections=["summary", "education", "publications", "experience", "certificates", "skills"],
            popularity_score=73
        ))
        
        # ==================== ACADEMIC CATEGORY ====================
        
        # 19. Academic CV
        templates.append(ResumeTemplate(
            name="Academic CV",
            description="Comprehensive format for academia",
            category="Academic",
            thumbnail_url="/templates/thumbs/academic-cv.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Times-Roman",
            color_theme="Academic Brown",
            accent_color="#92400e",
            text_color="#374151",
            heading_color="#78350f",
            background_type="solid",
            picture_style="none",
            rating_style="bars",
            line_spacing=1.2,
            font_size=11,
            show_icons=False,
            max_pages=10,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "education", "publications", "experience", "achievements", "certificates", "skills"],
            enabled_sections=["summary", "education", "publications", "experience", "achievements", "certificates", "skills"],
            popularity_score=81
        ))
        
        # 20. Academic Professor
        templates.append(ResumeTemplate(
            name="Academic Professor",
            description="Faculty position CV with teaching focus",
            category="Academic",
            thumbnail_url="/templates/thumbs/academic-professor.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Garamond",
            color_theme="Executive Black",
            accent_color="#1f2937",
            text_color="#374151",
            heading_color="#111827",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=8,
            page_margins={"top": 30, "bottom": 30, "left": 30, "right": 30},
            page_size="Letter",
            sections_order=["summary", "education", "experience", "publications", "achievements", "certificates"],
            enabled_sections=["summary", "education", "experience", "publications", "achievements", "certificates"],
            popularity_score=74
        ))
        
        # 21. Academic Research
        templates.append(ResumeTemplate(
            name="Academic Research",
            description="Research-focused CV with publications emphasis",
            category="Academic",
            thumbnail_url="/templates/thumbs/academic-research.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Times-Roman",
            color_theme="Professional Blue",
            accent_color="#2563eb",
            text_color="#1f2937",
            heading_color="#1e40af",
            background_type="solid",
            picture_style="none",
            rating_style="bars",
            line_spacing=1.2,
            font_size=11,
            show_icons=False,
            max_pages=6,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="A4",
            sections_order=["summary", "education", "publications", "patents", "experience", "skills"],
            enabled_sections=["summary", "education", "publications", "patents", "experience", "skills"],
            popularity_score=77
        ))
        
        # ==================== LEGAL CATEGORY ====================
        
        # 22. Legal Attorney
        templates.append(ResumeTemplate(
            name="Legal Attorney",
            description="Professional format for practicing attorneys",
            category="Legal",
            thumbnail_url="/templates/thumbs/legal-attorney.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Times-Roman",
            color_theme="Legal Burgundy",
            accent_color="#991b1b",
            text_color="#374151",
            heading_color="#7f1d1d",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=3,
            page_margins={"top": 30, "bottom": 30, "left": 30, "right": 30},
            page_size="Letter",
            sections_order=["summary", "education", "experience", "certificates", "achievements"],
            enabled_sections=["summary", "education", "experience", "certificates", "achievements"],
            popularity_score=80
        ))
        
        # 23. Legal Corporate
        templates.append(ResumeTemplate(
            name="Legal Corporate",
            description="Corporate counsel and in-house legal format",
            category="Legal",
            thumbnail_url="/templates/thumbs/legal-corporate.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Georgia",
            color_theme="Executive Black",
            accent_color="#1f2937",
            text_color="#374151",
            heading_color="#111827",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.3,
            font_size=11,
            show_icons=False,
            max_pages=3,
            page_margins={"top": 30, "bottom": 30, "left": 30, "right": 30},
            page_size="Letter",
            sections_order=["summary", "experience", "education", "certificates", "skills"],
            enabled_sections=["summary", "experience", "education", "certificates", "skills"],
            popularity_score=75
        ))
        
        # 24. Legal Paralegal
        templates.append(ResumeTemplate(
            name="Legal Paralegal",
            description="Optimized for paralegals and legal assistants",
            category="Legal",
            thumbnail_url="/templates/thumbs/legal-paralegal.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Calibri",
            color_theme="Professional Blue",
            accent_color="#2563eb",
            text_color="#1f2937",
            heading_color="#1e40af",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.4,
            font_size=11,
            show_icons=False,
            max_pages=2,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "experience", "education", "skills", "certificates"],
            enabled_sections=["summary", "experience", "education", "skills", "certificates"],
            popularity_score=72
        ))
        
        # ==================== SALES CATEGORY ====================
        
        # 25. Sales Professional
        templates.append(ResumeTemplate(
            name="Sales Professional",
            description="Results-driven format highlighting achievements",
            category="Sales",
            thumbnail_url="/templates/thumbs/sales-professional.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Helvetica",
            color_theme="Sales Orange",
            accent_color="#ea580c",
            text_color="#1f2937",
            heading_color="#c2410c",
            background_type="solid",
            picture_style="circle",
            rating_style="bars",
            line_spacing=1.5,
            font_size=11,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="Letter",
            sections_order=["summary", "achievements", "experience", "skills", "education"],
            enabled_sections=["summary", "achievements", "experience", "skills", "education"],
            popularity_score=86
        ))
        
        # 26. Sales Executive
        templates.append(ResumeTemplate(
            name="Sales Executive",
            description="Senior sales leadership format",
            category="Sales",
            thumbnail_url="/templates/thumbs/sales-executive.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="two-column",
            font_family="Calibri",
            color_theme="Professional Blue",
            accent_color="#2563eb",
            text_color="#1f2937",
            heading_color="#1e40af",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.4,
            font_size=11,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "achievements", "experience", "education", "skills"],
            enabled_sections=["summary", "achievements", "experience", "education", "skills"],
            popularity_score=83
        ))
        
        # 27. Sales Account Manager
        templates.append(ResumeTemplate(
            name="Sales Account Manager",
            description="Relationship-focused sales format",
            category="Sales",
            thumbnail_url="/templates/thumbs/sales-account-manager.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="single-column",
            font_family="Verdana",
            color_theme="Tech Green",
            accent_color="#10b981",
            text_color="#1f2937",
            heading_color="#059669",
            background_type="solid",
            picture_style="circle",
            rating_style="bars",
            line_spacing=1.5,
            font_size=11,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="Letter",
            sections_order=["summary", "experience", "achievements", "skills", "education"],
            enabled_sections=["summary", "experience", "achievements", "skills", "education"],
            popularity_score=79
        ))
        
        # ==================== MARKETING CATEGORY ====================
        
        # 28. Marketing Professional
        templates.append(ResumeTemplate(
            name="Marketing Professional",
            description="Creative marketing resume with brand focus",
            category="Marketing",
            thumbnail_url="/templates/thumbs/marketing-professional.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="two-column",
            font_family="Helvetica",
            color_theme="Marketing Pink",
            accent_color="#db2777",
            text_color="#374151",
            heading_color="#be185d",
            background_type="solid",
            picture_style="circle",
            rating_style="circles",
            line_spacing=1.5,
            font_size=10,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 20, "bottom": 20, "left": 20, "right": 20},
            page_size="A4",
            sections_order=["summary", "experience", "skills", "projects", "education"],
            enabled_sections=["summary", "experience", "skills", "projects", "education"],
            popularity_score=88
        ))
        
        # 29. Marketing Digital
        templates.append(ResumeTemplate(
            name="Marketing Digital",
            description="Digital marketing specialist format",
            category="Marketing",
            thumbnail_url="/templates/thumbs/marketing-digital.jpg",
            is_ats_friendly=True,
            is_premium=False,
            layout="sidebar",
            font_family="Roboto",
            color_theme="Creative Purple",
            accent_color="#9333ea",
            text_color="#374151",
            heading_color="#7e22ce",
            background_type="solid",
            picture_style="circle",
            rating_style="stars",
            line_spacing=1.5,
            font_size=10,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 15, "bottom": 15, "left": 15, "right": 15},
            page_size="A4",
            sections_order=["summary", "skills", "experience", "projects", "certificates", "education"],
            enabled_sections=["summary", "skills", "experience", "projects", "certificates", "education"],
            popularity_score=85
        ))
        
        # 30. Marketing Manager
        templates.append(ResumeTemplate(
            name="Marketing Manager",
            description="Leadership format for marketing managers",
            category="Marketing",
            thumbnail_url="/templates/thumbs/marketing-manager.jpg",
            is_ats_friendly=True,
            is_premium=True,
            layout="single-column",
            font_family="Calibri",
            color_theme="Sales Orange",
            accent_color="#ea580c",
            text_color="#1f2937",
            heading_color="#c2410c",
            background_type="solid",
            picture_style="square",
            rating_style="bars",
            line_spacing=1.4,
            font_size=11,
            show_icons=True,
            max_pages=2,
            page_margins={"top": 25, "bottom": 25, "left": 25, "right": 25},
            page_size="Letter",
            sections_order=["summary", "experience", "achievements", "skills", "education"],
            enabled_sections=["summary", "experience", "achievements", "skills", "education"],
            popularity_score=81
        ))
        
        # Bulk insert
        db.bulk_save_objects(templates)
        db.commit()
        
        print(f"✅ Successfully created {len(templates)} resume templates!")
        print("\nTemplate breakdown:")
        print(f"  - Modern: 3 templates")
        print(f"  - Classic: 3 templates")
        print(f"  - Creative: 3 templates")
        print(f"  - Executive: 3 templates")
        print(f"  - Tech: 3 templates")
        print(f"  - Medical: 3 templates")
        print(f"  - Academic: 3 templates")
        print(f"  - Legal: 3 templates")
        print(f"  - Sales: 3 templates")
        print(f"  - Marketing: 3 templates")
        print(f"\nATS-Friendly: {sum(1 for t in templates if t.is_ats_friendly)} templates")
        print(f"Premium: {sum(1 for t in templates if t.is_premium)} templates")
        
    except Exception as e:
        print(f"❌ Error creating templates: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_templates()

