#!/usr/bin/env python
"""
Simple test to verify admin login and auth works
"""
import requests
import json

API_BASE = "http://localhost:8001"
FRONTEND_BASE = "http://localhost:3000"

# Test credentials
superadmin_email = "superadmin@skillforge.com"
superadmin_password = "super123"

def test_superadmin_login():
    """Test super admin login"""
    print("\n" + "="*60)
    print("TEST 1: Super Admin Login")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE}/api/v1/auth/login",
        json={"email": superadmin_email, "password": superadmin_password}
    )
    
    print(f"POST /api/v1/auth/login")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Cookies: {response.cookies}")
    
    if response.ok:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.cookies
    else:
        print(f"❌ Login failed!")
        print(f"Response: {response.text}")
        return None

def test_admin_endpoints(cookies):
    """Test admin endpoints with auth"""
    print("\n" + "="*60)
    print("TEST 2: Admin Endpoints with Authentication")
    print("="*60)
    
    endpoints = [
        ("/api/v1x/admin/payouts/stats", "Get Stats"),
        ("/api/v1x/admin/payouts/pending", "Get Pending"),
        ("/api/v1x/admin/payouts/all", "Get All"),
        ("/api/v1x/admin/payouts/payment-methods/unverified", "Get Unverified Methods"),
    ]
    
    for endpoint, name in endpoints:
        response = requests.get(
            f"{API_BASE}{endpoint}",
            cookies=cookies,
            timeout=5
        )
        
        status_icon = "✅" if response.status_code < 400 else "❌"
        print(f"{status_icon} {name:30} {endpoint:45} → {response.status_code}")
        
        if response.status_code >= 400:
            print(f"   Response: {response.text[:200]}")

def test_frontend_page():
    """Test frontend page"""
    print("\n" + "="*60)
    print("TEST 3: Frontend Admin Page")
    print("="*60)
    
    # Try accessing the admin payouts page
    response = requests.get(
        f"{FRONTEND_BASE}/admin/payouts",
        timeout=5
    )
    
    status_icon = "✅" if response.status_code == 200 else "❌"
    print(f"{status_icon} GET /admin/payouts → {response.status_code}")
    
    # Try the pending sub-route (which might not exist)
    response = requests.get(
        f"{FRONTEND_BASE}/admin/payouts/pending",
        timeout=5,
        allow_redirects=False
    )
    
    status_icon = "✅" if response.status_code == 200 else "⚠️ "
    print(f"{status_icon} GET /admin/payouts/pending → {response.status_code}")
    if response.status_code in (301, 302, 307, 308):
        print(f"   Redirects to: {response.headers.get('Location')}")

if __name__ == "__main__":
    print("\n🔍 ADMIN AUTHENTICATION & PAYOUTS TEST\n")
    
    # Test 1: Login
    cookies = test_superadmin_login()
    
    if cookies:
        # Test 2: Admin endpoints
        test_admin_endpoints(cookies)
    
    # Test 3: Frontend page
    test_frontend_page()
    
    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60)
