#!/usr/bin/env python3
"""
Seed 20 advanced resume templates
"""
import sys
import os
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

# Import dependencies
from app.core.db import SessionLocal
from app.modelsx.resume import ResumeTemplate

# Define templates
ADVANCED_TEMPLATES = [
    # Minimalist Collection (5)
    {
        "name": "Minimalist Clean",
        "category": "Minimalist",
        "description": "Ultra-clean design with plenty of whitespace",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 45,
        "config": {
            "font_family": "Inter",
            "accent_color": "#000000",
            "layout": "single-column",
            "show_icons": False
        }
    },
    {
        "name": "Scandinavian Minimal",
        "category": "Minimalist",
        "description": "Nordic-inspired minimalist with soft grays",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 42,
        "config": {
            "font_family": "Helvetica",
            "accent_color": "#404040",
            "layout": "single-column",
            "background_type": "light_gray"
        }
    },
    {
        "name": "Typography Focus",
        "category": "Minimalist",
        "description": "Elegant serif typography-focused design",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 38,
        "config": {
            "font_family": "Garamond",
            "heading_size": 16,
            "line_spacing": 1.5
        }
    },
    {
        "name": "Monochrome Professional",
        "category": "Minimalist",
        "description": "Black and white professional resume",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 41,
        "config": {
            "font_family": "Roboto",
            "accent_color": "#1a1a1a",
            "text_color": "#333333"
        }
    },
    {
        "name": "Elegant Simplicity",
        "category": "Minimalist",
        "description": "Simple yet refined elegant design",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 40,
        "config": {
            "font_family": "Georgia",
            "accent_color": "#2c3e50",
            "line_spacing": 1.4
        }
    },
    # Modern Professional (5)
    {
        "name": "Corporate Executive Plus",
        "category": "Modern",
        "description": "Modern corporate design with accent color",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 55,
        "config": {
            "font_family": "Segoe UI",
            "accent_color": "#0066cc",
            "layout": "two-column"
        }
    },
    {
        "name": "Gradient Modern",
        "category": "Modern",
        "description": "Contemporary gradient header design",
        "is_ats_friendly": False,
        "is_active": True,
        "popularity": 50,
        "config": {
            "font_family": "Inter",
            "accent_color": "#667eea",
            "background_type": "gradient",
            "layout": "sidebar"
        }
    },
    {
        "name": "Tech-Forward Design",
        "category": "Modern",
        "description": "Perfect for tech professionals",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 58,
        "config": {
            "font_family": "Monaco",
            "accent_color": "#00a8e8",
            "show_icons": True
        }
    },
    {
        "name": "Startup Friendly",
        "category": "Modern",
        "description": "Casual yet professional startup style",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 48,
        "config": {
            "font_family": "Open Sans",
            "accent_color": "#ff6b6b",
            "layout": "single-column"
        }
    },
    {
        "name": "Infographic Style",
        "category": "Modern",
        "description": "Visual infographic resume design",
        "is_ats_friendly": False,
        "is_active": True,
        "popularity": 45,
        "config": {
            "font_family": "Montserrat",
            "accent_color": "#9b59b6",
            "show_icons": True,
            "background_type": "light_blue"
        }
    },
    # Industry-Specific (5)
    {
        "name": "Medical Professional",
        "category": "Industry",
        "description": "For healthcare professionals and doctors",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 52,
        "config": {
            "font_family": "Calibri",
            "accent_color": "#0066cc",
            "layout": "single-column"
        }
    },
    {
        "name": "Academic Scholar",
        "category": "Industry",
        "description": "For academics and researchers",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 48,
        "config": {
            "font_family": "Times New Roman",
            "accent_color": "#2c3e50",
            "line_spacing": 1.5
        }
    },
    {
        "name": "Legal Practice",
        "category": "Industry",
        "description": "For lawyers and legal professionals",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 46,
        "config": {
            "font_family": "Arial",
            "accent_color": "#1a1a1a",
            "layout": "single-column"
        }
    },
    {
        "name": "Creative Portfolio",
        "category": "Industry",
        "description": "For designers and creative professionals",
        "is_ats_friendly": False,
        "is_active": True,
        "popularity": 54,
        "config": {
            "font_family": "Montserrat",
            "accent_color": "#e74c3c",
            "background_type": "gradient",
            "show_icons": True
        }
    },
    {
        "name": "Sales Excellence",
        "category": "Industry",
        "description": "For sales and business professionals",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 50,
        "config": {
            "font_family": "Open Sans",
            "accent_color": "#27ae60",
            "layout": "two-column"
        }
    },
    # Elegant & Sophisticated (5)
    {
        "name": "Luxury Executive",
        "category": "Elegant",
        "description": "Premium luxury executive design",
        "is_ats_friendly": False,
        "is_active": True,
        "popularity": 56,
        "config": {
            "font_family": "Garamond",
            "accent_color": "#d4af37",
            "background_type": "cream",
            "line_spacing": 1.6
        }
    },
    {
        "name": "Sophisticated Blue",
        "category": "Elegant",
        "description": "Trust-inspiring sophisticated blue",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 53,
        "config": {
            "font_family": "Verdana",
            "accent_color": "#003d82",
            "layout": "sidebar"
        }
    },
    {
        "name": "Serif Traditional",
        "category": "Elegant",
        "description": "Traditional serif-based elegant resume",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 44,
        "config": {
            "font_family": "Georgia",
            "accent_color": "#5d4e37",
            "line_spacing": 1.5
        }
    },
    {
        "name": "Modern Serif Hybrid",
        "category": "Elegant",
        "description": "Modern meets traditional with serif hybrid",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 49,
        "config": {
            "font_family": "Lora",
            "accent_color": "#6b4423",
            "layout": "two-column"
        }
    },
    {
        "name": "Minimalist Elegant",
        "category": "Elegant",
        "description": "Minimal elegance with refined details",
        "is_ats_friendly": True,
        "is_active": True,
        "popularity": 51,
        "config": {
            "font_family": "Raleway",
            "accent_color": "#404040",
            "layout": "single-column",
            "line_spacing": 1.4
        }
    }
]

def seed_templates():
    """Seed 20 advanced templates"""
    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0
        
        for template_data in ADVANCED_TEMPLATES:
            # Check if exists
            existing = db.query(ResumeTemplate).filter(
                ResumeTemplate.name == template_data["name"]
            ).first()
            
            if existing:
                print(f"  SKIP: {template_data['name']} (already exists)")
                skipped += 1
                continue
            
            # Create new template
            template = ResumeTemplate(
                name=template_data["name"],
                category=template_data["category"],
                description=template_data["description"],
                is_ats_friendly=template_data["is_ats_friendly"],
                is_active=template_data["is_active"],
                popularity=template_data["popularity"],
                config=template_data["config"]
            )
            db.add(template)
            print(f"  ADDED: {template_data['name']}")
            inserted += 1
        
        db.commit()
        print(f"\nSuccess: {inserted} templates inserted, {skipped} skipped")
        return inserted, skipped
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return 0, 0
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding 20 advanced resume templates...\n")
    seed_templates()
