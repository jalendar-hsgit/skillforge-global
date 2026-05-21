"""
Stripe-Integrated Payments Endpoints
====================================

Enhanced payment endpoints with Stripe integration:
- Process session payments with Stripe
- Request mentor payouts
- Get payment history
- Refund payments
- Check mentor balance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User
from app.modelsx.phase_2_3_models import (
    SessionPayment,
    PaymentStatus,
    PayoutStatus,
)
from app.modelsx.payout import MentorPayout
from app.schemas.phase_2_3_schemas import (
    PaymentRequest,
    PaymentResponse,
    PayoutRequest,
    PayoutResponse,
    MentorBalanceResponse,
)
from app.services.stripe_service import StripeService, process_session_payment, process_mentor_payout
from app.services.email_service import email_service

payments_router = APIRouter(prefix="/payments", tags=["payments"])


# ============================================================
# PAYMENT ENDPOINTS
# ============================================================

@payments_router.post("/session", response_model=PaymentResponse)
async def process_session_payment_endpoint(
    request: PaymentRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Process payment for mentor session
    
    Returns Stripe payment_intent.client_secret for frontend payment completion
    """
    try:
        # Create payment record
        payment = SessionPayment(
            session_id=request.session_id,
            user_id=user.id,
            mentor_id=request.mentor_id if hasattr(request, 'mentor_id') else 0,
            amount=request.amount,
            currency=request.currency,
            payment_method=request.payment_method,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Create Stripe payment intent
        try:
            payment_intent = StripeService.create_payment_intent(
                amount=int(request.amount * 100),  # Convert to cents
                currency=request.currency.lower(),
                metadata={
                    "payment_id": str(payment.id),
                    "session_id": str(request.session_id),
                    "user_id": str(user.id),
                }
            )
            
            # Update payment with Stripe IDs
            payment.stripe_payment_id = payment_intent["id"]
            payment.stripe_payment_intent = payment_intent["client_secret"]
            db.commit()
            db.refresh(payment)
            
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            db.commit()
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
        
        return {
            "id": payment.id,
            "session_id": payment.session_id,
            "user_id": payment.user_id,
            "mentor_id": payment.mentor_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "stripe_payment_id": payment.stripe_payment_id,
            "stripe_payment_intent": payment.stripe_payment_intent,
            "created_at": payment.created_at,
            "paid_at": payment.paid_at,
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@payments_router.get("/history")
async def get_payment_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get payment history for current user (paginated)"""
    payments = db.query(SessionPayment).filter_by(user_id=user.id)\
        .order_by(SessionPayment.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "payments": [
            {
                "id": p.id,
                "session_id": p.session_id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "created_at": p.created_at,
            }
            for p in payments
        ],
        "total": db.query(SessionPayment).filter_by(user_id=user.id).count(),
        "skip": skip,
        "limit": limit,
    }


@payments_router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Request refund for payment"""
    payment = db.query(SessionPayment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check authorization
    if payment.user_id != user.id and user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        # Refund via Stripe if payment was completed
        if payment.status == PaymentStatus.COMPLETED and payment.stripe_payment_id:
            StripeService.refund_payment(payment.stripe_payment_id)
        
        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        db.commit()
        
        # Send refund notification email
        try:
            await email_service.send_payment_receipt(
                email=user.email,
                user_name=user.name,
                amount=payment.amount,
                mentor_name="N/A",
                session_date=payment.created_at,
            )
        except:
            pass  # Email sending failure shouldn't block refund
        
        return {
            "status": "refunded",
            "payment_id": payment_id,
            "amount": payment.amount,
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Refund failed: {str(e)}")


@payments_router.get("/balance")
async def get_mentor_balance(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current earnings balance for mentor"""
    from app.modelsx.mentor import Mentor
    
    mentor = db.query(Mentor).filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    # Calculate total earned
    total_earned_query = db.query(func.sum(SessionPayment.amount)).filter(
        and_(
            SessionPayment.mentor_id == mentor.id,
            SessionPayment.status == PaymentStatus.COMPLETED
        )
    )
    total_earned = total_earned_query.scalar() or 0.0
    
    # Calculate total paid
    total_paid_query = db.query(func.sum(MentorPayout.amount)).filter(
        and_(
            MentorPayout.mentor_id == mentor.id,
            MentorPayout.status == PayoutStatus.COMPLETED
        )
    )
    total_paid = total_paid_query.scalar() or 0.0
    
    # Available balance = earned - paid
    available_balance = total_earned - total_paid
    
    return {
        "mentor_id": mentor.id,
        "total_earned": round(total_earned, 2),
        "total_paid": round(total_paid, 2),
        "available_balance": round(max(0, available_balance), 2),
        "currency": "USD",
    }


# ============================================================
# PAYOUT ENDPOINTS
# ============================================================

@payments_router.post("/payouts/request")
async def request_payout(
    request: PayoutRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Request mentor payout"""
    from app.modelsx.mentor import Mentor
    
    mentor = db.query(Mentor).filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    try:
        # Get available balance
        total_earned_query = db.query(func.sum(SessionPayment.amount)).filter(
            and_(
                SessionPayment.mentor_id == mentor.id,
                SessionPayment.status == PaymentStatus.COMPLETED
            )
        )
        total_earned = total_earned_query.scalar() or 0.0
        
        total_paid_query = db.query(func.sum(MentorPayout.amount)).filter(
            and_(
                MentorPayout.mentor_id == mentor.id,
                MentorPayout.status == PayoutStatus.COMPLETED
            )
        )
        total_paid = total_paid_query.scalar() or 0.0
        
        available_balance = total_earned - total_paid
        
        # Determine payout amount
        payout_amount = request.amount if request.amount else available_balance
        
        # Validate amount
        if payout_amount <= 0:
            raise HTTPException(status_code=400, detail="Payout amount must be greater than 0")
        
        if payout_amount > available_balance:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Create payout record
        payout = MentorPayout(
            mentor_id=mentor.id,
            amount=payout_amount,
            currency="USD",
            status=PayoutStatus.REQUESTED,
        )
        db.add(payout)
        db.commit()
        db.refresh(payout)
        
        # Process payout via Stripe
        try:
            payout_result = StripeService.create_payout(
                account_id=mentor.stripe_account_id or "",
                amount=int(payout_amount * 100),  # Convert to cents
                currency="usd",
            )
            
            payout.stripe_payout_id = payout_result.get("id")
            payout.status = PayoutStatus.PROCESSING
            db.commit()
            
        except Exception as stripe_error:
            payout.status = PayoutStatus.FAILED
            payout.failure_reason = str(stripe_error)
            db.commit()
            raise HTTPException(status_code=400, detail=f"Stripe payout error: {str(stripe_error)}")
        
        # Send payout notification email
        try:
            await email_service.send_payout_notification(
                email=user.email,
                mentor_name=user.name,
                amount=payout_amount,
            )
        except:
            pass  # Email sending failure shouldn't block payout
        
        return {
            "id": payout.id,
            "mentor_id": payout.mentor_id,
            "amount": payout.amount,
            "currency": payout.currency,
            "status": payout.status,
            "requested_at": payout.requested_at,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@payments_router.get("/payouts")
async def get_payout_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get payout history for mentor"""
    from app.modelsx.mentor import Mentor
    
    mentor = db.query(Mentor).filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    payouts = db.query(MentorPayout).filter_by(mentor_id=mentor.id)\
        .order_by(MentorPayout.requested_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "payouts": [
            {
                "id": p.id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "requested_at": p.requested_at,
                "processed_at": p.processed_at,
            }
            for p in payouts
        ],
        "total": db.query(MentorPayout).filter_by(mentor_id=mentor.id).count(),
        "skip": skip,
        "limit": limit,
    }
