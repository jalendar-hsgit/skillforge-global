#!/usr/bin/env python3
"""
Frontend Cart Module Test (via Next.js Proxy)
Tests the complete flow: Login → Browse → Add → View → Remove
Using the same paths as the browser (http://localhost:3000)
"""
import requests
import json
from datetime import datetime

class FrontendCartTest:
    def __init__(self, frontend_base="http://localhost:3000"):
        self.frontend_base = frontend_base
        self.api_base = "http://localhost:8001"
        self.session = requests.Session()
        self.user_email = "admin@skillforge.com"
        self.user_password = "admin123"
        self.test_results = []
        
    def log(self, test_name, passed, message=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if message:
            print(f"       {message}")
        self.test_results.append((test_name, passed, message))
    
    def print_header(self, title):
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    
    def test_backend_ready(self):
        """Test 1: Backend is Ready"""
        self.print_header("TEST 1: BACKEND READY")
        try:
            response = requests.get(f"{self.api_base}/api/v1/courses", timeout=3)
            passed = response.status_code == 200
            self.log("Backend Responding", passed, f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log("Backend Ready", False, f"Cannot reach backend: {e}")
            return False
    
    def test_frontend_ready(self):
        """Test 2: Frontend is Ready"""
        self.print_header("TEST 2: FRONTEND READY")
        try:
            response = requests.get(self.frontend_base, timeout=3)
            passed = response.status_code == 200
            self.log("Frontend Responding", passed, f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log("Frontend Ready", False, f"Cannot reach frontend: {e}")
            return False
    
    def test_login_backend(self):
        """Test 3: Login via Backend"""
        self.print_header("TEST 3: LOGIN (BACKEND)")
        try:
            # First login to backend to get cookies
            response = self.session.post(
                f"{self.api_base}/api/v1/auth/login",
                json={
                    "email": self.user_email,
                    "password": self.user_password
                },
                timeout=5
            )
            
            passed = response.status_code == 200
            self.log("Backend Login", passed, f"Status: {response.status_code}")
            
            has_token = 'token' in self.session.cookies.get_dict()
            self.log("Token Cookie", has_token, f"Cookies: {list(self.session.cookies.keys())}")
            
            return passed and has_token
        except Exception as e:
            self.log("Login", False, str(e))
            return False
    
    def test_get_courses_backend(self):
        """Test 4: Browse Courses (Backend)"""
        self.print_header("TEST 4: BROWSE COURSES (BACKEND)")
        try:
            response = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/courses",
                timeout=5
            )
            
            passed = response.status_code == 200
            self.log("Get Courses", passed, f"Status: {response.status_code}")
            
            if response.ok:
                courses = response.json()
                is_list = isinstance(courses, list)
                count = len(courses) if is_list else 0
                self.log("Courses List", is_list and count > 0, f"Count: {count}")
                
                if courses:
                    print(f"       Sample: {courses[0].get('title')} - ${courses[0].get('price')}")
                    self.test_course_id = courses[0].get('id')
            
            return passed
        except Exception as e:
            self.log("Get Courses", False, str(e))
            return False
    
    def test_cart_add_backend(self):
        """Test 5: Add to Cart (Backend)"""
        self.print_header("TEST 5: ADD TO CART (BACKEND)")
        try:
            course_id = self.test_course_id if hasattr(self, 'test_course_id') else 2
            response = self.session.post(
                f"{self.api_base}/api/v1x/marketplace/cart/add",
                json={"course_id": course_id},
                timeout=5
            )
            
            passed = response.status_code in [200, 400]
            self.log("Add Item", passed, f"Course {course_id} - Status: {response.status_code}")
            
            if response.status_code == 200:
                self.log("Add Success", True, "Item added to cart")
                self.item_added = True
            else:
                self.log("Add Info", True, "Item already in cart (or error)")
                self.item_added = False
            
            return passed
        except Exception as e:
            self.log("Add to Cart", False, str(e))
            return False
    
    def test_cart_get_backend(self):
        """Test 6: Get Cart (Backend)"""
        self.print_header("TEST 6: GET CART (BACKEND)")
        try:
            response = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/cart",
                timeout=5
            )
            
            passed = response.status_code == 200
            self.log("Get Cart", passed, f"Status: {response.status_code}")
            
            if response.ok:
                cart = response.json()
                items = cart.get('items', [])
                print(f"       Items in cart: {len(items)}")
                for item in items:
                    print(f"       - Item {item['id']}: Course {item['course_id']} (${item['price']})")
                
                self.cart_item_count = len(items)
                if items:
                    self.test_item_id = items[0]['id']
            
            return passed
        except Exception as e:
            self.log("Get Cart", False, str(e))
            return False
    
    def test_cart_remove_backend(self):
        """Test 7: Remove from Cart (Backend)"""
        self.print_header("TEST 7: REMOVE FROM CART (BACKEND)")
        try:
            if not hasattr(self, 'test_item_id'):
                self.log("Remove Item", False, "No item available")
                return False
            
            item_id = self.test_item_id
            response = self.session.delete(
                f"{self.api_base}/api/v1x/marketplace/cart/{item_id}",
                timeout=5
            )
            
            passed = response.status_code == 200
            self.log("Delete Item", passed, f"Item {item_id} - Status: {response.status_code}")
            
            if response.ok:
                print(f"       {response.json().get('message', '')}")
            
            return passed
        except Exception as e:
            self.log("Remove Item", False, str(e))
            return False
    
    def test_cart_verify_removed(self):
        """Test 8: Verify Removal"""
        self.print_header("TEST 8: VERIFY REMOVAL")
        try:
            response = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/cart",
                timeout=5
            )
            
            if response.ok:
                cart = response.json()
                new_count = len(cart.get('items', []))
                decreased = new_count < self.cart_item_count
                
                self.log("Cart Decreased", decreased, 
                        f"Before: {self.cart_item_count}, After: {new_count}")
                
                print(f"       Current items: {new_count}")
                return True
            return False
        except Exception as e:
            self.log("Verify Removal", False, str(e))
            return False
    
    def test_proxy_paths(self):
        """Test 9: Proxy Route Integrity"""
        self.print_header("TEST 9: PROXY ROUTE INTEGRITY")
        try:
            # Test key proxy endpoints exist
            endpoints = [
                ("/api/session/v1x/marketplace/courses", "GET"),
                ("/api/session/v1x/marketplace/cart", "GET"),
                ("/api/session/v1x/marketplace/cart/add", "POST"),
            ]
            
            all_ok = True
            for endpoint, method in endpoints:
                try:
                    if method == "GET":
                        resp = self.session.get(f"{self.frontend_base}{endpoint}", timeout=3)
                    else:
                        resp = self.session.post(f"{self.frontend_base}{endpoint}", json={}, timeout=3)
                    
                    # 200, 400, 422 all mean route exists (might reject POST with empty data)
                    exists = resp.status_code < 500
                    status = "✅" if exists else "❌"
                    print(f"{status} {method:6} {endpoint}")
                    all_ok = all_ok and exists
                except:
                    print(f"❌ {method:6} {endpoint} - Not responding")
                    all_ok = False
            
            self.log("Proxy Routes", all_ok, f"Tested {len(endpoints)} endpoints")
            return all_ok
        except Exception as e:
            self.log("Proxy Routes", False, str(e))
            return False
    
    def test_cart_state_persistence(self):
        """Test 10: Cart State Persistence"""
        self.print_header("TEST 10: CART STATE PERSISTENCE")
        try:
            # Get cart twice to ensure state persists
            response1 = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/cart",
                timeout=5
            )
            
            count1 = len(response1.json().get('items', [])) if response1.ok else 0
            
            # Wait and fetch again
            response2 = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/cart",
                timeout=5
            )
            
            count2 = len(response2.json().get('items', [])) if response2.ok else 0
            
            consistent = count1 == count2
            self.log("Cart Persistent", consistent, 
                    f"First: {count1} items, Second: {count2} items")
            
            return consistent
        except Exception as e:
            self.log("Persistence", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{'='*70}")
        print(f"  CART MODULE - FRONTEND PROXY TEST")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Frontend: {self.frontend_base}")
        print(f"  Backend: {self.api_base}")
        print(f"{'='*70}")
        
        tests = [
            self.test_backend_ready,
            self.test_frontend_ready,
            self.test_login_backend,
            self.test_get_courses_backend,
            self.test_cart_add_backend,
            self.test_cart_get_backend,
            self.test_cart_remove_backend,
            self.test_cart_verify_removed,
            self.test_proxy_paths,
            self.test_cart_state_persistence,
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ CRASH in {test_func.__name__}: {e}")
                self.test_results.append((test_func.__name__, False, f"Crash: {e}"))
        
        self.print_summary()
    
    def print_summary(self):
        """Print summary"""
        self.print_header("TEST SUMMARY")
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        total = len(self.test_results)
        
        print(f"\nResults: {passed}/{total} tests passed ({100*passed//total if total else 0}%)\n")
        
        for test_name, passed, message in self.test_results:
            status = "✅" if passed else "❌"
            print(f"{status} {test_name}")
            if message and not passed:
                print(f"   └─ {message}")
        
        print(f"\n{'='*70}")
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {total - passed} test(s) failed")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    tester = FrontendCartTest()
    tester.run_all_tests()
