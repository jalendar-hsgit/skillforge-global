"""
Learning Paths API router.
Endpoints for browsing, starting, and progressing through learning paths.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.learning_paths import (
    LearningPath, PathChallenge, UserPathProgress,
    PathStatus, PathDifficulty, ChallengeStatus
)

router = APIRouter(prefix="/paths", tags=["learning_paths"])


# ===================== Learning Paths =====================

@router.get("")
def list_learning_paths(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    difficulty: str = None,
    is_featured: bool = None
):
    """
    List all published learning paths.
    
    Optional filters:
    - difficulty: beginner, intermediate, advanced, expert
    - is_featured: true/false
    """
    query = db.query(LearningPath).filter(LearningPath.status == PathStatus.PUBLISHED)
    
    if difficulty:
        try:
            query = query.filter(LearningPath.difficulty == PathDifficulty(difficulty))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty: {difficulty}")
    
    if is_featured is not None:
        query = query.filter(LearningPath.is_featured == is_featured)
    
    total = query.count()
    paths = query.order_by(LearningPath.order).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "paths": [_format_path(path) for path in paths]
    }


@router.get("/{path_id}")
def get_learning_path(path_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get details of a specific learning path with user's progress"""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    if path.status != PathStatus.PUBLISHED and (not current_user or path.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get user's progress if authenticated
    user_progress = None
    if current_user:
        user_progress = db.query(UserPathProgress).filter(
            UserPathProgress.user_id == current_user.id,
            UserPathProgress.path_id == path_id
        ).first()
    
    return {
        "path": _format_path(path),
        "challenges": [_format_challenge(ch) for ch in path.challenges],
        "user_progress": _format_user_progress(user_progress) if user_progress else None
    }


# ===================== User Path Progress =====================

@router.post("/{path_id}/start")
def start_learning_path(
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a learning path"""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path or path.status != PathStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # Check if already started
    existing = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if existing:
        return _format_user_progress(existing)
    
    # Create new progress
    total_challenges = len(path.challenges)
    progress = UserPathProgress(
        user_id=current_user.id,
        path_id=path_id,
        total_challenges=total_challenges,
        is_started=True,
        started_at=datetime.utcnow(),
        current_challenge_id=path.challenges[0].id if path.challenges else None
    )
    
    db.add(progress)
    db.commit()
    db.refresh(progress)
    
    return _format_user_progress(progress)


@router.get("/user/progress")
def get_user_path_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """Get current user's progress across all learning paths"""
    total = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id
    ).count()
    
    progress_list = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id
    ).order_by(UserPathProgress.last_accessed_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "progress": [_format_user_progress(p) for p in progress_list]
    }


@router.get("/{path_id}/progress")
def get_path_progress(
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's progress for a specific path"""
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found for this path")
    
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    
    return {
        "progress": _format_user_progress(progress),
        "challenges": [_format_challenge(ch) for ch in path.challenges]
    }


@router.post("/{path_id}/challenges/{challenge_id}/complete")
def mark_challenge_complete(
    path_id: int,
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a challenge as completed in a path"""
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found for this path")
    
    challenge = db.query(PathChallenge).filter(
        PathChallenge.path_id == path_id,
        PathChallenge.challenge_id == challenge_id
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found in this path")
    
    # Check if already completed
    if challenge_id in progress.completed_challenges or progress.completed_challenges >= progress.total_challenges:
        # Increment if not already counted
        if progress.completed_challenges < progress.total_challenges and challenge_id not in str(progress.completed_challenges):
            progress.completed_challenges += 1
    else:
        progress.completed_challenges += 1
    
    # Update completion percentage
    progress.calculate_completion_percentage()
    
    # Check if path is fully completed
    if progress.completed_challenges >= progress.total_challenges:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
    
    progress.last_accessed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(progress)
    
    return {
        "message": "Challenge marked as completed",
        "progress": _format_user_progress(progress)
    }


@router.get("/{path_id}/leaderboard")
def get_path_leaderboard(
    path_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """Get leaderboard for a learning path by completion and points"""
    leaderboard = db.query(UserPathProgress).filter(
        UserPathProgress.path_id == path_id,
        UserPathProgress.is_started == True
    ).order_by(
        UserPathProgress.completed_challenges.desc(),
        UserPathProgress.total_points_earned.desc()
    ).limit(limit).all()
    
    return [_format_user_progress(p) for p in leaderboard]


# ===================== Path Management (Admin) =====================

@router.post("")
def create_learning_path(
    path_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new learning path (admin only)"""
    # TODO: Add admin check
    
    path = LearningPath(
        title=path_data.get("title"),
        description=path_data.get("description"),
        icon=path_data.get("icon"),
        difficulty=PathDifficulty(path_data.get("difficulty", "beginner")),
        estimated_hours=path_data.get("estimated_hours"),
        status=PathStatus.DRAFT,
        created_by=current_user.id
    )
    
    db.add(path)
    db.commit()
    db.refresh(path)
    
    return _format_path(path)


@router.put("/{path_id}")
def update_learning_path(
    path_id: int,
    path_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a learning path"""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    if path.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    path.title = path_data.get("title", path.title)
    path.description = path_data.get("description", path.description)
    path.icon = path_data.get("icon", path.icon)
    path.difficulty = PathDifficulty(path_data.get("difficulty", path.difficulty))
    path.estimated_hours = path_data.get("estimated_hours", path.estimated_hours)
    path.status = PathStatus(path_data.get("status", path.status))
    
    db.commit()
    db.refresh(path)
    
    return _format_path(path)


@router.post("/{path_id}/challenges")
def add_challenge_to_path(
    path_id: int,
    challenge_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a challenge to a learning path"""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    if path.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    challenge = PathChallenge(
        path_id=path_id,
        challenge_id=challenge_data.get("challenge_id"),
        order=challenge_data.get("order", len(path.challenges)),
        required_previous_completion=challenge_data.get("required_previous_completion", False),
        min_score_for_unlock=challenge_data.get("min_score_for_unlock"),
        points_value=challenge_data.get("points_value", 0),
        estimated_minutes=challenge_data.get("estimated_minutes")
    )
    
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    
    return _format_challenge(challenge)


# ===================== Helper Functions =====================

def _format_path(path):
    """Format a learning path for API response"""
    return {
        "id": path.id,
        "title": path.title,
        "description": path.description,
        "icon": path.icon,
        "difficulty": path.difficulty.value,
        "estimated_hours": path.estimated_hours,
        "status": path.status.value,
        "is_featured": path.is_featured,
        "total_challenges": len(path.challenges),
        "created_at": path.created_at.isoformat()
    }


def _format_challenge(challenge):
    """Format a path challenge for API response"""
    return {
        "id": challenge.id,
        "path_id": challenge.path_id,
        "challenge_id": challenge.challenge_id,
        "order": challenge.order,
        "required_previous_completion": challenge.required_previous_completion,
        "min_score_for_unlock": challenge.min_score_for_unlock,
        "points_value": challenge.points_value,
        "estimated_minutes": challenge.estimated_minutes
    }


def _format_user_progress(progress):
    """Format user path progress for API response"""
    if not progress:
        return None
    
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "path_id": progress.path_id,
        "completed_challenges": progress.completed_challenges,
        "total_challenges": progress.total_challenges,
        "completion_percentage": round(progress.completion_percentage, 2),
        "total_points_earned": progress.total_points_earned,
        "is_started": progress.is_started,
        "is_completed": progress.is_completed,
        "current_challenge_id": progress.current_challenge_id,
        "started_at": progress.started_at.isoformat() if progress.started_at else None,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        "last_accessed_at": progress.last_accessed_at.isoformat()
    }
