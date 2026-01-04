#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script
Tests all major endpoints with proper authentication
"""
import requests
import json
import time
from typing import Optional, Dict, Any

BASE_URL = "http://127.0.0.1:8001"
API_V1 = f"{BASE_URL}/api/v1"
API_V1X = f"{BASE_URL}/api/v1x"

# Test user credentials
TEST_EMAIL = "test_api_user@example.com"
TEST_PASSWORD = "TestPassword123!"

class APITester:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log(self, message: str, is_error: bool = False):
        prefix = "[FAIL]" if is_error else "[PASS]"
        print(f"{prefix} {message}")

    def test_endpoint(self, method: str, url: str, expected_status: int = 200, 
                     data: Optional[Dict] = None, description: str = "") -> bool:
        """Test a single endpoint"""
        try:
            if method.upper() == "GET":
                r = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=10)
            elif method.upper() == "POST":
                r = requests.post(url, headers=self.headers, cookies=self.cookies, json=data, timeout=10)
            elif method.upper() == "PUT":
                r = requests.put(url, headers=self.headers, cookies=self.cookies, json=data, timeout=10)
            elif method.upper() == "DELETE":
                r = requests.delete(url, headers=self.headers, cookies=self.cookies, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = r.status_code == expected_status
            status_text = "PASS" if success else "FAIL"
            
            print(f"\n{status_text}: {method.upper()} {url}")
            if description:
                print(f"  Description: {description}")
            print(f"  Expected: {expected_status}, Got: {r.status_code}")
            
            if not success or r.status_code >= 400:
                print(f"  Response: {r.text[:500]}")
                self.results["failed"] += 1
                self.results["errors"].append({
                    "endpoint": url,
                    "status": r.status_code,
                    "error": r.text[:200]
                })
            else:
                self.results["passed"] += 1
                # Try to show response for successful calls
                try:
                    data = r.json()
                    if isinstance(data, dict) and "id" in data:
                        print(f"  ID: {data.get('id')}")
                except:
                    pass
            
            return success

        except requests.exceptions.RequestException as e:
            print(f"\n❌ ERROR: {method.upper()} {url}")
            print(f"  Exception: {str(e)}")
            self.results["failed"] += 1
            self.results["errors"].append({
                "endpoint": url,
                "error": str(e)
            })
            return False

    def setup_auth(self):
        """Setup: Create test user and get auth token"""
        print("\n" + "="*70)
        print("SETUP: Creating test user and getting auth token")
        print("="*70)
        
        # Try to sign up
        r = requests.post(f"{API_V1}/auth/signup", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Test API User"
        }, timeout=10)
        
        if r.status_code in [200, 201]:
            print(f"✅ User registered: {TEST_EMAIL}")
        elif r.status_code == 409:
            print(f"✅ User already exists: {TEST_EMAIL}")
        else:
            print(f"⚠️  Registration response: {r.status_code} - {r.text[:200]}")

        # Login
        r = requests.post(f"{API_V1}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=10)
        
        if r.status_code != 200:
            print(f"❌ Login failed: {r.status_code}")
            print(f"  {r.text}")
            return False
        
        data = r.json()
        
        # Extract token from cookie
        if 'token' in r.cookies:
            self.token = r.cookies['token']
            self.cookies['token'] = self.token
        else:
            print(f"❌ No token in cookies. Response: {r.text}")
            return False
        
        # Get user ID from /auth/me
        r2 = requests.get(f"{API_V1}/auth/me", cookies=self.cookies, timeout=10)
        if r2.status_code == 200:
            me_data = r2.json()
            self.user_id = me_data.get("id")
        
        self.headers = {
            "Content-Type": "application/json"
        }
        
        print(f"✅ Login successful")
        print(f"  Token: {self.token[:50]}...")
        print(f"  User ID: {self.user_id}")
        return True

    def run_auth_tests(self):
        """Test authentication endpoints"""
        print("\n" + "="*70)
        print("TESTING: Authentication Endpoints")
        print("="*70)
        
        # Get current user
        self.test_endpoint("GET", f"{API_V1}/auth/me", 200, 
                          description="Get current authenticated user")

    def run_course_tests(self):
        """Test course endpoints"""
        print("\n" + "="*70)
        print("TESTING: Course Endpoints")
        print("="*70)
        
        # List all courses
        self.test_endpoint("GET", f"{API_V1}/courses", 200,
                          description="List all courses")
        
        # Get specific course
        self.test_endpoint("GET", f"{API_V1}/courses/python-fundamentals", 200,
                          description="Get specific course by path")

    def run_progress_tests(self):
        """Test progress tracking endpoints"""
        print("\n" + "="*70)
        print("TESTING: Progress Tracking Endpoints")
        print("="*70)
        
        # Get progress for a path
        self.test_endpoint("GET", f"{API_V1}/progress?path=python-fundamentals", 200,
                          description="Get progress for python-fundamentals course")
        
        # Mark progress
        self.test_endpoint("POST", f"{API_V1}/progress?path=python-fundamentals&module_id=intro", 200,
                          description="Mark module complete")
        
        # Get progress again
        self.test_endpoint("GET", f"{API_V1}/progress?path=python-fundamentals", 200,
                          description="Get updated progress")

    def run_coin_tests(self):
        """Test coins/currency endpoints"""
        print("\n" + "="*70)
        print("TESTING: Coins/Currency Endpoints")
        print("="*70)
        
        # Get coin balance
        self.test_endpoint("GET", f"{API_V1X}/coins_db/balance", 200,
                          description="Get current coin balance")
        
        # Add coins (if endpoint exists)
        self.test_endpoint("POST", f"{API_V1X}/coins_db/add", 404,
                          data={"amount": 10},
                          description="Add coins to account (may not exist)")

    def run_mentor_tests(self):
        """Test mentor endpoints"""
        print("\n" + "="*70)
        print("TESTING: Mentor Endpoints")
        print("="*70)
        
        # List mentors
        self.test_endpoint("GET", f"{API_V1X}/mentors", 200,
                          description="List all mentors")

    def run_marketplace_tests(self):
        """Test marketplace endpoints"""
        print("\n" + "="*70)
        print("TESTING: Marketplace Endpoints")
        print("="*70)
        
        # List products
        self.test_endpoint("GET", f"{API_V1X}/marketplace/products", 200,
                          description="List marketplace products")
        
        # Get seller stats (requires seller role)
        self.test_endpoint("GET", f"{API_V1X}/marketplace/seller/stats", 403,
                          description="Get seller stats (no seller role)")

    def run_quiz_tests(self):
        """Test quiz/coding practice endpoints"""
        print("\n" + "="*70)
        print("TESTING: Quiz & Coding Practice Endpoints")
        print("="*70)
        
        # Get quizzes
        self.test_endpoint("GET", f"{API_V1X}/quizzes-db/quizzes", 200,
                          description="List quizzes")
        
        # Get quiz by path
        self.test_endpoint("GET", f"{API_V1X}/quizzes-db/quizzes/python-fundamentals", 200,
                          description="Get quizzes for python-fundamentals")

    def run_job_application_tests(self):
        """Test job application endpoints"""
        print("\n" + "="*70)
        print("TESTING: Job Application Endpoints")
        print("="*70)
        
        # Get job applications
        self.test_endpoint("GET", f"{API_V1X}/job-applications", 200,
                          description="List my job applications")

    def run_user_profile_tests(self):
        """Test user profile endpoints"""
        print("\n" + "="*70)
        print("TESTING: User Profile Endpoints")
        print("="*70)
        
        # Get user profile
        self.test_endpoint("GET", f"{API_V1X}/user-profiles/profile", 200,
                          description="Get my user profile")

    def run_dashboard_tests(self):
        """Test dashboard endpoints"""
        print("\n" + "="*70)
        print("TESTING: Dashboard Endpoints")
        print("="*70)
        
        # Get student dashboard
        self.test_endpoint("GET", f"{API_V1X}/student-dashboard", 200,
                          description="Get student dashboard data")

    def run_activity_tests(self):
        """Test activity/social endpoints"""
        print("\n" + "="*70)
        print("TESTING: Activity & Social Endpoints")
        print("="*70)
        
        # Get user activity
        self.test_endpoint("GET", f"{API_V1X}/activity", 200,
                          description="Get my activity feed")

    def run_all_tests(self):
        """Run all test suites"""
        if not self.setup_auth():
            print("❌ Failed to setup authentication. Exiting.")
            return
        
        self.run_auth_tests()
        self.run_course_tests()
        self.run_progress_tests()
        self.run_coin_tests()
        self.run_mentor_tests()
        self.run_marketplace_tests()
        self.run_quiz_tests()
        self.run_job_application_tests()
        self.run_user_profile_tests()
        self.run_dashboard_tests()
        self.run_activity_tests()
        
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        total = self.results["passed"] + self.results["failed"]
        print(f"✅ Passed: {self.results['passed']}/{total}")
        print(f"❌ Failed: {self.results['failed']}/{total}")
        
        if self.results["errors"]:
            print(f"\nFailed Endpoints ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  - {error['endpoint']}")
                if 'status' in error:
                    print(f"    Status: {error['status']}")
                if 'error' in error:
                    print(f"    Error: {error['error'][:100]}")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    tester = APITester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
