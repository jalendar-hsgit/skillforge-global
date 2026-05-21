# 🧪 MENTOR EARNINGS & PAYOUTS - TEST GUIDE

## Current System Status

✅ **Backend**: Running on http://localhost:8001  
✅ **Frontend**: Running on http://localhost:3002 (or 3001/3000 if ports in use)

---

## Test Plan

### 1. Login as Mentor
1. Go to http://localhost:3002
2. Login with mentor credentials:
   - Email: `sarah.chen@example.com` (mentor)
   - Password: `password123`

### 2. Navigate to Payouts Page
1. Click on Dashboard → Mentor Dashboard
2. Navigate to: **Dashboard → Payouts & Withdrawals** (or direct: `/mentors/dashboard/payouts`)

### 3. Test Payment Method Management

#### 3a. Add Payment Method
1. Click **"+ Add Method"** button
2. Fill in the form:
   - Account Holder Name: `Sarah Chen`
   - Bank Name: `Chase Bank`
   - Account Number: `123456789012345`
   - Routing Number: `021000021`
   - Check "Set as default"
3. Click **"Add Payment Method"**
4. Expected: ✅ Payment method appears in list with "PENDING VERIFICATION" status

#### 3b. Verify Payment Method (as Admin)
1. In separate browser, login as admin:
   - Email: `admin@skillforge.com`
   - Password: `password123`
2. Navigate to: **Admin → Payouts** (or direct: `/admin/payouts`)
3. Go to **"Payment Methods"** tab
4. Find the payment method added above
5. Click **"Verify"** button
6. Expected: ✅ Status changes to "VERIFIED"

#### 3c. Verify in Mentor View
1. Back to mentor browser/tab
2. Refresh the page or let it auto-refresh
3. Expected: ✅ Payment method status shows "VERIFIED"

### 4. Test Payout Request

#### 4a. Request Payout (as Mentor)
1. On Payouts page, note the **Available Balance** (should be from earnings)
2. Click **"💰 Request Withdrawal"** button
3. Fill in:
   - Amount: `$50.00` (or less than available balance)
   - Payment Method: Select the verified method
4. Click **"Request Withdrawal"**
5. Expected: ✅ Success message shows payout request ID
6. Expected: ✅ New request appears in "Payout Requests" section with "PENDING" status

#### 4b. Admin Approval (as Admin)
1. Go to `/admin/payouts` (Admin Payouts page)
2. Go to **"Pending Requests"** tab
3. View the pending payout request
4. Click **"Review Request"** button
5. In the action panel:
   - Add optional notes: "Approved - verified mentor"
   - Click **"Approve"** button
6. Expected: ✅ Status changes to "APPROVED"

#### 4c. Verify Status (as Mentor)
1. Back to mentor Payouts page
2. Refresh or wait for auto-refresh
3. Expected: ✅ Payout request status shows "APPROVED"

### 5. Check Dashboard Stats

#### For Mentor:
- ✅ Available Balance: Shows remaining balance
- ✅ Pending Payouts: Shows approved but not completed payouts
- ✅ Total Earned: Shows lifetime earnings

#### For Admin:
- ✅ Summary stats: Total pending, approved, processing, completed
- ✅ Payment methods: Count by status (verified/pending/rejected)
- ✅ Payout requests: Count by status

---

## API Testing (Optional)

### Test Endpoints Directly

#### Get Earnings Summary (Mentor)
```bash
curl -X GET http://localhost:8001/api/v1x/mentors/payouts/summary \
  -H "Cookie: session=YOUR_SESSION_ID"
```

#### Get Payment Methods (Mentor)
```bash
curl -X GET http://localhost:8001/api/v1x/mentors/payouts/payment-methods \
  -H "Cookie: session=YOUR_SESSION_ID"
```

#### Create Payment Method (Mentor)
```bash
curl -X POST http://localhost:8001/api/v1x/mentors/payouts/payment-methods \
  -H "Cookie: session=YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "account_holder_name": "Test User",
    "bank_name": "Test Bank",
    "account_number": "123456789012345",
    "routing_number": "021000021",
    "is_default": true
  }'
```

#### Get Payout Requests (Mentor)
```bash
curl -X GET http://localhost:8001/api/v1x/mentors/payouts/history \
  -H "Cookie: session=YOUR_SESSION_ID"
```

#### Create Payout Request (Mentor)
```bash
curl -X POST http://localhost:8001/api/v1x/mentors/payouts/payout-request \
  -H "Cookie: session=YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "payment_method_id": 1,
    "notes": "Test payout"
  }'
```

#### Get Pending Payouts (Admin)
```bash
curl -X GET http://localhost:8001/api/v1x/admin/payouts/pending \
  -H "Cookie: session=YOUR_ADMIN_SESSION_ID"
```

#### Approve Payout (Admin)
```bash
curl -X POST http://localhost:8001/api/v1x/admin/payouts/1/approve \
  -H "Cookie: session=YOUR_ADMIN_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_notes": "Approved"
  }'
```

---

## Expected Data Flow

```
MENTOR                          SYSTEM                          ADMIN
  |                               |                              |
  +---> Add Payment Method ------>|                              |
  |                               +--- Stored (PENDING) -------->|
  |                               |                              |
  |                               |<----- Verify Status --------+
  |<----- Status Updated (VERIFIED)                             |
  |                               |                              |
  +---> Request Payout ---------->|                              |
  |                               +--- Created (PENDING) ------->|
  |                               |                              |
  |                               |<----- Review & Approve -----+
  |<----- Status Updated (APPROVED)                             |
  |                               |                              |
  |                               +--- Process Payout --------->|
  |<----- Status Updated (COMPLETED)                            |
  |                               |                              |
```

---

## Known Test Accounts

### Mentors (all have `password123`)
- `sarah.chen@example.com` - $75/hr Python+AI expert
- `david.kumar@example.com` - $65/hr Web Dev expert
- `emily.rodriguez@example.com` - $85/hr ML expert
- `james.patterson@example.com` - $70/hr DevOps expert

### Admin (password: `password123`)
- `admin@skillforge.com` - Regular Admin
- `superadmin@skillforge.com` - Super Admin

---

## Common Issues & Fixes

### ❌ 404 Error on API Calls
**Cause**: Frontend calling wrong endpoint paths  
**Fix**: Check `src/lib/mentorEarningsApi.ts` uses `/api/v1x/mentors/payouts/*`  
**Status**: ✅ FIXED

### ❌ "Payment method not verified" Error
**Cause**: Admin hasn't verified the payment method yet  
**Fix**: Go to Admin Payouts → Payment Methods tab → Verify

### ❌ Can't request payout
**Cause**: Available balance < $10 minimum  
**Fix**: Check earnings summary shows available balance, might need demo data

### ❌ Form submission hangs
**Cause**: Backend not responding  
**Fix**: Check backend is running: `netstat -ano | findstr :8001`

---

## Test Completion Checklist

- [ ] Mentor can add payment method
- [ ] Payment method shows as PENDING VERIFICATION
- [ ] Admin can see unverified payment methods
- [ ] Admin can verify payment method
- [ ] Mentor sees updated status (VERIFIED)
- [ ] Mentor can request payout
- [ ] Payout request shows in list as PENDING
- [ ] Admin can see pending payout requests
- [ ] Admin can approve payout request
- [ ] Mentor sees status updated to APPROVED
- [ ] All form validations work
- [ ] Balance calculations are correct
- [ ] No console errors or 404s

---

## Success Indicators

✅ All mentor earnings pages load without 404s  
✅ Payment methods CRUD operations work  
✅ Payout requests flow from PENDING → APPROVED → COMPLETED  
✅ Admin approval workflow functions  
✅ Real-time data updates (after refresh)  
✅ Proper error messages for invalid inputs  
✅ Encrypted data stored in database  

---

**Ready to Test**: January 22, 2026
