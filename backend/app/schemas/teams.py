"""
Pydantic schemas for team management endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# Team Schemas
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    slug: str = Field(..., min_length=3, max_length=100, pattern="^[a-z0-9-]+$")
    description: str = Field(..., min_length=10, max_length=500)
    visibility: str = Field(default="private", description="public, private, restricted")
    icon_emoji: Optional[str] = Field(None, max_length=10)
    banner_url: Optional[str] = Field(None, max_length=500)
    max_members: int = Field(default=50, ge=5, le=500)
    has_contests: bool = Field(default=False)
    has_analytics: bool = Field(default=True)


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    icon_emoji: Optional[str] = None
    banner_url: Optional[str] = None
    max_members: Optional[int] = None
    has_contests: Optional[bool] = None
    has_analytics: Optional[bool] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    owner_id: int
    visibility: str
    icon_emoji: Optional[str]
    banner_url: Optional[str]
    max_members: int
    member_count: int
    total_challenges_solved: int
    total_points: int
    average_rating: float
    has_contests: bool
    has_analytics: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamDetailResponse(TeamResponse):
    owner_username: str
    members: List["TeamMemberResponse"] = []
    recent_activity: List[Dict] = []


# TeamMember Schemas
class TeamMemberCreate(BaseModel):
    user_id: int
    role: str = Field(default="member", description="owner, admin, mentor, member")


class TeamMemberUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: str
    is_active: bool
    challenges_solved: int
    contests_won: int
    points_contributed: int
    last_active_at: Optional[datetime]
    joined_at: datetime
    
    class Config:
        from_attributes = True


class TeamMemberDetailResponse(TeamMemberResponse):
    username: str
    avatar_url: Optional[str]


# TeamInvitation Schemas
class TeamInvitationCreate(BaseModel):
    invited_user_id: int
    expires_at: Optional[datetime] = None


class TeamInvitationAccept(BaseModel):
    invitation_id: int


class TeamInvitationResponse(BaseModel):
    id: int
    team_id: int
    invited_user_id: int
    invited_by_id: int
    status: str
    created_at: datetime
    responded_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TeamInvitationDetailResponse(TeamInvitationResponse):
    team_name: str
    team_icon: Optional[str]
    invited_by_username: str


# TeamChallenge Schemas
class TeamChallengeCreate(BaseModel):
    challenge_id: int
    deadline: Optional[datetime] = None
    is_mandatory: bool = Field(default=False)


class TeamChallengeResponse(BaseModel):
    id: int
    team_id: int
    challenge_id: int
    assigned_by_id: Optional[int]
    assigned_at: datetime
    deadline: Optional[datetime]
    is_mandatory: bool
    members_assigned: int
    members_completed: int
    completion_percentage: float
    
    class Config:
        from_attributes = True


# TeamStatistics Schemas
class TeamStatisticsResponse(BaseModel):
    team_id: int
    total_members: int
    active_members: int
    total_challenges_solved: int
    total_points: int
    average_points_per_member: float
    longest_streak: int
    total_contests: int
    contests_won: int
    top_contributor_id: Optional[int]
    contribution_distribution: Dict[str, float]
    growth_30_days: float
    new_members_30_days: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamLeaderboardResponse(BaseModel):
    rank: int
    member_id: int
    username: str
    points: int
    challenges_solved: int
    contests_won: int
    last_active_at: Optional[datetime]


# TeamContest Schemas
class TeamContestCreate(BaseModel):
    contest_id: int


class TeamContestResponse(BaseModel):
    id: int
    team_id: int
    contest_id: int
    registered_at: datetime
    final_score: int
    rank: Optional[int]
    challenges_completed: int
    problems_solved: int
    time_penalty: int
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# TeamAnnouncement Schemas
class TeamAnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    announcement_type: str = Field(default="general", description="general, milestone, contest, deadline")
    is_pinned: bool = Field(default=False)
    importance: str = Field(default="normal", description="low, normal, high, urgent")


class TeamAnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    announcement_type: Optional[str] = None
    is_pinned: Optional[bool] = None
    importance: Optional[str] = None


class TeamAnnouncementResponse(BaseModel):
    id: int
    team_id: int
    author_id: int
    title: str
    content: str
    announcement_type: str
    is_pinned: bool
    importance: str
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamAnnouncementDetailResponse(TeamAnnouncementResponse):
    author_username: str
    author_avatar: Optional[str]


# List Responses
class TeamsListResponse(BaseModel):
    teams: List[TeamResponse]
    total_count: int
    page: int
    page_size: int


class TeamMembersListResponse(BaseModel):
    members: List[TeamMemberDetailResponse]
    total_count: int
    page: int
    page_size: int


class TeamInvitationsListResponse(BaseModel):
    invitations: List[TeamInvitationDetailResponse]
    total_count: int
    pending_count: int


# Team Discovery Schemas
class TeamDiscoveryResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon_emoji: Optional[str]
    description: str
    member_count: int
    total_points: int
    average_rating: float
    visibility: str


class TeamJoinResponse(BaseModel):
    success: bool
    message: str
    team_id: Optional[int]
    membership_id: Optional[int]


# Team Stats Overview
class TeamStatsOverviewResponse(BaseModel):
    total_teams: int
    teams_owned: int
    teams_member: int
    active_teams: int
    total_team_points: int
    highest_rated_team: Optional[Dict]
