# 📊 Complete SkillForge Marketplace & Courses Architecture

## System Overview

SkillForge has **TWO main revenue modules**:
1. **Courses** - Traditional learning content (free & paid)
2. **Marketplace** - Digital products/resources from sellers

---

## 🏛️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                     SKILLFORGE PLATFORM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐    ┌──────────────────────────────┐   │
│  │   COURSES        │    │    MARKETPLACE               │   │
│  │  (Database)      │    │  (Digital Products)          │   │
│  ├──────────────────┤    ├──────────────────────────────┤   │
│  │ • Videos         │    │ • DigitalProduct (seller)    │   │
│  │ • Quizzes        │    │ • SellerAccount (profile)    │   │
│  │ • Tier: free/    │    │ • ProductPurchase (orders)   │   │
│  │   premium        │    │ • SellerPayout (earnings)    │   │
│  │ • Price: $$$     │    │ • ProductBundle (bundles)    │   │
│  │ • Orders         │    │ • MarketplaceAnalytics       │   │
│  └──────────────────┘    └──────────────────────────────┘   │
│           ↓                          ↓                        │
│     ┌──────────┐             ┌──────────────┐               │
│     │  PAYMENT │             │   PAYMENT    │               │
│     │ Stripe $$│             │ Stripe $$$   │               │
│     └──────────┘             └──────────────┘               │
│           ↓                          ↓                        │
│     ┌──────────┐             ┌──────────────┐               │
│     │  Orders  │             │  Seller Pay  │               │
│     │  (Order) │             │  (Payout)    │               │
│     └──────────┘             └──────────────┘               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 COURSES MODULE

### Database Structure
```python
Class: Course
├── id (Primary Key)
├── path (slug - unique) -> "python-basics"
├── title -> "Python Fundamentals"
├── description
├── category -> "Programming"
├── is_paid (Boolean)
├── price (Decimal) -> $49.99
├── tier -> "free" | "premium" | "enterprise"
├── is_premium (Boolean)
├── instructor -> "John Doe"
├── difficulty -> "beginner" | "intermediate" | "advanced"
├── duration_hours -> 40.5
├── rating -> 4.8
├── enrollment_count -> 150
├── youtube_playlist_id -> "PLxxxxx"
├── created_at
├── updated_at
│
└── Relationships:
    ├── videos: List[Video]
    ├── quizzes: List[Quiz]
    └── orders: List[Order]
```

### Adding a Course (Flow)

**Step 1: Create Course (Admin/Instructor)**
```
POST /api/v1/courses
{
  "path": "react-advanced",
  "title": "Advanced React",
  "description": "Master React hooks...",
  "category": "Frontend",
  "is_paid": true,
  "price": 99.99,
  "tier": "premium",
  "instructor": "Sarah Chen",
  "difficulty": "advanced",
  "duration_hours": 50
}
```

**Step 2: Add Videos**
```
POST /api/v1/courses/{course_id}/videos
{
  "title": "Intro to Hooks",
  "youtube_url": "https://youtube.com/...",
  "duration_minutes": 45
}
```

**Step 3: Add Quizzes**
```
POST /api/v1/courses/{course_id}/quizzes
{
  "title": "Hooks Assessment",
  "questions": [...]
}
```

**Step 4: Publish Course**
```
PATCH /api/v1/courses/{course_id}
{
  "status": "published"
}
```

### Buying a Course (Flow)

**1. Add to Cart**
```
POST /api/v1x/marketplace/cart
{
  "course_id": 1
}
Response: Cart item added
```

**2. Checkout**
```
POST /api/v1x/marketplace/checkout
{
  "product_ids": [1],
  "coupon_code": "SAVE10",
  "payment_method": "stripe"
}
Response: {
  "order_id": 42,
  "client_secret": "pi_xxx",
  "total_amount": 89.99
}
```

**3. Payment (Stripe)**
- User enters card details
- Stripe processes payment
- Order marked as "completed"

**4. Access Course**
```
GET /api/v1/courses/{course_id}/progress
Response: Course unlocked, can view all videos
```

---

## 🛍️ MARKETPLACE MODULE

### Three Levels of Models

#### Level 1: Seller Profile
```python
Class: SellerAccount
├── user_id (FK → User)
├── is_verified (Boolean)
├── store_name -> "Sarah's Tech Templates"
├── store_description
├── seller_email
├── payout_method -> "stripe" | "bank_transfer" | "paypal"
├── payout_account -> "acct_xxx" (encrypted)
├── tax_id (encrypted)
├── identification_verified
├── bank_verified
├── total_sales -> 150
├── total_revenue -> $5,000
├── total_payouts -> $4,000 (20% fee taken)
├── average_rating -> 4.9
├── seller_tier -> "basic" | "professional" | "premium"
├── commission_rate -> 0.20 (20% platform fee)
└── created_at, updated_at
```

#### Level 2: Digital Products (What's Sold)
```python
Class: DigitalProduct
├── id (Primary Key)
├── seller_id (FK → User)
├── name -> "Advanced React Template"
├── slug -> "advanced-react-template"
├── description -> "Production-ready template..."
├── product_type -> "template" | "resource" | "course" | "tool"
├── category -> "Frontend"
├── price -> 29.99
├── original_price -> 49.99
├── content_url -> "s3://..." | "gdrive://..."
├── preview_url -> "thumbnail.jpg"
├── file_size_mb -> 125.5
├── status -> "draft" | "published" | "archived" | "suspended"
├── is_featured (Boolean)
├── visibility -> "public" | "private"
├── requirements -> ["React 18+", "TypeScript knowledge"]
├── features -> ["Dark mode", "Responsive design"]
├── extra_data -> {...}
├── sales_count -> 50
├── total_revenue -> $1,500
├── average_rating -> 4.7
├── review_count -> 45
├── views_count -> 2,500
└── published_at
```

#### Level 3: Purchase Transaction
```python
Class: ProductPurchase
├── id (Primary Key)
├── product_id (FK → DigitalProduct)
├── buyer_id (FK → User)
├── seller_id (FK → User)
├── purchase_price -> 29.99
├── payment_method -> "stripe" | "paypal" | "coins"
├── transaction_id -> "ch_xxx"
├── status -> "completed" | "refunded" | "pending"
├── delivered_at (DateTime)
├── download_url -> "https://..."
├── download_count -> 3
├── refunded_at (DateTime)
├── refund_reason -> "Not as described"
├── platform_fee -> 6.00 (20%)
├── seller_payout -> 23.99 (80%)
└── purchased_at (DateTime)
```

---

## 💰 MARKETPLACE EARNING FLOW (How Money Works)

### Commission Structure

```
Customer Pays: $100.00
     ↓
  Stripe Fee: -$2.90 (2.9%)
     ↓
  Platform: $97.10
     ↓
  Platform Takes: -$19.42 (20% commission)
     ↓
  Seller Gets: $77.68 (80% payout)
```

### Step-by-Step Earning Process

**1. Seller Creates Product**
```
SellerAccount (seller_id=5)
├── store_name: "Tech Templates Co"
├── is_verified: true
├── commission_rate: 0.20 (20%)
└── payout_method: "stripe"

DigitalProduct (seller_id=5)
├── name: "React Dashboard Template"
├── price: 49.99
└── status: "published"
```

**2. Customer Purchases**
```
Customer clicks "Buy Now" → Stripe payment → Order created

Order (user_id=10, course_id=N/A)
├── amount: 49.99
├── payment_intent_id: "pi_xxx"
├── payment_status: "completed"
├── status: "completed"
└── paid_at: 2026-01-25

ProductPurchase (automatically created)
├── buyer_id: 10
├── seller_id: 5
├── purchase_price: 49.99
├── platform_fee: 9.99 (20%)
├── seller_payout: 39.99 (80%)
├── status: "completed"
└── delivered_at: 2026-01-25
```

**3. Seller's Revenue Tracked**
```
DigitalProduct (updated)
├── sales_count: 1 (incremented)
├── total_revenue: 49.99 (cumulative)
└── average_rating: 5.0
```

**4. Monthly Payout Processing**
```
SellerPayout (created monthly)
├── seller_id: 5
├── period_start: 2026-01-01
├── period_end: 2026-01-31
├── total_sales: 49.99 (from all products)
├── platform_fee: 9.99 (20% deducted)
├── payout_amount: 39.99 (after fees)
├── status: "pending" → "processing" → "completed"
├── payout_method: "stripe"
├── transaction_id: "tr_xxx"
└── processed_at: 2026-02-05

SellerAccount (updated)
├── total_sales: +1
├── total_revenue: +49.99
└── total_payouts: +39.99
```

---

## 🔗 ALL MARKETPLACE URLs

### CUSTOMER ENDPOINTS

#### Browse & Browse
```
GET /api/v1x/marketplace/
GET /api/v1x/marketplace/products
GET /api/v1x/marketplace/products/{product_id}
GET /api/v1x/marketplace/search?q=template&category=frontend
GET /api/v1x/marketplace/categories
GET /api/v1x/marketplace/featured
```

#### Cart Management
```
POST /api/v1x/marketplace/cart
GET /api/v1x/marketplace/cart
DELETE /api/v1x/marketplace/cart/{item_id}
POST /api/v1x/marketplace/cart/clear
```

#### Checkout & Payment
```
POST /api/v1x/marketplace/checkout
POST /api/v1x/marketplace/confirm-payment/{order_id}
POST /api/v1x/marketplace/validate-coupon
```

#### Orders
```
GET /api/v1x/marketplace/orders
GET /api/v1x/marketplace/orders/{order_id}
POST /api/v1x/marketplace/orders/{order_id}/download
```

#### Reviews & Ratings
```
POST /api/v1x/marketplace/products/{product_id}/reviews
GET /api/v1x/marketplace/products/{product_id}/reviews
POST /api/v1x/marketplace/orders/{order_id}/review
```

#### Wishlist
```
POST /api/v1x/marketplace/wishlist/add
GET /api/v1x/marketplace/wishlist
DELETE /api/v1x/marketplace/wishlist/{product_id}
```

---

### SELLER ENDPOINTS (Merchant Portal)

#### Dashboard & Analytics
```
GET /api/v1x/seller/dashboard
GET /api/v1x/seller/analytics
GET /api/v1x/seller/analytics/timeline?days=30
GET /api/v1x/seller/analytics/products
```

#### Product Management
```
POST /api/v1x/seller/products
GET /api/v1x/seller/products
GET /api/v1x/seller/products/{product_id}
PATCH /api/v1x/seller/products/{product_id}
DELETE /api/v1x/seller/products/{product_id}
POST /api/v1x/seller/products/{product_id}/publish
POST /api/v1x/seller/products/{product_id}/upload-file
```

#### Orders (Sales)
```
GET /api/v1x/seller/orders
GET /api/v1x/seller/orders/{order_id}
POST /api/v1x/seller/orders/{order_id}/deliver
POST /api/v1x/seller/orders/{order_id}/refund
```

#### Payouts & Earnings
```
GET /api/v1x/seller/payouts
POST /api/v1x/seller/payouts/request
GET /api/v1x/seller/payouts/{payout_id}
GET /api/v1x/seller/earnings/summary
GET /api/v1x/seller/earnings/timeline
```

#### Account Management
```
GET /api/v1x/seller/account
POST /api/v1x/seller/account
POST /api/v1x/seller/account/verify
POST /api/v1x/seller/account/payout-method
```

---

### ADMIN ENDPOINTS (Platform Management)

#### Revenue Management
```
GET /api/v1x/admin/marketplace/revenue
GET /api/v1x/admin/marketplace/revenue-by-seller
GET /api/v1x/admin/marketplace/revenue-by-category
GET /api/v1x/admin/marketplace/revenue-timeline
```

#### Product Moderation
```
GET /api/v1x/admin/marketplace/products
POST /api/v1x/admin/marketplace/products/{product_id}/approve
POST /api/v1x/admin/marketplace/products/{product_id}/reject
POST /api/v1x/admin/marketplace/products/{product_id}/suspend
```

#### Seller Management
```
GET /api/v1x/admin/marketplace/sellers
GET /api/v1x/admin/marketplace/sellers/{seller_id}
POST /api/v1x/admin/marketplace/sellers/{seller_id}/verify
POST /api/v1x/admin/marketplace/sellers/{seller_id}/suspend
POST /api/v1x/admin/marketplace/sellers/{seller_id}/tier
```

#### Order & Refund Management
```
GET /api/v1x/admin/marketplace/orders
GET /api/v1x/admin/marketplace/orders/{order_id}
POST /api/v1x/admin/marketplace/orders/{order_id}/refund
GET /api/v1x/admin/marketplace/refunds
GET /api/v1x/admin/marketplace/refunds/{refund_id}
```

#### Payout Management
```
GET /api/v1x/admin/marketplace/payouts
GET /api/v1x/admin/marketplace/payouts-pending
POST /api/v1x/admin/marketplace/payouts/{payout_id}/process
GET /api/v1x/admin/marketplace/payouts-report
```

#### Analytics & Reporting
```
GET /api/v1x/admin/marketplace/analytics
GET /api/v1x/admin/marketplace/analytics-daily
GET /api/v1x/admin/marketplace/top-products
GET /api/v1x/admin/marketplace/top-sellers
```

---

## 👨‍💼 ADMIN ROLE IN MARKETPLACE

### 1. **Product Approval/Moderation**
```
Seller creates product (status: "draft")
          ↓
Admin reviews content, pricing, compliance
          ↓
Admin approves → status: "published" (visible to customers)
OR rejects → status: "draft" (back to seller)
```

### 2. **Seller Verification**
```
Seller signs up → SellerAccount created
          ↓
Admin verifies:
├── Tax ID verification
├── Bank account verification
├── Identity verification
├── Store legitimacy
          ↓
is_verified: true → Can receive payouts
```

### 3. **Seller Tier Management**
```
Seller tier levels:
├── "basic" → commission_rate: 30%
├── "professional" → commission_rate: 25% (after 100 sales)
├── "premium" → commission_rate: 20% (after 500 sales)

Admin can:
├── Promote tier based on performance
├── Adjust commission rate
├── Apply promotional discounts
```

### 4. **Refund Processing**
```
Customer requests refund (reason: "Not as described")
          ↓
Admin reviews request
          ↓
Approve refund:
├── Refund customer (payment reversed)
├── Deduct from seller's earnings
├── Update SellerPayout
├── Send emails to both parties
          ↓
Update ProductPurchase (status: "refunded")
```

### 5. **Payout Verification**
```
Monthly: Automatic SellerPayout created
          ↓
Admin dashboard shows:
├── Pending payouts (status: "pending")
├── Verifies sellers have valid payout accounts
├── Processes payouts (status: "processing" → "completed")
├── Tracks all payout transactions
```

### 6. **Revenue Monitoring**
```
Admin dashboard shows:
├── Total revenue from all marketplace sales
├── Revenue by seller (leaderboard)
├── Revenue by category
├── Refund amounts (loss tracking)
├── Platform commission earned
├── Trend analysis (week-over-week growth)
```

---

## 🔄 HOW COURSES & MARKETPLACE RELATE

### Relationship Model

```
User (Student)
    ├── Takes Course (via Order)
    ├── Enrolls in: Course (free)
    └── Downloads: DigitalProduct (template/resource)
           ↓
    May learn from course, then buy related template
    
Example Flow:
1. Student enrolls in "React Basics" course (free)
2. Student sees link: "Buy Advanced React Template"
3. Student buys template from SellerAccount
4. Student uses template to practice course concepts
5. Seller gets commission, admin gets percentage
```

### Data Integration Points

```python
# Course can reference marketplace templates
Course
├── related_products: [DigitalProduct.id, ...]
└── prerequisites: "Must complete Python course"

# Marketplace can cross-sell courses
DigitalProduct
├── related_courses: [Course.id, ...]
├── description: "Complements React Basics course"
└── features: ["Based on SkillForge React course"]

# Orders can contain both
Order
├── course_id: 5 (Course purchase)
├── product_id: N/A
└── OR
├── course_id: N/A
├── product_ids: [1, 2, 3] (Multiple products)
```

---

## 💳 PAYMENT FLOW COMPARISON

### Course Purchase
```
Course (is_paid: true, price: $49.99)
    ↓
Customer clicks "Enroll Now"
    ↓
POST /api/v1x/marketplace/checkout (course_id: 5)
    ↓
Create Order + Stripe PaymentIntent
    ↓
Customer pays $49.99
    ↓
Order.status = "completed"
Course.enrollment_count += 1
Student can now watch all videos
    ↓
Revenue flows to platform (100%)
Note: For instructor courses, need separate tracking
```

### Marketplace Product Purchase
```
DigitalProduct (seller_id: 5, price: $29.99)
    ↓
Customer clicks "Buy Now"
    ↓
POST /api/v1x/marketplace/checkout (product_ids: [1])
    ↓
Create Order + ProductPurchase + Stripe PaymentIntent
    ↓
Customer pays $29.99
    ↓
Order.status = "completed"
ProductPurchase.status = "completed"
DigitalProduct.sales_count += 1
SellerPayout.total_sales += 29.99
    ↓
Revenue splits:
├── Stripe fee: $0.87 (2.9%)
├── Platform: $5.99 (20%)
└── Seller: $23.99 (80%)
    ↓
SellerAccount.total_revenue += 29.99
SellerAccount.total_payouts += 23.99 (pending)
```

---

## 📊 DATA FLOW DIAGRAM

```
┌────────────────┐
│   Customer     │
└────────┬───────┘
         │
    ┌────▼─────┐
    │ Browse    │
    │ Products/ │
    │ Courses   │
    └────┬─────┘
         │
    ┌────▼────────────┐
    │  Add to Cart /   │
    │  Select Course   │
    └────┬────────────┘
         │
    ┌────▼──────────────┐
    │   Checkout Page   │
    │  (Review Items)   │
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │  Stripe Payment   │
    │  (Card Details)   │
    └────┬──────────────┘
         │
    ┌────▼──────────────────┐
    │  Payment Success       │
    └────┬──────────────────┘
         │
    ┌────▼────────────────────────┐
    │  Create Order/Purchase       │
    │  └─ Order Table              │
    │  └─ ProductPurchase Table    │
    └────┬────────────────────────┘
         │
    ┌────▼──────────────────────┐
    │  Update Seller Metrics     │
    │  └─ sales_count += 1       │
    │  └─ total_revenue += price │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │  Create SellerPayout       │
    │  └─ Pending monthly payout │
    │  └─ Calculate commission   │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │  Admin Reviews Payout      │
    │  └─ Verify seller account  │
    │  └─ Process to seller      │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │  Seller Receives Payout    │
    │  └─ Bank transfer          │
    │  └─ Stripe connected acct  │
    │  └─ PayPal                 │
    └────────────────────────────┘
```

---

## 🏆 TWO REVENUE PILLARS

### Pillar 1: Courses
- **Type**: Structured learning
- **Created by**: Admin/Instructors
- **Revenue**: 100% to platform
- **Verification**: Admin approval + content review
- **Delivery**: Video streaming + quizzes
- **Pricing**: Set by admin

### Pillar 2: Marketplace
- **Type**: Digital products (templates, guides, tools)
- **Created by**: Community sellers (verified)
- **Revenue**: 80% seller, 20% platform + Stripe fee
- **Verification**: Seller KYC + product review
- **Delivery**: Direct download
- **Pricing**: Set by seller

---

## 🔐 VERIFICATION LEVELS

### Course Verification (Simple)
```
✓ Admin creates course
✓ Adds videos (YouTube sync)
✓ Adds quizzes
✓ Admin publishes
✓ Visible to students
```

### Marketplace Verification (Complex)
```
SELLER VERIFICATION:
✓ Email verification
✓ Tax ID verification (encrypted)
✓ Bank account verification
✓ Identity verification
✓ is_verified: true → can sell

PRODUCT VERIFICATION:
✓ Check for copyright issues
✓ Verify pricing reasonableness
✓ Check content compliance
✓ Review product metadata
✓ Approve → status: "published"
```

---

## 📈 ANALYTICS TRACKING

### Course Analytics
```
GET /api/v1/courses/{id}/analytics
Response:
├── enrollment_count: 150
├── completion_rate: 78%
├── average_rating: 4.8
├── revenue: $7,500 (if paid)
└── student_feedback
```

### Marketplace Analytics
```
GET /api/v1x/marketplace/analytics
Response:
├── total_revenue: $50,000
├── total_sales: 1,250
├── average_order_value: $40
├── top_products: [...]
├── top_sellers: [...]
└── sales_by_category: {...}

GET /api/v1x/admin/marketplace/analytics
Response: (same as above + admin-only metrics)
├── refund_rate: 2.1%
├── disputes: 5
├── platform_commission: $10,000
└── pending_payouts: $40,000
```

---

## 🎯 SUMMARY TABLE

| Aspect | Courses | Marketplace |
|--------|---------|-------------|
| Created by | Admin | Sellers |
| Revenue split | 100% Platform | 80% Seller, 20% Platform |
| Verification | Admin review | KYC + Content review |
| Product type | Videos, Quizzes | Files, Templates, etc |
| Pricing control | Admin | Seller |
| Admin involvement | High | Moderation + Payouts |
| User table | enrollment | order, ProductPurchase |
| Payment method | Stripe | Stripe |
| Commission table | N/A | SellerPayout |
| Analytics | Course stats | Seller dashboard |

---

**All systems integrated and ready for full marketplace operations!** 🚀
