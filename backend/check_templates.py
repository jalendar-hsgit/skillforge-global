"""
Check what templates exist in the database and their configs
"""
from app.modelsx.resume import ResumeTemplate
from app.core.db import SessionLocal

db = SessionLocal()
try:
    count = db.query(ResumeTemplate).count()
    print(f'Templates in DB: {count}')
    
    if count == 0:
        print('\nNo templates found. Creating sample templates...')
        
        samples = [
            ResumeTemplate(
                name='Modern Professional',
                description='Clean, modern design perfect for tech and corporate roles',
                category='Modern',
                config={'layout': 'modern', 'font': 'Inter', 'accent': '#2563eb', 'picture': 'square', 'icons': True},
                is_ats_friendly=True,
                popularity=100
            ),
            ResumeTemplate(
                name='Executive Leadership',
                description='Premium two-column layout for senior positions',
                category='Executive',
                config={'layout': 'executive-two', 'font': 'Georgia', 'accent': '#1e40af', 'picture': 'circle', 'icons': False},
                is_ats_friendly=True,
                popularity=85
            ),
            ResumeTemplate(
                name='Minimal Clean',
                description='Ultra-minimal design with maximum impact',
                category='Minimal',
                config={'layout': 'minimal', 'font': 'Inter', 'accent': '#6366f1', 'picture': 'none', 'icons': False},
                is_ats_friendly=True,
                popularity=75
            ),
            ResumeTemplate(
                name='Creative Bold',
                description='Eye-catching design for creative fields',
                category='Creative',
                config={'layout': 'creative', 'font': 'Montserrat', 'accent': '#ec4899', 'picture': 'circle', 'icons': True},
                is_ats_friendly=False,
                popularity=60
            ),
            ResumeTemplate(
                name='Tech Developer',
                description='Code-inspired layout for software engineers',
                category='Tech',
                config={'layout': 'tech-two', 'font': 'Roboto Mono', 'accent': '#10b981', 'picture': 'square', 'icons': True},
                is_ats_friendly=True,
                popularity=90
            ),
            ResumeTemplate(
                name='Academic Researcher',
                description='Publication-focused for academia and research',
                category='Academic',
                config={'layout': 'academic-two', 'font': 'Georgia', 'accent': '#8b5cf6', 'picture': 'square', 'icons': False},
                is_ats_friendly=True,
                popularity=50
            ),
            ResumeTemplate(
                name='Classic Traditional',
                description='Timeless professional design',
                category='Classic',
                config={'layout': 'classic', 'font': 'Georgia', 'accent': '#374151', 'picture': 'square', 'icons': False},
                is_ats_friendly=True,
                popularity=95
            ),
        ]
        
        for t in samples:
            db.add(t)
        db.commit()
        print(f'Created {len(samples)} sample templates.')
    
    # Show top 10
    samples = db.query(ResumeTemplate).order_by(ResumeTemplate.popularity.desc()).limit(10).all()
    print(f'\nTop {len(samples)} templates:')
    for t in samples:
        cfg = t.config if isinstance(t.config, dict) else {}
        layout = cfg.get('layout', 'N/A')
        accent = cfg.get('accent', 'N/A')
        font = cfg.get('font', 'N/A')
        print(f'  {t.id}. {t.name} ({t.category})')
        print(f'      layout: {layout}, accent: {accent}, font: {font}, ATS: {t.is_ats_friendly}')
    
finally:
    db.close()
