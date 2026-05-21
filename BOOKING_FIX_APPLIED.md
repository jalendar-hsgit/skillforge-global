# BOOKING FIX - Quick Reference

## ✅ WHAT WAS FIXED

**File:** `src/lib/api/mentorSessionApi.ts` (Line 193-206)

**Issue:** Student booking page showed "Failed to load availability" error

**Root Cause:** Frontend was calling wrong API endpoint path

---

## 📍 THE CHANGE

### Before (Broken)
```typescript
const response = await fetch(`${API_BASE}/api/v1x/mentors/${mentorId}/available-slots`)
// ❌ 404 NOT FOUND - This endpoint doesn't exist!
```

### After (Fixed)
```typescript
const response = await fetch(`${API_BASE}/api/v1x/mentors/availability/${mentorId}`)
// ✅ 200 OK - Returns 5 time slots per mentor
```

---

## 🧪 VERIFICATION

```bash
# Tested endpoint:
GET http://localhost:8001/api/v1x/mentors/availability/1

# Response:
Status: 200 OK ✓
{
  "slots": [
    {
      "id": 1,
      "mentor_id": 1,
      "day_of_week": 0,
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true
    },
    ... 4 more slots ...
  ]
}
```

---

## 🌊 FLOW NOW WORKS

```
Student Login
    ↓
Visit /student/book-session
    ↓ API: GET /api/v1x/mentors?limit=100
    ↓ Shows 4 approved mentors
Click "Book Session"
    ↓
Navigate to /student/book-session/1
    ↓ API: GET /api/v1x/mentors/availability/1
    ↓ ✅ NOW WORKS! Returns 5 time slots
Shows time slots (Mon-Fri, 9am-5pm)
    ↓
Select time, enter topic
    ↓ API: POST /api/v1x/mentors/sessions/book
    ↓ ✅ Creates session with status='pending'
Redirects to /student/sessions
    ↓
Shows new session in list
```

---

## 🎯 BUILDING RULES

### Use v1x for everything new:
```
✅ /api/v1x/mentors
✅ /api/v1x/mentors/availability/1
✅ /api/v1x/mentors/sessions/book
✅ /api/v1x/admin/analytics
✅ /api/v1x/marketplace
✅ /api/v1x/job-applications

❌ /api/v1/mentors (doesn't exist!)
❌ /api/v1/marketplace (might exist but don't use)
❌ /api/v1/admin (old admin)
```

### Check backend FIRST:
```
Before writing frontend:
1. Check if endpoint exists in /backend/app/api/v1x/
2. Test it with curl/Postman
3. Verify response format
4. THEN write frontend code
```

---

## 🚨 WHAT WAS BROKEN

| Component | Status | Details |
|-----------|--------|---------|
| API Path | BROKEN | Frontend: `/mentors/{id}/available-slots` |
| Backend Endpoint | MISSING | This path didn't exist |
| Correct Path | AVAILABLE | `/mentors/availability/{id}` exists |
| Fix | APPLIED | Updated frontend to use correct path |
| Status Code | NOW 200 | Was 404, now returns slots |
| Booking Page | NOW WORKS | Students can now book sessions |

---

## 📄 FILES CHANGED

```
src/lib/api/mentorSessionApi.ts
├─ Line 193: Changed endpoint path
├─ Line 194: GET /api/v1x/mentors/${mentorId}/available-slots
│           → GET /api/v1x/mentors/availability/${mentorId}
└─ Line 206: Comment added explaining wrapped response
```

**Build Status:** ✅ 0 Errors  
**All Pages:** ✅ Compile successfully

---

## 🧑‍💻 FOR DEVELOPERS

If you see "Failed to load [something]" error:

1. **Check the console** - What API endpoint is being called?
2. **Test endpoint directly** - Use Postman or curl
3. **Verify path matches backend** - Check `/backend/app/api/v1x/`
4. **Check response format** - Is it wrapped or direct?
5. **Add error logging** - Don't silently catch errors

Example:
```typescript
try {
  const response = await fetch(apiUrl)
  if (!response.ok) {
    console.error(`API Error: ${response.status}`)
    console.error(`Endpoint: ${apiUrl}`)  // ← Log this!
    console.error(`Response: ${response.text()}`)  // ← And this!
    throw new Error('API call failed')
  }
  return response.json()
} catch (err) {
  console.error('Complete error:', err)  // ← Log everything
  addToast({ type: 'error', message: err.message })
}
```

---

## 📚 DOCUMENTATION

For complete v1 vs v1x explanation, see:
- `V1_VS_V1X_ARCHITECTURE.md` - Full architecture guide
- `BOOKING_FLOWS_COMPLETE_EXPLANATION.md` - Complete booking flows
- `BOOKING_FLOWS_QUICK_SUMMARY.md` - Quick visual summary

---

## ✨ BOTTOM LINE

**Student booking is now fixed. Pages should load properly.**

Test with:
```
1. Login: john.doe@example.com / password123
2. Visit: http://localhost:3000/student/book-session
3. Click: "Book Session" on any mentor
4. See: Available time slots (should show, not error!)
5. Book: Select time and confirm
```

If you still see errors, check the console logs for exact API path that's failing.
