# Week 1 - Payment System - Quick Reference Card

## Status: PHASE 1 COMPLETE ✅

All backend payment endpoints working and tested.

---

## Backend API Endpoints

### 1. Create Order
**POST** `/api/v1x/orders/create`
```json
{
  "course_id": 1,
  "payment_method": "stripe"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": 8,
    "order_number": "ORD-12-1-e3117200",
    "amount": 49.99,
    "status": "pending",
    "payment_status": "pending"
  }
}
```

### 2. Create Payment Intent
**POST** `/api/v1x/orders/create-payment-intent`
```json
{
  "order_id": 8
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "client_secret": "pi_3Ss9jG...secret",
    "payment_intent_id": "pi_3Ss9jG...",
    "amount": 49.99
  }
}
```

### 3. Confirm Payment
**POST** `/api/v1x/orders/confirm-payment`
```json
{
  "order_id": 8,
  "payment_intent_id": "pi_3Ss9jG..."
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "order_id": 8,
    "status": "completed",
    "access_granted": true
  }
}
```

### 4. Get User Orders
**GET** `/api/v1x/orders/my-orders`
**Response:** List of user's orders with details

### 5. Get Order Details
**GET** `/api/v1x/orders/{order_id}`
**Response:** Single order with full details

---

## Stripe Test Credentials

**Public Key:** `pk_test_51SkcWEBydMsdVDYvDjEH5cNq0BO8VbYGcTq64NdlpvxFwaGaaaUIrKDFrTAAV4TrNYAAz3JdOvRFcDz8PWQLBc3K00kQDXwyCd`

**Test Card (succeeds):**
- Number: `4242 4242 4242 4242`
- Exp: `12/25`
- CVC: `123`

---

## Files Created This Session

| File | Purpose | Status |
|------|---------|--------|
| `backend/app/api/v1x/orders_db.py` | Payment endpoints | ✅ Complete |
| `backend/test_payment_quick.py` | Test verification | ✅ Passing |
| `WEEK1_PAYMENT_COMPLETE.md` | Full documentation | ✅ Done |
| `WEEK1_FRONTEND_CHECKOUT_GUIDE.md` | Frontend guide | ✅ Ready |
| `WEEK1_STATUS_UPDATE.md` | Progress report | ✅ Done |

---

## Database Schema

**orders table fields:**
- `id` - PK
- `user_id` - FK User
- `course_id` - FK Course
- `order_number` - Unique string
- `amount` - Decimal
- `currency` - String (USD)
- `status` - pending/completed/failed
- `payment_status` - pending/completed/failed
- `payment_id` - Stripe payment ID
- `payment_method` - "stripe"
- `created_at` - DateTime
- `paid_at` - DateTime

---

## Testing Commands

### Run Full Test Suite
```bash
cd backend
python test_payment_quick.py
```

### Start Backend Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Test Single Endpoint
```bash
curl -X POST http://localhost:8001/api/v1x/orders/create \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"course_id":1,"payment_method":"stripe"}'
```

### Check Database
```bash
sqlite3 backend/app/data/skillforge.db
SELECT * FROM orders WHERE user_id = 12;
```

---

## Frontend Next Steps (5 hours)

1. **Create Checkout Page** (`src/pages/checkout.tsx`)
   - Show course details
   - Create order
   - Display payment form
   - Confirm payment
   - Show success message

2. **Setup Stripe.js** in Next.js
   - Install: `npm install @stripe/stripe-js @stripe/react-stripe-js`
   - Add Elements provider in `_app.tsx`
   - Use CardElement in payment form

3. **Build Components**
   - `CheckoutForm` - Order + payment
   - `PaymentForm` - Stripe integration
   - `OrderConfirmation` - Success screen

4. **Test Flow**
   - Select course
   - Enter card details
   - Confirm payment
   - See success and order in /orders

---

## Key Integration Points

**Authentication:**
- All endpoints require JWT Bearer token
- Use existing `get_current_user` dependency

**Stripe Integration:**
- StripeService creates payment intents
- Stores payment ID in Order model
- Confirm payment verifies with Stripe

**Event System:**
- `on_course_enrolled` triggered on payment
- Grants user access to course
- Sends confirmation email

**Error Handling:**
- All inputs validated
- HTTPException with proper status codes
- Database rollback on error

---

## Current Progress (Week 1)

```
Payments Backend:        ████████████████░░░░░░  90%
Frontend Checkout:       ░░░░░░░░░░░░░░░░░░░░░░   0%
Order Confirmation:      ░░░░░░░░░░░░░░░░░░░░░░   0%
Mentor Booking:          ░░░░░░░░░░░░░░░░░░░░░░   0%

Total: 13/25 hours (52%)
```

---

## Production Ready?

**Backend:** YES ✅
- All endpoints working
- Tests passing
- Error handling complete
- Stripe configured

**Frontend:** NO ⏳
- Not started
- Guide provided
- Templates ready
- 4-5 hours to complete

---

## Quick Checklist for Frontend Dev

- [ ] Install Stripe libraries
- [ ] Create checkout page
- [ ] Build payment form
- [ ] Integrate CardElement
- [ ] Handle payment flow
- [ ] Show confirmation
- [ ] Test with 4242 4242 4242 4242
- [ ] Verify order in database
- [ ] Test order history
- [ ] Test order details page

---

## Support Resources

- **API Docs:** `WEEK1_PAYMENT_COMPLETE.md`
- **Frontend Guide:** `WEEK1_FRONTEND_CHECKOUT_GUIDE.md`
- **Test Script:** `backend/test_payment_quick.py`
- **Status Updates:** `WEEK1_STATUS_UPDATE.md`

---

**Last Updated:** January 22, 2026
**Backend Status:** ✅ OPERATIONAL
**Next Phase:** Frontend Checkout (Ready to start)
**Estimated Time to Complete:** 5 hours

