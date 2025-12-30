"""
Marketplace Schemas for request/response validation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Product Type Enums
class ProductType(str):
    COURSE = "course"
    TEMPLATE = "template"
    BUNDLE = "bundle"
    RESOURCE = "resource"
    TOOL = "tool"
    CONSULTATION = "consultation"


class ProductStatus(str):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


# Digital Product Schemas
class DigitalProductCreate(BaseModel):
    name: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    product_type: str = Field(..., description="Type of product")
    category: str = Field(..., min_length=2, max_length=100)
    tags: List[str] = Field(default=[], max_items=10)
    
    price: float = Field(..., gt=0, le=10000)
    original_price: Optional[float] = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    
    thumbnail_url: Optional[str] = None
    content_url: Optional[str] = None
    preview_url: Optional[str] = None
    file_size_mb: Optional[float] = None
    
    requirements: List[str] = Field(default=[])
    features: List[str] = Field(default=[])
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Advanced Python Masterclass",
                "description": "Complete guide to mastering Python",
                "product_type": "course",
                "category": "programming",
                "price": 49.99,
                "requirements": ["Basic Python knowledge"],
                "features": ["Lifetime access", "30 video hours"]
            }
        }


class DigitalProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    
    price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = None
    
    thumbnail_url: Optional[str] = None
    requirements: Optional[List[str]] = None
    features: Optional[List[str]] = None


class DigitalProductResponse(BaseModel):
    id: int
    seller_id: int
    name: str
    slug: str
    description: str
    product_type: str
    category: str
    price: float
    currency: str
    
    status: str
    is_featured: bool
    
    sales_count: int
    total_revenue: float
    average_rating: float
    review_count: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DigitalProductDetailResponse(DigitalProductResponse):
    thumbnail_url: Optional[str]
    preview_url: Optional[str]
    content_url: Optional[str]
    features: List[str]
    requirements: List[str]
    views_count: int


class ProductListingResponse(BaseModel):
    products: List[DigitalProductResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Product Purchase Schemas
class ProductPurchaseCreate(BaseModel):
    product_id: int
    payment_method: str = Field(..., description="stripe, paypal, or coins")


class ProductPurchaseResponse(BaseModel):
    id: int
    product_id: int
    buyer_id: int
    purchase_price: float
    currency: str
    status: str
    purchased_at: datetime
    download_url: Optional[str]
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PurchaseHistoryResponse(BaseModel):
    purchases: List[ProductPurchaseResponse]
    total: int
    total_spent: float


# Product Review Schemas
class ProductReviewCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=20, max_length=2000)
    overall_rating: float = Field(..., ge=1, le=5)
    quality_rating: Optional[float] = Field(None, ge=1, le=5)
    value_rating: Optional[float] = Field(None, ge=1, le=5)
    support_rating: Optional[float] = Field(None, ge=1, le=5)


class ProductReviewResponse(BaseModel):
    id: int
    product_id: int
    reviewer_id: int
    title: str
    content: str
    overall_rating: float
    is_verified: bool
    helpful_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductReviewListResponse(BaseModel):
    reviews: List[ProductReviewResponse]
    total: int
    average_rating: float
    rating_distribution: Dict[int, int]  # Rating: count


# Seller Account Schemas
class SellerAccountCreate(BaseModel):
    store_name: str = Field(..., min_length=3, max_length=200)
    store_description: Optional[str] = Field(None, max_length=1000)
    payout_method: str = Field(..., description="bank_transfer, paypal, or stripe")


class SellerAccountResponse(BaseModel):
    id: int
    user_id: int
    is_verified: bool
    is_active: bool
    store_name: Optional[str]
    store_description: Optional[str]
    
    seller_tier: str
    total_sales: int
    total_revenue: float
    average_rating: float
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class SellerStoreResponse(BaseModel):
    store_info: SellerAccountResponse
    products: List[DigitalProductResponse]
    stats: Dict[str, Any]


# Product Bundle Schemas
class ProductBundleCreate(BaseModel):
    name: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    product_ids: List[int] = Field(..., min_items=2, max_items=50)
    bundle_price: float = Field(..., gt=0)


class ProductBundleResponse(BaseModel):
    id: int
    creator_id: int
    name: str
    slug: str
    product_ids: List[int]
    
    bundle_price: float
    original_price: float
    discount_percentage: float
    
    sales_count: int
    is_active: bool
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# Payout Schemas
class SellerPayoutResponse(BaseModel):
    id: int
    seller_id: int
    period_start: datetime
    period_end: datetime
    
    total_sales: float
    platform_fee: float
    payout_amount: float
    
    status: str
    requested_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PayoutHistoryResponse(BaseModel):
    payouts: List[SellerPayoutResponse]
    total_received: float
    pending_amount: float


# Marketplace Analytics Schemas
class MarketplaceAnalyticsResponse(BaseModel):
    period_date: datetime
    
    # Sales metrics
    total_sales: int
    total_revenue: float
    average_order_value: float
    
    # User metrics
    unique_buyers: int
    unique_sellers: int
    new_sellers: int
    
    # Product metrics
    total_products: int
    products_sold: int
    
    # Top performers
    top_products: List[int]
    top_sellers: List[int]
    
    # Trends
    growth_rate: float
    churn_rate: float
    
    class Config:
        from_attributes = True


# Search and Discovery Schemas
class MarketplaceSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    product_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    tags: Optional[List[str]] = None
    
    sort_by: str = Field(default="popularity")  # "popularity", "newest", "price_low", "price_high", "rating"
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class BestSellerResponse(BaseModel):
    product_id: int
    name: str
    price: float
    sales_count: int
    average_rating: float
    seller_name: str
    category: str
    sales_this_month: int
    revenue_rank: int


class SellerPerformanceResponse(BaseModel):
    seller_id: int
    store_name: str
    products_count: int
    total_sales: int
    total_revenue: float
    average_rating: float
    response_time_hours: float
    return_rate: float
    seller_tier: str
