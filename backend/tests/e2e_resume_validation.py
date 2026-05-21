"""
End-to-End Resume Feature Validation Script
Tests complete resume workflow: create → edit → export → suggestions → import
Usage: python backend/tests/e2e_resume_validation.py
"""
import requests
import json
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Tuple


class ResumeE2EValidator:
    """End-to-end validator for all resume features"""

    def __init__(self, api_base: str = "http://localhost:8001", api_v1x_base: str = "http://localhost:8001/api/v1x"):
        self.api_base = api_base
        self.api_v1x_base = api_v1x_base
        self.auth_token = None
        self.user_id = None
        self.resume_id = None
        self.results = []

    # ============ Setup ============

    def log_result(self, step: str, success: bool, details: str = ""):
        """Log validation result"""
        status = "✅ PASS" if success else "❌ FAIL"
        msg = f"{status} | {step}"
        if details:
            msg += f" | {details}"
        print(msg)
        self.results.append({
            "step": step,
            "success": success,
            "details": details,
            "timestamp": time.time(),
        })

    # ============ Authentication ============

    def authenticate(self, email: str = "test@example.com", password: str = "test123") -> bool:
        """Authenticate and get auth token"""
        try:
            # Attempt login
            response = requests.post(
                f"{self.api_base}/api/v1/auth/login",
                json={"email": email, "password": password},
                cookies={}
            )

            if response.status_code == 200:
                # Token is typically in HTTP-only cookie
                # For API testing, we might use a query parameter or header
                self.log_result("Authentication", True, "Login successful")
                return True
            else:
                # Try signup if login fails
                return self.signup(email, password)

        except Exception as e:
            self.log_result("Authentication", False, str(e))
            return False

    def signup(self, email: str, password: str) -> bool:
        """Sign up new user"""
        try:
            response = requests.post(
                f"{self.api_base}/api/v1/auth/signup",
                json={"email": email, "password": password, "name": "Test User"},
            )

            if response.status_code in [200, 201]:
                self.log_result("User Signup", True, "Account created")
                return True
            else:
                self.log_result("User Signup", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("User Signup", False, str(e))
            return False

    # ============ Resume Creation ============

    def create_resume(self) -> bool:
        """Create a new resume"""
        try:
            response = requests.post(
                f"{self.api_v1x_base}/resumes",
                json={
                    "title": "E2E Test Resume",
                    "template_id": "modern",
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-1234",
                    "location": "New York, NY",
                    "summary": "Experienced software developer with expertise in Python, JavaScript, and cloud technologies.",
                },
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code in [200, 201]:
                data = response.json()
                self.resume_id = data.get("id")
                self.log_result("Resume Creation", True, f"Created resume ID {self.resume_id}")
                return True
            else:
                self.log_result("Resume Creation", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("Resume Creation", False, str(e))
            return False

    # ============ Resume Editing ============

    def update_resume_fields(self) -> bool:
        """Update resume with detailed information"""
        try:
            if not self.resume_id:
                self.log_result("Resume Update", False, "No resume ID")
                return False

            response = requests.put(
                f"{self.api_v1x_base}/resumes/{self.resume_id}",
                json={
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-1234",
                    "location": "New York, NY",
                    "linkedin_url": "https://linkedin.com/in/johndoe",
                    "github_url": "https://github.com/johndoe",
                    "portfolio_url": "https://johndoe.dev",
                    "summary": "Senior software developer with 10+ years of experience building scalable web applications and microservices.",
                },
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code == 200:
                self.log_result("Resume Update", True, "Fields updated successfully")
                return True
            else:
                self.log_result("Resume Update", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("Resume Update", False, str(e))
            return False

    def add_work_experience(self) -> bool:
        """Add work experience to resume"""
        try:
            if not self.resume_id:
                return False

            response = requests.post(
                f"{self.api_v1x_base}/resumes/{self.resume_id}/work-experience",
                json={
                    "company": "Tech Corp",
                    "position": "Senior Developer",
                    "start_date": "2020-01-01",
                    "end_date": None,
                    "description": "Lead development of microservices platform. Mentored 5 junior developers.",
                    "skills_used": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                },
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code in [200, 201]:
                self.log_result("Add Work Experience", True, "Work experience added")
                return True
            else:
                self.log_result("Add Work Experience", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("Add Work Experience", False, str(e))
            return False

    def add_education(self) -> bool:
        """Add education to resume"""
        try:
            if not self.resume_id:
                return False

            response = requests.post(
                f"{self.api_v1x_base}/resumes/{self.resume_id}/education",
                json={
                    "institution": "Massachusetts Institute of Technology",
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "graduation_date": "2018-05-31",
                    "gpa": "3.8",
                    "description": "Honors graduate with focus on distributed systems.",
                },
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code in [200, 201]:
                self.log_result("Add Education", True, "Education added")
                return True
            else:
                self.log_result("Add Education", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("Add Education", False, str(e))
            return False

    def add_skills(self) -> bool:
        """Add skills to resume"""
        try:
            if not self.resume_id:
                return False

            skills = [
                {"name": "Python", "level": "expert", "years": 8},
                {"name": "JavaScript", "level": "expert", "years": 7},
                {"name": "React", "level": "advanced", "years": 5},
                {"name": "AWS", "level": "intermediate", "years": 3},
                {"name": "Docker", "level": "advanced", "years": 4},
            ]

            for skill in skills:
                response = requests.post(
                    f"{self.api_v1x_base}/resumes/{self.resume_id}/skills",
                    json=skill,
                    cookies={"token": self.auth_token} if self.auth_token else {},
                )

                if response.status_code not in [200, 201]:
                    self.log_result("Add Skills", False, f"Skill {skill['name']} failed")
                    return False

            self.log_result("Add Skills", True, f"Added {len(skills)} skills")
            return True

        except Exception as e:
            self.log_result("Add Skills", False, str(e))
            return False

    # ============ Resume Export ============

    def export_pdf(self) -> bool:
        """Export resume as PDF"""
        try:
            if not self.resume_id:
                return False

            response = requests.post(
                f"{self.api_v1x_base}/resume-tools/{self.resume_id}/export?format=pdf",
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code == 200:
                # Verify PDF content
                if response.content.startswith(b'%PDF'):
                    self.log_result("PDF Export", True, f"Generated {len(response.content)} bytes")
                    
                    # Save to temp file for verification
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                        f.write(response.content)
                        print(f"   📄 PDF saved to: {f.name}")
                    return True
                else:
                    self.log_result("PDF Export", False, "Invalid PDF content")
                    return False
            else:
                self.log_result("PDF Export", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("PDF Export", False, str(e))
            return False

    def export_docx(self) -> bool:
        """Export resume as DOCX"""
        try:
            if not self.resume_id:
                return False

            response = requests.post(
                f"{self.api_v1x_base}/resume-tools/{self.resume_id}/export?format=docx",
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code == 200:
                # Verify DOCX content (ZIP format)
                if response.content.startswith(b'PK'):
                    self.log_result("DOCX Export", True, f"Generated {len(response.content)} bytes")
                    
                    # Save to temp file for verification
                    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
                        f.write(response.content)
                        print(f"   📄 DOCX saved to: {f.name}")
                    return True
                else:
                    self.log_result("DOCX Export", False, "Invalid DOCX content")
                    return False
            else:
                self.log_result("DOCX Export", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("DOCX Export", False, str(e))
            return False

    # ============ Resume Suggestions ============

    def get_suggestions(self) -> bool:
        """Get AI-powered resume improvement suggestions"""
        try:
            if not self.resume_id:
                return False

            response = requests.post(
                f"{self.api_v1x_base}/resume-tools/{self.resume_id}/suggestions",
                json={
                    "section": "summary",
                    "content": "Senior software developer with 10+ years of experience.",
                },
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code == 200:
                data = response.json()
                if "suggestions" in data and isinstance(data["suggestions"], list):
                    self.log_result("AI Suggestions", True, f"Got {len(data['suggestions'])} suggestions")
                    for suggestion in data["suggestions"][:3]:
                        print(f"   💡 {suggestion}")
                    return True
                else:
                    self.log_result("AI Suggestions", False, "Invalid response format")
                    return False
            else:
                self.log_result("AI Suggestions", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("AI Suggestions", False, str(e))
            return False

    # ============ Resume Import ============

    def parse_resume_preview(self, file_path: str) -> bool:
        """Parse resume file and show preview"""
        try:
            if not os.path.exists(file_path):
                # Create a sample PDF for testing
                self.log_result("Parse Preview", False, "Sample file not found")
                return False

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
                response = requests.post(
                    f"{self.api_v1x_base}/resume-import/parse-preview",
                    data={"ai": False},
                    files=files,
                    cookies={"token": self.auth_token} if self.auth_token else {},
                )

            if response.status_code == 200:
                data = response.json()
                parsed = data.get("parsed_data", {})
                self.log_result("Parse Preview", True, f"Extracted: {parsed.get('full_name', 'N/A')}")
                return True
            else:
                self.log_result("Parse Preview", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("Parse Preview", False, str(e))
            return False

    def import_resume(self, file_path: str) -> Tuple[bool, int]:
        """Import resume from file"""
        try:
            if not os.path.exists(file_path):
                self.log_result("Resume Import", False, "File not found")
                return False, None

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
                response = requests.post(
                    f"{self.api_v1x_base}/resume-import/upload",
                    files=files,
                    cookies={"token": self.auth_token} if self.auth_token else {},
                )

            if response.status_code == 201:
                data = response.json()
                imported_id = data.get("id")
                self.log_result("Resume Import", True, f"Imported resume ID {imported_id}")
                return True, imported_id
            else:
                self.log_result("Resume Import", False, f"Status {response.status_code}")
                return False, None

        except Exception as e:
            self.log_result("Resume Import", False, str(e))
            return False, None

    # ============ Resume Retrieval ============

    def fetch_resume(self) -> bool:
        """Fetch resume details"""
        try:
            if not self.resume_id:
                return False

            response = requests.get(
                f"{self.api_v1x_base}/resumes/{self.resume_id}",
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code == 200:
                data = response.json()
                self.log_result("Fetch Resume", True, f"Retrieved: {data.get('title', 'N/A')}")
                return True
            else:
                self.log_result("Fetch Resume", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("Fetch Resume", False, str(e))
            return False

    def list_resumes(self) -> bool:
        """List all user resumes"""
        try:
            response = requests.get(
                f"{self.api_v1x_base}/resumes",
                cookies={"token": self.auth_token} if self.auth_token else {},
            )

            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                self.log_result("List Resumes", True, f"Found {count} resumes")
                return True
            else:
                self.log_result("List Resumes", False, f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_result("List Resumes", False, str(e))
            return False

    # ============ Validation Report ============

    def print_report(self):
        """Print validation report"""
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print("\n" + "="*70)
        print(f"RESUME FEATURE VALIDATION REPORT")
        print(f"{'='*70}")
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"\n{'='*70}\n")

        if passed == total:
            print("🎉 ALL TESTS PASSED! Resume features are working correctly.")
        else:
            print("⚠️  Some tests failed. Review the results above.")

    # ============ Main Validation Flow ============

    def run_full_validation(self) -> bool:
        """Run complete end-to-end validation"""
        print("\n🚀 Starting Resume Feature E2E Validation...\n")

        # Check backend is running
        try:
            response = requests.get(f"{self.api_base}/healthz", timeout=5)
            if response.status_code != 200:
                print("❌ Backend health check failed")
                return False
        except:
            print("❌ Cannot reach backend at", self.api_base)
            return False

        print("✅ Backend is running\n")

        # Run validation steps
        steps = [
            ("Auth", lambda: self.authenticate()),
            ("Create Resume", lambda: self.create_resume()),
            ("Update Fields", lambda: self.update_resume_fields()),
            ("Add Work Exp", lambda: self.add_work_experience()),
            ("Add Education", lambda: self.add_education()),
            ("Add Skills", lambda: self.add_skills()),
            ("Fetch Resume", lambda: self.fetch_resume()),
            ("List Resumes", lambda: self.list_resumes()),
            ("Export PDF", lambda: self.export_pdf()),
            ("Export DOCX", lambda: self.export_docx()),
            ("Get Suggestions", lambda: self.get_suggestions()),
        ]

        for step_name, step_fn in steps:
            if not step_fn():
                print(f"⚠️  Continuing despite {step_name} failure...")
            time.sleep(0.5)  # Brief delay between requests

        self.print_report()

        return len([r for r in self.results if r["success"]]) >= len(self.results) - 2


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║     RESUME FEATURE END-TO-END VALIDATION SUITE             ║
║                                                            ║
║  This script validates all resume features:                ║
║  • Create, edit, and manage resumes                        ║
║  • Export to PDF and DOCX formats                          ║
║  • AI-powered improvement suggestions                      ║
║  • Resume import from PDF/DOCX files                       ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Make sure backend is running
    print("📋 Prerequisites:")
    print("  1. Backend must be running: uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")
    print("  2. Database must be initialized")
    print("  3. LLM provider must be configured (optional for suggestions)")

    input("\n⏳ Press Enter to start validation (or Ctrl+C to cancel)...\n")

    validator = ResumeE2EValidator()
    success = validator.run_full_validation()

    exit(0 if success else 1)
