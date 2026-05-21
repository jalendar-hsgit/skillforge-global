"""
Gamification & Badge System API Endpoints
Supports badge earning, leaderboards, achievements, and progression tracking
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.badges import (
    Badge, UserBadge, BadgeProgress, Leaderboard, Achievement,
    UserAchievement, BadgeRarity, BadgeCategory
)
from app.schemas.badges_forums import (
    BadgeResponse, UserBadgeResponse, BadgeProgressResponse,
    LeaderboardEntryResponse, LeaderboardListResponse,
    AchievementResponse, UserAchievementResponse, UserBadgesStatsResponse
)
from app.services.realtime_events import on_badge_earned

router = APIRouter(prefix="/badges", tags=["badges"])


# ============================================================================
# BADGE ENDPOINTS
# ============================================================================

@router.get("", response_model=List[BadgeResponse])
async def get_badges(
    category: Optional[str] = None,
    rarity: Optional[str] = None,
    is_active: bool = True,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all badges with optional filtering
    """
    query = db.query(Badge).filter(Badge.is_active == is_active)
    
    if category:
        try:
            category_enum = BadgeCategory(category)
            query = query.filter(Badge.category == category_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    if rarity:
        try:
            rarity_enum = BadgeRarity(rarity)
            query = query.filter(Badge.rarity == rarity_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid rarity: {rarity}")
    
    badges = query.limit(limit).all()
    return badges


@router.get("/{badge_id}", response_model=BadgeResponse)
async def get_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific badge by ID
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    return badge


@router.get("/user/earned", response_model=List[UserBadgeResponse])
async def get_user_badges(
    user_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get badges earned by user
    """
    target_user_id = user_id or current_user.id
    
    user_badges = db.query(UserBadge).filter(
        UserBadge.user_id == target_user_id
    ).order_by(desc(UserBadge.last_earned_at)).offset(skip).limit(limit).all()
    
    return user_badges


@router.get("/user/progress", response_model=List[BadgeProgressResponse])
async def get_user_badge_progress(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's in-progress badges
    """
    progress = db.query(BadgeProgress).filter(
        and_(
            BadgeProgress.user_id == current_user.id,
            BadgeProgress.is_completed == False
        )
    ).order_by(desc(BadgeProgress.progress_percentage)).offset(skip).limit(limit).all()
    
    return progress


@router.get("/user/stats", response_model=UserBadgesStatsResponse)
async def get_user_badge_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive badge statistics for a user
    """
    target_user_id = user_id or current_user.id
    
    # Get earned badges
    earned_badges = db.query(UserBadge).filter(
        UserBadge.user_id == target_user_id
    ).all()
    
    # Get in-progress badges
    in_progress = db.query(BadgeProgress).filter(
        and_(
            BadgeProgress.user_id == target_user_id,
            BadgeProgress.is_completed == False
        )
    ).all()
    
    # Get achievements
    achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == target_user_id
    ).all()
    
    # Calculate totals
    total_points = sum(badge.badge.points_value for badge in earned_badges)
    
    return UserBadgesStatsResponse(
        total_badges=len(earned_badges),
        total_achievements=len(achievements),
        total_points=total_points,
        earned_badges=earned_badges,
        in_progress=in_progress,
        achievements=achievements
    )


@router.post("/user/{badge_id}/earn", response_model=UserBadgeResponse)
async def earn_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Award a badge to current user (system use)
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    # Check if already earned
    existing = db.query(UserBadge).filter(
        and_(
            UserBadge.user_id == current_user.id,
            UserBadge.badge_id == badge_id
        )
    ).first()
    
    if existing:
        # For repeatable badges, increment earn count
        if badge.tier > 1 or badge.condition_type.value.endswith("_days"):
            existing.earn_count += 1
            existing.last_earned_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(status_code=400, detail="Badge already earned")
    
    # Create new badge
    user_badge = UserBadge(
        user_id=current_user.id,
        badge_id=badge_id,
        tier=1,
        earn_count=1
    )
    
    db.add(user_badge)
    db.commit()
    db.refresh(user_badge)

    await on_badge_earned(
        current_user.id,
        badge.id,
        badge.name,
        badge.description or "",
    )
    
    return user_badge


# ============================================================================
# LEADERBOARD ENDPOINTS
# ============================================================================

@router.get("/leaderboard/all", response_model=LeaderboardListResponse)
async def get_global_leaderboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get global leaderboard ranked by total points
    """
    query = db.query(Leaderboard).order_by(desc(Leaderboard.total_points))
    
    total = query.count()
    entries = query.offset(skip).limit(limit).all()
    
    return LeaderboardListResponse(total=total, entries=entries)


@router.get("/leaderboard/challenges", response_model=LeaderboardListResponse)
async def get_challenges_leaderboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get leaderboard ranked by challenges solved
    """
    query = db.query(Leaderboard).order_by(desc(Leaderboard.challenges_solved))
    
    total = query.count()
    entries = query.offset(skip).limit(limit).all()
    
    return LeaderboardListResponse(total=total, entries=entries)


@router.get("/leaderboard/contests", response_model=LeaderboardListResponse)
async def get_contests_leaderboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get leaderboard ranked by contests won
    """
    query = db.query(Leaderboard).order_by(desc(Leaderboard.contests_won))
    
    total = query.count()
    entries = query.offset(skip).limit(limit).all()
    
    return LeaderboardListResponse(total=total, entries=entries)


@router.get("/leaderboard/monthly", response_model=LeaderboardListResponse)
async def get_monthly_leaderboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get monthly leaderboard
    """
    query = db.query(Leaderboard).filter(
        Leaderboard.period == "monthly"
    ).order_by(desc(Leaderboard.total_points))
    
    total = query.count()
    entries = query.offset(skip).limit(limit).all()
    
    return LeaderboardListResponse(total=total, entries=entries)


@router.get("/leaderboard/user-rank", response_model=LeaderboardEntryResponse)
async def get_user_rank(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's current rank and stats
    """
    target_user_id = user_id or current_user.id
    
    leaderboard = db.query(Leaderboard).filter(
        Leaderboard.user_id == target_user_id
    ).first()
    
    if not leaderboard:
        raise HTTPException(status_code=404, detail="User not on leaderboard")
    
    return leaderboard


@router.post("/leaderboard/update", status_code=200)
async def update_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculate leaderboard rankings (admin only)
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or not getattr(user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Get all leaderboard entries
    entries = db.query(Leaderboard).all()
    
    # Sort and update ranks
    sorted_by_points = sorted(entries, key=lambda x: x.total_points, reverse=True)
    for idx, entry in enumerate(sorted_by_points, 1):
        entry.overall_rank = idx
        entry.points_rank = idx
    
    db.commit()
    
    return {"status": "leaderboard updated", "entries_updated": len(entries)}


# ============================================================================
# ACHIEVEMENT ENDPOINTS
# ============================================================================

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    achievement_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all achievements
    """
    query = db.query(Achievement)
    
    if achievement_type:
        query = query.filter(Achievement.achievement_type == achievement_type)
    
    achievements = query.limit(limit).all()
    return achievements


@router.get("/user/achievements", response_model=List[UserAchievementResponse])
async def get_user_achievements(
    user_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's earned achievements
    """
    target_user_id = user_id or current_user.id
    
    achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == target_user_id
    ).order_by(desc(UserAchievement.unlocked_at)).offset(skip).limit(limit).all()
    
    return achievements


@router.post("/user/{achievement_id}/unlock", response_model=UserAchievementResponse)
async def unlock_achievement(
    achievement_id: int,
    context_data: dict = {},
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Award an achievement to user
    """
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Check if already unlocked
    existing = db.query(UserAchievement).filter(
        and_(
            UserAchievement.user_id == current_user.id,
            UserAchievement.achievement_id == achievement_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Achievement already unlocked")
    
    user_achievement = UserAchievement(
        user_id=current_user.id,
        achievement_id=achievement_id,
        context_data=context_data or {}
    )
    
    db.add(user_achievement)
    db.commit()
    db.refresh(user_achievement)
    
    return user_achievement
