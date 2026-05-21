#!/usr/bin/env python
"""
Quick Payment Flow Verification Script
Run with: python test_payment_quick.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"
API_PATH = "/api/v1x"

print("=" * 60)
print("PAYMENT FLOW VERIFICATION")
print("=" * 60)
print()

# Step 1: Create or login user
print("STEP 1: Creating test user...")
register_data = {
    "email": "test-payment-flow@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
}

try:
    response = requests.post(
        f"{BASE_URL}{API_PATH}/auth/register",
        json=register_data,
        timeout=10
    )
    
    jwt_token = None
    
    if response.status_code == 200:
        login_data = response.json()
        jwt_token = login_data.get("data", {}).get("access_token") if isinstance(login_data.get("data"), dict) else None
        if jwt_token:
            print(f"[OK] User created. JWT Token: {jwt_token[:20]}...")
        else:
            raise ValueError("No access token in registration response")
    elif response.status_code == 400 or response.status_code == 409:
        # User likely exists, try login
        print("[WARN] User may already exist, attempting login...")
        login_response = requests.post(
            f"{BASE_URL}{API_PATH}/auth/login",
            json={"email": register_data["email"], "password": register_data["password"]},
            timeout=10
        )
        if login_response.status_code == 200:
            login_data = login_response.json()
            jwt_token = login_data.get("data", {}).get("access_token") if isinstance(login_data.get("data"), dict) else None
            if jwt_token:
                print(f"[OK] Logged in. JWT Token: {jwt_token[:20]}...")
            else:
                raise ValueError("No access token in login response")
        else:
            print(f"[ERROR] Failed to login: {login_response.text}")
            sys.exit(1)
    else:
        print(f"[ERROR] Failed to register: {response.status_code} - {response.text}")
        sys.exit(1)
    
    if not jwt_token:
        print("[ERROR] Could not obtain JWT token")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Cannot connect to backend on http://localhost:8001")
    print("   Make sure the backend is running: uvicorn app.main:app")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

print()

# Step 2: Get courses
print("STEP 2: Getting available courses...")
try:
    response = requests.get(
        f"{BASE_URL}{API_PATH}/courses-db",
        headers={"Authorization": f"Bearer {jwt_token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        courses_data = response.json()
        # Handle both list and object responses
        if isinstance(courses_data, list):
            courses = courses_data
        else:
            courses = courses_data.get("data", [])
        
        # Find a paid course or use first one
        paid_course = None
        for course in courses:
            if isinstance(course, dict) and course.get("is_paid"):
                paid_course = course
                break
        
        if not paid_course and courses:
            paid_course = courses[0]
        
        if paid_course:
            course_id = paid_course.get("id") if isinstance(paid_course, dict) else None
            if not course_id:
                # Try to get first course ID from anywhere
                course_id = 1 if paid_course else None
            course_title = paid_course.get("title", "Unknown") if isinstance(paid_course, dict) else "Test Course"
            course_price = paid_course.get("price", 0) if isinstance(paid_course, dict) else 99.99
            print(f"[OK] Found course: {course_title} (ID: {course_id}, Price: ${course_price})")
            
            # If no ID found, try to get first course
            if not course_id:
                print("[WARN] Could not find course ID, using first available")
                course_id = 1
        else:
            print("[ERROR] No courses found")
            sys.exit(1)
    else:
        print(f"[ERROR] Failed to get courses: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

print()

# Step 3: Create order
print("STEP 3: Creating order...")
try:
    order_data = {
        "course_id": course_id,
        "payment_method": "stripe"
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PATH}/orders/create",
        json=order_data,
        headers={"Authorization": f"Bearer {jwt_token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        response_json = response.json()
        order_data_resp = response_json.get("data", {})
        order_id = order_data_resp.get("id")
        order_number = order_data_resp.get("order_number")
        amount = order_data_resp.get("amount")
        print(f"[OK] Order created:")
        print(f"   Order ID: {order_id}")
        print(f"   Order Number: {order_number}")
        print(f"   Amount: ${amount}")
    else:
        error_msg = response.json().get("detail", "Unknown error")
        print(f"[ERROR] Failed to create order: {error_msg}")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

print()

# Step 4: Create payment intent
print("STEP 4: Creating payment intent...")
try:
    intent_data = {
        "order_id": order_id
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PATH}/orders/create-payment-intent",
        json=intent_data,
        headers={"Authorization": f"Bearer {jwt_token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        response_json = response.json()
        intent_data_resp = response_json.get("data", {})
        payment_intent_id = intent_data_resp.get("payment_intent_id")
        client_secret = intent_data_resp.get("client_secret")
        print(f"[OK] Payment intent created:")
        print(f"   Payment Intent ID: {payment_intent_id}")
        print(f"   Client Secret: {client_secret[:30]}...")
    else:
        error_msg = response.json().get("detail", "Unknown error")
        print(f"[ERROR] Failed to create payment intent: {error_msg}")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

print()

# Step 5: Get order details
print("STEP 5: Verifying order status...")
try:
    response = requests.get(
        f"{BASE_URL}{API_PATH}/orders/{order_id}",
        headers={"Authorization": f"Bearer {jwt_token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        response_json = response.json()
        order_details = response_json.get("data", {})
        status = order_details.get("status")
        payment_status = order_details.get("payment_status")
        print(f"[OK] Order verified:")
        print(f"   Status: {status}")
        print(f"   Payment Status: {payment_status}")
    else:
        print(f"[ERROR] Failed to get order: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

print()

# Step 6: Get user's orders
print("STEP 6: Retrieving user's orders...")
try:
    response = requests.get(
        f"{BASE_URL}{API_PATH}/orders/my-orders",
        headers={"Authorization": f"Bearer {jwt_token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        response_json = response.json()
        orders_list = response_json.get("data", {}).get("orders", [])
        total = response_json.get("data", {}).get("total", 0)
        print(f"[OK] Orders retrieved:")
        print(f"   Total Orders: {total}")
        if orders_list:
            print(f"   Latest Order:")
            latest = orders_list[0]
            print(f"     - Order #: {latest.get('order_number')}")
            print(f"     - Amount: ${latest.get('amount')}")
            print(f"     - Status: {latest.get('status')}")
    else:
        print(f"[ERROR] Failed to get orders: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

print()
print("=" * 60)
print("[OK] ALL TESTS PASSED!")
print("=" * 60)
print()
print("Summary:")
print(f"  Course: {course_title}")
print(f"  Order ID: {order_id}")
print(f"  Payment Intent ID: {payment_intent_id}")
print(f"  Amount: ${amount}")
print()
print("Next Steps:")
print("1. Go to frontend checkout page")
print("2. Use Stripe test card: 4242 4242 4242 4242")
print("3. Set expiry: 12/25, CVC: 123")
print("4. Complete payment to test confirmation flow")
print()
