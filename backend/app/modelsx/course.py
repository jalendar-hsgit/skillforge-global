from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True, nullable=False)  # slug
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    is_paid = Column(Boolean, default=False)
    price = Column(Numeric(10, 2))
    
    # Premium/Tier system
    tier = Column(String, default="free")  # free, premium, enterprise
    is_premium = Column(Boolean, default=False)
    
    # Course metadata
    instructor = Column(String)
    difficulty = Column(String, default="beginner")  # beginner, intermediate, advanced
    duration_hours = Column(Float)
    rating = Column(Float, default=0.0)
    enrollment_count = Column(Integer, default=0)
    
    # YouTube integration
    youtube_playlist_id = Column(String)  # For syncing entire playlists
    last_synced_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    videos = relationship(
        "Video",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    quizzes = relationship(
        "Quiz",
        back_populates="course",
        cascade="all, delete-orphan",
    )
