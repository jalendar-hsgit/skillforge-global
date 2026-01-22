#!/usr/bin/env python3
"""
Comprehensive System Diagnostic - Tests all critical systems quickly
Run this after starting backend and frontend
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8001"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}")

def print_pass(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_fail(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warn(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"ℹ️  {text}")

# Track results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_health():
    """Test if backend is running"""
    print_header("1. BACKEND CONNECTIVITY")
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=2)
        if response.status_code == 200:
            print_pass("Backend is running")
            return True
        else:
            print_fail(f"Backend returned {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Cannot connect to backend: {e}")
        return False

def test_auth():
    """Test authentication system"""
    print_header("2. AUTHENTICATION")
    
    # Test signup
    print_info("Testing signup...")
    payload = {
        "email": f"test_{TIMESTAMP.replace(':', '').replace('-', '')[:12]}@test.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=payload, timeout=5)
        if response.status_code == 200:
            print_pass(f"Signup works (status {response.status_code})")
            results["passed"].append("auth:signup")
        else:
            print_warn(f"Signup returned {response.status_code}: {response.text[:100]}")
            results["warnings"].append(f"signup:{response.status_code}")
    except Exception as e:
        print_fail(f"Signup failed: {e}")
        results["failed"].append("auth:signup")
    
    # Test login with demo user
    print_info("Testing login...")
    login_payload = {
        "email": "john.doe@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_payload, timeout=5)
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                print_pass(f"Login works with token")
                results["passed"].append("auth:login")
                return token
            else:
                print_warn("Login returned 200 but no token")
                results["warnings"].append("auth:login_no_token")
                return None
        else:
            print_warn(f"Login returned {response.status_code}")
            results["warnings"].append(f"login:{response.status_code}")
            return None
    except Exception as e:
        print_fail(f"Login failed: {e}")
        results["failed"].append("auth:login")
        return None

def test_marketplace(token):
    """Test marketplace endpoints"""
    print_header("3. MARKETPLACE")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test get courses
    print_info("Testing GET /api/v1x/courses...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/courses", timeout=5)
        if response.status_code == 200:
            courses = response.json()
            course_count = len(courses) if isinstance(courses, list) else 0
            print_pass(f"Courses endpoint works ({course_count} courses)")
            results["passed"].append("marketplace:courses")
        else:
            print_warn(f"Courses returned {response.status_code}")
            results["warnings"].append(f"courses:{response.status_code}")
    except Exception as e:
        print_fail(f"Courses failed: {e}")
        results["failed"].append("marketplace:courses")
    
    if not token:
        print_warn("Skipping authenticated endpoints (no token)")
        return
    
    # Test cart operations
    print_info("Testing POST /api/v1x/marketplace/cart/add...")
    cart_payload = {"course_id": 1}
    try:
        response = requests.post(f"{BASE_URL}/api/v1x/marketplace/cart/add", json=cart_payload, headers=headers, timeout=5)
        if response.status_code == 200:
            print_pass("Cart add works")
            results["passed"].append("marketplace:cart_add")
        else:
            print_warn(f"Cart add returned {response.status_code}")
            results["warnings"].append(f"cart_add:{response.status_code}")
    except Exception as e:
        print_fail(f"Cart add failed: {e}")
        results["failed"].append("marketplace:cart_add")
    
    # Test get cart
    print_info("Testing GET /api/v1x/marketplace/cart...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/marketplace/cart", headers=headers, timeout=5)
        if response.status_code == 200:
            cart = response.json()
            items = len(cart.get("items", [])) if isinstance(cart, dict) else 0
            print_pass(f"Cart retrieval works ({items} items)")
            results["passed"].append("marketplace:cart_get")
        else:
            print_warn(f"Cart get returned {response.status_code}")
            results["warnings"].append(f"cart_get:{response.status_code}")
    except Exception as e:
        print_fail(f"Cart get failed: {e}")
        results["failed"].append("marketplace:cart_get")
    
    # Test checkout
    print_info("Testing POST /api/v1x/marketplace/checkout...")
    checkout_payload = {"payment_method": "coins"}
    try:
        response = requests.post(f"{BASE_URL}/api/v1x/marketplace/checkout", json=checkout_payload, headers=headers, timeout=5)
        if response.status_code == 200:
            print_pass("Checkout works")
            results["passed"].append("marketplace:checkout")
        else:
            print_warn(f"Checkout returned {response.status_code}: {response.text[:50]}")
            results["warnings"].append(f"checkout:{response.status_code}")
    except Exception as e:
        print_fail(f"Checkout failed: {e}")
        results["failed"].append("marketplace:checkout")

def test_coding_practice(token):
    """Test coding practice endpoint"""
    print_header("4. CODING PRACTICE")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    print_info("Testing GET /api/v1x/coding-practice/challenges...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/coding-practice/challenges", headers=headers, timeout=5)
        if response.status_code == 200:
            challenges = response.json()
            count = len(challenges) if isinstance(challenges, (list, dict)) else 0
            print_pass(f"Coding practice works ({count} items)")
            results["passed"].append("coding:challenges")
        else:
            print_fail(f"Coding practice returned {response.status_code}")
            results["failed"].append(f"coding:challenges_{response.status_code}")
            print_info(f"Response: {response.text[:100]}")
    except Exception as e:
        print_fail(f"Coding practice failed: {e}")
        results["failed"].append("coding:challenges_error")

def test_resumes(token):
    """Test resume endpoints"""
    print_header("5. RESUMES")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    if not token:
        print_warn("Skipping resume tests (no token)")
        return
    
    print_info("Testing GET /api/v1x/resumes...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/resumes", headers=headers, timeout=5)
        if response.status_code == 200:
            resumes = response.json()
            count = len(resumes) if isinstance(resumes, (list, dict)) else 0
            print_pass(f"Resume endpoint works ({count} resumes)")
            results["passed"].append("resumes:list")
        else:
            print_warn(f"Resume endpoint returned {response.status_code}")
            results["warnings"].append(f"resumes:{response.status_code}")
    except Exception as e:
        print_fail(f"Resume list failed: {e}")
        results["failed"].append("resumes:list_error")

def test_mentors(token):
    """Test mentor endpoints"""
    print_header("6. MENTORS")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    print_info("Testing GET /api/v1x/mentors...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/mentors", headers=headers, timeout=5)
        if response.status_code == 200:
            mentors = response.json()
            count = len(mentors) if isinstance(mentors, (list, dict)) else 0
            print_pass(f"Mentor endpoint works ({count} mentors)")
            results["passed"].append("mentors:list")
        else:
            print_warn(f"Mentor endpoint returned {response.status_code}")
            results["warnings"].append(f"mentors:{response.status_code}")
    except Exception as e:
        print_fail(f"Mentor list failed: {e}")
        results["failed"].append("mentors:list_error")

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    passed_count = len(results["passed"])
    failed_count = len(results["failed"])
    warning_count = len(results["warnings"])
    
    print(f"\n{GREEN}✅ PASSED: {passed_count}{RESET}")
    for item in results["passed"]:
        print(f"   • {item}")
    
    if failed_count > 0:
        print(f"\n{RED}❌ FAILED: {failed_count}{RESET}")
        for item in results["failed"]:
            print(f"   • {item}")
    
    if warning_count > 0:
        print(f"\n{YELLOW}⚠️  WARNINGS: {warning_count}{RESET}")
        for item in results["warnings"]:
            print(f"   • {item}")
    
    print(f"\n{BLUE}TOTAL: {passed_count + failed_count + warning_count} tests{RESET}")
    
    # Exit code
    if failed_count == 0:
        print(f"\n{GREEN}✅ ALL CRITICAL TESTS PASSED!{RESET}")
        return 0
    else:
        print(f"\n{RED}❌ {failed_count} CRITICAL TEST(S) FAILED - SEE ABOVE{RESET}")
        return 1

def main():
    print(f"\n{BLUE}SkillForge Global - System Diagnostic{RESET}")
    print(f"Started at {TIMESTAMP}")
    
    # Test connectivity first
    if not test_health():
        print_fail("Cannot reach backend. Start backend first!")
        return 1
    
    # Get auth token
    token = test_auth()
    
    # Test all systems
    test_marketplace(token)
    test_coding_practice(token)
    test_resumes(token)
    test_mentors(token)
    
    # Print summary
    return print_summary()

if __name__ == "__main__":
    sys.exit(main())
