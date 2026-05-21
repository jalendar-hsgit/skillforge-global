"""
Interview Preparation Models
Supports mock interviews, question banks, interview scheduling, and performance tracking
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Float, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class InterviewType(str, Enum):
    """Types of interviews"""
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    DATA_STRUCTURES = "data_structures"
    CODING = "coding"
    MIXED = "mixed"


class InterviewDifficulty(str, Enum):
    """Interview difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuestionDifficulty(str, Enum):
    """Question difficulty"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionCategory(Base):
    """
    Categories for interview questions
    """
    __tablename__ = "question_categories"

    id = Column(Integer, primary_key=True, index=True)
    
    # Category metadata
    name = Column(String(100), nullable=False, unique=True, index=True)  # "Arrays", "Trees", "SQL", "System Design"
    description = Column(Text, nullable=True)
    icon_emoji = Column(String(10), nullable=True)
    
    # Category metrics
    question_count = Column(Integer, default=0)
    average_difficulty = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class InterviewQuestion(Base):
    """
    Question bank for interview preparation
    """
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("question_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Question content
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Question metadata
    difficulty = Column(SQLEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM)
    interview_type = Column(SQLEnum(InterviewType), default=InterviewType.TECHNICAL)
    tags = Column(JSON, default=[])  # "recursion", "dp", "binary search"
    company_tags = Column(JSON, default=[])  # "Google", "Amazon", "Facebook"
    
    # Expected solution
    expected_answer = Column(Text, nullable=True)
    solution_explanation = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=True)  # Example code
    solution_language = Column(String(30), default="python")
    
    # Resources and tips
    tips = Column(JSON, default=[])  # Common mistakes, hints
    resources = Column(JSON, default=[])  # Links to related articles
    time_limit_minutes = Column(Integer, default=30)
    
    # Statistics
    attempt_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("QuestionCategory", foreign_keys=[category_id])
    
    __table_args__ = (
        Index("ix_interview_question_difficulty", "difficulty"),
        Index("ix_interview_question_company", "company_tags"),
    )


class MockInterview(Base):
    """
    Mock interview sessions
    """
    __tablename__ = "mock_interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Interview configuration
    interview_type = Column(SQLEnum(InterviewType), nullable=False)
    difficulty = Column(SQLEnum(InterviewDifficulty), default=InterviewDifficulty.MEDIUM)
    duration_minutes = Column(Integer, default=60)
    
    # Target company/role
    target_company = Column(String(100), nullable=True)
    target_role = Column(String(100), nullable=True)
    target_level = Column(String(50), nullable=True)  # "junior", "mid", "senior"
    
    # Interview status
    status = Column(String(20), default="scheduled")  # "scheduled", "in_progress", "completed", "abandoned"
    
    # Interview timing
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Interview questions
    question_ids = Column(JSON, default=[])  # List of question IDs
    total_questions = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    
    # Performance tracking
    total_score = Column(Float, default=0.0)  # Overall score 0-100
    time_spent_minutes = Column(Integer, default=0)
    
    # Breakdown scores
    correctness_score = Column(Float, default=0.0)  # 0-100
    clarity_score = Column(Float, default=0.0)  # Communication clarity
    efficiency_score = Column(Float, default=0.0)  # Solution efficiency
    completion_percentage = Column(Float, default=0.0)  # % questions completed
    
    # Feedback
    feedback_text = Column(Text, nullable=True)
    extra_data = Column(JSON, default={})  # Additional metrics
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index("ix_mock_interview_user_date", "user_id", "created_at"),
        Index("ix_mock_interview_status", "status"),
    )


class InterviewAnswer(Base):
    """
    User's answer to interview question
    """
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    mock_interview_id = Column(Integer, ForeignKey("mock_interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    
    # Answer content
    user_answer = Column(Text, nullable=False)
    answer_language = Column(String(30), default="python")
    
    # Answer metadata
    is_correct = Column(Boolean, default=False)
    attempts = Column(Integer, default=1)
    skipped = Column(Boolean, default=False)
    
    # Scoring
    points_earned = Column(Float, default=0.0)
    max_points = Column(Float, default=100.0)
    accuracy_percentage = Column(Float, default=0.0)
    
    # Timing
    time_spent_seconds = Column(Integer, default=0)
    time_limit_exceeded = Column(Boolean, default=False)
    
    # Feedback
    feedback = Column(Text, nullable=True)
    
    # Timestamps
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mock_interview = relationship("MockInterview", foreign_keys=[mock_interview_id])
    question = relationship("InterviewQuestion", foreign_keys=[question_id])


class InterviewSchedule(Base):
    """
    User's interview schedule and calendar
    """
    __tablename__ = "interview_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Schedule details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Interview details
    interview_type = Column(SQLEnum(InterviewType), default=InterviewType.MIXED)
    difficulty = Column(SQLEnum(InterviewDifficulty), default=InterviewDifficulty.MEDIUM)
    
    # Company and role
    company_name = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)
    
    # Timing
    scheduled_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default="UTC")
    
    # Status
    status = Column(String(20), default="scheduled")  # "scheduled", "completed", "cancelled", "rescheduled"
    
    # Preparation
    preparation_status = Column(String(20), default="not_started")  # "not_started", "in_progress", "ready"
    preparation_percentage = Column(Float, default=0.0)
    
    # Linked interview
    mock_interview_id = Column(Integer, ForeignKey("mock_interviews.id", ondelete="SET NULL"), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    reminders = Column(JSON, default=[])  # Reminder times before interview
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    mock_interview = relationship("MockInterview", foreign_keys=[mock_interview_id])


class InterviewPerformance(Base):
    """
    Aggregated interview performance metrics for tracking improvement
    """
    __tablename__ = "interview_performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Overall statistics
    total_interviews = Column(Integer, default=0)
    completed_interviews = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    
    # Score breakdown
    average_correctness = Column(Float, default=0.0)
    average_clarity = Column(Float, default=0.0)
    average_efficiency = Column(Float, default=0.0)
    
    # By interview type
    by_type_stats = Column(JSON, default={})  # {type: {avg_score, count, success_rate}}
    
    # By difficulty
    by_difficulty_stats = Column(JSON, default={})  # {difficulty: {avg_score, count}}
    
    # Improvement tracking
    score_trend = Column(JSON, default=[])  # Last 10 interview scores
    best_score = Column(Float, default=0.0)
    worst_score = Column(Float, default=0.0)
    
    # Time analysis
    average_time_per_question = Column(Float, default=0.0)
    time_management_score = Column(Float, default=0.0)
    
    # Weak areas
    weak_categories = Column(JSON, default=[])  # Categories needing improvement
    strong_categories = Column(JSON, default=[])
    
    # Last updated
    last_interview_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class InterviewFeedback(Base):
    """
    Detailed feedback from mock interviews
    """
    __tablename__ = "interview_feedback"

    id = Column(Integer, primary_key=True, index=True)
    mock_interview_id = Column(Integer, ForeignKey("mock_interviews.id", ondelete="CASCADE"), nullable=False)
    
    # Overall feedback
    overall_feedback = Column(Text, nullable=True)
    
    # Feedback categories
    technical_feedback = Column(Text, nullable=True)
    communication_feedback = Column(Text, nullable=True)
    problem_solving_feedback = Column(Text, nullable=True)
    
    # Strengths and weaknesses
    strengths = Column(JSON, default=[])
    weaknesses = Column(JSON, default=[])
    improvement_suggestions = Column(JSON, default=[])
    
    # Resources for improvement
    recommended_resources = Column(JSON, default=[])  # Links to articles, courses
    next_practice_areas = Column(JSON, default=[])  # Categories to focus on
    
    # Score details
    score_breakdown = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mock_interview = relationship("MockInterview", foreign_keys=[mock_interview_id])
