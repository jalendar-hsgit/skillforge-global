"""Notifications API endpoints."""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.notifications import (
    Notification, NotificationPreference, NotificationLog, NotificationTemplate,
    NotificationType, NotificationPriority
)
from app.schemas.notifications_executor import (
    NotificationCreate, NotificationResponse, NotificationListResponse,
    NotificationPreferenceUpdate, NotificationPreferenceResponse
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============ NOTIFICATION ENDPOINTS ============

@router.get("", response_model=NotificationListResponse)
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user notifications."""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    unread_count = db.query(Notification).filter(
        and_(Notification.user_id == current_user.id,
             Notification.is_read == False)
    ).count()
    
    notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    
    return {
        "unread_count": unread_count,
        "notifications": notifications
    }


@router.post("/{notification_id}/mark-read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark notification as read."""
    notification = db.query(Notification).filter(
        and_(Notification.id == notification_id,
             Notification.user_id == current_user.id)
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Marked as read"}


@router.post("/{notification_id}/read")
def mark_notification_read_alias(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark notification as read (alias endpoint for /mark-read)."""
    return mark_notification_read(notification_id, db, current_user)


@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        and_(Notification.user_id == current_user.id,
             Notification.is_read == False)
    ).update({
        Notification.is_read: True,
        Notification.read_at: datetime.utcnow()
    })
    db.commit()
    
    return {"message": "Marked all as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete notification."""
    notification = db.query(Notification).filter(
        and_(Notification.id == notification_id,
             Notification.user_id == current_user.id)
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted"}


@router.delete("")
def delete_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all notifications."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).delete()
    db.commit()
    
    return {"message": "All notifications deleted"}


# ============ NOTIFICATION PREFERENCES ============

@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notification preferences."""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        # Create default preferences
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_notification_preferences(
    prefs_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update notification preferences."""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)
    
    # Update fields
    update_data = prefs_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)
    
    prefs.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(prefs)
    
    return prefs


# ============ NOTIFICATION STATISTICS ============

@router.get("/stats")
def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notification statistics."""
    total = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()
    
    unread = db.query(Notification).filter(
        and_(Notification.user_id == current_user.id,
             Notification.is_read == False)
    ).count()
    
    # Count by type
    type_breakdown = {}
    for notif_type in NotificationType:
        count = db.query(Notification).filter(
            and_(Notification.user_id == current_user.id,
                 Notification.notification_type == notif_type)
        ).count()
        type_breakdown[notif_type.value] = count
    
    # Last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    last_week = db.query(Notification).filter(
        and_(Notification.user_id == current_user.id,
             Notification.created_at >= week_ago)
    ).count()
    
    return {
        "total_notifications": total,
        "unread_count": unread,
        "read_count": total - unread,
        "type_breakdown": type_breakdown,
        "notifications_last_7_days": last_week,
    }


# ============ ADMIN ENDPOINTS ============

@router.post("/send", response_model=NotificationResponse)
def send_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send notification to user (admin only)."""
    # TODO: Add admin permission check
    
    notification = Notification(
        **notification_data.dict(),
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # TODO: Trigger real-time notification via WebSocket
    
    return notification


@router.post("/broadcast", response_model=dict)
def broadcast_notification(
    notification_data: NotificationCreate,
    user_ids: List[int] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Broadcast notification to multiple users (admin only)."""
    # TODO: Add admin permission check
    
    if not user_ids:
        return {"message": "No users specified"}
    
    notifications = []
    for user_id in user_ids:
        notif = Notification(
            user_id=user_id,
            notification_type=notification_data.notification_type,
            title=notification_data.title,
            message=notification_data.message,
            priority=notification_data.priority,
            actor_id=notification_data.actor_id,
            related_type=notification_data.related_type,
            related_id=notification_data.related_id,
            action_url=notification_data.action_url,
            extra_data=notification_data.extra_data,
            created_at=datetime.utcnow()
        )
        notifications.append(notif)
    
    db.add_all(notifications)
    db.commit()
    
    # TODO: Trigger real-time notifications via WebSocket
    
    return {
        "message": f"Notification sent to {len(notifications)} users",
        "count": len(notifications)
    }


@router.get("/templates", response_model=List[dict])
def get_notification_templates(
    db: Session = Depends(get_db),
):
    """Get all notification templates."""
    templates = db.query(NotificationTemplate).filter(
        NotificationTemplate.is_active == True
    ).all()
    return templates


@router.post("/templates", response_model=dict)
def create_notification_template(
    template_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create notification template (admin only)."""
    # TODO: Add admin permission check
    
    template = NotificationTemplate(
        **template_data,
        created_at=datetime.utcnow()
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template


# ============ REAL-TIME ENDPOINT (FOR WEBSOCKET INTEGRATION) ============

@router.get("/subscribe")
def subscribe_to_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Subscribe to real-time notifications via WebSocket."""
    # This endpoint prepares the connection
    # Actual WebSocket handling in websocket handler
    return {
        "message": "Ready for WebSocket connection",
        "user_id": current_user.id,
        "ws_endpoint": f"/ws/notifications/{current_user.id}"
    }
