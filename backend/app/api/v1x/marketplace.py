"""
Course marketplace API endpoints for browsing, cart, and purchasing.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import List, Optional
from datetime import datetime
import secrets

from app.core.db import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from app.modelsx.course import Course
from app.modelsx.order import Order, CartItem, Coupon
from app.modelsx.video import Video
from pydantic import BaseModel, Field
from decimal import Decimal


router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


# ===== Schemas =====

class CourseListItem(BaseModel):
    id: int
    path: str
    title: str
    description: Optional[str]
    category: Optional[str]
    is_paid: bool
    price: Optional[float]
    video_count: int = 0
    is_purchased: bool = False
    rating: Optional[float] = None
    
    class Config:
        from_attributes = True


class CourseDetail(CourseListItem):
    created_at: datetime
    videos: List[dict] = []


class CartItemResponse(BaseModel):
    id: int
    course_id: int
    course_title: str
    course_path: str
    price: float
    added_at: datetime
    
    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    items: List[CartItemResponse]
    subtotal: float
    discount: float = 0
    tax: float = 0
    total: float
    coupon_code: Optional[str] = None


class AddToCartRequest(BaseModel):
    course_id: int


class ApplyCouponRequest(BaseModel):
    coupon_code: str


class CheckoutRequest(BaseModel):
    payment_method: str = Field(..., description="stripe, paypal, or coins")
    coupon_code: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    amount: float
    currency: str
    payment_method: Optional[str]
    payment_status: Optional[str]
    created_at: datetime
    course_title: Optional[str] = None
    
    class Config:
        from_attributes = True


# ===== Endpoints =====

@router.get("/courses", response_model=List[CourseListItem])
async def browse_courses(
    category: Optional[str] = None,
    search: Optional[str] = None,
    free_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Browse all available courses with filters. Public endpoint (auth optional).
    """
    query = db.query(Course)
    
    # Apply filters
    if category:
        query = query.filter(Course.category == category)
    
    if search:
        query = query.filter(
            or_(
                Course.title.ilike(f"%{search}%"),
                Course.description.ilike(f"%{search}%")
            )
        )
    
    if free_only:
        query = query.filter(Course.is_paid == False)
    
    courses = query.order_by(desc(Course.created_at)).offset(skip).limit(limit).all()
    
    # Get purchased course IDs for current user
    purchased_ids = set()
    if current_user:
        purchased_ids = {
            order.course_id for order in db.query(Order).filter(
                and_(
                    Order.user_id == current_user.id,
                    Order.status == "completed"
                )
            ).all()
        }
    
    # Format response
    result = []
    for course in courses:
        video_count = db.query(func.count(Video.id)).filter(Video.course_id == course.id).scalar()
        result.append(CourseListItem(
            id=course.id,
            path=course.path,
            title=course.title,
            description=course.description,
            category=course.category,
            is_paid=course.is_paid,
            price=float(course.price) if course.price else None,
            video_count=video_count,
            is_purchased=course.id in purchased_ids
        ))
    
    return result


@router.get("/courses/{course_id}", response_model=CourseDetail)
async def get_course_detail(
    course_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific course. Public endpoint (auth optional).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if purchased
    is_purchased = False
    if current_user:
        is_purchased = db.query(Order).filter(
            and_(
                Order.user_id == current_user.id,
                Order.course_id == course_id,
                Order.status == "completed"
            )
        ).first() is not None
    
    # Get videos
    videos = db.query(Video).filter(Video.course_id == course_id).all()
    video_list = [{"id": v.id, "title": v.title, "duration": v.duration} for v in videos]
    
    return CourseDetail(
        id=course.id,
        path=course.path,
        title=course.title,
        description=course.description,
        category=course.category,
        is_paid=course.is_paid,
        price=float(course.price) if course.price else None,
        video_count=len(videos),
        is_purchased=is_purchased,
        created_at=course.created_at,
        videos=video_list
    )


@router.get("/cart", response_model=CartSummary)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's shopping cart.
    """
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    items = []
    subtotal = 0
    
    for item in cart_items:
        course = db.query(Course).filter(Course.id == item.course_id).first()
        if course:
            items.append(CartItemResponse(
                id=item.id,
                course_id=course.id,
                course_title=course.title,
                course_path=course.path,
                price=float(item.price),
                added_at=item.added_at
            ))
            subtotal += float(item.price)
    
    return CartSummary(
        items=items,
        subtotal=subtotal,
        total=subtotal
    )


@router.post("/cart/add")
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a course to the shopping cart.
    """
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if not course.is_paid:
        raise HTTPException(status_code=400, detail="Free courses cannot be added to cart")
    
    # Check if already purchased
    existing_order = db.query(Order).filter(
        and_(
            Order.user_id == current_user.id,
            Order.course_id == request.course_id,
            Order.status == "completed"
        )
    ).first()
    
    if existing_order:
        raise HTTPException(status_code=400, detail="Course already purchased")
    
    # Check if already in cart
    existing_item = db.query(CartItem).filter(
        and_(
            CartItem.user_id == current_user.id,
            CartItem.course_id == request.course_id
        )
    ).first()
    
    if existing_item:
        raise HTTPException(status_code=400, detail="Course already in cart")
    
    # Add to cart
    cart_item = CartItem(
        user_id=current_user.id,
        course_id=request.course_id,
        price=course.price
    )
    db.add(cart_item)
    db.commit()
    
    return {"message": "Course added to cart", "cart_item_id": cart_item.id}


@router.delete("/cart/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item from the shopping cart.
    """
    item = db.query(CartItem).filter(
        and_(
            CartItem.id == item_id,
            CartItem.user_id == current_user.id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item removed from cart"}


@router.post("/checkout", response_model=OrderResponse)
async def checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process checkout and create order.
    """
    # Get cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    subtotal = sum(float(item.price) for item in cart_items)
    discount_amount = 0
    
    # Apply coupon if provided
    if request.coupon_code:
        coupon = db.query(Coupon).filter(
            and_(
                Coupon.code == request.coupon_code,
                Coupon.is_active == True
            )
        ).first()
        
        if coupon:
            # Validate coupon
            if coupon.valid_from and coupon.valid_from > datetime.utcnow():
                raise HTTPException(status_code=400, detail="Coupon not yet valid")
            if coupon.valid_until and coupon.valid_until < datetime.utcnow():
                raise HTTPException(status_code=400, detail="Coupon expired")
            if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
                raise HTTPException(status_code=400, detail="Coupon usage limit reached")
            
            # Calculate discount
            if coupon.discount_type == "percentage":
                discount_amount = subtotal * (float(coupon.discount_value) / 100)
                if coupon.max_discount_amount:
                    discount_amount = min(discount_amount, float(coupon.max_discount_amount))
            else:  # fixed
                discount_amount = float(coupon.discount_value)
            
            discount_amount = min(discount_amount, subtotal)
    
    total = subtotal - discount_amount
    
    # Generate order number
    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
    
    # Create order (for single course for now - extend for multi-course later)
    course = db.query(Course).filter(Course.id == cart_items[0].course_id).first()
    
    order = Order(
        user_id=current_user.id,
        course_id=cart_items[0].course_id,
        order_number=order_number,
        status="pending",
        subtotal=Decimal(str(subtotal)),
        discount_amount=Decimal(str(discount_amount)),
        tax_amount=Decimal("0"),
        amount=Decimal(str(total)),
        currency="USD",
        payment_method=request.payment_method,
        payment_status="pending",
        coupon_code=request.coupon_code
    )
    
    db.add(order)
    
    # For demo purposes, mark as completed immediately
    # In production, integrate with Stripe/PayPal webhooks
    if request.payment_method == "coins":
        # TODO: Deduct coins from user balance
        order.status = "completed"
        order.payment_status = "completed"
        order.paid_at = datetime.utcnow()
    
    # Clear cart
    for item in cart_items:
        db.delete(item)
    
    # Update coupon usage
    if request.coupon_code:
        coupon.usage_count += 1
    
    db.commit()
    db.refresh(order)
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        status=order.status,
        subtotal=float(order.subtotal),
        discount_amount=float(order.discount_amount),
        tax_amount=float(order.tax_amount),
        amount=float(order.amount),
        currency=order.currency,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        created_at=order.created_at,
        course_title=course.title if course else None
    )


@router.get("/orders", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's order history.
    """
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(desc(Order.created_at)).all()
    
    result = []
    for order in orders:
        course = db.query(Course).filter(Course.id == order.course_id).first()
        result.append(OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            subtotal=float(order.subtotal),
            discount_amount=float(order.discount_amount),
            tax_amount=float(order.tax_amount),
            amount=float(order.amount),
            currency=order.currency,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            created_at=order.created_at,
            course_title=course.title if course else None
        ))
    
    return result


@router.post("/coupons/validate")
async def validate_coupon(
    request: ApplyCouponRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate a coupon code and return discount info.
    """
    coupon = db.query(Coupon).filter(
        and_(
            Coupon.code == request.coupon_code,
            Coupon.is_active == True
        )
    ).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    
    # Validate
    if coupon.valid_from and coupon.valid_from > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Coupon not yet valid")
    if coupon.valid_until and coupon.valid_until < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Coupon expired")
    if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    
    return {
        "code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": float(coupon.discount_value),
        "max_discount": float(coupon.max_discount_amount) if coupon.max_discount_amount else None,
        "valid": True
    }
