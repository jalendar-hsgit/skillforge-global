"""
Dashboard analytics API - provides comprehensive user statistics.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.quiz_attempt import QuizAttempt
from app.modelsx.quiz_template import GeneratedQuiz, QuizSession
from app.modelsx.progress import VideoProgress
from app.modelsx.coins import CoinLedger

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics for the authenticated user.
    
    Returns:
        - Total videos completed
        - Total quizzes taken (static + AI)
        - Current Forge AI Credits balance
        - Learning streak (consecutive days)
        - Paths in progress with completion %
        - Recent achievements
        - AI quiz stats (saved, favorites, best scores)
    """
    user_id = user.id
    
    # Video stats
    video_progress = db.query(VideoProgress).filter(
        VideoProgress.user_id == user_id,
        VideoProgress.completed == True
    ).count()
    
    # Quiz stats (legacy + new sessions)
    legacy_quiz_count = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).count()
    
    session_quiz_count = db.query(QuizSession).filter(
        QuizSession.user_id == user_id,
        QuizSession.completed_at.isnot(None)
    ).count()
    
    total_quizzes = legacy_quiz_count + session_quiz_count
    
    # Quiz pass rate
    passed_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.passed == True
    ).count()
    
    pass_rate = (passed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0
    
    # Forge AI Credits (Coins)
    coin_balance = db.query(func.sum(CoinLedger.amount)).filter(
        CoinLedger.user_id == user_id
    ).scalar() or 0
    
    # Learning streak (consecutive days with activity)
    streak = calculate_streak(user_id, db)
    
    # Saved AI quizzes
    saved_quizzes = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.user_id == user_id,
        GeneratedQuiz.is_archived == False
    ).count()
    
    favorite_quizzes = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.user_id == user_id,
        GeneratedQuiz.is_favorite == True,
        GeneratedQuiz.is_archived == False
    ).count()
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    recent_videos = db.query(VideoProgress).filter(
        VideoProgress.user_id == user_id,
        VideoProgress.last_position_updated >= seven_days_ago
    ).count()
    
    recent_quizzes = db.query(QuizSession).filter(
        QuizSession.user_id == user_id,
        QuizSession.created_at >= seven_days_ago
    ).count()
    
    # Best quiz scores
    best_scores = db.query(
        QuizAttempt.path,
        func.max(QuizAttempt.score).label('best_score'),
        func.max(QuizAttempt.total).label('total')
    ).filter(
        QuizAttempt.user_id == user_id
    ).group_by(QuizAttempt.path).order_by(desc('best_score')).limit(5).all()
    
    return {
        "user_id": user_id,
        "totals": {
            "videos_completed": video_progress,
            "quizzes_taken": total_quizzes,
            "forge_credits": int(coin_balance),
            "saved_quizzes": saved_quizzes,
            "favorite_quizzes": favorite_quizzes
        },
        "performance": {
            "quiz_pass_rate": round(pass_rate, 1),
            "learning_streak_days": streak,
            "best_quiz_scores": [
                {"path": s.path, "score": s.best_score, "total": s.total}
                for s in best_scores
            ]
        },
        "recent_activity": {
            "videos_last_7_days": recent_videos,
            "quizzes_last_7_days": recent_quizzes
        }
    }


@router.get("/learning-paths")
def get_learning_paths(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's learning path progress with completion percentages.
    Groups video progress by course/path.
    """
    user_id = user.id
    
    # This is simplified; ideally you'd query from Course model
    # For now, return progress grouped by path
    from app.modelsx.course import Course
    from app.modelsx.video import Video
    
    courses = db.query(Course).all()
    
    paths_progress = []
    for course in courses:
        total_videos = db.query(Video).filter(Video.course_id == course.id).count()
        
        completed_videos = db.query(VideoProgress).join(Video).filter(
            Video.course_id == course.id,
            VideoProgress.user_id == user_id,
            VideoProgress.completed == True
        ).count()
        
        if total_videos > 0:
            percentage = (completed_videos / total_videos) * 100
            
            # Get last watched video
            last_progress = db.query(VideoProgress).join(Video).filter(
                Video.course_id == course.id,
                VideoProgress.user_id == user_id
            ).order_by(desc(VideoProgress.last_position_updated)).first()
            
            paths_progress.append({
                "path": course.slug,
                "title": course.title,
                "total_videos": total_videos,
                "completed_videos": completed_videos,
                "percentage": round(percentage, 1),
                "last_watched": last_progress.last_position_updated.isoformat() if last_progress else None
            })
    
    return {"paths": paths_progress}


@router.get("/quiz-analytics")
def get_quiz_analytics(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """
    Get detailed quiz performance analytics.
    
    Args:
        days: Number of days to analyze (default 30)
    
    Returns:
        - Performance trends over time
        - Topic breakdown
        - Difficulty distribution
        - Time-of-day patterns
    """
    user_id = user.id
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get quiz sessions within date range
    sessions = db.query(QuizSession).filter(
        QuizSession.user_id == user_id,
        QuizSession.created_at >= cutoff
    ).all()
    
    if not sessions:
        return {
            "total_quizzes": 0,
            "avg_score_percentage": 0,
            "performance_trend": [],
            "topic_breakdown": [],
            "difficulty_distribution": {}
        }
    
    # Calculate metrics
    total_quizzes = len(sessions)
    avg_score = sum(s.score / s.total_questions for s in sessions if s.total_questions > 0) / total_quizzes * 100
    
    # Performance trend (daily)
    daily_scores = {}
    for session in sessions:
        date_key = session.created_at.date().isoformat()
        if date_key not in daily_scores:
            daily_scores[date_key] = []
        if session.total_questions > 0:
            daily_scores[date_key].append(session.score / session.total_questions * 100)
    
    performance_trend = [
        {"date": date, "avg_score": sum(scores) / len(scores)}
        for date, scores in sorted(daily_scores.items())
    ]
    
    # Get AI quiz topics
    saved_quizzes = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.user_id == user_id
    ).all()
    
    topic_breakdown = {}
    difficulty_distribution = {"easy": 0, "medium": 0, "hard": 0}
    
    for quiz in saved_quizzes:
        topic_breakdown[quiz.topic] = topic_breakdown.get(quiz.topic, 0) + quiz.times_taken
        difficulty_distribution[quiz.difficulty] = difficulty_distribution.get(quiz.difficulty, 0) + 1
    
    top_topics = sorted(topic_breakdown.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_quizzes": total_quizzes,
        "avg_score_percentage": round(avg_score, 1),
        "performance_trend": performance_trend,
        "topic_breakdown": [{"topic": t, "count": c} for t, c in top_topics],
        "difficulty_distribution": difficulty_distribution
    }


@router.get("/achievements")
def get_achievements(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's achievement progress and unlocked badges.
    Integrates with the achievements system.
    """
    # This would integrate with the achievements.json file
    # For now, return based on stats
    
    from app.models.quiz_attempt import QuizAttempt
    
    user_id = user.id
    
    achievements = []
    
    # Quiz-based achievements
    total_quizzes = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).count()
    
    if total_quizzes >= 1:
        achievements.append({
            "id": "first_quiz",
            "name": "Quiz Novice",
            "description": "Complete your first quiz",
            "icon": "🎯",
            "unlocked": True
        })
    
    if total_quizzes >= 10:
        achievements.append({
            "id": "quiz_enthusiast",
            "name": "Quiz Enthusiast",
            "description": "Complete 10 quizzes",
            "icon": "📚",
            "unlocked": True
        })
    
    if total_quizzes >= 50:
        achievements.append({
            "id": "quiz_master",
            "name": "Quiz Master",
            "description": "Complete 50 quizzes",
            "icon": "🏆",
            "unlocked": True
        })
    
    # Perfect score achievement
    perfect_scores = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.score == QuizAttempt.total
    ).count()
    
    if perfect_scores > 0:
        achievements.append({
            "id": "perfectionist",
            "name": "Perfectionist",
            "description": "Get a perfect score on any quiz",
            "icon": "💯",
            "unlocked": True
        })
    
    return {"achievements": achievements}


def calculate_streak(user_id: int, db: Session) -> int:
    """
    Calculate consecutive days of learning activity.
    Checks QuizSession and VideoProgress for activity.
    """
    from sqlalchemy import or_
    
    # Get all activity dates (quiz sessions + video progress)
    quiz_dates = db.query(
        func.date(QuizSession.created_at).label('activity_date')
    ).filter(QuizSession.user_id == user_id).all()
    
    video_dates = db.query(
        func.date(VideoProgress.last_position_updated).label('activity_date')
    ).filter(VideoProgress.user_id == user_id).all()
    
    # Combine and deduplicate
    activity_dates = set()
    for row in quiz_dates:
        activity_dates.add(row.activity_date)
    for row in video_dates:
        activity_dates.add(row.activity_date)
    
    if not activity_dates:
        return 0
    
    # Sort dates descending
    sorted_dates = sorted(activity_dates, reverse=True)
    
    # Check for consecutive days from today
    today = datetime.now(timezone.utc).date()
    streak = 0
    
    for i, date in enumerate(sorted_dates):
        expected_date = today - timedelta(days=i)
        if date == expected_date:
            streak += 1
        else:
            break
    
    return streak
