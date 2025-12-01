"""
Mentor Portal - Comprehensive dashboard for mentors
Provides earnings, sessions, students, and analytics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.db import get_db, SessionLocal
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import Mentor, MentorSession, MentorReview, SessionStatus, MentorStatus

router = APIRouter(prefix="/mentor-portal", tags=["mentor-portal"])


# ============================================================
# MENTOR PORTAL - Comprehensive Dashboard
# ============================================================

@router.get("/dashboard/overview")
def get_mentor_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive mentor dashboard overview:
    - Total sessions (all time & this month)
    - Total earnings (all time & this month)
    - Average rating
    - Upcoming sessions
    - Recent reviews
    - Student count
    """
    # Check if user is a mentor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    if mentor.status != MentorStatus.APPROVED:
        raise HTTPException(status_code=403, detail=f"Mentor status: {mentor.status}")
    
    # Calculate date ranges
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    # Total sessions
    total_sessions = db.query(func.count(MentorSession.id)).filter(
        MentorSession.mentor_id == mentor.id
    ).scalar() or 0
    
    # This month's sessions
    month_sessions = db.query(func.count(MentorSession.id)).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.created_at >= month_start
        )
    ).scalar() or 0
    
    # Completed sessions
    completed_sessions = db.query(func.count(MentorSession.id)).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).scalar() or 0
    
    # Total earnings (completed sessions only)
    total_earnings = db.query(func.sum(MentorSession.amount_paid)).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).scalar() or 0.0
    
    # This month's earnings
    month_earnings = db.query(func.sum(MentorSession.amount_paid)).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED,
            MentorSession.created_at >= month_start
        )
    ).scalar() or 0.0
    
    # Average rating
    avg_rating = db.query(func.avg(MentorReview.rating)).filter(
        MentorReview.mentor_id == mentor.id
    ).scalar() or 0.0
    
    # Total reviews
    total_reviews = db.query(func.count(MentorReview.id)).filter(
        MentorReview.mentor_id == mentor.id
    ).scalar() or 0
    
    # Unique students count
    unique_students = db.query(func.count(func.distinct(MentorSession.student_id))).filter(
        MentorSession.mentor_id == mentor.id
    ).scalar() or 0
    
    # Upcoming sessions (next 7 days)
    upcoming = db.query(MentorSession).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.scheduled_at >= now,
            MentorSession.scheduled_at <= now + timedelta(days=7),
            MentorSession.status.in_([SessionStatus.PENDING, SessionStatus.CONFIRMED])
        )
    ).order_by(MentorSession.scheduled_at).limit(5).all()
    
    # Recent reviews
    recent_reviews = db.query(MentorReview).filter(
        MentorReview.mentor_id == mentor.id
    ).order_by(MentorReview.created_at.desc()).limit(5).all()
    
    return {
        "mentor": {
            "id": mentor.id,
            "user_id": mentor.user_id,
            "status": mentor.status,
            "bio": mentor.bio,
            "expertise": mentor.expertise,
            "hourly_rate": mentor.hourly_rate
        },
        "stats": {
            "total_sessions": total_sessions,
            "month_sessions": month_sessions,
            "completed_sessions": completed_sessions,
            "total_earnings": round(total_earnings, 2),
            "month_earnings": round(month_earnings, 2),
            "average_rating": round(avg_rating, 2),
            "total_reviews": total_reviews,
            "unique_students": unique_students
        },
        "upcoming_sessions": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "topic": s.topic,
                "scheduled_at": s.scheduled_at.isoformat(),
                "duration_minutes": s.duration_minutes,
                "status": s.status
            }
            for s in upcoming
        ],
        "recent_reviews": [
            {
                "id": r.id,
                "student_id": r.student_id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat()
            }
            for r in recent_reviews
        ]
    }


@router.get("/dashboard/sessions")
def get_mentor_sessions(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sessions for the mentor with optional status filter"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    query = db.query(MentorSession).filter(MentorSession.mentor_id == mentor.id)
    
    if status:
        query = query.filter(MentorSession.status == status)
    
    total = query.count()
    sessions = query.order_by(MentorSession.scheduled_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "sessions": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "topic": s.topic,
                "description": s.description,
                "scheduled_at": s.scheduled_at.isoformat(),
                "duration_minutes": s.duration_minutes,
                "status": s.status,
                "amount_paid": s.amount_paid,
                "meeting_link": s.meeting_link,
                "notes": s.notes,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions
        ]
    }


@router.get("/dashboard/earnings")
def get_mentor_earnings(
    timeframe: str = "all",  # all, month, week
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed earnings breakdown"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    now = datetime.utcnow()
    
    # Determine date filter
    if timeframe == "month":
        start_date = datetime(now.year, now.month, 1)
    elif timeframe == "week":
        start_date = now - timedelta(days=7)
    else:
        start_date = datetime(1970, 1, 1)  # All time
    
    # Completed sessions for earnings
    sessions = db.query(MentorSession).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED,
            MentorSession.created_at >= start_date
        )
    ).all()
    
    total_earnings = sum(s.amount_paid or 0 for s in sessions)
    total_hours = sum(s.duration_minutes or 0 for s in sessions) / 60
    
    # Earnings by month (for chart)
    monthly_earnings = db.execute(text("""
        SELECT 
            DATE_FORMAT(created_at, '%Y-%m') as month,
            SUM(amount_paid) as earnings,
            COUNT(*) as session_count
        FROM mentor_sessions
        WHERE mentor_id = :mid
        AND status = 'completed'
        AND created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
        ORDER BY month DESC
    """), {"mid": mentor.id}).mappings().all()
    
    return {
        "total_earnings": round(total_earnings, 2),
        "total_hours": round(total_hours, 2),
        "session_count": len(sessions),
        "average_per_session": round(total_earnings / len(sessions), 2) if sessions else 0,
        "hourly_rate": mentor.hourly_rate,
        "monthly_breakdown": [
            {
                "month": row["month"],
                "earnings": float(row["earnings"] or 0),
                "sessions": row["session_count"]
            }
            for row in monthly_earnings
        ]
    }


@router.get("/dashboard/students")
def get_mentor_students(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of students who have booked sessions"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    # Get unique students with session counts
    students_data = db.execute(text("""
        SELECT 
            u.id,
            u.email,
            COUNT(ms.id) as session_count,
            SUM(CASE WHEN ms.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
            MAX(ms.scheduled_at) as last_session_date
        FROM users u
        INNER JOIN mentor_sessions ms ON u.id = ms.student_id
        WHERE ms.mentor_id = :mid
        GROUP BY u.id, u.email
        ORDER BY last_session_date DESC
    """), {"mid": mentor.id}).mappings().all()
    
    return {
        "students": [
            {
                "id": row["id"],
                "email": row["email"],
                "total_sessions": row["session_count"],
                "completed_sessions": row["completed_count"],
                "last_session": row["last_session_date"].isoformat() if row["last_session_date"] else None
            }
            for row in students_data
        ]
    }


@router.get("/dashboard/analytics")
def get_mentor_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for mentor performance"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    # Session status breakdown
    status_breakdown = db.execute(text("""
        SELECT 
            status,
            COUNT(*) as count
        FROM mentor_sessions
        WHERE mentor_id = :mid
        GROUP BY status
    """), {"mid": mentor.id}).mappings().all()
    
    # Rating distribution
    rating_dist = db.execute(text("""
        SELECT 
            rating,
            COUNT(*) as count
        FROM mentor_reviews
        WHERE mentor_id = :mid
        GROUP BY rating
        ORDER BY rating DESC
    """), {"mid": mentor.id}).mappings().all()
    
    # Sessions per day of week
    sessions_by_day = db.execute(text("""
        SELECT 
            DAYNAME(scheduled_at) as day_name,
            COUNT(*) as session_count
        FROM mentor_sessions
        WHERE mentor_id = :mid
        GROUP BY DAYNAME(scheduled_at), DAYOFWEEK(scheduled_at)
        ORDER BY DAYOFWEEK(scheduled_at)
    """), {"mid": mentor.id}).mappings().all()
    
    # Average session duration
    avg_duration = db.query(func.avg(MentorSession.duration_minutes)).filter(
        MentorSession.mentor_id == mentor.id
    ).scalar() or 0
    
    return {
        "status_breakdown": {
            row["status"]: row["count"]
            for row in status_breakdown
        },
        "rating_distribution": {
            str(row["rating"]): row["count"]
            for row in rating_dist
        },
        "sessions_by_day": {
            row["day_name"]: row["session_count"]
            for row in sessions_by_day
        },
        "average_session_duration": round(avg_duration, 1)
    }


@router.get("/dashboard/reviews")
def get_mentor_reviews(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews for the mentor"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    total = db.query(func.count(MentorReview.id)).filter(
        MentorReview.mentor_id == mentor.id
    ).scalar() or 0
    
    reviews = db.query(MentorReview).filter(
        MentorReview.mentor_id == mentor.id
    ).order_by(MentorReview.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "average_rating": mentor.average_rating,
        "reviews": [
            {
                "id": r.id,
                "student_id": r.student_id,
                "session_id": r.session_id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat()
            }
            for r in reviews
        ]
    }


@router.patch("/profile")
def update_mentor_profile(
    bio: Optional[str] = None,
    expertise: Optional[str] = None,
    hourly_rate: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update mentor profile information"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Not a mentor")
    
    if bio is not None:
        mentor.bio = bio
    if expertise is not None:
        mentor.expertise = expertise
    if hourly_rate is not None:
        if hourly_rate < 0:
            raise HTTPException(status_code=400, detail="Hourly rate cannot be negative")
        mentor.hourly_rate = hourly_rate
    
    mentor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(mentor)
    
    return {
        "id": mentor.id,
        "bio": mentor.bio,
        "expertise": mentor.expertise,
        "hourly_rate": mentor.hourly_rate,
        "updated_at": mentor.updated_at.isoformat()
    }
