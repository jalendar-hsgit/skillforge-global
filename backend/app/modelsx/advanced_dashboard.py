"""
Advanced Dashboard models for analytics and metrics.
- DashboardWidget: Individual dashboard components
- DashboardLayout: User's custom dashboard configuration
- DashboardMetric: Time-series metrics for analytics
- UserAnalytics: Aggregated user activity analytics
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.db import Base


class WidgetType(str, Enum):
    """Types of dashboard widgets"""
    STATS_CARD = "stats_card"
    CHART = "chart"
    PROGRESS_BAR = "progress_bar"
    LEADERBOARD = "leaderboard"
    ACTIVITY_FEED = "activity_feed"
    STREAK_CALENDAR = "streak_calendar"
    QUICK_STATS = "quick_stats"
    GOALS = "goals"
    SKILL_TREE = "skill_tree"
    RECOMMENDATIONS = "recommendations"


class ChartType(str, Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    AREA = "area"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    RADAR = "radar"


class MetricType(str, Enum):
    """Types of metrics to track"""
    CODING_SUBMISSIONS = "coding_submissions"
    CHALLENGES_COMPLETED = "challenges_completed"
    LEARNING_TIME = "learning_time"
    CODE_QUALITY_SCORE = "code_quality_score"
    CONTRIBUTIONS = "contributions"
    COINS_EARNED = "coins_earned"
    ACHIEVEMENTS_UNLOCKED = "achievements_unlocked"
    FOLLOWERS = "followers"
    COMPLETION_RATE = "completion_rate"
    AVERAGE_SCORE = "average_score"


class DashboardWidget(Base):
    """Individual dashboard widget template"""
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True)
    
    # Widget info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    widget_type = Column(SQLEnum(WidgetType), nullable=False)
    
    # Display
    icon = Column(String(100), default="📊")
    color = Column(String(50), default="blue")
    default_width = Column(Integer, default=1)  # Grid units
    default_height = Column(Integer, default=1)
    
    # Configuration
    config_schema = Column(JSON, default={})  # JSON schema for widget config
    metrics = Column(JSON, default=[])  # List of metric types this widget can display
    
    # Features
    is_customizable = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    requires_premium = Column(Boolean, default=False)
    
    # Ordering
    display_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_widgets = relationship("UserDashboardWidget", back_populates="widget", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DashboardWidget(id={self.id}, name={self.name}, type={self.widget_type})>"


class UserDashboardWidget(Base):
    """User's instance of a dashboard widget with custom configuration"""
    __tablename__ = "user_dashboard_widgets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    widget_id = Column(Integer, ForeignKey("dashboard_widgets.id"), nullable=False)
    
    # Position on dashboard
    layout_id = Column(Integer, ForeignKey("dashboard_layouts.id"), nullable=True)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=1)
    height = Column(Integer, default=1)
    
    # Configuration
    custom_config = Column(JSON, default={})  # User's custom settings
    is_enabled = Column(Boolean, default=True)
    
    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    widget = relationship("DashboardWidget", back_populates="user_widgets")
    layout = relationship("DashboardLayout", back_populates="widgets")
    
    def __repr__(self):
        return f"<UserDashboardWidget(user_id={self.user_id}, widget_id={self.widget_id})>"


class DashboardLayout(Base):
    """User's dashboard layout configuration"""
    __tablename__ = "dashboard_layouts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Layout info
    name = Column(String(255), default="My Dashboard")
    description = Column(Text, nullable=True)
    
    # Grid configuration
    grid_cols = Column(Integer, default=4)  # Number of columns
    grid_gap = Column(Integer, default=16)  # Pixel gap between widgets
    
    # Theme
    theme = Column(String(50), default="dark")  # "light", "dark"
    layout_style = Column(String(50), default="grid")  # "grid", "flex"
    
    # Settings
    auto_refresh_enabled = Column(Boolean, default=True)
    refresh_interval_seconds = Column(Integer, default=300)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="dashboard_layout")
    widgets = relationship("UserDashboardWidget", back_populates="layout", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DashboardLayout(user_id={self.user_id}, name={self.name})>"


class DashboardMetric(Base):
    """Time-series metrics for analytics"""
    __tablename__ = "dashboard_metrics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Metric info
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    metric_name = Column(String(255), nullable=False)
    
    # Data
    value = Column(Float, nullable=False)
    
    # Context
    context = Column(JSON, default={})  # Additional data (challenge_id, etc)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<DashboardMetric(user_id={self.user_id}, metric={self.metric_type}, value={self.value})>"


class UserAnalytics(Base):
    """Aggregated user analytics and insights"""
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Activity metrics
    total_submissions = Column(Integer, default=0)
    total_challenges_completed = Column(Integer, default=0)
    total_learning_minutes = Column(Integer, default=0)
    average_code_quality_score = Column(Float, default=0.0)
    
    # Engagement
    daily_active_days = Column(Integer, default=0)
    weekly_active_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    current_streak_days = Column(Integer, default=0)
    
    # Earnings
    total_coins_earned = Column(Integer, default=0)
    coins_earned_this_month = Column(Integer, default=0)
    
    # Achievements
    total_achievements = Column(Integer, default=0)
    achievements_this_month = Column(Integer, default=0)
    
    # Social
    total_followers = Column(Integer, default=0)
    total_following = Column(Integer, default=0)
    
    # Rankings
    global_rank = Column(Integer, nullable=True)  # Updated periodically
    local_rank = Column(Integer, nullable=True)
    
    # Language & Skills
    primary_language = Column(String(100), nullable=True)
    languages = Column(JSON, default={})  # {"Python": 10, "JavaScript": 5}
    skills = Column(JSON, default=[])  # ["algorithms", "data-structures"]
    
    # Growth metrics
    weekly_growth_percent = Column(Float, default=0.0)
    monthly_growth_percent = Column(Float, default=0.0)
    
    # Last calculated
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="analytics")
    
    def __repr__(self):
        return f"<UserAnalytics(user_id={self.user_id}, rank={self.global_rank})>"


class DashboardInsight(Base):
    """AI-generated insights and recommendations"""
    __tablename__ = "dashboard_insights"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Insight info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    insight_type = Column(String(100), nullable=False)  # "achievement", "improvement", "streak", "recommendation"
    
    # Importance
    priority = Column(String(50), default="normal")  # "high", "normal", "low"
    
    # Action
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_acted_upon = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<DashboardInsight(user_id={self.user_id}, type={self.insight_type})>"
