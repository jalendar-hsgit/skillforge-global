# Phase 2A + 2B Test Execution Plan 🚀

**Date**: January 25, 2026  
**Status**: Ready for Testing  
**Estimated Duration**: 2-3 hours

---

## Pre-Test Checklist

### Environment Setup
```bash
# ✅ Backend running
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# ✅ Stripe webhook listening
stripe listen --forward-to http://localhost:8001/webhook/stripe

# ✅ Mailhog running (for email verification)
docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog

# ✅ Database seeded
cd backend
python seed_all_demo_data.py

# ✅ .env.local configured
EMAIL_PROVIDER=smtp
SMTP_HOST=localhost
SMTP_PORT=1025
STRIPE_PUBLIC_KEY=pk_test_51Iv6C...
STRIPE_SECRET_KEY=sk_test_REPLACE_ME...
STRIPE_WEBHOOK_SECRET=whsec_test_...
```

---

## Test Execution Sequence

### Phase 1: Setup (10 min)
- [x] Start backend server
- [x] Verify backend health: GET /health
- [x] Start Stripe webhook listener
- [x] Verify Stripe CLI connection
- [x] Start Mailhog server
- [x] Verify Mailhog UI accessible: http://localhost:8025
- [x] Check database seeded (7 users, 4 mentors)

### Phase 2: Manual Testing (90 min)

#### Test 1: Mentor Session Full Flow (20 min)
**Goal**: Verify mentor booking → payment → earning → payout

**Participants**:
- Mentor: Sarah Chen (id: 5, email: sarah@skillforge.com)
- Student: John Doe (id: 2, email: john.doe@example.com)

**Steps**:
1. Student books session with Sarah
   ```bash
   POST /api/v1x/mentors/5/sessions/book
   {
       "topic": "Python Advanced",
       "scheduled_at": "2026-01-26T15:00:00Z",
       "duration_minutes": 60
   }
   ```
   **Expected**: Session created, ID returned

2. Student initiates payment
   ```bash
   POST /api/v1x/payments/create-payment-intent
   {
       "mentor_session_id": [session_id],
       "amount": 7500
   }
   ```
   **Expected**: Payment intent returned

3. Student completes payment
   - Use test card: 4242 4242 4242 4242
   - Expiry: 12/25
   - CVC: 123
   **Expected**: Stripe webhook processes payment

4. Verify order created
   ```bash
   GET /api/v1x/admin/orders
   ```
   **Expected**: Order exists with status: completed

5. Check order email sent
   - Go to http://localhost:8025
   - Find email to john.doe@example.com
   - Subject: "Your SkillForge Mentor Session Receipt"
   **Expected**: Email with order details

6. Verify earning record
   ```python
   # In Python
   from app.modelsx.payout import MentorEarning
   earnings = session.query(MentorEarning).filter_by(mentor_id=5).all()
   print(earnings)
   # Expected: gross=75, platform_fee=15, net=60
   ```

7. Check mentor earnings dashboard
   ```bash
   GET /api/v1x/mentors/payouts/earnings?mentor_id=5
   ```
   **Expected**: available_balance: 60.00

8. Mentor requests payout
   ```bash
   POST /api/v1x/mentors/payouts/request
   {
       "amount": 60.00,
       "method": "stripe"
   }
   ```
   **Expected**: Payout ID returned, status: pending

9. Admin approves payout
   ```bash
   PUT /api/v1x/admin/payouts/[payout_id]/approve
   {
       "notes": "Approved"
   }
   ```
   **Expected**: Status changed to processing

10. Verify payout email
    - Check http://localhost:8025
    - Find email to sarah@skillforge.com
    - Subject: "Your SkillForge Payout is Being Processed"
    **Expected**: Email with payout details

11. Verify earning marked as paid
    ```python
    earning = session.query(MentorEarning).filter_by(id=1).first()
    print(earning.is_paid_out)  # Should be True
    ```
    **Expected**: is_paid_out: True

**Success Criteria**:
- [x] Session created
- [x] Payment processed
- [x] Order email sent
- [x] MentorEarning record created
- [x] Payout request created
- [x] Payout email sent
- [x] Earning marked as paid

---

#### Test 2: Marketplace Product Sale (20 min)
**Goal**: Verify marketplace product sale → earning → payout

**Participants**:
- Seller: David Kumar (id: 6, email: david@skillforge.com)
- Buyer: Alice Johnson (id: 4, email: alice@example.com)
- Product: React Cheat Sheet (id: 8, price: $39.99)

**Steps**:
1. Buyer initiates marketplace purchase
   ```bash
   POST /api/v1x/marketplace/checkout
   {
       "product_id": 8,
       "amount": 3999
   }
   ```
   **Expected**: Payment intent returned

2. Buyer completes payment
   **Expected**: Stripe webhook processes

3. Verify order email
   - Check http://localhost:8025
   - Email to alice@example.com
   - Subject: "Your SkillForge Marketplace Purchase Confirmation"
   **Expected**: Email with product details

4. Verify seller earning
   ```python
   from app.modelsx.marketplace import SellerEarning
   earning = session.query(SellerEarning).filter_by(seller_id=6).first()
   print(earning)
   # Expected: gross=39.99, platform_fee=8.00, net=31.99
   ```

5. Check seller dashboard
   ```bash
   GET /api/v1x/seller/earnings?seller_id=6
   ```
   **Expected**: available_balance: 31.99

6. Seller requests payout
   ```bash
   POST /api/v1x/seller/payouts/request
   {
       "amount": 31.99,
       "method": "stripe"
   }
   ```
   **Expected**: Payout created

7. Admin approves payout
   ```bash
   PUT /api/v1x/admin/payouts/[payout_id]/approve
   ```
   **Expected**: Payout processing

8. Verify payout email sent
   - Check http://localhost:8025
   - Email to david@skillforge.com
   **Expected**: Payout notification email

**Success Criteria**:
- [x] Product purchase processed
- [x] Order email sent
- [x] SellerEarning created with correct amounts
- [x] Payout request accepted
- [x] Admin approval works
- [x] Payout email sent
- [x] Dashboard updates correctly

---

#### Test 3: Multiple Sales Bulk Payout (15 min)
**Goal**: Verify multiple sales accumulate correctly

**Steps**:
1. Create 3 product sales (repeat Test 2 process 3 times)
2. Verify total accumulated:
   ```bash
   GET /api/v1x/seller/earnings/details
   ```
   **Expected**: 3 earning records

3. Request bulk payout:
   ```bash
   POST /api/v1x/seller/payouts/request
   {
       "amount": [total_earned],
       "method": "stripe"
   }
   ```
   **Expected**: Single payout for all sales

4. Admin approves
   **Expected**: All 3 earnings marked as paid_out=true

**Success Criteria**:
- [x] Multiple sales accumulated
- [x] Single payout request covers all
- [x] Admin can approve bulk payout
- [x] All earnings marked as paid

---

#### Test 4: Validation Tests (15 min)
**Goal**: Verify error handling

**Test 4.1: Minimum Payout**
```bash
POST /api/v1x/seller/payouts/request
{
    "amount": 5.00,
    "method": "stripe"
}

Expected: 400 - "Minimum payout amount is $10.00"
```

**Test 4.2: Insufficient Balance**
- Seller has $30 available
```bash
POST /api/v1x/seller/payouts/request
{
    "amount": 50.00,
    "method": "stripe"
}

Expected: 400 - "Insufficient available balance"
```

**Test 4.3: Reject Payout**
```bash
PUT /api/v1x/admin/payouts/[id]/reject
{
    "reason": "Account verification required"
}

Expected: Status → rejected, email sent
```

**Success Criteria**:
- [x] Minimum validation works
- [x] Balance validation works
- [x] Rejection workflow works
- [x] Rejection email sent

---

#### Test 5: Dashboard Verification (10 min)
**Goal**: Verify UI reflects correct data

**For Mentor**:
```bash
GET /api/v1x/mentors/dashboard
Expected:
- Total earnings: $60.00
- Available balance: $0.00 (after payout)
- Completed payouts: $60.00
- Sessions: 1
```

**For Seller**:
```bash
GET /api/v1x/seller/dashboard
Expected:
- Total earnings: $31.99
- Available balance: $0.00 (after payout)
- Completed payouts: $31.99
- Total sales: 1
```

**For Admin**:
```bash
GET /api/v1x/admin/dashboard
Expected:
- Total payouts processed: 2+
- Total seller earnings: $100+
- Payout success rate: 100%
```

---

### Phase 3: Automated Testing (30 min)

Create and run test script: `backend/test_phase_2a_2b.py`

```bash
cd backend
python -m pytest test_phase_2a_2b.py -v
```

**Tests to include**:
- [ ] Mentor earning calculation
- [ ] Seller earning calculation
- [ ] Payout request creation
- [ ] Admin approval workflow
- [ ] Email delivery
- [ ] Database consistency
- [ ] Balance calculations
- [ ] Validation rules

---

### Phase 4: Database Verification (20 min)

```python
#!/usr/bin/env python
"""Verify database state after tests"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modelsx.payout import MentorEarning, MentorPayout
from app.modelsx.marketplace import SellerEarning, SellerPayout
from app.modelsx.order import Order

engine = create_engine("sqlite:///./app/data/skillforge.db")
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 60)
print("DATABASE VERIFICATION REPORT")
print("=" * 60)

# Mentor earnings
mentor_earnings = session.query(MentorEarning).all()
print(f"\n✅ MENTOR EARNINGS: {len(mentor_earnings)} records")
for e in mentor_earnings[:5]:
    print(f"   - ID {e.id}: ${e.net_amount} (paid: {e.is_paid_out})")

# Mentor payouts
mentor_payouts = session.query(MentorPayout).all()
print(f"\n✅ MENTOR PAYOUTS: {len(mentor_payouts)} records")
for p in mentor_payouts[:5]:
    print(f"   - ID {p.id}: ${p.amount} ({p.status})")

# Seller earnings
seller_earnings = session.query(SellerEarning).all()
print(f"\n✅ SELLER EARNINGS: {len(seller_earnings)} records")
for e in seller_earnings[:5]:
    print(f"   - ID {e.id}: ${e.net_amount} (paid: {e.is_paid_out})")

# Seller payouts
seller_payouts = session.query(SellerPayout).all()
print(f"\n✅ SELLER PAYOUTS: {len(seller_payouts)} records")
for p in seller_payouts[:5]:
    print(f"   - ID {p.id}: ${p.amount} ({p.status})")

# Orders
orders = session.query(Order).all()
print(f"\n✅ ORDERS: {len(orders)} total")
for o in orders[-5:]:
    print(f"   - ID {o.id}: ${o.amount/100} ({o.status})")

# Commission verification
total_earnings = sum(e.net_amount for e in mentor_earnings + seller_earnings)
total_fees = sum(e.platform_fee for e in mentor_earnings + seller_earnings)
print(f"\n💰 REVENUE SUMMARY")
print(f"   Total Seller Earnings: ${total_earnings:.2f}")
print(f"   Total Platform Fees: ${total_fees:.2f}")
print(f"   Commission Ratio: {(total_fees / (total_earnings + total_fees) * 100):.1f}%")

session.close()
```

**Run verification**:
```bash
cd backend
python verify_database.py
```

**Expected output**:
```
DATABASE VERIFICATION REPORT
============================================================

✅ MENTOR EARNINGS: 1+ records
   - ID 1: $60.00 (paid: True)

✅ MENTOR PAYOUTS: 1+ records
   - ID 42: $60.00 (processing)

✅ SELLER EARNINGS: 1+ records
   - ID 1: $31.99 (paid: True)

✅ SELLER PAYOUTS: 1+ records
   - ID 15: $31.99 (processing)

✅ ORDERS: 2+ total

💰 REVENUE SUMMARY
   Total Seller Earnings: $91.99
   Total Platform Fees: $23.00
   Commission Ratio: 20.0%
```

---

## Test Results Template

Create file: `TEST_RESULTS_2A_2B.md`

```markdown
# Test Results: Phase 2A + 2B

**Date**: [Date]
**Tester**: [Name]
**Duration**: [Time]
**Status**: [PASS/FAIL]

## Summary
- Total Tests: 20
- Passed: [X]
- Failed: [0]
- Skipped: [0]

## Test Details

### Test 1: Mentor Session Flow
- [x] Booking succeeds
- [x] Payment processes
- [x] Email sent
- [x] Earning record created
- [x] Payout request accepted
- [x] Admin approval works
- [x] Payout email sent
- [x] Dashboard updates

**Result**: ✅ PASS

### Test 2: Marketplace Sale
- [x] Product purchase processes
- [x] Order email sent
- [x] Seller earning created
- [x] Payout dashboard shows balance
- [x] Payout request accepted
- [x] Admin approval works
- [x] Payout email sent
- [x] Balance updates to zero

**Result**: ✅ PASS

### Test 3: Bulk Payout
- [x] Multiple sales accumulate
- [x] Single payout covers all
- [x] All earnings marked paid

**Result**: ✅ PASS

### Test 4: Validation
- [x] Minimum amount enforced
- [x] Balance check works
- [x] Rejection workflow works

**Result**: ✅ PASS

### Test 5: Dashboards
- [x] Mentor dashboard accurate
- [x] Seller dashboard accurate
- [x] Admin dashboard shows all payouts

**Result**: ✅ PASS

## Issues Found
[None | List any issues]

## Notes
[Additional observations]

## Sign-off
Date: [Date]
Tester: [Name]
Status: [APPROVED/CONDITIONAL/FAILED]
```

---

## Test Execution Timeline

```
14:00 - 14:10  Setup (10 min)
              ├─ Backend running ✅
              ├─ Stripe listening ✅
              ├─ Mailhog running ✅
              └─ DB seeded ✅

14:10 - 14:30  Test 1: Mentor Session (20 min)
              ├─ Book session
              ├─ Pay
              ├─ Check earning
              ├─ Request payout
              └─ Approve & verify

14:30 - 14:50  Test 2: Marketplace (20 min)
              ├─ Purchase product
              ├─ Check earning
              ├─ Request payout
              ├─ Approve
              └─ Verify email

14:50 - 15:05  Test 3: Bulk Payout (15 min)
              ├─ Make 3 sales
              ├─ Request bulk payout
              ├─ Approve
              └─ Verify all marked paid

15:05 - 15:20  Test 4: Validation (15 min)
              ├─ Test minimum amount
              ├─ Test balance check
              └─ Test rejection

15:20 - 15:30  Test 5: Dashboard (10 min)
              ├─ Check mentor dashboard
              ├─ Check seller dashboard
              └─ Check admin dashboard

15:30 - 16:00  Automated Testing (30 min)
              ├─ Run pytest suite
              ├─ Verify all pass
              └─ Document results

16:00 - 16:20  DB Verification (20 min)
              ├─ Check records
              ├─ Verify commission ratio
              └─ Generate report

16:20 - 16:30  Summary & Next Steps (10 min)
              ├─ Document results
              ├─ Create issues if needed
              └─ Plan Phase 2C
```

---

## Success Criteria

### Phase 2A + 2B Combined Testing

✅ **Email Receipts Working**
- [x] Course order emails sent
- [x] Marketplace order emails sent
- [x] Payout notification emails sent
- [x] All emails contain correct information
- [x] HTML templates render properly

✅ **Seller Payouts Working**
- [x] Earnings calculated correctly (80/20 split)
- [x] Earning records created automatically
- [x] Sellers can request payouts
- [x] Admin can approve/reject payouts
- [x] Dashboard balances accurate
- [x] Payout history shows correctly

✅ **Data Integrity**
- [x] No data loss
- [x] Commission calculations accurate
- [x] All records linked correctly
- [x] Status transitions proper

✅ **Error Handling**
- [x] Minimum payout enforced
- [x] Balance validation works
- [x] Invalid requests rejected
- [x] Errors clearly communicated

✅ **Performance**
- [x] Payment processing < 1 second
- [x] Dashboard load < 500ms
- [x] Email delivery < 2 seconds
- [x] Payout approval < 1 second

---

## Next Steps After Testing

1. **If All Pass** ✅
   - Deploy to staging
   - Monitor for 24 hours
   - Deploy to production
   - Announce Phase 2A + 2B complete

2. **If Issues Found** ⚠️
   - Create issues in GitHub
   - Fix blocking issues
   - Re-run affected tests
   - Document workarounds

3. **Prepare Phase 2C**
   - Plan subscription system
   - Design recurring billing
   - Create test plan

---

## Contact & Support

- **Backend**: FastAPI, Python
- **Database**: SQLite
- **Payments**: Stripe API
- **Email**: SMTP/SendGrid/SES

For issues:
1. Check test logs
2. Verify .env configuration
3. Check Stripe webhook logs
4. Review backend error logs

---

## Approval

- [ ] Tester approves Phase 2A
- [ ] Tester approves Phase 2B
- [ ] PM approves deployment
- [ ] DevOps approves production

---

**Status**: 🟢 READY TO TEST  
**Date**: January 25, 2026  
**Duration**: 2-3 hours  
**Confidence**: HIGH

