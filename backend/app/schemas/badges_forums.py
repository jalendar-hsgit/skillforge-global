"""
Pydantic Schemas for Badges, Forums, and Gamification
Request/response validation for gamification and community features
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# BADGE SCHEMAS
# ============================================================================

class BadgeRarityEnum(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class BadgeCategoryEnum(str, Enum):
    CHALLENGE = "challenge"
    STREAK = "streak"
    SOCIAL = "social"
    SPEED = "speed"
    MASTERY = "mastery"
    MILESTONE = "milestone"
    CONTEST = "contest"
    LEARNING = "learning"


class BadgeResponse(BaseModel):
    """Response schema for a badge"""
    id: int
    name: str
    description: str
    icon_url: str
    icon_emoji: Optional[str] = None
    category: str
    rarity: str
    condition_type: str
    condition_value: int
    points_value: int
    coins_reward: int
    is_active: bool
    is_hidden: bool
    tier: int
    extra_data: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    """Response schema for user's earned badge"""
    id: int
    user_id: int
    badge: BadgeResponse
    tier: int
    earn_count: int
    first_earned_at: datetime
    last_earned_at: datetime

    class Config:
        from_attributes = True


class BadgeProgressResponse(BaseModel):
    """Response schema for badge progress"""
    id: int
    user_id: int
    badge_id: int
    badge: Optional[BadgeResponse] = None
    current_value: int
    target_value: int
    progress_percentage: float
    is_completed: bool
    completed_at: Optional[datetime] = None
    started_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntryResponse(BaseModel):
    """Response schema for leaderboard entry"""
    id: int
    user_id: int
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int
    challenges_solved: int
    badges_earned: int
    contests_won: int
    overall_rank: Optional[int] = None
    points_rank: Optional[int] = None
    current_streak: int
    longest_streak: int
    total_days_active: int

    class Config:
        from_attributes = True


class LeaderboardListResponse(BaseModel):
    """Response schema for leaderboard list"""
    total: int
    entries: List[LeaderboardEntryResponse]


class AchievementResponse(BaseModel):
    """Response schema for an achievement"""
    id: int
    name: str
    description: str
    icon_url: str
    icon_emoji: Optional[str] = None
    achievement_type: str
    points: int
    coins_reward: int
    xp_reward: int
    rarity: str
    is_hidden: bool
    extra_data: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    """Response schema for user's earned achievement"""
    id: int
    user_id: int
    achievement: AchievementResponse
    context_data: Dict[str, Any] = {}
    unlocked_at: datetime

    class Config:
        from_attributes = True


class UserBadgesStatsResponse(BaseModel):
    """Response schema for user's badge statistics"""
    total_badges: int
    total_achievements: int
    total_points: int
    earned_badges: List[UserBadgeResponse]
    in_progress: List[BadgeProgressResponse]
    achievements: List[UserAchievementResponse]


# ============================================================================
# FORUM SCHEMAS
# ============================================================================

class ThreadStatusEnum(str, Enum):
    OPEN = "open"
    ANSWERED = "answered"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ThreadTypeEnum(str, Enum):
    QUESTION = "question"
    DISCUSSION = "discussion"
    ANNOUNCEMENT = "announcement"
    RESOURCE = "resource"
    BUG_REPORT = "bug_report"


class ForumCategoryResponse(BaseModel):
    """Response schema for forum category"""
    id: int
    name: str
    slug: str
    description: str
    icon_emoji: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: bool
    display_order: int
    thread_count: int
    reply_count: int
    last_activity_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserBasicResponse(BaseModel):
    """Basic user info for forum responses"""
    id: int
    username: str
    avatar_url: Optional[str] = None


class ForumReplyResponse(BaseModel):
    """Response schema for a forum reply"""
    id: int
    thread_id: int
    author_id: int
    author: Optional[UserBasicResponse] = None
    parent_reply_id: Optional[int] = None
    content: str
    code_snippet: Optional[str] = None
    language: Optional[str] = None
    is_accepted_answer: bool
    vote_count: int
    helpful_count: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    edited_count: int

    class Config:
        from_attributes = True


class ForumThreadCreateRequest(BaseModel):
    """Request schema for creating a thread"""
    category_id: int
    title: str = Field(..., min_length=5, max_length=300)
    content: str = Field(..., min_length=10, max_length=10000)
    thread_type: ThreadTypeEnum = ThreadTypeEnum.QUESTION
    tags: Optional[List[str]] = []


class ForumThreadResponse(BaseModel):
    """Response schema for a forum thread"""
    id: int
    category_id: int
    category: Optional[ForumCategoryResponse] = None
    creator_id: int
    creator: Optional[UserBasicResponse] = None
    title: str
    content: str
    tags: List[str] = []
    thread_type: str
    status: str
    view_count: int
    reply_count: int
    vote_count: int
    bookmark_count: int
    has_accepted_answer: bool
    is_pinned: bool
    is_featured: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    last_reply_at: Optional[datetime] = None
    replies: Optional[List[ForumReplyResponse]] = []

    class Config:
        from_attributes = True


class ForumThreadListResponse(BaseModel):
    """Response schema for thread list"""
    total: int
    threads: List[ForumThreadResponse]


class ForumReplyCreateRequest(BaseModel):
    """Request schema for creating a reply"""
    content: str = Field(..., min_length=1, max_length=5000)
    code_snippet: Optional[str] = None
    language: Optional[str] = None
    parent_reply_id: Optional[int] = None


class ForumBookmarkResponse(BaseModel):
    """Response schema for a bookmark"""
    id: int
    user_id: int
    thread_id: int
    thread: Optional[ForumThreadResponse] = None
    is_to_read: bool
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ForumStatsResponse(BaseModel):
    """Response schema for forum statistics"""
    total_threads: int
    total_replies: int
    total_bookmarks: int
    helpful_replies: int
    user_threads: List[ForumThreadResponse]
    bookmarks: List[ForumBookmarkResponse]


class ThreadSearchRequest(BaseModel):
    """Request schema for thread search"""
    query: str = Field(..., min_length=1, max_length=200)
    category_id: Optional[int] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = []
    sort_by: Optional[str] = "recent"  # recent, popular, answers, views


class ThreadSearchResponse(BaseModel):
    """Response schema for search results"""
    total: int
    threads: List[ForumThreadResponse]
    facets: Dict[str, Any] = {}  # category counts, tag counts, etc
