"""
Pydantic schemas for recommendation endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# UserPreferences Schemas
class UserPreferencesCreate(BaseModel):
    preferred_difficulty: str = Field(..., description="easy, medium, hard")
    language_weights: Dict[str, float] = Field(default={}, description="Language: weight pairs")
    category_weights: Dict[str, float] = Field(default={}, description="Category: weight pairs")
    recommendation_style: str = Field(default="balanced", description="balanced, diverse, similar")
    skip_completed: bool = Field(default=True)
    skip_bookmarked: bool = Field(default=False)
    max_recommendations: int = Field(default=10, ge=1, le=50)


class UserPreferencesUpdate(BaseModel):
    preferred_difficulty: Optional[str] = None
    language_weights: Optional[Dict[str, float]] = None
    category_weights: Optional[Dict[str, float]] = None
    recommendation_style: Optional[str] = None
    skip_completed: Optional[bool] = None
    skip_bookmarked: Optional[bool] = None
    max_recommendations: Optional[int] = None


class UserPreferencesResponse(BaseModel):
    user_id: int
    preferred_difficulty: str
    language_weights: Dict[str, float]
    category_weights: Dict[str, float]
    recommendation_style: str
    skip_completed: bool
    skip_bookmarked: bool
    max_recommendations: int
    
    class Config:
        from_attributes = True


# ChallengeInteraction Schemas
class ChallengeInteractionCreate(BaseModel):
    user_id: int
    challenge_id: int
    view_count: int = Field(default=0, ge=0)
    attempt_count: int = Field(default=0, ge=0)
    completion_count: int = Field(default=0, ge=0)
    rating: Optional[int] = Field(None, ge=1, le=5)


class ChallengeInteractionUpdate(BaseModel):
    view_count: Optional[int] = None
    attempt_count: Optional[int] = None
    completion_count: Optional[int] = None
    total_time_seconds: Optional[int] = None
    rating: Optional[int] = None
    difficulty_rating: Optional[int] = None
    quality_rating: Optional[int] = None


class ChallengeInteractionResponse(BaseModel):
    id: int
    user_id: int
    challenge_id: int
    view_count: int
    attempt_count: int
    completion_count: int
    total_time_seconds: Optional[int]
    rating: Optional[int]
    difficulty_rating: Optional[int]
    quality_rating: Optional[int]
    similarity_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationCreate(BaseModel):
    user_id: int
    challenge_id: int
    algorithm: str = Field(default="collaborative_filtering")
    recommendation_reason: str
    matching_percentage: float = Field(..., ge=0.0, le=100.0)
    rank: int = Field(default=1, ge=1)


class RecommendationUpdate(BaseModel):
    was_viewed: Optional[bool] = None
    was_attempted: Optional[bool] = None
    was_completed: Optional[bool] = None
    is_dismissed: Optional[bool] = None


class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    challenge_id: int
    algorithm: str
    recommendation_reason: str
    matching_percentage: float
    rank: int
    was_viewed: bool
    was_attempted: bool
    was_completed: bool
    is_dismissed: bool
    recommended_at: datetime
    viewed_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# SimilarityMatrix Schemas
class SimilarityMatrixCreate(BaseModel):
    user_id_1: int
    user_id_2: int
    overall_similarity: float = Field(..., ge=0.0, le=1.0)
    skill_similarity: float = Field(..., ge=0.0, le=1.0)
    language_similarity: float = Field(..., ge=0.0, le=1.0)
    difficulty_similarity: float = Field(..., ge=0.0, le=1.0)
    learning_speed_similarity: float = Field(..., ge=0.0, le=1.0)


class SimilarityMatrixResponse(BaseModel):
    id: int
    user_id_1: int
    user_id_2: int
    overall_similarity: float
    skill_similarity: float
    language_similarity: float
    difficulty_similarity: float
    learning_speed_similarity: float
    common_challenges: int
    last_updated_at: datetime
    
    class Config:
        from_attributes = True


# RecommendationFeedback Schemas
class RecommendationFeedbackCreate(BaseModel):
    recommendation_id: int
    feedback_type: str = Field(..., description="too_easy, too_hard, not_relevant, good_recommendation")
    rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = None


class RecommendationFeedbackResponse(BaseModel):
    id: int
    recommendation_id: int
    user_id: int
    feedback_type: str
    rating: Optional[int]
    comments: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# RecommendationQueue Schemas
class RecommendationQueueCreate(BaseModel):
    user_id: int
    challenge_ids: List[int] = Field(default=[])
    recommendation_scores: List[float] = Field(default=[])


class RecommendationQueueUpdate(BaseModel):
    challenge_ids: Optional[List[int]] = None
    recommendation_scores: Optional[List[float]] = None
    current_index: Optional[int] = None
    completed_from_queue: Optional[int] = None


class RecommendationQueueResponse(BaseModel):
    id: int
    user_id: int
    challenge_ids: List[int]
    recommendation_scores: List[float]
    current_index: int
    completed_from_queue: int
    conversion_rate: float
    last_updated_at: datetime
    
    class Config:
        from_attributes = True


# Recommendation Endpoint Responses
class RecommendationsListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    total_count: int
    page: int
    page_size: int


class SimilarUsersResponse(BaseModel):
    user_id: int
    overall_similarity: float
    skill_similarity: float
    common_challenges: int
    shared_interests: List[str]


class PersonalizedQueueResponse(BaseModel):
    user_id: int
    queue: List[Dict]  # {challenge_id, score, reason}
    total_in_queue: int
    completed_today: int
    recommended_at: datetime
