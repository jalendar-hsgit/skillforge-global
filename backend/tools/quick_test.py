"""Quick application test"""
import sys, time
sys.path.insert(0, r"D:\python code\sfg\skillforge-global\backend")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("="*60)
print("TESTING COMPLETE APPLICATION")
print("="*60 + "\n")

results = []

# Test 1: Health
r = client.get("/healthz")
results.append(("Health Check", r.status_code == 200))
print(f"[1] Health Check: {r.status_code} - {'PASS' if r.status_code == 200 else 'FAIL'}")

# Test 2-4: Auth
email = f"test_{int(time.time())}@example.com"
r = client.post("/api/v1/auth/signup", json={"email": email, "password": "test123", "full_name": "Test"})
results.append(("Signup", r.status_code == 200))
print(f"[2] Signup: {r.status_code} - {'PASS' if r.status_code == 200 else 'FAIL'}")

r = client.post("/api/v1/auth/login", json={"email": email, "password": "test123"})
token = r.cookies.get("token")
results.append(("Login", r.status_code == 200 and token))
print(f"[3] Login: {r.status_code} - {'PASS' if r.status_code == 200 and token else 'FAIL'}")

r = client.get("/api/v1/auth/me", cookies={"token": token})
results.append(("Get Me", r.status_code == 200))
print(f"[4] Get Me: {r.status_code} - {'PASS' if r.status_code == 200 else 'FAIL'}")

# Test 5: Courses
r = client.get("/api/v1/courses")
results.append(("List Courses", r.status_code == 200))
print(f"[5] List Courses: {r.status_code} ({len(r.json())} courses) - {'PASS' if r.status_code == 200 else 'FAIL'}")

# Test 6: Templates
r = client.get("/api/v1x/resume-templates")
templates = r.json() if r.status_code == 200 else []
results.append(("Resume Templates", r.status_code == 200))
print(f"[6] Resume Templates: {r.status_code} ({len(templates)} templates) - {'PASS' if r.status_code == 200 else 'FAIL'}")

# Test 7-9: Resume
if templates:
    r = client.post("/api/v1x/resumes/", json={"title": "Test", "template_id": str(templates[0]['id']), "full_name": "Test", "email": "test@test.com"}, cookies={"token": token})
    results.append(("Create Resume", r.status_code in [200, 201]))
    print(f"[7] Create Resume: {r.status_code} - {'PASS' if r.status_code in [200, 201] else 'FAIL'}")
    
    if r.status_code in [200, 201]:
        resume_id = r.json()['id']
        
        r = client.get(f"/api/v1x/resumes/{resume_id}/export?format=pdf", cookies={"token": token})
        results.append(("Export PDF", r.status_code == 200))
        print(f"[8] Export PDF: {r.status_code} ({len(r.content)/1024:.1f}KB) - {'PASS' if r.status_code == 200 else 'FAIL'}")
        
        r = client.get(f"/api/v1x/resumes/{resume_id}/export?format=docx", cookies={"token": token})
        results.append(("Export DOCX", r.status_code == 200))
        print(f"[9] Export DOCX: {r.status_code} ({len(r.content)/1024:.1f}KB) - {'PASS' if r.status_code == 200 else 'FAIL'}")

# Summary
print("\n" + "="*60)
passed = sum(1 for _, success in results if success)
total = len(results)
print(f"RESULTS: {passed}/{total} tests passed")
if passed == total:
    print("PASS - ALL TESTS PASSED - APPLICATION FULLY FUNCTIONAL")
else:
    print(f"FAIL - {total - passed} tests failed")
    for name, success in results:
        if not success:
            print(f"  - {name}")
print("="*60)
