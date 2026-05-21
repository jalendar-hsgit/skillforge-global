"""
Gamification & Badge System Models
Supports achievement tracking, badge unlocking, and user progression
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Float, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class BadgeRarity(str, Enum):
    """Rarity levels for badges (affects visibility and points)"""
    COMMON = "common"  # 5 points
    UNCOMMON = "uncommon"  # 10 points
    RARE = "rare"  # 25 points
    EPIC = "epic"  # 50 points
    LEGENDARY = "legendary"  # 100 points


class BadgeCategory(str, Enum):
    """Badge categories for organization"""
    CHALLENGE = "challenge"  # Solving challenges
    STREAK = "streak"  # Consecutive achievements
    SOCIAL = "social"  # Community engagement
    SPEED = "speed"  # Time-based achievements
    MASTERY = "mastery"  # Language/skill mastery
    MILESTONE = "milestone"  # Major milestones
    CONTEST = "contest"  # Contest participation
    LEARNING = "learning"  # Course completion


class BadgeConditionType(str, Enum):
    """Types of conditions to unlock badges"""
    CHALLENGES_SOLVED = "challenges_solved"  # Solve N challenges
    STREAK_DAYS = "streak_days"  # N day streak
    CONTESTS_WON = "contests_won"  # Win N contests
    POINTS_EARNED = "points_earned"  # Earn N points
    LANGUAGE_MASTER = "language_master"  # Solve N challenges in a language
    FIRST_ACHIEVEMENT = "first_achievement"  # One-time (first solved, first badge, etc)
    SOCIAL_MILESTONES = "social_milestones"  # Followers, solutions shared
    TIME_MILESTONE = "time_milestone"  # Time-based (joined 1 year ago, etc)


class Badge(Base):
    """
    Represents an achievement badge that users can earn
    """
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    icon_url = Column(String(500), nullable=False)  # Badge icon/image
    icon_emoji = Column(String(10), nullable=True)  # Backup emoji icon

    # Badge classification
    category = Column(SQLEnum(BadgeCategory), nullable=False, index=True)
    rarity = Column(SQLEnum(BadgeRarity), default=BadgeRarity.COMMON)

    # Unlock condition
    condition_type = Column(SQLEnum(BadgeConditionType), nullable=False)
    condition_value = Column(Integer, nullable=False)  # N challenges, N days, etc
    condition_extra = Column(JSON, default={})  # Language, category, etc

    # Rewards
    points_value = Column(Integer, default=0)  # Base points for this badge
    coins_reward = Column(Integer, default=0)  # Coins for earning this badge

    # Metadata
    is_active = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=False)  # Hidden until unlocked
    tier = Column(Integer, default=1)  # 1, 2, 3 for progression badges
    extra_data = Column(JSON, default={})  # Custom metadata

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_badge_category_rarity", "category", "rarity"),
    )


class UserBadge(Base):
    """
    Represents a badge earned by a user
    Tracks when and how many times a user earned a badge (for tiered badges)
    """
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    
    # For tiered badges (can earn badge multiple times at different levels)
    tier = Column(Integer, default=1)
    earn_count = Column(Integer, default=1)  # How many times earned (for repeatable badges)

    # Timestamps
    first_earned_at = Column(DateTime, default=datetime.utcnow)
    last_earned_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    badge = relationship("Badge", foreign_keys=[badge_id], back_populates="user_badges")

    __table_args__ = (
        Index("ix_user_badge_user", "user_id", "badge_id", unique=True),
    )


class BadgeProgress(Base):
    """
    Tracks progress toward earning a badge
    For example: user has solved 7/10 challenges for "Solver" badge
    """
    __tablename__ = "badge_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)

    # Progress tracking
    current_value = Column(Integer, default=0)  # Current progress
    target_value = Column(Integer, nullable=False)  # Target to reach
    progress_percentage = Column(Float, default=0.0)  # 0-100

    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    badge = relationship("Badge", foreign_keys=[badge_id])

    __table_args__ = (
        Index("ix_badge_progress_user", "user_id", "badge_id", unique=True),
    )


class Leaderboard(Base):
    """
    Leaderboard entries for competitive ranking
    Can be by points, badges, contests won, challenges solved, etc
    """
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Leaderboard metrics
    total_points = Column(Integer, default=0, index=True)  # Total points earned
    challenges_solved = Column(Integer, default=0, index=True)
    badges_earned = Column(Integer, default=0, index=True)
    contests_won = Column(Integer, default=0, index=True)
    contests_participated = Column(Integer, default=0)
    solution_votes = Column(Integer, default=0)  # Upvotes on solutions

    # Ranking
    overall_rank = Column(Integer, nullable=True)  # 1, 2, 3, etc
    points_rank = Column(Integer, nullable=True)
    challenges_rank = Column(Integer, nullable=True)
    language_ranks = Column(JSON, default={})  # {language: rank}

    # Streaks and milestones
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_days_active = Column(Integer, default=0)

    # Time period (can have monthly, seasonal leaderboards)
    period = Column(String(20), default="all_time")  # "all_time", "monthly", "seasonal"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_leaderboard_overall_rank", "overall_rank"),
        Index("ix_leaderboard_points_rank", "points_rank"),
        Index("ix_leaderboard_total_points", "total_points"),
    )


class Achievement(Base):
    """
    One-time achievement tracking (different from badges)
    For special accomplishments or rare events
    """
    __tablename__ = "gamification_achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(String(500), nullable=False)
    icon_emoji = Column(String(10), nullable=True)

    # Type of achievement
    achievement_type = Column(String(50), nullable=False)  # "first_challenge", "speedrun", "perfect_score", etc

    # Points and rewards
    points = Column(Integer, default=10)
    coins_reward = Column(Integer, default=0)
    xp_reward = Column(Integer, default=50)

    # Metadata
    rarity = Column(String(20), default="common")  # common, rare, epic, legendary
    is_hidden = Column(Boolean, default=False)  # Hidden until unlocked

    # Extra data for tracking conditions
    extra_data = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserAchievement(Base):
    """
    Tracks which achievements a user has unlocked
    """
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("gamification_achievements.id", ondelete="CASCADE"), nullable=False)

    # Additional context
    context_data = Column(JSON, default={})  # Challenge id, score, time, etc

    # Timestamps
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    achievement = relationship("Achievement", foreign_keys=[achievement_id])

    __table_args__ = (
        Index("ix_user_achievement_user", "user_id", "achievement_id", unique=True),
    )
