"""
Advanced Resume Templates - 20 New Beautiful, ATS-Friendly Templates
Database: Non-destructive insertion (won't drop tables)
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.modelsx.resume import ResumeTemplate

ADVANCED_TEMPLATES = [
    # Minimalist Professional Collection (5)
    {
        "name": "Minimalist Clean",
        "category": "Minimalist",
        "description": "Ultra-clean design with maximum whitespace and readability",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "spacing": "generous",
            "typography": "sans-serif",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Scandinavian Minimal",
        "category": "Minimalist",
        "description": "Nordic design approach with clean lines and balanced spacing",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "style": "nordic",
            "accent": "muted",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Typography Focus",
        "category": "Minimalist",
        "description": "Focuses on perfect typography and hierarchy with minimal colors",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "typography_emphasis": True,
            "colors": 2,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Monochrome Professional",
        "category": "Minimalist",
        "description": "Single-color design with varying opacity for depth",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "colors": "monochrome",
            "contrast": "high",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Elegant Simplicity",
        "category": "Minimalist",
        "description": "Simple yet elegant with sophisticated spacing",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "elegance_level": "high",
            "spacing": "optimal",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    
    # Modern Professional Collection (5)
    {
        "name": "Corporate Executive Plus",
        "category": "Executive",
        "description": "Modern corporate design with accent colors and professional layout",
        "is_ats_friendly": True,
        "config": {
            "layout": "two-column",
            "sidebar": "right",
            "accent_usage": "moderate",
            "section_dividers": True
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Gradient Modern",
        "category": "Modern",
        "description": "Subtle gradient backgrounds with modern typography",
        "is_ats_friendly": False,
        "config": {
            "layout": "single-column",
            "gradients": True,
            "effects": "subtle",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Tech-Forward Design",
        "category": "Tech",
        "description": "Modern design optimized for tech industry roles",
        "is_ats_friendly": True,
        "config": {
            "layout": "two-column",
            "tech_icons": True,
            "accent_color": "tech-blue",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Startup Friendly",
        "category": "Modern",
        "description": "Contemporary design for startup and creative roles",
        "is_ats_friendly": False,
        "config": {
            "layout": "asymmetric",
            "bold_accents": True,
            "modern_spacing": True,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Infographic Style",
        "category": "Creative",
        "description": "Visually rich with icons and graphics for creative roles",
        "is_ats_friendly": False,
        "config": {
            "layout": "multi-column",
            "graphics": True,
            "icons": True,
            "visual_heavy": True
        },
        "popularity": 0,
        "is_active": True
    },
    
    # Industry-Specific Collection (5)
    {
        "name": "Medical Professional",
        "category": "Medical",
        "description": "Designed for healthcare professionals with clinical feel",
        "is_ats_friendly": True,
        "config": {
            "layout": "two-column",
            "color_scheme": "clinical-blue",
            "credentials_highlight": True,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Academic Scholar",
        "category": "Academic",
        "description": "Ideal for academics with emphasis on publications and research",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "academic_format": True,
            "citation_style": "APA",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Legal Practice",
        "category": "Legal",
        "description": "Professional design for attorneys and legal professionals",
        "is_ats_friendly": True,
        "config": {
            "layout": "two-column",
            "formal_tone": True,
            "credentials_prominent": True,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Creative Portfolio",
        "category": "Creative",
        "description": "Showcase-style resume for designers and creative professionals",
        "is_ats_friendly": False,
        "config": {
            "layout": "portfolio-style",
            "visual_showcase": True,
            "color_bold": True,
            "alignment": "center"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Sales Excellence",
        "category": "Sales",
        "description": "Dynamic design with achievement-focused layout for sales professionals",
        "is_ats_friendly": True,
        "config": {
            "layout": "achievement-focused",
            "metrics_prominent": True,
            "bold_typography": True,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    
    # Elegant & Sophisticated Collection (5)
    {
        "name": "Luxury Executive",
        "category": "Executive",
        "description": "High-end design for senior executives with gold accents",
        "is_ats_friendly": False,
        "config": {
            "layout": "centered",
            "premium_colors": True,
            "elegance": "luxury",
            "alignment": "center"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Sophisticated Blue",
        "category": "Executive",
        "description": "Elegant design with sophisticated blue color scheme",
        "is_ats_friendly": True,
        "config": {
            "layout": "two-column",
            "color_scheme": "sophisticated-blue",
            "elegance_level": "high",
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Serif Traditional",
        "category": "Classic",
        "description": "Classic design using serif fonts for traditional industries",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "font_type": "serif",
            "traditional": True,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Modern Serif Hybrid",
        "category": "Modern",
        "description": "Combines modern layout with serif typography for distinction",
        "is_ats_friendly": True,
        "config": {
            "layout": "two-column",
            "font_mix": "serif-sans",
            "modern_traditional_blend": True,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
    {
        "name": "Minimalist Elegant",
        "category": "Minimalist",
        "description": "Elegant minimalism with refined spacing and typography",
        "is_ats_friendly": True,
        "config": {
            "layout": "single-column",
            "minimalism_with_elegance": True,
            "refined": True,
            "alignment": "left"
        },
        "popularity": 0,
        "is_active": True
    },
]

def seed_advanced_templates(db: Session):
    """
    Add advanced templates to database without dropping tables
    Non-destructive: Only inserts new templates, doesn't modify existing
    """
    from app.modelsx.resume import ResumeTemplate
    
    inserted_count = 0
    skipped_count = 0
    
    for template_data in ADVANCED_TEMPLATES:
        # Check if template already exists (prevent duplicates)
        existing = db.query(ResumeTemplate).filter(
            ResumeTemplate.name == template_data["name"]
        ).first()
        
        if existing:
            print(f"⏭️  Skipping '{template_data['name']}' - already exists")
            skipped_count += 1
            continue
        
        # Create new template
        template = ResumeTemplate(
            name=template_data["name"],
            category=template_data["category"],
            description=template_data["description"],
            is_ats_friendly=template_data["is_ats_friendly"],
            config=template_data["config"],
            popularity=template_data["popularity"],
            is_active=template_data["is_active"],
            thumbnail_url=None,  # Can be added later
            created_at=datetime.utcnow()
        )
        
        db.add(template)
        inserted_count += 1
        print(f"✅ Added template: {template_data['name']}")
    
    # Commit all changes
    try:
        db.commit()
        print(f"\n✅ Successfully inserted {inserted_count} new templates")
        print(f"⏭️  Skipped {skipped_count} existing templates")
        return inserted_count, skipped_count
    except Exception as e:
        db.rollback()
        print(f"❌ Error inserting templates: {e}")
        raise

if __name__ == "__main__":
    # For manual seeding
    from app.core.db import SessionLocal
    db = SessionLocal()
    try:
        inserted, skipped = seed_advanced_templates(db)
        print(f"\n📊 Summary: {inserted} inserted, {skipped} skipped")
    finally:
        db.close()
