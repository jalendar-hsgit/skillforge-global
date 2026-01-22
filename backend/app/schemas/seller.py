"""
Seller Portal Schemas
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class SellerProductBasic(BaseModel):
    """Basic product info for seller view"""
    id: int
    name: str
    slug: str
    price: float
    sales_count: int
    total_revenue: float
    average_rating: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SellerOrderBasic(BaseModel):
    """Basic order info for seller view"""
    id: int
    order_number: str
    amount: float
    status: str
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SellerDashboard(BaseModel):
    """Seller dashboard overview"""
    total_sales: int
    total_revenue: float
    average_rating: float
    total_products: int
    recent_orders: List[SellerOrderBasic]
    top_products: List[SellerProductBasic]
    
    class Config:
        from_attributes = True


class SellerOrders(BaseModel):
    """List of seller's orders"""
    total: int
    orders: List[SellerOrderBasic]
    
    class Config:
        from_attributes = True


class PayoutRequest(BaseModel):
    """Payout request schema"""
    amount: float
    reason: Optional[str] = None


class SellerPayout(BaseModel):
    """Seller payout info"""
    id: int
    seller_id: int
    amount: float
    status: str  # pending, processing, completed, failed
    request_date: datetime
    processed_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SellerAnalyticsTimeline(BaseModel):
    """Revenue timeline data"""
    date: str  # YYYY-MM-DD
    revenue: float
    sales_count: int
    
    class Config:
        from_attributes = True


class SellerAnalyticsProducts(BaseModel):
    """Product performance analytics"""
    product_id: int
    product_name: str
    sales_count: int
    revenue: float
    average_rating: float
    views_count: int
    
    class Config:
        from_attributes = True
