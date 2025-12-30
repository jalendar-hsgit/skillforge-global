#!/usr/bin/env python3
"""
Comprehensive Resume Builder & Full Application Testing
Tests all major features of the SkillForge platform
"""

import requests
import json
import time
from datetime import datetime
import sys

BASE_URL = "http://localhost:8001"
AUTH_TOKEN = None

def print_header(title):
    """Print formatted header"""
    print(f"\n{'=' * 90}")
    print(f"  {title}")
    print(f"{'=' * 90}\n")

def print_test(num, name):
    """Print test header"""
    print(f"{'-' * 90}")
    print(f"  {num}. {name}")
    print(f"{'-' * 90}")

def print_result(success, message, details=None):
    """Print test result"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status}: {message}")
    if details:
        for line in details.split('\n'):
            if line.strip():
                print(f"    {line}")

def test_health():
    """Test 1: Health check"""
    print_test(1, "HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        success = response.status_code == 200
        print_result(success, "Backend health check", f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result(False, "Backend health check", f"Error: {str(e)}")
        return False

def test_signup():
    """Test 2: User signup"""
    global AUTH_TOKEN
    print_test(2, "USER SIGNUP")
    try:
        timestamp = int(time.time())
        signup_data = {
            "email": f"testuser_{timestamp}@test.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=signup_data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "User signup successful", 
                        f"Signup result: {result}")
            return signup_data
        else:
            print_result(False, f"User signup failed", f"Status: {response.status_code}\nResponse: {response.text[:200]}")
            return None
    except Exception as e:
        print_result(False, "User signup failed", f"Error: {str(e)}")
        return None

def test_login(signup_data):
    """Test 3: User login"""
    global AUTH_TOKEN
    print_test(3, "USER LOGIN")
    try:
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            AUTH_TOKEN = response.cookies.get('token')
            print_result(True, "User login successful",
                        f"User: {user_data.get('email')}\nToken cookie set: {bool(AUTH_TOKEN)}")
            return True
        else:
            print_result(False, f"User login failed", f"Status: {response.status_code}\nResponse: {response.text[:200]}")
            return False
    except Exception as e:
        print_result(False, "User login failed", f"Error: {str(e)}")
        return False

def test_auth_me():
    """Test 4: Get current user"""
    print_test(4, "GET CURRENT USER")
    try:
        headers = {"Cookie": f"token={AUTH_TOKEN}"} if AUTH_TOKEN else {}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {}, timeout=5)
        
        if response.status_code == 200:
            user_data = response.json()
            print_result(True, "Get current user successful",
                        f"ID: {user_data.get('id')}\nUsername: {user_data.get('username')}\nEmail: {user_data.get('email')}")
            return True
        else:
            print_result(False, f"Get current user failed", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, "Get current user failed", f"Error: {str(e)}")
        return False

def test_list_courses():
    """Test 5: List courses"""
    print_test(5, "LIST COURSES")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/courses/", timeout=5)
        
        if response.status_code == 200:
            courses = response.json()
            count = len(courses) if isinstance(courses, list) else 0
            first_course = courses[0].get('title') if courses else 'N/A'
            print_result(True, f"List courses successful", f"Total courses: {count}\nFirst course: {first_course}")
            return True
        else:
            print_result(False, f"List courses failed", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, "List courses failed", f"Error: {str(e)}")
        return False

def test_list_resumes():
    """Test 6: List resumes"""
    print_test(6, "LIST RESUMES")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/resumes/", 
                              cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {}, timeout=5)
        
        if response.status_code == 200:
            resumes = response.json()
            count = len(resumes) if isinstance(resumes, list) else 0
            print_result(True, f"List resumes successful", f"Total resumes: {count}")
            return True
        else:
            print_result(False, f"List resumes failed", f"Status: {response.status_code}\nResponse: {response.text[:200]}")
            return False
    except Exception as e:
        print_result(False, "List resumes failed", f"Error: {str(e)}")
        return False

def test_create_resume():
    """Test 7: Create resume"""
    print_test(7, "CREATE RESUME")
    try:
        resume_data = {
            "title": f"Test Resume {int(time.time())}",
            "template_id": "modern",
            "summary": "Senior Software Engineer with 5+ years experience",
            "email": "test@example.com",
            "phone": "+1-234-567-8900"
        }
        response = requests.post(f"{BASE_URL}/api/v1x/resumes/",
                               json=resume_data,
                               cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                               timeout=5)
        
        if response.status_code in [200, 201]:
            resume = response.json()
            resume_id = resume.get('id')
            title = resume.get('title')
            print_result(True, "Create resume successful",
                        f"Resume ID: {resume_id}\nTitle: {title}")
            return resume_id
        else:
            print_result(False, f"Create resume failed", 
                        f"Status: {response.status_code}\nResponse: {response.text[:300]}")
            return None
    except Exception as e:
        print_result(False, "Create resume failed", f"Error: {str(e)}")
        return None

def test_get_resume(resume_id):
    """Test 8: Get single resume"""
    print_test(8, "GET SINGLE RESUME")
    if not resume_id:
        print_result(False, "Get resume skipped", "No resume ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/resumes/{resume_id}",
                              cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                              timeout=5)
        
        if response.status_code == 200:
            resume = response.json()
            print_result(True, "Get resume successful",
                        f"ID: {resume.get('id')}\nTitle: {resume.get('title')}")
            return True
        else:
            print_result(False, f"Get resume failed", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, "Get resume failed", f"Error: {str(e)}")
        return False

def test_add_work_experience(resume_id):
    """Test 9: Add work experience"""
    print_test(9, "ADD WORK EXPERIENCE")
    if not resume_id:
        print_result(False, "Add work experience skipped", "No resume ID available")
        return False
    
    try:
        exp_data = {
            "company_name": "Tech Corp",
            "job_title": "Senior Software Engineer",
            "start_date": "2020-01-15",
            "end_date": "2023-12-31",
            "description": "Led development of microservices architecture and managed team of 5 developers"
        }
        response = requests.post(f"{BASE_URL}/api/v1x/resumes/{resume_id}/experience",
                               json=exp_data,
                               cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                               timeout=5)
        
        if response.status_code in [200, 201]:
            print_result(True, "Add work experience successful",
                        f"Company: {exp_data['company_name']}\nPosition: {exp_data['job_title']}")
            return True
        else:
            print_result(False, f"Add work experience failed",
                        f"Status: {response.status_code}\nResponse: {response.text[:300]}")
            return False
    except Exception as e:
        print_result(False, "Add work experience failed", f"Error: {str(e)}")
        return False

def test_add_education(resume_id):
    """Test 10: Add education"""
    print_test(10, "ADD EDUCATION")
    if not resume_id:
        print_result(False, "Add education skipped", "No resume ID available")
        return False
    
    try:
        edu_data = {
            "school_name": "State University",
            "degree": "B.S. Computer Science",
            "start_date": "2015-09-01",
            "end_date": "2019-05-31"
        }
        response = requests.post(f"{BASE_URL}/api/v1x/resumes/{resume_id}/education",
                               json=edu_data,
                               cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                               timeout=5)
        
        if response.status_code in [200, 201]:
            print_result(True, "Add education successful",
                        f"School: {edu_data['school_name']}\nDegree: {edu_data['degree']}")
            return True
        else:
            print_result(False, f"Add education failed",
                        f"Status: {response.status_code}\nResponse: {response.text[:300]}")
            return False
    except Exception as e:
        print_result(False, "Add education failed", f"Error: {str(e)}")
        return False

def test_add_skill(resume_id):
    """Test 11: Add skills"""
    print_test(11, "ADD SKILLS")
    if not resume_id:
        print_result(False, "Add skills skipped", "No resume ID available")
        return False
    
    try:
        skills = ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"]
        added = 0
        for skill in skills:
            skill_data = {"name": skill, "proficiency": "Expert"}
            response = requests.post(f"{BASE_URL}/api/v1x/resumes/{resume_id}/skills",
                                   json=skill_data,
                                   cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                                   timeout=5)
            if response.status_code in [200, 201]:
                added += 1
        
        if added > 0:
            print_result(True, "Add skills successful", f"Added {added}/{len(skills)} skills")
            return True
        else:
            print_result(False, "Add skills failed", "No skills added")
            return False
    except Exception as e:
        print_result(False, "Add skills failed", f"Error: {str(e)}")
        return False

def test_export_pdf(resume_id):
    """Test 12: Export resume to PDF"""
    print_test(12, "EXPORT TO PDF")
    if not resume_id:
        print_result(False, "Export PDF skipped", "No resume ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/resumes/{resume_id}/export/pdf",
                              cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                              timeout=10)
        
        if response.status_code == 200 and len(response.content) > 0:
            size_kb = len(response.content) / 1024
            print_result(True, "Export to PDF successful", f"PDF size: {size_kb:.2f} KB")
            return True
        else:
            print_result(False, f"Export to PDF failed",
                        f"Status: {response.status_code}\nSize: {len(response.content)} bytes")
            return False
    except Exception as e:
        print_result(False, "Export to PDF failed", f"Error: {str(e)}")
        return False

def test_ats_analysis(resume_id):
    """Test 13: ATS Analysis"""
    print_test(13, "ATS ANALYSIS")
    if not resume_id:
        print_result(False, "ATS analysis skipped", "No resume ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/resumes/{resume_id}/ats-analysis",
                              cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                              timeout=5)
        
        if response.status_code == 200:
            analysis = response.json()
            score = analysis.get('score', 'N/A')
            issues = analysis.get('issues', [])
            print_result(True, "ATS analysis successful",
                        f"Score: {score}\nIssues found: {len(issues)}")
            return True
        else:
            print_result(False, f"ATS analysis failed",
                        f"Status: {response.status_code}\nResponse: {response.text[:300]}")
            return False
    except Exception as e:
        print_result(False, "ATS analysis failed", f"Error: {str(e)}")
        return False

def test_quizzes():
    """Test 14: List quizzes"""
    print_test(14, "LIST QUIZZES")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/quizzes/", timeout=5)
        
        if response.status_code == 200:
            quizzes = response.json()
            count = len(quizzes) if isinstance(quizzes, list) else 0
            print_result(True, f"List quizzes successful", f"Total quizzes: {count}")
            return True
        else:
            print_result(False, f"List quizzes failed", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, "List quizzes failed", f"Error: {str(e)}")
        return False

def test_leaderboard():
    """Test 15: Get leaderboard"""
    print_test(15, "GET LEADERBOARD")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/leaderboard/?period=week&limit=10", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print_result(True, f"Get leaderboard successful", f"Top users: {count}")
            return True
        else:
            print_result(False, f"Get leaderboard failed", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, "Get leaderboard failed", f"Error: {str(e)}")
        return False

def test_dashboard():
    """Test 16: Get dashboard"""
    print_test(16, "GET DASHBOARD")
    try:
        response = requests.get(f"{BASE_URL}/api/v1x/student-dashboard/",
                              cookies={"token": AUTH_TOKEN} if AUTH_TOKEN else {},
                              timeout=5)
        
        if response.status_code == 200:
            dashboard = response.json()
            print_result(True, f"Get dashboard successful", f"Data keys: {len(dashboard.keys()) if isinstance(dashboard, dict) else 'N/A'}")
            return True
        else:
            print_result(False, f"Get dashboard failed", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, "Get dashboard failed", f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("SKILLFORGE GLOBAL - COMPREHENSIVE APPLICATION TEST")
    print(f"Testing: {BASE_URL}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # Core tests
    print("\n" + "=" * 90)
    print("=  SECTION 1: CORE PLATFORM & AUTHENTICATION")
    print("=" * 90)
    
    results["health"] = test_health()
    
    signup_data = test_signup()
    if not signup_data:
        print("\n❌ Cannot continue without successful signup")
        return
    
    results["login"] = test_login(signup_data)
    results["auth_me"] = test_auth_me()
    
    # Course & Learning
    print("\n" + "=" * 90)
    print("=  SECTION 2: LEARNING SYSTEM")
    print("=" * 90)
    
    results["courses"] = test_list_courses()
    results["quizzes"] = test_quizzes()
    results["leaderboard"] = test_leaderboard()
    
    # Resume Builder (PRIMARY TEST)
    print("\n" + "=" * 90)
    print("=  SECTION 3: RESUME BUILDER (PRIMARY FOCUS)")
    print("=" * 90)
    
    results["list_resumes"] = test_list_resumes()
    
    resume_id = test_create_resume()
    results["create_resume"] = bool(resume_id)
    
    if resume_id:
        results["get_resume"] = test_get_resume(resume_id)
        results["work_experience"] = test_add_work_experience(resume_id)
        results["education"] = test_add_education(resume_id)
        results["skills"] = test_add_skill(resume_id)
        results["export_pdf"] = test_export_pdf(resume_id)
        results["ats_analysis"] = test_ats_analysis(resume_id)
    
    # Dashboard
    print("\n" + "=" * 90)
    print("=  SECTION 4: DASHBOARD")
    print("=" * 90)
    
    results["dashboard"] = test_dashboard()
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)\n")
    
    for test_name, result in results.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name.upper()}")
    
    print(f"\n{'=' * 90}")
    print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 90}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
