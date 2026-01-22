"""
Session wrapper that proxies requests to v1x endpoints with authentication
This provides the /api/session prefix that the frontend expects
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import List, Optional
from pydantic import BaseModel

from app.core.db import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from app.modelsx.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate, ResumeOut, ResumeListOut
from app.modelsx.course import Course
from app.modelsx.video import Video
from app.modelsx.order import Order, CartItem, Coupon
from app.modelsx.coins import CoinLedger
from datetime import datetime
from decimal import Decimal
import secrets


# ==================== Request/Response Schemas ====================

class AddToCartRequest(BaseModel):
    course_id: int

class ApplyCouponRequest(BaseModel):
    coupon_code: str

class CheckoutRequest(BaseModel):
    payment_method: str = "coins"
    coupon_code: Optional[str] = None

router = APIRouter(prefix="/session", tags=["session"])


# ==================== User Session ====================

@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


# ==================== Resume Session Routes ====================

@router.get("/resumes", response_model=List[ResumeListOut])
def list_user_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all user's resumes"""
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.updated_at.desc()).all()
    return resumes


@router.get("/resumes/{resume_id}", response_model=ResumeOut)
def get_user_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a user's resume by ID"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Increment view count
    resume.views = (resume.views or 0) + 1
    db.commit()
    
    return resume


@router.post("/resumes", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def create_user_resume(
    resume_data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new resume for the current user"""
    try:
        resume = Resume(
            user_id=current_user.id,
            **resume_data.dict()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create resume: {str(e)}"
        )


@router.patch("/resumes", response_model=ResumeOut)
@router.put("/resumes", response_model=ResumeOut)
def update_user_resume(
    resume_data: ResumeUpdate,
    id: int = Query(..., description="Resume ID to update"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a user's resume (supports both PATCH and PUT)"""
    resume = db.query(Resume).filter(
        Resume.id == id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    update_dict = resume_data.dict(exclude_unset=True)
    
    # Handle professional_summary alias
    if 'professional_summary' in update_dict and update_dict['professional_summary'] is not None:
        update_dict['summary'] = update_dict.pop('professional_summary')
    
    for key, value in update_dict.items():
        if hasattr(resume, key):
            setattr(resume, key, value)
    
    resume.version = (resume.version or 0) + 1
    db.commit()
    db.refresh(resume)
    
    return resume


@router.delete("/resumes")
def delete_user_resume(
    id: int = Query(..., description="Resume ID to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user's resume"""
    resume = db.query(Resume).filter(
        Resume.id == id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.delete(resume)
    db.commit()
    
    return {"ok": True}


# ==================== Marketplace Session Routes (Proxies) ====================

class CourseListItem:
    def __init__(self, id, path, title, description, category, is_paid, price, video_count, is_purchased, is_in_cart):
        self.id = id
        self.path = path
        self.title = title
        self.description = description
        self.category = category
        self.is_paid = is_paid
        self.price = price
        self.video_count = video_count
        self.is_purchased = is_purchased
        self.is_in_cart = is_in_cart


@router.get("/v1x/marketplace/courses")
def session_browse_courses(
    category: Optional[str] = None,
    search: Optional[str] = None,
    free_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Browse all available courses with filters"""
    try:
        query = db.query(Course)
        
        # Apply filters
        if category and category != 'All':
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
        cart_ids = set()
        if current_user:
            purchased_ids = {
                order.course_id for order in db.query(Order).filter(
                    and_(
                        Order.user_id == current_user.id,
                        Order.status == "completed"
                    )
                ).all()
            }
            
            # Also get cart items
            cart_ids = {
                item.course_id for item in db.query(CartItem).filter(
                    CartItem.user_id == current_user.id
                ).all()
            }
        
        # Format response
        result = []
        for course in courses:
            video_count = db.query(func.count(Video.id)).filter(Video.course_id == course.id).scalar() or 0
            result.append({
                "id": course.id,
                "path": course.path,
                "title": course.title,
                "description": course.description,
                "category": course.category,
                "is_paid": course.is_paid,
                "price": float(course.price) if course.price else None,
                "video_count": video_count,
                "is_purchased": course.id in purchased_ids,
                "is_in_cart": course.id in cart_ids
            })
        
        return result
    except Exception as e:
        print(f"Error in session_browse_courses: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1x/marketplace/cart")
def session_get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's shopping cart"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    items = []
    subtotal = 0
    for item in cart_items:
        price = float(item.price) if item.price else 0
        items.append({
            "id": item.id,
            "course_id": item.course_id,
            "course_title": item.course.title if item.course else "Unknown",
            "course_path": item.course.path if item.course else "",
            "price": price,
            "added_at": item.added_at
        })
        subtotal += price
    
    return {
        "items": items,
        "subtotal": subtotal,
        "discount": 0,
        "tax": 0,
        "total": subtotal,
        "coupon_code": None
    }


@router.post("/v1x/marketplace/cart/add")
def session_add_to_cart(
    payload: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to shopping cart"""
    course_id = payload.course_id
    
    if not course_id:
        raise HTTPException(status_code=400, detail="course_id required")
    
    # Get course to validate and get price
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.course_id == course_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already in cart")
    
    # Add to cart
    cart_item = CartItem(
        user_id=current_user.id,
        course_id=course_id,
        price=course.price
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    
    return {
        "id": cart_item.id,
        "course_id": cart_item.course_id,
        "course_title": course.title,
        "price": float(cart_item.price) if cart_item.price else 0,
        "message": "Added to cart"
    }


@router.delete("/v1x/marketplace/cart/{item_id}")
def session_remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from shopping cart"""
    # Get the cart item
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Delete from cart
    db.delete(cart_item)
    db.commit()
    
    return {
        "message": "Item removed from cart",
        "id": item_id
    }


@router.post("/v1x/marketplace/coupons/validate")
def session_validate_coupon(
    request: ApplyCouponRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate a coupon code and return discount info"""
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


@router.post("/v1x/marketplace/checkout")
def session_checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process checkout and create order"""
    # Get cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    subtotal = sum(float(item.price) for item in cart_items)
    discount_amount = 0
    coupon_obj = None
    
    # Apply coupon if provided
    if request.coupon_code:
        coupon_obj = db.query(Coupon).filter(
            and_(
                Coupon.code == request.coupon_code,
                Coupon.is_active == True
            )
        ).first()
        
        if coupon_obj:
            # Validate coupon
            if coupon_obj.valid_from and coupon_obj.valid_from > datetime.utcnow():
                raise HTTPException(status_code=400, detail="Coupon not yet valid")
            if coupon_obj.valid_until and coupon_obj.valid_until < datetime.utcnow():
                raise HTTPException(status_code=400, detail="Coupon expired")
            if coupon_obj.usage_limit and coupon_obj.usage_count >= coupon_obj.usage_limit:
                raise HTTPException(status_code=400, detail="Coupon usage limit reached")
            
            # Calculate discount
            if coupon_obj.discount_type == "percentage":
                discount_amount = subtotal * (float(coupon_obj.discount_value) / 100)
                if coupon_obj.max_discount_amount:
                    discount_amount = min(discount_amount, float(coupon_obj.max_discount_amount))
            else:  # fixed
                discount_amount = float(coupon_obj.discount_value)
            
            discount_amount = min(discount_amount, subtotal)
    
    total = subtotal - discount_amount
    
    # Generate order number
    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
    
    # Get first course from cart
    course = db.query(Course).filter(Course.id == cart_items[0].course_id).first()
    
    # Create order
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
    
    # Handle payment based on method
    if request.payment_method == "coins":
        # Calculate coin balance
        coin_balance = db.query(func.sum(CoinLedger.delta)).filter(
            CoinLedger.user_id == current_user.id
        ).scalar() or 0
        
        # Coins required (1 coin = $1)
        coins_required = int(total)
        
        # Check if user has enough coins
        if coin_balance < coins_required:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient coins. Balance: {coin_balance}, Required: {coins_required}"
            )
        
        # Deduct coins
        coin_transaction = CoinLedger(
            user_id=current_user.id,
            delta=-coins_required,
            reason=f"Course purchase: {course.title if course else 'Unknown'}"
        )
        db.add(coin_transaction)
        
        # Mark order as completed
        order.status = "completed"
        order.payment_status = "completed"
        order.paid_at = datetime.utcnow()
    
    # Clear cart
    for item in cart_items:
        db.delete(item)
    
    # Update coupon usage
    if request.coupon_code and coupon_obj:
        coupon_obj.usage_count += 1
    
    db.commit()
    db.refresh(order)
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "amount": float(order.amount),
        "message": "Order created successfully"
    }


@router.get("/v1x/marketplace/orders")
def session_get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's order history"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(desc(Order.created_at)).all()
    
    result = []
    for order in orders:
        course = db.query(Course).filter(Course.id == order.course_id).first()
        result.append({
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "subtotal": float(order.subtotal),
            "discount_amount": float(order.discount_amount),
            "tax_amount": float(order.tax_amount),
            "amount": float(order.amount),
            "currency": order.currency,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "created_at": order.created_at,
            "course_title": course.title if course else None
        })
    
    return result


# ==================== Admin Analytics Proxy Routes ====================

@router.get("/v1x/analytics/overview")
def analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Proxy to admin analytics overview endpoint"""
    from app.api.v1x.admin_analytics import get_overview
    return get_overview(db, current_user)


@router.get("/v1x/analytics/daily-active-users")
def analytics_daily_users(
    days: int = Query(30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Proxy to admin analytics daily active users"""
    from app.api.v1x.admin_analytics import get_daily_active_users
    return get_daily_active_users(days, db, current_user)


@router.get("/v1x/analytics/revenue-breakdown")
def analytics_revenue_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Proxy to admin analytics revenue breakdown"""
    from app.api.v1x.admin_analytics import get_revenue_breakdown
    return get_revenue_breakdown(db, current_user)


@router.get("/v1x/analytics/revenue")
def analytics_revenue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Proxy to admin analytics revenue"""
    from app.api.v1x.admin_analytics import get_revenue_analytics
    return get_revenue_analytics(db, current_user)


@router.get("/v1x/analytics/feature-adoption")
def analytics_feature_adoption(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Proxy to admin analytics feature adoption"""
    from app.api.v1x.admin_analytics import get_feature_adoption
    return get_feature_adoption(db, current_user)


@router.get("/v1x/analytics/mentors-performance")
def analytics_mentors_performance(
    limit: int = Query(10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Proxy to admin analytics mentors performance"""
    from app.api.v1x.admin_analytics import get_mentors_performance
    return get_mentors_performance(limit, db, current_user)


@router.get("/v1x/analytics/student-engagement")
def analytics_student_engagement(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Proxy to admin analytics student engagement"""
    from app.api.v1x.admin_analytics import get_student_engagement
    return get_student_engagement(db, current_user)
