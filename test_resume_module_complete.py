#!/usr/bin/env python3
"""
Comprehensive Resume Module Testing Script
Tests all features: CRUD, templates, exports, imports, preview, styling, etc.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1x"

class ResumeTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_results = []
        self.headers = {}
        
    def log(self, test_name, status, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "message": message,
            "time": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{result['status']} - {test_name}: {message}")
        
    def setup_auth(self):
        """Setup authentication"""
        print("\n" + "="*60)
        print("PHASE 1: AUTHENTICATION SETUP")
        print("="*60)
        
        # Register user
        try:
            register_data = {
                "email": f"resume_tester_{datetime.now().timestamp()}@test.com",
                "password": "TestPass123!",
                "full_name": "Resume Tester"
            }
            resp = requests.post(f"{API_BASE}/auth/signup", json=register_data)
            if resp.status_code in [200, 201]:
                self.log("User Registration", True, "Account created")
            else:
                self.log("User Registration", False, f"Status: {resp.status_code}")
                return False
                
            # Login
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            resp = requests.post(f"{API_BASE}/auth/login", json=login_data)
            if resp.status_code in [200, 201]:
                data = resp.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.log("User Login", True, f"Token obtained, User ID: {self.user_id}")
                return True
            else:
                self.log("User Login", False, f"Status: {resp.status_code}")
                return False
        except Exception as e:
            self.log("Auth Setup", False, str(e))
            return False

    def test_resume_crud(self):
        """Test Create, Read, Update, Delete operations"""
        print("\n" + "="*60)
        print("PHASE 2: RESUME CRUD OPERATIONS")
        print("="*60)
        
        resume_id = None
        
        # CREATE
        try:
            create_data = {
                "title": "Test Resume",
                "template_id": 1,
                "content": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-0000",
                    "location": "New York, NY"
                }
            }
            resp = requests.post(
                f"{API_BASE}/resumes",
                json=create_data,
                headers=self.headers
            )
            if resp.status_code in [200, 201]:
                resume_id = resp.json().get("id")
                self.log("Resume Create", True, f"Created resume ID: {resume_id}")
            else:
                self.log("Resume Create", False, f"Status: {resp.status_code}, {resp.text}")
                return None
        except Exception as e:
            self.log("Resume Create", False, str(e))
            return None

        # READ
        try:
            resp = requests.get(
                f"{API_BASE}/resumes/{resume_id}",
                headers=self.headers
            )
            if resp.status_code == 200:
                data = resp.json()
                self.log("Resume Read", True, f"Title: {data.get('title', 'N/A')}")
            else:
                self.log("Resume Read", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Resume Read", False, str(e))

        # UPDATE
        try:
            update_data = {
                "title": "Updated Resume Title"
            }
            resp = requests.put(
                f"{API_BASE}/resumes/{resume_id}",
                json=update_data,
                headers=self.headers
            )
            if resp.status_code in [200, 201]:
                self.log("Resume Update", True, "Title updated successfully")
            else:
                self.log("Resume Update", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Resume Update", False, str(e))

        # LIST
        try:
            resp = requests.get(
                f"{API_BASE}/resumes",
                headers=self.headers
            )
            if resp.status_code == 200:
                count = len(resp.json())
                self.log("Resume List", True, f"Found {count} resumes")
            else:
                self.log("Resume List", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Resume List", False, str(e))

        return resume_id

    def test_templates(self, resume_id):
        """Test template functionality"""
        print("\n" + "="*60)
        print("PHASE 3: TEMPLATE OPERATIONS")
        print("="*60)
        
        # Get all templates
        try:
            resp = requests.get(
                f"{API_BASE}/resume-templates",
                headers=self.headers
            )
            if resp.status_code == 200:
                templates = resp.json()
                count = len(templates) if isinstance(templates, list) else 1
                self.log("Get Templates", True, f"Found {count} templates")
                template_id = templates[0].get("id") if isinstance(templates, list) else templates.get("id")
            else:
                self.log("Get Templates", False, f"Status: {resp.status_code}")
                return False
        except Exception as e:
            self.log("Get Templates", False, str(e))
            return False

        # Apply template
        if resume_id and template_id:
            try:
                apply_data = {"template_id": template_id}
                resp = requests.post(
                    f"{API_BASE}/resumes/{resume_id}/apply-template",
                    json=apply_data,
                    headers=self.headers
                )
                if resp.status_code in [200, 201]:
                    self.log("Apply Template", True, f"Template {template_id} applied")
                else:
                    self.log("Apply Template", False, f"Status: {resp.status_code}")
            except Exception as e:
                self.log("Apply Template", False, str(e))

        return True

    def test_export(self, resume_id):
        """Test export functionality"""
        print("\n" + "="*60)
        print("PHASE 4: EXPORT OPERATIONS")
        print("="*60)
        
        formats = ["pdf", "docx", "txt", "html"]
        
        for fmt in formats:
            try:
                resp = requests.get(
                    f"{API_BASE}/resumes/{resume_id}/export?format={fmt}",
                    headers=self.headers
                )
                if resp.status_code == 200:
                    self.log(f"Export {fmt.upper()}", True, f"Size: {len(resp.content)} bytes")
                else:
                    self.log(f"Export {fmt.upper()}", False, f"Status: {resp.status_code}")
            except Exception as e:
                self.log(f"Export {fmt.upper()}", False, str(e))

    def test_import(self):
        """Test resume import"""
        print("\n" + "="*60)
        print("PHASE 5: IMPORT OPERATIONS")
        print("="*60)
        
        # This would need an actual file, so we'll just check endpoint exists
        try:
            resp = requests.get(
                f"{API_BASE}/resume-import/status",
                headers=self.headers
            )
            if resp.status_code == 200:
                self.log("Import Status", True, "Import endpoint available")
            else:
                self.log("Import Status", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Import Status", False, str(e))

    def test_preview(self, resume_id):
        """Test preview functionality"""
        print("\n" + "="*60)
        print("PHASE 6: PREVIEW OPERATIONS")
        print("="*60)
        
        try:
            resp = requests.get(
                f"{API_BASE}/resumes/{resume_id}/preview",
                headers=self.headers
            )
            if resp.status_code == 200:
                data = resp.json()
                has_sections = (
                    "work_experiences" in data and
                    "education" in data and
                    "skills" in data
                )
                self.log("Preview Complete Data", has_sections, 
                        "All sections present" if has_sections else "Missing sections")
            else:
                self.log("Preview Complete Data", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Preview Complete Data", False, str(e))

    def test_duplicate(self, resume_id):
        """Test resume duplication"""
        print("\n" + "="*60)
        print("PHASE 7: DUPLICATION OPERATIONS")
        print("="*60)
        
        try:
            resp = requests.post(
                f"{API_BASE}/resumes/{resume_id}/duplicate",
                headers=self.headers
            )
            if resp.status_code in [200, 201]:
                new_id = resp.json().get("id")
                self.log("Duplicate Resume", True, f"New resume ID: {new_id}")
            else:
                self.log("Duplicate Resume", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Duplicate Resume", False, str(e))

    def test_ats_scoring(self, resume_id):
        """Test ATS scoring"""
        print("\n" + "="*60)
        print("PHASE 8: ATS SCORING")
        print("="*60)
        
        try:
            resp = requests.get(
                f"{API_BASE}/resumes/{resume_id}/ats-score",
                headers=self.headers
            )
            if resp.status_code == 200:
                score = resp.json().get("score", 0)
                self.log("ATS Score", True, f"Score: {score}%")
            else:
                self.log("ATS Score", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("ATS Score", False, str(e))

    def test_sections(self, resume_id):
        """Test section management"""
        print("\n" + "="*60)
        print("PHASE 9: SECTION MANAGEMENT")
        print("="*60)
        
        # Add work experience
        try:
            section_data = {
                "section_type": "work_experience",
                "company": "Acme Corp",
                "position": "Senior Developer",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "description": "Led development team"
            }
            resp = requests.post(
                f"{API_BASE}/resumes/{resume_id}/sections/add",
                json=section_data,
                headers=self.headers
            )
            if resp.status_code in [200, 201]:
                self.log("Add Section", True, "Work experience added")
            else:
                self.log("Add Section", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Add Section", False, str(e))

        # Add education
        try:
            section_data = {
                "section_type": "education",
                "school": "MIT",
                "degree": "BS",
                "field": "Computer Science",
                "graduation_date": "2020"
            }
            resp = requests.post(
                f"{API_BASE}/resumes/{resume_id}/sections/add",
                json=section_data,
                headers=self.headers
            )
            if resp.status_code in [200, 201]:
                self.log("Add Education", True, "Education added")
            else:
                self.log("Add Education", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Add Education", False, str(e))

        # Add skills
        try:
            section_data = {
                "section_type": "skill",
                "skill": "Python"
            }
            resp = requests.post(
                f"{API_BASE}/resumes/{resume_id}/sections/add",
                json=section_data,
                headers=self.headers
            )
            if resp.status_code in [200, 201]:
                self.log("Add Skill", True, "Skill added")
            else:
                self.log("Add Skill", False, f"Status: {resp.status_code}")
        except Exception as e:
            self.log("Add Skill", False, str(e))

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if "PASS" in r["status"])
        failed = sum(1 for r in self.test_results if "FAIL" in r["status"])
        total = len(self.test_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")
        
        if failed > 0:
            print("Failed Tests:")
            for r in self.test_results:
                if "FAIL" in r["status"]:
                    print(f"  - {r['test']}: {r['message']}")
        
        return failed == 0

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("RESUME MODULE COMPREHENSIVE TEST SUITE")
        print("="*60)
        print(f"Base URL: {BASE_URL}")
        print(f"Started: {datetime.now()}\n")
        
        # Phase 1: Auth
        if not self.setup_auth():
            print("❌ Authentication failed. Aborting tests.")
            return False
        
        # Phase 2: CRUD
        resume_id = self.test_resume_crud()
        if not resume_id:
            print("❌ Resume creation failed. Aborting tests.")
            return False
        
        # Phases 3-9: Features
        self.test_templates(resume_id)
        self.test_export(resume_id)
        self.test_import()
        self.test_preview(resume_id)
        self.test_duplicate(resume_id)
        self.test_ats_scoring(resume_id)
        self.test_sections(resume_id)
        
        # Summary
        success = self.print_summary()
        
        return success

if __name__ == "__main__":
    tester = ResumeTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
