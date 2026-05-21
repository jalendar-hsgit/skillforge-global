# ✅ STEP-BY-STEP: Get Payouts Page Working

## Current Status
- ✅ Backend API running on http://localhost:8001
- ✅ Frontend running on http://localhost:3002
- ✅ Database initialized with test accounts
- ❌ Payouts page content not showing (needs authentication)

---

## Why Content Isn't Loading

The page makes API calls that require authentication:
- `GET /api/v1x/mentors/payouts/summary`
- `GET /api/v1x/mentors/payouts/payment-methods`
- `GET /api/v1x/mentors/payouts/history`

Without login → API returns 401 → No data → Page shows "Failed to load earnings data"

---

## Fix: Login First

### Step 1: Open Home Page
```
Go to: http://localhost:3002
```

You should see the SkillForge homepage with Login button.

### Step 2: Click Login
```
Click: "Login" or "Sign In" button
```

### Step 3: Enter Test Account
```
Email:    sarah.chen@example.com
Password: password123

Click: "Login"
```

### Step 4: Wait for Redirect
```
After successful login, you should be redirected to Dashboard
```

### Step 5: Navigate to Payouts
```
Method 1: Click Menu → Dashboard → Payouts & Withdrawals
Method 2: Direct URL: http://localhost:3002/mentors/dashboard/payouts
```

### Step 6: Page Should Load
```
You should now see:
✅ Earnings Summary Cards
  - Available Balance: $XXX.XX
  - Pending Payouts: $XX.XX
  - Total Earned: $XXX.XX

✅ Payment Methods Section
  - List of payment methods (if any)
  - "+ Add Method" button

✅ Payout Requests Section
  - History of payout requests (if any)
  - "💰 Request Withdrawal" button
```

---

## Test Accounts Available

### For Testing Mentor Features
```
Email:    sarah.chen@example.com
Password: password123
Role:     Mentor (Python+AI, $75/hr)
```

**Or try other mentors:**
- david.kumar@example.com (Web Dev)
- emily.rodriguez@example.com (ML)
- james.patterson@example.com (DevOps)

### For Testing Admin Features
```
Email:    admin@skillforge.com
Password: password123
Role:     Admin
```

---

## Troubleshooting

### Issue: Login page shows 404 error
**Fix**: Check if auth page exists
- Try: http://localhost:3002/ instead
- Then look for Login link on homepage

### Issue: Login successful but redirects to 404 page
**Fix**: Dashboard page might be broken
- Try going directly to: http://localhost:3002/mentors/dashboard

### Issue: Payouts page still shows "Failed to load"
**Check**:
1. Are you logged in? (check if you're on protected page)
2. Is backend running? (test http://localhost:8001/api/v1x/mentors)
3. Open browser DevTools (F12) → Console → check for errors

### Issue: Page loads but shows empty sections
**This is normal** if:
- No payment methods added yet
- No payout requests yet
- No earnings data yet
Try adding a payment method first!

---

## Full Test Workflow

```
1. Go to http://localhost:3002
   ↓
2. Login with sarah.chen@example.com / password123
   ↓
3. Go to Payouts page
   ↓
4. See balance and earnings data load ✅
   ↓
5. Click "+ Add Method"
   ↓
6. Fill form with test data:
   - Account Holder: Sarah Chen
   - Bank: Chase
   - Account: 123456789012345
   - Routing: 021000021
   ↓
7. Click "Add Payment Method"
   ↓
8. See success message ✅
   ↓
9. Payment method appears in list ✅
   ↓
10. Login as admin (admin@skillforge.com)
   ↓
11. Go to /admin/payouts
   ↓
12. See pending payment method
   ↓
13. Click "Verify"
   ↓
14. Status changes to VERIFIED ✅
```

---

## Expected Results After Login

### Mentor View
```
┌─────────────────────────────────────────┐
│ Available Balance    Pending Payouts    │
│    $100.00              $25.00          │
│                                         │
│ Total Earned                            │
│    $500.00                              │
└─────────────────────────────────────────┘

Payment Methods
+ Add Method

[List of methods...]

Payout Requests
💰 Request Withdrawal

[List of requests...]
```

### Admin View
```
Statistics
Total Pending: 5    Verified Methods: 3

Tabs: [Pending Requests] [Payment Methods]

[List of requests to approve/reject...]
```

---

**Ready?** Go to http://localhost:3002 and login! 🚀
