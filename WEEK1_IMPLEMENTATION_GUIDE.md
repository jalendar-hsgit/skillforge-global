# WEEK 1: REVENUE FOUNDATION - IMPLEMENTATION GUIDE

**Status:** Week 1 Implementation Started - January 22, 2026  
**Backend Server:** ✅ Running on http://localhost:8001  
**Stripe Keys:** ✅ Configured  
**Goal:** Complete payment processing, course orders, and mentor booking

---

## 📊 IMPLEMENTATION CHECKLIST

### Phase 1: Payment Processing (In Progress)

#### Backend: payments_integrated.py Enhancements
- [ ] Verify Stripe API key loaded from environment
- [ ] Test `/payments/create-payment-intent` endpoint
- [ ] Test `/payments/confirm-charge` endpoint
- [ ] Add webhook handler for Stripe events
- [ ] Test payment intent creation
- [ ] Test payment confirmation flow
- [ ] Add refund handling
- [ ] Add payment history retrieval

#### Database: Order Model
- [ ] Verify Order model has `stripe_payment_intent_id` field
- [ ] Verify Order model has `payment_status` field
- [ ] Verify Order model has `created_at` timestamp
- [ ] Test order creation

#### Testing: Stripe Integration
- [ ] Can create payment intent
- [ ] Test card charges with `4242 4242 4242 4242` (Stripe test card)
- [ ] Webhook receives payment confirmations
- [ ] Order status updates correctly
- [ ] User gains course access after payment

---

### Phase 2: Course Orders (Next)

#### Backend: orders_db.py Enhancements
- [ ] Create POST `/orders/create` endpoint
- [ ] Link order to payment system
- [ ] Create enrollment on successful payment
- [ ] Add order confirmation email
- [ ] Add order history endpoint
- [ ] Add order status endpoint

#### Frontend: Course Purchase Flow
- [ ] Create/update checkout page
- [ ] Add "Buy Course" button to course details
- [ ] Implement Stripe payment form
- [ ] Show payment confirmation
- [ ] Redirect to course on success
- [ ] Show error messages on failure

---

### Phase 3: Mentor Booking UI (After Orders)

#### Backend: Mentor Booking Endpoints
- [ ] Verify mentors endpoints exist
- [ ] Test availability checking
- [ ] Test session creation
- [ ] Test confirmation flow

#### Frontend: Mentor Booking Pages
- [ ] Create mentor availability calendar
- [ ] Create booking form
- [ ] Add confirmation interface
- [ ] Add booking history page
- [ ] Email notifications

---

### Phase 4: Testing & Verification

#### End-to-End Tests
- [ ] User can complete purchase
- [ ] Payment appears in Stripe dashboard
- [ ] Order created in database
- [ ] User gains access to course
- [ ] Course appears in "My Courses"

---

## 🚀 STEP-BY-STEP IMPLEMENTATION

### STEP 1: Verify Stripe Configuration

**File:** `backend/.env`  
**Status:** ✅ Already configured with your keys

```bash
STRIPE_PUBLIC_KEY=pk_test_51SkcWEBydMsdVDYvDjEH5cNq0BO8VbYGcTq64NdlpvxFwaGaaaUIrKDFrTAAV4TrNYAAz3JdOvRFcDz8PWQLBc3K00kQDXwyCd
STRIPE_SECRET_KEY=sk_test_REPLACE_ME
```

### STEP 2: Test Payment Intent Creation

**API Endpoint:** `POST /api/v1x/payments/create-payment-intent`

**Request:**
```json
{
  "session_id": 1,
  "amount": 49.99,
  "currency": "USD"
}
```

**Expected Response:**
```json
{
  "id": "payment_123",
  "client_secret": "pi_test_..._secret_...",
  "amount": 49.99,
  "currency": "USD",
  "status": "requires_payment_method"
}
```

### STEP 3: Create Order with Payment

**API Endpoint:** `POST /api/v1x/orders/create`

**Request:**
```json
{
  "course_id": 1,
  "payment_intent_id": "pi_test_...",
  "amount": 49.99
}
```

**Expected Response:**
```json
{
  "id": 1,
  "order_number": "ORD-1-1",
  "course_id": 1,
  "amount": 49.99,
  "status": "pending",
  "payment_status": "pending"
}
```

### STEP 4: Confirm Payment

**API Endpoint:** `POST /api/v1x/payments/confirm`

**Request:**
```json
{
  "payment_intent_id": "pi_test_...",
  "order_id": 1
}
```

**Expected Response:**
```json
{
  "status": "success",
  "order_id": 1,
  "payment_status": "completed",
  "access_granted": true
}
```

---

## 📱 FRONTEND IMPLEMENTATION

### Checkout Page (`src/pages/checkout.tsx`)

```typescript
import { useState } from 'react';
import { loadStripe } from '@stripe/js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY!);

export default function CheckoutPage() {
  const [loading, setLoading] = useState(false);
  const [courseId, setCourseId] = useState<number | null>(null);

  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm courseId={courseId} />
    </Elements>
  );
}

function CheckoutForm({ courseId }: { courseId: number | null }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements || !courseId) return;

    setLoading(true);

    try {
      // 1. Create order
      const orderRes = await fetch('/api/v1x/orders/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          course_id: courseId,
          amount: 49.99
        })
      });
      
      if (!orderRes.ok) throw new Error('Failed to create order');
      const { id: orderId } = await orderRes.json();

      // 2. Create payment intent
      const intentRes = await fetch('/api/v1x/payments/create-payment-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: orderId })
      });

      if (!intentRes.ok) throw new Error('Failed to create payment intent');
      const { client_secret } = await intentRes.json();

      // 3. Confirm payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: elements.getElement(CardElement)!,
          billing_details: { name: 'Customer' }
        }
      });

      if (stripeError) {
        setError(stripeError.message || 'Payment failed');
        return;
      }

      // 4. Confirm on backend
      const confirmRes = await fetch('/api/v1x/payments/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          payment_intent_id: paymentIntent?.id,
          order_id: orderId
        })
      });

      if (!confirmRes.ok) throw new Error('Failed to confirm payment');

      // 5. Redirect to course
      window.location.href = `/courses/${courseId}`;

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      <button disabled={!stripe || loading}>
        {loading ? 'Processing...' : 'Pay $49.99'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
}
```

---

## 🧪 TESTING THE PAYMENT FLOW

### Test with Stripe Test Card

**Card Number:** `4242 4242 4242 4242`  
**Expiry:** `12/25`  
**CVC:** `123`  
**Zip:** `12345`

### Using cURL to Test Endpoints

```bash
# 1. Create order
curl -X POST http://localhost:8001/api/v1x/orders/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"course_id": 1, "amount": 49.99}'

# 2. Create payment intent
curl -X POST http://localhost:8001/api/v1x/payments/create-payment-intent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"order_id": 1}'

# 3. Confirm payment
curl -X POST http://localhost:8001/api/v1x/payments/confirm \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"payment_intent_id": "pi_test_...", "order_id": 1}'
```

---

## 📊 CURRENT STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Stripe API Keys | ✅ Configured | In .env file |
| Backend Server | ✅ Running | On port 8001 |
| Payment Service | ✅ Exists | `stripe_service.py` |
| Payment Endpoints | ✅ Exists | `payments_integrated.py` |
| Order Model | ✅ Exists | `Order` model |
| Order Endpoints | 🟡 Partial | Needs enhancement |
| Webhook Handler | 🔴 Missing | Need to add |
| Frontend | 🔴 Missing | Need to build checkout |
| Tests | 🟡 Partial | Basic framework exists |

---

## ⏭️ NEXT STEPS

1. ✅ **Backend is running** - Start testing endpoints
2. **Test Payment Intent Creation** - Use cURL or Postman
3. **Enhance Order Creation** - Link payment to orders
4. **Build Checkout UI** - React component with Stripe
5. **Add Webhook Handler** - For payment confirmations
6. **End-to-End Testing** - Full purchase flow

---

## 🎯 SUCCESS CRITERIA

### By End of Today
- ✅ Backend running
- [ ] Can create payment intent
- [ ] Can create order
- [ ] Payment intent ID stored in database

### By End of Tomorrow
- [ ] Can confirm payment
- [ ] Order status updates
- [ ] User gains course access
- [ ] Email confirmation sent

### By End of Week
- [ ] Full checkout flow working
- [ ] Course orders generating revenue
- [ ] Mentor booking UI complete
- [ ] All tests passing

---

**Let's start building! Begin with testing the payment endpoints.** 🚀
