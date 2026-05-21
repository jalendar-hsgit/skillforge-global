from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal
import uuid

from app.core.db import get_db
from app.core.security import get_current_user
from app.core.responses import StandardResponse
from app.models.user import User
from app.modelsx.order import Order, CartItem
from app.modelsx.course import Course
from app.services.stripe_service import StripeService
from app.services.email_service import email_service
from app.services.realtime_events import on_course_enrolled

router = APIRouter(prefix="/orders", tags=["orders"])


# Request/Response Models
class CreateOrderRequest(BaseModel):
    course_id: int
    payment_method: str = "stripe"


class CreatePaymentIntentRequest(BaseModel):
    order_id: int
    amount: float = None


class ConfirmPaymentRequest(BaseModel):
    order_id: int
    payment_intent_id: str


class OrderResponse(BaseModel):
    id: int
    order_number: str
    course_id: int
    amount: float
    status: str
    payment_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# ORDER ENDPOINTS
# ============================================================

@router.post("/create", response_model=StandardResponse)
async def create_order(
    request: CreateOrderRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new order for a course
    
    Returns order details with client_secret for payment
    """
    try:
        # Get course
        course = db.query(Course).filter(Course.id == request.course_id).first()
        if not course:
            raise HTTPException(
                status_code=404,
                detail="Course not found"
            )
        
        if not course.is_paid:
            raise HTTPException(
                status_code=400,
                detail="This course is not for sale"
            )
        
        # Check if user already owns course
        existing = db.query(Order).filter(
            and_(
                Order.user_id == user.id,
                Order.course_id == course.id,
                Order.status == "completed"
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="You already own this course"
            )
        
        # Create order
        amount = float(course.price or 0)
        order_number = f"ORD-{user.id}-{course.id}-{uuid.uuid4().hex[:8]}"
        
        order = Order(
            user_id=user.id,
            course_id=course.id,
            order_number=order_number,
            subtotal=Decimal(str(amount)),
            amount=Decimal(str(amount)),
            currency="USD",
            payment_method=request.payment_method,
            status="pending",
            payment_status="pending"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return StandardResponse(
            success=True,
            data={
                "id": order.id,
                "order_number": order.order_number,
                "course_id": order.course_id,
                "amount": float(order.amount),
                "currency": order.currency,
                "status": order.status,
                "payment_status": order.payment_status
            },
            message="Order created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating order: {str(e)}"
        )


@router.post("/create-payment-intent", response_model=StandardResponse)
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create Stripe PaymentIntent for an order
    
    Frontend will use client_secret to complete payment
    """
    try:
        # Get order
        order = db.query(Order).filter(Order.id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Verify ownership
        if order.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get course details
        course = db.query(Course).filter(Course.id == order.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Create Stripe payment intent
        amount = float(order.amount)
        payment_intent = StripeService.create_payment_intent(
            amount=amount,
            currency=order.currency.lower(),
            session_id=order.id,
            mentor_id=None,
            student_id=user.id
        )
        
        # Store payment intent ID
        order.payment_id = payment_intent['id']
        db.commit()
        db.refresh(order)
        
        return StandardResponse(
            success=True,
            data={
                "client_secret": payment_intent['client_secret'],
                "payment_intent_id": payment_intent['id'],
                "amount": amount,
                "currency": order.currency,
                "order_id": order.id
            },
            message="Payment intent created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create payment intent: {str(e)}"
        )


@router.post("/confirm-payment", response_model=StandardResponse)
async def confirm_payment(
    request: ConfirmPaymentRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Confirm payment and grant course access
    
    Called after Stripe payment succeeds
    """
    try:
        # Get order
        order = db.query(Order).filter(Order.id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Verify ownership
        if order.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Verify payment intent matches
        if order.payment_id != request.payment_intent_id:
            raise HTTPException(
                status_code=400,
                detail="Payment intent does not match order"
            )
        
        # Retrieve payment intent from Stripe to verify
        try:
            intent = StripeService.retrieve_payment_intent(request.payment_intent_id)
            if intent['status'] != 'succeeded':
                raise HTTPException(
                    status_code=400,
                    detail=f"Payment not successful. Status: {intent['status']}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to verify payment: {str(e)}"
            )
        
        # Update order
        order.status = "completed"
        order.payment_status = "completed"
        order.paid_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
        
        # Get course
        course = db.query(Course).filter(Course.id == order.course_id).first()
        
        # Grant course access via enrollment event
        try:
            await on_course_enrolled(
                user.id,
                course.id,
                course.title,
                course_path=course.path,
            )
        except Exception as e:
            print(f"Warning: Failed to trigger course enrollment event: {e}")
        
        # Send confirmation email
        try:
            await email_service.send_payment_receipt(
                email=user.email,
                user_name=user.name,
                amount=float(order.amount),
                course_name=course.title,
                order_number=order.order_number
            )
        except Exception as e:
            print(f"Warning: Failed to send confirmation email: {e}")
        
        return StandardResponse(
            success=True,
            data={
                "order_id": order.id,
                "status": order.status,
                "payment_status": order.payment_status,
                "access_granted": True
            },
            message="Payment confirmed! Course access granted."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error confirming payment: {str(e)}"
        )


@router.get("/my-orders", response_model=StandardResponse)
async def get_my_orders(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all orders for current user"""
    try:
        orders = db.query(Order).filter(
            Order.user_id == user.id
        ).order_by(
            Order.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        total = db.query(Order).filter(Order.user_id == user.id).count()
        
        return StandardResponse(
            success=True,
            data={
                "orders": [
                    {
                        "id": o.id,
                        "order_number": o.order_number,
                        "course_id": o.course_id,
                        "amount": float(o.amount),
                        "currency": o.currency,
                        "status": o.status,
                        "payment_status": o.payment_status,
                        "created_at": o.created_at.isoformat() if o.created_at else None
                    }
                    for o in orders
                ],
                "total": total,
                "skip": skip,
                "limit": limit
            },
            message="Orders retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving orders: {str(e)}"
        )


@router.get("/{order_id}", response_model=StandardResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get order details"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check authorization
        if order.user_id != user.id and user.role not in ["ADMIN", "SUPERADMIN"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return StandardResponse(
            success=True,
            data={
                "id": order.id,
                "order_number": order.order_number,
                "course_id": order.course_id,
                "amount": float(order.amount),
                "currency": order.currency,
                "status": order.status,
                "payment_status": order.payment_status,
                "payment_method": order.payment_method,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None
            },
            message="Order retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving order: {str(e)}"
        )
