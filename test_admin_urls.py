#!/usr/bin/env python
"""
Test all admin URLs to identify 404s and issues
"""
import requests
import json

API_BASE = "http://localhost:8001"
AUTH_BASE = "http://localhost:8001"

# Admin credentials from demo data
admin_email = "admin@skillforge.com"
admin_password = "admin123"

def login():
    """Get auth token"""
    response = requests.post(
        f"{AUTH_BASE}/api/v1/auth/login",
        json={"email": admin_email, "password": admin_password}
    )
    if response.ok:
        data = response.json()
        print(f"✅ Login successful")
        return response.cookies
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_url(method, url, cookies, name):
    """Test a single URL"""
    try:
        if method == "GET":
            response = requests.get(url, cookies=cookies, timeout=5)
        else:
            response = requests.post(url, cookies=cookies, json={}, timeout=5)
        
        status = "✅" if response.status_code < 400 else "❌"
        print(f"{status} {method:4} {url:60} → {response.status_code}")
        
        if response.status_code >= 400:
            try:
                print(f"   Error: {response.json().get('detail', response.text[:100])}")
            except:
                print(f"   Error: {response.text[:100]}")
        
        return response.status_code < 400
    except Exception as e:
        print(f"❌ {method:4} {url:60} → ERROR: {str(e)[:50]}")
        return False

def main():
    print("\n" + "="*80)
    print("TESTING ADMIN PAYOUTS URLs")
    print("="*80 + "\n")
    
    # Login first
    cookies = login()
    if not cookies:
        print("Cannot proceed without authentication")
        return
    
    # Test admin payouts endpoints
    urls = [
        ("GET", f"{API_BASE}/api/v1x/admin/payouts/stats", "Admin Payouts Stats"),
        ("GET", f"{API_BASE}/api/v1x/admin/payouts/pending", "Admin Payouts Pending"),
        ("GET", f"{API_BASE}/api/v1x/admin/payouts/all", "Admin Payouts All"),
        ("GET", f"{API_BASE}/api/v1x/admin/payouts/payment-methods/unverified", "Admin Unverified Payment Methods"),
        ("GET", f"{API_BASE}/api/v1x/admin/payouts/1", "Admin Get Payout by ID (1)"),
        ("POST", f"{API_BASE}/api/v1x/admin/payouts/1/approve", "Admin Approve Payout"),
        ("POST", f"{API_BASE}/api/v1x/admin/payouts/1/reject", "Admin Reject Payout"),
        ("POST", f"{API_BASE}/api/v1x/admin/payouts/payment-methods/1/verify", "Admin Verify Payment Method"),
    ]
    
    results = []
    for method, url, name in urls:
        success = test_url(method, url, cookies, name)
        results.append((name, success))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    passed = sum(1 for _, s in results if s)
    print(f"Passed: {passed}/{len(results)}\n")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

if __name__ == "__main__":
    main()
