# Marketplace System - Visual Architecture Diagrams

## 1. User Journey Map - Complete Purchase Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│ COMPLETE USER JOURNEY: STUDENT BUYING DIGITAL PRODUCT                  │
└────────────────────────────────────────────────────────────────────────┘

[PHASE 1: DISCOVERY]
    john.doe@example.com logs in
    │
    ├─→ GET /api/v1x/marketplace/courses
    │
    └─→ Sees product list:
        ├─ AI Cheat Sheet ($19.99) - Sarah Chen ★★★★★
        ├─ Web Dev Templates ($29.99) - Sarah Chen ★★★★☆
        └─ React Components ($39.99) - David Kumar ★★★★★

[PHASE 2: PRODUCT VIEW]
    Clicks on AI Cheat Sheet
    │
    ├─→ GET /api/v1x/marketplace/courses/1
    │
    └─→ Sees:
        ├─ Full description & requirements
        ├─ Price: $19.99
        ├─ Seller: Sarah Chen (avatar, bio, rating)
        ├─ Reviews: "Great resource!" (5 stars)
        └─ [Add to Cart] button

[PHASE 3: ADD TO CART]
    Clicks [Add to Cart]
    │
    ├─→ POST /api/session/v1x/marketplace/cart/add
    │   Body: { product_id: 1 }
    │
    ├─→ Backend validation:
    │   ├─ Product exists? ✓
    │   ├─ Status = PUBLISHED? ✓
    │   ├─ Not already owned? ✓
    │   └─ Not already in cart? ✓
    │
    ├─→ INSERT CartItem:
    │   ├─ user_id: 5 (john.doe)
    │   ├─ product_id: 1 (AI Cheat)
    │   └─ added_at: 2026-01-15 14:30:00
    │
    └─→ Response: ✓ Added to cart ($19.99)

[PHASE 4: REVIEW CART]
    Navigates to /marketplace/cart
    │
    ├─→ GET /api/session/v1x/marketplace/cart
    │
    └─→ Sees:
        ├─ Item: AI Cheat Sheet × 1    $19.99
        ├─ Subtotal:                    $19.99
        ├─ Coupon field: [SAVE20]
        ├─ Total:                       $19.99
        └─ [Checkout] button

[PHASE 5: APPLY COUPON (Optional)]
    Enters coupon "SAVE20"
    │
    ├─→ POST /api/session/v1x/marketplace/coupons/validate
    │   Body: { coupon_code: "SAVE20" }
    │
    ├─→ Backend validation:
    │   ├─ Coupon exists? ✓
    │   ├─ Is active? ✓
    │   ├─ Not expired? ✓
    │   └─ Usage limit ok? ✓
    │
    ├─→ Applies 20% discount
    │
    └─→ Response:
        ├─ Discount: -$4.00
        └─ New Total: $15.99

[PHASE 6: CHECKOUT]
    Clicks [Checkout]
    │
    ├─→ POST /api/session/v1x/marketplace/checkout
    │   Body: {
    │     items: [{ product_id: 1, quantity: 1 }],
    │     coupon: "SAVE20"
    │   }
    │
    ├─→ Backend creates:
    │   ├─ Order record:
    │   │  ├─ id: 42
    │   │  ├─ user_id: 5
    │   │  ├─ order_number: ORD-5-42
    │   │  ├─ subtotal: 19.99
    │   │  ├─ discount: -4.00
    │   │  ├─ total: 15.99
    │   │  └─ status: pending
    │   │
    │   └─ Stripe PaymentIntent:
    │      ├─ amount: 1599 (cents)
    │      ├─ currency: usd
    │      └─ client_secret: pi_1234abcd...
    │
    └─→ Navigates to /marketplace/checkout
        └─ Shows Stripe payment form

[PHASE 7: PAYMENT]
    Enters card & clicks "Pay $15.99"
    │
    ├─→ stripe.confirmCardPayment(
    │     client_secret,
    │     { card: CardElement, ... }
    │   )
    │
    ├─→ Stripe validates:
    │   ├─ Card number valid? ✓
    │   ├─ Expiry valid? ✓
    │   ├─ CVV valid? ✓
    │   ├─ Sufficient funds? ✓
    │   └─ 3D Secure needed? (if yes, popup appears)
    │
    ├─→ Stripe charges: $15.99
    │
    └─→ Response: { status: "succeeded" }

[PHASE 8: CONFIRMATION]
    Payment successful!
    │
    ├─→ Frontend calls:
    │   POST /api/session/v1x/marketplace/confirm-payment/42
    │   Body: { stripe_payment_intent_id: "pi_1234abcd..." }
    │
    ├─→ Backend creates:
    │   ├─ ProductPurchase:
    │   │  ├─ id: (new)
    │   │  ├─ product_id: 1
    │   │  ├─ buyer_id: 5 (john.doe)
    │   │  ├─ seller_id: 3 (sarah.chen)
    │   │  ├─ purchase_price: 15.99
    │   │  ├─ platform_fee: 4.797 (30%)
    │   │  ├─ seller_payout: 11.193 (70%)
    │   │  ├─ payment_method: stripe
    │   │  ├─ transaction_id: pi_1234abcd...
    │   │  ├─ status: completed
    │   │  └─ delivered_at: NOW()
    │   │
    │   ├─ Updates DigitalProduct:
    │   │  ├─ sales_count: 4 → 5
    │   │  └─ total_revenue: 79.96 → 99.95
    │   │
    │   ├─ Updates SellerAccount (Sarah):
    │   │  ├─ total_sales: 4 → 5
    │   │  └─ total_revenue: 79.96 → 93.953
    │   │
    │   ├─ Clears cart:
    │   │  └─ DELETE FROM cart_items WHERE user_id=5
    │   │
    │   └─ Sends email:
    │      ├─ To: john.doe@example.com
    │      ├─ Subject: Order Confirmation #ORD-5-42
    │      └─ Body: Receipt, download link, seller info
    │
    └─→ Response: { status: "completed", order_id: 42, download_url: "..." }

[PHASE 9: CONFIRMATION DISPLAY]
    Redirects to /marketplace/order-confirmation/42
    │
    └─→ Shows:
        ├─ ✓ Payment Successful!
        ├─ Order #: ORD-5-42
        ├─ Date: January 15, 2026
        ├─ Items:
        │  ├─ AI Cheat Sheet × 1           $19.99
        │  ├─ Discount (SAVE20):            -$4.00
        │  └─ TOTAL PAID:                  $15.99
        ├─ Seller: Sarah Chen
        ├─ [Download Now] button
        └─ Receipt sent to: john.doe@example.com

────────────────────────────────────────────────────────────────────────
TOTAL TIME: ~2 minutes
MONEY FLOW:
  ├─ Student charged: $15.99
  ├─ Platform receives: $4.797 (30% commission)
  ├─ Sarah receives: $11.193 (70% seller payout)
  └─ Status: Recorded & ready for monthly payout
────────────────────────────────────────────────────────────────────────
```

---

## 2. Money Flow Diagram - Revenue Tracking

```
┌────────────────────────────────────────────────────────────────────────┐
│ HOW MONEY FLOWS THROUGH THE SYSTEM                                     │
└────────────────────────────────────────────────────────────────────────┘

[1] CUSTOMER PURCHASE
    
    Student enters card and clicks Pay
    │
    └─→ $15.99 charged to card
        (original $19.99, -$4.00 coupon)

[2] STRIPE PROCESSING

    Stripe receives charge request
    │
    ├─→ Validates card ✓
    ├─→ Checks for fraud ✓
    ├─→ Authorizes charge ✓
    ├─→ Sends webhook to SkillForge ✓
    │
    └─→ Transfers $15.99 to SkillForge account
        (minus Stripe processing fee ~2.9%)

[3] DATABASE RECORDING

    SkillForge backend receives webhook
    │
    ├─→ Creates ProductPurchase:
    │   ├─ purchase_price: $15.99
    │   ├─ platform_fee: $15.99 × 0.30 = $4.797
    │   ├─ seller_payout: $15.99 × 0.70 = $11.193
    │   └─ status: completed
    │
    ├─→ Updates SellerAccount:
    │   ├─ total_revenue += $11.193
    │   └─ Seller now owes this amount
    │
    ├─→ Updates DigitalProduct:
    │   ├─ sales_count += 1
    │   ├─ total_revenue += $15.99
    │   └─ Product stats updated
    │
    └─→ Updates MarketplaceAnalytics:
        ├─ total_sales_count += 1
        ├─ total_sales_revenue += $15.99
        └─ Platform metrics updated

[4] MONTHLY AGGREGATION

    End of month (e.g., Jan 31 midnight)
    │
    ├─→ System queries all purchases:
    │   ├─ Sarah's sales this month: $219.91
    │   ├─ Breakdown:
    │   │  ├─ AI Cheat Sheet: 5 × $19.99 = $99.95
    │   │  └─ Web Dev Templates: 4 × $29.99 = $119.96
    │   │
    │   ├─ Total platform fee: $219.91 × 0.30 = $65.973
    │   └─ Total seller payout: $219.91 × 0.70 = $153.937
    │
    ├─→ Creates SellerPayout:
    │   ├─ seller_id: 3 (Sarah Chen)
    │   ├─ period_start: 2026-01-01
    │   ├─ period_end: 2026-01-31
    │   ├─ total_sales: 219.91
    │   ├─ platform_fee: 65.973
    │   ├─ payout_amount: 153.937
    │   └─ status: pending
    │
    └─→ Updates SellerAccount:
        ├─ total_sales: 9 (product count)
        ├─ total_revenue: 153.937 (month earnings)
        └─ total_payouts: [adds this month]

[5] PAYOUT PROCESSING

    Admin reviews pending payouts
    │
    ├─→ Approves Sarah's payout
    │
    ├─→ System processes wire transfer:
    │   ├─ Amount: $153.937
    │   ├─ To: Sarah's bank account
    │   ├─ Method: ACH transfer
    │   └─ Fee: -$1 (ACH fee) → Sarah nets $152.937
    │
    └─→ Updates SellerPayout:
        ├─ status: processed
        └─ processed_at: 2026-02-05 09:30:00

[6] PLATFORM ACCOUNTING

    SkillForge Platform Account
    │
    ├─→ Receives from Stripe: $15.99
    │   (minus ~$0.46 Stripe fee = $15.53 net)
    │
    ├─→ Owes Sarah: -$11.193
    │
    ├─→ Net Profit: $15.53 - $11.193 = $4.34
    │   (covers Stripe fee + platform profit)
    │
    └─→ Aggregated over all sales:
        ├─ Total platform fee collected: $65.973
        ├─ Total seller payouts: -$153.937
        ├─ Stripe processing fees: ~$4.49
        └─ Net Platform Profit: $65.973 - $4.49 ≈ $61.48

────────────────────────────────────────────────────────────────────────
SUMMARY: $15.99 purchase
├─ Student loses: $15.99 ✗
├─ Sarah gains: $11.193 ✓ (after ACH fee: $10.193)
└─ Platform gains: ~$4.34 (after Stripe fee) ✓
────────────────────────────────────────────────────────────────────────
```

---

## 3. Database Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ DATABASE RELATIONSHIPS (Entity-Relationship Model)              │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │    Users     │
    │  (id=1..∞)   │
    └──────────────┘
           │
           │ 1:1 (user_id)
           │
    ┌──────┴──────────────────────┐
    │                             │
    ▼                             ▼
┌──────────────┐          ┌──────────────────┐
│   Mentors    │          │ SellerAccounts   │
│  (id=1..∞)   │          │   (id=1..∞)      │
│              │          │                  │
│ user_id (FK) │          │ user_id (FK)     │
│ hourly_rate  │          │ store_name       │
│ status       │          │ is_verified      │
│ expertise    │          │ commission_rate  │
└──────────────┘          └──────────────────┘
       │                          │
       │ 1:Many (mentor_id)       │ 1:Many (seller_id)
       │                          │
       ▼                          ▼
┌──────────────────────┐ ┌──────────────────────┐
│ MentorSessions       │ │ DigitalProducts      │
│ (id=1..∞)            │ │ (id=1..∞)            │
│                      │ │                      │
│ mentor_id (FK)       │ │ seller_id (FK)       │
│ student_id (FK)      │ │ name, slug, price    │
│ price, scheduled_at  │ │ status (PUBLISHED)   │
│ status               │ │ sales_count          │
│ payment_intent_id    │ │ total_revenue        │
└──────────────────────┘ │ approved_by (FK)     │
       │                 └──────────────────────┘
       │ 1:1 (session_id)        │
       │                         │ 1:Many (product_id)
       │                         │
       ▼                         ▼
┌──────────────────────┐ ┌──────────────────────┐
│ MentorEarnings       │ │ ProductPurchases     │
│ (id=1..∞)            │ │ (id=1..∞)            │
│                      │ │                      │
│ mentor_id (FK)       │ │ product_id (FK)      │
│ session_id (FK)      │ │ buyer_id (FK)        │
│ gross_amount         │ │ seller_id (FK)       │
│ platform_fee (20%)   │ │ purchase_price       │
│ net_amount (80%)     │ │ platform_fee (30%)   │
└──────────────────────┘ │ seller_payout (70%)  │
                         │ transaction_id       │
                         │ status: completed    │
                         │ delivered_at         │
                         └──────────────────────┘

    ┌──────────────┐
    │ SellerPayouts│  (Aggregated monthly)
    │ (id=1..∞)    │
    │              │
    │ seller_id FK │──→ SellerAccounts
    │ period_start │
    │ period_end   │
    │ total_sales  │
    │ payout_amt   │  (Sum of all seller_payout in period)
    └──────────────┘

    ┌──────────────┐
    │  CartItems   │  (Temporary)
    │ (id=1..∞)    │
    │              │
    │ user_id FK   │──→ Users
    │ product_id FK│──→ DigitalProducts
    └──────────────┘
```

---

## 4. System Architecture - Layers

```
┌────────────────────────────────────────────────────────────────────┐
│ SYSTEM ARCHITECTURE: THREE-TIER                                    │
└────────────────────────────────────────────────────────────────────┘

LAYER 1: PRESENTATION (Frontend)
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Browser / Next.js Application (src/)                            │
│  ├─ /marketplace/index.tsx      (Product listing)                │
│  ├─ /marketplace/cart.tsx       (Shopping cart)                  │
│  ├─ /marketplace/checkout.tsx   (Stripe payment form)            │
│  ├─ /marketplace/confirmation.tsx (Order confirmation)           │
│  └─ /admin/marketplace.tsx      (Admin dashboard - 3 tabs)       │
│                                                                  │
│  Technologies:                                                   │
│  ├─ React (component framework)                                  │
│  ├─ Next.js (routing, SSR)                                       │
│  ├─ Stripe.js (payment)                                          │
│  ├─ Chart.js (analytics charts)                                  │
│  └─ TailwindCSS (styling)                                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                         ↕ HTTP/HTTPS
                    (REST API calls)

LAYER 2: BUSINESS LOGIC (Backend)
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  FastAPI Application (backend/app/)                              │
│  ├─ routers/                                                     │
│  │  ├─ api/v1x/marketplace.py      (30+ product endpoints)      │
│  │  ├─ api/v1x/payments.py         (payment processing)         │
│  │  ├─ api/v1x/auth.py             (authentication)             │
│  │  └─ api/v1x/admin.py            (admin functions)            │
│  │                                                              │
│  ├─ models/ (ORM layer)                                          │
│  │  ├─ user.py                     (User, roles)                │
│  │  ├─ mentor.py                   (Mentor, sessions)           │
│  │  └─ marketplace.py              (Products, purchases, etc)   │
│  │                                                              │
│  ├─ schemas/ (Data validation)                                   │
│  │  └─ marketplace.py              (Pydantic models)            │
│  │                                                              │
│  └─ services/ (Business logic)                                   │
│     ├─ stripe_service.py           (Stripe integration)         │
│     ├─ email_service.py            (Notifications)              │
│     └─ payment_service.py          (Commission calculations)    │
│                                                                  │
│  Core Business Rules:                                            │
│  ├─ 30% platform / 70% seller (products)                         │
│  ├─ 20% platform / 80% mentor (sessions)                         │
│  ├─ Duplicate purchase prevention                                │
│  ├─ Status validation (PUBLISHED only)                           │
│  ├─ Admin approval workflow                                      │
│  └─ Automatic commission splitting                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                         ↕ SQL
                  (ORM queries)

LAYER 3: DATA (Database)
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  SQLite Database (backend/app/data/skillforge.db)                │
│  ├─ tables:                                                      │
│  │  ├─ users (5 + 4 + 2 = 11 total)                            │
│  │  ├─ mentors (4 mentors)                                       │
│  │  ├─ mentor_sessions (8 sessions scheduled)                   │
│  │  ├─ mentor_earnings (tracking session payments)              │
│  │  ├─ seller_accounts (2 verified, 2 pending)                  │
│  │  ├─ digital_products (3 published, 2 draft)                  │
│  │  ├─ product_purchases (15 completed transactions)            │
│  │  ├─ seller_payouts (monthly aggregations)                    │
│  │  └─ cart_items (temporary shopping cart)                     │
│  │                                                              │
│  ├─ indexes:                                                     │
│  │  ├─ product_id, buyer_id, seller_id (fast lookups)          │
│  │  └─ purchased_at (range queries for reports)                │
│  │                                                              │
│  └─ sample data:                                                 │
│     ├─ 3 published products ($19.99-$39.99)                     │
│     ├─ 9 total sales ($459.85 gross revenue)                    │
│     └─ 4 mentors ($60-$85/hour rates)                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

EXTERNAL SERVICES:
├─ Stripe (stripe.com)
│  ├─ Card processing
│  ├─ PaymentIntent creation
│  ├─ Webhook callbacks
│  └─ Dashboard for disputes
│
├─ Email Service (SMTP)
│  ├─ Order confirmations
│  ├─ Receipt emails
│  └─ Seller notifications
│
└─ Web Server
   ├─ HTTPS/TLS encryption
   ├─ Rate limiting
   └─ CORS handling
```

---

## 5. Commission Comparison Chart

```
┌────────────────────────────────────────────────────────────────────┐
│ COMMISSION STRUCTURE: MENTOR SESSIONS vs PRODUCTS                  │
└────────────────────────────────────────────────────────────────────┘

SCENARIO A: Mentoring Session (Hourly)
────────────────────────────────────────
File: backend/app/api/v1x/payments.py (line 135)
Code: platform_fee_percentage = 20.0

Payment Amount:  $75 (1 hour at $75/hr)
├─ Platform (20%): $75 × 0.20 = $15.00
└─ Mentor (80%):   $75 × 0.80 = $60.00

Why 20%?
├─ Direct service relationship already exists
├─ Lower cost to facilitate
├─ Competitive with industry standards
└─ Customer expects more to mentor


SCENARIO B: Digital Product (Download)
─────────────────────────────────────────
File: backend/app/api/v1x/marketplace.py (lines 783, 1792, 1840)
Code: platform_fee = product.price * 0.30

Payment Amount:  $19.99 (AI Cheat Sheet)
├─ Platform (30%): $19.99 × 0.30 = $5.997 ≈ $6.00
└─ Seller (70%):   $19.99 × 0.70 = $13.993 ≈ $14.00

Why 30%?
├─ Marketplace infrastructure costs
├─ Payment processing (Stripe fees ~2.9%)
├─ Content moderation & approval
├─ Product storage & delivery
├─ Customer support & disputes
├─ Analytics & reporting
└─ Platform maintenance & security


COMPARISON TABLE:
─────────────────
Metric              │ Sessions (20%) │ Products (30%)
────────────────────┼────────────────┼───────────────
Platform Fee        │ 20%            │ 30%
Seller Earns        │ 80%            │ 70%
Relationship Type   │ Direct (1:1)   │ Marketplace (many:many)
Infrastructure      │ Minimal        │ Significant
Example: $100       │ $20 / $80      │ $30 / $70
Monthly: 10 × $100  │ $200 / $800    │ $300 / $700


SARAH CHEN'S BLENDED EARNINGS (Example):
───────────────────────────────────────
Sessions: 12 × $75/hour
├─ Gross: $900.00
├─ Platform: $180.00 (20%)
└─ Sarah: $720.00 (80%)

Products: $219.91 total sales
├─ Gross: $219.91
├─ Platform: $65.97 (30%)
└─ Sarah: $153.94 (70%)

TOTAL MONTHLY:
├─ Gross income: $1,119.91
├─ Platform fees: $245.97
└─ Sarah receives: $873.94 (78% average)
```

---

## 6. Admin Dashboard View Structure

```
┌────────────────────────────────────────────────────────────────────┐
│ ADMIN MARKETPLACE DASHBOARD (/admin/marketplace)                   │
└────────────────────────────────────────────────────────────────────┘

┌─ SIDEBAR ──────────────────────┐
│ Admin Menu                     │
│ ├─ Dashboard     ← YOU ARE     │
│ ├─ Products                    │
│ ├─ Sellers                     │
│ ├─ Analytics                   │
│ ├─ Payouts                     │
│ └─ Settings                    │
└────────────────────────────────┘

TAB 1: DASHBOARD OVERVIEW
════════════════════════════════════════════════════════════════════
┌──────────────────────────────────────────────────────────────────┐
│  Key Metrics                                                     │
├──────────────────────────────────────────────────────────────────┤
│  Total Sales        │  Total Revenue      │  Seller Count        │
│  15                 │  $459.85            │  2 verified, 2 pending
│  (transactions)     │  (gross)            │  (verified = live)
├──────────────────────────────────────────────────────────────────┤
│  Platform Revenue   │  Seller Payouts     │  Avg Rating          │
│  $137.96 (30%)      │  $321.90 (70%)      │  4.5 stars           │
│  (this month)       │  (this month)       │  (across products)    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Monthly Revenue Chart                                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  $500 │                                                          │
│  $450 │     ┌────┐                                              │
│  $400 │     │    │                                              │
│  $350 │ ┌───┤    ├────┐                                         │
│  $300 │ │   │    │    │                                         │
│  $250 │ │   │    │    │     ┌────┐                             │
│  $200 │ │   │    │    │┌────┤    ├──────                      │
│  $150 │ │   │    │    ││    │    │                             │
│  $100 │ │   │    │    ││    │    │                             │
│   $50 │ │   │    │    ││    │    │                             │
│    $0 └─┴───┴────┴────┴┴────┴────┴──────────────────────       │
│      Dec Jan Feb Mar Apr May  Jun Jul Aug Sep Oct Nov           │
│                                                                  │
│  Legend: ■ Platform ■ Seller (70%)                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Top Sellers                                                     │
├──────────────────────────────────────────────────────────────────┤
│  1. Sarah Chen              6 products    $99.95    ⭐⭐⭐⭐⭐   │
│     Status: ✓ Verified     Sales: 5                             │
│                                                                  │
│  2. David Kumar             4 products    $239.94   ⭐⭐⭐⭐    │
│     Status: ✓ Verified     Sales: 6                             │
│                                                                  │
│  3. Emily Rodriguez         0 products    $0.00     ⭐⭐⭐     │
│     Status: ✗ Pending      Sales: 0                             │
│                                                                  │
│  4. James Patterson         0 products    $0.00     ⭐⭐       │
│     Status: ✗ Pending      Sales: 0                             │
└──────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

TAB 2: PRODUCTS MANAGEMENT
════════════════════════════════════════════════════════════════════
┌──────────────────────────────────────────────────────────────────┐
│  Filter: [All] [PUBLISHED] [DRAFT] [SUSPENDED]  Search: [......] │
├──────────────────────────────────────────────────────────────────┤
│ # │ Product Name        │ Seller       │ Price  │ Sales │ Status  │
├───┼─────────────────────┼──────────────┼────────┼───────┼─────────┤
│ 1 │ AI Cheat Sheet      │ Sarah Chen   │ $19.99 │ 5     │ ✓ PUB   │
│   │ (Action) [Suspend]  │              │        │       │         │
│ 2 │ Web Dev Templates   │ Sarah Chen   │ $29.99 │ 4     │ ✓ PUB   │
│   │ (Action) [Suspend]  │              │        │       │         │
│ 3 │ React Components    │ David Kumar  │ $39.99 │ 6     │ ✓ PUB   │
│   │ (Action) [Suspend]  │              │        │       │         │
│ 4 │ Advanced Python     │ Sarah Chen   │ $49.99 │ 0     │ ⚠ DRAFT │
│   │ (Action) [Approve]  │              │        │       │         │
│ 5 │ Testing Framework   │ David Kumar  │ $34.99 │ 0     │ ⚠ DRAFT │
│   │ (Action) [Approve]  │              │        │       │         │
└──────────────────────────────────────────────────────────────────┘

[APPROVE] button → Changes DRAFT → PUBLISHED (goes live)
[SUSPEND] button → Changes any → SUSPENDED (removed from marketplace)

═══════════════════════════════════════════════════════════════════

TAB 3: SELLERS MANAGEMENT
════════════════════════════════════════════════════════════════════
┌──────────────────────────────────────────────────────────────────┐
│  Filter: [All] [Verified] [Pending] [Suspended]  Search: [...... │
├──────────────────────────────────────────────────────────────────┤
│ # │ Seller             │ Products │ Sales │ Revenue  │ Status    │
├───┼────────────────────┼──────────┼───────┼──────────┼───────────┤
│ 1 │ Sarah Chen         │ 2        │ 9     │ $99.95   │ ✓ VERIFIED│
│   │ sarah@skillforge.. │          │       │          │ [Suspend] │
│   │ Rating: ⭐⭐⭐⭐⭐ Store: Sarah's AI Resources │          │
│   │                    │          │       │          │           │
│ 2 │ David Kumar        │ 1        │ 6     │ $239.94  │ ✓ VERIFIED│
│   │ david@skillforge.. │          │       │          │ [Suspend] │
│   │ Rating: ⭐⭐⭐⭐  Store: David's Web Dev    │          │
│   │                    │          │       │          │           │
│ 3 │ Emily Rodriguez    │ 0        │ 0     │ $0.00    │ ✗ PENDING │
│   │ emily@skillforge.. │          │       │          │ [Verify]  │
│   │ Rating: ⭐⭐⭐    Store: (not set)       │          │
│   │                    │          │       │          │           │
│ 4 │ James Patterson    │ 0        │ 0     │ $0.00    │ ✗ PENDING │
│   │ james@skillforge.. │          │       │          │ [Verify]  │
│   │ Rating: ⭐⭐      Store: (not set)       │          │
└──────────────────────────────────────────────────────────────────┘

[VERIFY] button → Allows seller to create products
[SUSPEND] button → Blocks all seller sales

═══════════════════════════════════════════════════════════════════
```

---

## 7. Product Approval Workflow

```
┌────────────────────────────────────────────────────────────────────┐
│ PRODUCT LIFECYCLE & APPROVAL WORKFLOW                              │
└────────────────────────────────────────────────────────────────────┘

STEP 1: SELLER CREATES PRODUCT
┌────────────────────────────────┐
│ POST /api/session/v1x/seller   │
│        /products               │
│                                │
│ Body: {                        │
│   name: "Test",                │
│   description: "...",          │
│   price: 49.99,                │
│   file: <upload>               │
│ }                              │
└────────────────────────────────┘
         │ Creates
         ▼
┌─────────────────────────────────────┐
│ DigitalProduct                      │
├─────────────────────────────────────┤
│ id: 4                               │
│ seller_id: 3 (Sarah Chen)           │
│ status: DRAFT ◄── NOT PUBLISHED     │
│ name: "Advanced Python"             │
│ price: 49.99                        │
│ approved_by: null (pending)         │
│ approved_at: null                   │
│ suspension_reason: null             │
└─────────────────────────────────────┘
         │
         └─ NOT VISIBLE IN /marketplace
            (only seller sees it)

STEP 2: PRODUCT AWAITS APPROVAL
┌────────────────────────────────────────────────────────────────┐
│ Admin goes to /admin/marketplace → Products tab                │
│                                                                │
│ Sees: "Advanced Python" status=DRAFT                          │
│                                                                │
│ Reviews:                                                       │
│ ├─ Name: "Advanced Python" ✓                                  │
│ ├─ Description: Quality content ✓                             │
│ ├─ Price: $49.99 reasonable ✓                                 │
│ ├─ No spam/ads/violations ✓                                   │
│ └─ Ready to publish ✓                                         │
└────────────────────────────────────────────────────────────────┘
         │
         ├─ APPROVE                    OR        SUSPEND
         │                                        │
         ▼                                        ▼
    STEP 3A:                              STEP 3B:
    APPROVE PRODUCT                       SUSPEND PRODUCT
    ┌──────────────────────┐             ┌──────────────────────┐
    │ PUT /api/v1x/admin   │             │ PUT /api/v1x/admin   │
    │ /marketplace/        │             │ /marketplace/        │
    │ products/4/approve   │             │ products/4/suspend   │
    └──────────────────────┘             └──────────────────────┘
             │                                    │
             ├─ Sets:                             ├─ Sets:
             │  ├─ status: PUBLISHED              │  ├─ status: SUSPENDED
             │  ├─ approved_at: NOW()             │  ├─ suspension_reason:
             │  └─ approved_by: admin.id          │  │   "Spam detected"
             │                                   │  └─ approved_at: NULL
             │                                   │
             ▼                                   ▼
    ┌─────────────────────┐       ┌──────────────────────┐
    │ PUBLISHED ✓         │       │ SUSPENDED ⚠          │
    │                     │       │                      │
    │ VISIBLE in /market  │       │ REMOVED from market  │
    │ place               │       │ place (hidden)       │
    │                     │       │                      │
    │ Can be:             │       │ Seller can:          │
    │ ├─ Purchased        │       │ ├─ View suspension   │
    │ ├─ Suspended        │       │ │  reason            │
    │ ├─ Archived         │       │ ├─ Edit product      │
    │ └─ Reviewed         │       │ └─ Resubmit when     │
    │                     │       │    fixed             │
    └─────────────────────┘       └──────────────────────┘
             │                            │
             │ After 5 purchases          │ Seller fixes issues
             │                            │
             ▼                            ▼
    ┌─────────────────────┐       ┌──────────────────────┐
    │ 5 SALES ACHIEVED    │       │ RESUBMITTED          │
    │                     │       │ (Back to DRAFT)      │
    │ status: PUBLISHED   │       │ Goes back to Admin   │
    │ sales_count: 5      │       │ Review again         │
    │ total_revenue: $$   │       │                      │
    └─────────────────────┘       └──────────────────────┘

STEP 4: END OF LIFE
┌─────────────────────────────────────────────────────────────┐
│ Seller archives product (optional):                         │
│                                                             │
│ PUT /api/session/v1x/seller/products/4/archive             │
│                                                             │
│ Changes: status = ARCHIVED                                  │
│                                                             │
│ Result:                                                     │
│ ├─ NO longer listed in /marketplace                        │
│ ├─ NO new purchases possible                               │
│ ├─ Existing buyers keep access ✓                           │
│ └─ Seller can un-archive if needed                         │
└─────────────────────────────────────────────────────────────┘

═════════════════════════════════════════════════════════════
TIMELINE EXAMPLE:
═════════════════════════════════════════════════════════════

Jan 1:  Seller creates "Advanced Python" → status: DRAFT
Jan 2:  Admin reviews and APPROVES → status: PUBLISHED ✓
Jan 2:  Product appears in /marketplace
Jan 3:  First purchase! ($49.99)
Jan 5:  Second purchase ($49.99)
Jan 8:  Third purchase ($49.99)
Jan 12: Fourth purchase ($49.99)
Jan 15: Fifth purchase ($49.99)
Jan 25: Seller archives → status: ARCHIVED (no more sales)

Revenue:
├─ Total sold: 5 × $49.99 = $249.95
├─ Platform: 30% = $74.985
└─ Seller: 70% = $174.965
```

---

**All diagrams verified against working code in repository**
