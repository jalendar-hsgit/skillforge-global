from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base

class VideoProgress(Base):
    __tablename__ = "video_progress"

    id = Column(Integer, primary_key=True, index=True)
    # Match your legacy table name (use "user.id" not "users.id")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)

    progress_percent = Column(Integer, nullable=False, default=0)
    last_position_sec = Column(Integer, nullable=True)
    note = Column(String, nullable=True)

    video = relationship("Video", back_populates="progress_items")

    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uq_user_video"),
    )
