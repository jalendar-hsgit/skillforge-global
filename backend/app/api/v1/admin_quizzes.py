"""
Admin endpoint for monitoring AI quiz generation activity and statistics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone

from app.core.db import get_db
from app.core.security import get_current_user
from app.modelsx.quiz_template import GeneratedQuiz, QuizSession

router = APIRouter(prefix="/admin/quizzes", tags=["admin-quizzes"])


def require_admin(user = Depends(get_current_user)):
    """Simple admin check - in production, use proper RBAC."""
    # For now, check if user email ends with @skillforge.global or is user_id 1
    if user.id != 1 and not (hasattr(user, 'email') and user.email and user.email.endswith('@skillforge.global')):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
def quiz_generation_stats(
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get overall AI quiz generation statistics."""
    
    # Total quizzes generated
    total_generated = db.query(func.count(GeneratedQuiz.id)).scalar()
    
    # Quizzes generated in last 24h
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    last_24h = db.query(func.count(GeneratedQuiz.id)).filter(
        GeneratedQuiz.created_at >= yesterday
    ).scalar()
    
    # Total sessions
    total_sessions = db.query(func.count(QuizSession.id)).scalar()
    
    # Completed sessions
    completed_sessions = db.query(func.count(QuizSession.id)).filter(
        QuizSession.completed_at.isnot(None)
    ).scalar()
    
    # Average score
    avg_score = db.query(func.avg(QuizSession.score * 100.0 / QuizSession.total_questions)).filter(
        QuizSession.completed_at.isnot(None)
    ).scalar() or 0
    
    # Top topics
    top_topics = db.query(
        GeneratedQuiz.topic,
        func.count(GeneratedQuiz.id).label('count')
    ).group_by(GeneratedQuiz.topic).order_by(desc('count')).limit(10).all()
    
    # Provider distribution
    provider_dist = db.query(
        GeneratedQuiz.provider,
        func.count(GeneratedQuiz.id).label('count')
    ).group_by(GeneratedQuiz.provider).all()
    
    # Difficulty distribution
    difficulty_dist = db.query(
        GeneratedQuiz.difficulty,
        func.count(GeneratedQuiz.id).label('count')
    ).group_by(GeneratedQuiz.difficulty).all()
    
    return {
        "total_generated": total_generated,
        "last_24h": last_24h,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "avg_score_pct": round(avg_score, 1),
        "top_topics": [{"topic": t, "count": c} for t, c in top_topics],
        "providers": [{"provider": p or "unknown", "count": c} for p, c in provider_dist],
        "difficulties": [{"difficulty": d, "count": c} for d, c in difficulty_dist]
    }


@router.get("/recent")
def recent_quizzes(
    limit: int = 20,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get recently generated quizzes."""
    quizzes = db.query(GeneratedQuiz).order_by(
        GeneratedQuiz.created_at.desc()
    ).limit(limit).all()
    
    return [{
        "id": q.id,
        "user_id": q.user_id,
        "topic": q.topic,
        "difficulty": q.difficulty,
        "num_questions": len(q.questions) if q.questions else 0,
        "provider": q.provider,
        "model": q.model,
        "times_taken": q.times_taken,
        "created_at": q.created_at.isoformat() if q.created_at else None,
        "is_favorite": q.is_favorite
    } for q in quizzes]


@router.get("/user/{user_id}")
def user_quiz_activity(
    user_id: int,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get quiz generation activity for a specific user."""
    
    # User's generated quizzes
    quizzes = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.user_id == user_id
    ).order_by(GeneratedQuiz.created_at.desc()).limit(50).all()
    
    # User's sessions
    sessions = db.query(QuizSession).filter(
        QuizSession.user_id == user_id
    ).order_by(QuizSession.started_at.desc()).limit(50).all()
    
    # Aggregate stats
    total_generated = len(quizzes)
    total_sessions = len(sessions)
    completed = len([s for s in sessions if s.completed_at])
    avg_score = sum(s.score / s.total_questions for s in sessions if s.completed_at and s.total_questions > 0) / max(completed, 1) * 100
    
    return {
        "user_id": user_id,
        "total_generated": total_generated,
        "total_sessions": total_sessions,
        "completed_sessions": completed,
        "avg_score_pct": round(avg_score, 1),
        "recent_quizzes": [{
            "id": q.id,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "created_at": q.created_at.isoformat() if q.created_at else None
        } for q in quizzes[:10]],
        "recent_sessions": [{
            "id": s.id,
            "score": s.score,
            "total": s.total_questions,
            "passed": s.passed,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        } for s in sessions[:10]]
    }
