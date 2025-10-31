"""
Payment API endpoints for mentor sessions
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.mentor import MentorSession
from app.services.stripe_service import stripe_service

router = APIRouter(prefix="/payments", tags=["payments"])


class CreatePaymentIntentRequest(BaseModel):
    session_id: int


class CreatePaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str


@router.post("/create-payment-intent", response_model=CreatePaymentIntentResponse)
def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe PaymentIntent for a mentor session
    """
    # Get session
    session = db.query(MentorSession).filter(
        MentorSession.id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify user is the student
    if session.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if session is pending
    if session.status != "pending":
        raise HTTPException(status_code=400, detail="Session must be in pending status")
    
    # Calculate amount
    from app.modelsx.mentor import Mentor
    mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    amount = (mentor.hourly_rate * session.duration_minutes) / 60
    
    try:
        # Create payment intent
        payment_info = stripe_service.create_payment_intent(
            amount=amount,
            session_id=session.id,
            mentor_id=session.mentor_id,
            student_id=current_user.id
        )
        
        # Store payment intent ID in session
        session.payment_intent_id = payment_info['id']
        db.commit()
        
        return CreatePaymentIntentResponse(
            client_secret=payment_info['client_secret'],
            payment_intent_id=payment_info['id'],
            amount=payment_info['amount'],
            currency=payment_info['currency']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capture-payment/{session_id}")
def capture_payment(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Capture payment after session is completed (mentor only)
    """
    session = db.query(MentorSession).filter(
        MentorSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify user is the mentor
    from app.modelsx.mentor import Mentor
    mentor = db.query(Mentor).filter(
        Mentor.user_id == current_user.id
    ).first()
    
    if not mentor or session.mentor_id != mentor.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check session is completed
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Session must be completed")
    
    if not session.payment_intent_id:
        raise HTTPException(status_code=400, detail="No payment to capture")
    
    try:
        success = stripe_service.capture_payment(session.payment_intent_id)
        
        if success:
            session.payment_status = "captured"
            db.commit()
            return {"success": True, "message": "Payment captured"}
        else:
            raise HTTPException(status_code=500, detail="Failed to capture payment")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-payment/{session_id}")
def cancel_payment(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel payment when session is cancelled
    """
    session = db.query(MentorSession).filter(
        MentorSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify user is student or mentor
    from app.modelsx.mentor import Mentor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    is_mentor = mentor and session.mentor_id == mentor.id
    is_student = session.student_id == current_user.id
    
    if not (is_mentor or is_student):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not session.payment_intent_id:
        return {"success": True, "message": "No payment to cancel"}
    
    try:
        success = stripe_service.cancel_payment(session.payment_intent_id)
        
        if success:
            session.payment_status = "canceled"
            db.commit()
            return {"success": True, "message": "Payment cancelled"}
        else:
            raise HTTPException(status_code=500, detail="Failed to cancel payment")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    try:
        payload = await request.body()
        event = stripe_service.verify_webhook_signature(payload, stripe_signature)
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            # Payment confirmed
            payment_intent = event['data']['object']
            session_id = payment_intent['metadata'].get('session_id')
            
            if session_id:
                db = next(get_db())
                session = db.query(MentorSession).filter(
                    MentorSession.id == int(session_id)
                ).first()
                
                if session:
                    session.payment_status = "succeeded"
                    db.commit()
        
        elif event['type'] == 'payment_intent.payment_failed':
            # Payment failed
            payment_intent = event['data']['object']
            session_id = payment_intent['metadata'].get('session_id')
            
            if session_id:
                db = next(get_db())
                session = db.query(MentorSession).filter(
                    MentorSession.id == int(session_id)
                ).first()
                
                if session:
                    session.payment_status = "failed"
                    db.commit()
        
        return {"success": True}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{session_id}")
def get_payment_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment status for a session
    """
    session = db.query(MentorSession).filter(
        MentorSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify user is student or mentor
    from app.modelsx.mentor import Mentor
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    is_mentor = mentor and session.mentor_id == mentor.id
    is_student = session.student_id == current_user.id
    
    if not (is_mentor or is_student):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not session.payment_intent_id:
        return {"status": "no_payment"}
    
    try:
        status = stripe_service.get_payment_status(session.payment_intent_id)
        return status
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
