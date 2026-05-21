# 🚀 LIVE TEST EXECUTION - FOLLOW THESE STEPS

## ✅ Services Ready
- **Backend:** http://localhost:8001 (Running ✅)
- **Frontend:** http://localhost:3001 (Running ✅)

---

## 📝 TEST SEQUENCE (Follow in Order)

### STEP 1️⃣: LOGIN (2 minutes)
**Browser:** http://localhost:3001

1. Look for login button in top right
2. Enter test credentials:
   - Email: `john.doe@example.com`
   - Password: `password123` (or check backend seed script)
3. Click Login
4. Wait for page to redirect to dashboard
5. **Expected:** Dashboard shows user name (e.g., "John Doe")
6. **Result:** [ ] PASS [ ] FAIL

---

### STEP 2️⃣: NAVIGATE TO MARKETPLACE (1 minute)
1. Look for "Marketplace" or "Courses" link in navigation menu
2. Click to navigate to marketplace page
3. **Expected:** See list of courses/products available for purchase
4. **Result:** [ ] PASS [ ] FAIL

---

### STEP 3️⃣: ADD COURSE TO CART (2 minutes)
1. Find any course in the listing (e.g., "Python Fundamentals" - $49.99)
2. Click "Add to Cart" button on the course card
3. **Expected:** See notification "Added to cart" or toast message
4. Small cart icon in top right should show item count (e.g., "1")
5. **Result:** [ ] PASS [ ] FAIL

---

### STEP 4️⃣: PROCEED TO CHECKOUT (1 minute)
1. Click on cart icon (top right) or navigate to cart page
2. You should see the course added to your cart
3. Click "Proceed to Checkout" or similar button
4. **Expected:** Page navigates to checkout page
5. **⚠️ CRITICAL TEST:** Look at the URL in address bar
6. **Result:** [ ] PASS [ ] FAIL

### ✅ CHECK ORDERID IN URL
**This is the MAIN fix we implemented!**

```
CORRECT URL:  http://localhost:3001/marketplace/checkout?orderId=5
WRONG URL:    http://localhost:3001/marketplace/checkout?orderId=undefined
```

**What to do:**
- [ ] URL shows `?orderId=5` (or any number) → **PASS ✅**
- [ ] URL shows `?orderId=undefined` → **FAIL ❌ Contact immediately**
- [ ] No orderId parameter at all → **FAIL ❌ Contact immediately**

**Document the orderId for later:** `orderId = _____`

---

### STEP 5️⃣: COUPON VALIDATION TEST (3 minutes)

**You should see a coupon input field on checkout page**

#### Test 5A: INVALID COUPON
1. Find coupon code input field
2. Type: `INVALID123`
3. Click "Apply Coupon" button
4. **Expected:** 
   - Error message appears (e.g., "Invalid coupon code")
   - Message auto-clears after 3 seconds
   - No errors in browser console (F12 to open)
5. **Result:** [ ] PASS [ ] FAIL

**Check browser console (F12):**
- No red errors ✅
- Network request to `/api/v1x/marketplace/apply-coupon` succeeded ✅

#### Test 5B: VALID COUPON (if available)
1. Check if you have a valid coupon code to test
   - Database may have: `SAVE10`, `WELCOME`, etc.
   - Seed script creates demo coupons
2. Type valid coupon code
3. Click "Apply Coupon"
4. **Expected:**
   - Success message appears (e.g., "Coupon applied successfully!")
   - Discount is calculated and shown on total
   - Message auto-clears after 3 seconds
5. **Result:** [ ] PASS [ ] FAIL

---

### STEP 6️⃣: PAYMENT FORM (3 minutes)

**You should see a payment form with Stripe CardElement**

1. Look for input fields:
   - Card Number field
   - Expiry Date field
   - CVC field
   - Name field

2. **Enter Test Card:**
   ```
   Card Number:  4242 4242 4242 4242
   Expiry Date:  12/25 (must be future date)
   CVC:          123
   Name:         Test User
   ```

3. **Expected:**
   - All fields accept input without errors
   - Card is accepted by Stripe (blue border, no error)
   - Form is ready to submit
4. **Result:** [ ] PASS [ ] FAIL

---

### STEP 7️⃣: COMPLETE PAYMENT (2 minutes)

1. Review order summary:
   - Course name and price visible
   - Total amount calculated correctly
   - Discount applied (if coupon used)

2. Click "Pay" or "Complete Purchase" button

3. **Expected:**
   - Loading animation appears
   - Payment is processed
   - No errors in browser console
   - Page redirects to confirmation page

4. **Check Browser Console (F12):**
   - No red errors
   - Look for success message about payment processing

5. **Result:** [ ] PASS [ ] FAIL

---

### STEP 8️⃣: CONFIRMATION PAGE (1 minute)

**After payment succeeds:**

1. **Check URL:** `http://localhost:3001/marketplace/order-confirmation/5`
   - Should contain same orderId as step 4
   - **Document:** `confirmation_orderId = _____`
   - Should match checkout orderId ✅

2. **Check Page Content:**
   - Order confirmation message (e.g., "Thank you for your purchase!")
   - Order number displayed
   - Course name and price shown
   - Order status (e.g., "COMPLETED" or "PAID")

3. **Expected:**
   - Confirmation orderId matches checkout orderId
   - All order details visible and correct
   - No errors on page

4. **Result:** [ ] PASS [ ] FAIL

---

### STEP 9️⃣: DATABASE VERIFICATION (2 minutes)

**This is the CRITICAL fix verification!**

Open a terminal and run:

```powershell
cd "D:\python code\sfg\skillforge-global\backend"
$env:PYTHONPATH = (Get-Location)
& "D:\python code\sfg\skillforge-global\backend\venv\Scripts\python.exe" -c "
import sqlite3
conn = sqlite3.connect('app/data/skillforge.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id = 1')
count = cursor.fetchone()[0]
print(f'Total orders for user 1: {count}')
if count == 1:
    print('✅ PASS - Only 1 order created (duplicate fix works!)')
else:
    print(f'❌ FAIL - Found {count} orders (expecting 1)')
cursor.execute('SELECT id, order_number, amount, status FROM orders WHERE user_id = 1 ORDER BY id DESC LIMIT 3')
rows = cursor.fetchall()
print('\\nLast orders:')
for row in rows:
    print(f'  ID: {row[0]}, Number: {row[1]}, Amount: {row[2]}, Status: {row[3]}')
conn.close()
"