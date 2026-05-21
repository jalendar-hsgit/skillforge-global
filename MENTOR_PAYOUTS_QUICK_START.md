# 🚀 QUICK START GUIDE - MENTOR EARNINGS SYSTEM

## ⚡ 5-MINUTE SETUP

### Step 1: Verify Servers Running
```
✅ Backend: http://localhost:8001
✅ Frontend: http://localhost:3001
```

### Step 2: Test Mentor Payouts Page
1. Open: http://localhost:3001/mentors/dashboard/payouts
2. Click "Add Method"
3. Fill form with test data
4. Submit and see it in list

### Step 3: Test Admin Payouts Page
1. Open: http://localhost:3001/admin/payouts
2. View stats and pending requests
3. Click "Review Request"
4. Approve or reject

---

## 📍 KEY LOCATIONS

### Mentor Pages
- Dashboard: `/mentors/dashboard`
- Earnings: `/mentors/dashboard/earnings`
- **Payouts:** `/mentors/dashboard/payouts` ← NEW

### Admin Pages
- Dashboard: `/admin/dashboard`
- **Payouts:** `/admin/payouts` ← NEW

### Backend APIs
- **Mentor Endpoints:** `/api/v1x/mentors/payouts/*`
- **Admin Endpoints:** `/api/v1x/admin/payouts/*`

---

## 🧪 QUICK TEST

### Create Payment Method (as mentor)
```bash
POST /api/v1x/mentors/payouts/payment-methods
{
  "account_holder_name": "John Doe",
  "bank_name": "Chase",
  "account_number": "123456789012345",
  "routing_number": "021000021",
  "is_default": true
}
```

### Request Payout (as mentor)
```bash
POST /api/v1x/mentors/payouts/payout-request
{
  "amount": 500.00,
  "payment_method_id": 1
}
```

### Approve Payout (as admin)
```bash
POST /api/v1x/admin/payouts/1/approve
{
  "admin_notes": "Verified"
}
```

---

## 📋 WHAT'S NEW

### New Files Created
- `backend/app/modelsx/payment_method.py` - Database models
- `backend/app/api/v1x/admin_payouts.py` - Admin APIs
- `src/lib/mentorEarningsApi.ts` - Frontend API wrapper
- `src/pages/admin/payouts.tsx` - Admin dashboard

### Files Modified
- `backend/app/modelsx/mentor.py` - Added relationships
- `backend/app/api/v1x/payouts.py` - Added 5 new endpoints
- `backend/app/main.py` - Added imports and mounting

### Files Deleted
- `src/pages/mentors/earnings.tsx` - Duplicate removed

---

## 🔐 SECURITY

- Fernet encryption for account/routing numbers
- Password input fields for sensitive data
- Only last 4 digits shown in UI
- Admin-only endpoints with role validation
- Available balance checks
- Payment method status verification

---

## ✨ FEATURES

### Mentor Can
- Add bank accounts
- Set default account
- Delete accounts
- Request payouts ($10 min)
- View payout history
- See earnings summary
- Track request status

### Admin Can
- View pending requests
- Approve with notes
- Reject with reason
- Verify payment methods
- See statistics
- View all requests
- Filter by status

---

## 📊 DATA STORED

### Payment Methods Table
- ID, mentor_id, account_holder_name, bank_name
- account_number_encrypted, routing_number_encrypted
- status (PENDING/VERIFIED/REJECTED/INACTIVE)
- is_default, verified_at
- created_at, updated_at

### Payout Requests Table
- ID, mentor_id, payment_method_id
- amount (in cents), status
- rejection_reason, admin_notes
- stripe_payout_id
- created_at, updated_at, approved_at, completed_at

---

## 🎯 TYPICAL WORKFLOW

### Mentor Workflow
```
1. Login to /mentors/dashboard/payouts
2. Add payment method (bank account)
3. System shows "Pending Verification"
4. Wait for admin approval
5. Once verified, can request payout
6. Request payout amount
7. Status shows as "Pending"
8. Admin approves
9. Status changes to "Approved"
10. Payment processes (Stripe)
11. Status becomes "Completed"
```

### Admin Workflow
```
1. Login to /admin/payouts
2. See pending payment methods (tab 2)
3. Click "Verify" for each
4. See pending requests (tab 1)
5. Click "Review Request"
6. Add notes if needed
7. Click "Approve"
8. Mentor gets approved notification
```

---

## 🚨 TROUBLESHOOTING

### Issue: "Payment method not verified"
**Fix:** Admin must verify it first in /admin/payouts

### Issue: "Minimum $10 required"
**Fix:** Mentor must have at least $10 available earnings

### Issue: Can't request payout
**Fix:** 
- Ensure payment method is verified
- Ensure balance >= $10
- Ensure payment method selected

### Issue: Server won't start
**Fix:**
- Check cryptography is installed: `pip install cryptography`
- Ensure port 8001 is free: `netstat -an | findstr 8001`

---

## 📱 RESPONSIVE DESIGN

All pages fully responsive:
- ✅ Mobile (320px+)
- ✅ Tablet (768px+)
- ✅ Desktop (1024px+)

Forms stack vertically on mobile
Tables scroll on small screens
Buttons are touch-friendly

---

## 🔄 DATA FLOW

```
Mentor Adds Payment Method
        ↓
Encrypted and stored in DB
        ↓
Admin Reviews in /admin/payouts
        ↓
Admin Verifies Payment Method
        ↓
Mentor Sees "VERIFIED" Status
        ↓
Mentor Requests Payout
        ↓
Payout Request stored as PENDING
        ↓
Admin Reviews and Approves
        ↓
Status changes to APPROVED
        ↓
[Optional] Stripe processes transfer
        ↓
Status changes to COMPLETED
```

---

## 📞 GETTING HELP

### Check Logs
- Backend: Check terminal output on port 8001
- Frontend: Check browser console (F12)

### Check Database
```bash
sqlite3 backend/app/data/skillforge.db
SELECT * FROM payment_methods;
SELECT * FROM payout_requests;
```

### Test Endpoint
```bash
curl http://localhost:8001/api/v1x/mentors/payouts/summary \
  -H "Cookie: session=your_session"
```

---

## ✅ CHECKLIST FOR FIRST USE

- [ ] Both servers running (8001 and 3001)
- [ ] Can access /mentors/dashboard/payouts
- [ ] Can access /admin/payouts
- [ ] Can add payment method
- [ ] Payment method shows in list
- [ ] Admin can see it in unverified list
- [ ] Admin can verify it
- [ ] Can request payout
- [ ] Admin can approve payout

---

## 🎉 YOU'RE ALL SET!

Everything is installed, configured, and running.

**Backend:** http://localhost:8001 ✅  
**Frontend:** http://localhost:3001 ✅  

Go to `/mentors/dashboard/payouts` to start testing!

---

## 📖 FULL DOCUMENTATION

See: `MENTOR_EARNINGS_IMPLEMENTATION_COMPLETE.md` for complete details

---

**Quick Reference**  
**Created:** January 22, 2026  
**Status:** ✅ Ready to Use
