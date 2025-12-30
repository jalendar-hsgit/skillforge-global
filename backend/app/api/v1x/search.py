"""
Advanced Search & Filtering API endpoints
Provides full-text search, filtering, trending searches, and search analytics
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.core.security import get_current_user
from app.core.db import get_db
from app.modelsx.search import (
    SearchQuery, SearchResult, SearchFilter, TrendingSearch,
    SearchAnalytics, SearchIndex, SavedSearch, SearchContentType
)
from app.models.user import User
from app.schemas.search import (
    SearchQueryCreate, SearchQueryResponse, SearchResultResponse,
    SearchFilterCreate, SearchFilterUpdate, SearchFilterResponse,
    TrendingSearchResponse, SearchAnalyticsResponse,
    SavedSearchCreate, SavedSearchUpdate, SavedSearchResponse,
    AdvancedSearchRequest, AdvancedSearchResponse
)

router = APIRouter(prefix="/api/v1x/search", tags=["search"])


# Advanced Search Endpoints
@router.post("/advanced", response_model=AdvancedSearchResponse)
def advanced_search(
    search_req: AdvancedSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform advanced search with filters
    Supports full-text search across multiple content types
    """
    start_time = datetime.utcnow()
    
    # Normalize query
    query_normalized = search_req.query.lower().strip()
    
    # Build search query record
    search_query = SearchQuery(
        user_id=current_user.id,
        query_text=search_req.query,
        query_normalized=query_normalized,
        content_types=search_req.content_types,
        filters={
            'difficulty': search_req.difficulty,
            'language': search_req.language,
            'category': search_req.category,
            'rating_min': search_req.rating_min,
            'rating_max': search_req.rating_max,
        }
    )
    
    # Query search index
    query_base = db.query(SearchIndex).filter(
        or_(
            SearchIndex.title.ilike(f"%{search_req.query}%"),
            SearchIndex.content.ilike(f"%{search_req.query}%"),
            SearchIndex.keywords.contains([search_req.query.lower()])
        )
    )
    
    # Apply content type filter
    if search_req.content_types:
        query_base = query_base.filter(
            SearchIndex.content_type.in_(search_req.content_types)
        )
    
    # Apply difficulty filter
    if search_req.difficulty:
        query_base = query_base.filter(
            SearchIndex.metadata['difficulty'].astext.in_(search_req.difficulty)
        )
    
    # Apply language filter
    if search_req.language:
        query_base = query_base.filter(
            SearchIndex.metadata['language'].astext.in_(search_req.language)
        )
    
    # Apply category filter
    if search_req.category:
        query_base = query_base.filter(
            SearchIndex.metadata['category'].astext.in_(search_req.category)
        )
    
    # Apply rating filter
    if search_req.rating_min is not None or search_req.rating_max is not None:
        if search_req.rating_min is not None:
            query_base = query_base.filter(SearchIndex.rating >= search_req.rating_min)
        if search_req.rating_max is not None:
            query_base = query_base.filter(SearchIndex.rating <= search_req.rating_max)
    
    # Sort results
    if search_req.sort_by == "rating":
        query_base = query_base.order_by(desc(SearchIndex.rating))
    elif search_req.sort_by == "newest":
        query_base = query_base.order_by(desc(SearchIndex.content_created_at))
    elif search_req.sort_by == "most_popular":
        query_base = query_base.order_by(desc(SearchIndex.popularity_score))
    else:  # relevance (default)
        query_base = query_base.order_by(
            desc(SearchIndex.popularity_score),
            desc(SearchIndex.rating)
        )
    
    # Get total count
    total_results = query_base.count()
    
    # Paginate
    offset = (search_req.page - 1) * search_req.page_size
    indexed_results = query_base.offset(offset).limit(search_req.page_size).all()
    
    # Convert to SearchResult objects
    results = []
    for rank, index_result in enumerate(indexed_results, 1):
        result = SearchResult(
            content_type=index_result.content_type,
            content_id=index_result.content_id,
            title=index_result.title,
            preview=index_result.content[:200] if index_result.content else None,
            relevance_score=index_result.popularity_score,
            match_type="full" if search_req.query.lower() in index_result.title.lower() else "partial",
            rank=rank
        )
        results.append(result)
    
    # Record search query
    search_query.results_count = total_results
    search_query.executed_at = datetime.utcnow()
    db.add(search_query)
    db.commit()
    
    # Calculate search time
    search_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return AdvancedSearchResponse(
        query=search_req.query,
        total_results=total_results,
        page=search_req.page,
        page_size=search_req.page_size,
        total_pages=(total_results + search_req.page_size - 1) // search_req.page_size,
        results=[SearchResultResponse.from_orm(r) for r in results],
        applied_filters={
            'difficulty': search_req.difficulty,
            'language': search_req.language,
            'category': search_req.category,
        },
        search_time_ms=search_time_ms
    )


@router.get("/trending", response_model=List[TrendingSearchResponse])
def get_trending_searches(
    limit: int = Query(10, ge=1, le=50),
    period: str = Query("week", pattern="^(today|week|month)$"),
    db: Session = Depends(get_db)
):
    """Get trending searches for the specified period"""
    if period == "today":
        order_col = TrendingSearch.search_count_today
    elif period == "month":
        order_col = TrendingSearch.search_count_month
    else:  # week
        order_col = TrendingSearch.search_count_week
    
    trending = db.query(TrendingSearch).order_by(
        desc(order_col)
    ).limit(limit).all()
    
    return trending


@router.get("/analytics", response_model=SearchAnalyticsResponse)
def get_search_analytics(
    days_back: int = Query(1, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get search analytics for the specified period"""
    target_date = datetime.utcnow() - timedelta(days=days_back)
    
    analytics = db.query(SearchAnalytics).filter(
        SearchAnalytics.period_date >= target_date
    ).order_by(desc(SearchAnalytics.period_date)).first()
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return analytics


# Search Filter Endpoints
@router.post("/filters", response_model=SearchFilterResponse)
def create_search_filter(
    filter_data: SearchFilterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new saved search filter"""
    search_filter = SearchFilter(
        user_id=current_user.id,
        name=filter_data.name,
        description=filter_data.description,
        content_types=filter_data.content_types,
        difficulty=filter_data.difficulty,
        language=filter_data.language,
        category=filter_data.category,
        rating_min=filter_data.rating_min,
        rating_max=filter_data.rating_max,
        sort_by=filter_data.sort_by
    )
    
    db.add(search_filter)
    db.commit()
    db.refresh(search_filter)
    
    return search_filter


@router.get("/filters", response_model=List[SearchFilterResponse])
def get_user_search_filters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved search filters"""
    filters = db.query(SearchFilter).filter(
        SearchFilter.user_id == current_user.id
    ).all()
    
    return filters


@router.get("/filters/{filter_id}", response_model=SearchFilterResponse)
def get_search_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific search filter"""
    search_filter = db.query(SearchFilter).filter(
        SearchFilter.id == filter_id,
        SearchFilter.user_id == current_user.id
    ).first()
    
    if not search_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    return search_filter


@router.put("/filters/{filter_id}", response_model=SearchFilterResponse)
def update_search_filter(
    filter_id: int,
    filter_data: SearchFilterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a search filter"""
    search_filter = db.query(SearchFilter).filter(
        SearchFilter.id == filter_id,
        SearchFilter.user_id == current_user.id
    ).first()
    
    if not search_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    update_data = filter_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(search_filter, field, value)
    
    db.commit()
    db.refresh(search_filter)
    
    return search_filter


@router.delete("/filters/{filter_id}")
def delete_search_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a search filter"""
    search_filter = db.query(SearchFilter).filter(
        SearchFilter.id == filter_id,
        SearchFilter.user_id == current_user.id
    ).first()
    
    if not search_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    db.delete(search_filter)
    db.commit()
    
    return {"message": "Filter deleted", "filter_id": filter_id}


# Saved Search Endpoints
@router.post("/saved", response_model=SavedSearchResponse)
def create_saved_search(
    saved_search: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a search for later"""
    new_saved_search = SavedSearch(
        user_id=current_user.id,
        query_text=saved_search.query_text,
        name=saved_search.name,
        description=saved_search.description,
        content_types=saved_search.content_types,
        filters=saved_search.filters
    )
    
    db.add(new_saved_search)
    db.commit()
    db.refresh(new_saved_search)
    
    return new_saved_search


@router.get("/saved", response_model=List[SavedSearchResponse])
def get_saved_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved searches"""
    saved_searches = db.query(SavedSearch).filter(
        SavedSearch.user_id == current_user.id
    ).order_by(desc(SavedSearch.created_at)).all()
    
    return saved_searches


@router.put("/saved/{saved_search_id}", response_model=SavedSearchResponse)
def update_saved_search(
    saved_search_id: int,
    update_data: SavedSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a saved search"""
    saved_search = db.query(SavedSearch).filter(
        SavedSearch.id == saved_search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    update_fields = update_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(saved_search, field, value)
    
    db.commit()
    db.refresh(saved_search)
    
    return saved_search


@router.delete("/saved/{saved_search_id}")
def delete_saved_search(
    saved_search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a saved search"""
    saved_search = db.query(SavedSearch).filter(
        SavedSearch.id == saved_search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    db.delete(saved_search)
    db.commit()
    
    return {"message": "Saved search deleted", "saved_search_id": saved_search_id}
