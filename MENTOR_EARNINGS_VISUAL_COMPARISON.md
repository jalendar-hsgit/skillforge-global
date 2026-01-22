# Mentor Earnings vs Booking - SIDE-BY-SIDE COMPARISON

## Quick Overview Table

| Feature | Booking System | Earnings System | Status |
|---------|----------------|-----------------|--------|
| **User Flow** | Student → Mentor Selection | Mentor → View Earnings | ✅ Partial |
| **Frontend Pages** | `/mentor-booking.tsx` (573 L) | `/mentors/dashboard/earnings.tsx` (545 L) | ✅ Both Exist |
| **Dashboard Page** | N/A | `/mentors/dashboard/index.tsx` (351 L) | ✅ Exists |
| **Payout Management** | N/A | `/mentors/dashboard/payouts.tsx` (445 L) | ✅ Exists |
| **Backend Router** | `mentors.py` (1267 L) | `payouts.py` (388 L) | ✅ Both Exist |
| **Portal Overview** | N/A | `mentor_portal.py` (481 L) | ✅ Exists |
| **Database Models** | MentorSession | MentorEarning, MentorPayout | ✅ Exist |
| **List Mentors** | ✅ Complete | N/A | ✅ Working |
| **Book Session** | ✅ Complete | N/A | ✅ Working |
| **Payment Processing** | ✅ Complete | ✅ Integrated | ✅ Working |
| **View Earnings** | N/A | ✅ Partial | ⚠️ 80% |
| **Request Payout** | N/A | ❌ Missing | ❌ 0% |
| **Manage Payment Methods** | N/A | ❌ Missing | ❌ 0% |
| **Admin Approval** | N/A | ❌ Missing | ❌ 0% |
| **Theme Consistency** | ✅ Yes | ✅ Yes | ✅ Good |
| **Security** | ✅ Good | ⚠️ Needs Work | ⚠️ Medium |

---

## Architecture Comparison

### STUDENT FLOW: Book a Mentor Session

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDENT EXPERIENCE                       │
└─────────────────────────────────────────────────────────────┘

1. FRONTEND: /mentor-booking.tsx (573 lines)
   ├─ State:
   │  ├─ mentors: MentorProfile[]           ← Loaded from API
   │  ├─ availableSlots: AvailabilitySlot[] ← Selected mentor
   │  ├─ booking: BookingState              ← Date/Time/Topic
   │  ├─ step: 'mentors' | 'slots' | 'payment' | 'confirmation'
   │  └─ processing: boolean
   │
   ├─ API Layer: mentorBookingApi.ts
   │  ├─ getMentors(limit)
   │  │  └─ GET /api/v1x/mentors → List
   │  ├─ searchMentors(expertise)
   │  │  └─ GET /api/v1x/mentors/search
   │  ├─ getAvailableSlots(mentorId, date)
   │  │  └─ GET /api/v1x/mentors/{id}/availability
   │  ├─ bookSession(sessionData)
   │  │  └─ POST /api/v1x/mentors/sessions/book
   │  └─ getMyBookings()
   │     └─ GET /api/v1x/mentors/sessions/my
   │
   ├─ Payment Layer: orderApi.ts
   │  ├─ createPaymentIntent(amount)
   │  │  └─ POST /api/v1x/payments/create-payment-intent
   │  ├─ confirmPayment(intentId, token)
   │  │  └─ POST /api/v1x/payments/confirm
   │  └─ Card Form:
   │     ├─ cardNumber (4242 4242 4242 4242)
   │     ├─ expiry (12/25)
   │     └─ cvc (123)
   │
   └─ Success → Redirect to /dashboard

2. BACKEND: API Layer
   ├─ GET /api/v1x/mentors
   │  ├─ Query: Mentor table with status=APPROVED
   │  ├─ Return: List of mentors with hourly_rate
   │  └─ Auth: Optional (public view)
   │
   ├─ GET /api/v1x/mentors/{id}/availability
   │  ├─ Query: MentorAvailability for date range
   │  ├─ Filter: Remove booked slots
   │  └─ Return: Available time slots
   │
   ├─ POST /api/v1x/mentors/sessions/book
   │  ├─ Validate:
   │  │  ├─ Mentor exists & status=APPROVED
   │  │  ├─ Student user exists
   │  │  └─ Slot is available
   │  ├─ Calculate: price = hourly_rate × (duration/60)
   │  ├─ Create: MentorSession record
   │  │  ├─ mentor_id = selected mentor
   │  │  ├─ student_id = current user
   │  │  ├─ scheduled_at = selected slot
   │  │  ├─ price = calculated amount
   │  │  └─ status = PENDING
   │  └─ Return: MentorSession with ID
   │
   ├─ POST /api/v1x/payments/create-payment-intent
   │  ├─ Input: { amount, currency, metadata }
   │  ├─ Call: stripe.PaymentIntent.create()
   │  ├─ Return: { client_secret, intent_id }
   │  └─ Store: PaymentIntent record
   │
   └─ POST /api/v1x/payments/confirm
      ├─ Input: { intent_id, payment_method_id }
      ├─ Call: stripe.PaymentIntent.confirm()
      ├─ If successful:
      │  ├─ Create: Order record
      │  ├─ Update: MentorSession.payment_status
      │  └─ Mark: Session as CONFIRMED
      └─ Return: Order details

3. DATABASE CHANGES
   ├─ MentorSession
   │  ├─ id: 123
   │  ├─ mentor_id: 5 (Sarah Chen)
   │  ├─ student_id: 10 (John Student)
   │  ├─ topic: "Python Advanced Topics"
   │  ├─ scheduled_at: 2026-01-25 14:00
   │  ├─ duration_minutes: 60
   │  ├─ price: 75.00 (from mentor's hourly_rate)
   │  ├─ status: CONFIRMED
   │  └─ payment_status: COMPLETED
   │
   └─ Payment (Stripe)
      ├─ amount: $75
      ├─ currency: USD
      ├─ student: john@example.com
      └─ status: succeeded

4. RESULT
   ✅ Session created with payment
   ✅ Mentor receives notification
   ✅ Student sees booking confirmation
   ✅ Session appears in mentor's upcoming list
```

---

### MENTOR FLOW: View Earnings & Request Payout

```
┌─────────────────────────────────────────────────────────────┐
│                   MENTOR EXPERIENCE                         │
└─────────────────────────────────────────────────────────────┘

1. FRONTEND: /mentors/dashboard/index.tsx (351 lines) - OVERVIEW
   ├─ Load: GET /api/v1x/mentor-portal/dashboard/overview
   ├─ Display:
   │  ├─ Stat Cards:
   │  │  ├─ Total Sessions: 47
   │  │  ├─ Month Sessions: 8
   │  │  ├─ Completed Sessions: 45
   │  │  ├─ Total Earnings: $3,375.00
   │  │  ├─ Month Earnings: $600.00
   │  │  └─ Average Rating: 4.8 ⭐
   │  ├─ Upcoming Sessions:
   │  │  ├─ Jan 23, 14:00 - Python Basics (45 min)
   │  │  └─ Jan 25, 10:00 - Web Dev (60 min)
   │  └─ Recent Reviews:
   │     ├─ ⭐⭐⭐⭐⭐ "Excellent mentor!"
   │     └─ ⭐⭐⭐⭐ "Very helpful, great pace"
   │
   └─ Color: Uses DashboardStatCard with "electric" color (aiElectric)

2. FRONTEND: /mentors/dashboard/earnings.tsx (545 lines) - DETAILS
   ├─ Tab 1: Overview
   │  ├─ Cards:
   │  │  ├─ Total Earnings: $3,375.00 (forgePurple)
   │  │  ├─ Sessions Count: 47 (green)
   │  │  └─ Avg Per Session: $71.80 (blue)
   │  └─ Monthly Breakdown:
   │     ├─ January 2026: $600.00 (8 sessions)
   │     ├─ December 2025: $550.00 (7 sessions)
   │     └─ November 2025: $480.00 (6 sessions)
   │
   ├─ Tab 2: Earnings List
   │  ├─ Load: GET /api/v1x/mentors/payouts/earnings?limit=100
   │  ├─ Shows:
   │  │  ├─ [ID] [Student] [Topic] [Gross] [Fee] [Net] [Earned] [Status]
   │  │  ├─ 123  John     Python  $75    $15   $60   Jan 20  Unpaid
   │  │  ├─ 124  Jane     WebDev  $85    $17   $68   Jan 18  Paid
   │  │  └─ 125  Bob      ML      $95    $19   $76   Jan 15  Paid
   │  └─ Filters: Date range, student, status
   │
   ├─ Tab 3: Payouts
   │  ├─ Load: GET /api/v1x/mentors/payouts (⚠️ MISSING)
   │  ├─ Shows:
   │  │  ├─ Status: Pending Payouts: $200.00
   │  │  ├─ Available Balance: $150.00
   │  │  ├─ Total Earned: $3,375.00
   │  │  └─ Last Payout: Dec 15, 2025 ($500)
   │  └─ Action: Request Payout Button
   │
   └─ Color: Uses techGray, success (for paid status)

3. FRONTEND: /mentors/dashboard/payouts.tsx (445 lines) - MANAGEMENT
   ├─ State:
   │  ├─ balance: { available, pending, total_earned, last_payout }
   │  ├─ payouts: Payout[]
   │  ├─ methods: PaymentMethod[]
   │  ├─ form: { amount, method_id }
   │  └─ submitting: boolean
   │
   ├─ Section 1: Balance Display
   │  ├─ Cards:
   │  │  ├─ Available Balance: $150.00 (Can withdraw NOW)
   │  │  ├─ Pending Payouts: $200.00 (Being processed)
   │  │  ├─ Total Earned: $3,375.00 (All time)
   │  │  └─ Last Payout: Dec 15, 2025
   │  └─ Colors: warning (pending), success (available), electric (total)
   │
   ├─ Section 2: Payment Methods (⚠️ IMPLEMENTATION NEEDED)
   │  ├─ List Current Methods:
   │  │  ├─ Chase Bank ••••1234 (Default)
   │  │  └─ Wells Fargo ••••5678
   │  ├─ Add New Method Button:
   │  │  ├─ Account Holder Name
   │  │  ├─ Account Number (encrypted in transmission)
   │  │  ├─ Routing Number (encrypted in transmission)
   │  │  ├─ Bank Name (auto-filled?)
   │  │  └─ Checkbox: Set as default
   │  └─ Calls: POST /api/v1x/mentors/payment-methods (⚠️ MISSING)
   │
   ├─ Section 3: Request Payout (⚠️ IMPLEMENTATION NEEDED)
   │  ├─ Form:
   │  │  ├─ Amount Input (validate ≤ available_balance)
   │  │  ├─ Payment Method Dropdown
   │  │  └─ Submit Button
   │  ├─ Validation:
   │  │  ├─ Amount > $0
   │  │  ├─ Amount ≤ Available Balance
   │  │  ├─ Amount ≥ $10 (minimum)
   │  │  ├─ Payment method selected
   │  │  └─ Confirmed
   │  └─ Calls: POST /api/v1x/mentors/payouts/request (⚠️ MISSING)
   │
   └─ Section 4: Payout History
      ├─ Shows:
      │  ├─ [ID] [Amount] [Status] [Requested] [Completed] [Actions]
      │  ├─ #P001 $500 COMPLETED Jan 15 Jan 18 [Download Receipt]
      │  ├─ #P002 $300 PROCESSING Jan 20 TBD [Cancel]
      │  └─ #P003 $200 PENDING Today - [View Details]
      └─ Filtering: Status, date range

4. BACKEND: API Layer
   ├─ GET /api/v1x/mentor-portal/dashboard/overview ✅
   │  ├─ Calculate:
   │  │  ├─ Total sessions = COUNT(MentorSession)
   │  │  ├─ Month sessions = COUNT(MentorSession > 1 month ago)
   │  │  ├─ Completed = COUNT(status=COMPLETED)
   │  │  ├─ Total earnings = SUM(price) where status=COMPLETED
   │  │  ├─ Month earnings = SUM(price) where completed & month
   │  │  ├─ Avg rating = AVG(MentorReview.rating)
   │  │  └─ Unique students = COUNT(DISTINCT student_id)
   │  └─ Return: { mentor, stats, upcoming_sessions, recent_reviews }
   │
   ├─ GET /api/v1x/mentors/payouts/summary ✅
   │  ├─ Calculate:
   │  │  ├─ Total earnings = SUM(MentorEarning.net_amount)
   │  │  ├─ Available = SUM(net_amount where is_paid_out=False)
   │  │  ├─ Pending = SUM(MentorPayout where status=PENDING|PROCESSING)
   │  │  └─ Completed = SUM(MentorPayout where status=COMPLETED)
   │  └─ Return: EarningsSummary
   │
   ├─ GET /api/v1x/mentors/payouts/earnings ✅
   │  ├─ Query: MentorEarning table
   │  ├─ Join: MentorSession (for student_name, topic)
   │  ├─ Return: List of earnings with pagination
   │  └─ Include: gross_amount, platform_fee, net_amount, status
   │
   ├─ POST /api/v1x/mentors/payouts/request ❌ MISSING
   │  ├─ Input: { amount, method_id }
   │  ├─ Validate:
   │  │  ├─ amount > 0 and ≤ available_balance
   │  │  ├─ mentor exists and status=APPROVED
   │  │  ├─ method exists and belongs to mentor
   │  │  └─ rate limiting (e.g., once per day)
   │  ├─ Create: MentorPayout record
   │  │  ├─ mentor_id = current_mentor
   │  │  ├─ amount = requested amount
   │  │  ├─ method = selected
   │  │  ├─ status = PENDING
   │  │  └─ requested_at = now
   │  ├─ Send: Email notification to mentor
   │  └─ Return: { payout_id, status, created_at }
   │
   ├─ GET /api/v1x/mentors/payment-methods ❌ MISSING
   │  ├─ Query: PaymentMethod table for current mentor
   │  ├─ Return: List WITHOUT showing full account numbers
   │  │  └─ Only: { id, bank_name, last4, is_default, verified }
   │  └─ Auth: Must be own mentor account
   │
   ├─ POST /api/v1x/mentors/payment-methods ❌ MISSING
   │  ├─ Input: { account_holder, account_number, routing_number }
   │  ├─ Validate:
   │  │  ├─ Account format valid
   │  │  ├─ Routing number format valid
   │  │  ├─ Account holder name provided
   │  │  └─ No duplicates
   │  ├─ Encrypt: account_number and routing_number
   │  ├─ Create: PaymentMethod record
   │  │  ├─ mentor_id = current
   │  │  ├─ account_number (encrypted)
   │  │  ├─ routing_number (encrypted)
   │  │  ├─ is_default = false (unless first)
   │  │  ├─ verified = false (needs email confirmation)
   │  │  └─ verification_code = generated
   │  ├─ Send: Verification email
   │  └─ Return: { id, last4, verified: false }
   │
   └─ PUT /api/v1x/mentors/payment-methods/{id} ❌ MISSING
      ├─ Input: { is_default: true }
      ├─ Validate: Method exists and belongs to mentor
      ├─ Update: Set is_default = true for this, false for others
      └─ Return: Updated method

5. DATABASE CHANGES
   ├─ MentorEarning (When session completes)
   │  ├─ id: 123
   │  ├─ mentor_id: 5 (Sarah Chen)
   │  ├─ session_id: 999 (from MentorSession)
   │  ├─ gross_amount: 75.00 (= MentorSession.price)
   │  ├─ platform_fee: 15.00 (20% of gross)
   │  ├─ net_amount: 60.00 (gross - fee)
   │  ├─ earned_at: 2026-01-21 15:00 (when session completed)
   │  ├─ is_paid_out: false (until payout processes)
   │  └─ payout_id: null (filled when included in payout)
   │
   ├─ PaymentMethod (NEW - When mentor adds bank account)
   │  ├─ id: 1
   │  ├─ mentor_id: 5
   │  ├─ type: "bank_transfer"
   │  ├─ account_holder: "Sarah Chen"
   │  ├─ account_number: "enc:xxxx1234" (encrypted)
   │  ├─ routing_number: "enc:123456789" (encrypted)
   │  ├─ bank_name: "Chase"
   │  ├─ is_default: true
   │  ├─ verified: false (until email confirmation)
   │  └─ verification_code: "abc123def456"
   │
   └─ MentorPayout (When mentor requests payout)
      ├─ id: 101
      ├─ mentor_id: 5
      ├─ amount: 150.00 (requested)
      ├─ method: "bank_transfer"
      ├─ status: "PENDING" → "PROCESSING" → "COMPLETED"
      ├─ requested_at: 2026-01-22 10:00
      ├─ processed_at: 2026-01-22 11:00
      ├─ completed_at: 2026-01-24 09:00
      └─ failure_reason: null (or error message if failed)

6. RESULT
   ✅ Mentor sees earnings breakdown
   ✅ Mentor can request payout
   ✅ Admin approves payout
   ✅ Money transferred to bank account
   ✅ Mentor receives payment notification
   ⚠️ Many parts still missing!
```

---

## Color Theme Reference

```
HEADER/TITLES:          forgePurple-500  (#6B3BFF)
ACCENT/HIGHLIGHTS:      aiElectric-500   (#00E5FF)
SECONDARY:              neuralBlue-500   (#1E9EFF)
BACKGROUNDS (Dark):     deepTech-900     (#0F172A)
BACKGROUNDS (Med):      deepTech-800     (#1E293B)
TEXT (Normal):          techGray-400     (#CED4DA)
TEXT (Light):           techGray-300     (#DEE2E6)
TEXT (Dark):            techGray-700     (#495057)
SUCCESS:                success          (#10B981)
WARNING:                warning          (#F59E0B)
ERROR:                  error            (#EF4444)

CURRENT USAGE:
├─ Dashboard Overview:  Electric color for stat cards
├─ Earnings Page:       Success for paid earnings
├─ Payouts Page:        Warning for pending, Success for available
└─ Forms:               Standard tailwind defaults
```

---

## Implementation Priority

### 🔴 CRITICAL (Do First - 3 hours)
1. Create PaymentMethod model
2. Implement POST /mentors/payouts/request endpoint
3. Implement GET/POST /mentors/payment-methods endpoints
4. Update frontend payouts.tsx to call new endpoints
5. Add security: Never expose full account numbers

### 🟡 HIGH (Do Next - 2 hours)
6. Add payout approval in admin panel
7. Add email notifications
8. Add payout receipt generation
9. Implement encryption for sensitive fields
10. Add rate limiting

### 🟢 MEDIUM (Do After - 1.5 hours)
11. Add charts to earnings page
12. Add earnings forecast
13. Add refund processing from mentor side
14. Add payment method verification
15. Add transaction export to CSV

### ⚪ LOW (Nice to Have - 1 hour)
16. Add earnings by category
17. Add student retention metrics
18. Add earnings trend prediction
19. Add mobile app (if applicable)
20. Add 2FA for payment method changes

---

## File Structure Reference

```
BACKEND:
backend/
├─ app/
│  ├─ modelsx/
│  │  ├─ mentor.py          (MentorSession ✅)
│  │  └─ payout.py          (MentorEarning ✅, MentorPayout ✅)
│  │  └─ payment_method.py  (PaymentMethod ❌ NEED TO CREATE)
│  │
│  └─ api/v1x/
│     ├─ mentors.py         (Booking endpoints ✅ 1267 L)
│     └─ payouts.py         (Earnings endpoints ✅ 388 L, Payout ❌)

FRONTEND:
src/
├─ pages/
│  ├─ mentor-booking.tsx    (Student booking flow ✅ 573 L)
│  └─ mentors/
│     ├─ dashboard/
│     │  ├─ index.tsx       (Overview ✅ 351 L)
│     │  ├─ earnings.tsx    (Details ✅ 545 L)
│     │  └─ payouts.tsx     (Management ⚠️ 445 L)
│     ├─ my-sessions.tsx    (Session list ✅)
│     └─ sessions/
│        └─ [id].tsx        (Session detail ✅)
│
└─ lib/
   ├─ mentorBookingApi.ts   (Booking layer ✅)
   ├─ orderApi.ts           (Payment layer ✅)
   └─ mentorEarningsApi.ts  (Earnings layer ❌ NEED TO CREATE)

STYLING:
├─ tailwind.config.ts       (Theme ✅ with all colors)
└─ src/components/
   ├─ DashboardLayout.tsx   (Container ✅)
   ├─ DashboardStatCard.tsx (KPI card ✅)
   └─ ... (many more ✅)
```

---

This analysis shows you have **80% of the infrastructure** already in place. You just need to:
1. Complete the missing backend endpoints
2. Create the PaymentMethod model
3. Update frontend to use the new endpoints
4. Add security measures

**Total estimated time: 5-6 hours from start to production-ready**

