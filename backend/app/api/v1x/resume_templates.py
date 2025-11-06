"""
Resume Templates API - Browse and select resume templates
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.resume import ResumeTemplate
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/resume-templates", tags=["Resume Templates"])


class ResumeTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    config: Optional[dict] = None
    is_ats_friendly: bool = True
    popularity: int = 0
    is_active: bool = True


@router.get("", response_model=List[ResumeTemplateResponse])
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category: Modern, Classic, Creative, Executive, Tech, Medical"),
    ats_friendly: Optional[bool] = Query(None, description="Filter ATS-friendly templates"),
    free_only: Optional[bool] = Query(None, description="Show only free templates"),
    db: Session = Depends(get_db)
):
    """
    Get list of all resume templates with optional filters
    Categories: Modern, Classic, Creative, Executive, Tech, Medical, Academic, Legal, Sales, Marketing
    """
    query = db.query(ResumeTemplate).filter(ResumeTemplate.is_active == True)
    
    if category:
        query = query.filter(ResumeTemplate.category == category)
    
    if ats_friendly is not None:
        query = query.filter(ResumeTemplate.is_ats_friendly == ats_friendly)
    
    # Sort by popularity
    query = query.order_by(ResumeTemplate.popularity.desc())
    
    templates = query.all()
    return templates


@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """Get list of all template categories"""
    categories = db.query(ResumeTemplate.category).distinct().all()
    return {"categories": [c[0] for c in categories if c[0]]}


@router.get("/{template_id}", response_model=ResumeTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific template by ID"""
    template = db.query(ResumeTemplate).filter(
        ResumeTemplate.id == template_id,
        ResumeTemplate.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.post("/{template_id}/popularity")
async def increment_popularity(
    template_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Increment template popularity when user selects it"""
    template = db.query(ResumeTemplate).filter(ResumeTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template.popularity += 1
    db.commit()
    
    return {"message": "Popularity updated", "new_popularity": template.popularity}


@router.get("/popular/top")
async def get_popular_templates(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get most popular templates"""
    templates = db.query(ResumeTemplate).filter(
        ResumeTemplate.is_active == True
    ).order_by(
        ResumeTemplate.popularity.desc()
    ).limit(limit).all()
    
    return templates
