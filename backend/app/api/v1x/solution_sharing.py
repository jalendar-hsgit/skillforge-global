"""
Solution Sharing API
Community solutions, voting, and discussion
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User
from app.modelsx.solution_sharing import (
    ChallengeSolution, SolutionVote, SolutionComment, SolutionBookmark
)


router = APIRouter(prefix="/solutions", tags=["solutions"])


class SolutionShareRequest:
    def __init__(self, code: str, language: str, challenge_id: int, explanation: str = None):
        self.code = code
        self.language = language
        self.challenge_id = challenge_id
        self.explanation = explanation


class SolutionResponse:
    def __init__(self, solution: ChallengeSolution):
        self.id = solution.id
        self.challenge_id = solution.challenge_id
        self.user = {
            "id": solution.user.id,
            "username": solution.user.username,
            "avatar": solution.user.get("avatar", ""),
        }
        self.code = solution.code
        self.language = solution.language
        self.explanation = solution.explanation
        self.score = solution.score
        self.test_cases_passed = solution.test_cases_passed
        self.execution_time_ms = solution.execution_time_ms
        self.memory_used_mb = solution.memory_used_mb
        self.complexity_explanation = solution.complexity_explanation
        self.approach_tags = solution.approach_tags
        self.difficulty_for_user = solution.difficulty_for_user
        self.helpful_votes = solution.helpful_votes
        self.unhelpful_votes = solution.unhelpful_votes
        self.view_count = solution.view_count
        self.is_public = solution.is_public
        self.created_at = solution.created_at.isoformat() if solution.created_at else None


# Share a solution
@router.post("/challenges/{challenge_id}/share")
async def share_solution(
    challenge_id: int,
    code: str,
    language: str,
    explanation: Optional[str] = None,
    complexity_explanation: Optional[str] = None,
    approach_tags: Optional[List[str]] = None,
    difficulty_for_user: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Share a solution to a challenge with the community
    Requires authentication
    """
    # Verify challenge exists
    from app.modelsx.coding_practice import CodingChallenge
    challenge = db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if user has already submitted this challenge
    existing = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id,
        ChallengeSolution.challenge_id == challenge_id
    ).first()
    
    if not existing:
        # Create new solution
        solution = ChallengeSolution(
            challenge_id=challenge_id,
            user_id=current_user.id,
            code=code,
            language=language,
            explanation=explanation,
            complexity_explanation=complexity_explanation,
            approach_tags=approach_tags,
            difficulty_for_user=difficulty_for_user,
            is_public=True,
            score=90,  # Assume passed validation
            test_cases_passed=challenge.test_cases_count if hasattr(challenge, 'test_cases_count') else 0,
        )
    else:
        # Update existing solution
        existing.code = code
        existing.language = language
        existing.explanation = explanation
        existing.complexity_explanation = complexity_explanation
        existing.approach_tags = approach_tags
        existing.difficulty_for_user = difficulty_for_user
        existing.is_public = True
        solution = existing
    
    db.add(solution)
    db.commit()
    db.refresh(solution)
    
    return {
        "id": solution.id,
        "challenge_id": solution.challenge_id,
        "language": solution.language,
        "is_public": solution.is_public,
        "helpful_votes": solution.helpful_votes,
        "created_at": solution.created_at.isoformat() if solution.created_at else None,
    }


# Get community solutions for a challenge
@router.get("/challenges/{challenge_id}/solutions")
async def get_challenge_solutions(
    challenge_id: int,
    sort_by: str = Query("votes", regex="^(votes|recent|helpful)$"),
    language: Optional[str] = None,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Get community solutions for a challenge
    Sorted by votes (helpfulness), recency, or helpful/unhelpful ratio
    No authentication required - viewing is public
    """
    # Verify challenge exists
    from app.modelsx.coding_practice import CodingChallenge
    challenge = db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Build query
    query = db.query(ChallengeSolution).filter(
        ChallengeSolution.challenge_id == challenge_id,
        ChallengeSolution.is_public == True,
    )
    
    # Filter by language if specified
    if language:
        query = query.filter(ChallengeSolution.language == language)
    
    # Sort
    if sort_by == "votes":
        # Sort by helpful votes minus unhelpful votes
        query = query.order_by(
            desc(ChallengeSolution.helpful_votes - ChallengeSolution.unhelpful_votes)
        )
    elif sort_by == "helpful":
        # Sort by helpful vote percentage
        query = query.order_by(desc(ChallengeSolution.helpful_votes))
    else:  # recent
        query = query.order_by(desc(ChallengeSolution.created_at))
    
    # Paginate
    total = query.count()
    solutions = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "solutions": [
            {
                "id": sol.id,
                "user": {
                    "id": sol.user.id,
                    "username": sol.user.username,
                },
                "language": sol.language,
                "score": sol.score,
                "test_cases_passed": sol.test_cases_passed,
                "helpful_votes": sol.helpful_votes,
                "unhelpful_votes": sol.unhelpful_votes,
                "view_count": sol.view_count,
                "complexity_explanation": sol.complexity_explanation,
                "approach_tags": sol.approach_tags,
                "difficulty_for_user": sol.difficulty_for_user,
                "created_at": sol.created_at.isoformat() if sol.created_at else None,
            }
            for sol in solutions
        ]
    }


# Get detailed solution
@router.get("/solutions/{solution_id}")
async def get_solution(
    solution_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Get detailed solution with code, explanation, and comments
    """
    solution = db.query(ChallengeSolution).filter(ChallengeSolution.id == solution_id).first()
    if not solution or not solution.is_public:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    # Increment view count
    solution.view_count += 1
    db.commit()
    
    # Check if current user has voted
    user_vote = None
    if current_user:
        user_vote = db.query(SolutionVote).filter(
            SolutionVote.solution_id == solution_id,
            SolutionVote.user_id == current_user.id,
        ).first()
    
    return {
        "id": solution.id,
        "challenge_id": solution.challenge_id,
        "user": {
            "id": solution.user.id,
            "username": solution.user.username,
        },
        "code": solution.code,
        "language": solution.language,
        "explanation": solution.explanation,
        "score": solution.score,
        "test_cases_passed": solution.test_cases_passed,
        "execution_time_ms": solution.execution_time_ms,
        "memory_used_mb": solution.memory_used_mb,
        "complexity_explanation": solution.complexity_explanation,
        "approach_tags": solution.approach_tags,
        "difficulty_for_user": solution.difficulty_for_user,
        "helpful_votes": solution.helpful_votes,
        "unhelpful_votes": solution.unhelpful_votes,
        "view_count": solution.view_count,
        "user_vote": user_vote.vote_type if user_vote else None,
        "created_at": solution.created_at.isoformat() if solution.created_at else None,
    }


# Vote on a solution
@router.post("/solutions/{solution_id}/vote")
async def vote_on_solution(
    solution_id: int,
    vote_type: str,  # "helpful" or "unhelpful"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Vote on a solution (helpful/unhelpful)
    Users can only vote once per solution
    """
    if vote_type not in ["helpful", "unhelpful"]:
        raise HTTPException(status_code=400, detail="Vote must be 'helpful' or 'unhelpful'")
    
    solution = db.query(ChallengeSolution).filter(ChallengeSolution.id == solution_id).first()
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    # Check if user already voted
    existing_vote = db.query(SolutionVote).filter(
        SolutionVote.solution_id == solution_id,
        SolutionVote.user_id == current_user.id,
    ).first()
    
    if existing_vote:
        # Update vote
        old_type = existing_vote.vote_type
        existing_vote.vote_type = vote_type
        
        # Update counts
        if old_type == "helpful":
            solution.helpful_votes -= 1
        else:
            solution.unhelpful_votes -= 1
    else:
        # Create new vote
        vote = SolutionVote(
            solution_id=solution_id,
            user_id=current_user.id,
            vote_type=vote_type,
        )
        db.add(vote)
    
    # Update vote count for new vote
    if vote_type == "helpful":
        solution.helpful_votes += 1
    else:
        solution.unhelpful_votes += 1
    
    db.commit()
    db.refresh(solution)
    
    return {
        "solution_id": solution.id,
        "vote_type": vote_type,
        "helpful_votes": solution.helpful_votes,
        "unhelpful_votes": solution.unhelpful_votes,
    }


# Bookmark a solution
@router.post("/solutions/{solution_id}/bookmark")
async def bookmark_solution(
    solution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bookmark a solution for later reference
    """
    solution = db.query(ChallengeSolution).filter(ChallengeSolution.id == solution_id).first()
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    # Check if already bookmarked
    existing = db.query(SolutionBookmark).filter(
        SolutionBookmark.user_id == current_user.id,
        SolutionBookmark.solution_id == solution_id,
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Solution already bookmarked")
    
    bookmark = SolutionBookmark(
        user_id=current_user.id,
        solution_id=solution_id,
    )
    db.add(bookmark)
    db.commit()
    
    return {"message": "Solution bookmarked", "solution_id": solution_id}


# Get user's bookmarked solutions
@router.get("/bookmarks")
async def get_bookmarks(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all solutions bookmarked by current user
    """
    query = db.query(SolutionBookmark).filter(
        SolutionBookmark.user_id == current_user.id
    ).order_by(desc(SolutionBookmark.bookmarked_at))
    
    total = query.count()
    bookmarks = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "bookmarks": [
            {
                "id": bm.solution.id,
                "challenge_id": bm.solution.challenge_id,
                "language": bm.solution.language,
                "score": bm.solution.score,
                "helpful_votes": bm.solution.helpful_votes,
                "created_at": bm.solution.created_at.isoformat() if bm.solution.created_at else None,
                "bookmarked_at": bm.bookmarked_at.isoformat() if bm.bookmarked_at else None,
            }
            for bm in bookmarks
        ]
    }


# Get solutions by user
@router.get("/users/{user_id}/solutions")
async def get_user_solutions(
    user_id: int,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Get all public solutions shared by a user
    """
    query = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == user_id,
        ChallengeSolution.is_public == True,
    ).order_by(desc(ChallengeSolution.created_at))
    
    total = query.count()
    solutions = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "solutions": [
            {
                "id": sol.id,
                "challenge_id": sol.challenge_id,
                "language": sol.language,
                "score": sol.score,
                "helpful_votes": sol.helpful_votes,
                "unhelpful_votes": sol.unhelpful_votes,
                "created_at": sol.created_at.isoformat() if sol.created_at else None,
            }
            for sol in solutions
        ]
    }
