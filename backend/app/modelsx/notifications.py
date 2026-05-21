"""Real-time notifications system."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.db import Base


class NotificationType(str, Enum):
    """Notification type enum."""
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    CHALLENGE_SOLVED = "challenge_solved"
    CONTEST_UPDATE = "contest_update"
    FRIEND_ACTIVITY = "friend_activity"
    MENTION = "mention"
    COMMENT_REPLY = "comment_reply"
    LEADERBOARD_RANK = "leaderboard_rank"
    CODING_PRACTICE = "coding_practice"
    SOLUTION_FEEDBACK = "solution_feedback"
    COURSE_UPDATE = "course_update"
    SYSTEM_MESSAGE = "system_message"
    DAILY_CHALLENGE = "daily_challenge"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """User notifications and alerts."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification content
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Related entity
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who triggered it
    related_type = Column(String(50), nullable=True)  # achievement, challenge, contest, etc.
    related_id = Column(Integer, nullable=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Action link
    action_url = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    actor = relationship("User", foreign_keys=[actor_id], backref="notifications_triggered")
    
    def __repr__(self):
        return f"<Notification(user_id={self.user_id}, type={self.notification_type}, read={self.is_read})>"


class NotificationPreference(Base):
    """User notification preferences and settings."""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Type-based settings
    achievement_enabled = Column(Boolean, default=True)
    challenge_enabled = Column(Boolean, default=True)
    contest_enabled = Column(Boolean, default=True)
    friend_activity_enabled = Column(Boolean, default=True)
    mention_enabled = Column(Boolean, default=True)
    comment_reply_enabled = Column(Boolean, default=True)
    leaderboard_enabled = Column(Boolean, default=False)
    system_message_enabled = Column(Boolean, default=True)
    
    # Channel settings
    push_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    # Timing
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), default="22:00")  # HH:MM
    quiet_hours_end = Column(String(5), default="08:00")
    
    # Batching
    batch_similar = Column(Boolean, default=True)
    batch_delay_minutes = Column(Integer, default=5)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="notification_preferences")
    
    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id})>"


class NotificationLog(Base):
    """Log of sent notifications for tracking and analytics."""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Delivery tracking
    channel = Column(String(50), nullable=False)  # push, email, in_app
    status = Column(String(50), default="pending")  # pending, sent, failed, read
    
    # Metadata
    error_message = Column(Text, nullable=True)
    extra_data = Column(JSON, default={})
    
    # Timestamps
    sent_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    notification = relationship("Notification", backref="logs")
    user = relationship("User", backref="notification_logs")
    
    def __repr__(self):
        return f"<NotificationLog(notification_id={self.notification_id}, channel={self.channel}, status={self.status})>"


class NotificationTemplate(Base):
    """Pre-built notification templates for consistency."""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True)
    
    # Template info
    name = Column(String(100), unique=True, nullable=False)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    
    # Template content
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    
    # Default settings
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    action_url_template = Column(String(255), nullable=True)
    
    # Variables expected in extra_data
    variables = Column(JSON, default={})  # e.g., {actor_name, achievement_name, etc}
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationTemplate(name={self.name}, type={self.notification_type})>"
