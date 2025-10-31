from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, conint
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.services.yt_sync import search_videos, save_videos

router = APIRouter(prefix="/youtube", tags=["YouTube Sync"])

class PreviewBody(BaseModel):
    course_id: int = Field(..., ge=1)
    query: str = Field(..., min_length=2)
    max_results: conint(ge=1, le=25) = 10

@router.get("/health")
def health_check():
    has_key = bool(getattr(settings, "YOUTUBE_API_KEY", None))
    return {"ok": True, "has_key": has_key}

@router.post("/preview")
def preview(payload: PreviewBody):
    if not settings.YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YOUTUBE_API_KEY missing")
    items = search_videos(payload.query, payload.max_results)
    return {"ok": True, "count": len(items), "items": items}

@router.post("/sync")
def sync(payload: PreviewBody, db: Session = Depends(get_db)):
    if not settings.YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YOUTUBE_API_KEY missing")
    items = search_videos(payload.query, payload.max_results)
    result = save_videos(db, payload.course_id, items)
    return {"ok": True, **result}
