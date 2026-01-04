#!/usr/bin/env python3
"""
Resume API Test Suite - Comprehensive testing of all resume endpoints
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8001"

class ResumeAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.user_id = None
        self.resume_id = None
        self.results = []
    
    def log(self, endpoint: str, method: str, status: int, message: str, data: Any = None):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "message": message,
            "data": data
        }
        self.results.append(result)
        status_emoji = "✅" if 200 <= status < 300 else "❌"
        print(f"{status_emoji} [{method}] {endpoint} - {status}: {message}")
        if data and status >= 400:
            print(f"   Details: {data}")
    
    def test_session_endpoint(self):
        """Test /api/v1x/session/me endpoint"""
        print("\n=== Testing Session Endpoints ===")
        try:
            # Note: This requires authentication which is not set up in this test
            # In production, you would have a valid session cookie
            resp = requests.get(f"{self.base_url}/api/v1x/session/me")
            self.log("/api/v1x/session/me", "GET", resp.status_code, 
                    "Get current user", resp.json() if resp.status_code < 400 else resp.text)
        except Exception as e:
            self.log("/api/v1x/session/me", "GET", 500, f"Error: {str(e)}")
    
    def test_resume_list_endpoint(self):
        """Test /api/v1x/resumes GET endpoint"""
        print("\n=== Testing Resume List Endpoint ===")
        try:
            resp = self.session.get(f"{self.base_url}/api/v1x/resumes")
            self.log("/api/v1x/resumes", "GET", resp.status_code,
                    "List resumes",  resp.json() if resp.status_code < 400 else resp.text)
        except Exception as e:
            self.log("/api/v1x/resumes", "GET", 500, f"Error: {str(e)}")
    
    def test_resume_create(self):
        """Test /api/v1x/resumes POST endpoint"""
        print("\n=== Testing Resume Create Endpoint ===")
        payload = {
            "title": "Test Resume",
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1-555-0000",
            "template": "modern"
        }
        try:
            resp = self.session.post(
                f"{self.base_url}/api/v1x/resumes",
                json=payload
            )
            self.log("/api/v1x/resumes", "POST", resp.status_code,
                    "Create resume", resp.json() if resp.status_code < 400 else resp.text)
            if resp.status_code == 201 and "id" in resp.json():
                self.resume_id = resp.json()["id"]
        except Exception as e:
            self.log("/api/v1x/resumes", "POST", 500, f"Error: {str(e)}")
    
    def test_resume_get(self):
        """Test /api/v1x/resumes/{id} GET endpoint"""
        if not self.resume_id:
            print("⏭️  Skipping GET test - no resume_id from create")
            return
        
        print("\n=== Testing Resume Get Endpoint ===")
        try:
            resp = self.session.get(f"{self.base_url}/api/v1x/resumes/{self.resume_id}")
            self.log(f"/api/v1x/resumes/{self.resume_id}", "GET", resp.status_code,
                    "Get resume", resp.json() if resp.status_code < 400 else resp.text)
        except Exception as e:
            self.log(f"/api/v1x/resumes/{self.resume_id}", "GET", 500, f"Error: {str(e)}")
    
    def test_resume_update(self):
        """Test /api/v1x/resumes/{id} PATCH endpoint"""
        if not self.resume_id:
            print("⏭️  Skipping PATCH test - no resume_id from create")
            return
        
        print("\n=== Testing Resume Update Endpoint ===")
        payload = {
            "title": "Updated Test Resume",
            "professional_summary": "A test professional summary"
        }
        try:
            resp = self.session.patch(
                f"{self.base_url}/api/v1x/resumes/{self.resume_id}",
                json=payload
            )
            self.log(f"/api/v1x/resumes/{self.resume_id}", "PATCH", resp.status_code,
                    "Update resume", resp.json() if resp.status_code < 400 else resp.text)
        except Exception as e:
            self.log(f"/api/v1x/resumes/{self.resume_id}", "PATCH", 500, f"Error: {str(e)}")
    
    def test_session_resume_endpoints(self):
        """Test /api/v1x/session/resumes endpoints"""
        print("\n=== Testing Session Resume Endpoints ===")
        try:
            # List via session
            resp = self.session.get(f"{self.base_url}/api/v1x/session/resumes")
            self.log("/api/v1x/session/resumes", "GET", resp.status_code,
                    "List resumes via session", resp.json() if resp.status_code < 400 else resp.text)
        except Exception as e:
            self.log("/api/v1x/session/resumes", "GET", 500, f"Error: {str(e)}")
        
        if self.resume_id:
            try:
                # Get via session
                resp = self.session.get(f"{self.base_url}/api/v1x/session/resumes/{self.resume_id}")
                self.log(f"/api/v1x/session/resumes/{self.resume_id}", "GET", resp.status_code,
                        "Get resume via session", resp.json() if resp.status_code < 400 else resp.text)
            except Exception as e:
                self.log(f"/api/v1x/session/resumes/{self.resume_id}", "GET", 500, f"Error: {str(e)}")
    
    def test_resume_delete(self):
        """Test /api/v1x/resumes/{id} DELETE endpoint"""
        if not self.resume_id:
            print("⏭️  Skipping DELETE test - no resume_id from create")
            return
        
        print("\n=== Testing Resume Delete Endpoint ===")
        try:
            resp = self.session.delete(f"{self.base_url}/api/v1x/resumes/{self.resume_id}")
            self.log(f"/api/v1x/resumes/{self.resume_id}", "DELETE", resp.status_code,
                    "Delete resume", resp.json() if resp.text else "Deleted")
        except Exception as e:
            self.log(f"/api/v1x/resumes/{self.resume_id}", "DELETE", 500, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if 200 <= r["status"] < 300)
        failed = sum(1 for r in self.results if r["status"] >= 400)
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if failed > 0:
            print("\nFailed Tests:")
            for r in self.results:
                if r["status"] >= 400:
                    print(f"  - [{r['method']}] {r['endpoint']}: {r['message']}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Resume API Tests...")
        print(f"Base URL: {self.base_url}\n")
        
        self.test_session_endpoint()
        self.test_resume_list_endpoint()
        self.test_resume_get()
        self.test_resume_update()
        self.test_session_resume_endpoints()
        self.test_resume_delete()
        
        self.print_summary()

if __name__ == "__main__":
    tester = ResumeAPITester()
    tester.run_all_tests()
