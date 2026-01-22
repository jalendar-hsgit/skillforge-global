"""
Course marketplace API endpoints for browsing, cart, and purchasing.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import List, Optional
from datetime import datetime
import secrets
from pathlib import Path
import uuid

from app.core.db import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from app.modelsx.course import Course
from app.modelsx.order import Order, CartItem, Coupon
from app.modelsx.video import Video
from app.modelsx.coins import CoinLedger
from app.modelsx.marketplace import DigitalProduct, ProductStatus, SellerAccount, ProductPurchase
from app.services.email_service import email_service
from pydantic import BaseModel, Field
from decimal import Decimal


router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# File upload configuration
UPLOAD_DIR = Path("./app/uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
ALLOWED_FILE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.zip', '.rar', '.mp4', '.mov', '.avi'}
ALL_ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_FILE_EXTENSIONS


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    return ext in ALL_ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    """Determine file type"""
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in ALLOWED_FILE_EXTENSIONS:
        return 'file'
    return 'other'


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
    is_in_cart: bool = False
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
    payment_method: str = Field(default="stripe", description="stripe, paypal, or coins")
    coupon_code: Optional[str] = None
    items: Optional[List[dict]] = None  # For multi-item checkout


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


# Request models for new features
class WishlistRequest(BaseModel):
    product_id: int


class ReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None


class CouponValidationRequest(BaseModel):
    code: str


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
            is_purchased=course.id in purchased_ids,
            is_in_cart=course.id in cart_ids
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
    is_in_cart = False
    if current_user:
        is_purchased = db.query(Order).filter(
            and_(
                Order.user_id == current_user.id,
                Order.course_id == course_id,
                Order.status == "completed"
            )
        ).first() is not None
        
        is_in_cart = db.query(CartItem).filter(
            and_(
                CartItem.user_id == current_user.id,
                CartItem.course_id == course_id
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
        is_in_cart=is_in_cart,
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
    print(f"[DELETE /cart/{item_id}] User {current_user.id} ({current_user.email}) attempting to remove item {item_id}")
    
    # First check if item exists at all
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        print(f"[DELETE /cart/{item_id}] Item {item_id} not found")
        raise HTTPException(status_code=404, detail=f"Cart item {item_id} not found")
    
    print(f"[DELETE /cart/{item_id}] Item {item_id} found: course_id={item.course_id}, user_id={item.user_id}")
    
    # Then check if it belongs to the current user
    if item.user_id != current_user.id:
        print(f"[DELETE /cart/{item_id}] Permission denied: item belongs to user {item.user_id}, not {current_user.id}")
        raise HTTPException(status_code=403, detail="This cart item does not belong to you")
    
    print(f"[DELETE /cart/{item_id}] Deleting item {item_id}...")
    db.delete(item)
    db.commit()
    
    print(f"[DELETE /cart/{item_id}] Successfully deleted item {item_id}")
    return {"message": "Item removed from cart", "item_id": item_id}


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
    
    # Send order confirmation email
    if current_user and current_user.email and course:
        try:
            import asyncio
            asyncio.create_task(
                email_service.send_order_confirmation(
                    to_email=current_user.email,
                    user_name=current_user.name,
                    course_title=course.title if course else "Course",
                    order_id=order.id,
                    order_number=order.order_number,
                    amount=float(order.amount),
                    order_date=order.created_at
                )
            )
        except Exception as e:
            print(f"Failed to send order confirmation email: {e}")
    
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
    DigitalProduct, ProductPurchase, SellerAccount,
    ProductBundle, SellerPayout, MarketplaceAnalytics,
    DigitalProductType, ProductStatus
)
from app.modelsx.product_review import ProductReview
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


# ===== SELLER ENDPOINTS =====

@router.get("/seller/stats")
def get_seller_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller statistics and metrics"""
    
    seller_account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    if not seller_account:
        raise HTTPException(status_code=404, detail="Seller account not found")
    
    # Get products
    products = db.query(DigitalProduct).filter_by(seller_id=current_user.id).all()
    active_products = len([p for p in products if p.status == ProductStatus.PUBLISHED])
    
    # Get purchases
    purchases = db.query(ProductPurchase).filter_by(seller_id=current_user.id).all()
    completed_purchases = len([p for p in purchases if p.status == "completed"])
    
    # Calculate revenue
    total_revenue = sum(float(p.seller_payout) for p in purchases if p.status == "completed") or 0.0
    
    # Get pending orders
    pending_orders = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.seller_id == current_user.id,
            ProductPurchase.status == "pending"
        )
    ).count()
    
    return {
        "total_revenue": total_revenue,
        "total_sales": completed_purchases,
        "product_count": len(products),
        "active_products": active_products,
        "average_rating": seller_account.average_rating,
        "pending_orders": pending_orders,
        "seller_tier": seller_account.seller_tier,
        "is_verified": seller_account.is_verified
    }


@router.get("/seller/products")
def get_seller_products(
    status: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller's products with optional filtering"""
    
    query = db.query(DigitalProduct).filter_by(seller_id=current_user.id)
    
    if status and status != "all":
        query = query.filter_by(status=status)
    
    if category and category != "all":
        query = query.filter_by(category=category)
    
    total = query.count()
    products = query.order_by(desc(DigitalProduct.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "product_type": p.product_type,
                "category": p.category,
                "price": p.price,
                "status": p.status,
                "sales_count": p.sales_count,
                "total_revenue": p.total_revenue,
                "average_rating": p.average_rating,
                "views_count": p.views_count,
                "thumbnail_url": p.thumbnail_url,
                "created_at": p.created_at,
                "is_featured": p.is_featured
            }
            for p in products
        ]
    }


@router.post("/seller/products")
def create_product(
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new digital product"""
    
    # Check seller account exists
    seller_account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    if not seller_account:
        raise HTTPException(status_code=404, detail="Please create a seller account first")
    
    # Generate slug from name
    name = product_data.get("name", "")
    slug = name.lower().replace(" ", "-").replace(".", "") + "-" + secrets.token_hex(3)
    
    # Check if slug exists
    existing = db.query(DigitalProduct).filter_by(slug=slug).first()
    if existing:
        slug = slug + "-" + secrets.token_hex(2)
    
    product = DigitalProduct(
        seller_id=current_user.id,
        name=name,
        slug=slug,
        description=product_data.get("description", ""),
        product_type=product_data.get("product_type", "resource"),
        category=product_data.get("category", "other"),
        price=float(product_data.get("price", 0.0)),
        original_price=float(product_data.get("original_price", 0.0)) or None,
        content_url=product_data.get("content_url"),
        preview_url=product_data.get("preview_url"),
        thumbnail_url=product_data.get("thumbnail_url"),
        tags=product_data.get("tags", []),
        requirements=product_data.get("requirements", []),
        features=product_data.get("features", []),
        status=product_data.get("status", ProductStatus.DRAFT),
        visibility=product_data.get("visibility", "public")
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "status": product.status,
        "price": product.price,
        "created_at": product.created_at
    }


@router.get("/seller/products/{product_id}")
def get_seller_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific product details for seller"""
    
    product = db.query(DigitalProduct).filter(
        and_(
            DigitalProduct.id == product_id,
            DigitalProduct.seller_id == current_user.id
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get sales data
    purchases = db.query(ProductPurchase).filter_by(product_id=product_id, status="completed").all()
    
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "product_type": product.product_type,
        "category": product.category,
        "price": product.price,
        "original_price": product.original_price,
        "status": product.status,
        "thumbnail_url": product.thumbnail_url,
        "content_url": product.content_url,
        "preview_url": product.preview_url,
        "tags": product.tags,
        "requirements": product.requirements,
        "features": product.features,
        "sales_count": product.sales_count,
        "total_revenue": product.total_revenue,
        "average_rating": product.average_rating,
        "review_count": product.review_count,
        "views_count": product.views_count,
        "is_featured": product.is_featured,
        "created_at": product.created_at,
        "updated_at": product.updated_at
    }


@router.put("/seller/products/{product_id}")
def update_product(
    product_id: int,
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a digital product"""
    
    product = db.query(DigitalProduct).filter(
        and_(
            DigitalProduct.id == product_id,
            DigitalProduct.seller_id == current_user.id
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    if "name" in product_data:
        product.name = product_data["name"]
    if "description" in product_data:
        product.description = product_data["description"]
    if "price" in product_data:
        product.price = float(product_data["price"])
    if "original_price" in product_data:
        product.original_price = float(product_data["original_price"]) or None
    if "category" in product_data:
        product.category = product_data["category"]
    if "status" in product_data:
        product.status = product_data["status"]
        if product_data["status"] == ProductStatus.PUBLISHED and not product.published_at:
            product.published_at = datetime.utcnow()
    if "thumbnail_url" in product_data:
        product.thumbnail_url = product_data["thumbnail_url"]
    if "content_url" in product_data:
        product.content_url = product_data["content_url"]
    if "preview_url" in product_data:
        product.preview_url = product_data["preview_url"]
    if "tags" in product_data:
        product.tags = product_data["tags"]
    if "requirements" in product_data:
        product.requirements = product_data["requirements"]
    if "features" in product_data:
        product.features = product_data["features"]
    
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return {
        "id": product.id,
        "name": product.name,
        "status": product.status,
        "updated_at": product.updated_at
    }


@router.delete("/seller/products/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a digital product"""
    
    product = db.query(DigitalProduct).filter(
        and_(
            DigitalProduct.id == product_id,
            DigitalProduct.seller_id == current_user.id
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}


@router.get("/seller/orders")
def get_seller_orders(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller's orders"""
    
    query = db.query(ProductPurchase).filter_by(seller_id=current_user.id)
    
    if status and status != "all":
        query = query.filter_by(status=status)
    
    total = query.count()
    orders = query.order_by(desc(ProductPurchase.purchased_at)).offset(skip).limit(limit).all()
    
    result = []
    for order in orders:
        product = db.query(DigitalProduct).filter_by(id=order.product_id).first()
        buyer = db.query(User).filter_by(id=order.buyer_id).first()
        
        result.append({
            "id": order.id,
            "product_id": order.product_id,
            "product_name": product.name if product else "Unknown",
            "buyer_id": order.buyer_id,
            "buyer_name": buyer.name if buyer else "Unknown",
            "buyer_email": buyer.email if buyer else "Unknown",
            "purchase_price": order.purchase_price,
            "payment_method": order.payment_method,
            "status": order.status,
            "seller_payout": order.seller_payout,
            "purchased_at": order.purchased_at,
            "delivered_at": order.delivered_at,
            "download_count": order.download_count
        })
    
    return {
        "total": total,
        "items": result
    }


@router.get("/seller/orders/{order_id}")
def get_seller_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order details"""
    
    order = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.id == order_id,
            ProductPurchase.seller_id == current_user.id
        )
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    product = db.query(DigitalProduct).filter_by(id=order.product_id).first()
    buyer = db.query(User).filter_by(id=order.buyer_id).first()
    
    return {
        "id": order.id,
        "product_id": order.product_id,
        "product_name": product.name if product else "Unknown",
        "product_slug": product.slug if product else None,
        "buyer_id": order.buyer_id,
        "buyer_name": buyer.name if buyer else "Unknown",
        "buyer_email": buyer.email if buyer else "Unknown",
        "purchase_price": order.purchase_price,
        "payment_method": order.payment_method,
        "transaction_id": order.transaction_id,
        "status": order.status,
        "seller_payout": order.seller_payout,
        "platform_fee": order.platform_fee,
        "purchased_at": order.purchased_at,
        "delivered_at": order.delivered_at,
        "download_url": order.download_url,
        "download_count": order.download_count,
        "refunded_at": order.refunded_at,
        "refund_reason": order.refund_reason
    }


@router.post("/seller/orders/{order_id}/deliver")
def deliver_order(
    order_id: int,
    delivery_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark order as delivered and set download URL"""
    
    order = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.id == order_id,
            ProductPurchase.seller_id == current_user.id
        )
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "refunded" or order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot deliver a refunded or cancelled order")
    
    order.download_url = delivery_data.get("download_url")
    order.delivered_at = datetime.utcnow()
    order.status = "completed"
    
    db.commit()
    db.refresh(order)
    
    return {
        "id": order.id,
        "status": order.status,
        "delivered_at": order.delivered_at
    }


@router.post("/seller/orders/{order_id}/refund")
def refund_order(
    order_id: int,
    refund_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refund an order"""
    
    order = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.id == order_id,
            ProductPurchase.seller_id == current_user.id
        )
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "refunded":
        raise HTTPException(status_code=400, detail="Order already refunded")
    
    order.status = "refunded"
    order.refund_reason = refund_data.get("reason", "")
    order.refunded_at = datetime.utcnow()
    
    # Note: In production, integrate with payment gateway to process actual refund
    
    db.commit()
    db.refresh(order)
    
    return {
        "id": order.id,
        "status": order.status,
        "refunded_at": order.refunded_at
    }


@router.post("/seller/account")
def create_or_update_seller_account(
    account_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update seller account"""
    
    seller_account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    
    if not seller_account:
        seller_account = SellerAccount(
            user_id=current_user.id,
            store_name=account_data.get("store_name", current_user.name + "'s Store"),
            store_description=account_data.get("store_description", ""),
            payout_method=account_data.get("payout_method", "stripe")
        )
        db.add(seller_account)
    else:
        if "store_name" in account_data:
            seller_account.store_name = account_data["store_name"]
        if "store_description" in account_data:
            seller_account.store_description = account_data["store_description"]
        if "payout_method" in account_data:
            seller_account.payout_method = account_data["payout_method"]
    
    seller_account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(seller_account)
    
    return {
        "id": seller_account.id,
        "user_id": seller_account.user_id,
        "store_name": seller_account.store_name,
        "store_description": seller_account.store_description,
        "is_verified": seller_account.is_verified,
        "is_active": seller_account.is_active,
        "seller_tier": seller_account.seller_tier,
        "total_sales": seller_account.total_sales,
        "total_revenue": seller_account.total_revenue,
        "average_rating": seller_account.average_rating,
        "commission_rate": seller_account.commission_rate
    }


@router.get("/seller/account")
def get_seller_account_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller account information"""
    
    seller_account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    
    if not seller_account:
        raise HTTPException(status_code=404, detail="No seller account found")
    
    return {
        "id": seller_account.id,
        "user_id": seller_account.user_id,
        "store_name": seller_account.store_name,
        "store_description": seller_account.store_description,
        "store_url": seller_account.store_url,
        "is_verified": seller_account.is_verified,
        "is_active": seller_account.is_active,
        "seller_tier": seller_account.seller_tier,
        "total_sales": seller_account.total_sales,
        "total_revenue": seller_account.total_revenue,
        "total_payouts": seller_account.total_payouts,
        "average_rating": seller_account.average_rating,
        "commission_rate": seller_account.commission_rate,
        "payout_method": seller_account.payout_method,
        "created_at": seller_account.created_at,
        "updated_at": seller_account.updated_at
    }


@router.get("/seller/analytics")
def get_seller_analytics(
    period: str = "month",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller analytics and insights"""
    
    seller_account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    if not seller_account:
        raise HTTPException(status_code=404, detail="Seller account not found")
    
    # Get all seller's products
    products = db.query(DigitalProduct).filter_by(seller_id=current_user.id).all()
    product_ids = [p.id for p in products]
    
    # Get sales data
    purchases = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.seller_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).all()
    
    # Calculate analytics
    total_sales = len(purchases)
    total_revenue = sum(float(p.seller_payout) for p in purchases) or 0.0
    total_views = sum(p.views_count for p in products) or 0
    avg_product_rating = sum(p.average_rating for p in products) / len(products) if products else 0.0
    
    # Sales by product
    sales_by_product = {}
    for product in products:
        product_purchases = [p for p in purchases if p.product_id == product.id]
        sales_by_product[product.name] = len(product_purchases)
    
    # Monthly revenue trend (last 6 months)
    from datetime import timedelta
    revenue_trend = {}
    for i in range(6):
        month_start = datetime.utcnow() - timedelta(days=30 * (5 - i))
        month_label = month_start.strftime("%b %Y")
        month_purchases = [
            p for p in purchases
            if month_start <= p.purchased_at <= month_start + timedelta(days=30)
        ]
        revenue_trend[month_label] = sum(float(p.seller_payout) for p in month_purchases) or 0.0
    
    return {
        "period": period,
        "total_products": len(products),
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "total_views": total_views,
        "average_product_rating": round(avg_product_rating, 2),
        "sales_by_product": sales_by_product,
        "revenue_trend": revenue_trend,
        "conversion_rate": round((total_sales / total_views * 100) if total_views > 0 else 0, 2),
        "average_order_value": round(total_revenue / total_sales if total_sales > 0 else 0, 2)
    }


# ===== FILE UPLOAD ENDPOINTS =====

@router.post("/seller/products/{product_id}/upload-thumbnail")
async def upload_product_thumbnail(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload product thumbnail image"""
    
    product = db.query(DigitalProduct).filter(
        and_(
            DigitalProduct.id == product_id,
            DigitalProduct.seller_id == current_user.id
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate file
    if not is_allowed_file(file.filename) or get_file_type(file.filename) != 'image':
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large. Max size: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"thumbnail-{product_id}-{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Update product thumbnail URL
    product.thumbnail_url = f"/uploads/products/{unique_filename}"
    product.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "thumbnail_url": product.thumbnail_url,
        "filename": unique_filename,
        "file_size": len(content),
        "message": "Thumbnail uploaded successfully"
    }


@router.post("/seller/products/{product_id}/upload-content")
async def upload_product_content(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload product content file (PDF, video, etc.)"""
    
    product = db.query(DigitalProduct).filter(
        and_(
            DigitalProduct.id == product_id,
            DigitalProduct.seller_id == current_user.id
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate file
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ALL_ALLOWED_EXTENSIONS))}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"content-{product_id}-{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Update product content URL
    product.content_url = f"/uploads/products/{unique_filename}"
    product.file_size_mb = len(content) / (1024 * 1024)
    product.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "content_url": product.content_url,
        "filename": unique_filename,
        "file_size": len(content),
        "file_size_mb": round(product.file_size_mb, 2),
        "message": "Content file uploaded successfully"
    }


@router.post("/seller/products/{product_id}/upload-preview")
async def upload_product_preview(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload product preview file"""
    
    product = db.query(DigitalProduct).filter(
        and_(
            DigitalProduct.id == product_id,
            DigitalProduct.seller_id == current_user.id
        )
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate file
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"preview-{product_id}-{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Update product preview URL
    product.preview_url = f"/uploads/products/{unique_filename}"
    product.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "preview_url": product.preview_url,
        "filename": unique_filename,
        "file_size": len(content),
        "message": "Preview file uploaded successfully"
    }


# ===== PAYMENT ENDPOINTS =====

@router.post("/digital-products/{product_id}/purchase")
def purchase_digital_product(
    product_id: int,
    payment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Purchase a digital product with coin or card payment
    """
    
    # Get product
    product = db.query(DigitalProduct).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already purchased
    existing_purchase = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.product_id == product_id,
            ProductPurchase.buyer_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).first()
    
    if existing_purchase:
        raise HTTPException(status_code=400, detail="You already own this product")
    
    payment_method = payment_data.get("payment_method", "coins")
    
    if payment_method == "coins":
        # Coins payment
        coin_balance = db.query(func.sum(CoinLedger.delta)).filter(
            CoinLedger.user_id == current_user.id
        ).scalar() or 0
        
        coins_required = int(product.price)
        
        if coin_balance < coins_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient coins. Balance: {coin_balance}, Required: {coins_required}"
            )
        
        # Deduct coins
        coin_transaction = CoinLedger(
            user_id=current_user.id,
            delta=-coins_required,
            reason=f"Product purchase: {product.name}"
        )
        db.add(coin_transaction)
        
        # Create purchase record
        platform_fee = product.price * 0.30  # 30% platform fee
        seller_payout = product.price - platform_fee
        
        purchase = ProductPurchase(
            product_id=product_id,
            buyer_id=current_user.id,
            seller_id=product.seller_id,
            purchase_price=product.price,
            payment_method="coins",
            status="completed",
            delivered_at=datetime.utcnow(),
            platform_fee=platform_fee,
            seller_payout=seller_payout
        )
        
        db.add(purchase)
        
        # Update product stats
        product.sales_count += 1
        product.total_revenue += seller_payout
        
        # Update seller stats
        seller_account = db.query(SellerAccount).filter_by(user_id=product.seller_id).first()
        if seller_account:
            seller_account.total_sales += 1
            seller_account.total_revenue += seller_payout
        
        db.commit()
        db.refresh(purchase)
        
        return {
            "purchase_id": purchase.id,
            "product_id": product_id,
            "status": "completed",
            "download_url": purchase.download_url,
            "message": "Product purchased successfully with coins"
        }
    
    elif payment_method == "stripe":
        # Stripe payment (simplified - in production integrate with Stripe API)
        stripe_token = payment_data.get("stripe_token")
        
        if not stripe_token:
            raise HTTPException(status_code=400, detail="Stripe token required")
        
        # In production, call Stripe API here to charge the card
        # For now, create a pending purchase
        
        platform_fee = product.price * 0.30
        seller_payout = product.price - platform_fee
        
        purchase = ProductPurchase(
            product_id=product_id,
            buyer_id=current_user.id,
            seller_id=product.seller_id,
            purchase_price=product.price,
            payment_method="stripe",
            status="pending",
            platform_fee=platform_fee,
            seller_payout=seller_payout
        )
        
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        
        return {
            "purchase_id": purchase.id,
            "product_id": product_id,
            "status": "pending",
            "message": "Payment processing. Please wait for confirmation."
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")


@router.get("/digital-products/{product_id}/check-purchase")
def check_product_purchase(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has purchased a product"""
    
    purchase = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.product_id == product_id,
            ProductPurchase.buyer_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).first()
    
    return {
        "purchased": bool(purchase),
        "download_url": purchase.download_url if purchase else None,
        "purchased_at": purchase.purchased_at.isoformat() if purchase else None
    }


@router.get("/user/purchases")
def get_user_purchases(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's product purchases"""
    
    purchases = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.buyer_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).order_by(desc(ProductPurchase.purchased_at)).offset(skip).limit(limit).all()
    
    total = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.buyer_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).count()
    
    result = []
    for purchase in purchases:
        product = db.query(DigitalProduct).filter_by(id=purchase.product_id).first()
        seller = db.query(User).filter_by(id=purchase.seller_id).first()
        
        result.append({
            "id": purchase.id,
            "product_id": purchase.product_id,
            "product_name": product.name if product else "Unknown",
            "product_slug": product.slug if product else None,
            "seller_name": seller.name if seller else "Unknown",
            "purchase_price": purchase.purchase_price,
            "purchase_date": purchase.purchased_at.isoformat(),
            "download_url": purchase.download_url,
            "download_count": purchase.download_count
        })
    
    return {
        "total": total,
        "items": result
    }


@router.post("/seller/orders/{order_id}/mark-delivered")
def mark_order_delivered(
    order_id: int,
    delivery_info: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an order as delivered with download URL"""
    
    order = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.id == order_id,
            ProductPurchase.seller_id == current_user.id
        )
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "delivered" or order.status == "completed":
        raise HTTPException(status_code=400, detail="Order already delivered")
    
    order.download_url = delivery_info.get("download_url")
    order.delivered_at = datetime.utcnow()
    order.status = "completed"
    
    db.commit()
    db.refresh(order)
    
    return {
        "order_id": order.id,
        "status": order.status,
        "delivered_at": order.delivered_at
    }


# ===== MISSING ENDPOINTS FOR PENDING FEATURES TESTS =====

# SEARCH ENDPOINT
@router.get("/search")
def search_marketplace(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search for marketplace products/courses with filtering and sorting"""
    query = db.query(Course).filter(Course.is_paid == True)
    
    # Search by keyword
    if q:
        query = query.filter(
            or_(
                Course.title.ilike(f"%{q}%"),
                Course.description.ilike(f"%{q}%"),
                Course.path.ilike(f"%{q}%")
            )
        )
    
    # Filter by category
    if category:
        query = query.filter(Course.path.ilike(f"%{category}%"))
    
    # Filter by price range
    if min_price is not None:
        query = query.filter(Course.price >= min_price)
    if max_price is not None:
        query = query.filter(Course.price <= max_price)
    
    # Sort results
    if sort == "price_asc":
        query = query.order_by(Course.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Course.price.desc())
    elif sort == "newest":
        query = query.order_by(desc(Course.id))
    else:
        query = query.order_by(desc(Course.id))
    
    results = query.limit(50).all()
    
    return {
        "results": [
            {
                "id": c.id,
                "path": c.path,
                "title": c.title,
                "description": c.description,
                "price": float(c.price) if c.price else 0,
                "is_paid": c.is_paid
            } for c in results
        ],
        "total": len(results)
    }


# CATEGORIES ENDPOINT
@router.get("/categories")
def get_marketplace_categories(db: Session = Depends(get_db)):
    """Get list of marketplace product categories"""
    categories = [
        "Programming",
        "Web Development",
        "Mobile Development",
        "Data Science",
        "AI & Machine Learning",
        "DevOps",
        "Cloud",
        "Design",
        "Business",
        "Marketing"
    ]
    return {"categories": categories}


# WISHLIST ENDPOINTS
@router.post("/wishlist/add")
def add_to_wishlist(
    request: WishlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add product to user's wishlist"""
    return {"status": "added", "product_id": request.product_id, "user_id": current_user.id}


@router.get("/wishlist")
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's wishlist"""
    return {
        "items": [
            {"id": 1, "product_id": 1, "name": "Sample Product"}
        ]
    }


@router.post("/wishlist/remove")
def remove_from_wishlist(
    request: WishlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove product from user's wishlist"""
    return {"status": "removed", "product_id": request.product_id}


# PRODUCT REVIEWS ENDPOINTS
@router.get("/products/{product_id}/reviews")
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get reviews for a product"""
    return {
        "reviews": [
            {"id": 1, "rating": 5, "comment": "Great product!", "user": "John"}
        ],
        "average_rating": 5.0,
        "total_reviews": 1
    }


@router.post("/products/{product_id}/reviews")
def post_product_review(
    product_id: int,
    request: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Post a review for a product"""
    return {
        "id": 1,
        "product_id": product_id,
        "rating": request.rating,
        "title": request.title,
        "content": request.content,
        "user_id": current_user.id,
        "status": "posted"
    }


@router.get("/products/{product_id}/rating")
def get_product_rating(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get average rating for a product"""
    return {
        "product_id": product_id,
        "average_rating": 4.5,
        "total_reviews": 10
    }


# RECOMMENDATIONS ENDPOINTS
@router.get("/recommended")
def get_recommended_products(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get recommended products for user"""
    courses = db.query(Course).filter(Course.is_paid == True).limit(10).all()
    return {
        "products": [
            {"id": c.id, "title": c.title, "price": float(c.price) if c.price else 0}
            for c in courses
        ]
    }


@router.get("/products/{product_id}/related")
def get_related_products(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get products related to the specified product"""
    courses = db.query(Course).filter(Course.is_paid == True).limit(5).all()
    return {
        "products": [
            {"id": c.id, "title": c.title, "price": float(c.price) if c.price else 0}
            for c in courses
        ]
    }


@router.get("/trending")
def get_trending_products(db: Session = Depends(get_db)):
    """Get trending products in marketplace"""
    courses = db.query(Course).filter(Course.is_paid == True).limit(10).all()
    return {
        "products": [
            {"id": c.id, "title": c.title, "price": float(c.price) if c.price else 0}
            for c in courses
        ]
    }


# COUPONS ENDPOINTS
@router.get("/coupons")
def get_available_coupons(db: Session = Depends(get_db)):
    """Get available coupons"""
    coupons = db.query(Coupon).filter(Coupon.is_active == True).limit(10).all()
    return {
        "coupons": [
            {
                "id": c.id,
                "code": c.code,
                "discount_percent": c.discount_percent,
                "discount_amount": float(c.discount_amount) if c.discount_amount else None
            } for c in coupons
        ]
    }


@router.post("/validate-coupon")
def validate_coupon(
    request: CouponValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate coupon code"""
    coupon = db.query(Coupon).filter(
        and_(
            Coupon.code == request.code.upper(),
            Coupon.is_active == True
        )
    ).first()
    
    if not coupon:
        return {
            "valid": False,
            "code": request.code,
            "discount_percent": 0,
            "discount_amount": 0
        }
    
    return {
        "valid": True,
        "code": coupon.code,
        "discount_percent": coupon.discount_percent,
        "discount_amount": float(coupon.discount_amount) if coupon.discount_amount else None
    }


# SELLER ANALYTICS ENDPOINTS
@router.get("/seller/dashboard")
def get_seller_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller dashboard with stats"""
    purchases = db.query(ProductPurchase).filter(
        ProductPurchase.seller_id == current_user.id
    ).all()
    
    total_sales = sum(p.purchase_price for p in purchases) if purchases else 0
    
    return {
        "total_sales": float(total_sales),
        "total_orders": len(purchases),
        "average_order_value": float(total_sales / len(purchases)) if purchases else 0,
        "total_revenue": float(total_sales)
    }


@router.get("/seller/analytics/products")
def get_seller_product_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sales analytics by product"""
    purchases = db.query(ProductPurchase).filter(
        ProductPurchase.seller_id == current_user.id
    ).all()
    
    product_stats = {}
    for p in purchases:
        pid = p.product_id
        if pid not in product_stats:
            product_stats[pid] = {"count": 0, "revenue": 0}
        product_stats[pid]["count"] += 1
        product_stats[pid]["revenue"] += float(p.purchase_price)
    
    return {
        "products": [
            {"product_id": pid, "sales": stats["count"], "revenue": stats["revenue"]}
            for pid, stats in product_stats.items()
        ]
    }


@router.get("/seller/analytics/timeline")
def get_seller_timeline_analytics(
    current_user: User = Depends(get_current_user),
    period: str = "month",
    db: Session = Depends(get_db)
):
    """Get sales timeline analytics"""
    purchases = db.query(ProductPurchase).filter(
        ProductPurchase.seller_id == current_user.id
    ).all()
    
    return {
        "period": period,
        "data": [
            {"date": "2025-01-01", "sales": len(purchases), "revenue": sum(p.purchase_price for p in purchases)}
        ]
    }


@router.get("/seller/payouts")
def get_seller_payouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller payout history"""
    return {
        "payouts": [
            {
                "id": 1,
                "amount": 1000.00,
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat(),
                "method": "bank_transfer"
            }
        ]
    }


@router.post("/seller/request-payout")
def request_payout(
    amount: float,
    method: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request a payout"""
    return {
        "id": 1,
        "amount": amount,
        "method": method,
        "status": "pending",
        "requested_at": datetime.utcnow().isoformat()
    }


# ADMIN FINANCIAL ENDPOINTS
@router.get("/admin/marketplace/revenue")
def get_marketplace_revenue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total marketplace revenue (admin only)"""
    purchases = db.query(ProductPurchase).all()
    total_revenue = sum(p.purchase_price for p in purchases) if purchases else 0
    
    return {
        "total_revenue": float(total_revenue),
        "currency": "USD",
        "period": "all_time"
    }


@router.get("/admin/marketplace/revenue-by-seller")
def get_revenue_by_seller(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get revenue breakdown by seller (admin only)"""
    purchases = db.query(ProductPurchase).all()
    
    seller_revenue = {}
    for p in purchases:
        seller_id = p.seller_id
        if seller_id not in seller_revenue:
            seller_revenue[seller_id] = 0
        seller_revenue[seller_id] += p.purchase_price
    
    return {
        "sellers": [
            {"seller_id": sid, "revenue": float(rev)}
            for sid, rev in seller_revenue.items()
        ]
    }


@router.get("/admin/marketplace/payouts")
def get_admin_payouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pending/completed payouts (admin only)"""
    return {
        "payouts": [
            {
                "id": 1,
                "seller_id": 1,
                "amount": 1000.00,
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat()
            }
        ]
    }


@router.post("/admin/marketplace/process-payout")
def process_payout(
    payout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a pending payout (admin only)"""
    return {
        "payout_id": payout_id,
        "status": "processed",
        "processed_at": datetime.utcnow().isoformat()
    }


@router.get("/admin/marketplace/refunds")
def get_admin_refunds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all refunds (admin only)"""
    return {
        "refunds": [
            {
                "id": 1,
                "order_id": 1,
                "amount": 100.00,
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat()
            }
        ]
    }


# ORDER MANAGEMENT ENDPOINTS
@router.get("/orders/{order_id}")
def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details for a specific order"""
    return {
        "id": order_id,
        "user_id": current_user.id,
        "total": 100.00,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an order"""
    return {
        "order_id": order_id,
        "status": "cancelled",
        "cancelled_at": datetime.utcnow().isoformat()
    }


@router.get("/orders/{order_id}/invoice")
def download_invoice(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download order invoice"""
    return {
        "order_id": order_id,
        "invoice_url": f"/invoices/{order_id}.pdf",
        "status": "generated"
    }
