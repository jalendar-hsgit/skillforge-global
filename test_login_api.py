#!/usr/bin/env python3
"""Test authentication flow."""
import requests
import json

BASE_URL = 'http://localhost:3000'
BACKEND_URL = 'http://localhost:8001'

print("=" * 60)
print("TESTING AUTHENTICATION FLOW")
print("=" * 60)

# Test 1: Direct backend login
print("\n1. Testing direct backend login...")
resp = requests.post(
    f'{BACKEND_URL}/api/v1/auth/login',
    json={'email': 'admin@skillforge.com', 'password': 'admin123'}
)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.json()}")
print(f"   Set-Cookie: {resp.headers.get('set-cookie', 'NOT SET')}")

# Test 2: Frontend proxy login
print("\n2. Testing frontend proxy login...")
session = requests.Session()
resp = session.post(
    f'{BASE_URL}/api/session/login',
    json={'email': 'admin@skillforge.com', 'password': 'admin123'}
)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text[:100]}...")
print(f"   Cookies: {session.cookies.get_dict()}")

# Test 3: Check me endpoint
print("\n3. Testing /api/session/me...")
resp = session.get(f'{BASE_URL}/api/session/me')
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"   User: {resp.json()}")
else:
    print(f"   Error: {resp.text[:100]}")

print("\n" + "=" * 60)

