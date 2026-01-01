"""
Phase 3.3 Social Features Pydantic Schemas
Forum, Messaging, Notifications, Social Feed
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== FORUM SCHEMAS ====================

class ForumTopicBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: str = Field(default="discussion", max_length=50)
    color: str = Field(default="blue", max_length=20)


class ForumTopicCreate(ForumTopicBase):
    pass


class ForumTopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_pinned: Optional[bool] = None


class ForumTopicResponse(ForumTopicBase):
    id: int
    is_pinned: bool
    thread_count: int
    reply_count: int
    last_activity_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ForumThreadBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class ForumThreadCreate(ForumThreadBase):
    topic_id: int


class ForumThreadUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None


class ForumThreadResponse(ForumThreadBase):
    id: int
    topic_id: int
    user_id: int
    is_pinned: bool
    is_locked: bool
    reply_count: int
    view_count: int
    last_reply_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ForumReplyBase(BaseModel):
    content: str = Field(..., min_length=1)


class ForumReplyCreate(ForumReplyBase):
    thread_id: int


class ForumReplyUpdate(BaseModel):
    content: Optional[str] = None
    is_best_answer: Optional[bool] = None


class ForumReplyResponse(ForumReplyBase):
    id: int
    thread_id: int
    user_id: int
    is_best_answer: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== MESSAGING SCHEMAS ====================

class ConversationBase(BaseModel):
    participant2_id: int


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(BaseModel):
    id: int
    participant1_id: int
    participant2_id: int
    last_message_at: Optional[datetime]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    attachment_url: Optional[str] = None


class MessageCreate(MessageBase):
    conversation_id: int


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageMarkReadRequest(BaseModel):
    message_ids: List[int]


# ==================== NOTIFICATION SCHEMAS ====================

class NotificationStatusEnum(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    actor_id: Optional[int] = None
    notification_type: str
    title: str
    description: Optional[str]
    related_id: Optional[int]
    status: str
    is_read: bool
    read_at: Optional[datetime]
    action_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationMarkReadRequest(BaseModel):
    notification_ids: List[int]


class NotificationMarkArchivedRequest(BaseModel):
    notification_ids: List[int]


# ==================== SOCIAL FEED SCHEMAS ====================

class SocialFeedItemResponse(BaseModel):
    id: int
    user_id: int
    activity_type: str
    title: str
    description: Optional[str]
    related_id: Optional[int]
    metadata: Optional[dict]
    visibility: str
    like_count: int
    comment_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ActivityMetadata(BaseModel):
    image_url: Optional[str] = None
    badge_name: Optional[str] = None
    course_title: Optional[str] = None
    achievement_name: Optional[str] = None


# ==================== USER PROFILE SCHEMAS ====================

class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[dict] = None
    interests: Optional[List[str]] = None
    is_public: bool = True


class UserProfileCreate(UserProfileBase):
    user_id: int


class UserProfileUpdate(BaseModel):
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[dict] = None
    interests: Optional[List[str]] = None
    is_public: Optional[bool] = None


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    follower_count: int
    following_count: int
    thread_count: int
    badge_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== COMBINED RESPONSE SCHEMAS ====================

class ForumThreadWithReplies(ForumThreadResponse):
    replies: List[ForumReplyResponse] = []


class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []


class NotificationSummary(BaseModel):
    unread_count: int
    total_count: int
    notifications: List[NotificationResponse]
