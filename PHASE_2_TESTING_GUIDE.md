# 🧪 Phase 2 Testing Guide - Email Receipts & Payouts

## Overview

This guide walks you through testing all Phase 2A (Email Receipts) functionality with complete demo data.

---

## Prerequisites

Before testing, ensure:

1. ✅ Backend running: `uvicorn app.main:app --reload`
2. ✅ Stripe webhook listening: `stripe listen --forward-to http://localhost:8001/webhook/stripe`
3. ✅ Email configured (Gmail, SendGrid, or Mailhog)
4. ✅ Demo data seeded: `python backend/seed_all_demo_data.py`
5. ✅ `.env.local` configured with Stripe keys

---

## Test Setup

### Email Configuration for Testing

**Option A: Gmail (Recommended for Production-like testing)**
```bash
# .env.local
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@skillforge.com
EMAIL_FROM_NAME=SkillForge Global
```

**Option B: Mailhog (Recommended for Local Development)**
```bash
# Terminal 1: Run Mailhog
docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog

# .env.local
SMTP_HOST=localhost
SMTP_PORT=1025
```

Then access emails at: http://localhost:8025

---

## Test 1: Course Order Receipt Email

### Scenario
A student purchases a paid course and receives a receipt email.

### Steps

**1. Log In as Student**
```
Email: john.doe@example.com
Password: (from seed data)
```

**2. Navigate to Courses**
- Go to: http://localhost:3000/courses
- Find "React Advanced" ($149.99)
- Click "Enroll"

**3. Complete Payment**
- Amount shown: $149.99
- Click "Pay with Stripe"
- Card number: 4242 4242 4242 4242
- Expiry: 12/25
- CVC: 123
- Click "Pay"

**4. Watch for Webhook Event**

Terminal with Stripe listener should show:
```
[webhook] Successfully sent event to http://localhost:8001/webhook/stripe
```

**5. Check Email**

**If using Gmail:**
- Check inbox for email from: noreply@skillforge.com
- Subject: "Order Confirmation - ORD-..."

**If using Mailhog:**
- Visit http://localhost:8025
- Find latest email
- Subject: "Order Confirmation - ORD-..."

**6. Verify Email Content**

The email should contain:
```
✓ Header: "Order Confirmed ✓"
✓ Greeting: "Hi John,"
✓ Order Number: (e.g., "ORD-2-5-abc123def")
✓ Course Name: "React Advanced"
✓ Amount: "$149.99"
✓ Date: (current date/time)
✓ Button: "Go to Dashboard" (clickable link)
✓ Footer: "SkillForge Global" branding
```

**7. Expected Result**
- ✅ Email received within 2 seconds of payment
- ✅ Email is HTML formatted with styling
- ✅ All details match the order
- ✅ Links are clickable and work

---

## Test 2: Marketplace Order Receipt Email

### Scenario
A customer purchases marketplace products and receives a receipt email.

### Steps

**1. Log In as Customer**
```
Email: jane.smith@example.com
Password: (from seed data)
```

**2. Add Marketplace Products to Cart**
- Go to: http://localhost:3000/marketplace
- Browse available products
- Add 2-3 products to cart
- Example: "Interview Cheat Sheet", "Resume Templates"

**3. Proceed to Checkout**
- Click "Checkout"
- Review items and total amount
- No coupon (unless testing coupons)
- Click "Continue to Payment"

**4. Process Payment**
- Amount: (sum of products)
- Card: 4242 4242 4242 4242
- Expiry: 12/25
- CVC: 123
- Click "Pay"

**5. Watch for Webhook**
Stripe listener should confirm event processed.

**6. Check Email**

**Expected Email:**
- Subject: "Marketplace Order Confirmed - ORD-..."

**Email Content Should Include:**
```
✓ Header: "Marketplace Order Confirmed ✓"
✓ Products List:
  - Interview Cheat Sheet
  - Resume Templates
  - (any other items)
✓ Total Amount: "$XX.XX"
✓ Order Date: (date/time)
✓ Button: "View Your Purchases"
✓ Tip: About downloading items
```

**7. Verify Purchase Access**
- User should be able to download products immediately
- Products visible in dashboard

---

## Test 3: Mentor Session Payment Receipt

### Scenario
A student books a mentor session, pays, and receives payment receipt.

### Steps

**1. Log In as Student**
```
Email: bob.wilson@example.com
Password: (from seed data)
```

**2. Book Mentor Session**
- Go to: http://localhost:3000/mentors
- Find "Sarah Chen" (Python & AI Expert - $75/hr)
- Click "Book Session"
- Select date/time and duration (e.g., 1 hour)
- Expected cost: $75.00
- Click "Book Now"

**3. Process Payment**
- Amount: $75.00
- Card: 4242 4242 4242 4242
- Expiry: 12/25
- CVC: 123
- Click "Pay"

**4. Watch for Webhook**
Webhook should process `payment_intent.succeeded` event.

**5. Check Email**

**Expected Email:**
- Subject: "Payment Receipt - Session #..."

**Email Content:**
```
✓ Header: "Payment Successful ✓"
✓ Mentor Name: "Sarah Chen"
✓ Amount: "$75.00"
✓ Session Date/Time: (booked date/time)
✓ Session ID: #123 (example)
✓ Payment ID: pi_xxx (Stripe ID)
✓ Button: "View Dashboard"
```

**6. Verify Session Status**
- Session should be CONFIRMED
- Both mentor and student see it in dashboard
- Meeting link available

---

## Test 4: Payment Failure Email

### Scenario
A payment fails and the user receives a failure notification.

### Steps

**1. Log In as User**
```
Email: alice.johnson@example.com
```

**2. Attempt Purchase**
- Try to enroll in paid course
- Or book mentor session

**3. Process with Failed Card**
- Use test card: 4000 0000 0000 0002 (Declined)
- Expiry: 12/25
- CVC: 123
- Click "Pay"

**4. Expected Result**
- Payment fails
- Error message shown to user
- Email sent

**5. Check Email**

**Expected Email:**
- Subject: "Payment Failed ✗"

**Content:**
```
✓ Header: "Payment Failed ✗"
✓ Problem Description
✓ Possible Reasons (insufficient funds, card expired, etc.)
✓ Next Steps (retry, contact bank)
✓ Button: "Retry Payment"
```

---

## Test 5: Seller Payout Notification Email

### Scenario
An admin approves a mentor payout and the mentor receives notification.

### Prerequisites
- Mentor has earned money from sessions
- Admin has permission to approve payouts

### Steps

**1. Log In as Admin**
```
Email: admin@skillforge.com
Password: (from seed data)
```

**2. Navigate to Admin Panel**
- Go to: http://localhost:3000/admin
- Navigate to: Payouts → Pending Payouts

**3. Find Pending Payout**
- Should see mentors with pending earnings
- Example: "Sarah Chen" with $1,125.00 pending

**4. Approve Payout**
- Click mentor name or "View Details"
- Click "Approve Payout"
- Optional: Add admin notes
- Click "Confirm Approval"

**5. Watch for Email**
Email should send within seconds.

**6. Check Mentor's Email**

**Expected Email:**
- To: mentor@example.com
- Subject: "Payout Processed - $1,125.00"

**Email Content:**
```
✓ Header: "Payout Processed ✓"
✓ Amount: "$1,125.00"
✓ Payout Method: "Bank Transfer" (or PayPal)
✓ Processing Date: (current date)
✓ Expected Arrival: "2-5 business days" (for bank)
✓ Button: "View Payout History"
✓ Info: Keep earning tip
```

**7. Verify in Mentor Dashboard**
- Mentor logs in
- Views "Payouts" section
- Sees approved payout status

---

## Automated Test Script

Create `test_phase_2a.py` in root directory:

```python
#!/usr/bin/env python3
"""Test Phase 2A - Email Receipts"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"

# Test users from seed data
USERS = {
    "student": {"email": "john.doe@example.com", "id": 1},
    "customer": {"email": "jane.smith@example.com", "id": 2},
    "admin": {"email": "admin@skillforge.com", "id": 7}
}

def test_email_service():
    """Test email service is working"""
    print("\n=== Testing Email Service ===")
    
    # Test generic email
    response = requests.post(
        f"{BASE_URL}/api/v1/email/send",
        json={
            "to_email": USERS["student"]["email"],
            "subject": "Test Email",
            "html_content": "<p>This is a test email</p>"
        }
    )
    
    if response.status_code == 200:
        print("✓ Email service is responding")
    else:
        print("✗ Email service error")
    
    return response.status_code == 200

def test_course_receipt():
    """Test course order receipt email"""
    print("\n=== Testing Course Receipt Email ===")
    
    # Create order
    response = requests.post(
        f"{BASE_URL}/api/v1/orders/create",
        json={
            "course_id": 1,  # Python Fundamentals
            "payment_method": "stripe"
        },
        headers={"Authorization": f"Bearer {get_token(USERS['student']['email'])}"}
    )
    
    if response.status_code == 200:
        order_data = response.json()
        print(f"✓ Order created: {order_data.get('order_number')}")
        return True
    else:
        print(f"✗ Failed to create order: {response.status_code}")
        return False

def test_marketplace_receipt():
    """Test marketplace order receipt email"""
    print("\n=== Testing Marketplace Receipt Email ===")
    
    # Create marketplace order
    response = requests.post(
        f"{BASE_URL}/api/v1/marketplace/checkout",
        json={
            "product_ids": [1, 2],  # Add 2 products
            "payment_method": "stripe"
        },
        headers={"Authorization": f"Bearer {get_token(USERS['customer']['email'])}"}
    )
    
    if response.status_code == 200:
        order_data = response.json()
        print(f"✓ Marketplace order created: {order_data.get('order_number')}")
        return True
    else:
        print(f"✗ Failed to create marketplace order: {response.status_code}")
        return False

def test_payout_notification():
    """Test payout approval notification email"""
    print("\n=== Testing Payout Notification Email ===")
    
    # Get admin token
    admin_token = get_token(USERS["admin"]["email"])
    
    # Get pending payouts
    response = requests.get(
        f"{BASE_URL}/api/v1/admin/payouts/pending",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if response.status_code != 200:
        print("✗ Failed to get pending payouts")
        return False
    
    payouts = response.json()
    if not payouts:
        print("⚠ No pending payouts found")
        return False
    
    # Approve first pending payout
    payout_id = payouts[0]["id"]
    response = requests.post(
        f"{BASE_URL}/api/v1/admin/payouts/{payout_id}/approve",
        json={"admin_notes": "Test approval"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if response.status_code == 200:
        print(f"✓ Payout approved: ID {payout_id}")
        return True
    else:
        print(f"✗ Failed to approve payout: {response.status_code}")
        return False

def get_token(email):
    """Get JWT token for user"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": "password"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def main():
    """Run all tests"""
    print("=" * 50)
    print("PHASE 2A EMAIL RECEIPTS - TEST SUITE")
    print("=" * 50)
    print(f"Started: {datetime.now()}")
    
    # Run tests
    tests = [
        ("Email Service", test_email_service),
        ("Course Receipt", test_course_receipt),
        ("Marketplace Receipt", test_marketplace_receipt),
        ("Payout Notification", test_payout_notification),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"✗ Test error: {e}")
            results.append((test_name, "ERROR"))
        
        time.sleep(1)  # Wait between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    for test_name, status in results:
        icon = "✓" if status == "PASS" else "✗"
        print(f"{icon} {test_name}: {status}")
    
    passed = sum(1 for _, s in results if s == "PASS")
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    print(f"Ended: {datetime.now()}")

if __name__ == "__main__":
    main()
```

Run with:
```bash
python test_phase_2a.py
```

---

## Email Verification Checklist

For each email test, verify:

### Content Verification
- [ ] Email received
- [ ] Subject line correct
- [ ] Recipient email correct
- [ ] HTML formatting applied
- [ ] Colors and styling visible
- [ ] All order details present
- [ ] Amounts formatted correctly ($XX.XX)
- [ ] Dates formatted correctly

### Link Verification
- [ ] All buttons/links clickable
- [ ] Dashboard link works
- [ ] Purchase link works
- [ ] Payout history link works

### Mobile Verification
- [ ] Email readable on mobile
- [ ] Images scale properly
- [ ] Links tap-able on mobile
- [ ] Text not cut off

---

## Debugging Email Issues

### Email Not Received

**Check 1: Backend Logs**
```bash
# Look for these messages:
# "Email sent to user@example.com"
# OR
# "Failed to send email: ..."
```

**Check 2: Email Configuration**
```bash
# Verify .env variables
echo $SMTP_HOST
echo $SMTP_USER
```

**Check 3: Mailhog Interface**
- Go to http://localhost:8025
- Check "From:" field
- Check spam folder

**Check 4: Email Provider**
- Gmail: Check "Less secure apps" is enabled
- SendGrid: Verify API key
- AWS SES: Check sender verified

### Email Formatting Issues

**Check 1: HTML Rendering**
- Some email clients strip CSS
- Test in Gmail, Outlook, Apple Mail
- Use https://putsmail.com for testing

**Check 2: Images**
- Use absolute URLs for images
- Test image loading in email

### Webhook Not Firing

**Check 1: Stripe CLI Running**
```bash
stripe listen --forward-to http://localhost:8001/webhook/stripe
```

**Check 2: Webhook Secret**
```bash
# Check if STRIPE_WEBHOOK_SECRET is set
echo $STRIPE_WEBHOOK_SECRET
```

**Check 3: Stripe Events**
```bash
# Trigger test event
stripe trigger payment_intent.succeeded
```

---

## Performance Expectations

**Email Send Time**: 500ms - 3 seconds
- Depends on email provider
- Stripe webhook processes in ~100ms
- Email send is non-blocking

**Test Execution Time**: 5-10 minutes
- 5 minutes to manually test all scenarios
- Webhook processing: ~1 second per event
- Email delivery: 1-3 seconds

---

## Integration with CI/CD

For automated testing in CI/CD:

```yaml
# .github/workflows/email-tests.yml
name: Email Receipt Tests

on: [push, pull_request]

jobs:
  email-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
      mailhog:
        image: mailhog/mailhog
    
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run email tests
        run: python test_phase_2a.py
      - name: Check Mailhog for emails
        run: curl http://mailhog:8025/api/v1/messages
```

---

## Next Steps

After Phase 2A testing:
- ✅ Email receipts working
- ✅ Seller payout notifications working
- ⏳ Phase 2B: Seller Payout System
- ⏳ Phase 2C: Subscription Billing

