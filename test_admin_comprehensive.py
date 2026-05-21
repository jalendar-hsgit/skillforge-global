#!/usr/bin/env python
"""
Comprehensive Admin URLs Test - Frontend Navigation
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8001"
FRONTEND_BASE = "http://localhost:3000"

# Admin credentials from demo data
admin_email = "admin@skillforge.com"
admin_password = "admin123"

def login():
    """Get auth token"""
    response = requests.post(
        f"{API_BASE}/api/v1/auth/login",
        json={"email": admin_email, "password": admin_password}
    )
    if response.ok:
        print(f"✅ Login successful - {admin_email}")
        return response.cookies
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_api_endpoint(method, endpoint, cookies, name):
    """Test API endpoint"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, cookies=cookies, timeout=5)
        else:
            response = requests.post(url, cookies=cookies, json={}, timeout=5)
        
        status = "✅" if response.status_code < 400 else "❌"
        print(f"  {status} {method:4} {endpoint:50} → {response.status_code}")
        return response.status_code < 400
    except Exception as e:
        print(f"  ❌ {method:4} {endpoint:50} → ERROR: {str(e)[:40]}")
        return False

def test_frontend_page(path, name):
    """Test frontend page loads"""
    url = f"{FRONTEND_BASE}{path}"
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"  {status} GET {path:50} → {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ GET {path:50} → ERROR: {str(e)[:40]}")
        return False

def main():
    print("\n" + "="*90)
    print("ADMIN URLS COMPREHENSIVE TEST")
    print("="*90 + "\n")
    
    # Login first
    cookies = login()
    if not cookies:
        print("❌ Cannot proceed without authentication\n")
        return
    
    print("\n" + "-"*90)
    print("FRONTEND PAGES (Next.js)")
    print("-"*90 + "\n")
    
    frontend_pages = [
        ("/admin", "Admin Dashboard"),
        ("/admin/payouts", "Admin Payouts"),
        ("/admin/analytics", "Admin Analytics"),
        ("/admin/users", "Admin Users"),
        ("/admin/mentors", "Admin Mentors"),
        ("/admin/courses", "Admin Courses"),
        ("/admin/marketplace", "Admin Marketplace"),
        ("/admin/settings", "Admin Settings"),
    ]
    
    frontend_results = []
    for path, name in frontend_pages:
        success = test_frontend_page(path, name)
        frontend_results.append((name, success))
    
    print("\n" + "-"*90)
    print("API ENDPOINTS - ADMIN PAYOUTS")
    print("-"*90 + "\n")
    
    api_endpoints = [
        ("GET", "/api/v1x/admin/payouts/stats", "Get Stats"),
        ("GET", "/api/v1x/admin/payouts/pending", "Get Pending Payouts"),
        ("GET", "/api/v1x/admin/payouts/all", "Get All Payouts"),
        ("GET", "/api/v1x/admin/payouts/payment-methods/unverified", "Get Unverified Payment Methods"),
    ]
    
    api_results = []
    for method, endpoint, name in api_endpoints:
        success = test_api_endpoint(method, endpoint, cookies, name)
        api_results.append((name, success))
    
    print("\n" + "-"*90)
    print("API ENDPOINTS - ADMIN GENERAL")
    print("-"*90 + "\n")
    
    admin_general = [
        ("GET", "/api/v1x/admin", "Admin Main"),
        ("GET", "/api/v1x/admin/analytics", "Admin Analytics"),
        ("GET", "/api/v1x/admin/mentors", "Admin Mentors"),
    ]
    
    for method, endpoint, name in admin_general:
        success = test_api_endpoint(method, endpoint, cookies, name)
        api_results.append((name, success))
    
    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90 + "\n")
    
    frontend_passed = sum(1 for _, s in frontend_results if s)
    api_passed = sum(1 for _, s in api_results if s)
    
    print(f"Frontend Pages: {frontend_passed}/{len(frontend_results)} passed")
    print(f"API Endpoints:  {api_passed}/{len(api_results)} passed\n")
    
    total_passed = frontend_passed + api_passed
    total_tests = len(frontend_results) + len(api_results)
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total_tests - total_passed} test(s) failed\n")
        print("Failed tests:")
        for name, success in frontend_results + api_results:
            if not success:
                print(f"  ❌ {name}")

if __name__ == "__main__":
    main()
