from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from app.core.db import Base

class Subscriber(Base):
    __tablename__ = "subscriber"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("email", name="uq_subscriber_email"),)
