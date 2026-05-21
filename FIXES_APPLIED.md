# Quick Start - PowerShell

## Start Backend
```powershell
.\start-backend.bat
```

## Start Frontend (in a new terminal)
```powershell
.\start-frontend.bat
```

## Or start both manually:

### Backend
```powershell
cd backend
pip install -r requirements.txt
pip install python-dateutil APScheduler==3.10.4
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend
```powershell
npm install
npm run dev
```

## Fixes Applied

✅ **Fixed:** `useToast must be used within a ToastProvider`
- Made toast hook SSR-safe with no-op fallback

✅ **Fixed:** Table name conflict between hiring and job tracker models
- Renamed job tracker table to `job_application_tracker`

✅ **Fixed:** Foreign key reference error
- Corrected `users.id` to `user.id` (matching existing User table)

✅ **Fixed:** Missing dependencies
- Added `python-dateutil` and `APScheduler` to installation

## Test Login

1. Start both servers using the batch files above
2. Navigate to http://localhost:3000/signup
3. Create an account with email/password
4. Go to http://localhost:3000/login
5. Log in with your credentials

## Verify Everything Works

- Backend health: http://localhost:8001/healthz should return `{"ok":true}`
- Frontend: http://localhost:3000 should show the homepage
- Job Tracker: http://localhost:3000/job-tracker should load

## Backend Console Should Show

```
INFO:     Uvicorn running on http://0.0.0.0:8001
Mounted v1x router: ['job-applications']
Mounted v1x router: ['job-notifications']
Mounted v1x router: ['job-calendar']
WebSocket server mounted at /ws
Scheduler lifecycle hooks registered
APScheduler started: follow-ups(30m), interviews(15m)
INFO:     Application startup complete.
```

## If Login Still Fails

1. Check backend console for errors
2. Verify database exists: `ls backend/app/data/skillforge.db`
3. Check browser console (F12) for frontend errors
4. Verify cookies are being set (check Network tab in DevTools)

---
**All fixes committed!** The application should now run without errors.
