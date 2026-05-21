from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from backend.app.modelsx.resume_analytics import ResumeAnalytics, Base
from backend.app.schemas.resume_analytics import ResumeAnalyticsCreate, ResumeAnalyticsUpdate, ResumeAnalyticsOut
from backend.app.core.db import get_db

router = APIRouter(prefix="/resume-analytics", tags=["Resume Analytics"])

@router.post("/", response_model=ResumeAnalyticsOut)
def create_analytics(data: ResumeAnalyticsCreate, db: Session = Depends(get_db)):
    analytics = ResumeAnalytics(**data.dict())
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics

@router.get("/{resume_id}", response_model=ResumeAnalyticsOut)
def get_analytics(resume_id: UUID, db: Session = Depends(get_db)):
    analytics = db.query(ResumeAnalytics).filter(ResumeAnalytics.resume_id == resume_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return analytics

@router.patch("/{resume_id}", response_model=ResumeAnalyticsOut)
def update_analytics(resume_id: UUID, data: ResumeAnalyticsUpdate, db: Session = Depends(get_db)):
    analytics = db.query(ResumeAnalytics).filter(ResumeAnalytics.resume_id == resume_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(analytics, key, value)
    db.commit()
    db.refresh(analytics)
    return analytics
