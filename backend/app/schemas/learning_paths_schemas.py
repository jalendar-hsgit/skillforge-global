"""
Phase 3.4 Learning Paths Pydantic Schemas
Learning paths, certificates, skill validation, recommendations
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== LEARNING PATH SCHEMAS ====================

class PathDifficultyEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PathStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PathChallengeBase(BaseModel):
    challenge_id: int
    order: int
    required_previous_completion: bool = False
    min_score_for_unlock: Optional[float] = None
    points_value: int = 0
    estimated_minutes: Optional[int] = None


class PathChallengeResponse(PathChallengeBase):
    id: int
    path_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LearningPathBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = None
    difficulty: PathDifficultyEnum = PathDifficultyEnum.BEGINNER
    estimated_hours: Optional[int] = None
    is_featured: bool = False


class LearningPathCreate(LearningPathBase):
    pass


class LearningPathUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    difficulty: Optional[PathDifficultyEnum] = None
    estimated_hours: Optional[int] = None
    is_featured: Optional[bool] = None
    status: Optional[PathStatusEnum] = None


class LearningPathResponse(LearningPathBase):
    id: int
    status: str
    created_by: Optional[int]
    order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LearningPathWithChallenges(LearningPathResponse):
    challenges: List[PathChallengeResponse] = []


# ==================== USER PROGRESS SCHEMAS ====================

class UserPathProgressBase(BaseModel):
    user_id: int
    path_id: int


class UserPathProgressCreate(UserPathProgressBase):
    total_challenges: int


class UserPathProgressResponse(BaseModel):
    id: int
    user_id: int
    path_id: int
    total_challenges: int
    completed_challenges: int
    current_challenge_id: Optional[int]
    total_points_earned: int
    completion_percentage: float
    is_started: bool
    is_completed: bool
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_accessed_at: datetime
    
    class Config:
        from_attributes = True


class UserPathProgressUpdate(BaseModel):
    completed_challenges: Optional[int] = None
    current_challenge_id: Optional[int] = None
    total_points_earned: Optional[int] = None
    is_started: Optional[bool] = None
    is_completed: Optional[bool] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ==================== CERTIFICATE SCHEMAS ====================

class CertificateStatusEnum(str, Enum):
    EARNED = "earned"
    REVOKED = "revoked"
    EXPIRED = "expired"


class CertificateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    issuer: str = Field(default="SkillForge", max_length=255)


class CertificateCreate(BaseModel):
    user_id: int
    path_id: int
    title: str
    description: Optional[str] = None


class CertificateResponse(CertificateBase):
    id: int
    user_id: int
    path_id: int
    certificate_number: str
    status: str
    verification_code: Optional[str]
    earned_at: datetime
    expires_at: Optional[datetime]
    created_at: datetime
    certificate_url: Optional[str]
    badge_url: Optional[str]
    
    class Config:
        from_attributes = True


class CertificateVerifyRequest(BaseModel):
    certificate_number: str


class CertificateVerifyResponse(BaseModel):
    is_valid: bool
    user_name: Optional[str]
    path_title: Optional[str]
    earned_at: Optional[datetime]
    expires_at: Optional[datetime]


# ==================== SKILL VALIDATION SCHEMAS ====================

class SkillValidationBase(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=255)
    proficiency_level: str = Field(default="intermediate")
    confidence_score: float = Field(default=0.0, ge=0, le=100)
    validation_method: str


class SkillValidationCreate(SkillValidationBase):
    user_id: int
    path_id: Optional[int] = None
    validated_by: Optional[int] = None


class SkillValidationResponse(SkillValidationBase):
    id: int
    user_id: int
    path_id: Optional[int]
    validated_by: Optional[int]
    is_active: bool
    validated_at: datetime
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SkillValidationUpdate(BaseModel):
    proficiency_level: Optional[str] = None
    confidence_score: Optional[float] = None
    is_active: Optional[bool] = None


class UserSkillsResponse(BaseModel):
    user_id: int
    skills: List[SkillValidationResponse]
    skill_count: int


# ==================== RECOMMENDATION SCHEMAS ====================

class PathRecommendationBase(BaseModel):
    path_id: int
    reason: str
    recommendation_score: float = Field(default=0.0, ge=0, le=100)
    algorithm: str = Field(default="collaborative")


class PathRecommendationCreate(PathRecommendationBase):
    user_id: int


class PathRecommendationResponse(PathRecommendationBase):
    id: int
    user_id: int
    is_dismissed: bool
    dismissed_at: Optional[datetime]
    is_started: bool
    started_at: Optional[datetime]
    recommended_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecommendationFeedback(BaseModel):
    recommendation_id: int
    feedback_type: str  # "helpful", "not_helpful", "dismiss"
    notes: Optional[str] = None


class UserRecommendationsResponse(BaseModel):
    user_id: int
    total_recommendations: int
    pending_recommendations: int
    recommendations: List[PathRecommendationResponse]


# ==================== COMBINED RESPONSE SCHEMAS ====================

class PathProgressSummary(BaseModel):
    path: LearningPathResponse
    progress: UserPathProgressResponse
    next_challenge: Optional[PathChallengeResponse]
    completion_percentage: float


class UserLearningDashboard(BaseModel):
    user_id: int
    in_progress_paths: List[PathProgressSummary]
    completed_paths: List[LearningPathResponse]
    recommendations: List[PathRecommendationResponse]
    skills: List[SkillValidationResponse]
    certificates: List[CertificateResponse]
    total_points: int


class ChallengeCompletionData(BaseModel):
    path_id: int
    challenge_id: int
    score: float
    time_spent_minutes: Optional[int]
    notes: Optional[str] = None
