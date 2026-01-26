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


class UserInfo(BaseModel):
    """User info for mentor profile"""
    full_name: Optional[str] = None
    email: str

class MentorProfileResponse(BaseModel):
    """Public mentor profile"""
    id: int
    user_id: int
    email: str  # From user relationship (deprecated, use user.email)
    bio: str
    expertise: str
    hourly_rate: float
    status: MentorStatusEnum
    total_sessions: int
    average_rating: float
    user: Optional[UserInfo] = None  # Nested user object
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
    mentor_notes: Optional[str] = None
    student_feedback: Optional[str] = None
    created_at: datetime
    mentor_name: Optional[str] = None  # Added for display
    mentor_rating: Optional[float] = None  # Added for display
    
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

# ============ Mentor Verification Schemas ============

class DocumentTypeEnum(str, Enum):
    GOVERNMENT_ID = "government_id"
    DEGREE = "degree"
    CERTIFICATION = "certification"
    CREDENTIAL = "credential"


class VerificationStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class MentorVerificationResponse(BaseModel):
    """Mentor verification document response"""
    id: int
    mentor_id: int
    document_type: str
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    reviewer_notes: Optional[str]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MentorVerificationListResponse(BaseModel):
    """List of verification documents"""
    verifications: List[MentorVerificationResponse]
    total: int
    status: str  # Overall verification status


class AdminVerificationResponse(BaseModel):
    """Admin view of verification with mentor info"""
    id: int
    mentor_id: int
    mentor_name: str
    mentor_email: str
    document_type: str
    document_url: str
    document_name: str
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    reviewer_notes: Optional[str]
    
    class Config:
        from_attributes = True


class AdminVerificationUpdateRequest(BaseModel):
    """Admin updates verification status"""
    status: str = Field(..., description="approved or rejected")
    reviewer_notes: Optional[str] = Field(None, description="Reason for rejection or additional notes")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['approved', 'rejected']:
            raise ValueError("Status must be 'approved' or 'rejected'")
        return v


# ============ Feedback Schemas ============

class SessionFeedbackRequest(BaseModel):
    """Submit feedback for a session"""
    mentor_feedback: Optional[str] = Field(None, max_length=2000)
    student_notes: Optional[str] = Field(None, max_length=2000)
    recording_url: Optional[str] = Field(None, description="URL to session recording")
    duration_actual: Optional[int] = Field(None, ge=0, le=600, description="Actual session duration in minutes")
    session_quality_rating: Optional[int] = Field(None, ge=1, le=5, description="1-5 rating for session quality")
    key_topics: Optional[str] = Field(None, description="Comma-separated topics covered")
    follow_up_required: Optional[bool] = Field(False)


class SessionFeedbackResponse(BaseModel):
    """Session feedback response"""
    id: int
    session_id: int
    mentor_feedback: Optional[str]
    student_notes: Optional[str]
    recording_url: Optional[str]
    duration_actual: Optional[int]
    session_quality_rating: Optional[int]
    key_topics: Optional[str]
    follow_up_required: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Search & Filter Schemas ============

class MentorSearchRequest(BaseModel):
    """Advanced mentor search filters"""
    query: Optional[str] = Field(None, max_length=100, description="Text search (name, bio, expertise)")
    expertise: Optional[str] = Field(None, description="Comma-separated expertise paths to filter")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum average rating")
    max_price: Optional[float] = Field(None, ge=0, le=500, description="Maximum hourly rate")
    min_price: Optional[float] = Field(None, ge=0, le=500, description="Minimum hourly rate")
    availability: Optional[bool] = Field(None, description="Only show mentors with available slots")
    sort_by: Optional[str] = Field(default="name", description="Sort by: name, rating, price, newest")
    limit: Optional[int] = Field(default=20, ge=1, le=100)
    offset: Optional[int] = Field(default=0, ge=0)


class MentorSearchResponse(BaseModel):
    """Search results with pagination"""
    mentors: List['MentorProfileResponse']
    total: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True


# ============ Calendar & Export Schemas ============

class CalendarEventResponse(BaseModel):
    """Calendar event for session"""
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    mentor_name: str
    mentor_id: int
    status: str
    price: float
    
    class Config:
        from_attributes = True


class CalendarExportRequest(BaseModel):
    """Request calendar export"""
    format: str = Field(..., description="Export format: 'ical' or 'google'")
    include_past: Optional[bool] = Field(default=False, description="Include past sessions")


class ICalResponse(BaseModel):
    """iCalendar export response"""
    ical_data: str = Field(..., description="iCalendar (.ics) content")
    filename: str = Field(default="mentor-sessions.ics")


class GoogleCalendarResponse(BaseModel):
    """Google Calendar integration response"""
    auth_url: str = Field(..., description="OAuth authorization URL")
    calendar_id: Optional[str] = Field(None, description="Google Calendar ID if already linked")


# ============ Email Notification Schemas ============

class EmailNotificationRequest(BaseModel):
    """Email notification trigger"""
    session_id: int
    notification_type: str = Field(..., description="Type: confirmation, reminder, review_request")
    recipient_email: Optional[str] = Field(None, description="Override default recipient")


class EmailNotificationResponse(BaseModel):
    """Email notification response"""
    success: bool
    message: str
    session_id: int
    notification_type: str
    sent_at: datetime


# ============ Payment Schemas ============

class PaymentIntentRequest(BaseModel):
    """Request to create a payment intent for a mentor session"""
    session_id: int = Field(..., description="ID of the mentor session to pay for")


class PaymentIntentResponse(BaseModel):
    """Stripe payment intent response"""
    client_secret: str = Field(..., description="Stripe client secret for payment form")
    payment_intent_id: str = Field(..., description="Stripe payment intent ID")
    amount: float = Field(..., description="Amount to pay in USD")
    currency: str = Field(default="usd", description="Currency code")
    session_id: int = Field(..., description="Associated session ID")
    message: Optional[str] = Field(None, description="Additional message (e.g., for free sessions)")
    
    class Config:
        from_attributes = True