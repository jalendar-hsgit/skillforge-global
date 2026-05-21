"""
Frontend Proxy Test - Tests Next.js API routes
"""
import requests
from datetime import datetime

FRONTEND_URL = "http://localhost:3000"

def test_frontend_proxies():
    """Test Next.js proxy endpoints"""
    session = requests.Session()
    email = f"frontend_test_{int(datetime.now().timestamp())}@example.com"
    password = "Test123!"
    
    print("=" * 70)
    print("🔍 FRONTEND PROXY TESTS")
    print("=" * 70)
    print()
    
    # Test 1: Signup via frontend proxy
    print("Test 1: POST /api/session/signup")
    try:
        payload = {"email": email, "password": password, "full_name": "Frontend Test"}
        r = session.post(f"{FRONTEND_URL}/api/session/signup", json=payload, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.text[:200]}")
        print(f"  Result: {'✅ PASS' if r.status_code == 200 else '❌ FAIL'}")
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Result: ❌ FAIL")
    print()
    
    # Test 2: Login via frontend proxy
    print("Test 2: POST /api/session/login")
    try:
        payload = {"email": email, "password": password}
        r = session.post(f"{FRONTEND_URL}/api/session/login", json=payload, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Cookies: {dict(r.cookies)}")
        print(f"  Response: {r.text[:200]}")
        print(f"  Result: {'✅ PASS' if r.status_code == 200 else '❌ FAIL'}")
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Result: ❌ FAIL")
    print()
    
    # Test 3: Get user info via frontend proxy
    print("Test 3: GET /api/session/me")
    try:
        r = session.get(f"{FRONTEND_URL}/api/session/me", timeout=5)
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.text[:200]}")
        print(f"  Result: {'✅ PASS' if r.status_code == 200 else '❌ FAIL'}")
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Result: ❌ FAIL")
    print()
    
    # Test 4: Create resume via frontend proxy
    print("Test 4: POST /api/session/resumes")
    resume_id = None
    try:
        payload = {
            "title": "Frontend Test Resume",
            "full_name": "Jane Smith",
            "email": "jane@example.com"
        }
        r = session.post(f"{FRONTEND_URL}/api/session/resumes", json=payload, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.text[:200]}")
        if r.status_code in [200, 201]:
            data = r.json()
            resume_id = data.get('id')
            print(f"  Resume ID: {resume_id}")
        print(f"  Result: {'✅ PASS' if r.status_code in [200, 201] else '❌ FAIL'}")
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Result: ❌ FAIL")
    print()
    
    # Test 5: Get resume via frontend proxy
    if resume_id:
        print(f"Test 5: GET /api/session/resumes?id={resume_id}")
        try:
            r = session.get(f"{FRONTEND_URL}/api/session/resumes?id={resume_id}", timeout=5)
            print(f"  Status: {r.status_code}")
            print(f"  Response: {r.text[:200]}")
            print(f"  Result: {'✅ PASS' if r.status_code == 200 else '❌ FAIL'}")
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Result: ❌ FAIL")
        print()
        
        # Test 6: Export PDF via frontend proxy
        print(f"Test 6: GET /api/session/v1x/resumes/{resume_id}/export?format=pdf")
        try:
            r = session.get(
                f"{FRONTEND_URL}/api/session/v1x/resumes/{resume_id}/export?format=pdf",
                timeout=15
            )
            print(f"  Status: {r.status_code}")
            print(f"  Content-Type: {r.headers.get('content-type', 'N/A')}")
            print(f"  Content-Length: {len(r.content)} bytes")
            print(f"  x-debug-target: {r.headers.get('x-debug-target', 'N/A')}")
            is_pdf = 'application/pdf' in r.headers.get('content-type', '') or len(r.content) > 1000
            print(f"  Result: {'✅ PASS' if r.status_code == 200 and is_pdf else '❌ FAIL'}")
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Result: ❌ FAIL")
        print()
        
        # Test 7: Export DOCX via frontend proxy
        print(f"Test 7: GET /api/session/v1x/resumes/{resume_id}/export?format=docx")
        try:
            r = session.get(
                f"{FRONTEND_URL}/api/session/v1x/resumes/{resume_id}/export?format=docx",
                timeout=15
            )
            print(f"  Status: {r.status_code}")
            print(f"  Content-Type: {r.headers.get('content-type', 'N/A')}")
            print(f"  Content-Length: {len(r.content)} bytes")
            print(f"  x-debug-target: {r.headers.get('x-debug-target', 'N/A')}")
            is_docx = 'wordprocessingml' in r.headers.get('content-type', '') or len(r.content) > 10000
            print(f"  Result: {'✅ PASS' if r.status_code == 200 and is_docx else '❌ FAIL'}")
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Result: ❌ FAIL")
        print()
    
    print("=" * 70)

if __name__ == "__main__":
    test_frontend_proxies()
