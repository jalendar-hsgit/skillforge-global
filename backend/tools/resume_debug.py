import sys
import os
import json
# Ensure repo root is on sys.path so `app` package imports succeed when running this script directly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.db import SessionLocal
from app.modelsx.resume import Resume

def summarize_resume(resume_id: int):
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            print(json.dumps({"error": "resume not found", "id": resume_id}))
            return

        def _proj_link(p):
            return getattr(p, 'github_url', None) or getattr(p, 'demo_url', None) or getattr(p, 'url', None)

        out = {
            "id": resume.id,
            "full_name": resume.full_name,
            "email": resume.email,
            "summary": resume.summary,
            "work_experience_count": len(resume.work_experiences) if resume.work_experiences else 0,
            "education_count": len(resume.education) if resume.education else 0,
            "skills": [getattr(s, 'name', str(s)) for s in (resume.skills or [])],
            "projects": [
                {"title": getattr(p, 'title', ''), "link": _proj_link(p)} for p in (resume.projects or [])
            ]
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    finally:
        db.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python resume_debug.py <resume_id>")
        sys.exit(1)
    try:
        rid = int(sys.argv[1])
    except ValueError:
        print("resume_id must be an integer")
        sys.exit(1)
    summarize_resume(rid)
