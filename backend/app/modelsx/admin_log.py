from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.core.db import Base
from datetime import datetime


class AdminLog(Base):
    """
    Audit log for tracking all admin actions.
    Essential for compliance, security, and accountability.
    """
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Action details
    action = Column(String, nullable=False, index=True)  # e.g., "approve_mentor", "suspend_user"
    resource_type = Column(String, nullable=False, index=True)  # e.g., "mentor", "user", "session"
    resource_id = Column(Integer, nullable=True, index=True)  # ID of affected resource
    
    # Context
    details = Column(Text, nullable=True)  # JSON or text description
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
