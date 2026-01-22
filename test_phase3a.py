#!/usr/bin/env python3
"""
Phase 3A Mentor Verification API Test Script
Tests the mentor document upload and approval endpoints
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8001"
MENTOR_EMAIL = "mentor.sarah@skillforge.com"
MENTOR_PASSWORD = "mentor123"
ADMIN_EMAIL = "admin@skillforge.com"
ADMIN_PASSWORD = "admin123"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

def log_success(message):
    print(f"{GREEN}✅ {message}{END}")

def log_error(message):
    print(f"{RED}❌ {message}{END}")

def log_info(message):
    print(f"{BLUE}ℹ️  {message}{END}")

def log_warning(message):
    print(f"{YELLOW}⚠️  {message}{END}")

def login(email, password):
    """Login and return session with token as cookie"""
    log_info(f"Logging in as {email}...")
    session = requests.Session()
    response = session.post(
        f"{API_BASE}/api/v1x/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code != 200:
        log_error(f"Login failed: {response.text}")
        return None, None
    
    data = response.json()
    if data.get("logged"):
        log_success(f"Logged in as {email}")
        # Token is in cookie, session will handle it automatically
        return session, response.cookies.get("token")
    else:
        log_error(f"Login failed: {data}")
        return None, None

def test_mentor_endpoints(mentor_session, mentor_token):
    """Test mentor-side endpoints"""
    print(f"\n{BLUE}{'='*60}")
    print("TESTING MENTOR ENDPOINTS")
    print(f"{'='*60}{END}\n")
    
    # Test 1: Get mentor's documents
    log_info("Testing GET /api/v1x/mentor-documents/my-documents...")
    response = mentor_session.get(
        f"{API_BASE}/api/v1x/mentor-documents/my-documents"
    )
    
    if response.status_code == 200:
        data = response.json()
        log_success(f"Retrieved documents: {data['total']} total, {data['pending']} pending")
    else:
        log_error(f"Failed to get documents: {response.status_code} - {response.text}")
    
    # Test 2: Create a test file
    log_info("Creating test file...")
    test_file_path = Path("test_document.txt")
    test_file_path.write_text("This is a test document for mentor verification.")
    
    # Test 3: Upload document
    log_info("Testing POST /api/v1x/mentor-documents/upload...")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'document_type': 'certification'}
            response = mentor_session.post(
                f"{API_BASE}/api/v1x/mentor-documents/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            log_success(f"Document uploaded: {result['document_id']}")
            doc_id = result['document_id']
            
            # Test 4: Get documents again (should see the new one)
            response = mentor_session.get(
                f"{API_BASE}/api/v1x/mentor-documents/my-documents"
            )
            
            if response.status_code == 200:
                data = response.json()
                log_success(f"After upload: {data['total']} total, {data['pending']} pending")
            
            return doc_id
        else:
            log_error(f"Upload failed: {response.status_code} - {response.text}")
            return None
    finally:
        test_file_path.unlink()

def test_admin_endpoints(admin_session, admin_token, doc_id):
    """Test admin-side endpoints"""
    print(f"\n{BLUE}{'='*60}")
    print("TESTING ADMIN ENDPOINTS")
    print(f"{'='*60}{END}\n")
    
    # Test 1: Get pending verifications
    log_info("Testing GET /api/v1x/mentor-documents/pending...")
    response = admin_session.get(
        f"{API_BASE}/api/v1x/mentor-documents/pending"
    )
    
    if response.status_code == 200:
        data = response.json()
        log_success(f"Retrieved pending verifications: {data['total']} mentors pending")
        if data['pending_verifications']:
            for v in data['pending_verifications']:
                print(f"  - {v['mentor_name']}: {v['pending_count']} documents")
    else:
        log_error(f"Failed to get pending: {response.status_code} - {response.text}")
        return
    
    if not doc_id:
        log_warning("No document ID to test approval/rejection")
        return
    
    # Test 2: Approve document
    log_info(f"Testing PATCH /api/v1x/mentor-documents/{doc_id}/approve...")
    response = admin_session.patch(
        f"{API_BASE}/api/v1x/mentor-documents/{doc_id}/approve",
        json={"reason": "Great credentials!"}
    )
    
    if response.status_code == 200:
        result = response.json()
        log_success(f"Document approved: {result['approval_id']}")
    else:
        log_error(f"Approval failed: {response.status_code} - {response.text}")

def main():
    print(f"\n{BLUE}{'='*60}")
    print("PHASE 3A: MENTOR VERIFICATION API TESTS")
    print(f"{'='*60}{END}\n")
    
    # Login as mentor
    mentor_session, mentor_token = login(MENTOR_EMAIL, MENTOR_PASSWORD)
    if not mentor_session:
        log_error("Failed to login as mentor")
        sys.exit(1)
    
    # Login as admin
    admin_session, admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_session:
        log_error("Failed to login as admin")
        sys.exit(1)
    
    # Test mentor endpoints
    doc_id = test_mentor_endpoints(mentor_session, mentor_token)
    
    # Test admin endpoints
    test_admin_endpoints(admin_session, admin_token, doc_id)
    
    print(f"\n{GREEN}{'='*60}")
    print("ALL TESTS COMPLETED")
    print(f"{'='*60}{END}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"Test failed with exception: {e}")
        sys.exit(1)
