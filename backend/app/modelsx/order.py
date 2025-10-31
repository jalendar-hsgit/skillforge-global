from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from datetime import datetime
from app.core.db import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    amount = Column(Numeric(10,2), nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String, default="pending")  # pending, paid, refunded
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course")
