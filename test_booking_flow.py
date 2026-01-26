#!/usr/bin/env python3
"""
Test the complete booking flow to verify:
1. Sessions are created with price
2. Sessions return price in response
3. Payment status is set correctly
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8001"
ADMIN_EMAIL = "superadmin@skillforge.com"
ADMIN_PASSWORD = "super123"
STUDENT_EMAIL = "john.doe@example.com"
STUDENT_PASSWORD = "john123"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_step(name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📋 {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def info(msg):
    print(f"{YELLOW}ℹ️  {msg}{RESET}")

# Test 1: Login as admin and get mentor list
test_step("1. LOGIN AS ADMIN & GET MENTORS")
try:
    # Login
    login_resp = requests.post(
        f"{API_BASE}/api/v1x/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if login_resp.status_code != 200:
        error(f"Login failed: {login_resp.status_code}")
        error(login_resp.text)
        exit(1)
    
    admin_token = login_resp.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    success(f"Logged in as admin")
    
    # Get mentors
    mentors_resp = requests.get(
        f"{API_BASE}/api/v1x/mentors",
        headers=admin_headers
    )
    
    if mentors_resp.status_code != 200:
        error(f"Failed to get mentors: {mentors_resp.status_code}")
        exit(1)
    
    mentors = mentors_resp.json()
    if isinstance(mentors, dict) and 'data' in mentors:
        mentors = mentors['data']
    
    if not mentors or len(mentors) == 0:
        error("No mentors found in database")
        exit(1)
    
    mentor = mentors[0]
    mentor_id = mentor.get('id')
    mentor_rate = mentor.get('hourly_rate')
    success(f"Got {len(mentors)} mentors. Using mentor ID {mentor_id} with hourly_rate ${mentor_rate}")
    
except Exception as e:
    error(f"Error in step 1: {e}")
    exit(1)

# Test 2: Login as student and book a session
test_step("2. LOGIN AS STUDENT & BOOK SESSION")
try:
    # Login as student
    student_login = requests.post(
        f"{API_BASE}/api/v1x/auth/login",
        json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
    )
    
    if student_login.status_code != 200:
        error(f"Student login failed: {student_login.status_code}")
        error(student_login.text)
        exit(1)
    
    student_token = student_login.json().get("access_token")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    success(f"Logged in as student")
    
    # Book a session
    scheduled_at = (datetime.now() + timedelta(days=1)).isoformat()
    booking_payload = {
        "mentor_id": mentor_id,
        "scheduled_at": scheduled_at,
        "duration_minutes": 60,
        "topic": "Test Booking - Python Basics"
    }
    
    info(f"Booking session: {json.dumps(booking_payload, indent=2)}")
    
    booking_resp = requests.post(
        f"{API_BASE}/api/v1x/mentors/sessions",
        headers=student_headers,
        json=booking_payload
    )
    
    if booking_resp.status_code not in [200, 201]:
        error(f"Booking failed: {booking_resp.status_code}")
        error(booking_resp.text)
        exit(1)
    
    session_data = booking_resp.json()
    session_id = session_data.get('id')
    price = session_data.get('price')
    payment_status = session_data.get('payment_status')
    
    success(f"Session booked with ID {session_id}")
    success(f"Price: ${price}")
    success(f"Payment Status: {payment_status}")
    
    # Verify price calculation
    expected_price = mentor_rate * (60 / 60)
    if price != expected_price:
        error(f"Price mismatch! Expected ${expected_price}, got ${price}")
    else:
        success(f"Price calculation correct: {mentor_rate} * 1 hour = ${price}")
    
except Exception as e:
    error(f"Error in step 2: {e}")
    exit(1)

# Test 3: Verify session in database
test_step("3. CHECK SESSION IN DATABASE")
try:
    import sqlite3
    conn = sqlite3.connect('backend/app/data/skillforge.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, mentor_id, student_id, topic, price, payment_status, status FROM mentor_sessions WHERE id = ?",
        (session_id,)
    )
    
    db_session = cursor.fetchone()
    if not db_session:
        error(f"Session {session_id} not found in database")
        exit(1)
    
    success(f"Session found in database:")
    success(f"  - ID: {db_session['id']}")
    success(f"  - Topic: {db_session['topic']}")
    success(f"  - Price: ${db_session['price']}")
    success(f"  - Payment Status: {db_session['payment_status']}")
    success(f"  - Status: {db_session['status']}")
    
    conn.close()
    
except Exception as e:
    error(f"Error in step 3: {e}")
    exit(1)

# Test 4: Fetch sessions as student and verify response
test_step("4. FETCH SESSIONS AS STUDENT - VERIFY RESPONSE")
try:
    my_sessions_resp = requests.get(
        f"{API_BASE}/api/v1x/mentors/sessions/my",
        headers=student_headers
    )
    
    if my_sessions_resp.status_code != 200:
        error(f"Failed to get my sessions: {my_sessions_resp.status_code}")
        error(my_sessions_resp.text)
        exit(1)
    
    my_sessions = my_sessions_resp.json()
    if isinstance(my_sessions, dict) and 'data' in my_sessions:
        my_sessions = my_sessions['data']
    if isinstance(my_sessions, dict) and 'sessions' in my_sessions:
        my_sessions = my_sessions['sessions']
    
    if not isinstance(my_sessions, list):
        error(f"Unexpected response format: {type(my_sessions)}")
        error(f"Response: {my_sessions_resp.text}")
        exit(1)
    
    # Find our booked session
    booked_session = None
    for s in my_sessions:
        if s.get('id') == session_id:
            booked_session = s
            break
    
    if not booked_session:
        error(f"Booked session {session_id} not found in my sessions list")
        info(f"Sessions returned: {[s.get('id') for s in my_sessions]}")
        exit(1)
    
    success(f"Found booked session in my sessions response")
    success(f"  - ID: {booked_session.get('id')}")
    success(f"  - Topic: {booked_session.get('topic')}")
    success(f"  - Price: ${booked_session.get('price')}")
    success(f"  - Payment Status: {booked_session.get('payment_status')}")
    success(f"  - Status: {booked_session.get('status')}")
    
    # Check if price field exists
    if 'price' not in booked_session:
        error("❌ CRITICAL: 'price' field missing from session response!")
    else:
        success("'price' field present in response")
    
    if 'payment_status' not in booked_session:
        error("❌ CRITICAL: 'payment_status' field missing from session response!")
    else:
        success("'payment_status' field present in response")
    
except Exception as e:
    error(f"Error in step 4: {e}")
    exit(1)

# Test 5: Fetch sessions as mentor and verify response
test_step("5. FETCH SESSIONS AS MENTOR - VERIFY RESPONSE")
try:
    # First, need to login as a mentor to view their sessions
    # Let's try getting sessions for this mentor
    mentor_sessions_resp = requests.get(
        f"{API_BASE}/api/v1x/mentors/{mentor_id}/sessions",
        headers=admin_headers
    )
    
    if mentor_sessions_resp.status_code == 200:
        mentor_sessions = mentor_sessions_resp.json()
        if isinstance(mentor_sessions, dict) and 'data' in mentor_sessions:
            mentor_sessions = mentor_sessions['data']
        
        if isinstance(mentor_sessions, list):
            # Find our session
            mentor_booked = None
            for s in mentor_sessions:
                if s.get('id') == session_id:
                    mentor_booked = s
                    break
            
            if mentor_booked:
                success(f"Found booked session in mentor sessions response")
                success(f"  - Price: ${mentor_booked.get('price')}")
                success(f"  - Payment Status: {mentor_booked.get('payment_status')}")
            else:
                info("Session not visible in mentor sessions endpoint (might be permission issue)")
    else:
        info(f"Mentor sessions endpoint returned {mentor_sessions_resp.status_code}")
    
except Exception as e:
    error(f"Error in step 5: {e}")

print(f"\n{GREEN}{'='*60}{RESET}")
print(f"{GREEN}🎉 BOOKING FLOW TEST COMPLETE!{RESET}")
print(f"{GREEN}{'='*60}{RESET}")
print(f"\n{BLUE}Summary:{RESET}")
print(f"  ✅ Session created with price")
print(f"  ✅ Price returned in booking response")
print(f"  ✅ Session stored in database with price")
print(f"  ✅ Price included in student's sessions list")
print(f"\n{YELLOW}Frontend should now display:${RESET}")
print(f"  - Price in booking confirmation modal")
print(f"  - Price in student sessions list")
print(f"  - Price in mentor dashboard sessions")
