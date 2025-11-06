"""
Test resume export endpoints (PDF, DOCX, TXT)
Uses existing credentials to avoid signup rate limit.
Run: python test_exports.py
"""
import requests
import sys

BASE = "http://127.0.0.1:8001"
AUTH = f"{BASE}/api/v1/auth"
RES  = f"{BASE}/api/v1x/resumes"

# Use existing test user from E2E tests
EMAIL = "test_lfupg_1762328544240@example.com"  # User ID 17
PASSWORD = "P@ssw0rd!123"


def section(title: str):
    print("\n" + "="*80)
    print(title)
    print("="*80)


def main():
    s = requests.Session()

    # Try to login (or signup if first time)
    section("1) Login/Signup")
    r = s.post(f"{AUTH}/login", json={"email": EMAIL, "password": PASSWORD})
    if r.status_code == 401:
        print("User doesn't exist, creating...")
        r = s.post(f"{AUTH}/signup", json={
            "email": EMAIL,
            "password": PASSWORD,
            "full_name": "Export Test User"
        })
        if r.status_code != 200:
            print(f"Signup failed: {r.status_code} {r.text}")
            return
        # Now login
        r = s.post(f"{AUTH}/login", json={"email": EMAIL, "password": PASSWORD})

    if r.status_code != 200:
        print(f"Login failed: {r.status_code} {r.text}")
        return

    print("Logged in")

    # Create a resume for export testing
    section("2) Create Resume")
    resume_data = {
        "title": "Export Test Resume",
        "template_id": "modern",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "location": "San Francisco, CA",
        "summary": "Experienced software engineer with 5+ years in full-stack development."
    }
    r = s.post(f"{RES}/", json=resume_data)
    if r.status_code not in (200, 201):
        print(f"Resume create failed: {r.status_code} {r.text[:200]}")
        return

    resume = r.json()
    rid = resume["id"]
    print(f"Resume created: ID={rid}")

    # Test PDF export
    section("3) Export PDF")
    r = s.get(f"{RES}/{rid}/export?format=pdf")
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('content-type')}")
    print(f"Size: {len(r.content)} bytes")

    if r.status_code == 200:
        assert "application/pdf" in r.headers.get("content-type", "")
        assert len(r.content) > 100
        print("PDF export OK")
    else:
        print(f"PDF export failed: {r.text[:500]}")
        return

    # Test DOCX export
    section("4) Export DOCX")
    r = s.get(f"{RES}/{rid}/export?format=docx")
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('content-type')}")
    print(f"Size: {len(r.content)} bytes")

    if r.status_code == 200:
        assert "application/vnd.openxmlformats" in r.headers.get("content-type", "")
        assert len(r.content) > 100
        print("DOCX export OK")
    else:
        print(f"DOCX export failed: {r.text[:500]}")
        return

    # Test TXT export
    section("5) Export TXT")
    r = s.get(f"{RES}/{rid}/export?format=txt")
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('content-type')}")
    print(f"Size: {len(r.content)} bytes")

    if r.status_code == 200:
        assert "text/plain" in r.headers.get("content-type", "")
        assert len(r.content) > 20
        print("TXT export OK")
    else:
        print(f"TXT export failed: {r.text[:500]}")
        return

    # Cleanup
    section("6) Cleanup")
    r = s.delete(f"{RES}/{rid}")
    print(f"Delete: {r.status_code}")

    print("\n" + "="*80)
    print("ALL EXPORT TESTS PASSED")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\nAssertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
