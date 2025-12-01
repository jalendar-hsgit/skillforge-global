"""
Platform Settings Service - Easy access to settings throughout the app.
Includes caching to avoid database queries on every request.
"""
from app.core.db import SessionLocal
from app.modelsx.platform_settings import PlatformSetting
from typing import Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


class SettingsCache:
    """Simple in-memory cache for settings with TTL"""
    
    def __init__(self, ttl_seconds: int = 60):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[tuple]:
        """Get cached value and timestamp"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value with current timestamp"""
        self.cache[key] = (value, time.time())
    
    def clear(self, key: Optional[str] = None):
        """Clear specific key or entire cache"""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()


# Global cache instance (60 second TTL)
_cache = SettingsCache(ttl_seconds=60)


def get_setting(key: str, default: Any = None, use_cache: bool = True) -> Any:
    """
    Get a platform setting value.
    
    Args:
        key: Setting key
        default: Default value if not found
        use_cache: Whether to use cache (default True)
    
    Returns:
        Setting value or default
    """
    # Check cache first
    if use_cache:
        cached = _cache.get(key)
        if cached is not None:
            return cached
    
    # Query database
    db = SessionLocal()
    try:
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        if setting:
            value = setting.get_value()
            if use_cache:
                _cache.set(key, value)
            return value
        return default
    except Exception as e:
        logger.error(f"Error fetching setting '{key}': {e}")
        return default
    finally:
        db.close()


def is_maintenance_mode() -> bool:
    """Check if platform is in maintenance mode"""
    return get_setting("maintenance_mode", False)


def allow_new_registrations() -> bool:
    """Check if new user registrations are allowed"""
    return get_setting("allow_new_registrations", True)


def require_mentor_approval() -> bool:
    """Check if mentor applications require admin approval"""
    return get_setting("mentor_approval_required", True)


def get_platform_name() -> str:
    """Get platform display name"""
    return get_setting("platform_name", "SkillForge Global")


def get_support_email() -> str:
    """Get support contact email"""
    return get_setting("support_email", "support@skillforge.com")


def get_featured_courses() -> list:
    """Get list of featured course slugs"""
    return get_setting("featured_courses", [])


def clear_settings_cache(key: Optional[str] = None):
    """
    Clear settings cache.
    Call this after updating settings to force refresh.
    
    Args:
        key: Specific key to clear, or None to clear all
    """
    _cache.clear(key)
    logger.info(f"Settings cache cleared: {key or 'all'}")


# Convenience dict for quick access
SETTINGS = {
    "maintenance_mode": is_maintenance_mode,
    "allow_new_registrations": allow_new_registrations,
    "mentor_approval_required": require_mentor_approval,
    "platform_name": get_platform_name,
    "support_email": get_support_email,
    "featured_courses": get_featured_courses,
}
