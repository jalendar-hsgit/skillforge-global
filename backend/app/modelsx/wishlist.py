"""
Wishlist Model - User product wishlists
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base


class Wishlist(Base):
    """
    Wishlist model for storing user product wishlists.
    
    A user can add products to their wishlist for later purchase.
    Each wishlist item is unique per user per product.
    
    Relationships:
    - user: User who owns the wishlist
    - product: DigitalProduct in the wishlist
    """
    
    __tablename__ = "wishlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("digital_products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    product = relationship("DigitalProduct")
    
    # Unique constraint: user can only add same product once
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_user_product_wishlist"),)
    
    def __repr__(self):
        return f"<Wishlist(user_id={self.user_id}, product_id={self.product_id}, created_at={self.created_at})>"
