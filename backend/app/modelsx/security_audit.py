"""
Security audit and logging models for tracking user actions and sessions
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime


class LoginHistory(Base):
    """Track user login sessions for security and audit purposes"""
    
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    device = Column(String(100), nullable=True)  # e.g., "Chrome on Windows", "Safari on iOS"
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    logout_time = Column(DateTime, nullable=True)
    success = Column(Boolean, default=True, nullable=False)  # False if login attempt failed
    failure_reason = Column(String(255), nullable=True)  # Why login failed (invalid creds, etc)
    
    # Relationship
    user = relationship("User", foreign_keys=[user_id])
    
    class Config:
        from_attributes = True


class AuditLog(Base):
    """System-wide audit trail for admin actions and sensitive operations"""
    
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., "USER_CREATED", "PASSWORD_CHANGED", "ADMIN_PANEL_ACCESS"
    resource_type = Column(String(50), nullable=False, index=True)  # e.g., "user", "course", "mentor", "admin_setting"
    resource_id = Column(Integer, nullable=True, index=True)  # ID of the resource affected
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    details = Column(JSON, nullable=True)  # Additional context (old_value, new_value, etc)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), default="success", nullable=False)  # "success", "failure", "warning"
    
    # Relationship
    user = relationship("User", foreign_keys=[user_id])
    
    class Config:
        from_attributes = True


class SessionRevocation(Base):
    """Track revoked sessions for explicit logout"""
    
    __tablename__ = "session_revocation"
    
    id = Column(Integer, primary_key=True)
    login_history_id = Column(Integer, ForeignKey("login_history.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_by_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)  # Admin who revoked it
    reason = Column(String(255), nullable=True)  # Why it was revoked
    
    # Relationships
    login_history = relationship("LoginHistory", foreign_keys=[login_history_id])
    user = relationship("User", foreign_keys=[user_id], primaryjoin="SessionRevocation.user_id == User.id")
    revoked_by_user = relationship("User", foreign_keys=[revoked_by_user_id], primaryjoin="SessionRevocation.revoked_by_user_id == User.id")
    
    class Config:
        from_attributes = True
