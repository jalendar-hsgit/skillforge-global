"""
Referral Program API Router
Multi-tier referral system with rewards, tracking, and campaign management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
from typing import List
import secrets

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.referral import (
    ReferralCode, Referral, ReferralReward, ReferralCampaign,
    ReferralStatistics, ReferralStatus, RewardType
)
from app.schemas.referral import (
    ReferralCodeCreate, ReferralCodeResponse, ReferralCreate, ReferralResponse,
    ReferralDetailResponse, ReferralRewardResponse, ReferralCampaignResponse,
    ReferralStatisticsResponse, ReferralLeaderboardResponse, ReferralLeaderboardEntry,
    ReferralDashboardResponse, ReferralListResponse
)

router = APIRouter(prefix="/referral", tags=["referral"])


# ==================== REFERRAL CODES ====================

@router.post("/code", response_model=ReferralCodeResponse)
def create_referral_code(
    code_data: ReferralCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or get user's referral code"""
    
    # Check if already has code
    existing = db.query(ReferralCode).filter_by(user_id=current_user.id).first()
    if existing:
        return ReferralCodeResponse.from_orm(existing)
    
    # Generate unique code
    while True:
        code = secrets.token_hex(5).upper()  # 10-char code
        if not db.query(ReferralCode).filter_by(code=code).first():
            break
    
    db_code = ReferralCode(
        user_id=current_user.id,
        code=code,
        custom_url=code_data.custom_url,
        bonus_per_referral=code_data.bonus_per_referral
    )
    
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    
    return ReferralCodeResponse.from_orm(db_code)


@router.get("/code", response_model=ReferralCodeResponse)
def get_referral_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's referral code"""
    
    code = db.query(ReferralCode).filter_by(user_id=current_user.id).first()
    if not code:
        raise HTTPException(status_code=404, detail="No referral code found")
    
    return ReferralCodeResponse.from_orm(code)


@router.put("/code", response_model=ReferralCodeResponse)
def update_referral_code(
    update_data: ReferralCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update referral code settings"""
    
    code = db.query(ReferralCode).filter_by(user_id=current_user.id).first()
    if not code:
        raise HTTPException(status_code=404, detail="No referral code found")
    
    code.custom_url = update_data.custom_url
    code.bonus_per_referral = update_data.bonus_per_referral
    code.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(code)
    
    return ReferralCodeResponse.from_orm(code)


# ==================== REFERRALS ====================

@router.post("/refer", response_model=ReferralResponse)
def create_referral(
    referral: ReferralCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a referral"""
    
    # Get referrer's code
    code = db.query(ReferralCode).filter_by(user_id=current_user.id).first()
    if not code:
        raise HTTPException(status_code=400, detail="Create referral code first")
    
    # Check if already referred
    existing = db.query(Referral).filter(
        and_(
            Referral.referrer_user_id == current_user.id,
            Referral.referred_email == referral.referred_email
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already referred this email")
    
    # Create referral
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    db_referral = Referral(
        code_id=code.id,
        referrer_user_id=current_user.id,
        referred_email=referral.referred_email,
        referral_source=referral.referral_source or "direct",
        bonus_amount=code.bonus_per_referral,
        bonus_type=RewardType.COINS,
        status=ReferralStatus.PENDING,
        expires_at=expires_at
    )
    
    db.add(db_referral)
    code.used_count += 1
    
    db.commit()
    db.refresh(db_referral)
    
    return ReferralResponse.from_orm(db_referral)


@router.get("/my-referrals", response_model=ReferralListResponse)
def get_my_referrals(
    status: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's referrals"""
    
    query = db.query(Referral).filter_by(referrer_user_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(desc(Referral.created_at))
    
    total = query.count()
    referrals = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Count statistics
    pending = db.query(Referral).filter(
        and_(
            Referral.referrer_user_id == current_user.id,
            Referral.status == ReferralStatus.PENDING
        )
    ).count()
    
    confirmed = db.query(Referral).filter(
        and_(
            Referral.referrer_user_id == current_user.id,
            Referral.status == ReferralStatus.CONFIRMED
        )
    ).count()
    
    # Calculate total pending rewards
    pending_rewards = db.query(func.sum(ReferralReward.amount)).filter(
        and_(
            ReferralReward.referrer_user_id == current_user.id,
            ReferralReward.is_claimed == False
        )
    ).scalar() or 0
    
    return ReferralListResponse(
        referrals=[ReferralResponse.from_orm(r) for r in referrals],
        total=total,
        pending_count=pending,
        confirmed_count=confirmed,
        total_pending_rewards=pending_rewards
    )


@router.get("/{referral_id}", response_model=ReferralDetailResponse)
def get_referral(
    referral_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get referral details"""
    
    referral = db.query(Referral).filter_by(id=referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    if referral.referrer_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return ReferralDetailResponse.from_orm(referral)


@router.post("/{referral_id}/claim-reward")
def claim_referral_reward(
    referral_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Claim reward for a confirmed referral"""
    
    referral = db.query(Referral).filter_by(id=referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    if referral.referrer_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if referral.status != ReferralStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Referral not confirmed yet")
    
    # Check if already has reward
    existing_reward = db.query(ReferralReward).filter_by(referral_id=referral_id).first()
    if existing_reward and existing_reward.is_claimed:
        raise HTTPException(status_code=400, detail="Reward already claimed")
    
    # Get or create reward
    if not existing_reward:
        reward = ReferralReward(
            referral_id=referral_id,
            referrer_user_id=referral.referrer_user_id,
            referred_user_id=referral.referred_user_id,
            reward_type=referral.bonus_type,
            amount=referral.bonus_amount,
            base_amount=referral.bonus_amount
        )
        db.add(reward)
    else:
        reward = existing_reward
    
    reward.is_claimed = True
    reward.claimed_at = datetime.utcnow()
    
    # Update statistics
    stats = db.query(ReferralStatistics).filter_by(user_id=current_user.id).first()
    if stats:
        stats.total_rewards_claimed += reward.amount
        stats.pending_rewards -= reward.amount
    
    db.commit()
    
    return {
        "success": True,
        "reward_amount": reward.amount,
        "reward_type": reward.reward_type,
        "claimed_at": reward.claimed_at
    }


# ==================== REWARDS ====================

@router.get("/rewards/pending")
def get_pending_rewards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's pending rewards"""
    
    rewards = db.query(ReferralReward).filter(
        and_(
            ReferralReward.referrer_user_id == current_user.id,
            ReferralReward.is_claimed == False
        )
    ).all()
    
    total_pending = sum(r.amount for r in rewards)
    
    return {
        "pending_amount": total_pending,
        "reward_count": len(rewards),
        "rewards": [ReferralRewardResponse.from_orm(r) for r in rewards]
    }


@router.get("/rewards/history")
def get_reward_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's reward history"""
    
    query = db.query(ReferralReward).filter_by(referrer_user_id=current_user.id).order_by(
        desc(ReferralReward.created_at)
    )
    
    total = query.count()
    rewards = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "rewards": [ReferralRewardResponse.from_orm(r) for r in rewards],
        "total": total,
        "page": page,
        "per_page": per_page
    }


# ==================== STATISTICS ====================

@router.get("/statistics", response_model=ReferralStatisticsResponse)
def get_referral_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's referral statistics"""
    
    stats = db.query(ReferralStatistics).filter_by(user_id=current_user.id).first()
    if not stats:
        # Create default stats
        stats = ReferralStatistics(user_id=current_user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return ReferralStatisticsResponse.from_orm(stats)


# ==================== DASHBOARD ====================

@router.get("/dashboard", response_model=ReferralDashboardResponse)
def get_referral_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete referral dashboard"""
    
    # Get code
    code = db.query(ReferralCode).filter_by(user_id=current_user.id).first()
    if not code:
        raise HTTPException(status_code=404, detail="No referral code")
    
    # Get statistics
    stats = db.query(ReferralStatistics).filter_by(user_id=current_user.id).first()
    if not stats:
        stats = ReferralStatistics(user_id=current_user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    # Get recent referrals
    recent = db.query(Referral).filter_by(referrer_user_id=current_user.id).order_by(
        desc(Referral.created_at)
    ).limit(5).all()
    
    # Get pending rewards
    pending = db.query(func.sum(ReferralReward.amount)).filter(
        and_(
            ReferralReward.referrer_user_id == current_user.id,
            ReferralReward.is_claimed == False
        )
    ).scalar() or 0
    
    # Get active campaigns
    now = datetime.utcnow()
    campaigns = db.query(ReferralCampaign).filter(
        and_(
            ReferralCampaign.is_active == True,
            ReferralCampaign.start_date <= now,
            ReferralCampaign.end_date >= now
        )
    ).limit(3).all()
    
    # Calculate next tier
    tier_thresholds = {"bronze": 0, "silver": 5, "gold": 15, "platinum": 30}
    current_tier = stats.referrer_tier
    next_tier = {"bronze": "silver", "silver": "gold", "gold": "platinum", "platinum": "platinum"}[current_tier]
    next_threshold = tier_thresholds.get(next_tier, 999)
    
    return ReferralDashboardResponse(
        referral_code=ReferralCodeResponse.from_orm(code),
        statistics=ReferralStatisticsResponse.from_orm(stats),
        recent_referrals=[ReferralDetailResponse.from_orm(r) for r in recent],
        pending_rewards=pending,
        active_campaigns=[ReferralCampaignResponse.from_orm(c) for c in campaigns],
        next_tier_threshold=next_threshold
    )


# ==================== LEADERBOARD ====================

@router.get("/leaderboard", response_model=ReferralLeaderboardResponse)
def get_referral_leaderboard(
    limit: int = Query(50, ge=10, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get global referral leaderboard"""
    
    # Get top referrers
    top_stats = db.query(ReferralStatistics).order_by(
        desc(ReferralStatistics.confirmed_referrals)
    ).limit(limit).all()
    
    entries = []
    user_rank = None
    
    for rank, stat in enumerate(top_stats, 1):
        user = db.query(User).filter_by(id=stat.user_id).first()
        if user:
            entry = ReferralLeaderboardEntry(
                user_id=stat.user_id,
                username=user.username,
                total_referrals=stat.total_referrals,
                confirmed_referrals=stat.confirmed_referrals,
                total_rewards=stat.total_rewards_earned,
                referrer_tier=stat.referrer_tier,
                rank=rank
            )
            entries.append(entry)
            
            if stat.user_id == current_user.id:
                user_rank = rank
    
    # Get user's stats
    user_stats = db.query(ReferralStatistics).filter_by(user_id=current_user.id).first()
    user_total = user_stats.total_referrals if user_stats else 0
    
    return ReferralLeaderboardResponse(
        entries=entries,
        user_rank=user_rank,
        user_total_referrals=user_total
    )


# ==================== CAMPAIGNS ====================

@router.get("/campaigns", response_model=List[ReferralCampaignResponse])
def get_active_campaigns(db: Session = Depends(get_db)):
    """Get active referral campaigns"""
    
    now = datetime.utcnow()
    campaigns = db.query(ReferralCampaign).filter(
        and_(
            ReferralCampaign.is_active == True,
            ReferralCampaign.start_date <= now,
            ReferralCampaign.end_date >= now
        )
    ).order_by(desc(ReferralCampaign.created_at)).all()
    
    return [ReferralCampaignResponse.from_orm(c) for c in campaigns]


@router.get("/campaigns/{campaign_id}", response_model=ReferralCampaignResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get campaign details"""
    
    campaign = db.query(ReferralCampaign).filter_by(id=campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return ReferralCampaignResponse.from_orm(campaign)
