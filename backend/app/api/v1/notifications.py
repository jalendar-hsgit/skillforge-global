"""
Notifications API Router - Phase 3.3
User notifications and activity alerts
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models import User
from app.modelsx.notifications import Notification
from app.schemas.social_schemas import (
    NotificationResponse, NotificationMarkReadRequest,
    NotificationMarkArchivedRequest, NotificationSummary
)
from app.api.deps import get_current_user
from app.services.realtime_events import on_notification_created

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationSummary)
def get_notifications(
    status_filter: str = "unread",
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    if status_filter == "unread":
        query = query.filter(Notification.is_read == False)
    elif status_filter == "read":
        query = query.filter(Notification.is_read == True)
    elif status_filter == "archived":
        query = query.filter(Notification.status == "archived")
    
    total_count = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    notifications = query.order_by(
        desc(Notification.created_at)
    ).offset(skip).limit(limit).all()
    
    return {
        "unread_count": unread_count,
        "total_count": total_count,
        "notifications": notifications
    }


@router.post("/mark-read")
def mark_notifications_read(
    request: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notifications as read"""
    notifications = db.query(Notification).filter(
        Notification.id.in_(request.notification_ids),
        Notification.user_id == current_user.id
    ).all()
    
    for notif in notifications:
        notif.is_read = True
        notif.read_at = datetime.utcnow()
    
    db.commit()
    return {"marked": len(notifications)}


@router.post("/mark-archived")
def mark_notifications_archived(
    request: NotificationMarkArchivedRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notifications as archived"""
    notifications = db.query(Notification).filter(
        Notification.id.in_(request.notification_ids),
        Notification.user_id == current_user.id
    ).all()
    
    for notif in notifications:
        notif.status = "archived"
    
    db.commit()
    return {"archived": len(notifications)}


@router.post("/mark-all-read")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()
    
    for notif in notifications:
        notif.is_read = True
        notif.read_at = datetime.utcnow()
    
    db.commit()
    return {"marked": len(notifications)}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()


@router.get("/count", response_model=dict)
def get_notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread notification count"""
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": unread_count}
