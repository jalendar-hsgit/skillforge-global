#!/usr/bin/env python
"""Complete resume workflow test"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1x"

def test_workflow():
    """Test complete resume workflow"""
    print("\n" + "="*60)
    print("SKILLFORGE RESUME WORKFLOW TEST")
    print("="*60)
    print(f"Timestamp: {datetime.now()}")
    print(f"API Base: {API_BASE}\n")
    
    # Step 1: Create test user
    print("[1/5] Creating test user...")
    user_email = f"test_{int(datetime.now().timestamp())}@test.com"
    signup_resp = requests.post(
        f"{BASE_URL}/api/v1/auth/signup",
        json={"email": user_email, "password": "TestPassword123!", "name": "Test User"}
    )
    print(f"  Status: {signup_resp.status_code}")
    if signup_resp.status_code not in [200, 201]:
        print(f"  Response: {signup_resp.text[:200]}")
        # Try login if signup failed (user might exist)
        login_resp = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": user_email, "password": "TestPassword123!"}
        )
        if login_resp.status_code != 200:
            print("  ✗ Failed to signup or login")
            return
    
    # Step 2: Login
    print("\n[2/5] Logging in...")
    login_resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": user_email, "password": "TestPassword123!"}
    )
    print(f"  Status: {login_resp.status_code}")
    
    if login_resp.status_code != 200:
        print(f"  ✗ Login failed: {login_resp.text[:200]}")
        return
    
    # Get auth cookie
    cookies = login_resp.cookies
    print(f"  OK: Got auth cookie: {list(cookies.keys())}")
    
    # Step 3: Get current user
    print("\n[3/5] Getting current user...")
    me_resp = requests.get(
        f"{API_BASE}/session/me",
        cookies=cookies
    )
    print(f"  Status: {me_resp.status_code}")
    if me_resp.status_code == 200:
        user_data = me_resp.json()
        print(f"  ✓ User ID: {user_data.get('id')}")
        print(f"  ✓ Email: {user_data.get('email')}")
    
    # Step 4: Create resume
    print("\n[4/5] Creating resume...")
    resume_data = {
        "title": "Test Resume",
        "name": "Test User",
        "email": user_email,
        "phone": "+1234567890",
        "summary": "A test resume",
        "template": "modern"
    }
    create_resp = requests.post(
        f"{API_BASE}/session/resumes",
        json=resume_data,
        cookies=cookies
    )
    print(f"  Status: {create_resp.status_code}")
    
    if create_resp.status_code not in [200, 201]:
        print(f"  Response: {create_resp.text[:200]}")
        return
    
    resume_json = create_resp.json()
    resume_id = resume_json.get('id')
    print(f"  ✓ Created resume ID: {resume_id}")
    
    # Step 5: Update resume
    print("\n[5/5] Updating resume (the critical test)...")
    update_data = {
        "summary": "Updated professional summary for the resume",
        "phone": "+9876543210"
    }
    update_resp = requests.patch(
        f"{API_BASE}/session/resumes?id={resume_id}",
        json=update_data,
        cookies=cookies
    )
    print(f"  Status: {update_resp.status_code}")
    
    if update_resp.status_code == 200:
        updated = update_resp.json()
        print(f"  ✓ Resume updated successfully")
        print(f"  ✓ New summary: {updated.get('summary', 'N/A')[:50]}...")
        print(f"  ✓ New phone: {updated.get('phone', 'N/A')}")
        print(f"  ✓ Version: {updated.get('version', 'N/A')}")
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED! Resume workflow is working!")
        print("="*60)
    else:
        print(f"  ✗ Update failed: {update_resp.text[:200]}")
        print("\n" + "="*60)
        print("❌ UPDATE TEST FAILED")
        print("="*60)

if __name__ == "__main__":
    test_workflow()
