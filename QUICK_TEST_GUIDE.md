# Quick Test Guide - New Endpoints & Components

**Quick Links:**
- Admin Endpoints: Test with admin user account
- Payment Endpoints: Test with non-admin user account
- Frontend: Test with browser dev tools

---

## 1. Backend - Admin Marketplace Endpoints

### Test 1: Get Total Revenue (Admin Only)
```bash
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/revenue" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```
**Expected Response (200):**
```json
{
  "total_revenue": 4500.00,
  "total_orders": 45,
  "total_sellers": 8,
  "total_products": 24,
  "net_revenue": 4050.00,
  "refund_amount": 450.00
}
```

### Test 2: Get Revenue By Seller (Admin Only, with Pagination)
```bash
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/revenue-by-seller?skip=0&limit=10&sort_by=revenue" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```
**Expected Response (200):**
```json
{
  "sellers": [
    {
      "seller_id": 5,
      "seller_name": "Alice Johnson",
      "total_revenue": 1500.00,
      "order_count": 15,
      "product_count": 5,
      "average_rating": 4.8
    }
  ],
  "total": 8Mentor Booking Flow - Complete the frontend for booking sessions
}
```

### Test 3: Get Payouts (Admin Only)
```bash
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/payouts?seller_id=5&status=pending" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```
**Expected Response (200):**
```json
{
  "payouts": [
    {
      "payout_id": "payout_123",
      "seller_id": 5,
      "amount": 500.00,
      "status": "pending",
      "created_at": "2026-01-10T10:00:00",
      "processed_at": null
    }
  ],
  "total": 1
}
```

### Test 4: Process Payout (Admin Only)
```bash
curl -X POST "http://localhost:8001/api/v1x/admin/marketplace/process-payout" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "seller_id": 5,
    "amount": 500.00
  }'
```
**Expected Response (200):**
```json
{
  "payout_id": "payout_456",
  "seller_id": 5,
  "amount": 500.00,
  "status": "processing",
  "created_at": "2026-01-10T10:05:00"
}
```

### Test 5: Get Refunds (Admin Only)
```bash
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/refunds?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```
**Expected Response (200):**
```json
{
  "refunds": [
    {
      "refund_id": "refund_001",
      "order_id": 123,
      "amount": 99.99,
      "reason": "not_satisfied",
      "created_at": "2026-01-10T10:10:00",
      "status": "completed"
    }
  ],
  "total_refunded": 450.00,
  "count": 5
}
```

### Test 6: Get Marketplace Analytics (Admin Only)
```bash
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/analytics/summary?days=30" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```
**Expected Response (200):**
```json
{
  "period_days": 30,
  "period_revenue": 4500.00,
  "total_orders": 45,
  "unique_sellers": 8,
  "unique_buyers": 25,
  "avg_order_value": 100.00,
  "top_sellers": [
    {
      "seller_id": 5,
      "seller_name": "Alice Johnson",
      "revenue": 1500.00
    }
  ],
  "top_products": [
    {
      "product_id": 12,
      "product_name": "Python Course",
      "sales": 50
    }
  ]
}
```

---

## 2. Backend - Payment Endpoints

### Test 1: Process Payment (User Only)
```bash
curl -X POST "http://localhost:8001/api/v1x/payments/process" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 100,
    "payment_method": "stripe"
  }'
```
**Expected Response (200):**
```json
{
  "success": true,
  "payment_id": "stripe_100_1705000000",
  "order_id": 100,
  "status": "completed",
  "amount": 99.99,
  "provider": "stripe",
  "paid_at": "2026-01-10T10:00:00"
}
```

### Test 2: Request Refund (User Only, Order Owner)
```bash
curl -X POST "http://localhost:8001/api/v1x/payments/refund" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 100,
    "amount": null,
    "reason": "not_satisfied"
  }'
```
**Expected Response (200):**
```json
{
  "success": true,
  "refund_id": "refund_001",
  "order_id": 100,
  "amount": 99.99,
  "status": "refunded",
  "message": "Refund processed successfully"
}
```

### Test 3: Check Payment Status (User Only)
```bash
curl -X GET "http://localhost:8001/api/v1x/payments/status/100" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected Response (200):**
```json
{
  "payment_id": "stripe_100_1705000000",
  "order_id": 100,
  "status": "completed",
  "amount": 99.99,
  "provider": "stripe",
  "paid_at": "2026-01-10T10:00:00"
}
```

### Test 4: Stripe Webhook (No Auth Required)
```bash
curl -X POST "http://localhost:8001/api/v1x/payments/webhook/stripe" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment_intent.succeeded",
    "data": {
      "object": {
        "id": "pi_1234567890",
        "amount": 9999,
        "currency": "usd",
        "metadata": {
          "order_id": 100
        }
      }
    }
  }'
```
**Expected Response (200):**
```json
{
  "received": true,
  "status": "processing"
}
```

### Test 5: PayPal Webhook (No Auth Required)
```bash
curl -X POST "http://localhost:8001/api/v1x/payments/webhook/paypal" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "PAYMENT.CAPTURE.COMPLETED",
    "resource": {
      "id": "123456789",
      "amount": {
        "value": "99.99",
        "currency_code": "USD"
      },
      "custom_id": "100"
    }
  }'
```
**Expected Response (200):**
```json
{
  "received": true,
  "status": "processing"
}
```

---

## 3. Frontend - Seller Dashboard

### Access the Page
```
http://localhost:3000/seller/dashboard
```

### What Should Display
1. ✅ **Loading Spinner** (while fetching data)
2. ✅ **4 Metric Cards:**
   - Total Sales (number)
   - Total Revenue (currency)
   - Average Rating (stars)
   - Total Products (number)
3. ✅ **Revenue Trend Chart**
   - Line chart showing last 30 days
   - X-axis: dates
   - Y-axis: revenue
4. ✅ **Top Products Section**
   - List of best-selling products
   - Sales count per product
5. ✅ **Recent Orders Table**
   - Order ID, customer, amount, date
   - Status badge (completed, pending, etc)

### Test User Flow
1. Login to a seller account
2. Navigate to `/seller/dashboard`
3. Verify all data loads correctly
4. Check no errors in browser console (F12)
5. Verify API calls in Network tab (F12 → Network)

### Expected API Calls (Network Tab)
```
GET /api/v1x/seller/dashboard → 200
GET /api/v1x/seller/orders → 200
GET /api/v1x/seller/analytics/timeline → 200
```

---

## 4. Frontend - Marketplace Checkout

### Access the Page
```
http://localhost:3000/marketplace/checkout
```

### What Should Display
1. ✅ **Cart Items Section**
   - List of products in cart
   - Quantity and price for each
   - Subtotal
2. ✅ **Coupon Code Input**
   - Text input field
   - "Apply" button
   - Discount display if applied
3. ✅ **Order Summary Sidebar**
   - Subtotal
   - Discount (if any)
   - Shipping (FREE)
   - Total amount
4. ✅ **Payment Method Selection**
   - Radio buttons for Stripe and PayPal
5. ✅ **Checkout Button**
   - "Pay $X.XX" button
   - Disabled while processing

### Test User Flow
1. Add products to cart (localStorage test)
2. Navigate to `/marketplace/checkout`
3. Try applying a coupon
4. Select payment method
5. Click "Pay" button
6. Verify success message or error handling
7. Check Network tab for API calls

### Expected API Calls
```
POST /api/v1x/marketplace/validate-coupon → 200 (with valid coupon)
POST /api/v1x/marketplace/checkout → 200
POST /api/v1x/payments/process → 200
Redirect to /orders/{order_id} → success page
```

---

## 5. Frontend - Order Details & Tracking

### Access the Page (After Checkout)
```
http://localhost:3000/orders/100
```

### What Should Display
1. ✅ **Order Header**
   - Order number
   - Order ID
2. ✅ **Status Card**
   - Large status display with emoji
   - Status color (green=completed, yellow=pending, etc)
   - Total amount
3. ✅ **Order Timeline**
   - "Order Placed" with date
   - "Payment Completed" with date (if paid)
   - "Refunded" status (if applicable)
4. ✅ **Payment Information**
   - Payment ID
   - Provider (Stripe/PayPal)
   - Amount
   - Status
5. ✅ **Refund Request Form** (if order is completed)
   - Dropdown: Reason for refund
   - Input: Optional refund amount
   - Button: "Request Refund"
6. ✅ **Order Summary**
   - Order number, payment method, dates
   - Total amount

### Test User Flow
1. Complete a purchase (checkout flow)
2. Verify redirected to `/orders/{id}`
3. Check all order details display
4. Try requesting a refund
5. Verify success message
6. Check Network tab for API calls

### Expected API Calls
```
GET /api/v1x/orders/{id} → 200
GET /api/v1x/payments/status/{id} → 200
POST /api/v1x/payments/refund → 200 (with refund request)
```

---

## 6. Error Testing

### Test Missing Authentication
```bash
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/revenue"
```
**Expected Response (401):**
```json
{"detail": "Not authenticated"}
```

### Test Insufficient Permissions
```bash
# Using non-admin token on admin endpoint
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/revenue" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected Response (403):**
```json
{"detail": "Admin access required"}
```

### Test Invalid Order ID
```bash
curl -X GET "http://localhost:8001/api/v1x/payments/status/99999" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected Response (404):**
```json
{"detail": "Order not found"}
```

### Test Refund on Non-Completed Order
```bash
curl -X POST "http://localhost:8001/api/v1x/payments/refund" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 50}'
```
**Expected Response (400):**
```json
{"detail": "Cannot refund pending order"}
```

---

## 7. Browser Developer Tools Testing

### Console (F12 → Console)
✅ No red errors  
✅ No failed API calls (404, 500)  
✅ localStorage shows auth token  

### Network Tab (F12 → Network)
✅ All API requests return 2xx status  
✅ Response times < 1 second  
✅ Content-Type headers correct  
✅ Authorization headers sent  

### Performance (F12 → Performance)
✅ Page loads in < 3 seconds  
✅ No layout thrashing  
✅ Smooth animations  

---

## 8. Test Data Needed

### For Admin Testing
```
Admin Email: admin@skillforge.com
Admin Password: (from seed data)
Role: ADMIN or SUPERADMIN
```

### For Seller Testing
```
Seller Email: seller1@example.com
Role: MENTOR or SELLER
```

### For Buyer Testing
```
Buyer Email: buyer@example.com
Role: USER
```

### Get Test Accounts
```bash
# Run seed script to create test data
python backend/seed_all_demo_data.py
```

---

## 9. Common Issues & Solutions

### Issue: 401 Unauthorized on Admin Endpoints
**Cause:** Token expired or not sent  
**Fix:** Login again to get fresh token

### Issue: 403 Forbidden on Admin Endpoints
**Cause:** Using non-admin user token  
**Fix:** Use admin account to login

### Issue: Checkout Button Does Nothing
**Cause:** Cart is empty  
**Fix:** Add items to cart first (localStorage)

### Issue: Payment Processing Stuck
**Cause:** Network request failing  
**Fix:** Check Network tab, verify API is running

### Issue: Refund Option Not Showing
**Cause:** Order not in "completed" status  
**Fix:** Verify order.status == "completed"

---

## 10. Success Criteria

### ✅ All Tests Pass When:

**Backend:**
- [ ] All admin endpoints return correct data with admin token
- [ ] All admin endpoints return 403 with user token
- [ ] Payment endpoints process correctly
- [ ] Refund endpoints work for order owners
- [ ] Webhooks accept POST requests

**Frontend:**
- [ ] Seller dashboard loads and displays metrics
- [ ] Checkout page completes order
- [ ] Order tracking page shows details
- [ ] Refund request form works
- [ ] No console errors
- [ ] All API responses load correctly

**Integration:**
- [ ] Checkout creates order and processes payment
- [ ] Payment updates order status
- [ ] Refund updates order status
- [ ] Admin can see all transactions
- [ ] Seller dashboard shows accurate data

---

## Running Tests in Order

### Step 1: Backend API Tests (5 min)
```bash
# Test each admin endpoint with curl
# Expected: All return 200 with data
```

### Step 2: Frontend Component Tests (10 min)
```bash
# Visit each page in browser
# Expected: All load without errors
```

### Step 3: End-to-End Tests (15 min)
```bash
# Complete full checkout flow
# Expected: Success message and order tracking page
```

### Step 4: Error Case Tests (10 min)
```bash
# Try invalid inputs, missing auth, etc
# Expected: Proper error messages
```

**Total Time: ~40 minutes**

---

## Documentation

- Full details: [IMPLEMENTATION_TEST_RESULTS.md](IMPLEMENTATION_TEST_RESULTS.md)
- API docs: [Backend endpoints section above]
- Component docs: [Frontend components section above]

**Status: Ready for testing ✅**
