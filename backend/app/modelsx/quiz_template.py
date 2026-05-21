"""
Persistent AI quiz templates - stores generated quizzes for review and retakes.
"""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.db import Base


class GeneratedQuiz(Base):
    """Stores AI-generated quizzes for user review and retakes."""
    __tablename__ = "generated_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Quiz metadata
    topic = Column(String(255), nullable=False, index=True)
    difficulty = Column(String(50), nullable=False)  # easy, medium, hard
    title = Column(String(500), nullable=False)
    
    # Generated content (full quiz JSON)
    questions = Column(JSON, nullable=False)  # Array of question objects
    
    # Generation context
    provider = Column(String(50), nullable=True)  # openai, anthropic, ollama
    model = Column(String(100), nullable=True)  # gpt-4, claude-3, etc.
    adaptive_context = Column(JSON, nullable=True)  # User performance context used
    
    # Usage tracking
    times_taken = Column(Integer, default=0)
    best_score = Column(Integer, nullable=True)
    best_score_total = Column(Integer, nullable=True)
    last_taken_at = Column(DateTime(timezone=True), nullable=True)
    
    # Flags
    is_favorite = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("app.models.user.User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<GeneratedQuiz(id={self.id}, topic='{self.topic}', user_id={self.user_id})>"


class QuizSession(Base):
    """Tracks individual quiz-taking sessions for analytics and adaptive learning."""
    __tablename__ = "quiz_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quiz_id = Column(Integer, ForeignKey("generated_quizzes.id"), nullable=True, index=True)
    quiz_path = Column(String(255), nullable=True, index=True)  # For static quizzes
    
    # Session data
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Performance
    score = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False, default=False)
    
    # Per-question analytics
    answers = Column(JSON, nullable=True)  # [{question_id, user_answer, correct, time_ms}]
    
    # Adaptive metrics
    difficulty_progression = Column(JSON, nullable=True)  # Track difficulty adjustments
    avg_response_time_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("app.models.user.User", foreign_keys=[user_id])
    generated_quiz = relationship("GeneratedQuiz", foreign_keys=[quiz_id])
    
    def __repr__(self):
        return f"<QuizSession(id={self.id}, score={self.score}/{self.total_questions}, user_id={self.user_id})>"
