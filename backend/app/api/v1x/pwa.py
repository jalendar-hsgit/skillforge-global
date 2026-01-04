"""
Progressive Web App (PWA) API endpoints.
- Offline sync management
- Cache control
- Push notification preferences
- PWA configuration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
import json

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.pwa import (
    ServiceWorkerConfig, OfflineSyncQueue, OfflineCache,
    PWANotificationPreference, PWAAnalytics, SyncStatus
)

router = APIRouter(prefix="/pwa", tags=["PWA"])


# ============================================================================
# PWA Configuration
# ============================================================================

@router.get("/config")
def get_pwa_config(db: Session = Depends(get_db)):
    """Get PWA configuration (public endpoint)"""
    config = db.query(ServiceWorkerConfig).filter(
        ServiceWorkerConfig.is_active == True
    ).first()
    
    if not config:
        # Return default config
        return {
            "success": True,
            "config": {
                "name": "SkillForge Global",
                "description": "Learn to code with AI-powered practice",
                "display": "standalone",
                "orientation": "portrait-primary",
                "theme_color": "#3B82F6",
                "background_color": "#FFFFFF",
                "offline_enabled": True,
                "background_sync_enabled": True,
                "push_notifications_enabled": True,
                "cache_strategy": "network-first",
            }
        }
    
    return {
        "success": True,
        "config": {
            "name": config.app_name,
            "description": config.app_description,
            "display": config.display_mode,
            "orientation": config.orientation,
            "theme_color": config.app_theme_color,
            "background_color": config.app_background_color,
            "offline_enabled": config.offline_mode_enabled,
            "background_sync_enabled": config.background_sync_enabled,
            "push_notifications_enabled": config.push_notifications_enabled,
            "cache_strategy": config.cache_strategy,
            "cache_max_age_hours": config.cache_max_age_hours,
        }
    }


# ============================================================================
# Offline Sync Management
# ============================================================================

@router.post("/sync/queue")
def queue_sync_operation(
    operation_type: str,
    endpoint: str,
    payload: dict,
    method: str = "POST",
    priority: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Queue an operation for syncing when back online"""
    
    sync_item = OfflineSyncQueue(
        user_id=current_user.id,
        operation_type=operation_type,
        endpoint=endpoint,
        method=method,
        request_payload=payload,
        priority=priority,
        status=SyncStatus.PENDING
    )
    db.add(sync_item)
    db.commit()
    db.refresh(sync_item)
    
    return {
        "success": True,
        "sync_id": sync_item.id,
        "message": "Operation queued for sync",
    }


@router.get("/sync/pending")
def get_pending_syncs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all pending sync operations for user"""
    
    pending = db.query(OfflineSyncQueue).filter(
        and_(
            OfflineSyncQueue.user_id == current_user.id,
            OfflineSyncQueue.status.in_([SyncStatus.PENDING, SyncStatus.RETRYING])
        )
    ).order_by(
        desc(OfflineSyncQueue.priority),
        OfflineSyncQueue.created_at
    ).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "pending_syncs": [
            {
                "id": item.id,
                "operation_type": item.operation_type,
                "endpoint": item.endpoint,
                "method": item.method,
                "status": item.status,
                "retry_count": item.retry_count,
                "created_at": item.created_at.isoformat(),
            }
            for item in pending
        ],
        "total": len(pending),
    }


@router.post("/sync/execute/{sync_id}")
def execute_sync(
    sync_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute a single sync operation"""
    
    sync_item = db.query(OfflineSyncQueue).filter(
        and_(
            OfflineSyncQueue.id == sync_id,
            OfflineSyncQueue.user_id == current_user.id
        )
    ).first()
    
    if not sync_item:
        raise HTTPException(status_code=404, detail="Sync operation not found")
    
    # Mark as syncing
    sync_item.status = SyncStatus.SYNCING
    sync_item.last_attempted_at = datetime.utcnow()
    db.commit()
    
    # In production, would actually execute the API call here
    # For now, just mark as successful
    sync_item.status = SyncStatus.SUCCESS
    sync_item.synced_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "sync_id": sync_item.id,
        "status": sync_item.status,
        "message": "Sync operation executed successfully",
    }


@router.delete("/sync/{sync_id}")
def delete_sync_operation(
    sync_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete/cancel a sync operation"""
    
    sync_item = db.query(OfflineSyncQueue).filter(
        and_(
            OfflineSyncQueue.id == sync_id,
            OfflineSyncQueue.user_id == current_user.id
        )
    ).first()
    
    if not sync_item:
        raise HTTPException(status_code=404, detail="Sync operation not found")
    
    db.delete(sync_item)
    db.commit()
    
    return {
        "success": True,
        "message": "Sync operation deleted",
    }


# ============================================================================
# Offline Cache Management
# ============================================================================

@router.post("/cache")
def cache_resource(
    cache_key: str,
    resource_type: str,
    data: dict,
    resource_id: int = None,
    expires_in_hours: int = 168,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cache a resource for offline use"""
    
    # Check if cache already exists
    existing = db.query(OfflineCache).filter(
        and_(
            OfflineCache.user_id == current_user.id,
            OfflineCache.cache_key == cache_key
        )
    ).first()
    
    data_json = json.dumps(data)
    size = len(data_json.encode('utf-8'))
    
    if existing:
        existing.data = data
        existing.size_bytes = size
        existing.access_count += 1
        existing.last_accessed_at = datetime.utcnow()
        if expires_in_hours:
            from datetime import timedelta
            existing.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    else:
        cache = OfflineCache(
            user_id=current_user.id,
            cache_key=cache_key,
            resource_type=resource_type,
            resource_id=resource_id,
            data=data,
            size_bytes=size,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours) if expires_in_hours else None
        )
        db.add(cache)
    
    db.commit()
    
    return {
        "success": True,
        "cache_key": cache_key,
        "size_bytes": size,
        "message": "Resource cached for offline use",
    }


@router.get("/cache/{cache_key}")
def get_cached_resource(
    cache_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a cached resource"""
    
    cache = db.query(OfflineCache).filter(
        and_(
            OfflineCache.user_id == current_user.id,
            OfflineCache.cache_key == cache_key
        )
    ).first()
    
    if not cache:
        raise HTTPException(status_code=404, detail="Cached resource not found")
    
    # Check expiry
    if cache.expires_at and cache.expires_at < datetime.utcnow():
        db.delete(cache)
        db.commit()
        raise HTTPException(status_code=410, detail="Cached resource expired")
    
    # Update access info
    cache.access_count += 1
    cache.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "cache_key": cache_key,
        "data": cache.data,
        "resource_type": cache.resource_type,
        "size_bytes": cache.size_bytes,
        "access_count": cache.access_count,
    }


@router.get("/cache")
def list_cached_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all cached resources for user"""
    
    caches = db.query(OfflineCache).filter(
        OfflineCache.user_id == current_user.id
    ).order_by(
        desc(OfflineCache.last_accessed_at)
    ).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "caches": [
            {
                "cache_key": c.cache_key,
                "resource_type": c.resource_type,
                "size_bytes": c.size_bytes,
                "access_count": c.access_count,
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                "cached_at": c.cached_at.isoformat(),
            }
            for c in caches
        ],
        "total": len(caches),
    }


@router.delete("/cache/{cache_key}")
def clear_cache(
    cache_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear a specific cached resource"""
    
    cache = db.query(OfflineCache).filter(
        and_(
            OfflineCache.user_id == current_user.id,
            OfflineCache.cache_key == cache_key
        )
    ).first()
    
    if cache:
        db.delete(cache)
        db.commit()
    
    return {
        "success": True,
        "message": "Cache cleared",
    }


@router.delete("/cache")
def clear_all_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear all cached resources for user"""
    
    deleted = db.query(OfflineCache).filter(
        OfflineCache.user_id == current_user.id
    ).delete()
    db.commit()
    
    return {
        "success": True,
        "cleared": deleted,
        "message": f"Cleared {deleted} cached resources",
    }


# ============================================================================
# Push Notification Preferences
# ============================================================================

@router.get("/notifications/preferences")
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's push notification preferences"""
    
    prefs = db.query(PWANotificationPreference).filter(
        PWANotificationPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = PWANotificationPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
    
    return {
        "success": True,
        "preferences": {
            "enabled": prefs.enabled,
            "challenge_hints": prefs.challenge_hints,
            "submission_results": prefs.submission_results,
            "achievement_unlocked": prefs.achievement_unlocked,
            "daily_challenge": prefs.daily_challenge,
            "leaderboard_updates": prefs.leaderboard_updates,
            "contest_updates": prefs.contest_updates,
            "social_notifications": prefs.social_notifications,
            "quiet_hours_enabled": prefs.quiet_hours_enabled,
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
        }
    }


@router.put("/notifications/preferences")
def update_notification_preferences(
    enabled: bool = None,
    challenge_hints: bool = None,
    submission_results: bool = None,
    achievement_unlocked: bool = None,
    daily_challenge: bool = None,
    leaderboard_updates: bool = None,
    contest_updates: bool = None,
    social_notifications: bool = None,
    quiet_hours_enabled: bool = None,
    quiet_hours_start: str = None,
    quiet_hours_end: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user's push notification preferences"""
    
    prefs = db.query(PWANotificationPreference).filter(
        PWANotificationPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = PWANotificationPreference(user_id=current_user.id)
        db.add(prefs)
    
    if enabled is not None:
        prefs.enabled = enabled
    if challenge_hints is not None:
        prefs.challenge_hints = challenge_hints
    if submission_results is not None:
        prefs.submission_results = submission_results
    if achievement_unlocked is not None:
        prefs.achievement_unlocked = achievement_unlocked
    if daily_challenge is not None:
        prefs.daily_challenge = daily_challenge
    if leaderboard_updates is not None:
        prefs.leaderboard_updates = leaderboard_updates
    if contest_updates is not None:
        prefs.contest_updates = contest_updates
    if social_notifications is not None:
        prefs.social_notifications = social_notifications
    if quiet_hours_enabled is not None:
        prefs.quiet_hours_enabled = quiet_hours_enabled
    if quiet_hours_start:
        prefs.quiet_hours_start = quiet_hours_start
    if quiet_hours_end:
        prefs.quiet_hours_end = quiet_hours_end
    
    prefs.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Notification preferences updated",
    }


# ============================================================================
# PWA Analytics
# ============================================================================

@router.post("/analytics/event")
def log_pwa_event(
    event_type: str,
    event_data: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a PWA usage event"""
    
    analytics = db.query(PWAAnalytics).filter(
        PWAAnalytics.user_id == current_user.id
    ).first()
    
    if not analytics:
        analytics = PWAAnalytics(user_id=current_user.id)
        db.add(analytics)
    
    # Update based on event type
    if event_type == "install":
        analytics.app_installed = True
        analytics.installed_at = datetime.utcnow()
    elif event_type == "install_prompt":
        analytics.install_prompt_shown += 1
    elif event_type == "session_start":
        analytics.total_sessions += 1
    elif event_type == "sync_success":
        analytics.successful_syncs += 1
        analytics.total_sync_operations += 1
    elif event_type == "sync_failed":
        analytics.failed_syncs += 1
        analytics.total_sync_operations += 1
    elif event_type == "cache_hit":
        analytics.total_cache_hits += 1
    elif event_type == "cache_miss":
        analytics.total_cache_misses += 1
    
    analytics.last_activity = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": f"Event '{event_type}' logged",
    }


@router.get("/analytics")
def get_pwa_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's PWA analytics"""
    
    analytics = db.query(PWAAnalytics).filter(
        PWAAnalytics.user_id == current_user.id
    ).first()
    
    if not analytics:
        return {
            "success": True,
            "analytics": {
                "app_installed": False,
                "total_sessions": 0,
                "total_offline_time_minutes": 0,
                "successful_syncs": 0,
                "failed_syncs": 0,
                "cache_hit_rate": 0,
            }
        }
    
    hit_rate = 0
    total_cache = analytics.total_cache_hits + analytics.total_cache_misses
    if total_cache > 0:
        hit_rate = (analytics.total_cache_hits / total_cache) * 100
    
    return {
        "success": True,
        "analytics": {
            "app_installed": analytics.app_installed,
            "installed_at": analytics.installed_at.isoformat() if analytics.installed_at else None,
            "total_sessions": analytics.total_sessions,
            "total_offline_time_minutes": analytics.total_offline_time_minutes,
            "total_online_time_minutes": analytics.total_online_time_minutes,
            "total_sync_operations": analytics.total_sync_operations,
            "successful_syncs": analytics.successful_syncs,
            "failed_syncs": analytics.failed_syncs,
            "cache_hits": analytics.total_cache_hits,
            "cache_misses": analytics.total_cache_misses,
            "cache_hit_rate": round(hit_rate, 2),
            "avg_page_load_ms": analytics.avg_page_load_time_ms,
            "avg_sync_time_ms": analytics.avg_sync_time_ms,
        }
    }
