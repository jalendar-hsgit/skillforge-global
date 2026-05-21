# CHECKOUT PAYMENT FLOW - MANUAL TEST EXECUTION

## Test Date: 2024-01-29
## Status: IN PROGRESS

---

## 🎯 Test Objectives

1. ✅ Verify orderId is NOT undefined in checkout URL
2. ✅ Verify ONLY 1 order created (not 2)
3. ✅ Verify coupon validation works
4. ✅ Verify payment processing succeeds
5. ✅ Verify redirect to confirmation page works

---

## 📋 Test Steps

### Phase 1: Service Setup
- [ ] Backend running on port 8001
- [ ] Frontend running on port 3000
- [ ] Both services initialized without errors

### Phase 2: Cart Flow
- [ ] Log in to application
- [ ] Navigate to marketplace
- [ ] Add course to cart
- [ ] Verify cart shows item

### Phase 3: Checkout Creation
- [ ] Click "Proceed to Checkout"
- [ ] Verify URL contains `?orderId=` (not undefined)
- [ ] Note the orderId value

### Phase 4: Coupon Validation
- [ ] Try invalid coupon: "INVALID123"
- [ ] Verify error message appears and auto-clears
- [ ] Try valid coupon (if exists in DB)
- [ ] Verify success message appears and auto-clears

### Phase 5: Payment Processing
- [ ] Enter test card: 4242 4242 4242 4242
- [ ] Enter expiry: 12/25 (future date)
- [ ] Enter CVC: 123
- [ ] Click "Pay"
- [ ] Verify payment processing animation
- [ ] Verify no errors in browser console

### Phase 6: Confirmation
- [ ] Verify redirect to order confirmation page
- [ ] Verify orderId in confirmation URL matches checkout
- [ ] Verify order details displayed correctly

### Phase 7: Database Verification
- [ ] Query orders table
- [ ] Verify only 1 order created (not 2)
- [ ] Verify order status matches payment result
- [ ] Verify order amount is correct

---

## 🔍 Expected Results

### URL Verification
```
CHECKOUT URL:
Before Fix: /marketplace/checkout?orderId=undefined
After Fix:  /marketplace/checkout?orderId=5
Status: ✅ PASS (if orderId is a number, not undefined)
```

### Database Count
```
Query: SELECT COUNT(*) FROM orders WHERE user_id = 1;
Before Fix: 2 orders
After Fix:  1 order
Status: ✅ PASS (only 1 order per purchase)
```

### Coupon Response
```
Request: POST /api/v1x/marketplace/apply-coupon
Payload: { "coupon_code": "SAVE10" }
Response: { "valid": true, "message": "Coupon applied successfully!" }
Status: ✅ PASS (coupon validates and returns response)
```

### Payment Intent
```
Order should contain:
- order_id: <number>
- order_number: ORD-...-...
- client_secret: pi_... (from Stripe)
- status: "pending"
Status: ✅ PASS (payment intent created)
```

---

## 📊 Test Results

### Result Summary
- [ ] All tests passed
- [ ] Minor issues (document below)
- [ ] Major issues found (see troubleshooting)

### Test Metrics
```
Total Test Steps: 25
Passed: ____ / 25
Failed: ____ / 25
Duration: ____ minutes
```

### Issues Found
```
(List any issues found during testing)
1. 
2. 
3. 
```

---

## 🐛 Troubleshooting

### If orderId is still undefined:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Restart frontend server
3. Check browser console for errors
4. Verify router.query is properly populated

### If 2 orders are created:
1. Check that checkout.tsx changes were saved
2. Verify loadCheckout() is reading orderId from router.query
3. Check if fallback code path is being executed

### If coupon validation fails:
1. Verify backend has /apply-coupon endpoint
2. Check if request/response format matches
3. Create test coupon in database if needed:
   ```sql
   INSERT INTO coupons (code, discount_type, discount_value, is_active)
   VALUES ('SAVE10', 'percentage', 10.0, 1);
   ```

### If payment doesn't process:
1. Check Stripe test keys are configured
2. Verify client_secret is returned from /checkout
3. Check Stripe Elements initialization
4. Review browser console for Stripe errors

---

## ✅ Sign-Off

**Tested By:** [Name]
**Date:** 2024-01-29
**Overall Status:** [ ] PASS [ ] FAIL [ ] PARTIAL

**Notes:**
```
(Add any additional notes or observations)
```

---

**Test Execution Time:** _____ minutes
**Ready for Deployment:** [ ] YES [ ] NO [ ] NEEDS REVIEW
