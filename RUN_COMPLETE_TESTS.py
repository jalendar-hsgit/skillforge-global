#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COMPREHENSIVE TEST EXECUTION & REPORT GENERATION
All 5 Revenue Features Testing with Full Results
"""

import requests
import json
from datetime import datetime, timedelta
import time
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_URL = "http://127.0.0.1:8001"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Test credentials (verified to exist in database)
CREDS = {
    "admin": ("admin@skillforge.com", "admin123"),
    "mentor": ("mentor.sarah@skillforge.com", "mentor123"),  # Correct!
    "student": ("charlie.brown@example.com", "charlie123"),  # Fresh student for cart tests
    "seller": ("jane.smith@example.com", "jane123"),          # Verified
}


def log_test(status, name, details=""):
    """Log test result"""
    symbol = "[PASS]" if status else "[FAIL]"
    msg = f"{symbol} {name}"
    if details:
        msg += f" - {details}"
    print(msg.encode('utf-8', 'replace').decode('utf-8'))
    return status


class TestRunner:
    def __init__(self):
        self.results = {}
        self.tokens = {}
        self.start_time = time.time()
        
    def get_token(self, role):
        """Get auth token"""
        try:
            email, password = CREDS[role]
            resp = requests.post(
                f"{BASE_URL}/api/v1x/auth/login",
                json={"email": email, "password": password},
                timeout=5
            )
            if resp.status_code == 200:
                # API returns: {"data": {"access_token": "..."}}
                return resp.json()["data"]["access_token"]
        except Exception as e:
            print(f"  Auth error for {role}: {str(e)}")
        return None
    
    def test_endpoint(self, name, method, endpoint, token=None, data=None, expected_status=200):
        """Test a single endpoint"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            if method == "GET":
                resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            else:
                resp = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=5)
            
            success = resp.status_code == expected_status or resp.status_code in [200, 201]
            return log_test(success, name, f"({resp.status_code})")
        except Exception as e:
            return log_test(False, name, str(e))
    
    def run_all(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("SKILLFORGE GLOBAL - COMPLETE FEATURE TEST SUITE")
        print("="*70)
        print(f"Timestamp: {TIMESTAMP}")
        print(f"API Base: {BASE_URL}\n")
        
        # Check API health
        try:
            requests.get(f"{BASE_URL}/health", timeout=5)
            print("[OK] API is running\n")
        except:
            print("[FAIL] API not responding!\n")
            return
        
        # Authenticate all roles
        print("AUTHENTICATION")
        print("-" * 70)
        for role in ["admin", "mentor", "student", "seller"]:
            token = self.get_token(role)
            if token:
                self.tokens[role] = token
                log_test(True, f"{role.upper()} auth", "")
            else:
                log_test(False, f"{role.upper()} auth", "")
        
        # Test each feature
        self.test_mentor_sessions()
        self.test_marketplace()
        self.test_subscriptions()
        self.test_courses()
        self.test_admin_payouts()
        
        # Summary
        self.print_summary()
    
    def test_mentor_sessions(self):
        """Test mentor sessions"""
        print("\n1. MENTOR SESSIONS ($150K/mo)")
        print("-" * 70)
        
        self.test_endpoint("List Mentors", "GET", "/api/v1x/mentors")
        self.test_endpoint("Mentor Detail", "GET", "/api/v1x/mentors/1")
        self.test_endpoint("Availability", "GET", "/api/v1x/mentors/availability/1")
        
        student_token = self.tokens.get("student")
        if student_token:
            future = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
            self.test_endpoint(
                "Create Session", "POST", "/api/v1x/mentors/sessions",
                token=student_token,
                data={
                    "mentor_id": 1,
                    "topic": "Python OOP",
                    "scheduled_at": future,
                    "duration_minutes": 60
                },
                expected_status=201
            )
            self.test_endpoint("My Sessions", "GET", "/api/v1x/mentors/sessions/my", token=student_token)
        
        mentor_token = self.tokens.get("mentor")
        if mentor_token:
            self.test_endpoint("Payout Summary", "GET", "/api/v1x/mentors/payouts/summary", token=mentor_token)
    
    def test_marketplace(self):
        """Test marketplace"""
        print("\n2. DIGITAL MARKETPLACE ($100K/mo)")
        print("-" * 70)
        
        self.test_endpoint("List Products", "GET", "/api/v1x/marketplace/digital-products")
        self.test_endpoint("Product Detail", "GET", "/api/v1x/marketplace/digital-products/1")
        
        student_token = self.tokens.get("student")
        if student_token:
            self.test_endpoint("View Cart", "GET", "/api/v1x/marketplace/cart", token=student_token)
            self.test_endpoint(
                "Add to Cart", "POST", "/api/v1x/marketplace/cart/add",
                token=student_token,
                data={"course_id": 3}
            )
        
        seller_token = self.tokens.get("seller")
        if seller_token:
            self.test_endpoint("Seller Dashboard", "GET", "/api/v1x/seller/dashboard", token=seller_token)
    
    def test_subscriptions(self):
        """Test subscriptions"""
        print("\n3. SUBSCRIPTIONS ($200K/mo)")
        print("-" * 70)
        
        self.test_endpoint("List Plans", "GET", "/api/v1x/subscriptions/plans")
        
        student_token = self.tokens.get("student")
        if student_token:
            self.test_endpoint("Current Subscription", "GET", "/api/v1x/subscriptions/current", token=student_token)
            self.test_endpoint("Features Access", "GET", "/api/v1x/subscriptions/features", token=student_token)
    
    def test_courses(self):
        """Test courses"""
        print("\n4. COURSE ENROLLMENT ($50K/mo)")
        print("-" * 70)
        
        self.test_endpoint("List Courses", "GET", "/api/v1/courses")
        self.test_endpoint("Course Detail", "GET", "/api/v1/courses/py-001")
        
        student_token = self.tokens.get("student")
        if student_token:
            self.test_endpoint("View Progress", "GET", "/api/v1/progress?path=python-ai", token=student_token)
            # Note: Course enrollment is managed through progress tracking, not a separate endpoint
    
    def test_admin_payouts(self):
        """Test admin payouts"""
        print("\n5. ADMIN PAYOUTS (Revenue Processing)")
        print("-" * 70)
        
        admin_token = self.tokens.get("admin")
        if admin_token:
            self.test_endpoint("Payout Stats", "GET", "/api/v1x/admin/payouts/stats", token=admin_token)
            self.test_endpoint("Pending Payouts", "GET", "/api/v1x/admin/payouts/pending", token=admin_token)
            self.test_endpoint("Unverified Methods", "GET", "/api/v1x/admin/payouts/payment-methods/unverified", token=admin_token)
    
    def print_summary(self):
        """Print test summary"""
        elapsed = time.time() - self.start_time
        
        print("\n" + "="*70)
        print("EXECUTION SUMMARY")
        print("="*70)
        print(f"Execution Time: {elapsed:.2f} seconds")
        print(f"Timestamp: {TIMESTAMP}")
        print("="*70 + "\n")


if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()
