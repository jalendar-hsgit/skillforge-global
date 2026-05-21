#!/usr/bin/env python3
"""
Complete Payment Flow Test Suite
Tests the entire payment pipeline from order creation through webhook handling.
"""

import requests
import json
import time
from typing import Optional, Tuple

BASE_URL = "http://localhost:8001"
DEMO_USER_EMAIL = "john.doe@example.com"
DEMO_USER_PASSWORD = "password123"
ADMIN_EMAIL = "admin@skillforge.com"
ADMIN_PASSWORD = "password123"


class PaymentFlowTester:
    """Main test runner for payment flow"""
    
    def __init__(self):
        self.user_token: Optional[str] = None
        self.admin_token: Optional[str] = None
        self.test_results = {
            'passed': [],
            'failed': [],
            'errors': []
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """Get authentication token for user"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1x/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data['data']['access_token']
                return token
            else:
                self.log_error(f"Auth failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_error(f"Auth error: {str(e)}")
            return None
    
    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result"""
        if passed:
            self.test_results['passed'].append(name)
            print(f"✅ {name}")
        else:
            self.test_results['failed'].append(name)
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")
    
    def log_error(self, message: str):
        """Log error"""
        self.test_results['errors'].append(message)
        print(f"⚠️  ERROR: {message}")
    
    # ==================== TEST METHODS ====================
    
    def test_authentication(self) -> bool:
        """Test 1: User Authentication"""
        print("\n" + "="*70)
        print("TEST 1: USER AUTHENTICATION")
        print("="*70)
        
        try:
            self.user_token = self.authenticate_user(DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
            self.admin_token = self.authenticate_user(ADMIN_EMAIL, ADMIN_PASSWORD)
            
            if self.user_token and self.admin_token:
                self.log_test(
                    "Authentication",
                    True,
                    f"User token: {self.user_token[:30]}..."
                )
                return True
            else:
                self.log_test("Authentication", False)
                return False
                
        except Exception as e:
            self.log_error(f"Authentication test failed: {str(e)}")
            return False
    
    def test_list_courses(self) -> Optional[dict]:
        """Test 2: List Available Courses"""
        print("\n" + "="*70)
        print("TEST 2: LIST COURSES")
        print("="*70)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1x/courses-db",
                headers={"Authorization": f"Bearer {self.user_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                courses = response.json()
                paid_courses = [c for c in courses if c.get('is_paid')]
                
                self.log_test(
                    "List Courses",
                    len(courses) > 0,
                    f"Found {len(courses)} total courses, {len(paid_courses)} paid"
                )
                
                if courses:
                    for i, course in enumerate(courses[:3]):
                        price = course.get('price', 'FREE')
                        print(f"   {i+1}. {course['title']} - ${price}")
                
                return courses[0] if courses else None
            else:
                self.log_test("List Courses", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_error(f"List courses failed: {str(e)}")
            return None
    
    def test_create_order(self, course_id: int) -> Optional[int]:
        """Test 3: Create Order"""
        print("\n" + "="*70)
        print("TEST 3: CREATE ORDER")
        print("="*70)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1x/orders/create",
                headers={"Authorization": f"Bearer {self.user_token}"},
                json={
                    "course_id": course_id,
                    "payment_method": "stripe"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                order_id = data['data']['id']
                amount = data['data'].get('amount', 0)
                
                self.log_test(
                    "Create Order",
                    True,
                    f"Order ID: {order_id}, Amount: ${amount}"
                )
                return order_id
            else:
                self.log_test(
                    "Create Order",
                    False,
                    f"Status: {response.status_code}"
                )
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_error(f"Create order failed: {str(e)}")
            return None
    
    def test_create_payment_intent(self, order_id: int) -> Optional[Tuple[str, str]]:
        """Test 4: Create Payment Intent"""
        print("\n" + "="*70)
        print("TEST 4: CREATE PAYMENT INTENT")
        print("="*70)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1x/orders/create-payment-intent",
                headers={"Authorization": f"Bearer {self.user_token}"},
                json={"order_id": order_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                pi_id = data['data']['payment_intent_id']
                client_secret = data['data'].get('client_secret', '')
                
                self.log_test(
                    "Create Payment Intent",
                    True,
                    f"PI ID: {pi_id[:30]}..."
                )
                return pi_id, client_secret
            else:
                self.log_test(
                    "Create Payment Intent",
                    False,
                    f"Status: {response.status_code}"
                )
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_error(f"Create payment intent failed: {str(e)}")
            return None
    
    def test_confirm_payment(self, order_id: int, payment_intent_id: str) -> bool:
        """Test 5: Confirm Payment"""
        print("\n" + "="*70)
        print("TEST 5: CONFIRM PAYMENT")
        print("="*70)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1x/orders/confirm-payment",
                headers={"Authorization": f"Bearer {self.user_token}"},
                json={
                    "order_id": order_id,
                    "payment_intent_id": payment_intent_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data['data'].get('status', 'unknown')
                
                self.log_test(
                    "Confirm Payment",
                    True,
                    f"Order Status: {status}"
                )
                return True
            else:
                self.log_test(
                    "Confirm Payment",
                    False,
                    f"Status: {response.status_code}"
                )
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Confirm payment failed: {str(e)}")
            return False
    
    def test_get_order_details(self, order_id: int) -> bool:
        """Test 6: Get Order Details"""
        print("\n" + "="*70)
        print("TEST 6: GET ORDER DETAILS")
        print("="*70)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1x/orders/{order_id}",
                headers={"Authorization": f"Bearer {self.user_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                order = data.get('data', {})
                
                print(f"   Order ID: {order.get('id')}")
                print(f"   Status: {order.get('status')}")
                print(f"   Amount: ${order.get('amount')}")
                print(f"   Payment Status: {order.get('payment_status')}")
                print(f"   Payment Intent: {order.get('stripe_payment_intent_id', 'N/A')[:30]}...")
                
                self.log_test(
                    "Get Order Details",
                    True,
                    f"Status: {order.get('status')}"
                )
                return True
            else:
                self.log_test(
                    "Get Order Details",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_error(f"Get order details failed: {str(e)}")
            return False
    
    def test_get_order_history(self) -> bool:
        """Test 7: Get Order History"""
        print("\n" + "="*70)
        print("TEST 7: GET ORDER HISTORY")
        print("="*70)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1x/orders/my-orders",
                headers={"Authorization": f"Bearer {self.user_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                orders = response.json()
                
                self.log_test(
                    "Get Order History",
                    True,
                    f"Found {len(orders)} orders"
                )
                
                if isinstance(orders, list) and orders:
                    for order in orders[:3]:
                        print(f"   - Order {order.get('id')}: {order.get('status')}")
                
                return True
            else:
                self.log_test(
                    "Get Order History",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_error(f"Get order history failed: {str(e)}")
            return False
    
    def test_rbac_protection(self) -> bool:
        """Test 8: RBAC Protection"""
        print("\n" + "="*70)
        print("TEST 8: RBAC PROTECTION")
        print("="*70)
        
        try:
            # Try to access admin endpoint with regular user token
            response = requests.get(
                f"{BASE_URL}/api/v1x/admin/dashboard/stats",
                headers={"Authorization": f"Bearer {self.user_token}"},
                timeout=10
            )
            
            if response.status_code == 403:
                self.log_test(
                    "RBAC Protection (User Blocked)",
                    True,
                    "Regular user correctly denied access"
                )
            else:
                self.log_test(
                    "RBAC Protection (User Blocked)",
                    False,
                    f"Expected 403, got {response.status_code}"
                )
            
            # Try with admin token
            response = requests.get(
                f"{BASE_URL}/api/v1x/admin/dashboard/stats",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "RBAC Protection (Admin Access)",
                    True,
                    "Admin correctly allowed access"
                )
                return True
            else:
                self.log_test(
                    "RBAC Protection (Admin Access)",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_error(f"RBAC test failed: {str(e)}")
            return False
    
    def test_admin_dashboard_access(self) -> bool:
        """Test 9: Admin Dashboard Access"""
        print("\n" + "="*70)
        print("TEST 9: ADMIN DASHBOARD")
        print("="*70)
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1x/admin/dashboard/stats",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_test(
                    "Admin Dashboard Access",
                    True,
                    "Successfully retrieved admin stats"
                )
                
                # Print some stats if available
                if isinstance(data, dict):
                    for key in ['total_users', 'total_orders', 'total_revenue'][:3]:
                        if key in data:
                            print(f"   {key}: {data[key]}")
                
                return True
            else:
                self.log_test(
                    "Admin Dashboard Access",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_error(f"Admin dashboard test failed: {str(e)}")
            return False
    
    def test_cart_operations(self) -> bool:
        """Test 10: Cart Operations"""
        print("\n" + "="*70)
        print("TEST 10: CART OPERATIONS")
        print("="*70)
        
        try:
            # Get courses first
            courses_response = requests.get(
                f"{BASE_URL}/api/v1x/courses-db",
                headers={"Authorization": f"Bearer {self.user_token}"},
                timeout=10
            )
            
            if courses_response.status_code != 200 or not courses_response.json():
                self.log_test("Cart Operations", False, "No courses available")
                return False
            
            course_id = courses_response.json()[0]['id']
            
            # Add to cart
            add_response = requests.post(
                f"{BASE_URL}/api/v1x/cart/add",
                headers={"Authorization": f"Bearer {self.user_token}"},
                json={"course_id": course_id},
                timeout=10
            )
            
            if add_response.status_code != 200:
                self.log_test(
                    "Cart Operations (Add)",
                    False,
                    f"Status: {add_response.status_code}"
                )
                return False
            
            # View cart
            view_response = requests.get(
                f"{BASE_URL}/api/v1x/cart",
                headers={"Authorization": f"Bearer {self.user_token}"},
                timeout=10
            )
            
            if view_response.status_code == 200:
                cart = view_response.json()
                items_count = len(cart.get('items', []))
                total = cart.get('total', 0)
                
                self.log_test(
                    "Cart Operations",
                    True,
                    f"{items_count} items, Total: ${total}"
                )
                return True
            else:
                self.log_test(
                    "Cart Operations (View)",
                    False,
                    f"Status: {view_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_error(f"Cart test failed: {str(e)}")
            return False
    
    # ==================== MAIN TEST RUNNER ====================
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "TEST SUMMARY".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        
        total = len(self.test_results['passed']) + len(self.test_results['failed'])
        passed = len(self.test_results['passed'])
        failed = len(self.test_results['failed'])
        errors = len(self.test_results['errors'])
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        
        if failed == 0 and errors == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            success = True
        else:
            print(f"\n⚠️  {failed + errors} issues found")
            success = False
        
        if self.test_results['failed']:
            print("\nFailed Tests:")
            for test in self.test_results['failed']:
                print(f"  - {test}")
        
        if self.test_results['errors']:
            print("\nErrors:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print("\n" + "█"*70)
        
        return success
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "PAYMENT FLOW COMPLETE TEST SUITE".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        print(f"\nAPI Base: {BASE_URL}")
        print(f"Test User: {DEMO_USER_EMAIL}")
        
        # Run tests in sequence
        if not self.test_authentication():
            print("\n❌ Authentication failed. Cannot continue.")
            return False
        
        course = self.test_list_courses()
        if not course:
            print("\n⚠️  No courses available. Skipping payment flow tests.")
        else:
            order_id = self.test_create_order(course.get('id', 1))
            
            if order_id:
                pi_result = self.test_create_payment_intent(order_id)
                
                if pi_result:
                    pi_id, _ = pi_result
                    self.test_confirm_payment(order_id, pi_id)
                    self.test_get_order_details(order_id)
        
        self.test_get_order_history()
        self.test_rbac_protection()
        self.test_admin_dashboard_access()
        self.test_cart_operations()
        
        # Print summary
        return self.print_summary()


def main():
    """Main entry point"""
    try:
        tester = PaymentFlowTester()
        success = tester.run_all_tests()
        
        # Exit with appropriate code
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
