from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from app.core.db import Base

class CreditLedger(Base):
    __tablename__ = "credit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
