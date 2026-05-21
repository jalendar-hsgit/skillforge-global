# MENTOR EARNINGS - VISUAL FLOW DIAGRAM

## Current System vs. What Needs to Be Built

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                          COMPLETE MENTOR PLATFORM                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ STUDENT SIDE: Booking Mentor Session (✅ 100% COMPLETE)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  1. BROWSE MENTORS                      2. SELECT AVAILABILITY              │
│     /mentor-booking.tsx                    GET /mentors/{id}/availability   │
│     ├─ List mentors                        ├─ Show calendar                 │
│     ├─ Search by expertise                 ├─ Select date/time              │
│     ├─ Filter by rating                    └─ Show price                    │
│     └─ Show hourly rate                                                      │
│                         ↓                                    ↓               │
│  3. PROCESS PAYMENT                     4. CONFIRMATION                    │
│     POST /payments/create-payment-intent   ├─ Session booked               │
│     ├─ Enter card details                  ├─ Mentor notified              │
│     ├─ Stripe processing                   └─ Redirect to dashboard        │
│     └─ Confirm payment                                                      │
│                         ↓                                                     │
│  5. DATABASE: MentorSession Created                                          │
│     ├─ mentor_id = 5 (Sarah Chen)                                           │
│     ├─ student_id = 10 (John Student)                                       │
│     ├─ price = $75                                                           │
│     ├─ status = CONFIRMED                                                    │
│     └─ payment_status = COMPLETED                                            │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ MENTOR SIDE: Earnings (✅ 80% COMPLETE)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  When Session Completes:                                                     │
│  • MentorEarning record created:                                             │
│    ├─ gross_amount = $75                                                     │
│    ├─ platform_fee = $15 (20%)                                               │
│    └─ net_amount = $60                                                       │
│                                                                               │
│  Mentor Views Dashboard:                                                     │
│  GET /mentor-portal/dashboard/overview                                       │
│  ├─ Total Earnings: $3,375.00 ✅                                            │
│  ├─ Month Earnings: $600.00 ✅                                              │
│  ├─ Completed Sessions: 45 ✅                                               │
│  ├─ Average Rating: 4.8 ✅                                                  │
│  └─ Upcoming Sessions: 2 ✅                                                 │
│                                                                               │
│  Mentor Views Earnings Details:                                              │
│  GET /mentors/payouts/earnings                                               │
│  ├─ [Session #123] [John] [Python] [$75] [$15 fee] [$60 net] ✅             │
│  ├─ [Session #124] [Jane] [WebDev] [$85] [$17 fee] [$68 net] ✅             │
│  └─ [Session #125] [Bob]  [ML]     [$95] [$19 fee] [$76 net] ✅             │
│                                                                               │
│  Mentor Wants to Request Payout... ❌ STOPS HERE                            │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ MISSING PIECES (❌ 0% COMPLETE) - THIS IS WHAT YOU BUILD                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Step 1: Add Payment Method (⏱️ 30 min to implement)                        │
│  ────────────────────────────────────────────────────────────────────        │
│  Mentor clicks "Add Payment Method"                                          │
│  Form appears with:                                                          │
│    ├─ Account Holder Name          [______________________]                  │
│    ├─ Account Number                [____ ____ ____ ____]  (password field) │
│    ├─ Routing Number                [_________]            (password field)  │
│    └─ [Add Method Button]                                                    │
│                                                                               │
│  Backend:                                                                     │
│    POST /mentors/payment-methods                                             │
│    ├─ Validate inputs                                                        │
│    ├─ Encrypt account_number                                                 │
│    ├─ Encrypt routing_number                                                 │
│    ├─ Create PaymentMethod record                                            │
│    └─ Send verification email                                                │
│                                                                               │
│  Response (safe - no full account number!):                                 │
│    {                                                                          │
│      "id": 1,                                                                 │
│      "bank_name": "Chase",                                                    │
│      "last4": "1234",      ← Only last 4 digits shown!                      │
│      "verified": false,                                                       │
│      "is_default": false                                                      │
│    }                                                                          │
│                                                                               │
│  Step 2: List Payment Methods (⏱️ 15 min to implement)                      │
│  ──────────────────────────────────────────────────────                    │
│  GET /mentors/payment-methods                                                │
│  Response:                                                                    │
│    [                                                                          │
│      {id: 1, bank: "Chase", last4: "1234", default: true, verified: true}  │
│      {id: 2, bank: "Wells Fargo", last4: "5678", default: false, verified: true}
│    ]                                                                          │
│                                                                               │
│  Step 3: Request Payout (⏱️ 45 min to implement)                            │
│  ─────────────────────────────────────────────────────                       │
│  Mentor clicks "Request Payout"                                              │
│  Form appears with:                                                          │
│    ├─ Available Balance: $150.00                                             │
│    ├─ Payout Amount:     [______] (validate: 10 ≤ amount ≤ $150)           │
│    ├─ Payment Method:    [Chase ••••1234 ▼]                                 │
│    └─ [Request Payout]                                                      │
│                                                                               │
│  Backend:                                                                     │
│    POST /mentors/payouts/request                                             │
│    ├─ Validate: amount > 0                                                   │
│    ├─ Validate: amount ≤ available_balance                                   │
│    ├─ Check rate limit (1 per 24h)                                           │
│    ├─ Create MentorPayout record                                             │
│    │  ├─ status = PENDING                                                    │
│    │  ├─ amount = $150                                                       │
│    │  └─ requested_at = now                                                  │
│    └─ Send email to mentor                                                   │
│                                                                               │
│  Database Changes:                                                            │
│    MentorPayout (NEW RECORD)                                                 │
│      ├─ id = #P001                                                           │
│      ├─ mentor_id = 5                                                        │
│      ├─ amount = $150.00                                                     │
│      ├─ status = PENDING                                                     │
│      └─ requested_at = 2026-01-22 14:00                                      │
│                                                                               │
│  Step 4: Verify Payment Method (⏱️ 30 min to implement) [BONUS]            │
│  ──────────────────────────────────────────────────────────────────        │
│  Email sent to mentor with verification link                                 │
│  Mentor clicks link                                                          │
│  Payment method marked as verified=true                                      │
│                                                                               │
│  Step 5: Admin Approval (⏱️ 1 hour to implement) [PHASE 6]                 │
│  ───────────────────────────────────────────────────────────                │
│  Admin Dashboard shows:                                                       │
│    [Pending Payout Request #P001]                                            │
│    Mentor: Sarah Chen                                                         │
│    Amount: $150.00                                                            │
│    Method: Chase ••••1234 (VERIFIED)                                         │
│    [APPROVE] [REJECT]                                                        │
│                                                                               │
│  If approved:                                                                 │
│    POST /admin/mentor-payouts/P001/approve                                   │
│    ├─ Transfer $150 to bank account                                          │
│    ├─ Update status = PROCESSING → COMPLETED                                 │
│    └─ Send email to mentor                                                   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ FINAL RESULT (After 5-6 hours of work)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Mentor Complete Flow:                                                       │
│  1. Views earnings in dashboard ✅                                           │
│  2. Adds bank account securely ✅                                            │
│  3. Requests payout (5-6 hours NEW WORK ✨)                                  │
│  4. Waits for admin approval ✅                                              │
│  5. Receives payment notification ✅                                         │
│  6. Money in bank account ✅                                                 │
│  7. Views payout history ✅                                                  │
│                                                                               │
│  Total Time: 5-6 hours                                                       │
│  Revenue Model: COMPLETE ✅                                                  │
│  Security: EXCELLENT ✅                                                      │
│  Design: CONSISTENT ✅                                                       │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technical Stack Reference

```
FRONTEND STACK:
  Pages:
    ├─ /mentor-booking.tsx ✅ (Student books mentor)
    └─ /mentors/dashboard/
       ├─ index.tsx ✅ (Overview)
       ├─ earnings.tsx ✅ (Earnings detail)
       ├─ payouts.tsx ⚠️ (Update with new endpoints)
       └─ ...other pages

  API Layer:
    ├─ lib/mentorBookingApi.ts ✅ (Booking)
    ├─ lib/orderApi.ts ✅ (Payments)
    └─ lib/mentorEarningsApi.ts ❌ (NEW - You create this)

  Components:
    ├─ DashboardLayout ✅
    ├─ DashboardStatCard ✅
    ├─ Form inputs ✅
    └─ All theme colors ✅

  Theme:
    ├─ forgePurple (#6B3BFF) - Headers
    ├─ aiElectric (#00E5FF) - Accents
    ├─ neuralBlue (#1E9EFF) - Secondary
    ├─ deepTech (#0B0A13) - Backgrounds
    └─ techGray (#B6BED3) - Text


BACKEND STACK:
  Models:
    ├─ Mentor ✅
    ├─ MentorSession ✅
    ├─ MentorEarning ✅
    ├─ MentorPayout ✅
    └─ PaymentMethod ❌ (NEW - You create this)

  Routers:
    ├─ mentors.py (1267 L) ✅ (Booking)
    ├─ payouts.py (388 L) ⚠️ (Update with 5 endpoints)
    └─ admin.py ✅ (Admin features)

  Security:
    ├─ JWT authentication ✅
    ├─ Role-based access ✅
    ├─ CORS configured ✅
    └─ Encryption utility ❌ (Add for payment methods)

  Database:
    ├─ SQLAlchemy ✅
    ├─ SQLite (dev) / PostgreSQL (prod) ✅
    ├─ 214 tables already ✅
    └─ Ready for PaymentMethod table ✅


THEME INTEGRATION:
  ├─ tailwind.config.ts ✅ (All colors defined)
  ├─ DashboardStatCard uses colors ✅
  ├─ Forms use standard Tailwind ✅
  ├─ Consistent spacing ✅
  └─ Mobile responsive ✅
```

---

## Code Statistics

```
EXISTING CODE:
  Lines of Frontend Code:   ~3,000+
  Lines of Backend Code:    ~20,000+
  Lines of Database Code:   ~2,000+
  Total Already Built:      25,000+ lines
  
TO BUILD (5-6 hours):
  PaymentMethod Model:      ~80 lines
  Backend Endpoints:        ~400 lines
  Frontend API Layer:       ~150 lines
  Frontend Component Updates: ~200 lines
  Total New Code:           ~830 lines
  
REUSE & LEVERAGE:
  Dashboard components:     ~100% reuse ✅
  API patterns:             ~100% reuse ✅
  Theme system:             ~100% reuse ✅
  Authentication:           ~100% reuse ✅
  
RESULT:
  "Standing on shoulders of giants"
  You're not building from scratch
  You're completing the last 20%
```

---

## Files Reference Card

```
🔧 FILES TO TOUCH:

BACKEND (3 files):
  1. Create: backend/app/modelsx/payment_method.py (80 L)
  2. Edit: backend/app/main.py (1 import line)
  3. Edit: backend/app/api/v1x/payouts.py (+400 L)

FRONTEND (2 files):
  4. Create: src/lib/mentorEarningsApi.ts (150 L)
  5. Edit: src/pages/mentors/dashboard/payouts.tsx (+50 L updates)

CONFIG (1 file):
  6. Edit: .env.local (1 new variable)

TESTING: Postman/curl + browser testing

TOTAL CHANGES: ~6 files, ~830 new lines, 5-6 hours

✅ Everything else stays the same!
✅ No breaking changes!
✅ No refactoring needed!
```

---

## Timeline Breakdown

```
HOUR 1 (0:00 - 1:00):
├─ Create PaymentMethod model (30 min)
├─ Import in app/main.py (5 min)
└─ Test table creation (25 min)

HOUR 2-3 (1:00 - 3:00):
├─ Write 5 backend endpoints (90 min)
│  ├─ POST /mentors/payment-methods (25 min)
│  ├─ GET /mentors/payment-methods (15 min)
│  ├─ PUT /mentors/payment-methods/{id} (15 min)
│  ├─ DELETE /mentors/payment-methods/{id} (10 min)
│  └─ POST /mentors/payouts/request (25 min)
└─ Test each endpoint (30 min)

HOUR 4 (3:00 - 4:00):
├─ Create mentorEarningsApi.ts (30 min)
└─ Test all API functions (30 min)

HOUR 5 (4:00 - 5:00):
├─ Update payouts.tsx component (40 min)
└─ Test UI integration (20 min)

HOUR 6 (5:00 - 5:30):
├─ Add encryption (15 min)
├─ Security review (10 min)
└─ Final testing (5 min)

TOTAL: 5.5 hours (with 30 min buffer = 6 hours)
```

---

This is your complete mentor earnings platform! 🚀

