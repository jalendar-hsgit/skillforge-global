# Checkout Payment Flow - Quick Test Guide

## 🎯 What Was Fixed
1. **orderId=undefined bug** - Checkout page now reads URL params correctly
2. **Duplicate orders** - Only 1 order created per purchase (not 2)
3. **Coupon validation** - `/apply-coupon` endpoint added to backend

---

## 🚀 Quick Test (5 minutes)

### Step 1: Start Services
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend  
npm run dev
# Visit http://localhost:3000
```

### Step 2: Test Single Order Creation
```
1. Go to /marketplace or /courses
2. Add a course to cart
3. Click "Proceed to Checkout"
   Expected: Navigate to /marketplace/checkout?orderId=5
4. Check database:
   sqlite3 backend/app/data/skillforge.db
   SELECT COUNT(*) FROM orders WHERE user_id = 1;
   Expected: 1 row (not 2)
```

### Step 3: Test Coupon Validation
```
1. In checkout page, find coupon input
2. Try invalid coupon: "INVALID123"
   Expected: ✗ Invalid coupon code (error clears after 3s)
3. Try valid coupon: "SAVE10" (or create one in DB)
   Expected: ✓ Coupon applied successfully! (clears after 3s)
```

### Step 4: Test Payment
```
1. Enter test card: 4242 4242 4242 4242
2. Expiry: 12/25 (or any future date)
3. CVC: 123 (any 3 digits)
4. Cardholder: Any name
5. Click "Pay"
   Expected: Payment processes successfully
   Redirect to: /marketplace/order-confirmation/5
```

---

## 🔍 Verification Queries

### Database - Check Order Count
```sql
-- Should return 1 row per purchase (not 2)
SELECT id, order_number, status, amount, created_at 
FROM orders 
WHERE user_id = 1 
ORDER BY created_at DESC 
LIMIT 5;
```

### Database - Check Coupon Validation
```sql
SELECT code, discount_type, discount_value, is_active, usage_count, usage_limit 
FROM coupons 
WHERE code = 'SAVE10';
```

### API Test - Create Order
```bash
curl -X POST http://localhost:8001/api/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your_session_id>" \
  -d '{
    "payment_method": "stripe",
    "coupon_code": null
  }'

# Expected Response:
# {
#   "order_id": 5,
#   "order_number": "ORD-123...",
#   "total_amount": 99.99,
#   "status": "pending",
#   "client_secret": "pi_...",
#   ...
# }
```

### API Test - Validate Coupon
```bash
curl -X POST http://localhost:8001/api/v1x/marketplace/apply-coupon \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your_session_id>" \
  -d '{ "coupon_code": "SAVE10" }'

# Expected Response:
# {
#   "valid": true,
#   "code": "SAVE10",
#   "discount_type": "percentage",
#   "discount_value": 10.0,
#   "message": "Coupon applied successfully!"
# }
```

### API Test - Fetch Order
```bash
curl http://localhost:8001/api/v1x/marketplace/orders/5 \
  -H "Cookie: session=<your_session_id>"

# Expected Response:
# {
#   "id": 5,
#   "order_number": "ORD-...",
#   "total_amount": 89.99,
#   "status": "pending",
#   "client_secret": "pi_...",
#   ...
# }
```

---

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `orderId=undefined` in URL | Checkout page not reading query params | ✅ FIXED - page now reads `router.query.orderId` |
| 2 orders in database | Checkout created duplicate order | ✅ FIXED - page fetches existing order instead |
| Coupon validation fails | Endpoint `/apply-coupon` didn't exist | ✅ FIXED - endpoint added to backend |
| Payment form doesn't show | `client_secret` missing from order | Ensure backend returns `client_secret` in response |
| Redirect to confirmation fails | Order confirmation page missing | Check `/marketplace/order-confirmation/[id].tsx` exists |

---

## ✅ Success Criteria

- [ ] Add course to cart
- [ ] Click "Proceed to Checkout"
- [ ] URL shows `/marketplace/checkout?orderId=5` (not undefined)
- [ ] Checkout page loads payment form
- [ ] Can apply coupon (shows success message)
- [ ] Can enter card details
- [ ] Payment processes with test card
- [ ] Redirect to confirmation page
- [ ] Database shows only 1 order (not 2)
- [ ] Order status is "pending" → "succeeded"

---

## 🔗 Related Files

- **Frontend:** `src/pages/marketplace/checkout.tsx` (Fixed)
- **Frontend:** `src/pages/marketplace/cart.tsx` (No changes needed)
- **Backend:** `backend/app/api/v1x/marketplace.py` (Added `/apply-coupon`)
- **Backend:** `backend/app/api/v1x/marketplace_checkout.py` (Existing, works correctly)

---

## 📞 Support

If tests fail:
1. Check browser console for errors
2. Check backend logs: `uvicorn app.main:app --reload`
3. Verify session cookie is set: `document.cookie` in console
4. Clear cache: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
5. Restart both servers

---

**Last Updated:** 2024-01-28  
**Status:** Ready for Testing ✅
