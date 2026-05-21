"""
MASTER TEST RUNNER - Execute All Revenue Feature Tests
Generates comprehensive test report for all 5 revenue features
"""

import requests
import json
from datetime import datetime, timedelta
import sys
from typing import List, Dict, Tuple

BASE_URL = "http://localhost:8001"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Test credentials
CREDENTIALS = {
    "admin": ("admin@skillforge.com", "admin123"),
    "mentor": ("sarah.chen@example.com", "mentor123"),
    "student": ("john.doe@example.com", "student123"),
    "seller": ("jane.smith@example.com", "seller123"),
}


class APITestRunner:
    """Execute all API tests and generate report"""
    
    def __init__(self):
        self.results = {
            "mentor_sessions": [],
            "marketplace": [],
            "subscriptions": [],
            "courses": [],
            "admin_payouts": [],
        }
        self.tokens = {}
        self.test_start_time = datetime.now()
    
    def authenticate(self):
        """Get auth tokens for all roles"""
        print("\n" + "="*70)
        print("AUTHENTICATION")
        print("="*70)
        
        for role, (email, password) in CREDENTIALS.items():
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1x/auth/login",
                    json={"email": email, "password": password},
                    timeout=5
                )
                
                if response.status_code == 200:
                    self.tokens[role] = response.json()["access_token"]
                    print(f"✅ {role.upper()} authenticated")
                else:
                    print(f"❌ {role.upper()} authentication failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ {role.upper()} error: {str(e)}")
                return False
        
        return True
    
    def test_mentor_sessions(self):
        """Test all mentor sessions endpoints"""
        print("\n" + "="*70)
        print("1. MENTOR SESSIONS ($150K/mo)")
        print("="*70)
        
        student_token = self.tokens.get("student")
        mentor_token = self.tokens.get("mentor")
        
        tests = []
        
        # Test 1: List mentors
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/mentors", timeout=5)
            success = response.status_code == 200 and len(response.json()["mentors"]) >= 4
            tests.append(("List Mentors", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /mentors - {response.status_code}")
        except Exception as e:
            tests.append(("List Mentors", False, str(e)))
            print(f"❌ GET /mentors - Error: {str(e)}")
        
        # Test 2: Get mentor detail
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/mentors/1", timeout=5)
            success = response.status_code == 200 and "availability" in response.json()
            tests.append(("Mentor Detail", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /mentors/1 - {response.status_code}")
        except Exception as e:
            tests.append(("Mentor Detail", False, str(e)))
            print(f"❌ GET /mentors/1 - Error: {str(e)}")
        
        # Test 3: Get availability
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/mentors/1/availability", timeout=5)
            success = response.status_code == 200 and len(response.json()["slots"]) > 0
            tests.append(("Mentor Availability", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /mentors/1/availability - {response.status_code}")
        except Exception as e:
            tests.append(("Mentor Availability", False, str(e)))
            print(f"❌ GET /mentors/1/availability - Error: {str(e)}")
        
        # Test 4: Create session
        if student_token:
            try:
                future_date = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
                response = requests.post(
                    f"{BASE_URL}/api/v1x/mentors/sessions",
                    json={
                        "mentor_id": 1,
                        "topic": "Test Session",
                        "scheduled_at": future_date,
                        "duration_minutes": 60
                    },
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code in [201, 200]
                tests.append(("Create Session", success, response.status_code))
                print(f"{'✅' if success else '❌'} POST /mentors/sessions - {response.status_code}")
            except Exception as e:
                tests.append(("Create Session", False, str(e)))
                print(f"❌ POST /mentors/sessions - Error: {str(e)}")
        
        # Test 5: Get my sessions
        if student_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/mentors/sessions/my",
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "upcoming" in response.json()
                tests.append(("Get My Sessions", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /mentors/sessions/my - {response.status_code}")
            except Exception as e:
                tests.append(("Get My Sessions", False, str(e)))
                print(f"❌ GET /mentors/sessions/my - Error: {str(e)}")
        
        # Test 6: Mentor payout summary
        if mentor_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/mentors/payouts/summary",
                    headers={"Authorization": f"Bearer {mentor_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "total_earned" in response.json()
                tests.append(("Payout Summary", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /mentors/payouts/summary - {response.status_code}")
            except Exception as e:
                tests.append(("Payout Summary", False, str(e)))
                print(f"❌ GET /mentors/payouts/summary - Error: {str(e)}")
        
        self.results["mentor_sessions"] = tests
        return tests
    
    def test_marketplace(self):
        """Test all marketplace endpoints"""
        print("\n" + "="*70)
        print("2. DIGITAL MARKETPLACE ($100K/mo)")
        print("="*70)
        
        student_token = self.tokens.get("student")
        
        tests = []
        
        # Test 1: List products
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/marketplace/digital-products", timeout=5)
            success = response.status_code == 200 and len(response.json()["products"]) >= 3
            tests.append(("List Products", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /marketplace/digital-products - {response.status_code}")
        except Exception as e:
            tests.append(("List Products", False, str(e)))
            print(f"❌ GET /marketplace/digital-products - Error: {str(e)}")
        
        # Test 2: Get product detail
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/marketplace/digital-products/1", timeout=5)
            success = response.status_code == 200 and "description" in response.json()
            tests.append(("Product Detail", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /marketplace/digital-products/1 - {response.status_code}")
        except Exception as e:
            tests.append(("Product Detail", False, str(e)))
            print(f"❌ GET /marketplace/digital-products/1 - Error: {str(e)}")
        
        # Test 3: Get cart
        if student_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/marketplace/cart",
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "items" in response.json()
                tests.append(("Get Cart", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /marketplace/cart - {response.status_code}")
            except Exception as e:
                tests.append(("Get Cart", False, str(e)))
                print(f"❌ GET /marketplace/cart - Error: {str(e)}")
        
        # Test 4: Add to cart
        if student_token:
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1x/marketplace/cart/add",
                    json={"product_id": 1},
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code == 200
                tests.append(("Add to Cart", success, response.status_code))
                print(f"{'✅' if success else '❌'} POST /marketplace/cart/add - {response.status_code}")
            except Exception as e:
                tests.append(("Add to Cart", False, str(e)))
                print(f"❌ POST /marketplace/cart/add - Error: {str(e)}")
        
        # Test 5: Seller dashboard
        seller_token = self.tokens.get("seller")
        if seller_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/seller/dashboard",
                    headers={"Authorization": f"Bearer {seller_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "total_revenue" in response.json()
                tests.append(("Seller Dashboard", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /seller/dashboard - {response.status_code}")
            except Exception as e:
                tests.append(("Seller Dashboard", False, str(e)))
                print(f"❌ GET /seller/dashboard - Error: {str(e)}")
        
        self.results["marketplace"] = tests
        return tests
    
    def test_subscriptions(self):
        """Test all subscription endpoints"""
        print("\n" + "="*70)
        print("3. SUBSCRIPTIONS ($200K/mo)")
        print("="*70)
        
        student_token = self.tokens.get("student")
        
        tests = []
        
        # Test 1: Get plans
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/subscriptions/plans", timeout=5)
            success = response.status_code == 200 and len(response.json()["plans"]) >= 3
            tests.append(("Get Plans", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /subscriptions/plans - {response.status_code}")
        except Exception as e:
            tests.append(("Get Plans", False, str(e)))
            print(f"❌ GET /subscriptions/plans - Error: {str(e)}")
        
        # Test 2: Current subscription
        if student_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/subscriptions/current",
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "plan" in response.json()
                tests.append(("Current Subscription", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /subscriptions/current - {response.status_code}")
            except Exception as e:
                tests.append(("Current Subscription", False, str(e)))
                print(f"❌ GET /subscriptions/current - Error: {str(e)}")
        
        # Test 3: Features access
        if student_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/subscriptions/features",
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "features" in response.json()
                tests.append(("Features Access", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /subscriptions/features - {response.status_code}")
            except Exception as e:
                tests.append(("Features Access", False, str(e)))
                print(f"❌ GET /subscriptions/features - Error: {str(e)}")
        
        self.results["subscriptions"] = tests
        return tests
    
    def test_courses(self):
        """Test all course endpoints"""
        print("\n" + "="*70)
        print("4. COURSE ENROLLMENT ($50K/mo)")
        print("="*70)
        
        student_token = self.tokens.get("student")
        
        tests = []
        
        # Test 1: List courses
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/courses", timeout=5)
            success = response.status_code == 200 and len(response.json()["courses"]) >= 5
            tests.append(("List Courses", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /courses - {response.status_code}")
        except Exception as e:
            tests.append(("List Courses", False, str(e)))
            print(f"❌ GET /courses - Error: {str(e)}")
        
        # Test 2: Get course detail
        try:
            response = requests.get(f"{BASE_URL}/api/v1x/courses/1", timeout=5)
            success = response.status_code == 200 and "lessons" in response.json()
            tests.append(("Course Detail", success, response.status_code))
            print(f"{'✅' if success else '❌'} GET /courses/1 - {response.status_code}")
        except Exception as e:
            tests.append(("Course Detail", False, str(e)))
            print(f"❌ GET /courses/1 - Error: {str(e)}")
        
        # Test 3: Enroll in course
        if student_token:
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1x/courses/1/enroll",
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code in [201, 409]  # 409 if already enrolled
                tests.append(("Enroll in Course", success, response.status_code))
                print(f"{'✅' if success else '❌'} POST /courses/1/enroll - {response.status_code}")
            except Exception as e:
                tests.append(("Enroll in Course", False, str(e)))
                print(f"❌ POST /courses/1/enroll - Error: {str(e)}")
        
        # Test 4: Get progress
        if student_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/courses/1/progress",
                    headers={"Authorization": f"Bearer {student_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "completion_percentage" in response.json()
                tests.append(("Get Progress", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /courses/1/progress - {response.status_code}")
            except Exception as e:
                tests.append(("Get Progress", False, str(e)))
                print(f"❌ GET /courses/1/progress - Error: {str(e)}")
        
        self.results["courses"] = tests
        return tests
    
    def test_admin_payouts(self):
        """Test all admin payout endpoints"""
        print("\n" + "="*70)
        print("5. ADMIN PAYOUTS (Revenue Processing)")
        print("="*70)
        
        admin_token = self.tokens.get("admin")
        
        tests = []
        
        # Test 1: Payout stats
        if admin_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/admin/payouts/stats",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "total_pending" in response.json()
                tests.append(("Payout Stats", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /admin/payouts/stats - {response.status_code}")
            except Exception as e:
                tests.append(("Payout Stats", False, str(e)))
                print(f"❌ GET /admin/payouts/stats - Error: {str(e)}")
        
        # Test 2: Get pending payouts
        if admin_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/admin/payouts/pending",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "payouts" in response.json()
                tests.append(("Pending Payouts", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /admin/payouts/pending - {response.status_code}")
            except Exception as e:
                tests.append(("Pending Payouts", False, str(e)))
                print(f"❌ GET /admin/payouts/pending - Error: {str(e)}")
        
        # Test 3: Get unverified payment methods
        if admin_token:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/v1x/admin/payouts/payment-methods/unverified",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    timeout=5
                )
                success = response.status_code == 200 and "methods" in response.json()
                tests.append(("Unverified Methods", success, response.status_code))
                print(f"{'✅' if success else '❌'} GET /admin/payouts/payment-methods/unverified - {response.status_code}")
            except Exception as e:
                tests.append(("Unverified Methods", False, str(e)))
                print(f"❌ GET /admin/payouts/payment-methods/unverified - Error: {str(e)}")
        
        self.results["admin_payouts"] = tests
        return tests
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("TEST EXECUTION SUMMARY")
        print("="*70 + "\n")
        
        all_tests = []
        for feature, tests in self.results.items():
            all_tests.extend(tests)
        
        passed = sum(1 for _, success, _ in all_tests if success)
        failed = len(all_tests) - passed
        success_rate = (passed / len(all_tests) * 100) if all_tests else 0
        
        print(f"Total Tests: {len(all_tests)}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        execution_time = (datetime.now() - self.test_start_time).total_seconds()
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        print("\n" + "="*70)
        print("FEATURE BREAKDOWN")
        print("="*70 + "\n")
        
        for feature, tests in self.results.items():
            passed_feature = sum(1 for _, success, _ in tests if success)
            total_feature = len(tests)
            rate = (passed_feature / total_feature * 100) if total_feature > 0 else 0
            
            feature_name = feature.replace("_", " ").title()
            print(f"{feature_name}: {passed_feature}/{total_feature} passed ({rate:.0f}%)")
        
        return {
            "total": len(all_tests),
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "execution_time": execution_time,
            "timestamp": TIMESTAMP,
            "results": self.results
        }


def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("SKILLFORGE GLOBAL - COMPLETE FEATURE TEST SUITE")
    print("="*70)
    print(f"Timestamp: {TIMESTAMP}")
    print(f"API Base URL: {BASE_URL}\n")
    
    runner = APITestRunner()
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ API is running\n")
    except Exception as e:
        print(f"❌ API not responding: {str(e)}")
        print(f"   Make sure backend is running on {BASE_URL}")
        return
    
    # Authenticate
    if not runner.authenticate():
        print("\n❌ Authentication failed!")
        return
    
    # Run all tests
    runner.test_mentor_sessions()
    runner.test_marketplace()
    runner.test_subscriptions()
    runner.test_courses()
    runner.test_admin_payouts()
    
    # Generate report
    report = runner.generate_report()
    
    # Save report to file
    report_file = "TEST_EXECUTION_REPORT.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ Report saved to {report_file}")


if __name__ == "__main__":
    main()
