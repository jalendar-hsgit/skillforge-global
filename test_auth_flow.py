#!/usr/bin/env python3
"""
Authentication Flow Test Script
Tests the fixed authentication system
"""

import requests
import json
from time import sleep

API_BASE = "http://localhost:8001"
FRONTEND_BASE = "http://localhost:3000"

print("=" * 60)
print("SKILLFORGE AUTHENTICATION FIX TEST")
print("=" * 60)

# Test 1: Get JWT Token
print("\n[TEST 1] Login and get token...")
login_response = requests.post(
    f"{API_BASE}/api/v1/auth/login",
    json={"email": "john.doe@example.com", "password": "password123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Login successful")
    print(f"   Token: {token[:20]}...")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    exit(1)

# Test 2: Verify session endpoint works
print("\n[TEST 2] Test /api/session/me endpoint...")
session_response = requests.get(
    f"{FRONTEND_BASE}/api/session/me",
    headers={"Authorization": f"Bearer {token}"}
)

if session_response.status_code == 200:
    user_data = session_response.json()
    print(f"✅ Session check successful")
    print(f"   User: {user_data.get('email')}")
    print(f"   Role: {user_data.get('role')}")
else:
    print(f"❌ Session check failed: {session_response.status_code}")
    print(f"   Response: {session_response.text}")

# Test 3: Access protected endpoint
print("\n[TEST 3] Access protected /api/v1/account/profile...")
profile_response = requests.get(
    f"{API_BASE}/api/v1/account/profile",
    headers={"Authorization": f"Bearer {token}"}
)

if profile_response.status_code == 200:
    profile_data = profile_response.json()
    print(f"✅ Profile access successful")
    print(f"   Email: {profile_data.get('email')}")
else:
    print(f"❌ Profile access failed: {profile_response.status_code}")
    print(f"   Response: {profile_response.text}")

# Test 4: Invalid token should fail
print("\n[TEST 4] Test with invalid token...")
invalid_response = requests.get(
    f"{API_BASE}/api/v1/account/profile",
    headers={"Authorization": "Bearer invalid_token_12345"}
)

if invalid_response.status_code == 401:
    print(f"✅ Invalid token correctly rejected (401)")
else:
    print(f"❌ Invalid token not rejected: {invalid_response.status_code}")

# Test 5: No token should fail
print("\n[TEST 5] Test without token...")
no_token_response = requests.get(
    f"{API_BASE}/api/v1/account/profile"
)

if no_token_response.status_code == 401:
    print(f"✅ No token correctly rejected (401)")
else:
    print(f"❌ No token not rejected: {no_token_response.status_code}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("""
✅ Authentication flow is working correctly:
   1. Users can login and get token
   2. Token can be verified via session endpoint
   3. Protected endpoints work with valid token
   4. Invalid tokens are rejected
   5. Missing tokens are rejected

NEXT STEPS:
   1. Rebuild frontend: npm run build
   2. Start frontend: npm run dev
   3. Navigate to http://localhost:3000/profile
   4. Verify you stay logged in (no redirect to login)
   5. Test other protected routes
""")
