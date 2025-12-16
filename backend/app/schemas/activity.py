"""
Pydantic Schemas for Activity, Feed, and Social Features
Request/response validation for Social Feeds & Activity Timeline
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ActivityTypeEnum(str, Enum):
    """Activity type values"""
    CHALLENGE_SOLVED = "challenge_solved"
    BADGE_EARNED = "badge_earned"
    CONTEST_PARTICIPATED = "contest_participated"
    CONTEST_WON = "contest_won"
    SOLUTION_SHARED = "solution_shared"
    COURSE_COMPLETED = "course_completed"
    PATH_STARTED = "path_started"
    PATH_COMPLETED = "path_completed"
    USER_FOLLOWED = "user_followed"
    STREAK_ACHIEVED = "streak_achieved"
    COMMENT_POSTED = "comment_posted"
    SOLUTION_UPVOTED = "solution_upvoted"
    MENTOR_SESSION = "mentor_session"
    AI_HINT_USED = "ai_hint_used"
    POINTS_EARNED = "points_earned"
    LEADERBOARD_RANK = "leaderboard_rank"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class ActivityVisibilityEnum(str, Enum):
    """Visibility levels"""
    PUBLIC = "public"
    FOLLOWERS = "followers"
    PRIVATE = "private"


class ActivityCreate(BaseModel):
    """Request schema for creating an activity"""
    activity_type: ActivityTypeEnum
    related_type: str  # "challenge", "badge", "contest", etc.
    related_id: int
    title: str
    description: Optional[str] = None
    points_earned: Optional[int] = 0
    extra_data: Optional[Dict[str, Any]] = {}
    visibility: Optional[ActivityVisibilityEnum] = ActivityVisibilityEnum.PUBLIC


class UserBasic(BaseModel):
    """Basic user info for activity responses"""
    id: int
    username: str
    avatar_url: Optional[str] = None


class ActivityResponse(BaseModel):
    """Response schema for a single activity"""
    id: int
    user_id: int
    user: Optional[UserBasic] = None
    activity_type: str
    related_type: str
    related_id: int
    title: str
    description: Optional[str] = None
    points_earned: int
    extra_data: Dict[str, Any] = {}
    visibility: str
    is_featured: bool
    like_count: int
    comment_count: int
    share_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Response schema for activity list"""
    total: int
    activities: List[ActivityResponse]


class ActivityLikeResponse(BaseModel):
    """Response schema for activity like"""
    id: int
    activity_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ActivityCommentCreate(BaseModel):
    """Request schema for adding a comment"""
    content: str = Field(..., min_length=1, max_length=1000)


class ActivityCommentResponse(BaseModel):
    """Response schema for activity comment"""
    id: int
    activity_id: int
    user_id: int
    user: Optional[UserBasic] = None
    content: str
    like_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedSettingsResponse(BaseModel):
    """Response schema for feed settings"""
    id: int
    user_id: int
    show_challenge_solved: bool
    show_badge_earned: bool
    show_contest_activity: bool
    show_solutions: bool
    show_course_progress: bool
    show_follows: bool
    sort_by: str
    include_system_announcements: bool
    notify_activity_likes: bool
    notify_activity_comments: bool
    notify_follower_activity: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedSettingsUpdate(BaseModel):
    """Request schema for updating feed settings"""
    show_challenge_solved: Optional[bool] = None
    show_badge_earned: Optional[bool] = None
    show_contest_activity: Optional[bool] = None
    show_solutions: Optional[bool] = None
    show_course_progress: Optional[bool] = None
    show_follows: Optional[bool] = None
    sort_by: Optional[str] = None
    include_system_announcements: Optional[bool] = None
    notify_activity_likes: Optional[bool] = None
    notify_activity_comments: Optional[bool] = None
    notify_follower_activity: Optional[bool] = None


class TrendingResponse(BaseModel):
    """Response schema for trending items"""
    id: int
    content_type: str
    content_id: int
    trend_score: float
    rank: int
    views: int
    likes: int
    comments: int
    shares: int
    velocity: float
    extra_data: Dict[str, Any] = {}
    started_trending: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TimelineResponse(BaseModel):
    """Response schema for user timeline"""
    id: int
    user_id: int
    total_activities: int
    total_points: int
    challenges_solved: int
    badges_earned: int
    paths_completed: int
    total_engagement: int
    first_activity_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    longest_streak: int
    current_streak: int
    bio: Optional[str] = None
    public_profile: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ActivityStatsResponse(BaseModel):
    """Response schema for activity statistics"""
    total_activities: int
    total_points: int
    challenges_solved: int
    badges_earned: int
    paths_completed: int
    total_engagement: int
    longest_streak: int
    current_streak: int
