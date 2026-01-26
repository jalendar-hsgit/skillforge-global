# ✅ MY-BOOKINGS FIX - TESTING GUIDE

## What Was Fixed

### Backend Changes
1. ✅ **SessionResponse Schema** (`backend/app/schemas/mentor.py`)
   - Added `mentor_name` field
   - Added `mentor_rating` field
   - These fields now properly returned in API response

2. ✅ **Sessions Endpoint** (`backend/app/api/v1x/mentors.py`)
   - Fixed to pass `mentor_name` directly to SessionResponse
   - Fixed to pass `mentor_rating` directly to SessionResponse
   - No more manual dict assignment

### Frontend Changes
1. ✅ **My Bookings Page** (`src/pages/my-bookings.tsx`)
   - Now uses `useProtectedPage` hook for proper auth
   - Added logging for debugging
   - Proper loading state management
   - Better error handling
   - Handles 401/403 responses
   - Supports both array and {sessions} response formats

---

## Step-by-Step Testing

### Step 1: Restart Backend

```bash
cd backend
# Kill any existing process
# Ctrl+C

# Start fresh
python -m uvicorn app.main:app --reload --port 8001
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started server process
```

### Step 2: Restart Frontend

```bash
# In another terminal
npm run dev
```

Expected output:
```
> next dev
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
```

### Step 3: Login

1. Go to http://localhost:3000
2. Click "Login" or navigate to /login
3. Enter credentials:
   - **Email**: john.doe@example.com
   - **Password**: john123
4. Click "Sign In"

Expected:
- ✅ Should redirect to /dashboard
- ✅ Should see welcome message
- ✅ Token should be in localStorage

### Step 4: Navigate to My Bookings

**Method 1: Direct URL**
- Go to: http://localhost:3000/my-bookings
- Should load without redirect

**Method 2: From Mentors**
- Go to /mentors
- Book a session
- Should redirect to /my-bookings after payment

### Step 5: Verify Display

Should see one of:

**A) If sessions exist:**
```
✅ My Mentor Sessions
   
   [Sarah Chen ⭐ 4.8]
   Python Fundamentals
   
   📅 Tue, Jan 28, 2026
   🕐 2:00 PM
   ⏱️ 60 min
   💰 $75.00
   
   Status: PENDING 🟡
   Payment: PENDING
   
   [Join Meeting] [View Details]
```

**B) If no sessions:**
```
✅ My Mentor Sessions

   📅 No Sessions Booked
   
   You haven't booked any mentor sessions yet.
   Start by browsing mentors and scheduling 
   your first session!
   
   [Browse Mentors]
```

---

## Expected Behavior

### Correct Flow ✅

1. **Login**: john.doe@example.com / john123
2. **Navigate**: Go to /my-bookings
3. **Load**: Page loads with existing sessions
4. **Display**: Shows mentor details (name, rating, price, date/time)
5. **Actions**: Can click "Join Meeting" or "View Details"

### What Changed
- ✅ Page now uses proper auth hook
- ✅ Mentor name is displayed
- ✅ Mentor rating is displayed
- ✅ Better error messages
- ✅ Console logging for debugging

---

## Browser Console Debugging

If something goes wrong, check the console (F12) for logs like:

```javascript
// Good logs:
"Fetching sessions for user..."
"Session fetch response status: 200"
"Sessions response data: Object {sessions: Array(1), total: 1}"
"Parsed sessions: Array(1)"

// Bad logs:
"No token found, redirecting to login"
"Unauthorized, clearing token and redirecting"
"API error: 404 Not Found"
```

---

## Database Check (Optional)

To verify sessions exist in database:

```bash
sqlite3 backend/app/data/skillforge.db

# List all sessions
SELECT id, mentor_id, student_id, price, payment_status, status FROM mentor_sessions;

# Should return rows like:
# 32|1|3|75.0|paid|pending
```

---

## API Endpoint Test

Test the endpoint directly:

```bash
# Get your token first
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"john123"}' \
  | grep -o '"token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

# Now test the sessions endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1x/mentors/sessions/my | python -m json.tool

# Should return:
# {
#   "sessions": [
#     {
#       "id": 32,
#       "mentor_id": 1,
#       "student_id": 3,
#       "topic": "Python Fundamentals",
#       "scheduled_at": "2026-01-28T14:00:00Z",
#       "duration_minutes": 60,
#       "price": 75.0,
#       "payment_status": "paid",
#       "status": "pending",
#       "mentor_name": "Sarah Chen",
#       "mentor_rating": 4.8,
#       ...
#     }
#   ],
#   "total": 1
# }
```

---

## Troubleshooting

### Issue: Still redirecting to login

**Solution:**
1. Check browser console for errors (F12)
2. Clear localStorage: `localStorage.clear()`
3. Logout from app
4. Login again
5. Try /my-bookings

### Issue: Shows "No Sessions Booked"

**Solution:**
1. Book a new session:
   - Go to /mentors
   - Click "Book Session"
   - Complete booking
   - Complete payment (test card: 4242 4242 4242 4242)
   - Should redirect to /my-bookings with new session

### Issue: Mentor name shows as "null" or "Mentor"

**Solution:**
1. Check backend logs for errors
2. Verify database has mentor data:
   ```bash
   sqlite3 backend/app/data/skillforge.db
   > SELECT id, user_id, name FROM mentors;
   ```
3. Verify mentor user exists:
   ```bash
   sqlite3 backend/app/data/skillforge.db
   > SELECT id, name, role FROM users WHERE role='MENTOR';
   ```

### Issue: API returns 401 Unauthorized

**Solution:**
1. Token expired - login again
2. Token invalid - clear localStorage and relogin
3. Check bearer token format in DevTools (should be "Bearer TOKEN")

---

## Success Checklist

- [ ] Backend started without errors
- [ ] Frontend started without errors
- [ ] Logged in successfully
- [ ] Navigated to /my-bookings
- [ ] Page loaded (didn't redirect to login)
- [ ] Either see sessions OR "No Sessions Booked"
- [ ] If sessions exist, see:
  - [ ] Mentor name
  - [ ] Mentor rating
  - [ ] Topic
  - [ ] Date and time
  - [ ] Duration
  - [ ] Price
  - [ ] Payment status
  - [ ] Status badge
- [ ] Action buttons present
- [ ] No console errors

---

## Files Modified

```
✅ backend/app/api/v1x/mentors.py
   - Line 440-464: Fixed mentor details passing

✅ backend/app/schemas/mentor.py
   - Line 100-118: Added mentor_name and mentor_rating fields

✅ src/pages/my-bookings.tsx
   - Line 1-30: Added useProtectedPage hook
   - Line 32-80: Improved auth and data loading
   - Line 111-128: Better loading and auth states
```

---

## Next: Book a Session to Test

1. Go to http://localhost:3000/mentors
2. Click "Book Session" on **Sarah Chen**
3. Fill in:
   - Date: Today + 2 days
   - Time: 2:00 PM
   - Duration: 1 hour
   - Topic: Python Fundamentals
4. Click "Book Session"
5. Complete Stripe payment:
   - Card: 4242 4242 4242 4242
   - Expiry: 12/28
   - CVC: 123
6. Should redirect to /my-bookings
7. Should see your new session!

---

**Status**: ✅ FIXED & READY TO TEST

Start with Step 1 above to begin testing!
