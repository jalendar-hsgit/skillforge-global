#!/usr/bin/env python3
"""
Comprehensive Test Suite for Skillforge Global
Tests all endpoints: Admin, Payment, Wishlist, Reviews, Search
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://localhost:8001"
API_V1 = "/api/v1"
API_V1X = "/api/v1x"

# Test accounts from seed data
TEST_ACCOUNTS = {
    "admin": {"email": "admin@skillforge.com", "password": "password123"},
    "user": {"email": "john.doe@example.com", "password": "password123"},
}

# ============================================================================
# TEST RESULT TRACKER
# ============================================================================

class TestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": {}
        }
        self.tokens = {}
    
    def log_test(self, category: str, name: str, passed: bool, 
                 response: Optional[requests.Response] = None, 
                 error: Optional[str] = None) -> None:
        """Log a single test result"""
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
            status = "✅"
        else:
            self.results["failed"] += 1
            status = "❌"
        
        if category not in self.results["tests"]:
            self.results["tests"][category] = []
        
        test_result = {
            "name": name,
            "passed": passed,
            "status": response.status_code if response else None,
            "error": error
        }
        self.results["tests"][category].append(test_result)
        
        status_text = f"{status} {name}"
        print(f"  {status_text}")
    
    def get_summary(self) -> str:
        """Get test summary"""
        total = self.results["total"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        rate = (passed / total * 100) if total > 0 else 0
        
        return f"\n{'='*80}\n" \
               f"TEST SUMMARY\n" \
               f"{'='*80}\n" \
               f"Total:  {total}\n" \
               f"Passed: {passed} ✅\n" \
               f"Failed: {failed} ❌\n" \
               f"Rate:   {rate:.1f}%\n" \
               f"{'='*80}"


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    runner = TestRunner()
    
    print("=" * 80)
    print("SKILLFORGE COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # ========== PHASE 1: CONNECTIVITY ==========
    print("\n[1/5] TESTING BACKEND CONNECTIVITY")
    print("-" * 80)
    
    try:
        resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if resp.status_code == 200:
            runner.log_test("Connectivity", "Backend Health Check", True, resp)
        else:
            runner.log_test("Connectivity", "Backend Health Check", False, resp)
    except Exception as e:
        runner.log_test("Connectivity", "Backend Health Check", False, 
                       error=str(e))
        print(f"\n❌ BACKEND NOT RUNNING!\n")
        print("   Start backend with:")
        print("   cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")
        return 1
    
    # ========== PHASE 2: AUTHENTICATION ==========
    print("\n[2/5] OBTAINING TEST TOKENS")
    print("-" * 80)
    
    for role, creds in TEST_ACCOUNTS.items():
        try:
            resp = requests.post(
                f"{BASE_URL}{API_V1}/auth/login",
                json=creds,
                timeout=5
            )
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                runner.tokens[role] = token
                runner.log_test("Auth", f"{role.title()} Login", True, resp)
            else:
                runner.log_test("Auth", f"{role.title()} Login", False, resp)
                print(f"     Error: {resp.text}")
        except Exception as e:
            runner.log_test("Auth", f"{role.title()} Login", False, error=str(e))
    
    if not runner.tokens.get("admin"):
        print("\n⚠️  Admin token required for remaining tests")
        return 1
    
    # ========== PHASE 3: ADMIN ENDPOINTS ==========
    print("\n[3/5] TESTING ADMIN MARKETPLACE ENDPOINTS")
    print("-" * 80)
    
    admin_headers = {"Authorization": f"Bearer {runner.tokens['admin']}"}
    
    admin_tests = [
        ("Get Revenue", f"{API_V1X}/admin/marketplace/revenue"),
        ("Get Revenue by Seller", f"{API_V1X}/admin/marketplace/revenue-by-seller?skip=0&limit=10"),
        ("Get Payouts", f"{API_V1X}/admin/marketplace/payouts?status=pending"),
        ("Get Refunds", f"{API_V1X}/admin/marketplace/refunds?skip=0&limit=10"),
        ("Get Analytics", f"{API_V1X}/admin/marketplace/analytics/summary?days=30"),
    ]
    
    for test_name, endpoint in admin_tests:
        try:
            resp = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=admin_headers,
                timeout=5
            )
            passed = resp.status_code == 200
            runner.log_test("Admin Endpoints", test_name, passed, resp)
            if passed:
                print(f"     ✓ Data: {str(resp.json())[:60]}...")
        except Exception as e:
            runner.log_test("Admin Endpoints", test_name, False, error=str(e))
    
    # ========== PHASE 4: PAYMENT ENDPOINTS ==========
    print("\n[4/5] TESTING PAYMENT ENDPOINTS")
    print("-" * 80)
    
    user_headers = {"Authorization": f"Bearer {runner.tokens.get('user', '')}"}
    
    payment_tests = [
        ("Check Payment Status", f"{API_V1X}/payments/status/1"),
    ]
    
    for test_name, endpoint in payment_tests:
        try:
            resp = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=user_headers,
                timeout=5
            )
            # 200 = success, 404 = order not found (both valid)
            passed = resp.status_code in [200, 404]
            runner.log_test("Payment Endpoints", test_name, passed, resp)
        except Exception as e:
            runner.log_test("Payment Endpoints", test_name, False, error=str(e))
    
    # ========== PHASE 5: NEW FEATURES ==========
    print("\n[5/5] TESTING NEW FEATURES")
    print("-" * 80)
    
    # Wishlist tests
    print("  Wishlist Tests:")
    wishlist_tests = [
        ("Get Wishlist Count", f"{API_V1X}/marketplace/wishlist/count", user_headers, 200),
        ("Get Wishlist Items", f"{API_V1X}/marketplace/wishlist?skip=0&limit=10", user_headers, 200),
    ]
    
    for test_name, endpoint, headers, expected_status in wishlist_tests:
        try:
            resp = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=5
            )
            passed = resp.status_code == expected_status
            runner.log_test("Wishlist", test_name, passed, resp)
        except Exception as e:
            runner.log_test("Wishlist", test_name, False, error=str(e))
    
    # Review tests
    print("  Review Tests:")
    review_tests = [
        ("Get Reviews List", f"{API_V1X}/marketplace/products/1/reviews?skip=0&limit=10", None, 200),
        ("Get Product Rating", f"{API_V1X}/marketplace/products/1/rating", None, 200),
    ]
    
    for test_name, endpoint, headers, expected_status in review_tests:
        try:
            resp = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers or {},
                timeout=5
            )
            passed = resp.status_code == expected_status
            runner.log_test("Reviews", test_name, passed, resp)
        except Exception as e:
            runner.log_test("Reviews", test_name, False, error=str(e))
    
    # Search tests
    print("  Search Tests:")
    search_tests = [
        ("Search Marketplace", f"{API_V1X}/search/marketplace?q=python", None, 200),
        ("Search Autocomplete", f"{API_V1X}/search/autocomplete?q=python", None, 200),
        ("Search Trending", f"{API_V1X}/search/trending", None, 200),
        ("Search Categories", f"{API_V1X}/search/categories", None, 200),
    ]
    
    for test_name, endpoint, headers, expected_status in search_tests:
        try:
            resp = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers or {},
                timeout=5
            )
            passed = resp.status_code == expected_status
            runner.log_test("Search", test_name, passed, resp)
        except Exception as e:
            runner.log_test("Search", test_name, False, error=str(e))
    
    # ========== FINAL REPORT ==========
    print(runner.get_summary())
    
    if runner.results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED!\n")
        return 0
    else:
        print(f"\n⚠️  {runner.results['failed']} TESTS FAILED\n")
        print("Failed Tests:")
        for category, tests in runner.results["tests"].items():
            for test in tests:
                if not test["passed"]:
                    print(f"  [{category}] {test['name']}")
                    if test["error"]:
                        print(f"     Error: {test['error']}")
                    if test["status"]:
                        print(f"     Status: {test['status']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
