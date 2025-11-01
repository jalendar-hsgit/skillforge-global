from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from backend.app.modelsx.resume_analytics import ResumeAnalytics
from backend.app.core.db import get_db

router = APIRouter(prefix="/resume-analytics/events", tags=["Resume Analytics Events"])

def get_or_create_analytics(resume_id: UUID, user_id: UUID, db: Session):
    analytics = db.query(ResumeAnalytics).filter_by(resume_id=resume_id, user_id=user_id).first()
    if not analytics:
        analytics = ResumeAnalytics(resume_id=resume_id, user_id=user_id)
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
    return analytics

@router.post("/view/{resume_id}")
def track_view(resume_id: UUID, user_id: UUID, db: Session = Depends(get_db)):
    analytics = get_or_create_analytics(resume_id, user_id, db)
    analytics.views += 1
    analytics.last_viewed = datetime.utcnow()
    db.commit()
    return {"success": True}

@router.post("/download/{resume_id}")
def track_download(resume_id: UUID, user_id: UUID, db: Session = Depends(get_db)):
    analytics = get_or_create_analytics(resume_id, user_id, db)
    analytics.downloads += 1
    analytics.last_downloaded = datetime.utcnow()
    db.commit()
    return {"success": True}

@router.post("/share/{resume_id}")
def track_share(resume_id: UUID, user_id: UUID, db: Session = Depends(get_db)):
    analytics = get_or_create_analytics(resume_id, user_id, db)
    analytics.shares += 1
    analytics.last_shared = datetime.utcnow()
    db.commit()
    return {"success": True}

@router.post("/template/{resume_id}")
def track_template_change(resume_id: UUID, user_id: UUID, template_id: str, db: Session = Depends(get_db)):
    analytics = get_or_create_analytics(resume_id, user_id, db)
    analytics.template_id = template_id
    db.commit()
    return {"success": True}
