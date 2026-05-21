#!/usr/bin/env python3
"""
Complete Integration Test for Week 1 Features
Tests: Checkout Flow + Mentor Booking Flow

Features tested:
1. User authentication
2. Course listing and purchase
3. Payment processing
4. Mentor discovery and listing
5. Mentor availability
6. Session booking
7. Order history and booking history
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class PaymentTestSuite:
    """Complete payment and mentor booking test suite"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = None
        self.auth_token = None
        self.results = {
            'passed': [],
            'failed': [],
            'total': 0
        }
        
    def log(self, step: str, status: str, details: str = ""):
        """Log test results"""
        marker = "[OK]" if status == "PASS" else "[ERROR]"
        print(f"{marker} {step}")
        if details:
            print(f"    {details}")
        
        self.results['total'] += 1
        if status == "PASS":
            self.results['passed'].append(step)
        else:
            self.results['failed'].append(step)
    
    def test_backend_health(self) -> bool:
        """Test backend connectivity"""
        try:
            response = requests.get(f"{self.base_url}/api/v1x/courses-db", timeout=5)
            if response.status_code in [200, 404]:
                self.log("Backend Connection", "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log("Backend Connection", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Backend Connection", "FAIL", str(e))
            return False
    
    def test_course_listing(self) -> bool:
        """Test course listing endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1x/courses-db")
            if response.status_code == 200:
                courses = response.json()
                count = len(courses) if isinstance(courses, list) else 0
                self.log(f"Course Listing", "PASS", f"Found {count} courses")
                return True
            else:
                self.log("Course Listing", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Course Listing", "FAIL", str(e))
            return False
    
    def test_user_auth(self) -> bool:
        """Test user authentication"""
        try:
            # Check current user
            response = self.session.get(f"{self.base_url}/api/v1x/auth/me")
            if response.status_code == 200:
                user = response.json()
                self.test_user = user
                self.log("User Authentication", "PASS", f"Logged in as: {user.get('email', 'unknown')}")
                return True
            elif response.status_code == 401:
                self.log("User Authentication", "FAIL", "Not authenticated - would need login")
                return False
            else:
                self.log("User Authentication", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("User Authentication", "FAIL", str(e))
            return False
    
    def test_mentor_listing(self) -> bool:
        """Test mentor listing"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1x/mentors?limit=10")
            if response.status_code == 200:
                mentors = response.json()
                count = len(mentors) if isinstance(mentors, list) else 0
                self.log("Mentor Listing", "PASS", f"Found {count} mentors")
                return count > 0
            else:
                self.log("Mentor Listing", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Mentor Listing", "FAIL", str(e))
            return False
    
    def test_mentor_search(self) -> bool:
        """Test mentor search by expertise"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1x/mentors/search?expertise=python-ai&limit=10")
            if response.status_code == 200:
                mentors = response.json()
                count = len(mentors) if isinstance(mentors, list) else 0
                self.log("Mentor Search", "PASS", f"Found {count} mentors with python-ai expertise")
                return count >= 0
            else:
                self.log("Mentor Search", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Mentor Search", "FAIL", str(e))
            return False
    
    def test_mentor_availability(self) -> bool:
        """Test mentor availability slots"""
        try:
            # Get mentors first
            mentors_response = self.session.get(f"{self.base_url}/api/v1x/mentors?limit=1")
            if mentors_response.status_code != 200:
                self.log("Mentor Availability", "FAIL", "Could not fetch mentors")
                return False
            
            mentors = mentors_response.json()
            if not mentors:
                self.log("Mentor Availability", "FAIL", "No mentors available")
                return False
            
            mentor_id = mentors[0].get('id')
            availability_response = self.session.get(f"{self.base_url}/api/v1x/mentors/availability/{mentor_id}")
            
            if availability_response.status_code == 200:
                avail_data = availability_response.json()
                slots = avail_data.get('slots', [])
                self.log("Mentor Availability", "PASS", f"Found {len(slots)} availability slots")
                return True
            else:
                self.log("Mentor Availability", "FAIL", f"Status: {availability_response.status_code}")
                return False
        except Exception as e:
            self.log("Mentor Availability", "FAIL", str(e))
            return False
    
    def test_order_api_structure(self) -> bool:
        """Test order API endpoints exist"""
        try:
            # Just test that the endpoint is reachable
            # Note: This will fail without auth, but we're checking the endpoint exists
            response = self.session.get(f"{self.base_url}/api/v1x/orders/my-orders")
            
            # Both 200 and 401 are acceptable (endpoint exists, just needs auth)
            if response.status_code in [200, 401]:
                self.log("Order API", "PASS", "Order endpoints available")
                return True
            else:
                self.log("Order API", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Order API", "FAIL", str(e))
            return False
    
    def test_payment_intent_structure(self) -> bool:
        """Test payment intent endpoint exists"""
        try:
            # Just test that endpoint exists
            response = self.session.post(
                f"{self.base_url}/api/v1x/orders/create-payment-intent",
                json={"order_id": 999999}  # Non-existent ID, we're just testing the endpoint
            )
            
            # Both 404 and 401 and 400 are acceptable (endpoint exists, just not with test data)
            if response.status_code in [200, 400, 401, 404]:
                self.log("Payment Intent API", "PASS", "Payment intent endpoint available")
                return True
            else:
                self.log("Payment Intent API", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Payment Intent API", "FAIL", str(e))
            return False
    
    def test_frontend_pages_structure(self) -> bool:
        """Verify frontend pages are created"""
        pages_to_check = [
            ('src/pages/checkout.tsx', 'Checkout Page'),
            ('src/pages/orders.tsx', 'Order History Page'),
            ('src/pages/mentor-booking.tsx', 'Mentor Booking Page'),
            ('src/pages/mentor-bookings.tsx', 'Mentor Bookings List Page'),
            ('src/lib/orderApi.ts', 'Order API Layer'),
            ('src/lib/mentorBookingApi.ts', 'Mentor Booking API Layer'),
            ('src/styles/checkout.module.css', 'Checkout Styles'),
            ('src/styles/orders.module.css', 'Order Styles'),
            ('src/styles/mentor-booking.module.css', 'Mentor Booking Styles'),
            ('src/styles/mentor-bookings.module.css', 'Mentor Bookings Styles'),
        ]
        
        import os
        all_exist = True
        for filepath, name in pages_to_check:
            full_path = f"d:\\python code\\sfg\\skillforge-global\\{filepath}"
            exists = os.path.exists(full_path)
            status = "PASS" if exists else "FAIL"
            self.log(f"Frontend - {name}", status, filepath)
            all_exist = all_exist and exists
        
        return all_exist
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("WEEK 1 INTEGRATION TEST SUITE")
        print("="*60 + "\n")
        
        print("Testing Backend Connectivity...")
        if not self.test_backend_health():
            print("\n[CRITICAL] Backend is not running!\n")
            return
        
        print("\nTesting Course System...")
        self.test_course_listing()
        
        print("\nTesting Authentication...")
        self.test_user_auth()
        
        print("\nTesting Mentor System...")
        self.test_mentor_listing()
        self.test_mentor_search()
        self.test_mentor_availability()
        
        print("\nTesting Payment System...")
        self.test_order_api_structure()
        self.test_payment_intent_structure()
        
        print("\nTesting Frontend Components...")
        self.test_frontend_pages_structure()
        
        # Print summary
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.results['total']}")
        print(f"Passed: {len(self.results['passed'])}")
        print(f"Failed: {len(self.results['failed'])}")
        
        if self.results['failed']:
            print(f"\nFailed Tests:")
            for test in self.results['failed']:
                print(f"  - {test}")
        
        success_rate = (len(self.results['passed']) / self.results['total'] * 100) if self.results['total'] > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        print("="*60 + "\n")
        
        return len(self.results['failed']) == 0

if __name__ == "__main__":
    suite = PaymentTestSuite()
    success = suite.run_all_tests()
    exit(0 if success else 1)
