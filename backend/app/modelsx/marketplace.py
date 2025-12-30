"""
Marketplace Extensions Models
Supports advanced marketplace features, digital products, seller accounts, and transactions
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Float, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from app.core.db import Base


class DigitalProductType(str, Enum):
    """Types of digital products"""
    COURSE = "course"
    TEMPLATE = "template"
    BUNDLE = "bundle"
    RESOURCE = "resource"
    TOOL = "tool"
    CONSULTATION = "consultation"


class ProductStatus(str, Enum):
    """Product status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class DigitalProduct(Base):
    """
    Digital products for sale in marketplace
    """
    __tablename__ = "digital_products"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Product details
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    
    # Product metadata
    product_type = Column(SQLEnum(DigitalProductType), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    tags = Column(JSON, default=[])
    thumbnail_url = Column(String(500), nullable=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)  # For discounts
    currency = Column(String(3), default="USD")
    
    # Content
    content_url = Column(String(500), nullable=True)  # S3, Google Drive, etc
    preview_url = Column(String(500), nullable=True)
    file_size_mb = Column(Float, nullable=True)
    
    # Status and visibility
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT)
    is_featured = Column(Boolean, default=False)
    visibility = Column(String(20), default="public")  # "public", "private", "listed"
    
    # Metadata
    requirements = Column(JSON, default=[])  # Prerequisites, skills needed
    features = Column(JSON, default=[])  # Key features/benefits
    extra_data = Column(JSON, default={})  # Custom fields
    
    # Statistics
    sales_count = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    seller = relationship("User", foreign_keys=[seller_id])
    
    __table_args__ = (
        Index("ix_digital_product_seller", "seller_id", "status"),
        Index("ix_digital_product_category", "category", "status"),
    )


class ProductPurchase(Base):
    """
    Purchase transaction for digital products
    """
    __tablename__ = "product_purchases"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("digital_products.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Purchase details
    purchase_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Payment details
    payment_method = Column(String(50), nullable=True)  # "stripe", "paypal", "coins"
    transaction_id = Column(String(100), nullable=True, unique=True)
    
    # Status
    status = Column(String(20), default="completed")  # "pending", "completed", "refunded", "cancelled"
    
    # Delivery
    delivered_at = Column(DateTime, nullable=True)
    download_url = Column(String(500), nullable=True)
    download_count = Column(Integer, default=0)
    
    # Refund tracking
    refunded_at = Column(DateTime, nullable=True)
    refund_reason = Column(String(200), nullable=True)
    
    # Commission/payout
    platform_fee = Column(Float, default=0.0)  # Platform takes percentage
    seller_payout = Column(Float, default=0.0)
    
    # Timestamps
    purchased_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    product = relationship("DigitalProduct", foreign_keys=[product_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller_rel = relationship("User", foreign_keys=[seller_id])
    
    __table_args__ = (
        Index("ix_product_purchase_buyer", "buyer_id", "purchased_at"),
        Index("ix_product_purchase_status", "status"),
    )


class ProductReview(Base):
    """
    Reviews and ratings for digital products
    """
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("digital_products.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Review content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Rating
    overall_rating = Column(Float, nullable=False)  # 1-5
    quality_rating = Column(Float, nullable=True)
    value_rating = Column(Float, nullable=True)
    support_rating = Column(Float, nullable=True)
    
    # Review status
    is_verified = Column(Boolean, default=False)  # Verified purchaser
    is_featured = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("DigitalProduct", foreign_keys=[product_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    __table_args__ = (
        Index("ix_product_review_product", "product_id", "created_at"),
    )


class SellerAccount(Base):
    """
    Seller account management and verification
    """
    __tablename__ = "seller_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Seller status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    verification_date = Column(DateTime, nullable=True)
    
    # Seller information
    store_name = Column(String(200), nullable=True)
    store_description = Column(Text, nullable=True)
    store_url = Column(String(500), nullable=True)
    
    # Contact and payout
    seller_email = Column(String(100), nullable=True)
    payout_method = Column(String(50), nullable=True)  # "bank_transfer", "paypal", "stripe"
    payout_account = Column(String(200), nullable=True)  # Encrypted
    
    # Verification documents
    tax_id = Column(String(100), nullable=True)  # Encrypted
    identification_verified = Column(Boolean, default=False)
    bank_verified = Column(Boolean, default=False)
    
    # Statistics
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_payouts = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    
    # Seller tier
    seller_tier = Column(String(30), default="basic")  # "basic", "professional", "premium"
    commission_rate = Column(Float, default=0.3)  # 30% platform fee
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class ProductBundle(Base):
    """
    Bundle multiple products for sale
    """
    __tablename__ = "product_bundles"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Bundle details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(200), nullable=False, unique=True)
    
    # Products in bundle
    product_ids = Column(JSON, default=[])  # List of product IDs
    
    # Pricing
    bundle_price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=False)  # Sum of individual prices
    discount_percentage = Column(Float, default=0.0)
    
    # Statistics
    sales_count = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id])


class SellerPayout(Base):
    """
    Payout tracking for sellers
    """
    __tablename__ = "seller_payouts"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Payout period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Payout amount
    total_sales = Column(Float, default=0.0)
    platform_fee = Column(Float, default=0.0)
    payout_amount = Column(Float, default=0.0)  # After fees
    
    # Payout status
    status = Column(String(20), default="pending")  # "pending", "processing", "completed", "failed"
    
    # Payout details
    payout_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    seller = relationship("User", foreign_keys=[seller_id])
    
    __table_args__ = (
        Index("ix_seller_payout_seller", "seller_id", "period_start"),
        Index("ix_seller_payout_status", "status"),
    )


class MarketplaceAnalytics(Base):
    """
    Platform-wide marketplace analytics
    """
    __tablename__ = "marketplace_analytics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    period_date = Column(DateTime, default=datetime.utcnow, unique=True)
    
    # Sales metrics
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    average_order_value = Column(Float, default=0.0)
    
    # User metrics
    unique_buyers = Column(Integer, default=0)
    unique_sellers = Column(Integer, default=0)
    new_sellers = Column(Integer, default=0)
    
    # Product metrics
    total_products = Column(Integer, default=0)
    products_sold = Column(Integer, default=0)
    featured_products = Column(Integer, default=0)
    
    # Category distribution
    sales_by_category = Column(JSON, default={})
    products_by_category = Column(JSON, default={})
    
    # Top performers
    top_products = Column(JSON, default=[])  # Top 10 product IDs
    top_sellers = Column(JSON, default=[])  # Top 10 seller IDs
    
    # Trends
    growth_rate = Column(Float, default=0.0)  # Week-over-week
    churn_rate = Column(Float, default=0.0)  # Seller churn
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
