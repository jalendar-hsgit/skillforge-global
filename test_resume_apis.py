"""
Test script for Resume Builder Backend APIs
Tests: CRUD operations, AI features, ATS scoring
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_health_check():
    """Test 1: Health Check"""
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        print_test("Health Check", response.status_code == 200, f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_auth_signup():
    """Test 2: User Signup"""
    try:
        payload = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "Test1234!",
            "full_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=payload, timeout=5)
        success = response.status_code in [200, 201]
        print_test("User Signup", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            return data.get("access_token")
        return None
    except Exception as e:
        print_test("User Signup", False, str(e))
        return None

def test_create_resume(token):
    """Test 3: Create Resume"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": "Test Resume - Software Engineer",
            "template": "modern",
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-234-567-8900",
            "location": "San Francisco, CA"
        }
        response = requests.post(f"{BASE_URL}/api/v1x/resumes", json=payload, headers=headers, timeout=5)
        success = response.status_code in [200, 201]
        print_test("Create Resume", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            return data.get("id")
        return None
    except Exception as e:
        print_test("Create Resume", False, str(e))
        return None

def test_get_resume(token, resume_id):
    """Test 4: Get Resume"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1x/resumes/{resume_id}", headers=headers, timeout=5)
        success = response.status_code == 200
        print_test("Get Resume", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("Get Resume", False, str(e))
        return False

def test_ai_bullet_points(token):
    """Test 5: AI Bullet Points Generator"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "position": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": "Led development of microservices architecture"
        }
        response = requests.post(f"{BASE_URL}/api/v1x/resume-ai/bullet-points", json=payload, headers=headers, timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            bullet_count = len(data.get("bullet_points", []))
            print_test("AI Bullet Points", success, f"Generated {bullet_count} bullets")
        else:
            print_test("AI Bullet Points", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("AI Bullet Points", False, str(e))
        return False

def test_ai_summary(token):
    """Test 6: AI Professional Summary"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "full_name": "John Doe",
            "target_role": "Senior Software Engineer",
            "experience_years": 5,
            "key_skills": ["Python", "React", "AWS", "Docker"],
            "achievements": ["Led team of 5 engineers", "Reduced costs by 30%"]
        }
        response = requests.post(f"{BASE_URL}/api/v1x/resume-ai/summary", json=payload, headers=headers, timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            summary_length = len(data.get("summary", ""))
            print_test("AI Summary", success, f"Generated {summary_length} characters")
        else:
            print_test("AI Summary", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("AI Summary", False, str(e))
        return False

def test_ats_score(token, resume_id):
    """Test 7: ATS Score Analysis"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "job_description": "Looking for a Senior Software Engineer with Python, React, and AWS experience. Must have 5+ years of experience."
        }
        response = requests.post(f"{BASE_URL}/api/v1x/resume-ai/ats-score/{resume_id}", json=payload, headers=headers, timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            score = data.get("overall_score", 0)
            print_test("ATS Score", success, f"Score: {score}/100")
        else:
            print_test("ATS Score", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("ATS Score", False, str(e))
        return False

def test_update_resume(token, resume_id):
    """Test 8: Update Resume"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": "Updated Resume - Senior Software Engineer",
            "template": "classic"
        }
        response = requests.patch(f"{BASE_URL}/api/v1x/resumes/{resume_id}", json=payload, headers=headers, timeout=5)
        success = response.status_code == 200
        print_test("Update Resume", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("Update Resume", False, str(e))
        return False

def test_list_resumes(token):
    """Test 9: List User Resumes"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1x/resumes", headers=headers, timeout=5)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get("total", 0)
            print_test("List Resumes", success, f"Found {count} resume(s)")
        else:
            print_test("List Resumes", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("List Resumes", False, str(e))
        return False

def main():
    print("\n" + "="*50)
    print("  🧪 RESUME BUILDER API TESTS")
    print("="*50 + "\n")
    
    # Test sequence
    if not test_health_check():
        print("\n❌ Backend not running. Please start with:")
        print("   cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")
        return
    
    print("\n📝 Testing Authentication...")
    token = test_auth_signup()
    if not token:
        print("❌ Cannot continue without auth token")
        return
    
    print("\n📄 Testing Resume CRUD...")
    resume_id = test_create_resume(token)
    if resume_id:
        test_get_resume(token, resume_id)
        test_update_resume(token, resume_id)
        test_list_resumes(token)
        
        print("\n🤖 Testing AI Features...")
        test_ai_bullet_points(token)
        test_ai_summary(token)
        test_ats_score(token, resume_id)
    
    print("\n" + "="*50)
    print("  ✅ API TESTS COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
