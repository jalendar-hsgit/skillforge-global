from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.db import SessionLocal

router = APIRouter(prefix="/courses-db", tags=["courses-db"])

@router.get("")
def list_courses():
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT id, path, title, description FROM courses ORDER BY id")).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()

@router.get("/{path}")
def get_course(path: str):
    db = SessionLocal()
    try:
        row = db.execute(text("SELECT id, path, title, description FROM courses WHERE path=:p"), {"p": path}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Course not found")
        return dict(row)
    finally:
        db.close()

@router.get("/{path}/videos")
def list_videos_for_course(path: str):
    db = SessionLocal()
    try:
        course = db.execute(text("SELECT id FROM courses WHERE path=:p"), {"p": path}).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        rows = db.execute(text("""
            SELECT id, course_id, title, youtube_id, duration
            FROM videos
            WHERE course_id=:cid
            ORDER BY id
        """), {"cid": course[0]}).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()
