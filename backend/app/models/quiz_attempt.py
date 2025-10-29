from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from app.core.db import Base

class QuizAttempt(Base):
    __tablename__ = "quiz_attempt"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    path = Column(String, nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
