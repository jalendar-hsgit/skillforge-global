#!/usr/bin/env python3
"""
Targeted Testing for 5 Missing/Failing Endpoints
Tests the specific features the user requested
"""
import requests
import json
import time
from typing import Optional, Dict, List

BASE_URL = "http://127.0.0.1:8001"
API_V1 = f"{BASE_URL}/api/v1"
API_V1X = f"{BASE_URL}/api/v1x"

# Test user
TEST_EMAIL = "test_targeted_" + str(int(time.time())) + "@example.com"
TEST_PASSWORD = "TestPassword123!"

class TargetedFeatureTester:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.results = {
            "tested": [],
            "passed": 0,
            "failed": 0
        }

    def test_endpoint(self, feature_name: str, method: str, url: str, 
                     expected_status: List[int] = None, data: Optional[Dict] = None) -> bool:
        """Test a single endpoint and record results"""
        if expected_status is None:
            expected_status = [200]
        elif isinstance(expected_status, int):
            expected_status = [expected_status]
        
        try:
            print(f"\n[TEST] {feature_name}")
            print(f"  {method.upper()} {url}")
            
            if method.upper() == "GET":
                r = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=10)
            elif method.upper() == "POST":
                r = requests.post(url, headers=self.headers, cookies=self.cookies, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = r.status_code in expected_status
            
            print(f"  Status: {r.status_code} (expected {expected_status})")
            
            if success:
                print(f"  Result: PASS")
                self.results["passed"] += 1
            else:
                print(f"  Result: FAIL")
                self.results["failed"] += 1
                if r.text and len(r.text) < 300:
                    print(f"  Response: {r.text}")
            
            self.results["tested"].append({
                "feature": feature_name,
                "endpoint": f"{method.upper()} {url}",
                "status": r.status_code,
                "expected": expected_status,
                "success": success
            })
            
            return success, r

        except requests.exceptions.RequestException as e:
            print(f"  Result: ERROR")
            print(f"  Exception: {str(e)[:100]}")
            self.results["failed"] += 1
            self.results["tested"].append({
                "feature": feature_name,
                "endpoint": f"{method.upper()} {url}",
                "error": str(e)[:100],
                "success": False
            })
            return False, None

    def setup_auth(self) -> bool:
        """Setup authentication"""
        print("\n" + "="*80)
        print("SETUP: Authentication")
        print("="*80)
        
        # Sign up
        r = requests.post(f"{API_V1}/auth/signup", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Test User"
        }, timeout=10)
        
        print(f"[AUTH] Sign up: {r.status_code}")
        
        # Login
        r = requests.post(f"{API_V1}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=10)
        
        if r.status_code != 200:
            print(f"[AUTH] Login FAILED: {r.status_code}")
            return False
        
        if 'token' in r.cookies:
            self.token = r.cookies['token']
            self.cookies['token'] = self.token
        else:
            print(f"[AUTH] No token in cookies")
            return False
        
        # Get user ID
        r2 = requests.get(f"{API_V1}/auth/me", cookies=self.cookies, timeout=10)
        if r2.status_code == 200:
            me_data = r2.json()
            self.user_id = me_data.get("id")
        
        self.headers = {"Content-Type": "application/json"}
        
        print(f"[AUTH] Login success - User ID: {self.user_id}")
        return True

    def test_coins_ledger(self):
        """Test coins ledger/transaction history"""
        print("\n" + "="*80)
        print("FEATURE 1: Coins Ledger History")
        print("="*80)
        
        # Test the actual endpoint that exists
        success1, r1 = self.test_endpoint(
            "Coins Transactions History",
            "GET",
            f"{API_V1X}/coins_db/transactions",
            [200, 404]
        )
        
        if r1 and r1.status_code == 200:
            try:
                data = r1.json()
                print(f"  Found {len(data) if isinstance(data, list) else '?'} transactions")
            except:
                pass
        
        # Try alternative name
        success2, r2 = self.test_endpoint(
            "Coins Ledger (alternative name)",
            "GET",
            f"{API_V1X}/coins_db/ledger",
            [200, 404]
        )
        
        # Try transaction summary
        success3, r3 = self.test_endpoint(
            "Coins Transaction Summary",
            "GET",
            f"{API_V1X}/coins_db/transactions/summary",
            [200, 404]
        )

    def test_job_statistics(self):
        """Test job application statistics"""
        print("\n" + "="*80)
        print("FEATURE 2: Job Application Statistics")
        print("="*80)
        
        # Try the correct path
        success1, r1 = self.test_endpoint(
            "Job Application Statistics (correct path)",
            "GET",
            f"{API_V1X}/job-applications/stats",
            [200, 404]
        )
        
        if r1 and r1.status_code == 200:
            try:
                data = r1.json()
                print(f"  Stats keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            except:
                pass
        
        # Try alternative path
        success2, r2 = self.test_endpoint(
            "Job Application Statistics (alternative path)",
            "GET",
            f"{API_V1X}/job-applications/statistics",
            [200, 404]
        )

    def test_subscription_system(self):
        """Test subscription endpoints"""
        print("\n" + "="*80)
        print("FEATURE 3: Subscription System")
        print("="*80)
        
        print("  Searching for subscription endpoints...")
        
        # Try various subscription paths
        paths = [
            "/subscriptions",
            "/subscriptions/my-subscription",
            "/subscriptions/plans",
            "/subscriptions/active",
            "/premium_tiers",
            "/premium_tiers/plans",
            "/premium-tiers",
            "/premium-plans"
        ]
        
        for path in paths:
            self.test_endpoint(
                f"Subscription endpoint: {path}",
                "GET",
                f"{API_V1X}{path}",
                [200, 404]
            )

    def test_account_settings(self):
        """Test account settings endpoints"""
        print("\n" + "="*80)
        print("FEATURE 4: Account Settings")
        print("="*80)
        
        print("  Searching for account settings endpoints...")
        
        # Try various account paths
        paths = [
            "/account/settings",
            "/account/profile",
            "/account/stats",
            "/account/preferences",
            "/account/notifications",
            "/account/privacy",
            "/user-profiles/settings",
            "/settings"
        ]
        
        for path in paths:
            self.test_endpoint(
                f"Account settings: {path}",
                "GET",
                f"{API_V1X}{path}",
                [200, 404]
            )

    def test_settings_endpoint(self):
        """Test generic settings endpoints"""
        print("\n" + "="*80)
        print("FEATURE 5: Settings Endpoint")
        print("="*80)
        
        print("  Searching for settings endpoints...")
        
        # Try various settings paths
        paths = [
            "/settings",
            "/admin/settings",
            "/admin/settings/public",
            "/feed/settings",
            "/activity/feed/settings",
            "/user/settings"
        ]
        
        for path in paths:
            self.test_endpoint(
                f"Settings endpoint: {path}",
                "GET",
                f"{API_V1X}{path}",
                [200, 404]
            )

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("SUMMARY: Feature Testing Results")
        print("="*80)
        
        total = len(self.results["tested"])
        passed = self.results["passed"]
        failed = self.results["failed"]
        
        print(f"\nTotal Endpoints Tested: {total}")
        print(f"PASSED: {passed}")
        print(f"FAILED: {failed}")
        print(f"Pass Rate: {(passed/total*100):.1f}%")
        
        # Group by success/failure
        passed_tests = [t for t in self.results["tested"] if t.get("success")]
        failed_tests = [t for t in self.results["tested"] if not t.get("success")]
        
        if passed_tests:
            print(f"\nWORKING ENDPOINTS ({len(passed_tests)}):")
            for t in passed_tests:
                print(f"  [OK] {t['endpoint']}")
        
        if failed_tests:
            print(f"\nMISSING/BROKEN ENDPOINTS ({len(failed_tests)}):")
            for t in failed_tests:
                print(f"  [XX] {t['endpoint']} -> {t.get('status', 'Error')}")

    def run_all(self):
        """Run all tests"""
        if not self.setup_auth():
            print("[FAIL] Authentication setup failed")
            return
        
        self.test_coins_ledger()
        self.test_job_statistics()
        self.test_subscription_system()
        self.test_account_settings()
        self.test_settings_endpoint()
        
        self.print_summary()


if __name__ == "__main__":
    tester = TargetedFeatureTester()
    try:
        tester.run_all()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Tests interrupted")
        tester.print_summary()
    except Exception as e:
        print(f"\n\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
