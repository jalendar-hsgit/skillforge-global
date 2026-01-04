from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.db import SessionLocal

router = APIRouter(prefix="/courses-db", tags=["courses-db"])

# Also create an alias router for /courses (the standard endpoint name)
courses_router = APIRouter(prefix="/courses", tags=["courses"])


def _list_courses():
    """Shared implementation for listing courses."""
    db = SessionLocal()
    try:
        rows = db.execute(text("SELECT id, path, title, description FROM courses ORDER BY id")).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()


def _get_course(path: str):
    """Shared implementation for getting a single course."""
    db = SessionLocal()
    try:
        row = db.execute(text("SELECT id, path, title, description FROM courses WHERE path=:p"), {"p": path}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Course not found")
        return dict(row)
    finally:
        db.close()


def _list_videos_for_course(path: str):
    """Shared implementation for listing course videos."""
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


# /courses-db endpoints (legacy)
@router.get("")
def list_courses():
    return _list_courses()


@router.get("/{path}")
def get_course(path: str):
    return _get_course(path)


@router.get("/{path}/videos")
def list_videos_for_course(path: str):
    return _list_videos_for_course(path)


# /courses endpoints (standard)
@courses_router.get("")
def courses_list():
    return _list_courses()


@courses_router.get("/{path}")
def courses_get(path: str):
    return _get_course(path)


@courses_router.get("/{path}/videos")
def courses_videos(path: str):
    return _list_videos_for_course(path)
