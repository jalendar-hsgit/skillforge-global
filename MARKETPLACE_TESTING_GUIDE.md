# 🛒 Marketplace & Purchase Order - Complete Testing Guide

**Date:** January 11, 2026  
**Status:** ✅ ALL ENDPOINTS CONNECTED  
**Flow:** Browse → Cart → Coupon → Checkout → Orders

---

## 📋 TABLE OF CONTENTS
1. [Quick Access URLs](#quick-access-urls)
2. [Complete Endpoint List](#complete-endpoint-list)
3. [Purchase Flow Diagram](#purchase-flow-diagram)
4. [Testing Scenarios](#testing-scenarios)
5. [URL Mapping & Redirects](#url-mapping--redirects)
6. [Seller Features](#seller-features)

---

## 🚀 QUICK ACCESS URLs

### Frontend Pages
| Page | URL | Auth | Description |
|------|-----|------|-------------|
| Browse Courses | `http://localhost:3000/marketplace` | Optional | Course catalog |
| Shopping Cart | `http://localhost:3000/marketplace/cart` | Required | Cart management |
| Order History | `http://localhost:3000/marketplace/orders` | Required | Past purchases |

### Backend Base URLs
- **Backend API:** `http://localhost:8001`
- **Frontend Dev:** `http://localhost:3000`
- **Session Proxy:** `/api/session/v1x/marketplace/*`

---

## 🔗 COMPLETE ENDPOINT LIST

### 1️⃣ COURSE BROWSING

#### GET - Browse All Courses
```
Frontend:  http://localhost:3000/marketplace
API:       /api/session/v1x/marketplace/courses
Backend:   /api/v1x/marketplace/courses
Method:    GET
Auth:      Optional
```

**Query Parameters:**
- `?category=web-dev` - Filter by category
- `?difficulty=beginner` - beginner/intermediate/advanced
- `?search=python` - Search in title/description
- `?is_paid=true` - Filter paid/free courses

**Response:**
```json
[
  {
    "id": 1,
    "title": "Python Fundamentals",
    "path": "python-fundamentals",
    "price": 49.99,
    "difficulty": "beginner",
    "category": "programming",
    "instructor_name": "John Doe",
    "enrollment_count": 150,
    "average_rating": 4.5,
    "in_cart": false,
    "purchased": false
  }
]
```

**Test Command:**
```bash
curl http://localhost:3000/api/session/v1x/marketplace/courses
```

---

### 2️⃣ SHOPPING CART

#### GET - View Cart
```
Frontend:  http://localhost:3000/marketplace/cart
API:       /api/session/v1x/marketplace/cart
Backend:   /api/v1x/marketplace/cart
Method:    GET
Auth:      Required ✓
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "course_id": 5,
      "course_title": "React Masterclass",
      "course_path": "react-masterclass",
      "price": 149.99,
      "added_at": "2026-01-11T10:30:00Z"
    }
  ],
  "subtotal": 149.99,
  "discount": 0,
  "tax": 0,
  "total": 149.99,
  "coupon_code": null
}
```

**Test Command:**
```bash
curl http://localhost:3000/api/session/v1x/marketplace/cart \
  -b cookies.txt
```

#### POST - Add to Cart
```
Frontend:  Marketplace page (Add to Cart button)
API:       /api/session/v1x/marketplace/cart/add
Backend:   /api/v1x/marketplace/cart/add
Method:    POST
Auth:      Required ✓
```

**Request:**
```json
{
  "course_id": 5
}
```

**Response:**
```json
{
  "id": 1,
  "course_id": 5,
  "course_title": "React Masterclass",
  "price": 149.99,
  "message": "Added to cart"
}
```

**Error Responses:**
- `400` - "Item already in cart"
- `400` - "Course already purchased"
- `400` - "course_id required"
- `404` - "Course not found"

**Test Command:**
```bash
curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":1}' \
  -b cookies.txt
```

#### DELETE - Remove from Cart
```
Frontend:  Cart page (Remove button)
API:       /api/session/v1x/marketplace/cart/{item_id}
Backend:   /api/v1x/marketplace/cart/{item_id}
Method:    DELETE
Auth:      Required ✓
```

**Response:**
```json
{
  "message": "Item removed from cart",
  "id": 1
}
```

**Error Response:**
- `404` - "Cart item not found"

**Test Command:**
```bash
curl -X DELETE http://localhost:3000/api/session/v1x/marketplace/cart/1 \
  -b cookies.txt
```

---

### 3️⃣ COUPON VALIDATION

#### POST - Validate Coupon
```
Frontend:  Cart page (Apply Coupon button)
API:       /api/session/v1x/marketplace/coupons/validate
Backend:   /api/v1x/marketplace/coupons/validate
Method:    POST
Auth:      Required ✓
```

**Request:**
```json
{
  "coupon_code": "SAVE20"
}
```

**Response:**
```json
{
  "code": "SAVE20",
  "discount_type": "percentage",
  "discount_value": 20.0,
  "max_discount": 50.0,
  "valid": true
}
```

**Error Responses:**
- `404` - "Invalid coupon code"
- `400` - "Coupon expired"
- `400` - "Coupon not yet valid"
- `400` - "Coupon usage limit reached"

**Test Command:**
```bash
curl -X POST http://localhost:3000/api/session/v1x/marketplace/coupons/validate \
  -H "Content-Type: application/json" \
  -d '{"coupon_code":"SAVE20"}' \
  -b cookies.txt
```

---

### 4️⃣ CHECKOUT

#### POST - Process Checkout
```
Frontend:  Cart page (Checkout button)
API:       /api/session/v1x/marketplace/checkout
Backend:   /api/v1x/marketplace/checkout
Method:    POST
Auth:      Required ✓
Redirect:  → /marketplace/orders (on success)
```

**Request:**
```json
{
  "payment_method": "coins",
  "coupon_code": "SAVE20"
}
```

**Response:**
```json
{
  "order_id": 123,
  "order_number": "ORD-20260111-A1B2C3D4",
  "status": "completed",
  "amount": 119.99,
  "message": "Order created successfully"
}
```

**Backend Process:**
1. ✅ Validate cart has items
2. ✅ Calculate subtotal from cart items
3. ✅ Validate coupon (if provided)
4. ✅ Calculate discount
5. ✅ Check user coin balance
6. ✅ Create Order record
7. ✅ Deduct coins from balance (CoinLedger)
8. ✅ Clear cart items
9. ✅ Update coupon usage count
10. ✅ Return order details

**Error Responses:**
- `400` - "Cart is empty"
- `400` - "Insufficient coins. Balance: X, Required: Y"
- `400` - "Coupon expired"

**Test Command:**
```bash
curl -X POST http://localhost:3000/api/session/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -d '{"payment_method":"coins","coupon_code":"SAVE20"}' \
  -b cookies.txt
```

---

### 5️⃣ ORDER HISTORY

#### GET - My Orders
```
Frontend:  http://localhost:3000/marketplace/orders
API:       /api/session/v1x/marketplace/orders
Backend:   /api/v1x/marketplace/orders
Method:    GET
Auth:      Required ✓
```

**Response:**
```json
[
  {
    "id": 123,
    "order_number": "ORD-20260111-A1B2C3D4",
    "status": "completed",
    "subtotal": 149.99,
    "discount_amount": 30.00,
    "tax_amount": 0.00,
    "amount": 119.99,
    "currency": "USD",
    "payment_method": "coins",
    "payment_status": "completed",
    "created_at": "2026-01-11T10:45:00Z",
    "course_title": "React Masterclass"
  }
]
```

**Test Command:**
```bash
curl http://localhost:3000/api/session/v1x/marketplace/orders \
  -b cookies.txt
```

---

## 🎯 PURCHASE FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPLETE PURCHASE FLOW                       │
└─────────────────────────────────────────────────────────────────┘

1. BROWSE COURSES
   URL: /marketplace
   API: GET /api/session/v1x/marketplace/courses
   │
   ├─→ [Add to Cart] (requires login)
   │
   ↓

2. ADD TO CART
   API: POST /api/session/v1x/marketplace/cart/add
   Body: { course_id: 5 }
   │
   ├─→ Success: Cart count +1
   ├─→ Error: "Already in cart" / "Already purchased"
   │
   ↓

3. VIEW CART
   URL: /marketplace/cart
   API: GET /api/session/v1x/marketplace/cart
   │
   ├─→ Remove item: DELETE /cart/{id}
   ├─→ Apply coupon: POST /coupons/validate
   │
   ↓

4. VALIDATE COUPON (Optional)
   API: POST /api/session/v1x/marketplace/coupons/validate
   Body: { coupon_code: "SAVE20" }
   │
   ├─→ Valid: Show discount message
   ├─→ Invalid: Show error message
   │
   ↓

5. CHECKOUT
   API: POST /api/session/v1x/marketplace/checkout
   Body: { payment_method: "coins", coupon_code: "SAVE20" }
   │
   Backend Actions:
   ├─→ Calculate total with discount
   ├─→ Check coin balance
   ├─→ Create Order record
   ├─→ Deduct coins (CoinLedger)
   ├─→ Clear cart (DELETE all CartItems)
   ├─→ Update coupon usage
   │
   ↓

6. ORDER COMPLETE
   Redirect: /marketplace/orders
   API: GET /api/session/v1x/marketplace/orders
   │
   Display: Order history with status badges
```

---

## 🧪 TESTING SCENARIOS

### ✅ Test Case 1: Complete Happy Path

```bash
# Step 1: Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"password123"}' \
  -c cookies.txt

# Step 2: Browse courses
curl http://localhost:3000/api/session/v1x/marketplace/courses \
  -b cookies.txt

# Step 3: Add to cart
curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":1}' \
  -b cookies.txt

# Step 4: View cart
curl http://localhost:3000/api/session/v1x/marketplace/cart \
  -b cookies.txt

# Step 5: Validate coupon
curl -X POST http://localhost:3000/api/session/v1x/marketplace/coupons/validate \
  -H "Content-Type: application/json" \
  -d '{"coupon_code":"SAVE20"}' \
  -b cookies.txt

# Step 6: Checkout
curl -X POST http://localhost:3000/api/session/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -d '{"payment_method":"coins","coupon_code":"SAVE20"}' \
  -b cookies.txt

# Step 7: View orders
curl http://localhost:3000/api/session/v1x/marketplace/orders \
  -b cookies.txt
```

**Expected Results:**
- ✅ Cart count updates after add
- ✅ Coupon validates successfully  
- ✅ Checkout completes
- ✅ Cart is empty after checkout
- ✅ Order appears in history
- ✅ Coins deducted from balance

---

### ❌ Test Case 2: Error Scenarios

#### Test: Add Already Purchased Course
```bash
# Purchase course first (complete checkout)
# Then try to add same course again
curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":1}' \
  -b cookies.txt

# Expected: 400 "Course already purchased"
```

#### Test: Add Duplicate to Cart
```bash
# Add once
curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":2}' \
  -b cookies.txt

# Add same course again
curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":2}' \
  -b cookies.txt

# Expected: 400 "Item already in cart"
```

#### Test: Checkout with Insufficient Coins
```bash
# Add expensive course to cart
# Try checkout without enough coins
curl -X POST http://localhost:3000/api/session/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -d '{"payment_method":"coins"}' \
  -b cookies.txt

# Expected: 400 "Insufficient coins. Balance: X, Required: Y"
```

#### Test: Invalid Coupon
```bash
curl -X POST http://localhost:3000/api/session/v1x/marketplace/coupons/validate \
  -H "Content-Type: application/json" \
  -d '{"coupon_code":"INVALID123"}' \
  -b cookies.txt

# Expected: 404 "Invalid coupon code"
```

#### Test: Empty Cart Checkout
```bash
# Make sure cart is empty
# Try to checkout
curl -X POST http://localhost:3000/api/session/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -d '{"payment_method":"coins"}' \
  -b cookies.txt

# Expected: 400 "Cart is empty"
```

---

### 🔄 Test Case 3: Cart Management

#### Add Multiple Items
```bash
# Add 3 courses
curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":1}' \
  -b cookies.txt

curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":3}' \
  -b cookies.txt

curl -X POST http://localhost:3000/api/session/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -d '{"course_id":5}' \
  -b cookies.txt

# Verify cart has 3 items
curl http://localhost:3000/api/session/v1x/marketplace/cart \
  -b cookies.txt
```

#### Remove Specific Item
```bash
# Get cart to find item IDs
curl http://localhost:3000/api/session/v1x/marketplace/cart \
  -b cookies.txt

# Remove item by ID
curl -X DELETE http://localhost:3000/api/session/v1x/marketplace/cart/1 \
  -b cookies.txt

# Verify removal
curl http://localhost:3000/api/session/v1x/marketplace/cart \
  -b cookies.txt
```

---

## 🗺️ URL MAPPING & REDIRECTS

### Frontend to Backend Flow

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   FRONTEND       │ ───→ │  NEXT.JS PROXY   │ ───→ │    BACKEND       │
│   (Browser)      │      │  (API Route)     │      │    (FastAPI)     │
└──────────────────┘      └──────────────────┘      └──────────────────┘
         │                         │                         │
    /marketplace              /api/session           /api/v1x
                                   │                         │
                          Adds cookies                Validates JWT
                          Forwards req              Returns response
```

### Complete URL Mapping

| Frontend Page | Next.js API Proxy | Backend Endpoint | Purpose |
|---------------|-------------------|------------------|---------|
| `/marketplace` | `/api/session/v1x/marketplace/courses` | `/api/v1x/marketplace/courses` | Browse courses |
| `/marketplace/cart` | `/api/session/v1x/marketplace/cart` | `/api/v1x/marketplace/cart` | View cart |
| - | `/api/session/v1x/marketplace/cart/add` | `/api/v1x/marketplace/cart/add` | Add to cart |
| - | `/api/session/v1x/marketplace/cart/{id}` | `/api/v1x/marketplace/cart/{id}` | Remove item |
| - | `/api/session/v1x/marketplace/coupons/validate` | `/api/v1x/marketplace/coupons/validate` | Validate coupon |
| - | `/api/session/v1x/marketplace/checkout` | `/api/v1x/marketplace/checkout` | Process order |
| `/marketplace/orders` | `/api/session/v1x/marketplace/orders` | `/api/v1x/marketplace/orders` | Order history |

### Authentication Redirects

| Condition | Source Page | Redirect To |
|-----------|-------------|-------------|
| Not logged in | Any marketplace action | `/login?redirect=/marketplace` |
| Not logged in | View cart | `/login?redirect=/marketplace/cart` |
| Not logged in | View orders | `/login?redirect=/marketplace/orders` |
| Successful checkout | Cart page | `/marketplace/orders` |
| Add to cart (not logged in) | Marketplace | Prompt → `/login?redirect=/marketplace` |

### Next.js API Proxy Structure

```
src/pages/api/session/v1x/marketplace/
├── cart.ts                    → GET /cart
├── cart/
│   ├── add.ts                 → POST /cart/add
│   └── [id].ts                → DELETE /cart/{id}
├── (coupons and checkout proxied via general proxy)
```

---

## 📊 DATABASE TABLES

### Tables Involved in Purchase Flow

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | User accounts | id, email, name, role |
| `courses` | Course catalog | id, title, price, path |
| `cart_items` | Shopping cart | id, user_id, course_id, price, added_at |
| `orders` | Purchase records | id, user_id, course_id, order_number, amount, status |
| `coupons` | Discount codes | code, discount_type, discount_value, is_active, usage_count |
| `coin_ledger` | Coin transactions | user_id, delta, reason |

### Data Flow Example

```sql
-- 1. User adds course to cart
INSERT INTO cart_items (user_id, course_id, price, added_at)
VALUES (1, 5, 149.99, NOW());

-- 2. On checkout:
-- a) Create order
INSERT INTO orders (user_id, course_id, order_number, amount, status, ...)
VALUES (1, 5, 'ORD-20260111-...', 119.99, 'completed', ...);

-- b) Deduct coins
INSERT INTO coin_ledger (user_id, delta, reason)
VALUES (1, -120, 'Course purchase: React Masterclass');

-- c) Clear cart
DELETE FROM cart_items WHERE user_id = 1;

-- d) Update coupon
UPDATE coupons SET usage_count = usage_count + 1 
WHERE code = 'SAVE20';
```

---

## 🎓 DEMO DATA

### Test Users (from seed data)
```
Email: john.doe@example.com
Password: password123

Email: jane.smith@example.com  
Password: password123
```

### Available Courses
1. **Python Fundamentals** - $49.99 (ID: 1)
2. **Web Development** - $99.99 (ID: 2)
3. **React Masterclass** - $149.99 (ID: 3)
4. **Machine Learning** - $199.99 (ID: 4)
5. **DevOps Bootcamp** - $129.99 (ID: 5)

### Create Test Coupons

```bash
# Login as admin
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@skillforge.com","password":"admin123"}' \
  -c admin-cookies.txt

# Create 20% off coupon
curl -X POST http://localhost:8001/api/v1x/admin/coupons \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE20",
    "discount_type": "percentage",
    "discount_value": 20,
    "max_discount_amount": 50,
    "is_active": true
  }' \
  -b admin-cookies.txt
```

---

## 🔍 BROWSER CONSOLE TESTING

### Quick Test in Browser DevTools

```javascript
// 1. Add to cart
fetch('/api/session/v1x/marketplace/cart/add', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ course_id: 1 })
}).then(r => r.json()).then(d => console.log('Add Result:', d));

// 2. View cart
fetch('/api/session/v1x/marketplace/cart', {
  credentials: 'include'
}).then(r => r.json()).then(d => console.log('Cart:', d));

// 3. Validate coupon
fetch('/api/session/v1x/marketplace/coupons/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ coupon_code: 'SAVE20' })
}).then(r => r.json()).then(d => console.log('Coupon:', d));

// 4. Checkout
fetch('/api/session/v1x/marketplace/checkout', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ 
    payment_method: 'coins',
    coupon_code: 'SAVE20'
  })
}).then(r => r.json()).then(d => console.log('Order:', d));

// 5. View orders
fetch('/api/session/v1x/marketplace/orders', {
  credentials: 'include'
}).then(r => r.json()).then(d => console.log('Orders:', d));
```

---

## ✅ TESTING CHECKLIST

### Basic Flow
- [ ] Browse courses without login ✓
- [ ] Add course to cart (login required) ✓
- [ ] Cart count updates after add ✓
- [ ] View cart with items ✓
- [ ] Remove item from cart ✓
- [ ] Apply valid coupon ✓
- [ ] Apply invalid coupon (shows error) ✓
- [ ] Checkout with sufficient coins ✓
- [ ] Cart clears after checkout ✓
- [ ] View order in history ✓

### Edge Cases  
- [ ] Add already purchased course → Error ✓
- [ ] Add duplicate to cart → Error ✓
- [ ] Checkout empty cart → Error ✓
- [ ] Checkout insufficient coins → Error ✓
- [ ] Apply expired coupon → Error ✓
- [ ] Remove non-existent item → Error ✓
- [ ] Unauthorized access → Redirect login ✓

### UI Behavior
- [ ] Cart icon shows correct count ✓
- [ ] Success message after add ✓
- [ ] Redirect to orders after checkout ✓
- [ ] Error messages display ✓
- [ ] Loading states work ✓
- [ ] Responsive design ✓

---

## 🐛 TROUBLESHOOTING

### Issue: Cart showing 0 items after adding
**Solution:** Fixed `added_at` field reference in GET cart endpoint.

### Issue: 404 on checkout
**Solution:** Added `/v1x/marketplace/checkout` endpoint to session.py router.

### Issue: 404 on orders page
**Solution:** Added `/v1x/marketplace/orders` endpoint to session.py router.

### Issue: Coupon not applying
**Solution:** Verify coupon is active, not expired, usage_count < usage_limit.

### Issue: Insufficient coins
**Check balance:**
```bash
curl http://localhost:8001/api/v1x/coins/balance -b cookies.txt
```

### Issue: Order not in history
**Check database:**
```bash
sqlite3 backend/app/data/skillforge.db
SELECT * FROM orders WHERE user_id = 1;
```

---

## 🎉 SUCCESS SUMMARY

**All Marketplace & Order Endpoints Connected:**
- ✅ Browse courses
- ✅ Add to cart  
- ✅ View cart
- ✅ Remove from cart
- ✅ Validate coupons
- ✅ Process checkout
- ✅ View order history

**Complete Flow Works End-to-End:**
1. Browse → Add to Cart → Cart Count +1
2. View Cart → Apply Coupon → See Discount
3. Checkout → Coins Deducted → Cart Cleared
4. Redirect to Orders → See Purchase History

**Ready for Production Testing!** 🚀

---

# 🏪 SELLER FEATURES
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
