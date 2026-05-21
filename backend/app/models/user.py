from sqlalchemy import Column, Integer, String, DateTime, func, Enum as SQLEnum, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration for role-based access control"""
    USER = "USER"           # Regular user
    MENTOR = "MENTOR"       # Can mentor (still needs mentor profile approval)
    ADMIN = "ADMIN"         # Platform administrator
    SUPERADMIN = "SUPERADMIN"  # Full system access


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Profile Information
    name = Column(String, nullable=True)  # User's full name
    bio = Column(Text, nullable=True)  # User's bio/about section
    avatar_url = Column(String, nullable=True)  # Profile picture URL
    phone = Column(String, nullable=True)  # Phone number
    location = Column(String, nullable=True)  # City, country
    skills = Column(JSON, default=[])  # List of skill tags ["Python", "Web Dev", etc.]
    
    # Statistics
    sessions_completed = Column(Integer, default=0)  # For students
    avg_rating = Column(Float, default=0.0)  # Average mentor rating
    total_hours = Column(Float, default=0.0)  # Total learning/mentoring hours
    
    # Preferences
    bio_visibility = Column(String, default="public")  # public, private, friends_only
    receive_notifications = Column(String, default="all")  # all, important, none
    
    # Settings (for settings page)
    email_notifications = Column(Integer, default=1)  # Boolean: 1=True, 0=False
    push_notifications = Column(Integer, default=1)
    two_factor_enabled = Column(Integer, default=0)
    theme = Column(String, default="auto")  # auto, dark, light
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    profile_visibility = Column(String, default="public")  # public, private, friends
    activity_status = Column(Integer, default=1)
    
    # Timestamps
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Note: Relationships to Wishlist, ProductReview, Mentor and Subscription models 
    # are defined in those models (via back_populates) to avoid circular import issues 
    # (those models are in modelsx/, not models/)
