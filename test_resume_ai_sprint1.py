#!/usr/bin/env python
"""
SPRINT 1 - Resume AI Integration Test
Tests all 4 AI resume features: summary, bullets, keywords, projects
"""

import requests
import json
import sys
from datetime import datetime

API_BASE = "http://localhost:8001/api"

class TestResumeAI:
    def __init__(self):
        self.user_token = None
        self.resume_id = None
        self.passed = 0
        self.failed = 0
        
    def log(self, message: str, status: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
    
    def setup_user(self):
        """Create test user and get token"""
        self.log("Creating test user...", "SETUP")
        
        user_data = {
            "email": f"resume_ai_test_{datetime.now().timestamp()}@test.com",
            "password": "testpass123"
        }
        
        # Signup
        signup_res = requests.post(
            f"{API_BASE}/v1/auth/signup",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if signup_res.status_code != 200:
            self.log(f"Failed to signup: {signup_res.text}", "ERROR")
            return False
        
        # Login
        login_res = requests.post(
            f"{API_BASE}/v1/auth/login",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_res.status_code != 200:
            self.log(f"Failed to login: {login_res.text}", "ERROR")
            return False
        
        # Get token from cookie
        if "token" in login_res.cookies:
            self.user_token = login_res.cookies["token"]
            self.log(f"✅ User created and logged in", "PASS")
            return True
        
        self.log("No token in response", "ERROR")
        return False
    
    def create_test_resume(self):
        """Create a test resume with sample data"""
        self.log("Creating test resume...", "SETUP")
        
        resume_data = {
            "title": "AI Integration Test Resume",
            "template": "modern",
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1-234-567-8900",
            "location": "San Francisco, CA",
            "professional_summary": "Experienced software engineer with 5+ years of experience",
            "work_experiences": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "start_date": "2020-01-01",
                    "end_date": "2024-01-01",
                    "description": "Led development of microservices architecture. Managed team of 5 engineers. Improved system performance by 40%."
                },
                {
                    "title": "Software Engineer",
                    "company": "StartUp Inc",
                    "start_date": "2018-06-01",
                    "end_date": "2019-12-31",
                    "description": "Developed full-stack web applications using React and Node.js"
                }
            ],
            "education": [
                {
                    "institution": "University of California",
                    "degree": "BS",
                    "field": "Computer Science",
                    "year": "2018"
                }
            ],
            "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"token={self.user_token}"
        }
        
        res = requests.post(
            f"{API_BASE}/v1x/resumes/",
            json=resume_data,
            headers=headers
        )
        
        if res.status_code != 200:
            self.log(f"Failed to create resume: {res.text}", "ERROR")
            return False
        
        self.resume_id = res.json().get("id")
        self.log(f"✅ Resume created (ID: {self.resume_id})", "PASS")
        return True
    
    def test_professional_summary(self):
        """Test professional summary generation"""
        self.log("Testing professional summary generation...", "TEST")
        
        payload = {
            "title": "Senior Software Engineer",
            "years_of_experience": 5,
            "skills": ["Python", "JavaScript", "React", "Docker"],
            "target_role": "Tech Lead"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"token={self.user_token}"
        }
        
        res = requests.post(
            f"{API_BASE}/v1x/resume-ai/professional-summary",
            json=payload,
            headers=headers
        )
        
        if res.status_code != 200:
            self.log(f"❌ Failed: {res.status_code} - {res.text}", "FAIL")
            self.failed += 1
            return False
        
        data = res.json()
        
        # Validate response
        if not data.get("summary"):
            self.log("❌ No summary in response", "FAIL")
            self.failed += 1
            return False
        
        summary_length = len(data["summary"])
        variations_count = len(data.get("variations", []))
        
        self.log(f"✅ Summary generated ({summary_length} chars, {variations_count} variations)", "PASS")
        self.passed += 1
        
        print(f"   Main Summary: {data['summary'][:100]}...")
        if variations_count > 0:
            print(f"   Variation 1: {data['variations'][0][:100]}...")
        
        return True
    
    def test_bullet_points(self):
        """Test bullet point generation"""
        self.log("Testing bullet points generation...", "TEST")
        
        payload = {
            "job_title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": "Led development of microservices, managed team, improved performance"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"token={self.user_token}"
        }
        
        res = requests.post(
            f"{API_BASE}/v1x/resume-ai/bullets",
            json=payload,
            headers=headers
        )
        
        if res.status_code != 200:
            self.log(f"❌ Failed: {res.status_code} - {res.text}", "FAIL")
            self.failed += 1
            return False
        
        data = res.json()
        
        # Validate response
        bullets = data.get("bullet_points", [])
        if not bullets or len(bullets) == 0:
            self.log("❌ No bullets in response", "FAIL")
            self.failed += 1
            return False
        
        self.log(f"✅ Generated {len(bullets)} bullet points", "PASS")
        self.passed += 1
        
        for i, bullet in enumerate(bullets[:3], 1):
            print(f"   Bullet {i}: {bullet[:80]}...")
        
        return True
    
    def test_keywords(self):
        """Test keyword extraction"""
        self.log("Testing keyword extraction...", "TEST")
        
        payload = {
            "job_description": "Experienced software engineer with 5+ years building scalable web applications"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"token={self.user_token}"
        }
        
        res = requests.post(
            f"{API_BASE}/v1x/resume-ai/keywords",
            json=payload,
            headers=headers
        )
        
        if res.status_code != 200:
            self.log(f"❌ Failed: {res.status_code} - {res.text}", "FAIL")
            self.failed += 1
            return False
        
        data = res.json()
        keywords = data.get("keywords", [])
        
        if not keywords or len(keywords) == 0:
            self.log("❌ No keywords in response", "FAIL")
            self.failed += 1
            return False
        
        self.log(f"✅ Extracted {len(keywords)} keywords", "PASS")
        self.passed += 1
        
        print(f"   Keywords: {', '.join(keywords[:10])}")
        
        return True
    
    def test_project_ideas(self):
        """Test project suggestions"""
        self.log("Testing project suggestions...", "TEST")
        
        payload = {
            "skill_level": "intermediate",
            "technologies": ["Python", "React", "PostgreSQL"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"token={self.user_token}"
        }
        
        res = requests.post(
            f"{API_BASE}/v1x/resume-ai/project-ideas",
            json=payload,
            headers=headers
        )
        
        if res.status_code != 200:
            self.log(f"❌ Failed: {res.status_code} - {res.text}", "FAIL")
            self.failed += 1
            return False
        
        data = res.json()
        projects = data.get("projects", [])
        
        if not projects or len(projects) == 0:
            self.log("❌ No projects in response", "FAIL")
            self.failed += 1
            return False
        
        self.log(f"✅ Generated {len(projects)} project ideas", "PASS")
        self.passed += 1
        
        for i, proj in enumerate(projects[:3], 1):
            print(f"   Project {i}: {proj.get('title', 'Untitled')}")
        
        return True
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*70)
        print("SKILLFORGE - RESUME AI INTEGRATION TEST SUITE")
        print("="*70)
        print(f"Timestamp: {datetime.now()}")
        print(f"API Base: {API_BASE}\n")
        
        # Setup
        if not self.setup_user():
            self.log("Setup failed, aborting tests", "ERROR")
            return False
        
        if not self.create_test_resume():
            self.log("Resume creation failed, aborting tests", "ERROR")
            return False
        
        # Tests
        print("\n" + "-"*70)
        print("RESUME AI ENDPOINTS\n")
        
        self.test_professional_summary()
        self.test_bullet_points()
        self.test_keywords()
        self.test_project_ideas()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        print("="*70 + "\n")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = TestResumeAI()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
