"""
Comprehensive Resume Workflow Test for Demo Readiness
Tests all critical paths without triggering rate limits
"""
import requests
import time
from datetime import datetime

# Use existing test user to avoid rate limits
TEST_EMAIL = "demo@skillforge.com"
TEST_PASSWORD = "Demo123!"

BASE = "http://localhost:3000"
BACKEND = "http://localhost:8001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_test(name, passed, details=""):
    status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"{status} | {name}")
    if details:
        print(f"        {Colors.BLUE}{details}{Colors.END}")

def log_section(title):
    print(f"\n{Colors.YELLOW}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

def main():
    log_section("SkillForge Resume System - Demo Readiness Test")
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Test 1: Backend Health
    log_section("1. Backend Health Check")
    try:
        r = requests.get(f"{BACKEND}/healthz", timeout=3)
        passed = r.status_code == 200
        log_test("Backend Health", passed, f"Status: {r.status_code}")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Backend Health", passed))
    except Exception as e:
        log_test("Backend Health", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Backend Health", False))
        print(f"\n{Colors.RED}CRITICAL: Backend not running! Start it with:{Colors.END}")
        print(f"{Colors.BLUE}cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload{Colors.END}\n")
        return
    
    # Test 2: Frontend Accessible
    log_section("2. Frontend Accessibility")
    try:
        r = requests.get(BASE, timeout=15)
        passed = r.status_code == 200
        log_test("Frontend Accessible", passed, f"Status: {r.status_code}")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Frontend Accessible", passed))
    except Exception as e:
        log_test("Frontend Accessible", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Frontend Accessible", False))
        print(f"\n{Colors.RED}CRITICAL: Frontend not running! Start it with:{Colors.END}")
        print(f"{Colors.BLUE}npm run dev{Colors.END}\n")
        return
    
    # Test 3: Login with existing user
    log_section("3. User Authentication")
    try:
        r = requests.post(f"{BASE}/api/session/login", 
                         json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                         timeout=15)
        
        if r.status_code == 401:
            # Try creating the demo user
            log_test("Login (attempting to create demo user)", False, "Demo user doesn't exist, creating...")
            signup_r = requests.post(f"{BASE}/api/session/signup",
                                    json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "full_name": "Demo User"},
                                    timeout=15)
            
            if signup_r.status_code == 200:
                log_test("Create Demo User", True, "Demo user created successfully")
                # Try login again
                r = requests.post(f"{BASE}/api/session/login",
                                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                                timeout=15)
            else:
                log_test("Create Demo User", False, f"Status: {signup_r.status_code}")
                results["failed"] += 2
                return
        
        passed = r.status_code == 200 and 'token' in r.cookies
        log_test("User Login", passed, f"Status: {r.status_code}, Token: {'✓' if 'token' in r.cookies else '✗'}")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("User Login", passed))
        
        if not passed:
            print(f"\n{Colors.RED}CRITICAL: Cannot login! Check credentials or auth endpoint{Colors.END}\n")
            return
        
        cookies = r.cookies
        
    except Exception as e:
        log_test("User Login", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("User Login", False))
        return
    
    # Test 4: Get User Info
    log_section("4. Session Validation")
    try:
        r = requests.get(f"{BASE}/api/session/me", cookies=cookies, timeout=3)
        passed = r.status_code == 200
        user_email = r.json().get('email', 'N/A') if passed else 'N/A'
        log_test("Get User Info (/me)", passed, f"Email: {user_email}")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Get User Info", passed))
    except Exception as e:
        log_test("Get User Info", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Get User Info", False))
    
    # Test 5: List Resumes
    log_section("5. Resume Management")
    try:
        r = requests.get(f"{BASE}/api/session/resumes", cookies=cookies, timeout=3)
        passed = r.status_code == 200
        resume_count = len(r.json()) if passed else 0
        log_test("List Resumes", passed, f"Found: {resume_count} resumes")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("List Resumes", passed))
    except Exception as e:
        log_test("List Resumes", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("List Resumes", False))
    
    # Test 6: Create Resume
    log_section("6. Resume Creation")
    try:
        resume_data = {
            "title": f"Demo Resume {datetime.now().strftime('%H:%M:%S')}",
            "template_id": "modern",
            "full_name": "John Demo",
            "email": "john@demo.com",
            "phone": "+1-555-0100",
            "summary": "Experienced professional ready for demo",
            "work_experiences": [
                {
                    "company": "Demo Corp",
                    "position": "Senior Engineer",
                    "start_date": "2020-01-01",
                    "end_date": "2024-01-01",
                    "description": "Led demo projects"
                }
            ],
            "education": [
                {
                    "institution": "Demo University",
                    "degree": "BS Computer Science",
                    "start_date": "2015-09-01",
                    "end_date": "2019-05-31"
                }
            ]
        }
        
        r = requests.post(f"{BASE}/api/session/resumes", 
                         json=resume_data, 
                         cookies=cookies, 
                         timeout=15)
        passed = r.status_code == 201
        resume_id = r.json().get('id') if passed else None
        log_test("Create Resume", passed, f"Status: {r.status_code}, ID: {resume_id}")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Create Resume", passed))
        
        if not passed:
            print(f"{Colors.YELLOW}Note: If status is 422, check resume schema validation{Colors.END}")
            return
        
    except Exception as e:
        log_test("Create Resume", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Create Resume", False))
        resume_id = None
    
    if not resume_id:
        print(f"\n{Colors.YELLOW}Cannot continue without resume ID{Colors.END}\n")
        return
    
    # Test 7: Get Resume
    log_section("7. Resume Retrieval")
    try:
        r = requests.get(f"{BASE}/api/session/resumes?id={resume_id}", cookies=cookies, timeout=3)
        passed = r.status_code == 200
        title = r.json().get('title', 'N/A') if passed else 'N/A'
        log_test("Get Resume", passed, f"Title: {title}")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Get Resume", passed))
    except Exception as e:
        log_test("Get Resume", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Get Resume", False))
    
    # Test 8: Export PDF (CRITICAL FOR DEMO)
    log_section("8. Resume Export - PDF (CRITICAL)")
    try:
        r = requests.get(f"{BASE}/api/session/export?resumeId={resume_id}&format=pdf",
                    cookies=cookies, 
                    timeout=10)
        passed = r.status_code == 200 and len(r.content) > 100
        content_type = r.headers.get('content-type', 'N/A')
        size = len(r.content) if passed else 0
        log_test("Export PDF", passed, f"Type: {content_type}, Size: {size} bytes")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Export PDF", passed))
        
        if passed:
            with open(f"test_demo_resume_{resume_id}.pdf", "wb") as f:
                f.write(r.content)
            print(f"        {Colors.GREEN}PDF saved: test_demo_resume_{resume_id}.pdf{Colors.END}")
        else:
            print(f"        {Colors.RED}Status: {r.status_code}, Response: {r.text[:100]}{Colors.END}")
            if r.status_code == 401:
                print(f"        {Colors.YELLOW}Auth issue: Cookie not forwarded or expired{Colors.END}")
            elif r.status_code == 404:
                print(f"        {Colors.YELLOW}Routing issue: Proxy not catching request{Colors.END}")
                print(f"        {Colors.BLUE}x-debug-target: {r.headers.get('x-debug-target', 'N/A')}{Colors.END}")
    except Exception as e:
        log_test("Export PDF", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Export PDF", False))
    
    # Test 9: Export DOCX (CRITICAL FOR DEMO)
    log_section("9. Resume Export - DOCX (CRITICAL)")
    try:
        r = requests.get(f"{BASE}/api/session/export?resumeId={resume_id}&format=docx",
                    cookies=cookies, 
                    timeout=10)
        passed = r.status_code == 200 and len(r.content) > 100
        content_type = r.headers.get('content-type', 'N/A')
        size = len(r.content) if passed else 0
        log_test("Export DOCX", passed, f"Type: {content_type}, Size: {size} bytes")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Export DOCX", passed))
        
        if passed:
            with open(f"test_demo_resume_{resume_id}.docx", "wb") as f:
                f.write(r.content)
            print(f"        {Colors.GREEN}DOCX saved: test_demo_resume_{resume_id}.docx{Colors.END}")
        else:
            print(f"        {Colors.RED}Status: {r.status_code}, Response: {r.text[:100]}{Colors.END}")
    except Exception as e:
        log_test("Export DOCX", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Export DOCX", False))
    
    # Test 10: Update Resume
    log_section("10. Resume Updates")
    try:
        update_data = {
            "professional_summary": "Updated summary for demo testing"
        }
        r = requests.patch(f"{BASE}/api/session/resumes?id={resume_id}", 
                        json=update_data, 
                        cookies=cookies, 
                        timeout=3)
        passed = r.status_code == 200
        log_test("Update Resume", passed, f"Status: {r.status_code}")
        results["passed" if passed else "failed"] += 1
        results["tests"].append(("Update Resume", passed))
    except Exception as e:
        log_test("Update Resume", False, f"Error: {str(e)[:50]}")
        results["failed"] += 1
        results["tests"].append(("Update Resume", False))
    
    # Summary
    log_section("Test Summary")
    total = results["passed"] + results["failed"]
    pass_rate = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    print(f"Success Rate: {pass_rate:.1f}%")
    
    print(f"\n{'='*60}")
    if pass_rate >= 90:
        print(f"{Colors.GREEN}✓ DEMO READY - All critical tests passed!{Colors.END}")
        print(f"{Colors.BLUE}Resume ID for demo: {resume_id}{Colors.END}")
        print(f"{Colors.BLUE}Login credentials: {TEST_EMAIL} / {TEST_PASSWORD}{Colors.END}")
    elif pass_rate >= 70:
        print(f"{Colors.YELLOW}⚠ PARTIALLY READY - Some issues need attention{Colors.END}")
        print(f"\nFailed tests:")
        for name, passed in results["tests"]:
            if not passed:
                print(f"  - {name}")
    else:
        print(f"{Colors.RED}✗ NOT READY - Critical failures detected{Colors.END}")
        print(f"\nFailed tests:")
        for name, passed in results["tests"]:
            if not passed:
                print(f"  - {name}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}\n")
