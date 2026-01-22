# 🔴 ACTION REQUIRED: Stop Backend & Reset Database

## Current Problem
The database file is locked by the backend process and cannot be deleted/reset.

## Solution: Stop Backend First

### Step 1: Stop the Backend
**In the terminal where backend is running, press:**
```
Ctrl + C
```

**Wait for it to show:**
```
Shutdown complete.
```

### Step 2: Delete the Database
**In PowerShell, run:**
```powershell
cd "d:\python code\sfg\skillforge-global"
Remove-Item -Path "backend/app/data/skillforge.db" -Force
```

### Step 3: Reinitialize Database
```powershell
cd backend
python init_db.py
```

**You should see:**
```
[Init] ✅ Database initialization complete!
```

### Step 4: Restart Backend
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Wait for:**
```
Uvicorn running on http://0.0.0.0:8001
```

---

## Why This Is Needed

- The old database file still has the old schema
- SQLAlchemy is selecting all columns from the User model (including the new Phase 2.5 columns)
- But the actual database file doesn't have those columns
- This causes "no such column: email_notifications" error

---

## After Reset

The tests will work because:
1. ✓ Database will have Phase 2.5 columns
2. ✓ User model will match database schema
3. ✓ Auth will work
4. ✓ Progress and Badge endpoints will work

---

**Ready to proceed?**

1. Stop the backend (Ctrl+C)
2. Run the PowerShell commands above
3. Let me know when backend is running again

