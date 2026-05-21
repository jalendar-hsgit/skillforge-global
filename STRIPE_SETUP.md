# Stripe Configuration Guide

## Overview
SkillForge Global uses Stripe for:
1. **Subscriptions** - Monthly/Annual Pro & Enterprise plans
2. **Stripe Connect** - Mentor payouts
3. **One-time Payments** - Individual mentor session bookings

## Setup Steps

### 1. Create Stripe Account
1. Go to [https://dashboard.stripe.com/register](https://dashboard.stripe.com/register)
2. Create account and verify email
3. Complete business information

### 2. Get API Keys
1. Navigate to: Developers → API keys
2. Copy your keys:
   - **Publishable key**: `pk_test_...` (for frontend)
   - **Secret key**: `sk_test_...` (for backend)

### 3. Configure Environment Variables

#### Backend (`backend/.env`)
```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Stripe Webhook Secret (for production)
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# App URLs
FRONTEND_ORIGIN=http://localhost:3001
API_BASE=http://localhost:8001
```

#### Frontend (`.env.local`)
```bash
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

### 4. Create Subscription Products

#### Via Stripe Dashboard:
1. Go to: Products → Create product
2. Create "Pro Plan":
   - Name: `Pro Plan`
   - Description: `Unlimited mentoring with session recording`
   - Pricing:
     - Monthly: $29/month (recurring)
     - Annual: $290/year (recurring)
   - Copy the Price IDs for configuration

3. Create "Enterprise Plan":
   - Name: `Enterprise Plan`
   - Description: `For teams with dedicated support`
   - Pricing:
     - Monthly: $99/month
     - Annual: $990/year

#### Via Stripe CLI (Automated):
```bash
# Install Stripe CLI
# Windows: https://github.com/stripe/stripe-cli/releases

# Login
stripe login

# Create Pro Plan
stripe products create \\
  --name "Pro Plan" \\
  --description "Unlimited mentoring with session recording"

# Create monthly price
stripe prices create \\
  --product prod_XXX \\
  --unit-amount 2900 \\
  --currency usd \\
  --recurring[interval]=month

# Create annual price
stripe prices create \\
  --product prod_XXX \\
  --unit-amount 29000 \\
  --currency usd \\
  --recurring[interval]=year
```

### 5. Configure Stripe Connect (Mentor Payouts)

#### Enable Connect in Dashboard:
1. Go to: Settings → Connect settings
2. Enable "Platforms"
3. Set branding (logo, colors)
4. Configure:
   - Account type: "Express" (recommended for mentors)
   - Onboarding: Embedded onboarding
   - Payouts: Automatic (daily/weekly)

#### Update Code Configuration:
```python
# backend/app/core/config.py
STRIPE_CONNECT_ENABLED = True
STRIPE_CONNECT_CLIENT_ID = "ca_XXX"  # From Connect settings
```

### 6. Set Up Webhooks (Production)

#### Create Webhook Endpoint:
1. Go to: Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/api/v1x/stripe/webhook`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `account.updated` (for Connect)
4. Copy webhook signing secret → `STRIPE_WEBHOOK_SECRET`

### 7. Test Configuration

#### Backend Test:
```bash
cd backend
python -c "
from app.core.config import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
print('✓ Stripe configured successfully')
print(f'Account: {stripe.Account.retrieve()}')
"
```

#### Frontend Test:
```bash
curl http://localhost:8001/api/v1x/subscriptions/plans
# Should return available subscription plans
```

### 8. Update Product Price IDs in Code

After creating products, update:
```python
# backend/app/api/v1x/subscriptions.py
SUBSCRIPTION_PLANS = {
    "pro_monthly": "price_XXX",  # Your monthly Pro price ID
    "pro_annual": "price_YYY",   # Your annual Pro price ID
    "enterprise_monthly": "price_ZZZ",
    "enterprise_annual": "price_AAA"
}
```

## Testing Stripe Integration

### Test Cards (Development):
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0025 0000 3155
```

### Test Subscription Flow:
1. Navigate to: `http://localhost:3001/pricing`
2. Click "Upgrade to Pro"
3. Complete Stripe Checkout
4. Verify subscription in dashboard

### Test Mentor Payout Flow:
1. Become a mentor (or use test account)
2. Complete Stripe Connect onboarding
3. Book and complete a session
4. Check payout in Stripe Dashboard

## Production Deployment

### Before Going Live:
- [ ] Switch from test keys to live keys
- [ ] Enable webhook endpoints with HTTPS
- [ ] Configure domain verification
- [ ] Set up monitoring for failed payments
- [ ] Enable Stripe Radar (fraud prevention)
- [ ] Configure email receipts
- [ ] Test complete payment flow

### Security Checklist:
- [ ] Never expose secret keys in frontend code
- [ ] Validate webhook signatures
- [ ] Use HTTPS for all payment endpoints
- [ ] Implement idempotency keys for retries
- [ ] Log all payment events
- [ ] Set up alerts for failed payments

## Common Issues & Solutions

### Issue: "No such customer"
**Solution**: Ensure customer is created before creating subscription
```python
customer = stripe.Customer.create(email=user.email)
```

### Issue: "Invalid price ID"
**Solution**: Verify price IDs match your Stripe dashboard

### Issue: Webhook signature verification failed
**Solution**: Check webhook secret matches `.env` configuration

### Issue: Connect account not ready
**Solution**: Mentor must complete full onboarding flow

## Support Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Connect Guide](https://stripe.com/docs/connect)
- [Testing Guide](https://stripe.com/docs/testing)
- [Webhook Best Practices](https://stripe.com/docs/webhooks/best-practices)

## Monitoring & Analytics

View in Stripe Dashboard:
- Revenue → See subscription MRR
- Customers → Track active subscribers
- Connect → Monitor mentor payouts
- Logs → Debug payment issues
