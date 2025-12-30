"""
User Follow System Models
Social connections and relationship tracking
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

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
