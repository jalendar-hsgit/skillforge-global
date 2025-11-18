"""
Comprehensive Resume Frontend/Backend Test
Tests: Auth → Resume CRUD → Export (PDF/DOCX)
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://localhost:3000"

class ResumeFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_email = f"test_{int(datetime.now().timestamp())}@example.com"
        self.user_password = "Test123!"
        self.resume_id = None
        self.results = []
        
    def log(self, test_name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append(f"{status} | {test_name}")
        if details:
            self.results.append(f"     └─ {details}")
        print(f"{status} | {test_name}")
        if details:
            print(f"     └─ {details}")
    
    def test_backend_health(self):
        """Test 1: Backend health check"""
        try:
            r = self.session.get(f"{BASE_URL}/healthz", timeout=5)
            self.log("Backend Health Check", r.status_code == 200, f"Status: {r.status_code}")
            return r.status_code == 200
        except Exception as e:
            self.log("Backend Health Check", False, f"Error: {e}")
            return False
    
    def test_signup(self):
        """Test 2: User signup"""
        try:
            payload = {
                "email": self.user_email,
                "password": self.user_password,
                "full_name": "Test User"
            }
            r = self.session.post(f"{BASE_URL}/api/v1/auth/signup", json=payload, timeout=10)
            success = r.status_code == 200
            self.log("User Signup", success, f"Status: {r.status_code}, Email: {self.user_email}")
            return success
        except Exception as e:
            self.log("User Signup", False, f"Error: {e}")
            return False
    
    def test_login(self):
        """Test 3: User login"""
        try:
            payload = {
                "email": self.user_email,
                "password": self.user_password
            }
            r = self.session.post(f"{BASE_URL}/api/v1/auth/login", json=payload, timeout=10)
            success = r.status_code == 200
            if success:
                # Store cookie for subsequent requests
                pass
            self.log("User Login", success, f"Status: {r.status_code}, Cookies: {len(r.cookies)}")
            return success
        except Exception as e:
            self.log("User Login", False, f"Error: {e}")
            return False
    
    def test_get_me(self):
        """Test 4: Get current user info"""
        try:
            r = self.session.get(f"{BASE_URL}/api/v1/auth/me", timeout=5)
            success = r.status_code == 200
            user_data = r.json() if success else {}
            self.log("Get User Info (/me)", success, f"Status: {r.status_code}, User: {user_data.get('email', 'N/A')}")
            return success
        except Exception as e:
            self.log("Get User Info (/me)", False, f"Error: {e}")
            return False
    
    def test_create_resume(self):
        """Test 5: Create new resume"""
        try:
            payload = {
                "title": "Test Resume for Export",
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "professional_summary": "Experienced software engineer with 5+ years in full-stack development."
            }
            r = self.session.post(f"{BASE_URL}/api/v1x/resumes/", json=payload, timeout=10)
            success = r.status_code == 201
            if success:
                data = r.json()
                self.resume_id = data.get('id')
            self.log("Create Resume", success, f"Status: {r.status_code}, Resume ID: {self.resume_id}")
            return success
        except Exception as e:
            self.log("Create Resume", False, f"Error: {e}")
            return False
    
    def test_get_resume(self):
        """Test 6: Retrieve created resume"""
        if not self.resume_id:
            self.log("Get Resume", False, "No resume ID available")
            return False
        try:
            r = self.session.get(f"{BASE_URL}/api/v1x/resumes/{self.resume_id}", timeout=5)
            success = r.status_code == 200
            data = r.json() if success else {}
            self.log("Get Resume", success, f"Status: {r.status_code}, Title: {data.get('title', 'N/A')}")
            return success
        except Exception as e:
            self.log("Get Resume", False, f"Error: {e}")
            return False
    
    def test_export_pdf(self):
        """Test 7: Export resume as PDF"""
        if not self.resume_id:
            self.log("Export PDF", False, "No resume ID available")
            return False
        try:
            r = self.session.get(
                f"{BASE_URL}/api/v1x/resumes/{self.resume_id}/export?format=pdf",
                timeout=15
            )
            success = r.status_code == 200
            content_type = r.headers.get('content-type', '')
            content_length = len(r.content) if success else 0
            is_pdf = 'application/pdf' in content_type or content_length > 1000
            self.log(
                "Export PDF",
                success and is_pdf,
                f"Status: {r.status_code}, Type: {content_type}, Size: {content_length} bytes"
            )
            return success and is_pdf
        except Exception as e:
            self.log("Export PDF", False, f"Error: {e}")
            return False
    
    def test_export_docx(self):
        """Test 8: Export resume as DOCX"""
        if not self.resume_id:
            self.log("Export DOCX", False, "No resume ID available")
            return False
        try:
            r = self.session.get(
                f"{BASE_URL}/api/v1x/resumes/{self.resume_id}/export?format=docx",
                timeout=15
            )
            success = r.status_code == 200
            content_type = r.headers.get('content-type', '')
            content_length = len(r.content) if success else 0
            is_docx = 'wordprocessingml' in content_type or content_length > 1000
            self.log(
                "Export DOCX",
                success and is_docx,
                f"Status: {r.status_code}, Type: {content_type}, Size: {content_length} bytes"
            )
            return success and is_docx
        except Exception as e:
            self.log("Export DOCX", False, f"Error: {e}")
            return False
    
    def test_frontend_accessible(self):
        """Test 9: Frontend server accessibility"""
        try:
            r = requests.get(FRONTEND_URL, timeout=5)
            success = r.status_code == 200
            self.log("Frontend Accessible", success, f"Status: {r.status_code}")
            return success
        except Exception as e:
            self.log("Frontend Accessible", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 70)
        print("🧪 SKILLFORGE RESUME FLOW TEST SUITE")
        print("=" * 70)
        print()
        
        tests = [
            self.test_backend_health,
            self.test_frontend_accessible,
            self.test_signup,
            self.test_login,
            self.test_get_me,
            self.test_create_resume,
            self.test_get_resume,
            self.test_export_pdf,
            self.test_export_docx,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
            print()
        
        print("=" * 70)
        print(f"📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {passed + failed}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print("=" * 70)
        
        return passed, failed

if __name__ == "__main__":
    tester = ResumeFlowTester()
    passed, failed = tester.run_all_tests()
    exit(0 if failed == 0 else 1)
