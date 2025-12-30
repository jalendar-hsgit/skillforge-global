"""
User Recommendations Engine Models
Supports collaborative filtering, personalized recommendations, and feedback tracking
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey,
    JSON, Index
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class UserPreferences(Base):
    """
    Stores user's explicit preferences for recommendations
    """
    __tablename__ = "user_preferences_recs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Difficulty preference
    preferred_difficulty = Column(String(20), default="mixed")  # "easy", "medium", "hard", "mixed"
    min_difficulty = Column(String(20), default="easy")
    max_difficulty = Column(String(20), default="hard")

    # Language preferences (JSON list)
    preferred_languages = Column(JSON, default=[])  # ["python", "javascript"]
    language_weights = Column(JSON, default={})  # {"python": 0.8, "javascript": 0.5}

    # Category preferences
    preferred_categories = Column(JSON, default=[])  # ["arrays", "strings", "graphs"]
    category_weights = Column(JSON, default={})

    # Recommendation settings
    recommendation_style = Column(String(30), default="progressive")  # "progressive", "challenging", "balanced"
    skip_completed = Column(Boolean, default=True)  # Skip already solved challenges
    skip_bookmarked = Column(Boolean, default=False)  # Skip bookmarked challenges
    max_recommendations = Column(Integer, default=10)

    # Updated tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class ChallengeInteraction(Base):
    """
    Tracks user interactions with challenges for collaborative filtering
    Includes views, attempts, completions, time spent, ratings
    """
    __tablename__ = "challenge_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, nullable=False, index=True)  # Could be any coding challenge ID

    # Interaction type and metrics
    interaction_type = Column(String(30), nullable=False)  # "view", "attempt", "completion", "hint_used", "solution_viewed"
    view_count = Column(Integer, default=0)
    attempt_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)

    # Time tracking
    first_viewed_at = Column(DateTime, nullable=True)
    last_viewed_at = Column(DateTime, nullable=True)
    total_time_seconds = Column(Integer, default=0)

    # Rating and feedback
    rating = Column(Integer, nullable=True)  # 1-5 stars
    difficulty_rating = Column(Integer, nullable=True)  # User's perceived difficulty: 1-5
    quality_rating = Column(Integer, nullable=True)  # Quality of problem: 1-5
    feedback = Column(String(200), nullable=True)  # User's text feedback

    # Computed similarity features (for ML models)
    similarity_score = Column(Float, default=0.0)  # Pre-computed similarity to user's history

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_challenge_interaction_user", "user_id", "challenge_id", unique=True),
        Index("ix_challenge_interaction_created", "user_id", "created_at"),
    )


class Recommendation(Base):
    """
    Stores generated recommendations for users
    Enables tracking which recommendations are accepted/ignored
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(Integer, nullable=False)  # Recommended challenge

    # Recommendation metadata
    recommendation_reason = Column(String(100), nullable=False)  # "similar_difficulty", "skill_gap", "trending", "trending_in_skill"
    matching_percentage = Column(Float, default=0.0)  # 0-100% match score
    rank = Column(Integer, default=0)  # Position in recommendation list

    # Recommendation quality tracking
    algorithm_version = Column(String(20), default="v1")  # Which algo generated this
    extra_data = Column(JSON, default={})  # Challenge metadata snapshot

    # Engagement tracking
    was_viewed = Column(Boolean, default=False)
    was_attempted = Column(Boolean, default=False)
    was_completed = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)

    # Timestamps
    recommended_at = Column(DateTime, default=datetime.utcnow, index=True)
    viewed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_recommendation_user_date", "user_id", "recommended_at"),
    )


class SimilarityMatrix(Base):
    """
    Pre-computed user-to-user similarity scores
    Updated periodically for efficient recommendations
    """
    __tablename__ = "similarity_matrix"

    id = Column(Integer, primary_key=True, index=True)
    user_id_1 = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_id_2 = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Similarity metrics
    overall_similarity = Column(Float, default=0.0)  # 0-1 score
    skill_similarity = Column(Float, default=0.0)  # Based on solved challenges
    language_similarity = Column(Float, default=0.0)  # Language preferences match
    difficulty_similarity = Column(Float, default=0.0)  # Preferred difficulty match
    learning_speed_similarity = Column(Float, default=0.0)  # Challenge completion rate

    # Metadata
    common_challenges = Column(Integer, default=0)  # Challenges both users solved
    last_updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user1 = relationship("User", foreign_keys=[user_id_1])
    user2 = relationship("User", foreign_keys=[user_id_2])

    __table_args__ = (
        Index("ix_similarity_users", "user_id_1", "user_id_2", unique=True),
    )


class RecommendationFeedback(Base):
    """
    Tracks user feedback on recommendations
    Used to improve algorithm accuracy
    """
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Feedback type
    feedback_type = Column(String(30), nullable=False)  # "too_easy", "too_hard", "not_relevant", "good_recommendation"
    rating = Column(Integer, nullable=True)  # 1-5 stars
    comments = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recommendation = relationship("Recommendation", foreign_keys=[recommendation_id])
    user = relationship("User", foreign_keys=[user_id])


class RecommendationQueue(Base):
    """
    Personalized challenge queue for each user
    Updated periodically as user progresses
    """
    __tablename__ = "recommendation_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Queue items (stored as JSON for flexibility)
    queue = Column(JSON, default=[])  # [{"challenge_id": 1, "score": 0.95, "reason": "..."}]
    current_index = Column(Integer, default=0)  # Current position in queue

    # Queue metadata
    total_items = Column(Integer, default=0)
    completed_from_queue = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)  # Completed / recommended ratio

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
