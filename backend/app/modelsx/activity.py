"""
Social Activity and Feed Models for Social Feeds & Activity Timeline Feature
Supports user activity tracking, engagement metrics, and trending content discovery
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, 
    JSON, Float, Enum as SQLEnum, Index, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ActivityType(str, Enum):
    """Types of activities tracked in the system"""
    CHALLENGE_SOLVED = "challenge_solved"
    BADGE_EARNED = "badge_earned"
    CONTEST_PARTICIPATED = "contest_participated"
    CONTEST_WON = "contest_won"
    SOLUTION_SHARED = "solution_shared"
    COURSE_COMPLETED = "course_completed"
    PATH_STARTED = "path_started"
    PATH_COMPLETED = "path_completed"
    USER_FOLLOWED = "user_followed"
    STREAK_ACHIEVED = "streak_achieved"
    COMMENT_POSTED = "comment_posted"
    SOLUTION_UPVOTED = "solution_upvoted"
    MENTOR_SESSION = "mentor_session"
    AI_HINT_USED = "ai_hint_used"
    POINTS_EARNED = "points_earned"
    LEADERBOARD_RANK = "leaderboard_rank"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class ActivityVisibility(str, Enum):
    """Visibility levels for activities"""
    PUBLIC = "public"  # Visible to all users
    FOLLOWERS = "followers"  # Visible to followers only
    PRIVATE = "private"  # Visible to user only


class Activity(Base):
    """
    Represents a user activity event (challenge solved, badge earned, etc.)
    Feeds are built by querying activities of followed users
    """
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(SQLEnum(ActivityType), nullable=False, index=True)
    
    # Related entity (challenge, badge, contest, etc.)
    related_type = Column(String(50), nullable=False)  # "challenge", "badge", "contest", etc.
    related_id = Column(Integer, nullable=False)  # ID of related entity
    
    # Activity description and details
    title = Column(String(255), nullable=False)  # e.g., "Solved: Binary Search Tree"
    description = Column(Text, nullable=True)  # Optional detailed description
    
    # Metrics and metadata
    points_earned = Column(Integer, default=0)  # Points from this activity
    extra_data = Column(JSON, default={})  # Language, difficulty, contest tier, etc.
    
    # Engagement metrics
    like_count = Column(Integer, default=0, index=True)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Visibility and features
    visibility = Column(SQLEnum(ActivityVisibility), default=ActivityVisibility.PUBLIC)
    is_featured = Column(Boolean, default=False)  # Admin feature flag
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    likes = relationship("ActivityLike", back_populates="activity", cascade="all, delete-orphan")
    comments = relationship("ActivityComment", back_populates="activity", cascade="all, delete-orphan")
    
    # Index for efficient feed queries
    __table_args__ = (
        Index("ix_activity_user_created", "user_id", "created_at"),
        Index("ix_activity_type_created", "activity_type", "created_at"),
        Index("ix_activity_visibility_created", "visibility", "created_at"),
    )


class ActivityLike(Base):
    """
    Represents a user liking an activity (engagement metric)
    """
    __tablename__ = "activity_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    activity = relationship("Activity", foreign_keys=[activity_id], back_populates="likes")
    user = relationship("User", foreign_keys=[user_id])
    
    # Prevent duplicate likes
    __table_args__ = (
        Index("ix_activity_like_unique", "activity_id", "user_id", unique=True),
    )


class ActivityComment(Base):
    """
    Represents a comment on an activity (engagement)
    """
    __tablename__ = "activity_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    content = Column(Text, nullable=False)
    
    # Engagement on comments
    like_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activity = relationship("Activity", foreign_keys=[activity_id], back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index("ix_activity_comment_activity", "activity_id", "created_at"),
    )


class FeedSettings(Base):
    """
    User preferences for their personalized feed
    """
    __tablename__ = "feed_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Activity type filters (which activities to show)
    show_challenge_solved = Column(Boolean, default=True)
    show_badge_earned = Column(Boolean, default=True)
    show_contest_activity = Column(Boolean, default=True)
    show_solutions = Column(Boolean, default=True)
    show_course_progress = Column(Boolean, default=True)
    show_follows = Column(Boolean, default=True)
    
    # Feed algorithm preferences
    sort_by = Column(String(20), default="recent")  # "recent", "trending", "engagement"
    include_system_announcements = Column(Boolean, default=True)
    
    # Notification preferences
    notify_activity_likes = Column(Boolean, default=True)
    notify_activity_comments = Column(Boolean, default=True)
    notify_follower_activity = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class Trending(Base):
    """
    Represents trending content (challenges, solutions, topics)
    Updated periodically by background jobs or on-demand
    """
    __tablename__ = "trending"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content identification
    content_type = Column(String(50), nullable=False, index=True)  # "challenge", "solution", "topic", "user"
    content_id = Column(Integer, nullable=False)
    
    # Trending metrics
    trend_score = Column(Float, nullable=False, index=True)  # Composite score for ranking
    rank = Column(Integer, nullable=False, index=True)  # Current rank (1, 2, 3, ...)
    
    # Engagement in trending period (last 24-72 hours)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    velocity = Column(Float, default=0.0)  # Growth rate
    
    # Metadata
    extra_data = Column(JSON, default={})  # difficulty, category, language, etc.
    
    # Time tracking
    started_trending = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # When item falls off trending
    
    __table_args__ = (
        Index("ix_trending_type_score", "content_type", "trend_score"),
        Index("ix_trending_rank", "rank"),
    )


class Timeline(Base):
    """
    User's personal timeline - curated view of their own activities
    Useful for public profiles showing user's achievement history
    """
    __tablename__ = "timelines"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Stats
    total_activities = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    challenges_solved = Column(Integer, default=0)
    badges_earned = Column(Integer, default=0)
    paths_completed = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)  # likes + comments + shares
    
    # Milestones
    first_activity_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    longest_streak = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    
    # Profile info
    bio = Column(Text, nullable=True)
    public_profile = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
