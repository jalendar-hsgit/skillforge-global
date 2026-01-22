"""
Wishlist Schemas - Pydantic models for wishlist operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class WishlistItemBase(BaseModel):
    """Base wishlist item schema"""
    product_id: int = Field(..., gt=0, description="Product ID to add to wishlist")


class WishlistItemCreate(WishlistItemBase):
    """Schema for creating wishlist item"""
    pass


class WishlistItemResponse(WishlistItemBase):
    """Schema for wishlist item response"""
    id: int
    user_id: int
    created_at: datetime
    
    # Product details
    product_name: Optional[str] = None
    product_slug: Optional[str] = None
    product_price: Optional[float] = None
    product_type: Optional[str] = None
    product_status: Optional[str] = None
    seller_id: Optional[int] = None
    seller_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class WishlistResponse(BaseModel):
    """Schema for full wishlist response"""
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class WishlistListResponse(BaseModel):
    """Schema for paginated wishlist list response"""
    items: List[WishlistItemResponse]
    total: int = Field(..., ge=0, description="Total wishlist items")
    skip: int = Field(..., ge=0, description="Items skipped")
    limit: int = Field(..., gt=0, description="Items returned")
    
    class Config:
        from_attributes = True


class WishlistCountResponse(BaseModel):
    """Schema for wishlist count response"""
    count: int = Field(..., ge=0, description="Number of items in wishlist")
    user_id: int = Field(..., gt=0, description="User ID")


class WishlistDeleteResponse(BaseModel):
    """Schema for delete response"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Response message")
    product_id: int = Field(..., description="Product ID that was removed")


class WishlistCheckResponse(BaseModel):
    """Schema for checking if product is in wishlist"""
    in_wishlist: bool = Field(..., description="Whether product is in user's wishlist")
    product_id: int = Field(..., description="Product ID")
