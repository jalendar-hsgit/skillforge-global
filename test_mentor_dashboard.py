#!/usr/bin/env python3
"""
Mentor Dashboard - Endpoint Verification Script
Tests all frontend-to-backend connections for the mentor dashboard
"""

import requests
import json
from typing import Dict, List, Tuple

# Configuration
API_BASE = "http://localhost:8001"
MENTOR_ENDPOINTS = {
    "Overview": "/api/v1x/mentor-portal/dashboard/overview",
    "Sessions": "/api/v1x/mentor-portal/dashboard/sessions",
    "Earnings": "/api/v1x/mentor-portal/dashboard/earnings",
    "Students": "/api/v1x/mentor-portal/dashboard/students",
    "Analytics": "/api/v1x/mentor-portal/dashboard/analytics",
    "Reviews": "/api/v1x/mentor-portal/dashboard/reviews",
    "Profile": "/api/v1x/mentor-portal/profile",
}

PAYOUTS_ENDPOINTS = {
    "Balance": "/api/v1x/mentors/balance",
    "Payouts History": "/api/v1x/mentors/payouts",
    "Payment Methods": "/api/v1x/mentors/payment-methods",
}

def test_endpoint(name: str, method: str, endpoint: str, cookies: Dict = None) -> Tuple[bool, str]:
    """Test a single endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, cookies=cookies, timeout=5)
        elif method == "PATCH":
            response = requests.patch(url, cookies=cookies, json={}, timeout=5)
        else:
            return False, f"Unknown method: {method}"
        
        if response.status_code == 401:
            return False, "❌ 401 Unauthorized (Not logged in)"
        elif response.status_code == 403:
            return False, "❌ 403 Forbidden (Mentor not approved)"
        elif response.status_code == 404:
            return False, "❌ 404 Not Found (Not a mentor)"
        elif response.status_code in [200, 201]:
            return True, f"✅ {response.status_code} OK"
        else:
            return False, f"❌ {response.status_code} Error"
    except requests.exceptions.ConnectionError:
        return False, "❌ Connection Error (Server not running?)"
    except Exception as e:
        return False, f"❌ Exception: {str(e)}"

def main():
    print("=" * 70)
    print("MENTOR DASHBOARD - ENDPOINT VERIFICATION")
    print("=" * 70)
    print()
    
    # Test if server is running
    try:
        response = requests.get(f"{API_BASE}/healthz", timeout=5)
        print(f"✅ Server running at {API_BASE}")
    except:
        print(f"❌ Server not running at {API_BASE}")
        print("Please start the backend server and try again.")
        return
    
    print()
    print("DASHBOARD ENDPOINTS")
    print("-" * 70)
    
    passed = 0
    failed = 0
    
    for name, endpoint in MENTOR_ENDPOINTS.items():
        method = "PATCH" if "profile" in endpoint else "GET"
        success, message = test_endpoint(name, method, endpoint)
        status = "✅" if success else "❌"
        print(f"{status} {name:20} {method:6} {endpoint:50} {message}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print()
    print("PAYOUTS ENDPOINTS")
    print("-" * 70)
    
    for name, endpoint in PAYOUTS_ENDPOINTS.items():
        success, message = test_endpoint(name, "GET", endpoint)
        status = "✅" if success else "❌"
        print(f"{status} {name:20} GET    {endpoint:50} {message}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 70)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)
    print()
    
    if failed == 0:
        print("✅ All endpoints are accessible!")
    else:
        print("⚠️  Some endpoints are not accessible.")
        print("   - Make sure you are logged in")
        print("   - Make sure you are registered as a mentor")
        print("   - Make sure your mentor account is approved")

if __name__ == "__main__":
    main()
