#!/usr/bin/env python3
"""
Test payout endpoints with demo data
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8001"
HEADERS = {"Content-Type": "application/json"}

def print_result(title, status, data):
    print(f"\n{'='*60}")
    print(f"✓ {title}: {status}")
    print('='*60)
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, default=str))
    else:
        print(data)

# Test 1: Login as admin
print("\n[TEST 1] Admin Login...")
admin_res = requests.post(
    f"{API_BASE}/api/v1/auth/login",
    json={"email": "admin@skillforge.com", "password": "admin123"},
    headers=HEADERS
)
if admin_res.status_code == 200:
    admin_data = admin_res.json()
    admin_token = admin_data.get("access_token") or admin_data.get("token")
    print_result("Admin Login", admin_res.status_code, {"token": admin_token[:20] + "..."})
else:
    print_result("Admin Login ERROR", admin_res.status_code, admin_res.text)
    admin_token = None

# Test 2: Login as mentor
print("\n[TEST 2] Mentor (Sarah Chen) Login...")
mentor_res = requests.post(
    f"{API_BASE}/api/v1/auth/login",
    json={"email": "mentor.sarah@skillforge.com", "password": "mentor123"},
    headers=HEADERS
)
if mentor_res.status_code == 200:
    mentor_data = mentor_res.json()
    mentor_token = mentor_data.get("access_token") or mentor_data.get("token")
    print_result("Mentor Login", mentor_res.status_code, {"token": mentor_token[:20] + "..."})
else:
    print_result("Mentor Login ERROR", mentor_res.status_code, mentor_res.text)
    mentor_token = None

# Test 3: Get mentor payouts summary
if mentor_token:
    print("\n[TEST 3] Get Mentor Earnings Summary...")
    summary_res = requests.get(
        f"{API_BASE}/api/v1x/mentors/payouts/summary",
        headers={**HEADERS, "Authorization": f"Bearer {mentor_token}"},
        cookies={"Authorization": mentor_token}
    )
    print_result("Earnings Summary", summary_res.status_code, summary_res.json() if summary_res.ok else summary_res.text)

# Test 4: Get mentor payment methods
if mentor_token:
    print("\n[TEST 4] Get Mentor Payment Methods...")
    methods_res = requests.get(
        f"{API_BASE}/api/v1x/mentors/payouts/payment-methods",
        headers={**HEADERS, "Authorization": f"Bearer {mentor_token}"},
        cookies={"Authorization": mentor_token}
    )
    print_result("Payment Methods", methods_res.status_code, methods_res.json() if methods_res.ok else methods_res.text)

# Test 5: Admin - Get payout stats
if admin_token:
    print("\n[TEST 5] Admin: Get Payout Stats...")
    stats_res = requests.get(
        f"{API_BASE}/api/v1x/admin/payouts/stats",
        headers={**HEADERS, "Authorization": f"Bearer {admin_token}"},
        cookies={"Authorization": admin_token}
    )
    print_result("Payout Stats", stats_res.status_code, stats_res.json() if stats_res.ok else stats_res.text)

# Test 6: Admin - Get unverified payment methods
if admin_token:
    print("\n[TEST 6] Admin: Get Unverified Payment Methods...")
    unverified_res = requests.get(
        f"{API_BASE}/api/v1x/admin/payouts/payment-methods/unverified",
        headers={**HEADERS, "Authorization": f"Bearer {admin_token}"},
        cookies={"Authorization": admin_token}
    )
    print_result("Unverified Methods", unverified_res.status_code, unverified_res.json() if unverified_res.ok else unverified_res.text)

# Test 7: Admin - Get pending payouts
if admin_token:
    print("\n[TEST 7] Admin: Get Pending Payouts...")
    pending_res = requests.get(
        f"{API_BASE}/api/v1x/admin/payouts/pending",
        headers={**HEADERS, "Authorization": f"Bearer {admin_token}"},
        cookies={"Authorization": admin_token}
    )
    print_result("Pending Payouts", pending_res.status_code, pending_res.json() if pending_res.ok else pending_res.text)

print("\n\n[SUMMARY] Testing complete!")
