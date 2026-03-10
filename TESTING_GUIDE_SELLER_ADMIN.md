# QUICK START - TESTING SELLER & ADMIN FEATURES

## Prerequisites

```bash
# Terminal 1: Start Backend
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
python seed_all_demo_data.py  # Populate demo data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

```bash
# Terminal 2: Start Frontend
cd ..
npm install
npm run dev
# Frontend at: http://localhost:3000
```

---

## Test Accounts (After Running Seed)

### Sellers
- **Sarah Chen** (Mentor/Seller)
  - Email: sarah.chen@skillforge.com
  - Password: password123
  - Has: 3 digital products
  
- **David Kumar** (Mentor/Seller)
  - Email: david.kumar@skillforge.com
  - Password: password123
  - Has: 3 digital products

### Admin
- **Admin User**
  - Email: admin@skillforge.com
  - Password: password123
  - Can approve products, verify sellers, process payouts

---

## TESTING FLOWS

### Flow 1: Test Seller Product Creation

**Step 1: Login as Seller**
```
1. Go to http://localhost:3000
2. Click "Login"
3. Email: sarah.chen@skillforge.com
4. Password: password123
5. Click "Sign In"
```

**Step 2: Navigate to Products**
```
1. Click sidebar or menu
2. Go to "Marketplace" → "My Products"
3. Should see 3 existing products:
   - "Python Cheatsheet" (PUBLISHED)
   - "React Templates" (PUBLISHED)
   - "Figma Design Guide" (PUBLISHED)
```

**Step 3: Create New Product**
```
1. Click "Create New Product" button
2. Fill in form:
   - Name: "Testing Product 123"
   - Description: "This is a test product"
   - Product Type: Select "TEMPLATE"
   - Price: 49.99
3. Click "Save as Draft"
4. System should:
   - POST to /api/v1x/marketplace/seller/products
   - Create product with status: DRAFT
   - Redirect back to products list
```

**Step 4: Verify Product Created**
```
1. Back on products page
2. Should see new product at top with DRAFT status
3. Try Edit → Update price to 59.99
4. Click "Publish" to change status
5. Product now visible to public
```

**Step 5: Delete Product**
```
1. Click trash/delete icon
2. Confirm deletion
3. Product removed from list
4. DELETE to /api/v1x/marketplace/seller/products/[id]
```

---

### Flow 2: Test Admin Product Approval

**Step 1: Create Product as Seller**
```
1. Login as sarah.chen@skillforge.com
2. Create new product
3. Save as DRAFT (don't publish)
```

**Step 2: Login as Admin**
```
1. Logout from seller account
2. Login as admin:
   - Email: admin@skillforge.com
   - Password: password123
```

**Step 3: View Marketplace**
```
1. Navigate to Admin Dashboard
2. Click "Marketplace" section
3. Click "Products" tab
4. Should see products awaiting approval
```

**Step 4: Approve Product**
```
1. Find the product you just created
2. Click "View" or "Approve"
3. Review product details:
   - Name, description, price
   - Seller information (Sarah Chen)
4. Click "Approve"
5. Modal appears asking for notes (optional)
6. Click "Confirm Approve"
7. Status changes to PUBLISHED
```

**Step 5: Verify Product Approved**
```
1. Go to public Marketplace
2. Search for product name
3. Should appear in available products
4. Price and description visible
5. "Buy Now" button available
```

---

### Flow 3: Test Admin Seller Verification

**Step 1: View Sellers**
```
1. Login as admin@skillforge.com
2. Go to Admin Dashboard
3. Click "Marketplace" → "Sellers"
4. Should see list of all sellers
```

**Step 2: Verify a Seller**
```
1. Find seller "Sarah Chen" in list
2. See status: "VERIFIED" or "PENDING"
3. If PENDING:
   - Click on seller to view details
   - Review seller information
   - Click "Verify" button
   - Add notes (optional): "Documents verified"
   - Confirm
```

**Step 3: Confirm Verification**
```
1. Status updates to "VERIFIED"
2. Seller can now publish products
3. All seller's products automatically approved
```

---

### Flow 4: Test Product Purchase

**Step 1: Browse as Customer**
```
1. Logout or use incognito window
2. Go to http://localhost:3000/marketplace
3. Browse available products
4. Should see published products from all sellers
```

**Step 2: Purchase Product**
```
1. Click on a product card
2. View details:
   - Name, description, price
   - Seller information
   - Preview files (if available)
3. Click "Buy Now" button
4. Proceed to checkout
```

**Step 3: Verify Order Created**
```
1. Login as buyer
2. View "My Orders" or "Purchases"
3. New order appears with:
   - Order number
   - Product name
   - Price
   - Download link
```

**Step 4: Verify Seller Sees Sale**
```
1. Login as seller
2. Go to "My Products" → "Orders"
3. New sale appears
4. Go to "Analytics"
5. Sales count and revenue updated
```

---

### Flow 5: Test Payout Request

**Step 1: Request Payout as Seller**
```
1. Login as sarah.chen@skillforge.com
2. Go to "Seller Dashboard" → "Payouts" (if available)
   Or → "Analytics"
3. Click "Request Payout"
4. Enter amount: 500.00
5. Select bank account (if multiple)
6. Click "Submit Request"
```

**Step 2: Admin Processes Payout**
```
1. Login as admin@skillforge.com
2. Go to Admin Dashboard
3. Click "Payouts" section
4. Find pending payout from Sarah Chen
5. Review details:
   - Amount: $500.00
   - Sales count backing payout
6. Click "Process"
7. Enter transaction ID: TXN-TEST-001
8. Click "Complete Payout"
```

**Step 3: Verify Payout Completed**
```
1. Status changes to "COMPLETED"
2. Seller sees payment in account
3. Analytics updated to show payout processed
```

---

## API TESTING WITH CURL

### Get Seller Products
```bash
curl -X GET http://localhost:8001/api/v1x/marketplace/seller/products \
  -H "Content-Type: application/json" \
  -b "sessionid=YOUR_SESSION_COOKIE"
```

### Create a Product
```bash
curl -X POST http://localhost:8001/api/v1x/marketplace/seller/products \
  -H "Content-Type: application/json" \
  -b "sessionid=YOUR_SESSION_COOKIE" \
  -d '{
    "name": "Test Course",
    "description": "Test description",
    "product_type": "COURSE",
    "price": 99.99
  }'
```

### Admin: Get Pending Products
```bash
curl -X GET "http://localhost:8001/api/v1x/admin/marketplace/products?status=DRAFT" \
  -H "Content-Type: application/json" \
  -b "sessionid=YOUR_SESSION_COOKIE"
```

### Admin: Approve Product
```bash
curl -X PUT http://localhost:8001/api/v1x/admin/marketplace/products/1/approve \
  -H "Content-Type: application/json" \
  -b "sessionid=YOUR_SESSION_COOKIE" \
  -d '{
    "status": "PUBLISHED",
    "notes": "Looks great!"
  }'
```

### Admin: Get Dashboard Stats
```bash
curl -X GET http://localhost:8001/api/v1x/admin/marketplace/dashboard \
  -b "sessionid=YOUR_SESSION_COOKIE"
```

---

## TROUBLESHOOTING

### Products Not Loading?
- [ ] Check browser console for errors
- [ ] Verify backend is running on port 8001
- [ ] Check NEXT_PUBLIC_API_BASE in .env.local
- [ ] Verify session cookie is being sent
- [ ] Check that URL uses `/api/v1x/marketplace/` prefix

### Product Creation Failing?
- [ ] Verify form fields filled correctly
- [ ] Check that user is logged in
- [ ] Verify POST endpoint returns 201 or 200
- [ ] Check response for error message
- [ ] Verify product type is valid enum value

### Admin Can't See Products?
- [ ] Verify logged in as admin user
- [ ] Check admin role is set correctly
- [ ] Verify products exist in database
- [ ] Check admin/marketplace/products endpoint
- [ ] Verify filter parameters are correct

### Files Not Uploading?
- [ ] Check file size limits
- [ ] Verify content type: multipart/form-data
- [ ] Check upload endpoints exist
- [ ] Verify S3 or file storage configured
- [ ] Check error response for details

---

## EXPECTED RESULTS

### After Running Seed Script:
- ✅ 7 Users created (2 admin, 5 regular, 2 are sellers)
- ✅ 4 Mentors with marketplace access
- ✅ 3 Digital Products per mentor (9 total)
- ✅ 8 Mentor Sessions scheduled
- ✅ Products in various statuses (DRAFT, PUBLISHED)

### After Testing Seller Creation:
- ✅ New product visible in seller's product list
- ✅ Product status: DRAFT initially
- ✅ Can edit and update product
- ✅ Can upload files (thumbnail, content, preview)
- ✅ Can publish product (status → PUBLISHED)
- ✅ Can delete product

### After Testing Admin Approval:
- ✅ Admin can see pending products
- ✅ Admin can approve/reject
- ✅ Product status changes on approval
- ✅ Published products visible in marketplace
- ✅ Rejected products show rejection reason

### After Testing Purchase:
- ✅ Order created with unique order_number
- ✅ Seller sees sale in orders list
- ✅ Sales count increases
- ✅ Revenue tracked in analytics
- ✅ Customer has access to files

---

## DEMO DATA STRUCTURE

After running `python seed_all_demo_data.py`:

```
Users:
  - superadmin@skillforge.com (SUPERADMIN) - 2
  - admin@skillforge.com (ADMIN) - 1
  - sarah.chen@skillforge.com (MENTOR/SELLER) - 3
  - david.kumar@skillforge.com (MENTOR/SELLER) - 3
  - emily.rodriguez@skillforge.com (MENTOR/SELLER) - 2
  - james.patterson@skillforge.com (MENTOR/SELLER) - 1
  Total: 7 users

Sellers (Mentors with marketplace access):
  - Sarah Chen - 3 products
  - David Kumar - 3 products
  - Emily Rodriguez - 2 products
  - James Patterson - 1 product
  Total: 4 sellers, 9 products

Products:
  - Python Cheatsheet - $29.99 - PUBLISHED
  - React Templates - $49.99 - PUBLISHED
  - Figma Design Guide - $39.99 - PUBLISHED
  - (And more per seller)

Statuses:
  - DRAFT: 1-2 products (awaiting seller action)
  - PUBLISHED: 7-8 products (ready for sale)
  - ARCHIVED: 0 (none initially)
```

---

## NEXT STEPS AFTER TESTING

1. ✅ API endpoints fixed
2. ✅ Backend endpoints verified
3. ⏳ Run seed script
4. ⏳ Test seller creation flow
5. ⏳ Test admin approval workflow
6. ⏳ Test payment processing
7. ⏳ Test payout workflow
8. ⏳ Deploy to production
