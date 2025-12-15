"""
AI Hints API endpoints for intelligent code assistance.
- Request and view hints
- Rate hint quality
- Track hint effectiveness
- Admin: Generate and manage hints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User
from app.modelsx.ai_hints import (
    AIHint, AIHintUsage, HintFeedback, HintTemplate, UserHintQuota,
    HintType, HintDifficulty, HintQuality
)

router = APIRouter(prefix="/api/v1x/hints", tags=["AI Hints"])


# ============================================================================
# Utility Functions
# ============================================================================

def _format_hint(hint: AIHint, include_stats: bool = False):
    """Format hint for response"""
    data = {
        "id": hint.id,
        "challengeId": hint.challenge_id,
        "type": hint.hint_type.value,
        "title": hint.title,
        "content": hint.content,
        "explanation": hint.explanation,
        "difficulty": hint.target_difficulty.value,
        "hasCodeExample": hint.code_example is not None,
        "codeExample": hint.code_example,
        "codeLanguage": hint.code_language,
        "resourceLinks": hint.resource_links,
        "quality": hint.quality_rating.value if hint.quality_rating else "good",
        "isPremiumOnly": hint.is_premium_only,
        "generatedAt": hint.generated_at.isoformat() if hint.generated_at else None,
        "createdAt": hint.created_at.isoformat() if hint.created_at else None,
    }
    
    if include_stats:
        data.update({
            "timesShown": hint.times_shown,
            "timesHelpful": hint.times_helpful,
            "timesUnhelpful": hint.times_unhelpful,
            "helpfulScore": hint.helpful_score,
        })
    
    return data


def _format_hint_usage(usage: AIHintUsage):
    """Format hint usage for response"""
    return {
        "id": usage.id,
        "hintId": usage.hint_id,
        "challengeId": usage.challenge_id,
        "viewedAt": usage.viewed_at.isoformat() if usage.viewed_at else None,
        "timeOnHintSeconds": usage.time_on_hint_seconds,
        "challengeSolvedAfter": usage.challenge_solved_after,
        "timeToSolveMinutes": usage.time_to_solve_minutes,
        "userTierAtTime": usage.user_tier_at_time,
    }


def _format_feedback(feedback: HintFeedback):
    """Format feedback for response"""
    return {
        "id": feedback.id,
        "hintId": feedback.hint_id,
        "userId": feedback.user_id,
        "isHelpful": feedback.is_helpful,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "wasClear": feedback.was_clear,
        "wasActionable": feedback.was_actionable,
        "wasComplete": feedback.was_complete,
        "hasErrors": feedback.has_errors,
        "createdAt": feedback.created_at.isoformat() if feedback.created_at else None,
    }


def _format_quota(quota: UserHintQuota):
    """Format hint quota for response"""
    return {
        "id": quota.id,
        "hintsRequestedToday": quota.hints_requested_today,
        "hintsQuotaPerDay": quota.hints_quota_per_day,
        "remainingToday": max(0, quota.hints_quota_per_day - quota.hints_requested_today),
        "hintsRequestedThisMonth": quota.hints_requested_this_month,
        "hintsQuotaPerMonth": quota.hints_quota_per_month,
        "remainingThisMonth": max(0, quota.hints_quota_per_month - quota.hints_requested_this_month),
        "isUnlimited": quota.is_unlimited,
        "dailyResetAt": quota.daily_reset_at.isoformat() if quota.daily_reset_at else None,
    }


def check_and_reset_quotas(db: Session, user_id: int):
    """Check and reset daily/monthly quotas if needed"""
    quota = db.query(UserHintQuota).filter_by(user_id=user_id).first()
    if not quota:
        return
    
    now = datetime.utcnow()
    
    # Reset daily if needed
    if now >= quota.daily_reset_at + timedelta(days=1):
        quota.hints_requested_today = 0
        quota.daily_reset_at = now
    
    # Reset monthly if needed
    if now >= quota.monthly_reset_at + timedelta(days=30):
        quota.hints_requested_this_month = 0
        quota.monthly_reset_at = now
    
    db.commit()


# ============================================================================
# User Endpoints
# ============================================================================

@router.get("/challenge/{challenge_id}")
def get_hints_for_challenge(
    challenge_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=20),
    hint_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available hints for a challenge"""
    
    query = db.query(AIHint).filter(
        AIHint.challenge_id == challenge_id,
        AIHint.is_active == True
    )
    
    # Filter by type
    if hint_type and hint_type in [h.value for h in HintType]:
        query = query.filter(AIHint.hint_type == hint_type)
    
    # Filter premium hints
    quota = db.query(UserHintQuota).filter_by(user_id=current_user.id).first()
    is_premium = quota and quota.is_unlimited if quota else False
    
    if not is_premium:
        query = query.filter(AIHint.is_premium_only == False)
    
    # Sort by quality/helpfulness
    hints = query.order_by(
        AIHint.helpful_score.desc(),
        AIHint.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "hints": [_format_hint(h) for h in hints],
        "total": query.count(),
    }


@router.post("/request/{challenge_id}")
def request_hint(
    challenge_id: int,
    hint_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request a hint for a challenge (uses quota)"""
    
    # Check quota
    quota = db.query(UserHintQuota).filter_by(user_id=current_user.id).first()
    if not quota:
        quota = UserHintQuota(user_id=current_user.id)
        db.add(quota)
        db.commit()
    
    check_and_reset_quotas(db, current_user.id)
    
    # Check if user can request
    if not quota.is_unlimited:
        if not quota.can_request_hint():
            remaining = max(0, quota.hints_quota_per_day - quota.hints_requested_today)
            raise HTTPException(
                status_code=429,
                detail=f"Daily hint quota exceeded. {remaining} hints remaining."
            )
    
    # Get available hints
    query = db.query(AIHint).filter(
        AIHint.challenge_id == challenge_id,
        AIHint.is_active == True,
    )
    
    if hint_type:
        query = query.filter(AIHint.hint_type == hint_type)
    
    if not quota.is_unlimited:
        query = query.filter(AIHint.is_premium_only == False)
    
    hints = query.order_by(AIHint.helpful_score.desc()).all()
    
    if not hints:
        raise HTTPException(status_code=404, detail="No hints available for this challenge")
    
    # Select hint (weighted by helpful_score)
    hint = random.choice(hints[:min(3, len(hints))])  # Choose from top 3
    
    # Record usage
    usage = AIHintUsage(
        hint_id=hint.id,
        user_id=current_user.id,
        challenge_id=challenge_id,
    )
    db.add(usage)
    
    # Update hint stats
    hint.times_shown += 1
    
    # Update quota
    quota.hints_requested_today += 1
    quota.hints_requested_this_month += 1
    
    db.commit()
    
    return {
        "success": True,
        "hint": _format_hint(hint),
        "quotaRemaining": max(0, quota.hints_quota_per_day - quota.hints_requested_today),
    }


@router.post("/rate/{hint_id}")
def rate_hint(
    hint_id: int,
    is_helpful: bool,
    rating: int = Query(3, ge=1, le=5),
    comment: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rate a hint for helpfulness"""
    
    hint = db.query(AIHint).filter_by(id=hint_id).first()
    if not hint:
        raise HTTPException(status_code=404, detail="Hint not found")
    
    # Check if already rated
    existing = db.query(HintFeedback).filter(
        HintFeedback.hint_id == hint_id,
        HintFeedback.user_id == current_user.id
    ).first()
    
    if existing:
        # Update existing feedback
        existing.is_helpful = is_helpful
        existing.rating = rating
        existing.comment = comment
        existing.updated_at = datetime.utcnow()
    else:
        # Create new feedback
        feedback = HintFeedback(
            hint_id=hint_id,
            user_id=current_user.id,
            is_helpful=is_helpful,
            rating=rating,
            comment=comment,
        )
        db.add(feedback)
    
    # Update hint stats
    if is_helpful:
        hint.times_helpful += 1
    else:
        hint.times_unhelpful += 1
    
    # Recalculate helpful_score
    total_ratings = hint.times_helpful + hint.times_unhelpful
    if total_ratings > 0:
        hint.helpful_score = hint.times_helpful / total_ratings
    
    db.commit()
    
    return {
        "success": True,
        "message": "Rating recorded",
        "hintStats": {
            "timesHelpful": hint.times_helpful,
            "timesUnhelpful": hint.times_unhelpful,
            "helpfulScore": hint.helpful_score,
        },
    }


@router.get("/quota")
def get_hint_quota(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's hint usage quota"""
    
    quota = db.query(UserHintQuota).filter_by(user_id=current_user.id).first()
    if not quota:
        quota = UserHintQuota(user_id=current_user.id)
        db.add(quota)
        db.commit()
    
    check_and_reset_quotas(db, current_user.id)
    db.refresh(quota)
    
    return {
        "success": True,
        "quota": _format_quota(quota),
    }


@router.get("/history")
def get_hint_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's hint viewing history"""
    
    usages = db.query(AIHintUsage).filter(
        AIHintUsage.user_id == current_user.id
    ).order_by(AIHintUsage.viewed_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(AIHintUsage).filter(
        AIHintUsage.user_id == current_user.id
    ).count()
    
    return {
        "success": True,
        "history": [_format_hint_usage(u) for u in usages],
        "total": total,
    }


@router.get("/feedback/{hint_id}")
def get_hint_feedback(
    hint_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get feedback for a hint (public)"""
    
    hint = db.query(AIHint).filter_by(id=hint_id).first()
    if not hint:
        raise HTTPException(status_code=404, detail="Hint not found")
    
    feedbacks = db.query(HintFeedback).filter(
        HintFeedback.hint_id == hint_id
    ).order_by(HintFeedback.created_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(HintFeedback).filter_by(hint_id=hint_id).count()
    
    return {
        "success": True,
        "feedback": [_format_feedback(f) for f in feedbacks],
        "total": total,
        "averageRating": sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else 0,
    }


# ============================================================================
# Admin Endpoints
# ============================================================================

@router.post("/admin/generate/{challenge_id}")
def generate_hint(
    challenge_id: int,
    hint_type: str,
    title: str,
    content: str,
    explanation: str = None,
    code_example: str = None,
    is_premium: bool = False,
    quality: str = "good",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new hint (admin only)"""
    
    # Check admin (basic check - can be extended)
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate inputs
    try:
        hint_type_enum = HintType(hint_type)
        quality_enum = HintQuality(quality)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create hint
    hint = AIHint(
        challenge_id=challenge_id,
        hint_type=hint_type_enum,
        title=title,
        content=content,
        explanation=explanation,
        code_example=code_example,
        is_premium_only=is_premium,
        quality_rating=quality_enum,
        is_manually_reviewed=True,
        reviewed_at=datetime.utcnow(),
    )
    db.add(hint)
    db.commit()
    
    return {
        "success": True,
        "hint": _format_hint(hint, include_stats=True),
    }


@router.put("/admin/hints/{hint_id}")
def update_hint(
    hint_id: int,
    title: str = None,
    content: str = None,
    is_active: bool = None,
    quality: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a hint (admin only)"""
    
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    hint = db.query(AIHint).filter_by(id=hint_id).first()
    if not hint:
        raise HTTPException(status_code=404, detail="Hint not found")
    
    if title:
        hint.title = title
    if content:
        hint.content = content
    if is_active is not None:
        hint.is_active = is_active
    if quality:
        try:
            hint.quality_rating = HintQuality(quality)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid quality value")
    
    hint.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "hint": _format_hint(hint, include_stats=True),
    }


@router.get("/admin/templates")
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List hint templates (admin only)"""
    
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    templates = db.query(HintTemplate).order_by(
        HintTemplate.is_active.desc(),
        HintTemplate.priority.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(HintTemplate).count()
    
    return {
        "success": True,
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "type": t.hint_type.value,
                "isActive": t.is_active,
                "priority": t.priority,
                "totalGenerated": t.total_generated,
                "successRate": t.success_rate,
            }
            for t in templates
        ],
        "total": total,
    }


@router.post("/admin/templates")
def create_template(
    name: str,
    hint_type: str,
    system_prompt: str,
    user_prompt_template: str,
    model_preference: str = "gpt-4",
    temperature: float = 0.7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a hint template (admin only)"""
    
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        hint_type_enum = HintType(hint_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hint type")
    
    template = HintTemplate(
        name=name,
        hint_type=hint_type_enum,
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        model_preference=model_preference,
        temperature=temperature,
    )
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "template": {
            "id": template.id,
            "name": template.name,
            "type": template.hint_type.value,
        },
    }


@router.get("/admin/analytics")
def get_hints_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get analytics on hints system (admin only)"""
    
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Count recent usages
    total_requests = db.query(AIHintUsage).filter(
        AIHintUsage.viewed_at >= since
    ).count()
    
    # Average helpful score
    hints = db.query(AIHint).all()
    avg_helpful_score = sum(h.helpful_score for h in hints) / len(hints) if hints else 0
    
    # Top hints
    top_hints = db.query(AIHint).order_by(
        AIHint.times_helpful.desc()
    ).limit(10).all()
    
    # Unique users who requested hints
    unique_users = db.query(AIHintUsage.user_id).distinct().filter(
        AIHintUsage.viewed_at >= since
    ).count()
    
    return {
        "success": True,
        "analytics": {
            "period": f"Last {days} days",
            "totalRequests": total_requests,
            "uniqueUsers": unique_users,
            "averageHelpfulScore": avg_helpful_score,
            "totalHintsAvailable": len(hints),
            "topHints": [
                {
                    "id": h.id,
                    "title": h.title,
                    "challengeId": h.challenge_id,
                    "timesShown": h.times_shown,
                    "helpfulScore": h.helpful_score,
                }
                for h in top_hints
            ],
        },
    }
