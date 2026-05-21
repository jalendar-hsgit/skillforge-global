"""
Stripe webhook handlers for real-time payment processing.
Handles payment intent events and updates session status accordingly.
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db, SessionLocal
from app.modelsx.mentor import MentorSession
from app.models.user import User
import stripe
import os
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Get Stripe secret key from environment
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


@router.post("/stripe/payment-intent")
async def handle_stripe_payment_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events for payment intent status changes.
    
    Events handled:
    - payment_intent.succeeded → Update session payment_status to 'paid'
    - payment_intent.payment_failed → Update session payment_status to 'failed'
    - payment_intent.canceled → Update session payment_status to 'cancelled'
    
    Webhook events from Stripe include:
    {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_1234567890",
                "status": "succeeded",
                "amount": 7500,  // in cents
                "currency": "usd",
                "metadata": {
                    "session_id": "32",
                    "student_id": "3",
                    "mentor_id": "1"
                }
            }
        }
    }
    """
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Handle payment intent events
    if event["type"] == "payment_intent.succeeded":
        await handle_payment_succeeded(event["data"]["object"], db)
    
    elif event["type"] == "payment_intent.payment_failed":
        await handle_payment_failed(event["data"]["object"], db)
    
    elif event["type"] == "payment_intent.canceled":
        await handle_payment_cancelled(event["data"]["object"], db)
    
    elif event["type"] == "charge.refunded":
        await handle_payment_refunded(event["data"]["object"], db)
    
    return {"received": True}


async def handle_payment_succeeded(payment_intent: dict, db: Session):
    """
    Update session to 'paid' status when payment succeeds.
    """
    metadata = payment_intent.get("metadata", {})
    session_id = metadata.get("session_id")
    
    if not session_id:
        print(f"⚠️  Warning: No session_id in payment intent metadata")
        return
    
    try:
        session = db.query(MentorSession).filter(MentorSession.id == int(session_id)).first()
        
        if not session:
            print(f"⚠️  Session {session_id} not found")
            return
        
        # Update payment status
        old_status = session.payment_status
        session.payment_status = "paid"
        session.payment_intent_id = payment_intent.get("id")
        
        db.commit()
        
        print(f"✅ Session {session_id}: Payment succeeded")
        print(f"   Amount: ${payment_intent.get('amount', 0) / 100:.2f}")
        print(f"   Status changed: {old_status} → paid")
        
        # Send payment confirmation email
        try:
            student = db.query(User).filter(User.id == session.student_id).first()
            if student and student.email:
                print(f"📧 Would send confirmation email to {student.email}")
                # email_service.send_payment_confirmation(student.email, session)
        except Exception as e:
            print(f"⚠️  Error sending email: {e}")
    
    except Exception as e:
        print(f"❌ Error processing payment success for session {session_id}: {e}")


async def handle_payment_failed(payment_intent: dict, db: Session):
    """
    Update session to 'failed' status when payment fails.
    """
    metadata = payment_intent.get("metadata", {})
    session_id = metadata.get("session_id")
    
    if not session_id:
        print(f"⚠️  Warning: No session_id in payment intent metadata")
        return
    
    try:
        session = db.query(MentorSession).filter(MentorSession.id == int(session_id)).first()
        
        if not session:
            print(f"⚠️  Session {session_id} not found")
            return
        
        # Update payment status
        old_status = session.payment_status
        session.payment_status = "failed"
        session.payment_intent_id = payment_intent.get("id")
        
        # Keep session but mark payment as failed
        db.commit()
        
        print(f"❌ Session {session_id}: Payment failed")
        print(f"   Error: {payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')}")
        print(f"   Status changed: {old_status} → failed")
        
        # Send payment failure email
        try:
            student = db.query(User).filter(User.id == session.student_id).first()
            if student and student.email:
                print(f"📧 Would send failure email to {student.email}")
                # email_service.send_payment_failed(student.email, session)
        except Exception as e:
            print(f"⚠️  Error sending email: {e}")
    
    except Exception as e:
        print(f"❌ Error processing payment failure for session {session_id}: {e}")


async def handle_payment_cancelled(payment_intent: dict, db: Session):
    """
    Update session when payment intent is cancelled.
    """
    metadata = payment_intent.get("metadata", {})
    session_id = metadata.get("session_id")
    
    if not session_id:
        print(f"⚠️  Warning: No session_id in payment intent metadata")
        return
    
    try:
        session = db.query(MentorSession).filter(MentorSession.id == int(session_id)).first()
        
        if not session:
            print(f"⚠️  Session {session_id} not found")
            return
        
        # Update payment status
        session.payment_status = "cancelled"
        db.commit()
        
        print(f"⚠️  Session {session_id}: Payment cancelled")
    
    except Exception as e:
        print(f"❌ Error processing payment cancellation for session {session_id}: {e}")


async def handle_payment_refunded(payment_intent: dict, db: Session):
    """
    Update session when payment is refunded.
    """
    metadata = payment_intent.get("metadata", {})
    session_id = metadata.get("session_id")
    
    if not session_id:
        print(f"⚠️  Warning: No session_id in payment metadata")
        return
    
    try:
        session = db.query(MentorSession).filter(MentorSession.id == int(session_id)).first()
        
        if not session:
            print(f"⚠️  Session {session_id} not found")
            return
        
        # Update payment status
        session.payment_status = "refunded"
        db.commit()
        
        print(f"🔄 Session {session_id}: Payment refunded")
        print(f"   Amount: ${payment_intent.get('amount_refunded', 0) / 100:.2f}")
        
        # Send refund confirmation email
        try:
            student = db.query(User).filter(User.id == session.student_id).first()
            if student and student.email:
                print(f"📧 Would send refund email to {student.email}")
        except Exception as e:
            print(f"⚠️  Error sending email: {e}")
    
    except Exception as e:
        print(f"❌ Error processing refund for session {session_id}: {e}")


# ============ Real-time Payment Status Endpoints ============

from app.schemas.mentor import SessionResponse

@router.get("/sessions/{session_id}/payment-status")
def get_payment_status(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get real-time payment status for a session.
    
    Returns:
    {
        "session_id": 32,
        "payment_status": "paid",  // pending, paid, failed, refunded, free
        "payment_intent_id": "pi_1234567890",
        "amount_paid": 75.00,
        "currency": "usd",
        "last_updated": "2026-01-26T18:30:00Z",
        "is_confirmed": true
    }
    """
    session = db.query(MentorSession).filter(MentorSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {
        "session_id": session.id,
        "payment_status": session.payment_status,
        "payment_intent_id": session.payment_intent_id or None,
        "amount_paid": session.price,
        "currency": "usd",
        "last_updated": session.created_at,
        "is_confirmed": session.status == "confirmed"
    }
