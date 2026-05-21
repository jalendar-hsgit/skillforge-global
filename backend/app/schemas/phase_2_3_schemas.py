"""
Phase 2.3 Pydantic Schemas
==========================

Request/response models for all Phase 2.3 features
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator, EmailStr


# ============================================================
# ENUMS
# ============================================================

class VerificationStatusEnum(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PaymentStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PayoutStatusEnum(str, Enum):
    REQUESTED = "REQUESTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class VideoSessionStatusEnum(str, Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ============================================================
# VERIFICATION & DOCUMENTS
# ============================================================

class DocumentBase(BaseModel):
    document_type: str
    file_name: str


class DocumentRequest(DocumentBase):
    document_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    mentor_id: int
    document_url: str
    status: VerificationStatusEnum
    uploaded_at: datetime
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True


class VerificationStatusUpdate(BaseModel):
    status: VerificationStatusEnum
    rejection_reason: Optional[str] = None


# ============================================================
# ANALYTICS & METRICS
# ============================================================

class MetricBase(BaseModel):
    metric_type: str
    metric_value: float


class MetricResponse(MetricBase):
    id: int
    mentor_id: int
    recorded_at: datetime
    period: Optional[str] = None

    class Config:
        from_attributes = True


class AnalyticsSummaryResponse(BaseModel):
    id: int
    mentor_id: int
    total_sessions: int
    total_hours: float
    total_earnings: float
    average_rating: float
    student_count: int
    completion_rate: float
    response_time: int
    last_session_date: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# PAYMENTS & PAYOUTS
# ============================================================

class PaymentRequest(BaseModel):
    session_id: int
    amount: float
    currency: str = "USD"
    payment_method: str = "card"


class PaymentResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    mentor_id: int
    amount: float
    currency: str
    status: PaymentStatusEnum
    stripe_payment_id: Optional[str] = None
    stripe_payment_intent: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentHistoryResponse(BaseModel):
    id: int
    session_id: int
    amount: float
    currency: str
    status: PaymentStatusEnum
    created_at: datetime


class PayoutRequest(BaseModel):
    amount: Optional[float] = None  # If None, payout all available earnings


class PayoutResponse(BaseModel):
    id: int
    mentor_id: int
    amount: float
    currency: str
    status: PayoutStatusEnum
    stripe_payout_id: Optional[str] = None
    requested_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MentorBalanceResponse(BaseModel):
    mentor_id: int
    total_earned: float
    total_paid: float
    available_balance: float
    currency: str = "USD"


# ============================================================
# VIDEO SESSIONS
# ============================================================

class VideoSessionCreate(BaseModel):
    mentor_session_id: int
    provider: str = "jitsi"


class VideoSessionResponse(BaseModel):
    id: int
    mentor_session_id: int
    room_id: str
    status: VideoSessionStatusEnum
    provider: str
    meeting_url: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int
    is_recording: bool
    recording_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoSessionUpdate(BaseModel):
    status: Optional[VideoSessionStatusEnum] = None
    is_recording: Optional[bool] = None


# ============================================================
# SESSION RECORDINGS
# ============================================================

class SessionRecordingResponse(BaseModel):
    id: int
    video_session_id: int
    recording_url: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    duration_seconds: Optional[int] = None
    is_processed: bool
    transcription_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# CHAT MESSAGES
# ============================================================

class ChatMessageCreate(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    video_session_id: int
    user_id: int
    message: str
    created_at: datetime
    is_edited: bool
    reactions: dict = {}

    class Config:
        from_attributes = True


# ============================================================
# DIRECT MESSAGES
# ============================================================

class MessageCreate(BaseModel):
    recipient_id: int
    message: str
    attachments: Optional[List[dict]] = []


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    conversation_id: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    conversation_id: str
    other_user_id: int
    other_user_name: str
    other_user_avatar: Optional[str] = None
    last_message: str
    last_message_time: datetime
    unread_count: int


# ============================================================
# FORUM - TOPICS
# ============================================================

class ForumTopicCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None


class ForumTopicResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    thread_count: int
    reply_count: int
    is_locked: bool
    is_archived: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# FORUM - THREADS
# ============================================================

class ForumThreadCreate(BaseModel):
    topic_id: int
    title: str
    content: str
    tags: Optional[List[str]] = []


class ForumThreadUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_resolved: Optional[bool] = None


class ForumThreadResponse(BaseModel):
    id: int
    topic_id: int
    creator_id: int
    creator_name: Optional[str] = None
    creator_avatar: Optional[str] = None
    title: str
    slug: str
    content: str
    is_pinned: bool
    is_locked: bool
    is_resolved: bool
    reply_count: int
    view_count: int
    like_count: int
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumThreadListResponse(BaseModel):
    id: int
    title: str
    slug: str
    creator_name: str
    reply_count: int
    view_count: int
    like_count: int
    is_pinned: bool
    is_locked: bool
    is_resolved: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime


# ============================================================
# FORUM - REPLIES
# ============================================================

class ForumReplyCreate(BaseModel):
    content: str


class ForumReplyUpdate(BaseModel):
    content: str


class ForumReplyResponse(BaseModel):
    id: int
    thread_id: int
    creator_id: int
    creator_name: Optional[str] = None
    creator_avatar: Optional[str] = None
    content: str
    is_marked_solution: bool
    is_edited: bool
    like_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
