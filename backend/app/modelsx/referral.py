from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from app.core.db import Base

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True, index=True)
    referrer_user_id = Column(Integer, nullable=False)
    referred_user_id = Column(Integer, nullable=False)
    bonus_credits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
