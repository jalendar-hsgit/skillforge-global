# Booking "Failed to Fetch" - Troubleshooting Guide

## Error: "Failed to fetch" when booking a session

This error typically means the frontend cannot reach the backend API. 

### Quick Diagnosis

#### Step 1: Verify Backend is Running
```powershell
# Check if backend is running on port 8001
Test-NetConnection -ComputerName localhost -Port 8001
```

Expected: `TcpTestSucceeded: True`

#### Step 2: Check Backend Health Endpoint
```powershell
Invoke-WebRequest -Uri "http://localhost:8001/healthz"
```

Expected response:
```json
{"ok": true}
```

#### Step 3: Check API_BASE URL
Open browser console (F12) and run:
```javascript
console.log(process.env.NEXT_PUBLIC_API_BASE)
```

Should output: `http://localhost:8001` (or your configured API base)

---

## Common Causes & Solutions

### 1. Backend Not Running ⚠️
**Symptom**: Can't reach health endpoint, "Failed to fetch"

**Solution**: Start the backend
```bash
# From backend directory or project root
cd backend
pip install -r requirements.txt  # First time only
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

### 2. CORS Issue ⚠️
**Symptom**: Network tab shows CORS error, or "Failed to fetch"

**Check**: Browser DevTools → Network tab → XHR/fetch requests
- Look for requests to `/api/v1x/mentors/sessions`
- Check Response headers for `Access-Control-Allow-Origin`

**Solution**: The backend has CORS configured to allow localhost:3000
- If using different domain, update backend:
  ```python
  # backend/app/main.py - Line ~485
  CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000", ...]
  ```

---

### 3. Wrong API Base URL ⚠️
**Symptom**: Console shows "Cannot reach booking server at [wrong-url]"

**Solution**: Check environment variables
- Frontend reads `NEXT_PUBLIC_API_BASE` from `.env.local`
- Verify file exists: `/.env.local`
- Content should be:
  ```
  NEXT_PUBLIC_API_BASE=http://localhost:8001
  ```

**If changed .env.local**: Restart frontend dev server
```bash
npm run dev  # Will pick up new env vars
```

---

### 4. User Not Authenticated ⚠️
**Symptom**: Request fails with 401 error, redirects to login

**Solution**: Ensure user is logged in
- Check localStorage has `auth_token`
- Browser DevTools → Application → Cookies → Check for `token` cookie
- Login again if token expired

---

### 5. Mentor Not Found ⚠️
**Symptom**: Request fails with 404 error for mentor

**Solution**: Ensure mentor exists
- Check if mentor ID in URL is valid
- Visit `/mentors` page to see available mentors
- Verify mentor is approved status in database

```bash
# Check mentors in database
python3 -c "
from app.core.db import SessionLocal
from app.modelsx.mentor import Mentor
db = SessionLocal()
mentors = db.query(Mentor).all()
for m in mentors:
    print(f'ID: {m.id}, User: {m.user_id}, Status: {m.status}')
"
```

---

## Detailed Error Messages

### "Network error: Cannot reach booking server at http://localhost:8001"
- Backend is NOT running
- Port 8001 not accessible
- Firewall blocking connection
- **Fix**: Start backend on correct port

### "Failed to book session" or "Server error (500)"
- Backend error in booking logic
- Check backend console/logs for detailed error
- Might be database issue, missing dependencies, etc.
- **Fix**: Check backend logs, verify database setup

### "Failed to book session: session not found" (400)
- Mentor doesn't exist or is not approved
- **Fix**: Verify mentor exists and is approved

### "Could not create session: conflicting time" (400)
- Selected time slot is already booked
- Student already has session at that time
- **Fix**: Select different time slot

---

## Debugging Steps

### 1. Check Browser Console
- Open DevTools (F12)
- Go to Console tab
- Look for detailed error messages
- Copy the full error message

### 2. Check Network Tab
- DevTools → Network tab
- Filter: `Fetch/XHR`
- Click the failed request
- Check Status (200=success, 400=bad request, 500=server error, etc.)
- Check Response body for error details

### 3. Check Backend Logs
- Terminal running `uvicorn app.main:app --reload ...`
- Look for error messages when request is made
- Should see request log like:
  ```
  INFO:     GET http://localhost:8001/api/v1x/mentors/{id} HTTP/1.1" 200
  INFO:     POST http://localhost:8001/api/v1x/mentors/sessions HTTP/1.1" 201
  ```

### 4. Enable Debug Mode
- Add to booking page component:
  ```typescript
  console.log('API_BASE:', API_BASE);
  console.log('Mentor ID:', id);
  console.log('Booking payload:', { mentor_id: id, scheduled_at, ... });
  ```

---

## Testing Endpoints Directly

### Test Mentor Fetch
```bash
# Using curl (Windows PowerShell)
$headers = @{
    'Accept' = 'application/json'
    'Cookie' = 'token=YOUR_TOKEN_HERE'  # From browser
}
Invoke-WebRequest -Uri "http://localhost:8001/api/v1x/mentors/1" -Headers $headers
```

### Test Booking Endpoint
```bash
$body = @{
    mentor_id = 1
    scheduled_at = "2024-01-15T14:00:00Z"
    duration_minutes = 60
    topic = "Test Session"
} | ConvertTo-Json

$headers = @{
    'Content-Type' = 'application/json'
    'Cookie' = 'token=YOUR_TOKEN_HERE'
}

Invoke-WebRequest -Uri "http://localhost:8001/api/v1x/mentors/sessions" `
  -Method POST `
  -Headers $headers `
  -Body $body
```

---

## Checklist

- [ ] Backend running: `uvicorn app.main:app --reload --port 8001`
- [ ] Backend responds to `/healthz` endpoint
- [ ] Frontend env var: `NEXT_PUBLIC_API_BASE=http://localhost:8001`
- [ ] User is logged in (has `token` cookie)
- [ ] Mentor exists and is approved
- [ ] No CORS errors in browser console
- [ ] Selected time is in future
- [ ] Topic is 5+ characters
- [ ] Selected slot is available (not booked)

---

## If Still Not Working

1. **Provide these details**:
   - Exact error message from browser console
   - Status code from Network tab
   - Backend logs output
   - Mentor ID you're trying to book with

2. **Try hard reset**:
   ```bash
   # Stop frontend and backend
   # Clear browser cache: Ctrl+Shift+Delete
   # Restart backend: uvicorn app.main:app --reload --port 8001
   # Restart frontend: npm run dev
   ```

3. **Check database**:
   ```bash
   python3 backend/check_db.py
   ```

---

## Files Affected by Recent Fix

- `src/pages/mentors/[id]/book.tsx` - Enhanced error handling, better error messages
- Backend API unchanged - should work as-is
- Environment variables: Check `.env.local`

---

## Related Files

- Backend API: `backend/app/api/v1x/mentors.py`
- Models: `backend/app/modelsx/mentor.py`
- Frontend config: `src/lib/apiBase.ts`
- Docker/production: See `.env.example` for API_BASE configuration
