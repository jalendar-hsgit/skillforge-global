"""
Admin Dashboard Metrics API
Aggregated metrics for admin monitoring and analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, List, Any

from app.core.db import SessionLocal
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin-metrics", tags=["Admin Metrics"])

def check_admin(user: User = Depends(get_current_user)) -> User:
    """Verify user is admin"""
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/dashboard-summary")
def get_dashboard_summary(user: User = Depends(check_admin)) -> Dict[str, Any]:
    """
    Get high-level dashboard summary with key metrics.
    """
    db = SessionLocal()
    try:
        # Total users
        total_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        
        # Active users (last 7 days)
        active_users_7d = db.execute(text("""
            SELECT COUNT(DISTINCT user_id)
            FROM user_activity
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)).scalar() or 0
        
        # New users this month
        new_users_month = db.execute(text("""
            SELECT COUNT(*) FROM users
            WHERE created_at >= DATE_TRUNC('month', NOW())
        """)).scalar() or 0
        
        # Total courses
        total_courses = db.execute(text("SELECT COUNT(*) FROM courses")).scalar() or 0
        
        # Total enrollments
        total_enrollments = db.execute(text("""
            SELECT COUNT(DISTINCT user_id)
            FROM course_enrollments
        """)).scalar() or 0
        
        # Enrollment rate
        enrollment_rate = (total_enrollments / total_users * 100) if total_users > 0 else 0
        
        # Total coins in circulation
        total_coins = db.execute(text("""
            SELECT COALESCE(SUM(delta), 0) FROM coin_ledger
        """)).scalar() or 0
        
        return {
            "summary": {
                "total_users": total_users,
                "active_users_7days": active_users_7d,
                "new_users_month": new_users_month,
                "enrollment_rate": round(enrollment_rate, 2),
                "total_courses": total_courses,
                "course_enrollments": total_enrollments,
                "total_coins_circulation": int(total_coins)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        db.close()

@router.get("/user-growth")
def get_user_growth(period_days: int = 30, user: User = Depends(check_admin)) -> Dict[str, Any]:
    """
    Get user growth metrics for specified period.
    """
    db = SessionLocal()
    try:
        # Daily user registrations
        rows = db.execute(text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as registrations
            FROM users
            WHERE created_at >= NOW() - INTERVAL ':days days'
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """), {"days": period_days}).fetchall()
        
        daily_data = [
            {"date": str(row[0]), "registrations": row[1]}
            for row in rows
        ]
        
        # Calculate growth rate
        total_registrations = sum(r["registrations"] for r in daily_data)
        days_with_data = len(daily_data)
        avg_daily = total_registrations / days_with_data if days_with_data > 0 else 0
        
        return {
            "period_days": period_days,
            "daily_data": daily_data,
            "total_registrations": total_registrations,
            "avg_daily_registrations": round(avg_daily, 2),
            "growth_trend": "upward" if len(daily_data) > 1 and daily_data[-1]["registrations"] > daily_data[0]["registrations"] else "downward"
        }
    finally:
        db.close()

@router.get("/course-analytics")
def get_course_analytics(user: User = Depends(check_admin)) -> Dict[str, Any]:
    """
    Get course enrollment and completion analytics.
    """
    db = SessionLocal()
    try:
        # Top courses by enrollment
        top_courses = db.execute(text("""
            SELECT 
                c.id,
                c.title,
                COUNT(DISTINCT ce.user_id) as enrollments,
                COUNT(DISTINCT cp.id) as completions,
                ROUND(100.0 * COUNT(DISTINCT cp.id) / NULLIF(COUNT(DISTINCT ce.user_id), 0), 2) as completion_rate
            FROM courses c
            LEFT JOIN course_enrollments ce ON c.id = ce.course_id
            LEFT JOIN course_progress cp ON ce.id = cp.enrollment_id AND cp.progress_percentage = 100
            GROUP BY c.id, c.title
            ORDER BY enrollments DESC
            LIMIT 20
        """)).fetchall()
        
        courses_data = [
            {
                "course_id": row[0],
                "title": row[1],
                "enrollments": row[2] or 0,
                "completions": row[3] or 0,
                "completion_rate": row[4] or 0
            }
            for row in top_courses
        ]
        
        # Overall stats
        total_courses = db.execute(text("SELECT COUNT(*) FROM courses")).scalar() or 0
        total_enrollments = db.execute(text("SELECT COUNT(*) FROM course_enrollments")).scalar() or 0
        total_completions = db.execute(text("""
            SELECT COUNT(DISTINCT cp.id)
            FROM course_progress cp
            WHERE cp.progress_percentage = 100
        """)).scalar() or 0
        
        return {
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "total_completions": total_completions,
            "overall_completion_rate": round(100.0 * total_completions / total_enrollments, 2) if total_enrollments > 0 else 0,
            "top_courses": courses_data
        }
    finally:
        db.close()

@router.get("/engagement-metrics")
def get_engagement_metrics(user: User = Depends(check_admin)) -> Dict[str, Any]:
    """
    Get user engagement metrics.
    """
    db = SessionLocal()
    try:
        # Quiz performance
        quiz_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_attempts,
                AVG(score) as avg_score,
                MAX(score) as max_score,
                MIN(score) as min_score
            FROM quiz_attempts
        """)).fetchone()
        
        # Coding submissions
        coding_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_submissions,
                SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
                ROUND(100.0 * SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
            FROM coding_submissions
        """)).fetchone()
        
        # Resume views/exports
        resume_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_events,
                SUM(CASE WHEN event_type = 'export' THEN 1 ELSE 0 END) as exports,
                SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) as views
            FROM resume_analytics_events
        """)).fetchone()
        
        # Daily active users (last 7 days)
        dau = db.execute(text("""
            SELECT COUNT(DISTINCT user_id)
            FROM user_activity
            WHERE created_at >= NOW() - INTERVAL '1 day'
        """)).scalar() or 0
        
        return {
            "quiz_engagement": {
                "total_attempts": quiz_stats[0] or 0,
                "avg_score": round(float(quiz_stats[1]) if quiz_stats[1] else 0, 2),
                "max_score": quiz_stats[2] or 0,
                "min_score": quiz_stats[3] or 0
            },
            "coding_engagement": {
                "total_submissions": coding_stats[0] or 0,
                "accepted_solutions": coding_stats[1] or 0,
                "success_rate": coding_stats[2] or 0
            },
            "resume_engagement": {
                "total_events": resume_stats[0] or 0,
                "exports": resume_stats[1] or 0,
                "views": resume_stats[2] or 0
            },
            "daily_active_users": dau
        }
    finally:
        db.close()

@router.get("/system-health")
def get_system_health(user: User = Depends(check_admin)) -> Dict[str, Any]:
    """
    Get system health indicators.
    """
    db = SessionLocal()
    try:
        # Database stats
        table_count = db.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
        """)).scalar() or 0
        
        # Check for pending migrations/issues
        # This is simplified - would need Alembic for real migrations
        
        # User sessions
        active_sessions = db.execute(text("""
            SELECT COUNT(DISTINCT user_id)
            FROM user_activity
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """)).scalar() or 0
        
        # API health (from logs if available)
        error_count_24h = db.execute(text("""
            SELECT COUNT(*) FROM admin_logs
            WHERE log_level = 'ERROR'
            AND created_at >= NOW() - INTERVAL '24 hours'
        """)).scalar() or 0
        
        return {
            "status": "healthy" if error_count_24h < 10 else "warning",
            "database": {
                "tables": table_count,
                "status": "connected"
            },
            "active_sessions": active_sessions,
            "errors_24h": error_count_24h,
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        db.close()

@router.get("/revenue-metrics")
def get_revenue_metrics(user: User = Depends(check_admin)) -> Dict[str, Any]:
    """
    Get revenue and payment metrics (if payments enabled).
    """
    db = SessionLocal()
    try:
        # Total transactions
        total_transactions = db.execute(text("""
            SELECT COUNT(*) FROM payments
        """)).scalar() or 0
        
        # Total revenue
        total_revenue = db.execute(text("""
            SELECT COALESCE(SUM(amount), 0) FROM payments
            WHERE status = 'completed'
        """)).scalar() or 0
        
        # Active subscriptions
        active_subscriptions = db.execute(text("""
            SELECT COUNT(*) FROM subscriptions
            WHERE status = 'active'
        """)).scalar() or 0
        
        # Monthly recurring revenue (MRR)
        mrr = db.execute(text("""
            SELECT COALESCE(SUM(amount), 0) FROM subscriptions
            WHERE status = 'active' AND billing_cycle = 'monthly'
        """)).scalar() or 0
        
        return {
            "total_transactions": total_transactions,
            "total_revenue": round(float(total_revenue), 2),
            "active_subscriptions": active_subscriptions,
            "monthly_recurring_revenue": round(float(mrr), 2),
            "currency": "USD",
            "period": "all_time"
        }
    finally:
        db.close()

@router.get("/admin-logs")
def get_admin_logs(
    limit: int = 50,
    user: User = Depends(check_admin)
) -> Dict[str, Any]:
    """
    Get recent admin logs for monitoring.
    """
    db = SessionLocal()
    try:
        logs = db.execute(text("""
            SELECT id, user_id, action, details, log_level, created_at
            FROM admin_logs
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        log_list = [
            {
                "id": log[0],
                "user_id": log[1],
                "action": log[2],
                "details": log[3],
                "level": log[4],
                "timestamp": str(log[5])
            }
            for log in logs
        ]
        
        return {
            "logs": log_list,
            "limit": limit,
            "total": len(log_list)
        }
    finally:
        db.close()
