"""
Referral Program Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Referral Code Schemas
class ReferralCodeCreate(BaseModel):
    custom_url: Optional[str] = None
    bonus_per_referral: int = Field(default=100, ge=10, le=1000)


class ReferralCodeResponse(BaseModel):
    id: int
    user_id: int
    code: str
    is_active: bool
    used_count: int
    successful_referrals: int
    bonus_per_referral: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Referral Schemas
class ReferralCreate(BaseModel):
    referred_email: str = Field(..., min_length=5)
    referral_source: Optional[str] = None


class ReferralResponse(BaseModel):
    id: int
    referrer_user_id: int
    referred_user_id: Optional[int]
    code_id: Optional[int]
    status: str
    bonus_amount: int
    bonus_type: str
    email_confirmed: bool
    first_purchase_completed: bool
    created_at: datetime
    confirmed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReferralDetailResponse(ReferralResponse):
    referral_email: Optional[str]
    referral_source: Optional[str]
    expires_at: Optional[datetime]


# Reward Schemas
class ReferralRewardResponse(BaseModel):
    id: int
    referral_id: int
    referrer_user_id: int
    reward_type: str
    amount: int
    tier_level: int
    tier_multiplier: float
    base_amount: int
    bonus_amount: int
    is_claimed: bool
    claimed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Campaign Schemas
class ReferralCampaignResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    is_active: bool
    reward_amount: int
    reward_type: str
    referrer_bonus: int
    referred_bonus: int
    max_referrals: Optional[int]
    current_referral_count: int
    start_date: datetime
    end_date: datetime
    
    class Config:
        from_attributes = True


# Statistics Schemas
class ReferralStatisticsResponse(BaseModel):
    user_id: int
    total_referrals: int
    confirmed_referrals: int
    pending_referrals: int
    total_rewards_earned: int
    total_rewards_claimed: int
    pending_rewards: int
    conversion_rate: float
    referrer_tier: str
    tier_multiplier: float
    rewards_by_type: Dict[str, int]
    
    class Config:
        from_attributes = True


# Leaderboard Schemas
class ReferralLeaderboardEntry(BaseModel):
    user_id: int
    username: str
    total_referrals: int
    confirmed_referrals: int
    total_rewards: int
    referrer_tier: str
    rank: int


class ReferralLeaderboardResponse(BaseModel):
    entries: List[ReferralLeaderboardEntry]
    user_rank: Optional[int]
    user_total_referrals: int


# Dashboard Schemas
class ReferralDashboardResponse(BaseModel):
    referral_code: ReferralCodeResponse
    statistics: ReferralStatisticsResponse
    recent_referrals: List[ReferralDetailResponse]
    pending_rewards: int
    active_campaigns: List[ReferralCampaignResponse]
    next_tier_threshold: int


# Summary Schemas
class ReferralListResponse(BaseModel):
    referrals: List[ReferralResponse]
    total: int
    pending_count: int
    confirmed_count: int
    total_pending_rewards: int
