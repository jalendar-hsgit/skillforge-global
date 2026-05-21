"""
Comprehensive endpoint test for core Resume features.
- Auth: login/signup, me
- Resume CRUD: create, get, list, update, duplicate, delete
- Collections: work experience, education, projects, skills, certificates, achievements (create/update/delete)
- Export: PDF, DOCX, TXT

Run: python test_all_endpoints.py
"""
import requests
import sys
from typing import Dict, Any

BASE = "http://127.0.0.1:8001"
API_V1 = f"{BASE}/api/v1"
API_V1X = f"{BASE}/api/v1x"

EMAIL = "test_endpoints_user@example.com"
PASSWORD = "P@ssw0rd!123"


def section(title: str):
    print("\n" + "="*80)
    print(title)
    print("="*80)


def expect(cond: bool, label: str, extra: str = ""):
    if cond:
        print(f"[PASS] {label}")
        return True
    else:
        print(f"[FAIL] {label}{(': ' + extra) if extra else ''}")
        return False


def main():
    s = requests.Session()
    results: Dict[str, bool] = {}

    # Health
    section("Health")
    r = s.get(f"{BASE}/healthz")
    results["healthz"] = expect(r.status_code == 200 and r.json().get("ok") is True, 
                                 "GET /healthz")

    # Auth: login or signup then login
    section("Auth")
    r = s.post(f"{API_V1}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    if r.status_code == 401:
        # signup then login
        r2 = s.post(f"{API_V1}/auth/signup", json={
            "email": EMAIL,
            "password": PASSWORD,
            "full_name": "Endpoint Test User"
        })
        results["auth_signup"] = expect(r2.status_code == 200, "POST /api/v1/auth/signup", r2.text[:200])
        r = s.post(f"{API_V1}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    results["auth_login"] = expect(r.status_code == 200, "POST /api/v1/auth/login", r.text[:200])

    r = s.get(f"{API_V1}/auth/me")
    results["auth_me"] = expect(r.status_code == 200 and "email" in r.text, "GET /api/v1/auth/me", r.text[:200])

    # Resume CRUD
    section("Resume CRUD")
    resume_payload = {
        "title": "Endpoint Test Resume",
        "template_id": "modern",
        "full_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "summary": "QA engineer with 3+ years experience."
    }
    r = s.post(f"{API_V1X}/resumes/", json=resume_payload)
    results["resume_create"] = expect(r.status_code in (200, 201), "POST /api/v1x/resumes/", r.text[:200])
    if not results["resume_create"]:
        print("Aborting due to resume create failure.")
        print_summary(results)
        sys.exit(1)
    resume = r.json()
    rid = resume["id"]
    print(f"Created resume ID={rid}")

    r = s.get(f"{API_V1X}/resumes/{rid}")
    results["resume_get"] = expect(r.status_code == 200, f"GET /api/v1x/resumes/{rid}", r.text[:200])

    r = s.get(f"{API_V1X}/resumes")
    results["resume_list"] = expect(r.status_code == 200 and any(x.get("id") == rid for x in r.json()),
                                     "GET /api/v1x/resumes")

    r = s.patch(f"{API_V1X}/resumes/{rid}", json={"title": "Endpoint Test Resume (Updated)"})
    results["resume_update"] = expect(r.status_code == 200 and r.json().get("title", "").endswith("Updated)"),
                                  f"PATCH /api/v1x/resumes/{rid}")

    # Collections: Work Experience
    section("Collections: Work Experience")
    exp_payload = {
        "company": "Acme Corp",
        "position": "QA Engineer",
        "location": "Remote",
        "start_date": "Jan 2023",
        "end_date": "Present",
        "is_current": True,
        "description": "Testing end-to-end flows",
        "bullet_points": ["Built test harness", "Increased coverage to 85%"]
    }
    r = s.post(f"{API_V1X}/resumes/{rid}/work-experience", json=exp_payload)
    results["workexp_create"] = expect(r.status_code == 200, f"POST /api/v1x/resumes/{rid}/work-experience", r.text[:200])
    exp = r.json()
    exp_id = exp["id"]
    r = s.put(f"{API_V1X}/resumes/work-experience/{exp_id}", json={**exp_payload, "position": "Senior QA Engineer"})
    results["workexp_update"] = expect(r.status_code == 200 and r.json().get("position") == "Senior QA Engineer",
                                        f"PUT /api/v1x/resumes/work-experience/{exp_id}")

    # Collections: Education
    section("Collections: Education")
    edu_payload = {
        "institution": "State University",
        "degree": "B.Sc.",
        "field_of_study": "Computer Science",
        "location": "CA",
        "start_date": "2016",
        "end_date": "2020",
        "gpa": "3.8",
        "achievements": ["Dean's list"]
    }
    r = s.post(f"{API_V1X}/resumes/{rid}/education", json=edu_payload)
    results["edu_create"] = expect(r.status_code == 200, f"POST /api/v1x/resumes/{rid}/education", r.text[:200])
    edu_id = r.json()["id"]
    r = s.put(f"{API_V1X}/resumes/education/{edu_id}", json={**edu_payload, "gpa": "3.9"})
    results["edu_update"] = expect(r.status_code == 200 and r.json().get("gpa") == "3.9",
                                    f"PUT /api/v1x/resumes/education/{edu_id}")

    # Collections: Projects
    section("Collections: Projects")
    proj_payload = {
        "title": "QA Dashboard",
        "description": "A dashboard to monitor test runs",
        "tech_stack": ["React", "FastAPI"]
    }
    r = s.post(f"{API_V1X}/resumes/{rid}/projects", json=proj_payload)
    results["project_create"] = expect(r.status_code == 200, f"POST /api/v1x/resumes/{rid}/projects", r.text[:200])
    proj_id = r.json()["id"]
    r = s.put(f"{API_V1X}/resumes/projects/{proj_id}", json={**proj_payload, "title": "QA E2E Dashboard"})
    results["project_update"] = expect(r.status_code == 200 and r.json().get("title") == "QA E2E Dashboard",
                                        f"PUT /api/v1x/resumes/projects/{proj_id}")

    # Collections: Skills
    section("Collections: Skills")
    skill_payload = {"name": "Python", "category": "Programming", "proficiency": "Advanced", "years_of_experience": 3}
    r = s.post(f"{API_V1X}/resumes/{rid}/skills", json=skill_payload)
    results["skill_create"] = expect(r.status_code == 200, f"POST /api/v1x/resumes/{rid}/skills", r.text[:200])
    skill_id = r.json()["id"]
    r = s.put(f"{API_V1X}/resumes/skills/{skill_id}", json={**skill_payload, "proficiency": "Expert"})
    results["skill_update"] = expect(r.status_code == 200 and r.json().get("proficiency") == "Expert",
                                      f"PUT /api/v1x/resumes/skills/{skill_id}")

    # Collections: Certificates
    section("Collections: Certificates")
    cert_payload = {"name": "AWS CCP", "issuing_organization": "Amazon"}
    r = s.post(f"{API_V1X}/resumes/{rid}/certificates", json=cert_payload)
    results["cert_create"] = expect(r.status_code == 200, f"POST /api/v1x/resumes/{rid}/certificates", r.text[:200])
    cert_id = r.json()["id"]
    r = s.put(f"{API_V1X}/resumes/certificates/{cert_id}", json={**cert_payload, "credential_id": "ABC-123"})
    results["cert_update"] = expect(r.status_code == 200 and r.json().get("credential_id") == "ABC-123",
                                     f"PUT /api/v1x/resumes/certificates/{cert_id}")

    # Collections: Achievements
    section("Collections: Achievements")
    ach_payload = {"title": "Employee of the Month", "description": "for outstanding QA"}
    r = s.post(f"{API_V1X}/resumes/{rid}/achievements", json=ach_payload)
    results["ach_create"] = expect(r.status_code == 200, f"POST /api/v1x/resumes/{rid}/achievements", r.text[:200])
    ach_id = r.json()["id"]
    r = s.put(f"{API_V1X}/resumes/achievements/{ach_id}", json={**ach_payload, "issuer": "QA Team"})
    results["ach_update"] = expect(r.status_code == 200 and r.json().get("issuer") == "QA Team",
                                    f"PUT /api/v1x/resumes/achievements/{ach_id}")

    # Export
    section("Export")
    r = s.get(f"{API_V1X}/resumes/{rid}/export?format=pdf")
    results["export_pdf"] = expect(r.status_code == 200 and "application/pdf" in r.headers.get("content-type", "") and len(r.content) > 100,
                                    f"GET /api/v1x/resumes/{rid}/export?format=pdf")
    r = s.get(f"{API_V1X}/resumes/{rid}/export?format=docx")
    results["export_docx"] = expect(r.status_code == 200 and "application/vnd.openxmlformats" in r.headers.get("content-type", "") and len(r.content) > 100,
                                     f"GET /api/v1x/resumes/{rid}/export?format=docx")
    r = s.get(f"{API_V1X}/resumes/{rid}/export?format=txt")
    results["export_txt"] = expect(r.status_code == 200 and "text/plain" in r.headers.get("content-type", "") and len(r.content) > 20,
                                    f"GET /api/v1x/resumes/{rid}/export?format=txt")

    # Duplicate and cleanup
    section("Duplicate & Cleanup")
    r = s.post(f"{API_V1X}/resumes/{rid}/duplicate")
    results["resume_duplicate"] = expect(r.status_code == 200 and r.json().get("id") != rid,
                                          f"POST /api/v1x/resumes/{rid}/duplicate")
    dup_id = r.json().get("id") if r.status_code == 200 else None

    # Delete collections
    r = s.delete(f"{API_V1X}/resumes/achievements/{ach_id}")
    results["ach_delete"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/achievements/{ach_id}")
    r = s.delete(f"{API_V1X}/resumes/certificates/{cert_id}")
    results["cert_delete"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/certificates/{cert_id}")
    r = s.delete(f"{API_V1X}/resumes/skills/{skill_id}")
    results["skill_delete"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/skills/{skill_id}")
    r = s.delete(f"{API_V1X}/resumes/projects/{proj_id}")
    results["project_delete"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/projects/{proj_id}")
    r = s.delete(f"{API_V1X}/resumes/education/{edu_id}")
    results["edu_delete"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/education/{edu_id}")
    r = s.delete(f"{API_V1X}/resumes/work-experience/{exp_id}")
    results["workexp_delete"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/work-experience/{exp_id}")

    # Delete duplicate, then original
    if dup_id:
        r = s.delete(f"{API_V1X}/resumes/{dup_id}")
        results["resume_delete_dup"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/{dup_id}")
    r = s.delete(f"{API_V1X}/resumes/{rid}")
    results["resume_delete"] = expect(r.status_code == 204, f"DELETE /api/v1x/resumes/{rid}")

    print_summary(results)
    # Exit non-zero if any failures
    if not all(results.values()):
        sys.exit(1)


def print_summary(results: Dict[str, bool]):
    section("SUMMARY")
    passes = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed {passes}/{total} checks")
    for k, v in results.items():
        print(f" - {k}: {'PASS' if v else 'FAIL'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
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
  python test_all_endpoints.py

Exit code non-zero if any critical step fails.
"""
import os
import time
import json
import random
import string
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
    print(f"[{'PASS' if ok else 'FAIL'}] {key}: {status} {detail}")

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
