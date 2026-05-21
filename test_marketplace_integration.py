#!/usr/bin/env python3
"""
Marketplace Frontend + Backend Integration Test
Tests the full flow through the frontend proxy
"""
import requests
import json
from datetime import datetime

class MarketplaceFrontendTest:
    def __init__(self):
        self.backend = "http://localhost:8001"
        self.frontend = "http://localhost:3000"
        self.session = requests.Session()
        self.test_results = []
        
    def log(self, test_name, passed, message=""):
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
        if message:
            print(f"   └─ {message}")
        self.test_results.append((test_name, passed, message))
    
    def header(self, title):
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    
    def test_servers_running(self):
        """Test 1: Both servers responding"""
        self.header("TEST 1: SERVER STATUS")
        
        # Backend
        try:
            r = requests.get(f"{self.backend}/api/v1/courses", timeout=2)
            backend_ok = r.status_code == 200
            self.log("Backend Running", backend_ok, f"Status: {r.status_code}")
        except:
            self.log("Backend Running", False, "Not responding")
            return False
        
        # Frontend
        try:
            r = requests.get(self.frontend, timeout=2)
            frontend_ok = r.status_code == 200
            self.log("Frontend Running", frontend_ok, f"Status: {r.status_code}")
        except:
            self.log("Frontend Running", False, "Not responding")
            return False
        
        return backend_ok and frontend_ok
    
    def test_proxy_routes(self):
        """Test 2: Proxy routes exist"""
        self.header("TEST 2: PROXY ROUTES")
        
        routes = [
            ("GET", "/api/session/v1x/marketplace/courses"),
            ("GET", "/api/session/v1x/marketplace/cart"),
            ("POST", "/api/session/v1x/marketplace/cart/add"),
            ("GET", "/api/session/v1x/marketplace/seller/products"),
            ("GET", "/api/session/v1x/admin/marketplace/stats"),
        ]
        
        all_ok = True
        for method, path in routes:
            try:
                if method == "GET":
                    r = self.session.get(f"{self.frontend}{path}", timeout=2)
                elif method == "POST":
                    r = self.session.post(f"{self.frontend}{path}", json={}, timeout=2)
                
                # 200, 401, 400, 422 all mean endpoint exists (might reject with auth/data)
                exists = r.status_code < 500
                status = "✅" if exists else "❌"
                print(f"{status} {method:6} {path}")
                all_ok = all_ok and exists
            except Exception as e:
                print(f"❌ {method:6} {path} - {str(e)[:40]}")
                all_ok = False
        
        self.log("Proxy Routes", all_ok)
        return all_ok
    
    def test_marketplace_pages(self):
        """Test 3: Frontend marketplace pages load"""
        self.header("TEST 3: FRONTEND PAGES")
        
        pages = [
            "/marketplace",
            "/marketplace/cart",
            "/marketplace/checkout",
            "/marketplace/seller/dashboard",
            "/admin/marketplace",
        ]
        
        all_ok = True
        for page in pages:
            try:
                r = requests.get(f"{self.frontend}{page}", timeout=3)
                ok = r.status_code == 200
                status = "✅" if ok else "❌"
                print(f"{status} GET {page}")
                all_ok = all_ok and ok
            except Exception as e:
                print(f"❌ GET {page} - {str(e)[:40]}")
                all_ok = False
        
        self.log("Frontend Pages", all_ok)
        return all_ok
    
    def test_end_to_end_flow(self):
        """Test 4: End-to-end marketplace flow"""
        self.header("TEST 4: END-TO-END FLOW")
        
        # Step 1: Login
        print("[Step 1] Login...")
        r = self.session.post(
            f"{self.backend}/api/v1/auth/login",
            json={"email": "john.doe@example.com", "password": "john123"},
            timeout=5
        )
        login_ok = r.status_code == 200
        self.log("  Login", login_ok, f"Status: {r.status_code}")
        
        if not login_ok:
            return False
        
        # Step 2: Browse via proxy
        print("[Step 2] Browse marketplace...")
        r = self.session.get(f"{self.frontend}/api/session/v1x/marketplace/courses", timeout=5)
        browse_ok = r.status_code == 200
        self.log("  Browse", browse_ok, f"Status: {r.status_code}")
        
        if not browse_ok:
            return False
        
        # Step 3: Get cart via proxy
        print("[Step 3] View cart...")
        r = self.session.get(f"{self.frontend}/api/session/v1x/marketplace/cart", timeout=5)
        cart_ok = r.status_code == 200
        self.log("  View Cart", cart_ok, f"Status: {r.status_code}")
        
        if cart_ok:
            cart = r.json()
            items = len(cart.get('items', []))
            print(f"     Items in cart: {items}")
        
        # Step 4: Add to cart via proxy
        print("[Step 4] Add to cart...")
        r = self.session.get(f"{self.backend}/api/v1x/marketplace/courses", timeout=5)
        courses = r.json() if r.ok else []
        
        if courses:
            course_id = courses[0]['id']
            r = self.session.post(
                f"{self.frontend}/api/session/v1x/marketplace/cart/add",
                json={"course_id": course_id},
                timeout=5
            )
            add_ok = r.status_code in [200, 400]  # 400 if already added
            self.log("  Add to Cart", add_ok, f"Status: {r.status_code}")
        else:
            self.log("  Add to Cart", False, "No courses available")
            return False
        
        # Step 5: Verify cart updated
        print("[Step 5] Verify cart...")
        r = self.session.get(f"{self.frontend}/api/session/v1x/marketplace/cart", timeout=5)
        verify_ok = r.status_code == 200
        self.log("  Verify Cart", verify_ok, f"Status: {r.status_code}")
        
        if verify_ok:
            cart = r.json()
            items = len(cart.get('items', []))
            print(f"     Items in cart after add: {items}")
        
        return all([login_ok, browse_ok, cart_ok, add_ok, verify_ok])
    
    def test_seller_flow(self):
        """Test 5: Seller features"""
        self.header("TEST 5: SELLER FLOW")
        
        # Login as seller
        print("[Seller Login] Logging in...")
        r = self.session.post(
            f"{self.backend}/api/v1/auth/login",
            json={"email": "jane.smith@example.com", "password": "jane123"},
            timeout=5
        )
        
        login_ok = r.status_code == 200
        self.log("  Login", login_ok, f"Status: {r.status_code}")
        
        if not login_ok:
            return False
        
        # Get seller products
        print("[Seller Products] Fetching...")
        r = self.session.get(
            f"{self.frontend}/api/session/v1x/marketplace/seller/products",
            timeout=5
        )
        
        products_ok = r.status_code == 200
        self.log("  Get Products", products_ok, f"Status: {r.status_code}")
        
        if products_ok:
            products = r.json()
            is_list = isinstance(products, list)
            print(f"     Products count: {len(products) if is_list else 'N/A'}")
        
        # Get seller analytics
        print("[Seller Analytics] Fetching...")
        r = self.session.get(
            f"{self.frontend}/api/session/v1x/marketplace/seller/analytics",
            timeout=5
        )
        
        analytics_ok = r.status_code == 200
        self.log("  Get Analytics", analytics_ok, f"Status: {r.status_code}")
        
        if analytics_ok:
            analytics = r.json()
            print(f"     Total Sales: ${analytics.get('total_sales', 0):.2f}")
            print(f"     Total Orders: {analytics.get('total_orders', 0)}")
        
        return login_ok and products_ok and analytics_ok
    
    def test_admin_flow(self):
        """Test 6: Admin features"""
        self.header("TEST 6: ADMIN FLOW")
        
        # Login as admin
        print("[Admin Login] Logging in...")
        r = self.session.post(
            f"{self.backend}/api/v1/auth/login",
            json={"email": "admin@skillforge.com", "password": "admin123"},
            timeout=5
        )
        
        login_ok = r.status_code == 200
        self.log("  Login", login_ok, f"Status: {r.status_code}")
        
        if not login_ok:
            return False
        
        # Get marketplace stats
        print("[Admin Stats] Fetching...")
        r = self.session.get(
            f"{self.frontend}/api/session/v1x/admin/marketplace/stats",
            timeout=5
        )
        
        stats_ok = r.status_code == 200
        self.log("  Get Stats", stats_ok, f"Status: {r.status_code}")
        
        if stats_ok:
            stats = r.json()
            print(f"     Total Products: {stats.get('total_products', 0)}")
            print(f"     Total Sales: ${stats.get('total_sales', 0):.2f}")
            print(f"     Active Sellers: {stats.get('active_sellers', 0)}")
        
        # Get all orders
        print("[Admin Orders] Fetching...")
        r = self.session.get(
            f"{self.frontend}/api/session/v1x/admin/marketplace/orders",
            timeout=5
        )
        
        orders_ok = r.status_code == 200
        self.log("  Get Orders", orders_ok, f"Status: {r.status_code}")
        
        if orders_ok:
            orders = r.json()
            is_list = isinstance(orders, list)
            print(f"     Orders count: {len(orders) if is_list else 'N/A'}")
        
        # Get all sellers
        print("[Admin Sellers] Fetching...")
        r = self.session.get(
            f"{self.frontend}/api/session/v1x/admin/marketplace/sellers",
            timeout=5
        )
        
        sellers_ok = r.status_code == 200
        self.log("  Get Sellers", sellers_ok, f"Status: {r.status_code}")
        
        if sellers_ok:
            sellers = r.json()
            is_list = isinstance(sellers, list)
            print(f"     Sellers count: {len(sellers) if is_list else 'N/A'}")
        
        return all([login_ok, stats_ok, orders_ok, sellers_ok])
    
    def test_error_handling(self):
        """Test 7: Error handling"""
        self.header("TEST 7: ERROR HANDLING")
        
        # Try invalid operation
        print("[Invalid Cart Item]...")
        r = self.session.delete(f"{self.frontend}/api/session/v1x/marketplace/cart/99999", timeout=5)
        
        is_error = r.status_code >= 400
        self.log("  Delete Non-Existent", is_error, f"Status: {r.status_code} (expected 404)")
        
        # Try unauthorized
        print("[Unauthorized]...")
        no_auth_session = requests.Session()
        r = no_auth_session.get(
            f"{self.frontend}/api/session/v1x/marketplace/seller/products",
            timeout=5
        )
        
        is_protected = r.status_code == 401 or r.status_code == 403
        self.log("  Seller Endpoint Protected", is_protected, f"Status: {r.status_code}")
        
        return is_error and is_protected
    
    def run_all(self):
        """Run all tests"""
        print(f"\n{'='*70}")
        print(f"  MARKETPLACE FRONTEND + BACKEND INTEGRATION TEST")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Frontend: {self.frontend}")
        print(f"  Backend: {self.backend}")
        print(f"{'='*70}")
        
        tests = [
            self.test_servers_running,
            self.test_proxy_routes,
            self.test_marketplace_pages,
            self.test_end_to_end_flow,
            self.test_seller_flow,
            self.test_admin_flow,
            self.test_error_handling,
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log(test_func.__name__, False, f"Exception: {str(e)[:60]}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print summary"""
        self.header("TEST SUMMARY")
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        total = len(self.test_results)
        pass_rate = (100 * passed // total) if total else 0
        
        print(f"\nResults: {passed}/{total} tests passed ({pass_rate}%)\n")
        
        for test, p, msg in self.test_results:
            status = "✅" if p else "❌"
            print(f"{status} {test}")
            if msg and not p:
                print(f"   └─ {msg}")
        
        print(f"\n{'='*70}")
        if pass_rate == 100:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
        elif pass_rate >= 80:
            print(f"⚠️  Some tests failed - {total - passed} issue(s)")
        else:
            print(f"❌ Major issues detected - {total - passed} test(s) failed")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    tester = MarketplaceFrontendTest()
    tester.run_all()
