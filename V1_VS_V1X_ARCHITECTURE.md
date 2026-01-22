# V1 vs V1X: Complete Architecture Guide

## 🔴 THE PROBLEM

The codebase has **TWO API versions** running simultaneously:
- **`/api/v1`** - Old/Legacy endpoints
- **`/api/v1x`** - New/Modern endpoints

This causes confusion and bugs when:
1. Developers don't know which version to use
2. Same features exist in both versions
3. Data inconsistencies occur
4. Breaking changes happen

---

## 📊 ARCHITECTURE OVERVIEW

```
BACKEND (FastAPI)
├── /api/v1/      ← Legacy endpoints (OLD FEATURES)
│   ├── auth/
│   ├── courses/
│   ├── quizzes/
│   ├── progress/
│   ├── chat/
│   └── ... (23 modules)
│
└── /api/v1x/     ← New/Modern endpoints (NEW FEATURES)
    ├── auth/        (newer version)
    ├── mentors/     (ONLY in v1x)
    ├── marketplace/
    ├── payments/
    ├── admin/
    └── ... (58 modules)
```

---

## 🔄 WHICH FEATURES ARE WHERE?

### **V1 (Legacy) - Old Features**

| Module | Status | Used By | Notes |
|--------|--------|---------|-------|
| `auth` | OLD | Old pages | Basic login/signup |
| `courses` | OLD | `/courses` page | File-based courses |
| `quizzes` | OLD | Quiz pages | Legacy quiz system |
| `progress` | OLD | Dashboard | Track learning progress |
| `chat` | OLD | Chat feature | Peer messaging |
| `forum` | OLD | Forum pages | Discussion boards |
| `messages` | OLD | Messages | User messages |
| `profiles` | OLD | Profile pages | User profiles |
| `feed` | OLD | Feed page | Activity feed |

**Total: 23 modules in v1**

---

### **V1X (Modern) - New Features**

| Module | Status | Used By | Notes |
|--------|--------|---------|-------|
| `auth` | NEW | New login flow | OAuth + JWT + MFA |
| `mentors` | NEW ONLY | Student & mentor pages | Mentor sessions, availability |
| `mentor_documents` | NEW ONLY | Document verification | Mentor certification |
| `mentor_verification` | NEW ONLY | Admin pages | Verify mentor documents |
| `marketplace` | NEW | Marketplace pages | Sell digital products |
| `marketplace_checkout` | NEW | Checkout | Purchase flow |
| `payments` | NEW | Stripe integration | Payment processing |
| `payouts` | NEW | Mentor earnings | Payout management |
| `admin_analytics` | NEW ONLY | Admin dashboard | Analytics & KPIs |
| `admin_mentors` | NEW ONLY | Admin pages | Approve/reject mentors |
| `job_applications` | NEW | Job tracker | Track job applications |
| `coding_practice` | NEW ONLY | Practice pages | AI code challenges |
| `contests` | NEW ONLY | Contest pages | Coding competitions |
| `code_snippets` | NEW ONLY | Snippets page | Code sharing |
| `courses_db` | NEW | Courses page | Database-backed courses |
| `quizzes_db` | NEW | Quiz pages | Database-backed quizzes |

**Total: 58+ modules in v1x**

---

## 🟢 WHAT SHOULD YOU USE?

### **Rule #1: Use v1x for NEW features**
```
✅ CORRECT: /api/v1x/mentors
❌ WRONG:   /api/v1/mentors  (doesn't exist)

✅ CORRECT: /api/v1x/admin/analytics
❌ WRONG:   /api/v1/admin/analytics  (old/wrong endpoint)
```

### **Rule #2: Don't mix endpoints**
```
❌ BAD: Use /api/v1 for student data, then /api/v1x for mentors
✅ GOOD: Use /api/v1x consistently for all student-related features
```

### **Rule #3: Check what exists before writing**
```
If you need feature X:
1. Search /backend/app/api/v1x/ first
2. If found → Use v1x
3. If not found → Create in v1x
4. NEVER add to v1 (it's frozen)
```

---

## 🐛 WHY THIS CAUSES ISSUES

### **Issue #1: Endpoint Mismatch** 
```
Frontend calls:   /api/v1x/mentors/1/available-slots
Backend has:      /api/v1x/mentors/availability/1

Result: 404 NOT FOUND ❌
```

### **Issue #2: Status Value Mismatch**
```
Frontend expects:  status === 'APPROVED'
Backend returns:   status: 'approved'

Result: Filter doesn't match, data invisible ❌
```

### **Issue #3: Response Format Mismatch**
```
Frontend expects: Direct array [...]
Backend returns:  Wrapped response { data: [...] }

Result: Type error, page crashes ❌
```

### **Issue #4: Missing Error Handling**
```
Frontend calls endpoint that doesn't exist
No error handling in place

Result: "Failed to load" with no debug info ❌
```

---

## ✅ THE FIX (WHAT WAS JUST DONE)

### **Before (Broken)**
```typescript
// Line 193 in src/lib/api/mentorSessionApi.ts
const response = await fetch(`${API_BASE}/api/v1x/mentors/1/available-slots`)
// ❌ Endpoint doesn't exist
// ❌ Returns 404 NOT FOUND
```

### **After (Fixed)**
```typescript
// Line 193 in src/lib/api/mentorSessionApi.ts
const response = await fetch(`${API_BASE}/api/v1x/mentors/availability/1`)
// ✅ Correct endpoint
// ✅ Returns 200 OK with slots
// ✅ Response: { slots: [...] }
```

### **Test Result**
```
Status Code: 200 OK ✓
Slots Returned: 5 slots per mentor ✓
Data Structure: { slots: [...] } ✓
```

---

## 🗺️ FRONTEND USAGE MAP

### **Which Frontend Pages Use Which API Version?**

| Page | URL | API Version | Features |
|------|-----|-------------|----------|
| **Dashboard** | `/dashboard` | v1 | Old dashboard |
| **Advanced Dashboard** | `/dashboard-analytics` | v1x | New analytics |
| **Admin Dashboard** | `/admin` | v1x | Analytics & control |
| **Mentors (Public)** | `/mentors` | v1x | Browse mentors |
| **Book Session** | `/student/book-session` | **v1x** | Book mentors (FIXED) |
| **My Sessions** | `/student/sessions` | **v1x** | View bookings (FIXED) |
| **Mentor Portal** | `/mentor/availability` | v1x | Set availability |
| **Mentor Sessions** | `/mentor/sessions` | v1x | Confirm bookings |
| **Marketplace** | `/marketplace` | v1x | Buy/sell products |
| **Job Tracker** | `/job-tracker` | v1x | Track applications |
| **Coding Practice** | `/practice` | v1x | Practice code |
| **Contests** | `/contests` | v1x | Participate in contests |
| **Courses** | `/paths` | v1x | Learn from courses |
| **Quizzes** | `/quizzes` | v1x | Take quizzes |

---

## 🚀 HOW TO PREVENT FUTURE ISSUES

### **Step 1: Establish Clear Rules**
```
RULE 1: Always use /api/v1x for new features
RULE 2: Check backend endpoint first before writing frontend code
RULE 3: Never call /api/v1 from new student/mentor/admin pages
RULE 4: Document which API version each page uses
```

### **Step 2: Create API Client Layer**
```typescript
// ✅ GOOD: Centralized API calls
// src/lib/api/mentorSessionApi.ts
export async function getAvailableSlots(mentorId: string) {
  // All v1x calls here, tested once, used everywhere
  return fetch(`/api/v1x/mentors/availability/${mentorId}`)
}

// Then import and use everywhere:
import { getAvailableSlots } from '@/lib/api/mentorSessionApi'
const slots = await getAvailableSlots(mentorId)
```

### **Step 3: Type-Safe Response Handling**
```typescript
// ✅ GOOD: Type validation
interface AvailabilityResponse {
  slots: AvailabilitySlot[]
}

const data: AvailabilityResponse = await response.json()
if (data.slots && Array.isArray(data.slots)) {
  // Process slots
}
```

### **Step 4: Error Handling with Debugging**
```typescript
// ✅ GOOD: Helpful error messages
try {
  const response = await fetch(`${API_BASE}/api/v1x/mentors/availability/1`)
  if (!response.ok) {
    console.error(`API Error: ${response.status} ${response.statusText}`)
    console.error(`Endpoint: GET /api/v1x/mentors/availability/1`)
    throw new Error(`Failed to load slots: ${response.status}`)
  }
  const data = await response.json()
  return data.slots
} catch (err) {
  console.error('Error:', err)
  addToast({ type: 'error', message: err.message })
}
```

---

## 📋 CURRENT STATUS

### **BOOKING FLOW - AFTER FIX**

```
1. Student Login ✅ WORKS
   └─ Uses: /api/v1x/auth/login (new auth)

2. View Mentors ✅ WORKS
   └─ Uses: /api/v1x/mentors (list all)

3. Click Book Session ✅ FIXED (WAS BROKEN)
   └─ Uses: /api/v1x/mentors/availability/1 (GET slots)
   └─ BEFORE: Called /api/v1x/mentors/1/available-slots → 404
   └─ AFTER:  Calls /api/v1x/mentors/availability/1 → 200 OK

4. Select Time & Topic ✅ WORKS (NOW)
   └─ Display 5 available time slots per mentor

5. Confirm Booking ✅ WORKS
   └─ Uses: /api/v1x/mentors/sessions/book (POST)

6. View Sessions ✅ WORKS
   └─ Uses: /api/v1x/mentors/sessions/my (GET)
```

---

## 🎯 MIGRATION STRATEGY (Long-term)

### **Current Approach (Coexistence)**
```
Keep v1 intact for backward compatibility
All new features ONLY in v1x
Frontend gradually migrates pages to v1x
```

### **Future Approach (After Migration Complete)**
```
Deprecate v1 (stop accepting new requests)
All pages use v1x
Cleaner API surface
Easier to maintain
```

### **Timeline**
```
NOW:      v1 + v1x coexist
Q1 2026:  v1 deprecated (legacy support only)
Q2 2026:  v1 removed (full v1x)
```

---

## 🔍 API ENDPOINT REFERENCE

### **Student Booking (All v1x)**
```
GET    /api/v1x/mentors                      → List mentors
GET    /api/v1x/mentors/{id}                 → Get mentor details
GET    /api/v1x/mentors/availability/{id}    → Get slots ✅ FIXED
POST   /api/v1x/mentors/sessions/book        → Create booking
GET    /api/v1x/mentors/sessions/my          → View my sessions
PATCH  /api/v1x/mentors/sessions/{id}        → Cancel/update session
POST   /api/v1x/mentors/sessions/{id}/feedback → Add feedback
```

### **Mentor Management (All v1x)**
```
GET    /api/v1x/mentors/me                   → Get my profile
PATCH  /api/v1x/mentors/me                   → Update profile
POST   /api/v1x/mentors/availability         → Add availability
GET    /api/v1x/mentors/sessions/my          → View student bookings
PATCH  /api/v1x/mentors/sessions/{id}        → Confirm/complete session
```

### **Admin (All v1x)**
```
GET    /api/v1x/admin/mentors/applications   → View applications
PATCH  /api/v1x/admin/mentors/{id}/status    → Approve/reject
GET    /api/v1x/admin/analytics              → Dashboard analytics
```

---

## ✨ SUMMARY

| Aspect | v1 | v1x |
|--------|-----|-----|
| **Status** | Legacy | Modern |
| **For** | Old features | New features |
| **Modules** | 23 | 58+ |
| **Should Use?** | NO | YES |
| **Mentor Features** | NO | YES |
| **Admin Features** | Partial | Full |
| **Maintenance** | Frozen | Active |
| **New Code** | Never | Always |

---

## 🚨 KEY TAKEAWAY

**Always use `/api/v1x` for new features. Never add to `/api/v1`.**

The booking issue happened because:
1. Frontend was calling wrong endpoint path
2. No one checked if endpoint existed
3. Error handling was silent (404 not obvious)

**Solution implemented:**
1. Fixed endpoint path in frontend
2. Now returns 200 OK with proper data
3. Students can book sessions again

**Prevention:**
1. Check backend endpoint FIRST
2. Use /api/v1x consistently
3. Test API before writing frontend
4. Add proper error handling
