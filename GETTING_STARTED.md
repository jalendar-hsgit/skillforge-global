# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9+ installed
- Node.js 18+ installed
- PowerShell (Windows)

## 🔧 Backend Setup

### 1. Install Backend Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### 2. Start Backend Server
```powershell
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Or from repository root
cd backend ; uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
Scheduler lifecycle hooks registered
APScheduler started: follow-ups(30m), interviews(15m)
```

### 3. Verify Backend
Open a new terminal and test:
```powershell
curl http://localhost:8001/healthz
```

Should return: `{"ok":true}`

## 🎨 Frontend Setup

### 1. Install Frontend Dependencies
```powershell
# From repository root
npm install
```

### 2. Start Frontend Dev Server
```powershell
npm run dev
```

**Expected Output:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

The dev server will automatically use port 3001 if 3000 is taken.

### 3. Open Application
Visit: http://localhost:3000 (or http://localhost:3001)

## 🔐 First Time Login

### Create an Account
1. Navigate to http://localhost:3000/signup
2. Enter email and password
3. Click "Sign up for free"

### Login
1. Navigate to http://localhost:3000/login
2. Enter your credentials
3. Click "Log In"

## 🛠️ Common Issues

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```powershell
cd backend
pip install -r requirements.txt
```

**Error:** `Import "apscheduler.schedulers.asyncio" could not be resolved`

**Solution:**
```powershell
pip install APScheduler==3.10.4
```

### Login Not Working

**Check:**
1. Backend is running on port 8001
   ```powershell
   curl http://localhost:8001/healthz
   ```

2. Database exists
   ```powershell
   # Should see database file
   ls backend/app/data/skillforge.db
   ```

3. Check backend logs for errors

**If database is missing:**
Backend will create it automatically on first startup.

### Frontend Errors

**Error:** `useToast must be used within a ToastProvider`

**Solution:** Already fixed! Update your code:
```powershell
git pull origin v1.0.0-release
npm install
```

**Error:** `Module not found: Can't resolve '@/components/Toast'`

**Solution:**
```powershell
npm install
```

## 📧 Email Configuration (Optional)

For email reminders to work, add to `backend/.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

**Note:** For Gmail, create an [App Password](https://support.google.com/accounts/answer/185833).

Without email config, the app works fine but reminders won't be sent.

## 🧪 Testing

### E2E Tests
```powershell
# Install Playwright
npx playwright install

# Run tests
npx playwright test

# Run specific test
npx playwright test e2e/job-tracker-drag.spec.ts
```

### Manual Testing
1. **Job Tracker:**
   - Go to http://localhost:3000/job-tracker
   - Click "Add Application"
   - Fill form and submit
   - Switch to Kanban view
   - Drag cards between columns

2. **Toasts:**
   - Drag a card in Kanban
   - See success toast appear
   - Should auto-dismiss after 3.5 seconds

3. **Background Scheduler:**
   - Check backend console logs
   - Should see scheduler messages every 15-30 minutes
   - Test manually:
     ```powershell
     curl -X POST http://localhost:8001/api/v1x/job-applications-notifications/send-follow-up-reminders `
       -H "Cookie: token=YOUR_TOKEN"
     ```

## 🚀 Production Deployment

### Backend
```powershell
# Set production environment variables
$env:DATABASE_URL="postgresql://user:pass@host/db"
$env:JWT_SECRET="strong-random-secret"
$env:FRONTEND_ORIGIN="https://yourdomain.com"

# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Frontend
```powershell
npm run build
npm start
```

## 📚 Documentation

- **TRACKER_ENHANCEMENTS.md** - Technical documentation
- **QUICKSTART_SCHEDULER.md** - Scheduler setup guide
- **JOB_TRACKER_STATUS.md** - Feature status
- **.github/copilot-instructions.md** - Architecture overview

## 🆘 Need Help?

1. Check backend logs for errors
2. Check frontend console (F12 in browser)
3. Verify both servers are running:
   - Backend: http://localhost:8001/healthz
   - Frontend: http://localhost:3000

4. Common commands:
   ```powershell
   # Kill process on port 8001 (if stuck)
   netstat -ano | findstr :8001
   taskkill /PID <PID> /F

   # Kill process on port 3000
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F

   # Clear npm cache
   npm cache clean --force
   rm -r node_modules
   npm install

   # Reset backend database
   rm backend/app/data/skillforge.db
   # Restart backend to recreate
   ```

---
**Ready to start!** 🎉

Run these two commands in separate terminals:
```powershell
# Terminal 1: Backend
cd backend ; uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
npm run dev
```

Then open http://localhost:3000 in your browser!
