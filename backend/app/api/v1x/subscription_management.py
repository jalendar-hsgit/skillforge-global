"""
Subscription Management System API
Handles subscription tiers, billing cycles, plan management, upgrades/downgrades
Author: SkillForge Development Team
Date: January 26, 2026
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import enum

from app.core.db import get_db, SessionLocal
from app.core.security import get_current_user
from app.models.user import User

# ============================================================================
# SCHEMAS & MODELS
# ============================================================================

class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class BillingCycle(str, enum.Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

# ============================================================================
# SUBSCRIPTION MODELS (Pseudo - using dict in demo)
# ============================================================================

SUBSCRIPTION_TIERS = {
    SubscriptionTier.FREE: {
        "name": "Free",
        "monthly_price": 0.00,
        "features": [
            "5 courses",
            "2 mentor sessions/month",
            "Basic challenges",
            "Community access"
        ],
        "storage_gb": 1,
        "api_calls_per_day": 100
    },
    SubscriptionTier.BASIC: {
        "name": "Basic",
        "monthly_price": 9.99,
        "features": [
            "Unlimited courses",
            "5 mentor sessions/month",
            "All challenges",
            "Priority support",
            "Certificate of completion"
        ],
        "storage_gb": 50,
        "api_calls_per_day": 1000
    },
    SubscriptionTier.PRO: {
        "name": "Professional",
        "monthly_price": 29.99,
        "features": [
            "All Basic features",
            "Unlimited mentor sessions",
            "1-on-1 coaching",
            "Advanced analytics",
            "Job board premium",
            "Resume reviews (2/month)"
        ],
        "storage_gb": 500,
        "api_calls_per_day": 10000
    },
    SubscriptionTier.PREMIUM: {
        "name": "Premium",
        "monthly_price": 99.99,
        "features": [
            "All Pro features",
            "Dedicated mentor",
            "Interview prep",
            "Portfolio builder",
            "Resume reviews unlimited",
            "Company partnerships",
            "Early job access"
        ],
        "storage_gb": 2000,
        "api_calls_per_day": 100000
    },
    SubscriptionTier.ENTERPRISE: {
        "name": "Enterprise",
        "monthly_price": 0.00,  # Custom pricing
        "features": [
            "All Premium features",
            "Custom training",
            "API access",
            "Team management",
            "White-label options",
            "Dedicated support",
            "SLA guarantee"
        ],
        "storage_gb": 10000,
        "api_calls_per_day": 1000000
    }
}

# In-memory storage for subscriptions (would be DB in production)
user_subscriptions = {}
subscription_history = {}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# ============================================================================
# 1. GET SUBSCRIPTION TIERS
# ============================================================================

@router.get("/tiers")
async def get_subscription_tiers():
    """Get all available subscription tiers with pricing and features"""
    tiers = []
    
    for tier, details in SUBSCRIPTION_TIERS.items():
        tiers.append({
            "tier": tier,
            "name": details["name"],
            "monthly_price": details["monthly_price"],
            "features": details["features"],
            "storage_gb": details["storage_gb"],
            "api_calls_per_day": details["api_calls_per_day"],
            "recommended": tier == SubscriptionTier.PRO,  # Pro recommended for most
            "tag": "Most Popular" if tier == SubscriptionTier.PRO else None
        })
    
    return {
        "total_tiers": len(tiers),
        "tiers": tiers,
        "currency": "USD",
        "billing_cycles": [c.value for c in BillingCycle],
        "discounts": {
            "quarterly": 0.05,  # 5% discount
            "annual": 0.15  # 15% discount
        }
    }

# ============================================================================
# 2. GET CURRENT USER SUBSCRIPTION
# ============================================================================

@router.get("/me")
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's active subscription"""
    
    user_id = current_user.id
    subscription = user_subscriptions.get(user_id, {
        "tier": SubscriptionTier.FREE,
        "status": SubscriptionStatus.ACTIVE,
        "billing_cycle": None,
        "next_billing_date": None,
        "expires_at": None,
        "created_at": datetime.utcnow(),
        "features": SUBSCRIPTION_TIERS[SubscriptionTier.FREE]["features"]
    })
    
    return {
        "user_id": user_id,
        "tier": subscription["tier"],
        "status": subscription["status"],
        "billing_cycle": subscription.get("billing_cycle"),
        "next_billing_date": subscription.get("next_billing_date"),
        "expires_at": subscription.get("expires_at"),
        "created_at": subscription["created_at"],
        "features": subscription["features"],
        "storage_used_gb": 0.5,  # Example
        "storage_limit_gb": SUBSCRIPTION_TIERS[subscription["tier"]]["storage_gb"],
        "api_calls_today": 45,  # Example
        "api_call_limit_daily": SUBSCRIPTION_TIERS[subscription["tier"]]["api_calls_per_day"]
    }

# ============================================================================
# 3. UPGRADE SUBSCRIPTION
# ============================================================================

@router.post("/upgrade")
async def upgrade_subscription(
    target_tier: SubscriptionTier = Query(...),
    billing_cycle: BillingCycle = Query(BillingCycle.MONTHLY),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade to a higher tier subscription"""
    
    user_id = current_user.id
    current_sub = user_subscriptions.get(user_id, {})
    current_tier = current_sub.get("tier", SubscriptionTier.FREE)
    
    # Verify upgrade (can't downgrade with this endpoint)
    tier_order = [SubscriptionTier.FREE, SubscriptionTier.BASIC, SubscriptionTier.PRO, 
                  SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]
    
    if tier_order.index(target_tier) <= tier_order.index(current_tier):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upgrade from {current_tier} to {target_tier}"
        )
    
    # Calculate pricing
    current_price = SUBSCRIPTION_TIERS[current_tier]["monthly_price"]
    target_price = SUBSCRIPTION_TIERS[target_tier]["monthly_price"]
    
    # Prorate remaining days
    days_remaining = 30  # Simplified
    daily_current_rate = current_price / 30
    daily_target_rate = target_price / 30
    proration_credit = daily_current_rate * days_remaining
    additional_charge = (daily_target_rate * days_remaining) - proration_credit
    
    # Calculate cycle pricing
    cycle_prices = {
        BillingCycle.MONTHLY: target_price,
        BillingCycle.QUARTERLY: target_price * 3 * 0.95,  # 5% discount
        BillingCycle.ANNUAL: target_price * 12 * 0.85  # 15% discount
    }
    
    next_billing_price = cycle_prices[billing_cycle]
    
    # Create subscription record
    next_billing_date = datetime.utcnow() + timedelta(days=30)
    if billing_cycle == BillingCycle.QUARTERLY:
        next_billing_date = datetime.utcnow() + timedelta(days=90)
    elif billing_cycle == BillingCycle.ANNUAL:
        next_billing_date = datetime.utcnow() + timedelta(days=365)
    
    new_subscription = {
        "tier": target_tier,
        "status": SubscriptionStatus.ACTIVE,
        "billing_cycle": billing_cycle,
        "next_billing_date": next_billing_date,
        "expires_at": None,
        "created_at": datetime.utcnow(),
        "features": SUBSCRIPTION_TIERS[target_tier]["features"]
    }
    
    user_subscriptions[user_id] = new_subscription
    
    # Record in history
    if user_id not in subscription_history:
        subscription_history[user_id] = []
    
    subscription_history[user_id].append({
        "action": "upgrade",
        "from_tier": current_tier,
        "to_tier": target_tier,
        "timestamp": datetime.utcnow(),
        "proration_credit": proration_credit,
        "additional_charge": additional_charge,
        "next_billing_date": next_billing_date,
        "billing_cycle": billing_cycle
    })
    
    return {
        "status": "success",
        "message": f"Upgraded to {target_tier}",
        "from_tier": current_tier,
        "to_tier": target_tier,
        "effective_date": datetime.utcnow(),
        "next_billing_date": next_billing_date,
        "billing_cycle": billing_cycle,
        "proration": {
            "credit_applied": f"${proration_credit:.2f}",
            "additional_charge": f"${additional_charge:.2f}",
            "next_charge": f"${next_billing_price:.2f}"
        },
        "features_unlocked": SUBSCRIPTION_TIERS[target_tier]["features"]
    }

# ============================================================================
# 4. DOWNGRADE SUBSCRIPTION
# ============================================================================

@router.post("/downgrade")
async def downgrade_subscription(
    target_tier: SubscriptionTier = Query(...),
    effective_date: Optional[str] = Query(None),  # YYYY-MM-DD
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Downgrade subscription (takes effect at end of cycle or specified date)"""
    
    user_id = current_user.id
    current_sub = user_subscriptions.get(user_id, {})
    current_tier = current_sub.get("tier", SubscriptionTier.FREE)
    
    # Verify downgrade
    tier_order = [SubscriptionTier.FREE, SubscriptionTier.BASIC, SubscriptionTier.PRO, 
                  SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]
    
    if tier_order.index(target_tier) >= tier_order.index(current_tier):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot downgrade from {current_tier} to {target_tier}"
        )
    
    # Determine effective date (default: end of current billing cycle)
    if effective_date:
        downgrade_date = datetime.fromisoformat(effective_date)
    else:
        downgrade_date = current_sub.get("next_billing_date", datetime.utcnow() + timedelta(days=30))
    
    # Record pending downgrade
    if user_id not in subscription_history:
        subscription_history[user_id] = []
    
    subscription_history[user_id].append({
        "action": "downgrade_scheduled",
        "from_tier": current_tier,
        "to_tier": target_tier,
        "timestamp": datetime.utcnow(),
        "effective_date": downgrade_date,
        "status": "pending"
    })
    
    return {
        "status": "scheduled",
        "message": f"Downgrade to {target_tier} scheduled",
        "from_tier": current_tier,
        "to_tier": target_tier,
        "effective_date": downgrade_date,
        "current_tier_active_until": current_sub.get("next_billing_date"),
        "new_monthly_cost": f"${SUBSCRIPTION_TIERS[target_tier]['monthly_price']:.2f}",
        "savings": f"${(SUBSCRIPTION_TIERS[current_tier]['monthly_price'] - SUBSCRIPTION_TIERS[target_tier]['monthly_price']):.2f}/month"
    }

# ============================================================================
# 5. CANCEL SUBSCRIPTION
# ============================================================================

@router.post("/cancel")
async def cancel_subscription(
    reason: Optional[str] = Query(None),
    immediate: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    
    user_id = current_user.id
    current_sub = user_subscriptions.get(user_id, {})
    current_tier = current_sub.get("tier", SubscriptionTier.FREE)
    
    if current_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel Free tier"
        )
    
    # Calculate refund if immediate
    refund_amount = 0.0
    if immediate and current_sub.get("next_billing_date"):
        days_remaining = (current_sub["next_billing_date"] - datetime.utcnow()).days
        if days_remaining > 0:
            daily_rate = SUBSCRIPTION_TIERS[current_tier]["monthly_price"] / 30
            refund_amount = daily_rate * days_remaining
    
    # Cancel subscription
    cancelled_sub = {
        "tier": SubscriptionTier.FREE,
        "status": SubscriptionStatus.CANCELLED if immediate else SubscriptionStatus.ACTIVE,
        "billing_cycle": None,
        "cancelled_at": datetime.utcnow(),
        "cancelled_reason": reason
    }
    
    if immediate:
        user_subscriptions[user_id] = cancelled_sub
    else:
        # Schedule cancellation at end of billing
        current_sub["scheduled_cancellation"] = {
            "date": current_sub.get("next_billing_date"),
            "reason": reason
        }
    
    # Record in history
    if user_id not in subscription_history:
        subscription_history[user_id] = []
    
    subscription_history[user_id].append({
        "action": "cancel",
        "from_tier": current_tier,
        "to_tier": SubscriptionTier.FREE,
        "timestamp": datetime.utcnow(),
        "reason": reason,
        "immediate": immediate,
        "refund_issued": f"${refund_amount:.2f}" if immediate else "$0.00"
    })
    
    return {
        "status": "cancelled" if immediate else "scheduled",
        "message": f"Subscription {'cancelled immediately' if immediate else 'scheduled for cancellation'}",
        "from_tier": current_tier,
        "effective_date": datetime.utcnow() if immediate else current_sub.get("next_billing_date"),
        "refund_issued": f"${refund_amount:.2f}" if immediate else "$0.00",
        "reason": reason
    }

# ============================================================================
# 6. PAUSE SUBSCRIPTION
# ============================================================================

@router.post("/pause")
async def pause_subscription(
    duration_days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause subscription temporarily (won't charge during pause)"""
    
    user_id = current_user.id
    current_sub = user_subscriptions.get(user_id, {})
    
    if current_sub.get("status") == SubscriptionStatus.PAUSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is already paused"
        )
    
    pause_end_date = datetime.utcnow() + timedelta(days=duration_days)
    
    # Update subscription
    current_sub["status"] = SubscriptionStatus.PAUSED
    current_sub["paused_at"] = datetime.utcnow()
    current_sub["paused_until"] = pause_end_date
    
    user_subscriptions[user_id] = current_sub
    
    return {
        "status": "paused",
        "message": f"Subscription paused for {duration_days} days",
        "paused_at": datetime.utcnow(),
        "paused_until": pause_end_date,
        "will_resume": pause_end_date,
        "billing_suspended": True,
        "features_available": []
    }

# ============================================================================
# 7. RESUME SUBSCRIPTION
# ============================================================================

@router.post("/resume")
async def resume_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resume paused subscription"""
    
    user_id = current_user.id
    current_sub = user_subscriptions.get(user_id, {})
    
    if current_sub.get("status") != SubscriptionStatus.PAUSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is not paused"
        )
    
    # Resume
    current_sub["status"] = SubscriptionStatus.ACTIVE
    paused_duration = (datetime.utcnow() - current_sub.get("paused_at")).days
    
    # Extend next billing date by pause duration
    if current_sub.get("next_billing_date"):
        current_sub["next_billing_date"] = current_sub["next_billing_date"] + timedelta(days=paused_duration)
    
    del current_sub["paused_at"]
    del current_sub["paused_until"]
    
    user_subscriptions[user_id] = current_sub
    
    return {
        "status": "resumed",
        "message": "Subscription resumed",
        "resumed_at": datetime.utcnow(),
        "next_billing_date": current_sub.get("next_billing_date"),
        "billing_extended_by_days": paused_duration,
        "tier": current_sub["tier"]
    }

# ============================================================================
# 8. GET SUBSCRIPTION HISTORY
# ============================================================================

@router.get("/history")
async def get_subscription_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's subscription change history"""
    
    user_id = current_user.id
    history = subscription_history.get(user_id, [])
    
    # Sort by timestamp descending
    sorted_history = sorted(history, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    return {
        "user_id": user_id,
        "total_changes": len(history),
        "showing": len(sorted_history),
        "history": sorted_history
    }

# ============================================================================
# 9. GET BILLING DETAILS
# ============================================================================

@router.get("/billing")
async def get_billing_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing details and payment methods"""
    
    user_id = current_user.id
    subscription = user_subscriptions.get(user_id, {})
    
    tier = subscription.get("tier", SubscriptionTier.FREE)
    billing_cycle = subscription.get("billing_cycle", "N/A")
    
    # Calculate next billing amount
    if billing_cycle == BillingCycle.MONTHLY:
        next_amount = SUBSCRIPTION_TIERS[tier]["monthly_price"]
    elif billing_cycle == BillingCycle.QUARTERLY:
        next_amount = SUBSCRIPTION_TIERS[tier]["monthly_price"] * 3 * 0.95
    elif billing_cycle == BillingCycle.ANNUAL:
        next_amount = SUBSCRIPTION_TIERS[tier]["monthly_price"] * 12 * 0.85
    else:
        next_amount = 0.0
    
    return {
        "user_id": user_id,
        "tier": tier,
        "billing_cycle": billing_cycle,
        "next_billing_date": subscription.get("next_billing_date"),
        "next_billing_amount": f"${next_amount:.2f}",
        "payment_method": {
            "type": "card",
            "last_four": "4242",
            "brand": "Visa",
            "expires": "12/2025"
        },
        "billing_email": current_user.email,
        "auto_renew": True,
        "invoices": [
            {
                "date": "2026-01-26",
                "amount": f"${next_amount:.2f}",
                "status": "Paid",
                "invoice_url": "/invoices/INV-001"
            }
        ]
    }

# ============================================================================
# 10. UPDATE PAYMENT METHOD
# ============================================================================

@router.put("/payment-method")
async def update_payment_method(
    card_token: str = Query(...),
    default: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update payment method for billing"""
    
    # In production, this would:
    # 1. Tokenize card with Stripe
    # 2. Update customer payment method
    # 3. Set as default if requested
    
    return {
        "status": "success",
        "message": "Payment method updated",
        "payment_method": {
            "type": "card",
            "last_four": "4242",
            "brand": "Visa",
            "expires": "12/2025",
            "set_as_default": default
        }
    }

# ============================================================================
# 11. GET AVAILABLE UPGRADES
# ============================================================================

@router.get("/available-upgrades")
async def get_available_upgrades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available upgrade options from current tier"""
    
    user_id = current_user.id
    current_sub = user_subscriptions.get(user_id, {})
    current_tier = current_sub.get("tier", SubscriptionTier.FREE)
    
    tier_order = [SubscriptionTier.FREE, SubscriptionTier.BASIC, SubscriptionTier.PRO, 
                  SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]
    current_index = tier_order.index(current_tier)
    
    upgrades = []
    for i in range(current_index + 1, len(tier_order)):
        tier = tier_order[i]
        details = SUBSCRIPTION_TIERS[tier]
        upgrades.append({
            "tier": tier,
            "name": details["name"],
            "monthly_price": details["monthly_price"],
            "new_features": [
                f for f in details["features"] 
                if f not in SUBSCRIPTION_TIERS[current_tier].get("features", [])
            ],
            "total_features": len(details["features"]),
            "upgrade_button": f"Upgrade to {details['name']}"
        })
    
    return {
        "current_tier": current_tier,
        "available_upgrades": upgrades,
        "recommended": upgrades[0] if upgrades else None
    }

# ============================================================================
# 12. BILLING ANALYTICS
# ============================================================================

@router.get("/analytics")
async def get_billing_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing and usage analytics for user"""
    
    user_id = current_user.id
    subscription = user_subscriptions.get(user_id, {})
    tier = subscription.get("tier", SubscriptionTier.FREE)
    
    tier_limits = SUBSCRIPTION_TIERS[tier]
    
    return {
        "user_id": user_id,
        "tier": tier,
        "usage": {
            "storage": {
                "used_gb": 2.5,
                "limit_gb": tier_limits["storage_gb"],
                "percentage": (2.5 / tier_limits["storage_gb"] * 100) if tier_limits["storage_gb"] > 0 else 0
            },
            "api_calls": {
                "used_today": 245,
                "limit_daily": tier_limits["api_calls_per_day"],
                "percentage": (245 / tier_limits["api_calls_per_day"] * 100) if tier_limits["api_calls_per_day"] > 0 else 0,
                "reset_at": datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            }
        },
        "spent_this_month": "$0.00" if tier == SubscriptionTier.FREE else f"${tier_limits['monthly_price']:.2f}",
        "spent_this_year": "$0.00" if tier == SubscriptionTier.FREE else f"${tier_limits['monthly_price'] * 12:.2f}",
        "next_charge": subscription.get("next_billing_date")
    }

# ============================================================================
# EXPORT ROUTER
# ============================================================================

if __name__ != "__main__":
    # Make sure router is exported for main app
    __all__ = ["router"]
