from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from datetime import datetime, timedelta
from typing import List, Optional
from app.core.db import SessionLocal
from app.core.security import get_current_user

router = APIRouter(prefix="/student", tags=["student-dashboard"])

# ============================================================
# STUDENT DASHBOARD - Comprehensive Learning Overview
# ============================================================

@router.get("/dashboard/overview")
def get_student_overview(user = Depends(get_current_user)):
    """
    Get comprehensive student dashboard overview:
    - Enrolled courses count
    - Courses in progress
    - Completed courses
    - Quiz statistics
    - Learning streak
    - Total learning time
    - Achievements earned
    """
    db = SessionLocal()
    try:
        # Get course enrollments and progress
        course_stats = db.execute(text("""
            SELECT 
                COUNT(DISTINCT vp.video_id) as videos_watched,
                AVG(vp.progress_percent) as avg_progress,
                COUNT(DISTINCT CASE WHEN vp.progress_percent = 100 THEN vp.video_id END) as videos_completed
            FROM video_progress vp
            WHERE vp.user_id = :uid
        """), {"uid": user.id}).mappings().first()

        # Get quiz statistics (be tolerant of missing 'passed' column in older DBs)
        try:
            quiz_stats = db.execute(text("""
                SELECT 
                    COUNT(*) as total_attempts,
                    COUNT(CASE WHEN passed THEN 1 END) as passed_count,
                    AVG(score) as avg_score,
                    MAX(score) as best_score
                FROM quiz_attempts
                WHERE user_id = :uid
            """), {"uid": user.id}).mappings().first()
        except OperationalError:
            # Fallback to safe defaults when DB schema doesn't include 'passed'
            quiz_stats = {"total_attempts": 0, "passed_count": 0, "avg_score": 0, "best_score": 0}

        # Get learning streak (consecutive days with activity)
        recent_activity = db.execute(text("""
            SELECT DATE(updated_at) as activity_date
            FROM video_progress
            WHERE user_id = :uid
            AND updated_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(updated_at)
            ORDER BY activity_date DESC
        """), {"uid": user.id}).mappings().all()

        # Calculate streak
        streak = 0
        if recent_activity:
            today = datetime.utcnow().date()
            for i, row in enumerate(recent_activity):
                expected_date = today - timedelta(days=i)
                if row['activity_date'] == expected_date:
                    streak += 1
                else:
                    break

        # Get total learning time (estimate based on video progress)
        learning_time = db.execute(text("""
            SELECT SUM(progress_percent) as total_progress_points
            FROM video_progress
            WHERE user_id = :uid
        """), {"uid": user.id}).mappings().first()

        # Estimate hours (assuming avg 10min per video, 100% = 10min)
        estimated_hours = (learning_time['total_progress_points'] or 0) / 100 * 10 / 60

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role
            },
            "courses": {
                "videos_watched": course_stats['videos_watched'] or 0,
                "videos_completed": course_stats['videos_completed'] or 0,
                "avg_progress": round(course_stats['avg_progress'] or 0, 1)
            },
            "quizzes": {
                "total_attempts": (quiz_stats.get('total_attempts') if isinstance(quiz_stats, dict) else (quiz_stats['total_attempts'] if quiz_stats else 0)) or 0,
                "passed": (quiz_stats.get('passed_count') if isinstance(quiz_stats, dict) else (quiz_stats['passed_count'] if quiz_stats else 0)) or 0,
                "avg_score": round((quiz_stats.get('avg_score') if isinstance(quiz_stats, dict) else (quiz_stats['avg_score'] if quiz_stats else 0)) or 0, 1),
                "best_score": round((quiz_stats.get('best_score') if isinstance(quiz_stats, dict) else (quiz_stats['best_score'] if quiz_stats else 0)) or 0, 1)
            },
            "activity": {
                "learning_streak": streak,
                "estimated_hours": round(estimated_hours, 1),
                "last_active": datetime.utcnow().isoformat()
            }
        }
    finally:
        db.close()


@router.get("/dashboard/courses")
def get_enrolled_courses(user = Depends(get_current_user)):
    """Get all courses with user's progress"""
    db = SessionLocal()
    try:
        # Get all videos with progress
        results = db.execute(text("""
            SELECT 
                vp.video_id,
                vp.progress_percent,
                vp.updated_at as last_watched,
                c.title as course_title,
                c.path as course_path,
                c.youtubeId as youtube_id
            FROM video_progress vp
            LEFT JOIN courses c ON c.id = vp.video_id
            WHERE vp.user_id = :uid
            ORDER BY vp.updated_at DESC
        """), {"uid": user.id}).mappings().all()

        # Group by course path
        courses = {}
        for row in results:
            path = row['course_path'] or 'other'
            if path not in courses:
                courses[path] = {
                    "path": path,
                    "title": row['course_title'] or "Unknown Course",
                    "videos": [],
                    "total_progress": 0,
                    "videos_count": 0,
                    "completed_count": 0
                }
            
            courses[path]['videos'].append({
                "video_id": row['video_id'],
                "progress": row['progress_percent'],
                "last_watched": row['last_watched'].isoformat() if row['last_watched'] else None,
                "youtube_id": row['youtube_id']
            })
            courses[path]['total_progress'] += row['progress_percent']
            courses[path]['videos_count'] += 1
            if row['progress_percent'] == 100:
                courses[path]['completed_count'] += 1

        # Calculate average progress for each course
        for course in courses.values():
            if course['videos_count'] > 0:
                course['avg_progress'] = round(course['total_progress'] / course['videos_count'], 1)
            else:
                course['avg_progress'] = 0

        return {"courses": list(courses.values())}
    finally:
        db.close()


@router.get("/dashboard/recent-activity")
def get_recent_activity(user = Depends(get_current_user), limit: int = 10):
    """Get recent learning activity"""
    db = SessionLocal()
    try:
        activities = []

        # Recent video progress
        video_activity = db.execute(text("""
            SELECT 
                'video_progress' as type,
                vp.updated_at as timestamp,
                c.title as title,
                vp.progress_percent as progress
            FROM video_progress vp
            LEFT JOIN courses c ON c.id = vp.video_id
            WHERE vp.user_id = :uid
            ORDER BY vp.updated_at DESC
            LIMIT :lim
        """), {"uid": user.id, "lim": limit}).mappings().all()

        # Recent quiz attempts (tolerant of schema differences)
        try:
            quiz_activity = db.execute(text("""
                SELECT 
                    'quiz_attempt' as type,
                    qa.created_at as timestamp,
                    q.title as title,
                    qa.score,
                    qa.passed
                FROM quiz_attempts qa
                LEFT JOIN quizzes q ON q.id = qa.quiz_id
                WHERE qa.user_id = :uid
                ORDER BY qa.created_at DESC
                LIMIT :lim
            """), {"uid": user.id, "lim": limit}).mappings().all()
        except OperationalError:
            quiz_activity = []

        # Combine and sort
        for item in video_activity:
            activities.append({
                "type": "video",
                "timestamp": item['timestamp'].isoformat() if item['timestamp'] else None,
                "title": item['title'] or "Unknown Video",
                "progress": item['progress']
            })

        for item in quiz_activity:
            activities.append({
                "type": "quiz",
                "timestamp": item['timestamp'].isoformat() if item['timestamp'] else None,
                "title": item['title'] or "Unknown Quiz",
                "score": item['score'],
                "passed": item['passed']
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)

        return {"activities": activities[:limit]}
    finally:
        db.close()


@router.get("/dashboard/quiz-results")
def get_quiz_results(user = Depends(get_current_user)):
    """Get all quiz attempts with results"""
    db = SessionLocal()
    try:
        try:
            results = db.execute(text("""
                SELECT 
                    qa.id,
                    qa.quiz_id,
                    q.title as quiz_title,
                    qa.score,
                    qa.passed,
                    qa.created_at,
                    qa.answers
                FROM quiz_attempts qa
                LEFT JOIN quizzes q ON q.id = qa.quiz_id
                WHERE qa.user_id = :uid
                ORDER BY qa.created_at DESC
            """), {"uid": user.id}).mappings().all()
        except OperationalError:
            results = []

        return {
            "quiz_attempts": [
                {
                    "id": row['id'],
                    "quiz_id": row['quiz_id'],
                    "quiz_title": row['quiz_title'] or "Unknown Quiz",
                    "score": row['score'],
                    "passed": row['passed'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "answers": row['answers']
                }
                for row in results
            ]
        }
    finally:
        db.close()


@router.get("/dashboard/achievements")
def get_achievements(user = Depends(get_current_user)):
    """Get earned achievements and badges"""
    db = SessionLocal()
    try:
        # Calculate achievements based on activity
        achievements = []

        # Videos watched milestones
        video_count = db.execute(text("""
            SELECT COUNT(DISTINCT video_id) as count
            FROM video_progress
            WHERE user_id = :uid
        """), {"uid": user.id}).mappings().first()['count']

        if video_count >= 1:
            achievements.append({
                "id": "first_video",
                "title": "First Steps",
                "description": "Watched your first video",
                "icon": "🎬",
                "earned": True
            })
        if video_count >= 10:
            achievements.append({
                "id": "video_enthusiast",
                "title": "Video Enthusiast",
                "description": "Watched 10 videos",
                "icon": "📺",
                "earned": True
            })
        if video_count >= 50:
            achievements.append({
                "id": "binge_learner",
                "title": "Binge Learner",
                "description": "Watched 50 videos",
                "icon": "🍿",
                "earned": True
            })

        # Completed videos
        completed_count = db.execute(text("""
            SELECT COUNT(*) as count
            FROM video_progress
            WHERE user_id = :uid AND progress_percent = 100
        """), {"uid": user.id}).mappings().first()['count']

        if completed_count >= 5:
            achievements.append({
                "id": "completionist",
                "title": "Completionist",
                "description": "Completed 5 videos",
                "icon": "✅",
                "earned": True
            })

        # Quiz achievements
        try:
            quiz_passed = db.execute(text("""
                SELECT COUNT(*) as count
                FROM quiz_attempts
                WHERE user_id = :uid AND passed = 1
            """), {"uid": user.id}).mappings().first()['count']
        except OperationalError:
            quiz_passed = 0

        if quiz_passed >= 1:
            achievements.append({
                "id": "quiz_master",
                "title": "Quiz Master",
                "description": "Passed your first quiz",
                "icon": "🎯",
                "earned": True
            })
        if quiz_passed >= 5:
            achievements.append({
                "id": "quiz_expert",
                "title": "Quiz Expert",
                "description": "Passed 5 quizzes",
                "icon": "🏆",
                "earned": True
            })

        # Perfect score achievement
        try:
            perfect_score = db.execute(text("""
                SELECT COUNT(*) as count
                FROM quiz_attempts
                WHERE user_id = :uid AND score = 100
            """), {"uid": user.id}).mappings().first()['count']
        except OperationalError:
            perfect_score = 0

        if perfect_score >= 1:
            achievements.append({
                "id": "perfect_score",
                "title": "Perfect Score",
                "description": "Got 100% on a quiz",
                "icon": "💯",
                "earned": True
            })

        return {
            "achievements": achievements,
            "total_earned": len(achievements)
        }
    finally:
        db.close()


@router.get("/dashboard/recommendations")
def get_recommendations(user = Depends(get_current_user)):
    """Get personalized course recommendations"""
    db = SessionLocal()
    try:
        # Get user's learning paths
        user_paths = db.execute(text("""
            SELECT DISTINCT c.path
            FROM video_progress vp
            JOIN courses c ON c.id = vp.video_id
            WHERE vp.user_id = :uid
        """), {"uid": user.id}).mappings().all()

        paths = [row['path'] for row in user_paths if row['path']]

        # Get unwatched videos from same paths
        if paths:
            placeholders = ', '.join([f':path{i}' for i in range(len(paths))])
            params = {"uid": user.id}
            params.update({f'path{i}': path for i, path in enumerate(paths)})

            recommendations = db.execute(text(f"""
                SELECT DISTINCT
                    c.id,
                    c.title,
                    c.path,
                    c.youtubeId,
                    c.duration
                FROM courses c
                WHERE c.path IN ({placeholders})
                AND c.id NOT IN (
                    SELECT video_id FROM video_progress WHERE user_id = :uid
                )
                LIMIT 5
            """), params).mappings().all()
        else:
            # No learning history, recommend featured/popular courses
            recommendations = db.execute(text("""
                SELECT id, title, path, youtubeId, duration
                FROM courses
                WHERE featured = 1
                LIMIT 5
            """)).mappings().all()

        return {
            "recommendations": [
                {
                    "id": row['id'],
                    "title": row['title'],
                    "path": row['path'],
                    "youtube_id": row['youtubeId'],
                    "duration": row['duration']
                }
                for row in recommendations
            ]
        }
    finally:
        db.close()
