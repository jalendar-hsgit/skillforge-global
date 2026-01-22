from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, conint
from sqlalchemy import text
from datetime import datetime
from app.core.db import SessionLocal
from app.core.security import get_current_user
from app.services.realtime_events import (
    on_course_progress,
    on_course_completed,
)
from app.services.badge_service import BadgeService

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
async def upsert_progress(data: ProgressIn, user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        video = db.execute(
            text(
                """
                SELECT v.id, v.course_id, v.title as video_title, c.title as course_title, c.path as course_path
                FROM videos v
                LEFT JOIN courses c ON c.id = v.course_id
                WHERE v.id=:vid
                """
            ),
            {"vid": data.video_id}
        ).mappings().first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

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

        course_progress_pct = None
        try:
            total_videos_row = db.execute(
                text("SELECT COUNT(*) as cnt FROM videos WHERE course_id=:cid"),
                {"cid": video["course_id"]}
            ).mappings().first()
            completed_videos_row = db.execute(
                text("""
                    SELECT COUNT(DISTINCT vp.video_id) as cnt
                    FROM video_progress vp
                    JOIN videos v ON v.id = vp.video_id
                    WHERE vp.user_id=:uid AND v.course_id=:cid AND vp.progress_percent = 100
                """),
                {"uid": user.id, "cid": video["course_id"]}
            ).mappings().first()
            total_videos = total_videos_row["cnt"] or 0
            completed_videos = completed_videos_row["cnt"] or 0
            if total_videos > 0:
                course_progress_pct = round((completed_videos / total_videos) * 100, 2)
        except Exception:
            course_progress_pct = None

        if course_progress_pct is not None:
            await on_course_progress(
                user.id,
                video["course_id"],
                video.get("course_title") or "",
                course_progress_pct,
                video_id=video["id"],
                video_title=video.get("video_title"),
                video_progress=float(data.progress_percent)
            )
            if course_progress_pct >= 100:
                await on_course_completed(
                    user.id,
                    video["course_id"],
                    video.get("course_title") or "",
                    completion_percentage=course_progress_pct
                )
                # Award badge for course completion
                try:
                    awarded = BadgeService.check_milestone_badges(
                        db,
                        user.id,
                        'courses_completed',
                        1  # User completed 1 course
                    )
                    if awarded:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Awarded {len(awarded)} badges to user {user.id} for course completion")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error awarding badges: {str(e)}")
        return {"ok": True}
    finally:
        db.close()
