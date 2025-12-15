"""
User Follow System API
Manage user relationships and social connections
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User
from app.modelsx.social import UserFollow, Notification


router = APIRouter(prefix="/users", tags=["user-social"])


# Follow a user
@router.post("/{user_id}/follow")
async def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Follow another user"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id,
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    # Create follow relationship
    follow = UserFollow(
        follower_id=current_user.id,
        following_id=user_id,
    )
    
    db.add(follow)
    
    # Create notification for followed user
    notification = Notification(
        user_id=user_id,
        notification_type="follow",
        title=f"{current_user.username} started following you",
        description=f"Check out their profile and solutions!",
        related_user_id=current_user.id,
    )
    db.add(notification)
    
    db.commit()
    db.refresh(follow)
    
    return {
        "message": "Successfully followed user",
        "followed_at": follow.followed_at.isoformat(),
    }


# Unfollow a user
@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unfollow a user"""
    follow = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id,
    ).first()
    
    if not follow:
        raise HTTPException(status_code=404, detail="Not following this user")
    
    db.delete(follow)
    db.commit()
    
    return {"message": "Successfully unfollowed user"}


# Get user's followers
@router.get("/{username}/followers")
async def get_followers(
    username: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get list of users following a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(UserFollow).filter(
        UserFollow.following_id == user.id
    ).order_by(desc(UserFollow.followed_at))
    
    total = query.count()
    follows = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "followers": [
            {
                "id": f.follower.id,
                "username": f.follower.username,
                "followed_at": f.followed_at.isoformat(),
            }
            for f in follows
        ]
    }


# Get user's following list
@router.get("/{username}/following")
async def get_following(
    username: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get list of users a user is following"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(UserFollow).filter(
        UserFollow.follower_id == user.id
    ).order_by(desc(UserFollow.followed_at))
    
    total = query.count()
    follows = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "following": [
            {
                "id": f.following.id,
                "username": f.following.username,
                "followed_at": f.followed_at.isoformat(),
            }
            for f in follows
        ]
    }


# Check if following a user
@router.get("/{user_id}/is-following")
async def is_following(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if current user is following a user"""
    follow = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id,
    ).first()
    
    return {"is_following": follow is not None}


# Get notifications
@router.get("/me/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's notifications"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    query = query.order_by(desc(Notification.created_at))
    
    total = query.count()
    notifications = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "unread_count": db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count(),
        "notifications": [
            {
                "id": n.id,
                "type": n.notification_type,
                "title": n.title,
                "description": n.description,
                "is_read": n.is_read,
                "related_user": {
                    "id": n.related_user.id,
                    "username": n.related_user.username,
                } if n.related_user else None,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ]
    }


# Mark notification as read
@router.post("/notifications/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Marked as read"}


# Mark all notifications as read
@router.post("/me/notifications/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    
    db.commit()
    
    return {"message": "All notifications marked as read"}
