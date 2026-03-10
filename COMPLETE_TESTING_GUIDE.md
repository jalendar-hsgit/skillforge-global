# SKILLFORGE GLOBAL - COMPLETE TESTING GUIDE
## Test All User Roles: Student → Seller → Mentor → Admin

---

## PART 1: SETUP (5 minutes)

### 1.1 Start Backend API
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```
Expected: "Uvicorn running on http://0.0.0.0:8001"

### 1.2 Start Frontend
```bash
# From project root
npm run dev
```
Expected: "ready - started server on 0.0.0.0:3000"

### 1.3 Verify Database
```bash
cd backend
python -c "import sqlite3; conn = sqlite3.connect('app/data/skillforge.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(f'Users in DB: {cursor.fetchone()[0]}'); conn.close()"
```
Expected: "Users in DB: 11"

---

## PART 2: STUDENT/BUYER COMPLETE FLOW TEST (30 minutes)

### Objective: 
Register as student → Browse marketplace → Add to cart → Complete purchase

### Test Steps:

#### Step 1: Visit Login Page
- **URL**: `http://localhost:3000/login`
- **Expected**: Login form loads
- **Check**: Email input, password input, login button visible

#### Step 2: Register New Student Account
- **URL**: `http://localhost:3000/signup`
- **Action**: Register with:
  - Email: `student-test@example.com`
  - Password: `TestPass123!`
  - Name: `Test Student`
  - Role: Select "Student"
- **Expected**: Registration succeeds, redirects to dashboard
- **API Call**: `POST /api/v1x/auth/register`

#### Step 3: Login as Student
- **URL**: `http://localhost:3000/login`
- **Action**: Login with registered credentials
- **Expected**: Redirects to `/dashboard`
- **API Call**: `POST /api/v1x/auth/login`

#### Step 4: Browse Marketplace
- **URL**: `http://localhost:3000/marketplace`
- **Expected**: Shows 3 demo products:
  - Python Fundamentals Cheat Sheet ($19.99)
  - React Component Templates ($29.99)
  - ML Model Training Guide ($49.99)
- **API Call**: `GET /api/v1x/marketplace/products`

#### Step 5: View Product Detail
- **URL**: `http://localhost:3000/marketplace/[product-id]`
- **Action**: Click on "Python Fundamentals Cheat Sheet"
- **Expected**: Shows product details, price, seller, reviews
- **API Call**: `GET /api/v1x/marketplace/products/{id}`

#### Step 6: Add to Cart
- **URL**: Marketplace product detail page
- **Action**: Click "Add to Cart" button
- **Expected**: Item added, cart count increases
- **API Call**: `POST /api/v1x/marketplace/cart/items`

#### Step 7: View Shopping Cart
- **URL**: `http://localhost:3000/marketplace/cart`
- **Expected**: Shows added item with subtotal
- **Check**: 
  - Product name visible
  - Price: $19.99
  - Subtotal calculated correctly
  - Remove button available
- **API Call**: `GET /api/v1x/marketplace/cart`

#### Step 8: Proceed to Checkout
- **URL**: Cart page
- **Action**: Click "Proceed to Checkout" button
- **Expected**: Redirects to checkout page
- **URL**: `http://localhost:3000/marketplace/checkout`

#### Step 9: Enter Shipping Address
- **Form Fields**:
  - First Name: Test
  - Last Name: Student
  - Address: 123 Main St
  - City: New York
  - State: NY
  - ZIP: 10001
  - Country: USA
- **Expected**: Form accepts input

#### Step 10: Select Payment Method
- **Action**: Select "Credit Card"
- **Expected**: Payment form appears

#### Step 11: Enter Test Card Details
- **Stripe Test Card**: `4242 4242 4242 4242`
- **Expiry**: `12/34` (any future date)
- **CVC**: `123`
- **Expected**: Form accepts input

#### Step 12: Complete Purchase
- **Action**: Click "Place Order" button
- **Expected**: 
  - Order confirmation page shows
  - Order ID generated
  - Total charged: $19.99
- **API Call**: `POST /api/v1x/marketplace/checkout`
- **DB Verification**:
  ```sql
  SELECT * FROM product_purchases WHERE user_id = (SELECT id FROM users WHERE email='student-test@example.com');
  ```

#### Step 13: View Order History
- **URL**: `http://localhost:3000/marketplace/orders`
- **Expected**: Order appears in list with status "Completed"
- **API Call**: `GET /api/v1x/marketplace/orders`

#### Step 14: Download Product
- **Action**: Click "Download" on order
- **Expected**: Product file downloads
- **API Call**: `GET /api/v1x/marketplace/product-files/{id}`

---

## PART 3: SELLER COMPLETE FLOW TEST (30 minutes)

### Objective:
Setup as seller → Create product → Manage inventory → View earnings → Request payout

### Test Steps:

#### Step 1: Register as Seller
- **URL**: `http://localhost:3000/signup`
- **Action**: Register with:
  - Email: `seller-test@example.com`
  - Password: `TestPass123!`
  - Name: `Test Seller`
  - Role: Select "Seller"
- **Expected**: Account created
- **API Call**: `POST /api/v1x/auth/register`

#### Step 2: Complete Seller Profile
- **URL**: `http://localhost:3000/marketplace/seller`
- **Expected**: Seller dashboard loads
- **Action**: Complete profile:
  - Business Name: Test Shop
  - Description: Test seller
  - Bank Account: (Stripe Connect - can skip for demo)
- **Expected**: Profile saved
- **API Call**: `PUT /api/v1x/seller/profile`

#### Step 3: Create Product
- **URL**: `http://localhost:3000/marketplace/seller/create-product`
- **Form Fields**:
  - Product Name: "Advanced Python Course"
  - Description: "Complete Python course with examples"
  - Category: "Programming"
  - Price: $39.99
  - Product Type: "Digital Download"
- **Expected**: Form accepts input

#### Step 4: Upload Product File
- **Action**: Upload PDF/document file
- **Expected**: File uploaded successfully
- **API Call**: `POST /api/v1x/seller/products/{id}/upload`

#### Step 5: Submit for Approval
- **Action**: Click "Submit for Review" button
- **Expected**: Product status: PENDING_APPROVAL
- **API Call**: `POST /api/v1x/seller/products/{id}/submit`

#### Step 6: View Seller Dashboard
- **URL**: `http://localhost:3000/marketplace/seller`
- **Expected**: Shows:
  - Total Sales: 0 (initially)
  - Total Earnings: $0 (initially)
  - Pending Approval Products: 1
  - Published Products: 3 (demo products)
- **API Call**: `GET /api/v1x/seller/analytics/overview`

#### Step 7: View Sales Analytics
- **URL**: `http://localhost:3000/marketplace/seller/analytics`
- **Expected**: Shows sales data (empty initially)
- **API Call**: `GET /api/v1x/seller/analytics/sales`

#### Step 8: View Products
- **URL**: `http://localhost:3000/marketplace/seller/products`
- **Expected**: Lists all seller products with statuses
- **API Call**: `GET /api/v1x/seller/products`

#### Step 9: View Earnings
- **URL**: `http://localhost:3000/marketplace/seller/earnings`
- **Expected**: Shows earnings breakdown by product/period
- **API Call**: `GET /api/v1x/seller/analytics/earnings`

#### Step 10: View Payouts
- **URL**: `http://localhost:3000/marketplace/seller/payouts`
- **Expected**: Shows payout history (empty initially)
- **API Call**: `GET /api/v1x/seller/payouts`

#### Step 11: Request Payout
- **Action**: Click "Request Payout" button (shows if earnings > $100)
- **Expected**: Payout request created
- **API Call**: `POST /api/v1x/seller/payouts/request`

---

## PART 4: MENTOR COMPLETE FLOW TEST (30 minutes)

### Objective:
Setup as mentor → Set availability → View sessions → Track earnings → Create product to sell

### Test Steps:

#### Step 1: Register as Mentor
- **URL**: `http://localhost:3000/signup`
- **Action**: Register with:
  - Email: `mentor-test@example.com`
  - Password: `TestPass123!`
  - Name: `Test Mentor`
  - Role: Select "Mentor"
- **Expected**: Account created
- **API Call**: `POST /api/v1x/auth/register`

#### Step 2: Complete Mentor Profile
- **URL**: `http://localhost:3000/mentors/dashboard`
- **Expected**: Mentor dashboard loads
- **Action**: Complete profile:
  - Bio: "Experienced Python developer"
  - Expertise: Python, Web Development, JavaScript
  - Hourly Rate: $75
  - Certification: Computer Science (optional)
- **Expected**: Profile saved
- **API Call**: `PUT /api/v1x/mentors/{id}/profile`

#### Step 3: Set Availability
- **URL**: `http://localhost:3000/mentors/availability`
- **Action**: Set availability slots:
  - Monday-Friday: 9 AM - 5 PM
  - Weekend: Not available
- **Expected**: Slots saved
- **API Call**: `POST /api/v1x/mentors/availability`

#### Step 4: View Dashboard
- **URL**: `http://localhost:3000/mentors/dashboard`
- **Expected**: Shows:
  - Total Sessions: (from demo data)
  - Total Earnings: (from demo data)
  - Pending Sessions: (from demo data)
- **API Call**: `GET /api/v1x/mentors/analytics/overview`

#### Step 5: View Pending Sessions
- **URL**: `http://localhost:3000/mentors/dashboard/sessions`
- **Expected**: Lists pending mentor sessions
- **API Call**: `GET /api/v1x/mentors/sessions?status=pending`

#### Step 6: Confirm Session
- **Action**: Click confirm on a pending session
- **Expected**: Session status changes to CONFIRMED
- **API Call**: `PUT /api/v1x/mentors/sessions/{id}/confirm`

#### Step 7: View Earnings
- **URL**: `http://localhost:3000/mentors/dashboard/earnings`
- **Expected**: Shows earnings from sessions
- **API Call**: `GET /api/v1x/mentors/analytics/earnings`

#### Step 8: View Analytics
- **URL**: `http://localhost:3000/mentors/dashboard/analytics`
- **Expected**: Shows:
  - Sessions completed
  - Students tutored
  - Ratings/reviews
  - Earnings trends
- **API Call**: `GET /api/v1x/mentors/analytics/detailed`

#### Step 9: Create Product as Mentor
- **URL**: `http://localhost:3000/marketplace/seller/create-product`
- **Action**: Create product (mentors can sell):
  - Name: "Interview Preparation Guide"
  - Price: $29.99
  - Upload file
- **Expected**: Product created
- **API Call**: `POST /api/v1x/seller/products`

#### Step 10: View Combined Earnings
- **Expected**: Earnings from both:
  - Mentor sessions (hourly)
  - Product sales (70% commission)

---

## PART 5: ADMIN COMPLETE FLOW TEST (30 minutes)

### Objective:
Login as admin → Review pending products → Approve/reject → View analytics → Manage payouts

### Test Steps:

#### Step 1: Login as Admin
- **URL**: `http://localhost:3000/login`
- **Action**: Login with admin credentials:
  - Email: `admin@skillforge.com`
  - Password: (check backend seed file for password)
- **Expected**: Redirects to admin dashboard
- **API Call**: `POST /api/v1x/auth/login`

#### Step 2: View Admin Dashboard
- **URL**: `http://localhost:3000/admin/marketplace`
- **Expected**: Shows:
  - Total Products: 4 (3 published + 1 pending)
  - Total Sales: $0 initially
  - Total Revenue: $0 initially
  - Pending Approvals: 1
- **API Call**: `GET /api/v1x/admin/analytics/dashboard`

#### Step 3: View Pending Products
- **URL**: `http://localhost:3000/admin/products`
- **Expected**: Shows product awaiting approval
- **API Call**: `GET /api/v1x/admin/products?status=pending`

#### Step 4: Approve Product
- **URL**: Admin products page
- **Action**: Click "Approve" on pending product
- **Expected**: Product status changes to PUBLISHED
- **API Call**: `PUT /api/v1x/admin/products/{id}/approve`

#### Step 5: Reject Product (Test)
- **Action**: Create another test product and reject it
- **Expected**: Product status changes to REJECTED
- **API Call**: `PUT /api/v1x/admin/products/{id}/reject`

#### Step 6: View Seller Management
- **URL**: `http://localhost:3000/admin/sellers`
- **Expected**: Lists all sellers with:
  - Verification status
  - Sales count
  - Earnings
  - Commission owed
- **API Call**: `GET /api/v1x/admin/sellers`

#### Step 7: Verify Seller
- **URL**: Admin sellers page
- **Action**: Click "Verify" on unverified seller
- **Expected**: Seller verified, can now withdraw funds
- **API Call**: `PUT /api/v1x/admin/sellers/{id}/verify`

#### Step 8: View Platform Analytics
- **URL**: `http://localhost:3000/admin/analytics`
- **Expected**: Shows:
  - Total Revenue: Sum of all sales * 30% commission
  - Sales Trend
  - Top Sellers
  - Top Products
  - User Growth
- **API Call**: `GET /api/v1x/admin/analytics/detailed`

#### Step 9: View Payout Requests
- **URL**: `http://localhost:3000/admin/payouts`
- **Expected**: Lists pending payout requests
- **API Call**: `GET /api/v1x/admin/payouts?status=pending`

#### Step 10: Approve Payout
- **URL**: Admin payouts page
- **Action**: Click "Approve" on payout request
- **Expected**: Payout status changes to APPROVED
- **API Call**: `PUT /api/v1x/admin/payouts/{id}/approve`

#### Step 11: Process Payout to Stripe
- **Action**: Click "Process" to send to Stripe
- **Expected**: Payout sent to seller's Stripe account
- **API Call**: `POST /api/v1x/admin/payouts/{id}/process`

#### Step 12: View Audit Logs
- **URL**: `http://localhost:3000/admin/audit-logs`
- **Expected**: Shows all admin actions with timestamps
- **API Call**: `GET /api/v1x/admin/audit-logs`

#### Step 13: Manage Users
- **URL**: `http://localhost:3000/admin/users`
- **Expected**: Lists all users with:
  - Email
  - Role
  - Status
  - Join date
- **API Call**: `GET /api/v1x/admin/users`

---

## PART 6: VERIFY DATABASE STATE (10 minutes)

### After all tests, verify database reflects changes:

```sql
-- Check total users
SELECT role, COUNT(*) FROM users GROUP BY role;

-- Check marketplace products
SELECT COUNT(*) FROM digital_products WHERE status='PUBLISHED';

-- Check sales
SELECT COUNT(*) FROM product_purchases;

-- Check seller earnings
SELECT seller_id, SUM(amount * 0.7) as earnings FROM product_purchases GROUP BY seller_id;

-- Check mentor sessions
SELECT mentor_id, COUNT(*) FROM mentor_sessions GROUP BY mentor_id;

-- Check pending payouts
SELECT * FROM seller_payouts WHERE status='PENDING';
```

---

## PART 7: AUTOMATED TEST EXECUTION

### Run Complete Test Suite:

```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Or use the test runner
python run_all_tests.py

# Or run E2E tests
python -m pytest tests_e2e/test_all_endpoints_clean.py -v
```

### Expected Output:
```
test_marketplace_listing ... PASSED
test_student_checkout ... PASSED
test_seller_product_creation ... PASSED
test_mentor_session_booking ... PASSED
test_admin_product_approval ... PASSED
test_payment_processing ... PASSED
...
========= 50+ tests PASSED =========
```

---

## PART 8: TROUBLESHOOTING

### Backend Won't Start:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Won't Start:
```bash
npm install
npm run dev
```

### Database Issues:
```bash
# Reset database
rm backend/app/data/skillforge.db*
cd backend
python init_db.py
python seed_all_demo_data.py
```

### API Not Responding:
```bash
# Check if backend is running
curl http://localhost:8001/api/v1x/health
# Should return 200 OK
```

### Login Not Working:
- Check seed file for default credentials
- Verify user email is correct
- Check password in database (encrypted)

---

## EXPECTED RESULTS

### ✅ Student Test Results:
- [x] Can register new account
- [x] Can login
- [x] Can browse marketplace
- [x] Can add products to cart
- [x] Can complete checkout
- [x] Can pay with test Stripe card
- [x] Can download purchased product
- [x] Order appears in history

### ✅ Seller Test Results:
- [x] Can register as seller
- [x] Can complete seller profile
- [x] Can create new product
- [x] Can upload product file
- [x] Can submit for approval
- [x] Can view products
- [x] Can view sales analytics
- [x] Can view earnings
- [x] Can request payout

### ✅ Mentor Test Results:
- [x] Can register as mentor
- [x] Can complete mentor profile
- [x] Can set availability
- [x] Can view pending sessions
- [x] Can confirm sessions
- [x] Can view earnings from sessions
- [x] Can view analytics
- [x] Can create products to sell

### ✅ Admin Test Results:
- [x] Can login as admin
- [x] Can view dashboard
- [x] Can view pending products
- [x] Can approve/reject products
- [x] Can view sellers
- [x] Can verify sellers
- [x] Can view analytics
- [x] Can view payout requests
- [x] Can approve/process payouts
- [x] Can view audit logs

---

## FINAL VERIFICATION

After completing all tests, verify:

1. ✅ **Database Updated**: All test data persisted
2. ✅ **Revenue Calculated**: Commission amounts correct
3. ✅ **Emails Sent**: (if email configured)
4. ✅ **Payments Processed**: Stripe shows test charges
5. ✅ **Payouts Ready**: Admin can process withdrawals
6. ✅ **Roles Enforced**: Can't access pages without proper role
7. ✅ **Data Integrity**: No orphaned records in database

---

## NEXT STEPS

### To Deploy to Production:
1. Configure real Stripe account credentials
2. Setup email service (SendGrid/SMTP)
3. Deploy backend to server
4. Deploy frontend to CDN/hosting
5. Migrate production data
6. Test with real payment cards
7. Monitor for errors

### Status: **✅ READY FOR FULL SYSTEM TEST**
