"""
Code Snippets Library API
Reusable code patterns and solutions for common problems
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from app.modelsx.code_snippets import (
    CodeSnippet, SnippetVote, SnippetCopy,
    SnippetLanguage, SnippetCategory
)

router = APIRouter(prefix="/code-snippets", tags=["Code Snippets"])


# ==================== Schemas ====================

class SnippetOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    category: str
    language: str
    code: str
    explanation: Optional[str]
    tags: Optional[List[str]]
    complexity: Optional[str]
    uses_count: int
    helpful_count: int
    is_community: bool
    
    class Config:
        from_attributes = True


class SnippetListOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    category: str
    language: str
    tags: Optional[List[str]]
    complexity: Optional[str]
    uses_count: int
    helpful_count: int
    
    class Config:
        from_attributes = True


# ==================== Snippets API ====================

@router.get("/", response_model=List[SnippetListOut])
def list_snippets(
    category: Optional[str] = None,
    language: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List available code snippets with filtering
    """
    query = db.query(CodeSnippet)
    
    if category:
        query = query.filter(CodeSnippet.category == category)
    
    if language:
        query = query.filter(CodeSnippet.language == language)
    
    if search:
        query = query.filter(
            (CodeSnippet.title.ilike(f"%{search}%")) |
            (CodeSnippet.description.ilike(f"%{search}%")) |
            (CodeSnippet.keywords.contains([search]))
        )
    
    snippets = query.order_by(CodeSnippet.helpful_count.desc()).offset(skip).limit(limit).all()
    return snippets


@router.get("/{slug}", response_model=SnippetOut)
def get_snippet(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get a specific snippet by slug
    """
    snippet = db.query(CodeSnippet).filter(CodeSnippet.slug == slug).first()
    
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    # Log copy if user viewed full snippet
    if current_user:
        # Don't increment uses here - only on actual copy
        pass
    
    return snippet


@router.post("/{slug}/copy")
def copy_snippet(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Record snippet copy and increment usage counter
    """
    snippet = db.query(CodeSnippet).filter(CodeSnippet.slug == slug).first()
    
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    # Increment uses
    snippet.uses_count += 1
    
    # Log copy event if user is authenticated
    if current_user:
        copy_record = SnippetCopy(
            user_id=current_user.id,
            snippet_id=snippet.id,
            context="code_snippets_page"
        )
        db.add(copy_record)
    
    db.commit()
    
    return {
        "success": True,
        "code": snippet.code,
        "message": "Snippet copied successfully"
    }


@router.post("/{snippet_id}/vote")
def vote_snippet(
    snippet_id: int,
    vote_type: str = Query("helpful"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Vote on snippet helpfulness
    """
    snippet = db.query(CodeSnippet).filter(CodeSnippet.id == snippet_id).first()
    
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    # Check if already voted
    existing_vote = db.query(SnippetVote).filter(
        and_(
            SnippetVote.user_id == current_user.id,
            SnippetVote.snippet_id == snippet_id
        )
    ).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.vote_type = vote_type
    else:
        # Create new vote
        vote = SnippetVote(
            user_id=current_user.id,
            snippet_id=snippet_id,
            vote_type=vote_type
        )
        db.add(vote)
    
    # Update snippet helpful count
    helpful_votes = db.query(func.count(SnippetVote.id)).filter(
        and_(
            SnippetVote.snippet_id == snippet_id,
            SnippetVote.vote_type == "helpful"
        )
    ).scalar()
    
    snippet.helpful_count = helpful_votes
    db.commit()
    
    return {
        "success": True,
        "helpful_count": snippet.helpful_count
    }


# ==================== Categories & Languages ====================

@router.get("/categories/list")
def get_categories():
    """Get all snippet categories"""
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} for cat in SnippetCategory]


@router.get("/languages/list")
def get_languages():
    """Get all supported snippet languages"""
    return [{"value": lang.value, "label": lang.value.title()} for lang in SnippetLanguage]


# ==================== Search & Discovery ====================

@router.get("/search")
def search_snippets(
    q: str = Query(..., min_length=2),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Full-text search snippets
    """
    snippets = db.query(CodeSnippet).filter(
        (CodeSnippet.title.ilike(f"%{q}%")) |
        (CodeSnippet.description.ilike(f"%{q}%")) |
        (CodeSnippet.explanation.ilike(f"%{q}%"))
    ).order_by(
        CodeSnippet.helpful_count.desc(),
        CodeSnippet.uses_count.desc()
    ).offset(skip).limit(limit).all()
    
    return [SnippetListOut.from_orm(s) for s in snippets]


@router.get("/trending")
def get_trending_snippets(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get trending/most-used snippets
    """
    snippets = db.query(CodeSnippet).order_by(
        CodeSnippet.uses_count.desc()
    ).limit(limit).all()
    
    return snippets
