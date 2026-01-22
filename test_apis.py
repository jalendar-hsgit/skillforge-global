#!/usr/bin/env python3
"""
Comprehensive API Test Script for SkillForge Mentor Payouts
Tests authentication, mentor payouts, and admin workflows
"""

import requests
import json
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8001"
API_V1X = f"{BASE_URL}/api/v1x"

# Test accounts
MENTOR_ACCOUNT = {
    "email": "sarah.chen@example.com",
    "password": "password123"
}

ADMIN_ACCOUNT = {
    "email": "admin@skillforge.com",
    "password": "password123"
}

STUDENT_ACCOUNT = {
    "email": "john.doe@example.com",
    "password": "password123"
}

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.mentor_session = requests.Session()
        self.admin_session = requests.Session()
        self.student_session = requests.Session()
        self.mentor_token = None
        self.admin_token = None
        self.results = []
        
    def log(self, message: str, status: str = "INFO"):
        """Log test results"""
        print(f"[{status}] {message}")
        self.results.append({"message": message, "status": status})
    
    def test_auth(self) -> bool:
        """Test authentication with mentor and admin accounts"""
        self.log("\n" + "="*60)
        self.log("TESTING AUTHENTICATION", "TEST")
        self.log("="*60, "TEST")
        
        # Test mentor login
        try:
            response = self.mentor_session.post(
                f"{API_V1X}/auth/login",
                json=MENTOR_ACCOUNT,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.mentor_token = data["access_token"]
                    self.mentor_session.headers.update({
                        "Authorization": f"Bearer {self.mentor_token}"
                    })
                    self.log(f"✅ Mentor login successful", "PASS")
                    self.log(f"   Token: {self.mentor_token[:20]}...", "INFO")
                    return True
                else:
                    self.log(f"❌ No token in response: {data}", "FAIL")
                    return False
            else:
                self.log(f"❌ Mentor login failed: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Auth error: {str(e)}", "FAIL")
            return False

    def test_admin_auth(self) -> bool:
        """Test admin authentication"""
        try:
            response = self.admin_session.post(
                f"{API_V1X}/auth/login",
                json=ADMIN_ACCOUNT,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.admin_token = data["access_token"]
                    self.admin_session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    self.log(f"✅ Admin login successful", "PASS")
                    return True
                else:
                    self.log(f"❌ No admin token in response", "FAIL")
                    return False
            else:
                self.log(f"❌ Admin login failed: {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ Admin auth error: {str(e)}", "FAIL")
            return False

    def test_mentor_payouts(self):
        """Test mentor payout endpoints"""
        self.log("\n" + "="*60)
        self.log("TESTING MENTOR PAYOUT ENDPOINTS", "TEST")
        self.log("="*60, "TEST")
        
        # Test 1: Get earnings summary
        try:
            response = self.mentor_session.get(f"{API_V1X}/mentors/payouts/summary")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ GET /mentors/payouts/summary - {response.status_code}", "PASS")
                self.log(f"   Total Earned: ${data.get('total_earned', 0)}", "INFO")
                self.log(f"   Available Payout: ${data.get('available_payout', 0)}", "INFO")
                return True
            else:
                self.log(f"❌ GET /mentors/payouts/summary - {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ GET summary error: {str(e)}", "FAIL")
            return False

    def test_payment_methods(self):
        """Test payment method CRUD operations"""
        self.log("\n" + "="*60)
        self.log("TESTING PAYMENT METHODS", "TEST")
        self.log("="*60, "TEST")
        
        # Create payment method
        payment_method = {
            "bank_name": "Test Bank",
            "account_holder_name": "Sarah Chen",
            "account_number": "1234567890",
            "routing_number": "123456789",
            "account_type": "checking",
            "is_primary": True
        }
        
        method_id = None
        
        try:
            response = self.mentor_session.post(
                f"{API_V1X}/mentors/payouts/payment-methods",
                json=payment_method
            )
            if response.status_code in [200, 201]:
                data = response.json()
                method_id = data.get('id')
                self.log(f"✅ POST /payment-methods - {response.status_code}", "PASS")
                self.log(f"   Method ID: {method_id}", "INFO")
            else:
                self.log(f"❌ POST /payment-methods - {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ POST payment method error: {str(e)}", "FAIL")
            return False
        
        # Get payment methods
        try:
            response = self.mentor_session.get(
                f"{API_V1X}/mentors/payouts/payment-methods"
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ GET /payment-methods - {response.status_code}", "PASS")
                self.log(f"   Count: {len(data)}", "INFO")
                return True
            else:
                self.log(f"❌ GET /payment-methods - {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ GET payment methods error: {str(e)}", "FAIL")
            return False

    def test_payout_requests(self):
        """Test payout request creation"""
        self.log("\n" + "="*60)
        self.log("TESTING PAYOUT REQUESTS", "TEST")
        self.log("="*60, "TEST")
        
        # Create payout request
        payout_request = {
            "amount": 150.00,
            "payment_method_id": 1  # Assuming ID 1 exists from previous test
        }
        
        try:
            response = self.mentor_session.post(
                f"{API_V1X}/mentors/payouts/request",
                json=payout_request
            )
            if response.status_code in [200, 201]:
                data = response.json()
                self.log(f"✅ POST /request - {response.status_code}", "PASS")
                self.log(f"   Request created with status: {data.get('status')}", "INFO")
                return True
            else:
                self.log(f"❌ POST /request - {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ POST payout request error: {str(e)}", "FAIL")
            return False

    def test_admin_payouts(self):
        """Test admin payout management endpoints"""
        self.log("\n" + "="*60)
        self.log("TESTING ADMIN PAYOUT ENDPOINTS", "TEST")
        self.log("="*60, "TEST")
        
        # Test 1: Get pending payout requests
        try:
            response = self.admin_session.get(
                f"{API_V1X}/admin/payouts/pending"
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ GET /admin/payouts/pending - {response.status_code}", "PASS")
                self.log(f"   Pending requests: {len(data)}", "INFO")
                return len(data) >= 0
            else:
                self.log(f"❌ GET /admin/payouts/pending - {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ GET pending error: {str(e)}", "FAIL")
            return False

    def test_admin_stats(self):
        """Test admin statistics endpoint"""
        self.log("\n" + "="*60)
        self.log("TESTING ADMIN STATISTICS", "TEST")
        self.log("="*60, "TEST")
        
        try:
            response = self.admin_session.get(
                f"{API_V1X}/admin/payouts/stats"
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ GET /admin/payouts/stats - {response.status_code}", "PASS")
                self.log(f"   Total pending: ${data.get('total_pending', 0)}", "INFO")
                self.log(f"   Total completed: ${data.get('total_completed', 0)}", "INFO")
                self.log(f"   Total mentors: {data.get('total_mentors', 0)}", "INFO")
                return True
            else:
                self.log(f"❌ GET /admin/payouts/stats - {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ GET stats error: {str(e)}", "FAIL")
            return False

    def test_mentor_endpoints(self):
        """Test general mentor endpoints"""
        self.log("\n" + "="*60)
        self.log("TESTING MENTOR ENDPOINTS", "TEST")
        self.log("="*60, "TEST")
        
        try:
            response = self.mentor_session.get(f"{API_V1X}/mentors")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ GET /mentors - {response.status_code}", "PASS")
                self.log(f"   Response data type: {type(data).__name__}", "INFO")
                return True
            else:
                self.log(f"❌ GET /mentors - {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"❌ GET mentors error: {str(e)}", "FAIL")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        self.log("\n" + "#"*60)
        self.log("SKILLFORGE MENTOR PAYOUTS - API TEST SUITE", "TEST")
        self.log("#"*60, "TEST")
        
        # Authentication
        if not self.test_auth():
            self.log("\n❌ AUTHENTICATION FAILED - Cannot continue tests", "FAIL")
            return
        
        if not self.test_admin_auth():
            self.log("\n⚠️ Admin authentication failed - skipping admin tests", "WARN")
        
        # Mentor endpoints
        self.test_mentor_payouts()
        self.test_payment_methods()
        self.test_payout_requests()
        
        # Admin endpoints
        if self.admin_token:
            self.test_admin_payouts()
            self.test_admin_stats()
        
        self.test_mentor_endpoints()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "#"*60)
        self.log("TEST SUMMARY", "SUMMARY")
        self.log("#"*60, "SUMMARY")
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        total = passed + failed
        
        self.log(f"Total Tests: {total}", "SUMMARY")
        self.log(f"Passed: {passed} ✅", "SUMMARY")
        self.log(f"Failed: {failed} ❌", "SUMMARY")
        
        if failed == 0 and passed > 0:
            self.log(f"\n🎉 ALL TESTS PASSED! 🎉", "SUMMARY")
        else:
            self.log(f"\n⚠️ Some tests failed", "SUMMARY")


if __name__ == "__main__":
    print("\nStarting API tests...")
    print(f"Backend URL: {BASE_URL}")
    
    tester = APITester(API_V1X)
    tester.run_all_tests()
