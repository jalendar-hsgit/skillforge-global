"""
Phase 2.3 Database Models
=========================

Implements 10 new database models for:
- Mentor Verification & Documents
- Analytics & Metrics
- Payments & Payouts
- Video Sessions
- Messaging & Forums
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.db import Base


# ============================================================
# ENUMS
# ============================================================

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PayoutStatus(str, Enum):
    REQUESTED = "REQUESTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class VideoSessionStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ============================================================
# VERIFICATION & DOCUMENTS
# ============================================================

class MentorVerificationDocument(Base):
    """Documents uploaded for mentor verification"""
    __tablename__ = "mentor_verification_documents"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    document_type = Column(String(50), nullable=False)  # e.g., "CERTIFICATE", "DEGREE", "LICENSE"
    document_url = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin who verified
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    mentor = relationship("Mentor", backref="verification_documents")
    verified_by_user = relationship("User", foreign_keys=[verified_by])


# ============================================================
# ANALYTICS & METRICS
# ============================================================

class AnalyticsMetric(Base):
    """Real-time analytics metrics"""
    __tablename__ = "analytics_metrics"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # e.g., "SESSION_COUNT", "RATING", "EARNINGS"
    metric_value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    period = Column(String(20))  # "daily", "weekly", "monthly"
    
    mentor = relationship("Mentor", backref="metrics")


class MentorAnalyticsSummary(Base):
    """Aggregated analytics for mentors"""
    __tablename__ = "mentor_analytics_summaries"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), unique=True, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_hours = Column(Float, default=0.0)
    total_earnings = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    student_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)  # percentage
    response_time = Column(Integer, default=0)  # in minutes
    last_session_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    mentor = relationship("Mentor", backref="analytics_summary", uselist=False)


# ============================================================
# PAYMENTS & PAYOUTS
# ============================================================

class SessionPayment(Base):
    """Payment tracking for mentor sessions"""
    __tablename__ = "session_payments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mentor_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Stripe integration
    stripe_payment_id = Column(String(255), unique=True, nullable=True)
    stripe_payment_intent = Column(String(255), nullable=True)
    payment_method = Column(String(50), default="card")  # card, paypal, etc.
    
    # Metadata
    meta = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("MentorSession", backref="payment")
    user = relationship("User", foreign_keys=[user_id])
    mentor = relationship("Mentor", foreign_keys=[mentor_id], backref="session_payments")


# ============================================================
# VIDEO SESSIONS
# ============================================================

class VideoSession(Base):
    """Video session tracking"""
    __tablename__ = "video_sessions"

    id = Column(Integer, primary_key=True, index=True)
    mentor_session_id = Column(Integer, ForeignKey("mentor_sessions.id"), nullable=False)
    room_id = Column(String(255), unique=True, nullable=False)  # Jitsi room ID
    status = Column(SQLEnum(VideoSessionStatus), default=VideoSessionStatus.SCHEDULED)
    
    # Video provider (Jitsi, Zoom, etc.)
    provider = Column(String(50), default="jitsi")
    provider_session_id = Column(String(255), nullable=True)
    
    # Session details
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0)
    
    # Participant tracking
    mentor_joined_at = Column(DateTime, nullable=True)
    student_joined_at = Column(DateTime, nullable=True)
    
    # Recording
    is_recording = Column(Boolean, default=False)
    recording_url = Column(String(500), nullable=True)
    
    # Meeting details
    meeting_url = Column(String(500), nullable=True)
    password = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mentor_session = relationship("MentorSession", backref="video_session", uselist=False)


class SessionRecording(Base):
    """Session recording metadata"""
    __tablename__ = "session_recordings"

    id = Column(Integer, primary_key=True, index=True)
    video_session_id = Column(Integer, ForeignKey("video_sessions.id"), nullable=False)
    recording_url = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size = Column(Integer)  # in bytes
    duration_seconds = Column(Integer)
    
    # Provider details
    provider_recording_id = Column(String(255), nullable=True)
    
    # Processing
    is_processed = Column(Boolean, default=False)
    transcription_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # For soft delete
    
    # Relationships
    video_session = relationship("VideoSession", backref="recordings")


# ============================================================
# MESSAGING & CHAT
# ============================================================

class SessionChatMessage(Base):
    """Chat messages during sessions"""
    __tablename__ = "session_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    video_session_id = Column(Integer, ForeignKey("video_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    
    # Message metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    
    # Reactions & sentiment
    reactions = Column(JSON, default={})  # {"emoji": count}
    
    # Relationships
    video_session = relationship("VideoSession", backref="chat_messages")
    user = relationship("User", backref="session_chat_messages")


# NOTE: Message model is defined in app/modelsx/social.py
# Do not duplicate here to avoid SQLAlchemy MetaData conflicts


# ============================================================
# FORUM & DISCUSSIONS
# ============================================================
