"""
Premium Tiers subscription system models.
- SubscriptionTier: Definition of subscription tiers (Free, Pro, Premium, Elite)
- FeatureBenefit: Features included in each tier
- UserSubscription: User's active subscription
- SubscriptionHistory: Historical record of user subscriptions
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.db import Base


class TierType(str, Enum):
    """Subscription tier types"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ELITE = "elite"


class BillingPeriod(str, Enum):
    """Billing period for subscriptions"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class SubscriptionTier(Base):
    """Definition of subscription tiers with pricing and features"""
    __tablename__ = "subscription_tiers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    tier_type = Column(SQLEnum(TierType), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Pricing
    monthly_price = Column(Float, default=0.0)  # USD
    yearly_price = Column(Float, default=0.0)   # USD
    lifetime_price = Column(Float, nullable=True)  # One-time payment
    
    # Limits and quotas
    max_coding_submissions_per_day = Column(Integer, default=10)
    max_code_snippets = Column(Integer, default=5)
    max_learning_paths = Column(Integer, default=3)
    max_ai_hints_per_day = Column(Integer, default=5)
    max_storage_gb = Column(Float, default=1.0)
    
    # Features
    has_advanced_analytics = Column(Boolean, default=False)
    has_ai_code_review = Column(Boolean, default=False)
    has_video_tutorials = Column(Boolean, default=False)
    has_mentorship = Column(Boolean, default=False)
    has_certification = Column(Boolean, default=False)
    has_early_access = Column(Boolean, default=False)
    has_priority_support = Column(Boolean, default=False)
    has_custom_learning_paths = Column(Boolean, default=False)
    
    # Display
    display_order = Column(Integer, default=0)
    color = Column(String(50), default="gray")  # For UI badges: "green", "blue", "purple", "gold"
    icon = Column(String(100), default="📦")
    is_popular = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="tier", cascade="all, delete-orphan")
    benefits = relationship("FeatureBenefit", back_populates="tier", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SubscriptionTier(id={self.id}, name={self.name}, tier={self.tier_type})>"


class FeatureBenefit(Base):
    """Feature benefits included in each tier"""
    __tablename__ = "feature_benefits"

    id = Column(Integer, primary_key=True)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    
    feature_name = Column(String(255), nullable=False)
    feature_description = Column(Text, nullable=True)
    icon = Column(String(100), default="✓")
    
    # Display order within tier
    order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tier = relationship("SubscriptionTier", back_populates="benefits")
    
    def __repr__(self):
        return f"<FeatureBenefit(tier_id={self.tier_id}, feature={self.feature_name})>"


class UserSubscription(Base):
    """User's active subscription"""
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    
    # Subscription details
    billing_period = Column(SQLEnum(BillingPeriod), default=BillingPeriod.MONTHLY)
    payment_status = Column(String(50), default="active")  # "active", "pending", "failed", "cancelled"
    
    # Dates
    started_at = Column(DateTime, default=datetime.utcnow)
    renewed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Stripe info
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Auto-renewal
    auto_renew = Column(Boolean, default=True)
    
    # Extra Data
    extra_data = Column(JSON, default={})  # Store extra data like promocode, discount, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="subscription")
    tier = relationship("SubscriptionTier", back_populates="subscriptions")
    
    def is_active(self):
        """Check if subscription is currently active"""
        if self.payment_status != "active":
            return False
        if self.cancelled_at:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def days_until_renewal(self):
        """Days until subscription renews"""
        if self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            return max(0, delta.days)
        return None
    
    def __repr__(self):
        return f"<UserSubscription(user_id={self.user_id}, tier={self.tier_id}, active={self.is_active()})>"


class SubscriptionHistory(Base):
    """Historical record of user subscription changes"""
    __tablename__ = "subscription_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    
    # Event
    event_type = Column(String(50), nullable=False)  # "upgraded", "downgraded", "renewed", "cancelled", "created"
    reason = Column(String(255), nullable=True)
    
    # Billing period and amount
    billing_period = Column(SQLEnum(BillingPeriod), nullable=True)
    amount_paid = Column(Float, nullable=True)
    
    # Dates
    occurred_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Payment method
    payment_method = Column(String(100), nullable=True)  # "stripe", "paypal", "manual", etc.
    transaction_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    tier = relationship("SubscriptionTier")
    
    def __repr__(self):
        return f"<SubscriptionHistory(user_id={self.user_id}, event={self.event_type}, date={self.occurred_at})>"


class PromoCode(Base):
    """Promotional codes for discounts"""
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Discount
    discount_type = Column(String(20), default="percentage")  # "percentage" or "fixed"
    discount_value = Column(Float, nullable=False)  # Percentage (0-100) or fixed amount
    
    # Limitations
    max_uses = Column(Integer, nullable=True)  # Unlimited if None
    current_uses = Column(Integer, default=0)
    applicable_tiers = Column(JSON, default=[])  # List of tier IDs, or empty for all
    
    # Dates
    starts_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """Check if promo code is valid"""
        if not self.is_active:
            return False
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def __repr__(self):
        return f"<PromoCode(code={self.code}, discount={self.discount_value}{self.discount_type})>"
