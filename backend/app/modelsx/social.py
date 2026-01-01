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


# ==================== FORUM MODELS ====================

class ForumTopic(Base):
    """Forum topic/category"""
    __tablename__ = "forum_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="discussion")
    color = Column(String(20), default="blue")
    is_pinned = Column(Boolean, default=False)
    thread_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    last_activity_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    threads = relationship("ForumThread", back_populates="topic", cascade="all, delete-orphan")


class ForumThread(Base):
    """Forum discussion thread"""
    __tablename__ = "forum_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("forum_topics.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    reply_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    last_reply_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topic = relationship("ForumTopic", back_populates="threads")
    user = relationship("User", foreign_keys=[user_id], viewonly=True)
    replies = relationship("ForumReply", back_populates="thread", cascade="all, delete-orphan")


class ForumReply(Base):
    """Forum thread reply"""
    __tablename__ = "forum_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("forum_threads.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_best_answer = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    thread = relationship("ForumThread", back_populates="replies")
    user = relationship("User", foreign_keys=[user_id], viewonly=True)


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


# ==================== NOTIFICATION MODELS ====================

class NotificationStatus(str, enum.Enum):
    """Notification statuses"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class Notification(Base):
    """User notifications for platform activities"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    notification_type = Column(String(50), nullable=False, index=True)  # forum_reply, message, mention, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    related_id = Column(Integer, nullable=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD, index=True)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    action_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)
    actor = relationship("User", foreign_keys=[actor_id], viewonly=True)


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
    metadata = Column(JSON, nullable=True)
    visibility = Column(String(20), default="public")  # public, friends_only, private
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)


# ==================== USER PROFILE MODELS ====================

class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    banner_image_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    social_links = Column(JSON, nullable=True)
    interests = Column(JSON, nullable=True)
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    thread_count = Column(Integer, default=0)
    badge_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)
