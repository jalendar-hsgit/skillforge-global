# 🚀 Payment System - Quick Reference

## What's Done ✅

**Complete payment integration for mentor sessions and marketplace products using Stripe**

### Backend
- ✅ Stripe payment service
- ✅ Mentor payment endpoints
- ✅ Marketplace checkout endpoints
- ✅ Webhook handler
- ✅ Error handling
- ✅ Database fields

### Frontend
- ✅ Stripe payment forms
- ✅ Marketplace checkout page
- ✅ Cart integration
- ✅ Payment confirmation
- ✅ Error display

### Documentation
- ✅ Implementation guide
- ✅ Testing guide
- ✅ API reference
- ✅ Troubleshooting

---

## Get Started (5 minutes)

### 1. Set Stripe Keys
```bash
export STRIPE_SECRET_KEY=sk_test_YOUR_KEY
export STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
export STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_KEY
```

### 2. Start Servers
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8001

# Terminal 2: Frontend
npm run dev
```

### 3. Test Payment
- Go to http://localhost:3000/marketplace
- Add product → Checkout
- Card: `4242 4242 4242 4242`
- Exp: `12/25` | CVC: `123`
- Done! ✅

---

## Key Files

### Backend
- `backend/app/services/stripe_service.py` - Stripe integration
- `backend/app/api/v1x/payments.py` - Mentor payments
- `backend/app/api/v1x/marketplace_checkout.py` - Marketplace checkout
- `backend/app/modelsx/order.py` - Order model

### Frontend
- `src/components/MentorPaymentForm.tsx` - Mentor payment UI
- `src/components/MarketplacePaymentForm.tsx` - Marketplace payment UI
- `src/pages/marketplace/checkout.tsx` - Checkout page
- `src/pages/marketplace/cart.tsx` - Shopping cart

---

## Payment Flows

### Mentor Session
1. Book session → Create payment intent
2. Pay with card → Stripe confirms payment
3. Webhook updates session status
4. After session ends → Mentor captures payment
5. Funds transferred to mentor (80% after 20% platform fee)

### Marketplace
1. Add products → Go to checkout
2. Apply coupon (optional) → Create payment intent
3. Pay with card → Stripe confirms payment
4. Confirm order in system
5. Order marked complete, products delivered

---

## API Endpoints

### Create Payment Intent (Mentor)
```bash
POST /api/v1x/payments/create-payment-intent
Body: {"session_id": 1}
Response: {client_secret, payment_intent_id, amount}
```

### Marketplace Checkout
```bash
POST /api/v1x/marketplace/checkout
Body: {product_ids: [1,2], coupon_code: "SAVE10", payment_method: "stripe"}
Response: {order_id, client_secret, total_amount}
```

### Confirm Payment
```bash
POST /api/v1x/marketplace/confirm-payment/{order_id}
Response: {status: "completed"}
```

---

## Test Cards

| Use Case | Card | Result |
|----------|------|--------|
| Success | 4242 4242 4242 4242 | Payment works ✅ |
| Decline | 4000 0000 0000 0002 | Payment fails ❌ |
| 3DS Required | 4000 0025 0000 3155 | Need authentication |

All cards: Exp `12/25`, CVC `123`, ZIP `12345`

---

## Database Check

```bash
# See recent orders
sqlite3 backend/app/data/skillforge.db
SELECT id, order_number, payment_status, amount FROM orders LIMIT 5;

# See mentor sessions
SELECT id, status, payment_status, price FROM mentor_sessions LIMIT 5;
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Stripe not configured" | Set STRIPE_SECRET_KEY env var |
| Payment hangs | Check browser console for errors |
| Webhook not firing | Use Stripe CLI to forward events |
| Order not created | Check user is logged in |
| Card declined | Use test card 4242... instead |

---

## Documentation

Read these files for details:
1. **PAYMENT_SYSTEM_COMPLETE.md** - Full implementation details
2. **PAYMENT_TESTING_GUIDE.md** - Complete testing procedures
3. **PAYMENT_SYSTEM_INTEGRATION.md** - Deployment checklist

---

## Important Notes

✅ **No Breaking Changes** - All existing code preserved
✅ **Production Ready** - Fully tested and secure
✅ **PCI Compliant** - Stripe handles card data
✅ **Webhook Support** - Automatic payment confirmation
✅ **Error Handling** - Full error messages and logging
✅ **Test Mode** - Use test keys for development

---

## Next Steps

1. **Get Stripe Account**: https://stripe.com
2. **Copy Test Keys**: https://dashboard.stripe.com/test/apikeys
3. **Set Environment Variables** (see "Get Started" above)
4. **Run Test Payments** (follow "Test Payment" above)
5. **Deploy to Production** (use live keys in production)

---

## Support

- 📚 Stripe Docs: https://stripe.com/docs
- 🔧 Stripe API: https://stripe.com/docs/api
- 🪝 Webhooks: https://stripe.com/docs/webhooks
- 🧪 Test Cards: https://stripe.com/docs/testing

---

## Commands Reference

```bash
# Start backend with Stripe keys
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_PUBLISHABLE_KEY=pk_test_...
cd backend && uvicorn app.main:app --reload --port 8001

# Start frontend
npm run dev

# Check database
sqlite3 backend/app/data/skillforge.db

# View payment orders
sqlite3 backend/app/data/skillforge.db "SELECT * FROM orders LIMIT 5;"

# Forward Stripe webhooks (local testing)
stripe listen --forward-to localhost:8001/api/v1x/payments/webhook

# Trigger test webhook
stripe trigger payment_intent.succeeded
```

---

## Security Checklist

✅ API keys configured
✅ Webhook signature verification enabled
✅ No card data stored locally
✅ SSL/TLS encryption ready
✅ Authorization checks in place
✅ Error messages don't expose sensitive data
✅ Database backups recommended

---

**Everything is ready. Start with Step 1 above and you'll have payments working in minutes!**

For detailed information, see the documentation files in the repository root.
