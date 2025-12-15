# Manual Testing Guide: Coin Deduction Feature

## Prerequisites

1. Backend server running on port 8001
2. Database with test data (users, courses, coins)
3. HTTP client (Postman, curl, or browser console)

## Test User Setup

Use the demo user from video progress tests:
- **Email**: demo@skillforge.com
- **Password**: Demo123!@#

OR create a new test user:
```bash
# Login to create account
curl -X POST http://localhost:8001/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cointest@test.com",
    "username": "cointest",
    "password": "Test123!@#",
    "first_name": "Coin",
    "last_name": "Tester"
  }'
```

## Test Scenario 1: Check Initial Balance

### Step 1: Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@skillforge.com", "password": "Demo123!@#"}' \
  -c cookies.txt
```

### Step 2: Check Dashboard (includes coin balance)
```bash
curl -X GET http://localhost:8001/api/v1/dashboard \
  -b cookies.txt
```

Look for the `forge_ai_credits` field in the response.

## Test Scenario 2: Add Test Coins (via database)

If user has 0 coins, add some for testing:

```sql
-- Add 500 coins to user ID 1
INSERT INTO coin_ledger (user_id, delta, reason, created_at)
VALUES (1, 500, 'Test coins for purchase', datetime('now'));

-- Verify balance
SELECT SUM(delta) as balance FROM coin_ledger WHERE user_id = 1;
```

## Test Scenario 3: Insufficient Coins Error

### Step 1: Set low balance
```sql
-- Clear existing coins
DELETE FROM coin_ledger WHERE user_id = 1;

-- Add only 10 coins
INSERT INTO coin_ledger (user_id, delta, reason, created_at)
VALUES (1, 10, 'Low test balance', datetime('now'));
```

### Step 2: Find a course (price > 10)
```bash
curl -X GET http://localhost:8001/api/v1x/marketplace/courses \
  -b cookies.txt
```

Note a course ID with price > $10.

### Step 3: Add to cart
```bash
curl -X POST http://localhost:8001/api/v1x/marketplace/cart \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"course_id": 1}'
```

### Step 4: Attempt checkout (should fail)
```bash
curl -X POST http://localhost:8001/api/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"payment_method": "coins"}'
```

**Expected Response**: HTTP 400
```json
{
  "detail": "Insufficient coins. Balance: 10, Required: 50"
}
```

## Test Scenario 4: Successful Purchase

### Step 1: Add sufficient coins
```sql
DELETE FROM coin_ledger WHERE user_id = 1;
INSERT INTO coin_ledger (user_id, delta, reason, created_at)
VALUES (1, 500, 'Sufficient test balance', datetime('now'));
```

### Step 2: Check balance before
```bash
curl -X GET http://localhost:8001/api/v1/dashboard -b cookies.txt | grep forge_ai_credits
```

Should show 500 coins.

### Step 3: Clear cart and add course
```bash
# Get cart items
curl -X GET http://localhost:8001/api/v1x/marketplace/cart -b cookies.txt

# Add course ID 1 to cart
curl -X POST http://localhost:8001/api/v1x/marketplace/cart \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"course_id": 1}'
```

### Step 4: Complete purchase
```bash
curl -X POST http://localhost:8001/api/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"payment_method": "coins"}'
```

**Expected Response**: HTTP 200
```json
{
  "id": 1,
  "order_number": "ORD-XXXXX",
  "status": "completed",
  "payment_status": "completed",
  "subtotal": 49.99,
  "amount": 49.99,
  "payment_method": "coins",
  "course_title": "Python Programming"
}
```

### Step 5: Verify balance deduction
```bash
curl -X GET http://localhost:8001/api/v1/dashboard -b cookies.txt | grep forge_ai_credits
```

Should show reduced balance (e.g., 500 - 49 = 451 coins).

### Step 6: Check coin ledger (database)
```sql
-- View recent transactions
SELECT * FROM coin_ledger 
WHERE user_id = 1 
ORDER BY created_at DESC 
LIMIT 5;
```

Should see:
- Positive entry: +500 "Sufficient test balance"
- Negative entry: -49 "Course purchase: Python Programming"

### Step 7: Verify order in database
```sql
SELECT order_number, status, payment_status, payment_method, amount, paid_at
FROM orders
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 1;
```

Should show:
- `status`: "completed"
- `payment_status`: "completed"
- `payment_method`: "coins"
- `paid_at`: recent timestamp

## Test Scenario 5: Multiple Purchases

### Step 1: Add generous balance
```sql
DELETE FROM coin_ledger WHERE user_id = 1;
INSERT INTO coin_ledger (user_id, delta, reason, created_at)
VALUES (1, 1000, 'Test multiple purchases', datetime('now'));
```

### Step 2: Purchase 3 courses in sequence
For each course:
1. Add to cart
2. Checkout with coins
3. Verify balance decreased

After 3 purchases (e.g., $49, $39, $29):
- Initial: 1000 coins
- After purchase 1: 951 coins
- After purchase 2: 912 coins
- After purchase 3: 883 coins

### Step 3: Verify transaction history
```sql
SELECT delta, reason, created_at
FROM coin_ledger
WHERE user_id = 1
ORDER BY created_at DESC;
```

Should show 4 entries:
1. -29 "Course purchase: Course C"
2. -39 "Course purchase: Course B"
3. -49 "Course purchase: Course A"
4. +1000 "Test multiple purchases"

## Test Scenario 6: Edge Case - Exact Balance

### Step 1: Set balance to exact course price
```sql
DELETE FROM coin_ledger WHERE user_id = 1;
-- If course costs $49.99 (49 coins), add exactly 49
INSERT INTO coin_ledger (user_id, delta, reason, created_at)
VALUES (1, 49, 'Exact balance test', datetime('now'));
```

### Step 2: Purchase course
```bash
# Add to cart
curl -X POST http://localhost:8001/api/v1x/marketplace/cart \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"course_id": 1}'

# Checkout
curl -X POST http://localhost:8001/api/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"payment_method": "coins"}'
```

**Expected**: Success (HTTP 200), balance becomes 0

### Step 3: Verify zero balance
```bash
curl -X GET http://localhost:8001/api/v1/dashboard -b cookies.txt | grep forge_ai_credits
```

Should show 0 coins.

## Test Scenario 7: Price Rounding

Coins are integers, but course prices can have decimals.

### Test Cases:
- $49.99 → 49 coins (int truncation)
- $50.00 → 50 coins
- $50.50 → 50 coins

This is handled by `coins_required = int(total)` in the code.

## Quick Verification Queries

### Current Balance for User
```sql
SELECT SUM(delta) as balance FROM coin_ledger WHERE user_id = 1;
```

### All Transactions for User
```sql
SELECT delta, reason, created_at
FROM coin_ledger
WHERE user_id = 1
ORDER BY created_at DESC;
```

### Recent Orders
```sql
SELECT order_number, status, payment_method, amount, course_id, created_at
FROM orders
WHERE user_id = 1 AND payment_method = 'coins'
ORDER BY created_at DESC;
```

### Total Coins Earned vs Spent
```sql
SELECT 
  SUM(CASE WHEN delta > 0 THEN delta ELSE 0 END) as total_earned,
  SUM(CASE WHEN delta < 0 THEN delta ELSE 0 END) as total_spent,
  SUM(delta) as current_balance
FROM coin_ledger
WHERE user_id = 1;
```

## Expected Test Results Summary

| Test Scenario | Expected Result | Verification |
|---------------|----------------|--------------|
| Insufficient coins | HTTP 400 error | Error message shows balance and required |
| Sufficient coins | HTTP 200 success | Order completed, balance reduced |
| Exact balance | HTTP 200 success | Balance becomes 0 after purchase |
| Multiple purchases | All succeed | Balance decreases with each purchase |
| Zero balance | HTTP 400 error | Cannot purchase with 0 coins |
| Cart cleared | Empty cart | No cart items after successful checkout |
| Ledger audit | Negative entry | Coin deduction recorded with reason |
| Order status | Completed | Status and payment_status = "completed" |

## Troubleshooting

### Issue: "Insufficient coins" but balance is correct
- Check that cart still has items (cleared after failed checkout)
- Re-add course to cart before retrying

### Issue: Balance not updating
- Verify database commit succeeded
- Check for transaction errors in server logs
- Query `coin_ledger` table directly

### Issue: Order created but coins not deducted
- Check server logs for errors after "Deduct coins from balance"
- Verify CoinLedger model is imported correctly
- Check database constraints on `coin_ledger` table

### Issue: 500 Internal Server Error
- Check backend logs: `uvicorn` console output
- Verify all imports in `marketplace.py`
- Check database connection is active

## Success Criteria

All tests pass if:
1. ✅ Insufficient coins returns HTTP 400 with clear message
2. ✅ Sufficient coins completes purchase (HTTP 200)
3. ✅ Balance decreases by exact course price
4. ✅ Negative ledger entry created with course name
5. ✅ Order marked as completed with timestamp
6. ✅ Cart cleared after successful purchase
7. ✅ Multiple sequential purchases work correctly
8. ✅ Exact balance (0 remaining) handled correctly

---

**Test Duration**: ~15 minutes for all scenarios
**Required Access**: Database admin, backend server access
**Test Environment**: Development/staging only
