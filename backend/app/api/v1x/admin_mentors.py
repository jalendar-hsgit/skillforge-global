"""
Admin endpoints for managing mentor applications and system settings.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.rbac import require_admin
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorStatus, MentorSession
from app.services.email_service import email_service
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/admin/mentors", tags=["admin"])


class MentorApplicationResponse(BaseModel):
    id: int
    user_id: int
    bio: str
    expertise: str
    hourly_rate: float
    status: str
    total_sessions: int
    average_rating: float
    created_at: datetime
    user: dict  # {email, full_name}

    class Config:
        from_attributes = True


class UpdateMentorStatusRequest(BaseModel):
    status: MentorStatus


@router.get("/applications", response_model=List[MentorApplicationResponse])
def get_mentor_applications(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all mentor applications (admin only).
    Optionally filter by status.
    """
    query = db.query(Mentor)
    
    if status_filter:
        query = query.filter(Mentor.status == status_filter)
    
    applications = query.order_by(Mentor.created_at.desc()).limit(limit).all()
    
    # Build response with user info
    results = []
    for mentor in applications:
        user = db.query(User).filter(User.id == mentor.user_id).first()
        results.append(MentorApplicationResponse(
            id=mentor.id,
            user_id=mentor.user_id,
            bio=mentor.bio,
            expertise=mentor.expertise,
            hourly_rate=mentor.hourly_rate,
            status=mentor.status.value,
            total_sessions=mentor.total_sessions,
            average_rating=mentor.average_rating,
            created_at=mentor.created_at,
            user={
                "email": user.email if user else "unknown@example.com",
                "full_name": getattr(user, 'full_name', getattr(user, 'name', 'Unknown')) if user else 'Unknown'
            }
        ))
    
    return results


@router.patch("/{mentor_id}/status")
def update_mentor_status(
    mentor_id: int,
    request: UpdateMentorStatusRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update mentor application status (admin only).
    Approve or reject applications.
    """
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    
    # Update status
    old_status = mentor.status
    mentor.status = request.status
    
    # Set approval timestamp if being approved
    if request.status == MentorStatus.APPROVED and old_status != MentorStatus.APPROVED:
        mentor.approved_at = datetime.utcnow()
    
    mentor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(mentor)
    
    # Send email notification to mentor about status change
    user = db.query(User).filter(User.id == mentor.user_id).first()
    if user and user.email:
        try:
            mentor_name = f"{user.first_name} {user.last_name}" if user.first_name else user.username
            
            if request.status == MentorStatus.APPROVED:
                # Send approval email
                asyncio.create_task(
                    email_service.send_mentor_approved(
                        to_email=user.email,
                        mentor_name=mentor_name
                    )
                )
            elif request.status == MentorStatus.REJECTED:
                # Send rejection email with reason if provided
                rejection_reason = getattr(request, 'reason', None)
                asyncio.create_task(
                    email_service.send_mentor_rejected(
                        to_email=user.email,
                        mentor_name=mentor_name,
                        reason=rejection_reason
                    )
                )
        except Exception as e:
            # Log error but don't fail the status update
            print(f"Failed to send mentor status email: {e}")
    
    return {
        "message": f"Mentor status updated to {request.status.value}",
        "mentor_id": mentor_id,
        "new_status": mentor.status.value
    }


@router.get("/stats")
def get_mentor_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get mentor system statistics (admin only).
    """
    total_mentors = db.query(Mentor).count()
    pending = db.query(Mentor).filter(Mentor.status == MentorStatus.PENDING).count()
    approved = db.query(Mentor).filter(Mentor.status == MentorStatus.APPROVED).count()
    rejected = db.query(Mentor).filter(Mentor.status == MentorStatus.REJECTED).count()
    suspended = db.query(Mentor).filter(Mentor.status == MentorStatus.SUSPENDED).count()
    
    total_sessions = db.query(MentorSession).count()
    active_sessions = db.query(MentorSession).filter(
        MentorSession.status.in_(["pending", "confirmed"])
    ).count()
    
    # Calculate total revenue (completed paid sessions)
    completed_sessions = db.query(MentorSession).filter(
        MentorSession.status == "completed",
        MentorSession.payment_status == "paid"
    ).all()
    total_revenue = sum(s.price for s in completed_sessions)
    
    return {
        "mentors": {
            "total": total_mentors,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "suspended": suspended
        },
        "sessions": {
            "total": total_sessions,
            "active": active_sessions,
            "completed": len(completed_sessions)
        },
        "revenue": {
            "total": total_revenue,
            "currency": "USD"
        }
    }


@router.delete("/{mentor_id}")
def delete_mentor(
    mentor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a mentor profile (admin only).
    Warning: This will cascade delete all sessions, reviews, etc.
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    
    # Check if has active sessions
    active_sessions = db.query(MentorSession).filter(
        MentorSession.mentor_id == mentor_id,
        MentorSession.status.in_(["pending", "confirmed"])
    ).count()
    
    if active_sessions > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete mentor with {active_sessions} active sessions"
        )
    
    db.delete(mentor)
    db.commit()
    
    return {
        "message": "Mentor deleted successfully",
        "mentor_id": mentor_id
    }
