"""
End-to-End Test: Auth (signup/login/me) + Resume CRUD
Run with backend server on http://127.0.0.1:8001
"""
import requests
import random
import string
import json

BASE = "http://127.0.0.1:8001"
s = requests.Session()


def rand_email():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"qa_{suffix}@example.com"


def test_auth_and_resume():
    print("\n=== AUTH & RESUME E2E TEST ===")
    email = rand_email()
    password = "TestPass123!"

    # 1) Signup
    print("\n[1] Signup")
    resp = s.post(f"{BASE}/api/v1/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": "QA User"
    })
    if resp.status_code in (200, 201):
        print(f"  ✓ signup -> {resp.status_code} {resp.json()}")
    elif resp.status_code == 400:
        print("  • signup -> 400 already exists; will login")
    else:
        print(f"  ✗ signup -> {resp.status_code} {resp.text[:200]}")
        return

    # 2) Login
    print("\n[2] Login")
    resp = s.post(f"{BASE}/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"  ✗ login -> {resp.status_code} {resp.text[:200]}")
        return
    print(f"  ✓ login -> {resp.status_code}; cookies: {'token' in s.cookies}")

    # 3) Me
    print("\n[3] Me")
    resp = s.get(f"{BASE}/api/v1/auth/me")
    if resp.status_code != 200:
        print(f"  ✗ me -> {resp.status_code} {resp.text[:200]}")
        return
    me = resp.json()
    print(f"  ✓ me -> id={me.get('id')} email={me.get('email')}")

    # 4) Resume Create
    print("\n[4] Resume Create")
    resp = s.post(f"{BASE}/api/v1x/resumes/", json={
        "title": "QA Test Resume",
        "template_id": "modern"
    })
    if resp.status_code not in (200, 201):
        print(f"  ✗ create resume -> {resp.status_code} {resp.text[:200]}")
        return
    resume = resp.json()
    rid = resume["id"]
    print(f"  ✓ create resume -> id={rid}, title={resume['title']}")

    # 5) Resume List
    print("\n[5] Resume List")
    resp = s.get(f"{BASE}/api/v1x/resumes")
    if resp.status_code != 200:
        print(f"  ✗ list resumes -> {resp.status_code} {resp.text[:200]}")
        return
    lst = resp.json()
    print(f"  ✓ list resumes -> count={len(lst)}")

    # 6) Resume Get by ID
    print("\n[6] Resume Get by ID")
    resp = s.get(f"{BASE}/api/v1x/resumes/{rid}")
    if resp.status_code != 200:
        print(f"  ✗ get resume -> {resp.status_code} {resp.text[:200]}")
        return
    print(f"  ✓ get resume -> version={resp.json().get('version')}")

    # 7) Resume Update
    print("\n[7] Resume Update (PATCH)")
    resp = s.patch(f"{BASE}/api/v1x/resumes/{rid}", json={
        "title": "QA Test Resume (Updated)",
        "template_id": "two-column"
    })
    if resp.status_code != 200:
        print(f"  ✗ update resume -> {resp.status_code} {resp.text[:200]}")
        return
    updated = resp.json()
    print(f"  ✓ update resume -> title={updated['title']} template_id={updated['template_id']} version={updated['version']}")

    # 8) Resume Delete
    print("\n[8] Resume Delete")
    resp = s.delete(f"{BASE}/api/v1x/resumes/{rid}")
    if resp.status_code not in (200, 204):
        print(f"  ✗ delete resume -> {resp.status_code} {resp.text[:200]}")
        return
    print("  ✓ delete resume -> ok")

    # 9) Resume Templates sanity
    print("\n[9] Resume Templates (sanity)")
    resp = s.get(f"{BASE}/api/v1x/resume-templates")
    if resp.status_code == 200:
        data = resp.json()
        first = data[0]["name"] if data else "<none>"
        print(f"  ✓ resume-templates -> {len(data)} (first: {first})")
    else:
        print(f"  • resume-templates -> {resp.status_code} {resp.text[:160]}")

    print("\n=== DONE ===\n")


if __name__ == "__main__":
    test_auth_and_resume()
