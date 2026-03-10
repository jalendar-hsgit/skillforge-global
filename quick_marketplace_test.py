#!/usr/bin/env python3
"""
Simple marketplace quick test - verifies basic functionality
"""
import requests
import time

BASE_URL = "http://localhost:8001"

print("Waiting for backend to be ready...")
for i in range(30):
    try:
        r = requests.get(f"{BASE_URL}/api/v1/courses", timeout=2)
        if r.status_code == 200:
            print("✓ Backend is ready!\n")
            break
    except:
        pass
    print(f"  Attempt {i+1}/30...", end="\r")
    time.sleep(1)
else:
    print("✗ Backend is not responding after 30 seconds")
    exit(1)

print("\n" + "="*70)
print("MARKETPLACE QUICK TEST")
print("="*70 + "\n")

tests_passed = 0
tests_failed = 0

def test(name, func):
    global tests_passed, tests_failed
    print(f"Testing: {name}...", end=" ")
    try:
        func()
        print("✓")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ {e}")
        tests_failed += 1
    except Exception as e:
        print(f"✗ Error: {e}")
        tests_failed += 1

# Test 1: List Products
def test_list_products():
    r = requests.get(f"{BASE_URL}/api/v1x/marketplace/digital-products")
    assert r.status_code == 200, f"Status {r.status_code}"
    data = r.json()
    assert "products" in data, "No products key"
    print(f"({len(data['products'])} products found)", end="")

# Test 2: Get Product Detail
def test_product_detail():
    r = requests.get(f"{BASE_URL}/api/v1x/marketplace/digital-products/1")
    assert r.status_code == 200, f"Status {r.status_code}"
    data = r.json()
    assert "id" in data and "name" in data and "price" in data
    print(f"({data['name']})", end="")

# Test 3: Authentication
def test_auth():
    r = requests.post(
        f"{BASE_URL}/api/v1x/auth/login",
        json={"email": "john.doe@example.com", "password": "student123"}
    )
    assert r.status_code == 200, f"Status {r.status_code}"
    data = r.json()
    assert "access_token" in data
    global student_token
    student_token = data["access_token"]

# Test 4: Get Cart
def test_get_cart():
    headers = {"Authorization": f"Bearer {student_token}"}
    r = requests.get(f"{BASE_URL}/api/v1x/marketplace/cart", headers=headers)
    assert r.status_code == 200, f"Status {r.status_code}"
    data = r.json()
    assert "items" in data and "total" in data
    print(f"(items: {len(data['items'])})", end="")

# Test 5: Add to Cart
def test_add_to_cart():
    headers = {"Authorization": f"Bearer {student_token}"}
    r = requests.post(
        f"{BASE_URL}/api/v1x/marketplace/cart/add-digital-product",
        json={"product_id": 1},
        headers=headers
    )
    assert r.status_code == 200, f"Status {r.status_code}"

# Test 6: Get Orders
def test_get_orders():
    headers = {"Authorization": f"Bearer {student_token}"}
    r = requests.get(f"{BASE_URL}/api/v1x/marketplace/orders", headers=headers)
    assert r.status_code == 200, f"Status {r.status_code}"
    print(f"({len(r.json())} orders)", end="")

# Test 7: Get Wishlist
def test_wishlist():
    headers = {"Authorization": f"Bearer {student_token}"}
    r = requests.get(f"{BASE_URL}/api/v1x/wishlist", headers=headers)
    assert r.status_code == 200, f"Status {r.status_code}"

# Run tests
student_token = None
test("List digital products", test_list_products)
test("Get product detail", test_product_detail)
test("Login (authentication)", test_auth)
test("Fetch empty cart", test_get_cart)
test("Add digital product to cart", test_add_to_cart)
test("Get cart after add", test_get_cart)
test("Fetch order history", test_get_orders)
test("Fetch wishlist", test_wishlist)

# Print summary
print("\n" + "="*70)
print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
print("="*70)

if tests_failed == 0:
    print("✓ All tests passed!")
else:
    print(f"✗ {tests_failed} test(s) failed")
    
exit(0 if tests_failed == 0 else 1)
