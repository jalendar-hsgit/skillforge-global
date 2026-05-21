# 🔴 LOGIN NOT WORKING - QUICK FIX GUIDE

**Problem:** Backend crashes on startup because logger wasn't imported  
**Status:** ✅ FIXED - Ready to test  
**Time to Fix:** 5 minutes

---

# 🚀 QUICK FIX (Copy & Paste)

## Option 1: Auto-Test (Easiest)

```bash
# From repo root
python test_login.py
```

This will:
1. Check if backend is running
2. Start backend if needed
3. Wait 5 seconds
4. Test login endpoint
5. Show you the result

---

## Option 2: Manual Test

### Step 1: Start Backend

**Windows PowerShell:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Mac/Linux:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected output:**
```
[Init] ✅ SQLite database ready with WAL + foreign keys enabled
[Init] ✅ Database ready with XX tables
Uvicorn running on http://0.0.0.0:8001
```

If you see these lines → ✅ Backend is working

### Step 2: Test Login (New Terminal)

```bash
curl -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@skillforge.com","password":"superadmin"}'
```

**Expected response (HTTP 200):**
```json
{
  "logged": true,
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user_id": 1
}
```

If you see this → ✅ LOGIN IS WORKING

---

# 🔍 TROUBLESHOOTING

## Problem 1: Backend Crashes with "logger is not defined"

**Cause:** The main.py file didn't get the logger import  
**Fix:**

1. Open `backend/app/main.py`
2. Look at line 1-15
3. Should contain:
   ```python
   import logging
   ...
   logger = logging.getLogger(__name__)
   ```
4. If missing, add these 2 lines manually
5. Save file
6. Restart backend

---

## Problem 2: "database is locked" error

**Cause:** SQLite database is still locked from previous crash  
**Fix:**

```bash
# Stop backend (Ctrl+C in terminal)

# Delete database files
rm backend/app/data/skillforge.db
rm backend/app/data/skillforge.db-*

# Restart backend
cd backend && python -m uvicorn app.main:app --reload

# Backend will recreate database on startup
```

---

## Problem 3: "Connection refused" when testing

**Cause:** Backend isn't running  
**Fix:**

```bash
# In terminal, go to backend folder
cd backend

# Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Wait for message: "Uvicorn running on http://0.0.0.0:8001"
```

---

## Problem 4: Login returns 401 "Invalid login"

**Cause:** Wrong email/password or user doesn't exist  
**Fix:**

Check you're using:
- Email: `superadmin@skillforge.com`
- Password: `superadmin`

Or check database has demo users:
```bash
sqlite3 backend/app/data/skillforge.db "SELECT email FROM user LIMIT 5;"
```

Should show:
```
superadmin@skillforge.com
admin@skillforge.com
john.doe@example.com
...
```

If empty, seed demo data:
```bash
cd backend
python seed_all_demo_data.py
```

---

# ✅ SUCCESS CHECKLIST

After running the fix:

```
□ Backend starts without errors
□ See "[Init] ✅ Database ready" message
□ Login endpoint responds with HTTP 200
□ Response includes "access_token"
□ Response includes "user_id"
□ Multiple concurrent logins work
```

All checked? → **LOGIN IS WORKING** ✅

---

# 📋 WHAT WAS THE PROBLEM?

```
Previous code:
  logger.info("[Init] ✅ Database ready")
  ↑
  logger is not defined!
  ↑
  Backend crashes on startup

Fixed code:
  import logging  ← ADDED
  logger = logging.getLogger(__name__)  ← ADDED
  logger.info("[Init] ✅ Database ready")
  ↑
  Now it works!
```

---

# 🎯 NEXT STEPS

1. ✅ Run `python test_login.py` OR manually test login
2. ✅ Verify you get HTTP 200 with token
3. ✅ Then test frontend login at http://localhost:3000/login
4. ✅ If working, proceed to Phase 1 implementation

---

**Status:** ✅ FIX APPLIED  
**Action:** Run test_login.py now  
**Expected:** Login working in 5 minutes

