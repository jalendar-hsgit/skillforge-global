"""
Comprehensive Resume Template Seeder
Seeds 30+ professional resume templates with beautiful designs
"""
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.core.db import SessionLocal
from app.modelsx.resume import ResumeTemplate
from datetime import datetime

def seed_comprehensive_templates():
    db = SessionLocal()
    
    try:
        # Clear existing templates
        db.query(ResumeTemplate).delete()
        db.commit()
        
        templates = [
            # === MODERN CATEGORY (Clean, minimalist, professional) ===
            {
                "name": "Modern Professional",
                "description": "Clean and minimal design with center-aligned header. Perfect for beginners and all industries.",
                "category": "Modern",
                "thumbnail_url": "https://via.placeholder.com/400x550/4F46E5/ffffff?text=Modern+Pro",
                "config": {
                    "layout": "single-column",
                    "font_family": "Roboto",
                    "accent_color": "#4F46E5",
                    "picture_style": "circle",
                    "show_icons": True,
                    "text_color": "#000000",
                    "heading_color": "#4F46E5",
                    "alignment": "center",  # Center-aligned for beginners
                },
                "is_ats_friendly": True,
                "popularity": 100,
            },
            {
                "name": "Minimalist Blue",
                "description": "Ultra-clean single-column layout with subtle blue accents. ATS-friendly and beginner-friendly.",
                "category": "Modern",
                "thumbnail_url": "https://via.placeholder.com/400x550/2563EB/ffffff?text=Minimalist",
                "config": {
                    "layout": "single-column",
                    "font_family": "Inter",
                    "accent_color": "#2563EB",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 95,
            },
            {
                "name": "Contemporary Edge",
                "description": "Modern design with bold headings and clean lines. Great for tech and creative roles.",
                "category": "Modern",
                "thumbnail_url": "https://via.placeholder.com/400x550/06B6D4/ffffff?text=Contemporary",
                "config": {
                    "layout": "single-column",
                    "font_family": "Poppins",
                    "accent_color": "#06B6D4",
                    "picture_style": "rounded",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 88,
            },
            {
                "name": "Simple Elegance",
                "description": "Elegant and straightforward. Perfect for entry-level positions.",
                "category": "Modern",
                "thumbnail_url": "https://via.placeholder.com/400x550/10B981/ffffff?text=Simple+Elegance",
                "config": {
                    "layout": "single-column",
                    "font_family": "Open Sans",
                    "accent_color": "#10B981",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 82,
            },
            {
                "name": "Tech Forward",
                "description": "Modern tech-focused design with geometric elements.",
                "category": "Modern",
                "thumbnail_url": "https://via.placeholder.com/400x550/8B5CF6/ffffff?text=Tech+Forward",
                "config": {
                    "layout": "two-column",
                    "font_family": "Montserrat",
                    "accent_color": "#8B5CF6",
                    "picture_style": "square",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 76,
            },

            # === CLASSIC CATEGORY (Traditional, timeless, professional) ===
            {
                "name": "Executive Classic",
                "description": "Timeless serif design for senior positions. Center-aligned header for traditional look.",
                "category": "Classic",
                "thumbnail_url": "https://via.placeholder.com/400x550/1F2937/ffffff?text=Executive",
                "config": {
                    "layout": "single-column",
                    "font_family": "Times New Roman",
                    "accent_color": "#1F2937",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 90,
            },
            {
                "name": "Traditional Professional",
                "description": "Conservative design ideal for law, finance, and government sectors.",
                "category": "Classic",
                "thumbnail_url": "https://via.placeholder.com/400x550/374151/ffffff?text=Traditional",
                "config": {
                    "layout": "single-column",
                    "font_family": "Georgia",
                    "accent_color": "#374151",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 85,
            },
            {
                "name": "Corporate Standard",
                "description": "Standard corporate format accepted everywhere.",
                "category": "Classic",
                "thumbnail_url": "https://via.placeholder.com/400x550/475569/ffffff?text=Corporate",
                "config": {
                    "layout": "single-column",
                    "font_family": "Calibri",
                    "accent_color": "#475569",
                    "picture_style": "circle",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 80,
            },
            {
                "name": "Business Formal",
                "description": "Formal business resume with professional typography.",
                "category": "Classic",
                "thumbnail_url": "https://via.placeholder.com/400x550/334155/ffffff?text=Business+Formal",
                "config": {
                    "layout": "single-column",
                    "font_family": "Merriweather",
                    "accent_color": "#334155",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 72,
            },

            # === CREATIVE CATEGORY (Bold, artistic, unique) ===
            {
                "name": "Creative Designer",
                "description": "Bold and artistic design for creatives. Stand out with unique layouts.",
                "category": "Creative",
                "thumbnail_url": "https://via.placeholder.com/400x550/EC4899/ffffff?text=Creative",
                "config": {
                    "layout": "two-column",
                    "font_family": "Playfair Display",
                    "accent_color": "#EC4899",
                    "picture_style": "circle",
                    "show_icons": True,
                    "background_type": "gradient",
                    "alignment": "left",
                },
                "is_ats_friendly": False,
                "popularity": 78,
            },
            {
                "name": "Artistic Vision",
                "description": "Unique layout for designers and artists.",
                "category": "Creative",
                "thumbnail_url": "https://via.placeholder.com/400x550/F59E0B/ffffff?text=Artistic",
                "config": {
                    "layout": "sidebar",
                    "font_family": "Lato",
                    "accent_color": "#F59E0B",
                    "picture_style": "rounded",
                    "show_icons": True,
                    "background_type": "pattern",
                    "alignment": "left",
                },
                "is_ats_friendly": False,
                "popularity": 70,
            },
            {
                "name": "Bold Statement",
                "description": "Make a statement with vibrant colors and modern design.",
                "category": "Creative",
                "thumbnail_url": "https://via.placeholder.com/400x550/EF4444/ffffff?text=Bold",
                "config": {
                    "layout": "two-column",
                    "font_family": "Raleway",
                    "accent_color": "#EF4444",
                    "picture_style": "square",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": False,
                "popularity": 65,
            },
            {
                "name": "Portfolio Pro",
                "description": "Perfect for showcasing creative work and projects.",
                "category": "Creative",
                "thumbnail_url": "https://via.placeholder.com/400x550/7C3AED/ffffff?text=Portfolio",
                "config": {
                    "layout": "sidebar",
                    "font_family": "Oswald",
                    "accent_color": "#7C3AED",
                    "picture_style": "rounded",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": False,
                "popularity": 68,
            },

            # === TECH CATEGORY (Developer-focused, clean code aesthetic) ===
            {
                "name": "Developer Pro",
                "description": "Clean design for software developers with emphasis on technical skills.",
                "category": "Tech",
                "thumbnail_url": "https://via.placeholder.com/400x550/0EA5E9/ffffff?text=Developer",
                "config": {
                    "layout": "two-column",
                    "font_family": "Source Code Pro",
                    "accent_color": "#0EA5E9",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 92,
            },
            {
                "name": "Software Engineer",
                "description": "Technical resume optimized for engineering positions.",
                "category": "Tech",
                "thumbnail_url": "https://via.placeholder.com/400x550/3B82F6/ffffff?text=SWE",
                "config": {
                    "layout": "single-column",
                    "font_family": "Fira Code",
                    "accent_color": "#3B82F6",
                    "picture_style": "rounded",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 88,
            },
            {
                "name": "Full Stack",
                "description": "Two-column layout perfect for full-stack developers.",
                "category": "Tech",
                "thumbnail_url": "https://via.placeholder.com/400x550/14B8A6/ffffff?text=Full+Stack",
                "config": {
                    "layout": "two-column",
                    "font_family": "Roboto Mono",
                    "accent_color": "#14B8A6",
                    "picture_style": "square",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 84,
            },
            {
                "name": "Data Scientist",
                "description": "Analytical layout for data science professionals.",
                "category": "Tech",
                "thumbnail_url": "https://via.placeholder.com/400x550/6366F1/ffffff?text=Data+Science",
                "config": {
                    "layout": "single-column",
                    "font_family": "Inter",
                    "accent_color": "#6366F1",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 86,
            },

            # === EXECUTIVE CATEGORY (Leadership roles, senior positions) ===
            {
                "name": "C-Level Executive",
                "description": "Premium design for C-suite and executive positions.",
                "category": "Executive",
                "thumbnail_url": "https://via.placeholder.com/400x550/0F172A/ffffff?text=C-Level",
                "config": {
                    "layout": "single-column",
                    "font_family": "Crimson Text",
                    "accent_color": "#0F172A",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 75,
            },
            {
                "name": "Senior Manager",
                "description": "Professional design for senior management roles.",
                "category": "Executive",
                "thumbnail_url": "https://via.placeholder.com/400x550/1E293B/ffffff?text=Manager",
                "config": {
                    "layout": "single-column",
                    "font_family": "Garamond",
                    "accent_color": "#1E293B",
                    "picture_style": "circle",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 70,
            },
            {
                "name": "Director Level",
                "description": "Sophisticated layout for director-level positions.",
                "category": "Executive",
                "thumbnail_url": "https://via.placeholder.com/400x550/334155/ffffff?text=Director",
                "config": {
                    "layout": "single-column",
                    "font_family": "Baskerville",
                    "accent_color": "#334155",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 68,
            },

            # === MEDICAL/HEALTHCARE ===
            {
                "name": "Healthcare Professional",
                "description": "Clean professional design for medical and healthcare workers.",
                "category": "Medical",
                "thumbnail_url": "https://via.placeholder.com/400x550/0891B2/ffffff?text=Healthcare",
                "config": {
                    "layout": "single-column",
                    "font_family": "Arial",
                    "accent_color": "#0891B2",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 72,
            },
            {
                "name": "Medical Doctor",
                "description": "Professional CV format for physicians and doctors.",
                "category": "Medical",
                "thumbnail_url": "https://via.placeholder.com/400x550/059669/ffffff?text=Doctor",
                "config": {
                    "layout": "single-column",
                    "font_family": "Times New Roman",
                    "accent_color": "#059669",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 70,
            },
            {
                "name": "Nurse Practitioner",
                "description": "Clear and organized layout for nursing professionals.",
                "category": "Medical",
                "thumbnail_url": "https://via.placeholder.com/400x550/0D9488/ffffff?text=Nurse",
                "config": {
                    "layout": "single-column",
                    "font_family": "Verdana",
                    "accent_color": "#0D9488",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 68,
            },

            # === ACADEMIC ===
            {
                "name": "Academic CV",
                "description": "Comprehensive CV format for academia and research.",
                "category": "Academic",
                "thumbnail_url": "https://via.placeholder.com/400x550/7E22CE/ffffff?text=Academic",
                "config": {
                    "layout": "single-column",
                    "font_family": "Georgia",
                    "accent_color": "#7E22CE",
                    "picture_style": "none",
                    "show_icons": False,
                    "page_margins": {"top": 25, "bottom": 25, "left": 30, "right": 30},
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 65,
            },
            {
                "name": "Research Scholar",
                "description": "Detailed format for researchers and PhD candidates.",
                "category": "Academic",
                "thumbnail_url": "https://via.placeholder.com/400x550/9333EA/ffffff?text=Research",
                "config": {
                    "layout": "single-column",
                    "font_family": "Palatino",
                    "accent_color": "#9333EA",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 62,
            },

            # === SALES & MARKETING ===
            {
                "name": "Sales Executive",
                "description": "Dynamic design for sales professionals with impact metrics focus.",
                "category": "Sales",
                "thumbnail_url": "https://via.placeholder.com/400x550/DC2626/ffffff?text=Sales",
                "config": {
                    "layout": "two-column",
                    "font_family": "Helvetica",
                    "accent_color": "#DC2626",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 74,
            },
            {
                "name": "Marketing Manager",
                "description": "Creative yet professional design for marketing roles.",
                "category": "Marketing",
                "thumbnail_url": "https://via.placeholder.com/400x550/DB2777/ffffff?text=Marketing",
                "config": {
                    "layout": "two-column",
                    "font_family": "Nunito",
                    "accent_color": "#DB2777",
                    "picture_style": "rounded",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 76,
            },
            {
                "name": "Digital Marketer",
                "description": "Modern layout for digital marketing professionals.",
                "category": "Marketing",
                "thumbnail_url": "https://via.placeholder.com/400x550/F97316/ffffff?text=Digital",
                "config": {
                    "layout": "sidebar",
                    "font_family": "Quicksand",
                    "accent_color": "#F97316",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "left",
                },
                "is_ats_friendly": True,
                "popularity": 72,
            },

            # === LEGAL ===
            {
                "name": "Legal Professional",
                "description": "Conservative and formal design for legal sector.",
                "category": "Legal",
                "thumbnail_url": "https://via.placeholder.com/400x550/1E40AF/ffffff?text=Legal",
                "config": {
                    "layout": "single-column",
                    "font_family": "Times New Roman",
                    "accent_color": "#1E40AF",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 66,
            },
            {
                "name": "Attorney",
                "description": "Traditional CV format for attorneys and lawyers.",
                "category": "Legal",
                "thumbnail_url": "https://via.placeholder.com/400x550/1E3A8A/ffffff?text=Attorney",
                "config": {
                    "layout": "single-column",
                    "font_family": "Garamond",
                    "accent_color": "#1E3A8A",
                    "picture_style": "none",
                    "show_icons": False,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 64,
            },

            # === BEGINNER-FRIENDLY (Simple, easy to fill) ===
            {
                "name": "First Job",
                "description": "Simple and clean design perfect for your first resume. Center-aligned.",
                "category": "Beginner",
                "thumbnail_url": "https://via.placeholder.com/400x550/22C55E/ffffff?text=First+Job",
                "config": {
                    "layout": "single-column",
                    "font_family": "Arial",
                    "accent_color": "#22C55E",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 95,
            },
            {
                "name": "Student Resume",
                "description": "Perfect template for students and recent graduates. Easy to use.",
                "category": "Beginner",
                "thumbnail_url": "https://via.placeholder.com/400x550/3B82F6/ffffff?text=Student",
                "config": {
                    "layout": "single-column",
                    "font_family": "Calibri",
                    "accent_color": "#3B82F6",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 90,
            },
            {
                "name": "Entry Level",
                "description": "Straightforward layout for entry-level positions.",
                "category": "Beginner",
                "thumbnail_url": "https://via.placeholder.com/400x550/8B5CF6/ffffff?text=Entry",
                "config": {
                    "layout": "single-column",
                    "font_family": "Helvetica",
                    "accent_color": "#8B5CF6",
                    "picture_style": "circle",
                    "show_icons": True,
                    "alignment": "center",
                },
                "is_ats_friendly": True,
                "popularity": 88,
            },
        ]
        
        # Insert all templates
        for idx, template_data in enumerate(templates, start=1):
            template = ResumeTemplate(
                id=idx,
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                thumbnail_url=template_data["thumbnail_url"],
                config=template_data["config"],
                is_ats_friendly=template_data["is_ats_friendly"],
                popularity=template_data["popularity"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(template)
        
        db.commit()
        print(f"✓ Successfully seeded {len(templates)} resume templates!")
        print("\nCategories:")
        categories = {}
        for t in templates:
            cat = t["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items()):
            print(f"  - {cat}: {count} templates")
        
    except Exception as e:
        print(f"Error seeding templates: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding comprehensive resume templates...")
    seed_comprehensive_templates()
