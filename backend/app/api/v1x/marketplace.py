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
from app.modelsx.coins import CoinLedger
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
        # Calculate coin balance
        coin_balance = db.query(func.sum(CoinLedger.delta)).filter(
            CoinLedger.user_id == current_user.id
        ).scalar() or 0
        
        # Coins required (1 coin = $1, so convert from dollars)
        coins_required = int(total)
        
        # Check if user has enough coins
        if coin_balance < coins_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient coins. Balance: {coin_balance}, Required: {coins_required}"
            )
        
        # Deduct coins from balance
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


# ==================== DIGITAL PRODUCTS EXTENSION ====================

# Import additional models
from app.modelsx.marketplace import (
    DigitalProduct, ProductPurchase, ProductReview, SellerAccount,
    ProductBundle, SellerPayout, MarketplaceAnalytics,
    DigitalProductType, ProductStatus
)
from app.schemas.marketplace import (
    DigitalProductCreate, DigitalProductUpdate, DigitalProductResponse,
    ProductReviewCreate, ProductReviewResponse, ProductListingResponse
)


@router.post("/digital-products", response_model=DigitalProductResponse)
def create_digital_product(
    product: DigitalProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new digital product"""
    
    # Check seller account exists
    seller_account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    if not seller_account:
        raise HTTPException(status_code=403, detail="Must have a seller account")
    
    # Create slug
    slug = product.name.lower().replace(" ", "-")
    if db.query(DigitalProduct).filter_by(slug=slug).first():
        raise HTTPException(status_code=400, detail="Product name already exists")
    
    db_product = DigitalProduct(
        seller_id=current_user.id,
        name=product.name,
        slug=slug,
        description=product.description,
        product_type=product.product_type,
        category=product.category,
        tags=product.tags,
        price=product.price,
        original_price=product.original_price or product.price,
        currency=product.currency,
        thumbnail_url=product.thumbnail_url,
        content_url=product.content_url,
        preview_url=product.preview_url,
        file_size_mb=product.file_size_mb,
        requirements=product.requirements,
        features=product.features,
        status=ProductStatus.DRAFT
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return DigitalProductResponse.from_orm(db_product)


@router.get("/digital-products/{product_id}", response_model=DigitalProductResponse)
def get_digital_product(product_id: int, db: Session = Depends(get_db)):
    """Get digital product details"""
    
    product = db.query(DigitalProduct).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check visibility
    if product.status == ProductStatus.ARCHIVED or product.status == ProductStatus.SUSPENDED:
        raise HTTPException(status_code=404, detail="Product not available")
    
    # Increment views
    product.views_count += 1
    db.commit()
    
    return DigitalProductResponse.from_orm(product)


@router.get("/digital-products", response_model=ProductListingResponse)
def list_digital_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    product_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "popularity",
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """List and search digital products with filters"""
    
    query = db.query(DigitalProduct).filter(
        DigitalProduct.status == ProductStatus.PUBLISHED
    )
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                DigitalProduct.name.ilike(f"%{search}%"),
                DigitalProduct.description.ilike(f"%{search}%")
            )
        )
    
    # Category filter
    if category:
        query = query.filter_by(category=category)
    
    # Type filter
    if product_type:
        query = query.filter_by(product_type=product_type)
    
    # Price range
    if min_price is not None:
        query = query.filter(DigitalProduct.price >= min_price)
    if max_price is not None:
        query = query.filter(DigitalProduct.price <= max_price)
    
    # Sorting
    if sort_by == "newest":
        query = query.order_by(desc(DigitalProduct.created_at))
    elif sort_by == "price_low":
        query = query.order_by(DigitalProduct.price)
    elif sort_by == "price_high":
        query = query.order_by(desc(DigitalProduct.price))
    elif sort_by == "rating":
        query = query.order_by(desc(DigitalProduct.average_rating))
    else:  # popularity
        query = query.order_by(desc(DigitalProduct.sales_count))
    
    # Pagination
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return ProductListingResponse(
        products=[DigitalProductResponse.from_orm(p) for p in products],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.post("/digital-products/{product_id}/purchase")
def purchase_digital_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase a digital product"""
    
    # Get product
    product = db.query(DigitalProduct).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check not already owned
    existing = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.product_id == product_id,
            ProductPurchase.buyer_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already purchased")
    
    # Create purchase
    db_purchase = ProductPurchase(
        product_id=product_id,
        buyer_id=current_user.id,
        seller_id=product.seller_id,
        purchase_price=product.price,
        currency=product.currency,
        payment_method="coins",
        status="completed",
        delivered_at=datetime.utcnow(),
        platform_fee=product.price * 0.30,
        seller_payout=product.price * 0.70
    )
    
    # Update product stats
    product.sales_count += 1
    product.total_revenue += product.price
    
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return {
        "id": db_purchase.id,
        "product_id": db_purchase.product_id,
        "status": "completed",
        "purchase_price": db_purchase.purchase_price,
        "purchased_at": db_purchase.purchased_at
    }


@router.post("/digital-products/{product_id}/reviews", response_model=ProductReviewResponse)
def create_product_review(
    product_id: int,
    review: ProductReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a review for a digital product"""
    
    # Check product exists
    product = db.query(DigitalProduct).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check verified purchase
    purchase = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.product_id == product_id,
            ProductPurchase.buyer_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).first()
    
    db_review = ProductReview(
        product_id=product_id,
        reviewer_id=current_user.id,
        title=review.title,
        content=review.content,
        overall_rating=review.overall_rating,
        quality_rating=review.quality_rating,
        value_rating=review.value_rating,
        support_rating=review.support_rating,
        is_verified=bool(purchase)
    )
    
    db.add(db_review)
    
    # Update product rating
    all_reviews = db.query(ProductReview).filter_by(product_id=product_id).all()
    avg_rating = sum(r.overall_rating for r in all_reviews) / len(all_reviews) if all_reviews else review.overall_rating
    product.average_rating = avg_rating
    product.review_count = len(all_reviews) + 1
    
    db.commit()
    db.refresh(db_review)
    
    return ProductReviewResponse.from_orm(db_review)


@router.post("/seller/account")
def create_seller_account(
    account_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a seller account"""
    
    # Check if already has account
    existing = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a seller")
    
    db_account = SellerAccount(
        user_id=current_user.id,
        store_name=account_data.get("store_name"),
        store_description=account_data.get("store_description"),
        payout_method=account_data.get("payout_method", "stripe")
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return {
        "id": db_account.id,
        "user_id": db_account.user_id,
        "store_name": db_account.store_name,
        "is_verified": db_account.is_verified,
        "total_revenue": db_account.total_revenue
    }


@router.get("/seller/account")
def get_seller_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller account details"""
    
    account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="No seller account")
    
    return {
        "id": account.id,
        "user_id": account.user_id,
        "store_name": account.store_name,
        "is_verified": account.is_verified,
        "seller_tier": account.seller_tier,
        "total_sales": account.total_sales,
        "total_revenue": account.total_revenue,
        "average_rating": account.average_rating
    }


@router.get("/best-sellers")
def get_best_sellers(
    period: str = "month",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get best selling digital products"""
    
    products = db.query(DigitalProduct).filter(
        DigitalProduct.status == ProductStatus.PUBLISHED
    ).order_by(desc(DigitalProduct.sales_count)).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "sales_count": p.sales_count,
            "average_rating": p.average_rating,
            "category": p.category
        }
        for p in products
    ]


@router.get("/top-sellers")
def get_top_sellers(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top performing sellers"""
    
    sellers = db.query(SellerAccount).filter_by(
        is_verified=True,
        is_active=True
    ).order_by(desc(SellerAccount.total_revenue)).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "store_name": s.store_name,
            "total_sales": s.total_sales,
            "total_revenue": s.total_revenue,
            "average_rating": s.average_rating,
            "seller_tier": s.seller_tier
        }
        for s in sellers
    ]


@router.get("/marketplace-analytics")
def get_marketplace_analytics(db: Session = Depends(get_db)):
    """Get marketplace analytics"""
    
    analytics = db.query(MarketplaceAnalytics).order_by(
        desc(MarketplaceAnalytics.period_date)
    ).first()
    
    if not analytics:
        return {
            "period_date": datetime.utcnow(),
            "total_sales": 0,
            "total_revenue": 0.0,
            "unique_buyers": 0,
            "unique_sellers": 0,
            "total_products": 0
        }
    
    return {
        "period_date": analytics.period_date,
        "total_sales": analytics.total_sales,
        "total_revenue": analytics.total_revenue,
        "unique_buyers": analytics.unique_buyers,
        "unique_sellers": analytics.unique_sellers,
        "total_products": analytics.total_products,
        "growth_rate": analytics.growth_rate
    }
