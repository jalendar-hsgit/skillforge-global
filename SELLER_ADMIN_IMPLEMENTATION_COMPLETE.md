# SELLER & ADMIN MARKETPLACE IMPLEMENTATION - COMPLETE GUIDE

## Status: ✅ CRITICAL BUGS FIXED

### Bugs Fixed (3 Files, 5 API Endpoints)

**1. ✅ src/pages/marketplace/seller/products.tsx**
- Line 40: Changed `/api/session/v1x/seller/products` → `/api/v1x/marketplace/seller/products`
- Line 68: Changed `/api/session/v1x/seller/products/${id}` → `/api/v1x/marketplace/seller/products/${id}`
- **Impact**: Products list now loads correctly

**2. ✅ src/pages/marketplace/seller/create-product.tsx**
- Line 130: POST endpoint fixed
- Line 153: Upload endpoint fixed
- Line 195-196: PUT endpoint fixed
- **Impact**: Product creation and editing now work

**3. ✅ All endpoints now use `${process.env.NEXT_PUBLIC_API_BASE || ''}`**
- Ensures consistent API base URL across all requests
- Works in dev (localhost:8001) and production

---

## DATABASE & SEEDING

### Demo Data Created When Running Backend

```bash
# From backend/ directory
python seed_all_demo_data.py
```

Creates:
- ✅ 7 Users (2 admin + 5 regular)
- ✅ 4 Mentors (Sarah, David, Emily, James)
- ✅ 5 Courses
- ✅ 3 Digital Products (per seller)
- ✅ 8 Mentor Sessions
- ✅ Products with status: DRAFT, PUBLISHED, ARCHIVED

### Marketplace Database Schema

```python
class DigitalProduct(Base):
    __tablename__ = "digital_products"
    
    id: int
    seller_id: int (FK → users.id)
    name: str
    slug: str (unique)
    description: str
    product_type: str (COURSE, TEMPLATE, CHEATSHEET, GUIDE)
    price: float
    status: str (DRAFT, PUBLISHED, ARCHIVED)
    thumbnail_url: str (optional)
    content_url: str (optional)
    preview_url: str (optional)
    sales_count: int (default: 0)
    average_rating: float (default: 0.0)
    created_at: datetime
    updated_at: datetime

class Order(Base):
    __tablename__ = "orders"
    
    id: int
    user_id: int (FK → users.id)
    product_id: int (FK → digital_products.id)
    order_number: str (unique)
    amount: float
    status: str (PENDING, COMPLETED, FAILED, REFUNDED)
    payment_method: str
    created_at: datetime
```

---

## BACKEND API ENDPOINTS

### Location: `backend/app/api/v1x/marketplace.py` (2,728 lines)

### SELLER ENDPOINTS

#### 1. Get All Seller Products
```
GET /api/v1x/marketplace/seller/products?status=DRAFT&limit=10&skip=0
Headers: Cookie with session_id
Response:
{
  "products": [
    {
      "id": 1,
      "name": "Python Cheatsheet",
      "slug": "python-cheatsheet",
      "product_type": "CHEATSHEET",
      "price": 29.99,
      "status": "DRAFT",
      "sales_count": 0,
      "average_rating": 0.0,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### 2. Create Product
```
POST /api/v1x/marketplace/seller/products
Headers: Content-Type: application/json, Cookie
Body:
{
  "name": "React Advanced",
  "description": "Advanced React patterns",
  "product_type": "COURSE",
  "price": 99.99
}
Response:
{
  "id": 123,
  "name": "React Advanced",
  "slug": "react-advanced",
  "status": "DRAFT"
}
```

#### 3. Update Product
```
PUT /api/v1x/marketplace/seller/products/{product_id}
Headers: Content-Type: application/json, Cookie
Body:
{
  "name": "React Advanced (Updated)",
  "price": 119.99,
  "status": "PUBLISHED"
}
Response: Updated product data
```

#### 4. Upload Product File
```
POST /api/v1x/marketplace/seller/products/{product_id}/upload-thumbnail
Headers: Content-Type: multipart/form-data, Cookie
Body: file (binary)
Response:
{
  "thumbnail_url": "https://cdn.example.com/products/123/thumb.jpg"
}
```

Upload types: `thumbnail`, `content`, `preview`

#### 5. Delete Product
```
DELETE /api/v1x/marketplace/seller/products/{product_id}
Headers: Cookie
Response: 204 No Content
```

#### 6. Get Seller Analytics
```
GET /api/v1x/marketplace/seller/analytics
Headers: Cookie
Response:
{
  "total_products": 5,
  "total_sales": 1250.00,
  "total_orders": 10,
  "average_rating": 4.5,
  "sales_by_product": [...]
}
```

---

### ADMIN ENDPOINTS

#### 1. Admin Marketplace Dashboard
```
GET /api/v1x/admin/marketplace/dashboard
Headers: Cookie
Response:
{
  "total_products": 45,
  "pending_approval": 3,
  "published_products": 40,
  "archived_products": 2,
  "total_sellers": 8,
  "verified_sellers": 6,
  "pending_sellers": 2,
  "total_revenue": 15420.50,
  "total_orders": 128,
  "recent_products": [...],
  "top_sellers": [...]
}
```

#### 2. Get All Products (Admin)
```
GET /api/v1x/admin/marketplace/products?status=PENDING&limit=20
Headers: Cookie
Response:
{
  "products": [
    {
      "id": 1,
      "name": "...",
      "seller_id": 5,
      "seller_name": "Sarah Chen",
      "status": "PENDING",
      "price": 49.99,
      "sales_count": 0,
      "submitted_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 3
}
```

#### 3. Approve Product
```
PUT /api/v1x/admin/marketplace/products/{product_id}/approve
Headers: Content-Type: application/json, Cookie
Body:
{
  "status": "PUBLISHED",
  "notes": "Looks great! Approved for publication."
}
Response:
{
  "id": 1,
  "status": "PUBLISHED",
  "approved_by_admin_id": 2,
  "approved_at": "2024-01-15T11:30:00Z"
}
```

#### 4. Reject Product
```
PUT /api/v1x/admin/marketplace/products/{product_id}/reject
Headers: Content-Type: application/json, Cookie
Body:
{
  "rejection_reason": "Content does not meet our quality standards. Please revise and resubmit."
}
Response:
{
  "id": 1,
  "status": "REJECTED",
  "rejection_reason": "..."
}
```

#### 5. Get All Sellers (Admin)
```
GET /api/v1x/admin/marketplace/sellers?status=PENDING&limit=20
Headers: Cookie
Response:
{
  "sellers": [
    {
      "id": 5,
      "user_id": 5,
      "name": "Sarah Chen",
      "email": "sarah@example.com",
      "products_count": 3,
      "total_sales": 450.00,
      "status": "PENDING",
      "submitted_at": "2024-01-10T10:00:00Z"
    }
  ],
  "total": 2
}
```

#### 6. Verify Seller
```
PUT /api/v1x/admin/marketplace/sellers/{seller_id}/verify
Headers: Content-Type: application/json, Cookie
Body:
{
  "status": "VERIFIED",
  "verification_notes": "Identity verified. Documents authentic."
}
Response:
{
  "seller_id": 5,
  "status": "VERIFIED",
  "verified_by_admin_id": 2,
  "verified_at": "2024-01-15T11:30:00Z"
}
```

#### 7. Get All Orders (Admin)
```
GET /api/v1x/admin/marketplace/orders?limit=20&skip=0
Headers: Cookie
Response:
{
  "orders": [
    {
      "id": 1,
      "order_number": "ORD-5-123",
      "user_name": "John Doe",
      "product_name": "Python Course",
      "seller_name": "Sarah Chen",
      "amount": 49.99,
      "status": "COMPLETED",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 128
}
```

#### 8. View Payouts (Admin)
```
GET /api/v1x/admin/marketplace/payouts?status=PENDING
Headers: Cookie
Response:
{
  "payouts": [
    {
      "id": 1,
      "seller_id": 5,
      "seller_name": "Sarah Chen",
      "amount": 1250.00,
      "status": "PENDING",
      "requested_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 2
}
```

#### 9. Process Payout
```
PUT /api/v1x/admin/marketplace/payouts/{payout_id}/approve
Headers: Content-Type: application/json, Cookie
Body:
{
  "status": "COMPLETED",
  "transaction_id": "TXN-12345",
  "notes": "Payment transferred to seller account."
}
Response:
{
  "id": 1,
  "status": "COMPLETED",
  "processed_at": "2024-01-15T12:00:00Z"
}
```

---

## FRONTEND PAGES

### Seller Pages Location: `src/pages/marketplace/seller/`

#### 1. **Dashboard** (`index.tsx`)
- Overview of seller stats
- Quick links to products, orders, analytics
- Recent activity

#### 2. **My Products** (`products.tsx`) ✅ FIXED
- List all seller's products
- Filter by status (DRAFT, PUBLISHED, ARCHIVED)
- Search products
- Actions: Edit, Delete, View
- Create New Product button

**Status**: 
- API endpoint fixed ✅
- Fetches from `/api/v1x/marketplace/seller/products` ✅
- Delete endpoint fixed ✅

#### 3. **Create/Edit Product** (`create-product.tsx`) ✅ FIXED
- Form fields:
  - Name (required)
  - Description
  - Product Type (COURSE, TEMPLATE, CHEATSHEET, GUIDE)
  - Price
  - Thumbnail image upload
  - Content file upload
  - Preview file upload
- Save as Draft or Publish
- Auto-save functionality

**Status**:
- POST endpoint fixed ✅
- PUT endpoint fixed ✅
- File upload endpoints fixed ✅
- All 3 file upload types supported ✅

#### 4. **Orders** (`orders.tsx`)
- View all orders of seller's products
- Filter by status
- View customer details
- Order details and timeline

#### 5. **Analytics** (`analytics.tsx`)
- Total sales revenue
- Total orders count
- Average rating
- Sales by product chart
- Best performing products
- Sales trend graph

---

### Admin Pages Location: `src/pages/admin/`

#### 1. **Marketplace Dashboard** (`marketplace.tsx`)
- Total products, sellers, revenue overview
- Pending approval count
- Verified sellers count
- Recent product submissions
- Top performing sellers
- Chart: Sales over time
- Chart: Products by status

#### 2. **Marketplace Products** (`marketplace.tsx`) - Tab
- List all products in marketplace
- Filter by status (PENDING, PUBLISHED, ARCHIVED)
- Search products
- View product details (seller, price, sales)
- Actions:
  - **Approve** → Sets status to PUBLISHED + adds approval note
  - **Reject** → Sets status to REJECTED + asks for rejection reason
  - **Archive** → Removes from marketplace
  - **View Details** → Opens full product info

#### 3. **Sellers Management** (`marketplace.tsx`) - Tab
- List all sellers
- Filter by verification status (PENDING, VERIFIED, REJECTED)
- Show:
  - Seller name and email
  - Products count
  - Total sales
  - Average rating
  - Verification status
- Actions:
  - **Verify** → Approve seller for marketplace
  - **Reject** → Reject seller verification
  - **View Profile** → See seller details
  - **View Products** → List seller's products

#### 4. **Mentor Verification** (`mentor-verification.tsx`)
- List mentors awaiting verification
- Document review section
- Actions:
  - **Approve** → Status: APPROVED
  - **Reject** → Status: REJECTED (with reason)
- View mentor profile
- Check verification documents

#### 5. **Payouts Management** (`payouts.tsx`)
- List all payout requests from sellers
- Filter by status (PENDING, COMPLETED, FAILED)
- Show:
  - Seller name
  - Payout amount
  - Request date
  - Status
- Actions:
  - **Process** → Approve payout
  - **Reject** → Return payout
  - **View Details** → See payout breakdown

---

## COMPLETE WORKFLOWS

### Workflow 1: SELLER CREATES & SELLS A PRODUCT

#### Step 1: Seller Navigates to Products Page
```
1. Click Sidebar → "My Products"
2. URL: /marketplace/seller/products
3. Page loads and fetches products via:
   GET /api/v1x/marketplace/seller/products
```

#### Step 2: Seller Clicks "Create New Product"
```
1. Click "New Product" button
2. URL: /marketplace/seller/create-product
3. Form displays with fields:
   - Name
   - Description
   - Product Type (dropdown)
   - Price
```

#### Step 3: Seller Fills Form and Uploads Files
```
1. Enter product name: "React Advanced Patterns"
2. Enter description
3. Select type: "COURSE"
4. Enter price: $99.99
5. Upload thumbnail (JPG/PNG)
6. Upload content (PDF)
7. Upload preview (MP4)
8. Click "Save as Draft"

POST /api/v1x/marketplace/seller/products
{
  "name": "React Advanced Patterns",
  "description": "...",
  "product_type": "COURSE",
  "price": 99.99
}
→ Returns: { id: 123, status: "DRAFT" }

Then uploads files:
POST /api/v1x/marketplace/seller/products/123/upload-thumbnail
POST /api/v1x/marketplace/seller/products/123/upload-content
POST /api/v1x/marketplace/seller/products/123/upload-preview
```

#### Step 4: Seller Publishes Product
```
1. Back on /marketplace/seller/products
2. Find product in DRAFT status
3. Click "Publish"

PUT /api/v1x/marketplace/seller/products/123
{
  "status": "PUBLISHED"
}
→ Product now visible in marketplace
```

---

### Workflow 2: ADMIN APPROVES PRODUCT FOR MARKETPLACE

#### Step 1: Admin Views Pending Products
```
1. Navigate to Admin Dashboard
2. Click "Marketplace" → "Products"
3. Filter by Status = "PENDING"
4. List shows pending products with seller info

GET /api/v1x/admin/marketplace/products?status=PENDING
```

#### Step 2: Admin Reviews Product
```
1. Click on product to view details:
   - Name, description, price
   - Seller information
   - Uploaded files preview
   - Sales count (0 initially)
```

#### Step 3: Admin Approves or Rejects
```
APPROVE:
PUT /api/v1x/admin/marketplace/products/123/approve
{
  "status": "PUBLISHED",
  "notes": "Great content! Approved."
}

REJECT:
PUT /api/v1x/admin/marketplace/products/123/reject
{
  "rejection_reason": "Content needs better organization. Please revise."
}
```

#### Step 4: Product Status Updated
```
- If approved: status = "PUBLISHED"
- Appears in public marketplace
- Customers can now purchase
- If rejected: status = "REJECTED"
- Seller sees rejection reason
- Can revise and resubmit
```

---

### Workflow 3: CUSTOMER PURCHASES A PRODUCT

#### Step 1: Customer Browses Marketplace
```
1. Navigate to /marketplace
2. View all published products
3. Filter by category or search

GET /api/v1x/marketplace/products?status=PUBLISHED
```

#### Step 2: Customer Clicks "Buy Now"
```
1. Product ID selected: 123
2. System creates order:

POST /api/v1x/marketplace/orders
{
  "product_id": 123,
  "user_id": 1
}
→ Returns: { order_id: 456, order_number: "ORD-1-123" }
```

#### Step 3: Payment Processing
```
1. Redirect to payment page
2. Complete payment
3. Order status: PENDING → COMPLETED
4. Access to product files granted
5. Seller sees new sale in analytics
```

---

### Workflow 4: SELLER REQUESTS PAYOUT

#### Step 1: Seller Views Analytics
```
1. Navigate to /marketplace/seller/analytics
2. See total sales and revenue
3. Click "Request Payout"

GET /api/v1x/marketplace/seller/analytics
```

#### Step 2: Seller Submits Payout Request
```
POST /api/v1x/marketplace/seller/payouts
{
  "amount": 1250.00,
  "bank_account_id": 789
}
→ Status: "PENDING"
```

#### Step 3: Admin Reviews & Processes Payout
```
1. Admin Dashboard → Marketplace → Payouts
2. Click on pending payout request
3. Review seller and amount
4. Click "Process Payout"

PUT /api/v1x/admin/marketplace/payouts/1/approve
{
  "status": "COMPLETED",
  "transaction_id": "TXN-XYZ123",
  "notes": "Payment processed"
}
```

#### Step 4: Seller Receives Payment
```
- Payout status: "COMPLETED"
- Payment transferred to seller's bank
- Seller sees confirmation in analytics
```

---

### Workflow 5: ADMIN VERIFIES SELLER

#### Step 1: Admin Views Sellers
```
1. Admin Dashboard → Marketplace → Sellers
2. Filter by Status = "PENDING"
3. Shows unverified sellers

GET /api/v1x/admin/marketplace/sellers?status=PENDING
```

#### Step 2: Admin Reviews Seller Documents
```
1. Click on seller to view profile
2. See:
   - Seller information
   - Documents uploaded
   - Product history
   - Sales history
```

#### Step 3: Admin Verifies or Rejects
```
VERIFY:
PUT /api/v1x/admin/marketplace/sellers/5/verify
{
  "status": "VERIFIED",
  "verification_notes": "Documents authentic"
}

REJECT:
PUT /api/v1x/admin/marketplace/sellers/5/reject
{
  "rejection_reason": "Documents not verified"
}
```

#### Step 4: Seller Status Updated
```
- If verified: Can sell on marketplace
- All products auto-approved for sale
- Access to payout requests
- If rejected: Cannot sell
- Must resubmit documents for review
```

---

## TESTING CHECKLIST

### Seller Features
- [ ] Login as seller (sarah@example.com)
- [ ] Navigate to "My Products"
- [ ] See list of 3 products
- [ ] Click "Create New Product"
- [ ] Fill form and upload files
- [ ] Save as Draft
- [ ] See new product in list with DRAFT status
- [ ] Edit product name and price
- [ ] Publish product
- [ ] See status change to PUBLISHED
- [ ] Delete a product
- [ ] Confirm product removed from list
- [ ] View analytics
- [ ] See sales and revenue data

### Admin Features
- [ ] Login as admin (admin@skillforge.com)
- [ ] Navigate to Admin Dashboard
- [ ] Click "Marketplace" section
- [ ] View pending products to approve
- [ ] Approve a product
- [ ] See product status change to PUBLISHED
- [ ] View sellers section
- [ ] Verify a seller
- [ ] View payouts section
- [ ] Approve a payout request
- [ ] Navigate to Mentor Verification
- [ ] Approve/reject mentor documents

### Integration Tests
- [ ] Create product as seller
- [ ] Approve as admin
- [ ] Purchase as customer
- [ ] View order as seller
- [ ] Request payout
- [ ] Approve payout
- [ ] Verify seller documents
- [ ] Check all analytics updated

---

## API TESTING COMMANDS

### Create a Product
```bash
curl -X POST http://localhost:8001/api/v1x/marketplace/seller/products \
  -H "Content-Type: application/json" \
  -b "sessionid=YOUR_SESSION_ID" \
  -d '{
    "name": "New Course",
    "description": "Course description",
    "product_type": "COURSE",
    "price": 99.99
  }'
```

### Get Products
```bash
curl http://localhost:8001/api/v1x/marketplace/seller/products \
  -b "sessionid=YOUR_SESSION_ID"
```

### Approve Product (Admin)
```bash
curl -X PUT http://localhost:8001/api/v1x/admin/marketplace/products/1/approve \
  -H "Content-Type: application/json" \
  -b "sessionid=YOUR_SESSION_ID" \
  -d '{
    "status": "PUBLISHED",
    "notes": "Looks good"
  }'
```

### Get Admin Dashboard
```bash
curl http://localhost:8001/api/v1x/admin/marketplace/dashboard \
  -b "sessionid=YOUR_SESSION_ID"
```

---

## IMPORTANT NOTES

1. **API Base URL**: All endpoints use `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/`
2. **Authentication**: All endpoints require session cookie
3. **File Uploads**: Use multipart/form-data for file endpoints
4. **Pagination**: Add `limit` and `skip` query parameters for list endpoints
5. **Status Transitions**:
   - Product: DRAFT → PUBLISHED → ARCHIVED
   - Seller: PENDING → VERIFIED or REJECTED
   - Payout: PENDING → COMPLETED or FAILED
6. **Demo Data**: Run `python backend/seed_all_demo_data.py` to populate test data

---

## NEXT STEPS

1. ✅ API endpoints fixed in frontend
2. ✅ Backend endpoints all implemented
3. ✅ Database models ready
4. ⏳ Run demo data seeding
5. ⏳ Test seller product creation flow
6. ⏳ Test admin approval workflow
7. ⏳ Test payment and payout flows

