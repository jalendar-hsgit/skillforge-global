from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class MentorStatus(str, enum.Enum):
    """Mentor status enumeration"""
    PENDING = "pending"  # Application submitted
    APPROVED = "approved"  # Can take sessions
    REJECTED = "rejected"  # Application denied
    SUSPENDED = "suspended"  # Temporarily disabled


class Mentor(Base):
    """
    Mentor profiles for users who qualify to mentor others.
    
    Eligibility Requirements:
    - Completed at least one learning path (100% progress)
    - Achieved 80%+ average on quizzes
    - Optional: minimum time as user (e.g., 30 days)
    """
    __tablename__ = "mentors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Profile Information
    bio = Column(Text, nullable=False)  # Mentor's bio/introduction
    expertise = Column(String, nullable=False)  # Comma-separated paths (e.g., "python-ai,web-dev")
    hourly_rate = Column(Float, default=0.0)  # USD per hour (0 = free)
    
    # Status
    status = Column(Enum(MentorStatus), default=MentorStatus.PENDING, nullable=False, index=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Statistics
    total_sessions = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_earnings = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # Note: User relationship commented to avoid circular import at mapper initialization
    # user = relationship("User", foreign_keys=[user_id], viewonly=True)
    sessions = relationship("MentorSession", back_populates="mentor", cascade="all, delete-orphan")
    availability = relationship("MentorAvailability", back_populates="mentor", cascade="all, delete-orphan")
    reviews = relationship("MentorReview", back_populates="mentor", cascade="all, delete-orphan")
    documents = relationship("MentorDocument", back_populates="mentor", cascade="all, delete-orphan")  # Phase 3A
    # Note: payment_methods and payout_requests will load via lazy importing
    
    def __repr__(self):
        return f"<Mentor(id={self.id}, user_id={self.user_id}, status={self.status})>"


class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    PENDING = "pending"  # Booked, awaiting confirmation
    CONFIRMED = "confirmed"  # Confirmed by mentor
    COMPLETED = "completed"  # Session finished
    CANCELLED = "cancelled"  # Cancelled by either party
    NO_SHOW = "no_show"  # Student didn't attend


class MentorSession(Base):
    """
    One-on-one mentoring sessions between mentors and students.
    """
    __tablename__ = "mentor_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session Details
    topic = Column(String, nullable=False)  # Session topic/focus
    description = Column(Text, nullable=True)  # Additional details
    scheduled_at = Column(DateTime, nullable=False, index=True)  # Start time
    duration_minutes = Column(Integer, default=60, nullable=False)  # Session length
    
    # Status & URLs
    status = Column(Enum(SessionStatus), default=SessionStatus.PENDING, nullable=False, index=True)
    meeting_url = Column(String, nullable=True)  # Zoom/Meet link
    
    # Payment
    price = Column(Float, default=0.0)  # Amount charged
    payment_status = Column(String, default="pending")  # pending, paid, refunded, captured
    payment_intent_id = Column(String, nullable=True)  # Stripe PaymentIntent ID
    
    # Notes
    mentor_notes = Column(Text, nullable=True)  # Mentor's private notes
    student_feedback = Column(Text, nullable=True)  # Student's feedback after session

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    mentor = relationship("Mentor", back_populates="sessions")
    student = relationship("User", foreign_keys=[student_id], lazy="joined")
    review = relationship("MentorReview", uselist=False, back_populates="session")
    feedback = relationship("SessionFeedback", uselist=False, back_populates="session")
    # chat_files = relationship("MentorChatFile", back_populates="session")  # TODO: Define MentorChatFile model

    @property
    def rating(self):
        return self.review.rating if self.review else None
    
    def __repr__(self):
        return f"<MentorSession(id={self.id}, mentor_id={self.mentor_id}, status={self.status})>"


class MentorAvailability(Base):
    """
    Mentor availability schedule.
    Can be recurring (e.g., every Monday 2-4pm) or specific dates.
    """
    __tablename__ = "mentor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Time Slot
    day_of_week = Column(Integer, nullable=True)  # 0-6 (Mon-Sun) for recurring, NULL for specific date
    date = Column(DateTime, nullable=True)  # Specific date if not recurring
    start_time = Column(String, nullable=False)  # "14:00" format
    end_time = Column(String, nullable=False)  # "16:00" format
    
    # Availability
    is_available = Column(Boolean, default=True)  # Can be toggled off
    is_booked = Column(Boolean, default=False)  # Slot is booked
    
    # Timezone
    timezone = Column(String, default="UTC")  # Timezone for the slot
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    mentor = relationship("Mentor", back_populates="availability")
    
    def __repr__(self):
        return f"<MentorAvailability(id={self.id}, mentor_id={self.mentor_id}, day={self.day_of_week})>"


class MentorMessage(Base):
    """
    Real-time chat messages between mentors and students.
    """
    __tablename__ = "mentor_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mentor_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message Content
    message = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, image, file, system
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    # session = relationship("MentorSession")
    
    def __repr__(self):
        return f"<MentorMessage(id={self.id}, session_id={self.session_id}, sender_id={self.sender_id})>"


class MentorReview(Base):
    """
    Student reviews and ratings for mentors after sessions.
    """
    __tablename__ = "mentor_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("mentor_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Rating & Review
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    
    # Tags (helpful, knowledgeable, patient, etc.)
    tags = Column(String, nullable=True)  # Comma-separated
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    mentor = relationship("Mentor", back_populates="reviews")
    session = relationship("MentorSession", back_populates="review")
    # student = relationship("app.models.user.User", foreign_keys=[student_id])
    
    def __repr__(self):
        return f"<MentorReview(id={self.id}, mentor_id={self.mentor_id}, rating={self.rating})>"


class SessionFeedback(Base):
    """
    Post-session feedback from mentor and student.
    Stores mentor notes, student feedback, and additional metadata.
    """
    __tablename__ = "session_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mentor_sessions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Feedback Content
    mentor_feedback = Column(Text, nullable=True)  # Mentor's post-session notes
    student_notes = Column(Text, nullable=True)  # Student's summary of what they learned
    recording_url = Column(String, nullable=True)  # Link to session recording/video
    
    # Metadata
    duration_actual = Column(Integer, nullable=True)  # Actual session duration in minutes
    session_quality_rating = Column(Integer, nullable=True)  # 1-5 rating for session quality
    key_topics = Column(String, nullable=True)  # Comma-separated topics covered
    follow_up_required = Column(Boolean, default=False)  # Whether follow-up session needed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("MentorSession", back_populates="feedback")
    
    def __repr__(self):
        return f"<SessionFeedback(id={self.id}, session_id={self.session_id})>"
