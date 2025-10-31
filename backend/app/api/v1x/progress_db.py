from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, conint
from sqlalchemy import text
from datetime import datetime
from app.core.db import SessionLocal
from app.core.security import get_current_user

router = APIRouter(prefix="/progress-db", tags=["progress-db"])

class ProgressIn(BaseModel):
    video_id: int
    progress_percent: conint(ge=0, le=100)

@router.get("")
def list_my_progress(user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT id, user_id, video_id, progress_percent, updated_at
            FROM video_progress
            WHERE user_id=:uid
            ORDER BY updated_at DESC
        """), {"uid": user.id}).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()

@router.post("")
def upsert_progress(data: ProgressIn, user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # try update
        res = db.execute(text("""
            UPDATE video_progress
            SET progress_percent=:pp, updated_at=:ts
            WHERE user_id=:uid AND video_id=:vid
        """), {"pp": data.progress_percent, "ts": datetime.utcnow(), "uid": user.id, "vid": data.video_id})
        if res.rowcount == 0:
            # insert
            db.execute(text("""
                INSERT INTO video_progress (user_id, video_id, progress_percent, updated_at)
                VALUES (:uid, :vid, :pp, :ts)
            """), {"uid": user.id, "vid": data.video_id, "pp": data.progress_percent, "ts": datetime.utcnow()})
        db.commit()
        return {"ok": True}
    finally:
        db.close()
