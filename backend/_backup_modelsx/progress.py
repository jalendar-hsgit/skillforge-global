from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class VideoProgress(Base):
    __tablename__ = "video_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False, index=True)
    progress_percent = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    video = relationship("Video", back_populates="progress_items")
