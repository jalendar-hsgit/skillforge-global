from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MentorStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class SessionStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


# ============ Mentor Schemas ============

class MentorApplicationRequest(BaseModel):
    """Request to become a mentor"""
    bio: str = Field(..., min_length=50, max_length=1000, description="Your mentor bio (50-1000 chars)")
    expertise: str = Field(..., description="Comma-separated learning paths you can mentor (e.g., 'python-ai,web-dev')")
    hourly_rate: float = Field(default=0.0, ge=0, le=500, description="Hourly rate in USD (0 for free)")
    
    @validator('expertise')
    def validate_expertise(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Expertise cannot be empty')
        # Check if contains valid path names
        valid_paths = ['python-ai', 'web-dev', 'data-science', 'cloud', 'mobile']
        paths = [p.strip() for p in v.split(',')]
        for path in paths:
            if path not in valid_paths:
                raise ValueError(f'Invalid path: {path}. Valid: {valid_paths}')
        return v


class MentorProfileUpdate(BaseModel):
    """Update mentor profile"""
    bio: Optional[str] = Field(None, min_length=50, max_length=1000)
    expertise: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, ge=0, le=500)


class MentorProfileResponse(BaseModel):
    """Public mentor profile"""
    id: int
    user_id: int
    email: str  # From user relationship
    bio: str
    expertise: str
    hourly_rate: float
    status: MentorStatusEnum
    total_sessions: int
    average_rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class MentorEligibilityResponse(BaseModel):
    """Response for checking mentor eligibility"""
    eligible: bool
    reasons: List[str] = []
    completed_paths: List[str] = []
    average_quiz_score: float


# ============ Session Schemas ============

class SessionBookingRequest(BaseModel):
    """Request to book a mentor session"""
    mentor_id: int
    topic: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, ge=30, le=180)


class SessionUpdateRequest(BaseModel):
    """Update session details"""
    status: Optional[SessionStatusEnum] = None
    meeting_url: Optional[str] = None
    mentor_notes: Optional[str] = None
    student_feedback: Optional[str] = None


class SessionResponse(BaseModel):
    """Session details response"""
    id: int
    mentor_id: int
    student_id: int
    topic: str
    description: Optional[str]
    scheduled_at: datetime
    duration_minutes: int
    status: SessionStatusEnum
    meeting_url: Optional[str]
    price: float
    payment_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """List of sessions"""
    sessions: List[SessionResponse]
    total: int


# ============ Availability Schemas ============

class AvailabilitySlotRequest(BaseModel):
    """Add availability slot"""
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="0=Monday, 6=Sunday")
    date: Optional[datetime] = Field(None, description="Specific date if not recurring")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM format (e.g., '14:00')")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM format (e.g., '16:00')")
    timezone: str = Field(default="UTC")
    
    @validator('date', 'day_of_week')
    def validate_date_or_day(cls, v, values):
        # Either date or day_of_week must be set, not both
        if 'date' in values and 'day_of_week' in values:
            if values.get('date') and values.get('day_of_week') is not None:
                raise ValueError('Provide either date or day_of_week, not both')
        return v


class AvailabilitySlotResponse(BaseModel):
    """Availability slot response"""
    id: int
    mentor_id: int
    day_of_week: Optional[int]
    date: Optional[datetime]
    start_time: str
    end_time: str
    is_available: bool
    is_booked: bool
    timezone: str
    
    class Config:
        from_attributes = True


class AvailabilityListResponse(BaseModel):
    """List of availability slots"""
    slots: List[AvailabilitySlotResponse]


# ============ Message Schemas ============

class MessageSendRequest(BaseModel):
    """Send a message in a session"""
    session_id: int
    message: str = Field(..., min_length=1, max_length=5000)
    message_type: str = Field(default="text")


class MessageResponse(BaseModel):
    """Message response"""
    id: int
    session_id: int
    sender_id: int
    message: str
    message_type: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """List of messages"""
    messages: List[MessageResponse]
    total: int


# ============ Review Schemas ============

class ReviewSubmitRequest(BaseModel):
    """Submit a review for a mentor session"""
    session_id: int
    rating: int = Field(..., ge=1, le=5, description="1-5 star rating")
    review_text: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, description="Comma-separated tags (e.g., 'helpful,patient')")


class ReviewResponse(BaseModel):
    """Review response"""
    id: int
    mentor_id: int
    session_id: int
    student_id: int
    rating: int
    review_text: Optional[str]
    tags: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """List of reviews"""
    reviews: List[ReviewResponse]
    total: int
    average_rating: float


# ============ Dashboard Schemas ============

class MentorDashboardStats(BaseModel):
    """Mentor dashboard statistics"""
    total_sessions: int
    completed_sessions: int
    upcoming_sessions: int
    total_earnings: float
    average_rating: float
    total_reviews: int
    active_chats: int


class StudentDashboardStats(BaseModel):
    """Student dashboard for mentoring"""
    booked_sessions: int
    completed_sessions: int
    upcoming_sessions: int
    total_spent: float
    favorite_mentors: List[int] = []
