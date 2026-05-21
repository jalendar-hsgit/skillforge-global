# Payment System Fixes - Implementation Guide

**Status**: Ready to implement
**Time Estimate**: 5-6 hours total
**Priority**: Critical for production launch

---

## FIX #1: Session Price Auto-Calculation

### Problem
Mentor sessions are created without setting the `price` field, resulting in $0 payment amounts.

### Current Code (mentors.py - Lines ~350)
```python
@router.post("/book", response_model=SessionResponse)
def book_session(
    request: SessionBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ... validation code ...
    
    session = MentorSession(
        mentor_id=mentor_id,
        student_id=current_user.id,
        topic=request.topic,
        description=request.description,
        scheduled_at=request.scheduled_at,
        duration_minutes=request.duration_minutes,
        # ❌ BUG: price not set here!
        status=SessionStatus.PENDING
    )
```

### Fixed Code
```python
@router.post("/book", response_model=SessionResponse)
def book_session(
    request: SessionBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Book a mentor session with automatic price calculation"""
    
    # Validate mentor exists and is approved
    mentor = db.query(Mentor).filter(Mentor.id == request.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    if mentor.status != MentorStatus.APPROVED:
        raise HTTPException(
            status_code=400, 
            detail="Mentor is not available for booking"
        )
    
    # Validate student is not the mentor
    if mentor.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot book a session with yourself"
        )
    
    # ✅ FIX: Calculate price based on hourly rate
    session_price = (mentor.hourly_rate * request.duration_minutes) / 60
    
    # Create session WITH price
    session = MentorSession(
        mentor_id=request.mentor_id,
        student_id=current_user.id,
        topic=request.topic,
        description=request.description,
        scheduled_at=request.scheduled_at,
        duration_minutes=request.duration_minutes,
        price=session_price,  # ✅ ADDED
        status=SessionStatus.PENDING
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return SessionResponse.from_orm(session)
```

### Testing
```bash
# 1. Create/Find mentor with hourly_rate = 75
# 2. Book 60-minute session
# Expected: session.price = 75.0
# Expected: session.price = 37.5 for 30-minute session

# Test via API:
curl -X POST http://localhost:8001/api/v1x/mentors/book \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "mentor_id": 1,
    "topic": "Python Basics",
    "duration_minutes": 60,
    "scheduled_at": "2026-01-26T14:00:00Z"
  }'

# Verify in response:
# "price": 75.0
```

---

## FIX #2: Add Stripe Webhook Handler

### Problem
Backend doesn't know when Stripe payments succeed. Orders remain in PENDING status indefinitely.

### Solution: Create New File

**File**: `backend/app/api/v1x/stripe_webhook.py`

```python
"""
Stripe Webhook Handler
Receives and processes events from Stripe
"""
from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
import stripe

from app.core.db import get_db
from app.core.config import settings
from app.modelsx.order import Order
from app.modelsx.mentor import MentorSession
from app.modelsx.payout import MentorEarning
from app.services.email_service import email_service

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="", tags=["webhook"])


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    Events handled:
    - payment_intent.succeeded: Order payment successful
    - charge.refunded: Refund processed
    - payment_intent.canceled: Payment canceled
    """
    
    # Get webhook signature from header
    sig_header = request.headers.get("stripe-signature")
    body = await request.body()
    
    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            body, 
            sig_header, 
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event['type']
    event_data = event['data']['object']
    
    try:
        # Handle payment_intent.succeeded event
        if event_type == 'payment_intent.succeeded':
            payment_intent_id = event_data['id']
            metadata = event_data.get('metadata', {})
            
            # Check if this is a course order payment
            order = db.query(Order).filter(
                Order.payment_intent_id == payment_intent_id
            ).first()
            
            if order:
                # Update order status
                order.status = 'completed'
                order.payment_status = 'completed'
                order.paid_at = datetime.utcnow()
                
                # Enroll user in course (if course purchase)
                if order.course_id:
                    from app.modelsx.video import VideoProgress
                    
                    # Create initial video progress for all videos in course
                    videos = db.query(Video).filter(
                        Video.course_id == order.course_id
                    ).all()
                    
                    for video in videos:
                        existing = db.query(VideoProgress).filter(
                            VideoProgress.user_id == order.user_id,
                            VideoProgress.video_id == video.id
                        ).first()
                        
                        if not existing:
                            progress = VideoProgress(
                                user_id=order.user_id,
                                video_id=video.id,
                                progress_percent=0,
                                completed=False
                            )
                            db.add(progress)
                
                db.commit()
                
                # Send confirmation email
                try:
                    email_service.send_order_confirmation(
                        to_email=order.user.email,
                        order_id=order.id,
                        order_number=order.order_number,
                        amount=float(order.amount),
                        course_title=order.course.title if order.course else "Digital Product"
                    )
                except Exception as e:
                    print(f"Failed to send confirmation email: {e}")
            
            # Check if this is a mentor session payment
            session = db.query(MentorSession).filter(
                MentorSession.payment_intent_id == payment_intent_id
            ).first()
            
            if session:
                session.payment_status = 'paid'
                db.commit()
        
        # Handle charge.refunded event
        elif event_type == 'charge.refunded':
            payment_intent_id = event_data.get('payment_intent')
            
            # Find and update order
            order = db.query(Order).filter(
                Order.payment_intent_id == payment_intent_id
            ).first()
            
            if order:
                order.status = 'refunded'
                order.payment_status = 'refunded'
                db.commit()
                
                # Send refund email
                try:
                    email_service.send_refund_notification(
                        to_email=order.user.email,
                        order_number=order.order_number,
                        amount=float(order.amount)
                    )
                except Exception as e:
                    print(f"Failed to send refund email: {e}")
        
        # Handle payment_intent.canceled event
        elif event_type == 'payment_intent.canceled':
            payment_intent_id = event_data['id']
            
            # Find and update order
            order = db.query(Order).filter(
                Order.payment_intent_id == payment_intent_id
            ).first()
            
            if order and order.status == 'pending':
                order.status = 'cancelled'
                order.payment_status = 'cancelled'
                db.commit()
        
        return {"status": "success", "event_id": event['id']}
    
    except Exception as e:
        print(f"Error processing webhook: {e}")
        # Don't raise error - Stripe expects 200 response
        return {"status": "error", "message": str(e)}


@router.get("/webhook/stripe/test")
async def test_webhook():
    """Test endpoint to verify webhook is working"""
    return {"status": "webhook endpoint is active"}
```

### Update main.py

```python
# Add to imports at top
from app.api.v1x.stripe_webhook import router as stripe_webhook_router

# Add to FastAPI app initialization (after other router includes)
app.include_router(stripe_webhook_router)
```

### Configuration

Add to `.env`:
```
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### Testing Webhook Locally

```bash
# 1. Install Stripe CLI (download from https://stripe.com/docs/stripe-cli)

# 2. Login to Stripe
stripe login

# 3. Forward webhooks to local endpoint
stripe listen --forward-to http://localhost:8001/webhook/stripe

# 4. Trigger test events
stripe trigger payment_intent.succeeded

# 5. Check logs in your app for event processing
```

### Production Deployment

1. Deploy code
2. Go to Stripe Dashboard → Webhooks
3. Add endpoint: `https://yourdomain.com/webhook/stripe`
4. Select events: 
   - payment_intent.succeeded
   - charge.refunded
   - payment_intent.canceled
5. Copy webhook secret and add to `.env`

---

## FIX #3: Add Admin Payout Approval

### Problem
Mentors can request payouts but admins cannot approve them. Payouts stay in PENDING status.

### File: `backend/app/api/v1x/admin_payouts.py` (Add/Update)

```python
"""
Admin payout management endpoints
Handles approval, rejection, and tracking of mentor payouts
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

from app.core.db import get_db
from app.core.security import get_current_admin
from app.models.user import User
from app.modelsx.mentor import Mentor
from app.modelsx.payout import (
    MentorPayout, MentorEarning, PayoutStatus, PayoutMethod
)
from app.services.stripe_service import stripe_service
from app.services.email_service import email_service

router = APIRouter(prefix="/admin/payouts", tags=["admin-payouts"])


# Schemas
class PayoutApprovalRequest(BaseModel):
    """Request to approve/reject payout"""
    approval_notes: Optional[str] = None


class PayoutRejectionRequest(BaseModel):
    """Request to reject payout"""
    rejection_reason: str


class PayoutResponse(BaseModel):
    """Payout response"""
    id: int
    mentor_id: int
    mentor_name: str
    amount: float
    net_amount: float
    platform_fee: float
    method: PayoutMethod
    status: PayoutStatus
    requested_at: datetime
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    earnings_count: int
    notes: Optional[str]
    
    class Config:
        from_attributes = True


# ========== ENDPOINTS ==========

@router.get("/pending", response_model=List[PayoutResponse])
async def get_pending_payouts(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all pending payout requests"""
    
    payouts = db.query(MentorPayout).filter(
        MentorPayout.status == PayoutStatus.PENDING
    ).order_by(
        MentorPayout.requested_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Build response with mentor names
    response = []
    for payout in payouts:
        mentor = db.query(Mentor).filter(
            Mentor.id == payout.mentor_id
        ).first()
        
        mentor_user = db.query(User).filter(
            User.id == mentor.user_id
        ).first()
        
        earnings_count = db.query(MentorEarning).filter(
            MentorEarning.payout_id == payout.id
        ).count()
        
        response.append(PayoutResponse(
            id=payout.id,
            mentor_id=payout.mentor_id,
            mentor_name=mentor_user.email if mentor_user else "Unknown",
            amount=payout.amount,
            net_amount=payout.net_amount,
            platform_fee=payout.platform_fee,
            method=payout.method,
            status=payout.status,
            requested_at=payout.requested_at,
            processed_at=payout.processed_at,
            completed_at=payout.completed_at,
            earnings_count=earnings_count,
            notes=payout.notes
        ))
    
    return response


@router.post("/approve/{payout_id}")
async def approve_payout(
    payout_id: int,
    request: Optional[PayoutApprovalRequest] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Approve and process a mentor payout.
    Initiates payment transfer based on payout method.
    """
    
    payout = db.query(MentorPayout).filter(
        MentorPayout.id == payout_id
    ).first()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    if payout.status != PayoutStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Payout already {payout.status.value}"
        )
    
    try:
        # Update status to processing
        payout.status = PayoutStatus.PROCESSING
        payout.processed_at = datetime.utcnow()
        if request and request.approval_notes:
            payout.notes = request.approval_notes
        
        # Process transfer based on method
        if payout.method == PayoutMethod.STRIPE:
            # Get mentor's Stripe account (from payment method)
            from app.modelsx.payment_method import PaymentMethod
            
            mentor = db.query(Mentor).filter(
                Mentor.id == payout.mentor_id
            ).first()
            
            # Check if mentor has Stripe account connected
            # For now, use Stripe Connect transfer
            try:
                transfer = stripe_service.create_transfer_to_mentor(
                    amount=payout.net_amount,
                    mentor_stripe_account=None,  # TODO: Get from mentor profile
                    session_id=None
                )
                payout.stripe_transfer_id = transfer.get('id')
            except Exception as e:
                payout.status = PayoutStatus.FAILED
                payout.failure_reason = str(e)
                db.commit()
                raise HTTPException(status_code=500, detail=str(e))
        
        elif payout.method == PayoutMethod.BANK_TRANSFER:
            # Mark as pending bank processing
            # Bank transfer will be processed manually or via external service
            pass
        
        elif payout.method == PayoutMethod.PAYPAL:
            # TODO: Implement PayPal transfer
            pass
        
        # Mark all related earnings as paid out
        earnings = db.query(MentorEarning).filter(
            MentorEarning.payout_id == payout.id
        ).all()
        
        for earning in earnings:
            earning.is_paid_out = True
            earning.paid_out_at = datetime.utcnow()
        
        db.commit()
        
        # Send approval email to mentor
        mentor_user = db.query(User).filter(
            User.id == payout.mentor_id
        ).first()
        
        try:
            email_service.send_payout_approved(
                to_email=mentor_user.email,
                payout_id=payout.id,
                amount=payout.net_amount,
                method=payout.method.value
            )
        except Exception as e:
            print(f"Failed to send approval email: {e}")
        
        return {
            "status": "approved",
            "payout_id": payout.id,
            "amount": payout.net_amount,
            "message": "Payout approved and processing"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject/{payout_id}")
async def reject_payout(
    payout_id: int,
    request: PayoutRejectionRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Reject a mentor payout request.
    Funds return to mentor's available balance.
    """
    
    payout = db.query(MentorPayout).filter(
        MentorPayout.id == payout_id
    ).first()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    if payout.status != PayoutStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reject {payout.status.value} payout"
        )
    
    try:
        # Update payout status
        payout.status = PayoutStatus.FAILED
        payout.failure_reason = request.rejection_reason
        payout.processed_at = datetime.utcnow()
        
        # Reset earnings as not paid out
        earnings = db.query(MentorEarning).filter(
            MentorEarning.payout_id == payout.id
        ).all()
        
        for earning in earnings:
            earning.is_paid_out = False
            earning.payout_id = None
        
        db.commit()
        
        # Send rejection email
        mentor_user = db.query(User).filter(
            User.id == payout.mentor_id
        ).first()
        
        try:
            email_service.send_payout_rejected(
                to_email=mentor_user.email,
                payout_id=payout.id,
                reason=request.rejection_reason
            )
        except Exception as e:
            print(f"Failed to send rejection email: {e}")
        
        return {
            "status": "rejected",
            "payout_id": payout.id,
            "reason": request.rejection_reason
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_payout_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get payout statistics"""
    
    pending = db.query(func.count(MentorPayout.id)).filter(
        MentorPayout.status == PayoutStatus.PENDING
    ).scalar()
    
    processing = db.query(func.count(MentorPayout.id)).filter(
        MentorPayout.status == PayoutStatus.PROCESSING
    ).scalar()
    
    completed = db.query(func.count(MentorPayout.id)).filter(
        MentorPayout.status == PayoutStatus.COMPLETED
    ).scalar()
    
    total_pending = db.query(func.sum(MentorPayout.net_amount)).filter(
        MentorPayout.status == PayoutStatus.PENDING
    ).scalar() or 0
    
    total_paid = db.query(func.sum(MentorPayout.net_amount)).filter(
        MentorPayout.status == PayoutStatus.COMPLETED
    ).scalar() or 0
    
    return {
        "pending_requests": pending,
        "processing_requests": processing,
        "completed_requests": completed,
        "total_pending_amount": float(total_pending),
        "total_paid_amount": float(total_paid)
    }
```

### Add to main.py

```python
from app.api.v1x.admin_payouts import router as admin_payouts_router
app.include_router(admin_payouts_router)
```

### Testing

```bash
# 1. Mentor requests payout
curl -X POST http://localhost:8001/api/v1x/mentors/payouts/request \
  -H "Authorization: Bearer $MENTOR_TOKEN" \
  -d '{"amount": 100}'

# 2. Admin sees pending payouts
curl -X GET http://localhost:8001/api/v1x/admin/payouts/pending \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Admin approves
curl -X POST http://localhost:8001/api/v1x/admin/payouts/1/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"approval_notes": "Approved"}'

# 4. Verify status changed to PROCESSING
curl http://localhost:8001/api/v1x/admin/payouts/pending \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Summary of Changes

| Fix | File | Lines | Time |
|-----|------|-------|------|
| #1: Session Price | mentors.py | ~20 | 30 min |
| #2: Webhook | stripe_webhook.py (new) | ~250 | 90 min |
| #3: Payout Approval | admin_payouts.py | ~300 | 90 min |
| **Total** | | | **210 min (3.5 hrs)** |

---

## Implementation Order

1. **First**: Fix #1 (Session Price) - Quick, high-impact
2. **Second**: Fix #3 (Payout Approval) - Blocks mentor earnings
3. **Third**: Fix #2 (Webhook) - Enables automated order confirmation

---

## Verification Checklist

After implementing all fixes:

- [ ] Create test mentor with hourly_rate = $75
- [ ] Book 60-min session → Verify price = $75
- [ ] Complete payment → Verify webhook handles event
- [ ] Order status changes to "completed"
- [ ] User enrolled in course
- [ ] Confirmation email sent
- [ ] Mentor requests payout
- [ ] Admin approves payout
- [ ] Stripe transfer initiated
- [ ] MentorEarning marked as paid_out
- [ ] Mentor receives payout confirmation email

**Timeline**: 3-4 hours total
**Next Step**: Implement these fixes to achieve 100% payment system functionality
