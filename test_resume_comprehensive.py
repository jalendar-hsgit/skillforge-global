#!/usr/bin/env python
"""Comprehensive Resume Module Test Suite"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1x"

def log(msg, status="INFO"):
    """Print log with timestamp"""
    prefix = {
        "INFO": "[INFO]",
        "OK": "[PASS]",
        "FAIL": "[FAIL]",
        "TEST": "[TEST]"
    }.get(status, "[LOG]")
    print(f"{prefix} {msg}")

def setup_test_user():
    """Create and login test user"""
    log("Setting up test user...", "TEST")
    
    user_email = f"test_{int(datetime.now().timestamp())}@test.com"
    password = "TestPassword123!"
    
    # Signup
    requests.post(
        f"{BASE_URL}/api/v1/auth/signup",
        json={"email": user_email, "password": password, "name": "Test User"}
    )
    
    # Login
    login_resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": user_email, "password": password}
    )
    
    if login_resp.status_code != 200:
        log(f"Login failed: {login_resp.text}", "FAIL")
        return None, None
    
    cookies = login_resp.cookies
    log(f"User created and logged in: {user_email}", "OK")
    return cookies, user_email

def test_session_endpoints(cookies):
    """Test all session endpoints"""
    log("Testing Session Endpoints", "TEST")
    
    tests = []
    
    # Test /session/me
    resp = requests.get(f"{API_BASE}/session/me", cookies=cookies)
    tests.append(("GET /session/me", resp.status_code == 200, resp.status_code))
    
    # Test /session/resumes (should be empty initially)
    resp = requests.get(f"{API_BASE}/session/resumes", cookies=cookies)
    tests.append(("GET /session/resumes", resp.status_code == 200, resp.status_code))
    
    for name, passed, code in tests:
        status = "OK" if passed else "FAIL"
        log(f"  {name}: {code}", status)
    
    return all(p for _, p, _ in tests)

def test_resume_crud(cookies, user_email):
    """Test CRUD operations"""
    log("Testing Resume CRUD Operations", "TEST")
    
    results = {}
    
    # CREATE
    create_data = {
        "title": "Test Resume",
        "full_name": "Test User",
        "email": user_email,
        "phone": "+1234567890",
        "professional_summary": "Test summary",
        "template": "modern"
    }
    resp = requests.post(f"{API_BASE}/session/resumes", json=create_data, cookies=cookies)
    create_ok = resp.status_code in [200, 201]
    results["CREATE"] = create_ok
    log(f"  POST /session/resumes: {resp.status_code}", "OK" if create_ok else "FAIL")
    
    if not create_ok:
        return results
    
    resume_id = resp.json().get("id")
    log(f"    Created resume ID: {resume_id}", "OK")
    
    # READ
    resp = requests.get(f"{API_BASE}/session/resumes/{resume_id}", cookies=cookies)
    read_ok = resp.status_code == 200
    results["READ"] = read_ok
    log(f"  GET /session/resumes/{resume_id}: {resp.status_code}", "OK" if read_ok else "FAIL")
    
    # UPDATE
    update_data = {
        "professional_summary": "Updated summary",
        "phone": "+9876543210"
    }
    resp = requests.patch(f"{API_BASE}/session/resumes?id={resume_id}", json=update_data, cookies=cookies)
    update_ok = resp.status_code == 200
    results["UPDATE"] = update_ok
    log(f"  PATCH /session/resumes?id={resume_id}: {resp.status_code}", "OK" if update_ok else "FAIL")
    
    if update_ok:
        updated = resp.json()
        version_ok = updated.get("version", 0) > 1
        results["VERSION_INCREMENT"] = version_ok
        log(f"    Version incremented: {updated.get('version')}", "OK" if version_ok else "FAIL")
    
    # LIST
    resp = requests.get(f"{API_BASE}/session/resumes", cookies=cookies)
    list_ok = resp.status_code == 200 and len(resp.json()) > 0
    results["LIST"] = list_ok
    log(f"  GET /session/resumes: {resp.status_code}", "OK" if list_ok else "FAIL")
    if list_ok:
        log(f"    Found {len(resp.json())} resume(s)", "OK")
    
    # DELETE
    resp = requests.delete(f"{API_BASE}/session/resumes?id={resume_id}", cookies=cookies)
    delete_ok = resp.status_code in [200, 204]
    results["DELETE"] = delete_ok
    log(f"  DELETE /session/resumes?id={resume_id}: {resp.status_code}", "OK" if delete_ok else "FAIL")
    
    return results

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SKILLFORGE RESUME MODULE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Timestamp: {datetime.now()}")
    print(f"API Base: {API_BASE}\n")
    
    # Setup
    cookies, user_email = setup_test_user()
    if not cookies:
        log("Failed to setup test user", "FAIL")
        sys.exit(1)
    
    print()
    
    # Tests
    session_ok = test_session_endpoints(cookies)
    print()
    crud_results = test_resume_crud(cookies, user_email)
    
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_ok = session_ok and all(crud_results.values())
    
    for test_name, passed in crud_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name:20}: {status}")
    
    print()
    if all_ok:
        print("SUCCESS: All resume tests passed!")
        print("The resume module is working correctly.")
        return 0
    else:
        print("FAILURE: Some tests failed.")
        print("Check details above for more information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
