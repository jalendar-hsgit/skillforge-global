"""
Comprehensive API Endpoint Testing
Tests: Signup, Login, Resume CRUD, Templates
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"
session = requests.Session()

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(endpoint, method, status, message, data=None):
    """Print test result"""
    icon = "✅" if status < 400 else "❌"
    print(f"\n{icon} {method} {endpoint}")
    print(f"   Status: {status} - {message}")
    if data and isinstance(data, dict):
        # Print key fields only
        for key in ['id', 'email', 'full_name', 'title', 'template', 'name', 'category', 'message']:
            if key in data:
                print(f"   {key}: {data[key]}")

def test_signup():
    """Test user signup"""
    print_section("1. SIGNUP ENDPOINT TEST")
    
    # Generate unique email
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"test_{timestamp}@skillforge.com"
    
    payload = {
        "email": email,
        "password": "Test123!@#",
        "full_name": "Test User"
    }
    
    try:
        resp = session.post(f"{BASE_URL}/api/v1/auth/signup", json=payload)
        
        if resp.status_code == 201:
            data = resp.json()
            print_result("/api/v1/auth/signup", "POST", resp.status_code, "User created successfully", data)
            return email, "Test123!@#", True
        elif resp.status_code == 400:
            print_result("/api/v1/auth/signup", "POST", resp.status_code, "User already exists", resp.json())
            return email, "Test123!@#", False
        else:
            print_result("/api/v1/auth/signup", "POST", resp.status_code, "Unexpected response", resp.json())
            return None, None, False
    except Exception as e:
        print(f"❌ Signup failed: {e}")
        return None, None, False

def test_login(email, password):
    """Test user login"""
    print_section("2. LOGIN ENDPOINT TEST")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        resp = session.post(f"{BASE_URL}/api/v1/auth/login", json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            print_result("/api/v1/auth/login", "POST", resp.status_code, "Login successful", data)
            
            # Check for token cookie
            if 'token' in session.cookies:
                print(f"   ✅ Token cookie set: {session.cookies['token'][:20]}...")
                return True
            else:
                print(f"   ⚠️  No token cookie found")
                return False
        else:
            print_result("/api/v1/auth/login", "POST", resp.status_code, "Login failed", resp.json())
            return False
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def test_get_me():
    """Test get current user"""
    print_section("3. GET CURRENT USER TEST")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1/auth/me")
        
        if resp.status_code == 200:
            data = resp.json()
            print_result("/api/v1/auth/me", "GET", resp.status_code, "User info retrieved", data)
            return data.get('id')
        else:
            print_result("/api/v1/auth/me", "GET", resp.status_code, "Failed to get user", resp.json())
            return None
    except Exception as e:
        print(f"❌ Get me failed: {e}")
        return None

def test_create_resume():
    """Test create resume"""
    print_section("4. CREATE RESUME TEST")
    
    payload = {
        "title": "Software Engineer Resume",
        "template": "modern",
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "location": "San Francisco, CA",
        "professional_summary": "Experienced software engineer with 5+ years in full-stack development.",
        "work_experiences": [],
        "education": [],
        "skills": ["Python", "JavaScript", "React", "FastAPI"],
        "projects": [],
        "certificates": [],
        "achievements": []
    }
    
    try:
        resp = session.post(f"{BASE_URL}/api/v1x/resumes", json=payload)
        
        if resp.status_code == 201:
            data = resp.json()
            print_result("/api/v1x/resumes", "POST", resp.status_code, "Resume created", data)
            return data.get('id')
        else:
            print_result("/api/v1x/resumes", "POST", resp.status_code, "Failed to create resume", resp.json())
            return None
    except Exception as e:
        print(f"❌ Create resume failed: {e}")
        return None

def test_list_resumes():
    """Test list resumes"""
    print_section("5. LIST RESUMES TEST")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1x/resumes")
        
        if resp.status_code == 200:
            data = resp.json()
            count = len(data) if isinstance(data, list) else 0
            print_result("/api/v1x/resumes", "GET", resp.status_code, f"Retrieved {count} resumes", 
                        {"count": count, "first_title": data[0].get('title') if data else None})
            return True
        else:
            print_result("/api/v1x/resumes", "GET", resp.status_code, "Failed to list resumes", resp.json())
            return False
    except Exception as e:
        print(f"❌ List resumes failed: {e}")
        return False

def test_get_resume(resume_id):
    """Test get single resume"""
    print_section("6. GET RESUME BY ID TEST")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1x/resumes/{resume_id}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_result(f"/api/v1x/resumes/{resume_id}", "GET", resp.status_code, "Resume retrieved", data)
            return True
        else:
            print_result(f"/api/v1x/resumes/{resume_id}", "GET", resp.status_code, "Failed to get resume", resp.json())
            return False
    except Exception as e:
        print(f"❌ Get resume failed: {e}")
        return False

def test_update_resume(resume_id):
    """Test update resume"""
    print_section("7. UPDATE RESUME TEST")
    
    payload = {
        "title": "Senior Software Engineer Resume - Updated",
        "template": "professional",
        "font_family": "Roboto",
        "accent_color": "#2563eb",
        "layout": "two-column"
    }
    
    try:
        resp = session.patch(f"{BASE_URL}/api/v1x/resumes/{resume_id}", json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            print_result(f"/api/v1x/resumes/{resume_id}", "PATCH", resp.status_code, "Resume updated", data)
            return True
        else:
            print_result(f"/api/v1x/resumes/{resume_id}", "PATCH", resp.status_code, "Failed to update", resp.json())
            return False
    except Exception as e:
        print(f"❌ Update resume failed: {e}")
        return False

def test_list_templates():
    """Test list resume templates"""
    print_section("8. LIST TEMPLATES TEST")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1x/resume-templates")
        
        if resp.status_code == 200:
            data = resp.json()
            count = len(data) if isinstance(data, list) else 0
            print_result("/api/v1x/resume-templates", "GET", resp.status_code, f"Retrieved {count} templates", 
                        {"count": count, "first_template": data[0].get('name') if data else None})
            return True
        else:
            print_result("/api/v1x/resume-templates", "GET", resp.status_code, "Failed to list templates", resp.json())
            return False
    except Exception as e:
        print(f"❌ List templates failed: {e}")
        return False

def test_get_categories():
    """Test get template categories"""
    print_section("9. GET CATEGORIES TEST")
    
    try:
        resp = session.get(f"{BASE_URL}/api/v1x/resume-templates/categories")
        
        if resp.status_code == 200:
            data = resp.json()
            print_result("/api/v1x/resume-templates/categories", "GET", resp.status_code, 
                        f"Retrieved {len(data)} categories", {"categories": data})
            return True
        else:
            print_result("/api/v1x/resume-templates/categories", "GET", resp.status_code, "Failed", resp.json())
            return False
    except Exception as e:
        print(f"❌ Get categories failed: {e}")
        return False

def test_delete_resume(resume_id):
    """Test delete resume"""
    print_section("10. DELETE RESUME TEST")
    
    try:
        resp = session.delete(f"{BASE_URL}/api/v1x/resumes/{resume_id}")
        
        if resp.status_code == 204:
            print_result(f"/api/v1x/resumes/{resume_id}", "DELETE", resp.status_code, "Resume deleted successfully", {})
            return True
        else:
            print_result(f"/api/v1x/resumes/{resume_id}", "DELETE", resp.status_code, "Failed to delete", resp.json())
            return False
    except Exception as e:
        print(f"❌ Delete resume failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  🧪 SKILLFORGE API ENDPOINT TESTING")
    print("  Backend: http://127.0.0.1:8001")
    print("="*70)
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 10
    }
    
    # Test flow
    email, password, signup_success = test_signup()
    
    if not email:
        print("\n❌ Cannot proceed without valid credentials")
        return
    
    # If signup failed (user exists), try login with existing user
    if not signup_success:
        email = "test@example.com"  # Fallback to default test user
        password = "password123"
    
    # Login
    login_success = test_login(email, password)
    if login_success:
        results["passed"] += 2  # Signup + Login
    else:
        results["failed"] += 2
        print("\n❌ Cannot proceed without authentication")
        print_summary(results)
        return
    
    # Get current user
    user_id = test_get_me()
    if user_id:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Resume operations
    resume_id = test_create_resume()
    if resume_id:
        results["passed"] += 1
        
        # List resumes
        if test_list_resumes():
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Get resume
        if test_get_resume(resume_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Update resume
        if test_update_resume(resume_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Delete resume
        if test_delete_resume(resume_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    else:
        results["failed"] += 5  # Create, list, get, update, delete all failed
    
    # Template operations
    if test_list_templates():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    if test_get_categories():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Summary
    print_summary(results)

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    print(f"\nTotal Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    success_rate = (results['passed'] / results['total']) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 All tests passed! API is fully functional.")
    elif success_rate >= 80:
        print("\n✅ Most tests passed. Minor issues detected.")
    elif success_rate >= 50:
        print("\n⚠️  Some tests failed. Review errors above.")
    else:
        print("\n❌ Multiple failures. API needs attention.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
