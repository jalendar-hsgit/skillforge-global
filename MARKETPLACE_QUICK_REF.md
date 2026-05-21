# MARKETPLACE - QUICK REFERENCE CARD

## Your Products Created

| Product | Price | Status | Views | Sales |
|---------|-------|--------|-------|-------|
| Advanced Python Programming | $99.99 | Draft | 0 | 0 |
| Python Cheat Sheet | $9.99 | Published | 0 | 0 |

---

## View Your Products

### Option 1: Browser
Go to: `http://localhost:3000/marketplace/seller/products`

### Option 2: API Call
```bash
curl "http://localhost:8001/api/v1x/marketplace/seller/products" \
  -H "Cookie: token=YOUR_JWT_TOKEN"
```

### Option 3: Python Code
```python
import requests

response = requests.get(
    "http://localhost:8001/api/v1x/marketplace/seller/products",
    cookies={"token": "your_jwt_token"}
)
print(response.json())
```

---

## Admin Marketplace Features

### 1. View Dashboard
```
API: GET /api/v1x/marketplace/admin/marketplace/dashboard
Shows: Products, Sellers, Sales metrics
```

### 2. List All Products
```
API: GET /api/v1x/marketplace/admin/marketplace/products
Shows: 5 total products
```

### 3. List All Sellers
```
API: GET /api/v1x/marketplace/admin/marketplace/sellers
Shows: 4 total sellers
```

### 4. Approve Product
```
API: PUT /api/v1x/marketplace/admin/marketplace/products/{id}/approve
Action: Publish product for sale
```

### 5. Suspend Product
```
API: PUT /api/v1x/marketplace/admin/marketplace/products/{id}/suspend
Action: Remove product from marketplace
```

---

## Current Stats

```
Products:     5 (3 published, 2 draft)
Sellers:      4 (all verified)
Orders:       0
Revenue:      $0.00
```

---

## Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Seller | mentor.sarah@skillforge.com | mentor123 |
| Admin | admin@skillforge.com | admin123 |
| Superadmin | superadmin@skillforge.com | super123 |

---

## Key Endpoints

### Seller APIs
```
GET    /api/v1x/marketplace/seller/products       ← View your products
POST   /api/v1x/marketplace/seller/products       ← Create product
GET    /api/v1x/marketplace/seller/products/{id}  ← View one product
PUT    /api/v1x/marketplace/seller/products/{id}  ← Edit product
DELETE /api/v1x/marketplace/seller/products/{id}  ← Delete product
GET    /api/v1x/marketplace/seller/stats          ← Your statistics
GET    /api/v1x/marketplace/seller/analytics      ← Your analytics
```

### Admin APIs
```
GET    /api/v1x/marketplace/admin/marketplace/dashboard          ← Dashboard
GET    /api/v1x/marketplace/admin/marketplace/products           ← All products
GET    /api/v1x/marketplace/admin/marketplace/sellers            ← All sellers
PUT    /api/v1x/marketplace/admin/marketplace/products/{id}/approve
PUT    /api/v1x/marketplace/admin/marketplace/products/{id}/suspend
PUT    /api/v1x/marketplace/admin/marketplace/sellers/{id}/verify
```

---

## Test Commands

### Create Product
```bash
curl -X POST "http://localhost:8001/api/v1x/marketplace/seller/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Course",
    "description": "Course description",
    "product_type": "course",
    "category": "programming",
    "price": 49.99,
    "tags": ["python", "course"]
  }' \
  -b cookies.txt
```

### View Products
```bash
curl "http://localhost:8001/api/v1x/marketplace/seller/products" \
  -b cookies.txt | jq
```

### Admin Dashboard
```bash
curl "http://localhost:8001/api/v1x/marketplace/admin/marketplace/dashboard" \
  -b cookies.txt | jq
```

### Approve Product
```bash
curl -X PUT "http://localhost:8001/api/v1x/marketplace/admin/marketplace/products/4/approve" \
  -H "Content-Type: application/json" \
  -d '{"approval_notes": "Approved"}' \
  -b cookies.txt
```

---

## All Sellers

```
1. Sarah Chen (ID: 8)
   - Email: mentor.sarah@skillforge.com
   - Products: 2
   - Status: Verified ✓

2. David Kumar (ID: 9)
   - Email: mentor.david@skillforge.com
   - Products: 2
   - Status: Verified ✓

3. Emily Rodriguez (ID: 10)
   - Email: mentor.emily@skillforge.com
   - Products: 1
   - Status: Verified ✓

4. James Patterson (ID: 11)
   - Email: mentor.james@skillforge.com
   - Products: 0
   - Status: Verified ✓
```

---

## All Products

```
ID  Name                          Price    Status
─────────────────────────────────────────────────
1   Python Cheat Sheet            $9.99    published
2   Python Templates Bundle       $24.99   published
3   React Advanced Course         $149.99  published
4   Advanced Python Programming  $99.99   draft
5   DevOps Essentials            $79.99   draft
```

---

## Files

| File | Purpose |
|------|---------|
| MARKETPLACE_SELLER_ADMIN_GUIDE.md | Complete guide with all endpoints |
| MARKETPLACE_TESTED_WORKING.md | Test results and status |
| QUICK_START.md | Quick start guide |
| LOGIN_AND_PRODUCT_CREATION_FIXED.md | Login and creation fixes |

---

## Status: ✅ ALL WORKING

- Products created: 2
- Admin features: All operational
- API endpoints: Tested and working
- Authentication: Working
- Database: Synchronized

Ready to use! 🚀
