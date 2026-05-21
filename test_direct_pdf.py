"""
Simple test: Export PDF directly from backend with a known resume ID
"""
import requests

BACKEND = "http://127.0.0.1:8001"

# Use existing test credentials from previous runs
email = "test_1763188156@example.com"  # From earlier successful test
password = "TestPass123!"

print("=== Direct Backend PDF Export Test ===\n")

# Login
print("1. Login...")
r = requests.post(f"{BACKEND}/api/v1/auth/login", json={"email": email, "password": password})
print(f"   Status: {r.status_code}")

if r.status_code != 200:
    print(f"   Failed: {r.text}")
    exit(1)

cookies = r.cookies
print(f"   Cookies: {list(cookies.keys())}")

# Get user's resumes
print("\n2. Get resumes...")
r = requests.get(f"{BACKEND}/api/v1x/resumes", cookies=cookies)
print(f"   Status: {r.status_code}")

if r.status_code == 200:
    resumes = r.json()
    if resumes:
        resume_id = resumes[0]["id"]
        print(f"   Found resume ID: {resume_id}")
        
        # Export PDF
        print(f"\n3. Export PDF for resume {resume_id}...")
        r = requests.get(f"{BACKEND}/api/v1x/resumes/{resume_id}/export?format=pdf", cookies=cookies)
        print(f"   Status: {r.status_code}")
        print(f"   Content-Type: {r.headers.get('content-type')}")
        print(f"   Content-Length: {len(r.content)} bytes")
        
        if r.status_code == 200:
            print(f"   ✅ PDF export SUCCESS!")
            with open("direct_export_test.pdf", "wb") as f:
                f.write(r.content)
            print(f"   Saved to direct_export_test.pdf")
        else:
            print(f"   ❌ PDF export FAILED")
            print(f"   Response: {r.text[:200]}")
    else:
        print("   No resumes found")
else:
    print(f"   Failed: {r.text}")
