# MARKETPLACE - SELLER & ADMIN FEATURES GUIDE

## Overview

Your product "Advanced Python Programming" has been created successfully! Here's a complete guide on how to view your products and access admin marketplace features.

---

## PART 1: SELLER SIDE - View Your Created Products

### How to Access (Browser)
1. Go to: `http://localhost:3000/marketplace/seller/products`
2. Login as: `mentor.sarah@skillforge.com / mentor123`

### What You'll See
- **All your created products**
- Product details: name, price, status, ratings, sales count
- Ability to edit, delete, or publish products
- Sales analytics and earnings

### API Endpoint
```
GET /api/v1x/marketplace/seller/products
Authentication: Cookie (login required)

Query Parameters:
  - status: Optional filter (e.g., "draft", "published")
  - category: Optional filter (e.g., "programming")
  - skip: Pagination offset (default: 0)
  - limit: Items per page (default: 20)

Response:
{
  "total": 2,
  "items": [
    {
      "id": 4,
      "name": "Advanced Python Programming",
      "price": 99.99,
      "status": "draft",
      "sales_count": 0,
      "average_rating": 0.0,
      "thumbnail_url": null,
      "created_at": "2026-01-27T16:35:17..."
    },
    ...
  ]
}
```

### Test with cURL
```bash
curl -X GET "http://localhost:8001/api/v1x/marketplace/seller/products" \
  -H "Cookie: token=YOUR_JWT_TOKEN"
```

---

## PART 2: ADMIN SIDE - Marketplace Management

### Admin Credentials
- Email: `admin@skillforge.com`
- Password: `admin123`

### Admin Features Available

#### 1. View All Products (For Approval)
**Browser**: `http://localhost:3000/admin/marketplace/products` (if UI exists)

**API Endpoint**:
```
GET /api/v1x/marketplace/admin/marketplace/products
Authentication: Admin login required

Query Parameters:
  - status: Filter by product status (draft, published, suspended)
  - seller_id: Filter by specific seller
  - skip: Pagination offset
  - limit: Items per page

Response:
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "name": "Python Cheat Sheet",
      "seller_id": 8,
      "price": 9.99,
      "status": "published",
      "approved_at": "2026-01-27T...",
      "approved_by": 2
    },
    ...
  ]
}
```

#### 2. View All Sellers
**API Endpoint**:
```
GET /api/v1x/marketplace/admin/marketplace/sellers
Authentication: Admin login required

Query Parameters:
  - status: Filter by verification (verified, unverified, active, inactive)
  - skip: Pagination offset
  - limit: Items per page

Response:
{
  "sellers": [
    {
      "seller_id": 1,
      "user_id": 8,
      "email": "mentor.sarah@skillforge.com",
      "store_name": "Sarah Chen's Store",
      "is_verified": true,
      "is_active": true,
      "seller_tier": "basic",
      "products_count": 2,
      "sales_count": 0,
      "total_revenue": 0.0,
      "created_at": "2026-01-27T..."
    },
    ...
  ],
  "total": 4
}
```

#### 3. Admin Marketplace Dashboard
**Purpose**: View marketplace metrics and KPIs

**API Endpoint**:
```
GET /api/v1x/marketplace/admin/marketplace/dashboard
Authentication: Admin login required

Response:
{
  "products": {
    "total": 5,
    "published": 3,
    "draft": 2,
    "suspended": 0
  },
  "sellers": {
    "total": 4,
    "verified": 4,
    "pending": 0
  },
  "sales": {
    "total_transactions": 0,
    "total_revenue": 0.0,
    "platform_fee": 0.0,
    "seller_earnings": 0.0
  }
}
```

**Metrics Explained**:
- **Products Total**: All products in system
- **Published**: Products available for purchase
- **Draft**: Products not yet published
- **Verified Sellers**: Sellers who've completed verification
- **Total Revenue**: All sales combined
- **Platform Fee**: 20% of revenue (admin keeps)
- **Seller Earnings**: 80% of revenue (sellers keep)

#### 4. Product Approval (Admin)
**API Endpoint** (Admin):
```
PUT /api/v1x/marketplace/admin/marketplace/products/{product_id}/approve
Authentication: Admin login required

Request Body:
{
  "approval_notes": "Product approved after review"
}

Response:
{
  "id": 4,
  "name": "Advanced Python Programming",
  "status": "published",
  "approved_at": "2026-01-27T16:50:00...",
  "approved_by": 2
}
```

#### 5. Suspend Product (Admin)
**API Endpoint** (Admin):
```
PUT /api/v1x/marketplace/admin/marketplace/products/{product_id}/suspend
Authentication: Admin login required

Request Body:
{
  "reason": "Violates marketplace policies"
}

Response:
{
  "id": 4,
  "status": "suspended",
  "suspension_reason": "Violates marketplace policies"
}
```

#### 6. Verify Seller (Admin)
**API Endpoint**:
```
PUT /api/v1x/marketplace/admin/marketplace/sellers/{seller_id}/verify
Authentication: Admin login required

Request Body:
{
  "verified": true
}
```

#### 7. Marketplace Revenue
**API Endpoint**:
```
GET /api/v1x/marketplace/admin/revenue
Authentication: Admin login required

Response:
{
  "total_revenue": 0.0,
  "net_revenue": 0.0,
  "refund_amount": 0.0,
  "total_orders": 0,
  "pending_orders": 0,
  "refunded_orders": 0,
  "total_sellers": 4,
  "total_products": 5,
  "average_order_value": 0.0,
  "timestamp": "2026-01-27T..."
}
```

#### 8. Revenue by Seller
**API Endpoint**:
```
GET /api/v1x/marketplace/admin/revenue-by-seller
Query Parameters:
  - sort_by: Sort field (revenue, orders, rating)
  - skip: Pagination
  - limit: Items per page
```

---

## Current System Status

### Summary
```
Total Products:     5
├─ Published:       3
├─ Draft:           2
└─ Suspended:       0

Total Sellers:      4
├─ Verified:        4
└─ Active:          4

Sales Metrics:
├─ Total Orders:    0
├─ Total Revenue:   $0.00
├─ Platform Fee:    $0.00
└─ Seller Earnings: $0.00
```

### Your Products (Seller: mentor.sarah@skillforge.com)
1. **Advanced Python Programming** (ID: 4)
   - Price: $99.99
   - Status: Draft
   - Created: Jan 27, 2026
   - Views: 0
   - Sales: 0

2. **Python Cheat Sheet** (ID: 1)
   - Price: $9.99
   - Status: Published
   - Created: Jan 27, 2026
   - Views: 0
   - Sales: 0

### Other Sellers
- David Kumar (2 products)
- Emily Rodriguez (1 product)
- James Patterson (0 products)

---

## Quick Reference - All Endpoints

### Seller Endpoints
```
GET    /api/v1x/marketplace/seller/products           - List your products
GET    /api/v1x/marketplace/seller/products/{id}      - Get product details
POST   /api/v1x/marketplace/seller/products           - Create product
PUT    /api/v1x/marketplace/seller/products/{id}      - Update product
DELETE /api/v1x/marketplace/seller/products/{id}      - Delete product
GET    /api/v1x/marketplace/seller/stats              - Your sales stats
GET    /api/v1x/marketplace/seller/orders             - Your orders
GET    /api/v1x/marketplace/seller/account            - Your seller account
GET    /api/v1x/marketplace/seller/analytics          - Your analytics
```

### Admin Endpoints
```
GET    /api/v1x/marketplace/admin/marketplace/dashboard        - Dashboard metrics
GET    /api/v1x/marketplace/admin/marketplace/products         - All products
PUT    /api/v1x/marketplace/admin/marketplace/products/{id}/approve  - Approve product
PUT    /api/v1x/marketplace/admin/marketplace/products/{id}/suspend  - Suspend product
GET    /api/v1x/marketplace/admin/marketplace/sellers          - All sellers
PUT    /api/v1x/marketplace/admin/marketplace/sellers/{id}/verify - Verify seller
GET    /api/v1x/marketplace/admin/revenue                      - Revenue metrics
GET    /api/v1x/marketplace/admin/revenue-by-seller            - Revenue by seller
GET    /api/v1x/marketplace/admin/payouts                      - Payout info
```

---

## Testing Guide

### Test 1: View Your Products (Seller)
```bash
# 1. Login
curl -X POST "http://localhost:8001/api/v1x/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mentor.sarah@skillforge.com",
    "password": "mentor123"
  }' \
  -c cookies.txt

# 2. Get your products
curl -X GET "http://localhost:8001/api/v1x/marketplace/seller/products" \
  -b cookies.txt
```

### Test 2: Admin Dashboard
```bash
# 1. Login as admin
curl -X POST "http://localhost:8001/api/v1x/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@skillforge.com",
    "password": "admin123"
  }' \
  -c cookies.txt

# 2. Get dashboard
curl -X GET "http://localhost:8001/api/v1x/marketplace/admin/marketplace/dashboard" \
  -b cookies.txt
```

### Test 3: Approve a Product (Admin)
```bash
# Approve product ID 4
curl -X PUT "http://localhost:8001/api/v1x/marketplace/admin/marketplace/products/4/approve" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "approval_notes": "Product approved after quality review"
  }'
```

---

## Product Workflow

### Seller Workflow
1. **Create Product** → Draft status
2. **Fill Details** → Complete description, pricing, files
3. **Submit for Review** → Sent to admin
4. **Admin Reviews** → Checks content and policies
5. **Product Published** → Available for purchase (if approved)
6. **Track Sales** → View stats and earnings
7. **Manage Product** → Edit, update, or remove

### Admin Workflow
1. **Review Products** → View pending products
2. **Check Quality** → Verify content meets standards
3. **Approve/Reject** → Publish or suspend product
4. **Monitor Sales** → Track revenue and metrics
5. **Manage Sellers** → Verify sellers, handle disputes
6. **Payout Management** → Process seller payments

---

## Next Steps

1. **Publish Your Products**: Go to seller dashboard and change draft products to published
2. **Add Product Details**: Upload thumbnail, add files, improve descriptions
3. **Invite Customers**: Share products with users
4. **Monitor Sales**: Check your analytics and earnings
5. **Request Payout**: Once you have earnings, request payment

---

## Support

For issues or questions:
1. Check backend logs: `tail backend.log`
2. Verify credentials are correct
3. Ensure backend is running: `python -m uvicorn app.main:app --reload`
4. Clear browser cache if frontend issues
5. Check database: `sqlite3 backend/app/data/skillforge.db`

---

**System Ready!** You can now manage your marketplace products and view admin controls.
