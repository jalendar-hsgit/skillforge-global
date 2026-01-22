"""
Product Review Model - Customer reviews and ratings for digital products
"""
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean, Index, UniqueConstraint, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base


class ProductReview(Base):
    """
    Product review model for storing customer reviews and ratings.
    
    Features:
    - Star ratings (1-5)
    - Review text/comments
    - Helpful votes tracking
    - Verified purchase checking
    - Seller responses
    
    Relationships:
    - reviewer: User who left the review
    - product: DigitalProduct being reviewed
    - helpful_votes: Users who marked as helpful
    """
    
    __tablename__ = "product_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("digital_products.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)
    text = Column(Text, nullable=True)
    
    # Verification & moderation
    is_verified_purchase = Column(Boolean, default=False)  # Was this product purchased?
    is_approved = Column(Boolean, default=True)  # Admin approval for moderation
    
    # Engagement metrics
    helpful_count = Column(Integer, default=0)
    unhelpful_count = Column(Integer, default=0)
    
    # Seller response
    seller_response = Column(Text, nullable=True)
    seller_response_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    reviewer = relationship("User")
    product = relationship("DigitalProduct")
    helpful_votes = relationship("ReviewHelpfulVote", back_populates="review", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        Index("ix_product_review_product_rating", "product_id", "rating"),
        Index("ix_product_review_reviewer", "reviewer_id"),
        Index("ix_product_review_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<ProductReview(product_id={self.product_id}, reviewer_id={self.reviewer_id}, rating={self.rating})>"


class ReviewHelpfulVote(Base):
    """
    Track users who marked a review as helpful or unhelpful.
    """
    
    __tablename__ = "review_helpful_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("product_reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Vote type
    is_helpful = Column(Boolean, nullable=False)  # True = helpful, False = unhelpful
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    review = relationship("ProductReview", back_populates="helpful_votes")
    user = relationship("User")
    
    # Unique constraint: one vote per user per review
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_helpful_vote_review_user"),
    )
    
    def __repr__(self):
        return f"<ReviewHelpfulVote(review_id={self.review_id}, user_id={self.user_id}, helpful={self.is_helpful})>"
