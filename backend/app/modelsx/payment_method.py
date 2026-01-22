"""
Payment Method model for mentors to store bank account information
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.core.db import Base


class PaymentMethodStatus(str, enum.Enum):
    """Status of payment method verification"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    INACTIVE = "INACTIVE"


class PaymentMethodType(str, enum.Enum):
    """Type of payment method"""
    BANK_ACCOUNT = "BANK_ACCOUNT"
    PAYPAL = "PAYPAL"
    STRIPE = "STRIPE"


class PaymentMethod(Base):
    """
    Stores mentor bank account information for payouts
    Sensitive fields (account_number, routing_number) are encrypted
    """
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic info
    payment_type = Column(SQLEnum(PaymentMethodType), default=PaymentMethodType.BANK_ACCOUNT)
    account_holder_name = Column(String(255), nullable=False)
    bank_name = Column(String(255), nullable=False)
    
    # Encrypted fields (stored as encrypted strings)
    # Use cryptography.fernet to encrypt/decrypt
    account_number_encrypted = Column(Text, nullable=True)  # Encrypted account number
    routing_number_encrypted = Column(Text, nullable=True)  # Encrypted routing number
    
    # Status and verification
    status = Column(
        SQLEnum(PaymentMethodStatus),
        default=PaymentMethodStatus.PENDING,
        index=True
    )
    is_default = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # mentor relationship is defined in Mentor model with back_populates to avoid circular imports
    # mentor = relationship("Mentor", back_populates="payment_methods", foreign_keys=[mentor_id])
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, mentor_id={self.mentor_id}, bank={self.bank_name}, status={self.status})>"


class PayoutRequest(Base):
    """
    Tracks payout requests from mentors
    """
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)
    
    # Amount and status
    amount = Column(Integer, nullable=False)  # Amount in cents
    status = Column(
        String(50),
        default="PENDING",
        index=True
    )  # PENDING, APPROVED, REJECTED, PROCESSING, COMPLETED
    
    # Reason for rejection
    rejection_reason = Column(Text, nullable=True)
    
    # Processing info
    stripe_payout_id = Column(String(255), nullable=True, unique=True)
    
    # Timeline
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Admin notes
    admin_notes = Column(Text, nullable=True)
    
    # Relationships
    # mentor relationship is defined in Mentor model with back_populates
    # mentor = relationship("Mentor", back_populates="payout_requests", foreign_keys=[mentor_id])
    payment_method = relationship("PaymentMethod")
    
    def __repr__(self):
        return f"<PayoutRequest(id={self.id}, mentor_id={self.mentor_id}, amount={self.amount}, status={self.status})>"
