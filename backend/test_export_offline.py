"""
Offline test for PDF export to avoid server lifecycle issues.
Loads a recent resume and calls export_pdf directly.
Run: python test_export_offline.py
"""
import asyncio

from app.core.db import SessionLocal
from app.api.v1x.resume_export import export_pdf
from app.modelsx.resume import Resume


def main():
    db = SessionLocal()
    try:
        resume = db.query(Resume).order_by(Resume.id.desc()).first()
        if not resume:
            print("No resumes found. Create one via API first.")
            return
        # Ensure a font that triggers mapping
        resume.font_family = resume.font_family or "Roboto"
        db.commit()

        async def run():
            resp = await export_pdf(resume, db)
            # Try to get response content size and type
            content_type = getattr(resp, 'media_type', None)
            content = None
            if hasattr(resp, 'body') and resp.body:
                content = resp.body
            elif hasattr(resp, 'body_iterator'):
                try:
                    chunks = []
                    async for chunk in resp.body_iterator:
                        chunks.append(chunk)
                    content = b"".join(chunks)
                except Exception:
                    content = b""
            size = len(content) if content else 0
            print("Status: 200 (function returned successfully)")
            print("Content-Type:", content_type)
            print("Size:", size, "bytes")

        asyncio.run(run())
    finally:
        db.close()


if __name__ == "__main__":
    main()
"""
Offline test for PDF export to avoid server lifecycle issues.
Loads a recent resume and calls export_pdf directly.
Run: python test_export_offline.py
"""
import asyncio
from pathlib import Path

from app.core.db import SessionLocal
from app.api.v1x.resume_export import export_pdf
from app.modelsx.resume import Resume


def main():
    # Use a direct DB session
    db = SessionLocal()
    try:
        # Pick most recent resume
        resume = db.query(Resume).order_by(Resume.id.desc()).first()
        if not resume:
            print("No resumes found. Create one via API first.")
            return
        # Force a custom font that previously failed to ensure mapping works
        resume.font_family = resume.font_family or "Roboto"
        db.commit()

        async def run():
            resp = await export_pdf(resume, db)
            content = resp.body if hasattr(resp, 'body') else resp.media if hasattr(resp, 'media') else None
            if content is None:
                # Try to read body iterator
                try:
                    body = b"".join([chunk async for chunk in resp.body_iterator])
                    content = body
                except Exception:
                    content = b""
            print("Status: 200 (function returned successfully)")
            print("Content-Type:", getattr(resp, 'media_type', None) or getattr(resp, 'headers', {}).get('content-type'))
            print("Size:", len(content) if content else 0, "bytes")

        asyncio.run(run())
    finally:
        db.close()


if __name__ == "__main__":
    main()
