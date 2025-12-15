"""
User Profile Models
Extended user information, statistics, and customization
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base


class UserProfile(Base):
    """
    Extended user profile information
    """
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Profile information
    bio = Column(Text)  # User bio/about
    location = Column(String)  # City/country
    website = Column(String)  # Personal website
    company = Column(String)  # Current company
    job_title = Column(String)  # Current job title
    
    # Profile customization
    avatar_url = Column(String)  # Profile picture URL
    cover_image_url = Column(String)  # Banner image
    theme_preference = Column(String, default="light")  # light, dark
    preferred_language = Column(String, default="python")  # Preferred programming language
    
    # Profile visibility
    is_public = Column(Boolean, default=True)  # Public profile
    show_statistics = Column(Boolean, default=True)  # Show stats
    show_activity = Column(Boolean, default=True)  # Show activity feed
    
    # Statistics (cached for performance)
    total_challenges_solved = Column(Integer, default=0)
    total_solutions_shared = Column(Integer, default=0)
    total_upvotes_received = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Profile badges and achievements
    badges = Column(JSON)  # List of badge IDs earned
    favorite_tags = Column(JSON)  # ["array", "sorting", "dp"]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="profile", uselist=False)


class UserActivity(Base):
    """
    Track user activity for feed/timeline
    """
    __tablename__ = "user_activity"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    activity_type = Column(String, nullable=False)  # "challenge_solved", "solution_shared", "achievement_earned", "streak_milestone"
    activity_data = Column(JSON)  # Flexible data storage
    
    # Reference to the actual object if applicable
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"))
    solution_id = Column(Integer, ForeignKey("challenge_solutions.id"))
    achievement_id = Column(Integer, ForeignKey("coding_achievements.id"))
    
    description = Column(String)  # Human-readable description
    is_public = Column(Boolean, default=True)  # Privacy control
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", backref="activity")
    challenge = relationship("CodingChallenge")


class UserPreferences(Base):
    """
    User settings and preferences
    """
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Notification preferences
    notify_challenge_reminders = Column(Boolean, default=True)
    notify_streak_achievements = Column(Boolean, default=True)
    notify_solution_votes = Column(Boolean, default=True)
    notify_comments = Column(Boolean, default=True)
    notify_friend_activity = Column(Boolean, default=True)
    
    # Learning preferences
    preferred_difficulty = Column(String, default="medium")  # easy, medium, hard
    show_hints_automatically = Column(Boolean, default=False)
    daily_challenge_enabled = Column(Boolean, default=True)
    
    # Privacy & Security
    email_visibility = Column(String, default="private")  # private, contacts, public
    profile_indexed = Column(Boolean, default=True)  # Allow search engines
    allow_suggestions = Column(Boolean, default=True)  # Personalized suggestions
    
    # Analytics
    allow_tracking = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="preferences", uselist=False)


class UserStatistics(Base):
    """
    Detailed user statistics for analytics
    """
    __tablename__ = "user_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Challenge statistics
    challenges_attempted = Column(Integer, default=0)
    challenges_completed = Column(Integer, default=0)
    challenges_perfect = Column(Integer, default=0)  # 100/100 score
    success_rate = Column(Float, default=0.0)  # Percentage
    
    # Solution statistics
    solutions_shared = Column(Integer, default=0)
    solutions_helpful_votes = Column(Integer, default=0)
    solutions_unhelpful_votes = Column(Integer, default=0)
    avg_solution_rating = Column(Float, default=0.0)
    
    # Streak statistics
    current_daily_streak = Column(Integer, default=0)
    longest_daily_streak = Column(Integer, default=0)
    streak_freeze_used = Column(Boolean, default=False)
    
    # Language statistics
    languages_used = Column(JSON)  # {"python": 15, "javascript": 8, "java": 3}
    most_used_language = Column(String)
    
    # Time statistics
    total_time_spent_minutes = Column(Integer, default=0)
    avg_time_per_challenge_minutes = Column(Float, default=0.0)
    fastest_completion_minutes = Column(Float)
    
    # Difficulty breakdown
    easy_solved = Column(Integer, default=0)
    medium_solved = Column(Integer, default=0)
    hard_solved = Column(Integer, default=0)
    
    # Coins
    total_coins_earned = Column(Integer, default=0)
    total_coins_spent = Column(Integer, default=0)
    coins_balance = Column(Integer, default=0)
    
    # Ranking
    global_rank = Column(Integer)  # Cached rank
    percentile = Column(Float)  # Top X% of users
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="statistics", uselist=False)
