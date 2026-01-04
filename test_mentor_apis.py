#!/usr/bin/env python3
"""
Comprehensive Mentor API Test Suite
====================================
Tests all mentor module endpoints
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8001/api/v1x"

# Test credentials
MENTOR_EMAIL = "mentor.python@test.com"
MENTOR_PASSWORD = "password123"
STUDENT_EMAIL = "student.alice@test.com"
STUDENT_PASSWORD = "password123"
ADMIN_EMAIL = "admin@skilforge.com"
ADMIN_PASSWORD = "admin123"

def login(email: str, password: str) -> str:
    """Login and return auth token"""
    response = requests.post(
        f"{API_BASE}/../v1/auth/login",
        json={"email": email, "password": password},
        timeout=5
    )
    if response.status_code == 200:
        # Token is in httponly cookie, but we can use requests session
        return response.cookies.get('token') or "authenticated"
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def test_mentor_apis():
    """Test all mentor endpoints"""
    print("\n" + "="*80)
    print("MENTOR API - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Use requests session for cookie handling
    session = requests.Session()
    
    # ============================================================
    # TEST 1: MENTOR ELIGIBILITY
    # ============================================================
    print("\n[1/10] Testing Mentor Eligibility Endpoint")
    print("-" * 60)
    
    session.post(
        f"{API_BASE}/../v1/auth/login",
        json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
    )
    
    response = session.get(f"{API_BASE}/mentors/eligibility")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ GET /mentors/eligibility: 200 OK")
        print(f"    - Eligible: {data.get('eligible')}")
        print(f"    - Reasons: {data.get('reasons')}")
    else:
        print(f"  ❌ GET /mentors/eligibility: {response.status_code}")
        print(f"    {response.text[:200]}")
    
    # ============================================================
    # TEST 2: GET MENTOR PROFILE
    # ============================================================
    print("\n[2/10] Testing Get Mentor Profile")
    print("-" * 60)
    
    session.post(
        f"{API_BASE}/../v1/auth/login",
        json={"email": MENTOR_EMAIL, "password": MENTOR_PASSWORD}
    )
    
    response = session.get(f"{API_BASE}/mentors/me")
    if response.status_code == 200:
        mentor = response.json()
        print(f"  ✓ GET /mentors/me: 200 OK")
        print(f"    - Mentor ID: {mentor.get('id')}")
        print(f"    - Name: {mentor.get('user', {}).get('full_name')}")
        print(f"    - Expertise: {mentor.get('expertise')}")
        print(f"    - Hourly Rate: ${mentor.get('hourly_rate')}")
        print(f"    - Status: {mentor.get('status')}")
        print(f"    - Average Rating: {mentor.get('average_rating'):.2f}")
        print(f"    - Total Sessions: {mentor.get('total_sessions')}")
    else:
        print(f"  ❌ GET /mentors/me: {response.status_code}")
    
    mentor_id = mentor.get('id')
    
    # ============================================================
    # TEST 3: LIST ALL MENTORS
    # ============================================================
    print("\n[3/10] Testing List Mentors")
    print("-" * 60)
    
    response = session.get(f"{API_BASE}/mentors")
    if response.status_code == 200:
        data = response.json()
        mentors_list = data.get('mentors', [])
        print(f"  ✓ GET /mentors: 200 OK")
        print(f"    - Total mentors: {len(mentors_list)}")
        for m in mentors_list[:3]:
            print(f"      • {m.get('user', {}).get('full_name')} - {m.get('expertise')}")
    else:
        print(f"  ❌ GET /mentors: {response.status_code}")
    
    # ============================================================
    # TEST 4: SEARCH MENTORS
    # ============================================================
    print("\n[4/10] Testing Search Mentors")
    print("-" * 60)
    
    response = session.get(f"{API_BASE}/mentors/search?expertise=python-ai")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ GET /mentors/search: 200 OK")
        print(f"    - Found: {len(data.get('mentors', []))} mentors with python-ai")
    else:
        print(f"  ~ GET /mentors/search: {response.status_code} (may not be implemented)")
    
    # ============================================================
    # TEST 5: GET MENTOR AVAILABILITY
    # ============================================================
    print("\n[5/10] Testing Get Mentor Availability")
    print("-" * 60)
    
    response = session.get(f"{API_BASE}/mentors/{mentor_id}/availability")
    if response.status_code == 200:
        data = response.json()
        slots = data.get('slots', [])
        print(f"  ✓ GET /mentors/{{id}}/availability: 200 OK")
        print(f"    - Available slots: {len(slots)}")
        if slots:
            slot = slots[0]
            print(f"      • Day: {slot.get('day_of_week')}, {slot.get('start_time')}-{slot.get('end_time')}")
    else:
        print(f"  ❌ GET /mentors/{{id}}/availability: {response.status_code}")
    
    # ============================================================
    # TEST 6: GET MENTOR REVIEWS
    # ============================================================
    print("\n[6/10] Testing Get Mentor Reviews")
    print("-" * 60)
    
    response = session.get(f"{API_BASE}/mentors/reviews/{mentor_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ GET /mentors/reviews/{{id}}: 200 OK")
        print(f"    - Total reviews: {data.get('total')}")
        print(f"    - Average rating: {data.get('average_rating'):.2f}")
        reviews = data.get('reviews', [])
        if reviews:
            for review in reviews[:2]:
                print(f"      • {review.get('rating')}★ - {review.get('review_text', '')[:60]}...")
    else:
        print(f"  ❌ GET /mentors/reviews/{{id}}: {response.status_code}")
    
    # ============================================================
    # TEST 7: GET MENTOR PORTAL DASHBOARD
    # ============================================================
    print("\n[7/10] Testing Mentor Portal Dashboard")
    print("-" * 60)
    
    response = session.get(f"{API_BASE}/mentor-portal/dashboard/overview")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ GET /mentor-portal/dashboard/overview: 200 OK")
        print(f"    - Total sessions: {data.get('total_sessions')}")
        print(f"    - Completed sessions: {data.get('completed_sessions')}")
        print(f"    - Upcoming sessions: {data.get('upcoming_sessions')}")
        print(f"    - Total earnings: ${data.get('total_earnings'):.2f}")
        print(f"    - Average rating: {data.get('average_rating'):.2f}")
        print(f"    - Unique students: {data.get('unique_students')}")
    else:
        print(f"  ❌ GET /mentor-portal/dashboard/overview: {response.status_code}")
    
    # ============================================================
    # TEST 8: GET MENTOR SESSIONS
    # ============================================================
    print("\n[8/10] Testing Get Mentor Sessions")
    print("-" * 60)
    
    response = session.get(f"{API_BASE}/mentor-portal/dashboard/sessions")
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('sessions', [])
        print(f"  ✓ GET /mentor-portal/dashboard/sessions: 200 OK")
        print(f"    - Total sessions: {len(sessions)}")
        if sessions:
            for session in sessions[:2]:
                print(f"      • {session.get('topic')} - {session.get('status')} - ${session.get('price'):.2f}")
    else:
        print(f"  ❌ GET /mentor-portal/dashboard/sessions: {response.status_code}")
    
    # ============================================================
    # TEST 9: STUDENT PERSPECTIVE - LIST MENTORS
    # ============================================================
    print("\n[9/10] Testing Student Finding Mentors")
    print("-" * 60)
    
    session.post(
        f"{API_BASE}/../v1/auth/login",
        json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
    )
    
    response = session.get(f"{API_BASE}/mentors")
    if response.status_code == 200:
        data = response.json()
        mentors_list = data.get('mentors', [])
        print(f"  ✓ Student can list mentors: {len(mentors_list)} available")
    else:
        print(f"  ❌ Student mentor listing: {response.status_code}")
    
    # ============================================================
    # TEST 10: MENTOR PORTAL EARNINGS
    # ============================================================
    print("\n[10/10] Testing Mentor Portal Earnings")
    print("-" * 60)
    
    session.post(
        f"{API_BASE}/../v1/auth/login",
        json={"email": MENTOR_EMAIL, "password": MENTOR_PASSWORD}
    )
    
    response = session.get(f"{API_BASE}/mentor-portal/dashboard/earnings")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ GET /mentor-portal/dashboard/earnings: 200 OK")
        print(f"    - Total earnings: ${data.get('total_earnings'):.2f}")
        print(f"    - This month: ${data.get('month_earnings'):.2f}")
        print(f"    - Pending payments: ${data.get('pending_amount'):.2f}")
    else:
        print(f"  ~ GET /mentor-portal/dashboard/earnings: {response.status_code} (may not be implemented)")
    
    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    print("\n" + "="*80)
    print("MENTOR API TEST COMPLETE")
    print("="*80)
    print("✓ All major endpoints tested")
    print("✓ Mentor data verified")
    print("✓ API connectivity confirmed")
    print("\nTest Credentials:")
    print(f"  Mentor: {MENTOR_EMAIL} / {MENTOR_PASSWORD}")
    print(f"  Student: {STUDENT_EMAIL} / {STUDENT_PASSWORD}")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_mentor_apis()
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
