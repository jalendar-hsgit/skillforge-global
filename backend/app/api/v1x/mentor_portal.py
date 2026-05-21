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
    total_earnings = db.query(func.sum(MentorSession.price)).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).scalar() or 0.0
    
    # This month's earnings
    month_earnings = db.query(func.sum(MentorSession.price)).filter(
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
            "status": mentor.status.value if hasattr(mentor.status, 'value') else str(mentor.status),
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
                "status": s.status.value if hasattr(s.status, 'value') else str(s.status)
            }
            for s in upcoming
        ],
        "recent_reviews": [
            {
                "id": r.id,
                "student_id": r.student_id,
                "rating": r.rating,
                "review_text": r.review_text,
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
                "status": s.status.value if hasattr(s.status, 'value') else str(s.status),
                "price": s.price,
                "meeting_link": s.meeting_url,
                "mentor_notes": s.mentor_notes,
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
    
    total_earnings = sum(s.price or 0 for s in sessions)
    total_hours = sum(s.duration_minutes or 0 for s in sessions) / 60
    
    # Earnings by month (for chart) - use Python grouping instead of DB-specific functions
    from collections import defaultdict
    
    six_months_ago = now - timedelta(days=180)
    recent_completed = db.query(MentorSession).filter(
        and_(
            MentorSession.mentor_id == mentor.id,
            MentorSession.status == SessionStatus.COMPLETED,
            MentorSession.created_at >= six_months_ago
        )
    ).all()
    
    # Group by month in Python
    monthly_dict = defaultdict(lambda: {"earnings": 0.0, "count": 0})
    for s in recent_completed:
        month_key = s.created_at.strftime("%Y-%m")
        monthly_dict[month_key]["earnings"] += s.price or 0
        monthly_dict[month_key]["count"] += 1
    
    monthly_breakdown = [
        {
            "month": month,
            "earnings": round(data["earnings"], 2),
            "sessions": data["count"]
        }
        for month, data in sorted(monthly_dict.items(), reverse=True)
    ]
    
    return {
        "total_earnings": round(total_earnings, 2),
        "total_hours": round(total_hours, 2),
        "session_count": len(sessions),
        "average_per_session": round(total_earnings / len(sessions), 2) if sessions else 0,
        "hourly_rate": mentor.hourly_rate,
        "monthly_breakdown": monthly_breakdown
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
    
    # Get unique students with session counts using ORM
    # Group sessions by student and aggregate
    all_sessions = db.query(MentorSession).filter(
        MentorSession.mentor_id == mentor.id
    ).all()
    
    from collections import defaultdict
    student_data = defaultdict(lambda: {"total": 0, "completed": 0, "last_date": None})
    
    for session in all_sessions:
        sid = session.student_id
        student_data[sid]["total"] += 1
        if session.status == SessionStatus.COMPLETED:
            student_data[sid]["completed"] += 1
        if student_data[sid]["last_date"] is None or session.scheduled_at > student_data[sid]["last_date"]:
            student_data[sid]["last_date"] = session.scheduled_at
    
    # Fetch user details for each student
    students_list = []
    for student_id, data in student_data.items():
        student = db.query(User).filter(User.id == student_id).first()
        if student:
            students_list.append({
                "id": student.id,
                "email": student.email,
                "total_sessions": data["total"],
                "completed_sessions": data["completed"],
                "last_session": data["last_date"].isoformat() if data["last_date"] else None
            })
    
    return {
        "students": sorted(students_list, key=lambda x: x.get("last_session") or "", reverse=True)
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
    
    # Sessions per day of week - use Python grouping instead of DAYNAME
    all_sessions = db.query(MentorSession).filter(MentorSession.mentor_id == mentor.id).all()
    
    from collections import defaultdict
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = defaultdict(int)
    
    for s in all_sessions:
        day_idx = s.scheduled_at.weekday()  # 0=Monday, 6=Sunday
        day_counts[day_names[day_idx]] += 1
    
    sessions_by_day_list = [
        {"day_name": day, "session_count": day_counts[day]}
        for day in day_names
    ]
    
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
            item["day_name"]: item["session_count"]
            for item in sessions_by_day_list
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
                "review_text": r.review_text,
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
    
    # Validate inputs
    if bio is not None:
        bio = bio.strip()
        if len(bio) < 50:
            raise HTTPException(status_code=400, detail="Bio must be at least 50 characters")
        if len(bio) > 2000:
            raise HTTPException(status_code=400, detail="Bio cannot exceed 2000 characters")
        mentor.bio = bio
    
    if expertise is not None:
        expertise = expertise.strip()
        if not expertise:
            raise HTTPException(status_code=400, detail="Expertise cannot be empty")
        # Validate expertise format (comma-separated tags)
        skills = [s.strip() for s in expertise.split(',')]
        if len(skills) < 1:
            raise HTTPException(status_code=400, detail="At least one skill required")
        if len(skills) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 skills allowed")
        for skill in skills:
            if len(skill) < 2 or len(skill) > 50:
                raise HTTPException(status_code=400, detail=f"Invalid skill length: {skill}")
        mentor.expertise = ','.join(skills)
    
    if hourly_rate is not None:
        if hourly_rate < 0:
            raise HTTPException(status_code=400, detail="Hourly rate cannot be negative")
        if hourly_rate > 1000:
            raise HTTPException(status_code=400, detail="Hourly rate cannot exceed $1000")
        if hourly_rate > 0 and hourly_rate < 10:
            raise HTTPException(status_code=400, detail="Hourly rate must be at least $10")
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
