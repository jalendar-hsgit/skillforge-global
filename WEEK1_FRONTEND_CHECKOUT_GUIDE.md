# Week 1 Phase 2: Frontend Checkout Implementation Guide

**Status:** Ready to start

**Time Available:** 10 hours (Frontend checkout + order confirmation)

---

## Quick Summary: Backend is Done ✅

All backend payment endpoints are working:
- POST `/api/v1x/orders/create` - Create order
- POST `/api/v1x/orders/create-payment-intent` - Get payment intent
- POST `/api/v1x/orders/confirm-payment` - Confirm payment
- GET `/api/v1x/orders/my-orders` - List orders  
- GET `/api/v1x/orders/{order_id}` - Get order details

**Test Results:** All 6 endpoints passing ✅

---

## Frontend Checkout Page (5 hours)

### What to Build

Create a checkout page component that:

1. **Shows course details**
   - Course title, description, price
   - Fetch from `/api/v1x/courses-db`

2. **Creates order**
   - POST to `/api/v1x/orders/create` with `course_id` and `payment_method`
   - Stores returned `order_id` for payment confirmation

3. **Payment form**
   - Use Stripe Elements (CardElement or Payment Element)
   - Collect card details
   - Display amount and currency

4. **Processes payment**
   - Call `/api/v1x/orders/create-payment-intent` with `order_id`
   - Get `client_secret` from response
   - Submit payment with Stripe.js

5. **Confirms payment**
   - POST to `/api/v1x/orders/confirm-payment` with `order_id` and `payment_intent_id`
   - Wait for confirmation
   - Show success/error message

### File Structure

```
src/
├── pages/
│   └── checkout.tsx          # Main checkout page
├── components/
│   ├── CheckoutForm.tsx      # Order + payment form
│   ├── CourseSelector.tsx    # Course selection
│   ├── PaymentForm.tsx       # Stripe payment form
│   └── OrderConfirmation.tsx # Success screen
└── lib/
    └── payment.ts            # API calls
```

### Code Template: Checkout Page

```typescript
// src/pages/checkout.tsx
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import { CourseSelector } from '@/components/CourseSelector';
import { CheckoutForm } from '@/components/CheckoutForm';
import { OrderConfirmation } from '@/components/OrderConfirmation';

export default function CheckoutPage() {
  const router = useRouter();
  const [course, setCourse] = useState(null);
  const [orderCreated, setOrderCreated] = useState(false);
  const [orderId, setOrderId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!course) {
    return <CourseSelector onSelect={setCourse} />;
  }

  if (orderCreated && orderId) {
    return <OrderConfirmation orderId={orderId} course={course} />;
  }

  return (
    <CheckoutForm
      course={course}
      onSuccess={(id) => {
        setOrderId(id);
        setOrderCreated(true);
      }}
      onError={setError}
      loading={loading}
    />
  );
}
```

### Code Template: Payment Form

```typescript
// src/components/PaymentForm.tsx
import { useStripe, useElements, CardElement } from '@stripe/react-stripe-js';
import { createPaymentIntent, confirmPayment } from '@/lib/payment';
import { useState } from 'react';

interface PaymentFormProps {
  orderId: number;
  amount: number;
  onSuccess: () => void;
  onError: (error: string) => void;
}

export function PaymentForm({
  orderId,
  amount,
  onSuccess,
  onError
}: PaymentFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!stripe || !elements) return;

    setLoading(true);

    try {
      // 1. Create payment intent
      const intentResponse = await createPaymentIntent(orderId);
      const clientSecret = intentResponse.data.client_secret;
      const paymentIntentId = intentResponse.data.payment_intent_id;

      // 2. Confirm payment with Stripe
      const cardElement = elements.getElement(CardElement);
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement!,
          billing_details: { name: 'User Name' }
        }
      });

      if (result.error) {
        throw new Error(result.error.message);
      }

      // 3. Confirm payment on backend
      await confirmPayment(orderId, paymentIntentId);

      onSuccess();
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4 p-4 border rounded">
        <label className="block text-sm font-medium mb-2">Card Details</label>
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': { color: '#aab7c4' }
              }
            }
          }}
        />
      </div>

      <div className="mb-4 p-4 bg-gray-50 rounded">
        <p className="text-lg font-semibold">Amount: ${(amount / 100).toFixed(2)}</p>
      </div>

      <button
        type="submit"
        disabled={!stripe || loading}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Processing...' : 'Complete Payment'}
      </button>
    </form>
  );
}
```

### API Helper Functions

```typescript
// src/lib/payment.ts
import { api } from './api';

export async function createOrder(courseId: number) {
  return api.post('/orders/create', {
    course_id: courseId,
    payment_method: 'stripe'
  });
}

export async function createPaymentIntent(orderId: number) {
  return api.post('/orders/create-payment-intent', {
    order_id: orderId
  });
}

export async function confirmPayment(
  orderId: number,
  paymentIntentId: string
) {
  return api.post('/orders/confirm-payment', {
    order_id: orderId,
    payment_intent_id: paymentIntentId
  });
}

export async function getOrder(orderId: number) {
  return api.get(`/orders/${orderId}`);
}

export async function getUserOrders() {
  return api.get('/orders/my-orders');
}
```

---

## Order Confirmation Page (1-2 hours)

### What to Build

After successful payment, show:

1. **Success message** - "Payment successful!"
2. **Order details**
   - Order number
   - Amount paid
   - Course title
   - Payment date

3. **Course access**
   - "Course access granted"
   - Link to start course
   - Download materials button

4. **Next steps**
   - Button to go to course
   - Button to view all orders
   - Share/email receipt option

### Code Template

```typescript
// src/components/OrderConfirmation.tsx
import { useEffect, useState } from 'react';
import { getOrder } from '@/lib/payment';

interface OrderConfirmationProps {
  orderId: number;
  course: any;
}

export function OrderConfirmation({
  orderId,
  course
}: OrderConfirmationProps) {
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOrder() {
      try {
        const response = await getOrder(orderId);
        setOrder(response.data);
      } finally {
        setLoading(false);
      }
    }
    loadOrder();
  }, [orderId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-green-700 mb-2">
          Payment Successful!
        </h1>
        <p className="text-green-600">
          Your order has been confirmed. Course access is now available.
        </p>
      </div>

      <div className="bg-white border rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Order Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-600">Order Number</p>
            <p className="font-semibold">{order.order_number}</p>
          </div>
          <div>
            <p className="text-gray-600">Amount Paid</p>
            <p className="font-semibold">${order.amount}</p>
          </div>
          <div>
            <p className="text-gray-600">Course</p>
            <p className="font-semibold">{course.title}</p>
          </div>
          <div>
            <p className="text-gray-600">Date</p>
            <p className="font-semibold">
              {new Date(order.paid_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => window.location.href = `/courses/${course.path}`}
          className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold"
        >
          Go to Course
        </button>
        <button
          onClick={() => window.location.href = '/orders'}
          className="flex-1 bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 font-semibold"
        >
          View All Orders
        </button>
      </div>
    </div>
  );
}
```

---

## Stripe Setup in React

### 1. Install Dependencies

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 2. Add Stripe Elements Provider

```typescript
// src/_app.tsx
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
);

export default function App({ Component, pageProps }: AppProps) {
  return (
    <Elements stripe={stripePromise}>
      <Component {...pageProps} />
    </Elements>
  );
}
```

### 3. Add Environment Variables

```bash
# .env.local
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51Skc...
```

---

## Testing the Checkout Flow

### Test Card Details
- **Card Number:** 4242 4242 4242 4242
- **Exp Date:** 12/25
- **CVC:** 123
- **ZIP:** Any 5 digits

### Test Sequence
1. Go to `/checkout` page
2. Select a course
3. Click "Buy Course"
4. Enter test card details
5. Click "Complete Payment"
6. Should see "Payment Successful!" message
7. Check `/orders` page - order should appear

### Database Verification
```sql
sqlite3 backend/app/data/skillforge.db

-- Check order created
SELECT * FROM orders WHERE user_id = 12 ORDER BY created_at DESC;

-- Check payment status
SELECT id, order_number, payment_status, paid_at FROM orders WHERE id = 8;
```

---

## Remaining Work

### Phase 2 Deliverables (5 hours)
- ✅ Backend payment endpoints complete
- ⏳ Checkout page component
- ⏳ Payment form with Stripe integration
- ⏳ Order confirmation page
- ⏳ Course access after payment

### Phase 3: Mentor Booking (5 hours)
- ⏳ Booking form
- ⏳ Availability calendar
- ⏳ Payment processing
- ⏳ Confirmation email

### Phase 4: Testing (5 hours)
- ⏳ End-to-end tests
- ⏳ Error scenarios
- ⏳ UI polish

---

## API Response Examples

### Create Order Response
```json
{
  "success": true,
  "data": {
    "id": 8,
    "order_number": "ORD-12-1-e3117200",
    "course_id": 1,
    "amount": 49.99,
    "currency": "USD",
    "status": "pending",
    "payment_status": "pending"
  },
  "message": "Order created successfully"
}
```

### Create Payment Intent Response
```json
{
  "success": true,
  "data": {
    "client_secret": "pi_3Ss9jG...secret...",
    "payment_intent_id": "pi_3Ss9jG...",
    "amount": 49.99,
    "currency": "USD",
    "order_id": 8
  },
  "message": "Payment intent created successfully"
}
```

### Confirm Payment Response
```json
{
  "success": true,
  "data": {
    "order_id": 8,
    "status": "completed",
    "payment_status": "completed",
    "access_granted": true
  },
  "message": "Payment confirmed! Course access granted."
}
```

---

## Next Steps

1. **Start Here:** Create `/src/pages/checkout.tsx`
2. **Build Components:** PaymentForm, CourseSelector, OrderConfirmation
3. **Add API Helpers:** Update `src/lib/payment.ts`
4. **Test Flow:** Create order → confirm payment → show success
5. **Polish:** Styling, error messages, loading states

Backend is ready - let's build the frontend!

