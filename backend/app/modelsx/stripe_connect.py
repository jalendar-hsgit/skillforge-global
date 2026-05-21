from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base

class MentorStripeAccount(Base):
    __tablename__ = "mentor_stripe_accounts"
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    account_id = Column(String, nullable=True, index=True)  # Stripe Connect Account ID (acct_...)
    onboarding_complete = Column(Boolean, default=False)
    payouts_enabled = Column(Boolean, default=False)
    details_submitted = Column(Boolean, default=False)
    requirements_due = Column(String, nullable=True)  # CSV of outstanding requirements

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    mentor = relationship("Mentor")

    __table_args__ = (
        UniqueConstraint('mentor_id', name='uq_mentor_stripe_account_mentor'),
    )
