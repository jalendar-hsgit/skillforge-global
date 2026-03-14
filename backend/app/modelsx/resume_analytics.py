from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from app.core.db import Base
from datetime import datetime

class ResumeAnalytics(Base):
    __tablename__ = "resume_analytics"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    template_id = Column(String, nullable=True)
    ats_scores = Column(JSON, default=list)  # [{"score": 85, "date": "2025-11-02"}]
    last_viewed = Column(DateTime, nullable=True)
    last_downloaded = Column(DateTime, nullable=True)
    last_shared = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
