#!/usr/bin/env python3
"""
Complete API Endpoint Testing Suite
Tests all backend API endpoints across all routers
"""
import requests
import json
import time
from typing import Optional, Dict, Any, List

BASE_URL = "http://127.0.0.1:8001"
API_V1 = f"{BASE_URL}/api/v1"
API_V1X = f"{BASE_URL}/api/v1x"

# Test user credentials (unique per run)
TEST_EMAIL = "test_api_" + str(int(time.time())) + "@example.com"
TEST_PASSWORD = "TestPassword123!"

class ComprehensiveAPITester:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        self.endpoints_tested = []

    def test_endpoint(self, method: str, url: str, expected_status: List[int] = None, 
                     data: Optional[Dict] = None, description: str = "") -> bool:
        """Test a single endpoint"""
        if expected_status is None:
            expected_status = [200]
        elif isinstance(expected_status, int):
            expected_status = [expected_status]
        
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

            success = r.status_code in expected_status
            status_text = "PASS" if success else "FAIL"
            
            self.endpoints_tested.append({
                "method": method.upper(),
                "url": url,
                "status": r.status_code,
                "expected": expected_status,
                "success": success
            })
            
            print(f"\n[{status_text}] {method.upper()} {url}")
            if description:
                print(f"  Desc: {description}")
            print(f"  Status: {r.status_code} (expected {expected_status[0]})")
            
            if not success or r.status_code >= 400:
                if r.text and len(r.text) < 500:
                    print(f"  Response: {r.text}")
                self.results["failed"] += 1
                self.results["errors"].append({
                    "endpoint": f"{method.upper()} {url}",
                    "status": r.status_code,
                    "expected": expected_status,
                    "error": r.text[:200] if r.text else "No response"
                })
            else:
                self.results["passed"] += 1
            
            return success

        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] {method.upper()} {url}")
            print(f"  Exception: {str(e)[:100]}")
            self.results["failed"] += 1
            self.results["errors"].append({
                "endpoint": f"{method.upper()} {url}",
                "error": str(e)[:100]
            })
            return False

    def setup_auth(self):
        """Setup: Create test user and get auth token"""
        print("\n" + "="*80)
        print("SETUP: Authentication")
        print("="*80)
        
        # Sign up
        r = requests.post(f"{API_V1}/auth/signup", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "API Test User"
        }, timeout=10)
        
        if r.status_code in [200, 201, 400]:
            print(f"[OK] User created/exists: {TEST_EMAIL}")
        else:
            print(f"[FAIL] Registration failed: {r.status_code}")
            return False

        # Login
        r = requests.post(f"{API_V1}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=10)
        
        if r.status_code != 200:
            print(f"[FAIL] Login failed: {r.status_code}")
            return False
        
        if 'token' in r.cookies:
            self.token = r.cookies['token']
            self.cookies['token'] = self.token
        else:
            print(f"[FAIL] No token in cookies")
            return False
        
        # Get user ID
        r2 = requests.get(f"{API_V1}/auth/me", cookies=self.cookies, timeout=10)
        if r2.status_code == 200:
            me_data = r2.json()
            self.user_id = me_data.get("id")
        
        self.headers = {"Content-Type": "application/json"}
        
        print(f"[OK] Login successful")
        print(f"  Token: {self.token[:40]}...")
        print(f"  User ID: {self.user_id}")
        return True

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Authentication (v1)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1}/auth/me", [200], 
                          description="Get current user info")
        self.test_endpoint("POST", f"{API_V1}/auth/logout", [200],
                          description="Logout (should set expired cookie)")

    def test_course_endpoints(self):
        """Test course endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Courses (v1)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1}/courses", [200],
                          description="List all courses")
        self.test_endpoint("GET", f"{API_V1}/courses/python-fundamentals", [200, 404],
                          description="Get specific course (may not exist)")

    def test_progress_endpoints(self):
        """Test progress tracking"""
        print("\n" + "="*80)
        print("TEST SUITE: Progress Tracking (v1)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1}/progress?path=python-fundamentals", [200],
                          description="Get progress for course")
        self.test_endpoint("POST", f"{API_V1}/progress?path=python-fundamentals&module_id=intro", [200],
                          description="Mark module complete")

    def test_coins_endpoints(self):
        """Test coins/currency endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Coins System (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/coins_db/balance", [200],
                          description="Get coin balance")
        self.test_endpoint("GET", f"{API_V1X}/coins_db/ledger", [200],
                          description="Get transaction history")

    def test_mentor_endpoints(self):
        """Test mentor endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Mentors (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/mentors", [200],
                          description="List all mentors")
        self.test_endpoint("GET", f"{API_V1X}/mentors/search?skill=python", [200, 404],
                          description="Search mentors by skill")

    def test_marketplace_endpoints(self):
        """Test marketplace endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Marketplace (v1x)")
        print("="*80)
        
        # Courses marketplace
        self.test_endpoint("GET", f"{API_V1X}/marketplace/courses", [200],
                          description="List marketplace courses")
        
        # Digital products
        self.test_endpoint("GET", f"{API_V1X}/marketplace/digital-products", [200],
                          description="List digital products")
        self.test_endpoint("GET", f"{API_V1X}/marketplace/best-sellers", [200],
                          description="Get best sellers")
        
        # Cart
        self.test_endpoint("GET", f"{API_V1X}/marketplace/cart", [200],
                          description="Get shopping cart")
        
        # Orders
        self.test_endpoint("GET", f"{API_V1X}/marketplace/orders", [200],
                          description="Get my orders")
        
        # Seller
        self.test_endpoint("GET", f"{API_V1X}/marketplace/seller/account", [200, 404],
                          description="Get seller account (may not be seller)")

    def test_job_endpoints(self):
        """Test job application endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Job Applications (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/job-applications", [200],
                          description="List my job applications")
        self.test_endpoint("GET", f"{API_V1X}/job-applications/statistics", [200],
                          description="Get application stats")

    def test_activity_endpoints(self):
        """Test activity/social endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Activity & Social (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/activity", [200],
                          description="Get activity feed")
        self.test_endpoint("GET", f"{API_V1X}/activity/streak", [200],
                          description="Get learning streak")

    def test_learning_endpoints(self):
        """Test learning/educational endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Learning Content (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/coding-practice", [200, 404],
                          description="Get coding practice problems")
        self.test_endpoint("GET", f"{API_V1X}/learning-paths", [200, 404],
                          description="Get learning paths")

    def test_badges_endpoints(self):
        """Test badges/gamification"""
        print("\n" + "="*80)
        print("TEST SUITE: Badges & Gamification (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/badges", [200],
                          description="Get my badges")
        self.test_endpoint("GET", f"{API_V1X}/badges/achievements", [200],
                          description="Get achievements list")

    def test_subscription_endpoints(self):
        """Test subscription endpoints"""
        print("\n" + "="*80)
        print("TEST SUITE: Subscriptions (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/subscriptions", [200],
                          description="Get my subscriptions")
        self.test_endpoint("GET", f"{API_V1X}/subscriptions/plans", [200],
                          description="Get available plans")

    def test_account_endpoints(self):
        """Test account management"""
        print("\n" + "="*80)
        print("TEST SUITE: Account Management (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/account/profile", [200],
                          description="Get profile info")
        self.test_endpoint("GET", f"{API_V1X}/account/settings", [200],
                          description="Get account settings")

    def test_recommendations_endpoints(self):
        """Test recommendation system"""
        print("\n" + "="*80)
        print("TEST SUITE: Recommendations (v1x)")
        print("="*80)
        
        self.test_endpoint("GET", f"{API_V1X}/recommendations", [200],
                          description="Get course recommendations")
        self.test_endpoint("GET", f"{API_V1X}/recommendations/jobs", [200],
                          description="Get job recommendations")

    def run_all_tests(self):
        """Run all test suites"""
        if not self.setup_auth():
            print("[FAIL] Authentication setup failed. Exiting.")
            return
        
        # Run all test suites
        self.test_auth_endpoints()
        self.test_course_endpoints()
        self.test_progress_endpoints()
        self.test_coins_endpoints()
        self.test_mentor_endpoints()
        self.test_marketplace_endpoints()
        self.test_job_endpoints()
        self.test_activity_endpoints()
        self.test_learning_endpoints()
        self.test_badges_endpoints()
        self.test_subscription_endpoints()
        self.test_account_endpoints()
        self.test_recommendations_endpoints()
        
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        
        print(f"\nResults:")
        print(f"  PASSED: {self.results['passed']}/{total}")
        print(f"  FAILED: {self.results['failed']}/{total}")
        print(f"  PASS RATE: {pass_rate:.1f}%")
        
        print(f"\nEndpoints Tested: {len(self.endpoints_tested)}")
        
        if self.results["errors"]:
            print(f"\nFailed Tests ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results["errors"][:10], 1):
                print(f"\n  {i}. {error.get('endpoint', 'Unknown')}")
                if 'status' in error:
                    print(f"     Status: {error['status']}")
                if 'expected' in error:
                    print(f"     Expected: {error['expected']}")
                print(f"     Error: {error.get('error', 'No message')[:80]}")
            
            if len(self.results["errors"]) > 10:
                print(f"\n  ... and {len(self.results['errors']) - 10} more")
        
        print("\n" + "="*80)
        print("Detailed Results by Endpoint:")
        print("="*80)
        
        # Group by status
        passed_endpoints = [e for e in self.endpoints_tested if e['success']]
        failed_endpoints = [e for e in self.endpoints_tested if not e['success']]
        
        print(f"\nPASSED ({len(passed_endpoints)}):")
        for e in passed_endpoints[:20]:
            print(f"  [OK] {e['method']:6s} {e['url']}")
        if len(passed_endpoints) > 20:
            print(f"  ... and {len(passed_endpoints) - 20} more")
        
        print(f"\nFAILED ({len(failed_endpoints)}):")
        for e in failed_endpoints:
            print(f"  [XX] {e['method']:6s} {e['url']} -> {e['status']}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    tester = ComprehensiveAPITester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Tests interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\n\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
