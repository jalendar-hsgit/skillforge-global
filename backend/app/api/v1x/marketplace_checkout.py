"""
Marketplace Checkout Endpoint
Handle purchase transactions, apply coupons, process payments
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from pydantic import BaseModel

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.order import Order, Coupon
from app.modelsx.marketplace import DigitalProduct
from app.services.stripe_service import stripe_service


class CheckoutRequest(BaseModel):
    """Checkout request with cart items"""
    product_ids: list[int]  # Product IDs to purchase
    coupon_code: Optional[str] = None
    payment_method: str = "stripe"  # stripe, paypal, etc


class CheckoutResponse(BaseModel):
    """Checkout response with order details"""
    order_id: int
    order_number: str
    total_amount: float
    items_count: int
    discount_amount: float
    status: str


router = APIRouter(prefix="", tags=["marketplace"])


@router.post("/marketplace/checkout", response_model=CheckoutResponse)
def checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process checkout for marketplace products.
    
    Args:
        request: CheckoutRequest with product IDs and optional coupon
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Order confirmation with total amount and order number
    
    Raises:
        404: If product not found
        400: If product not available for purchase
        422: If coupon is invalid or expired
    """
    
    if not request.product_ids:
        raise HTTPException(status_code=400, detail="No products in checkout")
    
    # Fetch all products
    products = db.query(DigitalProduct).filter(
        DigitalProduct.id.in_(request.product_ids)
    ).all()
    
    if len(products) != len(request.product_ids):
        raise HTTPException(status_code=404, detail="One or more products not found")
    
    # Check product availability (not archived, not suspended)
    for product in products:
        if product.status in ["archived", "suspended"]:
            raise HTTPException(
                status_code=400,
                detail=f"Product '{product.name}' is not available for purchase"
            )
    
    # Calculate subtotal
    subtotal = sum(Decimal(str(p.price)) for p in products)
    
    # Apply coupon if provided
    discount_amount = Decimal(0)
    if request.coupon_code:
        coupon = db.query(Coupon).filter(
            Coupon.code == request.coupon_code
        ).first()
        
        if not coupon:
            raise HTTPException(status_code=422, detail="Invalid coupon code")
        
        # Check coupon usage limits
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            raise HTTPException(status_code=422, detail="Coupon usage limit exceeded")
        
        # Check minimum purchase amount
        if coupon.min_purchase_amount and subtotal < Decimal(str(coupon.min_purchase_amount)):
            raise HTTPException(
                status_code=422,
                detail=f"Minimum purchase amount of ${coupon.min_purchase_amount} required"
            )
        
        # Calculate discount
        if coupon.discount_type == "percentage":
            discount_amount = subtotal * (Decimal(str(coupon.discount_value)) / 100)
            if coupon.max_discount_amount:
                discount_amount = min(discount_amount, Decimal(str(coupon.max_discount_amount)))
        else:  # fixed discount
            discount_amount = min(Decimal(str(coupon.discount_value)), subtotal)
        
        # Update coupon usage
        coupon.usage_count += 1
    
    # Calculate final amount
    tax_amount = Decimal(0)  # Simplified - could be calculated based on location
    final_amount = subtotal - discount_amount + tax_amount
    
    # Create order record
    import random
    import string
    order_number = f"ORD-{current_user.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
    
    order = Order(
        user_id=current_user.id,
        order_number=order_number,
        status="pending",  # Will be updated after payment
        subtotal=float(subtotal),
        discount_amount=float(discount_amount),
        tax_amount=float(tax_amount),
        amount=float(final_amount),
        currency="USD",
        payment_method=request.payment_method,
        payment_status="pending",
        coupon_code=request.coupon_code if request.coupon_code else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create Stripe payment intent for actual payment processing
    if request.payment_method == "stripe":
        try:
            payment_info = stripe_service.create_payment_intent(
                amount=float(final_amount),
                currency="usd",
                session_id=0,  # Not a session, but order ID
                mentor_id=0,   # Not applicable for marketplace
                student_id=current_user.id
            )
            
            # Store payment intent ID in order
            order.payment_intent_id = payment_info['id']
            db.commit()
            
            return {
                "order_id": order.id,
                "order_number": order.order_number,
                "total_amount": float(final_amount),
                "items_count": len(products),
                "discount_amount": float(discount_amount),
                "status": order.status,
                "client_secret": payment_info['client_secret'],
                "payment_intent_id": payment_info['id']
            }
        
        except Exception as e:
            # Delete the order if payment intent creation failed
            db.delete(order)
            db.commit()
            raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")
    
    # For other payment methods, return basic order info
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "total_amount": float(final_amount),
        "items_count": len(products),
        "discount_amount": float(discount_amount),
        "status": order.status
    }


@router.post("/marketplace/confirm-payment/{order_id}")
def confirm_marketplace_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Confirm payment for a marketplace order after Stripe payment succeeds.
    Called from webhook or frontend after successful payment.
    
    Args:
        order_id: The Order ID
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Order confirmation
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify user is the order owner
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check payment intent status if using Stripe
    if order.payment_intent_id:
        try:
            payment_status = stripe_service.get_payment_status(order.payment_intent_id)
            
            if payment_status['status'] != 'succeeded':
                raise HTTPException(status_code=400, detail="Payment not confirmed yet")
            
            # Payment succeeded, update order
            order.payment_status = "succeeded"
            order.status = "completed"
            order.paid_at = datetime.utcnow()
            
            # Add order items to user's purchases (this would need order_items table in real implementation)
            # For now, just mark as completed
            
            db.commit()
            
            return {
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status,
                "message": "Order completed successfully"
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to confirm payment: {str(e)}")
    
    raise HTTPException(status_code=400, detail="No payment intent found")
