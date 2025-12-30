"""Test authentication and all API endpoints"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_auth():
    """Test signup and login"""
    print("=" * 70)
    print("AUTHENTICATION TESTS")
    print("=" * 70)
    
    # Test signup
    print("\n1. Testing Signup...")
    signup_data = {
        "email": f"testuser_{datetime.now().timestamp()}@test.com",
        "username": f"testuser_{int(datetime.now().timestamp())}",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [PASS] Signup successful")
            data = response.json()
            print(f"   User ID: {data.get('id')}")
        else:
            print(f"   [FAIL] {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test login
    print("\n2. Testing Login...")
    login_data = {
        "username": "admin",  # Try default admin
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [PASS] Login successful")
            token = response.cookies.get('token')
            if token:
                print(f"   Token received: {token[:20]}...")
                return token
        else:
            print(f"   [FAIL] {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    return None

def test_all_endpoints():
    """Test all available API endpoints"""
    print("\n\n" + "=" * 70)
    print("API ENDPOINTS TEST")
    print("=" * 70)
    
    endpoints = [
        # Core APIs
        ("GET", "/healthz", "Health Check"),
        ("GET", "/api/v1/courses", "Courses List"),
        ("GET", "/api/v1/quizzes", "Quizzes"),
        
        # V1X APIs
        ("GET", "/api/v1x/courses-db", "Courses DB"),
        ("GET", "/api/v1x/coding-practice/challenges", "Coding Challenges"),
        ("GET", "/api/v1x/snippets", "Code Snippets"),
        ("GET", "/api/v1x/solutions", "Solutions"),
        ("GET", "/api/v1x/mentors", "Mentors List"),
        ("GET", "/api/v1x/learning-paths", "Learning Paths"),
        ("GET", "/api/v1x/contests", "Contests"),
        ("GET", "/api/v1x/notifications/preferences", "Notification Preferences"),
        ("GET", "/api/v1x/badges", "Badges"),
        ("GET", "/api/v1x/forums/categories", "Forum Categories"),
        ("GET", "/api/v1x/teams", "Teams"),
        
        # Admin APIs
        ("GET", "/api/v1/admin/settings", "Admin Settings"),
    ]
    
    results = {"pass": 0, "fail": 0, "error": 0}
    
    print("\nTesting endpoints...\n")
    for method, endpoint, name in endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"[PASS] {name:<35} {endpoint}")
                results["pass"] += 1
            elif response.status_code == 401:
                print(f"[AUTH] {name:<35} {endpoint} (requires login)")
                results["pass"] += 1
            elif response.status_code == 404:
                print(f"[404 ] {name:<35} {endpoint}")
                results["fail"] += 1
            else:
                print(f"[{response.status_code}] {name:<35} {endpoint}")
                results["fail"] += 1
        except requests.exceptions.ConnectionError:
            print(f"[CONN] {name:<35} BACKEND NOT RUNNING!")
            results["error"] += 1
            break
        except Exception as e:
            print(f"[ERR ] {name:<35} {str(e)[:40]}")
            results["error"] += 1
    
    print("\n" + "-" * 70)
    print(f"Results: {results['pass']} passed, {results['fail']} failed, {results['error']} errors")
    return results

def test_frontend():
    """Check if frontend is running"""
    print("\n\n" + "=" * 70)
    print("FRONTEND TEST")
    print("=" * 70)
    
    frontend_urls = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
    for url in frontend_urls:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"\n[PASS] Frontend running at {url}")
                return True
        except:
            pass
    
    print("\n[FAIL] Frontend not running on ports 3000 or 3001")
    return False

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print(f"COMPREHENSIVE API TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Test auth
    token = test_auth()
    
    # Test all endpoints
    results = test_all_endpoints()
    
    # Test frontend
    frontend_running = test_frontend()
    
    print("\n\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Backend Status: {'RUNNING' if results['error'] == 0 else 'NOT RUNNING'}")
    print(f"Frontend Status: {'RUNNING' if frontend_running else 'NOT RUNNING'}")
    print(f"API Tests: {results['pass']} passed, {results['fail']} failed")
    print("=" * 70 + "\n")
