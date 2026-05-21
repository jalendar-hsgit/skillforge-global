"""
Comprehensive endpoint sanity test for core SkillForge Global APIs.

Covers:
- Health check
- Auth: signup/login/me
- Resume CRUD: create/get/update/duplicate/list/delete
- Resume export: PDF/DOCX/TXT
- Work experience add/update/delete
- Error cases: get non-existent resume, export non-owned resume

Usage:
  python tests_e2e/test_all_endpoints_clean.py

Exit code non-zero if any critical step fails.
"""
import os
import time
import json
import random
import requests
from typing import Dict, Any

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8001")
AUTH = f"{API_BASE}/api/v1/auth"
V1X = f"{API_BASE}/api/v1x"
RESUMES = f"{V1X}/resumes"

session = requests.Session()
report: Dict[str, Any] = {}
failures = []

def section(name: str):
    print("\n" + "="*90)
    print(name)
    print("="*90)

def record(key: str, status: int, ok: bool, detail: str = "", extra: Dict[str, Any] | None = None):
    report[key] = {"status": status, "ok": ok, "detail": detail, **(extra or {})}
    if not ok:
        failures.append(key)
    print(f"[{ 'PASS' if ok else 'FAIL' }] {key}: {status} {detail}")

def random_email(prefix="ep_test"):
    return f"{prefix}_{int(time.time())}_{random.randint(1000,9999)}@example.com"

def safe_json(r: requests.Response):
    try:
        return r.json()
    except Exception:
        return {"raw": r.text[:300]}

section("1) Health Check")
r = session.get(f"{API_BASE}/healthz")
record("healthz", r.status_code, r.ok, detail=r.text[:100])

section("2) Auth: signup/login/me")
EMAIL = random_email()
PASSWORD = "P@ssw0rd!123"
# signup
r = session.post(f"{AUTH}/signup", json={"email": EMAIL, "password": PASSWORD, "full_name": "Endpoint Tester"})
record("auth_signup", r.status_code, r.status_code in (200,201), detail=r.text[:120])
# login
r = session.post(f"{AUTH}/login", json={"email": EMAIL, "password": PASSWORD})
record("auth_login", r.status_code, r.ok, detail=r.text[:120])
# me
r = session.get(f"{AUTH}/me")
me = safe_json(r)
record("auth_me", r.status_code, r.ok and me.get("email") == EMAIL, detail=json.dumps(me)[:120])
USER_ID = me.get("id")

section("3) Resume Create")
resume_payload = {
    "title": "Endpoint Test Resume",
    "template_id": "modern",
    "full_name": "Endpoint Tester",
    "email": EMAIL,
    "summary": "Automated test resume summary"
}
r = session.post(f"{RESUMES}/", json=resume_payload)
resume_data = safe_json(r)
record("resume_create", r.status_code, r.status_code in (200,201), detail=json.dumps(resume_data)[:150])
RID = resume_data.get("id")

section("4) Resume Get/List")
r_get = session.get(f"{RESUMES}/{RID}")
record("resume_get", r_get.status_code, r_get.ok, detail=r_get.text[:120])
r_list = session.get(f"{RESUMES}/")
list_data = safe_json(r_list)
record("resume_list", r_list.status_code, r_list.ok and any(x.get("id") == RID for x in list_data), detail=f"count={len(list_data) if isinstance(list_data,list) else 'n/a'}")

section("5) Resume Update")
update_payload = {"summary": "Updated automated summary"}
r_upd = session.patch(f"{RESUMES}/{RID}", json=update_payload)
upd_data = safe_json(r_upd)
record("resume_update", r_upd.status_code, r_upd.ok and upd_data.get("summary") == update_payload["summary"], detail=json.dumps(upd_data)[:120])

section("6) Work Experience Add/Update/Delete")
we_payload = {
    "company": "TestCorp",
    "position": "QA Engineer",
    "location": "Remote",
    "start_date": "Jan 2024",
    "end_date": "Present",
    "is_current": True,
    "description": "Testing endpoints.",
    "bullet_points": ["Implemented automated endpoint tests"]
}
r_we_add = session.post(f"{RESUMES}/{RID}/work-experience", json=we_payload)
we_add = safe_json(r_we_add)
record("work_exp_add", r_we_add.status_code, r_we_add.ok, detail=json.dumps(we_add)[:120])
WID = we_add.get("id")
# update
we_payload_upd = {**we_payload, "position": "Senior QA Engineer"}
r_we_upd = session.put(f"{RESUMES}/work-experience/{WID}", json=we_payload_upd)
we_upd = safe_json(r_we_upd)
record("work_exp_update", r_we_upd.status_code, r_we_upd.ok and we_upd.get("position") == "Senior QA Engineer", detail=json.dumps(we_upd)[:120])
# delete
r_we_del = session.delete(f"{RESUMES}/work-experience/{WID}")
record("work_exp_delete", r_we_del.status_code, r_we_del.status_code == 204, detail=r_we_del.text[:80])

section("7) Resume Duplicate")
r_dup = session.post(f"{RESUMES}/{RID}/duplicate")
dup_data = safe_json(r_dup)
record("resume_duplicate", r_dup.status_code, r_dup.ok and dup_data.get("id") != RID, detail=json.dumps(dup_data)[:120])
DUP_ID = dup_data.get("id")

section("8) Resume Export PDF/DOCX/TXT")
for fmt, key in [("pdf","export_pdf"),("docx","export_docx"),("txt","export_txt")]:
    r_exp = session.get(f"{RESUMES}/{RID}/export", params={"format": fmt})
    ok = r_exp.ok and len(r_exp.content) > 100
    record(key, r_exp.status_code, ok, detail=f"len={len(r_exp.content)} ct={r_exp.headers.get('content-type')}")

section("9) Error Cases")
# Non-existent resume
fake_id = RID + 999999
r_fake = session.get(f"{RESUMES}/{fake_id}")
record("resume_get_missing", r_fake.status_code, r_fake.status_code == 404, detail=r_fake.text[:100])
# Export non-owned resume (simulate by using another session without auth)
unauth = requests.Session()
r_unauth_exp = unauth.get(f"{RESUMES}/{RID}/export", params={"format": "pdf"})
record("export_unauth", r_unauth_exp.status_code, r_unauth_exp.status_code == 401, detail=r_unauth_exp.text[:120])

section("10) Cleanup")
r_del_main = session.delete(f"{RESUMES}/{RID}")
record("resume_delete", r_del_main.status_code, r_del_main.status_code == 204, detail=r_del_main.text[:60])
if DUP_ID:
    r_del_dup = session.delete(f"{RESUMES}/{DUP_ID}")
    record("resume_delete_duplicate", r_del_dup.status_code, r_del_dup.status_code == 204, detail=r_del_dup.text[:60])

section("11) Summary")
print(json.dumps(report, indent=2)[:5000])
print("\nTOTAL ENDPOINTS TESTED:", len(report))
print("FAILURES:", failures)

if failures:
    print(f"\nFAILED: {len(failures)} endpoints -> {failures}")
    raise SystemExit(1)
else:
    print("\nALL TESTS PASSED")
