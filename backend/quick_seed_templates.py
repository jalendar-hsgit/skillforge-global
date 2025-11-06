"""
Quick Template Seeder - Seeds 32 professional resume templates
Run: python quick_seed_templates.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.db import SessionLocal
from app.modelsx.resume import ResumeTemplate


def seed_templates():
    """Seed 32 professional templates"""
    db = SessionLocal()
    
    try:
        # Clear existing
        count = db.query(ResumeTemplate).count()
        if count > 0:
            print(f"Found {count} existing templates. Clearing...")
            db.query(ResumeTemplate).delete()
            db.commit()
        
        templates_data = [
            # MODERN (8)
            {"name": "Modern Professional", "category": "Modern", "desc": "Clean, modern design with bold headers. Perfect for tech roles.", "thumb": "/templates/modern-pro.png", "ats": True, "pop": 95, "config": {"layout": "single-column", "font": "Roboto", "accent": "#2563eb", "picture": "circle", "icons": True}},
            {"name": "Minimalist Blue", "category": "Modern", "desc": "Ultra-clean design with subtle blue accents. Corporate-friendly.", "thumb": "/templates/minimal-blue.png", "ats": True, "pop": 88, "config": {"layout": "single-column", "font": "Open Sans", "accent": "#0ea5e9", "picture": "square", "icons": False}},
            {"name": "Tech Stack", "category": "Modern", "desc": "Developer-focused with prominent skills section.", "thumb": "/templates/tech-stack.png", "ats": True, "pop": 92, "config": {"layout": "two-column", "font": "Inter", "accent": "#8b5cf6", "picture": "rounded", "icons": True}},
            {"name": "Creative Bold", "category": "Modern", "desc": "Eye-catching with bold typography and vibrant colors.", "thumb": "/templates/creative-bold.png", "ats": False, "pop": 75, "config": {"layout": "sidebar", "font": "Montserrat", "accent": "#f59e0b", "picture": "circle", "icons": True}},
            {"name": "Gradient Modern", "category": "Modern", "desc": "Contemporary with subtle gradient backgrounds.", "thumb": "/templates/gradient.png", "ats": True, "pop": 82, "config": {"layout": "single-column", "font": "Lato", "accent": "#06b6d4", "picture": "rounded", "icons": True}},
            {"name": "Dark Mode Pro", "category": "Modern", "desc": "Stunning dark theme perfect for creative professionals.", "thumb": "/templates/dark-pro.png", "ats": False, "pop": 78, "config": {"layout": "two-column", "font": "Poppins", "accent": "#10b981", "picture": "circle", "icons": True}},
            {"name": "Sleek Professional", "category": "Modern", "desc": "Perfect balance of style and readability.", "thumb": "/templates/sleek.png", "ats": True, "pop": 90, "config": {"layout": "single-column", "font": "Source Sans Pro", "accent": "#6366f1", "picture": "square", "icons": False}},
            {"name": "Startup Hustle", "category": "Modern", "desc": "Dynamic template showing entrepreneurial spirit.", "thumb": "/templates/startup.png", "ats": True, "pop": 80, "config": {"layout": "sidebar", "font": "Raleway", "accent": "#ef4444", "picture": "rounded", "icons": True}},
            
            # CLASSIC (6)
            {"name": "Traditional Serif", "category": "Classic", "desc": "Timeless serif design for law, finance, traditional industries.", "thumb": "/templates/traditional.png", "ats": True, "pop": 85, "config": {"layout": "single-column", "font": "Georgia", "accent": "#1f2937", "picture": "square", "icons": False}},
            {"name": "Executive Black", "category": "Classic", "desc": "Sophisticated black and white for senior professionals.", "thumb": "/templates/exec-black.png", "ats": True, "pop": 88, "config": {"layout": "single-column", "font": "Times New Roman", "accent": "#000000", "picture": "square", "icons": False}},
            {"name": "Corporate Standard", "category": "Classic", "desc": "Standard corporate template, universally accepted.", "thumb": "/templates/corporate.png", "ats": True, "pop": 93, "config": {"layout": "single-column", "font": "Calibri", "accent": "#1e40af", "picture": "square", "icons": False}},
            {"name": "Banking Professional", "category": "Classic", "desc": "Conservative design for banking and finance.", "thumb": "/templates/banking.png", "ats": True, "pop": 82, "config": {"layout": "single-column", "font": "Arial", "accent": "#065f46", "picture": "square", "icons": False}},
            {"name": "Academic Scholar", "category": "Classic", "desc": "Traditional academic CV with publications emphasis.", "thumb": "/templates/academic.png", "ats": True, "pop": 78, "config": {"layout": "single-column", "font": "Garamond", "accent": "#7c3aed", "picture": "square", "icons": False}},
            {"name": "Professional Gray", "category": "Classic", "desc": "Elegant gray tones for refined appearance.", "thumb": "/templates/gray.png", "ats": True, "pop": 86, "config": {"layout": "single-column", "font": "Helvetica", "accent": "#4b5563", "picture": "square", "icons": False}},
            
            # CREATIVE (5)
            {"name": "Designer Portfolio", "category": "Creative", "desc": "Visual-first template for designers.", "thumb": "/templates/designer.png", "ats": False, "pop": 72, "config": {"layout": "sidebar", "font": "Playfair Display", "accent": "#ec4899", "picture": "circle", "icons": True}},
            {"name": "Artistic Flair", "category": "Creative", "desc": "Expressive design for artists and creatives.", "thumb": "/templates/artistic.png", "ats": False, "pop": 68, "config": {"layout": "two-column", "font": "Merriweather", "accent": "#f97316", "picture": "rounded", "icons": True}},
            {"name": "Marketing Maven", "category": "Creative", "desc": "Dynamic template for marketing professionals.", "thumb": "/templates/marketing.png", "ats": True, "pop": 84, "config": {"layout": "sidebar", "font": "Nunito", "accent": "#14b8a6", "picture": "circle", "icons": True}},
            {"name": "Content Creator", "category": "Creative", "desc": "Vibrant for social media managers.", "thumb": "/templates/content.png", "ats": False, "pop": 76, "config": {"layout": "two-column", "font": "Quicksand", "accent": "#a855f7", "picture": "circle", "icons": True}},
            {"name": "Innovative Thinker", "category": "Creative", "desc": "Bold design for forward-thinking professionals.", "thumb": "/templates/innovative.png", "ats": True, "pop": 80, "config": {"layout": "sidebar", "font": "Ubuntu", "accent": "#06b6d4", "picture": "rounded", "icons": True}},
            
            # EXECUTIVE (4)
            {"name": "C-Suite Executive", "category": "Executive", "desc": "Premium design for C-level executives.", "thumb": "/templates/c-suite.png", "ats": True, "pop": 87, "config": {"layout": "single-column", "font": "Georgia", "accent": "#991b1b", "picture": "square", "icons": False}},
            {"name": "Senior Leader", "category": "Executive", "desc": "Distinguished for senior leadership positions.", "thumb": "/templates/senior.png", "ats": True, "pop": 85, "config": {"layout": "single-column", "font": "Times New Roman", "accent": "#1e3a8a", "picture": "square", "icons": False}},
            {"name": "Board Member", "category": "Executive", "desc": "Prestigious for board and advisory roles.", "thumb": "/templates/board.png", "ats": True, "pop": 79, "config": {"layout": "single-column", "font": "Garamond", "accent": "#4c1d95", "picture": "square", "icons": False}},
            {"name": "VP Level", "category": "Executive", "desc": "Professional for Vice President and Director roles.", "thumb": "/templates/vp.png", "ats": True, "pop": 83, "config": {"layout": "single-column", "font": "Calibri", "accent": "#075985", "picture": "square", "icons": False}},
            
            # TECH (4)
            {"name": "Software Engineer", "category": "Tech", "desc": "Optimized for software developers.", "thumb": "/templates/software.png", "ats": True, "pop": 94, "config": {"layout": "two-column", "font": "Fira Code", "accent": "#059669", "picture": "rounded", "icons": True}},
            {"name": "DevOps Specialist", "category": "Tech", "desc": "Template for DevOps and infrastructure engineers.", "thumb": "/templates/devops.png", "ats": True, "pop": 86, "config": {"layout": "two-column", "font": "Source Code Pro", "accent": "#dc2626", "picture": "square", "icons": True}},
            {"name": "Data Scientist", "category": "Tech", "desc": "Analytics-focused for data scientists and ML engineers.", "thumb": "/templates/data.png", "ats": True, "pop": 89, "config": {"layout": "sidebar", "font": "IBM Plex Sans", "accent": "#7c3aed", "picture": "rounded", "icons": True}},
            {"name": "Cybersecurity Pro", "category": "Tech", "desc": "Security-focused with professional styling.", "thumb": "/templates/security.png", "ats": True, "pop": 81, "config": {"layout": "two-column", "font": "Roboto Mono", "accent": "#0891b2", "picture": "square", "icons": True}},
            
            # MEDICAL (3)
            {"name": "Healthcare Professional", "category": "Medical", "desc": "Clean, professional for healthcare workers.", "thumb": "/templates/healthcare.png", "ats": True, "pop": 88, "config": {"layout": "single-column", "font": "Arial", "accent": "#0284c7", "picture": "square", "icons": False}},
            {"name": "Clinical Researcher", "category": "Medical", "desc": "Academic-style for medical researchers.", "thumb": "/templates/clinical.png", "ats": True, "pop": 82, "config": {"layout": "single-column", "font": "Times New Roman", "accent": "#16a34a", "picture": "square", "icons": False}},
            {"name": "Nursing Excellence", "category": "Medical", "desc": "Caring, professional for nursing professionals.", "thumb": "/templates/nursing.png", "ats": True, "pop": 85, "config": {"layout": "single-column", "font": "Calibri", "accent": "#be185d", "picture": "circle", "icons": False}},
        ]
        
        print(f"\n🌱 Seeding {len(templates_data)} templates...")
        
        for data in templates_data:
            template = ResumeTemplate(
                name=data["name"],
                description=data["desc"],
                category=data["category"],
                thumbnail_url=data["thumb"],
                config=data["config"],
                is_ats_friendly=data["ats"],
                popularity=data["pop"],
                is_active=True
            )
            db.add(template)
        
        db.commit()
        
        # Stats
        categories = {}
        for t in templates_data:
            cat = t["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n✅ Successfully seeded {len(templates_data)} templates!")
        print(f"\n📊 By category:")
        for cat, count in sorted(categories.items()):
            print(f"   {cat}: {count} templates")
        
        ats_count = sum(1 for t in templates_data if t["ats"])
        print(f"\n🎯 Stats:")
        print(f"   ATS-friendly: {ats_count}/{len(templates_data)}")
        print(f"   Creative: {len(templates_data) - ats_count}/{len(templates_data)}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("Resume Template Seeder".center(60))
    print("="*60)
    seed_templates()
    print("\n" + "="*60)
    print("✅ Done!".center(60))
    print("="*60)
