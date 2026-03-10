# 🎯 Marketplace URLs Quick Card

## ✅ FIXES APPLIED

| Issue | Fix | File | Status |
|-------|-----|------|--------|
| Product edit not working | Added useEffect to load product data + fixed redirect | `src/pages/marketplace/seller/create-product.tsx` | ✅ |
| Admin dashboard crash | Added null safety operators | `src/pages/admin/marketplace.tsx` | ✅ |

---

## 🌐 FRONTEND URLS

### Customer
- `http://localhost:3000/marketplace` - Browse products
- `http://localhost:3000/marketplace/cart` - Shopping cart
- `http://localhost:3000/marketplace/checkout` - Checkout
- `http://localhost:3000/marketplace/orders` - Order history

### Seller (role: MENTOR or seller)
- `http://localhost:3000/marketplace/seller` - Dashboard
- `http://localhost:3000/marketplace/seller/create-product` - Create product
- **`http://localhost:3000/marketplace/seller/create-product?productId=7`** - **Edit product ✅**
- `http://localhost:3000/marketplace/seller/products` - My products
- `http://localhost:3000/marketplace/seller/orders` - Customer orders
- `http://localhost:3000/marketplace/seller/analytics` - Analytics

### Admin (role: ADMIN or SUPERADMIN)
- `http://localhost:3000/admin/marketplace` - Admin dashboard

---

## 🔌 API ENDPOINTS

### Seller Products
```
POST   /api/v1x/marketplace/seller/products              Create
GET    /api/v1x/marketplace/seller/products              List
GET    /api/v1x/marketplace/seller/products/{id}         Get one
PUT    /api/v1x/marketplace/seller/products/{id}         Update ✅
DELETE /api/v1x/marketplace/seller/products/{id}         Delete
POST   /api/v1x/marketplace/seller/products/{id}/upload-thumbnail
POST   /api/v1x/marketplace/seller/products/{id}/upload-content
POST   /api/v1x/marketplace/seller/products/{id}/upload-preview
```

### Customer Browse
```
GET    /api/v1x/marketplace/digital-products            All products
GET    /api/v1x/marketplace/digital-products/{id}       Single product
GET    /api/v1x/marketplace/search                       Search
GET    /api/v1x/marketplace/trending                     Trending
```

### Shopping
```
GET    /api/v1x/marketplace/cart                        Get cart
POST   /api/v1x/marketplace/cart/add                     Add item
DELETE /api/v1x/marketplace/cart/{item_id}              Remove item
POST   /api/v1x/marketplace/checkout                     Checkout
GET    /api/v1x/marketplace/orders                       My orders
```

### Admin
```
GET    /api/v1x/marketplace/admin/marketplace/dashboard  Dashboard stats
GET    /api/v1x/marketplace/admin/marketplace/products   All products
GET    /api/v1x/marketplace/admin/marketplace/sellers    All sellers
PUT    /api/v1x/marketplace/admin/marketplace/products/{id}/approve    Approve
PUT    /api/v1x/marketplace/admin/marketplace/products/{id}/suspend    Suspend
PUT    /api/v1x/marketplace/admin/marketplace/sellers/{id}/verify      Verify
```

---

## 👤 TEST ACCOUNTS

| Type | Email | Password |
|------|-------|----------|
| Seller | `mentor.sarah@skillforge.com` | `test123` |
| Admin | `admin@skillforge.com` | `test123` |

**Seller Sarah has**: 2 products (Python Cheat Sheet $9.99, Advanced Python $99.99)

---

## 📋 PRODUCT FIELDS

When creating/updating products, use these fields:
```json
{
  "name": "Product Name",
  "description": "Product description",
  "product_type": "course|template|bundle|resource|tool|consultation",
  "category": "programming|design|business|marketing|education|health|other",
  "price": 29.99,
  "original_price": 39.99,
  "tags": ["tag1", "tag2"],
  "requirements": ["requirement1"],
  "features": ["feature1", "feature2"],
  "thumbnail_url": "http://...",
  "content_url": "http://...",
  "preview_url": "http://..."
}
```

---

## 🧪 QUICK TEST

### Test Product Edit
```
1. Login: mentor.sarah@skillforge.com / test123
2. Visit: http://localhost:3000/marketplace/seller/create-product?productId=1
3. Form loads with data ✅
4. Change price to 14.99
5. Click Save
6. Sent: PUT /api/v1x/marketplace/seller/products/1
7. Redirect to /marketplace/seller/products ✅
```

### Test Admin Dashboard
```
1. Login: admin@skillforge.com / test123
2. Visit: http://localhost:3000/admin/marketplace
3. Dashboard tab shows metrics (no errors) ✅
4. Products tab lists all 7+ products ✅
5. Sellers tab lists all sellers ✅
```

---

## 📊 DATABASE

**Products table**: `digital_products`
- 31 columns including: id, seller_id, name, price, status, category, tags, features, etc.
- Demo data: 7+ products from different sellers

**Sellers table**: `seller_accounts`
- id, user_id, is_verified, is_active, seller_tier, store_name, total_revenue, average_rating

---

## 🔄 WORKFLOWS

### Create Flow
1. Click "Create Product"
2. Fill form → POST `/seller/products`
3. Get back product ID
4. Redirect to `?productId=ID`
5. Can now upload files

### Edit Flow ✅
1. Click "Edit" on product OR use `?productId=7`
2. Form auto-loads with data
3. Modify fields
4. Save → PUT `/seller/products/7`
5. Redirect to products list

### Admin Approval
1. Admin views `/admin/marketplace`
2. Click "Products" tab
3. See all products
4. Click "Approve" → PUT `/admin/marketplace/products/7/approve`
5. Or "Suspend" → PUT `/admin/marketplace/products/7/suspend`

---

## ⚡ KEY CHANGES MADE

### File: `src/pages/marketplace/seller/create-product.tsx`

**Added useEffect** (lines 51-109):
```typescript
useEffect(() => {
  if (!router.query.productId) return;
  // Fetch product data from API
  // Populate form with existing data
}, [router.query.productId]);
```

**Fixed redirect** (line 175):
- Before: `edit-product?productId=7` ❌
- After: `create-product?productId=7` ✅

### File: `src/pages/admin/marketplace.tsx`

**Added null safety** (lines 202, 210, 215, 220, 225, 229, 244, 249, 253):
```typescript
// Before: stats.products.total
// After:  (stats.products?.total ?? 0)
```

---

## ✅ STATUS

- [x] Create product - WORKING
- [x] Edit product - **NOW FIXED** ✅
- [x] Delete product - WORKING
- [x] Upload files - WORKING
- [x] View products - WORKING
- [x] Admin dashboard - **NOW FIXED** ✅
- [x] All API endpoints - WORKING
- [x] Database - CORRECT

**Overall**: 🟢 **ALL SYSTEMS GO**

---

**Last Updated**: January 28, 2026  
**Backend**: Running on port 8001 ✅  
**Frontend**: Running on port 3000 ✅  
**Database**: SQLite at `backend/app/data/skillforge.db` ✅
