from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True


# ============ User Profile Schemas ============

class UserProfileResponse(BaseModel):
    """User profile information (public view)"""
    id: int
    email: EmailStr
    name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    location: Optional[str]
    skills: List[str] = []
    sessions_completed: int
    avg_rating: float
    total_hours: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Update user profile"""
    name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    skills: Optional[List[str]] = None
    bio_visibility: Optional[str] = Field(None, pattern="^(public|private|friends_only)$")
    receive_notifications: Optional[str] = Field(None, pattern="^(all|important|none)$")


class UserStatsResponse(BaseModel):
    """User statistics and metrics"""
    user_id: int
    sessions_completed: int
    avg_rating: float
    total_hours: float
    recent_sessions: List[dict] = []
    courses_enrolled: int
    certificates_earned: int
    current_streak: int  # Learning streak days
    total_learning_time: float  # Total hours spent learning
    
    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """Public profile view (limited information)"""
    id: int
    name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    location: Optional[str]
    skills: List[str] = []
    avg_rating: float
    sessions_completed: int
    
    class Config:
        from_attributes = True
