"""
Comments on Solutions API
Discussion and feedback on shared solutions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User
from app.modelsx.solution_sharing import SolutionComment


router = APIRouter(prefix="/solutions", tags=["solution-comments"])


# Post a comment on a solution
@router.post("/{solution_id}/comments")
async def post_comment(
    solution_id: int,
    comment: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Post a comment on a solution"""
    from app.modelsx.solution_sharing import ChallengeSolution
    
    # Verify solution exists
    solution = db.query(ChallengeSolution).filter(ChallengeSolution.id == solution_id).first()
    if not solution or not solution.is_public:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    if not comment or len(comment.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    
    # Create comment
    new_comment = SolutionComment(
        solution_id=solution_id,
        user_id=current_user.id,
        comment=comment.strip(),
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {
        "id": new_comment.id,
        "user": current_user.username,
        "comment": new_comment.comment,
        "helpful_votes": new_comment.helpful_votes,
        "created_at": new_comment.created_at.isoformat(),
    }


# Get comments on a solution
@router.get("/{solution_id}/comments")
async def get_comments(
    solution_id: int,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get all comments on a solution"""
    from app.modelsx.solution_sharing import ChallengeSolution
    
    # Verify solution exists
    solution = db.query(ChallengeSolution).filter(ChallengeSolution.id == solution_id).first()
    if not solution or not solution.is_public:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    # Get comments
    query = db.query(SolutionComment).filter(
        SolutionComment.solution_id == solution_id
    ).order_by(desc(SolutionComment.created_at))
    
    total = query.count()
    comments = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "comments": [
            {
                "id": c.id,
                "user": {
                    "id": c.user.id,
                    "username": c.user.username,
                },
                "comment": c.comment,
                "helpful_votes": c.helpful_votes,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in comments
        ]
    }


# Delete a comment
@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment (only own comments or admin)"""
    comment = db.query(SolutionComment).filter(SolutionComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check ownership
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own comments")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted"}


# Mark comment as helpful
@router.post("/comments/{comment_id}/helpful")
async def mark_helpful(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a comment as helpful"""
    comment = db.query(SolutionComment).filter(SolutionComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Increment helpful votes
    comment.helpful_votes += 1
    db.commit()
    db.refresh(comment)
    
    return {
        "id": comment.id,
        "helpful_votes": comment.helpful_votes,
    }
