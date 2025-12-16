"""
Advanced Search & Filtering Models
Supports full-text search, aggregated results, trending searches, and search analytics
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, Float, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SearchContentType(str, Enum):
    """Types of searchable content"""
    CHALLENGE = "challenge"
    FORUM_POST = "forum_post"
    SOLUTION = "solution"
    ARTICLE = "article"
    PROFILE = "profile"
    TEAM = "team"


class SearchQuery(Base):
    """
    Stores user search queries for analytics and trending
    """
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Search metadata
    query_text = Column(String(500), nullable=False, index=True)
    query_normalized = Column(String(500), nullable=False, index=True)  # Lowercase, trimmed
    
    # Search scope
    content_types = Column(JSON, default=[])  # ["challenge", "forum_post", "solution"]
    filters = Column(JSON, default={})  # {"difficulty": "hard", "language": "python"}
    
    # Results
    results_count = Column(Integer, default=0)
    top_result_clicked = Column(Boolean, default=False)
    user_refined = Column(Boolean, default=False)  # Did user refine search?
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    executed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index("ix_search_query_normalized", "query_normalized", "created_at"),
        Index("ix_search_query_user", "user_id", "created_at"),
    )


class SearchResult(Base):
    """
    Individual search result with relevance ranking
    """
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    search_query_id = Column(Integer, ForeignKey("search_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Result identification
    content_type = Column(SQLEnum(SearchContentType), nullable=False)
    content_id = Column(Integer, nullable=False)  # ID in respective table
    
    # Content metadata snapshot
    title = Column(String(200), nullable=False)
    preview = Column(Text, nullable=True)  # First 200 chars
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relevance scoring
    relevance_score = Column(Float, default=0.0)  # 0-1 based on match quality
    match_type = Column(String(50), default="full")  # "full", "partial", "tag_match", "metadata"
    match_fields = Column(JSON, default=[])  # Fields matched: ["title", "content", "tags"]
    
    # Ranking
    rank = Column(Integer, default=1)  # Position in results
    
    # Engagement
    was_clicked = Column(Boolean, default=False)
    clicked_at = Column(DateTime, nullable=True)
    time_on_result = Column(Integer, nullable=True)  # Seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    search_query = relationship("SearchQuery", foreign_keys=[search_query_id])
    author = relationship("User", foreign_keys=[author_id])


class SearchFilter(Base):
    """
    Saved search filters for quick access
    """
    __tablename__ = "search_filters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Filter metadata
    name = Column(String(100), nullable=False)  # "Beginner Python", "System Design"
    description = Column(String(500), nullable=True)
    
    # Filter configuration
    content_types = Column(JSON, default=[])  # ["challenge"]
    difficulty = Column(JSON, default=[])  # ["easy", "medium"]
    language = Column(JSON, default=[])  # ["python", "javascript"]
    category = Column(JSON, default=[])  # ["arrays", "strings"]
    tag_filters = Column(JSON, default=[])  # Tags to include/exclude
    rating_min = Column(Float, default=0.0)
    rating_max = Column(Float, default=5.0)
    sort_by = Column(String(30), default="relevance")  # "relevance", "rating", "newest", "most_popular"
    
    # Usage tracking
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class TrendingSearch(Base):
    """
    Aggregated trending searches for platform-wide insights
    """
    __tablename__ = "trending_searches"

    id = Column(Integer, primary_key=True, index=True)
    
    # Search metadata
    query_text = Column(String(500), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=True)  # "general", "python", "system_design", etc
    
    # Trend metrics
    search_count_today = Column(Integer, default=0)
    search_count_week = Column(Integer, default=0)
    search_count_month = Column(Integer, default=0)
    click_through_rate = Column(Float, default=0.0)  # 0-1
    
    # Trend direction
    trend_direction = Column(String(20), default="neutral")  # "up", "down", "neutral"
    growth_percentage = Column(Float, default=0.0)  # Week-over-week growth
    
    # Top content
    top_result_content_type = Column(SQLEnum(SearchContentType), nullable=True)
    top_result_id = Column(Integer, nullable=True)
    
    # Timestamps
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_trending_search_trend", "trend_direction", "search_count_week"),
    )


class SearchAnalytics(Base):
    """
    Aggregated search analytics for insights
    """
    __tablename__ = "search_analytics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    period_date = Column(DateTime, default=datetime.utcnow, unique=True)
    
    # Search statistics
    total_searches = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    unique_queries = Column(Integer, default=0)
    
    # Engagement metrics
    average_results_per_query = Column(Float, default=0.0)
    average_click_through_rate = Column(Float, default=0.0)
    searches_with_refinement = Column(Integer, default=0)
    
    # Content type distribution
    content_type_distribution = Column(JSON, default={})  # {"challenge": 0.5, "forum": 0.3}
    
    # Top searches
    top_searches = Column(JSON, default=[])  # List of top 10 search texts
    
    # Filter usage
    most_used_filters = Column(JSON, default={})  # Filter name: usage count
    
    # Performance metrics
    average_query_time_ms = Column(Float, default=0.0)
    slow_queries = Column(Integer, default=0)  # Queries > 1000ms
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class SearchIndex(Base):
    """
    Full-text search index for performance
    Denormalized data for faster searching
    """
    __tablename__ = "search_index"

    id = Column(Integer, primary_key=True, index=True)
    
    # Content reference
    content_type = Column(SQLEnum(SearchContentType), nullable=False, index=True)
    content_id = Column(Integer, nullable=False, index=True)
    
    # Indexed content
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Full content for search
    tags = Column(JSON, default=[])  # Indexed tags
    metadata = Column(JSON, default={})  # difficulty, language, category, etc
    
    # Searchable attributes
    author_name = Column(String(100), nullable=True, index=True)
    keywords = Column(JSON, default=[])  # Pre-computed keywords
    
    # Ranking signals
    popularity_score = Column(Float, default=0.0)  # Based on views/ratings
    recency_score = Column(Float, default=0.0)  # Newer = higher
    rating = Column(Float, default=0.0)
    
    # Timestamps
    content_created_at = Column(DateTime, default=datetime.utcnow, index=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_search_index_type_id", "content_type", "content_id", unique=True),
    )


class SavedSearch(Base):
    """
    Saved searches for users to quickly access again
    """
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Search query
    query_text = Column(String(500), nullable=False)
    content_types = Column(JSON, default=[])
    filters = Column(JSON, default={})
    
    # Metadata
    name = Column(String(100), nullable=True)  # Optional custom name
    description = Column(String(500), nullable=True)
    
    # Usage
    last_executed_at = Column(DateTime, nullable=True)
    execution_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
