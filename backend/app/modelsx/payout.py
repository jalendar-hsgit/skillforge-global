from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime
import enum


class PayoutStatus(str, enum.Enum):
    """Payout request status"""
    PENDING = "pending"  # Awaiting processing
    PROCESSING = "processing"  # Being processed
    COMPLETED = "completed"  # Paid out
    FAILED = "failed"  # Failed to process
    CANCELLED = "cancelled"  # Cancelled by admin


class PayoutMethod(str, enum.Enum):
    """Payout method"""
    STRIPE = "stripe"  # Stripe Connect
    BANK_TRANSFER = "bank_transfer"  # Direct bank transfer
    PAYPAL = "paypal"  # PayPal


class MentorPayout(Base):
    """
    Payout requests from mentors for their earnings.
    """
    __tablename__ = "mentor_payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Amount
    amount = Column(Float, nullable=False)  # Amount requested in USD
    platform_fee = Column(Float, default=0.0)  # Platform commission (e.g., 20%)
    net_amount = Column(Float, nullable=False)  # Amount mentor receives
    
    # Payment Details
    method = Column(Enum(PayoutMethod), default=PayoutMethod.STRIPE, nullable=False)
    status = Column(Enum(PayoutStatus), default=PayoutStatus.PENDING, nullable=False, index=True)
    
    # External References
    stripe_transfer_id = Column(String, nullable=True)  # Stripe transfer ID if using Stripe
    paypal_transaction_id = Column(String, nullable=True)  # PayPal transaction ID
    
    # Banking (for bank transfer)
    bank_account_last4 = Column(String, nullable=True)  # Last 4 digits of account
    
    # Notes
    notes = Column(Text, nullable=True)  # Admin notes
    failure_reason = Column(Text, nullable=True)  # Reason if failed
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    mentor = relationship("Mentor", backref="payouts")
    
    def __repr__(self):
        return f"<MentorPayout(id={self.id}, mentor_id={self.mentor_id}, amount={self.amount}, status={self.status})>"


class MentorEarning(Base):
    """
    Individual earnings records from completed sessions.
    Links sessions to payouts for tracking.
    """
    __tablename__ = "mentor_earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("mentor_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Amounts
    gross_amount = Column(Float, nullable=False)  # Total session price
    platform_fee = Column(Float, default=0.0)  # Platform commission
    net_amount = Column(Float, nullable=False)  # Mentor's earnings
    
    # Payout Tracking
    payout_id = Column(Integer, ForeignKey("mentor_payouts.id", ondelete="SET NULL"), nullable=True, index=True)
    is_paid_out = Column(Boolean, default=False)  # Has been included in a payout
    
    # Timestamps
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    paid_out_at = Column(DateTime, nullable=True)
    
    # Relationships
    mentor = relationship("Mentor", backref="earnings")
    session = relationship("MentorSession", backref="earning")
    payout = relationship("MentorPayout", backref="earnings")
    
    def __repr__(self):
        return f"<MentorEarning(id={self.id}, mentor_id={self.mentor_id}, net_amount={self.net_amount})>"
