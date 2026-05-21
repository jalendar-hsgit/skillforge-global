"""
End-to-end test for auth (signup/login/me) and resume CRUD.
Run: python api_e2e_test.py
"""
from __future__ import annotations
import requests
import time
import random
import string
import sys

BASE = "http://127.0.0.1:8001"
AUTH = f"{BASE}/api/v1/auth"
RES  = f"{BASE}/api/v1x/resumes"


def rand_email() -> str:
    ts = int(time.time() * 1000)
    letters = ''.join(random.choices(string.ascii_lowercase, k=5))
    return f"test_{letters}_{ts}@example.com"


def section(title: str):
    print("\n" + "."*80)
    print(title)
    print("."*80)


def main():
    # Wait for the server to be ready before starting tests.
    def wait_for_server(timeout: int = 30):
        deadline = time.time() + timeout
        url = BASE + "/healthz"
        print(f"Waiting for server {url} to become available (timeout {timeout}s)")
        while time.time() < deadline:
            try:
                r = requests.get(url, timeout=2)
                if r.status_code == 200:
                    print("Server is ready")
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        print(f"Server did not become ready after {timeout}s")
        return False

    if not wait_for_server(30):
        print("Aborting tests: server not available")
        sys.exit(2)
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})

    # 1) Signup
    section("1) Signup")
    email = rand_email()
    password = "P@ssw0rd!123"
    payload = {"email": email, "password": password, "full_name": "Test User"}
    r = s.post(f"{AUTH}/signup", json=payload)
    print("Signup:", r.status_code, r.text[:120])
    assert r.status_code == 200, f"Signup failed: {r.text}"

    # 2) Login (ensure cookie is set)
    section("2) Login")
    r = s.post(f"{AUTH}/login", json={"email": email, "password": password})
    print("Login:", r.status_code, r.text.strip())
    assert r.status_code == 200, f"Login failed: {r.text}"
    # Cookie debug
    token_cookie = next((c for c in s.cookies if c.name == "token"), None)
    print("Cookie token present:", bool(token_cookie))
    assert token_cookie is not None, "Auth cookie not set"

    # 3) Me
    section("3) Me")
    r = s.get(f"{AUTH}/me")
    print("Me:", r.status_code, r.json())
    assert r.status_code == 200 and r.json().get("email") == email

    # 4) Resume create
    section("4) Resume Create")
    r = s.post(RES + "/", json={"title": "My First Resume", "template_id": "modern"})
    print("Create:", r.status_code)
    assert r.status_code in (200, 201), f"Resume create failed: {r.status_code} {r.text}"
    resume = r.json()
    rid = resume["id"]
    print("Resume ID:", rid)

    # 5) Resume list
    section("5) Resume List")
    r = s.get(RES + "/")
    print("List:", r.status_code, f"count={len(r.json()) if r.ok else 'N/A'}")
    assert r.status_code == 200

    # 6) Resume get by id
    section("6) Resume Get")
    r = s.get(f"{RES}/{rid}")
    print("Get:", r.status_code, r.json().get("title"))
    assert r.status_code == 200

    # 7) Resume update (PATCH)
    section("7) Resume Update")
    r = s.patch(f"{RES}/{rid}", json={"title": "Updated Title", "template_id": "two-column"})
    print("Patch:", r.status_code, r.json().get("title"))
    assert r.status_code == 200 and r.json().get("title") == "Updated Title"

    # 8) Export PDF
    section("8) Export PDF")
    r = s.get(f"{RES}/{rid}/export?format=pdf")
    print("PDF Export:", r.status_code, f"size={len(r.content)} bytes, type={r.headers.get('content-type')}")
    if r.status_code != 200:
        print("ERROR:", r.text[:500])
    assert r.status_code == 200, f"PDF export failed: {r.status_code}"
    assert len(r.content) > 0, "PDF is empty"
    assert "application/pdf" in r.headers.get("content-type", ""), "Wrong content-type for PDF"

    # 9) Export DOCX
    section("9) Export DOCX")
    r = s.get(f"{RES}/{rid}/export?format=docx")
    print("DOCX Export:", r.status_code, f"size={len(r.content)} bytes, type={r.headers.get('content-type')}")
    assert r.status_code == 200, f"DOCX export failed: {r.status_code}"
    assert len(r.content) > 0, "DOCX is empty"
    assert "application/vnd.openxmlformats" in r.headers.get("content-type", ""), "Wrong content-type for DOCX"

    # 10) Export TXT
    section("10) Export TXT")
    r = s.get(f"{RES}/{rid}/export?format=txt")
    print("TXT Export:", r.status_code, f"size={len(r.content)} bytes, type={r.headers.get('content-type')}")
    assert r.status_code == 200, f"TXT export failed: {r.status_code}"
    assert len(r.content) > 0, "TXT is empty"
    assert "text/plain" in r.headers.get("content-type", ""), "Wrong content-type for TXT"

    # 11) Resume delete
    section("11) Resume Delete")
    r = s.delete(f"{RES}/{rid}")
    print("Delete:", r.status_code)
    assert r.status_code == 204

    # 12) Verify deleted
    section("12) Verify Deleted")
    r = s.get(f"{RES}/{rid}")
    print("Get after delete:", r.status_code, r.text[:120])
    assert r.status_code == 404

    print("\nAll tests passed")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
    print("\nTest failed:", e)
    except Exception as ex:
    print("\nUnexpected error:", ex)
