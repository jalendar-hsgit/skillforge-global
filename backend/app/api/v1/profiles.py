"""
User Profile API Router - Phase 3.3
User profiles and social profiles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models import User
from app.modelsx.social import UserProfile, UserFollow
from app.schemas.social_schemas import (
    UserProfileResponse, UserProfileCreate, UserProfileUpdate
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        # Create default profile if doesn't exist
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


@router.post("/", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create user profile"""
    # Check if profile already exists
    existing = db.query(UserProfile).filter(UserProfile.user_id == profile_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    new_profile = UserProfile(**profile_data.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.patch("/me", response_model=UserProfileResponse)
def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()
    
    update_fields = profile_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("/{user_id}", response_model=UserProfileResponse)
def update_user_profile(
    user_id: int,
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile (self or admin)"""
    if user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_fields = profile_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{user_id}/followers", response_model=List[dict])
def get_user_followers(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's followers"""
    followers = db.query(UserFollow).filter(
        UserFollow.following_id == user_id
    ).offset(skip).limit(limit).all()
    
    return [{"id": f.follower_id, "followed_at": f.followed_at} for f in followers]


@router.get("/{user_id}/following", response_model=List[dict])
def get_user_following(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get users that user is following"""
    following = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id
    ).offset(skip).limit(limit).all()
    
    return [{"id": f.following_id, "followed_at": f.followed_at} for f in following]


@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    new_follow = UserFollow(
        follower_id=current_user.id,
        following_id=user_id
    )
    
    # Update follower/following counts
    follower_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if follower_profile:
        follower_profile.following_count += 1
    
    target_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if target_profile:
        target_profile.follower_count += 1
    
    db.add(new_follow)
    db.commit()
    
    return {"status": "following", "user_id": user_id}


@router.post("/{user_id}/unfollow")
def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    follow = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id
    ).first()
    
    if not follow:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    # Update follower/following counts
    follower_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if follower_profile:
        follower_profile.following_count = max(0, follower_profile.following_count - 1)
    
    target_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if target_profile:
        target_profile.follower_count = max(0, target_profile.follower_count - 1)
    
    db.delete(follow)
    db.commit()
    
    return {"status": "unfollowed", "user_id": user_id}


@router.get("/{user_id}/is-following", response_model=dict)
def is_following(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user is following target user"""
    follow = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id
    ).first()
    
    return {"is_following": follow is not None}
