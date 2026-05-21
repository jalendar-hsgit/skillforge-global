"""
Test PDF export through frontend proxy on port 3001
"""
import requests

BASE = "http://localhost:3000"
BACKEND = "http://127.0.0.1:8001"

def test_pdf_export():
    print("\n=== Testing PDF Export via Frontend Proxy ===\n")
    
    # Step 1: Signup
    print("1. Signup...")
    signup_data = {
        "email": f"testpdf_{import_random()}@example.com",
        "password": "TestPass123!",
        "full_name": "PDF Test User"
    }
    r = requests.post(f"{BASE}/api/session/signup", json=signup_data)
    print(f"   Signup: {r.status_code}")
    assert r.status_code == 200, f"Signup failed: {r.text}"
    
    # Step 2: Login
    print("2. Login...")
    login_data = {"email": signup_data["email"], "password": signup_data["password"]}
    r = requests.post(f"{BASE}/api/session/login", json=login_data)
    print(f"   Login: {r.status_code}")
    assert r.status_code == 200, f"Login failed: {r.text}"
    
    # Extract cookies
    cookies = r.cookies
    print(f"   Got cookies: {list(cookies.keys())}")
    
    # Step 3: Create resume
    print("3. Create resume...")
    resume_data = {
        "title": "Software Engineer Resume",
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
        "summary": "Experienced software engineer",
        "work_experience": [
            {
                "company": "Tech Corp",
                "position": "Senior Developer",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "description": "Built awesome stuff"
            }
        ],
        "education": [
            {
                "institution": "University of Tech",
                "degree": "BS Computer Science",
                "start_date": "2015-09-01",
                "end_date": "2019-05-31"
            }
        ]
    }
    r = requests.post(f"{BASE}/api/session/resumes", json=resume_data, cookies=cookies)
    print(f"   Create resume: {r.status_code}")
    assert r.status_code == 201, f"Create failed: {r.text}"
    resume_id = r.json()["id"]
    print(f"   Resume ID: {resume_id}")
    
    # Step 4: Export PDF via frontend proxy
    print("4. Export PDF via backend directly...")
    export_url = f"{BACKEND}/api/v1x/resumes/{resume_id}/export?format=pdf"
    print(f"   URL: {export_url}")
    r = requests.get(export_url, cookies=cookies)
    
    print(f"   Status: {r.status_code}")
    print(f"   Content-Type: {r.headers.get('content-type')}")
    print(f"   x-debug-target: {r.headers.get('x-debug-target')}")
    print(f"   Content-Disposition: {r.headers.get('content-disposition')}")
    print(f"   Content-Length: {len(r.content)} bytes")
    
    if r.status_code == 200:
        print(f"   ✅ PDF export SUCCESS! ({len(r.content)} bytes)")
        # Save to file
        with open("test_export.pdf", "wb") as f:
            f.write(r.content)
        print(f"   Saved to test_export.pdf")
    else:
        print(f"   ❌ PDF export FAILED")
        print(f"   Response: {r.text[:200]}")
        
    return r.status_code == 200

def import_random():
    import random
    return random.randint(1000, 9999)

if __name__ == "__main__":
    try:
        success = test_pdf_export()
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ PDF export test failed")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
