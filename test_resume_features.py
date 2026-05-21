#!/usr/bin/env python
"""Test all resume feature endpoints"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1x"

# Create a test user and resume first
def setup_test_data():
    print("Setting up test data...")
    
    # Signup
    user_email = f"test_features_{int(datetime.now().timestamp())}@test.com"
    requests.post(
        f"{BASE_URL}/api/v1/auth/signup",
        json={"email": user_email, "password": "Test123!", "name": "Test User"}
    )
    
    # Login
    login_resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": user_email, "password": "Test123!"}
    )
    cookies = login_resp.cookies
    
    # Create resume
    resume_resp = requests.post(
        f"{API_BASE}/session/resumes",
        json={
            "title": "Feature Test Resume",
            "full_name": "Test User",
            "email": user_email,
            "phone": "+1234567890",
            "professional_summary": "Test summary",
            "template": "modern"
        },
        cookies=cookies
    )
    
    resume_id = resume_resp.json()['id']
    print(f"✓ Created test resume ID: {resume_id}\n")
    return cookies, resume_id

def test_endpoints(cookies, resume_id):
    """Test all resume feature endpoints"""
    
    endpoints = {
        "List Resumes": f"/api/session/resumes",
        "Get Resume": f"/api/session/resumes/{resume_id}",
        "Get ATS Score": f"/resumes/{resume_id}/ats-score",
        "Get Export": f"/resumes/{resume_id}/export",
        "Get Versions": f"/resumes/{resume_id}/versions",
        "Get Sharing": f"/resumes/{resume_id}/sharing",
        "Get Compare": f"/resumes/{resume_id}/compare",
        "Get Templates": f"/resumes/{resume_id}/templates",
    }
    
    print("Testing Resume Feature Endpoints:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for feature, endpoint in endpoints.items():
        try:
            # Session endpoints need API_BASE prefix
            if "/api/session" in endpoint:
                url = f"{BASE_URL}{endpoint}"
            else:
                # These are frontend pages, check with Node.js
                url = f"http://localhost:3002{endpoint}"
            
            resp = requests.get(url, cookies=cookies, timeout=5)
            status = resp.status_code
            
            # Frontend pages return 200, API endpoints should be 2xx
            is_ok = 200 <= status < 300
            symbol = "✓" if is_ok else "✗"
            
            print(f"{symbol} {feature:20} : {status}")
            
            if is_ok:
                passed += 1
            else:
                failed += 1
                print(f"  Response: {resp.text[:100]}")
        except Exception as e:
            print(f"✗ {feature:20} : ERROR - {str(e)[:50]}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print(f"Resume Features Test - {datetime.now()}\n")
    
    try:
        cookies, resume_id = setup_test_data()
        success = test_endpoints(cookies, resume_id)
        
        if success:
            print("\n✅ All endpoints are accessible!")
        else:
            print("\n⚠️  Some endpoints failed - check details above")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
