from sqlalchemy import Column, Integer, String, DateTime, func, Enum as SQLEnum
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

    # Note: Relationships to Mentor and Subscription models are defined in those models
    # to avoid circular import issues (those models are in modelsx/, not models/)
