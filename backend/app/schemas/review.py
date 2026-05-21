"""
Product Review Schemas - Pydantic models for review operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    """Schema for creating a review"""
    product_id: int = Field(..., gt=0, description="Product ID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    text: Optional[str] = Field(None, description="Review text/comment")


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    text: Optional[str] = Field(None, description="Review text/comment")


class ReviewResponse(BaseModel):
    """Schema for review response"""
    id: int
    product_id: int
    reviewer_id: int
    reviewer_name: Optional[str] = None
    reviewer_avatar: Optional[str] = None
    
    rating: int
    title: Optional[str]
    text: Optional[str]
    
    is_verified_purchase: bool
    is_approved: bool
    
    helpful_count: int
    unhelpful_count: int
    
    seller_response: Optional[str]
    seller_response_at: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Schema for paginated review list"""
    reviews: List[ReviewResponse]
    total: int = Field(..., ge=0, description="Total reviews")
    skip: int = Field(..., ge=0, description="Items skipped")
    limit: int = Field(..., gt=0, description="Items returned")
    average_rating: float = Field(..., ge=0, le=5, description="Average rating")
    rating_distribution: dict = Field(..., description="Count of each rating (1-5)")


class ReviewDeleteResponse(BaseModel):
    """Schema for delete response"""
    success: bool
    message: str


class ReviewHelpfulResponse(BaseModel):
    """Schema for helpful vote response"""
    review_id: int
    helpful_count: int
    unhelpful_count: int
    user_vote: Optional[bool] = None  # True=helpful, False=unhelpful, None=no vote


class ProductRatingResponse(BaseModel):
    """Schema for product rating summary"""
    product_id: int
    average_rating: float = Field(..., ge=0, le=5)
    total_reviews: int = Field(..., ge=0)
    rating_distribution: dict  # {"1": 0, "2": 2, "3": 5, "4": 15, "5": 28}
    verified_reviews: int = Field(..., ge=0, description="Count of verified purchase reviews")


class SellerResponseSchema(BaseModel):
    """Schema for seller response to review"""
    response_text: str = Field(..., min_length=1, max_length=1000, description="Seller's response")
