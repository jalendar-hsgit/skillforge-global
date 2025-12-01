"""
Comprehensive Admin Feature Testing Script
Tests all implemented admin features including signup, authentication, and all admin endpoints.
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"

# Test credentials
ADMIN_EMAIL = "admin@skillforge.test"
ADMIN_PASSWORD = "Admin123!"
SUPERADMIN_EMAIL = "superadmin@skillforge.test"
SUPERADMIN_PASSWORD = "SuperAdmin123!"

# Global session for maintaining cookies
session = requests.Session()

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_test(test_name: str, status: str, details: str = ""):
    """Print test result"""
    emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{emoji} {test_name}: {status}")
    if details:
        print(f"   → {details}")

def test_endpoint(method: str, endpoint: str, data: Optional[dict] = None, 
                 expected_status: int = 200, description: str = ""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = session.get(url)
        elif method == "POST":
            response = session.post(url, json=data)
        elif method == "PUT":
            response = session.put(url, json=data)
        elif method == "PATCH":
            response = session.patch(url, json=data)
        elif method == "DELETE":
            response = session.delete(url)
        else:
            return False, "Invalid method"
        
        success = response.status_code == expected_status
        status = "PASS" if success else "FAIL"
        details = f"{method} {endpoint} → {response.status_code}"
        
        if description:
            details = f"{description} | {details}"
        
        if not success:
            try:
                error_data = response.json()
                details += f" | Error: {error_data.get('detail', 'Unknown')}"
            except:
                details += f" | Response: {response.text[:100]}"
        
        print_test(f"{method} {endpoint}", status, details)
        return success, response
    except Exception as e:
        print_test(f"{method} {endpoint}", "FAIL", f"Exception: {str(e)}")
        return False, None

# ============================================================================
# TEST SUITE
# ============================================================================

def test_1_admin_signup():
    """Test 1: Admin Signup and Authentication"""
    print_section("TEST 1: Admin Signup & Authentication")
    
    # Test regular signup (will be USER role by default)
    test_endpoint("POST", "/api/v1/auth/signup", {
        "email": "testuser@skillforge.test",
        "password": "Test123!",
        "full_name": "Test User"
    }, 200, "Create regular user")
    
    # Test admin signup (if endpoint exists) - Note: typically created via database
    # For testing, we'll assume admin users are pre-created
    
    # Test login as admin
    success, response = test_endpoint("POST", "/api/v1/auth/login", {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }, 200, "Admin login")
    
    if success:
        print_test("Admin Authentication", "PASS", "Admin logged in successfully")
    else:
        print_test("Admin Authentication", "FAIL", "Login failed - ensure admin user exists")
        print("   → Create admin user manually in database with role='ADMIN'")
    
    # Test /me endpoint
    test_endpoint("GET", "/api/v1/auth/me", 
                 expected_status=200, description="Get current user info")

def test_2_dashboard_stats():
    """Test 2: Admin Dashboard Statistics"""
    print_section("TEST 2: Admin Dashboard Stats")
    
    test_endpoint("GET", "/api/v1x/admin/dashboard/stats", 
                 expected_status=200, description="Dashboard statistics")

def test_3_user_management():
    """Test 3: User Management"""
    print_section("TEST 3: User Management")
    
    test_endpoint("GET", "/api/v1x/admin/users", 
                 expected_status=200, description="List all users")
    
    test_endpoint("GET", "/api/v1x/admin/users?role=student", 
                 expected_status=200, description="Filter users by role")
    
    # Get a user ID for testing (assuming user exists)
    success, response = session.get(f"{BASE_URL}/api/v1x/admin/users")
    if success and response.status_code == 200:
        users = response.json().get("users", [])
        if users:
            user_id = users[0]["id"]
            test_endpoint("GET", f"/api/v1x/admin/users/{user_id}", 
                         expected_status=200, description="Get user details")

def test_4_mentor_management():
    """Test 4: Mentor Management"""
    print_section("TEST 4: Mentor Management")
    
    test_endpoint("GET", "/api/v1x/admin/mentors", 
                 expected_status=200, description="List all mentors")
    
    test_endpoint("GET", "/api/v1x/admin/mentors?status=pending", 
                 expected_status=200, description="Get pending mentor applications")

def test_5_session_management():
    """Test 5: Session Management"""
    print_section("TEST 5: Session Management")
    
    test_endpoint("GET", "/api/v1x/admin/sessions", 
                 expected_status=200, description="List all sessions")
    
    test_endpoint("GET", "/api/v1x/admin/sessions/stats", 
                 expected_status=200, description="Session statistics")

def test_6_audit_logs():
    """Test 6: Audit Logs"""
    print_section("TEST 6: Audit Logs")
    
    test_endpoint("GET", "/api/v1x/admin/logs", 
                 expected_status=200, description="Get audit logs")
    
    test_endpoint("GET", "/api/v1x/admin/logs?action=user_login", 
                 expected_status=200, description="Filter logs by action")

def test_7_platform_settings():
    """Test 7: Platform Settings"""
    print_section("TEST 7: Platform Settings")
    
    test_endpoint("GET", "/api/v1x/admin/settings", 
                 expected_status=200, description="Get all platform settings")
    
    # Test update setting
    test_endpoint("PUT", "/api/v1x/admin/settings/maintenance_mode", {
        "value": "false",
        "description": "Maintenance mode toggle"
    }, expected_status=200, description="Update setting")

def test_8_analytics_dashboard():
    """Test 8: Analytics Dashboard"""
    print_section("TEST 8: Analytics Dashboard")
    
    test_endpoint("GET", "/api/v1x/admin/analytics", 
                 expected_status=200, description="Platform analytics")
    
    test_endpoint("GET", "/api/v1x/admin/analytics?timeframe=30d", 
                 expected_status=200, description="Analytics with timeframe")

def test_9_course_management():
    """Test 9: Course Management"""
    print_section("TEST 9: Course Management")
    
    test_endpoint("GET", "/api/v1x/admin/courses", 
                 expected_status=200, description="List all courses")
    
    # Test create course
    success, response = test_endpoint("POST", "/api/v1x/admin/courses", {
        "title": "Test Admin Course",
        "slug": "test-admin-course",
        "description": "Created via admin API test",
        "level": "beginner",
        "duration_hours": 10,
        "is_featured": False
    }, expected_status=200, description="Create new course")
    
    if success and response:
        try:
            course_data = response.json()
            course_id = course_data.get("course", {}).get("id")
            if course_id:
                # Test toggle featured
                test_endpoint("POST", f"/api/v1x/admin/courses/{course_id}/toggle-featured", 
                             expected_status=200, description="Toggle course featured status")
                
                # Test delete course
                test_endpoint("DELETE", f"/api/v1x/admin/courses/{course_id}", 
                             expected_status=200, description="Delete test course")
        except:
            pass

def test_10_revenue_dashboard():
    """Test 10: Revenue & Payments Dashboard"""
    print_section("TEST 10: Revenue & Payments Dashboard")
    
    test_endpoint("GET", "/api/v1x/admin/revenue/overview", 
                 expected_status=200, description="Revenue overview")
    
    test_endpoint("GET", "/api/v1x/admin/revenue/transactions", 
                 expected_status=200, description="Transaction history")
    
    test_endpoint("GET", "/api/v1x/admin/revenue/mentor-earnings", 
                 expected_status=200, description="Mentor earnings")

def test_11_marketplace_admin():
    """Test 11: Marketplace Admin Panel"""
    print_section("TEST 11: Marketplace Admin Panel")
    
    test_endpoint("GET", "/api/v1x/admin/marketplace/orders", 
                 expected_status=200, description="List all orders")
    
    test_endpoint("GET", "/api/v1x/admin/marketplace/stats", 
                 expected_status=200, description="Marketplace statistics")
    
    test_endpoint("GET", "/api/v1x/admin/marketplace/coupons", 
                 expected_status=200, description="List all coupons")

def test_12_user_analytics():
    """Test 12: User Analytics & Engagement"""
    print_section("TEST 12: User Analytics & Engagement")
    
    test_endpoint("GET", "/api/v1x/admin/user-analytics/overview", 
                 expected_status=200, description="User engagement overview (DAU/WAU/MAU)")
    
    test_endpoint("GET", "/api/v1x/admin/user-analytics/cohorts", 
                 expected_status=200, description="Retention cohort analysis")
    
    test_endpoint("GET", "/api/v1x/admin/user-analytics/activity", 
                 expected_status=200, description="User segmentation & activity")
    
    test_endpoint("GET", "/api/v1x/admin/user-analytics/popular-content", 
                 expected_status=200, description="Popular content analytics")
    
    test_endpoint("GET", "/api/v1x/admin/user-analytics/churn-risk", 
                 expected_status=200, description="Churn risk detection")

def test_13_notifications():
    """Test 13: Email & Notification Management"""
    print_section("TEST 13: Email & Notification Management")
    
    test_endpoint("GET", "/api/v1x/admin/notifications/stats", 
                 expected_status=200, description="Notification statistics")
    
    test_endpoint("GET", "/api/v1x/admin/notifications/templates", 
                 expected_status=200, description="List email templates")
    
    test_endpoint("GET", "/api/v1x/admin/notifications/history", 
                 expected_status=200, description="Notification send history")
    
    # Test create template
    success, response = test_endpoint("POST", "/api/v1x/admin/notifications/templates", {
        "name": "Test Template",
        "subject": "Test Email Subject",
        "html_content": "<h1>Test Email</h1><p>This is a test.</p>",
        "text_content": "Test Email - This is a test."
    }, expected_status=200, description="Create email template")
    
    if success and response:
        try:
            template_data = response.json()
            template = template_data.get("template", {})
            template_id = template.get("id")
            if template_id:
                # Test delete template
                test_endpoint("DELETE", f"/api/v1x/admin/notifications/templates/{template_id}", 
                             expected_status=200, description="Delete test template")
        except:
            pass

def test_14_rate_limiting():
    """Test 14: Rate Limiting Management"""
    print_section("TEST 14: Rate Limiting Management")
    
    test_endpoint("GET", "/api/v1x/admin/rate-limits", 
                 expected_status=200, description="Get rate limit info")
    
    test_endpoint("POST", "/api/v1x/admin/clear-rate-limits", 
                 expected_status=200, description="Clear rate limits")

def print_all_urls():
    """Print all available admin URLs"""
    print_section("ALL ADMIN URLs - Frontend & Backend")
    
    print("\n📱 FRONTEND URLs (http://localhost:3000):")
    print("-" * 80)
    frontend_urls = [
        ("/admin", "Admin Dashboard - Main hub with stats and quick links"),
        ("/admin/analytics", "Analytics Dashboard - Platform performance metrics"),
        ("/admin/user-analytics", "User Analytics - DAU/WAU/MAU, cohorts, churn"),
        ("/admin/revenue", "Revenue Dashboard - Financial analytics & payments"),
        ("/admin/marketplace", "Marketplace Admin - Orders, coupons, sales"),
        ("/admin/notifications", "Email & Notifications - Broadcast emails, templates"),
        ("/admin/users", "User Management - List, edit, suspend users"),
        ("/admin/mentors", "Mentor Management - Approve, manage mentors"),
        ("/admin/sessions", "Session Management - Review, moderate sessions"),
        ("/admin/courses-enhanced", "Course Management - Full CRUD, bulk ops"),
        ("/admin/logs", "Audit Logs - View all admin activity"),
        ("/admin/settings", "Platform Settings - Configure platform"),
        ("/login", "Login Page - Admin authentication"),
        ("/signup", "Signup Page - Create new accounts"),
    ]
    
    for url, description in frontend_urls:
        print(f"  {FRONTEND_URL}{url:<30} - {description}")
    
    print("\n🔌 BACKEND API URLs (http://localhost:8001):")
    print("-" * 80)
    
    backend_urls = [
        # Authentication
        ("POST", "/api/v1/auth/signup", "Create new user account"),
        ("POST", "/api/v1/auth/login", "User login (sets auth cookie)"),
        ("POST", "/api/v1/auth/logout", "User logout (clears cookie)"),
        ("GET", "/api/v1/auth/me", "Get current user info"),
        
        # Dashboard
        ("GET", "/api/v1x/admin/dashboard/stats", "Dashboard statistics"),
        
        # User Management
        ("GET", "/api/v1x/admin/users", "List all users (paginated, filterable)"),
        ("GET", "/api/v1x/admin/users/{id}", "Get user details by ID"),
        ("PUT", "/api/v1x/admin/users/{id}/role", "Update user role"),
        ("POST", "/api/v1x/admin/users/{id}/suspend", "Suspend/unsuspend user"),
        ("DELETE", "/api/v1x/admin/users/{id}", "Delete user"),
        
        # Mentor Management
        ("GET", "/api/v1x/admin/mentors", "List all mentors (filterable by status)"),
        ("GET", "/api/v1x/admin/mentors/{id}", "Get mentor details"),
        ("POST", "/api/v1x/admin/mentors/{id}/approve", "Approve mentor application"),
        ("POST", "/api/v1x/admin/mentors/{id}/reject", "Reject mentor application"),
        
        # Session Management
        ("GET", "/api/v1x/admin/sessions", "List all sessions (filterable)"),
        ("GET", "/api/v1x/admin/sessions/stats", "Session statistics"),
        ("POST", "/api/v1x/admin/sessions/{id}/cancel", "Cancel session"),
        
        # Audit Logs
        ("GET", "/api/v1x/admin/logs", "Get audit logs (filterable, paginated)"),
        
        # Platform Settings
        ("GET", "/api/v1x/admin/settings", "Get all platform settings"),
        ("PUT", "/api/v1x/admin/settings/{key}", "Update setting by key"),
        ("DELETE", "/api/v1x/admin/settings/{key}", "Delete setting"),
        
        # Analytics Dashboard
        ("GET", "/api/v1x/admin/analytics", "Platform analytics with timeframe"),
        
        # Course Management
        ("GET", "/api/v1x/admin/courses", "List all courses"),
        ("POST", "/api/v1x/admin/courses", "Create new course"),
        ("PUT", "/api/v1x/admin/courses/{id}", "Update course"),
        ("DELETE", "/api/v1x/admin/courses/{id}", "Delete course"),
        ("POST", "/api/v1x/admin/courses/bulk-delete", "Bulk delete courses"),
        ("POST", "/api/v1x/admin/courses/{id}/toggle-featured", "Toggle featured status"),
        
        # Revenue Dashboard
        ("GET", "/api/v1x/admin/revenue/overview", "Revenue overview with timeframe"),
        ("GET", "/api/v1x/admin/revenue/transactions", "Transaction history"),
        ("GET", "/api/v1x/admin/revenue/mentor-earnings", "Mentor earnings leaderboard"),
        
        # Marketplace Admin
        ("GET", "/api/v1x/admin/marketplace/orders", "List all orders"),
        ("GET", "/api/v1x/admin/marketplace/stats", "Marketplace statistics"),
        ("GET", "/api/v1x/admin/marketplace/coupons", "List all coupons"),
        ("POST", "/api/v1x/admin/marketplace/coupons", "Create new coupon"),
        ("PATCH", "/api/v1x/admin/marketplace/coupons/{id}/toggle", "Toggle coupon active status"),
        ("DELETE", "/api/v1x/admin/marketplace/coupons/{id}", "Delete coupon"),
        ("POST", "/api/v1x/admin/marketplace/orders/{id}/refund", "Process order refund"),
        
        # User Analytics
        ("GET", "/api/v1x/admin/user-analytics/overview", "Engagement overview (DAU/WAU/MAU)"),
        ("GET", "/api/v1x/admin/user-analytics/cohorts", "Retention cohort analysis"),
        ("GET", "/api/v1x/admin/user-analytics/activity", "User segmentation & activity"),
        ("GET", "/api/v1x/admin/user-analytics/popular-content", "Popular mentors & courses"),
        ("GET", "/api/v1x/admin/user-analytics/churn-risk", "Users at risk of churning"),
        
        # Email & Notifications
        ("POST", "/api/v1x/admin/notifications/broadcast", "Send broadcast email"),
        ("GET", "/api/v1x/admin/notifications/history", "Notification send history"),
        ("GET", "/api/v1x/admin/notifications/stats", "Notification statistics"),
        ("GET", "/api/v1x/admin/notifications/templates", "List email templates"),
        ("POST", "/api/v1x/admin/notifications/templates", "Create email template"),
        ("PUT", "/api/v1x/admin/notifications/templates/{id}", "Update email template"),
        ("DELETE", "/api/v1x/admin/notifications/templates/{id}", "Delete email template"),
        
        # Rate Limiting
        ("GET", "/api/v1x/admin/rate-limits", "Get rate limit information"),
        ("POST", "/api/v1x/admin/clear-rate-limits", "Clear all rate limits"),
    ]
    
    for method, url, description in backend_urls:
        print(f"  {method:<7} {url:<50} - {description}")
    
    print("\n📊 API Documentation:")
    print("-" * 80)
    print(f"  {BASE_URL}/docs        - Swagger UI (Interactive API docs)")
    print(f"  {BASE_URL}/redoc       - ReDoc (Alternative API docs)")
    print(f"  {BASE_URL}/openapi.json - OpenAPI schema")

def run_all_tests():
    """Run all test suites"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "SKILLFORGE ADMIN FEATURE TESTS" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    
    # Print all URLs first
    print_all_urls()
    
    # Run tests
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "RUNNING TEST SUITE" + " "*35 + "║")
    print("╚" + "="*78 + "╝")
    
    test_1_admin_signup()
    test_2_dashboard_stats()
    test_3_user_management()
    test_4_mentor_management()
    test_5_session_management()
    test_6_audit_logs()
    test_7_platform_settings()
    test_8_analytics_dashboard()
    test_9_course_management()
    test_10_revenue_dashboard()
    test_11_marketplace_admin()
    test_12_user_analytics()
    test_13_notifications()
    test_14_rate_limiting()
    
    print_section("TEST SUITE COMPLETE")
    print("\n✨ All admin features have been tested!")
    print("\n📝 Notes:")
    print("  - Some tests may fail if required data doesn't exist (users, sessions, etc.)")
    print("  - Create test data using the frontend or seed scripts for comprehensive testing")
    print("  - Ensure both frontend (npm run dev) and backend (uvicorn) are running")
    print("  - Admin user must exist with email:", ADMIN_EMAIL)
    print("\n")

if __name__ == "__main__":
    print("\n🚀 Starting SkillForge Admin Feature Tests...")
    print(f"   Backend:  {BASE_URL}")
    print(f"   Frontend: {FRONTEND_URL}")
    print("\n⚠️  Prerequisites:")
    print("   1. Backend server running: uvicorn app.main:app --reload --port 8001")
    print("   2. Frontend server running: npm run dev")
    print("   3. Admin user exists with credentials above")
    print("\n")
    
    input("Press ENTER to continue...")
    
    run_all_tests()
