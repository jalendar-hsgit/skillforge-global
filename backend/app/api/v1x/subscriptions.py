"""
Subscription management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.subscription import (
    Subscription, SubscriptionPlan, SubscriptionStatus,
    PlanFeature, SubscriptionEvent
)
from app.services.stripe_service import stripe_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# Schemas
class PlanFeatureSchema(BaseModel):
    plan: SubscriptionPlan
    name: str
    description: Optional[str] = None
    monthly_price_cents: int
    annual_price_cents: int
    max_session_duration_minutes: int
    monthly_session_limit: Optional[int] = None
    can_share_files: bool
    can_record_sessions: bool
    can_access_ai_assistant: bool
    can_book_mentors: bool
    support_level: str
    
    class Config:
        from_attributes = True


class SubscriptionSchema(BaseModel):
    id: int
    user_id: int
    plan: SubscriptionPlan
    status: SubscriptionStatus
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    is_active: bool
    is_premium: bool
    
    class Config:
        from_attributes = True


class CreateSubscriptionRequest(BaseModel):
    plan: SubscriptionPlan = Field(..., description="Subscription plan to subscribe to")
    payment_method_id: str = Field(..., description="Stripe payment method ID")
    billing_cycle: str = Field("monthly", description="monthly or annual")


class CancelSubscriptionRequest(BaseModel):
    cancel_immediately: bool = Field(False, description="Cancel immediately or at period end")
    reason: Optional[str] = None


# Helper Functions
def initialize_plan_features(db: Session):
    """Initialize default plan features if they don't exist"""
    plans_data = [
        {
            "plan": SubscriptionPlan.FREE,
            "name": "Free",
            "description": "Perfect for getting started with learning",
            "monthly_price_cents": 0,
            "annual_price_cents": 0,
            "max_session_duration_minutes": 30,
            "monthly_session_limit": 2,
            "can_share_files": False,
            "can_record_sessions": False,
            "can_access_ai_assistant": True,
            "can_book_mentors": True,
            "support_level": "community"
        },
        {
            "plan": SubscriptionPlan.PRO,
            "name": "Pro",
            "description": "For serious learners who want unlimited access",
            "monthly_price_cents": 2900,  # $29/month
            "annual_price_cents": 29000,  # $290/year (save ~17%)
            "max_session_duration_minutes": 120,
            "monthly_session_limit": None,  # Unlimited
            "can_share_files": True,
            "can_record_sessions": True,
            "can_access_ai_assistant": True,
            "can_book_mentors": True,
            "support_level": "email"
        },
        {
            "plan": SubscriptionPlan.ENTERPRISE,
            "name": "Enterprise",
            "description": "For teams and organizations",
            "monthly_price_cents": 9900,  # $99/month
            "annual_price_cents": 99000,  # $990/year (save ~17%)
            "max_session_duration_minutes": 240,
            "monthly_session_limit": None,  # Unlimited
            "can_share_files": True,
            "can_record_sessions": True,
            "can_access_ai_assistant": True,
            "can_book_mentors": True,
            "support_level": "priority"
        }
    ]
    
    for plan_data in plans_data:
        existing = db.query(PlanFeature).filter(
            PlanFeature.plan == plan_data["plan"]
        ).first()
        
        if not existing:
            feature = PlanFeature(**plan_data)
            db.add(feature)
    
    db.commit()


def get_or_create_subscription(user: User, db: Session) -> Subscription:
    """Get existing subscription or create free one"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).first()
    
    if not subscription:
        # Create free subscription
        subscription = Subscription(
            user_id=user.id,
            plan=SubscriptionPlan.FREE,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # Log event
        event = SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="created",
            to_plan=SubscriptionPlan.FREE
        )
        db.add(event)
        db.commit()
    
    return subscription


# Endpoints

@router.get("/plans", response_model=List[PlanFeatureSchema])
def get_plans(db: Session = Depends(get_db)):
    """
    Get all available subscription plans and their features.
    """
    # Initialize plans if they don't exist
    initialize_plan_features(db)
    
    plans = db.query(PlanFeature).all()
    return plans


@router.get("/current", response_model=SubscriptionSchema)
def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription details.
    """
    subscription = get_or_create_subscription(current_user, db)
    return subscription


@router.post("/subscribe", response_model=SubscriptionSchema, status_code=status.HTTP_201_CREATED)
def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a paid plan using Stripe.
    Creates or updates the user's subscription.
    """
    if request.plan == SubscriptionPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot subscribe to free plan via this endpoint"
        )
    
    # Get plan features
    plan_feature = db.query(PlanFeature).filter(
        PlanFeature.plan == request.plan
    ).first()
    
    if not plan_feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Calculate price based on billing cycle
    if request.billing_cycle == "annual":
        price_cents = plan_feature.annual_price_cents
    else:
        price_cents = plan_feature.monthly_price_cents
    
    try:
        # Get or create subscription
        subscription = get_or_create_subscription(current_user, db)
        old_plan = subscription.plan
        
        # Create Stripe subscription
        stripe_subscription = stripe_service.create_subscription(
            user_id=current_user.id,
            email=current_user.email,
            payment_method_id=request.payment_method_id,
            plan=request.plan.value,
            price_cents=price_cents,
            billing_cycle=request.billing_cycle
        )
        
        # Update subscription
        subscription.plan = request.plan
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.stripe_subscription_id = stripe_subscription['id']
        subscription.stripe_customer_id = stripe_subscription['customer']
        subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
        subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
        subscription.cancel_at_period_end = False
        
        db.commit()
        db.refresh(subscription)
        
        # Log event
        event = SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="upgraded" if old_plan == SubscriptionPlan.FREE else "plan_changed",
            from_plan=old_plan,
            to_plan=request.plan,
            event_data=json.dumps({"billing_cycle": request.billing_cycle})
        )
        db.add(event)
        db.commit()
        
        return subscription
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.post("/cancel", response_model=SubscriptionSchema)
def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription.
    Can cancel immediately or at the end of the billing period.
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    if subscription.plan == SubscriptionPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel free plan"
        )
    
    try:
        # Cancel Stripe subscription
        if subscription.stripe_subscription_id:
            stripe_service.cancel_subscription(
                subscription_id=subscription.stripe_subscription_id,
                cancel_immediately=request.cancel_immediately
            )
        
        old_plan = subscription.plan
        
        if request.cancel_immediately:
            subscription.plan = SubscriptionPlan.FREE
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            subscription.cancel_at_period_end = False
        else:
            subscription.cancel_at_period_end = True
            subscription.cancelled_at = datetime.utcnow()
        
        db.commit()
        db.refresh(subscription)
        
        # Log event
        event = SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="cancelled",
            from_plan=old_plan,
            to_plan=SubscriptionPlan.FREE if request.cancel_immediately else old_plan,
            event_data=json.dumps({
                "reason": request.reason,
                "cancel_immediately": request.cancel_immediately
            })
        )
        db.add(event)
        db.commit()
        
        return subscription
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events for subscription updates.
    Events: subscription.updated, subscription.deleted, invoice.payment_failed, etc.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # Verify webhook signature (implement in stripe_service)
        event = stripe_service.verify_webhook(payload, sig_header)
        
        if event['type'] == 'customer.subscription.updated':
            subscription_data = event['data']['object']
            
            # Find subscription by Stripe ID
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_data['id']
            ).first()
            
            if subscription:
                # Update status
                subscription.status = SubscriptionStatus(subscription_data['status'])
                subscription.current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
                subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
                subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
                
                db.commit()
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription_data = event['data']['object']
            
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_data['id']
            ).first()
            
            if subscription:
                old_plan = subscription.plan
                subscription.plan = SubscriptionPlan.FREE
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.utcnow()
                
                db.commit()
                
                # Log event
                event_log = SubscriptionEvent(
                    subscription_id=subscription.id,
                    event_type="cancelled",
                    from_plan=old_plan,
                    to_plan=SubscriptionPlan.FREE
                )
                db.add(event_log)
                db.commit()
        
        elif event['type'] == 'invoice.payment_failed':
            # Handle payment failure
            subscription_data = event['data']['object'].get('subscription')
            if subscription_data:
                subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription_data
                ).first()
                
                if subscription:
                    subscription.status = SubscriptionStatus.PAST_DUE
                    db.commit()
        
        return {"success": True}
    
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/features", response_model=PlanFeatureSchema)
def get_user_features(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get feature limits for the current user's plan.
    """
    subscription = get_or_create_subscription(current_user, db)
    
    features = db.query(PlanFeature).filter(
        PlanFeature.plan == subscription.plan
    ).first()
    
    if not features:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan features not found"
        )
    
    return features
