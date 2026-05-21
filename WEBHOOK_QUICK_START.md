# Real-Time Payment Implementation - Quick Start

## 🚀 What's New

Real-time payment webhook processing for mentor sessions. When a student pays via Stripe, the session is automatically updated in the database within seconds.

## 📋 What Changed

### Backend
- ✅ **NEW**: `backend/app/api/v1x/webhooks.py` (283 lines) - Stripe webhook handler
- ✅ **UPDATED**: `backend/app/main.py` - Registered webhooks router

### Frontend
- ✅ **EXISTING**: `src/components/SessionPayment.tsx` - Already uses correct endpoint
- ✅ **EXISTING**: `src/pages/mentors/[id]/book.tsx` - Already passes correct price
- ✅ **EXISTING**: `src/pages/my-bookings.tsx` - Already displays payment status

## 🔌 How It Works

### Without Webhooks (Before)
```
Student pays → Stripe confirms → Frontend hopes database is updated → Sometimes payment_status stays "pending" ❌
```

### With Webhooks (Now)
```
Student pays → Stripe confirms → Webhook automatically updates database → Payment_status = "paid" ✅ in seconds
```

## 🧪 Test It Locally (5 Minutes)

### 1. Install Stripe CLI
```powershell
choco install stripe-cli
```

### 2. Start Services
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 8001

# Terminal 2: Frontend
npm run dev

# Terminal 3: Webhook forwarding
stripe listen --forward-to http://localhost:8001/api/v1x/webhooks/stripe/payment-intent
```

### 3. Test Payment Flow
```
1. Go to http://localhost:3000/mentors
2. Click "Book Session" on any mentor
3. Fill in booking details
4. Click "Book Session"
5. Enter test card: 4242 4242 4242 4242
6. Click "Pay $75.00"
7. Check backend logs for: ✅ Session 32: Payment succeeded
8. Go to /my-bookings - see session with "Paid" status ✓
```

### 4. Verify in Database
```bash
sqlite3 backend/app/data/skillforge.db
> SELECT payment_status FROM mentor_sessions WHERE id = 32;
# Should show: paid
```

## 📊 API Endpoints

### Create Payment Intent
```
POST /api/v1x/mentors/sessions/payment-intent
Authorization: Bearer {token}
Content-Type: application/json

Body: { "session_id": 32 }

Response:
{
  "client_secret": "pi_1234567890_secret_abc",
  "payment_intent_id": "pi_1234567890",
  "amount": 75.00,
  "currency": "usd"
}
```

### Receive Webhook
```
POST /api/v1x/webhooks/stripe/payment-intent
stripe-signature: <Stripe signature>

Auto-triggered by Stripe when payment succeeds
Updates: mentor_sessions.payment_status = 'paid'
```

### Check Payment Status
```
GET /api/v1x/webhooks/sessions/{session_id}/payment-status

Response:
{
  "session_id": 32,
  "payment_status": "paid",
  "payment_intent_id": "pi_1234567890",
  "amount_paid": 75.00
}
```

## 🔑 Environment Variables

Add to `.env` (backend):
```env
STRIPE_API_KEY=sk_test_REPLACE_ME
STRIPE_PUBLISHABLE_KEY=pk_test_123456789
STRIPE_WEBHOOK_SECRET=whsec_test_123456789
```

Get values from: https://dashboard.stripe.com → Developers → Keys & credentials

## 📊 Payment Status Values

| Status | Meaning | When? |
|--------|---------|-------|
| `pending` | Waiting for payment | Initial state |
| `paid` | Payment successful | Webhook: payment_intent.succeeded |
| `failed` | Payment declined | Webhook: payment_intent.payment_failed |
| `refunded` | Money returned | Webhook: charge.refunded |
| `cancelled` | User cancelled | Webhook: payment_intent.canceled |

## 🐛 Troubleshooting

### Problem: Backend shows "Cannot import webhooks"
**Solution**: Check that `backend/app/api/v1x/webhooks.py` file exists

### Problem: Webhook not triggering
**Solution**: Run `stripe listen --forward-to http://localhost:8001/api/v1x/webhooks/stripe/payment-intent`

### Problem: Payment status not updating
**Solution**: Check backend logs for `✅ Session X: Payment succeeded`

### Problem: Webhook signature error
**Solution**: Copy correct STRIPE_WEBHOOK_SECRET from stripe listen output

## 📚 Full Documentation

- **Complete Testing Guide**: [WEBHOOK_TESTING_GUIDE.md](WEBHOOK_TESTING_GUIDE.md)
- **Architecture Details**: [PAYMENT_ARCHITECTURE_COMPLETE.md](PAYMENT_ARCHITECTURE_COMPLETE.md)
- **Original Booking Fix**: [BOOKING_AND_PAYMENT_FIX_COMPLETE.md](BOOKING_AND_PAYMENT_FIX_COMPLETE.md)

## ✅ Success Indicators

You've successfully set up real-time payments when:

1. ✅ Stripe CLI is running with `stripe listen --forward-to ...`
2. ✅ Backend imports webhooks without errors: `uvicorn app.main:app --reload`
3. ✅ Student books a session and completes payment
4. ✅ Backend logs show: `✅ Session X: Payment succeeded`
5. ✅ Database shows: `payment_status = 'paid'`
6. ✅ `/my-bookings` displays session with "Paid" status
7. ✅ Payment status endpoint returns: `"payment_status": "paid"`

## 🚀 Production Deployment

### Step 1: Configure Stripe Dashboard
1. Go to https://dashboard.stripe.com → Developers → Webhooks
2. Add endpoint: `https://yourapp.com/api/v1x/webhooks/stripe/payment-intent`
3. Select events: payment_intent.succeeded, payment_intent.payment_failed, payment_intent.canceled, charge.refunded
4. Copy webhook signing secret

### Step 2: Set Environment Variables
```env
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...
```

### Step 3: Deploy
```bash
cd backend && pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 💾 Database Integration

The webhook handler automatically:
- ✅ Updates `mentor_sessions.payment_status = 'paid'`
- ✅ Saves `payment_intent_id` for reference
- ✅ Records timestamp
- ✅ Sends confirmation email
- ✅ Logs transaction

No additional code needed in other endpoints!

## 🎯 User Experience

**Before Webhook Implementation** ❌
```
Student → Pays → Sees "Success" → Refreshes page → Payment status still "pending" 😕
```

**After Webhook Implementation** ✅
```
Student → Pays → Sees "Success" → Gets confirmation email → Sees "Paid" status immediately 😊
```

## 🔗 Integration Points

The webhook system automatically integrates with:
- ✅ Session creation (`POST /api/v1x/mentors/sessions`)
- ✅ Payment intent endpoint (`POST /api/v1x/mentors/sessions/payment-intent`)
- ✅ Session list endpoint (`GET /api/v1x/mentors/sessions/my`)
- ✅ My bookings page (`/my-bookings`)
- ✅ Email notification system
- ✅ Database (`mentor_sessions.payment_status`)

## 📞 Support

For issues or questions:
1. Check WEBHOOK_TESTING_GUIDE.md for detailed troubleshooting
2. Check backend logs: `grep "Session" backend.log`
3. Verify Stripe API keys at https://dashboard.stripe.com

---

**Status**: ✅ Production Ready

The mentor booking and real-time payment system is now fully implemented and tested!
