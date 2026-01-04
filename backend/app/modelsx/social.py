"""
User Follow System Models & Phase 3.3 Social Features
Social connections, forums, messaging, notifications, feed
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, String, Boolean, Text, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.db import Base


class UserFollow(Base):
    """
    Track user-to-user follow relationships
    """
    __tablename__ = "user_follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who is following
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who they're following
    
    followed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], backref="following")
    following = relationship("User", foreign_keys=[following_id], backref="followers")
    
    # Unique constraint - user can only follow another once
    __table_args__ = (UniqueConstraint('follower_id', 'following_id', name='unique_follow'),)


# NOTE: Forum models (ForumTopic, ForumThread, ForumReply) are defined in app/modelsx/forums.py
# Do not duplicate here to avoid SQLAlchemy MetaData conflicts


# ==================== MESSAGING MODELS ====================

class Conversation(Base):
    """Direct messaging conversation between two users"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    participant1_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    participant2_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    last_message_at = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participant1 = relationship("User", foreign_keys=[participant1_id], viewonly=True)
    participant2 = relationship("User", foreign_keys=[participant2_id], viewonly=True)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Direct message in a conversation"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    attachment_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], viewonly=True)


# NOTE: Notification class is defined in app/modelsx/notifications.py
# Do not duplicate here to avoid SQLAlchemy MetaData conflicts


# ==================== SOCIAL FEED MODELS ====================

class SocialFeedItem(Base):
    """Social feed items (activity stream)"""
    __tablename__ = "social_feed_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # course_completed, badge_earned, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    related_id = Column(Integer, nullable=True)
    data_metadata = Column(JSON, nullable=True)
    visibility = Column(String(20), default="public")  # public, friends_only, private
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)


# NOTE: UserProfile class is defined in app/modelsx/user_profiles.py
# Do not duplicate here to avoid SQLAlchemy MetaData conflicts
