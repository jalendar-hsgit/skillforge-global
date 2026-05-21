"""
Generate PDF previews for all resume templates using ReportLab and your template logic.
"""
import os
from pathlib import Path
from app.core.db import SessionLocal
from app.modelsx.resume import ResumeTemplate
from app.api.v1x import resume_export

OUT_DIR = Path(__file__).parent.parent / "public" / "templates"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Dummy resume data for preview
DUMMY_RESUME = {
    "full_name": "Jane Doe",
    "email": "jane.doe@email.com",
    "phone": "+1 555-123-4567",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/janedoe",
    "github": "github.com/janedoe",
    "website": "janedoe.dev",
    "professional_summary": "Experienced software engineer with a passion for building scalable web applications and leading cross-functional teams.",
    "work_experiences": [
        {"title": "Senior Software Engineer", "company": "TechCorp", "start_date": "2021-01-01", "end_date": "2023-01-01", "description": "Led a team of 5 engineers to deliver a new SaaS platform."},
        {"title": "Software Engineer", "company": "Webify", "start_date": "2018-06-01", "end_date": "2020-12-31", "description": "Built and maintained core features for a high-traffic e-commerce site."}
    ],
    "education": [
        {"degree": "B.Sc. Computer Science", "school": "State University", "start_date": "2014-09-01", "end_date": "2018-05-31"}
    ],
    "skills": ["Python", "JavaScript", "React", "SQL", "AWS"],
    "projects": [
        {"name": "Open Source CRM", "description": "Built a CRM used by 100+ companies."}
    ],
    "certificates": [
        {"name": "AWS Certified Solutions Architect", "issuer": "Amazon", "date": "2022-03-01"}
    ],
    "achievements": [
        {"name": "Hackathon Winner", "description": "Won 1st place at City Hackathon 2021."}
    ],
}

def main():
    db = SessionLocal()
    try:
        templates = db.query(ResumeTemplate).all()
        for template in templates:
            # Use template config for preview
            resume_data = DUMMY_RESUME.copy()
            resume_data.update({
                "font_family": template.font or "Inter",
                "color_theme": template.color_theme or "blue",
                "layout": template.layout or "modern",
                "accent_color": template.accent or "#2563eb",
                "picture_style": template.picture or "circle",
                "show_icons": template.icons if template.icons is not None else True,
            })
            # Use the export logic to generate PDF
            pdf_bytes = resume_export.export_resume_pdf_from_dict(resume_data)
            out_path = OUT_DIR / f"{template.slug or template.id}.pdf"
            with open(out_path, "wb") as f:
                f.write(pdf_bytes)
            print(f"✓ Wrote {out_path}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
