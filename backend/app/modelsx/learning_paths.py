"""
Learning Paths models for structured course progression.
- LearningPath: Definition of a learning path
- PathChallenge: Challenges within a path
- UserPathProgress: User progress tracking
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.db import Base


class PathStatus(str, Enum):
    """Status of a learning path"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PathDifficulty(str, Enum):
    """Difficulty level of a path"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ChallengeStatus(str, Enum):
    """Status of a challenge in a path"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    COMPLETED = "completed"


class LearningPath(Base):
    """A structured learning path with multiple challenges"""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)  # URL or emoji
    
    # Path structure
    difficulty = Column(SQLEnum(PathDifficulty), default=PathDifficulty.BEGINNER)
    estimated_hours = Column(Integer, nullable=True)  # Estimated completion time
    status = Column(SQLEnum(PathStatus), default=PathStatus.DRAFT)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_featured = Column(Boolean, default=False)
    order = Column(Integer, default=0)  # For sorting paths
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    challenges = relationship("PathChallenge", back_populates="path", cascade="all, delete-orphan")
    user_progress = relationship("UserPathProgress", back_populates="path", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningPath(id={self.id}, title={self.title}, difficulty={self.difficulty})>"


class PathChallenge(Base):
    """Individual challenges that make up a learning path"""
    __tablename__ = "path_challenges"

    id = Column(Integer, primary_key=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False)
    
    # Challenge sequence
    order = Column(Integer, nullable=False)  # Position in the path
    
    # Prerequisites
    required_previous_completion = Column(Boolean, default=False)  # Must complete previous challenge first
    min_score_for_unlock = Column(Float, nullable=True)  # If None, just needs completion
    
    # Metadata
    points_value = Column(Integer, default=0)
    estimated_minutes = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    path = relationship("LearningPath", back_populates="challenges")
    challenge = relationship("CodingChallenge")
    
    def __repr__(self):
        return f"<PathChallenge(id={self.id}, path_id={self.path_id}, order={self.order})>"


class UserPathProgress(Base):
    """User's progress through a learning path"""
    __tablename__ = "user_path_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    
    # Progress tracking
    total_challenges = Column(Integer, nullable=False)  # Denormalized for performance
    completed_challenges = Column(Integer, default=0)
    current_challenge_id = Column(Integer, ForeignKey("path_challenges.id"), nullable=True)
    
    # Stats
    total_points_earned = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    
    # Status
    is_started = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    path = relationship("LearningPath", back_populates="user_progress")
    user = relationship("User")
    
    def calculate_completion_percentage(self):
        """Calculate and update completion percentage"""
        if self.total_challenges > 0:
            self.completion_percentage = (self.completed_challenges / self.total_challenges) * 100
        return self.completion_percentage
    
    def __repr__(self):
        return f"<UserPathProgress(user_id={self.user_id}, path_id={self.path_id}, completed={self.completed_challenges}/{self.total_challenges})>"

# ==================== CERTIFICATE MODELS ====================

class CertificateStatus(str, Enum):
    """Certificate statuses"""
    EARNED = "earned"
    REVOKED = "revoked"
    EXPIRED = "expired"


class Certificate(Base):
    """Certificates earned by completing learning paths"""
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False, index=True)
    
    # Certificate info
    certificate_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), default="SkillForge", nullable=False)
    description = Column(Text, nullable=True)
    
    # Validation
    status = Column(SQLEnum(CertificateStatus), default=CertificateStatus.EARNED)
    verification_code = Column(String(100), unique=True, nullable=True)
    
    # Dates
    earned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Files
    certificate_url = Column(String(500), nullable=True)  # URL to PDF/image
    badge_url = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)
    path = relationship("LearningPath", foreign_keys=[path_id], viewonly=True)
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, certificate_number={self.certificate_number})>"


class SkillValidation(Base):
    """Skill validations and endorsements"""
    __tablename__ = "skill_validations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False, index=True)
    
    # Validation info
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Mentor/admin who validated
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=True)  # Path that led to skill
    
    # Proficiency
    proficiency_level = Column(String(50), default="intermediate")  # beginner, intermediate, advanced, expert
    confidence_score = Column(Float, default=0.0)  # 0-100
    
    # Status
    is_active = Column(Boolean, default=True)
    validation_method = Column(String(100))  # path_completion, assessment, mentor_review, etc.
    
    # Timestamps
    validated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)
    validator = relationship("User", foreign_keys=[validated_by], viewonly=True)
    path = relationship("LearningPath", foreign_keys=[path_id], viewonly=True)
    
    def __repr__(self):
        return f"<SkillValidation(user_id={self.user_id}, skill={self.skill_name}, level={self.proficiency_level})>"


# ==================== RECOMMENDATION MODELS ====================

class PathRecommendation(Base):
    """Learning path recommendations for users"""
    __tablename__ = "path_recommendations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False, index=True)
    
    # Recommendation info
    reason = Column(String(255), nullable=False)  # "Based on your interests", "Popular path", etc.
    recommendation_score = Column(Float, default=0.0)  # 0-100, higher = better match
    
    # Algorithm/source
    algorithm = Column(String(100), default="collaborative")  # collaborative, content, hybrid, etc.
    
    # Status
    is_dismissed = Column(Boolean, default=False)
    dismissed_at = Column(DateTime, nullable=True)
    is_started = Column(Boolean, default=False)
    started_at = Column(DateTime, nullable=True)
    
    # Timestamps
    recommended_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)
    path = relationship("LearningPath", foreign_keys=[path_id], viewonly=True)
    
    def __repr__(self):
        return f"<PathRecommendation(user_id={self.user_id}, path_id={self.path_id}, score={self.recommendation_score})>"