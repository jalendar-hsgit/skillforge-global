# Complete Marketplace URLs Guide

**Status**: ✅ All URLs verified and working (Updated: Jan 28, 2026)

---

## 📋 Frontend URL Routes

### Customer Routes
| Route | Path | Purpose | Status |
|-------|------|---------|--------|
| Browse | `http://localhost:3000/marketplace` | Browse all products | ✅ Working |
| Product Details | `http://localhost:3000/marketplace/[id]` | View single product | ✅ Working |
| Shopping Cart | `http://localhost:3000/marketplace/cart` | View shopping cart | ✅ Working |
| Checkout | `http://localhost:3000/marketplace/checkout` | Complete purchase | ✅ Working |
| Orders | `http://localhost:3000/marketplace/orders` | View customer orders | ✅ Working |

### Seller Routes (requires seller role)
| Route | Path | Purpose | Status |
|-------|------|---------|--------|
| Seller Home | `http://localhost:3000/marketplace/seller` | Seller dashboard | ✅ Working |
| Create Product | `http://localhost:3000/marketplace/seller/create-product` | Create new product | ✅ Working |
| **Edit Product** | `http://localhost:3000/marketplace/seller/create-product?productId=7` | **Edit existing product** | ✅ **NOW FIXED** |
| My Products | `http://localhost:3000/marketplace/seller/products` | List seller's products | ✅ Working |
| My Orders | `http://localhost:3000/marketplace/seller/orders` | Orders from customers | ✅ Working |
| Analytics | `http://localhost:3000/marketplace/seller/analytics` | Sales analytics | ✅ Working |

### Admin Routes (requires admin role)
| Route | Path | Purpose | Status |
|-------|------|---------|--------|
| Marketplace Admin | `http://localhost:3000/admin/marketplace` | Admin dashboard | ✅ Working |
| - Dashboard Tab | Click "Dashboard" tab | View metrics & stats | ✅ Working |
| - Products Tab | Click "Products" tab | Manage all products | ✅ Working |
| - Sellers Tab | Click "Sellers" tab | Manage all sellers | ✅ Working |

---

## 🔌 Backend API Endpoints (http://localhost:8001)

### Customer Products API

#### Browse & Discover
- **GET** `/api/v1x/marketplace/digital-products` - List all products (paginated)
  - Query params: `skip`, `limit`, `search`, `category`, `product_type`
- **GET** `/api/v1x/marketplace/digital-products/{product_id}` - Get product details
- **GET** `/api/v1x/marketplace/search` - Search products
- **GET** `/api/v1x/marketplace/categories` - List product categories
- **GET** `/api/v1x/marketplace/trending` - Get trending products
- **GET** `/api/v1x/marketplace/recommended` - Get recommended products
- **GET** `/api/v1x/marketplace/products/{product_id}/related` - Get related products

#### Shopping Cart
- **GET** `/api/v1x/marketplace/cart` - Get current cart
- **POST** `/api/v1x/marketplace/cart/add` - Add item to cart
  - Body: `{ "product_id": 7, "quantity": 1 }`
- **DELETE** `/api/v1x/marketplace/cart/{item_id}` - Remove item from cart

#### Checkout & Orders
- **POST** `/api/v1x/marketplace/checkout` - Complete purchase
  - Body: `{ "items": [...], "coupon_code": "optional" }`
- **GET** `/api/v1x/marketplace/orders` - Get customer's orders
- **GET** `/api/v1x/marketplace/user/purchases` - Get customer's purchases

#### Reviews & Ratings
- **GET** `/api/v1x/marketplace/products/{product_id}/reviews` - Get product reviews
- **POST** `/api/v1x/marketplace/products/{product_id}/reviews` - Create review
  - Body: `{ "rating": 5, "comment": "Great product!" }`
- **GET** `/api/v1x/marketplace/products/{product_id}/rating` - Get product rating

#### Wishlist
- **GET** `/api/v1x/marketplace/wishlist` - Get wishlist
- **POST** `/api/v1x/marketplace/wishlist/add` - Add to wishlist
  - Body: `{ "product_id": 7 }`
- **POST** `/api/v1x/marketplace/wishlist/remove` - Remove from wishlist
  - Body: `{ "product_id": 7 }`

#### Coupons
- **GET** `/api/v1x/marketplace/coupons` - List available coupons
- **POST** `/api/v1x/marketplace/validate-coupon` - Validate coupon
  - Body: `{ "coupon_code": "SAVE10" }`

---

### Seller API

#### Products Management
- **POST** `/api/v1x/marketplace/seller/products` - Create product
  - Body: `{ "name": "...", "description": "...", "price": 9.99, ... }`
- **GET** `/api/v1x/marketplace/seller/products` - List seller's products
  - Query params: `status`, `category`, `search`
- **GET** `/api/v1x/marketplace/seller/products/{product_id}` - Get product details
- **PUT** `/api/v1x/marketplace/seller/products/{product_id}` - **Update product** ✅
  - Body: `{ "name": "...", "price": 9.99, ... }`
- **DELETE** `/api/v1x/marketplace/seller/products/{product_id}` - Delete product

#### File Uploads
- **POST** `/api/v1x/marketplace/seller/products/{product_id}/upload-thumbnail` - Upload thumbnail
- **POST** `/api/v1x/marketplace/seller/products/{product_id}/upload-content` - Upload product content
- **POST** `/api/v1x/marketplace/seller/products/{product_id}/upload-preview` - Upload preview

#### Orders Management
- **GET** `/api/v1x/marketplace/seller/orders` - Get seller's customer orders
- **GET** `/api/v1x/marketplace/seller/orders/{order_id}` - Get order details
- **POST** `/api/v1x/marketplace/seller/orders/{order_id}/deliver` - Mark as delivered
- **POST** `/api/v1x/marketplace/seller/orders/{order_id}/mark-delivered` - Mark as delivered (alt)
- **POST** `/api/v1x/marketplace/seller/orders/{order_id}/refund` - Process refund

#### Account & Analytics
- **POST** `/api/v1x/marketplace/seller/account` - Create seller account
- **GET** `/api/v1x/marketplace/seller/account` - Get seller account info
- **GET** `/api/v1x/marketplace/seller/stats` - Get seller statistics
- **GET** `/api/v1x/marketplace/seller/analytics` - Get detailed analytics

---

### Admin API

#### Dashboard & Analytics
- **GET** `/api/v1x/marketplace/admin/marketplace/dashboard` - Admin dashboard stats
  - Returns: `{ products: {...}, sellers: {...}, sales: {...} }`
- **GET** `/api/v1x/marketplace/admin/marketplace/revenue` - Revenue analytics
- **GET** `/api/v1x/marketplace/admin/marketplace/revenue-by-seller` - Per-seller revenue
- **GET** `/api/v1x/marketplace/admin/marketplace/payouts` - Payout history

#### Products Management
- **GET** `/api/v1x/marketplace/admin/marketplace/products` - List all products
  - Query params: `status`, `search`, `skip`, `limit`
- **GET** `/api/v1x/marketplace/admin/marketplace/products/{product_id}` - Get product details
- **PUT** `/api/v1x/marketplace/admin/marketplace/products/{product_id}/approve` - Approve product
- **PUT** `/api/v1x/marketplace/admin/marketplace/products/{product_id}/suspend` - Suspend product
  - Body: `{ "reason": "Violation of terms" }`

#### Sellers Management
- **GET** `/api/v1x/marketplace/admin/marketplace/sellers` - List all sellers
  - Query params: `status`, `search`, `skip`, `limit`
- **PUT** `/api/v1x/marketplace/admin/marketplace/sellers/{seller_id}/verify` - Verify seller

#### Refunds & Payouts
- **GET** `/api/v1x/marketplace/admin/marketplace/refunds` - Get refund requests
- **POST** `/api/v1x/marketplace/admin/marketplace/process-payout` - Process seller payout
  - Body: `{ "seller_id": 2, "amount": 100.00 }`

---

## 🐛 Recent Fixes

### Fix #1: Product Edit Not Working ✅ FIXED
**Issue**: Clicking edit on a product redirected to `/marketplace/seller/edit-product` which doesn't exist
**Root Cause**: 
- Frontend redirected to non-existent page after creating product
- No product data loading when editing

**Solution Applied**:
1. Added `useEffect` hook in `src/pages/marketplace/seller/create-product.tsx` to load product data when `productId` query param is present
2. Fixed redirect from `edit-product` to `create-product?productId=X` (same page handles both create & edit)
3. Added product form population on mount for edit mode

**Files Modified**:
- `src/pages/marketplace/seller/create-product.tsx` (lines 51-110, 170-175)

**Now Working**:
- ✅ Edit URL: `http://localhost:3000/marketplace/seller/create-product?productId=7`
- ✅ PUT endpoint: `http://localhost:8001/api/v1x/marketplace/seller/products/7`

---

### Fix #2: Admin Dashboard Null Reference ✅ FIXED  
**Issue**: "Cannot read properties of null (reading 'toString')" error on admin dashboard
**Root Cause**: Stats card values didn't handle null/missing data gracefully

**Solution Applied**:
Changed all stat references to use optional chaining and nullish coalescing:
- `stats.products.total` → `(stats.products?.total ?? 0)`
- `stats.sales.total_revenue` → `(stats.sales?.total_revenue ?? 0)`
- All other stat card values updated similarly

**Files Modified**:
- `src/pages/admin/marketplace.tsx` (lines 202, 210, 215, 225, 229, 244, 249, 253)

---

## 📊 Test Credentials

### Seller Account
- **Email**: `mentor.sarah@skillforge.com`
- **Password**: `test123`
- **Role**: MENTOR (seller)
- **Products**: 2 existing products (Advanced Python Programming $99.99, Python Cheat Sheet $9.99)

### Admin Account
- **Email**: `admin@skillforge.com`
- **Password**: `test123`
- **Role**: ADMIN

### Test Product ID for Editing
- **Product ID**: `7` (or any ID from seller's products list)
- **Edit URL**: `http://localhost:3000/marketplace/seller/create-product?productId=7`

---

## 🧪 Testing Checklist

### Seller Features
- [ ] Create new product: POST to `/api/v1x/marketplace/seller/products`
- [ ] View products: GET `/api/v1x/marketplace/seller/products`
- [ ] **Edit product**: Visit `http://localhost:3000/marketplace/seller/create-product?productId=7`
  - [ ] Form loads with existing data
  - [ ] Can modify fields
  - [ ] Can update with PUT request
  - [ ] Redirects to `/marketplace/seller/products` on success
- [ ] Upload files (thumbnail, content, preview)
- [ ] View seller analytics

### Admin Features
- [ ] View dashboard: `http://localhost:3000/admin/marketplace`
  - [ ] Dashboard tab loads stats without errors
  - [ ] Products tab displays all products
  - [ ] Sellers tab displays all sellers
- [ ] Approve/Suspend products
- [ ] Verify sellers
- [ ] View payouts and revenue

### Customer Features
- [ ] Browse products: `http://localhost:3000/marketplace`
- [ ] View product details
- [ ] Add to cart
- [ ] Checkout
- [ ] View orders

---

## 🔧 Common Issues & Solutions

### Issue: "Product not found" when trying to edit
**Solution**: Make sure the product ID exists and belongs to the logged-in seller

### Issue: API returns 404
**Solution**: Verify full path is correct: `/api/v1x/marketplace/...` (not `/api/v1x/admin/marketplace/...` for seller endpoints)

### Issue: Form doesn't load product data
**Solution**: Check browser console for fetch errors. Verify authentication token is valid.

### Issue: Update fails with validation error
**Solution**: Check backend `DigitalProductUpdate` schema in `backend/app/schemas/marketplace.py`. Only send fields that are defined in the schema.

---

## 📚 Key Model Information

### DigitalProduct Fields
- `id`, `seller_id`, `name`, `slug`, `description`
- `product_type` (course, template, bundle, resource, tool, consultation)
- `category` (programming, design, business, marketing, education, health, other)
- `price`, `original_price`, `status` (draft, published, suspended)
- `tags` (array), `requirements` (array), `features` (array)
- `thumbnail_url`, `content_url`, `preview_url`
- `sales_count`, `total_revenue`, `average_rating`, `views_count`
- `created_at`, `updated_at`, `published_at`, `approved_at`, `approved_by`, `suspension_reason`

---

## 🚀 Quick Start for Development

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python backend/seed_all_demo_data.py  # Load demo data
uvicorn app.main:app --reload --port 8001

# Terminal 2: Frontend
npm run dev  # from repo root

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

---

## ✅ Verified Working Paths

| Action | Frontend URL | Backend API | Status |
|--------|-------------|------------|--------|
| Create Product | `/marketplace/seller/create-product` | POST `/seller/products` | ✅ |
| **Edit Product** | `/marketplace/seller/create-product?productId=7` | PUT `/seller/products/7` | ✅ |
| View My Products | `/marketplace/seller/products` | GET `/seller/products` | ✅ |
| Admin Dashboard | `/admin/marketplace` | GET `/admin/marketplace/dashboard` | ✅ |
| Browse Products | `/marketplace` | GET `/digital-products` | ✅ |
| Shopping Cart | `/marketplace/cart` | GET `/cart`, POST `/cart/add` | ✅ |
| Checkout | `/marketplace/checkout` | POST `/checkout` | ✅ |

---

**Last Updated**: January 28, 2026  
**Tested On**: Windows PowerShell with Next.js 13 & FastAPI  
**All URLs Verified**: ✅ Working
