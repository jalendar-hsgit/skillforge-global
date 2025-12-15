"""
Solution Sharing Models
Community solutions, code reviews, and voting
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base


class ChallengeSolution(Base):
    """
    User-submitted solutions to challenges
    Can be shared with community for voting and discussion
    """
    __tablename__ = "challenge_solutions"
    
    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Solution details
    code = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    explanation = Column(Text)  # Optional explanation of approach
    
    # Stats
    execution_time_ms = Column(Integer)  # How fast it runs
    memory_used_mb = Column(Float)  # Memory usage
    test_cases_passed = Column(Integer, default=0)
    score = Column(Float, default=0)  # Score out of 100
    
    # Community features
    is_public = Column(Boolean, default=False)  # Share with community
    helpful_votes = Column(Integer, default=0)  # Upvotes
    unhelpful_votes = Column(Integer, default=0)  # Downvotes
    view_count = Column(Integer, default=0)  # How many viewed
    
    # Metadata
    complexity_explanation = Column(String)  # E.g., "O(n log n) time, O(1) space"
    approach_tags = Column(JSON)  # ["two-pointer", "sorting", "dynamic-programming"]
    difficulty_for_user = Column(String)  # "easy", "medium", "hard" - how hard was it for this user
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    challenge = relationship("CodingChallenge")
    user = relationship("User", backref="challenge_solutions")
    votes = relationship("SolutionVote", back_populates="solution", cascade="all, delete-orphan")


class SolutionVote(Base):
    """
    Community votes on shared solutions
    """
    __tablename__ = "solution_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    solution_id = Column(Integer, ForeignKey("challenge_solutions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    vote_type = Column(String, nullable=False)  # "helpful" or "unhelpful"
    voted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    solution = relationship("ChallengeSolution", back_populates="votes")
    user = relationship("User", backref="solution_votes")
    
    # Unique constraint - user can only vote once per solution
    __table_args__ = (UniqueConstraint('solution_id', 'user_id', name='solution_user_vote_unique'),)


class SolutionComment(Base):
    """
    Comments/discussion on solutions
    """
    __tablename__ = "solution_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    solution_id = Column(Integer, ForeignKey("challenge_solutions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    comment = Column(Text, nullable=False)
    helpful_votes = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    solution = relationship("ChallengeSolution", backref="comments")
    user = relationship("User", backref="solution_comments")


class SolutionBookmark(Base):
    """
    Users can bookmark useful solutions for later reference
    """
    __tablename__ = "solution_bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    solution_id = Column(Integer, ForeignKey("challenge_solutions.id"), nullable=False)
    
    bookmarked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="bookmarked_solutions")
    solution = relationship("ChallengeSolution", backref="bookmarks")
    
    # Unique constraint - user can only bookmark each solution once
    __table_args__ = (UniqueConstraint('user_id', 'solution_id', name='user_solution_bookmark_unique'),)
