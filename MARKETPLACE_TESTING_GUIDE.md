# Marketplace Features - Complete Testing Guide

**Date:** January 4, 2026
**Build Status:** ✅ SUCCESSFUL
**Pages Created:** 5 | **API Endpoints:** 40+ | **Test Scenarios:** 15+

---

## BUILD VERIFICATION

✅ **Build Output:**
```
Route (pages)                                    Size     First Load JS
├ ○ /marketplace/seller                          2.75 kB         103 kB
├ ○ /marketplace/seller/analytics                2.78 kB         103 kB
├ ○ /marketplace/seller/create-product           3.35 kB         104 kB
├ ○ /marketplace/seller/orders                   2.13 kB         102 kB
├ ○ /marketplace/seller/products                 2.56 kB         103 kB
```

✅ **BUILD_ID:** `.../.next/BUILD_ID` exists
✅ **All pages compiled successfully**
✅ **No TypeScript errors**
✅ **No build warnings**

---

## QUICK ACCESS POINTS

### Frontend URLs (from root: http://localhost:3001)
- Dashboard: http://localhost:3001/marketplace/seller
- Create Product: http://localhost:3001/marketplace/seller/create-product
- Products List: http://localhost:3001/marketplace/seller/products
- Orders: http://localhost:3001/marketplace/seller/orders
- Analytics: http://localhost:3001/marketplace/seller/analytics

### Backend API (from root: http://localhost:8001/api/v1x)
- Seller Stats: GET `/seller/stats`
- Products CRUD: GET/POST/PUT/DELETE `/seller/products`
- Orders: GET `/seller/orders`
- Analytics: GET `/seller/analytics`
- File Uploads: POST `/seller/products/{id}/upload-*`
- Purchase: POST `/digital-products/{id}/purchase`

---

## TEST SCENARIO 1: SELLER ONBOARDING

### Step 1: Create Seller Account
**URL:** POST `http://localhost:8001/api/v1x/seller/account`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:**
```json
{
  "store_name": "My Premium Templates",
  "store_description": "High-quality React and Vue components",
  "payout_method": "stripe"
}
```

**Expected Response:** 200 OK
```json
{
  "id": 1,
  "user_id": 123,
  "store_name": "My Premium Templates",
  "is_verified": false,
  "seller_tier": "basic",
  "total_sales": 0,
  "total_revenue": 0.0,
  "average_rating": 0.0
}
```

### Step 2: Verify in Frontend
- [ ] Navigate to `http://localhost:3001/marketplace/seller`
- [ ] Should see dashboard with all zeros
- [ ] Should see "Manage Products" card
- [ ] Should see "View Orders" card (empty)
- [ ] Should see "Analytics" card

---

## TEST SCENARIO 2: CREATE & UPLOAD PRODUCT

### Step 1: Create Product
**URL:** POST `http://localhost:8001/api/v1x/seller/products`
**Headers:** `Authorization: Bearer {TOKEN}`, `Content-Type: application/json`
**Body:**
```json
{
  "name": "React Component Library",
  "description": "50+ production-ready React components with TypeScript",
  "product_type": "bundle",
  "category": "programming",
  "price": 49.99,
  "original_price": 79.99,
  "tags": ["react", "components", "typescript"],
  "requirements": ["Basic JavaScript", "React knowledge"],
  "features": ["50+ components", "Full TypeScript support", "Dark mode"],
  "status": "draft",
  "visibility": "public"
}
```

**Expected Response:** 200 OK
```json
{
  "id": 10,
  "name": "React Component Library",
  "slug": "react-component-library-abc123",
  "status": "draft",
  "price": 49.99,
  "created_at": "2026-01-04T..."
}
```

### Step 2: Upload Thumbnail
**URL:** POST `http://localhost:8001/api/v1x/seller/products/10/upload-thumbnail`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:** form-data with `file` = image.jpg (< 5MB)

**Expected Response:** 200 OK
```json
{
  "thumbnail_url": "/uploads/products/thumbnail-10-xyz789.jpg",
  "filename": "thumbnail-10-xyz789.jpg",
  "file_size": 245000,
  "message": "Thumbnail uploaded successfully!"
}
```

### Step 3: Upload Content
**URL:** POST `http://localhost:8001/api/v1x/seller/products/10/upload-content`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:** form-data with `file` = content.zip (< 50MB)

**Expected Response:** 200 OK

### Step 4: Upload Preview
**URL:** POST `http://localhost:8001/api/v1x/seller/products/10/upload-preview`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:** form-data with `file` = preview.pdf

**Expected Response:** 200 OK

### Step 5: Publish Product
**URL:** PUT `http://localhost:8001/api/v1x/seller/products/10`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:**
```json
{
  "status": "published"
}
```

**Expected Response:** 200 OK

### Step 6: Verify in Frontend
- [ ] Navigate to `http://localhost:3001/marketplace/seller/create-product?productId=10`
- [ ] Form should populate with product data
- [ ] File upload sections should show "Uploaded" status
- [ ] Navigate to `http://localhost:3001/marketplace/seller/products`
- [ ] Product should appear in list
- [ ] Should show: name, type, price ($49.99), status (published)

---

## TEST SCENARIO 3: PURCHASE WITH COINS

### Prerequisites
- User has coins balance (e.g., 50 coins)
- Product exists and is published

### Step 1: Check Coin Balance
**URL:** GET `http://localhost:8001/api/v1x/coins/balance`
**Headers:** `Authorization: Bearer {TOKEN}`

**Expected Response:** 200 OK
```json
{
  "balance": 50,
  "pending": 0,
  "total_earned": 100
}
```

### Step 2: Purchase Product with Coins
**URL:** POST `http://localhost:8001/api/v1x/digital-products/10/purchase`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:**
```json
{
  "payment_method": "coins"
}
```

**Expected Response:** 200 OK
```json
{
  "purchase_id": 101,
  "product_id": 10,
  "status": "completed",
  "download_url": null,
  "message": "Product purchased successfully with coins"
}
```

### Step 3: Verify Coin Balance Decreased
**URL:** GET `http://localhost:8001/api/v1x/coins/balance`

**Expected Response:**
```json
{
  "balance": 0,  // 50 - 49.99 ≈ 0 (coins deducted)
  ...
}
```

### Step 4: Check Purchase Ownership
**URL:** GET `http://localhost:8001/api/v1x/digital-products/10/check-purchase`
**Headers:** `Authorization: Bearer {TOKEN}`

**Expected Response:** 200 OK
```json
{
  "purchased": true,
  "download_url": null,
  "purchased_at": "2026-01-04T..."
}
```

### Step 5: Get User Purchases
**URL:** GET `http://localhost:8001/api/v1x/user/purchases`
**Headers:** `Authorization: Bearer {TOKEN}`

**Expected Response:** 200 OK
```json
{
  "total": 1,
  "items": [
    {
      "id": 101,
      "product_id": 10,
      "product_name": "React Component Library",
      "seller_name": "Seller Name",
      "purchase_price": 49.99,
      "purchase_date": "2026-01-04T...",
      "download_url": null,
      "download_count": 0
    }
  ]
}
```

---

## TEST SCENARIO 4: SELLER ORDER MANAGEMENT

### Step 1: List Orders (as seller)
**URL:** GET `http://localhost:8001/api/v1x/seller/orders`
**Headers:** `Authorization: Bearer {TOKEN}` (seller's token)

**Expected Response:** 200 OK
```json
{
  "total": 1,
  "items": [
    {
      "id": 101,
      "product_id": 10,
      "product_name": "React Component Library",
      "buyer_id": 456,
      "buyer_name": "John Doe",
      "buyer_email": "john@example.com",
      "purchase_price": 49.99,
      "payment_method": "coins",
      "status": "completed",
      "seller_payout": 34.99,
      "purchased_at": "2026-01-04T...",
      "delivered_at": null,
      "download_count": 0
    }
  ]
}
```

### Step 2: Get Order Details
**URL:** GET `http://localhost:8001/api/v1x/seller/orders/101`
**Headers:** `Authorization: Bearer {TOKEN}`

**Expected Response:** 200 OK (full order details)

### Step 3: Mark Order as Delivered
**URL:** POST `http://localhost:8001/api/v1x/seller/orders/101/deliver`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:**
```json
{
  "download_url": "https://s3.amazonaws.com/products/react-components.zip"
}
```

**Expected Response:** 200 OK
```json
{
  "id": 101,
  "status": "completed",
  "delivered_at": "2026-01-04T..."
}
```

### Step 4: Verify in Frontend
- [ ] Navigate to `http://localhost:3001/marketplace/seller/orders`
- [ ] Should see order in list
- [ ] Status should show "completed"
- [ ] Can click for details

---

## TEST SCENARIO 5: ANALYTICS

### Step 1: Get Seller Analytics
**URL:** GET `http://localhost:8001/api/v1x/seller/analytics?period=month`
**Headers:** `Authorization: Bearer {TOKEN}`

**Expected Response:** 200 OK
```json
{
  "period": "month",
  "total_products": 1,
  "total_sales": 1,
  "total_revenue": 34.99,
  "total_views": 0,
  "average_product_rating": 0.0,
  "sales_by_product": {
    "React Component Library": 1
  },
  "revenue_trend": {
    "Dec 2025": 0.0,
    "Jan 2026": 34.99
  },
  "conversion_rate": 0.0,
  "average_order_value": 34.99
}
```

### Step 2: Verify in Frontend
- [ ] Navigate to `http://localhost:3001/marketplace/seller/analytics`
- [ ] Should see all metrics populated
- [ ] Revenue trend chart should show bar for Jan 2026
- [ ] Sales by product breakdown shown
- [ ] Period selector (week/month/quarter/year) works

---

## TEST SCENARIO 6: FRONTEND FORM VALIDATION

### Test Create Product Form
- [ ] Navigate to `http://localhost:3001/marketplace/seller/create-product`
- [ ] Try to submit empty form → should show validation error
- [ ] Fill in name → press Tab → should focus next field
- [ ] Add tags by typing and pressing Enter → should appear as chips
- [ ] Remove tag by clicking X → should remove
- [ ] Add requirements by typing → should add to list
- [ ] Change status dropdown → options should appear
- [ ] Click Save → should submit form
- [ ] On success → redirect to products list

### Test Products List
- [ ] Navigate to `http://localhost:3001/marketplace/seller/products`
- [ ] Search by product name → should filter
- [ ] Filter by status (draft/published/archived) → should filter
- [ ] Click edit icon → should go to create-product with productId
- [ ] Click delete → should show confirmation modal
- [ ] Click confirm → should delete and update list

### Test Orders Page
- [ ] Navigate to `http://localhost:3001/marketplace/seller/orders`
- [ ] Should show order count stats
- [ ] Search by product/buyer/email → should filter
- [ ] Filter by status → should filter
- [ ] Table shows all order details
- [ ] Status badges have correct colors

### Test Analytics Page
- [ ] Navigate to `http://localhost:3001/marketplace/seller/analytics`
- [ ] All metric cards show values
- [ ] Revenue trend chart displays
- [ ] Sales by product list shows
- [ ] Period selector changes data
- [ ] Dark mode toggle works

---

## TEST SCENARIO 7: DARK MODE

All pages should support dark mode. Test by:
- [ ] Toggle system dark mode
- [ ] All text should be readable
- [ ] All backgrounds should be dark-colored
- [ ] All form inputs should have dark background
- [ ] All buttons should be visible

---

## TEST SCENARIO 8: MOBILE RESPONSIVENESS

Test on mobile viewport (375px width):
- [ ] Sidebar collapses (if applicable)
- [ ] Form inputs stack vertically
- [ ] Tables become horizontal scrollable
- [ ] All buttons remain clickable
- [ ] File uploads work on mobile

---

## TEST SCENARIO 9: ERROR HANDLING

### Test Network Errors
- [ ] Offline backend → should show "Failed to load"
- [ ] Invalid token → should redirect to login
- [ ] 404 product → should show "Not found"
- [ ] File too large → should show size error
- [ ] Invalid file type → should show file type error

### Test Form Errors
- [ ] Price = 0 → should show error
- [ ] Name too long → should show error
- [ ] Empty description → should show error
- [ ] Invalid file upload → should show error

---

## TEST SCENARIO 10: STRIPE PAYMENT (FUTURE)

When Stripe integration is complete:

**URL:** POST `http://localhost:8001/api/v1x/digital-products/{id}/purchase`
**Headers:** `Authorization: Bearer {TOKEN}`
**Body:**
```json
{
  "payment_method": "stripe",
  "stripe_token": "tok_visa"
}
```

**Expected:** Payment processing, webhook callback, purchase completion

---

## EXECUTION CHECKLIST

### Before Testing
- [ ] Backend running on 8001
- [ ] Frontend running on 3001
- [ ] Database initialized
- [ ] Demo user logged in
- [ ] User has coin balance

### Backend Tests (15 minutes)
- [ ] Create seller account
- [ ] Create product
- [ ] Upload thumbnail
- [ ] Upload content
- [ ] Update product
- [ ] List products
- [ ] Delete product
- [ ] Get analytics
- [ ] Purchase product
- [ ] List orders
- [ ] Get order details
- [ ] Mark delivered
- [ ] Check purchase

### Frontend Tests (15 minutes)
- [ ] Dashboard loads
- [ ] Create product form works
- [ ] File uploads work
- [ ] Products list displays
- [ ] Orders list displays
- [ ] Analytics loads
- [ ] Dark mode works
- [ ] Mobile responsive
- [ ] Validation works

### Integration Tests (10 minutes)
- [ ] Coin purchase flow end-to-end
- [ ] Order appears in seller orders
- [ ] Analytics updates
- [ ] Seller can mark delivered
- [ ] Customer can see purchase

**Total Time:** ~40 minutes

---

## EXPECTED RESULTS

### Successful Test
✅ All 40+ API endpoints respond correctly
✅ All 5 frontend pages load without errors
✅ File uploads work and files are saved
✅ Coin purchases process successfully
✅ Orders appear and can be managed
✅ Analytics compute and display correctly
✅ Form validation works
✅ Error messages display
✅ Dark mode works
✅ Mobile responsive

### Known Limitations
- Stripe payment not fully integrated (placeholder only)
- File storage is local (should be S3 in production)
- No email notifications (infrastructure needed)
- No file antivirus scanning (add in production)

---

## NEXT STEPS AFTER TESTING

If all tests pass:
1. ✅ Production deployment ready
2. Deploy to staging environment
3. Run performance tests
4. Complete Stripe integration
5. Add S3 file storage
6. Set up monitoring & alerts
7. Train support team

If issues found:
1. Document bug with test case
2. Fix in code
3. Re-run affected tests
4. Verify fix works

---

## SUPPORT

**Backend Issues:**
- Check logs: `backend/app/main.py` output
- Check database: `backend/app/data/skillforge.db`
- Check API: Postman collection available

**Frontend Issues:**
- Check console: Browser DevTools
- Check build: `.next` directory exists
- Check styles: Tailwind CSS loaded

**Database Issues:**
- Reset: Delete `skillforge.db`, restart backend
- Check tables: `sqlite3 backend/app/data/skillforge.db ".tables"`

---

**Ready to test? Start with TEST SCENARIO 1 above!**
