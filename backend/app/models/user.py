from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.db import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    mentor_profile = relationship("Mentor", back_populates="user", uselist=False)
    sent_mentor_messages = relationship("MentorMessage", foreign_keys="MentorMessage.sender_id", back_populates="sender")
