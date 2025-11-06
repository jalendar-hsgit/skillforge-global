from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.db import Base

class CoinLedger(Base):
    __tablename__ = "coin_ledger"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    delta = Column(Integer, nullable=False)  # positive = earn, negative = spend
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional backref to user if your User model defines relationship("CoinLedger", ...)
    # user = relationship("User", back_populates="coin_ledger")
