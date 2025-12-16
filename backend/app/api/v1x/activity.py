"""
Social Activity and Feed API Endpoints
Supports activity tracking, user feeds, engagement, and trending content
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.activity import (
    Activity, ActivityLike, ActivityComment, FeedSettings, Trending, Timeline,
    ActivityType, ActivityVisibility
)
from app.schemas.activity import (
    ActivityCreate, ActivityResponse, ActivityListResponse,
    ActivityLikeResponse, ActivityCommentCreate, ActivityCommentResponse,
    FeedSettingsResponse, FeedSettingsUpdate, TrendingResponse,
    TimelineResponse, ActivityStatsResponse
)

router = APIRouter(prefix="/api/v1x/activity", tags=["activity"])


# ============================================================================
# ACTIVITY ENDPOINTS
# ============================================================================

@router.post("/", response_model=ActivityResponse)
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new activity record (called by system events)
    """
    db_activity = Activity(
        user_id=current_user.id,
        activity_type=activity.activity_type,
        related_type=activity.related_type,
        related_id=activity.related_id,
        title=activity.title,
        description=activity.description,
        points_earned=activity.points_earned or 0,
        extra_data=activity.extra_data or {},
        visibility=activity.visibility or ActivityVisibility.PUBLIC
    )
    
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Update timeline stats
    timeline = db.query(Timeline).filter(Timeline.user_id == current_user.id).first()
    if timeline:
        timeline.total_activities += 1
        timeline.total_points += db_activity.points_earned
        timeline.last_activity_at = datetime.utcnow()
        if activity.activity_type == ActivityType.CHALLENGE_SOLVED:
            timeline.challenges_solved += 1
        elif activity.activity_type == ActivityType.BADGE_EARNED:
            timeline.badges_earned += 1
        elif activity.activity_type == ActivityType.PATH_COMPLETED:
            timeline.paths_completed += 1
        db.commit()
    
    return db_activity


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific activity by ID
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check visibility
    if activity.visibility == ActivityVisibility.PRIVATE and activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Activity is private")
    
    # Increment view count
    activity.view_count += 1
    db.commit()
    
    return activity


@router.get("", response_model=ActivityListResponse)
async def list_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    activity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List activities with optional filters
    """
    query = db.query(Activity).filter(Activity.visibility != ActivityVisibility.PRIVATE)
    
    if activity_type:
        try:
            activity_type_enum = ActivityType(activity_type)
            query = query.filter(Activity.activity_type == activity_type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid activity type: {activity_type}")
    
    if user_id:
        query = query.filter(Activity.user_id == user_id)
    
    total = query.count()
    activities = query.order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()
    
    return ActivityListResponse(
        total=total,
        activities=activities
    )


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an activity (only owner or admin can delete)
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete own activities")
    
    db.delete(activity)
    db.commit()


# ============================================================================
# FEED ENDPOINTS (Personalized activity stream)
# ============================================================================

@router.get("/feed/personal", response_model=ActivityListResponse)
async def get_personal_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized feed from followed users' activities
    """
    # Get list of users being followed
    from app.models.follower import Follower
    followed_ids = db.query(Follower.followed_id).filter(
        Follower.follower_id == current_user.id
    ).all()
    followed_ids = [f[0] for f in followed_ids]
    
    if not followed_ids:
        # If not following anyone, return trending instead
        return TrendingResponse(total=0, activities=[])
    
    # Get activities from followed users, sorted by recency
    query = db.query(Activity).filter(
        and_(
            Activity.user_id.in_(followed_ids),
            Activity.visibility.in_([ActivityVisibility.PUBLIC, ActivityVisibility.FOLLOWERS])
        )
    )
    
    total = query.count()
    activities = query.order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()
    
    return ActivityListResponse(
        total=total,
        activities=activities
    )


@router.get("/feed/global", response_model=ActivityListResponse)
async def get_global_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get global feed of all public activities (most liked/commented)
    """
    # Prioritize featured and high-engagement activities
    query = db.query(Activity).filter(
        Activity.visibility == ActivityVisibility.PUBLIC
    )
    
    total = query.count()
    
    # Sort by: featured first, then by engagement score (likes + comments), then by recency
    activities = query.order_by(
        desc(Activity.is_featured),
        desc(Activity.like_count + Activity.comment_count),
        desc(Activity.created_at)
    ).offset(skip).limit(limit).all()
    
    return ActivityListResponse(
        total=total,
        activities=activities
    )


@router.get("/feed/settings", response_model=FeedSettingsResponse)
async def get_feed_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's feed settings
    """
    settings = db.query(FeedSettings).filter(FeedSettings.user_id == current_user.id).first()
    if not settings:
        # Create default settings
        settings = FeedSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/feed/settings", response_model=FeedSettingsResponse)
async def update_feed_settings(
    update_data: FeedSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user's feed settings
    """
    settings = db.query(FeedSettings).filter(FeedSettings.user_id == current_user.id).first()
    if not settings:
        settings = FeedSettings(user_id=current_user.id)
        db.add(settings)
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    return settings


# ============================================================================
# ENGAGEMENT ENDPOINTS (Likes, Comments)
# ============================================================================

@router.post("/{activity_id}/like", response_model=ActivityLikeResponse)
async def like_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Like an activity
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if already liked
    existing = db.query(ActivityLike).filter(
        and_(
            ActivityLike.activity_id == activity_id,
            ActivityLike.user_id == current_user.id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already liked this activity")
    
    like = ActivityLike(activity_id=activity_id, user_id=current_user.id)
    activity.like_count += 1
    
    db.add(like)
    db.commit()
    db.refresh(like)
    
    return like


@router.delete("/{activity_id}/like", status_code=204)
async def unlike_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unlike an activity
    """
    like = db.query(ActivityLike).filter(
        and_(
            ActivityLike.activity_id == activity_id,
            ActivityLike.user_id == current_user.id
        )
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if activity:
        activity.like_count = max(0, activity.like_count - 1)
    
    db.delete(like)
    db.commit()


@router.post("/{activity_id}/comments", response_model=ActivityCommentResponse)
async def add_comment(
    activity_id: int,
    comment_data: ActivityCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a comment to an activity
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    comment = ActivityComment(
        activity_id=activity_id,
        user_id=current_user.id,
        content=comment_data.content
    )
    
    activity.comment_count += 1
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


@router.get("/{activity_id}/comments", response_model=List[ActivityCommentResponse])
async def get_activity_comments(
    activity_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comments on an activity
    """
    comments = db.query(ActivityComment).filter(
        ActivityComment.activity_id == activity_id
    ).order_by(desc(ActivityComment.created_at)).offset(skip).limit(limit).all()
    
    return comments


@router.delete("/{activity_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    activity_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment (only owner can delete)
    """
    comment = db.query(ActivityComment).filter(
        and_(
            ActivityComment.id == comment_id,
            ActivityComment.activity_id == activity_id
        )
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete own comments")
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if activity:
        activity.comment_count = max(0, activity.comment_count - 1)
    
    db.delete(comment)
    db.commit()


# ============================================================================
# TRENDING ENDPOINTS
# ============================================================================

@router.get("/trending/challenges", response_model=List[TrendingResponse])
async def get_trending_challenges(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trending challenges
    """
    trending = db.query(Trending).filter(
        Trending.content_type == "challenge"
    ).order_by(desc(Trending.trend_score)).limit(limit).all()
    
    return trending


@router.get("/trending/solutions", response_model=List[TrendingResponse])
async def get_trending_solutions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trending solutions
    """
    trending = db.query(Trending).filter(
        Trending.content_type == "solution"
    ).order_by(desc(Trending.trend_score)).limit(limit).all()
    
    return trending


@router.get("/trending/users", response_model=List[TrendingResponse])
async def get_trending_users(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trending users (rising stars)
    """
    trending = db.query(Trending).filter(
        Trending.content_type == "user"
    ).order_by(desc(Trending.trend_score)).limit(limit).all()
    
    return trending


@router.post("/trending/calculate", status_code=200)
async def calculate_trending(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculate trending scores (admin only)
    """
    # Get user from DB to check if admin
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or not getattr(user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Calculate trending scores for activities in last 3 days
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    
    activities = db.query(Activity).filter(
        and_(
            Activity.created_at >= three_days_ago,
            Activity.visibility == ActivityVisibility.PUBLIC
        )
    ).all()
    
    # Clear existing trending for this period
    db.query(Trending).filter(Trending.started_trending >= three_days_ago).delete()
    
    # Recalculate trend scores
    for activity in activities:
        # Trend score = (likes * 2) + (comments * 3) + (views * 0.1)
        trend_score = (activity.like_count * 2) + (activity.comment_count * 3) + (activity.view_count * 0.1)
        
        trending = Trending(
            content_type="activity",
            content_id=activity.id,
            trend_score=trend_score,
            rank=0,  # Will be calculated after sorting
            views=activity.view_count,
            likes=activity.like_count,
            comments=activity.comment_count,
            shares=activity.share_count
        )
        db.add(trending)
    
    db.commit()
    return {"status": "trending calculated"}


# ============================================================================
# TIMELINE ENDPOINTS (User profile timeline)
# ============================================================================

@router.get("/timeline/{user_id}", response_model=TimelineResponse)
async def get_user_timeline(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a user's timeline (public achievement history)
    """
    timeline = db.query(Timeline).filter(Timeline.user_id == user_id).first()
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    # Check if public
    if not timeline.public_profile and timeline.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Profile is private")
    
    return timeline


@router.get("/timeline/{user_id}/activities", response_model=ActivityListResponse)
async def get_user_timeline_activities(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activities from a user's timeline
    """
    # Check if user's profile is public
    timeline = db.query(Timeline).filter(Timeline.user_id == user_id).first()
    if timeline and not timeline.public_profile and timeline.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Profile is private")
    
    query = db.query(Activity).filter(
        and_(
            Activity.user_id == user_id,
            Activity.visibility.in_([ActivityVisibility.PUBLIC, ActivityVisibility.FOLLOWERS])
        )
    )
    
    total = query.count()
    activities = query.order_by(desc(Activity.created_at)).offset(skip).limit(limit).all()
    
    return ActivityListResponse(
        total=total,
        activities=activities
    )


@router.put("/timeline/", response_model=TimelineResponse)
async def update_timeline(
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user's timeline settings (bio, public profile)
    """
    timeline = db.query(Timeline).filter(Timeline.user_id == current_user.id).first()
    if not timeline:
        timeline = Timeline(user_id=current_user.id)
        db.add(timeline)
    
    if "bio" in updates:
        timeline.bio = updates["bio"]
    if "public_profile" in updates:
        timeline.public_profile = updates["public_profile"]
    
    timeline.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(timeline)
    
    return timeline


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@router.get("/stats/user", response_model=ActivityStatsResponse)
async def get_user_activity_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's activity statistics
    """
    timeline = db.query(Timeline).filter(Timeline.user_id == current_user.id).first()
    if not timeline:
        timeline = Timeline(user_id=current_user.id)
        db.add(timeline)
        db.commit()
        db.refresh(timeline)
    
    return ActivityStatsResponse(
        total_activities=timeline.total_activities,
        total_points=timeline.total_points,
        challenges_solved=timeline.challenges_solved,
        badges_earned=timeline.badges_earned,
        paths_completed=timeline.paths_completed,
        total_engagement=timeline.total_engagement,
        longest_streak=timeline.longest_streak,
        current_streak=timeline.current_streak
    )
