"""
Update resume templates to use SVG thumbnails from public/templates
"""
from sqlalchemy import text, create_engine
from pathlib import Path
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Get database URL from config
try:
    from app.core.config import settings
    DATABASE_URL = settings.DATABASE_URL
except:
    DATABASE_URL = "sqlite:///./skillforge.db"

engine = create_engine(DATABASE_URL)

# Map of template names to their slugified SVG filenames
TEMPLATE_SVG_MAP = {
    'Modern Professional': 'modern-professional',
    'Software Engineer': 'software-engineer',
    'Corporate Standard': 'corporate-standard',
    'Tech Stack': 'tech-stack',
    'Sleek Professional': 'sleek-professional',
    'Data Scientist': 'data-scientist',
    'Minimalist Blue': 'minimalist-blue',
    'Executive Black': 'executive-black',
    'Healthcare Professional': 'healthcare-professional',
    'C-Suite Executive': 'c-suite-executive',
    'Professional Gray': 'professional-gray',
    'DevOps Specialist': 'devops-specialist',
    'Traditional Serif': 'traditional-serif',
    'Senior Leader': 'senior-leader',
    'Nursing Excellence': 'nursing-excellence',
    'Marketing Maven': 'marketing-maven',
    'VP Level': 'vp-level',
    'Gradient Modern': 'gradient-modern',
    'Banking Professional': 'banking-professional',
    'Clinical Researcher': 'clinical-researcher',
    'Cybersecurity Pro': 'cybersecurity-pro',
    'Startup Hustle': 'startup-hustle',
    'Innovative Thinker': 'innovative-thinker',
    'Board Member': 'board-member',
    'Dark Mode Pro': 'dark-mode-pro',
    'Academic Scholar': 'academic-scholar',
    'Content Creator': 'content-creator',
    'Creative Bold': 'creative-bold',
    'Designer Portfolio': 'designer-portfolio',
    'Artistic Flair': 'artistic-flair',
}

try:
    with engine.connect() as conn:
        # Get all templates
        result = conn.execute(text("SELECT id, name, thumbnail_url FROM resume_templates"))
        templates = result.fetchall()
        
        updated_count = 0
        
        for template_id, name, current_url in templates:
            # Try to find matching PNG
            svg_slug = TEMPLATE_SVG_MAP.get(name)
            if svg_slug:
                new_url = f"/templates/{svg_slug}.png"
                if current_url != new_url:
                    conn.execute(
                        text("UPDATE resume_templates SET thumbnail_url = :url WHERE id = :id"),
                        {"url": new_url, "id": template_id}
                    )
                    updated_count += 1
                    print(f"✓ Updated {name} -> {new_url}")
            else:
                # Set to null for gradient fallback
                if current_url:
                    conn.execute(
                        text("UPDATE resume_templates SET thumbnail_url = NULL WHERE id = :id"),
                        {"id": template_id}
                    )
                    updated_count += 1
                    print(f"ℹ Cleared thumbnail for {name} (will use gradient fallback)")
        
        conn.commit()
        print(f"\n✅ Updated {updated_count} template thumbnails")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
