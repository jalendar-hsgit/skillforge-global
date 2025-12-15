"""
AI Hints system models for intelligent code assistance.
- AIHint: Generated hints for coding challenges
- AIHintUsage: Track hint usage and effectiveness
- HintFeedback: User feedback on hints
- AIHintTemplate: Templates for hint generation
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.db import Base


class HintType(str, Enum):
    """Types of AI hints"""
    CONCEPT_EXPLANATION = "concept_explanation"
    APPROACH_SUGGESTION = "approach_suggestion"
    STEP_BY_STEP = "step_by_step"
    COMMON_MISTAKES = "common_mistakes"
    EDGE_CASES = "edge_cases"
    CODE_PATTERN = "code_pattern"
    DEBUGGING_HINT = "debugging_hint"
    OPTIMIZATION_HINT = "optimization_hint"


class HintDifficulty(str, Enum):
    """Difficulty level of hints"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"


class HintQuality(str, Enum):
    """Quality rating of hints"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class AIHint(Base):
    """AI-generated hint for a coding challenge"""
    __tablename__ = "ai_hints"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False, index=True)
    
    # Hint content
    hint_type = Column(SQLEnum(HintType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)  # Why this hint helps
    
    # Difficulty
    target_difficulty = Column(SQLEnum(HintDifficulty), default=HintDifficulty.MODERATE)
    
    # Code examples (optional)
    code_example = Column(Text, nullable=True)
    code_language = Column(String(50), default="python")
    
    # Related resources
    resource_links = Column(JSON, default=[])  # [{"title": "...", "url": "..."}, ...]
    
    # AI metadata
    model_used = Column(String(100), nullable=True)  # "gpt-4", "claude-3", etc.
    generation_prompt = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    
    # Quality
    quality_rating = Column(SQLEnum(HintQuality), default=HintQuality.GOOD)
    is_manually_reviewed = Column(Boolean, default=False)
    
    # Stats
    times_shown = Column(Integer, default=0)
    times_helpful = Column(Integer, default=0)
    times_unhelpful = Column(Integer, default=0)
    helpful_score = Column(Float, default=0.5)  # 0-1
    
    # Status
    is_active = Column(Boolean, default=True)
    is_premium_only = Column(Boolean, default=False)
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    challenge = relationship("CodingChallenge")
    usages = relationship("AIHintUsage", back_populates="hint", cascade="all, delete-orphan")
    feedback = relationship("HintFeedback", back_populates="hint", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AIHint(id={self.id}, challenge_id={self.challenge_id}, type={self.hint_type})>"


class AIHintUsage(Base):
    """Track when users view hints"""
    __tablename__ = "ai_hint_usage"

    id = Column(Integer, primary_key=True)
    hint_id = Column(Integer, ForeignKey("ai_hints.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False)
    
    # Usage context
    viewed_at = Column(DateTime, default=datetime.utcnow)
    time_on_hint_seconds = Column(Integer, default=0)
    
    # Did they solve the challenge after viewing?
    challenge_solved_after = Column(Boolean, nullable=True)
    time_to_solve_minutes = Column(Integer, nullable=True)
    
    # Subscription tier when hint was used
    user_tier_at_time = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hint = relationship("AIHint", back_populates="usages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<AIHintUsage(hint_id={self.hint_id}, user_id={self.user_id})>"


class HintFeedback(Base):
    """User feedback on hint quality"""
    __tablename__ = "hint_feedback"

    id = Column(Integer, primary_key=True)
    hint_id = Column(Integer, ForeignKey("ai_hints.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Feedback
    is_helpful = Column(Boolean, nullable=False)
    rating = Column(Integer, default=3)  # 1-5 stars
    comment = Column(Text, nullable=True)
    
    # Feedback categories
    was_clear = Column(Boolean, nullable=True)
    was_actionable = Column(Boolean, nullable=True)
    was_complete = Column(Boolean, nullable=True)
    
    # Issues
    has_errors = Column(Boolean, default=False)
    error_description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hint = relationship("AIHint", back_populates="feedback")
    user = relationship("User")
    
    def __repr__(self):
        return f"<HintFeedback(hint_id={self.hint_id}, user_id={self.user_id}, helpful={self.is_helpful})>"


class HintTemplate(Base):
    """Template for generating hints via AI"""
    __tablename__ = "hint_templates"

    id = Column(Integer, primary_key=True)
    
    # Template info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    hint_type = Column(SQLEnum(HintType), nullable=False)
    
    # Template structure
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)
    
    # Configuration
    temperature = Column(Float, default=0.7)  # For LLM
    max_tokens = Column(Integer, default=500)
    model_preference = Column(String(100), default="gpt-4")
    
    # Activation
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher = used first
    
    # Stats
    total_generated = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<HintTemplate(id={self.id}, name={self.name}, type={self.hint_type})>"


class UserHintQuota(Base):
    """Track hint usage quotas for users"""
    __tablename__ = "user_hint_quotas"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Daily quota
    hints_requested_today = Column(Integer, default=0)
    hints_quota_per_day = Column(Integer, default=5)  # Free tier
    
    # Monthly quota
    hints_requested_this_month = Column(Integer, default=0)
    hints_quota_per_month = Column(Integer, default=50)
    
    # Reset dates
    daily_reset_at = Column(DateTime, default=datetime.utcnow)
    monthly_reset_at = Column(DateTime, default=datetime.utcnow)
    
    # Premium override
    is_unlimited = Column(Boolean, default=False)  # For premium users
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="hint_quota")
    
    def can_request_hint(self):
        """Check if user can request a hint"""
        if self.is_unlimited:
            return True
        return self.hints_requested_today < self.hints_quota_per_day
    
    def __repr__(self):
        return f"<UserHintQuota(user_id={self.user_id}, remaining={self.hints_quota_per_day - self.hints_requested_today})>"
