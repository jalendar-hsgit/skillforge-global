from fastapi import APIRouter, Depends, HTTPException, Query, Header, Cookie, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ...core.db import get_db
from ...core.security import decode_token
from ...models.progress import Progress
from ...schemas.progress import ProgressList, ProgressItem
from ...modelsx.progress import VideoProgress

router = APIRouter(prefix="/progress", tags=["progress"])

# ============ Video Progress Models ============
class VideoProgressUpdate(BaseModel):
    progress_percent: int
    last_position_sec: Optional[int] = None

class VideoProgressResponse(BaseModel):
    video_id: int
    progress_percent: int
    last_position_sec: Optional[int] = None
    updated_at: Optional[datetime] = None

def _require_user(authorization: str | None, token_cookie: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        # Try cookie token (v1 auth sets HTTP-only cookie named 'token')
        if not token_cookie:
            raise HTTPException(status_code=401, detail="Missing token")
        claims = decode_token(token_cookie)
    else:
        # decode_token returns the JWT claims dict; extract the `sub` claim
        claims = decode_token(authorization.split(" ",1)[1])
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("", response_model=ProgressList)
def get_progress(path: str = Query(...), authorization: str | None = Header(None), token: str | None = Cookie(None), db: Session = Depends(get_db)):
    user_id = _require_user(authorization, token)
    rows = db.query(Progress).filter(Progress.user_id==user_id, Progress.path==path).all()
    return ProgressList(path=path, completed=[r.module_id for r in rows])

@router.post("", response_model=ProgressList)
def mark_complete(
    path: str = Query(None),
    module_id: str = Query(None),
    body: ProgressItem | None = None,
    authorization: str | None = Header(None),
    token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    user_id = _require_user(authorization, token)
    # Accept from body if query params not provided
    if body:
        path = path or body.path
        module_id = module_id or body.module_id
    if not path or not module_id:
        raise HTTPException(status_code=422, detail="path and module_id are required")
    exists = db.query(Progress).filter(Progress.user_id==user_id, Progress.module_id==module_id).first()
    if not exists:
        db.add(Progress(user_id=user_id, path=path, module_id=module_id))
        db.commit()
    rows = db.query(Progress).filter(Progress.user_id==user_id, Progress.path==path).all()
    return ProgressList(path=path, completed=[r.module_id for r in rows])

# ============ Video Progress Endpoints ============
@router.get("/videos/{video_id}", response_model=VideoProgressResponse)
def get_video_progress(
    video_id: int,
    authorization: str | None = Header(None),
    token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    """Get progress for a specific video"""
    user_id = _require_user(authorization, token)
    
    progress = db.query(VideoProgress).filter(
        VideoProgress.user_id == user_id,
        VideoProgress.video_id == video_id
    ).first()
    
    if not progress:
        # Return default progress (0%) if not found
        return VideoProgressResponse(
            video_id=video_id,
            progress_percent=0,
            last_position_sec=0
        )
    
    return VideoProgressResponse(
        video_id=progress.video_id,
        progress_percent=progress.progress_percent,
        last_position_sec=progress.last_position_sec,
        updated_at=getattr(progress, 'updated_at', None)
    )

@router.post("/videos/{video_id}", response_model=VideoProgressResponse)
def update_video_progress(
    video_id: int,
    update: VideoProgressUpdate = Body(...),
    authorization: str | None = Header(None),
    token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    """Update or create video progress"""
    user_id = _require_user(authorization, token)
    
    # Find existing progress
    progress = db.query(VideoProgress).filter(
        VideoProgress.user_id == user_id,
        VideoProgress.video_id == video_id
    ).first()
    
    if progress:
        # Update existing progress
        progress.progress_percent = min(100, max(0, update.progress_percent))
        if update.last_position_sec is not None:
            progress.last_position_sec = update.last_position_sec
    else:
        # Create new progress
        progress = VideoProgress(
            user_id=user_id,
            video_id=video_id,
            progress_percent=min(100, max(0, update.progress_percent)),
            last_position_sec=update.last_position_sec or 0
        )
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    
    return VideoProgressResponse(
        video_id=progress.video_id,
        progress_percent=progress.progress_percent,
        last_position_sec=progress.last_position_sec,
        updated_at=getattr(progress, 'updated_at', None)
    )

