"""Security-related endpoints (login history, audit logs, etc.)"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.core.db import get_db
from app.core.security import get_current_user, get_current_superadmin
from app.models.user import User
from app.modelsx.security_audit import LoginHistory, AuditLog, SessionRevocation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["security"])


class LoginHistoryItem(BaseModel):
    """Login history record"""
    id: Optional[int] = None
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_time: datetime
    logout_time: Optional[datetime] = None
    device: Optional[str] = None
    success: bool = True
    
    class Config:
        from_attributes = True


class AuditLogItem(BaseModel):
    """Audit log record"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    timestamp: datetime
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    status: str = "success"
    
    class Config:
        from_attributes = True


@router.get("/login-history", response_model=List[LoginHistoryItem])
def get_login_history(
    days: int = Query(30, ge=1, le=365, description="Number of days to fetch"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get login history for current user
    
    - Can fetch up to 365 days of history
    - Returns most recent logins first
    - Paginated results
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    history = db.query(LoginHistory).filter(
        and_(
            LoginHistory.user_id == current_user.id,
            LoginHistory.login_time >= cutoff_date
        )
    ).order_by(
        desc(LoginHistory.login_time)
    ).offset(offset).limit(limit).all()
    
    return history


@router.post("/login-history/{history_id}/revoke")
def revoke_session(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke/logout a specific session
    
    - Only user who owns the session or admin can revoke
    - Revoked sessions cannot be used
    """
    history = db.query(LoginHistory).filter(LoginHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check authorization: only user or superadmin can revoke
    if history.user_id != current_user.id and current_user.role not in ("ADMIN", "SUPERADMIN"):
        raise HTTPException(status_code=403, detail="Not authorized to revoke this session")
    
    # Check if already revoked
    existing_revoke = db.query(SessionRevocation).filter(
        SessionRevocation.login_history_id == history_id
    ).first()
    
    if existing_revoke:
        return {"revoked": True, "session_id": history_id, "already_revoked": True}
    
    # Create revocation record
    revocation = SessionRevocation(
        login_history_id=history_id,
        user_id=history.user_id,
        revoked_by_user_id=current_user.id,
        reason="User initiated logout"
    )
    
    db.add(revocation)
    db.commit()
    
    # Log the revocation
    log_action(
        db=db,
        user_id=current_user.id,
        action="SESSION_REVOKED",
        resource_type="login_history",
        resource_id=history_id,
        details={"revoked_session_id": history_id, "target_user": history.user_id}
    )
    
    return {"revoked": True, "session_id": history_id}


@router.get("/audit-logs", response_model=List[AuditLogItem])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Get system audit logs (admin only)
    
    - Requires SUPERADMIN role
    - Shows all user actions
    - Supports filtering by resource_type and action
    - Default 90 days of history
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(AuditLog).filter(AuditLog.timestamp >= cutoff_date)
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(
        desc(AuditLog.timestamp)
    ).offset(offset).limit(limit).all()
    
    return logs


def log_action(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    status: str = "success"
):
    """
    Log an action to audit trail (internal utility)
    
    Called by other endpoints to track changes.
    Does NOT require authentication - called from internal services.
    """
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            status=status,
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        logger.info(f"Audit: {action} by user {user_id} on {resource_type} {resource_id}")
        return {"logged": True}
    except Exception as e:
        logger.error(f"Failed to log action: {str(e)}")
        # Don't raise - audit failures shouldn't break the app
        return {"logged": False, "error": str(e)}


@router.post("/audit-logs")
def post_audit_log(
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Log an action to audit trail (internal use)
    
    Called by other endpoints to track changes
    """
    return log_action(
        db=db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )


def record_login_attempt(
    db: Session,
    user_id: int,
    ip_address: Optional[str],
    user_agent: Optional[str],
    device: Optional[str],
    success: bool = True,
    failure_reason: Optional[str] = None
):
    """
    Record a login attempt in the database
    
    Called by login endpoint after authentication attempt
    """
    try:
        login = LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device=device,
            success=success,
            failure_reason=failure_reason,
            login_time=datetime.utcnow()
        )
        db.add(login)
        db.commit()
        db.refresh(login)
        return login
    except Exception as e:
        logger.error(f"Failed to record login attempt: {str(e)}")
        return None
