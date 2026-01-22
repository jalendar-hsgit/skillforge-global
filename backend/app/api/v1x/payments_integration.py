"""
Payment Integration Endpoints
Handle payment processing, refunds, and webhooks
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.order import Order
from app.services.payment_processor import (
    PaymentRequest, PaymentResponse, PaymentStatus,
    get_payment_processor, PaymentProvider
)

router = APIRouter(prefix="/payments", tags=["payments"])


class ProcessPaymentRequest(BaseModel):
    """Request to process a payment"""
    order_id: int
    payment_method: str  # stripe, paypal
    token: Optional[str] = None  # Payment token from frontend


class RefundRequest(BaseModel):
    """Request to refund a payment"""
    order_id: int
    amount: Optional[float] = None
    reason: str = "Customer request"


class PaymentStatusRequest(BaseModel):
    """Request to check payment status"""
    order_id: int


@router.post("/process")
def process_payment(
    request_data: ProcessPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process a payment for an order.
    
    Request Body:
        {
            "order_id": 123,
            "payment_method": "stripe",
            "token": "tok_..." (optional, for card payments)
        }
    
    Returns:
        - payment_id: Unique payment transaction ID
        - status: Payment status (completed, failed, pending)
        - amount: Payment amount
        - message: Human readable status message
    """
    
    # Get order
    order = db.query(Order).filter(Order.id == request_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to user
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to process this payment")
    
    # Check order is in pending state
    if order.payment_status and order.payment_status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Order already has payment status: {order.payment_status}"
        )
    
    try:
        # Get payment processor
        processor = get_payment_processor(
            provider=request_data.payment_method.lower()
        )
        
        # Create payment request
        payment_request = PaymentRequest(
            order_id=order.id,
            amount=float(order.amount),
            currency=order.currency or "USD",
            payment_method=request_data.payment_method,
            customer_email=current_user.email,
            description=f"Order {order.order_number}"
        )
        
        # Process payment
        payment_response = processor.process_payment(payment_request)
        
        # Update order with payment info
        order.payment_id = payment_response.payment_id
        order.payment_status = "completed" if payment_response.status == PaymentStatus.COMPLETED else "failed"
        order.status = "completed" if payment_response.status == PaymentStatus.COMPLETED else "failed"
        order.paid_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": payment_response.status == PaymentStatus.COMPLETED,
            "payment_id": payment_response.payment_id,
            "order_id": order.id,
            "order_number": order.order_number,
            "amount": payment_response.amount,
            "currency": payment_response.currency,
            "status": str(payment_response.status),
            "provider": str(payment_response.provider),
            "message": "Payment processed successfully" if payment_response.status == PaymentStatus.COMPLETED else "Payment failed"
        }
    
    except Exception as e:
        # Update order with failure
        order.payment_status = "failed"
        order.status = "failed"
        db.commit()
        
        raise HTTPException(status_code=400, detail=f"Payment processing failed: {str(e)}")


@router.post("/refund")
def refund_payment(
    request_data: RefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Request a refund for an order.
    
    Request Body:
        {
            "order_id": 123,
            "amount": 50.00 (optional, for partial refunds),
            "reason": "Defective product"
        }
    
    Returns:
        - success: Whether refund was processed
        - refund_id: Refund transaction ID
        - amount: Refund amount
        - status: Refund status
    """
    
    # Get order
    order = db.query(Order).filter(Order.id == request_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check user is order owner or admin
    is_owner = order.user_id == current_user.id
    is_admin = hasattr(current_user, 'role') and str(current_user.role) in ['admin', 'superadmin']
    
    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to refund this order")
    
    # Check order has payment
    if not order.payment_id:
        raise HTTPException(status_code=400, detail="Order has no payment to refund")
    
    try:
        # Get payment processor
        processor = get_payment_processor(order.payment_method.lower())
        
        # Determine refund amount
        refund_amount = request_data.amount or float(order.amount)
        
        # Verify refund amount is valid
        if refund_amount > float(order.amount):
            raise ValueError("Refund amount exceeds order total")
        
        # Process refund
        refund_response = processor.refund_payment(order.payment_id, refund_amount)
        
        # Update order
        order.status = "refunded"
        order.payment_status = "refunded"
        db.commit()
        
        return {
            "success": True,
            "refund_id": refund_response.payment_id,
            "order_id": order.id,
            "order_number": order.order_number,
            "refund_amount": refund_amount,
            "original_amount": float(order.amount),
            "reason": request_data.reason,
            "status": str(refund_response.status),
            "message": "Refund processed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Refund processing failed: {str(e)}")


@router.get("/status/{order_id}")
def get_payment_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get payment status for an order.
    
    Returns:
        - order_id: Order ID
        - payment_id: Payment transaction ID
        - status: Payment status
        - amount: Payment amount
        - provider: Payment provider used
    """
    
    # Get order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "payment_id": order.payment_id,
        "status": order.payment_status or "pending",
        "amount": float(order.amount),
        "currency": order.currency or "USD",
        "provider": order.payment_method,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "order_status": order.status
    }


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint for payment events.
    
    Handles:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - charge.refunded
    """
    
    # TODO: Implement Stripe webhook signature verification
    # In production, verify webhook signature:
    # endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    # sig_header = request.headers.get("stripe-signature")
    # Verify signature before processing
    
    payload = await request.json()
    event_type = payload.get("type")
    event_data = payload.get("data", {}).get("object", {})
    
    # Log webhook event
    print(f"Stripe webhook received: {event_type}")
    
    # TODO: Process webhook events
    # Examples:
    # - Update order payment status
    # - Trigger notifications
    # - Update analytics
    
    return {"received": True}


@router.post("/webhook/paypal")
async def paypal_webhook(request: Request):
    """
    PayPal webhook endpoint for payment events.
    
    Handles:
    - PAYMENT.CAPTURE.COMPLETED
    - PAYMENT.CAPTURE.DENIED
    - BILLING.SUBSCRIPTION.CREATED
    """
    
    # TODO: Implement PayPal webhook verification
    # In production, verify webhook signature
    
    payload = await request.json()
    event_type = payload.get("event_type")
    
    # Log webhook event
    print(f"PayPal webhook received: {event_type}")
    
    # TODO: Process webhook events
    
    return {"received": True}
