# 🧪 MARKETPLACE FIXES - TEST & VERIFICATION GUIDE

**Date**: January 29, 2026  
**Status**: Endpoint fixes applied - Ready for testing

---

## ✅ FIXES APPLIED

1. ✅ Course add-to-cart endpoint: `/marketplace/cart/add`
2. ✅ Course field name: `course_id` (not `product_id`)
3. ✅ Digital product endpoint: `/marketplace/digital-products/{id}/purchase`
4. ✅ All 4 marketplace pages updated

---

## 🧪 STEP-BY-STEP TEST PROCEDURE

### Test 1: Add Course to Cart (From List)

```
STEP 1: Open marketplace
  URL: http://localhost:3000/marketplace
  Expected: See 5-6 courses displayed
  Result: _______________

STEP 2: Click "Add to Cart" on Python Fundamentals
  Action: Click button
  Expected: Button shows "Adding..."
  Result: _______________

STEP 3: Wait for response
  Wait: 2-3 seconds
  Expected: Shows "✓ Added to cart successfully!"
  Result: _______________

STEP 4: Check network tab (F12)
  Action: Open DevTools → Network tab
  Check: POST to /api/v1x/marketplace/cart/add
  Body: {"course_id": 1}
  Status: 200 OK
  Result: _______________
```

### Test 2: Add Course to Cart (From Details Page)

```
STEP 1: Click "View Details" on a course
  Action: Click button
  Expected: Load /courses/[path]
  Result: _______________

STEP 2: Click "Add to Cart"
  Action: Click button on course details
  Expected: Button shows "Adding..."
  Result: _______________

STEP 3: Check for success
  Expected: "✓ Added to cart successfully!"
  Result: _______________

STEP 4: Check network tab
  Check: POST to /api/v1x/marketplace/cart/add
  Body: {"course_id": 1}
  Status: 200 OK
  Result: _______________
```

### Test 3: Add Digital Product (From List)

```
STEP 1: Go to digital products
  URL: http://localhost:3000/marketplace/digital-products
  Expected: See 3-6 products
  Result: _______________

STEP 2: Click "Add to Cart" or "Purchase"
  Action: Click button
  Expected: Button shows "Adding..." or "Purchasing..."
  Result: _______________

STEP 3: Check for completion
  Expected: "✓ Added to cart!" or "✓ Purchased!"
  Result: _______________

STEP 4: Check network tab
  Check: POST to /api/v1x/marketplace/digital-products/{id}/purchase
  Status: 200 OK
  Body sent: {}
  Result: _______________
```

### Test 4: Add Digital Product (From Details)

```
STEP 1: Click on a product
  Action: Click product name or details link
  Expected: Load /marketplace/digital-products/[id]
  Result: _______________

STEP 2: Click "Add to Cart" or "Purchase"
  Action: Click button
  Expected: Shows loading state
  Result: _______________

STEP 3: Check success message
  Expected: "✓ Purchased successfully!" or "✓ Added to cart!"
  Result: _______________

STEP 4: Check network tab
  Check: POST to /api/v1x/marketplace/digital-products/{id}/purchase
  Status: 200 OK
  Result: _______________
```

### Test 5: View Cart

```
STEP 1: Go to cart
  URL: http://localhost:3000/marketplace/cart
  Expected: See items added
  Result: _______________

STEP 2: Check items display
  Expected: 
    - Course: Python Fundamentals $49.99 (if added)
    - Product: Python Cheat Sheet $9.99 (if added)
  Result: _______________

STEP 3: Check totals
  Expected:
    - Subtotal: (sum of prices)
    - Tax: (calculated)
    - Total: (subtotal + tax)
  Result: _______________

STEP 4: Test remove button
  Action: Click "Remove" on an item
  Expected: Item disappears, totals recalculate
  Result: _______________
```

### Test 6: Checkout Flow

```
STEP 1: Proceed to checkout
  Action: Click "Proceed to Checkout" button
  Expected: Load /marketplace/checkout
  Result: _______________

STEP 2: Check order summary
  Expected:
    - Order number: ORD-...
    - Subtotal: $
    - Tax: $
    - Total: $
  Result: _______________

STEP 3: Check payment form
  Expected: See Stripe payment form
  Result: _______________

STEP 4: Enter test payment
  Card: 4242 4242 4242 4242
  Expiry: 12/25
  CVC: 123
  Expected: Payment form accepts input
  Result: _______________

STEP 5: Click "Pay" or "Complete Payment"
  Action: Submit form
  Expected: Processing... then redirect
  Result: _______________
```

### Test 7: View Orders

```
STEP 1: Go to orders page
  URL: http://localhost:3000/marketplace/orders
  Expected: Load /marketplace/orders
  Result: _______________

STEP 2: Check order displays
  Expected: See purchased order with:
    - Order number
    - Status
    - Amount
    - Payment status
  Result: _______________

STEP 3: Check order details
  Expected: See course/product info
  Result: _______________
```

---

## 🔍 DEBUGGING CHECKLIST

If a test fails, check these:

### Add-to-Cart Fails

```
Check 1: Network tab (F12 → Network)
  ✓ Request sent to correct endpoint?
  ✓ Status code is 200?
  ✓ Response has { message: "..." }?

Check 2: Console (F12 → Console)
  ✓ Any red error messages?
  ✓ Any 404 errors?
  ✓ Any CORS errors?

Check 3: Backend running
  ✓ Try: curl http://localhost:8001/api/v1x/marketplace/cart
  ✓ Should return empty cart or user's cart
  ✓ If error, backend not running

Check 4: API base URL
  ✓ In .env.local: NEXT_PUBLIC_API_BASE=http://localhost:8001
  ✓ Refresh page after changing .env
  ✓ Check in Network tab that requests go to localhost:8001
```

### Checkout Fails

```
Check 1: Stripe key configured
  ✓ NEXT_PUBLIC_STRIPE_KEY in .env.local
  ✓ Valid publishable key format

Check 2: Payment form appears
  ✓ See Stripe card input in checkout page
  ✓ No console errors about Stripe

Check 3: Test payment
  ✓ Card: 4242 4242 4242 4242 (success)
  ✓ Card: 4000 0000 0000 0002 (decline to test failure)
  ✓ Card: 4000 0000 0000 9995 (requires auth)

Check 4: Order created
  ✓ After payment, order appears in /marketplace/orders
  ✓ Status shows "completed" or "pending"
```

### Orders Not Showing

```
Check 1: Logged in
  ✓ User logged in? Check profile page
  ✓ If not logged in, login first

Check 2: Orders endpoint
  ✓ Try: curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/v1x/marketplace/orders
  ✓ Should return list of orders

Check 3: Auth token
  ✓ Credentials: 'include' in fetch
  ✓ Login session valid
  ✓ Check browser cookies for auth token
```

---

## 📊 RESULTS SUMMARY

Fill in your test results:

```
Test 1: Add Course (from list)     ☐ Pass ☐ Fail
Test 2: Add Course (from details)  ☐ Pass ☐ Fail
Test 3: Add Product (from list)    ☐ Pass ☐ Fail
Test 4: Add Product (from details) ☐ Pass ☐ Fail
Test 5: View Cart                  ☐ Pass ☐ Fail
Test 6: Checkout                   ☐ Pass ☐ Fail
Test 7: View Orders                ☐ Pass ☐ Fail

Overall Status: ☐ All Pass ☐ Some Failures ☐ Critical Issues
```

---

## 🎯 WHAT SHOULD HAPPEN

### Correct Course Add-to-Cart
```
1. User clicks "Add to Cart"
2. Frontend sends: POST /api/v1x/marketplace/cart/add
   Body: { "course_id": 1 }
3. Backend responds: { "message": "Course added to cart", ... }
4. Frontend shows: "✓ Added to cart successfully!"
5. Cart count increases
6. Button changes to "View in Cart"
```

### Correct Digital Product Purchase
```
1. User clicks "Purchase"
2. Frontend sends: POST /api/v1x/marketplace/digital-products/1/purchase
   Body: {}
3. Backend responds: { "id": ..., "status": "completed", ... }
4. Frontend shows: "✓ Purchased successfully!"
5. Product immediately available
6. No checkout needed
```

---

## ❌ WHAT MIGHT BE WRONG

| Issue | Check |
|-------|-------|
| "404 Not Found" on add-to-cart | Endpoint is `/cart/add` not `/cart` ✅ |
| "Invalid field" error | Should be `course_id` not `product_id` ✅ |
| Stripe payment form not showing | Check NEXT_PUBLIC_STRIPE_KEY in .env |
| Order not showing in /orders | Check authentication, try logout/login |
| Cart shows no items | Verify GET /api/v1x/marketplace/cart works |
| Payment fails immediately | Check test card number (should be 4242...) |

---

## 📞 REPORT YOUR RESULTS

When you've completed testing, share:

1. **Which tests passed** ✅
2. **Which tests failed** ❌
3. **Error messages from console** (F12 → Console)
4. **Network request details** (F12 → Network)
5. **Backend response** (what the API returned)

This will help identify remaining issues!

---

## 🚀 READY TO TEST?

1. ✅ Endpoint fixes applied
2. ✅ Code compiles (no TypeScript errors)
3. ✅ Backend is running (http://localhost:8001)
4. ✅ Frontend is running (http://localhost:3000)
5. ✅ Test guide ready

**GO TEST THE MARKETPLACE!** 🎊
