"""
Recommendation engine API endpoints
Provides personalized challenge recommendations using collaborative filtering,
similarity scoring, and user preference learning
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.core.security import get_current_user
from app.core.db import get_db
from app.modelsx.recommendations import (
    UserPreferences, ChallengeInteraction, Recommendation,
    SimilarityMatrix, RecommendationFeedback, RecommendationQueue
)
from app.models.user import User
from app.schemas.recommendations import (
    UserPreferencesCreate, UserPreferencesUpdate, UserPreferencesResponse,
    ChallengeInteractionResponse, RecommendationResponse, RecommendationCreate,
    RecommendationUpdate, SimilarityMatrixResponse, RecommendationFeedbackCreate,
    RecommendationFeedbackResponse, RecommendationQueueResponse,
    RecommendationsListResponse, SimilarUsersResponse, PersonalizedQueueResponse
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


# User Preferences Endpoints
@router.get("/preferences", response_model=UserPreferencesResponse)
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's recommendation preferences"""
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not prefs:
        # Create default preferences
        prefs = UserPreferences(
            user_id=current_user.id,
            preferred_difficulty="medium",
            recommendation_style="balanced"
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs


@router.put("/preferences", response_model=UserPreferencesResponse)
def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's recommendation preferences"""
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
    
    update_data = preferences.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)
    
    db.commit()
    db.refresh(prefs)
    return prefs


# Recommendation Endpoints
@router.get("/", response_model=RecommendationsListResponse)
def get_recommendations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    algorithm: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for the current user"""
    query = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.is_dismissed == False
    )
    
    if algorithm:
        query = query.filter(Recommendation.algorithm == algorithm)
    
    total_count = query.count()
    recommendations = query.order_by(
        desc(Recommendation.matching_percentage),
        Recommendation.rank
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return RecommendationsListResponse(
        recommendations=recommendations,
        total_count=total_count,
        page=page,
        page_size=page_size
    )


@router.post("/generate", response_model=List[RecommendationResponse])
def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized recommendations using collaborative filtering
    This endpoint triggers the recommendation algorithm
    """
    # Get user preferences
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not prefs:
        raise HTTPException(status_code=400, detail="User preferences not found")
    
    # Find similar users (collaborative filtering)
    similar_users = db.query(SimilarityMatrix).filter(
        or_(
            SimilarityMatrix.user_id_1 == current_user.id,
            SimilarityMatrix.user_id_2 == current_user.id
        )
    ).order_by(desc(SimilarityMatrix.overall_similarity)).limit(5).all()
    
    # Collect challenges from similar users
    recommendations = []
    rank = 1
    
    for similarity in similar_users:
        other_user_id = (
            similarity.user_id_2 if similarity.user_id_1 == current_user.id
            else similarity.user_id_1
        )
        
        # Get challenges from similar user
        challenges = db.query(ChallengeInteraction).filter(
            ChallengeInteraction.user_id == other_user_id,
            ChallengeInteraction.completion_count > 0
        ).order_by(desc(ChallengeInteraction.rating)).limit(5).all()
        
        for challenge in challenges:
            # Check if user already completed this challenge
            existing = db.query(ChallengeInteraction).filter(
                ChallengeInteraction.user_id == current_user.id,
                ChallengeInteraction.challenge_id == challenge.challenge_id
            ).first()
            
            if existing and existing.completion_count > 0:
                continue
            
            # Check if already recommended
            already_recommended = db.query(Recommendation).filter(
                Recommendation.user_id == current_user.id,
                Recommendation.challenge_id == challenge.challenge_id,
                Recommendation.is_dismissed == False
            ).first()
            
            if already_recommended:
                continue
            
            # Calculate matching percentage based on similarity and preference match
            matching_percentage = (
                similarity.overall_similarity * 100 * 0.7 +
                (challenge.rating or 3) * 20 if challenge.rating else 60
            )
            
            rec = Recommendation(
                user_id=current_user.id,
                challenge_id=challenge.challenge_id,
                algorithm="collaborative_filtering",
                recommendation_reason=f"Similar to users you learn like (Similarity: {similarity.overall_similarity:.1%})",
                matching_percentage=min(matching_percentage, 100),
                rank=rank
            )
            db.add(rec)
            recommendations.append(rec)
            rank += 1
            
            if rank > prefs.max_recommendations:
                break
        
        if rank > prefs.max_recommendations:
            break
    
    db.commit()
    
    # Refresh recommendations
    db.refresh_all(recommendations)
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recommendation"""
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Mark as viewed if not already
    if not rec.was_viewed:
        rec.was_viewed = True
        rec.viewed_at = datetime.utcnow()
        db.commit()
        db.refresh(rec)
    
    return rec


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    update: RecommendationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update recommendation status (viewed, attempted, completed, dismissed)"""
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    update_data = update.dict(exclude_unset=True)
    
    # Update completion timestamp
    if update_data.get("was_completed"):
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(rec, field, value)
    
    db.commit()
    db.refresh(rec)
    return rec


@router.post("/{recommendation_id}/dismiss", response_model=dict)
def dismiss_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss a recommendation"""
    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec.is_dismissed = True
    db.commit()
    
    return {"message": "Recommendation dismissed", "recommendation_id": recommendation_id}


# Feedback Endpoints
@router.post("/feedback", response_model=RecommendationFeedbackResponse)
def submit_recommendation_feedback(
    feedback: RecommendationFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on a recommendation to improve the algorithm"""
    # Verify recommendation exists and belongs to user
    rec = db.query(Recommendation).filter(
        Recommendation.id == feedback.recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Validate feedback type
    valid_types = ["too_easy", "too_hard", "not_relevant", "good_recommendation"]
    if feedback.feedback_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid feedback type. Must be one of: {valid_types}")
    
    fb = RecommendationFeedback(
        recommendation_id=feedback.recommendation_id,
        user_id=current_user.id,
        feedback_type=feedback.feedback_type,
        rating=feedback.rating,
        comments=feedback.comments
    )
    
    db.add(fb)
    db.commit()
    db.refresh(fb)
    
    return fb


# Similar Users Endpoint
@router.get("/similar-users", response_model=List[SimilarUsersResponse])
def get_similar_users(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users similar to the current user"""
    similarities = db.query(SimilarityMatrix).filter(
        or_(
            SimilarityMatrix.user_id_1 == current_user.id,
            SimilarityMatrix.user_id_2 == current_user.id
        )
    ).order_by(desc(SimilarityMatrix.overall_similarity)).limit(limit).all()
    
    results = []
    for sim in similarities:
        other_user_id = (
            sim.user_id_2 if sim.user_id_1 == current_user.id
            else sim.user_id_1
        )
        
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        results.append(SimilarUsersResponse(
            user_id=other_user_id,
            overall_similarity=sim.overall_similarity,
            skill_similarity=sim.skill_similarity,
            common_challenges=sim.common_challenges,
            shared_interests=[]  # Could be populated from preference overlap
        ))
    
    return results


# Recommendation Queue (Personalized Daily Challenge Queue)
@router.get("/queue", response_model=PersonalizedQueueResponse)
def get_personalized_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's personalized challenge queue"""
    queue = db.query(RecommendationQueue).filter(
        RecommendationQueue.user_id == current_user.id
    ).first()
    
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    
    # Build queue response with challenge details
    queue_items = []
    for i, challenge_id in enumerate(queue.challenge_ids):
        queue_items.append({
            "challenge_id": challenge_id,
            "score": queue.recommendation_scores[i] if i < len(queue.recommendation_scores) else 0,
            "position": i + 1
        })
    
    return PersonalizedQueueResponse(
        user_id=current_user.id,
        queue=queue_items,
        total_in_queue=len(queue.challenge_ids),
        completed_today=queue.completed_from_queue,
        recommended_at=queue.last_updated_at
    )


@router.post("/queue/refresh", response_model=PersonalizedQueueResponse)
def refresh_personalized_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh the personalized challenge queue"""
    queue = db.query(RecommendationQueue).filter(
        RecommendationQueue.user_id == current_user.id
    ).first()
    
    if not queue:
        # Create new queue
        queue = RecommendationQueue(user_id=current_user.id)
        db.add(queue)
    
    # Get latest recommendations
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.is_dismissed == False,
        Recommendation.was_completed == False
    ).order_by(desc(Recommendation.matching_percentage)).limit(10).all()
    
    # Update queue
    queue.challenge_ids = [r.challenge_id for r in recommendations]
    queue.recommendation_scores = [r.matching_percentage / 100.0 for r in recommendations]
    queue.current_index = 0
    queue.last_updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(queue)
    
    # Return response
    queue_items = []
    for i, challenge_id in enumerate(queue.challenge_ids):
        queue_items.append({
            "challenge_id": challenge_id,
            "score": queue.recommendation_scores[i],
            "position": i + 1
        })
    
    return PersonalizedQueueResponse(
        user_id=current_user.id,
        queue=queue_items,
        total_in_queue=len(queue.challenge_ids),
        completed_today=queue.completed_from_queue,
        recommended_at=queue.last_updated_at
    )


@router.post("/queue/next")
def get_next_queue_challenge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the next challenge from the queue"""
    queue = db.query(RecommendationQueue).filter(
        RecommendationQueue.user_id == current_user.id
    ).first()
    
    if not queue or queue.current_index >= len(queue.challenge_ids):
        raise HTTPException(status_code=400, detail="No more challenges in queue")
    
    challenge_id = queue.challenge_ids[queue.current_index]
    score = queue.recommendation_scores[queue.current_index]
    
    return {
        "challenge_id": challenge_id,
        "score": score,
        "position": queue.current_index + 1,
        "total_in_queue": len(queue.challenge_ids)
    }


@router.post("/queue/advance")
def advance_queue_position(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move to the next challenge in the queue"""
    queue = db.query(RecommendationQueue).filter(
        RecommendationQueue.user_id == current_user.id
    ).first()
    
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    
    if queue.current_index < len(queue.challenge_ids):
        queue.current_index += 1
        queue.completed_from_queue += 1
        queue.conversion_rate = (
            queue.completed_from_queue / len(queue.challenge_ids)
            if queue.challenge_ids else 0
        )
        db.commit()
    
    return {
        "current_position": queue.current_index,
        "total_in_queue": len(queue.challenge_ids),
        "conversion_rate": queue.conversion_rate
    }


# Statistics Endpoint
@router.get("/stats", response_model=dict)
def get_recommendation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics about recommendations for the user"""
    total_recs = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).count()
    
    viewed = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.was_viewed == True
    ).count()
    
    attempted = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.was_attempted == True
    ).count()
    
    completed = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.was_completed == True
    ).count()
    
    return {
        "total_recommendations": total_recs,
        "viewed": viewed,
        "attempted": attempted,
        "completed": completed,
        "view_rate": viewed / total_recs if total_recs > 0 else 0,
        "completion_rate": completed / total_recs if total_recs > 0 else 0
    }
