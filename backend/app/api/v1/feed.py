"""
Social Feed API Router - Phase 3.3
User activity stream and social feed
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models import User
from app.modelsx.social import SocialFeedItem
from app.schemas.social_schemas import SocialFeedItemResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=List[SocialFeedItemResponse])
def get_social_feed(
    feed_type: str = "all",
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social feed for current user"""
    query = db.query(SocialFeedItem)
    
    if feed_type == "personal":
        # Only user's own activities
        query = query.filter(SocialFeedItem.user_id == current_user.id)
    elif feed_type == "following":
        # Activities from followed users (requires UserFollow relationship)
        # This would need to join with UserFollow table
        pass
    elif feed_type == "all":
        # Public activities from all users
        query = query.filter(SocialFeedItem.visibility == "public")
    
    feed_items = query.order_by(
        desc(SocialFeedItem.created_at)
    ).offset(skip).limit(limit).all()
    
    return feed_items


@router.get("/user/{user_id}", response_model=List[SocialFeedItemResponse])
def get_user_feed(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feed for specific user"""
    feed_items = db.query(SocialFeedItem).filter(
        SocialFeedItem.user_id == user_id,
        SocialFeedItem.visibility == "public"
    ).order_by(
        desc(SocialFeedItem.created_at)
    ).offset(skip).limit(limit).all()
    
    return feed_items


@router.post("/", response_model=SocialFeedItemResponse, status_code=status.HTTP_201_CREATED)
def create_feed_item(
    activity_type: str,
    title: str,
    description: str = None,
    related_id: int = None,
    metadata: dict = None,
    visibility: str = "public",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create social feed item (internal use)"""
    new_item = SocialFeedItem(
        user_id=current_user.id,
        activity_type=activity_type,
        title=title,
        description=description,
        related_id=related_id,
        metadata=metadata,
        visibility=visibility
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.post("/{feed_item_id}/like")
def like_feed_item(
    feed_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a feed item"""
    item = db.query(SocialFeedItem).filter(SocialFeedItem.id == feed_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    
    item.like_count += 1
    db.commit()
    db.refresh(item)
    return {"like_count": item.like_count}


@router.post("/{feed_item_id}/unlike")
def unlike_feed_item(
    feed_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlike a feed item"""
    item = db.query(SocialFeedItem).filter(SocialFeedItem.id == feed_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    
    item.like_count = max(0, item.like_count - 1)
    db.commit()
    db.refresh(item)
    return {"like_count": item.like_count}


@router.get("/trending", response_model=List[SocialFeedItemResponse])
def get_trending_feed(
    days: int = 7,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trending feed items"""
    from sqlalchemy import and_
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    feed_items = db.query(SocialFeedItem).filter(
        and_(
            SocialFeedItem.visibility == "public",
            SocialFeedItem.created_at >= cutoff_date
        )
    ).order_by(
        desc(SocialFeedItem.like_count + SocialFeedItem.comment_count)
    ).limit(limit).all()
    
    return feed_items


@router.delete("/{feed_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed_item(
    feed_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete feed item (author only)"""
    item = db.query(SocialFeedItem).filter(SocialFeedItem.id == feed_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    
    if item.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")
    
    db.delete(item)
    db.commit()
