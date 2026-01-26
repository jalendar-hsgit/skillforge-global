# Phase 2B: Quick Reference Guide ⚡

**Status**: Ready to Test  
**Date**: January 25, 2026

---

## What's New in Phase 2B?

```
Phase 2A: Email Receipts (✅ Complete)
  └─ Course order emails
  └─ Marketplace order emails
  └─ Payout notifications

Phase 2B: Seller Payouts (📝 Implementation Plan)
  ├─ MentorEarning records (session → 80% to mentor)
  ├─ SellerEarning records (product sale → 80% to seller)
  ├─ Payout request system
  └─ Admin approval workflow
```

---

## Commission Structure

```
MENTOR SESSIONS
┌──────────────────────┐
│ Session Price: $75   │
├──────────────────────┤
│ Platform (20%): $15  │
│ Mentor (80%):   $60  │
└──────────────────────┘

MARKETPLACE PRODUCTS
┌──────────────────────┐
│ Product Price: $50   │
├──────────────────────┤
│ Platform (20%): $10  │
│ Seller (80%):   $40  │
└──────────────────────┘

COURSES
┌──────────────────────┐
│ Course Price: $99.99 │
├──────────────────────┤
│ Platform (100%): $99.99 │
│ Creator (0%):   $0   │
└──────────────────────┘
```

---

## Key Endpoints

### For Sellers/Mentors

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/seller/earnings` | GET | View earnings summary |
| `/seller/earnings/details` | GET | View detailed transactions |
| `/seller/payouts/request` | POST | Request payout |
| `/seller/payouts/history` | GET | View payout history |
| `/mentors/payouts/earnings` | GET | Mentor earnings summary |
| `/mentors/payouts/earnings/details` | GET | Mentor detailed earnings |
| `/mentors/payouts/request` | POST | Mentor request payout |
| `/mentors/payouts/history` | GET | Mentor payout history |

### For Admin

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/payouts` | GET | List all pending payouts |
| `/admin/payouts/{id}` | GET | View payout details |
| `/admin/payouts/{id}/approve` | PUT | Approve payout |
| `/admin/payouts/{id}/reject` | PUT | Reject payout |
| `/admin/payouts/{id}/retry` | POST | Retry failed payout |

---

## Implementation Overview

### Models Used

```
MentorEarning
├─ mentor_id (FK)
├─ session_id (FK)
├─ gross_amount ($100)
├─ platform_fee (20%)
└─ net_amount (80%)

MentorPayout
├─ mentor_id
├─ amount (requested)
├─ status: pending/processing/completed/failed
├─ method: stripe/bank_transfer/paypal
└─ stripe_transfer_id

SellerEarning (NEW)
├─ seller_id (FK to User)
├─ order_id (FK)
├─ gross_amount
├─ platform_fee
└─ net_amount

SellerPayout
├─ seller_id
├─ amount
├─ status
├─ payout_method
└─ transaction_id
```

---

## Data Flow

```
1. Payment Completed
   └─ Stripe webhook: payment_intent.succeeded

2. Create Earning Record
   ├─ Detect order type (course/marketplace)
   ├─ Calculate commission (80/20 split)
   ├─ Create MentorEarning OR SellerEarning
   └─ Send order confirmation email (Phase 2A)

3. Seller/Mentor Requests Payout
   ├─ Check minimum amount ($10)
   ├─ Check available balance
   ├─ Create payout request (status: pending)
   └─ Dashboard shows pending

4. Admin Approves Payout
   ├─ Review request
   ├─ Approve or reject
   ├─ If approved: status → processing
   ├─ Process with Stripe/PayPal/Bank
   ├─ Mark earnings as is_paid_out=true
   └─ Send payout email (Phase 2A)

5. Funds Transferred
   ├─ Stripe transfers to account
   ├─ Status → completed
   ├─ Available balance updated
   └─ Dashboard shows completed
```

---

## Testing Checklist

### Test 1: Mentor Session Payout
- [ ] Book mentor session ($75)
- [ ] Complete payment
- [ ] Verify earning created (60 net)
- [ ] Request payout
- [ ] Admin approves
- [ ] Email sent
- [ ] Balance updates

### Test 2: Marketplace Product Sale
- [ ] Purchase product ($50)
- [ ] Complete payment
- [ ] Verify earning created (40 net)
- [ ] Request payout
- [ ] Admin approves
- [ ] Email sent
- [ ] Balance updates

### Test 3: Multiple Sales Bulk Payout
- [ ] Make 3 product sales
- [ ] Earnings accumulate
- [ ] Request payout for all
- [ ] Admin approves
- [ ] All marked as paid

### Test 4: Reject Payout
- [ ] Create payout request
- [ ] Admin rejects with reason
- [ ] Email sent to seller
- [ ] Balance remains available

### Test 5: Minimum Payout Validation
- [ ] Try payout < $10 → Error
- [ ] Try payout = $10 → Success

### Test 6: Insufficient Balance
- [ ] Have $50, request $100 → Error

---

## API Examples

### Get Seller Earnings
```bash
GET /api/v1x/seller/earnings

Response:
{
    "total_earnings": 125.50,
    "available_balance": 75.50,
    "pending_payouts": 0.00,
    "completed_payouts": 50.00,
    "total_sales": 3,
    "total_revenue": 156.88
}
```

### Request Payout
```bash
POST /api/v1x/seller/payouts/request

{
    "amount": 75.50,
    "method": "stripe"
}

Response:
{
    "id": 15,
    "seller_id": 3,
    "amount": 75.50,
    "status": "pending",
    "payout_method": "stripe",
    "requested_at": "2026-01-25T10:30:00Z"
}
```

### Admin Approve Payout
```bash
PUT /api/v1x/admin/payouts/15/approve

{
    "notes": "Approved - account verified"
}

Response:
{
    "id": 15,
    "amount": 75.50,
    "status": "processing",
    "transaction_id": "tr_1234567890",
    "message": "Payout approved and processing"
}
```

---

## Minimum Requirements

| Requirement | Value |
|------------|-------|
| Minimum Payout | $10.00 |
| Commission Split | 80% seller, 20% platform |
| Payout Methods | Stripe (primary) |
| Processing Time | 1-2 business days |

---

## Emails Sent (Phase 2A Integration)

| Event | Email | To | Trigger |
|-------|-------|----|---------| 
| Order Placed | Order confirmation | Buyer | Webhook: payment.succeeded |
| Payout Approved | Payout notification | Seller | Admin: approve payout |
| Payout Rejected | Rejection notice | Seller | Admin: reject payout |

---

## Database Tables

### New Table: seller_earnings
```sql
CREATE TABLE seller_earnings (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER,
    order_id INTEGER UNIQUE,
    product_id INTEGER,
    gross_amount FLOAT,
    platform_fee FLOAT,
    net_amount FLOAT,
    payout_id INTEGER,
    is_paid_out BOOLEAN DEFAULT FALSE,
    earned_at DATETIME,
    paid_out_at DATETIME,
    FOREIGN KEY(seller_id) REFERENCES users(id),
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(product_id) REFERENCES digital_products(id),
    FOREIGN KEY(payout_id) REFERENCES seller_payouts(id)
);
```

### Updated Table: mentor_earnings
- Now created on every completed mentor session
- Tracks 80/20 commission split
- Links to MentorPayout

### Updated Table: seller_payouts
- Status values: pending, processing, completed, failed
- Supports: stripe, bank_transfer, paypal (methods)

---

## Configuration Needed

### .env.local
```bash
# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# Email Configuration (for payout emails)
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@skillforge.com
SMTP_PASSWORD=app-password
```

---

## Validation Rules

```
Payout Request:
✅ amount > 0
✅ amount >= 10.00 (minimum)
✅ amount <= available_balance
✅ seller/mentor is authenticated
✅ at least one earning exists

Admin Approval:
✅ payout exists
✅ status is "pending"
✅ seller/mentor exists
✅ email is valid
✅ payout method is valid
```

---

## Success Metrics

After Phase 2B implementation:

```
✅ No earning records lost
✅ 100% commission accuracy
✅ Zero failed payouts in test
✅ All emails delivered
✅ <1 second response times
✅ Dashboard reflects reality
✅ Admin controls effective
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Email not sent | Check SMTP config, verify provider |
| Payout fails | Verify Stripe keys, check logs |
| Balance incorrect | Recalculate from earnings, verify commission |
| Payout rejected | Check seller account verification |

---

## Next: Phase 2C

Coming soon:
- ✅ Subscriptions (monthly/annual)
- ✅ Recurring billing
- ✅ Usage tracking
- ✅ Tier management

---

## Quick Start

```bash
# 1. Start backend
cd backend
uvicorn app.main:app --reload

# 2. Start Stripe webhook listener
stripe listen --forward-to http://localhost:8001/webhook/stripe

# 3. Run tests
python -m pytest test_phase_2a_2b.py -v

# 4. Check emails at
http://localhost:8025  # Mailhog UI

# 5. Monitor logs
tail -f backend.log
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| PHASE_2B_SELLER_PAYOUTS_IMPLEMENTATION.md | Complete specification |
| PHASE_2A_2B_COMBINED_TESTING_GUIDE.md | Full test scenarios |
| STRIPE_CONFIGURATION_GUIDE.md | Stripe setup |
| ENV_CONFIGURATION_TEMPLATE.md | .env setup |

---

## Status Summary

- ✅ Phase 2A: Email receipts (COMPLETE)
- 📝 Phase 2B: Seller payouts (READY TO IMPLEMENT)
- 📋 Phase 2C: Subscriptions (PLANNED)

**Ready to code?** → See PHASE_2B_SELLER_PAYOUTS_IMPLEMENTATION.md
**Ready to test?** → See PHASE_2A_2B_COMBINED_TESTING_GUIDE.md

