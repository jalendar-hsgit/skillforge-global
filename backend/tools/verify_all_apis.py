"""
Comprehensive API verification script.
Tests all backend API endpoints to ensure they're functional.
"""
import sys
sys.path.insert(0, r"D:\python code\sfg\skillforge-global\backend")

from fastapi.testclient import TestClient
from app.main import app
import time
import json

client = TestClient(app)

# Track all results
results = []
total_endpoints = 0

def test_endpoint(name, method, url, **kwargs):
    """Test an endpoint and record result"""
    global total_endpoints
    total_endpoints += 1
    
    try:
        if method == "GET":
            r = client.get(url, **kwargs)
        elif method == "POST":
            r = client.post(url, **kwargs)
        elif method == "PUT":
            r = client.put(url, **kwargs)
        elif method == "DELETE":
            r = client.delete(url, **kwargs)
        
        success = r.status_code < 400
        results.append((name, r.status_code, success))
        status = "PASS" if success else "FAIL"
        print(f"  [{total_endpoints}] {name}: {r.status_code} - {status}")
        return r
    except Exception as e:
        results.append((name, "ERROR", False))
        print(f"  [{total_endpoints}] {name}: ERROR - {str(e)[:50]}")
        return None

print("="*70)
print("COMPREHENSIVE API VERIFICATION")
print("="*70)

# Setup: Create test user and get token
email = f"test_{int(time.time())}@example.com"
token = None

print("\n[SETUP] Creating test user and logging in...")
r = client.post("/api/v1/auth/signup", json={
    "email": email,
    "password": "test123",
    "full_name": "Test User"
})
if r.status_code == 200:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "test123"})
    token = r.cookies.get("token")
    print(f"  Token obtained: {token[:20] if token else 'None'}...")

print("\n" + "="*70)
print("TESTING BACKEND API ENDPOINTS")
print("="*70)

# Health & Core
print("\n[CORE ENDPOINTS]")
test_endpoint("Health Check", "GET", "/healthz")
test_endpoint("Docs", "GET", "/docs")

# Authentication (v1)
print("\n[AUTHENTICATION - /api/v1/auth]")
test_endpoint("Get Current User", "GET", "/api/v1/auth/me", cookies={"token": token})
test_endpoint("Logout", "POST", "/api/v1/auth/logout", cookies={"token": token})

# Re-login after logout
r = client.post("/api/v1/auth/login", json={"email": email, "password": "test123"})
token = r.cookies.get("token")

# Courses (v1)
print("\n[COURSES - /api/v1/courses]")
test_endpoint("List Courses", "GET", "/api/v1/courses")
r = test_endpoint("Get First Course", "GET", "/api/v1/courses/1")

# Progress (v1)
print("\n[PROGRESS - /api/v1/progress]")
test_endpoint("Get Progress", "GET", "/api/v1/progress?path=python-fundamentals", cookies={"token": token})
test_endpoint("Update Progress", "POST", "/api/v1/progress", 
              json={"path": "test", "module": 1, "lesson": 1, "completed": True},
              cookies={"token": token})

# Quizzes (v1)
print("\n[QUIZZES - /api/v1/quizzes]")
test_endpoint("Get Quiz", "GET", "/api/v1/quizzes/python-basics")
test_endpoint("Submit Quiz", "POST", "/api/v1/quizzes/python-basics/submit",
              json={"answers": {}}, cookies={"token": token})

# Chat (v1)
print("\n[CHAT - /api/v1/chat]")
test_endpoint("Chat Completion", "POST", "/api/v1/chat",
              json={"messages": [{"role": "user", "content": "Hello"}], "model": "gpt-3.5-turbo"},
              cookies={"token": token})

# Credits (v1)
print("\n[CREDITS - /api/v1/credits]")
test_endpoint("Get Credits", "GET", "/api/v1/credits", cookies={"token": token})

# Resume Templates (v1x)
print("\n[RESUME TEMPLATES - /api/v1x/resume-templates]")
r = test_endpoint("List Resume Templates", "GET", "/api/v1x/resume-templates")
templates = r.json() if r and r.status_code == 200 else []
if templates:
    test_endpoint("Get Template Detail", "GET", f"/api/v1x/resume-templates/{templates[0]['id']}")

# Resumes (v1x)
print("\n[RESUMES - /api/v1x/resumes]")
test_endpoint("List User Resumes", "GET", "/api/v1x/resumes", cookies={"token": token})

if templates:
    r = test_endpoint("Create Resume", "POST", "/api/v1x/resumes/",
                     json={"title": "Test Resume", "template_id": str(templates[0]['id']),
                           "full_name": "Test", "email": "test@test.com"},
                     cookies={"token": token})
    
    if r and r.status_code in [200, 201]:
        resume_id = r.json()['id']
        test_endpoint("Get Resume Detail", "GET", f"/api/v1x/resumes/{resume_id}", cookies={"token": token})
        test_endpoint("Export Resume PDF", "GET", f"/api/v1x/resumes/{resume_id}/export?format=pdf", 
                     cookies={"token": token})
        test_endpoint("Export Resume DOCX", "GET", f"/api/v1x/resumes/{resume_id}/export?format=docx",
                     cookies={"token": token})

# Cover Letters (v1x)
print("\n[COVER LETTERS - /api/v1x/cover-letters]")
test_endpoint("List Cover Letters", "GET", "/api/v1x/cover-letters", cookies={"token": token})

# Job Applications (v1x)
print("\n[JOB APPLICATIONS - /api/v1x/job-applications]")
test_endpoint("List Applications", "GET", "/api/v1x/job-applications", cookies={"token": token})

# Courses DB (v1x)
print("\n[COURSES DB - /api/v1x/courses-db]")
test_endpoint("List DB Courses", "GET", "/api/v1x/courses-db")

# Progress DB (v1x)
print("\n[PROGRESS DB - /api/v1x/progress-db]")
test_endpoint("Get User Progress", "GET", "/api/v1x/progress-db", cookies={"token": token})

# Quizzes DB (v1x)
print("\n[QUIZZES DB - /api/v1x/quizzes-db]")
test_endpoint("List DB Quizzes", "GET", "/api/v1x/quizzes-db")

# Coins (v1x)
print("\n[COINS - /api/v1x/coins]")
test_endpoint("Get Coin Balance", "GET", "/api/v1x/coins/balance", cookies={"token": token})
test_endpoint("Get Coin Transactions", "GET", "/api/v1x/coins/transactions", cookies={"token": token})

# Subscriptions (v1x)
print("\n[SUBSCRIPTIONS - /api/v1x/subscriptions]")
test_endpoint("Get Subscription Status", "GET", "/api/v1x/subscriptions/status", cookies={"token": token})

# Payments (v1x)
print("\n[PAYMENTS - /api/v1x/payments]")
test_endpoint("Get Payment History", "GET", "/api/v1x/payments/history", cookies={"token": token})

# Mentors (v1x)
print("\n[MENTORS - /api/v1x/mentors]")
test_endpoint("List Mentors", "GET", "/api/v1x/mentors")

# YouTube Sync (v1x)
print("\n[YOUTUBE SYNC - /api/v1x/youtube]")
test_endpoint("Get YouTube Sync Status", "GET", "/api/v1x/youtube/sync/status", cookies={"token": token})

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

passed = sum(1 for _, _, success in results if success)
failed = sum(1 for _, _, success in results if not success)

print(f"\nTotal Endpoints Tested: {total_endpoints}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {(passed/total_endpoints*100):.1f}%")

if failed > 0:
    print("\nFailed Endpoints:")
    for name, status, success in results:
        if not success:
            print(f"  - {name}: {status}")

print("\n" + "="*70)
if failed == 0:
    print("PASS - ALL API ENDPOINTS WORKING")
else:
    print(f"PARTIAL - {failed} endpoints need attention")
print("="*70)
