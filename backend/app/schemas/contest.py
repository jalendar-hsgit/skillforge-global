"""Contest and competition request/response schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ContestCreate(BaseModel):
    """Create contest request."""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    rules: Optional[str] = None
    contest_type: str = "individual"
    difficulty: str = "medium"
    category: str
    start_time: datetime
    end_time: datetime
    registration_deadline: datetime
    is_public: bool = True
    is_featured: bool = False
    entry_fee: int = 0
    total_prize_pool: int = 0
    max_participants: Optional[int] = None
    min_skill_level: int = 0
    banner_image: Optional[str] = None
    tags: Dict[str, Any] = {}


class ContestUpdate(BaseModel):
    """Update contest request."""
    title: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[str] = None
    status: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    banner_image: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None


class ContestResponse(BaseModel):
    """Contest response."""
    id: int
    title: str
    description: str
    contest_type: str
    difficulty: str
    category: str
    status: str
    is_public: bool
    is_featured: bool
    total_prize_pool: int
    total_participants: int
    total_submissions: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContestListResponse(ContestResponse):
    """Contest list response."""
    start_time: datetime
    end_time: datetime
    registration_deadline: datetime
    banner_image: Optional[str] = None
    max_participants: Optional[int] = None


class ContestDetailResponse(BaseModel):
    """Contest detail response."""
    id: int
    title: str
    description: str
    rules: Optional[str]
    contest_type: str
    difficulty: str
    category: str
    status: str
    is_public: bool
    is_featured: bool
    start_time: datetime
    end_time: datetime
    registration_deadline: datetime
    entry_fee: int
    total_prize_pool: int
    max_participants: Optional[int]
    min_skill_level: int
    banner_image: Optional[str]
    total_participants: int
    total_submissions: int
    created_at: datetime
    is_participant: bool = False
    participant_rank: Optional[int] = None
    participant_score: int = 0
    
    class Config:
        from_attributes = True


class ContestParticipationResponse(BaseModel):
    """Contest participation response."""
    id: int
    contest_id: int
    user_id: int
    joined_at: datetime
    is_active: bool
    total_points: int
    challenges_solved: int
    rank: Optional[int] = None
    percentile: Optional[float] = None
    last_submission_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContestSubmissionRequest(BaseModel):
    """Contest submission request."""
    challenge_id: int
    code: str = Field(..., min_length=1)
    language: str = "python"


class ContestSubmissionResponse(BaseModel):
    """Contest submission response."""
    id: int
    contest_id: int
    user_id: int
    challenge_id: int
    language: str
    status: str
    test_cases_passed: int
    test_cases_total: int
    points_earned: int
    execution_time_ms: Optional[int]
    memory_used_mb: Optional[int]
    error_message: Optional[str]
    submitted_at: datetime
    evaluated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ContestLeaderboardResponse(BaseModel):
    """Contest leaderboard entry response."""
    user_id: int
    rank: int
    score: int
    challenges_solved: int
    accuracy: float
    penalties: int
    current_streak: int
    best_streak: int
    last_accepted_time: Optional[datetime]
    updated_at: datetime
    
    class Config:
        from_attributes = True
