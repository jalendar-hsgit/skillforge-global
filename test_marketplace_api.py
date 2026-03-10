#!/usr/bin/env python3
"""
Marketplace API Test - Comprehensive Feature Test
Tests all marketplace endpoints against running backend
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001"

print("="*70)
print("MARKETPLACE API TEST SUITE")
print("="*70)

# Step 1: Wait for backend
print("\n[1] Checking backend...")
for i in range(60):
    try:
        r = requests.get(f"{BASE_URL}/api/v1/courses", timeout=1)
        if r.status_code in [200, 401, 403]:
            print("✓ Backend is ready\n")
            break
    except:
        pass
    if i % 10 == 0:
        print(f"  Waiting... ({i}s)")
    time.sleep(1)
else:
    print("✗ Backend did not respond after 60 seconds")
    sys.exit(1)

passed = 0
failed = 0

def test(name, method, url, **kwargs):
    global passed, failed
    try:
        if method == "GET":
            r = requests.get(url, timeout=5, **kwargs)
        elif method == "POST":
            r = requests.post(url, timeout=5, **kwargs)
        else:
            r = requests.get(url, timeout=5, **kwargs)
        
        status = "✓" if r.status_code < 400 else "✗"
        print(f"{status} [{r.status_code}] {name}")
        
        if r.status_code < 400:
            passed += 1
        else:
            failed += 1
        
        return r
    except Exception as e:
        print(f"✗ [ERR] {name} - {str(e)[:50]}")
        failed += 1
        return None

print("[2] MARKETPLACE ENDPOINTS\n")

# Public endpoints
test("List digital products", "GET", f"{BASE_URL}/api/v1x/marketplace/digital-products")
test("Get product by ID", "GET", f"{BASE_URL}/api/v1x/marketplace/digital-products/1")
test("Search products", "GET", f"{BASE_URL}/api/v1x/marketplace/digital-products/search?q=test")

print("\n[3] AUTHENTICATION\n")

# Auth
r = test("Login (student)", "POST", 
    f"{BASE_URL}/api/v1x/auth/login",
    json={"email": "john.doe@example.com", "password": "student123"},
    headers={"Content-Type": "application/json"}
)

if r and r.status_code == 200:
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n[4] CART OPERATIONS\n")
    
    # Cart endpoints (authenticated)
    test("Get cart", "GET", f"{BASE_URL}/api/v1x/marketplace/cart", headers=headers)
    test("Add product to cart", "POST", 
        f"{BASE_URL}/api/v1x/marketplace/cart/add-digital-product",
        json={"product_id": 1},
        headers={**headers, "Content-Type": "application/json"}
    )
    test("Get updated cart", "GET", f"{BASE_URL}/api/v1x/marketplace/cart", headers=headers)
    
    print("\n[5] CHECKOUT & ORDERS\n")
    
    # Orders
    test("Get order history", "GET", f"{BASE_URL}/api/v1x/marketplace/orders", headers=headers)
    
    print("\n[6] WISHLIST & REVIEWS\n")
    
    # Wishlist
    test("Get wishlist", "GET", f"{BASE_URL}/api/v1x/wishlist", headers=headers)
    test("Add to wishlist", "POST",
        f"{BASE_URL}/api/v1x/wishlist",
        json={"product_id": 1},
        headers={**headers, "Content-Type": "application/json"}
    )
    
    # Reviews
    test("Get product reviews", "GET", 
        f"{BASE_URL}/api/v1x/marketplace/digital-products/1/reviews",
        headers=headers
    )
    
    # Admin endpoints
    print("\n[7] ADMIN FEATURES\n")
    
    r = test("Admin login", "POST",
        f"{BASE_URL}/api/v1x/auth/login",
        json={"email": "admin@skillforge.com", "password": "admin123"},
        headers={"Content-Type": "application/json"}
    )
    
    if r and r.status_code == 200:
        admin_token = r.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        test("Get revenue stats", "GET",
            f"{BASE_URL}/api/v1x/admin/marketplace/revenue",
            headers=admin_headers
        )
        test("Get revenue by seller", "GET",
            f"{BASE_URL}/api/v1x/admin/marketplace/revenue-by-seller",
            headers=admin_headers
        )

print("\n" + "="*70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*70)

if failed == 0:
    print("✓ All marketplace features are working!")
    sys.exit(0)
else:
    print(f"✗ {failed} feature(s) not working")
    sys.exit(1)
