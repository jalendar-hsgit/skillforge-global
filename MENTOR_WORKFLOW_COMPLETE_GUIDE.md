# Mentor Module - Complete Workflow Guide

## 📋 Overview

This guide covers the **complete mentor workflow** from user navigation to earnings withdrawal, including all features, APIs, and implementations.

---

## 🚀 PART 1: MENTOR NAVIGATION & ACCESS FLOW

### Current Issue ❌
Mentors can't easily access the mentor dashboard. The Layout navbar doesn't show mentor-specific links.

### Solution ✅
Add mentor-aware navigation to the Layout component so mentors see dashboard links.

### Navigation Flow

```
User Dashboard (📊)
    ↓ (If Mentor)
    └→ See "Mentor Dashboard" option
    └→ Redirects to /mentors/dashboard
```

### How Mentors Access Dashboard

1. **After Login**: User sees `/dashboard` (student view)
2. **If User is a Mentor**: Show additional "Mentor Dashboard" link
3. **Click Mentor Dashboard**: Navigate to `/mentors/dashboard`
4. **Dashboard loads**: Shows all mentor stats & features

---

## 🔧 PART 2: MENTOR DASHBOARD STRUCTURE

### Main Dashboard (`/mentors/dashboard`)
**File**: `src/pages/mentors/dashboard/index.tsx`

**Features**:
- Stats Cards (Earnings, Sessions, Rating, Students)
- Month Comparison
- Upcoming Sessions
- Quick Actions Grid
- Profile Summary
- Recent Reviews

**Sections/Sub-pages**:

1. **Sessions** (`/mentors/dashboard/sessions`)
   - View all sessions
   - Filter by status (pending, confirmed, completed, cancelled)
   - Join session via meeting link
   - Mark as complete
   - Take session notes

2. **Earnings** (`/mentors/dashboard/earnings`)
   - Total earnings breakdown
   - Monthly earnings chart
   - Payment history
   - Withdraw funds (CRITICAL FEATURE)
   - Payment method management

3. **Students** (`/mentors/dashboard/students`)
   - List of all students taught
   - Student progress
   - Revenue per student
   - Contact/message students

4. **Analytics** (`/mentors/dashboard/analytics`)
   - Session completion rate
   - Average rating trends
   - Student satisfaction
   - Peak hours for sessions
   - Growth metrics

5. **Reviews** (`/mentors/dashboard/reviews`)
   - All reviews received
   - Rating breakdown
   - Response to reviews
   - Review analytics

---

## 📊 PART 3: BACKEND API ENDPOINTS

### Base URL
```
http://localhost:8001/api/v1x
```

### Mentor Portal Endpoints

#### Dashboard Overview
```
GET /mentor-portal/dashboard/overview
Response: {
  "mentor": { id, user_id, status, bio, expertise, hourly_rate },
  "stats": { 
    total_sessions, month_sessions, completed_sessions, 
    total_earnings, month_earnings, average_rating, 
    total_reviews, unique_students 
  },
  "upcoming_sessions": [ { id, student_id, topic, scheduled_at, ... } ],
  "recent_reviews": [ { id, rating, comment, created_at, ... } ]
}
```

#### Sessions Management
```
GET /mentor-portal/dashboard/sessions?status=pending&limit=20&offset=0
Response: {
  "sessions": [ { id, student_id, topic, status, scheduled_at, ... } ],
  "total": 45,
  "completed": 30
}

PATCH /mentor-portal/dashboard/sessions/{session_id}
Body: { "status": "completed" }  // or other status changes
```

#### Earnings Tracking
```
GET /mentor-portal/dashboard/earnings
Response: {
  "total_earnings": 5000.00,
  "month_earnings": 850.50,
  "available_balance": 5000.00,
  "pending_payouts": 0.00,
  "earnings_by_month": [ { month, earnings }, ... ]
}
```

#### Students List
```
GET /mentor-portal/dashboard/students
Response: {
  "students": [
    { 
      id, 
      name, 
      email, 
      sessions_count, 
      total_spent, 
      average_rating,
      last_session 
    },
    ...
  ],
  "total": 15
}
```

#### Analytics Data
```
GET /mentor-portal/dashboard/analytics
Response: {
  "session_stats": { completed, total, completion_rate },
  "rating_trend": [ { date, average_rating }, ... ],
  "peak_hours": { hour, sessions_count },
  "student_satisfaction": { percentage, trend },
  "growth": { month_vs_month_percent, trend }
}
```

#### Reviews
```
GET /mentor-portal/dashboard/reviews?limit=50&offset=0
Response: {
  "reviews": [
    { 
      id, 
      student_id, 
      rating, 
      comment, 
      created_at 
    },
    ...
  ],
  "total": 30,
  "average_rating": 4.6
}
```

### Mentor Endpoints (Main Routes)

#### Apply to Become Mentor
```
POST /mentors/apply
Body: {
  "bio": "string",
  "expertise": ["python", "web-development"],
  "hourly_rate": 75.00
}
Response: { mentor_id, status: "pending" }
```

#### Get Own Mentor Profile
```
GET /mentors/me
Response: {
  "id": 1,
  "user_id": 5,
  "bio": "...",
  "expertise": ["python"],
  "hourly_rate": 75.00,
  "status": "approved",
  "average_rating": 4.6,
  "total_sessions": 45,
  "created_at": "2025-12-20"
}
```

#### Update Mentor Profile
```
PATCH /mentors/me
Body: { bio: "string", expertise: [...], hourly_rate: 80.00 }
```

#### Set Availability Slots
```
POST /mentors/availability
Body: {
  "day_of_week": "monday",
  "start_time": "09:00",
  "end_time": "17:00",
  "timezone": "UTC",
  "max_sessions_per_day": 5
}
```

#### Get Availability Slots
```
GET /mentors/availability
```

---

## 💰 PART 4: PAYOUTS & WITHDRAWALS (CRITICAL)

### Earnings Flow

```
Student Books Session
    ↓
Student pays (Stripe/payment)
    ↓
Payment processed (Stripe takes fee ~2.9% + $0.30)
    ↓
Mentor sees in "available_balance"
    ↓
Mentor requests withdrawal
    ↓
Payment sent to mentor's bank account
```

### Payout Endpoints (TO BE IMPLEMENTED)

#### Get Payout History
```
GET /mentors/payouts
Response: {
  "payouts": [
    {
      "id": 1,
      "amount": 500.00,
      "status": "completed",  // pending, processing, completed, failed
      "requested_at": "2025-12-25",
      "completed_at": "2025-12-26",
      "bank_account": "****1234",
      "method": "bank_transfer"
    }
  ]
}
```

#### Request Withdrawal
```
POST /mentors/payouts/request
Body: {
  "amount": 500.00,
  "payment_method": "bank_transfer"  // or "stripe"
}
Response: {
  "payout_id": 1,
  "status": "pending",
  "estimated_completion": "2025-12-27"
}
```

#### Get Available Balance
```
GET /mentors/balance
Response: {
  "available_balance": 5000.00,
  "pending_payouts": 200.00,
  "total_earned": 5200.00
}
```

#### Add Bank Account (Stripe Connect)
```
POST /mentors/payment-method
Body: {
  "account_holder": "John Doe",
  "account_number": "****1234",
  "routing_number": "****5678",
  "country": "US"
}
```

### Payout Status Flow

```
1. PENDING: User requests withdrawal
2. PROCESSING: Admin verifies bank account
3. COMPLETED: Funds transferred
4. FAILED: Bank rejected, user notified
```

---

## 🔌 PART 5: SESSION WORKFLOW

### Session Lifecycle

```
1. PENDING: Mentor scheduled by student, waiting for mentor confirmation
2. CONFIRMED: Mentor confirms, ready for session
3. IN_PROGRESS: Session is happening right now
4. COMPLETED: Session finished, ready for rating
5. CANCELLED: One party cancelled
```

### Session Management Flow

#### Upcoming Sessions
```
1. Display next 7 days of sessions
2. Show student name, topic, scheduled time
3. Provide "Join" button (leads to meeting link)
4. Show duration (default 60 min, can be custom)
```

#### Join Session
```
1. Mentor clicks "Join Meeting"
2. Opens video call interface (Zoom/Google Meet/custom)
3. Meeting link from database
4. Can record session
5. Timer shows session duration
```

#### Complete Session
```
1. Session time expires or mentor clicks "End Session"
2. Shows "Session Completed"
3. Can add notes
4. Student can rate (1-5 stars)
5. Payment processed
```

### Session Data
```
{
  "id": 1,
  "mentor_id": 5,
  "student_id": 10,
  "topic": "Python Basics",
  "description": "Learn Python fundamentals",
  "scheduled_at": "2025-12-31 14:00",
  "duration_minutes": 60,
  "price": 75.00,
  "status": "confirmed",
  "meeting_link": "https://zoom.us/...",
  "notes": "",
  "recording_url": null,
  "created_at": "2025-12-25"
}
```

---

## 📹 PART 6: CALL RECORDING & STORAGE

### Recording Flow

```
1. Session starts
2. Meeting tool (Zoom/Google Meet) records automatically
3. Recording file created on provider's server
4. After session ends, recording URL stored in database
5. Mentor can download/share with student
```

### Storage Implementation
```
Database Field:
  MentorSession.recording_url: string (nullable)
  
Example:
  "https://zoom.us/recordings/xyz123"
  "https://drive.google.com/file/d/xyz123"
```

### Features
- Auto-record all sessions
- Store in cloud (Zoom/Google Drive)
- Share link with student
- Delete after 30 days (compliance)
- Transcript generation (optional)

---

## 🎯 PART 7: COMPLETE MENTOR FEATURES LIST

### ✅ Already Implemented
- [x] Mentor application/profile
- [x] Session booking API
- [x] Availability slots
- [x] Review system
- [x] Dashboard overview API
- [x] Sessions list API
- [x] Earnings tracking API
- [x] Students list API
- [x] Analytics API
- [x] Admin approval flow

### 🔄 Need Frontend Implementation
- [ ] **Mentor navigation in Layout** (CRITICAL - FIRST PRIORITY)
- [ ] **Payout request interface** (CRITICAL - SECOND PRIORITY)
- [ ] **Sessions management UI**
- [ ] **Earnings chart visualization**
- [ ] **Students list with filters**
- [ ] **Analytics dashboard**
- [ ] **Bank account setup form**
- [ ] **Payment method management**

### 📝 Need Backend Implementation
- [ ] **Payout request endpoint** (POST /mentors/payouts/request)
- [ ] **Payout history endpoint** (GET /mentors/payouts)
- [ ] **Balance check endpoint** (GET /mentors/balance)
- [ ] **Bank account setup** (POST /mentors/payment-method)
- [ ] **Payment processing** (Stripe integration)

---

## 🛠️ PART 8: IMPLEMENTATION ROADMAP

### Phase 1: Navigation (1-2 hours) ✅ FIRST DO THIS
**Goal**: Mentors can access dashboard

**Tasks**:
1. [ ] Update `src/lib/routes.ts` - Add mentor dashboard routes
2. [ ] Update `src/components/Layout.tsx` - Show mentor link if user is mentor
3. [ ] Check `useMe` hook - Returns mentor status
4. [ ] Test: Login as mentor → See mentor dashboard link → Click → Load dashboard

**Files to modify**:
```
src/lib/routes.ts (add mentor routes)
src/components/Layout.tsx (add conditional mentor link)
src/hooks/useMe.ts (ensure mentor status available)
```

### Phase 2: Session Management (2-3 hours)
**Goal**: Mentors can view and manage sessions

**Tasks**:
1. [ ] Complete `src/pages/mentors/dashboard/sessions.tsx`
2. [ ] Add join meeting button with Zoom/Meet integration
3. [ ] Add session filtering (status)
4. [ ] Add complete session action
5. [ ] Handle session notes

**Files**:
```
src/pages/mentors/dashboard/sessions.tsx
src/components/mentor/SessionCard.tsx
```

### Phase 3: Earnings & Payouts (3-4 hours) ⭐ CRITICAL
**Goal**: Mentors can see earnings and request withdrawals

**Tasks**:
1. [ ] Complete `src/pages/mentors/dashboard/earnings.tsx`
2. [ ] Add earnings chart (recharts)
3. [ ] Display balance breakdown
4. [ ] Create payout request form
5. [ ] Add bank account setup form
6. [ ] Backend: Implement payout endpoints
7. [ ] Backend: Stripe Connect integration

**Files**:
```
src/pages/mentors/dashboard/earnings.tsx
src/components/mentor/PayoutRequestModal.tsx
src/components/mentor/BankAccountForm.tsx
backend/app/api/v1x/payouts.py (NEW)
```

### Phase 4: Analytics & Students (2-3 hours)
**Goal**: Mentors can see performance metrics

**Tasks**:
1. [ ] Complete analytics page with charts
2. [ ] Complete students list with filters
3. [ ] Add revenue per student
4. [ ] Add charts for trends

### Phase 5: Testing (1-2 hours)
**Goal**: Ensure all features work without breaking existing

**Tests**:
1. [ ] Student can still book sessions
2. [ ] Sessions appear in mentor dashboard
3. [ ] Earnings calculated correctly
4. [ ] Payout requests work
5. [ ] All navigation works
6. [ ] Error states handled

---

## 🔐 PART 9: SECURITY CHECKLIST

- [ ] Only mentors can access `/mentors/dashboard/*`
- [ ] Mentors can only see their own data
- [ ] Payments verified through Stripe
- [ ] Bank account info encrypted
- [ ] Session recordings access controlled
- [ ] Rate limiting on payout requests
- [ ] Admin approval for payouts > $5000

---

## 📞 PART 10: ERROR HANDLING

### 401 Unauthorized
```
User not logged in
→ Redirect to /login?redirect=/mentors/dashboard
```

### 404 Not a Mentor
```
User not registered as mentor
→ Show message: "You are not registered as a mentor"
→ Button: "Apply to become mentor"
```

### 403 Not Approved
```
Mentor pending approval
→ Show message: "Your mentor application is pending approval"
→ Show approval status
→ Can't access dashboard until approved
```

### 422 Invalid Bank Account
```
Bank account verification failed
→ Show form to update bank details
→ Suggest retry
→ Show helpful error message
```

---

## 🧪 PART 11: TESTING THE COMPLETE FLOW

### Setup Test Data
```bash
# Run seeding script
cd backend
python seed_complete_mentors.py

# Creates:
# - 5 mentors (approved)
# - 45 sessions (mixed statuses)
# - 30 reviews
# - 20 availability slots
```

### Manual Testing Checklist

```
1. LOGIN AS MENTOR
   [ ] Login with mentor.python@test.com
   [ ] Redirect to /dashboard
   [ ] See "Mentor Dashboard" link

2. NAVIGATE TO MENTOR DASHBOARD
   [ ] Click "Mentor Dashboard"
   [ ] Page loads without errors
   [ ] Shows stats cards
   [ ] Shows upcoming sessions

3. VIEW SESSIONS
   [ ] Click "All Sessions"
   [ ] See list of all sessions
   [ ] Filter by status works
   [ ] Join meeting button visible

4. VIEW EARNINGS
   [ ] Click "Earnings"
   [ ] See total earnings
   [ ] See chart of earnings by month
   [ ] See available balance

5. VIEW STUDENTS
   [ ] Click "Students"
   [ ] See list of unique students
   [ ] See revenue per student
   [ ] See session count per student

6. VIEW ANALYTICS
   [ ] Click "Analytics"
   [ ] See completion rate
   [ ] See rating trends
   [ ] See growth metrics

7. REQUEST PAYOUT
   [ ] Click "Withdraw"
   [ ] Enter amount
   [ ] Verify bank account (or add new)
   [ ] Submit payout request
   [ ] Confirm success message
   [ ] Check payout history

8. STUDENT CAN STILL BOOK
   [ ] Login as student
   [ ] Browse mentors
   [ ] Book session
   [ ] Appears in mentor dashboard
```

---

## 🎓 PART 12: COMPLETE API TEST SCRIPT

Save as `test_mentor_complete.py`:

```python
import requests
import json
from datetime import datetime, timedelta

BASE = "http://localhost:8001/api/v1x"
MENTOR_EMAIL = "mentor.python@test.com"
MENTOR_PASS = "password123"

# LOGIN
r = requests.post(f"{BASE}/auth/login", json={
    "email": MENTOR_EMAIL,
    "password": MENTOR_PASS
})
token = r.json()["access_token"]
cookies = {"token": token}

print("✓ Logged in as mentor")

# GET DASHBOARD OVERVIEW
r = requests.get(f"{BASE}/mentor-portal/dashboard/overview", cookies=cookies)
data = r.json()
print(f"\n📊 DASHBOARD OVERVIEW")
print(f"  Total Sessions: {data['stats']['total_sessions']}")
print(f"  Earnings This Month: ${data['stats']['month_earnings']}")
print(f"  Average Rating: {data['stats']['average_rating']}⭐")

# GET SESSIONS
r = requests.get(f"{BASE}/mentor-portal/dashboard/sessions", cookies=cookies)
sessions = r.json()["sessions"]
print(f"\n📋 SESSIONS: {len(sessions)} total")
for s in sessions[:3]:
    print(f"  - {s['topic']} ({s['status']}) @ {s['scheduled_at']}")

# GET EARNINGS
r = requests.get(f"{BASE}/mentor-portal/dashboard/earnings", cookies=cookies)
earnings = r.json()
print(f"\n💵 EARNINGS")
print(f"  Total: ${earnings['total_earnings']}")
print(f"  Available: ${earnings['available_balance']}")

# GET STUDENTS
r = requests.get(f"{BASE}/mentor-portal/dashboard/students", cookies=cookies)
students = r.json()["students"]
print(f"\n👨‍🎓 STUDENTS: {len(students)} unique")

# GET ANALYTICS
r = requests.get(f"{BASE}/mentor-portal/dashboard/analytics", cookies=cookies)
analytics = r.json()
print(f"\n📈 ANALYTICS")
print(f"  Completion Rate: {analytics['session_stats']['completion_rate']}%")
print(f"  Avg Rating Trend: {analytics.get('rating_trend', [])[:3]}")
```

---

## 📚 PART 13: DOCUMENTATION STRUCTURE

This complete guide includes:
1. **Navigation Flow** - How mentors access dashboard
2. **Dashboard Structure** - All pages and features
3. **Backend APIs** - All endpoints with examples
4. **Payouts System** - Withdrawal process
5. **Session Workflow** - Complete session lifecycle
6. **Recording Storage** - Video/call recording
7. **Feature Checklist** - What's done, what's pending
8. **Implementation Roadmap** - Step-by-step instructions
9. **Security** - Safety considerations
10. **Error Handling** - All error cases
11. **Testing** - How to verify everything
12. **API Tests** - Complete testing script

---

## ✨ NEXT STEPS

1. **Read this guide carefully** (you're doing it!)
2. **Check current implementation** (sections below)
3. **Start with Phase 1** - Navigation (most critical)
4. **Follow roadmap** - Complete each phase
5. **Test thoroughly** - Use testing checklist
6. **Deploy** - When all tests pass

---

**Status**: 🔴 **Not Started - Ready to Implement**  
**Estimated Time**: 10-15 hours for complete implementation  
**Priority**: ⭐⭐⭐⭐⭐ **CRITICAL**

