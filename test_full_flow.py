#!/usr/bin/env python3
"""Test the complete login -> subscribe flow."""
import requests
from urllib.parse import urlencode

BASE_URL = 'http://localhost:3000'

print("=" * 60)
print("TESTING LOGIN -> SUBSCRIBE FLOW")
print("=" * 60)

# Create a session to maintain cookies
session = requests.Session()

# Step 1: Try to visit /subscribe (should redirect to login)
print("\n1. Visiting /subscribe?plan=pro&cycle=monthly...")
resp = session.get(f'{BASE_URL}/subscribe?plan=pro&cycle=monthly', allow_redirects=False)
print(f"   Status: {resp.status_code}")
print(f"   Location: {resp.headers.get('location', 'N/A')}")

# Step 2: Login via the proxy endpoint
print("\n2. Logging in...")
resp = session.post(
    f'{BASE_URL}/api/session/login',
    json={'email': 'admin@skillforge.com', 'password': 'admin123'}
)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text[:100]}")
print(f"   Cookies: {dict(session.cookies)}")

# Step 3: Check /api/session/me
print("\n3. Checking authentication...")
resp = session.get(f'{BASE_URL}/api/session/me')
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"   User: {resp.json()}")
    print(f"   ✅ Authenticated!")
else:
    print(f"   ❌ Not authenticated!")
    print(f"   Response: {resp.text}")

# Step 4: Visit /subscribe again
print("\n4. Visiting /subscribe again...")
resp = session.get(f'{BASE_URL}/subscribe?plan=pro&cycle=monthly', allow_redirects=True)
print(f"   Final URL: {resp.url}")
print(f"   Status: {resp.status_code}")
if 'subscribe' in resp.url:
    print(f"   ✅ Successfully redirected to subscribe page!")
else:
    print(f"   ⚠️  Unexpected redirect")

print("\n" + "=" * 60)
