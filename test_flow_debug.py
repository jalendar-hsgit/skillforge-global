#!/usr/bin/env python3
"""
Test to check actual request/response flow
"""
import requests

session = requests.Session()

# Test 1: Login
print("[TEST 1] Login...")
r = session.post("http://localhost:8001/api/v1/auth/login", json={
    "email": "admin@skillforge.com",
    "password": "admin123"
})
print(f"Status: {r.status_code}")
print(f"Cookies: {session.cookies.get_dict()}\n")

# Test 2: Get cart directly from backend
print("[TEST 2] GET cart from backend directly...")
r = session.get("http://localhost:8001/api/v1x/marketplace/cart")
print(f"Status: {r.status_code}")
if r.ok:
    items = r.json().get('items', [])
    print(f"Items: {len(items)}")
    if items:
        print(f"First item ID: {items[0]['id']}\n")

# Test 3: DELETE from backend directly (if items exist)
if items:
    item_id = items[0]['id']
    print(f"[TEST 3] DELETE item {item_id} from backend directly...")
    r = session.delete(f"http://localhost:8001/api/v1x/marketplace/cart/{item_id}")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}\n")

# Test 4: Verify via proxy
print("[TEST 4] GET cart via FRONTEND proxy /api/session/...")
headers = {
    "Cookie": session.cookies.get_dict().get('token', '')
}
r = requests.get("http://localhost:3000/api/session/v1x/marketplace/cart", cookies=session.cookies)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}\n")

# Test 5: DELETE via proxy
if items:
    item_id = items[0]['id']
    print(f"[TEST 5] DELETE item {item_id} via FRONTEND proxy /api/session/...")
    r = requests.delete(f"http://localhost:3000/api/session/v1x/marketplace/cart/{item_id}", cookies=session.cookies)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}\n")
