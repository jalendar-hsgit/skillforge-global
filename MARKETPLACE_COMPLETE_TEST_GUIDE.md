# 🧪 MARKETPLACE COMPLETE TEST GUIDE

## ✅ ALL FIXES APPLIED

### Fix #1: Checkout orderId Display ✅
- Modified checkout page to properly display order when orderId in URL
- Shows order total even if client_secret not yet available
- Better error handling with console logging

### Fix #2: Digital Products Cart Icon ✅
- Added cart icon to digital-products listing page
- Cart count updates when adding digital products
- Links to /marketplace/cart for checkout

### Fix #3: Cart Functionality ✅
- All marketplace pages now have cart functionality
- Add to cart works on both courses and digital products
- Cart updates across all pages

---

## 🖥️ CORRECT PORTS & URLs

**PORT 3000 (OLD):** ❌ NOT WORKING - Already in use  
**PORT 3001 (CURRENT):** ✅ FRONTEND RUNNING

**Services:**
- Frontend: http://localhost:3001 ✅
- Backend: http://localhost:8001 ✅

---

## 📋 COMPLETE TEST FLOW

### Step 1: Browse Courses Marketplace (5 min)
```
URL: http://localhost:3001/marketplace

Actions:
1. Page loads with course listings
2. Cart icon visible in top right (should show 0)
3. Click "Add to Cart" on any course
4. Cart count updates to 1
5. Click cart icon → goes to /marketplace/cart
```

### Step 2: Browse Digital Products (3 min)
```
URL: http://localhost:3001/marketplace/digital-products

Actions:
1. Page loads with digital product listings
2. Cart icon visible in top right (showing current count)
3. Click on a product to see details
4. Click "Add to Cart"
5. Cart count updates
6. Click digital-products cart icon → goes to /marketplace/cart
```

### Step 3: View Cart (2 min)
```
URL: http://localhost:3001/marketplace/cart

Actions:
1. Cart shows all items (courses + digital products)
2. Total price calculated correctly
3. Option to apply coupon
4. Click "Proceed to Checkout"
```

### Step 4: Checkout with Order (3 min) 🔴 CRITICAL TEST
```
URL: http://localhost:3001/marketplace/checkout?orderId=X

Expected:
1. Page shows "Complete Your Purchase" (NOT "Your cart is empty")
2. Order summary displays:
   - Order number
   - Total amount
   - Item count
   - Discount (if applied)
3. Either payment form displays OR "Preparing payment..." message
4. Test card info shown below payment form
```

### Step 5: Complete Payment (3 min)
```
If payment form is ready:
1. Enter test card: 4242 4242 4242 4242
2. Enter expiry: 12/25 (or any future date)
3. Enter CVC: 123
4. Name: (any name)
5. Click "Pay" button
6. Wait for redirect to confirmation page
```

### Step 6: Verify Database (2 min)
```
Open PowerShell and run:

cd "D:\python code\sfg\skillforge-global\backend"
sqlite3 app/data/skillforge.db
SELECT COUNT(*) FROM orders WHERE user_id = 1;

Expected: 1 (not 0, not 2)
```

---

## 🔍 BROWSER CONSOLE DEBUGGING

Open DevTools (F12) → Console tab:

Look for these logs:
```
[Checkout] Fetched order: {...}  ← Shows order from API
[Checkout] Setting orderData: {...}  ← Shows what's being displayed
[Checkout] Cart data: {...}  ← Shows cart if no orderId
```

---

## ✅ SUCCESS CRITERIA

All should be TRUE:

- [ ] Marketplace courses page loads and shows cart icon
- [ ] Can add courses to cart
- [ ] Cart count updates on marketplace page
- [ ] Digital products page loads and shows cart icon
- [ ] Can add digital products to cart
- [ ] Cart page shows all items with correct total
- [ ] Checkout URL shows: /checkout?orderId=X (X is number)
- [ ] Checkout page shows order summary (NOT "cart is empty")
- [ ] Payment form displays or "Preparing payment..." shows
- [ ] Can enter test card details
- [ ] Payment processes without errors
- [ ] Redirects to confirmation page
- [ ] Database shows exactly 1 order (not 2)

---

## 🐛 TROUBLESHOOTING

### "Your cart is empty" on checkout page:
1. Check browser console (F12) for `[Checkout]` logs
2. Verify orderId in URL is a number, not "undefined"
3. Hard refresh: Ctrl+Shift+R
4. Restart frontend: npm run dev

### Cart icon not showing:
1. Clear browser cache: Ctrl+Shift+Delete
2. Hard refresh: Ctrl+Shift+R
3. Check console for errors

### Can't add to cart:
1. Make sure logged in
2. Check backend is running (http://localhost:8001)
3. Look at Network tab (F12) to see API response

### orderId still undefined:
1. Check that cart has items before checkout
2. Verify /api/v1x/marketplace/checkout returns order_id field
3. Check console logs for errors

---

## 📞 QUICK SUPPORT

**Still broken? Provide:**
1. Browser console errors (F12 → Console tab)
2. Network errors (F12 → Network tab)
3. URL you're trying to access
4. What step failed

---

**Status:** 🟢 READY TO TEST  
**Last Updated:** 2026-01-29  
**Test Time Estimate:** 15-20 minutes total
