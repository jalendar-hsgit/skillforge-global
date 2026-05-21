# Signup 500 Error - Root Cause & Fix

## Problem
"Unexpected token 'I', 'Internal S'... is not valid JSON" during signup

## Root Cause
**SQLAlchemy registry conflict**: Two classes named `JobApplication` in the same Base registry:
1. `app.modelsx.hiring.JobApplication` (hiring module, table: `job_applications`)
2. `app.modelsx.job_application.JobApplication` (job tracker, table: `job_application_tracker`)

Even though table names differ, SQLAlchemy registers classes by CLASS NAME, not table name.

## Attempted Fixes That Didn't Work
1. ✗ Removing circular relationships from User model (helped but not enough)
2. ✗ Aliasing imports in main.py (`JobApplication as HiringJobApplication`)  
3. ✗ Commenting out hiring model import in main.py (but router still imported it)
4. ✗ Installing APScheduler in venv (needed but didn't fix signup)

## SOLUTION
Temporarily disable the hiring router in `backend/app/main.py` since it's not being used yet:

**Line ~112 in main.py, change from:**
```python
try:
    from app.api.v1x.hiring import router as hiring
except Exception as e:
    print(f"Failed to import hiring: {e}")
```

**To:**
```python
# TEMP: Disabled to avoid JobApplication class name conflict with job tracker
# The hiring module has JobApplication class which conflicts with job_application tracker
# hiring = None  # Uncomment when hiring module JobApplication is renamed to HiringJobApplication
```

Then remove `hiring` from the mount list around line 191.

## Permanent Fix (TODO)
Rename the hiring `JobApplication` class to `HiringJobApplication` throughout:
- `backend/app/modelsx/hiring.py`
- `backend/app/api/v1x/hiring.py`  
- Any other files referencing the hiring JobApplication

## Files Modified
1. `backend/app/models/user.py` - Removed Mentor/Subscription relationships
2. `backend/app/modelsx/mentor.py` - Removed back_populates to user
3. `backend/app/modelsx/subscription.py` - Removed back_populates to user
4. `backend/app/api/v1/auth.py` - Added full_name optional field to SignupRequest
5. `backend/app/main.py` - Need to disable hiring router import
6. `backend/venv` - Installed APScheduler==3.10.4

## Verification
After fixing, run:
```powershell
cd backend
.\venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from app.main import app; c = TestClient(app); r = c.post('/api/v1/auth/signup', json={'email': 'test@test.com', 'password': 'Test123!!'}); print(f'Status: {r.status_code}, Body: {r.text}')"
```

Expected: `Status: 200, Body: {"created":true}`
