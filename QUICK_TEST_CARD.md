# 🎯 QUICK TEST REFERENCE CARD

## 🚀 Start Here
1. **Open Browser**: http://localhost:3002
2. **Login** (as mentor): sarah.chen@example.com / password123
3. **Navigate**: Dashboard → Payouts & Withdrawals

---

## ✅ What to Test

### Payment Methods
- [ ] Click "+ Add Method"
- [ ] Fill: Account Holder, Bank, Account #, Routing #
- [ ] Click "Add" → See success message
- [ ] Method appears in list with PENDING status
- [ ] Click "Delete" → Confirm removes it
- [ ] Add again and check "Set as default"

### Payout Request
- [ ] Click "💰 Request Withdrawal"
- [ ] Enter amount: 25.00
- [ ] Select payment method from dropdown
- [ ] Click "Request" → See success message
- [ ] Request appears in list as PENDING
- [ ] Shows correct amount and timestamp

### Admin Approval (log in as admin@skillforge.com)
- [ ] Go to: /admin/payouts
- [ ] Click "Payment Methods" tab
- [ ] Click "Verify" on pending method
- [ ] Status changes to VERIFIED
- [ ] Click "Pending Requests" tab
- [ ] See the payout request
- [ ] Click "Review Request"
- [ ] Add optional note
- [ ] Click "Approve"
- [ ] Status changes to APPROVED

### Back to Mentor
- [ ] Refresh Payouts page
- [ ] See payout request status is APPROVED
- [ ] Check earnings summary cards loaded
- [ ] View payment methods list

---

## 🐛 Error Checks

**Should NOT see any of these:**
- [ ] 404 errors in console
- [ ] Red error messages on page
- [ ] Blank pages or missing data
- [ ] Network errors in browser console
- [ ] "Cannot read properties of undefined"

**If you see any, report it!**

---

## 📊 Expected Results

### Mentor Page Should Show:
```
Balance Cards:
  - Available Balance: $XXX.XX
  - Pending Payouts: $XX.XX
  - Total Earned: $XXX.XX

Payment Methods:
  - Add button at top
  - List of methods below
  - Delete button per method

Payout Requests:
  - Request button at top
  - List of requests below
  - Status badges (PENDING, APPROVED, etc.)
```

### Admin Page Should Show:
```
Statistics Cards:
  - Total Pending: X
  - Total Verified Methods: X
  - etc.

Two Tabs:
  1. Pending Requests (list)
  2. Payment Methods (list)

Action Buttons:
  - Verify (for methods)
  - Approve/Reject (for requests)
```

---

## ⚡ Quick Test (2 minutes)

1. **Add Method** (30 sec)
   - Fill form → Click Add → ✅ Success

2. **Request Payout** (30 sec)
   - Click Request → Fill $25 → ✅ Success

3. **Admin Verify** (30 sec)
   - Login as admin → Verify method → ✅ Changed status

4. **Admin Approve** (30 sec)
   - Approve payout request → ✅ Status changed

---

## 📱 Test on Different Devices

- [ ] Desktop (wide screen)
- [ ] Tablet (medium screen)  
- [ ] Mobile (narrow screen)

*All should work and display correctly*

---

## 🔗 Useful URLs

| Feature | URL |
|---------|-----|
| Home | http://localhost:3002 |
| Mentor Login | http://localhost:3002/auth/login |
| Mentor Payouts | http://localhost:3002/mentors/dashboard/payouts |
| Admin Payouts | http://localhost:3002/admin/payouts |
| Admin Dashboard | http://localhost:3002/admin/dashboard |

---

## 👥 Test Accounts

**Mentor** (password: password123)
- sarah.chen@example.com

**Admin** (password: password123)
- admin@skillforge.com

---

## 🎯 Success Indicators

✅ No red errors  
✅ Forms submit successfully  
✅ Data persists after refresh  
✅ Status updates correctly  
✅ Admin can approve/reject  
✅ Mentor sees updated status  
✅ All buttons clickable  
✅ Forms validate input  

---

## 💾 Keep This Open

Have this card nearby while testing to quickly verify:
- All expected features work
- No unexpected errors appear
- Data flows correctly through the system

---

**Ready? Open http://localhost:3002 and start testing!** 🚀
