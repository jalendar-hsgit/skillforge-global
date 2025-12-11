"""
Comprehensive Admin API endpoints.
All endpoints require admin role (admin or superadmin).
Includes audit logging for all actions.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os

from pydantic import BaseModel

from app.core.db import get_db
from app.core.security import get_current_admin, get_current_superadmin
from app.models.user import User, UserRole
from app.modelsx.mentor import Mentor, MentorSession, MentorStatus, SessionStatus
from app.modelsx.admin_log import AdminLog
from app.modelsx.platform_settings import PlatformSetting
from app.schemas.admin import (
    AdminDashboardStats, UserListItem, UserUpdateRole, UserSuspend,
    AdminLogResponse, AdminLogListResponse, PlatformSettings
)
from app.schemas.course import CourseItem

# Try to import subscription models (may not exist)
try:
    from app.modelsx.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
    HAS_SUBSCRIPTIONS = True
except ImportError:
    HAS_SUBSCRIPTIONS = False

# Try to import marketplace models (may not exist)
try:
    from app.modelsx.order import Order, CartItem, Coupon
    from app.modelsx.course import Course as CourseModel
    HAS_MARKETPLACE = True
except ImportError:
    HAS_MARKETPLACE = False

router = APIRouter(prefix="/admin", tags=["admin"])


def log_admin_action(
    db: Session,
    admin_user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[str] = None,
    request: Optional[Request] = None
):
    """Helper to create audit log entries"""
    log = AdminLog(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(log)
    db.commit()


# ============ Dashboard & Stats ============

@router.get("/dashboard/stats", response_model=AdminDashboardStats)
def get_dashboard_stats(
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard statistics for admin overview"""
    
    # User stats
    total_users = db.query(func.count(User.id)).scalar() or 0
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users_30d = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Mentor stats
    total_mentors = db.query(func.count(Mentor.id)).scalar() or 0
    pending_applications = db.query(func.count(Mentor.id)).filter(
        Mentor.status == MentorStatus.PENDING
    ).scalar() or 0
    
    # Session stats
    total_sessions = db.query(func.count(MentorSession.id)).scalar() or 0
    scheduled_sessions = db.query(func.count(MentorSession.id)).filter(
        MentorSession.status.in_([SessionStatus.PENDING, SessionStatus.CONFIRMED])
    ).scalar() or 0
    completed_sessions = db.query(func.count(MentorSession.id)).filter(
        MentorSession.status == SessionStatus.COMPLETED
    ).scalar() or 0
    
    # Revenue (sum of completed session prices)
    total_revenue = db.query(func.sum(MentorSession.price)).filter(
        MentorSession.status == SessionStatus.COMPLETED
    ).scalar() or 0.0
    
    return AdminDashboardStats(
        total_users=total_users,
        total_mentors=total_mentors,
        pending_mentor_applications=pending_applications,
        total_sessions=total_sessions,
        scheduled_sessions=scheduled_sessions,
        completed_sessions=completed_sessions,
        total_revenue=float(total_revenue),
        active_users_30d=active_users_30d
    )


# ============ User Management ============

@router.get("/users", response_model=List[UserListItem])
def get_all_users(
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users with optional filtering"""
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        UserListItem(
            id=u.id,
            email=u.email,
            role=(u.role.value if hasattr(u.role, "value") else str(u.role)),
            created_at=u.created_at
        )
        for u in users
    ]


@router.patch("/users/{user_id}/role", response_model=dict)
def update_user_role(
    user_id: int,
    role_update: UserUpdateRole,
    request: Request,
    admin_user: User = Depends(get_current_superadmin),  # Only superadmin can change roles
    db: Session = Depends(get_db)
):
    """Update user role (superadmin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate role
    try:
        new_role = UserRole(role_update.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Prevent self-demotion from superadmin
    if user.id == admin_user.id and new_role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=400,
            detail="Cannot demote yourself from superadmin"
        )
    
    old_role = user.role
    user.role = new_role
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_user_id=admin_user.id,
        action="update_user_role",
        resource_type="user",
        resource_id=user_id,
        details=f"Changed role from {old_role} to {new_role}",
        request=request
    )
    
    return {
        "message": f"User role updated to {new_role}",
        "user_id": user_id,
        "new_role": new_role
    }


@router.delete("/users/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    request: Request,
    admin_user: User = Depends(get_current_superadmin),  # Only superadmin can delete
    db: Session = Depends(get_db)
):
    """Delete a user (superadmin only) - WARNING: This is permanent"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user_email = user.email
    db.delete(user)
    
    # Log before commit
    log_admin_action(
        db=db,
        admin_user_id=admin_user.id,
        action="delete_user",
        resource_type="user",
        resource_id=user_id,
        details=f"Deleted user: {user_email}",
        request=request
    )
    
    db.commit()
    
    return {"message": f"User {user_email} deleted", "user_id": user_id}


# ============ Mentor Management ============

@router.get("/mentors/applications", response_model=dict)
def get_mentor_applications(
    status: Optional[str] = Query(None),
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List mentor applications with optional status filtering (admin only)"""
    query = db.query(Mentor)
    if status and status in [s.value for s in MentorStatus]:
        query = query.filter(Mentor.status == status)

    mentors = query.order_by(Mentor.created_at.desc()).all()

    applications = []
    for mentor in mentors:
        user = db.query(User).filter(User.id == mentor.user_id).first()
        email = user.email if user else "unknown@example.com"
        full_name = email.split('@')[0].replace('.', ' ').title()
        applications.append({
            "id": mentor.id,
            "user_id": mentor.user_id,
            "bio": mentor.bio,
            "expertise": mentor.expertise,
            "hourly_rate": mentor.hourly_rate,
            "status": mentor.status,
            "total_sessions": mentor.total_sessions,
            "average_rating": mentor.average_rating,
            "created_at": mentor.created_at,
            "user": {"full_name": full_name, "email": email}
        })

    return {"applications": applications}

@router.patch("/mentors/{mentor_id}/status", response_model=dict)
def update_mentor_status(
    mentor_id: int,
    status_update: dict,
    request: Request,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update mentor status with audit logging"""
    
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    new_status = status_update.get("status")
    if new_status not in ['approved', 'rejected', 'suspended']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    old_status = mentor.status
    mentor.status = new_status
    
    if new_status == 'approved' and not mentor.approved_at:
        mentor.approved_at = datetime.utcnow()
    
    mentor.updated_at = datetime.utcnow()
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_user_id=admin_user.id,
        action="update_mentor_status",
        resource_type="mentor",
        resource_id=mentor_id,
        details=f"Changed status from {old_status} to {new_status}",
        request=request
    )
    
    return {
        "message": f"Mentor status updated to {new_status}",
        "mentor_id": mentor_id,
        "old_status": old_status,
        "new_status": new_status
    }


# ============ Session Management ============

@router.patch("/sessions/{session_id}/status", response_model=dict)
def update_session_status(
    session_id: int,
    status_update: dict,
    request: Request,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update session status (e.g., cancel, mark no-show) with audit logging"""
    
    session = db.query(MentorSession).filter(MentorSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    new_status = status_update.get("status")
    reason = status_update.get("reason", "Admin action")
    
    if new_status not in ['cancelled', 'no_show', 'completed']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    old_status = session.status
    session.status = new_status
    
    if new_status in ['cancelled', 'no_show']:
        session.mentor_notes = f"{session.mentor_notes or ''}\n[Admin] {reason}".strip()
    
    db.commit()
    
    # Log action
    log_admin_action(
        db=db,
        admin_user_id=admin_user.id,
        action="update_session_status",
        resource_type="session",
        resource_id=session_id,
        details=f"Changed status from {old_status} to {new_status}. Reason: {reason}",
        request=request
    )
    
    return {
        "message": f"Session status updated to {new_status}",
        "session_id": session_id,
        "old_status": old_status,
        "new_status": new_status
    }


# ============ Audit Logs ============

@router.get("/logs", response_model=AdminLogListResponse)
def get_audit_logs(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering"""
    
    query = db.query(AdminLog)
    
    if action:
        query = query.filter(AdminLog.action == action)
    
    if resource_type:
        query = query.filter(AdminLog.resource_type == resource_type)
    
    total = query.count()
    logs = query.order_by(AdminLog.created_at.desc()).offset(offset).limit(limit).all()
    
    # Enrich with admin email
    log_responses = []
    for log in logs:
        admin_email = None
        if log.admin_user_id:
            admin = db.query(User).filter(User.id == log.admin_user_id).first()
            admin_email = admin.email if admin else None
        
        log_responses.append(
            AdminLogResponse(
                id=log.id,
                admin_user_id=log.admin_user_id,
                admin_email=admin_email,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                details=log.details,
                ip_address=log.ip_address,
                created_at=log.created_at
            )
        )
    
    return AdminLogListResponse(logs=log_responses, total=total)


# ============ Platform Settings ============

def get_setting_value(db: Session, key: str, default=None):
    """Helper to get a setting value from database"""
    setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if setting:
        return setting.get_value()
    return default


def set_setting_value(db: Session, key: str, value, value_type: str, description: str = None):
    """Helper to set a setting value in database"""
    setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    
    # Encode value based on type
    if value_type == "json":
        encoded = json.dumps(value)
    elif value_type == "boolean":
        encoded = "true" if value else "false"
    else:
        encoded = str(value)
    
    if setting:
        # Update existing
        setting.value = encoded
        setting.value_type = value_type
        if description:
            setting.description = description
    else:
        # Create new
        setting = PlatformSetting(
            key=key,
            value=encoded,
            value_type=value_type,
            description=description
        )
        db.add(setting)
    
    db.commit()
    return setting


@router.get("/settings/public", response_model=PlatformSettings)
def get_public_platform_settings(db: Session = Depends(get_db)):
    """Get platform settings (public access for reading)"""
    return PlatformSettings(
        platform_name=get_setting_value(db, "platform_name", "SkillForge Global"),
        support_email=get_setting_value(db, "support_email", "support@skillforge.com"),
        allow_new_registrations=get_setting_value(db, "allow_new_registrations", True),
        mentor_approval_required=get_setting_value(db, "mentor_approval_required", True),
        maintenance_mode=get_setting_value(db, "maintenance_mode", False),
        featured_courses=get_setting_value(db, "featured_courses", [])
    )


@router.get("/settings", response_model=PlatformSettings)
def get_platform_settings(
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform settings from database (admin only)"""
    return PlatformSettings(
        platform_name=get_setting_value(db, "platform_name", "SkillForge Global"),
        support_email=get_setting_value(db, "support_email", "support@skillforge.com"),
        allow_new_registrations=get_setting_value(db, "allow_new_registrations", True),
        mentor_approval_required=get_setting_value(db, "mentor_approval_required", True),
        maintenance_mode=get_setting_value(db, "maintenance_mode", False),
        featured_courses=get_setting_value(db, "featured_courses", [])
    )


@router.post("/settings", response_model=dict)
def update_platform_settings(
    settings: PlatformSettings,
    request: Request,
    admin_user: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """Update platform settings (superadmin only) - now persisted to database"""
    
    # Store each setting in database
    set_setting_value(db, "platform_name", settings.platform_name, "string", "Platform display name")
    set_setting_value(db, "support_email", settings.support_email, "string", "Support contact email")
    set_setting_value(db, "allow_new_registrations", settings.allow_new_registrations, "boolean", "Allow new user signups")
    set_setting_value(db, "mentor_approval_required", settings.mentor_approval_required, "boolean", "Require admin approval for mentors")
    set_setting_value(db, "maintenance_mode", settings.maintenance_mode, "boolean", "Platform maintenance mode")
    set_setting_value(db, "featured_courses", settings.featured_courses, "json", "List of featured course slugs")
    
    # Clear settings cache to force refresh
    from app.services.settings_service import clear_settings_cache
    clear_settings_cache()
    
    log_admin_action(
        db=db,
        admin_user_id=admin_user.id,
        action="update_platform_settings",
        resource_type="settings",
        details=json.dumps(settings.dict()),
        request=request
    )
    
    return {"message": "Settings updated successfully", "settings": settings.dict()}


@router.post("/clear-rate-limits")
def clear_rate_limits(
    admin_user: User = Depends(get_current_superadmin)
):
    """Clear all rate limit caches (superadmin only) - useful for development/testing"""
    from app.services.rate_limiter import rate_limit_cache
    
    count = len(rate_limit_cache)
    rate_limit_cache.clear()
    
    return {
        "message": "Rate limit cache cleared successfully",
        "cleared_entries": count
    }


# ============ Analytics ============

@router.get("/analytics")
def get_analytics(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get platform analytics for specified timeframe"""
    
    # Parse timeframe
    timeframe_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365
    }
    days = timeframe_map[timeframe]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # User growth (simplified - could be enhanced with daily counts)
    total_users = db.query(User).count()
    new_users = db.query(User).filter(User.created_at >= start_date).count()
    
    # Session stats
    total_sessions = db.query(MentorSession).filter(
        MentorSession.scheduled_at >= start_date
    ).count()
    
    completed_sessions = db.query(MentorSession).filter(
        and_(
            MentorSession.scheduled_at >= start_date,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).count()
    
    cancelled_sessions = db.query(MentorSession).filter(
        and_(
            MentorSession.scheduled_at >= start_date,
            MentorSession.status == SessionStatus.CANCELLED
        )
    ).count()
    
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Top mentors
    top_mentors = db.query(
        Mentor.user_id,
        User.email,
        func.count(MentorSession.id).label("total_sessions"),
        func.avg(MentorSession.rating).label("avg_rating"),
        func.sum(MentorSession.price_paid).label("total_earnings")
    ).join(
        User, Mentor.user_id == User.id
    ).join(
        MentorSession, MentorSession.mentor_id == Mentor.id
    ).filter(
        MentorSession.scheduled_at >= start_date
    ).group_by(
        Mentor.user_id, User.email
    ).order_by(
        func.count(MentorSession.id).desc()
    ).limit(10).all()
    
    top_mentors_data = [
        {
            "id": m.user_id,
            "email": m.email,
            "total_sessions": m.total_sessions,
            "avg_rating": float(m.avg_rating) if m.avg_rating else None,
            "total_earnings": float(m.total_earnings) if m.total_earnings else 0.0
        }
        for m in top_mentors
    ]
    
    return {
        "user_growth": [
            {"date": start_date.strftime("%Y-%m-%d"), "count": new_users},
            {"date": datetime.utcnow().strftime("%Y-%m-%d"), "count": total_users}
        ],
        "revenue_trend": [],  # Placeholder for future implementation
        "session_stats": {
            "total": total_sessions,
            "completed": completed_sessions,
            "cancelled": cancelled_sessions,
            "completion_rate": round(completion_rate, 1)
        },
        "top_mentors": top_mentors_data,
        "popular_courses": []  # Placeholder for course enrollment tracking
    }


# ============ Course Management ============

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "courses.json")
DATA_PATH = os.path.normpath(DATA_PATH)

def _load_courses():
    """Load courses from JSON file"""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_courses(items):
    """Save courses to JSON file"""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

@router.get("/courses")
def admin_list_courses(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get all courses with admin metadata"""
    courses = _load_courses()
    
    # Add enrollment counts (placeholder - would need enrollments table)
    for course in courses:
        course["enrollments"] = 0  # TODO: Get from enrollments table
        course["completion_rate"] = 0  # TODO: Calculate from progress
        course["published"] = True  # TODO: Add published field to schema
    
    return courses

@router.post("/courses")
def admin_create_course(
    course: CourseItem,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Create a new course"""
    courses = _load_courses()
    
    # Check for duplicate ID or path
    if any(c["id"] == course.id for c in courses):
        raise HTTPException(status_code=400, detail="Course ID already exists")
    if any(c["path"] == course.path for c in courses):
        raise HTTPException(status_code=400, detail="Course path already exists")
    
    new_course = course.model_dump()
    courses.append(new_course)
    _save_courses(courses)
    
    # Log action
    log_admin_action(
        db, admin_user.id, "create", "course",
        resource_id=None,
        details=f"Created course: {course.title}",
        request=request
    )
    
    return new_course

@router.put("/courses/{course_id}")
def admin_update_course(
    course_id: str,
    course: CourseItem,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Update an existing course"""
    courses = _load_courses()
    
    # Find course index
    idx = next((i for i, c in enumerate(courses) if c["id"] == course_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Update course
    courses[idx] = course.model_dump()
    _save_courses(courses)
    
    # Log action
    log_admin_action(
        db, admin_user.id, "update", "course",
        resource_id=None,
        details=f"Updated course: {course.title}",
        request=request
    )
    
    return courses[idx]

@router.delete("/courses/{course_id}")
def admin_delete_course(
    course_id: str,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Delete a course"""
    courses = _load_courses()
    
    # Find and remove course
    original_count = len(courses)
    courses = [c for c in courses if c["id"] != course_id]
    
    if len(courses) == original_count:
        raise HTTPException(status_code=404, detail="Course not found")
    
    _save_courses(courses)
    
    # Log action
    log_admin_action(
        db, admin_user.id, "delete", "course",
        resource_id=None,
        details=f"Deleted course ID: {course_id}",
        request=request
    )
    
    return {"message": "Course deleted successfully"}

@router.post("/courses/bulk-delete")
def admin_bulk_delete_courses(
    course_ids: List[str],
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Delete multiple courses at once"""
    courses = _load_courses()
    
    original_count = len(courses)
    courses = [c for c in courses if c["id"] not in course_ids]
    deleted_count = original_count - len(courses)
    
    _save_courses(courses)
    
    # Log action
    log_admin_action(
        db, admin_user.id, "bulk_delete", "course",
        resource_id=None,
        details=f"Deleted {deleted_count} courses",
        request=request
    )
    
    return {
        "message": f"Deleted {deleted_count} courses successfully",
        "deleted_count": deleted_count
    }

@router.post("/courses/{course_id}/toggle-featured")
def admin_toggle_featured_course(
    course_id: str,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Toggle featured status for a course"""
    courses = _load_courses()
    
    # Find course
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Toggle featured (add field if it doesn't exist)
    course["featured"] = not course.get("featured", False)
    _save_courses(courses)
    
    # Log action
    log_admin_action(
        db, admin_user.id, "update", "course",
        resource_id=None,
        details=f"Toggled featured for course: {course['title']} -> {course['featured']}",
        request=request
    )
    
    return course


# ============ Revenue & Financial Analytics ============

@router.get("/revenue/overview")
def get_revenue_overview(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y|all)$"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get revenue overview and statistics"""
    
    # Parse timeframe
    if timeframe == "all":
        start_date = datetime(2020, 1, 1)
    else:
        timeframe_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = timeframe_map[timeframe]
        start_date = datetime.utcnow() - timedelta(days=days)
    
    # Session-based revenue (from mentor sessions)
    session_revenue_query = db.query(
        func.sum(MentorSession.price_paid).label("total"),
        func.count(MentorSession.id).label("count")
    ).filter(
        and_(
            MentorSession.status == SessionStatus.COMPLETED,
            MentorSession.completed_at >= start_date,
            MentorSession.price_paid.isnot(None)
        )
    ).first()
    
    session_revenue = float(session_revenue_query.total or 0)
    session_count = session_revenue_query.count or 0
    
    # Subscription revenue (if available)
    subscription_revenue = 0
    active_subscriptions = 0
    subscription_mrr = 0
    
    if HAS_SUBSCRIPTIONS:
        try:
            # Calculate subscription revenue (simplified - would need payment records)
            active_subs = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).all()
            
            active_subscriptions = len(active_subs)
            
            # Rough MRR calculation based on plan pricing
            plan_prices = {
                SubscriptionPlan.PRO: 29.99,
                SubscriptionPlan.PREMIUM: 79.99,
                SubscriptionPlan.ENTERPRISE: 199.99
            }
            
            for sub in active_subs:
                subscription_mrr += plan_prices.get(sub.plan, 0)
            
            # Estimate total subscription revenue for timeframe
            if timeframe == "30d" or timeframe == "all":
                subscription_revenue = subscription_mrr
            elif timeframe == "7d":
                subscription_revenue = subscription_mrr / 4
            elif timeframe == "90d":
                subscription_revenue = subscription_mrr * 3
            elif timeframe == "1y":
                subscription_revenue = subscription_mrr * 12
                
        except Exception as e:
            print(f"Error calculating subscription revenue: {e}")
    
    # Total revenue
    total_revenue = session_revenue + subscription_revenue
    
    # Average transaction value
    avg_transaction = session_revenue / session_count if session_count > 0 else 0
    
    # Mentor payouts (70% of session revenue - example split)
    mentor_payouts = session_revenue * 0.7
    platform_revenue = session_revenue * 0.3
    
    return {
        "timeframe": timeframe,
        "total_revenue": round(total_revenue, 2),
        "session_revenue": round(session_revenue, 2),
        "subscription_revenue": round(subscription_revenue, 2),
        "session_count": session_count,
        "avg_transaction_value": round(avg_transaction, 2),
        "active_subscriptions": active_subscriptions,
        "monthly_recurring_revenue": round(subscription_mrr, 2),
        "mentor_payouts": round(mentor_payouts, 2),
        "platform_revenue": round(platform_revenue, 2)
    }


@router.get("/revenue/transactions")
def get_revenue_transactions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get recent payment transactions"""
    
    # Get completed sessions with payment info
    transactions = db.query(MentorSession).filter(
        and_(
            MentorSession.status == SessionStatus.COMPLETED,
            MentorSession.price_paid.isnot(None)
        )
    ).order_by(
        MentorSession.completed_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Get mentor and student info
    from app.modelsx.mentor import Mentor as MentorModel
    
    result = []
    for session in transactions:
        mentor = db.query(MentorModel).filter(MentorModel.id == session.mentor_id).first()
        student = db.query(User).filter(User.id == session.student_id).first()
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first() if mentor else None
        
        result.append({
            "id": session.id,
            "date": session.completed_at.isoformat() if session.completed_at else None,
            "amount": float(session.price_paid) if session.price_paid else 0,
            "mentor_email": mentor_user.email if mentor_user else "Unknown",
            "student_email": student.email if student else "Unknown",
            "duration_minutes": session.duration_minutes,
            "payment_intent_id": session.payment_intent_id,
            "status": session.status.value
        })
    
    total = db.query(func.count(MentorSession.id)).filter(
        and_(
            MentorSession.status == SessionStatus.COMPLETED,
            MentorSession.price_paid.isnot(None)
        )
    ).scalar()
    
    return {
        "transactions": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/revenue/mentor-earnings")
def get_mentor_earnings(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y|all)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get mentor earnings leaderboard"""
    
    # Parse timeframe
    if timeframe == "all":
        start_date = datetime(2020, 1, 1)
    else:
        timeframe_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = timeframe_map[timeframe]
        start_date = datetime.utcnow() - timedelta(days=days)
    
    # Aggregate earnings per mentor
    earnings = db.query(
        Mentor.user_id,
        User.email,
        func.sum(MentorSession.price_paid).label("total_earnings"),
        func.count(MentorSession.id).label("session_count"),
        func.avg(MentorSession.rating).label("avg_rating")
    ).join(
        User, Mentor.user_id == User.id
    ).join(
        MentorSession, MentorSession.mentor_id == Mentor.id
    ).filter(
        and_(
            MentorSession.status == SessionStatus.COMPLETED,
            MentorSession.completed_at >= start_date,
            MentorSession.price_paid.isnot(None)
        )
    ).group_by(
        Mentor.user_id, User.email
    ).order_by(
        func.sum(MentorSession.price_paid).desc()
    ).limit(limit).all()
    
    result = []
    for e in earnings:
        # Calculate mentor payout (70% example)
        gross_earnings = float(e.total_earnings) if e.total_earnings else 0
        mentor_payout = gross_earnings * 0.7
        platform_fee = gross_earnings * 0.3
        
        result.append({
            "mentor_id": e.user_id,
            "email": e.email,
            "total_earnings": round(gross_earnings, 2),
            "mentor_payout": round(mentor_payout, 2),
            "platform_fee": round(platform_fee, 2),
            "session_count": e.session_count,
            "avg_rating": round(float(e.avg_rating), 2) if e.avg_rating else None
        })
    
    return {
        "timeframe": timeframe,
        "mentors": result
    }


# ============ Marketplace & Orders Management ============

@router.get("/marketplace/orders")
def get_all_orders(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get all marketplace orders with filters"""
    
    if not HAS_MARKETPLACE:
        raise HTTPException(status_code=501, detail="Marketplace module not available")
    
    query = db.query(Order).join(User, Order.user_id == User.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for order in orders:
        user = db.query(User).filter(User.id == order.user_id).first()
        course = db.query(CourseModel).filter(CourseModel.id == order.course_id).first()
        
        result.append({
            "id": order.id,
            "order_number": order.order_number,
            "user_email": user.email if user else "Unknown",
            "course_title": course.title if course else "Unknown",
            "status": order.status,
            "amount": float(order.amount) if order.amount else 0,
            "discount_amount": float(order.discount_amount) if order.discount_amount else 0,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "coupon_code": order.coupon_code
        })
    
    return {
        "orders": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/marketplace/stats")
def get_marketplace_stats(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y|all)$"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get marketplace statistics and analytics"""
    
    if not HAS_MARKETPLACE:
        raise HTTPException(status_code=501, detail="Marketplace module not available")
    
    # Parse timeframe
    if timeframe == "all":
        start_date = datetime(2020, 1, 1)
    else:
        timeframe_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = timeframe_map[timeframe]
        start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total orders and revenue
    orders_query = db.query(
        func.count(Order.id).label("count"),
        func.sum(Order.amount).label("revenue")
    ).filter(
        and_(
            Order.created_at >= start_date,
            Order.status == "completed"
        )
    ).first()
    
    total_orders = orders_query.count or 0
    total_revenue = float(orders_query.revenue or 0)
    
    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Top selling courses
    top_courses = db.query(
        CourseModel.id,
        CourseModel.title,
        func.count(Order.id).label("order_count"),
        func.sum(Order.amount).label("revenue")
    ).join(
        Order, Order.course_id == CourseModel.id
    ).filter(
        and_(
            Order.created_at >= start_date,
            Order.status == "completed"
        )
    ).group_by(
        CourseModel.id, CourseModel.title
    ).order_by(
        func.count(Order.id).desc()
    ).limit(10).all()
    
    top_courses_data = [
        {
            "course_id": c.id,
            "title": c.title,
            "sales": c.order_count,
            "revenue": round(float(c.revenue or 0), 2)
        }
        for c in top_courses
    ]
    
    # Active coupons
    active_coupons = db.query(Coupon).filter(
        and_(
            Coupon.is_active == True,
            or_(
                Coupon.expires_at.is_(None),
                Coupon.expires_at > datetime.utcnow()
            )
        )
    ).count()
    
    return {
        "timeframe": timeframe,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "avg_order_value": round(avg_order_value, 2),
        "active_coupons": active_coupons,
        "top_courses": top_courses_data
    }


@router.get("/marketplace/coupons")
def get_all_coupons(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get all coupon codes"""
    
    if not HAS_MARKETPLACE:
        raise HTTPException(status_code=501, detail="Marketplace module not available")
    
    coupons = db.query(Coupon).order_by(Coupon.created_at.desc()).all()
    
    result = []
    for coupon in coupons:
        result.append({
            "id": coupon.id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": float(coupon.discount_value) if coupon.discount_value else 0,
            "is_active": coupon.is_active,
            "expires_at": coupon.expires_at.isoformat() if coupon.expires_at else None,
            "max_uses": coupon.max_uses,
            "current_uses": coupon.current_uses,
            "created_at": coupon.created_at.isoformat() if coupon.created_at else None
        })
    
    return result


class CreateCouponRequest(BaseModel):
    code: str
    discount_type: str  # "percentage" or "fixed"
    discount_value: float
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None


@router.post("/marketplace/coupons")
def create_coupon(
    req: CreateCouponRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Create a new coupon code"""
    
    if not HAS_MARKETPLACE:
        raise HTTPException(status_code=501, detail="Marketplace module not available")
    
    # Check if code already exists
    existing = db.query(Coupon).filter(Coupon.code == req.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    
    # Validate discount type and value
    if req.discount_type not in ["percentage", "fixed"]:
        raise HTTPException(status_code=400, detail="Invalid discount type")
    
    if req.discount_type == "percentage" and (req.discount_value < 0 or req.discount_value > 100):
        raise HTTPException(status_code=400, detail="Percentage must be between 0 and 100")
    
    # Create coupon
    coupon = Coupon(
        code=req.code.upper(),
        discount_type=req.discount_type,
        discount_value=req.discount_value,
        max_uses=req.max_uses,
        expires_at=req.expires_at,
        is_active=True,
        current_uses=0
    )
    
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    
    # Log action
    log_admin_action(
        db, admin_user.id, "create", "coupon",
        resource_id=coupon.id,
        details=f"Created coupon: {coupon.code} ({req.discount_type}: {req.discount_value})",
        request=request
    )
    
    return {
        "id": coupon.id,
        "code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": float(coupon.discount_value),
        "is_active": coupon.is_active
    }


@router.patch("/marketplace/coupons/{coupon_id}/toggle")
def toggle_coupon(
    coupon_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Toggle coupon active status"""
    
    if not HAS_MARKETPLACE:
        raise HTTPException(status_code=501, detail="Marketplace module not available")
    
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    coupon.is_active = not coupon.is_active
    db.commit()
    
    # Log action
    log_admin_action(
        db, admin_user.id, "update", "coupon",
        resource_id=coupon.id,
        details=f"Toggled coupon {coupon.code} -> active: {coupon.is_active}",
        request=request
    )
    
    return {"id": coupon.id, "code": coupon.code, "is_active": coupon.is_active}


@router.delete("/marketplace/coupons/{coupon_id}")
def delete_coupon(
    coupon_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Delete a coupon"""
    
    if not HAS_MARKETPLACE:
        raise HTTPException(status_code=501, detail="Marketplace module not available")
    
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    code = coupon.code
    db.delete(coupon)
    db.commit()
    
    # Log action
    log_admin_action(
        db, admin_user.id, "delete", "coupon",
        resource_id=coupon_id,
        details=f"Deleted coupon: {code}",
        request=request
    )
    
    return {"message": "Coupon deleted successfully"}


@router.post("/marketplace/orders/{order_id}/refund")
def refund_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Process a refund for an order"""
    
    if not HAS_MARKETPLACE:
        raise HTTPException(status_code=501, detail="Marketplace module not available")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "refunded":
        raise HTTPException(status_code=400, detail="Order already refunded")
    
    # Update order status
    order.status = "refunded"
    order.payment_status = "refunded"
    db.commit()
    
    # Log action
    user = db.query(User).filter(User.id == order.user_id).first()
    log_admin_action(
        db, admin_user.id, "refund", "order",
        resource_id=order.id,
        details=f"Refunded order {order.order_number} for user {user.email if user else 'unknown'}",
        request=request
    )
    
    return {
        "message": "Order refunded successfully",
        "order_id": order.id,
        "order_number": order.order_number,
        "status": order.status
    }


# ============ User Analytics & Engagement ============

@router.get("/user-analytics/overview")
def get_user_analytics_overview(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get user engagement overview and metrics"""
    
    # Parse timeframe
    timeframe_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = timeframe_map[timeframe]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total users
    total_users = db.query(User).count()
    new_users = db.query(User).filter(User.created_at >= start_date).count()
    
    # Calculate DAU, WAU, MAU using login activity
    # Note: This is simplified - in production, track login events in a separate table
    now = datetime.utcnow()
    
    # Users created in last 24h (proxy for DAU)
    dau_threshold = now - timedelta(days=1)
    dau = db.query(User).filter(User.created_at >= dau_threshold).count()
    
    # Users created in last 7 days (proxy for WAU)
    wau_threshold = now - timedelta(days=7)
    wau = db.query(User).filter(User.created_at >= wau_threshold).count()
    
    # Users created in last 30 days (proxy for MAU)
    mau_threshold = now - timedelta(days=30)
    mau = db.query(User).filter(User.created_at >= mau_threshold).count()
    
    # User role distribution
    role_distribution = {}
    for role in UserRole:
        count = db.query(User).filter(User.role == role).count()
        role_distribution[role.value] = count
    
    # Session activity (completed sessions as proxy for active users)
    active_users_with_sessions = db.query(func.count(func.distinct(MentorSession.student_id))).filter(
        and_(
            MentorSession.scheduled_at >= start_date,
            MentorSession.status == SessionStatus.COMPLETED
        )
    ).scalar() or 0
    
    # Engagement rate
    engagement_rate = (active_users_with_sessions / total_users * 100) if total_users > 0 else 0
    
    # Growth rate
    previous_start = start_date - timedelta(days=days)
    previous_users = db.query(User).filter(
        and_(
            User.created_at >= previous_start,
            User.created_at < start_date
        )
    ).count()
    
    growth_rate = ((new_users - previous_users) / previous_users * 100) if previous_users > 0 else 0
    
    return {
        "timeframe": timeframe,
        "total_users": total_users,
        "new_users": new_users,
        "growth_rate": round(growth_rate, 2),
        "dau": dau,
        "wau": wau,
        "mau": mau,
        "engagement_rate": round(engagement_rate, 2),
        "active_users_with_sessions": active_users_with_sessions,
        "role_distribution": role_distribution
    }


@router.get("/user-analytics/cohorts")
def get_retention_cohorts(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get retention cohort analysis"""
    
    # Get users grouped by signup month
    cohorts = []
    
    # Last 6 months of cohorts
    for i in range(6):
        cohort_start = datetime.utcnow() - timedelta(days=(i+1)*30)
        cohort_end = datetime.utcnow() - timedelta(days=i*30)
        
        # Users who signed up in this cohort
        cohort_users = db.query(User).filter(
            and_(
                User.created_at >= cohort_start,
                User.created_at < cohort_end
            )
        ).all()
        
        cohort_size = len(cohort_users)
        if cohort_size == 0:
            continue
        
        # Check how many are still active (have sessions in last 30 days)
        user_ids = [u.id for u in cohort_users]
        active_count = db.query(func.count(func.distinct(MentorSession.student_id))).filter(
            and_(
                MentorSession.student_id.in_(user_ids),
                MentorSession.scheduled_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).scalar() or 0
        
        retention_rate = (active_count / cohort_size * 100) if cohort_size > 0 else 0
        
        cohorts.append({
            "cohort_month": cohort_start.strftime("%Y-%m"),
            "cohort_size": cohort_size,
            "active_users": active_count,
            "retention_rate": round(retention_rate, 2)
        })
    
    return {"cohorts": cohorts}


@router.get("/user-analytics/activity")
def get_user_activity_stats(
    timeframe: str = Query("30d", regex="^(7d|30d|90d)$"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get detailed user activity statistics"""
    
    timeframe_map = {"7d": 7, "30d": 30, "90d": 90}
    days = timeframe_map[timeframe]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Session participation
    students_with_sessions = db.query(
        func.count(func.distinct(MentorSession.student_id))
    ).filter(
        MentorSession.scheduled_at >= start_date
    ).scalar() or 0
    
    # Mentor activity
    active_mentors = db.query(
        func.count(func.distinct(MentorSession.mentor_id))
    ).filter(
        and_(
            MentorSession.scheduled_at >= start_date,
            MentorSession.status.in_([SessionStatus.COMPLETED, SessionStatus.SCHEDULED])
        )
    ).scalar() or 0
    
    # Purchase activity (if marketplace available)
    purchasing_users = 0
    if HAS_MARKETPLACE:
        try:
            purchasing_users = db.query(
                func.count(func.distinct(Order.user_id))
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == "completed"
                )
            ).scalar() or 0
        except:
            pass
    
    # User segmentation
    total_users = db.query(User).count()
    
    segments = {
        "highly_active": students_with_sessions,  # Users with sessions
        "purchasers": purchasing_users,  # Users who made purchases
        "mentors": active_mentors,  # Active mentors
        "inactive": total_users - students_with_sessions  # Users with no sessions
    }
    
    return {
        "timeframe": timeframe,
        "segments": segments,
        "total_users": total_users
    }


@router.get("/user-analytics/popular-content")
def get_popular_content(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Get most popular courses and mentors"""
    
    timeframe_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = timeframe_map[timeframe]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Most booked mentors
    popular_mentors = db.query(
        Mentor.user_id,
        User.email,
        func.count(MentorSession.id).label("session_count"),
        func.avg(MentorSession.rating).label("avg_rating")
    ).join(
        User, Mentor.user_id == User.id
    ).join(
        MentorSession, MentorSession.mentor_id == Mentor.id
    ).filter(
        MentorSession.scheduled_at >= start_date
    ).group_by(
        Mentor.user_id, User.email
    ).order_by(
        func.count(MentorSession.id).desc()
    ).limit(10).all()
    
    popular_mentors_data = [
        {
            "mentor_id": m.user_id,
            "email": m.email,
            "bookings": m.session_count,
            "avg_rating": round(float(m.avg_rating), 2) if m.avg_rating else None
        }
        for m in popular_mentors
    ]
    
    # Most purchased courses (if marketplace available)
    popular_courses = []
    if HAS_MARKETPLACE:
        try:
            courses = db.query(
                CourseModel.id,
                CourseModel.title,
                func.count(Order.id).label("purchases")
            ).join(
                Order, Order.course_id == CourseModel.id
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == "completed"
                )
            ).group_by(
                CourseModel.id, CourseModel.title
            ).order_by(
                func.count(Order.id).desc()
            ).limit(10).all()
            
            popular_courses = [
                {
                    "course_id": c.id,
                    "title": c.title,
                    "purchases": c.purchases
                }
                for c in courses
            ]
        except:
            pass
    
    return {
        "timeframe": timeframe,
        "popular_mentors": popular_mentors_data,
        "popular_courses": popular_courses
    }


@router.get("/user-analytics/churn-risk")
def get_churn_risk_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """Identify users at risk of churning"""
    
    # Users who signed up more than 30 days ago but have no recent activity
    signup_threshold = datetime.utcnow() - timedelta(days=30)
    activity_threshold = datetime.utcnow() - timedelta(days=14)
    
    # Get all users who signed up 30+ days ago
    older_users = db.query(User).filter(User.created_at < signup_threshold).all()
    
    at_risk_users = []
    
    for user in older_users:
        # Check if they have any recent sessions
        recent_sessions = db.query(MentorSession).filter(
            and_(
                or_(
                    MentorSession.student_id == user.id,
                    MentorSession.mentor_id == user.id
                ),
                MentorSession.scheduled_at >= activity_threshold
            )
        ).count()
        
        # Check recent orders
        recent_orders = 0
        if HAS_MARKETPLACE:
            try:
                recent_orders = db.query(Order).filter(
                    and_(
                        Order.user_id == user.id,
                        Order.created_at >= activity_threshold
                    )
                ).count()
            except:
                pass
        
        # If no recent activity, mark as at-risk
        if recent_sessions == 0 and recent_orders == 0:
            days_since_signup = (datetime.utcnow() - user.created_at).days
            
            at_risk_users.append({
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
                "days_since_signup": days_since_signup,
                "last_activity": "30+ days ago",
                "risk_level": "high" if days_since_signup > 60 else "medium"
            })
    
    # Limit to top 50 at-risk users
    at_risk_users = at_risk_users[:50]
    
    return {
        "at_risk_count": len(at_risk_users),
        "users": at_risk_users
    }


# ==================== Email & Notifications Management ====================

from pydantic import BaseModel, EmailStr
from typing import List

class BroadcastEmailRequest(BaseModel):
    subject: str
    html_content: str
    text_content: str
    recipient_filter: str = "all"  # all, students, mentors, at_risk
    role_filter: Optional[str] = None

class EmailTemplate(BaseModel):
    id: Optional[int] = None
    name: str
    subject: str
    html_content: str
    text_content: str
    created_at: Optional[datetime] = None

# In-memory storage for email templates and history (can be moved to DB later)
email_templates: List[EmailTemplate] = []
notification_history: List[dict] = []
template_id_counter = 1

@router.post("/notifications/broadcast")
async def send_broadcast_email(
    request: BroadcastEmailRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send broadcast email to filtered users"""
    from app.services.email_service import EmailService
    
    try:
        # Get filtered user list
        query = db.query(User)
        
        if request.recipient_filter == "students":
            query = query.filter(User.role == "student")
        elif request.recipient_filter == "mentors":
            query = query.filter(User.role == "mentor")
        elif request.recipient_filter == "at_risk":
            # Users with no activity in 30 days
            activity_threshold = datetime.utcnow() - timedelta(days=30)
            active_user_ids = db.query(Session.user_id).filter(
                Session.scheduled_at >= activity_threshold
            ).distinct().all()
            active_ids = [uid[0] for uid in active_user_ids]
            query = query.filter(~User.id.in_(active_ids))
        
        if request.role_filter:
            query = query.filter(User.role == request.role_filter)
        
        users = query.all()
        
        # Send emails
        email_service = EmailService()
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                await email_service.send_email(
                    to_email=user.email,
                    subject=request.subject,
                    html_content=request.html_content,
                    text_content=request.text_content
                )
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send email to {user.email}: {str(e)}")
        
        # Log notification
        notification_record = {
            "id": len(notification_history) + 1,
            "subject": request.subject,
            "recipient_filter": request.recipient_filter,
            "recipient_count": len(users),
            "sent_count": sent_count,
            "failed_count": failed_count,
            "sent_by": current_admin["email"],
            "sent_at": datetime.utcnow().isoformat(),
        }
        notification_history.append(notification_record)
        
        # Audit log
        await log_admin_action(
            db=db,
            admin_id=current_admin["id"],
            action="send_broadcast_email",
            details={
                "subject": request.subject,
                "filter": request.recipient_filter,
                "sent": sent_count,
                "failed": failed_count
            }
        )
        
        return {
            "success": True,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_recipients": len(users)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/history")
async def get_notification_history(
    current_admin: dict = Depends(get_current_admin),
    limit: int = 50,
    offset: int = 0
):
    """Get notification send history"""
    # Reverse to show most recent first
    history = list(reversed(notification_history))
    
    return {
        "total": len(history),
        "notifications": history[offset:offset+limit]
    }


@router.get("/notifications/templates")
async def get_email_templates(
    current_admin: dict = Depends(get_current_admin)
):
    """Get all email templates"""
    return {"templates": email_templates}


@router.post("/notifications/templates")
async def create_email_template(
    template: EmailTemplate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    global template_id_counter
    
    template.id = template_id_counter
    template.created_at = datetime.utcnow()
    template_id_counter += 1
    
    email_templates.append(template)
    
    await log_admin_action(
        db=db,
        admin_id=current_admin["id"],
        action="create_email_template",
        details={"template_name": template.name}
    )
    
    return {"success": True, "template": template}


@router.put("/notifications/templates/{template_id}")
async def update_email_template(
    template_id: int,
    updated_template: EmailTemplate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update an email template"""
    for i, template in enumerate(email_templates):
        if template.id == template_id:
            updated_template.id = template_id
            updated_template.created_at = template.created_at
            email_templates[i] = updated_template
            
            await log_admin_action(
                db=db,
                admin_id=current_admin["id"],
                action="update_email_template",
                details={"template_id": template_id, "template_name": updated_template.name}
            )
            
            return {"success": True, "template": updated_template}
    
    raise HTTPException(status_code=404, detail="Template not found")


@router.delete("/notifications/templates/{template_id}")
async def delete_email_template(
    template_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete an email template"""
    global email_templates
    
    for i, template in enumerate(email_templates):
        if template.id == template_id:
            deleted_template = email_templates.pop(i)
            
            await log_admin_action(
                db=db,
                admin_id=current_admin["id"],
                action="delete_email_template",
                details={"template_id": template_id, "template_name": deleted_template.name}
            )
            
            return {"success": True}
    
    raise HTTPException(status_code=404, detail="Template not found")


@router.get("/notifications/stats")
async def get_notification_stats(
    current_admin: dict = Depends(get_current_admin)
):
    """Get notification statistics"""
    total_sent = sum(n.get("sent_count", 0) for n in notification_history)
    total_failed = sum(n.get("failed_count", 0) for n in notification_history)
    
    # Recent notifications (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_notifications = [
        n for n in notification_history
        if datetime.fromisoformat(n["sent_at"]) >= seven_days_ago
    ]
    
    return {
        "total_notifications_sent": len(notification_history),
        "total_emails_sent": total_sent,
        "total_emails_failed": total_failed,
        "success_rate": round((total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0, 2),
        "recent_notifications": len(recent_notifications),
        "templates_count": len(email_templates)
    }

