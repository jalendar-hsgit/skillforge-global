from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime
import enum


class SubscriptionPlan(str, enum.Enum):
    """Subscription plan tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    UNPAID = "unpaid"


class Subscription(Base):
    """
    User subscription plans for accessing premium features.
    """
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Plan Details
    plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False, index=True)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False, index=True)
    
    # Stripe References
    stripe_subscription_id = Column(String, unique=True, nullable=True, index=True)
    stripe_customer_id = Column(String, nullable=True, index=True)
    stripe_price_id = Column(String, nullable=True)  # Price ID from Stripe
    
    # Billing
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Trial
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
            return False
        
        if self.current_period_end and self.current_period_end < datetime.utcnow():
            return False
        
        return True
    
    @property
    def is_premium(self) -> bool:
        """Check if user has a premium plan"""
        return self.plan in [SubscriptionPlan.PRO, SubscriptionPlan.ENTERPRISE] and self.is_active


class PlanFeature(Base):
    """
    Feature limits and capabilities for each subscription plan.
    """
    __tablename__ = "plan_features"
    
    id = Column(Integer, primary_key=True, index=True)
    plan = Column(Enum(SubscriptionPlan), unique=True, nullable=False, index=True)
    
    # Session Limits
    max_session_duration_minutes = Column(Integer, default=60)  # Max session length
    monthly_session_limit = Column(Integer, nullable=True)  # NULL = unlimited
    
    # Feature Access
    can_share_files = Column(Boolean, default=True)
    can_record_sessions = Column(Boolean, default=False)
    can_access_ai_assistant = Column(Boolean, default=True)
    can_book_mentors = Column(Boolean, default=True)
    
    # Support Level
    support_level = Column(String, default="community")  # community, email, priority
    
    # Price
    monthly_price_cents = Column(Integer, default=0)  # Price in cents (USD)
    annual_price_cents = Column(Integer, default=0)  # Annual price in cents
    
    # Description
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PlanFeature(plan={self.plan}, name={self.name})>"


class SubscriptionEvent(Base):
    """
    Log of subscription events (upgrades, downgrades, cancellations, etc.)
    """
    __tablename__ = "subscription_events"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event Details
    event_type = Column(String, nullable=False, index=True)  # created, upgraded, downgraded, cancelled, renewed, payment_failed
    from_plan = Column(Enum(SubscriptionPlan), nullable=True)
    to_plan = Column(Enum(SubscriptionPlan), nullable=True)
    
    # Event Data
    event_data = Column(Text, nullable=True)  # JSON string with additional data
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    subscription = relationship("Subscription", backref="events")
    
    def __repr__(self):
        return f"<SubscriptionEvent(id={self.id}, event_type={self.event_type})>"
