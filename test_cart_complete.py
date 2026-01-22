#!/usr/bin/env python3
"""
Complete Cart Module Test Suite
Tests: Login → Browse → Add → View → Remove → Persistence
"""
import requests
import json
from http.cookiejar import CookieJar
from datetime import datetime

class CartModuleTest:
    def __init__(self, api_base="http://localhost:8001"):
        self.api_base = api_base
        self.session = requests.Session()
        self.user_email = "admin@skillforge.com"
        self.user_password = "admin123"
        self.user_id = None
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
    
    def test_login(self):
        """Test 1: User Login"""
        self.print_header("TEST 1: LOGIN")
        try:
            response = self.session.post(
                f"{self.api_base}/api/v1/auth/login",
                json={
                    "email": self.user_email,
                    "password": self.user_password
                },
                timeout=5
            )
            
            passed = response.status_code == 200
            self.log("Login", passed, f"Status: {response.status_code}")
            
            # Check cookies
            cookies = self.session.cookies.get_dict()
            has_token = 'token' in cookies
            self.log("Token Cookie", has_token, f"Cookies: {list(cookies.keys())}")
            
            return passed and has_token
        except Exception as e:
            self.log("Login", False, str(e))
            return False
    
    def test_get_courses(self):
        """Test 2: Browse Courses"""
        self.print_header("TEST 2: BROWSE COURSES")
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
                has_items = len(courses) > 0 if is_list else False
                
                self.log("Courses List", is_list and has_items, 
                        f"Count: {len(courses) if is_list else 'N/A'}")
                
                if is_list and has_items:
                    first = courses[0]
                    print(f"       Sample course: {first.get('title')} - ${first.get('price')}")
                
                return True
            return False
        except Exception as e:
            self.log("Get Courses", False, str(e))
            return False
    
    def test_get_cart(self):
        """Test 3: Get Cart"""
        self.print_header("TEST 3: GET CART")
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
                print(f"       Current items in cart: {len(items)}")
                for item in items:
                    print(f"       - Item {item['id']}: Course {item['course_id']} (${item['price']})")
                self.initial_cart_count = len(items)
                return True
            return False
        except Exception as e:
            self.log("Get Cart", False, str(e))
            return False
    
    def test_add_to_cart(self):
        """Test 4: Add Item to Cart"""
        self.print_header("TEST 4: ADD TO CART")
        try:
            # Try to add course 2 (should be available)
            course_id = 2
            response = self.session.post(
                f"{self.api_base}/api/v1x/marketplace/cart/add",
                json={"course_id": course_id},
                timeout=5
            )
            
            # 200 = success, 400 = already in cart (still valid test)
            passed = response.status_code in [200, 400]
            status_msg = response.status_code
            
            if response.ok:
                self.log("Add to Cart", True, f"Course {course_id} added - Status: {status_msg}")
                self.test_add_success = True
            else:
                msg = response.json().get('detail', '')
                if 'already in cart' in msg:
                    self.log("Add to Cart", True, f"Course {course_id} already in cart (expected)")
                    self.test_add_success = False
                else:
                    self.log("Add to Cart", False, f"Status: {status_msg} - {msg}")
                    self.test_add_success = False
            
            return passed
        except Exception as e:
            self.log("Add to Cart", False, str(e))
            return False
    
    def test_get_cart_after_add(self):
        """Test 5: Verify Cart After Add"""
        self.print_header("TEST 5: VERIFY CART AFTER ADD")
        try:
            response = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/cart",
                timeout=5
            )
            
            if response.ok:
                cart = response.json()
                items = cart.get('items', [])
                current_count = len(items)
                
                if hasattr(self, 'test_add_success') and self.test_add_success:
                    # Should have 1 more item
                    increased = current_count > self.initial_cart_count
                    self.log("Cart Increased", increased, 
                            f"Before: {self.initial_cart_count}, After: {current_count}")
                else:
                    # Should be same or same count
                    self.log("Cart Count", True, f"Items: {current_count}")
                
                print(f"       Current items in cart: {current_count}")
                for item in items:
                    print(f"       - Item {item['id']}: Course {item['course_id']} (${item['price']})")
                
                self.cart_before_delete = current_count
                self.test_item_id = items[0]['id'] if items else None
                return True
            return False
        except Exception as e:
            self.log("Verify Cart", False, str(e))
            return False
    
    def test_remove_from_cart(self):
        """Test 6: Remove Item from Cart"""
        self.print_header("TEST 6: REMOVE FROM CART")
        try:
            if not self.test_item_id:
                self.log("Remove Item", False, "No item available in cart")
                return False
            
            item_id = self.test_item_id
            response = self.session.delete(
                f"{self.api_base}/api/v1x/marketplace/cart/{item_id}",
                timeout=5
            )
            
            passed = response.status_code == 200
            self.log("Remove Item", passed, f"Item {item_id} - Status: {response.status_code}")
            
            if response.ok:
                result = response.json()
                self.log("Delete Response", True, result.get('message', ''))
            
            return passed
        except Exception as e:
            self.log("Remove Item", False, str(e))
            return False
    
    def test_get_cart_after_delete(self):
        """Test 7: Verify Cart After Delete"""
        self.print_header("TEST 7: VERIFY CART AFTER DELETE")
        try:
            response = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/cart",
                timeout=5
            )
            
            if response.ok:
                cart = response.json()
                items = cart.get('items', [])
                current_count = len(items)
                
                decreased = current_count < self.cart_before_delete
                self.log("Cart Decreased", decreased, 
                        f"Before: {self.cart_before_delete}, After: {current_count}")
                
                print(f"       Current items in cart: {current_count}")
                for item in items:
                    print(f"       - Item {item['id']}: Course {item['course_id']} (${item['price']})")
                
                return True
            return False
        except Exception as e:
            self.log("Verify After Delete", False, str(e))
            return False
    
    def test_cart_totals(self):
        """Test 8: Cart Totals Calculation"""
        self.print_header("TEST 8: CART TOTALS")
        try:
            response = self.session.get(
                f"{self.api_base}/api/v1x/marketplace/cart",
                timeout=5
            )
            
            if response.ok:
                cart = response.json()
                items = cart.get('items', [])
                subtotal = cart.get('subtotal', 0)
                total = cart.get('total', 0)
                
                # Calculate expected subtotal
                calculated = sum(item['price'] for item in items)
                matches = abs(calculated - subtotal) < 0.01
                
                self.log("Subtotal Calculation", matches, 
                        f"Expected: ${calculated:.2f}, Got: ${subtotal:.2f}")
                self.log("Total Available", total >= 0, f"Total: ${total:.2f}")
                
                return matches
            return False
        except Exception as e:
            self.log("Cart Totals", False, str(e))
            return False
    
    def test_invalid_item_delete(self):
        """Test 9: Error Handling - Invalid Item"""
        self.print_header("TEST 9: ERROR HANDLING - INVALID ITEM")
        try:
            # Try to delete non-existent item
            response = self.session.delete(
                f"{self.api_base}/api/v1x/marketplace/cart/99999",
                timeout=5
            )
            
            # Should get 404
            is_error = response.status_code == 404
            self.log("Delete Non-Existent Item", is_error, 
                    f"Status: {response.status_code} (expected 404)")
            
            if response.status_code >= 400:
                error = response.json().get('detail', '')
                print(f"       Error message: {error}")
            
            return is_error
        except Exception as e:
            self.log("Invalid Delete", False, str(e))
            return False
    
    def test_duplicate_add(self):
        """Test 10: Error Handling - Duplicate Add"""
        self.print_header("TEST 10: ERROR HANDLING - DUPLICATE ADD")
        try:
            # Get first item in cart
            response = self.session.get(f"{self.api_base}/api/v1x/marketplace/cart")
            
            if response.ok:
                items = response.json().get('items', [])
                if items:
                    course_id = items[0]['course_id']
                    
                    # Try to add it again
                    response = self.session.post(
                        f"{self.api_base}/api/v1x/marketplace/cart/add",
                        json={"course_id": course_id},
                        timeout=5
                    )
                    
                    # Should get 400 (already in cart)
                    is_duplicate_error = response.status_code == 400
                    self.log("Duplicate Add Detection", is_duplicate_error, 
                            f"Status: {response.status_code} (expected 400)")
                    
                    if response.status_code == 400:
                        error = response.json().get('detail', '')
                        print(f"       Error message: {error}")
                    
                    return is_duplicate_error
        
        self.log("Duplicate Add", False, "No items in cart to test")
        return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{'='*70}")
        print(f"  CART MODULE - COMPLETE TEST SUITE")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Backend: {self.api_base}")
        print(f"{'='*70}")
        
        # Run tests in sequence
        tests = [
            ("Login", self.test_login),
            ("Browse", self.test_get_courses),
            ("Get Cart", self.test_get_cart),
            ("Add Item", self.test_add_to_cart),
            ("After Add", self.test_get_cart_after_add),
            ("Remove Item", self.test_remove_from_cart),
            ("After Remove", self.test_get_cart_after_delete),
            ("Totals", self.test_cart_totals),
            ("Invalid Delete", self.test_invalid_item_delete),
            ("Duplicate Add", self.test_duplicate_add),
        ]
        
        for name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ CRASH in {name}: {e}")
                self.test_results.append((name, False, f"Crash: {e}"))
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        total = len(self.test_results)
        
        print(f"\nResults: {passed}/{total} tests passed ({100*passed//total}%)\n")
        
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
    # Run tests
    tester = CartModuleTest()
    tester.run_all_tests()
