from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True, nullable=False)  # slug
    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    is_paid = Column(Boolean, default=False)
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

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
