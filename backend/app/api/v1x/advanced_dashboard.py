"""
Advanced Dashboard API router.
Endpoints for dashboard customization, analytics, and insights.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.advanced_dashboard import (
    DashboardWidget, UserDashboardWidget, DashboardLayout, DashboardMetric,
    UserAnalytics, DashboardInsight, WidgetType, MetricType
)

router = APIRouter(prefix="/dashboard", tags=["advanced_dashboard"])


# ===================== Dashboard Layout =====================

@router.get("/layout")
def get_dashboard_layout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's dashboard layout and widgets"""
    layout = db.query(DashboardLayout).filter(
        DashboardLayout.user_id == current_user.id
    ).first()
    
    if not layout:
        # Create default layout
        layout = DashboardLayout(user_id=current_user.id)
        db.add(layout)
        db.commit()
        db.refresh(layout)
    
    widgets = db.query(UserDashboardWidget).filter(
        UserDashboardWidget.layout_id == layout.id
    ).all()
    
    return {
        "layout": _format_layout(layout),
        "widgets": [_format_user_widget(w) for w in widgets]
    }


@router.put("/layout")
def update_dashboard_layout(
    layout_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update dashboard layout configuration"""
    layout = db.query(DashboardLayout).filter(
        DashboardLayout.user_id == current_user.id
    ).first()
    
    if not layout:
        layout = DashboardLayout(user_id=current_user.id)
        db.add(layout)
    
    layout.name = layout_data.get("name", layout.name)
    layout.grid_cols = layout_data.get("grid_cols", layout.grid_cols)
    layout.theme = layout_data.get("theme", layout.theme)
    layout.auto_refresh_enabled = layout_data.get("auto_refresh_enabled", layout.auto_refresh_enabled)
    layout.refresh_interval_seconds = layout_data.get("refresh_interval_seconds", layout.refresh_interval_seconds)
    
    db.commit()
    db.refresh(layout)
    
    return {
        "message": "Layout updated",
        "layout": _format_layout(layout)
    }


# ===================== Dashboard Widgets =====================

@router.get("/widgets/available")
def list_available_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List all available dashboard widgets"""
    query = db.query(DashboardWidget).filter(DashboardWidget.is_available == True)
    
    # Filter by premium if user doesn't have premium tier
    # TODO: Check user's subscription tier
    
    total = query.count()
    widgets = query.order_by(DashboardWidget.display_order).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "widgets": [_format_widget(w) for w in widgets]
    }


@router.post("/widgets/add")
def add_widget_to_dashboard(
    widget_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a widget to user's dashboard"""
    widget_id = widget_data.get("widget_id")
    position_x = widget_data.get("position_x", 0)
    position_y = widget_data.get("position_y", 0)
    custom_config = widget_data.get("custom_config", {})
    
    # Get or create layout
    layout = db.query(DashboardLayout).filter(
        DashboardLayout.user_id == current_user.id
    ).first()
    
    if not layout:
        layout = DashboardLayout(user_id=current_user.id)
        db.add(layout)
        db.commit()
    
    # Verify widget exists
    widget = db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    # Check if already added
    existing = db.query(UserDashboardWidget).filter(
        UserDashboardWidget.user_id == current_user.id,
        UserDashboardWidget.widget_id == widget_id
    ).first()
    
    if existing:
        return {"message": "Widget already added", "widget": _format_user_widget(existing)}
    
    # Add widget
    user_widget = UserDashboardWidget(
        user_id=current_user.id,
        widget_id=widget_id,
        layout_id=layout.id,
        position_x=position_x,
        position_y=position_y,
        width=widget.default_width,
        height=widget.default_height,
        custom_config=custom_config
    )
    
    db.add(user_widget)
    db.commit()
    db.refresh(user_widget)
    
    return {
        "message": "Widget added",
        "widget": _format_user_widget(user_widget)
    }


@router.delete("/widgets/{widget_id}")
def remove_widget_from_dashboard(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a widget from user's dashboard"""
    user_widget = db.query(UserDashboardWidget).filter(
        UserDashboardWidget.id == widget_id,
        UserDashboardWidget.user_id == current_user.id
    ).first()
    
    if not user_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    db.delete(user_widget)
    db.commit()
    
    return {"message": "Widget removed"}


@router.put("/widgets/{widget_id}/position")
def update_widget_position(
    widget_id: int,
    position_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update widget position on dashboard"""
    user_widget = db.query(UserDashboardWidget).filter(
        UserDashboardWidget.id == widget_id,
        UserDashboardWidget.user_id == current_user.id
    ).first()
    
    if not user_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    user_widget.position_x = position_data.get("position_x", user_widget.position_x)
    user_widget.position_y = position_data.get("position_y", user_widget.position_y)
    user_widget.width = position_data.get("width", user_widget.width)
    user_widget.height = position_data.get("height", user_widget.height)
    
    db.commit()
    db.refresh(user_widget)
    
    return {
        "message": "Position updated",
        "widget": _format_user_widget(user_widget)
    }


# ===================== Analytics & Metrics =====================

@router.get("/analytics")
def get_user_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's aggregated analytics"""
    analytics = db.query(UserAnalytics).filter(
        UserAnalytics.user_id == current_user.id
    ).first()
    
    if not analytics:
        # Create default analytics
        analytics = UserAnalytics(user_id=current_user.id)
        db.add(analytics)
        db.commit()
    
    return {
        "analytics": _format_analytics(analytics)
    }


@router.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    metric_type: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get time-series metrics for a user"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(DashboardMetric).filter(
        DashboardMetric.user_id == current_user.id,
        DashboardMetric.recorded_at >= start_date
    )
    
    if metric_type:
        try:
            query = query.filter(DashboardMetric.metric_type == MetricType(metric_type))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
    
    total = query.count()
    metrics = query.order_by(DashboardMetric.recorded_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "metrics": [_format_metric(m) for m in metrics]
    }


@router.post("/metrics/record")
def record_metric(
    metric_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a new metric (internal use)"""
    metric_type = metric_data.get("metric_type")
    value = metric_data.get("value")
    
    try:
        MetricType(metric_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
    
    metric = DashboardMetric(
        user_id=current_user.id,
        metric_type=MetricType(metric_type),
        metric_name=metric_data.get("metric_name", metric_type),
        value=value,
        context=metric_data.get("context", {})
    )
    
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    return {
        "message": "Metric recorded",
        "metric": _format_metric(metric)
    }


# ===================== Insights =====================

@router.get("/insights")
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    unread_only: bool = False
):
    """Get AI-generated insights and recommendations"""
    query = db.query(DashboardInsight).filter(
        DashboardInsight.user_id == current_user.id
    )
    
    # Filter active insights
    now = datetime.utcnow()
    query = query.filter(
        (DashboardInsight.expires_at == None) | (DashboardInsight.expires_at > now)
    )
    
    if unread_only:
        query = query.filter(DashboardInsight.is_read == False)
    
    total = query.count()
    insights = query.order_by(DashboardInsight.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "insights": [_format_insight(i) for i in insights]
    }


@router.put("/insights/{insight_id}/read")
def mark_insight_read(
    insight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an insight as read"""
    insight = db.query(DashboardInsight).filter(
        DashboardInsight.id == insight_id,
        DashboardInsight.user_id == current_user.id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_read = True
    db.commit()
    
    return {"message": "Insight marked as read"}


@router.put("/insights/{insight_id}/act")
def mark_insight_acted(
    insight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an insight as acted upon"""
    insight = db.query(DashboardInsight).filter(
        DashboardInsight.id == insight_id,
        DashboardInsight.user_id == current_user.id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_acted_upon = True
    db.commit()
    
    return {"message": "Insight marked as acted upon"}


# ===================== Helper Functions =====================

def _format_layout(layout):
    """Format dashboard layout"""
    return {
        "id": layout.id,
        "name": layout.name,
        "grid_cols": layout.grid_cols,
        "theme": layout.theme,
        "auto_refresh_enabled": layout.auto_refresh_enabled,
        "refresh_interval_seconds": layout.refresh_interval_seconds,
        "created_at": layout.created_at.isoformat(),
        "updated_at": layout.updated_at.isoformat()
    }


def _format_widget(widget):
    """Format dashboard widget"""
    return {
        "id": widget.id,
        "name": widget.name,
        "description": widget.description,
        "widget_type": widget.widget_type.value,
        "icon": widget.icon,
        "color": widget.color,
        "default_width": widget.default_width,
        "default_height": widget.default_height,
        "metrics": widget.metrics,
        "is_customizable": widget.is_customizable,
        "requires_premium": widget.requires_premium
    }


def _format_user_widget(user_widget):
    """Format user's dashboard widget instance"""
    widget = user_widget.widget
    return {
        "id": user_widget.id,
        "widget_id": widget.id,
        "widget_name": widget.name,
        "widget_type": widget.widget_type.value,
        "position_x": user_widget.position_x,
        "position_y": user_widget.position_y,
        "width": user_widget.width,
        "height": user_widget.height,
        "custom_config": user_widget.custom_config,
        "is_enabled": user_widget.is_enabled,
        "added_at": user_widget.added_at.isoformat()
    }


def _format_analytics(analytics):
    """Format user analytics"""
    return {
        "id": analytics.id,
        "total_submissions": analytics.total_submissions,
        "total_challenges_completed": analytics.total_challenges_completed,
        "total_learning_minutes": analytics.total_learning_minutes,
        "average_code_quality_score": round(analytics.average_code_quality_score, 2),
        "daily_active_days": analytics.daily_active_days,
        "weekly_active_days": analytics.weekly_active_days,
        "longest_streak_days": analytics.longest_streak_days,
        "current_streak_days": analytics.current_streak_days,
        "total_coins_earned": analytics.total_coins_earned,
        "coins_earned_this_month": analytics.coins_earned_this_month,
        "total_achievements": analytics.total_achievements,
        "total_followers": analytics.total_followers,
        "global_rank": analytics.global_rank,
        "primary_language": analytics.primary_language,
        "languages": analytics.languages,
        "skills": analytics.skills,
        "weekly_growth_percent": round(analytics.weekly_growth_percent, 2),
        "monthly_growth_percent": round(analytics.monthly_growth_percent, 2),
        "calculated_at": analytics.calculated_at.isoformat()
    }


def _format_metric(metric):
    """Format metric"""
    return {
        "id": metric.id,
        "metric_type": metric.metric_type.value,
        "metric_name": metric.metric_name,
        "value": metric.value,
        "context": metric.context,
        "recorded_at": metric.recorded_at.isoformat()
    }


def _format_insight(insight):
    """Format insight"""
    return {
        "id": insight.id,
        "title": insight.title,
        "description": insight.description,
        "insight_type": insight.insight_type,
        "priority": insight.priority,
        "action_url": insight.action_url,
        "action_label": insight.action_label,
        "is_read": insight.is_read,
        "is_acted_upon": insight.is_acted_upon,
        "created_at": insight.created_at.isoformat(),
        "expires_at": insight.expires_at.isoformat() if insight.expires_at else None
    }
