# Complete Booking Flow Explanation

## 🎯 PROBLEM SUMMARY
The student booking flow is **broken** because:
1. **Frontend calls**: `/api/v1x/mentors/{mentorId}/available-slots`
2. **Backend provides**: `/api/v1x/mentors/availability/{mentor_id}`
3. **Endpoint mismatch** = 404 error when student tries to book

---

## 📊 THE TWO FLOWS

### **FLOW #1: Public Discovery (`/mentors`)**

**Who Can Use:** Anyone (no login needed)
**Purpose:** Browse all mentors in the system
**Page Location:** `/src/pages/mentors/index.tsx`

```
START (Public User)
  ↓
1. Visit http://localhost:3000/mentors
  ↓
2. API Call: GET /api/v1x/mentors/search?expertise=&min_rating=&max_price=
  ↓
3. Backend Returns: List of all mentors with status
  ✓ Status values: LOWERCASE ("approved", "pending", "rejected", "suspended")
  ✓ Includes: id, name, bio, expertise, hourly_rate, average_rating
  ↓
4. Frontend Displays: Search/Filter mentors by:
   - Name search
   - Expertise filter
   - Minimum rating filter
   - Maximum price filter
  ↓
5. End User Journey: 
   - View mentor profile
   - See "Become a Mentor" option
   - NO BOOKING (This is just discovery)
```

**Example Response:**
```json
{
  "id": 1,
  "user_id": 8,
  "email": "mentor.sarah@skillforge.com",
  "bio": "Senior Python Dev, 10+ years experience",
  "expertise": "python-ai,web-dev",
  "hourly_rate": 75.0,
  "status": "approved",
  "average_rating": 4.5,
  "total_sessions": 5,
  "user": {
    "full_name": "Mentor Sarah",
    "email": "mentor.sarah@skillforge.com"
  }
}
```

---

### **FLOW #2: Student Booking (`/student/book-session`) ⚠️ BROKEN**

**Who Can Use:** Logged-in students only (protected page)
**Purpose:** Book a mentor session
**Page Locations:** 
- `/src/pages/student/book-session/index.tsx` (Mentor list)
- `/src/pages/student/book-session/[mentorId].tsx` (Time selection)

```
START (Logged-in Student)
  ↓
1. Visit http://localhost:3000/student/book-session
  ↓
2. Page checks: useProtectedPage('user') ← Authentication required
  ↓
3. API Call: GET /api/v1x/mentors?limit=100
  ✓ Works! Backend responds with mentors
  ↓
4. Frontend Filters: Shows ONLY approved mentors
   - Filter: m.status === 'approved' ← LOWERCASE NOW FIXED
  ↓
5. User Sees: 4 mentors (Sarah, David, Emily, James) with:
   - Name, bio, expertise, rate, rating
   - "Book Session" button
  ↓
6. User Clicks: "Book Session" on any mentor
  ↓
7. Navigate to: http://localhost:3000/student/book-session/1
   (Where 1 = mentor ID)
  ↓
8. Page Calls API: GET /api/v1x/mentors/{mentorId}/available-slots
  ❌ ERROR! This endpoint doesn't exist!
     Backend has: /api/v1x/mentors/availability/{mentor_id}
  ↓
9. Page Shows: "Failed to load availability" error
  ↓
10. User Can't: Select time slots or book session
```

---

## 🔴 THE CRITICAL BUG

| Layer | Issue | Status |
|-------|-------|--------|
| **Frontend API Call** | Requests `/api/v1x/mentors/1/available-slots` | ❌ Wrong path |
| **Backend Endpoint** | Provides `/api/v1x/mentors/availability/1` | ✅ Exists |
| **Result** | 404 Not Found | 🚫 BROKEN |

---

## 📋 WHAT EXISTS IN DATABASE

```
✅ 4 Mentors: All with status='APPROVED' in DB
✅ 20 Availability Slots: 
   - 5 per mentor (Mon-Fri, 9am-5pm)
   - Stored in mentor_availability table
✅ 61 Mentor Sessions:
   - 37 PENDING
   - 12 CONFIRMED  
   - 12 COMPLETED
```

---

## 🔧 HOW TO FIX

### **Option A: Fix Frontend to Use Correct Endpoint**

**File:** `/src/lib/api/mentorSessionApi.ts` (Line 193)

**Current (Wrong):**
```typescript
export async function getAvailableSlots(mentorId: string): Promise<AvailabilitySlot[]> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/${mentorId}/available-slots`, {
    // ❌ Wrong path!
```

**Should Be:**
```typescript
export async function getAvailableSlots(mentorId: string): Promise<AvailabilitySlot[]> {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/availability/${mentorId}`, {
    // ✅ Correct path!
```

**AND Fix Response Parsing:**

**Current:**
```typescript
const data = await response.json();
return data.slots || [];  // ❌ Response is wrapped in 'slots' object
```

**Should Be:**
```typescript
const data = await response.json();
// Response structure from backend is: { slots: [...] }
return data.slots || data || [];  // ✅ Handle wrapped response
```

### **Option B: Create Missing Endpoint in Backend**

Alternative: Add `/api/v1x/mentors/{mentorId}/available-slots` endpoint that mirrors the existing one.
**Not recommended** - Just fix the frontend to use existing endpoint.

---

## 🌊 COMPLETE STUDENT BOOKING WORKFLOW (After Fix)

```
LOGIN as Student: john.doe@example.com
  ↓
Visit /student/book-session
  ↓
API: GET /api/v1x/mentors?limit=100
  ↓ Response (4 mentors, all with status='approved')
Display: List of available mentors
  ↓
Click: "Book Session" on Sarah Chen
  ↓
Navigate to: /student/book-session/1
  ↓
API: GET /api/v1x/mentors/availability/1 ← FIXED ENDPOINT
  ↓ Response (20 time slots for Sarah)
Display: Calendar/time slots showing:
  - Monday 9:00-17:00
  - Tuesday 9:00-17:00
  - Wednesday 9:00-17:00
  - Thursday 9:00-17:00
  - Friday 9:00-17:00
  ↓
User: Selects a time slot (e.g., Monday 2:00 PM)
  ↓
User: Enters:
  - Session topic
  - Duration (30, 60, or 90 minutes)
  - Description (optional)
  ↓
Click: "Book Session" button
  ↓
API: POST /api/v1x/mentors/sessions/book
Body:
{
  "mentor_id": "1",
  "topic": "React Hooks Tutorial",
  "description": "Help with custom hooks",
  "scheduled_at": "2026-01-27T14:00:00Z",
  "duration_minutes": 60
}
  ↓ Response (Session created with status='pending')
Success: "Session booked successfully!"
  ↓
Redirect to: /student/sessions
  ↓
Display: "My Sessions" page showing:
  - New session in PENDING status
  - Other sessions (confirmed/completed)
  - Option to cancel or view details
```

---

## 🔗 ALL CORRECT ENDPOINTS

### **Public Browsing**
```
GET /api/v1x/mentors/search
  Returns: List of mentors with filters
  Auth: Optional
  Query Params: expertise, min_rating, max_price
```

### **Student Booking (PROTECTED)**
```
GET /api/v1x/mentors?limit=100
  Returns: List of mentors
  Auth: Required
  Usage: Show mentors to book from

GET /api/v1x/mentors/availability/{mentor_id}
  Returns: { slots: [...] }
  Auth: Not required
  Usage: Get available time slots for a mentor
  ⚠️ FRONTEND IS CALLING WRONG PATH!

POST /api/v1x/mentors/sessions/book
  Body: { mentor_id, topic, scheduled_at, duration_minutes }
  Returns: SessionResponse with id, status='pending'
  Auth: Required (Bearer token)
  Usage: Create a booking

GET /api/v1x/mentors/sessions/my
  Returns: { sessions: [...], total, upcoming, completed, cancelled }
  Auth: Required
  Usage: Student view their sessions

PATCH /api/v1x/mentors/sessions/{session_id}
  Body: { status: 'cancelled' }
  Returns: Updated session
  Auth: Required
  Usage: Cancel a session

POST /api/v1x/mentors/sessions/{session_id}/feedback
  Body: { rating, comments }
  Returns: SessionFeedbackResponse
  Auth: Required
  Usage: Submit feedback on completed session
```

### **Mentor Management (MENTOR ROLE)**
```
POST /api/v1x/mentors/availability
  Body: { day_of_week, start_time, end_time }
  Returns: AvailabilitySlotResponse
  Auth: Required
  Usage: Mentor adds availability

GET /api/v1x/mentors/sessions/my
  Returns: Sessions for this mentor to confirm
  Auth: Required
  Usage: Mentor see student bookings
```

---

## 👥 USER ROLES RECAP

| Role | Can Access | Main Pages | Action |
|------|---|---|---|
| **USER** (Student) | /student/book-session, /student/sessions | Browse & book mentors | Book sessions |
| **MENTOR** | /mentor/availability, /mentor/sessions | Manage availability | Confirm bookings |
| **ADMIN** | /admin/mentors | Review applications | Approve/reject mentors |
| **SUPERADMIN** | All admin pages | Full system control | Everything |
| **Anonymous** | /mentors (public browse) | Public discovery | View mentor profiles |

---

## 📝 SUMMARY

**Status:** 🔴 **BOOKING BROKEN - ENDPOINT MISMATCH**

**Root Cause:** Frontend calls `/api/v1x/mentors/{id}/available-slots` (wrong)  
**Backend Has:** `/api/v1x/mentors/availability/{id}` (correct)

**Quick Fix:** Update 1 line in `/src/lib/api/mentorSessionApi.ts` (Line 193)

**After Fix:** Students will be able to:
1. ✅ See list of approved mentors
2. ✅ Click to book a session
3. ✅ See available time slots
4. ✅ Select date/time and topic
5. ✅ Confirm booking
6. ✅ View sessions with mentors

---

## 🧪 TEST STEPS

### Before Fix (Current - Broken)
```
1. Login: http://localhost:3000/login
   Email: john.doe@example.com
   Password: password123

2. Navigate: http://localhost:3000/student/book-session
   ✓ Shows 4 mentors

3. Click: "Book Session" on Sarah Chen
   Navigate to: /student/book-session/1
   ✗ ERROR: "Failed to load availability"
```

### After Fix (Expected)
```
1. Login: http://localhost:3000/login
   Email: john.doe@example.com
   Password: password123

2. Navigate: http://localhost:3000/student/book-session
   ✓ Shows 4 mentors

3. Click: "Book Session" on Sarah Chen
   ✓ Navigate to: /student/book-session/1
   ✓ Shows 20 available time slots
   ✓ Can select date/time
   ✓ Can enter topic and duration
   ✓ "Book Session" button works
   ✓ Redirects to /student/sessions
   ✓ Shows the new pending session
```
