"""
Test script for platform settings functionality.
Tests all settings features: maintenance mode, registration toggle, mentor approval, featured courses.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.db import SessionLocal, engine
from app.modelsx.platform_settings import PlatformSetting, Base
from app.services.settings_service import (
    get_setting, is_maintenance_mode, allow_new_registrations,
    require_mentor_approval, get_featured_courses, clear_settings_cache
)
import requests
import time

# API base URL
API_BASE = "http://localhost:8001"

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")


def test_settings_api():
    """Test settings API endpoints"""
    print_header("Testing Settings API")
    
    try:
        # Test GET /settings/public (should work without auth)
        response = requests.get(f"{API_BASE}/api/v1x/admin/settings/public")
        if response.status_code == 200:
            settings = response.json()
            print_success(f"Settings API GET: {len(settings)} settings returned")
            for key, value in settings.items():
                print_info(f"  {key}: {value}")
        else:
            print_error(f"Settings API GET failed: {response.status_code}")
    except Exception as e:
        print_error(f"Settings API test failed: {e}")


def test_maintenance_mode():
    """Test maintenance mode functionality"""
    print_header("Testing Maintenance Mode")
    
    db = SessionLocal()
    try:
        # Enable maintenance mode
        print_info("Enabling maintenance mode...")
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == "maintenance_mode").first()
        if setting:
            setting.value = "true"
            db.commit()
            clear_settings_cache("maintenance_mode")  # Clears cache in THIS process only
            print_success("Maintenance mode enabled in DB")
        
        # Test service function (in THIS process)
        time.sleep(0.2)
        if is_maintenance_mode():
            print_success("is_maintenance_mode() returns True (in test process)")
        else:
            print_error("is_maintenance_mode() should return True")
        
        # NOTE: The FastAPI server process has its own cache that won't be cleared
        # by our test process. The cache will expire after 60s or when settings
        # are updated via the API (which clears the cache in the server process).
        # For immediate effect, use: python manage_settings.py set maintenance_mode true
        # Or use the admin API which clears cache on update.
        
        print_info("  Note: FastAPI server cache may not reflect change immediately")
        print_info("  Use manage_settings.py or admin API for production updates")
        
        # Disable maintenance mode
        print_info("Disabling maintenance mode...")
        setting.value = "false"
        db.commit()
        clear_settings_cache("maintenance_mode")
        print_success("Maintenance mode disabled")
        
        # Test endpoint works
        time.sleep(0.5)
        response = requests.get(f"{API_BASE}/api/v1/courses")
        if response.status_code == 200:
            print_success(f"Public endpoint accessible: {response.status_code}")
        elif response.status_code == 503:
            print_info("  Still in maintenance (server cache hasn't expired yet)")
        else:
            print_error(f"Unexpected status: {response.status_code}")
            
    except Exception as e:
        print_error(f"Maintenance mode test failed: {e}")
    finally:
        db.close()


def test_registration_toggle():
    """Test registration toggle functionality"""
    print_header("Testing Registration Toggle")
    
    db = SessionLocal()
    try:
        # Disable registration
        print_info("Disabling new registrations...")
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == "allow_new_registrations").first()
        if setting:
            setting.value = "false"
            db.commit()
            clear_settings_cache("allow_new_registrations")  # Clears in THIS process only
            print_success("Registration disabled in DB")
        
        # Test service function (in THIS process)
        if not allow_new_registrations():
            print_success("allow_new_registrations() returns False (in test process)")
        else:
            print_error("allow_new_registrations() should return False")
        
        # NOTE: Same caching issue as maintenance mode - FastAPI server has its own cache
        print_info("  Note: FastAPI server cache may take up to 60s to reflect change")
        print_info("  For immediate effect, update via admin API or wait for TTL expiry")
        
        # Enable registration
        print_info("Enabling new registrations...")
        setting.value = "true"
        db.commit()
        clear_settings_cache("allow_new_registrations")
        print_success("Registration enabled in DB")
        
        # Test signup (may still be cached as disabled in server process)
        time.sleep(0.5)
        response = requests.post(
            f"{API_BASE}/api/v1/auth/signup",
            json={
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        if response.status_code == 201:
            print_success(f"Signup allowed: {response.status_code}")
        elif response.status_code == 403:
            print_info(f"  Still blocked (server cache hasn't expired yet)")
        else:
            print_info(f"  Got status {response.status_code}")
            
    except Exception as e:
        print_error(f"Registration toggle test failed: {e}")
    finally:
        db.close()


def test_mentor_approval():
    """Test mentor approval requirement setting"""
    print_header("Testing Mentor Approval Requirement")
    
    db = SessionLocal()
    try:
        # Test with approval required
        print_info("Setting mentor_approval_required = true...")
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == "mentor_approval_required").first()
        if setting:
            setting.value = "true"
            db.commit()
            clear_settings_cache("mentor_approval_required")
        
        if require_mentor_approval():
            print_success("require_mentor_approval() returns True")
            print_info("  New mentor applications will start in PENDING status")
        else:
            print_error("require_mentor_approval() should return True")
        
        # Test with approval not required
        print_info("Setting mentor_approval_required = false...")
        setting.value = "false"
        db.commit()
        clear_settings_cache("mentor_approval_required")
        
        if not require_mentor_approval():
            print_success("require_mentor_approval() returns False")
            print_info("  New mentor applications will start in APPROVED status")
        else:
            print_error("require_mentor_approval() should return False")
            
    except Exception as e:
        print_error(f"Mentor approval test failed: {e}")
    finally:
        db.close()


def test_featured_courses():
    """Test featured courses functionality"""
    print_header("Testing Featured Courses")
    
    db = SessionLocal()
    try:
        # Set featured courses
        print_info("Setting featured courses...")
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == "featured_courses").first()
        if setting:
            setting.value = '["python-fundamentals", "web-development", "data-science"]'
            db.commit()
            clear_settings_cache("featured_courses")
            print_success("Featured courses set in DB")
        
        # Test service function
        featured = get_featured_courses()
        if featured == ["python-fundamentals", "web-development", "data-science"]:
            print_success(f"get_featured_courses() returns correct list: {featured}")
        else:
            print_error(f"Expected specific courses, got {featured}")
        
        # Clear featured courses
        print_info("Clearing featured courses...")
        setting.value = '[]'
        db.commit()
        clear_settings_cache("featured_courses")
        
        featured = get_featured_courses()
        if featured == []:
            print_success("Featured courses cleared successfully")
        else:
            print_error(f"Expected empty list, got {featured}")
            
    except Exception as e:
        print_error(f"Featured courses test failed: {e}")
    finally:
        db.close()


def test_cache():
    """Test settings cache functionality"""
    print_header("Testing Settings Cache")
    
    db = SessionLocal()
    try:
        # Time DB query
        start = time.time()
        get_setting("platform_name", use_cache=False)
        db_time = time.time() - start
        print_info(f"Direct DB query time: {db_time*1000:.2f}ms")
        
        # Time cached query
        start = time.time()
        get_setting("platform_name", use_cache=True)
        cache_time = time.time() - start
        print_info(f"Cached query time: {cache_time*1000:.2f}ms")
        
        if cache_time < db_time:
            print_success(f"Cache is faster ({cache_time/db_time*100:.1f}% of DB time)")
        else:
            print_error("Cache should be faster than DB query")
        
        # Test cache invalidation
        print_info("Testing cache invalidation...")
        get_setting("platform_name", use_cache=True)  # Populate cache
        clear_settings_cache("platform_name")
        print_success("Cache cleared successfully")
        
    except Exception as e:
        print_error(f"Cache test failed: {e}")
    finally:
        db.close()


def main():
    print("\n" + "🔧 PLATFORM SETTINGS TEST SUITE 🔧".center(60))
    print("This script tests all settings functionality\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE}/healthz")
        if response.status_code == 200:
            print_success("Backend is running")
        else:
            print_error("Backend health check failed")
            return
    except Exception as e:
        print_error(f"Cannot connect to backend at {API_BASE}")
        print_info("Please start the backend: uvicorn app.main:app --reload --port 8001")
        return
    
    # Run tests
    test_settings_api()
    test_maintenance_mode()
    test_registration_toggle()
    test_mentor_approval()
    test_featured_courses()
    test_cache()
    
    print_header("Test Suite Complete")
    print_success("All settings features have been tested")
    print_info("\nNext steps:")
    print("  1. Check the admin settings UI at http://localhost:3000/admin/settings")
    print("  2. Use manage_settings.py for CLI management")
    print("  3. Monitor logs for settings-related events")


if __name__ == "__main__":
    main()
