"""
Advanced Coding Practice & Simulator API
Real-time coding environment with multi-language support and cloud labs
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import uuid
import json

from app.core.db import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.code_executor import CodeExecutor
from app.modelsx.coding_practice import (
    CodingChallenge, CodingSubmission, SimulatorEnvironment,
    PracticeSession, CloudLabScenario, ChallengeHint,
    PracticeCategory, PracticeDifficulty, LanguageSupport, SimulatorType,
    CodingAchievement, UserCodingAchievement, UserHintUnlock,
    DailyChallenge, UserDailyChallengeStreak
)
from app.core.db import SessionLocal

router = APIRouter(prefix="/coding-practice", tags=["Coding Practice & Simulator"])

# Initialize code executor (set use_docker=True for production)
code_executor = CodeExecutor(use_docker=False)


# ==================== Pydantic Schemas ====================

class ChallengeFilter(BaseModel):
    category: Optional[str] = None
    difficulty: Optional[str] = None
    language: Optional[str] = None
    is_premium: Optional[bool] = None
    tags: Optional[List[str]] = None


class ChallengeListOut(BaseModel):
    id: int
    title: str
    slug: str
    category: str
    difficulty: str
    tags: List[str]
    estimated_time_minutes: Optional[int]
    points: int
    is_premium: bool
    success_rate: float
    total_attempts: int
    
    class Config:
        from_attributes = True


class ChallengeDetailOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    category: str
    difficulty: str
    tags: List[str]
    problem_statement: str
    constraints: Optional[str]
    examples: List[Dict[str, Any]]
    supported_languages: List[str]
    starter_code: Dict[str, str]
    simulator_type: str
    time_limit_seconds: int
    memory_limit_mb: int
    estimated_time_minutes: Optional[int]
    points: int
    coins_reward: int
    is_premium: bool
    success_rate: float = 0.0
    total_attempts: int = 0
    average_completion_time: Optional[int] = None
    hints: Optional[List[str]] = []
    
    class Config:
        from_attributes = True


class SubmitCodeRequest(BaseModel):
    challenge_id: int
    language: str
    code: Union[str, Dict[str, str]]
    
    @field_validator('code', mode='before')
    @classmethod
    def normalize_code(cls, v):
        """Accept both string and dict formats for code"""
        if isinstance(v, dict):
            # If code is a dict like {'python': 'code...'}, extract the code string
            # Use the provided language or try common language keys
            for key in v.keys():
                return v[key]  # Return the first value (the code)
        return v


class RunCodeRequest(BaseModel):
    language: str
    code: Union[str, Dict[str, str]]
    input_data: Optional[str] = None
    
    @field_validator('code', mode='before')
    @classmethod
    def normalize_code(cls, v):
        """Accept both string and dict formats for code"""
        if isinstance(v, dict):
            # If code is a dict like {'python': 'code...'}, extract the code string
            for key in v.keys():
                return v[key]  # Return the first value (the code)
        return v


class RunCodeResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str]
    execution_time: float  # milliseconds


class SubmissionResult(BaseModel):
    id: int
    status: str
    passed_tests: int
    total_tests: int
    execution_time_ms: Optional[int]
    memory_used_mb: Optional[float]
    test_results: Optional[List[Dict[str, Any]]]
    error_message: Optional[str]
    score: float
    coins_earned: int
    
    class Config:
        from_attributes = True


class StartSessionRequest(BaseModel):
    environment_id: Optional[int] = None
    challenge_id: Optional[int] = None
    language: str = "python"


class SessionOut(BaseModel):
    id: int
    session_token: str
    status: str
    access_url: Optional[str]
    expires_at: datetime
    
    class Config:
        from_attributes = True


class CloudLabOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    cloud_provider: str
    services_used: List[str]
    difficulty: str
    estimated_time_minutes: Optional[int]
    points_reward: int
    coins_reward: int
    is_premium: bool
    
    class Config:
        from_attributes = True


# ==================== Challenges ====================

@router.get("/challenges", response_model=List[ChallengeListOut])
def list_challenges(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    language: Optional[str] = None,
    is_premium: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    List all available coding challenges with filtering (public access).
    Returns UNIQUE challenges with variety in difficulty and category.
    """
    query = db.query(CodingChallenge)
    
    if category:
        query = query.filter(CodingChallenge.category == category)
    
    if difficulty:
        query = query.filter(CodingChallenge.difficulty == difficulty)
    
    if language:
        query = query.filter(CodingChallenge.supported_languages.contains([language]))
    
    if is_premium is not None:
        query = query.filter(CodingChallenge.is_premium == is_premium)
    
    # Order by difficulty for progression (easy -> medium -> hard), then by ID for variety
    # This ensures user sees different challenges with variety in difficulty levels
    challenges = query.order_by(CodingChallenge.difficulty, CodingChallenge.id).offset(skip).limit(limit).all()
    
    # Remove any duplicates by slug (shouldn't happen, but safety check)
    seen_slugs = set()
    unique_challenges = []
    for challenge in challenges:
        if challenge.slug not in seen_slugs:
            unique_challenges.append(challenge)
            seen_slugs.add(challenge.slug)
    
    return unique_challenges


@router.get("/challenges/{slug}", response_model=ChallengeDetailOut)
def get_challenge(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get detailed challenge information (public access)
    """
    challenge = db.query(CodingChallenge).filter(CodingChallenge.slug == slug).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check premium access
    if challenge.is_premium:
        # TODO: Check user subscription
        pass
    
    # Convert challenge to dict and add hints
    challenge_dict = {
        "id": challenge.id,
        "title": challenge.title,
        "slug": challenge.slug,
        "description": challenge.description,
        "category": challenge.category,
        "difficulty": challenge.difficulty,
        "tags": challenge.tags or [],
        "problem_statement": challenge.problem_statement,
        "constraints": challenge.constraints,
        "examples": challenge.examples or [],
        "supported_languages": challenge.supported_languages or [],
        "starter_code": challenge.starter_code or {},
        "simulator_type": challenge.simulator_type,
        "time_limit_seconds": challenge.time_limit_seconds,
        "memory_limit_mb": challenge.memory_limit_mb,
        "estimated_time_minutes": challenge.estimated_time_minutes,
        "points": challenge.points,
        "coins_reward": challenge.coins_reward,
        "is_premium": challenge.is_premium,
        "success_rate": challenge.success_rate or 0.0,
        "total_attempts": challenge.total_attempts or 0,
        "average_completion_time": challenge.average_completion_time,
        "hints": [hint.hint_text for hint in sorted(challenge.hints, key=lambda h: h.hint_order)] if challenge.hints else []
    }
    
    return challenge_dict


@router.post("/run", response_model=RunCodeResponse)
async def run_code(
    request: RunCodeRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Run code without submitting (for quick testing) - Public access
    """
    result = code_executor.execute_code(
        code=request.code,
        language=request.language,
        test_cases=None,
        timeout=30
    )
    
    return RunCodeResponse(
        success=result['success'],
        output=result['output'],
        error=result.get('error'),
        execution_time=result['execution_time']
    )


@router.post("/challenges/{challenge_id}/submit", response_model=SubmissionResult)
async def submit_solution(
    challenge_id: int,
    request: SubmitCodeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit code solution for a challenge
    """
    challenge = db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id).first()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if request.language not in challenge.supported_languages:
        raise HTTPException(status_code=400, detail=f"Language {request.language} not supported for this challenge")
    
    # Create submission record
    submission = CodingSubmission(
        challenge_id=challenge_id,
        user_id=current_user.id,
        language=request.language,
        code=request.code,
        status="pending",
        total_tests=len(challenge.test_cases or [])
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Execute code in background (mock execution for now)
    background_tasks.add_task(_execute_code, submission.id, challenge, request.code, request.language)
    
    # Update challenge stats
    challenge.total_attempts += 1
    db.commit()
    
    return submission


def _execute_code(submission_id: int, challenge: CodingChallenge, code: str, language: str):
    """
    Execute submitted code against test cases (background task)
    Uses real code execution with sandboxing
    """
    db = SessionLocal()
    try:
        submission = db.query(CodingSubmission).filter(CodingSubmission.id == submission_id).first()
        if not submission:
            return
        
        # Update status
        submission.status = "running"
        db.commit()
        
        # Prepare test cases
        test_cases = challenge.test_cases or []
        
        # Execute code with real executor
        result = code_executor.validate_solution(
            code=code,
            language=language,
            test_cases=test_cases,
            timeout=challenge.time_limit_seconds
        )
        
        # Update submission with results
        submission.status = "success" if result['success'] else "failed"
        submission.passed_tests = result.get('passed_tests', 0)
        submission.execution_time_ms = int(result.get('execution_time', 0))
        submission.score = result.get('score', 0)
        submission.test_results = result.get('test_results', [])
        submission.error_message = result.get('error')
        submission.executed_at = datetime.utcnow()
        
        # Award coins for perfect solutions
        if submission.score >= 100:
            submission.coins_earned = challenge.coins_reward
            # TODO: Add coins to user account
        
        # Update challenge success rate
        total_successful = db.query(func.count(CodingSubmission.id)).filter(
            and_(
                CodingSubmission.challenge_id == challenge.id,
                CodingSubmission.score >= 100
            )
        ).scalar()
        
        if challenge.total_attempts > 0:
            challenge.success_rate = (total_successful / challenge.total_attempts) * 100
        
        db.commit()
        
    except Exception as e:
        print(f"Execution error: {e}")
        submission.status = "error"
        submission.error_message = str(e)
        db.commit()
    finally:
        db.close()


@router.get("/challenges/{challenge_id}/hints", response_model=List[Dict[str, Any]])
def get_hints(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get progressive hints for a challenge
    Shows which hints user has already unlocked
    """
    hints = db.query(ChallengeHint).filter(
        ChallengeHint.challenge_id == challenge_id
    ).order_by(ChallengeHint.hint_order).all()
    
    # Get user's unlocked hints
    unlocked_hint_ids = set()
    if current_user:
        unlocked_records = db.query(UserHintUnlock).filter(
            UserHintUnlock.user_id == current_user.id
        ).all()
        unlocked_hint_ids = {uh.hint_id for uh in unlocked_records}
    
    return [{
        "id": h.id,
        "hint_order": h.hint_order,
        "cost_coins": h.cost_coins,
        "hint_text": h.hint_text,
        "unlocked": h.id in unlocked_hint_ids
    } for h in hints]


# ==================== Practice Sessions ====================

@router.post("/sessions/start", response_model=SessionOut)
def start_practice_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new practice session with simulator environment
    """
    # Generate session token
    session_token = str(uuid.uuid4())
    
    # Calculate expiration (60 minutes default)
    expires_at = datetime.utcnow() + timedelta(minutes=60)
    
    # Create session
    session = PracticeSession(
        user_id=current_user.id,
        environment_id=request.environment_id,
        challenge_id=request.challenge_id,
        session_token=session_token,
        status="active",
        expires_at=expires_at,
        access_url=f"https://simulator.skillforge.com/session/{session_token}"  # Mock URL
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # In production, this would:
    # 1. Spin up Docker container with selected environment
    # 2. Configure networking and security
    # 3. Return connection details (SSH, HTTP, WebSocket)
    
    return session


@router.get("/sessions/{session_token}", response_model=Dict[str, Any])
def get_session(
    session_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get session details and current state
    """
    session = db.query(PracticeSession).filter(
        PracticeSession.session_token == session_token,
        PracticeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check expiration
    if datetime.utcnow() > session.expires_at:
        session.status = "expired"
        db.commit()
    
    return {
        "id": session.id,
        "status": session.status,
        "access_url": session.access_url,
        "expires_at": session.expires_at,
        "current_code": session.current_code,
        "files": session.files,
        "terminal_history": session.terminal_history
    }


@router.post("/sessions/{session_token}/save")
def save_session_state(
    session_token: str,
    state: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save current session state (code, files, terminal history)
    """
    session = db.query(PracticeSession).filter(
        PracticeSession.session_token == session_token,
        PracticeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.current_code = state.get("code")
    session.files = state.get("files")
    session.terminal_history = state.get("terminal_history")
    session.last_activity_at = datetime.utcnow()
    
    db.commit()
    
    return {"ok": True, "saved_at": datetime.utcnow()}


@router.post("/sessions/{session_token}/end")
def end_session(
    session_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End practice session and clean up resources
    """
    session = db.query(PracticeSession).filter(
        PracticeSession.session_token == session_token,
        PracticeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    
    db.commit()
    
    # In production: Clean up Docker container, release resources
    
    return {"ok": True, "message": "Session ended successfully"}


# ==================== Cloud Labs ====================

@router.get("/cloud-labs", response_model=List[CloudLabOut])
def list_cloud_labs(
    cloud_provider: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_premium: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List available cloud platform lab scenarios
    """
    query = db.query(CloudLabScenario)
    
    if cloud_provider:
        query = query.filter(CloudLabScenario.cloud_provider == cloud_provider)
    
    if difficulty:
        query = query.filter(CloudLabScenario.difficulty == difficulty)
    
    if is_premium is not None:
        query = query.filter(CloudLabScenario.is_premium == is_premium)
    
    labs = query.order_by(CloudLabScenario.difficulty, CloudLabScenario.points_reward).offset(skip).limit(limit).all()
    
    return labs


@router.get("/cloud-labs/{slug}", response_model=Dict[str, Any])
def get_cloud_lab(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed cloud lab scenario
    """
    lab = db.query(CloudLabScenario).filter(CloudLabScenario.slug == slug).first()
    
    if not lab:
        raise HTTPException(status_code=404, detail="Cloud lab not found")
    
    # Check premium access
    if lab.is_premium:
        # TODO: Check user subscription
        pass
    
    return {
        "id": lab.id,
        "title": lab.title,
        "slug": lab.slug,
        "description": lab.description,
        "cloud_provider": lab.cloud_provider,
        "services_used": lab.services_used,
        "objective": lab.objective,
        "instructions": lab.instructions,
        "architecture_diagram_url": lab.architecture_diagram_url,
        "difficulty": lab.difficulty,
        "estimated_time_minutes": lab.estimated_time_minutes,
        "points_reward": lab.points_reward,
        "coins_reward": lab.coins_reward,
        "is_premium": lab.is_premium
    }


# ==================== User Progress ====================

@router.get("/my-submissions")
def get_my_submissions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get user's submission history (returns empty list if not authenticated)
    """
    if not current_user:
        return []
    
    submissions = db.query(CodingSubmission).filter(
        CodingSubmission.user_id == current_user.id
    ).order_by(CodingSubmission.submitted_at.desc()).offset(skip).limit(limit).all()
    
    return submissions


@router.get("/my-stats")
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get user's coding practice statistics (returns defaults if not authenticated)
    """
    if not current_user:
        return {
            "total_submissions": 0,
            "perfect_solutions": 0,
            "challenges_attempted": 0,
            "coins_earned": 0,
            "avg_score": 0,
            "active_sessions": 0,
            "success_rate": 0,
            "total_coins": 0
        }
    # Total submissions
    total_submissions = db.query(func.count(CodingSubmission.id)).filter(
        CodingSubmission.user_id == current_user.id
    ).scalar()
    
    # Successful submissions
    successful = db.query(func.count(CodingSubmission.id)).filter(
        and_(
            CodingSubmission.user_id == current_user.id,
            CodingSubmission.status == "success",
            CodingSubmission.score >= 100
        )
    ).scalar()
    
    # Unique challenges solved
    solved_challenges = db.query(func.count(func.distinct(CodingSubmission.challenge_id))).filter(
        and_(
            CodingSubmission.user_id == current_user.id,
            CodingSubmission.status == "success",
            CodingSubmission.score >= 100
        )
    ).scalar()
    
    # Total coins earned
    total_coins = db.query(func.sum(CodingSubmission.coins_earned)).filter(
        CodingSubmission.user_id == current_user.id
    ).scalar() or 0
    
    # Languages used
    languages = db.query(
        CodingSubmission.language,
        func.count(CodingSubmission.id).label("count")
    ).filter(
        CodingSubmission.user_id == current_user.id
    ).group_by(CodingSubmission.language).all()
    
    return {
        "total_submissions": total_submissions or 0,
        "successful_submissions": successful or 0,
        "challenges_solved": solved_challenges or 0,
        "success_rate": (successful / total_submissions * 100) if total_submissions > 0 else 0,
        "total_coins_earned": total_coins,
        "total_coins": total_coins,  # Alias for frontend compatibility
        "languages_used": [{"language": lang, "count": count} for lang, count in languages]
    }


@router.post("/challenges/{slug}/unlock-hint")
def unlock_hint(
    slug: str,
    hint_index: int,
    cost: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Unlock a hint for a challenge (persists to database)
    """
    if not current_user:
        return {
            "success": True,
            "message": f"Hint {hint_index + 1} unlocked for {cost} coins"
        }
    
    challenge = db.query(CodingChallenge).filter(CodingChallenge.slug == slug).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Get the hint
    hint = db.query(ChallengeHint).filter(
        and_(
            ChallengeHint.challenge_id == challenge.id,
            ChallengeHint.hint_order == hint_index + 1
        )
    ).first()
    
    if not hint:
        raise HTTPException(status_code=404, detail="Hint not found")
    
    # Check if already unlocked
    already_unlocked = db.query(UserHintUnlock).filter(
        and_(
            UserHintUnlock.user_id == current_user.id,
            UserHintUnlock.hint_id == hint.id
        )
    ).first()
    
    if already_unlocked:
        return {
            "success": True,
            "message": f"Hint {hint_index + 1} already unlocked"
        }
    
    # Record the unlock
    hint_unlock = UserHintUnlock(
        user_id=current_user.id,
        hint_id=hint.id,
        coins_spent=cost
    )
    db.add(hint_unlock)
    db.commit()
    
    return {
        "success": True,
        "message": f"Hint {hint_index + 1} unlocked for {cost} coins"
    }



# ==================== Achievements ====================

@router.get("/achievements")
def get_user_achievements(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get all available achievements and user's unlocked achievements
    """
    # Get all achievements
    achievements = db.query(CodingAchievement).all()
    
    # Get user's unlocked achievements
    unlocked_ids = []
    if current_user:
        user_achievements = db.query(UserCodingAchievement).filter(
            UserCodingAchievement.user_id == current_user.id
        ).all()
        unlocked_ids = [ua.achievement_id for ua in user_achievements]
    
    result = []
    for achievement in achievements:
        result.append({
            "id": achievement.id,
            "key": achievement.key,
            "title": achievement.title,
            "description": achievement.description,
            "icon_url": achievement.icon_url,
            "badge_color": achievement.badge_color,
            "points": achievement.points,
            "coins": achievement.coins,
            "unlocked": achievement.id in unlocked_ids
        })
    
    return result


@router.post("/achievements/check")
async def check_and_award_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if user qualifies for any new achievements based on their stats
    This should be called after major actions (submission, etc.)
    """
    from sqlalchemy import func
    
    # Get user stats
    user_submissions = db.query(CodingSubmission).filter(
        CodingSubmission.user_id == current_user.id
    ).all()
    
    perfect_count = sum(1 for s in user_submissions if s.score >= 100)
    submission_count = len(user_submissions)
    challenges_completed = len(set(s.challenge_id for s in user_submissions if s.score >= 100))
    
    # Get all achievements
    all_achievements = db.query(CodingAchievement).all()
    
    # Check each achievement criteria
    newly_unlocked = []
    for achievement in all_achievements:
        # Check if already unlocked
        already_unlocked = db.query(UserCodingAchievement).filter(
            and_(
                UserCodingAchievement.user_id == current_user.id,
                UserCodingAchievement.achievement_id == achievement.id
            )
        ).first()
        
        if already_unlocked:
            continue
        
        # Check criteria
        should_unlock = False
        if achievement.criteria_type == "first_perfect" and perfect_count >= 1:
            should_unlock = True
        elif achievement.criteria_type == "perfect_solutions" and perfect_count >= (achievement.criteria_value or 10):
            should_unlock = True
        elif achievement.criteria_type == "challenges_solved" and challenges_completed >= (achievement.criteria_value or 5):
            should_unlock = True
        elif achievement.criteria_type == "submissions" and submission_count >= (achievement.criteria_value or 20):
            should_unlock = True
        
        # Unlock achievement
        if should_unlock:
            user_achievement = UserCodingAchievement(
                user_id=current_user.id,
                achievement_id=achievement.id
            )
            db.add(user_achievement)
            newly_unlocked.append({
                "id": achievement.id,
                "title": achievement.title,
                "points": achievement.points,
                "coins": achievement.coins
            })
    
    if newly_unlocked:
        db.commit()
    
    return {"newly_unlocked": newly_unlocked, "count": len(newly_unlocked)}



# ==================== Daily Challenges ====================

def _get_or_create_daily_challenge(db: Session) -> Optional[DailyChallenge]:
    """
    Get today's daily challenge or create one if it doesn't exist
    """
    from datetime import date
    today = date.today()
    
    # Check if today's challenge exists
    daily = db.query(DailyChallenge).filter(
        func.date(DailyChallenge.date) == today
    ).first()
    
    if daily:
        return daily
    
    # Create new daily challenge from random challenge
    challenges = db.query(CodingChallenge).filter(
        CodingChallenge.difficulty.in_(["easy", "medium"])
    ).all()
    
    if not challenges:
        return None
    
    import random
    chosen = random.choice(challenges)
    
    daily = DailyChallenge(
        date=datetime.utcnow(),
        challenge_id=chosen.id,
        bonus_coins=20,
        bonus_points=25
    )
    db.add(daily)
    db.commit()
    db.refresh(daily)
    return daily


@router.get("/daily-challenge")
def get_daily_challenge(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get today's daily challenge
    """
    daily = _get_or_create_daily_challenge(db)
    
    if not daily or not daily.challenge:
        raise HTTPException(status_code=404, detail="No daily challenge available")
    
    challenge = daily.challenge
    return {
        "id": challenge.id,
        "title": challenge.title,
        "slug": challenge.slug,
        "difficulty": challenge.difficulty,
        "category": challenge.category,
        "bonus_coins": daily.bonus_coins,
        "bonus_points": daily.bonus_points,
        "description": challenge.description,
        "problem_statement": challenge.problem_statement,
        "points": challenge.points
    }


@router.get("/daily-challenge/streak")
def get_daily_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's daily challenge streak
    """
    streak = db.query(UserDailyChallengeStreak).filter(
        UserDailyChallengeStreak.user_id == current_user.id
    ).first()
    
    if not streak:
        streak = UserDailyChallengeStreak(user_id=current_user.id)
        db.add(streak)
        db.commit()
        db.refresh(streak)
    
    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_solved": streak.total_solved,
        "last_solved_date": streak.last_solved_date
    }


@router.post("/daily-challenge/complete")
async def complete_daily_challenge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """
    Mark today's daily challenge as completed
    Updates streak and awards bonus coins
    """
    from datetime import date
    
    daily = _get_or_create_daily_challenge(db)
    if not daily:
        raise HTTPException(status_code=404, detail="No daily challenge available")
    
    # Get or create streak
    streak = db.query(UserDailyChallengeStreak).filter(
        UserDailyChallengeStreak.user_id == current_user.id
    ).first()
    
    if not streak:
        streak = UserDailyChallengeStreak(user_id=current_user.id)
        db.add(streak)
        db.flush()
    
    today_date = date.today()
    
    # Check if already completed today
    if streak.last_solved_date and streak.last_solved_date.date() == today_date:
        return {
            "message": "Already completed today's challenge",
            "current_streak": streak.current_streak,
            "bonus_coins": daily.bonus_coins
        }
    
    # Update streak
    yesterday = today_date - timedelta(days=1)
    if streak.last_solved_date and streak.last_solved_date.date() == yesterday:
        # Consecutive day - increment streak
        streak.current_streak += 1
    else:
        # Break in streak - start new one
        streak.current_streak = 1
    
    # Update longest streak
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    
    streak.total_solved += 1
    streak.last_solved_date = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Daily challenge completed!",
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "bonus_coins": daily.bonus_coins,
        "bonus_points": daily.bonus_points,
        "streak_milestone": streak.current_streak % 7 == 0  # Weekly milestone
    }


# ==================== Leaderboard ====================

@router.get("/leaderboard")
def get_leaderboard(
    timeframe: str = "all",  # all, month, week
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get coding practice leaderboard based on user performance
    Timeframe: 'all' (all-time), 'month' (last 30 days), 'week' (last 7 days)
    """
    
    # Calculate date filter
    date_filter = None
    if timeframe == "week":
        date_filter = datetime.utcnow() - timedelta(days=7)
    elif timeframe == "month":
        date_filter = datetime.utcnow() - timedelta(days=30)
    
    # Build query to get user stats
    query = db.query(
        User.id.label('user_id'),
        User.email.label('username'),
        func.count(func.distinct(CodingSubmission.challenge_id)).label('challenges_completed'),
        func.count(func.case((CodingSubmission.score >= 100, 1))).label('perfect_solutions'),
        func.sum(CodingSubmission.score).label('total_score'),
        func.sum(CodingSubmission.coins_earned).label('coins_earned'),
        func.count(CodingSubmission.id).label('total_submissions')
    ).join(
        CodingSubmission, CodingSubmission.user_id == User.id
    )
    
    if date_filter:
        query = query.filter(CodingSubmission.executed_at >= date_filter)
    
    # Filter to only users with submissions
    query = query.filter(CodingSubmission.status == 'success')
    
    query = query.group_by(User.id, User.email).order_by(
        func.sum(CodingSubmission.score).desc(),
        func.count(func.case((CodingSubmission.score >= 100, 1))).desc()
    ).limit(limit)
    
    results = query.all()
    
    # Format results as leaderboard entries
    leaderboard = []
    for rank, row in enumerate(results, 1):
        total_score = row.total_score or 0
        total_submissions = row.total_submissions or 1
        success_rate = (row.perfect_solutions / total_submissions * 100) if total_submissions > 0 else 0
        
        leaderboard.append({
            "rank": rank,
            "user_id": row.user_id,
            "username": row.username.split("@")[0] or f"User{row.user_id}",
            "total_score": int(total_score),
            "challenges_completed": row.challenges_completed or 0,
            "perfect_solutions": row.perfect_solutions or 0,
            "coins_earned": int(row.coins_earned or 0),
            "success_rate": round(success_rate, 1)
        })
    
    return leaderboard


# ==================== Categories & Languages ====================

@router.get("/categories")
def get_categories():
    """Get all available challenge categories"""
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} for cat in PracticeCategory]


@router.get("/languages")
def get_supported_languages():
    """Get all supported programming languages"""
    return [{"value": lang.value, "label": lang.value.title()} for lang in LanguageSupport]


@router.get("/simulators")
def get_simulator_types():
    """Get all available simulator types"""
    return [{"value": sim.value, "label": sim.value.replace("_", " ").title()} for sim in SimulatorType]


# Import SessionLocal for background task
from app.core.db import SessionLocal
