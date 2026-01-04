"""
Session wrapper that proxies requests to v1x endpoints with authentication
This provides the /api/session prefix that the frontend expects
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate, ResumeOut, ResumeListOut

router = APIRouter(prefix="/session", tags=["session"])


# ==================== User Session ====================

@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


# ==================== Resume Session Routes ====================

@router.get("/resumes", response_model=List[ResumeListOut])
def list_user_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all user's resumes"""
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.updated_at.desc()).all()
    return resumes


@router.get("/resumes/{resume_id}", response_model=ResumeOut)
def get_user_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a user's resume by ID"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Increment view count
    resume.views = (resume.views or 0) + 1
    db.commit()
    
    return resume


@router.post("/resumes", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def create_user_resume(
    resume_data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new resume for the current user"""
    try:
        resume = Resume(
            user_id=current_user.id,
            **resume_data.dict()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create resume: {str(e)}"
        )


@router.patch("/resumes", response_model=ResumeOut)
@router.put("/resumes", response_model=ResumeOut)
def update_user_resume(
    resume_data: ResumeUpdate,
    id: int = Query(..., description="Resume ID to update"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a user's resume (supports both PATCH and PUT)"""
    resume = db.query(Resume).filter(
        Resume.id == id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    update_dict = resume_data.dict(exclude_unset=True)
    
    # Handle professional_summary alias
    if 'professional_summary' in update_dict and update_dict['professional_summary'] is not None:
        update_dict['summary'] = update_dict.pop('professional_summary')
    
    for key, value in update_dict.items():
        if hasattr(resume, key):
            setattr(resume, key, value)
    
    resume.version = (resume.version or 0) + 1
    db.commit()
    db.refresh(resume)
    
    return resume


@router.delete("/resumes")
def delete_user_resume(
    id: int = Query(..., description="Resume ID to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user's resume"""
    resume = db.query(Resume).filter(
        Resume.id == id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.delete(resume)
    db.commit()
    
    return {"ok": True}
