"""
Discussion Forums & Q&A System Models
Supports community discussions, threads, replies, and knowledge sharing
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Index, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ThreadStatus(str, Enum):
    """Status of a forum thread"""
    OPEN = "open"  # Active discussion
    ANSWERED = "answered"  # Has accepted answer
    CLOSED = "closed"  # Locked by moderator
    ARCHIVED = "archived"  # Old thread, read-only


class ThreadType(str, Enum):
    """Type of thread for organization"""
    QUESTION = "question"  # Q&A style
    DISCUSSION = "discussion"  # General discussion
    ANNOUNCEMENT = "announcement"  # News/updates
    RESOURCE = "resource"  # Shared resources/tutorials
    BUG_REPORT = "bug_report"  # Bug reports


class ForumCategory(Base):
    """
    Forum category (like Getting Started, JavaScript, Algorithms, etc)
    """
    __tablename__ = "forum_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    icon_emoji = Column(String(10), nullable=True)  # 📚, 💬, 🐛, etc
    icon_url = Column(String(500), nullable=True)

    # Moderation
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

    # Statistics
    thread_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    last_activity_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    threads = relationship("ForumThread", back_populates="category", cascade="all, delete-orphan")


class ForumThread(Base):
    """
    A forum thread/post - the main discussion unit
    """
    __tablename__ = "forum_threads"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("forum_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Content
    title = Column(String(300), nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=[])  # ["python", "arrays", "help"]

    # Type and status
    thread_type = Column(String(20), default=ThreadType.QUESTION)
    status = Column(String(20), default=ThreadStatus.OPEN, index=True)

    # Engagement metrics
    view_count = Column(Integer, default=0, index=True)
    reply_count = Column(Integer, default=0)
    vote_count = Column(Integer, default=0)  # Up/down votes
    bookmark_count = Column(Integer, default=0)

    # Q&A specific
    has_accepted_answer = Column(Boolean, default=False)
    accepted_answer_id = Column(Integer, ForeignKey("forum_replies.id", ondelete="SET NULL"), nullable=True)

    # Moderation
    is_pinned = Column(Boolean, default=False)  # Sticky/pinned threads
    is_featured = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)  # Locked for replies

    # Metadata
    extra_data = Column(JSON, default={})  # language, challenge_id, etc

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    last_reply_at = Column(DateTime, nullable=True, index=True)

    # Relationships
    category = relationship("ForumCategory", foreign_keys=[category_id], back_populates="threads")
    creator = relationship("User", foreign_keys=[creator_id])
    replies = relationship("ForumReply", back_populates="thread", cascade="all, delete-orphan")
    votes = relationship("ForumThreadVote", back_populates="thread", cascade="all, delete-orphan")
    bookmarks = relationship("ForumBookmark", back_populates="thread", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_thread_category_created", "category_id", "created_at"),
        Index("ix_thread_status_created", "status", "created_at"),
        Index("ix_thread_view_count", "view_count"),
    )


class ForumReply(Base):
    """
    A reply to a forum thread
    """
    __tablename__ = "forum_replies"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # For nested replies (reply to a reply)
    parent_reply_id = Column(Integer, ForeignKey("forum_replies.id", ondelete="CASCADE"), nullable=True)

    # Content
    content = Column(Text, nullable=False)
    code_snippet = Column(Text, nullable=True)  # Optional code for code reviews
    language = Column(String(20), nullable=True)  # For syntax highlighting

    # Status
    is_accepted_answer = Column(Boolean, default=False)  # Marked as solution in Q&A
    vote_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)

    # Moderation
    is_deleted = Column(Boolean, default=False)
    deleted_reason = Column(String(200), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited_count = Column(Integer, default=0)

    # Relationships
    thread = relationship("ForumThread", foreign_keys=[thread_id], back_populates="replies")
    author = relationship("User", foreign_keys=[author_id])
    parent_reply = relationship("ForumReply", remote_side=[id], foreign_keys=[parent_reply_id])
    votes = relationship("ForumReplyVote", back_populates="reply", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_reply_thread_created", "thread_id", "created_at"),
        Index("ix_reply_author_created", "author_id", "created_at"),
    )


class ForumThreadVote(Base):
    """
    Voting on forum threads (helpful, not helpful)
    """
    __tablename__ = "forum_thread_votes"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Vote type
    vote_type = Column(String(10), nullable=False)  # "upvote", "downvote"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    thread = relationship("ForumThread", foreign_keys=[thread_id], back_populates="votes")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_thread_vote_unique", "thread_id", "user_id", unique=True),
    )


class ForumReplyVote(Base):
    """
    Voting on forum replies (helpful, not helpful)
    """
    __tablename__ = "forum_reply_votes"

    id = Column(Integer, primary_key=True, index=True)
    reply_id = Column(Integer, ForeignKey("forum_replies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Vote type
    vote_type = Column(String(10), nullable=False)  # "upvote", "downvote"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reply = relationship("ForumReply", foreign_keys=[reply_id], back_populates="votes")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_reply_vote_unique", "reply_id", "user_id", unique=True),
    )


class ForumBookmark(Base):
    """
    User bookmarks for saving threads
    """
    __tablename__ = "forum_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    thread_id = Column(Integer, ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False)

    # Bookmark info
    is_to_read = Column(Boolean, default=True)  # Marked for later reading
    note = Column(Text, nullable=True)  # User's note on bookmark

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    thread = relationship("ForumThread", foreign_keys=[thread_id], back_populates="bookmarks")

    __table_args__ = (
        Index("ix_bookmark_user", "user_id"),
        Index("ix_bookmark_unique", "user_id", "thread_id", unique=True),
    )


class ModeratorAction(Base):
    """
    Track moderation actions (lock, close, delete, etc)
    """
    __tablename__ = "moderator_actions"

    id = Column(Integer, primary_key=True, index=True)
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Action target (can be thread or reply)
    action_type = Column(String(30), nullable=False)  # "lock", "close", "delete", "pin", "unpin"
    target_type = Column(String(20), nullable=False)  # "thread" or "reply"
    target_id = Column(Integer, nullable=False)

    # Reason and notes
    reason = Column(String(300), nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    moderator = relationship("User", foreign_keys=[moderator_id])
