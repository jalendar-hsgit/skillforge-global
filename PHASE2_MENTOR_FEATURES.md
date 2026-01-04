# PHASE 2: MENTOR FEATURES - IMPLEMENTATION GUIDE

**Start Date**: After Phase 1 (Early Week 2)  
**Duration**: 10 hours  
**Goal**: Complete mentor system features (verification, payments, ratings)

---

## 📋 SCOPE: 3 MAJOR FEATURES

### 1. Mentor Verification System (3-4 hours)
**What**: Approval workflow for mentors

**Backend Status**: ⏳ 60% done
**Frontend Status**: ❌ 0% done
**Files to Create/Update**:
- `backend/app/api/v1x/mentors.py` - Add verification endpoints
- `src/pages/mentors/verify.tsx` - NEW: Verification dashboard

**Tasks**:
```
BACKEND (1-2 hours):
- [ ] GET /api/v1x/mentors/verification-status
- [ ] GET /api/v1x/mentors/documents (proof of expertise)
- [ ] POST /api/v1x/mentors/documents/upload
- [ ] Admin: GET /api/v1x/admin/mentor-verifications
- [ ] Admin: PATCH /api/v1x/admin/mentor-verifications/{id}/approve
- [ ] Admin: PATCH /api/v1x/admin/mentor-verifications/{id}/reject

FRONTEND (2-3 hours):
- [ ] Create verification status page
- [ ] Document upload UI
- [ ] Verification timeline display
- [ ] Admin approval queue page
- [ ] Success/rejection notifications
```

**Expected Outcome**:
- Mentors can upload verification documents
- Admins can approve/reject with feedback
- Notifications sent on status change

---

### 2. Payment Processing (4-5 hours)
**What**: Stripe integration for mentor earnings

**Backend Status**: ❌ Stub only
**Frontend Status**: ❌ 0% done
**Dependencies**: Stripe account setup

**Files to Create/Update**:
- `backend/app/api/v1x/payments.py` - COMPLETE: Payment endpoints
- `backend/app/services/stripe_service.py` - NEW: Stripe integration
- `src/pages/mentors/payments.tsx` - NEW: Mentor payment page
- `src/pages/admin/payments.tsx` - NEW: Admin payment dashboard

**Tasks**:
```
BACKEND (2-3 hours):
- [ ] Setup Stripe SDK
- [ ] Implement Stripe Connect account creation
- [ ] Payment intent creation endpoint
- [ ] Webhook handler for payment confirmation
- [ ] Payout scheduling endpoint
- [ ] Transaction history endpoint

FRONTEND (2-3 hours):
- [ ] Create Stripe checkout form
- [ ] Payment method management
- [ ] Payout request form
- [ ] Transaction history UI
- [ ] Success/error messages
- [ ] Mobile-friendly payment flow
```

**Expected Outcome**:
- Mentors can add payment methods
- Students can pay for sessions
- Mentors receive earnings

---

### 3. Session Rating & Reviews (2-3 hours)
**What**: Students rate mentors after sessions

**Backend Status**: ✅ 80% done
**Frontend Status**: ⏳ 50% done
**Files**: Mostly complete, just needs UI polish

**Tasks**:
```
FRONTEND (2-3 hours):
- [ ] Rating modal on session end
- [ ] 5-star rating component
- [ ] Comment/feedback textarea
- [ ] Submit button + validation
- [ ] Success notification
- [ ] Prevent duplicate ratings
- [ ] Display mentor's average rating

BACKEND (minor):
- [ ] Rate limit per student per session
- [ ] Prevent rating if session not complete
- [ ] Calculate mentor rating average
```

**Expected Outcome**:
- Students can rate mentors 1-5 stars
- Mentors see their ratings/reviews
- Rating affects mentor visibility

---

## 🛠️ IMPLEMENTATION STEPS

### Day 1 (4 hours): Mentor Verification
```
Hour 1: Backend verification endpoints
  - Create GET endpoints for status
  - Create POST for document upload
  
Hour 2: Admin verification endpoints
  - GET all pending verifications
  - PATCH approve/reject with reason
  
Hour 3: Frontend verification page
  - Document upload form
  - Status display
  - Timeline view
  
Hour 4: Testing & polish
  - Test upload flow
  - Test admin approval
  - Error handling
```

### Day 2 (4 hours): Payment Processing
```
Hour 1: Stripe setup
  - API keys configuration
  - Webhook configuration
  - Test mode setup
  
Hour 2: Backend payment endpoints
  - Payment intent creation
  - Payout scheduling
  - Transaction history
  
Hour 3: Frontend checkout UI
  - Stripe card element
  - Form validation
  - Success/error handling
  
Hour 4: Payment method management
  - Add/remove payment methods
  - Set default method
  - List saved cards
```

### Day 3 (2 hours): Session Ratings
```
Hour 1: Rating modal UI
  - 5-star component
  - Comment field
  - Submit flow
  
Hour 2: Display & validation
  - Show avg rating on profile
  - Prevent duplicate ratings
  - List of recent reviews
```

---

## 📦 FILE STRUCTURE

```
NEW FILES:
├─ src/pages/mentors/
│  ├─ verify.tsx (Verification status & upload)
│  └─ payments.tsx (Payment method management)
│
├─ src/components/
│  ├─ VerificationUpload.tsx (Document upload)
│  ├─ PaymentForm.tsx (Stripe form)
│  ├─ RatingModal.tsx (Rate session)
│  └─ StarRating.tsx (5-star display)
│
└─ backend/app/services/
   └─ stripe_service.py (Stripe integration)

MODIFIED FILES:
├─ backend/app/api/v1x/mentors.py
├─ backend/app/api/v1x/payments.py
├─ src/pages/mentors/dashboard/sessions.tsx
└─ src/pages/mentors/profile.tsx
```

---

## 🔌 API ENDPOINTS TO CREATE

### Verification
```
GET    /api/v1x/mentors/verification-status
POST   /api/v1x/mentors/documents/upload
GET    /api/v1x/mentors/documents
DELETE /api/v1x/mentors/documents/{id}

ADMIN:
GET    /api/v1x/admin/mentor-verifications
PATCH  /api/v1x/admin/mentor-verifications/{id}/approve
PATCH  /api/v1x/admin/mentor-verifications/{id}/reject
```

### Payments
```
POST   /api/v1x/mentors/payment-methods
GET    /api/v1x/mentors/payment-methods
DELETE /api/v1x/mentors/payment-methods/{id}
PATCH  /api/v1x/mentors/payment-methods/{id}/default

POST   /api/v1x/mentors/payouts/request
GET    /api/v1x/mentors/payouts
GET    /api/v1x/mentors/transactions

STUDENT:
POST   /api/v1x/sessions/{id}/pay (Create payment intent)
```

### Reviews/Ratings
```
POST   /api/v1x/sessions/{id}/rate
GET    /api/v1x/mentors/{id}/reviews
GET    /api/v1x/mentors/{id}/rating-stats
```

---

## 🧪 TESTING CHECKLIST

### Verification Testing
- [ ] Can upload document
- [ ] Document size validated (< 10MB)
- [ ] File type validated (PDF, PNG, JPEG)
- [ ] Status updates when approved
- [ ] Reject reason displayed to mentor
- [ ] Admin sees all pending requests
- [ ] Email notification sent

### Payment Testing
- [ ] Can add Stripe payment method
- [ ] Test card works (4242 4242 4242 4242)
- [ ] Invalid card rejected
- [ ] Can set default payment method
- [ ] Can remove payment method
- [ ] Payout request succeeds
- [ ] Amount validation works

### Rating Testing
- [ ] Rating modal shows after session
- [ ] 5-star rating works
- [ ] Can write comment
- [ ] Cannot rate twice
- [ ] Average rating calculates
- [ ] Reviews display on profile

---

## 💾 DATABASE CHANGES

New tables/columns needed:
```sql
-- Mentor verification documents
CREATE TABLE mentor_documents (
  id INT PRIMARY KEY,
  mentor_id INT NOT NULL,
  document_type VARCHAR,
  file_url VARCHAR,
  status VARCHAR (pending, approved, rejected),
  rejected_reason TEXT,
  created_at TIMESTAMP,
  approved_at TIMESTAMP
);

-- Payment methods
CREATE TABLE mentor_payment_methods (
  id INT PRIMARY KEY,
  mentor_id INT NOT NULL,
  stripe_payment_method_id VARCHAR,
  is_default BOOLEAN,
  created_at TIMESTAMP
);

-- Session ratings
ALTER TABLE sessions ADD COLUMN rating INT;
ALTER TABLE sessions ADD COLUMN review_comment TEXT;
ALTER TABLE sessions ADD COLUMN reviewed_at TIMESTAMP;
```

---

## 🚀 DEPLOYMENT CHECKLIST

Before going live:
- [ ] Stripe test mode works
- [ ] Stripe live keys configured
- [ ] Webhook secret verified
- [ ] Payment amount correct
- [ ] Payout schedule correct (weekly/monthly)
- [ ] Tax calculation implemented
- [ ] Error messages user-friendly
- [ ] Refund process documented

---

## ⏱️ TIME ESTIMATE

| Task | Hours | Status |
|------|-------|--------|
| Mentor Verification | 3-4 | ⏳ |
| Payment Processing | 4-5 | ⏳ |
| Session Ratings | 2-3 | ⏳ |
| Testing & Fixes | 1-2 | ⏳ |
| **TOTAL** | **10-14** | |

---

## 📚 RESOURCES

- Stripe Docs: https://stripe.com/docs/stripe-js
- Stripe Test Cards: https://stripe.com/docs/testing
- FastAPI Upload: https://fastapi.tiangolo.com/tutorial/request-files/
- React Hooks: https://react.dev/reference/react/hooks

---

**Phase**: 2 of 4  
**Duration**: 10 hours  
**Start**: After dashboard testing completes  
**Blockers**: Stripe account needed

🚀 **READY TO BUILD MENTOR FEATURES!**
