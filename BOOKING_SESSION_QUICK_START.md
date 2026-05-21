# Session Booking - Quick Start & Testing

## What Was Fixed

The booking form now has:
1. **Better error messages** - Shows exact issue instead of generic "Failed to fetch"
2. **Console logging** - Open DevTools (F12) to see detailed debug info
3. **Network error handling** - Detects if backend is unreachable
4. **Response error handling** - Shows server errors clearly
5. **Availability expansion** - Converts recurring slots to future dates

---

## How to Test

### Prerequisites
1. **Backend running** (port 8001):
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Frontend running** (port 3000):
   ```bash
   npm run dev
   ```

3. **Database seeded**:
   ```bash
   python backend/seed_mentors.py
   ```

4. **Logged in** as student

---

### Test Steps

#### 1. Open Booking Page
- Visit `/mentors` page
- Click on any mentor card
- Click "Book a Session" button
- You should see: `/mentors/[id]/book`

#### 2. Check Console (F12)
- Open DevTools: **F12**
- Go to **Console** tab
- You should see:
  ```
  Fetching mentor and availability from: http://localhost:8001
  Mentor loaded: { id: 1, ... }
  Raw availability slots: [ { id: 1, day_of_week: 0, ... } ]
  Expanded slots: [ { id: 1, expanded_date: "2026-01-06T09:00:00.000Z", ... } ]
  ```

#### 3. Verify Availability Display
- Should see 8 time slots displayed
- Each slot shows: **"Monday, January 6, 2026" + "9:00 AM"**
- Not just: "09:00"

#### 4. Test Slot Selection
- Click any slot
- Slot should highlight (purple border)
- Booking summary on right should update with:
  - Full date and time
  - Duration (60 min)
  - Total cost

#### 5. Test Booking Submission
- Fill in topic: "Learn FastAPI" (min 5 chars)
- Optionally add notes
- Click "Book Session" button
- Monitor Console for:
  ```
  Booking session: { mentor_id: 1, scheduled_at: "2026-01-06T09:00:00.000Z", ... }
  ```

#### 6. Check Result
- Success: Redirect to dashboard after 2 seconds
- Error: See detailed error message with:
  - Network error indication
  - Server error details
  - Example: "Network error: Cannot reach booking server at http://localhost:8001..."

---

## Debugging if Something's Wrong

### If you see "Failed to fetch" in UI:

1. **Check browser console** (F12 → Console):
   - Look for detailed error message
   - Copy exact error text

2. **Check Network tab** (F12 → Network):
   - Filter by "Fetch/XHR"
   - Click on `mentors/sessions` request
   - Check Status: 
     - 201 = Success ✅
     - 400 = Bad request ❌
     - 500 = Server error ❌

3. **Check backend logs**:
   - Terminal running uvicorn should show:
     ```
     INFO:     POST http://localhost:8001/api/v1x/mentors/sessions HTTP/1.1" 201
     ```

### If Backend Can't Be Reached:

Error message: `"Network error: Cannot reach booking server at http://localhost:8001..."`

**Solution**:
```bash
# Terminal 1: Start Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Test connectivity
curl http://localhost:8001/healthz
# Expected: {"ok":true}
```

### If Mentor Not Found:

Error: `"Could not find mentor with id: X"`

**Solution**:
```bash
# Check mentors exist in database
python3 -c "
from app.core.db import SessionLocal
from app.modelsx.mentor import Mentor
db = SessionLocal()
mentors = db.query(Mentor).all()
print(f'Total mentors: {len(mentors)}')
for m in mentors:
    print(f'  ID: {m.id}, Approved: {m.status}')
"

# If none, seed:
python backend/seed_mentors.py
```

### If No Availability Slots:

You see: `"Demo Mode: No availability slots found..."`

**Solution**:
```bash
# Check availability in database
python3 -c "
from app.core.db import SessionLocal
from app.modelsx.mentor import MentorAvailability
db = SessionLocal()
slots = db.query(MentorAvailability).all()
print(f'Total slots: {len(slots)}')
for s in slots:
    print(f'  Mentor {s.mentor_id}: {s.start_time}-{s.end_time}')
"

# If none, add:
python backend/add_future_availability.py
```

---

## Console Output Examples

### ✅ Successful Load
```javascript
Fetching mentor and availability from: http://localhost:8001
Mentor loaded: {
  id: 1,
  user_id: 1,
  bio: "Full-stack engineer...",
  expertise: "python,nodejs,react",
  hourly_rate: 80,
  average_rating: 4.8
}
Raw availability slots: [
  {
    id: 1,
    mentor_id: 1,
    day_of_week: 0,        // Monday
    date: null,
    start_time: "09:00",
    end_time: "12:00",
    is_available: true
  }
]
Expanded slots: [
  {
    id: 1,
    mentor_id: 1,
    day_of_week: 0,
    date: null,
    start_time: "09:00",
    end_time: "12:00",
    is_available: true,
    expanded_date: "2026-01-06T09:00:00.000Z"  // ← Added!
  }
]
```

### ✅ Successful Booking
```javascript
Booking session: {
  mentor_id: 1,
  scheduled_at: "2026-01-06T09:00:00.000Z",
  duration_minutes: 60,
  topic: "Learn FastAPI"
}
// Then redirects to dashboard
```

### ❌ Backend Not Running
```javascript
Network error: Cannot reach booking server at http://localhost:8001. 
Make sure the backend is running.
```

### ❌ Server Error
```javascript
Booking error: Could not create session: Database constraint violation
```

---

## API Endpoints Being Called

| Method | Endpoint | Purpose | Expected Response |
|--------|----------|---------|------------------|
| GET | `/api/v1x/mentors/{id}` | Get mentor info | 200, MentorProfileResponse |
| GET | `/api/v1x/mentors/availability/{id}` | Get availability slots | 200, AvailabilityListResponse |
| POST | `/api/v1x/mentors/sessions` | Create booking | 201, SessionResponse |

---

## Data Flow

```
1. User opens booking page
   ↓
2. Frontend fetches mentor info + availability
   ↓
3. Convert recurring slots (e.g., "Monday") → future dates
   ↓
4. Display 8 expanded slots in calendar
   ↓
5. User selects slot + fills form
   ↓
6. POST /api/v1x/mentors/sessions with:
   - mentor_id
   - scheduled_at (ISO datetime from expanded_date)
   - duration_minutes
   - topic
   ↓
7. Backend validates:
   - User is logged in (401 if not)
   - Mentor exists (404 if not)
   - Time slot is available
   - Session doesn't conflict with other bookings
   ↓
8. Create session with status: PENDING
   ↓
9. Return SessionResponse with session.id
   ↓
10. Frontend shows success message or payment modal
```

---

## Files Changed

- ✅ `src/pages/mentors/[id]/book.tsx`
  - Enhanced error handling with network error detection
  - Detailed console logging for debugging
  - Better error messages for users
  - Availability expansion logic (recurring → future dates)

- ✅ `BOOKING_SESSION_FIX.md` - Technical details
- ✅ `BOOKING_TEST_GUIDE.md` - Testing instructions
- ✅ `FAILED_TO_FETCH_FIX.md` - Troubleshooting guide

---

## Next Steps if Still Issues

1. **Provide**:
   - Exact error message from browser console
   - Screenshot of Network tab response
   - Backend logs output

2. **Check**:
   - `backend/.env` exists with DATABASE_URL
   - Database is initialized: `python backend/create_db.py`
   - Mentors are seeded: `python backend/seed_mentors.py`

3. **Restart Everything**:
   ```bash
   # Stop all processes (Ctrl+C)
   # Clear cache: Ctrl+Shift+Delete in browser
   # Restart backend
   # Restart frontend
   ```
