"""
Comprehensive Auth & Resume Endpoints Test
Tests signup, login, /me, and full resume CRUD operations
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"
session = requests.Session()

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def print_result(endpoint, method, status, success, details=""):
    icon = "✅" if success else "❌"
    print(f"{icon} {method:6} {endpoint:40} [{status}]")
    if details:
        print(f"   → {details}")

def test_signup():
    """Test user signup"""
    print_header("1. TESTING SIGNUP ENDPOINT")
    
    # Generate unique email
    timestamp = int(time.time())
    email = f"testuser_{timestamp}@example.com"
    password = "TestPass123!"
    
    payload = {
        "email": email,
        "password": password,
        "full_name": "Test User"
    }
    
    try:
        resp = session.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json=payload
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print_result("/api/v1/auth/signup", "POST", resp.status_code, True,
                        f"User created: {data.get('email', 'N/A')}")
            return email, password, data
        elif resp.status_code == 400 and "already exists" in resp.text.lower():
            print_result("/api/v1/auth/signup", "POST", resp.status_code, True,
                        "User already exists (expected behavior)")
            return email, password, None
        else:
            print_result("/api/v1/auth/signup", "POST", resp.status_code, False,
                        f"Error: {resp.text[:100]}")
            return None, None, None
    except Exception as e:
        print_result("/api/v1/auth/signup", "POST", 0, False, f"Exception: {str(e)}")
        return None, None, None

def test_login(email, password):
    """Test user login"""
    print_header("2. TESTING LOGIN ENDPOINT")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        resp = session.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=payload
        )
        
        if resp.status_code == 200:
            data = resp.json()
            cookies = session.cookies.get_dict()
            has_token = 'token' in cookies
            
            print_result("/api/v1/auth/login", "POST", resp.status_code, True,
                        f"Token cookie: {'✓ Present' if has_token else '✗ Missing'}")
            if has_token:
                print(f"   → Cookie value length: {len(cookies['token'])} chars")
            return data
        else:
            print_result("/api/v1/auth/login", "POST", resp.status_code, False,
                        f"Error: {resp.text[:100]}")
            return None
    except Exception as e:
        print_result("/api/v1/auth/login", "POST", 0, False, f"Exception: {str(e)}")
        return None

def test_me():
    """Test /me endpoint (authenticated)"""
    print_header("3. TESTING /ME ENDPOINT (AUTHENTICATED)")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1/auth/me")
        
        if resp.status_code == 200:
            data = resp.json()
            print_result("/api/v1/auth/me", "GET", resp.status_code, True,
                        f"User ID: {data.get('id')}, Email: {data.get('email')}")
            return data
        else:
            print_result("/api/v1/auth/me", "GET", resp.status_code, False,
                        f"Error: {resp.text[:100]}")
            return None
    except Exception as e:
        print_result("/api/v1/auth/me", "GET", 0, False, f"Exception: {str(e)}")
        return None

def test_resume_create():
    """Test creating a resume"""
    print_header("4. TESTING RESUME CREATE")
    
    payload = {
        "title": f"Software Engineer Resume - {datetime.now().strftime('%H:%M:%S')}",
        "template": "modern",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "location": "San Francisco, CA",
        "professional_summary": "Experienced software engineer with 5+ years building scalable web applications.",
        "skills": ["Python", "JavaScript", "React", "FastAPI"],
        "work_experiences": [
            {
                "company": "Tech Corp",
                "position": "Senior Software Engineer",
                "start_date": "2020-01",
                "end_date": "Present",
                "is_current": True,
                "description": "Led development of microservices architecture"
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "BS Computer Science",
                "field_of_study": "Computer Science",
                "start_date": "2015",
                "end_date": "2019",
                "gpa": "3.8"
            }
        ]
    }
    
    try:
        resp = session.post(
            f"{BASE_URL}/api/v1x/resumes",
            json=payload
        )
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            resume_id = data.get('id')
            print_result("/api/v1x/resumes", "POST", resp.status_code, True,
                        f"Resume created: ID={resume_id}, Title={data.get('title', 'N/A')}")
            return resume_id, data
        else:
            print_result("/api/v1x/resumes", "POST", resp.status_code, False,
                        f"Error: {resp.text[:200]}")
            return None, None
    except Exception as e:
        print_result("/api/v1x/resumes", "POST", 0, False, f"Exception: {str(e)}")
        return None, None

def test_resume_list():
    """Test listing resumes"""
    print_header("5. TESTING RESUME LIST")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1x/resumes")
        
        if resp.status_code == 200:
            data = resp.json()
            count = len(data) if isinstance(data, list) else data.get('total', 0)
            print_result("/api/v1x/resumes", "GET", resp.status_code, True,
                        f"Found {count} resume(s)")
            if isinstance(data, list) and len(data) > 0:
                print(f"   → First resume: ID={data[0].get('id')}, Title={data[0].get('title', 'N/A')}")
            return data
        else:
            print_result("/api/v1x/resumes", "GET", resp.status_code, False,
                        f"Error: {resp.text[:200]}")
            return None
    except Exception as e:
        print_result("/api/v1x/resumes", "GET", 0, False, f"Exception: {str(e)}")
        return None

def test_resume_get(resume_id):
    """Test getting a specific resume"""
    print_header("6. TESTING RESUME GET BY ID")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1x/resumes/{resume_id}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_result(f"/api/v1x/resumes/{resume_id}", "GET", resp.status_code, True,
                        f"Title: {data.get('title', 'N/A')}")
            print(f"   → Template: {data.get('template', 'N/A')}")
            print(f"   → Skills: {len(data.get('skills', []))} items")
            print(f"   → Work Experience: {len(data.get('work_experiences', []))} items")
            print(f"   → Education: {len(data.get('education', []))} items")
            return data
        else:
            print_result(f"/api/v1x/resumes/{resume_id}", "GET", resp.status_code, False,
                        f"Error: {resp.text[:200]}")
            return None
    except Exception as e:
        print_result(f"/api/v1x/resumes/{resume_id}", "GET", 0, False, f"Exception: {str(e)}")
        return None

def test_resume_update(resume_id):
    """Test updating a resume"""
    print_header("7. TESTING RESUME UPDATE")
    
    payload = {
        "title": f"Updated Resume - {datetime.now().strftime('%H:%M:%S')}",
        "template": "modern-professional",
        "font_family": "Inter",
        "accent_color": "#8b5cf6",
        "layout": "two-column"
    }
    
    try:
        resp = session.patch(
            f"{BASE_URL}/api/v1x/resumes/{resume_id}",
            json=payload
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print_result(f"/api/v1x/resumes/{resume_id}", "PATCH", resp.status_code, True,
                        f"Updated title: {data.get('title', 'N/A')}")
            print(f"   → Template: {data.get('template', 'N/A')}")
            print(f"   → Font: {data.get('font_family', 'N/A')}")
            print(f"   → Accent: {data.get('accent_color', 'N/A')}")
            print(f"   → Layout: {data.get('layout', 'N/A')}")
            return data
        else:
            print_result(f"/api/v1x/resumes/{resume_id}", "PATCH", resp.status_code, False,
                        f"Error: {resp.text[:200]}")
            return None
    except Exception as e:
        print_result(f"/api/v1x/resumes/{resume_id}", "PATCH", 0, False, f"Exception: {str(e)}")
        return None

def test_resume_templates():
    """Test resume templates endpoint"""
    print_header("8. TESTING RESUME TEMPLATES")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1x/resume-templates")
        
        if resp.status_code == 200:
            data = resp.json()
            count = len(data) if isinstance(data, list) else 0
            print_result("/api/v1x/resume-templates", "GET", resp.status_code, True,
                        f"Found {count} template(s)")
            if isinstance(data, list) and len(data) > 0:
                categories = set(t.get('category') for t in data if t.get('category'))
                ats_count = sum(1 for t in data if t.get('is_ats_friendly'))
                print(f"   → Categories: {', '.join(sorted(categories))}")
                print(f"   → ATS-friendly: {ats_count}/{count}")
                print(f"   → First template: {data[0].get('name', 'N/A')} ({data[0].get('category', 'N/A')})")
            return data
        else:
            print_result("/api/v1x/resume-templates", "GET", resp.status_code, False,
                        f"Error: {resp.text[:200]}")
            return None
    except Exception as e:
        print_result("/api/v1x/resume-templates", "GET", 0, False, f"Exception: {str(e)}")
        return None

def test_resume_delete(resume_id):
    """Test deleting a resume"""
    print_header("9. TESTING RESUME DELETE")
    
    try:
        resp = session.delete(f"{BASE_URL}/api/v1x/resumes/{resume_id}")
        
        if resp.status_code in [200, 204]:
            print_result(f"/api/v1x/resumes/{resume_id}", "DELETE", resp.status_code, True,
                        "Resume deleted successfully")
            return True
        else:
            print_result(f"/api/v1x/resumes/{resume_id}", "DELETE", resp.status_code, False,
                        f"Error: {resp.text[:200]}")
            return False
    except Exception as e:
        print_result(f"/api/v1x/resumes/{resume_id}", "DELETE", 0, False, f"Exception: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("  🧪 SKILLFORGE API ENDPOINT TEST SUITE")
    print("  Testing Auth & Resume CRUD Operations")
    print("="*70)
    print(f"\n📡 Base URL: {BASE_URL}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Track results
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # 1. Signup
    email, password, signup_data = test_signup()
    if email:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n❌ Signup failed. Cannot continue tests.")
        return
    results["total"] += 1
    
    # 2. Login
    login_data = test_login(email, password)
    if login_data:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n❌ Login failed. Cannot continue tests.")
        return
    results["total"] += 1
    
    # 3. /me endpoint
    me_data = test_me()
    if me_data:
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["total"] += 1
    
    # 4. Create resume
    resume_id, resume_data = test_resume_create()
    if resume_id:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Resume creation failed. Skipping CRUD tests.")
        print_summary(results)
        return
    results["total"] += 1
    
    # 5. List resumes
    list_data = test_resume_list()
    if list_data is not None:
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["total"] += 1
    
    # 6. Get resume by ID
    get_data = test_resume_get(resume_id)
    if get_data:
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["total"] += 1
    
    # 7. Update resume
    update_data = test_resume_update(resume_id)
    if update_data:
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["total"] += 1
    
    # 8. Templates
    templates_data = test_resume_templates()
    if templates_data is not None:
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["total"] += 1
    
    # 9. Delete resume
    delete_success = test_resume_delete(resume_id)
    if delete_success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["total"] += 1
    
    # Print summary
    print_summary(results)

def print_summary(results):
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    print(f"\n  Total Tests:  {results['total']}")
    print(f"  ✅ Passed:    {results['passed']} ({results['passed']/results['total']*100:.0f}%)")
    print(f"  ❌ Failed:    {results['failed']} ({results['failed']/results['total']*100:.0f}%)")
    print("\n" + "="*70)
    
    if results['failed'] == 0:
        print("  🎉 ALL TESTS PASSED!")
    else:
        print(f"  ⚠️  {results['failed']} test(s) failed. Check output above.")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.\n")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
