#!/usr/bin/env python3
"""
Quick Marketplace API Check
"""
import requests
import time

BASE = "http://localhost:8001"
print("Waiting for backend...")
time.sleep(3)

print("\nTesting Marketplace Endpoints:\n")

try:
    # Test 1: List products
    print("[1] GET /api/v1x/marketplace/digital-products")
    r = requests.get(f"{BASE}/api/v1x/marketplace/digital-products", timeout=3)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    Products: {len(data.get('products', []))}")
    print()
    
    # Test 2: Get courses
    print("[2] GET /api/v1/courses")
    r = requests.get(f"{BASE}/api/v1/courses", timeout=3)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Courses: {len(r.json())}")
    print()
    
    # Test 3: Login
    print("[3] POST /api/v1x/auth/login")
    r = requests.post(
        f"{BASE}/api/v1x/auth/login",
        json={"email": "john.doe@example.com", "password": "student123"},
        timeout=3
    )
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        token = r.json().get("access_token")
        print(f"    Token obtained: {token[:20]}...")
        print()
        
        # Test 4: Get cart
        print("[4] GET /api/v1x/marketplace/cart")
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{BASE}/api/v1x/marketplace/cart", headers=headers, timeout=3)
        print(f"    Status: {r.status_code}")
        if r.status_code == 200:
            print(f"    Items: {len(r.json().get('items', []))}")
        print()
    
    print("✓ Marketplace endpoints are responsive!")
    
except Exception as e:
    print(f"✗ Error: {e}")
