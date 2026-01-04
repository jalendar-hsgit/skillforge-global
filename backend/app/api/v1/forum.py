"""
Forum API Router - Phase 3.3
Topics, threads, replies management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.core.db import get_db
from app.models import User
from app.modelsx.forums import ForumCategory as ForumTopic, ForumThread, ForumReply
from app.schemas.social_schemas import (
    ForumTopicResponse, ForumTopicCreate, ForumTopicUpdate,
    ForumThreadResponse, ForumThreadCreate, ForumThreadUpdate,
    ForumReplyResponse, ForumReplyCreate, ForumReplyUpdate,
    ForumThreadWithReplies
)
from app.api.deps import get_current_user
from app.services.realtime_events import on_forum_thread_created, on_forum_reply_posted

router = APIRouter(prefix="/forum", tags=["forum"])


# ==================== TOPICS ====================

@router.get("/topics", response_model=List[ForumTopicResponse])
def get_forum_topics(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get all forum topics"""
    topics = db.query(ForumTopic).order_by(
        desc(ForumTopic.is_pinned),
        desc(ForumTopic.last_activity_at)
    ).offset(skip).limit(limit).all()
    return topics


@router.get("/topics/{topic_slug}", response_model=ForumTopicResponse)
def get_forum_topic(topic_slug: str, db: Session = Depends(get_db)):
    """Get specific forum topic"""
    topic = db.query(ForumTopic).filter(ForumTopic.slug == topic_slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.post("/topics", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
def create_forum_topic(
    topic: ForumTopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new forum topic (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check slug uniqueness
    existing = db.query(ForumTopic).filter(ForumTopic.slug == topic.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Topic slug already exists")
    
    new_topic = ForumTopic(**topic.dict())
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic


@router.patch("/topics/{topic_id}", response_model=ForumTopicResponse)
def update_forum_topic(
    topic_id: int,
    update_data: ForumTopicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update forum topic (admin only)"""
    if current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    update_fields = update_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(topic, key, value)
    
    db.commit()
    db.refresh(topic)
    return topic


# ==================== THREADS ====================

@router.get("/topics/{topic_slug}/threads", response_model=List[ForumThreadResponse])
def get_topic_threads(
    topic_slug: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get threads for a topic"""
    topic = db.query(ForumTopic).filter(ForumTopic.slug == topic_slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    threads = db.query(ForumThread).filter(
        ForumThread.topic_id == topic.id
    ).order_by(
        desc(ForumThread.is_pinned),
        desc(ForumThread.last_reply_at)
    ).offset(skip).limit(limit).all()
    
    return threads


@router.get("/threads/{thread_id}", response_model=ForumThreadWithReplies)
def get_thread_detail(thread_id: int, db: Session = Depends(get_db)):
    """Get thread with all replies"""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Increment view count
    thread.view_count += 1
    db.commit()
    
    return thread


@router.post("/topics/{topic_id}/threads", response_model=ForumThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    topic_id: int,
    thread_data: ForumThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new thread in a topic"""
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    new_thread = ForumThread(
        topic_id=topic_id,
        user_id=current_user.id,
        title=thread_data.title,
        content=thread_data.content
    )
    
    db.add(new_thread)
    topic.thread_count += 1
    topic.last_activity_at = thread_data.__class__.__module__  # timestamp
    
    db.commit()
    db.refresh(new_thread)
    
    # Emit real-time event
    await on_forum_thread_created(
        thread_id=new_thread.id,
        topic_id=topic_id,
        author_id=current_user.id,
        author_name=current_user.name or current_user.email,
        title=thread_data.title,
        created_at=new_thread.created_at
    )
    
    return new_thread


@router.patch("/threads/{thread_id}", response_model=ForumThreadResponse)
def update_thread(
    thread_id: int,
    update_data: ForumThreadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update thread (author or admin)"""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this thread")
    
    update_fields = update_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(thread, key, value)
    
    db.commit()
    db.refresh(thread)
    return thread


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thread(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete thread (author or admin)"""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this thread")
    
    topic = thread.topic
    topic.thread_count = max(0, topic.thread_count - 1)
    
    db.delete(thread)
    db.commit()


# ==================== REPLIES ====================

@router.get("/threads/{thread_id}/replies", response_model=List[ForumReplyResponse])
def get_thread_replies(
    thread_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get replies for a thread"""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    replies = db.query(ForumReply).filter(
        ForumReply.thread_id == thread_id
    ).order_by(
        desc(ForumReply.is_best_answer),
        ForumReply.created_at
    ).offset(skip).limit(limit).all()
    
    return replies


@router.post("/threads/{thread_id}/replies", response_model=ForumReplyResponse, status_code=status.HTTP_201_CREATED)
async def create_reply(
    thread_id: int,
    reply_data: ForumReplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add reply to thread"""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.is_locked:
        raise HTTPException(status_code=400, detail="Thread is locked")
    
    new_reply = ForumReply(
        thread_id=thread_id,
        user_id=current_user.id,
        content=reply_data.content
    )
    
    db.add(new_reply)
    thread.reply_count += 1
    thread.last_reply_at = __import__('datetime').datetime.utcnow()
    thread.topic.last_activity_at = thread.last_reply_at
    
    db.commit()
    db.refresh(new_reply)
    
    # Emit real-time event
    await on_forum_reply_posted(
        reply_id=new_reply.id,
        thread_id=thread_id,
        topic_id=thread.topic_id,
        author_id=current_user.id,
        author_name=current_user.name or current_user.email,
        content=reply_data.content,
        created_at=new_reply.created_at
    )
    
    return new_reply


@router.patch("/replies/{reply_id}", response_model=ForumReplyResponse)
def update_reply(
    reply_id: int,
    update_data: ForumReplyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update reply (author or admin)"""
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    if reply.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this reply")
    
    update_fields = update_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(reply, key, value)
    
    db.commit()
    db.refresh(reply)
    return reply


@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reply(
    reply_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete reply (author or admin)"""
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    if reply.user_id != current_user.id and current_user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this reply")
    
    thread = reply.thread
    thread.reply_count = max(0, thread.reply_count - 1)
    thread.topic.reply_count = max(0, thread.topic.reply_count - 1)
    
    db.delete(reply)
    db.commit()


@router.post("/replies/{reply_id}/helpful", response_model=ForumReplyResponse)
def mark_reply_helpful(
    reply_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark reply as helpful"""
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    reply.helpful_count += 1
    db.commit()
    db.refresh(reply)
    return reply
