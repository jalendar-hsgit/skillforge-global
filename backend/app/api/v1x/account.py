"""
User Account API endpoints
Handles user account profile and settings
Separate from user_profiles.py which handles public profiles
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserProfileResponse, UserProfileUpdate, UserStatsResponse, UserPublicProfile
)

router = APIRouter(prefix="/account", tags=["account"])


# ============ User Account Endpoints ============

@router.get("/profile", response_model=UserProfileResponse)
def get_account_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's account profile
    Returns complete profile with all editable fields
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    return UserProfileResponse.from_orm(user)


@router.patch("/profile", response_model=UserProfileResponse)
def update_account_profile(
    update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's account profile
    Returns updated profile
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    # Update fields if provided
    update_data = update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserProfileResponse.from_orm(user)


# ============ User Statistics Endpoints ============

@router.get("/stats", response_model=UserStatsResponse)
def get_account_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's statistics and metrics
    Includes learning history, achievements, streaks
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    # Get recent sessions (if student or mentor)
    recent_sessions = []
    try:
        from app.modelsx.mentor import MentorSession
        sessions = db.query(MentorSession).filter(
            (MentorSession.student_id == user.id) | 
            (MentorSession.mentor_id == 
             db.query(app.modelsx.mentor.Mentor.id).filter(
                 app.modelsx.mentor.Mentor.user_id == user.id
             ))
        ).order_by(MentorSession.scheduled_at.desc()).limit(5).all()
        
        recent_sessions = [
            {
                "id": s.id,
                "topic": s.topic,
                "scheduled_at": s.scheduled_at.isoformat() if s.scheduled_at else None,
                "status": s.status,
                "price": s.price
            }
            for s in sessions
        ]
    except Exception:
        recent_sessions = []
    
    # Get courses enrolled
    courses_enrolled = 0
    try:
        from app.modelsx.progress import Progress
        courses_enrolled = db.query(Progress).filter(
            Progress.user_id == user.id
        ).distinct(Progress.course_id).count()
    except Exception:
        pass
    
    # Calculate metrics
    current_streak = 0
    total_learning_time = 0.0
    
    try:
        from app.modelsx.progress import Progress
        progress_records = db.query(Progress).filter(
            Progress.user_id == user.id
        ).all()
        
        for p in progress_records:
            if hasattr(p, 'time_spent') and p.time_spent:
                total_learning_time += p.time_spent
    except Exception:
        pass
    
    return UserStatsResponse(
        user_id=user.id,
        sessions_completed=user.sessions_completed,
        avg_rating=user.avg_rating,
        total_hours=user.total_hours,
        recent_sessions=recent_sessions,
        courses_enrolled=courses_enrolled,
        certificates_earned=0,
        current_streak=current_streak,
        total_learning_time=total_learning_time
    )

