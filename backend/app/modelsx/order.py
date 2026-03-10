from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Boolean
from datetime import datetime
from app.core.db import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), index=True)
    
    # Order details
    order_number = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="pending")  # pending, completed, failed, refunded
    
    # Pricing
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    amount = Column(Numeric(10, 2), nullable=False)  # Total amount (for backward compatibility)
    currency = Column(String(10), default="USD")
    
    # Payment
    payment_method = Column(String)  # stripe, paypal, coins
    payment_id = Column(String)
    payment_intent_id = Column(String, nullable=True)  # Stripe PaymentIntent ID
    payment_status = Column(String)
    paid_at = Column(DateTime)
    
    # Coupon
    coupon_code = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course")
    user = relationship("User", backref="orders")


class Coupon(Base):
    """Discount coupons for course purchases"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    
    # Discount
    discount_type = Column(String, nullable=False)  # percentage, fixed
    discount_value = Column(Numeric(10, 2), nullable=False)
    max_discount_amount = Column(Numeric(10, 2))
    
    # Applicability
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    min_purchase_amount = Column(Numeric(10, 2))
    
    # Usage
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    per_user_limit = Column(Integer, default=1)
    
    # Validity
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course")


class CartItem(Base):
    """Shopping cart items (supports courses and digital products)"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    product_id = Column(Integer, ForeignKey("digital_products.id", ondelete="CASCADE"), nullable=True)
    
    price = Column(Numeric(10, 2), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    course = relationship("Course")
    product = relationship("DigitalProduct")


class OrderItem(Base):
    """Order items - tracks individual courses and digital products in an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(Integer, ForeignKey("digital_products.id", ondelete="SET NULL"), nullable=True)
    
    # Item pricing at time of purchase
    item_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, default=1)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", backref="items")
    course = relationship("Course")
    product = relationship("DigitalProduct")
