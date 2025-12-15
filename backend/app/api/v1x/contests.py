"""Contest and competition management API endpoints."""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.contests import (
    Contest, ContestStatus, ContestType, ContestParticipant, 
    ContestSubmission, ContestLeaderboard, ContestChallenge, 
    ContestPrize, ContestTeam, ContestRound
)
from app.schemas.contest import (
    ContestCreate, ContestUpdate, ContestResponse, 
    ContestDetailResponse, ContestParticipationResponse, 
    ContestSubmissionRequest, ContestSubmissionResponse,
    ContestLeaderboardResponse, ContestListResponse
)

router = APIRouter(prefix="/api/v1x/contests", tags=["contests"])


# ============ PUBLIC ENDPOINTS ============

@router.get("", response_model=List[ContestListResponse])
def list_contests(
    status_filter: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: str = Query("start_time", regex="^(start_time|prize_pool|participants)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all public contests with filters."""
    query = db.query(Contest).filter(Contest.is_public == True)
    
    if status_filter:
        query = query.filter(Contest.status == status_filter)
    if category:
        query = query.filter(Contest.category == category)
    
    # Sorting
    if sort_by == "start_time":
        query = query.order_by(Contest.start_time)
    elif sort_by == "prize_pool":
        query = query.order_by(desc(Contest.total_prize_pool))
    elif sort_by == "participants":
        query = query.order_by(desc(Contest.total_participants))
    
    contests = query.offset(skip).limit(limit).all()
    return contests


@router.get("/featured", response_model=List[ContestListResponse])
def get_featured_contests(
    db: Session = Depends(get_db),
):
    """Get featured contests."""
    return db.query(Contest).filter(
        Contest.is_featured == True,
        Contest.is_public == True,
        Contest.status.in_([ContestStatus.UPCOMING, ContestStatus.ACTIVE])
    ).order_by(desc(Contest.total_prize_pool)).limit(10).all()


@router.get("/{contest_id}", response_model=ContestDetailResponse)
def get_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get contest details."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    # Check participation
    participant = db.query(ContestParticipant).filter(
        and_(ContestParticipant.contest_id == contest_id, 
             ContestParticipant.user_id == current_user.id)
    ).first()
    
    # Build response
    result = {
        **{k: getattr(contest, k) for k in contest.__table__.columns.keys()},
        "is_participant": participant is not None,
        "participant_rank": participant.rank if participant else None,
        "participant_score": participant.total_points if participant else 0,
    }
    return result


# ============ PARTICIPATION ENDPOINTS ============

@router.post("/{contest_id}/join", response_model=ContestParticipationResponse)
def join_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join a contest."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    # Check if already joined
    existing = db.query(ContestParticipant).filter(
        and_(ContestParticipant.contest_id == contest_id,
             ContestParticipant.user_id == current_user.id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already joined this contest")
    
    # Check registration deadline
    if datetime.utcnow() > contest.registration_deadline:
        raise HTTPException(status_code=400, detail="Registration deadline passed")
    
    # Check max participants
    if contest.max_participants:
        count = db.query(ContestParticipant).filter(
            ContestParticipant.contest_id == contest_id
        ).count()
        if count >= contest.max_participants:
            raise HTTPException(status_code=400, detail="Contest is full")
    
    # Create participation
    participant = ContestParticipant(
        contest_id=contest_id,
        user_id=current_user.id,
        joined_at=datetime.utcnow()
    )
    db.add(participant)
    contest.total_participants += 1
    db.commit()
    db.refresh(participant)
    
    return participant


@router.post("/{contest_id}/leave")
def leave_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Leave a contest."""
    participant = db.query(ContestParticipant).filter(
        and_(ContestParticipant.contest_id == contest_id,
             ContestParticipant.user_id == current_user.id)
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Not a participant in this contest")
    
    participant.is_active = False
    participant.withdrew_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Left contest"}


@router.get("/my/list", response_model=List[ContestParticipationResponse])
def get_my_contests(
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's contest participations."""
    query = db.query(ContestParticipant).filter(
        ContestParticipant.user_id == current_user.id,
        ContestParticipant.is_active == True
    )
    
    if status_filter:
        query = query.join(Contest).filter(Contest.status == status_filter)
    
    return query.all()


# ============ SUBMISSION ENDPOINTS ============

@router.post("/{contest_id}/submit", response_model=ContestSubmissionResponse)
def submit_solution(
    contest_id: int,
    submission: ContestSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit solution to contest challenge."""
    # Verify participation
    participant = db.query(ContestParticipant).filter(
        and_(ContestParticipant.contest_id == contest_id,
             ContestParticipant.user_id == current_user.id,
             ContestParticipant.is_active == True)
    ).first()
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant in this contest")
    
    # Verify contest is active
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if contest.status != ContestStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Contest is not active")
    
    # Verify challenge is in contest
    challenge = db.query(ContestChallenge).filter(
        and_(ContestChallenge.contest_id == contest_id,
             ContestChallenge.challenge_id == submission.challenge_id)
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not in this contest")
    
    # Create submission
    sub = ContestSubmission(
        contest_id=contest_id,
        user_id=current_user.id,
        challenge_id=submission.challenge_id,
        code=submission.code,
        language=submission.language,
        status="pending"
    )
    db.add(sub)
    contest.total_submissions += 1
    db.commit()
    db.refresh(sub)
    
    # TODO: Queue for execution in background
    
    return sub


@router.get("/{contest_id}/submissions", response_model=List[ContestSubmissionResponse])
def get_submissions(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's submissions for contest."""
    participant = db.query(ContestParticipant).filter(
        and_(ContestParticipant.contest_id == contest_id,
             ContestParticipant.user_id == current_user.id)
    ).first()
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant in this contest")
    
    return db.query(ContestSubmission).filter(
        and_(ContestSubmission.contest_id == contest_id,
             ContestSubmission.user_id == current_user.id)
    ).order_by(desc(ContestSubmission.submitted_at)).all()


@router.get("/{contest_id}/submissions/{submission_id}", response_model=ContestSubmissionResponse)
def get_submission(
    contest_id: int,
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get submission details."""
    submission = db.query(ContestSubmission).filter(
        and_(ContestSubmission.id == submission_id,
             ContestSubmission.contest_id == contest_id)
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Only owner or contest creator can view
    if submission.user_id != current_user.id:
        contest = db.query(Contest).filter(Contest.id == contest_id).first()
        if contest.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Permission denied")
    
    return submission


# ============ LEADERBOARD ENDPOINTS ============

@router.get("/{contest_id}/leaderboard", response_model=List[ContestLeaderboardResponse])
def get_leaderboard(
    contest_id: int,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get contest leaderboard."""
    return db.query(ContestLeaderboard).filter(
        ContestLeaderboard.contest_id == contest_id
    ).order_by(ContestLeaderboard.rank).limit(limit).all()


@router.get("/{contest_id}/leaderboard/user/{user_id}", response_model=ContestLeaderboardResponse)
def get_user_leaderboard_entry(
    contest_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get specific user's leaderboard entry."""
    entry = db.query(ContestLeaderboard).filter(
        and_(ContestLeaderboard.contest_id == contest_id,
             ContestLeaderboard.user_id == user_id)
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="User not in leaderboard")
    
    return entry


@router.post("/{contest_id}/leaderboard/refresh")
def refresh_leaderboard(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Refresh leaderboard (admin only)."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest or contest.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Get all participants with their scores
    participants = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id
    ).order_by(
        desc(ContestParticipant.total_points),
        ContestParticipant.last_submission_time
    ).all()
    
    # Update leaderboard
    for idx, participant in enumerate(participants, 1):
        entry = db.query(ContestLeaderboard).filter(
            and_(ContestLeaderboard.contest_id == contest_id,
                 ContestLeaderboard.user_id == participant.user_id)
        ).first()
        
        if not entry:
            entry = ContestLeaderboard(
                contest_id=contest_id,
                user_id=participant.user_id
            )
            db.add(entry)
        
        entry.rank = idx
        entry.score = participant.total_points
        entry.challenges_solved = participant.challenges_solved
        entry.last_accepted_time = participant.last_submission_time
        entry.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Leaderboard refreshed"}


# ============ ADMIN ENDPOINTS ============

@router.post("", response_model=ContestResponse)
def create_contest(
    contest_data: ContestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new contest (admin only)."""
    # TODO: Add admin check
    
    contest = Contest(
        **contest_data.dict(),
        created_by_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(contest)
    db.commit()
    db.refresh(contest)
    
    return contest


@router.put("/{contest_id}", response_model=ContestResponse)
def update_contest(
    contest_id: int,
    contest_data: ContestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update contest (creator only)."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest or contest.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Update fields
    update_data = contest_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contest, field, value)
    
    contest.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contest)
    
    return contest


@router.delete("/{contest_id}")
def delete_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete contest (creator only)."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest or contest.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    db.delete(contest)
    db.commit()
    
    return {"message": "Contest deleted"}


@router.post("/{contest_id}/challenges", response_model=dict)
def add_challenge_to_contest(
    contest_id: int,
    challenge_id: int,
    points: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add challenge to contest."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest or contest.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Check challenge exists
    challenge = db.query(ContestChallenge).filter(
        and_(ContestChallenge.contest_id == contest_id,
             ContestChallenge.challenge_id == challenge_id)
    ).first()
    if challenge:
        raise HTTPException(status_code=400, detail="Challenge already in contest")
    
    challenge = ContestChallenge(
        contest_id=contest_id,
        challenge_id=challenge_id,
        points=points
    )
    db.add(challenge)
    db.commit()
    
    return {"message": "Challenge added"}


@router.delete("/{contest_id}/challenges/{challenge_id}")
def remove_challenge_from_contest(
    contest_id: int,
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove challenge from contest."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest or contest.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    challenge = db.query(ContestChallenge).filter(
        and_(ContestChallenge.contest_id == contest_id,
             ContestChallenge.challenge_id == challenge_id)
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    db.delete(challenge)
    db.commit()
    
    return {"message": "Challenge removed"}


@router.get("/{contest_id}/analytics")
def get_contest_analytics(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get contest analytics (creator only)."""
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest or contest.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Calculate stats
    participants = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id,
        ContestParticipant.is_active == True
    ).count()
    
    submissions = db.query(ContestSubmission).filter(
        ContestSubmission.contest_id == contest_id
    ).count()
    
    accepted = db.query(ContestSubmission).filter(
        and_(ContestSubmission.contest_id == contest_id,
             ContestSubmission.status == "passed")
    ).count()
    
    avg_score = db.query(ContestParticipant).filter(
        ContestParticipant.contest_id == contest_id
    ).count()
    
    return {
        "contest_id": contest_id,
        "total_participants": participants,
        "total_submissions": submissions,
        "accepted_submissions": accepted,
        "submission_success_rate": (accepted / submissions * 100) if submissions > 0 else 0,
        "challenges_count": len(contest.challenges),
        "prize_pool": contest.total_prize_pool,
    }
