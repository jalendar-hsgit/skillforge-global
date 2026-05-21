# Payment System Testing Guide

## Quick Start - Test Payment End-to-End

### Prerequisites
1. Backend running: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`
2. Frontend running: `npm run dev` (port 3000)
3. Stripe test API keys configured in environment

### Step 1: Set Stripe Test Keys

```bash
# Add to your .env file in backend root
STRIPE_PUBLIC_KEY=pk_test_YOUR_TEST_PUBLIC_KEY
STRIPE_SECRET_KEY=sk_test_YOUR_TEST_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_TEST_PUBLIC_KEY
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_TEST_WEBHOOK_SECRET
```

Or set as environment variables:
```bash
export STRIPE_PUBLIC_KEY=pk_test_...
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_PUBLISHABLE_KEY=pk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_test_...
```

### Step 2: Test Marketplace Payment

1. **Open marketplace**
   - Go to http://localhost:3000/marketplace
   - Browse products

2. **Add to cart**
   - Click on a product
   - Click "Add to Cart"
   - Repeat for 2-3 products

3. **Go to checkout**
   - Click "View Cart" or go to http://localhost:3000/marketplace/cart
   - Review items
   - Click "Proceed to Checkout"

4. **Review order**
   - See order summary
   - (Optional) Enter coupon code
   - Click "Continue to Payment"

5. **Make payment**
   - Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/25)
   - CVC: Any 3 digits (e.g., 123)
   - Name: Any name
   - Click "Pay $XX.XX"

6. **Confirm payment**
   - Should see success confirmation
   - Order status should be "completed"
   - Redirect to confirmation page

### Step 3: Test Mentor Session Payment

1. **Login as a student**
   - Go to http://localhost:3000/login
   - Use: `john.doe@example.com` / `password123`

2. **Book a mentor session**
   - Go to http://localhost:3000/mentor-booking
   - Select a mentor
   - Select date and time from available slots
   - Enter session topic and description
   - Click "Continue to Slots"
   - Select a time slot
   - Click "Continue to Payment"

3. **Make payment**
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - Click "Pay $XX.XX"

4. **Confirm booking**
   - Should see payment succeeded
   - Session should be confirmed
   - Mentor should receive booking notification

## Test API Endpoints with cURL

### Test Marketplace Checkout

```bash
# 1. Login to get session
curl -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@example.com", "password": "password123"}' \
  -c cookies.txt

# 2. Add product to cart
curl -X POST http://localhost:8001/api/session/v1x/marketplace/cart \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"product_id": 1}'

# 3. Get cart
curl -X GET http://localhost:8001/api/session/v1x/marketplace/cart \
  -b cookies.txt

# 4. Checkout
curl -X POST http://localhost:8001/api/session/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "product_ids": [1],
    "payment_method": "stripe"
  }' | jq .

# 5. Confirm payment (after Stripe payment succeeds)
curl -X POST http://localhost:8001/api/session/v1x/marketplace/confirm-payment/ORDER_ID \
  -b cookies.txt

# Response should show: order status = "completed"
```

### Test Mentor Session Payment

```bash
# 1. Login
curl -X POST http://localhost:8001/api/v1x/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@example.com", "password": "password123"}' \
  -c cookies.txt

# 2. Get available mentors
curl -X GET http://localhost:8001/api/v1x/mentors \
  -b cookies.txt | jq .

# 3. Get available slots for mentor (ID=1)
curl -X GET "http://localhost:8001/api/v1x/mentors/1/availability?date=2024-01-15" \
  -b cookies.txt

# 4. Book session
curl -X POST http://localhost:8001/api/v1x/mentors/1/book \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "scheduled_at": "2024-01-15T10:00:00",
    "duration_minutes": 60,
    "topic": "Python Basics",
    "description": "Help with Python fundamentals"
  }' | jq .

# Response should include session_id

# 5. Create payment intent
curl -X POST http://localhost:8001/api/v1x/payments/create-payment-intent \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"session_id": 1}' | jq .

# Response should include client_secret and amount

# 6. After payment succeeds (webhook), confirm it
curl -X POST http://localhost:8001/api/v1x/payments/capture-payment/1 \
  -b cookies.txt

# Response should show: payment_status = "captured"
```

## Test Different Card Scenarios

### 1. Successful Payment
```
Card Number: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123
ZIP: 12345
```
**Result:** Payment succeeds, order completed

### 2. Card Declined
```
Card Number: 4000 0000 0000 0002
Expiry: 12/25
CVC: 123
ZIP: 12345
```
**Result:** Payment fails with error message

### 3. Requires Authentication
```
Card Number: 4000 0025 0000 3155
Expiry: 12/25
CVC: 123
ZIP: 12345
```
**Result:** Payment requires 3D Secure authentication

### 4. Expired Card
```
Card Number: 4000 0069 0000 1500
Expiry: 12/20 (past date)
CVC: 123
ZIP: 12345
```
**Result:** Card declined due to expiration

## Webhook Testing (Local)

### Setup Stripe CLI

```bash
# 1. Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# 2. Login
stripe login

# 3. Forward webhooks to local server
stripe listen --forward-to localhost:8001/api/v1x/payments/webhook

# You'll see output like:
# > Ready! Your webhook signing secret is: whsec_test_...
# Copy this secret!

# 4. Set webhook secret in environment
export STRIPE_WEBHOOK_SECRET=whsec_test_...

# 5. In another terminal, trigger test events
stripe trigger payment_intent.succeeded

# Check your server logs - you should see webhook processed
```

### Verify Webhook Processing

1. Make a test payment
2. Watch server logs for webhook event
3. Payment status should auto-update
4. Email notification should be sent
5. Order status should change to "completed"

## Database Verification

### Check Orders Table

```bash
# Login to SQLite
sqlite3 backend/app/data/skillforge.db

# View recent orders
SELECT id, order_number, status, payment_status, amount, payment_intent_id 
FROM orders 
ORDER BY created_at DESC 
LIMIT 5;

# View order details
SELECT * FROM orders WHERE id = 1;
```

### Check Mentor Sessions

```bash
# View mentor sessions
SELECT id, mentor_id, student_id, status, payment_status, payment_intent_id, price 
FROM mentor_sessions 
ORDER BY created_at DESC 
LIMIT 5;
```

## Performance Testing

### Load Testing Payment Endpoint

```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8001/api/v1x/payments/

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8001/api/v1x/marketplace/checkout

# Using hey
go install github.com/rakyll/hey@latest
hey -n 100 -c 10 http://localhost:8001/api/v1x/payments/
```

## Debugging Tips

### Enable Debug Logging

```python
# In backend/app/services/stripe_service.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
stripe_logger = logging.getLogger('stripe')
stripe_logger.setLevel(logging.DEBUG)
```

### Check Stripe Dashboard

1. Go to https://dashboard.stripe.com/test/payments
2. See all test payment intents
3. View detailed logs
4. Test webhook delivery

### Browser DevTools

1. Open DevTools (F12)
2. Go to Network tab
3. Make payment
4. See API requests/responses
5. Check for errors in Console

### Server Logs

```bash
# Watch backend logs
tail -f backend/logs/*.log

# Search for payment errors
grep -i "payment\|stripe" backend/logs/*.log
```

## Common Issues & Solutions

### Issue: "Stripe is not configured"
**Solution:** 
```bash
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Issue: Webhook Not Triggering
**Solution:**
- Verify webhook secret is set correctly
- Check server is accessible: `curl http://localhost:8001/api/v1x/payments/webhook`
- Use Stripe CLI to forward events

### Issue: "Card declined"
**Solution:**
- Use correct test card for scenario
- Check expiry date is in future
- Try a different test card

### Issue: Payment Hangs
**Solution:**
- Check browser console for errors
- Check server logs
- Verify Stripe API keys
- Try different test card

### Issue: Order Not Created
**Solution:**
- Check user is authenticated
- Verify product_ids exist
- Check database for errors
- Review server logs

## Monitoring Payment Health

### Key Metrics to Check

1. **Payment Success Rate**
   ```sql
   SELECT 
     payment_status,
     COUNT(*) as count,
     ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM orders), 2) as percentage
   FROM orders
   GROUP BY payment_status;
   ```

2. **Average Transaction Value**
   ```sql
   SELECT 
     AVG(amount) as avg_amount,
     SUM(amount) as total_revenue,
     COUNT(*) as transaction_count
   FROM orders
   WHERE payment_status = 'completed';
   ```

3. **Payment Methods Used**
   ```sql
   SELECT 
     payment_method,
     COUNT(*) as count
   FROM orders
   WHERE payment_status = 'completed'
   GROUP BY payment_method;
   ```

## Support

For issues, check:
1. Stripe Dashboard: https://dashboard.stripe.com/test/
2. API Docs: https://stripe.com/docs/api
3. Server logs: `backend/logs/`
4. Browser console: DevTools > Console
