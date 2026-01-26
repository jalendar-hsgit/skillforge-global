# 🔐 Stripe Configuration Guide - Phase 2

## Overview
This guide walks you through configuring Stripe for local development and production.

---

## 📋 Prerequisites

1. **Stripe Account** - https://dashboard.stripe.com/
2. **Stripe CLI** - For local webhook testing
3. **.env file** - In repository root

---

## 🚀 Step 1: Get Your Stripe Keys

### From Stripe Dashboard

1. Log in to **https://dashboard.stripe.com/**
2. Go to **Developers → API Keys**
3. You'll see two key pairs:
   - **Test Mode** (development) - starts with `pk_test_` and `sk_test_`
   - **Live Mode** (production) - starts with `pk_live_` and `sk_live_`

**For local development, use TEST MODE keys**

### Copy These Keys:
- `Publishable key` → `STRIPE_PUBLIC_KEY`
- `Secret key` → `STRIPE_SECRET_KEY`

**Example:**
```
STRIPE_PUBLIC_KEY=pk_test_51234567890abcdefghij
STRIPE_SECRET_KEY=sk_test_REPLACE_ME
```

---

## 🪝 Step 2: Get Your Webhook Secret

### Create Webhook Endpoint

1. Go to **Developers → Webhooks**
2. Click **+ Add endpoint**
3. Endpoint URL: `https://yourdomain.com/webhook/stripe`
   - For local testing: Will be handled by Stripe CLI
4. Events to send: Select these events
   - ✅ `payment_intent.succeeded`
   - ✅ `payment_intent.payment_failed`
   - ✅ `payment_intent.canceled`
   - ✅ `charge.refunded`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`

5. Click **Add endpoint**
6. Click on your endpoint
7. Copy **Signing secret**
   - Starts with `whsec_test_` or `whsec_`

**Example:**
```
STRIPE_WEBHOOK_SECRET=whsec_test_abcdefghij1234567890
```

---

## ✏️ Step 3: Update .env File

Open `.env.local` in root directory and add:

```bash
# Stripe Payment Processing
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_SECRET_HERE

# Email Configuration (for receipts & notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@skillforge.com
SMTP_FROM_NAME=SkillForge Global
```

### 📧 Email Setup (Gmail)

If using Gmail for email receipts:

1. Go to **Google Account** → **Security**
2. Enable **2-Factor Authentication**
3. Go to **App passwords** (at the bottom)
4. Create new app password for "Mail" on "Windows Computer"
5. Copy the 16-character password
6. Paste as `SMTP_PASSWORD` in .env

---

## 🧪 Step 4: Test Configuration Locally

### Install Stripe CLI

**Windows (PowerShell as Admin):**
```powershell
choco install stripe
```

Or download from: https://github.com/stripe/stripe-cli/releases

### Verify Installation
```bash
stripe version
stripe login
```

### Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Listen for Webhook Events
```bash
stripe listen --forward-to http://localhost:8001/webhook/stripe
```

**Output should show:**
```
> Ready! You are now listening for Stripe events...
> Your webhook signing secret is: whsec_test_xxxxxxxxx
```

Copy this signing secret to your `.env` file if different.

### Test Event in Another Terminal
```bash
stripe trigger payment_intent.succeeded
```

**Expected Result:**
```
[webhook] Successfully sent event to http://localhost:8001/webhook/stripe
```

---

## 🔄 Step 5: Test Complete Payment Flow

### 1. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

**Terminal 3 - Webhook Listener:**
```bash
stripe listen --forward-to http://localhost:8001/webhook/stripe
```

### 2. Test Flow

1. Open http://localhost:3000
2. Log in as a regular user
3. Book a mentor session
4. Proceed to payment
5. Use **Stripe test card**: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/25)
   - CVC: Any 3 digits
6. Complete payment
7. **Check Terminal 3** - Should see webhook event
8. **Check Backend Logs** - Should show order updated to "completed"
9. **Check Email** - Receipt should be sent (if configured)

---

## 📊 Step 6: Verify Payment Processing

Run comprehensive test:
```bash
cd d:\python code\sfg\skillforge-global
python payment_test_report.py
```

**Expected Output:**
```
✓ User Types: PASS (11 users)
✓ Mentor Sessions: PASS (61 sessions, $4,490 revenue)
✓ Orders & Payments: PASS
✓ Revenue Analysis: PASS ($4,490 verified)
```

---

## 🔒 Production Deployment

### Update for Production

1. Switch to **Live Mode** in Stripe Dashboard
2. Get Live keys (start with `pk_live_` and `sk_live_`)
3. Create production webhook endpoint
4. Update `.env.production` with live keys:

```bash
STRIPE_PUBLIC_KEY=pk_live_YOUR_LIVE_KEY
STRIPE_SECRET_KEY=sk_live_YOUR_LIVE_SECRET
STRIPE_WEBHOOK_SECRET=whsec_YOUR_LIVE_SECRET
```

### Important Security Notes

⚠️ **NEVER** commit `.env.local` to git
✅ **Always** use environment variables for secrets
✅ **Rotate** webhook secrets regularly
✅ **Monitor** Failed Events in Stripe Dashboard
✅ **Test** production keys before going live

---

## 🐛 Troubleshooting

### Webhook Not Receiving Events

**Problem:** Events forwarded but not processed
**Solution:**
1. Check backend logs for errors
2. Verify webhook endpoint URL is correct
3. Check signing secret matches in .env
4. Restart backend service

**Debug:**
```bash
# In backend logs, look for:
# "Webhook received" message
# "Order updated to: completed"
```

### Email Not Sending

**Problem:** Receipts not received
**Solution:**
1. Verify SMTP credentials in .env
2. Check Gmail "Less secure apps" is enabled
3. Allow "Less secure apps": https://myaccount.google.com/lesssecureapps
4. Use App Password instead (recommended)

**Test Email:**
```bash
cd backend
python -c "from app.services.email_service import email_service; email_service.send_test_email('your-email@example.com')"
```

### Test Mode vs Live Mode

**Always** develop with test mode keys:
- ✅ Test cards: 4242 4242 4242 4242
- ✅ No real charges
- ✅ Safe to test multiple times

---

## 📚 Useful Links

- [Stripe API Docs](https://stripe.com/docs/api)
- [Stripe Test Cards](https://stripe.com/docs/testing)
- [Webhook Events](https://stripe.com/docs/webhooks)
- [Stripe CLI Guide](https://stripe.com/docs/stripe-cli)
- [Python Stripe SDK](https://github.com/stripe/stripe-python)

---

## ✅ Checklist Before Phase 2 Testing

- [ ] Stripe account created
- [ ] Test keys copied to .env.local
- [ ] Webhook secret configured
- [ ] Stripe CLI installed and tested
- [ ] Backend starts successfully
- [ ] Email service configured (SMTP)
- [ ] Webhook listener running locally
- [ ] Test payment flow executed
- [ ] payment_test_report.py passes all tests
- [ ] Ready for Phase 2A implementation

---

## 🎯 Next Steps

Once configuration is verified:

1. **Phase 2A** - Implement email receipts for orders
2. **Phase 2B** - Implement seller payouts system
3. **Phase 2C** - Implement subscription billing

**Estimated Time:** 30 minutes for configuration + testing
