from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.db import Base

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    youtube_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    duration = Column(String)
    level = Column(String)
    sort_order = Column(Integer, default=0)

    course = relationship("Course", back_populates="videos")
    progress_items = relationship("Progress", back_populates="video")

Video.progress_items = relationship('Progress', back_populates='video', cascade='all, delete-orphan')
