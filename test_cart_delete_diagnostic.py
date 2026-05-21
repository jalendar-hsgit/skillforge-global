#!/usr/bin/env python3
"""
Diagnostic Test for Cart Delete Issue
Tests both direct backend DELETE and proxy DELETE
"""
import requests
import json

class CartDeleteDiagnostic:
    def __init__(self):
        self.backend = "http://localhost:8001"
        self.frontend = "http://localhost:3000"
        self.session = requests.Session()
        
    def login(self):
        """Login to get auth token"""
        print("[1/5] Logging in...")
        response = self.session.post(
            f"{self.backend}/api/v1/auth/login",
            json={"email": "admin@skillforge.com", "password": "admin123"}
        )
        if response.status_code == 200:
            print(f"✅ Logged in, cookies: {list(self.session.cookies.keys())}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def get_cart(self):
        """Get current cart"""
        print("\n[2/5] Getting cart items...")
        response = self.session.get(f"{self.backend}/api/v1x/marketplace/cart")
        if response.ok:
            items = response.json().get('items', [])
            print(f"✅ Cart has {len(items)} items")
            for item in items:
                print(f"   - Item {item['id']}: Course {item['course_id']} (${item['price']})")
            return items
        else:
            print(f"❌ Get cart failed: {response.status_code}")
            return []
    
    def test_direct_delete(self, item_id):
        """Test DELETE directly on backend"""
        print(f"\n[3/5] Testing DIRECT backend DELETE /api/v1x/marketplace/cart/{item_id}")
        
        url = f"{self.backend}/api/v1x/marketplace/cart/{item_id}"
        print(f"   URL: {url}")
        print(f"   Method: DELETE")
        print(f"   Cookies: {list(self.session.cookies.keys())}")
        
        response = self.session.delete(url)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print(f"✅ Direct DELETE worked!")
            return True
        else:
            print(f"❌ Direct DELETE failed!")
            return False
    
    def test_proxy_delete(self, item_id):
        """Test DELETE via proxy"""
        print(f"\n[4/5] Testing PROXY DELETE /api/session/v1x/marketplace/cart/{item_id}")
        
        url = f"{self.frontend}/api/session/v1x/marketplace/cart/{item_id}"
        print(f"   URL: {url}")
        print(f"   Method: DELETE")
        print(f"   Cookies: {list(self.session.cookies.keys())}")
        
        response = self.session.delete(url)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print(f"✅ Proxy DELETE worked!")
            return True
        else:
            print(f"❌ Proxy DELETE failed!")
            return False
    
    def verify_delete(self):
        """Verify item was deleted"""
        print(f"\n[5/5] Verifying deletion...")
        response = self.session.get(f"{self.backend}/api/v1x/marketplace/cart")
        if response.ok:
            items = response.json().get('items', [])
            print(f"✅ Cart now has {len(items)} items")
            return True
        return False
    
    def run(self):
        print("="*70)
        print("CART DELETE DIAGNOSTIC TEST")
        print("="*70)
        
        if not self.login():
            return
        
        items = self.get_cart()
        if not items:
            print("\n⚠️  No items in cart to test delete")
            return
        
        test_item = items[0]
        print(f"\n→ Testing with item {test_item['id']} (Course {test_item['course_id']})")
        
        # Get fresh cart items (need 2 items to test both)
        if len(items) >= 2:
            # Test direct delete on first item
            success1 = self.test_direct_delete(items[0]['id'])
            
            # Verify
            self.verify_delete()
            
            # Get updated cart for proxy test
            items = self.get_cart()
            if items:
                success2 = self.test_proxy_delete(items[0]['id'])
                self.verify_delete()
                
                print("\n" + "="*70)
                print(f"Direct DELETE: {'✅ PASS' if success1 else '❌ FAIL'}")
                print(f"Proxy DELETE:  {'✅ PASS' if success2 else '❌ FAIL'}")
                print("="*70)
        else:
            print("\n⚠️  Need at least 2 items in cart to test both methods")
            success1 = self.test_direct_delete(items[0]['id'])
            print("\n" + "="*70)
            print(f"Direct DELETE: {'✅ PASS' if success1 else '❌ FAIL'}")
            print("="*70)

if __name__ == "__main__":
    test = CartDeleteDiagnostic()
    test.run()
