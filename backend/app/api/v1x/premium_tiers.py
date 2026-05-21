"""
Premium Tiers API router.
Endpoints for subscription management, tier browsing, and payment handling.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.premium_tiers import (
    SubscriptionTier, UserSubscription, SubscriptionHistory, FeatureBenefit, PromoCode,
    TierType, BillingPeriod
)

router = APIRouter(prefix="/subscriptions", tags=["premium_tiers"])


# ===================== Browse Subscription Tiers =====================

@router.get("/tiers")
def list_subscription_tiers(db: Session = Depends(get_db)):
    """List all available subscription tiers with features"""
    tiers = db.query(SubscriptionTier).filter(
        SubscriptionTier.is_active == True
    ).order_by(SubscriptionTier.display_order).all()
    
    result = []
    for tier in tiers:
        result.append(_format_tier_with_benefits(tier))
    
    return {"tiers": result}


@router.get("/tiers/{tier_id}")
def get_subscription_tier(tier_id: int, db: Session = Depends(get_db)):
    """Get details of a specific subscription tier"""
    tier = db.query(SubscriptionTier).filter(SubscriptionTier.id == tier_id).first()
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    return {"tier": _format_tier_with_benefits(tier)}


# ===================== User Subscription Management =====================

@router.get("/me")
def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription details"""
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        # Return free tier
        free_tier = db.query(SubscriptionTier).filter(
            SubscriptionTier.tier_type == TierType.FREE
        ).first()
        if free_tier:
            return {
                "subscription": None,
                "tier": _format_tier_with_benefits(free_tier),
                "is_free_tier": True
            }
        return {"subscription": None, "tier": None, "is_free_tier": True}
    
    tier = db.query(SubscriptionTier).filter(SubscriptionTier.id == subscription.tier_id).first()
    
    return {
        "subscription": _format_user_subscription(subscription),
        "tier": _format_tier_with_benefits(tier) if tier else None,
        "is_active": subscription.is_active(),
        "days_until_renewal": subscription.days_until_renewal()
    }


@router.post("/upgrade")
def upgrade_subscription(
    upgrade_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upgrade to a higher tier"""
    new_tier_id = upgrade_data.get("tier_id")
    billing_period = upgrade_data.get("billing_period", "monthly")
    promo_code = upgrade_data.get("promo_code")
    
    # Validate tier
    new_tier = db.query(SubscriptionTier).filter(
        SubscriptionTier.id == new_tier_id
    ).first()
    if not new_tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    # Get or create subscription
    current_sub = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id
    ).first()
    
    if current_sub:
        # Record history for downgrade/upgrade
        old_tier = db.query(SubscriptionTier).filter(
            SubscriptionTier.id == current_sub.tier_id
        ).first()
        
        # Determine event type
        if new_tier.display_order > old_tier.display_order:
            event_type = "upgraded"
        elif new_tier.display_order < old_tier.display_order:
            event_type = "downgraded"
        else:
            event_type = "changed"
        
        # Update existing subscription
        current_sub.tier_id = new_tier_id
        current_sub.billing_period = BillingPeriod(billing_period)
        current_sub.payment_status = "active"
        current_sub.renewed_at = datetime.utcnow()
        
        # Calculate expiration
        if billing_period == "monthly":
            current_sub.expires_at = datetime.utcnow() + timedelta(days=30)
        elif billing_period == "yearly":
            current_sub.expires_at = datetime.utcnow() + timedelta(days=365)
        else:
            current_sub.expires_at = None
        
        subscription = current_sub
    else:
        # Create new subscription
        expires_at = None
        if billing_period == "monthly":
            expires_at = datetime.utcnow() + timedelta(days=30)
        elif billing_period == "yearly":
            expires_at = datetime.utcnow() + timedelta(days=365)
        
        subscription = UserSubscription(
            user_id=current_user.id,
            tier_id=new_tier_id,
            billing_period=BillingPeriod(billing_period),
            payment_status="active",
            expires_at=expires_at,
            auto_renew=True
        )
        db.add(subscription)
        event_type = "created"
    
    # Apply promo code if provided
    amount_paid = None
    if billing_period == "monthly":
        amount_paid = new_tier.monthly_price
    elif billing_period == "yearly":
        amount_paid = new_tier.yearly_price
    elif billing_period == "lifetime":
        amount_paid = new_tier.lifetime_price
    
    if promo_code:
        promo = db.query(PromoCode).filter(PromoCode.code == promo_code).first()
        if promo and promo.is_valid():
            if promo.discount_type == "percentage":
                discount = (amount_paid or 0) * (promo.discount_value / 100)
            else:
                discount = promo.discount_value
            amount_paid = max(0, (amount_paid or 0) - discount)
            promo.current_uses += 1
        else:
            raise HTTPException(status_code=400, detail="Invalid or expired promo code")
    
    # Record history
    history = SubscriptionHistory(
        user_id=current_user.id,
        tier_id=new_tier_id,
        event_type=event_type,
        billing_period=BillingPeriod(billing_period),
        amount_paid=amount_paid,
        payment_method="stripe"  # TODO: integrate with Stripe
    )
    
    db.add(history)
    db.commit()
    db.refresh(subscription)
    
    return {
        "message": f"Successfully {event_type}d to {new_tier.name}",
        "subscription": _format_user_subscription(subscription),
        "tier": _format_tier_with_benefits(new_tier)
    }


@router.post("/cancel")
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel current subscription"""
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    subscription.cancelled_at = datetime.utcnow()
    subscription.payment_status = "cancelled"
    subscription.auto_renew = False
    
    # Record history
    history = SubscriptionHistory(
        user_id=current_user.id,
        tier_id=subscription.tier_id,
        event_type="cancelled",
        reason="User initiated cancellation"
    )
    
    db.add(history)
    db.commit()
    db.refresh(subscription)
    
    return {
        "message": "Subscription cancelled",
        "subscription": _format_user_subscription(subscription)
    }


# ===================== Subscription History =====================

@router.get("/history")
def get_subscription_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's subscription history"""
    total = db.query(SubscriptionHistory).filter(
        SubscriptionHistory.user_id == current_user.id
    ).count()
    
    history = db.query(SubscriptionHistory).filter(
        SubscriptionHistory.user_id == current_user.id
    ).order_by(SubscriptionHistory.occurred_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "history": [_format_subscription_history(h) for h in history]
    }


# ===================== Promo Codes =====================

@router.post("/validate-promo")
def validate_promo_code(
    promo_data: dict,
    db: Session = Depends(get_db)
):
    """Validate a promo code and get discount info"""
    code = promo_data.get("code")
    tier_id = promo_data.get("tier_id")
    
    promo = db.query(PromoCode).filter(PromoCode.code == code).first()
    if not promo or not promo.is_valid():
        raise HTTPException(status_code=400, detail="Invalid or expired promo code")
    
    # Check if applicable to tier
    if promo.applicable_tiers and tier_id not in promo.applicable_tiers:
        raise HTTPException(status_code=400, detail="Promo code not applicable to this tier")
    
    tier = db.query(SubscriptionTier).filter(SubscriptionTier.id == tier_id).first()
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    return {
        "code": code,
        "valid": True,
        "discount_type": promo.discount_type,
        "discount_value": promo.discount_value,
        "description": promo.description
    }


# ===================== Admin: Manage Promo Codes =====================

@router.post("/promo-codes")
def create_promo_code(
    promo_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new promo code (admin only)"""
    # TODO: Add admin check
    
    promo = PromoCode(
        code=promo_data.get("code").upper(),
        description=promo_data.get("description"),
        discount_type=promo_data.get("discount_type", "percentage"),
        discount_value=promo_data.get("discount_value"),
        max_uses=promo_data.get("max_uses"),
        applicable_tiers=promo_data.get("applicable_tiers", [])
    )
    
    db.add(promo)
    db.commit()
    db.refresh(promo)
    
    return _format_promo_code(promo)


@router.get("/promo-codes")
def list_promo_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all promo codes (admin only)"""
    # TODO: Add admin check
    
    total = db.query(PromoCode).count()
    codes = db.query(PromoCode).order_by(PromoCode.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "promo_codes": [_format_promo_code(c) for c in codes]
    }


# ===================== Helper Functions =====================

def _format_tier_with_benefits(tier):
    """Format tier with all benefits"""
    return {
        "id": tier.id,
        "name": tier.name,
        "tier_type": tier.tier_type.value,
        "description": tier.description,
        "monthly_price": tier.monthly_price,
        "yearly_price": tier.yearly_price,
        "lifetime_price": tier.lifetime_price,
        "display_order": tier.display_order,
        "color": tier.color,
        "icon": tier.icon,
        "is_popular": tier.is_popular,
        "quotas": {
            "max_coding_submissions_per_day": tier.max_coding_submissions_per_day,
            "max_code_snippets": tier.max_code_snippets,
            "max_learning_paths": tier.max_learning_paths,
            "max_ai_hints_per_day": tier.max_ai_hints_per_day,
            "max_storage_gb": tier.max_storage_gb
        },
        "features": {
            "advanced_analytics": tier.has_advanced_analytics,
            "ai_code_review": tier.has_ai_code_review,
            "video_tutorials": tier.has_video_tutorials,
            "mentorship": tier.has_mentorship,
            "certification": tier.has_certification,
            "early_access": tier.has_early_access,
            "priority_support": tier.has_priority_support,
            "custom_learning_paths": tier.has_custom_learning_paths
        },
        "benefits": [_format_benefit(b) for b in tier.benefits]
    }


def _format_benefit(benefit):
    """Format a feature benefit"""
    return {
        "id": benefit.id,
        "feature_name": benefit.feature_name,
        "feature_description": benefit.feature_description,
        "icon": benefit.icon,
        "order": benefit.order
    }


def _format_user_subscription(subscription):
    """Format user subscription for API response"""
    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "tier_id": subscription.tier_id,
        "billing_period": subscription.billing_period.value,
        "payment_status": subscription.payment_status,
        "auto_renew": subscription.auto_renew,
        "started_at": subscription.started_at.isoformat(),
        "renewed_at": subscription.renewed_at.isoformat(),
        "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
        "cancelled_at": subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
        "stripe_subscription_id": subscription.stripe_subscription_id,
        "created_at": subscription.created_at.isoformat()
    }


def _format_subscription_history(history):
    """Format subscription history entry"""
    return {
        "id": history.id,
        "event_type": history.event_type,
        "reason": history.reason,
        "billing_period": history.billing_period.value if history.billing_period else None,
        "amount_paid": history.amount_paid,
        "payment_method": history.payment_method,
        "transaction_id": history.transaction_id,
        "occurred_at": history.occurred_at.isoformat()
    }


def _format_promo_code(promo):
    """Format promo code for API response"""
    return {
        "id": promo.id,
        "code": promo.code,
        "description": promo.description,
        "discount_type": promo.discount_type,
        "discount_value": promo.discount_value,
        "max_uses": promo.max_uses,
        "current_uses": promo.current_uses,
        "applicable_tiers": promo.applicable_tiers,
        "starts_at": promo.starts_at.isoformat(),
        "expires_at": promo.expires_at.isoformat() if promo.expires_at else None,
        "is_active": promo.is_active,
        "is_valid": promo.is_valid()
    }
