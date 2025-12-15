"""
Progressive Web App (PWA) models for offline support and background sync.
- ServiceWorkerConfig: PWA configuration
- OfflineSyncQueue: Queue for background sync
- OfflineCache: Offline cache metadata
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.db import Base


class SyncStatus(str, Enum):
    """Status of a sync operation"""
    PENDING = "pending"
    SYNCING = "syncing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class CacheType(str, Enum):
    """Type of cached data"""
    CHALLENGE = "challenge"
    SUBMISSION = "submission"
    HINT = "hint"
    PROGRESS = "progress"
    LEADERBOARD = "leaderboard"
    RESOURCE = "resource"


class ServiceWorkerConfig(Base):
    """PWA Service Worker configuration"""
    __tablename__ = "service_worker_config"

    id = Column(Integer, primary_key=True)
    
    # SW Configuration
    sw_version = Column(String(50), nullable=False)
    update_url = Column(String(500), nullable=True)
    
    # Features
    offline_mode_enabled = Column(Boolean, default=True)
    background_sync_enabled = Column(Boolean, default=True)
    push_notifications_enabled = Column(Boolean, default=True)
    
    # Cache settings
    cache_strategy = Column(String(50), default="network-first")  # network-first, cache-first, stale-while-revalidate
    cache_max_age_hours = Column(Integer, default=168)  # 1 week
    max_cache_size_mb = Column(Integer, default=50)
    
    # App info
    app_name = Column(String(255), default="SkillForge Global")
    app_description = Column(Text, nullable=True)
    app_icon_url = Column(String(500), nullable=True)
    app_theme_color = Column(String(50), default="#3B82F6")
    app_background_color = Column(String(50), default="#FFFFFF")
    
    # Display mode
    display_mode = Column(String(50), default="standalone")  # standalone, fullscreen, minimal-ui, browser
    start_url = Column(String(500), default="/")
    orientation = Column(String(50), default="portrait-primary")  # portrait-primary, landscape, etc
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ServiceWorkerConfig(version={self.sw_version}, active={self.is_active})>"


class OfflineSyncQueue(Base):
    """Queue for operations to sync when back online"""
    __tablename__ = "offline_sync_queue"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Operation details
    operation_type = Column(String(50), nullable=False)  # submit, progress_update, hint_request, etc
    endpoint = Column(String(500), nullable=False)  # API endpoint to call
    method = Column(String(10), default="POST")  # GET, POST, PUT, DELETE
    
    # Payload
    request_payload = Column(JSON, nullable=False)  # The data to send
    
    # Status
    status = Column(String(50), default=SyncStatus.PENDING)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Error tracking
    last_error = Column(Text, nullable=True)
    last_attempted_at = Column(DateTime, nullable=True)
    
    # Priority
    priority = Column(Integer, default=0)  # Higher = synced first
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="sync_queue")
    
    def __repr__(self):
        return f"<OfflineSyncQueue(user_id={self.user_id}, op={self.operation_type}, status={self.status})>"


class OfflineCache(Base):
    """Metadata for offline cached resources"""
    __tablename__ = "offline_cache"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Cache info
    cache_key = Column(String(255), nullable=False, unique=True, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    
    # Cache data
    data = Column(JSON, nullable=False)
    extra_data = Column(JSON, default={})  # Extra info like size, compression, etc
    
    # Size tracking
    size_bytes = Column(Integer, default=0)
    
    # TTL
    expires_at = Column(DateTime, nullable=True)
    
    # Access tracking
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    cached_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="offline_cache")
    
    def __repr__(self):
        return f"<OfflineCache(user_id={self.user_id}, key={self.cache_key}, size={self.size_bytes})>"


class PWANotificationPreference(Base):
    """User's push notification preferences for PWA"""
    __tablename__ = "pwa_notification_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Notification settings
    enabled = Column(Boolean, default=True)
    
    # Notification types
    challenge_hints = Column(Boolean, default=True)
    submission_results = Column(Boolean, default=True)
    achievement_unlocked = Column(Boolean, default=True)
    daily_challenge = Column(Boolean, default=True)
    leaderboard_updates = Column(Boolean, default=False)
    contest_updates = Column(Boolean, default=True)
    social_notifications = Column(Boolean, default=True)
    
    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), default="22:00")  # HH:MM format
    quiet_hours_end = Column(String(5), default="08:00")
    
    # Subscription
    subscription_endpoint = Column(String(500), nullable=True)  # Browser push subscription endpoint
    subscription_auth = Column(String(500), nullable=True)  # Auth secret for VAPID
    subscription_p256dh = Column(String(500), nullable=True)  # P256DH secret
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    subscribed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="notification_preference")
    
    def __repr__(self):
        return f"<PWANotificationPreference(user_id={self.user_id}, enabled={self.enabled})>"


class PWAAnalytics(Base):
    """Analytics for PWA usage and performance"""
    __tablename__ = "pwa_analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Installation
    app_installed = Column(Boolean, default=False)
    install_prompt_shown = Column(Integer, default=0)  # Times prompt was shown
    installed_at = Column(DateTime, nullable=True)
    
    # Usage
    total_sessions = Column(Integer, default=0)
    total_offline_time_minutes = Column(Integer, default=0)
    total_online_time_minutes = Column(Integer, default=0)
    
    # Sync
    total_sync_operations = Column(Integer, default=0)
    successful_syncs = Column(Integer, default=0)
    failed_syncs = Column(Integer, default=0)
    
    # Cache
    total_cache_hits = Column(Integer, default=0)
    total_cache_misses = Column(Integer, default=0)
    
    # Performance
    avg_page_load_time_ms = Column(Integer, default=0)
    avg_sync_time_ms = Column(Integer, default=0)
    
    # Device
    device_type = Column(String(50), nullable=True)  # mobile, tablet, desktop
    os = Column(String(100), nullable=True)  # iOS, Android, Windows, etc
    browser = Column(String(100), nullable=True)  # Chrome, Safari, Firefox, etc
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="pwa_analytics")
    
    def __repr__(self):
        return f"<PWAAnalytics(user_id={self.user_id}, installed={self.app_installed})>"
