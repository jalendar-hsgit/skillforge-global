# Session Booking Error Flow Diagram

## Error Diagnosis Tree

```
User sees: "Failed to fetch" error on booking page
│
├─ STEP 1: Check if Backend is Running
│  │
│  ├─ Backend NOT running ❌
│  │  └─ Error shown: "Network error: Cannot reach booking server at 
│  │     http://localhost:8001. Make sure the backend is running."
│  │  └─ ACTION: Start backend
│  │     cd backend
│  │     uvicorn app.main:app --reload --port 8001
│  │
│  └─ Backend IS running ✅
│     └─ Continue to STEP 2
│
├─ STEP 2: Check Browser Console (F12)
│  │
│  ├─ Console shows network error
│  │  └─ Backend is not responding at configured API_BASE
│  │  └─ ACTION: Check API_BASE in env variables
│  │     echo $NEXT_PUBLIC_API_BASE
│  │     Should be: http://localhost:8001
│  │
│  ├─ Console shows 400 status
│  │  └─ Bad request - validation error
│  │  └─ ACTION: Check form data
│  │     - Topic must be 5+ characters
│  │     - Duration must be 30-180 minutes
│  │     - scheduled_at must be valid datetime
│  │
│  ├─ Console shows 401 status
│  │  └─ Unauthorized - user not authenticated
│  │  └─ ACTION: Login again
│  │     Visit /login and authenticate
│  │
│  ├─ Console shows 404 status
│  │  └─ Mentor not found
│  │  └─ ACTION: Verify mentor exists
│  │     Check /mentors page, verify mentor ID
│  │
│  └─ Console shows 500 status
│     └─ Server error - backend issue
│     └─ ACTION: Check backend logs
│        Look at terminal running uvicorn
│
├─ STEP 3: Check Network Tab (F12 → Network)
│  │
│  ├─ Request to /api/v1x/mentors/sessions
│  │  ├─ Status 201 ✅ SUCCESS
│  │  │  └─ Session created, redirecting to dashboard
│  │  │
│  │  ├─ Status 400 ❌ BAD REQUEST
│  │  │  └─ Response body shows validation error
│  │  │  └─ ACTION: Check request body in Network tab
│  │  │
│  │  ├─ Status 401 ❌ UNAUTHORIZED  
│  │  │  └─ Auth token missing or expired
│  │  │  └─ ACTION: Re-authenticate
│  │  │
│  │  ├─ Status 500 ❌ SERVER ERROR
│  │  │  └─ Backend error
│  │  │  └─ ACTION: Check backend console logs
│  │  │
│  │  └─ Status "pending" or timeout ❌ NETWORK ERROR
│  │     └─ Backend not responding
│  │     └─ ACTION: Check backend is running
│  │
│  └─ No request made
│     └─ Frontend prevented the request (validation)
│     └─ ACTION: Check form validation
│        - Selected slot exists?
│        - Topic entered and 5+ chars?
│        - Duration selected?
│
└─ STEP 4: Database Check
   │
   ├─ Mentors exist?
   │  python -c "
   │  from app.core.db import SessionLocal
   │  from app.modelsx.mentor import Mentor
   │  db = SessionLocal()
   │  print(len(db.query(Mentor).all()))
   │  "
   │
   ├─ Availability slots exist?
   │  python -c "
   │  from app.core.db import SessionLocal
   │  from app.modelsx.mentor import MentorAvailability
   │  db = SessionLocal()
   │  print(len(db.query(MentorAvailability).all()))
   │  "
   │
   └─ Sessions creating correctly?
      Check mentors/sessions table for recent records
```

---

## Console Output Interpreter

### ✅ Happy Path Console Output
```
Fetching mentor and availability from: http://localhost:8001
Mentor loaded: {id: 1, bio: "...", hourly_rate: 80}
Raw availability slots: [{id: 1, day_of_week: 0, start_time: "09:00", ...}]
Expanded slots: [{..., expanded_date: "2026-01-06T09:00:00Z"}]
Booking session: {mentor_id: 1, scheduled_at: "2026-01-06T09:00:00Z", ...}
✅ SUCCESS - Redirecting to dashboard
```

### ⚠️ Backend Not Running
```
Fetching mentor and availability from: http://localhost:8001
Network error: Cannot reach booking server at http://localhost:8001. 
Make sure the backend is running.
```

### ⚠️ Validation Error
```
Booking session: {mentor_id: 1, ...}
Booking error: Topic must be at least 5 characters
```

### ⚠️ Auth Expired
```
Redirecting to login...
// Page redirects to /login?redirect=/mentors/1/book
```

### ⚠️ Mentor Not Found
```
Booking session: {mentor_id: 999, ...}
Booking error: Could not find mentor with id: 999
```

---

## API Request/Response Examples

### Request: Book Session
```http
POST /api/v1x/mentors/sessions HTTP/1.1
Host: localhost:8001
Content-Type: application/json
Cookie: token=eyJ0eXAiOiJKV1QiLCJhbGc...
Accept: application/json

{
  "mentor_id": 1,
  "scheduled_at": "2026-01-06T09:00:00.000Z",
  "duration_minutes": 60,
  "topic": "Learn FastAPI authentication",
  "description": "Focus on JWT and OAuth2"
}
```

### Response: Success (201)
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 42,
  "mentor_id": 1,
  "student_id": 5,
  "topic": "Learn FastAPI authentication",
  "description": "Focus on JWT and OAuth2",
  "scheduled_at": "2026-01-06T09:00:00",
  "duration_minutes": 60,
  "status": "pending",
  "price": 80.00,
  "created_at": "2026-01-01T10:30:45",
  "meeting_url": null
}
```

### Response: Validation Error (400)
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "detail": "Topic must be at least 5 characters"
}
```

### Response: Unauthorized (401)
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Not authenticated"
}
```

### Response: Server Error (500)
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "detail": "Internal server error"
}
```

---

## Debugging Checklist

### 🔍 Quick Checks (2 min)
- [ ] Backend running on port 8001? `lsof -i :8001`
- [ ] Frontend running on port 3000? `lsof -i :3000`
- [ ] User logged in? Check `/mentors` page loads
- [ ] Mentor exists? See mentors listed on `/mentors`

### 🔬 Medium Checks (5 min)
- [ ] Browser console error? F12 → Console
- [ ] Network request details? F12 → Network tab
- [ ] Correct API_BASE? Check `.env.local`
- [ ] Availability slots exist? Frontend should show 8 slots

### 🔧 Deep Checks (10+ min)
```bash
# Test health endpoint
curl http://localhost:8001/healthz

# Test mentor fetch
curl -H "Cookie: token=YOUR_TOKEN" \
     http://localhost:8001/api/v1x/mentors/1

# Test availability fetch
curl -H "Cookie: token=YOUR_TOKEN" \
     http://localhost:8001/api/v1x/mentors/availability/1

# Test booking (full request)
curl -X POST http://localhost:8001/api/v1x/mentors/sessions \
     -H "Cookie: token=YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "mentor_id": 1,
       "scheduled_at": "2026-01-06T09:00:00Z",
       "duration_minutes": 60,
       "topic": "Test Session"
     }'

# Check database
sqlite3 app.db "SELECT COUNT(*) FROM mentor_sessions;"
```

---

## Common Error Messages & Fixes

| Error Message | Cause | Fix |
|---------------|-------|-----|
| "Network error: Cannot reach booking server..." | Backend not running | Start: `uvicorn app.main:app --reload --port 8001` |
| "Topic must be at least 5 characters" | Validation failed | Enter topic with 5+ characters |
| "Not authenticated" (401) | Token missing/expired | Login again via `/login` |
| "Could not find mentor" (404) | Mentor ID wrong | Verify mentor ID from `/mentors` page |
| "Internal server error" (500) | Backend error | Check backend console logs |
| "CORS error" | Cross-origin blocked | Check CORS config in `backend/app/main.py` |

---

## Monitoring During Booking

### Frontend (Browser Console)
- Logs: ✅ Shows when data loaded
- Logs: ✅ Shows booking payload sent
- Error: ✅ Shows detailed error message
- Warning: ⚠️ Check availability fetch warnings

### Backend (Terminal)
- `INFO: GET /api/v1x/mentors/1` - Mentor fetch
- `INFO: GET /api/v1x/mentors/availability/1` - Slots fetch
- `INFO: POST /api/v1x/mentors/sessions` - Booking creation
- `ERROR: ...` - Any errors during processing

### Network (F12 Network Tab)
- Status 200: ✅ Mentor and availability loaded
- Status 201: ✅ Session created
- Status 400+: ❌ Error occurred

---

## Recovery Steps

If booking is stuck or broken:

```bash
# 1. Stop everything (Ctrl+C)
# 2. Clear browser cache
Ctrl+Shift+Delete  # Open clear cache dialog

# 3. Reset database (WARNING: Deletes data)
rm app.db
python backend/create_db.py
python backend/seed_mentors.py

# 4. Restart backend
cd backend
uvicorn app.main:app --reload --port 8001

# 5. Restart frontend
npm run dev

# 6. Clear browser session storage
F12 → Application → Session Storage → Clear All

# 7. Login again and test
```

---

## Success Indicators

✅ **Booking page loaded**:
- Console shows: "Fetching mentor and availability from: http://localhost:8001"
- Page displays mentor name and 8 time slots

✅ **Slots visible**:
- Console shows: "Expanded slots: [...]"
- Page shows: "Monday, January 6, 2026 at 9:00 AM" (not just "09:00")

✅ **Slot selected**:
- Console shows: "Booking session: {...}"
- Page shows purple highlighted button
- Summary shows date and time

✅ **Booking submitted successfully**:
- Network tab shows 201 status
- Page shows success message
- Redirects to dashboard after 2 seconds

