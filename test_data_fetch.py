#!/usr/bin/env python
"""Test login and data fetching"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"
time.sleep(1)

# Test 1: Check if server is responding
print("=" * 60)
print("Test 1: Server Health Check")
print("=" * 60)
try:
    response = requests.get(f"{BASE_URL}/api/v1x/auth/login", timeout=5)
    print(f"Server is responding: {response.status_code}")
except Exception as e:
    print(f"❌ Server not responding: {e}")
    exit(1)

# Test 2: Try to login with demo superadmin
print("\n" + "=" * 60)
print("Test 2: SuperAdmin Login")
print("=" * 60)
login_data = {
    "email": "superadmin@skillforge.com",
    "password": "super123"
}
try:
    response = requests.post(
        f"{BASE_URL}/api/v1x/auth/login",
        json=login_data,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200 and data.get('data', {}).get('access_token'):
        token = data['data']['access_token']
        print(f"✅ Login successful! Token: {token[:30]}...")
        
        # Test 3: Fetch courses with token
        print("\n" + "=" * 60)
        print("Test 3: Fetch Courses")
        print("=" * 60)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1x/courses",
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        courses = response.json()
        print(f"Courses count: {len(courses) if isinstance(courses, list) else 'N/A'}")
        if isinstance(courses, list) and courses:
            print(f"First course: {courses[0]}")
        else:
            print(f"Response: {courses}")
    else:
        print(f"❌ Login failed")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Check mentors endpoint
print("\n" + "=" * 60)
print("Test 4: Fetch Mentors (without auth)")
print("=" * 60)
try:
    response = requests.get(
        f"{BASE_URL}/api/v1x/mentors",
        timeout=10
    )
    print(f"Status: {response.status_code}")
    mentors = response.json()
    print(f"Mentors count: {len(mentors) if isinstance(mentors, list) else 'N/A'}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Testing complete")
print("=" * 60)
