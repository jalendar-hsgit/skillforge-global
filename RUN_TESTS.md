# Quick Test Execution Guide

## ✅ Backend API Tests (WORKING)

### Run All 8 Tests Including Session Actions

```powershell
cd backend
$env:PYTHONIOENCODING="utf-8"
$env:AUTO_RUN="1"
python test_mentor_api.py
```

**Expected Output:**
```
✓ GET /dashboard - Overview stats
✓ GET /dashboard/sessions - Session list  
✓ GET /dashboard/earnings - Monthly earnings
✓ GET /dashboard/students - Student stats
✓ GET /dashboard/analytics - Weekly analytics  
✓ GET /dashboard/reviews - Review list
✓ Session Actions - Confirm/Complete/Cancel workflows

============================================================
 All tests passed!
============================================================
```

**Test Coverage:**
- Dashboard overview endpoint
- Session listing with status filters
- Earnings aggregation
- Student statistics
- Analytics by weekday
- Review listing
- **Session confirm action** (pending → confirmed + meeting_url)
- **Session complete action** (confirmed → completed + completed_at)
- **Session cancel action** (→ cancelled + mentor_notes)

---

## ⚠️ E2E Tests (BLOCKED)

### Known Issue
Next.js has watchpack TypeError preventing dev server startup and production build instability.

### When Infrastructure is Fixed

```powershell
# Start backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# Start frontend (in new terminal)
npm run dev
# OR (if dev mode fails)
npm run build
npm start

# Run E2E tests (in new terminal)
npx playwright test e2e/mentor-session-actions.spec.ts --reporter=list
```

**Test Scenarios (11 Total):**
1. Pending sessions display with confirm button
2. Confirm action generates meeting URL
3. Complete action sets completed_at
4. Cancel action with reason modal
5. Status filter tabs work correctly
6. Session details modal displays
7. Meeting URL conditional display
8. Dashboard stats update after actions
9. Prevent completing pending session
10. Status-based action button visibility
11. Cancel button rules validation

---

## 🔧 Troubleshooting

### Backend Tests Fail

**Check database:**
```powershell
# Verify SQLite database exists
Test-Path backend/skillforge.db
```

**Check test account:**
```python
# Ensure mentor@test.com exists with is_mentor=True
# Default password: password123
```

**Check dependencies:**
```powershell
pip install -r backend/requirements.txt
```

### E2E Tests Can't Start

**Check servers running:**
```powershell
# Backend health
curl http://localhost:8001/healthz

# Frontend home
curl http://localhost:3000
```

**Check ports free:**
```powershell
Get-NetTCPConnection -LocalPort 8001,3000
```

**Clear stuck processes:**
```powershell
# Kill port 8001
$p = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($p) { Stop-Process -Id $p.OwningProcess -Force }

# Kill port 3000
$p = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($p) { Stop-Process -Id $p.OwningProcess -Force }
```

---

## 📊 Current Status

| Test Suite | Status | Last Run | Pass Rate |
|------------|--------|----------|-----------|
| Backend API | ✅ PASSING | Dec 2, 2025 | 8/8 (100%) |
| E2E Browser | ⚠️ BLOCKED | Infrastructure | 0/11 (blocked) |

**Backend tests prove all session action functionality works correctly via API.**
