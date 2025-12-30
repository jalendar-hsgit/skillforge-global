"""
Discussion Forums & Q&A System API Endpoints
Supports community discussions, threads, replies, voting, and moderation
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.forums import (
    ForumCategory, ForumThread, ForumReply, ForumThreadVote, ForumReplyVote,
    ForumBookmark, ModeratorAction, ThreadStatus, ThreadType
)
from app.schemas.badges_forums import (
    ForumCategoryResponse, ForumThreadResponse, ForumThreadListResponse,
    ForumReplyResponse, ForumReplyCreateRequest, ForumThreadCreateRequest,
    ForumBookmarkResponse, ForumStatsResponse, ThreadSearchRequest,
    ThreadSearchResponse
)

router = APIRouter(prefix="/api/v1x/forums", tags=["forums"])


# ============================================================================
# CATEGORY ENDPOINTS
# ============================================================================

@router.get("/categories", response_model=List[ForumCategoryResponse])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all forum categories
    """
    categories = db.query(ForumCategory).filter(
        ForumCategory.is_active == True
    ).order_by(ForumCategory.display_order).all()
    
    return categories


@router.get("/categories/{category_id}", response_model=ForumCategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific category
    """
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category


# ============================================================================
# THREAD ENDPOINTS
# ============================================================================

@router.post("/threads", response_model=ForumThreadResponse)
async def create_thread(
    thread_data: ForumThreadCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new forum thread
    """
    # Verify category exists
    category = db.query(ForumCategory).filter(ForumCategory.id == thread_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    thread = ForumThread(
        category_id=thread_data.category_id,
        creator_id=current_user.id,
        title=thread_data.title,
        content=thread_data.content,
        thread_type=thread_data.thread_type.value,
        tags=thread_data.tags or []
    )
    
    db.add(thread)
    category.thread_count += 1
    db.commit()
    db.refresh(thread)
    
    return thread


@router.get("/threads", response_model=ForumThreadListResponse)
async def list_threads(
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("recent", pattern="recent|popular|unanswered|viewed"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List threads with optional filtering and sorting
    """
    query = db.query(ForumThread)
    
    if category_id:
        query = query.filter(ForumThread.category_id == category_id)
    
    if status:
        query = query.filter(ForumThread.status == status)
    else:
        # Exclude closed/archived by default
        query = query.filter(ForumThread.status.in_([ThreadStatus.OPEN.value, ThreadStatus.ANSWERED.value]))
    
    # Apply sorting
    if sort_by == "popular":
        query = query.order_by(desc(ForumThread.vote_count))
    elif sort_by == "viewed":
        query = query.order_by(desc(ForumThread.view_count))
    elif sort_by == "unanswered":
        query = query.filter(ForumThread.reply_count == 0)
        query = query.order_by(desc(ForumThread.created_at))
    else:  # recent
        query = query.order_by(desc(ForumThread.last_reply_at.isnot(None)), desc(ForumThread.created_at))
    
    total = query.count()
    threads = query.offset(skip).limit(limit).all()
    
    return ForumThreadListResponse(total=total, threads=threads)


@router.get("/threads/{thread_id}", response_model=ForumThreadResponse)
async def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a thread with all its replies
    """
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Increment view count
    thread.view_count += 1
    db.commit()
    
    return thread


@router.put("/threads/{thread_id}", response_model=ForumThreadResponse)
async def update_thread(
    thread_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a thread (only creator can edit)
    """
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only edit own threads")
    
    if "title" in update_data:
        thread.title = update_data["title"]
    if "content" in update_data:
        thread.content = update_data["content"]
    if "tags" in update_data:
        thread.tags = update_data["tags"]
    
    thread.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(thread)
    
    return thread


@router.delete("/threads/{thread_id}", status_code=204)
async def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a thread (only creator can delete)
    """
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete own threads")
    
    category = thread.category
    if category:
        category.thread_count = max(0, category.thread_count - 1)
        category.reply_count = max(0, category.reply_count - thread.reply_count)
    
    db.delete(thread)
    db.commit()


# ============================================================================
# REPLY ENDPOINTS
# ============================================================================

@router.post("/threads/{thread_id}/replies", response_model=ForumReplyResponse)
async def create_reply(
    thread_id: int,
    reply_data: ForumReplyCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a reply to a thread
    """
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.is_locked:
        raise HTTPException(status_code=403, detail="Thread is locked")
    
    reply = ForumReply(
        thread_id=thread_id,
        author_id=current_user.id,
        content=reply_data.content,
        code_snippet=reply_data.code_snippet,
        language=reply_data.language,
        parent_reply_id=reply_data.parent_reply_id
    )
    
    db.add(reply)
    thread.reply_count += 1
    thread.last_reply_at = datetime.utcnow()
    
    # Update category
    if thread.category:
        thread.category.reply_count += 1
    
    db.commit()
    db.refresh(reply)
    
    return reply


@router.get("/threads/{thread_id}/replies", response_model=List[ForumReplyResponse])
async def get_thread_replies(
    thread_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("helpful", pattern="helpful|recent"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get replies for a thread
    """
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    query = db.query(ForumReply).filter(
        and_(
            ForumReply.thread_id == thread_id,
            ForumReply.is_deleted == False,
            ForumReply.parent_reply_id.isnot(None) == False  # Top-level replies only
        )
    )
    
    if sort_by == "helpful":
        query = query.order_by(desc(ForumReply.vote_count), desc(ForumReply.is_accepted_answer))
    else:
        query = query.order_by(desc(ForumReply.created_at))
    
    replies = query.offset(skip).limit(limit).all()
    
    return replies


@router.put("/replies/{reply_id}", response_model=ForumReplyResponse)
async def update_reply(
    reply_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a reply (only author can edit)
    """
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    if reply.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only edit own replies")
    
    if "content" in update_data:
        reply.content = update_data["content"]
        reply.edited_count += 1
    
    reply.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reply)
    
    return reply


@router.delete("/replies/{reply_id}", status_code=204)
async def delete_reply(
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a reply (soft delete)
    """
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    if reply.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete own replies")
    
    reply.is_deleted = True
    reply.deleted_reason = "User deleted"
    
    thread = reply.thread
    if thread:
        thread.reply_count = max(0, thread.reply_count - 1)
    
    db.commit()


# ============================================================================
# VOTING ENDPOINTS
# ============================================================================

@router.post("/threads/{thread_id}/vote", response_model=ForumThreadResponse)
async def vote_thread(
    thread_id: int,
    vote_type: str = Query("upvote", pattern="upvote|downvote"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Vote on a thread (upvote/downvote)
    """
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Check existing vote
    existing = db.query(ForumThreadVote).filter(
        and_(
            ForumThreadVote.thread_id == thread_id,
            ForumThreadVote.user_id == current_user.id
        )
    ).first()
    
    if existing:
        if existing.vote_type == vote_type:
            raise HTTPException(status_code=400, detail="Already voted")
        # Change vote
        old_vote = existing.vote_type
        existing.vote_type = vote_type
        thread.vote_count += 2 if vote_type == "upvote" else -2
    else:
        # New vote
        vote = ForumThreadVote(
            thread_id=thread_id,
            user_id=current_user.id,
            vote_type=vote_type
        )
        db.add(vote)
        thread.vote_count += 1 if vote_type == "upvote" else -1
    
    db.commit()
    db.refresh(thread)
    
    return thread


@router.post("/replies/{reply_id}/vote", response_model=ForumReplyResponse)
async def vote_reply(
    reply_id: int,
    vote_type: str = Query("upvote", regex="upvote|downvote"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Vote on a reply (upvote/downvote)
    """
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    # Check existing vote
    existing = db.query(ForumReplyVote).filter(
        and_(
            ForumReplyVote.reply_id == reply_id,
            ForumReplyVote.user_id == current_user.id
        )
    ).first()
    
    if existing:
        if existing.vote_type == vote_type:
            raise HTTPException(status_code=400, detail="Already voted")
        # Change vote
        existing.vote_type = vote_type
        reply.vote_count += 2 if vote_type == "upvote" else -2
    else:
        # New vote
        vote = ForumReplyVote(
            reply_id=reply_id,
            user_id=current_user.id,
            vote_type=vote_type
        )
        db.add(vote)
        reply.vote_count += 1 if vote_type == "upvote" else -1
    
    db.commit()
    db.refresh(reply)
    
    return reply


# ============================================================================
# BOOKMARKS & SEARCH
# ============================================================================

@router.post("/threads/{thread_id}/bookmark", response_model=ForumBookmarkResponse)
async def bookmark_thread(
    thread_id: int,
    note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmark a thread for later
    """
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Check if already bookmarked
    existing = db.query(ForumBookmark).filter(
        and_(
            ForumBookmark.user_id == current_user.id,
            ForumBookmark.thread_id == thread_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already bookmarked")
    
    bookmark = ForumBookmark(
        user_id=current_user.id,
        thread_id=thread_id,
        note=note
    )
    
    thread.bookmark_count += 1
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    
    return bookmark


@router.get("/user/bookmarks", response_model=List[ForumBookmarkResponse])
async def get_user_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's bookmarked threads
    """
    bookmarks = db.query(ForumBookmark).filter(
        ForumBookmark.user_id == current_user.id
    ).order_by(desc(ForumBookmark.created_at)).offset(skip).limit(limit).all()
    
    return bookmarks


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a bookmark
    """
    bookmark = db.query(ForumBookmark).filter(ForumBookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    if bookmark.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete own bookmarks")
    
    thread = bookmark.thread
    if thread:
        thread.bookmark_count = max(0, thread.bookmark_count - 1)
    
    db.delete(bookmark)
    db.commit()


@router.post("/search", response_model=ThreadSearchResponse)
async def search_threads(
    search_data: ThreadSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for threads by query, category, tags, status
    """
    query = db.query(ForumThread).filter(
        or_(
            ForumThread.title.ilike(f"%{search_data.query}%"),
            ForumThread.content.ilike(f"%{search_data.query}%")
        )
    )
    
    if search_data.category_id:
        query = query.filter(ForumThread.category_id == search_data.category_id)
    
    if search_data.status:
        query = query.filter(ForumThread.status == search_data.status)
    
    if search_data.tags:
        for tag in search_data.tags:
            query = query.filter(ForumThread.tags.contains([tag]))
    
    # Apply sorting
    if search_data.sort_by == "popular":
        query = query.order_by(desc(ForumThread.vote_count))
    elif search_data.sort_by == "answers":
        query = query.order_by(desc(ForumThread.reply_count))
    elif search_data.sort_by == "views":
        query = query.order_by(desc(ForumThread.view_count))
    else:
        query = query.order_by(desc(ForumThread.created_at))
    
    total = query.count()
    threads = query.offset(skip).limit(limit).all()
    
    return ThreadSearchResponse(
        total=total,
        threads=threads,
        facets={}  # Can be expanded with category counts, tag counts, etc
    )


@router.get("/user/threads", response_model=ForumStatsResponse)
async def get_user_forum_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's forum statistics (threads, replies, bookmarks)
    """
    target_user_id = user_id or current_user.id
    
    user_threads = db.query(ForumThread).filter(
        ForumThread.creator_id == target_user_id
    ).all()
    
    bookmarks = db.query(ForumBookmark).filter(
        ForumBookmark.user_id == target_user_id
    ).all()
    
    # Count helpful replies
    helpful_replies = db.query(ForumReply).filter(
        and_(
            ForumReply.author_id == target_user_id,
            ForumReply.vote_count > 0
        )
    ).count()
    
    return ForumStatsResponse(
        total_threads=len(user_threads),
        total_replies=sum(t.reply_count for t in user_threads),
        total_bookmarks=len(bookmarks),
        helpful_replies=helpful_replies,
        user_threads=user_threads,
        bookmarks=bookmarks
    )
