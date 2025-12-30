"""
Referral Program Models
Multi-tier referral system with rewards, tracking, and campaign management
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Float, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class ReferralStatus(str, Enum):
    """Status of a referral"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REWARDED = "rewarded"
    EXPIRED = "expired"
    REJECTED = "rejected"


class RewardType(str, Enum):
    """Type of reward"""
    COINS = "coins"
    CREDITS = "credits"
    DISCOUNT = "discount"
    PREMIUM_ACCESS = "premium_access"


class ReferralCode(Base):
    """
    Personal referral codes for users
    """
    __tablename__ = "referral_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Code details
    code = Column(String(20), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    
    # Statistics
    used_count = Column(Integer, default=0)
    successful_referrals = Column(Integer, default=0)
    
    # Settings
    custom_url = Column(String(500), nullable=True)  # utm_source parameter
    bonus_per_referral = Column(Integer, default=100)  # coins/credits
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index("ix_referral_code_code", "code"),
    )


class Referral(Base):
    """
    Individual referral tracking
    """
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey("referral_codes.id", ondelete="SET NULL"), nullable=True)
    referrer_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    referred_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Status and validation
    status = Column(SQLEnum(ReferralStatus), default=ReferralStatus.PENDING)
    
    # Verification
    email_confirmed = Column(Boolean, default=False)
    first_purchase_completed = Column(Boolean, default=False)
    
    # Rewards
    bonus_amount = Column(Integer, default=0)  # coins/credits
    bonus_type = Column(SQLEnum(RewardType), default=RewardType.COINS)
    reward_claimed_at = Column(DateTime, nullable=True)
    
    # Tracking
    referred_email = Column(String(100), nullable=True)
    referral_source = Column(String(100), nullable=True)  # "email", "link", "social"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    confirmed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # 30 days from creation
    
    # Relationships
    code = relationship("ReferralCode", foreign_keys=[code_id])
    referrer = relationship("User", foreign_keys=[referrer_user_id])
    referred = relationship("User", foreign_keys=[referred_user_id])
    
    __table_args__ = (
        Index("ix_referral_referrer", "referrer_user_id", "status"),
        Index("ix_referral_referred", "referred_user_id"),
    )


class ReferralReward(Base):
    """
    Reward ledger for referrals (tracks bonus calculations)
    """
    __tablename__ = "referral_rewards"

    id = Column(Integer, primary_key=True, index=True)
    referral_id = Column(Integer, ForeignKey("referrals.id", ondelete="CASCADE"), nullable=False)
    referrer_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    referred_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Reward details
    reward_type = Column(SQLEnum(RewardType), nullable=False)
    amount = Column(Integer, nullable=False)  # coins/credits amount
    
    # Tier bonus (increased for more referrals)
    tier_level = Column(Integer, default=1)  # 1 = first 5 referrals, 2 = 6-20, 3 = 20+
    tier_multiplier = Column(Float, default=1.0)  # 1.0, 1.5, 2.0
    base_amount = Column(Integer, nullable=False)
    bonus_amount = Column(Integer, default=0)  # tier_bonus
    
    # Status
    is_claimed = Column(Boolean, default=False)
    claimed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    referral = relationship("Referral", foreign_keys=[referral_id])
    referrer = relationship("User", foreign_keys=[referrer_user_id])
    referred = relationship("User", foreign_keys=[referred_user_id])
    
    __table_args__ = (
        Index("ix_referral_reward_referrer", "referrer_user_id", "is_claimed"),
    )


class ReferralCampaign(Base):
    """
    Marketing campaigns with special referral terms
    """
    __tablename__ = "referral_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(100), nullable=False, unique=True)
    
    # Campaign terms
    reward_amount = Column(Integer, nullable=False)  # coins/credits
    reward_type = Column(SQLEnum(RewardType), default=RewardType.COINS)
    referrer_bonus = Column(Integer, default=100)
    referred_bonus = Column(Integer, default=50)  # Bonus for new user
    
    # Campaign details
    is_active = Column(Boolean, default=True)
    max_referrals = Column(Integer, nullable=True)  # Unlimited if null
    current_referral_count = Column(Integer, default=0)
    
    # Validity period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Marketing
    banner_url = Column(String(500), nullable=True)
    terms = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReferralStatistics(Base):
    """
    Aggregated referral statistics per user
    """
    __tablename__ = "referral_statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Counts
    total_referrals = Column(Integer, default=0)
    confirmed_referrals = Column(Integer, default=0)
    pending_referrals = Column(Integer, default=0)
    
    # Rewards
    total_rewards_earned = Column(Integer, default=0)
    total_rewards_claimed = Column(Integer, default=0)
    pending_rewards = Column(Integer, default=0)
    
    # Breakdown by reward type
    rewards_by_type = Column(JSON, default={})  # {"coins": 500, "credits": 100}
    
    # Performance
    conversion_rate = Column(Float, default=0.0)  # confirmed / total
    average_time_to_confirm = Column(Integer, default=0)  # hours
    
    # Top tier
    referrer_tier = Column(String(20), default="bronze")  # "bronze", "silver", "gold", "platinum"
    tier_multiplier = Column(Float, default=1.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index("ix_referral_stats_user", "user_id"),
    )
