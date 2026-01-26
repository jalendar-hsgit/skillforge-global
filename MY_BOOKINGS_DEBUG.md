# /my-bookings Debugging Guide

## Issue: Page redirects to login or shows no bookings

### Step 1: Verify Backend is Running
```bash
# Check if backend is responding
curl http://localhost:8001/api/v1x/mentors/list

# Should return list of mentors (no auth required)
```

### Step 2: Test Authentication Token
```bash
# Login to get a token
curl -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"john123"}'

# Save the token from response
# Expected response: {"token":"eyJhbGc...","user_id":3}
```

### Step 3: Test Sessions Endpoint Directly
```bash
# Replace TOKEN with actual token from login
curl http://localhost:8001/api/v1x/mentors/sessions/my \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json"

# Expected response:
# {
#   "sessions": [
#     {
#       "id": 32,
#       "mentor_id": 1,
#       "student_id": 3,
#       "topic": "Python Fundamentals",
#       "scheduled_at": "2026-01-28T14:00:00Z",
#       "duration_minutes": 60,
#       "price": 75.00,
#       "payment_status": "pending",
#       "status": "pending",
#       "mentor_name": "Sarah Chen",
#       "mentor_rating": 4.8
#     }
#   ],
#   "total": 1
# }
```

### Step 4: Check Browser LocalStorage
```javascript
// Open browser console (F12) and run:
console.log('Token:', localStorage.getItem('token'));
console.log('User:', localStorage.getItem('user'));

// Should show your auth token
```

### Step 5: Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Navigate to /my-bookings
4. Check the API call to `/api/v1x/mentors/sessions/my`
5. Look for:
   - Status code (should be 200, not 401/403)
   - Response headers (should have auth)
   - Response body (should have sessions array)

---

## Common Issues & Solutions

### Issue 1: "Redirects to login immediately"

**Cause**: No token in localStorage

**Solution**:
1. Go to /login
2. Login with: email: john.doe@example.com, password: john123
3. Should be redirected and token saved
4. Then go to /my-bookings

### Issue 2: "401 Unauthorized on API call"

**Cause**: Token expired or invalid

**Solution**:
1. Clear localStorage: `localStorage.clear()`
2. Logout from app
3. Login again
4. Try /my-bookings again

### Issue 3: "Shows empty sessions (No Sessions Booked)"

**Cause**: No sessions booked for this user or API returns empty array

**Solution**:
1. Go to /mentors
2. Click "Book Session" on a mentor
3. Complete the booking
4. Go back to /my-bookings
5. Should now see the session

### Issue 4: "Mentor details not showing (null/undefined)"

**Cause**: Backend not returning mentor_name and mentor_rating

**Solution**:
Check backend logs:
```bash
# Make sure mentor_name and mentor_rating are in response
curl http://localhost:8001/api/v1x/mentors/sessions/my \
  -H "Authorization: Bearer YOUR_TOKEN" | python -m json.tool
```

---

## Quick Fix Checklist

- [ ] Backend running on port 8001
- [ ] Logged in to app (see token in DevTools)
- [ ] Token is in localStorage
- [ ] API endpoint returns 200 status
- [ ] Sessions array is not empty
- [ ] mentor_name field is present
- [ ] mentor_rating field is present

---

## Manual Test Flow

```
1. Start backend:
   cd backend
   python -m uvicorn app.main:app --reload --port 8001

2. Start frontend:
   npm run dev

3. Open http://localhost:3000/login

4. Login with:
   Email: john.doe@example.com
   Password: john123

5. Navigate to /mentors

6. Click "Book Session" on Sarah Chen

7. Fill in booking details:
   Date: Today + 2 days
   Time: 2:00 PM
   Duration: 1 hour
   Topic: Python Fundamentals

8. Click "Book Session"

9. Pay with test card: 4242 4242 4242 4242

10. Should redirect to /my-bookings

11. Should see your booked session with:
    - Mentor name: Sarah Chen
    - Rating: 4.8 stars
    - Price: $75.00
    - Date/Time
    - Status: Pending
```

---

## Files Updated to Fix Issues

1. **src/pages/my-bookings.tsx**
   - ✅ Added token check in useEffect
   - ✅ Added 401/403 error handling
   - ✅ Fixed response parsing (handle both array and {sessions} format)
   - ✅ Added logging for debugging

2. **backend/app/schemas/mentor.py**
   - ✅ Added mentor_name field to SessionResponse
   - ✅ Added mentor_rating field to SessionResponse

3. **backend/app/api/v1x/mentors.py**
   - ✅ Pass mentor_name directly to SessionResponse
   - ✅ Pass mentor_rating directly to SessionResponse

---

## Browser Console Commands

```javascript
// Check token exists
localStorage.getItem('token') // Should show JWT token

// Check API base
console.log(process.env.NEXT_PUBLIC_API_BASE) // Should show http://localhost:8001

// Clear all data and relogin
localStorage.clear()

// Check what /my-bookings is trying to fetch
// Open Network tab and look for mentors/sessions/my
```

---

## Backend Test Command

```bash
# Test endpoint directly without token (should fail with 401)
curl http://localhost:8001/api/v1x/mentors/sessions/my

# Test with token (should return sessions)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1x/mentors/sessions/my

# See full response with pretty print
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1x/mentors/sessions/my | python -m json.tool
```

---

## Success Indicators

When fixed, you should see:
✅ Page loads without redirect  
✅ Either "No Sessions Booked" OR list of sessions  
✅ Each session shows:
  - Mentor name
  - Mentor rating
  - Topic
  - Date and time
  - Duration
  - Price
  - Payment status
  - Status badge
- ✅ Action buttons (Join Meeting, View Details)
- ✅ "Book New Session" button works
- ✅ No errors in console

---

## Next Steps if Still Issues

1. Check backend logs for errors
2. Verify database has sessions (sqlite3)
3. Check API response with curl
4. Check browser DevTools Network tab
5. Clear browser cache (Ctrl+Shift+Del)
6. Try incognito window
7. Restart both backend and frontend
