"""
Test script for Resume Builder and Hiring Platform APIs
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code < 400:
        print("✅ SUCCESS")
        if response.text:
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
    else:
        print("❌ FAILED")
        print(response.text)
    print()

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/healthz")
    print_response("Health Check", response)
    return response.status_code == 200

def test_signup():
    """Create a test user"""
    data = {
        "email": "test_hiring@example.com",
        "password": "TestPass123!",
        "name": "Test Hiring User"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=data)
    print_response("User Signup", response)
    return response.status_code in [200, 201, 400]  # 400 if user exists

def test_login():
    """Login and get auth token"""
    data = {
        "email": "test_hiring@example.com",
        "password": "TestPass123!"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=data)
    print_response("User Login", response)
    
    # Extract token from cookie
    if response.status_code == 200:
        cookies = response.cookies
        return cookies
    return None

def test_create_resume(cookies):
    """Test resume creation"""
    data = {
        "title": "Software Engineer Resume",
        "template_name": "modern",
        "target_role": "Senior Software Engineer",
        "summary": "Experienced full-stack developer with 5+ years building scalable web applications using React, Node.js, and Python."
    }
    response = requests.post(f"{BASE_URL}/api/v1x/resumes", json=data, cookies=cookies)
    print_response("Create Resume", response)
    
    if response.status_code in [200, 201]:
        return response.json()["id"]
    return None

def test_add_work_experience(resume_id, cookies):
    """Test adding work experience"""
    data = {
        "company": "Tech Corp Inc",
        "position": "Senior Software Engineer",
        "start_date": "2020-01-01",
        "end_date": "2024-10-31",
        "description": "Led development of microservices architecture",
        "location": "San Francisco, CA",
        "is_current": False,
        "bullet_points": [
            "Architected and deployed 15+ microservices handling 1M+ daily requests",
            "Reduced API response time by 60% through optimization and caching strategies",
            "Mentored team of 5 junior developers, improving code quality by 40%"
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/resumes/{resume_id}/work-experience",
        json=data,
        cookies=cookies
    )
    print_response("Add Work Experience", response)
    return response.status_code in [200, 201]

def test_add_skills(resume_id, cookies):
    """Test adding skills in bulk"""
    data = {
        "skills": [
            {"name": "Python", "category": "programming", "proficiency": "expert"},
            {"name": "React", "category": "framework", "proficiency": "advanced"},
            {"name": "Node.js", "category": "backend", "proficiency": "advanced"},
            {"name": "Docker", "category": "devops", "proficiency": "intermediate"},
            {"name": "AWS", "category": "cloud", "proficiency": "advanced"}
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/resumes/{resume_id}/skills/bulk",
        json=data,
        cookies=cookies
    )
    print_response("Add Skills (Bulk)", response)
    return response.status_code in [200, 201]

def test_ai_bullet_points(cookies):
    """Test AI bullet point generator"""
    data = {
        "responsibility": "Managed development team and built features",
        "role": "Senior Software Engineer"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/resumes/ai/bullet-points",
        json=data,
        cookies=cookies
    )
    print_response("AI Bullet Points Generator", response)
    return response.status_code == 200

def test_ai_project_generator(cookies):
    """Test AI project idea generator"""
    data = {
        "difficulty": "intermediate",
        "tech_stack": ["Python", "React", "PostgreSQL"]
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/resumes/ai/generate-project",
        json=data,
        cookies=cookies
    )
    print_response("AI Project Generator", response)
    return response.status_code == 200

def test_create_job_posting(cookies):
    """Test job posting creation"""
    data = {
        "title": "Senior Full-Stack Engineer",
        "description": "We're looking for an experienced full-stack engineer to join our growing team. You'll work on building scalable web applications using modern technologies.",
        "requirements": "5+ years experience with React, Node.js, and Python. Experience with microservices and cloud platforms (AWS/GCP). Strong problem-solving skills.",
        "salary_range": "$120,000 - $180,000",
        "location": "San Francisco, CA",
        "remote_option": True,
        "required_skills": ["Python", "React", "Node.js", "AWS", "Microservices"],
        "nice_to_have_skills": ["Docker", "Kubernetes", "GraphQL"],
        "experience_level": "senior",
        "employment_type": "full-time"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/hiring/jobs",
        json=data,
        cookies=cookies
    )
    print_response("Create Job Posting", response)
    
    if response.status_code in [200, 201]:
        return response.json()["id"]
    return None

def test_submit_application(job_id, resume_id, cookies):
    """Test job application submission with AI matching"""
    data = {
        "job_id": job_id,
        "resume_id": resume_id,
        "cover_letter": "I am excited to apply for the Senior Full-Stack Engineer position. With 5+ years of experience building scalable applications, I believe I would be a great fit for your team."
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/hiring/applications",
        json=data,
        cookies=cookies
    )
    print_response("Submit Job Application (with AI Matching)", response)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"🎯 Match Score: {result.get('match_score', 'N/A')}/100")
        print(f"💡 Recommendation: {result.get('recommendation', 'N/A')}")
        print(f"✅ Matching Skills: {', '.join(result.get('matching_skills', []))}")
        print(f"❌ Missing Skills: {', '.join(result.get('missing_skills', []))}")
        return result["id"]
    return None

def test_schedule_interview(application_id, cookies):
    """Test interview scheduling"""
    scheduled_time = (datetime.now() + timedelta(days=3)).isoformat()
    data = {
        "interview_type": "technical",
        "scheduled_at": scheduled_time,
        "duration_minutes": 60,
        "interviewers": ["hiring.manager@company.com", "tech.lead@company.com"],
        "notes": "Focus on system design and coding skills"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/hiring/applications/{application_id}/schedule-interview",
        json=data,
        cookies=cookies
    )
    print_response("Schedule Interview", response)
    return response.status_code in [200, 201]

def test_verify_education(application_id, cookies):
    """Test education verification"""
    response = requests.post(
        f"{BASE_URL}/api/v1x/hiring/applications/{application_id}/verify-education",
        cookies=cookies
    )
    print_response("Start Education Verification", response)
    return response.status_code in [200, 201]

def test_ats_analysis(resume_id, cookies):
    """Test ATS analysis"""
    data = {
        "resume_id": resume_id,
        "job_description": "Looking for Senior Software Engineer with 5+ years Python, React, microservices experience. Must have AWS/cloud platform knowledge."
    }
    response = requests.post(
        f"{BASE_URL}/api/v1x/resumes/ai/ats-analysis",
        json=data,
        cookies=cookies
    )
    print_response("ATS Analysis", response)
    return response.status_code == 200

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 TESTING RESUME BUILDER & HIRING PLATFORM")
    print("="*60)
    
    # Test health
    if not test_health():
        print("❌ Server not responding. Exiting.")
        return
    
    # Auth tests
    test_signup()
    cookies = test_login()
    if not cookies:
        print("❌ Login failed. Exiting.")
        return
    
    print("\n" + "="*60)
    print("📝 TESTING RESUME BUILDER APIs")
    print("="*60)
    
    # Resume tests
    resume_id = test_create_resume(cookies)
    if resume_id:
        test_add_work_experience(resume_id, cookies)
        test_add_skills(resume_id, cookies)
        test_ats_analysis(resume_id, cookies)
    
    # AI tests
    test_ai_bullet_points(cookies)
    test_ai_project_generator(cookies)
    
    print("\n" + "="*60)
    print("💼 TESTING HIRING PLATFORM APIs")
    print("="*60)
    
    # Hiring tests
    job_id = test_create_job_posting(cookies)
    if job_id and resume_id:
        application_id = test_submit_application(job_id, resume_id, cookies)
        if application_id:
            test_schedule_interview(application_id, cookies)
            test_verify_education(application_id, cookies)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    main()
