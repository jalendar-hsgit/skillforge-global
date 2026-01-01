"""
Path Recommendations API Router - Phase 3.4
Personalized learning path recommendations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models import User
from app.modelsx.learning_paths import PathRecommendation, LearningPath, UserPathProgress
from app.schemas.learning_paths_schemas import (
    PathRecommendationResponse, PathRecommendationCreate,
    UserRecommendationsResponse, RecommendationFeedback
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=PathRecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    rec_data: PathRecommendationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create path recommendation (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if already recommended
    existing = db.query(PathRecommendation).filter(
        PathRecommendation.user_id == rec_data.user_id,
        PathRecommendation.path_id == rec_data.path_id,
        PathRecommendation.is_dismissed == False
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already recommended to this user")
    
    recommendation = PathRecommendation(
        **rec_data.dict(),
        recommended_at=datetime.utcnow()
    )
    
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation


@router.get("/my-recommendations", response_model=UserRecommendationsResponse)
def get_my_recommendations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for current user"""
    recommendations = db.query(PathRecommendation).filter(
        PathRecommendation.user_id == current_user.id,
        PathRecommendation.is_dismissed == False
    ).order_by(
        desc(PathRecommendation.recommendation_score),
        desc(PathRecommendation.recommended_at)
    ).offset(skip).limit(limit).all()
    
    total = db.query(PathRecommendation).filter(
        PathRecommendation.user_id == current_user.id,
        PathRecommendation.is_dismissed == False
    ).count()
    
    pending = db.query(PathRecommendation).filter(
        PathRecommendation.user_id == current_user.id,
        PathRecommendation.is_dismissed == False,
        PathRecommendation.is_started == False
    ).count()
    
    return {
        "user_id": current_user.id,
        "total_recommendations": total,
        "pending_recommendations": pending,
        "recommendations": recommendations
    }


@router.get("/{recommendation_id}", response_model=PathRecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific recommendation"""
    recommendation = db.query(PathRecommendation).filter(
        PathRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Check authorization
    if recommendation.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return recommendation


@router.post("/{recommendation_id}/dismiss")
def dismiss_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss a recommendation"""
    recommendation = db.query(PathRecommendation).filter(
        PathRecommendation.id == recommendation_id,
        PathRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.is_dismissed = True
    recommendation.dismissed_at = datetime.utcnow()
    db.commit()
    db.refresh(recommendation)
    
    return {"dismissed": True}


@router.post("/{recommendation_id}/accept")
def accept_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept and start recommended path"""
    recommendation = db.query(PathRecommendation).filter(
        PathRecommendation.id == recommendation_id,
        PathRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Check if already enrolled
    existing_progress = db.query(UserPathProgress).filter(
        UserPathProgress.user_id == current_user.id,
        UserPathProgress.path_id == recommendation.path_id
    ).first()
    
    if existing_progress:
        raise HTTPException(status_code=400, detail="Already enrolled in this path")
    
    # Get path
    path = db.query(LearningPath).filter(LearningPath.id == recommendation.path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    # Create progress record
    from sqlalchemy import func
    total_challenges = db.query(func.count(PathRecommendation)).filter(
        PathRecommendation.path_id == path.id
    ).scalar()
    
    progress = UserPathProgress(
        user_id=current_user.id,
        path_id=recommendation.path_id,
        total_challenges=total_challenges or 0,
        is_started=True,
        started_at=datetime.utcnow()
    )
    
    # Mark recommendation as started
    recommendation.is_started = True
    recommendation.started_at = datetime.utcnow()
    
    db.add(progress)
    db.commit()
    db.refresh(recommendation)
    
    return {
        "accepted": True,
        "recommendation": recommendation,
        "progress_created": True
    }


@router.post("/{recommendation_id}/feedback")
def provide_recommendation_feedback(
    recommendation_id: int,
    feedback: RecommendationFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Provide feedback on recommendation"""
    recommendation = db.query(PathRecommendation).filter(
        PathRecommendation.id == recommendation_id,
        PathRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Process feedback
    if feedback.feedback_type == "helpful":
        recommendation.recommendation_score = min(100, recommendation.recommendation_score + 10)
    elif feedback.feedback_type == "not_helpful":
        recommendation.recommendation_score = max(0, recommendation.recommendation_score - 10)
    elif feedback.feedback_type == "dismiss":
        recommendation.is_dismissed = True
        recommendation.dismissed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(recommendation)
    
    return {
        "feedback_recorded": True,
        "recommendation": recommendation
    }


@router.get("/user/{user_id}", response_model=List[PathRecommendationResponse])
def get_user_recommendations(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's recommendations"""
    if user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    recommendations = db.query(PathRecommendation).filter(
        PathRecommendation.user_id == user_id,
        PathRecommendation.is_dismissed == False
    ).order_by(
        desc(PathRecommendation.recommendation_score)
    ).all()
    
    return recommendations


@router.post("/batch-create")
def batch_create_recommendations(
    recommendations: List[PathRecommendationCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple recommendations at once (admin)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    created = []
    skipped = []
    
    for rec_data in recommendations:
        # Check if already exists
        existing = db.query(PathRecommendation).filter(
            PathRecommendation.user_id == rec_data.user_id,
            PathRecommendation.path_id == rec_data.path_id,
            PathRecommendation.is_dismissed == False
        ).first()
        
        if existing:
            skipped.append({
                "user_id": rec_data.user_id,
                "path_id": rec_data.path_id,
                "reason": "Already recommended"
            })
            continue
        
        recommendation = PathRecommendation(
            **rec_data.dict(),
            recommended_at=datetime.utcnow()
        )
        db.add(recommendation)
        created.append(recommendation)
    
    db.commit()
    
    return {
        "created": len(created),
        "skipped": len(skipped),
        "skipped_details": skipped
    }


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete recommendation (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    recommendation = db.query(PathRecommendation).filter(
        PathRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    db.delete(recommendation)
    db.commit()
