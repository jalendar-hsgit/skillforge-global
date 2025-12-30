"""
Pydantic schemas for search endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# SearchQuery Schemas
class SearchQueryCreate(BaseModel):
    query_text: str = Field(..., min_length=1, max_length=500)
    content_types: List[str] = Field(default=[], description="challenge, forum_post, solution, etc")
    filters: Dict[str, Any] = Field(default={}, description="difficulty, language, category, etc")


class SearchQueryResponse(BaseModel):
    id: int
    user_id: int
    query_text: str
    content_types: List[str]
    filters: Dict[str, Any]
    results_count: int
    top_result_clicked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# SearchResult Schemas
class SearchResultResponse(BaseModel):
    id: int
    content_type: str
    content_id: int
    title: str
    preview: Optional[str]
    author_id: Optional[int]
    relevance_score: float
    match_type: str
    rank: int
    was_clicked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# SearchFilter Schemas
class SearchFilterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content_types: List[str] = Field(default=[])
    difficulty: List[str] = Field(default=[])
    language: List[str] = Field(default=[])
    category: List[str] = Field(default=[])
    rating_min: float = Field(default=0.0, ge=0.0, le=5.0)
    rating_max: float = Field(default=5.0, ge=0.0, le=5.0)
    sort_by: str = Field(default="relevance", pattern="^(relevance|rating|newest|most_popular)$")


class SearchFilterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content_types: Optional[List[str]] = None
    difficulty: Optional[List[str]] = None
    language: Optional[List[str]] = None
    category: Optional[List[str]] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    sort_by: Optional[str] = None
    is_public: Optional[bool] = None


class SearchFilterResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    content_types: List[str]
    difficulty: List[str]
    language: List[str]
    category: List[str]
    rating_min: float
    rating_max: float
    sort_by: str
    is_public: bool
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# TrendingSearch Schemas
class TrendingSearchResponse(BaseModel):
    id: int
    query_text: str
    category: Optional[str]
    search_count_today: int
    search_count_week: int
    trend_direction: str
    growth_percentage: float
    click_through_rate: float
    top_result_content_type: Optional[str]
    top_result_id: Optional[int]
    
    class Config:
        from_attributes = True


# SearchAnalytics Schemas
class SearchAnalyticsResponse(BaseModel):
    id: int
    period_date: datetime
    total_searches: int
    unique_users: int
    unique_queries: int
    average_results_per_query: float
    average_click_through_rate: float
    searches_with_refinement: int
    content_type_distribution: Dict[str, float]
    top_searches: List[str]
    most_used_filters: Dict[str, int]
    average_query_time_ms: float
    slow_queries: int
    
    class Config:
        from_attributes = True


# SavedSearch Schemas
class SavedSearchCreate(BaseModel):
    query_text: str = Field(..., min_length=1)
    name: Optional[str] = None
    description: Optional[str] = None
    content_types: List[str] = Field(default=[])
    filters: Dict[str, Any] = Field(default={})


class SavedSearchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content_types: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class SavedSearchResponse(BaseModel):
    id: int
    user_id: int
    query_text: str
    name: Optional[str]
    description: Optional[str]
    content_types: List[str]
    filters: Dict[str, Any]
    last_executed_at: Optional[datetime]
    execution_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Advanced Search Request/Response
class AdvancedSearchRequest(BaseModel):
    query: str
    content_types: List[str] = Field(default=["challenge", "forum_post", "solution"])
    difficulty: Optional[List[str]] = None
    language: Optional[List[str]] = None
    category: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    sort_by: str = Field(default="relevance", pattern="^(relevance|rating|newest|most_popular)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AdvancedSearchResponse(BaseModel):
    query: str
    total_results: int
    page: int
    page_size: int
    total_pages: int
    results: List[SearchResultResponse]
    applied_filters: Dict[str, Any]
    search_time_ms: float
    suggestions: Optional[List[str]] = None  # "Did you mean?" suggestions
