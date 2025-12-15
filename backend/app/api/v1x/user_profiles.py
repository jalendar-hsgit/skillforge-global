"""
User Profiles API
Public profiles, statistics, activity feeds
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User
from app.modelsx.user_profiles import UserProfile, UserActivity, UserPreferences, UserStatistics


router = APIRouter(prefix="/profiles", tags=["user-profiles"])


# Get current user's profile
@router.get("/me")
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile with full details"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    stats = db.query(UserStatistics).filter(UserStatistics.user_id == current_user.id).first()
    
    if not profile:
        # Create profile if doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    if not stats:
        stats = UserStatistics(user_id=current_user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "bio": profile.bio,
        "location": profile.location,
        "company": profile.company,
        "job_title": profile.job_title,
        "avatar_url": profile.avatar_url,
        "cover_image_url": profile.cover_image_url,
        "website": profile.website,
        "joined_date": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None,
        "statistics": {
            "challenges_completed": stats.challenges_completed,
            "solutions_shared": stats.solutions_shared,
            "current_streak": stats.current_daily_streak,
            "longest_streak": stats.longest_daily_streak,
            "success_rate": stats.success_rate,
            "global_rank": stats.global_rank,
            "total_coins": stats.coins_balance,
        },
        "badges": profile.badges or [],
        "is_public": profile.is_public,
    }


# Update user profile
@router.put("/me")
async def update_my_profile(
    bio: Optional[str] = None,
    location: Optional[str] = None,
    company: Optional[str] = None,
    job_title: Optional[str] = None,
    website: Optional[str] = None,
    avatar_url: Optional[str] = None,
    cover_image_url: Optional[str] = None,
    theme_preference: Optional[str] = None,
    preferred_language: Optional[str] = None,
    is_public: Optional[bool] = None,
    show_statistics: Optional[bool] = None,
    show_activity: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update fields if provided
    if bio is not None:
        profile.bio = bio
    if location is not None:
        profile.location = location
    if company is not None:
        profile.company = company
    if job_title is not None:
        profile.job_title = job_title
    if website is not None:
        profile.website = website
    if avatar_url is not None:
        profile.avatar_url = avatar_url
    if cover_image_url is not None:
        profile.cover_image_url = cover_image_url
    if theme_preference is not None:
        profile.theme_preference = theme_preference
    if preferred_language is not None:
        profile.preferred_language = preferred_language
    if is_public is not None:
        profile.is_public = is_public
    if show_statistics is not None:
        profile.show_statistics = show_statistics
    if show_activity is not None:
        profile.show_activity = show_activity
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    
    return {"message": "Profile updated successfully"}


# Get public profile by username
@router.get("/users/{username}")
async def get_user_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get public profile of any user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    stats = db.query(UserStatistics).filter(UserStatistics.user_id == user.id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check visibility
    if not profile.is_public and (not current_user or current_user.id != user.id):
        raise HTTPException(status_code=403, detail="Profile is private")
    
    return {
        "id": user.id,
        "username": user.username,
        "bio": profile.bio,
        "location": profile.location,
        "company": profile.company,
        "job_title": profile.job_title,
        "avatar_url": profile.avatar_url,
        "cover_image_url": profile.cover_image_url,
        "website": profile.website,
        "joined_date": user.created_at.isoformat() if hasattr(user, 'created_at') else None,
        "statistics": {
            "challenges_completed": stats.challenges_completed if stats else 0,
            "solutions_shared": stats.solutions_shared if stats else 0,
            "current_streak": stats.current_daily_streak if stats else 0,
            "longest_streak": stats.longest_daily_streak if stats else 0,
            "success_rate": stats.success_rate if stats else 0,
            "global_rank": stats.global_rank if stats else None,
            "total_coins": stats.coins_balance if stats else 0,
        } if profile.show_statistics else None,
        "badges": profile.badges or [],
    }


# Get user activity feed
@router.get("/users/{username}/activity")
async def get_user_activity(
    username: str,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get user's activity feed"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile or not profile.show_activity:
        raise HTTPException(status_code=403, detail="Activity feed not visible")
    
    # Get activity
    query = db.query(UserActivity).filter(
        UserActivity.user_id == user.id,
        UserActivity.is_public == True
    ).order_by(desc(UserActivity.created_at))
    
    total = query.count()
    activities = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "activity": [
            {
                "id": activity.id,
                "type": activity.activity_type,
                "description": activity.description,
                "data": activity.activity_data,
                "created_at": activity.created_at.isoformat(),
            }
            for activity in activities
        ]
    }


# Get user statistics
@router.get("/users/{username}/statistics")
async def get_user_statistics(
    username: str,
    db: Session = Depends(get_db),
):
    """Get detailed user statistics"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    stats = db.query(UserStatistics).filter(UserStatistics.user_id == user.id).first()
    
    if not profile or not profile.show_statistics:
        raise HTTPException(status_code=403, detail="Statistics not visible")
    
    if not stats:
        stats = UserStatistics(user_id=user.id)
    
    return {
        "user": username,
        "challenges": {
            "attempted": stats.challenges_attempted,
            "completed": stats.challenges_completed,
            "perfect": stats.challenges_perfect,
            "success_rate": stats.success_rate,
            "by_difficulty": {
                "easy": stats.easy_solved,
                "medium": stats.medium_solved,
                "hard": stats.hard_solved,
            }
        },
        "solutions": {
            "shared": stats.solutions_shared,
            "helpful_votes": stats.solutions_helpful_votes,
            "unhelpful_votes": stats.solutions_unhelpful_votes,
            "avg_rating": stats.avg_solution_rating,
        },
        "streaks": {
            "current": stats.current_daily_streak,
            "longest": stats.longest_daily_streak,
        },
        "languages": {
            "most_used": stats.most_used_language,
            "breakdown": stats.languages_used or {},
        },
        "time": {
            "total_minutes": stats.total_time_spent_minutes,
            "avg_per_challenge": stats.avg_time_per_challenge_minutes,
        },
        "coins": {
            "earned": stats.total_coins_earned,
            "spent": stats.total_coins_spent,
            "balance": stats.coins_balance,
        },
        "ranking": {
            "global_rank": stats.global_rank,
            "percentile": stats.percentile,
        }
    }


# Update user preferences
@router.put("/preferences")
async def update_preferences(
    notify_challenge_reminders: Optional[bool] = None,
    notify_streak_achievements: Optional[bool] = None,
    notify_solution_votes: Optional[bool] = None,
    notify_comments: Optional[bool] = None,
    notify_friend_activity: Optional[bool] = None,
    preferred_difficulty: Optional[str] = None,
    show_hints_automatically: Optional[bool] = None,
    daily_challenge_enabled: Optional[bool] = None,
    allow_tracking: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user preferences"""
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
    
    # Update fields if provided
    if notify_challenge_reminders is not None:
        prefs.notify_challenge_reminders = notify_challenge_reminders
    if notify_streak_achievements is not None:
        prefs.notify_streak_achievements = notify_streak_achievements
    if notify_solution_votes is not None:
        prefs.notify_solution_votes = notify_solution_votes
    if notify_comments is not None:
        prefs.notify_comments = notify_comments
    if notify_friend_activity is not None:
        prefs.notify_friend_activity = notify_friend_activity
    if preferred_difficulty is not None:
        prefs.preferred_difficulty = preferred_difficulty
    if show_hints_automatically is not None:
        prefs.show_hints_automatically = show_hints_automatically
    if daily_challenge_enabled is not None:
        prefs.daily_challenge_enabled = daily_challenge_enabled
    if allow_tracking is not None:
        prefs.allow_tracking = allow_tracking
    
    prefs.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Preferences updated"}


# Get user preferences
@router.get("/preferences")
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user preferences"""
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return {
        "notifications": {
            "challenge_reminders": prefs.notify_challenge_reminders,
            "streak_achievements": prefs.notify_streak_achievements,
            "solution_votes": prefs.notify_solution_votes,
            "comments": prefs.notify_comments,
            "friend_activity": prefs.notify_friend_activity,
        },
        "learning": {
            "preferred_difficulty": prefs.preferred_difficulty,
            "show_hints_automatically": prefs.show_hints_automatically,
            "daily_challenge_enabled": prefs.daily_challenge_enabled,
        },
        "privacy": {
            "allow_tracking": prefs.allow_tracking,
        }
    }


# Get leaderboard (top users by rank)
@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(100, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get global user leaderboard"""
    query = db.query(UserStatistics).filter(
        UserStatistics.global_rank.isnot(None)
    ).order_by(UserStatistics.global_rank)
    
    total = query.count()
    users = query.offset(offset).limit(limit).all()
    
    result = []
    for stat in users:
        user = db.query(User).filter(User.id == stat.user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == stat.user_id).first()
        
        if user and profile and profile.is_public:
            result.append({
                "rank": stat.global_rank,
                "username": user.username,
                "avatar_url": profile.avatar_url,
                "challenges_completed": stat.challenges_completed,
                "solutions_shared": stat.solutions_shared,
                "current_streak": stat.current_daily_streak,
                "coins": stat.coins_balance,
                "percentile": stat.percentile,
            })
    
    return {
        "total": total,
        "leaderboard": result
    }
