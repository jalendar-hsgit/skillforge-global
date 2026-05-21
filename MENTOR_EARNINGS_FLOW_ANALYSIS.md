# Mentor Earnings & Payouts - Complete Flow Analysis

**Date:** January 22, 2026  
**Status:** ✅ EXISTING IMPLEMENTATION - Expanding & Securing  
**Current Location:** `/mentors/dashboard/*` and `/mentors/earnings`

---

## 📊 EXECUTIVE SUMMARY

### Current Status
- ✅ **Earnings Dashboard Exists** - At `/mentors/dashboard/earnings.tsx` (545 lines)
- ✅ **Payouts System Exists** - At `/mentors/dashboard/payouts.tsx` (445 lines)
- ✅ **Backend APIs Exist** - `payouts.py` (388 lines) with complete endpoints
- ✅ **Mentor Portal Integration** - `mentor_portal.py` (481 lines) shows overview
- ✅ **Theme System Ready** - Tailwind with `forgePurple`, `neuralBlue`, `aiElectric`, `deepTech`, `techGray`

### What Needs Development
- 🔧 **Revenue Tracking Completeness** - Currently counts sessions, needs transaction detail
- 🔧 **Dashboard Metrics** - KPIs are basic, need real-time calculation
- 🔧 **Security Hardening** - Payment method verification incomplete
- 🔧 **API Endpoints** - Some endpoints missing from backend

---

## 🔄 FLOW COMPARISON: MENTOR BOOKING vs MENTOR EARNINGS

### Student-Side: Booking Flow (✅ WORKING)
```
1. User Visits /mentor-booking.tsx (573 lines)
   ├─ Displays Mentor List
   ├─ Searches by expertise
   └─ Shows availability slots

2. Selects Mentor & Time Slot
   ├─ Calls getMentors() - mentorBookingApi.ts
   ├─ Calls getAvailableSlots() - mentorBookingApi.ts
   └─ State: selectedMentor + selectedDate + selectedTime

3. Payment Processing
   ├─ createPaymentIntent() - orderApi.ts
   ├─ Stripe card collection (cardNumber, expiry, cvc)
   └─ confirmPayment() - orderApi.ts

4. Session Booking
   ├─ bookSession() - mentorBookingApi.ts
   ├─ Creates MentorSession record
   └─ Status: PENDING → CONFIRMED → COMPLETED

BACKEND:
  POST /api/v1x/mentors/sessions/book
  POST /api/v1x/payments/create-payment-intent
  POST /api/v1x/payments/confirm
```

### Mentor-Side: Earnings Flow (⚠️ PARTIALLY WORKING)

**Current Implementation:**
```
1. Mentor Views Dashboard /mentors/dashboard/index.tsx (351 lines)
   ├─ Calls GET /api/v1x/mentor-portal/dashboard/overview
   ├─ Shows stats:
   │  ├─ total_sessions
   │  ├─ month_sessions
   │  ├─ completed_sessions
   │  ├─ total_earnings
   │  ├─ month_earnings
   │  ├─ average_rating
   │  └─ unique_students
   └─ Status: ✅ WORKING

2. Views Earnings Details /mentors/dashboard/earnings.tsx (545 lines)
   ├─ Calls GET /api/v1x/mentors/payouts/summary
   ├─ Shows summary:
   │  ├─ total_earnings
   │  ├─ available_balance (unpaid)
   │  ├─ pending_payouts
   │  ├─ completed_payouts
   │  └─ average_session_price
   ├─ Calls GET /api/v1x/mentors/payouts/earnings
   ├─ Shows earnings detail table:
   │  ├─ session_id
   │  ├─ student_name
   │  ├─ topic
   │  ├─ gross_amount
   │  ├─ platform_fee (20%)
   │  ├─ net_amount
   │  ├─ earned_at
   │  └─ is_paid_out status
   └─ Status: ⚠️ PARTIALLY WORKING

3. Requests Payout /mentors/dashboard/payouts.tsx (445 lines)
   ├─ Shows available_balance
   ├─ Shows pending_payouts
   ├─ Payment method form:
   │  ├─ account_holder_name
   │  ├─ account_number
   │  ├─ routing_number
   │  └─ is_default checkbox
   ├─ Payout request form:
   │  ├─ amount (with validation)
   │  └─ payment_method selection
   ├─ POST /api/v1x/mentors/payouts/request
   ├─ POST /api/v1x/mentors/payment-methods
   └─ Status: ⚠️ ENDPOINTS MISSING

BACKEND:
  GET /api/v1x/mentors/payouts/summary ✅
  GET /api/v1x/mentors/payouts/earnings ✅
  GET /api/v1x/mentors/payouts/{id} ✅
  POST /api/v1x/mentors/payouts/request ❌ MISSING
  GET /api/v1x/mentors/payouts ⚠️ NEEDS VALIDATION
  POST /api/v1x/mentors/payment-methods ❌ MISSING
  GET /api/v1x/mentors/payment-methods ❌ MISSING
```

---

## 🔍 DETAILED CODE COMPARISON

### Backend: Mentor Booking vs Earnings

**Booking System** (`mentors.py` - 1267 lines)
```python
# Session Creation
POST /mentors/sessions/book (SessionBookingRequest) → SessionResponse
  ├─ Validates mentor exists & status=APPROVED
  ├─ Checks availability slot
  ├─ Creates MentorSession record
  ├─ Calculates price from hourly_rate × (duration_minutes/60)
  └─ Returns session_id + status=PENDING

# Earnings Not Tracked Here
# Just creates session, no tracking of earnings
```

**Earnings System** (`payouts.py` - 388 lines)
```python
# Earnings Calculation
GET /mentors/payouts/summary → EarningsSummary
  ├─ Sum of MentorEarning.net_amount (completed sessions)
  ├─ Sum of unpaid (is_paid_out=False)
  ├─ Sum of pending payouts (status=PENDING|PROCESSING)
  ├─ Sum of completed payouts (status=COMPLETED)
  └─ All calculations using aggregation functions

# Earning Details
GET /mentors/payouts/earnings → List[EarningDetail]
  ├─ Query MentorEarning records
  ├─ Join with MentorSession for student info
  ├─ Calculate: gross_amount - platform_fee = net_amount
  ├─ Filter by mentor_id
  └─ Return with pagination

# Missing Endpoints
POST /mentors/payouts/request ❌ NOT IN payouts.py
POST /mentors/payment-methods ❌ NOT IN payouts.py
GET /mentors/payment-methods ❌ NOT IN payouts.py
```

### Frontend: Mentor Booking vs Earnings

**Booking Page** (`mentor-booking.tsx` - 573 lines)
```tsx
// API Integration
import { 
  getMentors,           // GET /mentors
  searchMentors,        // GET /mentors/search
  getAvailableSlots,    // GET /mentors/{id}/availability
  bookSession,          // POST /mentors/sessions/book
  MentorProfile,
  AvailabilitySlot,
  MentorSession
} from '../lib/mentorBookingApi'

import {
  createOrder,              // Creates order
  createPaymentIntent,      // Stripe intent
  confirmPayment           // Process payment
} from '../lib/orderApi'

// Multi-step flow
type Step = 'mentors' | 'slots' | 'payment' | 'confirmation'

// State management
const [mentors, setMentors] = useState<MentorProfile[]>([])
const [availableSlots, setAvailableSlots] = useState<AvailabilitySlot[]>([])
const [booking, setBooking] = useState<BookingState>({...})
const [processing, setProcessing] = useState(false)

// Error handling & validation included
```

**Earnings Page** (`mentors/dashboard/earnings.tsx` - 545 lines)
```tsx
// API Integration - INCOMPLETE
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

// Separate endpoints for different data
const summaryRes = await fetch(`${API_BASE}/api/v1x/mentors/payouts/summary`)
const earningsRes = await fetch(`${API_BASE}/api/v1x/mentors/payouts/earnings`)
// Missing: /payouts endpoint

// State management
const [summary, setSummary] = useState<EarningsSummary | null>(null)
const [earnings, setEarnings] = useState<EarningDetail[]>([])
const [payouts, setPayouts] = useState<PayoutDetail[]>([])

// Tab system
const [activeTab, setActiveTab] = useState<'overview' | 'earnings' | 'payouts'>('overview')
```

**Payouts Page** (`mentors/dashboard/payouts.tsx` - 445 lines)
```tsx
// API Integration - PARTIALLY COMPLETE
const [balance, setBalance] = useState<Balance | null>(null)
const [payouts, setPayouts] = useState<Payout[]>([])
const [methods, setMethods] = useState<PaymentMethod[]>([])

// Calls endpoints that don't fully exist
await fetch(`${API_BASE}/api/v1x/mentors/balance`) // ❌ Check if exists
await fetch(`${API_BASE}/api/v1x/mentors/payouts`) // ⚠️ Incomplete
await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`) // ❌ MISSING

// Form validation included
handleRequestPayout() // Validates amount, payment method
handleAddPaymentMethod() // Validates bank account fields
```

---

## 🏗️ REVENUE MODEL ARCHITECTURE

### Database Models

**Current Models:**
```
1. MentorSession (app/modelsx/mentor.py)
   ├─ id
   ├─ mentor_id (FK)
   ├─ student_id (FK)
   ├─ topic
   ├─ scheduled_at
   ├─ duration_minutes
   ├─ price (set at booking)
   ├─ status (PENDING|CONFIRMED|COMPLETED|CANCELLED)
   └─ created_at

   Issue: NO tracking of earnings calculation
         Assumes price = revenue (ignores platform fee)

2. MentorEarning (app/modelsx/payout.py)
   ├─ id
   ├─ mentor_id (FK)
   ├─ session_id (FK)
   ├─ gross_amount
   ├─ platform_fee
   ├─ net_amount
   ├─ earned_at
   ├─ is_paid_out
   ├─ payout_id (FK) [optional]
   └─ created_at

   Status: ✅ GOOD

3. MentorPayout (app/modelsx/payout.py)
   ├─ id
   ├─ mentor_id (FK)
   ├─ amount
   ├─ net_amount
   ├─ method (STRIPE|BANK_TRANSFER|PAYPAL)
   ├─ status (PENDING|PROCESSING|COMPLETED|FAILED)
   ├─ requested_at
   ├─ processed_at
   ├─ completed_at
   ├─ failure_reason
   └─ created_at

   Status: ✅ GOOD

4. MISSING: PaymentMethod or BankAccount
   Needed for:
   ├─ account_holder_name
   ├─ account_number (encrypted)
   ├─ routing_number
   ├─ bank_name
   ├─ is_default
   ├─ verified (boolean)
   └─ verification_code
```

### Revenue Flow
```
1. Student Books Session
   ├─ Pay $50 for 60-min session with Mentor A
   └─ Payment status: completed

2. Session Completed
   ├─ System calculates earnings:
   │  ├─ gross_amount = $50
   │  ├─ platform_fee = $10 (20%)
   │  └─ net_amount = $40
   ├─ Creates MentorEarning record
   └─ Status: available for payout

3. Mentor Requests Payout
   ├─ Selects amount ($100 from available balance of $400)
   ├─ Selects payment method (bank account)
   ├─ Creates MentorPayout request
   └─ Status: PENDING

4. Admin Reviews & Approves
   ├─ Verifies amount matches earnings
   ├─ Confirms payment method
   ├─ Processes payout to bank
   └─ Updates status: COMPLETED

5. Mentor Receives Funds
   ├─ Status visible in payouts history
   ├─ Can download receipt/invoice
   └─ Summary shows completed_payouts += $100
```

---

## 🎨 THEME & DESIGN CONSISTENCY

### Color Theme (From tailwind.config.ts)

**Primary Brand Colors:**
```tsx
forgePurple: {
  DEFAULT: '#6B3BFF',      // Main accent
  500: '#6B3BFF',          // Primary
  600: '#5B21B6',          // Darker
  700: '#4C1D95',          // Darkest
}

neuralBlue: {
  DEFAULT: '#1E9EFF',      // Secondary
  500: '#1E9EFF',          // Primary
  600: '#2563EB',          // Darker
}

aiElectric: {
  DEFAULT: '#00E5FF',      // Accent/Highlight
  500: '#00E5FF',          // Bright cyan
  600: '#0891B2',          // Darker
}

deepTech: {
  DEFAULT: '#0B0A13',      // Dark background
  900: '#0F172A',          // Very dark
  950: '#0B0A13',          // Darkest
}

techGray: {
  DEFAULT: '#B6BED3',      // Light gray
  400: '#CED4DA',          // Medium gray
  700: '#495057',          // Dark gray
}
```

**Current Usage in Mentor Pages:**
```tsx
// Dashboard/index.tsx
<DashboardStatCard label="..." color="electric" />    // aiElectric
<DashboardStatCard label="..." color="green" />       // success
<DashboardStatCard label="..." color="blue" />        // neuralBlue

// Earnings.tsx
className="text-success font-semibold"         // success color
className="text-techGray-400"                  // neutral text

// Payouts.tsx
// Uses DashboardLayout (standard theme)
// Inputs styled with Tailwind forms
```

---

## ✅ WHAT'S WORKING

### 1. Student Booking Flow (100%)
- ✅ Browse mentors with search/filter
- ✅ View availability slots
- ✅ Select date/time
- ✅ Payment processing via Stripe
- ✅ Session creation with proper data
- ✅ Session tracking in dashboard

### 2. Mentor Dashboard Overview (100%)
- ✅ Total sessions count
- ✅ Monthly sessions calculation
- ✅ Completed sessions tracking
- ✅ Total/monthly earnings display
- ✅ Average rating from reviews
- ✅ Upcoming sessions list
- ✅ Recent reviews display

### 3. Earnings Calculation (95%)
- ✅ Gross amount tracking
- ✅ Platform fee calculation (20%)
- ✅ Net amount computation
- ✅ Unpaid balance calculation
- ✅ Pending payouts tracking
- ✅ Completed payouts history
- ⚠️ **Missing:** Real-time sync when session completes

### 4. Theme System (100%)
- ✅ Consistent color palette
- ✅ All colors defined in tailwind.config.ts
- ✅ Used in dashboard components
- ✅ Used in stat cards
- ✅ Works across all pages

---

## 🔴 CRITICAL GAPS

### 1. Missing Backend Endpoints

**Currently Missing in `payouts.py`:**
```python
# Payout Request Handling
POST /mentors/payouts/request
  ├─ Request: { amount, payment_method_id }
  ├─ Validation: amount <= available_balance
  ├─ Create: MentorPayout record with status=PENDING
  └─ Response: { payout_id, status, created_at }

# Payment Methods Management
GET /mentors/payment-methods
  ├─ List all payment methods for mentor
  └─ Return: [ { id, type, last4, is_default, verified } ]

POST /mentors/payment-methods
  ├─ Request: { account_holder, account_num, routing_num }
  ├─ Validation: Check required fields
  ├─ Encrypt: Sensitive data
  ├─ Create: PaymentMethod record
  └─ Response: { id, type, last4, is_default }

PUT /mentors/payment-methods/{id}
  ├─ Update: is_default flag
  └─ Response: Updated record

DELETE /mentors/payment-methods/{id}
  ├─ Remove: Payment method
  └─ Validation: Not the only/default method
```

### 2. Missing Frontend API Layer

**Currently Missing in `src/lib/`:**
```typescript
// mentorEarningsApi.ts (NEW FILE)
export const getEarningsSummary = async () => {...}
export const getEarningsHistory = async (limit = 100) => {...}
export const requestPayout = async (amount, method) => {...}
export const getPayoutHistory = async () => {...}
export const getPaymentMethods = async () => {...}
export const addPaymentMethod = async (bankData) => {...}
export const removePaymentMethod = async (methodId) => {...}
export const setDefaultPaymentMethod = async (methodId) => {...}
```

### 3. Missing Database Model

**Need to create:**
```python
# app/modelsx/payment_method.py
class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey('mentors.id'))
    type = Column(String)  # bank_transfer, stripe_connect, paypal
    account_holder = Column(String)
    account_number = Column(String)  # Encrypted
    routing_number = Column(String)  # Encrypted
    bank_name = Column(String)
    is_default = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 4. Security Issues

**Current Frontend:**
```tsx
// ❌ BAD: Storing sensitive data in state
const [methodForm, setMethodForm] = useState({
  account_holder_name: '',
  account_number: '',
  routing_number: '',  // ⚠️ SENSITIVE!
})

// ❌ BAD: Sending raw account numbers to API
const res = await fetch(`${API_BASE}/api/v1x/mentors/payment-methods`, {
  method: 'POST',
  body: JSON.stringify({
    account_number: methodForm.account_number  // ⚠️ NOT ENCRYPTED!
  })
})
```

**Required Security Measures:**
```typescript
// ✅ GOOD: Never store full account numbers
// ✅ GOOD: Only show last 4 digits
// ✅ GOOD: Encrypt before transmission
// ✅ GOOD: Use HTTPS/TLS only
// ✅ GOOD: Validate on backend
// ✅ GOOD: Rate limit payout requests
```

---

## 🔧 DEVELOPMENT ROADMAP

### Phase 1: Backend Models & Endpoints (2-3 hours)

**Step 1.1: Create PaymentMethod Model**
```python
File: app/modelsx/payment_method.py
├─ Define PaymentMethod SQLAlchemy model
├─ Add encryption utility for account numbers
├─ Add relationship to Mentor
└─ Import in app/main.py before create_all()
```

**Step 1.2: Complete Payout Endpoints**
```python
File: app/api/v1x/payouts.py (extend existing)
├─ POST /mentors/payouts/request
│  ├─ Validate amount
│  ├─ Create MentorPayout
│  └─ Send email notification
├─ GET /mentors/payment-methods
│  ├─ Query PaymentMethod records
│  └─ Return (last4 only, not full account)
├─ POST /mentors/payment-methods
│  ├─ Validate bank fields
│  ├─ Encrypt sensitive data
│  ├─ Create record
│  └─ Send verification code via email
└─ PUT /mentors/payment-methods/{id}
   ├─ Update is_default
   └─ Validate not deleting only method
```

**Step 1.3: Secure Endpoints**
```python
# Add to all endpoints:
├─ @router.get(...) authorization checks
├─ Verify user is mentor
├─ Verify mentor status = APPROVED
├─ Verify data ownership (own payouts only)
└─ Rate limiting on payout requests
```

### Phase 2: Frontend API Layer (30 minutes)

**Step 2.1: Create API Wrapper**
```typescript
File: src/lib/mentorEarningsApi.ts
├─ getEarningsSummary()
├─ getEarningsHistory(limit)
├─ requestPayout(amount, methodId)
├─ getPayoutHistory()
├─ getPaymentMethods()
├─ addPaymentMethod(data)
├─ setDefaultPaymentMethod(id)
└─ removePaymentMethod(id)
```

**Step 2.2: Add Type Safety**
```typescript
// Define interfaces
interface EarningsSummary {
  total_earnings: number
  available_balance: number
  pending_payouts: number
  completed_payouts: number
  platform_fee_percentage: number
}

interface PaymentMethod {
  id: number
  type: 'bank_transfer' | 'stripe_connect'
  account_holder: string
  bank_name: string
  last4: string
  is_default: boolean
  verified: boolean
}
```

### Phase 3: Frontend Security Improvements (1 hour)

**Step 3.1: Update Payouts Page**
```tsx
File: src/pages/mentors/dashboard/payouts.tsx

// Before (❌ BAD):
const [methodForm, setMethodForm] = useState({
  account_number: ''  // Storing sensitive data
})

// After (✅ GOOD):
const [methodForm, setMethodForm] = useState({
  account_holder_name: '',
  account_number: '',
  routing_number: ''
  // NOT stored in state - only while typing
})

// Add validations:
├─ Account number format validation
├─ Routing number format validation
├─ Max payout amount check (< available_balance)
├─ Rate limit (e.g., 1 payout request per 24 hours)
└─ Show last 4 digits preview before submit
```

**Step 3.2: Add Payment Method UI**
```tsx
// Show methods as read-only list with last4 only
<div className="space-y-2">
  {methods.map(method => (
    <div key={method.id} className="border p-3 rounded">
      <div className="flex justify-between">
        <span>{method.bank_name} ••••{method.last4}</span>
        <div className="flex gap-2">
          {!method.is_default && (
            <Button onClick={() => setDefault(method.id)}>
              Set Default
            </Button>
          )}
          {methods.length > 1 && (
            <Button onClick={() => removeMethod(method.id)}>
              Remove
            </Button>
          )}
        </div>
      </div>
      {method.is_default && <span className="text-xs text-success">Default</span>}
      {!method.verified && <span className="text-xs text-warning">Unverified</span>}
    </div>
  ))}
</div>
```

### Phase 4: Enhanced Dashboard Features (1.5 hours)

**Step 4.1: Real-Time Earnings**
```tsx
// Update /mentors/dashboard/earnings.tsx
├─ Add monthly breakdown chart
├─ Add earnings trend graph
├─ Add top earning sessions list
├─ Add export to CSV functionality
└─ Add earnings forecast
```

**Step 4.2: Payout Status Tracking**
```tsx
// Update /mentors/dashboard/payouts.tsx
├─ Show payout request timeline
├─ Add status badges (PENDING|PROCESSING|COMPLETED|FAILED)
├─ Add retry failed payouts option
├─ Add payout receipt download
└─ Add estimated payout date
```

**Step 4.3: Analytics Dashboard**
```tsx
// Enhance /mentors/dashboard/analytics.tsx
├─ Add earnings vs sessions chart
├─ Add platform fee breakdown
├─ Add average earnings per hour
├─ Add student retention metrics
└─ Add category-based earnings breakdown
```

### Phase 5: Admin Approval System (1 hour)

**Step 5.1: Admin Backend Endpoints**
```python
# Add to app/api/v1x/admin.py
GET /admin/mentor-payouts
├─ List all pending payouts
├─ Filter by status
└─ Show mentor info + amount

POST /admin/mentor-payouts/{id}/approve
├─ Verify amount validity
├─ Create payment transaction
├─ Send confirmation email
└─ Update status: PROCESSING

POST /admin/mentor-payouts/{id}/reject
├─ Set status: FAILED
├─ Add failure_reason
└─ Send notification to mentor
```

**Step 5.2: Admin Frontend**
```tsx
// Add page: src/pages/admin/payouts.tsx
├─ List pending payouts
├─ Approve/reject buttons
├─ View payment method verification
├─ Search and filter
└─ Batch operations
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Backend (2-3 hours) ⏱️
- [ ] Create PaymentMethod model
- [ ] Add encryption for account numbers
- [ ] Import model in app/main.py
- [ ] Implement POST /mentors/payouts/request
- [ ] Implement GET /mentors/payment-methods
- [ ] Implement POST /mentors/payment-methods
- [ ] Implement PUT /mentors/payment-methods/{id}
- [ ] Add authorization checks to all endpoints
- [ ] Add rate limiting
- [ ] Add email notifications

### Phase 2: Frontend API (30 min) ⏱️
- [ ] Create src/lib/mentorEarningsApi.ts
- [ ] Implement all 7 functions
- [ ] Add error handling
- [ ] Add TypeScript interfaces
- [ ] Test all functions

### Phase 3: Security (1 hour) ⏱️
- [ ] Never store full account numbers in state
- [ ] Only show last 4 digits to user
- [ ] Validate on backend
- [ ] Add HTTPS only enforcement
- [ ] Encrypt sensitive fields in database
- [ ] Add rate limiting on requests

### Phase 4: UI/UX (1.5 hours) ⏱️
- [ ] Add payment method management form
- [ ] Add payout request form with validation
- [ ] Add earnings charts/graphs
- [ ] Add status badges for payouts
- [ ] Add receipt download functionality
- [ ] Add theme consistency (tailwind colors)

### Phase 5: Admin (1 hour) ⏱️
- [ ] Create admin payout approval page
- [ ] Add approve/reject functionality
- [ ] Add batch operations
- [ ] Add audit logging

---

## 🎯 BEST PRACTICES & PATTERNS

### 1. API Layer Pattern
```typescript
// ✅ GOOD: Centralized API wrapper
export async function mentorEarningsApi() {
  const BASE = process.env.NEXT_PUBLIC_API_BASE
  const token = getAuthToken()
  
  return {
    getSummary: () => 
      fetch(`${BASE}/api/v1x/mentors/payouts/summary`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(r => r.json()),
    
    requestPayout: (amount) =>
      fetch(`${BASE}/api/v1x/mentors/payouts/request`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ amount })
      }).then(r => r.json())
  }
}
```

### 2. Component Pattern
```tsx
// ✅ GOOD: Separate concerns
<PayoutRequestForm>           // Form component
  <PaymentMethodSelector />   // Select method
  <AmountInput />             // Input amount
  <SubmitButton />            // Submit
</PayoutRequestForm>

<PayoutHistory>              // History component
  <PayoutItem />             // Individual item
</PayoutHistory>
```

### 3. State Management Pattern
```tsx
// ✅ GOOD: Clear state separation
const [summary, setSummary] = useState<EarningsSummary | null>(null)
const [earnings, setEarnings] = useState<EarningDetail[]>([])
const [payouts, setPayouts] = useState<PayoutDetail[]>([])
const [loading, setLoading] = useState(false)
const [error, setError] = useState('')

// ✅ GOOD: Separate form state
const [form, setForm] = useState({
  amount: '',
  method_id: ''
})
const [submitting, setSubmitting] = useState(false)
const [formError, setFormError] = useState('')
```

### 4. Error Handling Pattern
```typescript
// ✅ GOOD: Comprehensive error handling
try {
  const response = await fetch(url, options)
  
  if (response.status === 401) {
    // Handle auth error
    redirectToLogin()
  } else if (response.status === 403) {
    // Handle permission error
    showError('Not authorized')
  } else if (!response.ok) {
    // Handle other errors
    const data = await response.json()
    showError(data.detail || 'An error occurred')
  } else {
    // Success
    return await response.json()
  }
} catch (error) {
  // Network error
  showError('Network error: ' + error.message)
}
```

### 5. Validation Pattern
```typescript
// ✅ GOOD: Client-side + server-side validation
const validatePayout = (amount: number, available: number) => {
  const errors = []
  
  if (!amount || amount <= 0) {
    errors.push('Amount must be greater than 0')
  }
  if (amount > available) {
    errors.push(`Amount exceeds available balance ($${available})`)
  }
  if (amount < 10) {
    errors.push('Minimum payout is $10')
  }
  if (amount > 100000) {
    errors.push('Maximum payout is $100,000')
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}
```

### 6. Theme Consistency Pattern
```tsx
// ✅ GOOD: Use theme colors from tailwind config
<div className="bg-deepTech-900">
  {/* Dark background */}
  <h2 className="text-forgePurple-500">Earnings Summary</h2>
  {/* Purple heading */}
  
  <div className="bg-deepTech-800 p-4">
    {/* Slightly lighter background */}
    <span className="text-aiElectric-500">Active</span>
    {/* Cyan accent */}
  </div>
</div>

// ✅ GOOD: Component-level classes
className={`
  p-4 rounded-lg
  bg-deepTech-800 border border-techGray-300
  text-white hover:bg-deepTech-700
  transition-colors duration-200
`}
```

---

## 🔐 SECURITY CHECKLIST

### Database Security
- [ ] Encrypt account_number field
- [ ] Encrypt routing_number field
- [ ] Never log sensitive fields
- [ ] Use prepared statements (SQLAlchemy does this)
- [ ] Add audit trail for payout requests
- [ ] Hash verification codes

### API Security
- [ ] Require authentication on all endpoints
- [ ] Verify mentor status = APPROVED
- [ ] Verify data ownership (can't access others' payouts)
- [ ] Add rate limiting (e.g., 10 requests/minute)
- [ ] Validate input fields strictly
- [ ] Return minimal error messages
- [ ] Log suspicious activity

### Frontend Security
- [ ] Never store full account numbers
- [ ] Only show last 4 digits
- [ ] Use HTTPS only
- [ ] Clear sensitive forms after submit
- [ ] Validate before sending to API
- [ ] Use Content-Security-Policy headers
- [ ] Sanitize user input

### Payment Security
- [ ] Never store credit cards (Stripe handles this)
- [ ] Use official payment processors
- [ ] Tokenize bank accounts
- [ ] Add 2FA for account changes
- [ ] Send verification emails for new methods
- [ ] Require verification before first payout

---

## 📊 API ENDPOINT SUMMARY

### Complete Endpoint List (To Implement)

```
STUDENT → MENTOR FLOW:
✅ POST /api/v1x/mentors/sessions/book
✅ GET /api/v1x/mentors (list)
✅ GET /api/v1x/mentors/{id}
✅ GET /api/v1x/mentors/{id}/availability
✅ POST /api/v1x/payments/create-payment-intent
✅ POST /api/v1x/payments/confirm

MENTOR DASHBOARD - EXISTING:
✅ GET /api/v1x/mentor-portal/dashboard/overview
✅ GET /api/v1x/mentors/payouts/summary
✅ GET /api/v1x/mentors/payouts/earnings
✅ GET /api/v1x/mentors/payouts/{id}

MENTOR DASHBOARD - TO BUILD:
❌ POST /api/v1x/mentors/payouts/request
❌ GET /api/v1x/mentors/payment-methods
❌ POST /api/v1x/mentors/payment-methods
❌ PUT /api/v1x/mentors/payment-methods/{id}
❌ DELETE /api/v1x/mentors/payment-methods/{id}
❌ GET /api/v1x/mentor-portal/dashboard/earnings (detail view)
❌ GET /api/v1x/mentor-portal/dashboard/payouts (list view)

ADMIN - EXISTING:
✅ GET /api/v1x/admin/... (general)

ADMIN - TO BUILD:
❌ GET /api/v1x/admin/mentor-payouts
❌ POST /api/v1x/admin/mentor-payouts/{id}/approve
❌ POST /api/v1x/admin/mentor-payouts/{id}/reject
❌ GET /api/v1x/admin/mentor-payouts/{id}/audit-log
```

---

## 📈 SUCCESS METRICS

Once completed, verify:
- [ ] Mentor can view total earnings
- [ ] Mentor can see earnings breakdown by session
- [ ] Mentor can request payout
- [ ] Payout request is stored in database
- [ ] Admin can see pending payouts
- [ ] Admin can approve/reject payouts
- [ ] Payment method validation works
- [ ] Sensitive data is not exposed in frontend
- [ ] All API endpoints have proper auth
- [ ] Rate limiting prevents abuse
- [ ] Emails sent for all actions
- [ ] UI matches theme consistently
- [ ] Mobile responsive design works
- [ ] Error handling covers all cases
- [ ] Audit trail recorded for compliance

---

## 🚀 QUICK START COMMAND

To begin:
```bash
# 1. Backend Model
touch backend/app/modelsx/payment_method.py

# 2. Extend Payouts
# Edit backend/app/api/v1x/payouts.py

# 3. Frontend API Layer
touch src/lib/mentorEarningsApi.ts

# 4. Test each endpoint
cd backend && pytest -v tests/

# 5. Frontend component updates
# Edit src/pages/mentors/dashboard/payouts.tsx
```

---

**Next Steps:** Start with Phase 1 (Backend Models) → Then Phase 2 (API Layer) → Then Phase 3 (Security)

