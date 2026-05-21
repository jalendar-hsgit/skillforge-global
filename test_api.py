"""
Comprehensive API Testing Script for SkillForge Global
Tests all major endpoints and validates responses
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"
session = requests.Session()

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")
    print()

def test_health():
    """Test health endpoint"""
    try:
        response = session.get(f"{BASE_URL}/healthz")
        passed = response.status_code == 200 and response.json().get("ok") == True
        print_test("Health Check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_signup(email, password):
    """Test user signup"""
    try:
        response = session.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json={"email": email, "password": password}
        )
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        if not passed:
            details += f" - {response.text}"
        print_test(f"Signup ({email})", passed, details)
        return passed, response
    except Exception as e:
        print_test(f"Signup ({email})", False, f"Error: {str(e)}")
        return False, None

def test_login(email, password):
    """Test user login"""
    try:
        response = session.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        if passed:
            # Check if cookie was set
            has_cookie = 'token' in session.cookies
            details += f" - Cookie set: {has_cookie}"
        else:
            details += f" - {response.text}"
        print_test(f"Login ({email})", passed, details)
        return passed, response
    except Exception as e:
        print_test(f"Login ({email})", False, f"Error: {str(e)}")
        return False, None

def test_me():
    """Test /me endpoint (requires auth)"""
    try:
        response = session.get(f"{BASE_URL}/api/v1/auth/me")
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        if passed:
            data = response.json()
            details += f" - User ID: {data.get('id')}, Email: {data.get('email')}"
        else:
            details += f" - {response.text}"
        print_test("Get Current User (/me)", passed, details)
        return passed, response
    except Exception as e:
        print_test("Get Current User (/me)", False, f"Error: {str(e)}")
        return False, None

def test_job_applications():
    """Test job application CRUD"""
    try:
        # Create application
        app_data = {
            "company_name": "Test Company",
            "position_title": "Senior Developer",
            "job_type": "full_time",
            "location": "Remote",
            "work_mode": "remote",
            "status": "applied",
            "priority": 5,
            "application_date": datetime.now().isoformat(),
            "skills_required": ["Python", "React", "PostgreSQL"],
            "notes": "Test application from API test script"
        }
        
        response = session.post(
            f"{BASE_URL}/api/v1x/job-applications",
            json=app_data
        )
        passed = response.status_code == 200
        details = f"Create - Status: {response.status_code}"
        
        if passed:
            app_id = response.json().get('id')
            details += f" - Created ID: {app_id}"
            
            # Get application
            get_response = session.get(f"{BASE_URL}/api/v1x/job-applications/{app_id}")
            if get_response.status_code == 200:
                details += " | Get - OK"
            
            # List applications
            list_response = session.get(f"{BASE_URL}/api/v1x/job-applications")
            if list_response.status_code == 200:
                count = len(list_response.json())
                details += f" | List - {count} apps"
            
            # Get stats
            stats_response = session.get(f"{BASE_URL}/api/v1x/job-applications/stats")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                details += f" | Stats - {stats.get('total_applications')} total"
        else:
            details += f" - {response.text}"
            
        print_test("Job Application CRUD", passed, details)
        return passed, response
    except Exception as e:
        print_test("Job Application CRUD", False, f"Error: {str(e)}")
        return False, None

def test_notifications():
    """Test notification endpoints"""
    try:
        response = session.get(f"{BASE_URL}/api/v1x/job-applications-notifications/pending-reminders")
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        if passed:
            data = response.json()
            details += f" - Overdue: {data.get('overdue_followups')}, Interviews: {data.get('upcoming_interviews')}"
        else:
            details += f" - {response.text}"
        print_test("Get Pending Reminders", passed, details)
        return passed, response
    except Exception as e:
        print_test("Get Pending Reminders", False, f"Error: {str(e)}")
        return False, None

def test_logout():
    """Test logout"""
    try:
        response = session.post(f"{BASE_URL}/api/v1/auth/logout")
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        print_test("Logout", passed, details)
        return passed, response
    except Exception as e:
        print_test("Logout", False, f"Error: {str(e)}")
        return False, None

def run_all_tests():
    print("=" * 60)
    print("SkillForge Global - API Test Suite")
    print("=" * 60)
    print()
    
    # Generate unique test email
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_{timestamp}@example.com"
    test_password = "TestPass123!"
    
    # Run tests in sequence
    results = []
    
    # 1. Health check
    results.append(("Health", test_health()))
    
    # 2. Signup
    signup_passed, _ = test_signup(test_email, test_password)
    results.append(("Signup", signup_passed))
    
    if signup_passed:
        # 3. Login
        login_passed, _ = test_login(test_email, test_password)
        results.append(("Login", login_passed))
        
        if login_passed:
            # 4. Get current user
            me_passed, _ = test_me()
            results.append(("Get User", me_passed))
            
            # 5. Job applications
            job_passed, _ = test_job_applications()
            results.append(("Job Apps", job_passed))
            
            # 6. Notifications
            notif_passed, _ = test_notifications()
            results.append(("Notifications", notif_passed))
            
            # 7. Logout
            logout_passed, _ = test_logout()
            results.append(("Logout", logout_passed))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    print()
    print(f"TOTAL: {passed_count}/{total_count} tests passed")
    print(f"Success Rate: {(passed_count/total_count*100):.1f}%")
    print("=" * 60)
    
    return passed_count == total_count

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        exit(1)
