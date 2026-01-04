"""
Learning Paths API Router - Phase 3.4
Structured learning path management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models import User
from app.modelsx.learning_paths import LearningPath, PathChallenge, UserPathProgress
from app.schemas.learning_paths_schemas import (
    LearningPathResponse, LearningPathCreate, LearningPathUpdate,
    LearningPathWithChallenges, PathChallengeResponse, PathChallengeBase,
    UserPathProgressResponse, UserPathProgressCreate, UserPathProgressUpdate,
    PathProgressSummary, ChallengeCompletionData
)
from app.api.deps import get_current_user

# Phase 3.5: Real-time event emission
from app.services.realtime_events import (
    on_learning_path_enrolled,
    on_challenge_completed,
    on_certificate_issued
)

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])


# ==================== LEARNING PATHS ====================

@router.get("", response_model=List[LearningPathResponse])
def get_learning_paths(
    skip: int = 0,
    limit: int = 20,
    difficulty: str = None,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get learning paths"""
    query = db.query(LearningPath).filter(LearningPath.status == "published")
    
    if difficulty:
        query = query.filter(LearningPath.difficulty == difficulty)
    
    if featured_only:
        query = query.filter(LearningPath.is_featured == True)
    
    paths = query.order_by(
        desc(LearningPath.is_featured),
        LearningPath.order,
        desc(LearningPath.created_at)
    ).offset(skip).limit(limit).all()
    
    return paths


@router.get("/{path_id}", response_model=LearningPathWithChallenges)
def get_learning_path(
    path_id: int,
    db: Session = Depends(get_db)
):
    """Get learning path with challenges"""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    if path.status != "published":
        raise HTTPException(status_code=404, detail="Learning path not available")
    
    return path


@router.post("", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
def create_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create learning path (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    new_path = LearningPath(
        **path_data.dict(),
        created_by=current_user.id,
        status="draft"
    )
    
    db.add(new_path)
    db.commit()
    db.refresh(new_path)
    return new_path


@router.patch("/{path_id}", response_model=LearningPathResponse)
def update_learning_path(
    path_id: int,
    update_data: LearningPathUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update learning path (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    update_fields = update_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(path, key, value)
    
    path.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(path)
    return path


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete learning path (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    db.delete(path)
    db.commit()


# ==================== CHALLENGES ====================

@router.post("/{path_id}/challenges", response_model=PathChallengeResponse, status_code=status.HTTP_201_CREATED)
def add_challenge_to_path(
    path_id: int,
    challenge_data: PathChallengeBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add challenge to learning path (admin)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    new_challenge = PathChallenge(
        path_id=path_id,
        **challenge_data.dict()
    )
    
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    return new_challenge


@router.get("/{path_id}/challenges", response_model=List[PathChallengeResponse])
def get_path_challenges(
    path_id: int,
    db: Session = Depends(get_db)
):
    """Get all challenges in a learning path"""
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    challenges = db.query(PathChallenge).filter(
        PathChallenge.path_id == path_id
    ).order_by(PathChallenge.order).all()
    
    return challenges


@router.delete("/{path_id}/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_challenge_from_path(
    path_id: int,
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove challenge from learning path (admin)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    challenge = db.query(PathChallenge).filter(
        PathChallenge.path_id == path_id,
        PathChallenge.challenge_id == challenge_id
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found in this path")
    
    db.delete(challenge)
    db.commit()


# ==================== USER PROGRESS ====================

@router.post("/enroll", response_model=UserPathProgressResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll user in a learning path"""
    path = db.query(LearningPath).filter(
        LearningPath.id == path_id,
        LearningPath.status == "published"
    ).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    # Check if already enrolled
    existing = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this path")
    
    # Get total challenges
    total_challenges = db.query(PathChallenge).filter(
        PathChallenge.path_id == path_id
    ).count()
    
    progress = UserPathProgress(
        user_id=current_user.id,
        path_id=path_id,
        total_challenges=total_challenges,
        is_started=True,
        started_at=datetime.utcnow()
    )
    
    db.add(progress)
    db.commit()
    db.refresh(progress)
    
    # Emit real-time event
    await on_learning_path_enrolled(
        user_id=current_user.id,
        path_id=path_id,
        path_title=path.title,
        difficulty=path.difficulty
    )
    
    return progress


@router.get("/my-progress", response_model=List[UserPathProgressResponse])
def get_my_progress(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's path progress"""
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id
    ).order_by(
        desc(UserPathProgress.last_accessed_at)
    ).offset(skip).limit(limit).all()
    
    return progress


@router.get("/{path_id}/progress", response_model=PathProgressSummary)
def get_path_progress(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress in a specific path"""
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Not enrolled in this path")
    
    path = progress.path
    next_challenge = None
    
    if not progress.is_completed and progress.current_challenge_id:
        next_challenge = db.query(PathChallenge).filter(
            PathChallenge.id == progress.current_challenge_id
        ).first()
    
    return {
        "path": path,
        "progress": progress,
        "next_challenge": next_challenge,
        "completion_percentage": progress.completion_percentage
    }


@router.post("/{path_id}/complete-challenge")
async def complete_challenge(
    path_id: int,
    challenge_data: ChallengeCompletionData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark challenge as completed in path"""
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Not enrolled in this path")
    
    if progress.is_completed:
        raise HTTPException(status_code=400, detail="Path already completed")
    
    # Find and update challenge
    challenge = db.query(PathChallenge).filter(
        PathChallenge.path_id == path_id,
        PathChallenge.challenge_id == challenge_data.challenge_id
    ).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found in path")
    
    # Update progress
    progress.completed_challenges += 1
    progress.total_points_earned += challenge.points_value
    progress.last_accessed_at = datetime.utcnow()
    
    # Check if path is completed
    is_path_completed = False
    if progress.completed_challenges >= progress.total_challenges:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        is_path_completed = True
    
    progress.calculate_completion_percentage()
    
    db.commit()
    db.refresh(progress)
    
    # Get path info for event
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    
    # Emit real-time event for challenge completion
    await on_challenge_completed(
        user_id=current_user.id,
        path_id=path_id,
        challenge_id=challenge_data.challenge_id,
        challenge_name=challenge.name or f"Challenge {challenge_data.challenge_id}",
        points_earned=challenge.points_value,
        completion_percentage=progress.completion_percentage,
        is_path_completed=is_path_completed
    )
    
    return {
        "completed": True,
        "progress": progress,
        "path_completed": progress.is_completed
    }


@router.post("/{path_id}/progress/update", response_model=UserPathProgressResponse)
def update_path_progress(
    path_id: int,
    update_data: UserPathProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update path progress"""
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Not enrolled in this path")
    
    update_fields = update_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(progress, key, value)
    
    progress.last_accessed_at = datetime.utcnow()
    progress.calculate_completion_percentage()
    
    db.commit()
    db.refresh(progress)
    return progress


@router.delete("/{path_id}/unenroll", status_code=status.HTTP_204_NO_CONTENT)
def unenroll_from_path(
    path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unenroll from a learning path"""
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == path_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Not enrolled in this path")
    
    db.delete(progress)
    db.commit()


# ==================== STATS & ANALYTICS ====================

@router.get("/stats/popular", response_model=List[LearningPathResponse])
def get_popular_paths(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get most popular learning paths"""
    paths = db.query(LearningPath).filter(
        LearningPath.status == "published"
    ).order_by(
        desc(LearningPath.is_featured)
    ).limit(limit).all()
    
    return paths


@router.get("/user/{user_id}/paths", response_model=List[UserPathProgressResponse])
def get_user_paths(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's learning paths (public view)"""
    if user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == user_id,
        UserPathProgress.is_started == True
    ).all()
    
    return progress
