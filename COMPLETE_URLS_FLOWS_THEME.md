# COMPLETE URLS, DATA FLOWS & THEME - FINAL REFERENCE

## 📊 ARCHITECTURE OVERVIEW

```
Frontend (Next.js)           Backend (FastAPI)          Database (SQLite)
├── Public Pages             ├── v1 Routes              ├── Users (11)
├── Auth Pages               ├── v1x Routes (DB-backed) ├── Mentors (4)
├── Marketplace              └── API Endpoints          ├── Products (3)
├── Mentor Booking           └── 40+ Models             └── Sessions (8)
├── Seller Dashboard
├── Mentor Dashboard
└── Admin Dashboard

DATA FLOW:
User Login → Browse Mentors → Check Availability → Book Session → 
Mentor Confirms → Payment → Session Recorded → Feedback → Rating Update

Admin Flow:
Dashboard Metrics ← Admin Analytics
Product Approval ← Pending Products
Seller Verification ← All Sellers
Payout Processing ← Payout Requests
```

---

## 🌐 COMPLETE FRONTEND URLS (90+ ROUTES)

### A. PUBLIC PAGES (8 URLs)
```
GET /                          Home page - hero, trending content
GET /trending                  Trending content, courses, mentors
GET /teams                     Organizations & teams
GET /subscribe                 Subscription plans & pricing
GET /terms                     Terms of service
GET /status                    System status & uptime
GET /ui-showcase               Component showcase (debug)
GET /courses                   Course listing & search (public)
```

### B. AUTHENTICATION (3 URLs)
```
GET  /login                    Login form
GET  /signup                   Registration form
GET  /unauthorized             Access denied page (401/403)
```

### C. MARKETPLACE - BUYER (11 URLs)
```
GET  /marketplace              Product listing, search, filters
GET  /marketplace/search?q=    Search results
GET  /marketplace/[id]         Product detail page
GET  /marketplace/cart         Shopping cart
GET  /marketplace/checkout     Payment form (requires auth)
POST /marketplace/checkout     Process payment
GET  /marketplace/orders       Order history (requires auth)
GET  /marketplace/order-[id]   Order detail
GET  /marketplace/order-[id]/invoice Order invoice/receipt
```

### D. MENTOR BOOKING - STUDENT (8 URLs) ⭐ NEW
```
GET  /mentors                  Browse all mentors (public)
GET  /mentors?expertise=python Filter by expertise (public)
GET  /mentors?rate_min=50&rate_max=100 Filter by rate (public)
GET  /mentors/[id]             Mentor profile (public)
GET  /mentors/[id]/reviews     Mentor reviews (public)
GET  /mentors/[id]/availability Check availability (public)
GET  /mentors/[id]/book        Booking form (requires auth)
POST /mentors/[id]/book        Submit booking (requires auth)
```

### E. SELLER/MENTOR FEATURES (15 URLs) ⭐ ENHANCED
```
GET  /marketplace/seller                    Seller dashboard (requires role: MENTOR)
GET  /marketplace/seller/products           My products list
POST /marketplace/seller/products           Create product form
GET  /marketplace/seller/products/[id]/edit Edit product form
POST /marketplace/seller/products/[id]      Update product
GET  /marketplace/seller/orders             View sales & orders
GET  /marketplace/seller/analytics          Sales analytics & charts
GET  /marketplace/seller/earnings           Earnings summary
GET  /marketplace/seller/payouts            Payout history
GET  /marketplace/seller/reviews            Customer reviews
GET  /marketplace/seller/customers          Customer list & details
POST /marketplace/seller/request-payout     Request payout
GET  /marketplace/seller/settings           Seller settings
POST /marketplace/seller/bank-details       Add bank account
```

### F. MENTOR DASHBOARD (8 URLs)
```
GET  /mentors/dashboard                     Mentor overview
GET  /mentors/dashboard/sessions            My sessions
GET  /mentors/dashboard/sessions/[id]       Session detail
POST /mentors/dashboard/sessions/[id]/confirm Confirm session
GET  /mentors/dashboard/earnings            Earnings summary
GET  /mentors/dashboard/analytics           Analytics
GET  /mentors/dashboard/availability        Manage availability
GET  /mentors/dashboard/profile             Edit profile
```

### G. STUDENT SESSIONS (3 URLs)
```
GET  /dashboard/mentor-sessions             My booked sessions
GET  /dashboard/mentor-sessions/[id]        Session detail
POST /dashboard/mentor-sessions/[id]/feedback Leave feedback
```

### H. USER PROFILE & SETTINGS (6 URLs)
```
GET  /profile                  My profile
GET  /profile/edit             Edit profile
POST /profile/edit             Update profile
GET  /settings                 Account settings
GET  /settings/notifications   Notification preferences
GET  /users/[id]               View other user profile
```

### I. LEARNING & COURSES (8 URLs)
```
GET  /courses                  All courses
GET  /courses?difficulty=beginner Filter by difficulty
GET  /courses/[slug]           Course detail
GET  /courses/[slug]/lessons   Course content (requires purchase)
GET  /courses/[slug]/lessons/[id] Lesson detail
GET  /dashboard/learning       My learning dashboard
GET  /dashboard/learning/[id]  Course progress
POST /dashboard/learning/[id]/complete Mark complete
```

### J. COMMUNITY & SOCIAL (2 URLs)
```
GET  /community                Community forum
GET  /community/[id]           Discussion thread
```

### K. ADMIN PAGES (20+ URLs) ⭐ COMPLETE
```
GET  /admin                              Admin dashboard (requires role: ADMIN|SUPERADMIN)
GET  /admin/marketplace                  Marketplace management
GET  /admin/marketplace/products         All products list
GET  /admin/marketplace/products/[id]    Product detail
POST /admin/marketplace/products/[id]/approve Approve product
POST /admin/marketplace/products/[id]/reject Reject product
GET  /admin/marketplace/sellers          All sellers list
GET  /admin/marketplace/sellers/[id]     Seller detail
POST /admin/marketplace/sellers/[id]/verify Verify seller
POST /admin/marketplace/sellers/[id]/suspend Suspend seller
GET  /admin/marketplace/orders           All orders
GET  /admin/marketplace/orders/[id]      Order detail
GET  /admin/users                        User management
GET  /admin/users/[id]                   User detail
POST /admin/users/[id]/role              Change user role
POST /admin/users/[id]/suspend           Suspend user
GET  /admin/users/[id]/email             Send email
GET  /admin/analytics                    Analytics dashboard
GET  /admin/analytics/sales              Sales metrics
GET  /admin/analytics/revenue            Revenue report
GET  /admin/analytics/trending           Trending products
GET  /admin/analytics/users              User growth
GET  /admin/payouts                      Payout requests
GET  /admin/payouts/[id]                 Payout detail
POST /admin/payouts/[id]/approve         Approve payout
POST /admin/payouts/[id]/process         Process to bank
POST /admin/payouts/[id]/reject          Reject payout
GET  /admin/settings                     Admin settings
POST /admin/settings                     Update settings
GET  /admin/audit-logs                   Audit logs
GET  /admin/audit-logs?user=[id]         Filter logs by user
```

---

## 🔄 COMPLETE DATA FLOWS

### FLOW 1: Student Booking Mentor

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Browse Mentors                                            │
│    GET /api/v1x/mentors                                      │
│    ↓                                                          │
│    Returns: [mentor1, mentor2, mentor3, mentor4]             │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Filter Mentors (Optional)                                 │
│    GET /api/v1x/mentors?expertise=python&rate_max=80        │
│    ↓                                                          │
│    Returns: Filtered mentors matching criteria               │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. View Mentor Profile                                       │
│    GET /api/v1x/mentors/[mentorId]                          │
│    ↓                                                          │
│    Returns: Full profile, bio, expertise, rate, reviews      │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Check Availability                                        │
│    GET /api/v1x/mentors/[mentorId]/availability             │
│    ↓                                                          │
│    Returns: Available slots by date & time                   │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Book Session                                              │
│    POST /api/v1x/mentors/[mentorId]/book                    │
│    Body: { date, time, topic, duration_minutes, notes }     │
│    ↓                                                          │
│    Creates: MentorSession with status=PENDING_CONFIRMATION   │
│    Returns: Session details, meeting_url                     │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Wait for Confirmation                                     │
│    Status: PENDING_CONFIRMATION                              │
│    Mentor receives notification, reviews, and confirms       │
│    ↓                                                          │
│    Status changes to: CONFIRMED                              │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Join Session                                              │
│    GET /api/v1x/dashboard/mentor-sessions/[sessionId]       │
│    ↓                                                          │
│    Returns: meeting_url                                      │
│    Student clicks link to join video call                    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Leave Feedback                                            │
│    POST /api/v1x/dashboard/mentor-sessions/[id]/feedback     │
│    Body: { rating, comment, would_recommend }               │
│    ↓                                                          │
│    Creates: Review                                           │
│    Updates: Mentor.average_rating                            │
│    Status changes to: COMPLETED                              │
└─────────────────────────────────────────────────────────────┘
```

### FLOW 2: Seller Creating & Selling Product

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Login as Mentor/Seller                                    │
│    POST /api/v1/auth/login                                   │
│    ↓                                                          │
│    Returns: Token (with role: MENTOR)                        │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Access Seller Dashboard                                   │
│    GET /marketplace/seller                                   │
│    ↓                                                          │
│    Requires: Authorization header with token                 │
│    Returns: Dashboard with product list, earnings            │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Create Product                                            │
│    POST /api/v1x/seller/products                            │
│    Body: {                                                   │
│      name, description, price, product_type,                │
│      tags, cover_image, files                                │
│    }                                                          │
│    ↓                                                          │
│    Creates: DigitalProduct with status=DRAFT                │
│    Returns: Product ID                                       │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Submit for Review                                         │
│    PUT /api/v1x/seller/products/[id]/submit                │
│    ↓                                                          │
│    Status changes to: PENDING_APPROVAL                       │
│    Admin gets notification                                   │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Admin Reviews Product                                     │
│    GET /admin/marketplace/products/[id]                      │
│    ↓                                                          │
│    Admin checks: content, pricing, compliance                │
│    POST /admin/marketplace/products/[id]/approve             │
│    OR                                                        │
│    POST /admin/marketplace/products/[id]/reject              │
│    ↓                                                          │
│    If approved:  Status = PUBLISHED                          │
│    If rejected:  Status = REJECTED, Seller gets reason       │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Product Listed for Sale                                   │
│    GET /marketplace                                          │
│    ↓                                                          │
│    Product visible to all buyers                             │
│    Status: PUBLISHED                                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Buyer Purchases Product                                   │
│    POST /api/v1/marketplace/checkout                        │
│    ↓                                                          │
│    Creates: Order (status=pending)                           │
│    Returns: Payment URL                                      │
│    Buyer completes payment                                   │
│    ↓                                                          │
│    Order status changes to: COMPLETED                        │
│    Payment splits: 70% seller, 30% platform                 │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Seller Views Analytics                                    │
│    GET /api/v1x/seller/analytics/sales                      │
│    ↓                                                          │
│    Returns: Sales by date, top products, revenue trends      │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. Seller Views Earnings                                     │
│    GET /api/v1x/seller/analytics/earnings                   │
│    ↓                                                          │
│    Total earned: Sum of 70% splits from all orders           │
│    Pending: Amount waiting for payout approval               │
│    Paid out: Amount already received                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. Request Payout                                           │
│     POST /api/v1x/seller/request-payout                     │
│     Body: { amount }                                         │
│     ↓                                                         │
│     Creates: Payout with status=PENDING                      │
│     Admin gets notification                                  │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 11. Admin Approves Payout                                    │
│     GET /admin/payouts                                       │
│     ↓                                                         │
│     POST /admin/payouts/[id]/approve                         │
│     ↓                                                         │
│     Status: APPROVED                                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 12. Process Payout to Bank                                   │
│     POST /admin/payouts/[id]/process                         │
│     ↓                                                         │
│     Integrates with Stripe Connect                           │
│     Transfers funds to seller's bank account                 │
│     Status: PROCESSED                                        │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 13. Seller Sees Payout History                               │
│     GET /api/v1x/seller/payouts                             │
│     ↓                                                         │
│     Returns: List of all payouts with status                │
└─────────────────────────────────────────────────────────────┘
```

### FLOW 3: Admin Managing Platform

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Admin Dashboard                                           │
│    GET /admin                                                │
│    ↓                                                          │
│    Returns: Key metrics (revenue, users, products, payouts)  │
│    Shows: Pending approvals count                            │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Review Pending Products                                   │
│    GET /admin/marketplace/products?status=pending            │
│    ↓                                                          │
│    Returns: All products awaiting approval                   │
│    GET /admin/marketplace/products/[id]                      │
│    ↓                                                          │
│    Returns: Product details for review                       │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Approve or Reject Product                                 │
│    POST /admin/marketplace/products/[id]/approve             │
│    or                                                        │
│    POST /admin/marketplace/products/[id]/reject              │
│    ↓                                                          │
│    Product becomes PUBLISHED or REJECTED                     │
│    Seller notified                                           │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Manage Sellers                                            │
│    GET /admin/marketplace/sellers                            │
│    ↓                                                          │
│    Returns: All sellers with verification status             │
│    GET /admin/marketplace/sellers/[id]                       │
│    ↓                                                          │
│    Returns: Seller details, sales, status                    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Verify or Suspend Sellers                                 │
│    POST /admin/marketplace/sellers/[id]/verify               │
│    or                                                        │
│    POST /admin/marketplace/sellers/[id]/suspend              │
│    ↓                                                          │
│    Seller.is_verified updated                                │
│    Seller can/cannot create products                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Review Pending Payouts                                    │
│    GET /admin/payouts?status=pending                         │
│    ↓                                                          │
│    Returns: All payout requests                              │
│    GET /admin/payouts/[id]                                   │
│    ↓                                                          │
│    Returns: Payout details, seller info, amount              │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Approve Payout                                            │
│    POST /admin/payouts/[id]/approve                          │
│    ↓                                                          │
│    Status: APPROVED                                          │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Process to Bank                                           │
│    POST /admin/payouts/[id]/process                          │
│    ↓                                                          │
│    Integrates with Stripe Connect                            │
│    Status: PROCESSED                                         │
│    Seller receives funds                                     │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. View Platform Analytics                                   │
│    GET /admin/analytics                                      │
│    ↓                                                          │
│    Returns: Dashboard with 4 key charts                      │
│                                                              │
│    GET /admin/analytics/sales                                │
│    ↓ Returns: Total sales, orders, avg order value           │
│                                                              │
│    GET /admin/analytics/revenue                              │
│    ↓ Returns: Revenue trend (30% platform fee)               │
│                                                              │
│    GET /admin/analytics/trending                             │
│    ↓ Returns: Top 10 products by sales                       │
│                                                              │
│    GET /admin/analytics/users                                │
│    ↓ Returns: User growth, active users                      │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. Manage Users                                             │
│     GET /admin/users                                         │
│     ↓                                                         │
│     Returns: All platform users                              │
│     GET /admin/users/[id]                                    │
│     ↓                                                         │
│     Returns: User details, role, activity                    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 11. Change User Role                                         │
│     POST /admin/users/[id]/role                              │
│     ↓                                                         │
│     User role updated (USER → MENTOR, etc)                   │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 12. Suspend User                                             │
│     POST /admin/users/[id]/suspend                           │
│     ↓                                                         │
│     User cannot login or access platform                     │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 13. View Audit Logs                                          │
│     GET /admin/audit-logs                                    │
│     ↓                                                         │
│     Returns: All admin actions logged                        │
│     GET /admin/audit-logs?user=[id]                          │
│     ↓                                                         │
│     Filter logs by specific user                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 THEME & STYLING SYSTEM

### Color Palette

```
Primary Colors:
  --primary: #007BFF (Blue) - Main actions, links
  --success: #28A745 (Green) - Approved, completed, success
  --warning: #FFC107 (Amber) - Pending, needs review
  --danger: #DC3545 (Red) - Rejected, errors, suspensions
  --info: #17A2B8 (Cyan) - Informational messages

Neutral Colors:
  --light: #F8F9FA (Light Gray) - Backgrounds
  --dark: #212529 (Dark Gray) - Text, borders
  --white: #FFFFFF - Cards, surfaces
  --gray-300: #DEE2E6 - Borders
  --gray-600: #6C757D - Secondary text
```

### Component Status Badges

```
Status          Badge Color    Text Color
PENDING         --warning      White
PENDING_CONFIRMATION --warning White
APPROVED        --success      White
PUBLISHED       --success      White
COMPLETED       --success      White
CONFIRMED       --success      White
REJECTED        --danger       White
DRAFT           --light        Dark
SUSPENDED       --danger       White
ARCHIVED        --gray-600     White
FAILED          --danger       White
CANCELLED       --danger       White
PROCESSING      --info         White
```

### Layout Grid

```
Desktop (>= 1200px)
├── Navbar (100% width, fixed top)
├── Sidebar (250px, fixed left)
├── Main Content (calc(100% - 250px))
│   ├── Header
│   ├── Content Grid
│   └── Footer

Tablet (768px - 1199px)
├── Navbar (100% width, fixed top)
├── Sidebar (collapsible, slide-out)
├── Main Content (100%)
│   ├── Header with menu toggle
│   ├── Content Grid (2 cols)
│   └── Footer

Mobile (< 768px)
├── Navbar (100% width, fixed top, compact)
├── Sidebar (hidden, accessible via hamburger)
├── Main Content (100%)
│   ├── Header with menu toggle
│   ├── Content Grid (1 col)
│   └── Footer (sticky)
```

### Component Spacing

```
--spacing-xs:  0.25rem (4px)   - Micro spacing
--spacing-sm:  0.5rem (8px)    - Small padding
--spacing-md:  1rem (16px)     - Default padding
--spacing-lg:  1.5rem (24px)   - Large padding
--spacing-xl:  2rem (32px)     - Extra large padding
```

### Typography Scale

```
h1 (page title)      2.5rem    font-weight: 700
h2 (section title)   2rem      font-weight: 600
h3 (subsection)      1.5rem    font-weight: 600
h4 (card title)      1.25rem   font-weight: 600
p (body)             1rem      font-weight: 400
small (helper text)  0.875rem  font-weight: 400
```

### Interactive Components

```
Buttons:
  .btn              Base button style
  .btn-primary      Main actions (blue)
  .btn-success      Confirm actions (green)
  .btn-warning      Caution actions (amber)
  .btn-danger       Destructive actions (red)
  .btn-secondary    Alternative actions
  
  States:
    :hover          Opacity 0.9, slight shadow
    :active         Brightness decreased
    :disabled       Opacity 0.5, cursor not-allowed

Forms:
  input/select/textarea
    Border: 1px solid --gray-300
    Focus: Border --primary, shadow outline
    Error: Border --danger
    Disabled: Background --light, opacity 0.6

Cards:
  Background: --white
  Border: 1px solid --gray-300
  Padding: --spacing-lg
  Border-radius: 8px
  Box-shadow: 0 1px 3px rgba(0,0,0,0.1)
  
  Hover: 
    Box-shadow: 0 4px 12px rgba(0,0,0,0.15)
    Transform: translateY(-2px)

Tables:
  Header Background: --light
  Row Border: 1px solid --gray-300
  Row Hover: Background --light
  Padding: --spacing-md
  
Badges:
  Padding: --spacing-xs --spacing-sm
  Border-radius: 4px
  Font-size: 0.875rem
  Font-weight: 600
```

---

## 📡 BACKEND API ENDPOINTS FOR FRONTEND

### Mentors API

```
GET /api/v1x/mentors
  Query: ?expertise=&rate_min=&rate_max=&rating_min=&page=&limit=
  Response: { mentors: [], total, page, limit }

GET /api/v1x/mentors/[id]
  Response: {
    id, name, bio, expertise, hourly_rate, average_rating,
    total_students, reviews_count, response_time,
    image_url, certifications, teaching_style, availability_status
  }

GET /api/v1x/mentors/[id]/availability
  Response: {
    mentor_id, mentor_name,
    available_slots: [
      { date, day, slots: [{ time, available, price }] }
    ]
  }

GET /api/v1x/mentors/[id]/reviews
  Response: {
    mentor_id, mentor_name, average_rating, total_reviews,
    reviews: [{ id, student_name, rating, comment, date, verified }]
  }

POST /api/v1x/mentors/[id]/book
  Headers: Authorization: Bearer {token}
  Body: { date, time, topic, duration_minutes, notes }
  Response: {
    session_id, mentor_id, mentor_name, student_name,
    scheduled_at, duration_minutes, price, status, meeting_url
  }
```

### Seller API

```
GET /api/v1x/seller/products
  Headers: Authorization: Bearer {token} (role: MENTOR)
  Response: { products: [{id, name, price, status, sales_count, rating}] }

POST /api/v1x/seller/products
  Headers: Authorization: Bearer {token}
  Body: { name, description, price, product_type, tags, cover_image, files }
  Response: { product_id, status }

GET /api/v1x/seller/analytics/sales
  Headers: Authorization: Bearer {token}
  Query: ?period=month
  Response: { total_sales, total_orders, average_order_value, by_date: [] }

GET /api/v1x/seller/analytics/earnings
  Headers: Authorization: Bearer {token}
  Response: { total_earned, pending_payout, paid_out, by_product: [] }

GET /api/v1x/seller/payouts
  Headers: Authorization: Bearer {token}
  Response: {
    payouts: [
      { id, amount, status, requested_date, processed_date }
    ]
  }

POST /api/v1x/seller/request-payout
  Headers: Authorization: Bearer {token}
  Body: { amount }
  Response: { payout_id, status, message }
```

### Admin API

```
GET /api/v1x/admin/analytics/dashboard
  Headers: Authorization: Bearer {token} (role: ADMIN|SUPERADMIN)
  Response: {
    total_revenue, total_users, total_products,
    total_orders, platform_fee_collected,
    metrics_by_date: []
  }

GET /api/v1x/admin/products
  Query: ?status=pending&page=&limit=
  Response: {
    products: [
      { id, name, seller_name, price, status, created_at }
    ],
    total
  }

POST /api/v1x/admin/products/[id]/approve
  Response: { message, product_id, status }

POST /api/v1x/admin/products/[id]/reject
  Body: { reason }
  Response: { message, product_id, status }

GET /api/v1x/admin/sellers
  Response: {
    sellers: [
      { id, name, email, is_verified, product_count, total_sales }
    ]
  }

POST /api/v1x/admin/marketplace/sellers/[id]/verify
  Response: { message, seller_id, is_verified }

GET /api/v1x/admin/payouts
  Query: ?status=pending
  Response: {
    payouts: [
      { id, seller_name, amount, status, requested_date }
    ]
  }

POST /api/v1x/admin/payouts/[id]/approve
  Response: { message, payout_id, status }

POST /api/v1x/admin/payouts/[id]/process
  Response: { message, payout_id, status, tracking_id }

GET /api/v1x/admin/users
  Response: {
    users: [
      { id, name, email, role, status, created_at }
    ]
  }

GET /api/v1x/admin/audit-logs
  Query: ?user=[id]&page=
  Response: {
    logs: [
      { id, admin_name, action, target, timestamp }
    ]
  }
```

### Dashboard API

```
GET /api/v1x/dashboard/mentor-sessions
  Headers: Authorization: Bearer {token}
  Query: ?status=&page=
  Response: {
    sessions: [
      {
        id, mentor_id, mentor_name, scheduled_at,
        duration_minutes, topic, status, price, meeting_url
      }
    ]
  }

POST /api/v1x/dashboard/mentor-sessions/[id]/feedback
  Headers: Authorization: Bearer {token}
  Body: { rating, comment, would_recommend }
  Response: { session_id, feedback_submitted, message }
```

---

## ✅ IMPLEMENTATION CHECKLIST

**Frontend Pages**:
- [ ] All 90+ URLs accessible
- [ ] Mentor browse/filter working
- [ ] Product listing showing 3 demo products
- [ ] Seller dashboard showing 4 mentors' products
- [ ] Admin dashboard showing metrics
- [ ] Product approval page working
- [ ] Payout management page working

**Styling**:
- [ ] Colors applied (7 colors)
- [ ] Badges showing correct status colors
- [ ] Responsive layout on mobile/tablet/desktop
- [ ] Button hover/active states working
- [ ] Form validation styling
- [ ] Badge colors matching status

**Data Integration**:
- [ ] API endpoints returning demo data
- [ ] Frontend consuming API responses
- [ ] Loading states showing
- [ ] Error handling displaying
- [ ] Charts/analytics rendering
- [ ] Tables sorting/filtering

**Testing**:
- [ ] Student can book mentor (4 available)
- [ ] Seller can create and sell product (3 demo products)
- [ ] Admin can approve/reject products
- [ ] Admin can process payouts
- [ ] Analytics showing correct metrics
- [ ] All 90+ URLs have no 404 errors

---

## 🚀 DEPLOYMENT STEPS

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python init_db.py
   python seed_all_demo_data.py
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Frontend Setup**
   ```bash
   npm install
   npm run dev
   # Runs on http://localhost:3000
   ```

3. **Database Verification**
   ```bash
   # Check demo data was seeded
   sqlite3 backend/app/data/skillforge.db
   > SELECT COUNT(*) FROM users;        # Should be 11
   > SELECT COUNT(*) FROM mentors;      # Should be 4
   > SELECT COUNT(*) FROM digital_products; # Should be 3
   ```

4. **API Testing**
   ```bash
   # Test mentor endpoints
   curl http://localhost:8001/api/v1x/mentors
   
   # Test seller endpoints
   curl -H "Authorization: Bearer TOKEN" http://localhost:8001/api/v1x/seller/products
   
   # Test admin endpoints
   curl -H "Authorization: Bearer TOKEN" http://localhost:8001/api/v1x/admin/analytics/dashboard
   ```

5. **Browser Testing**
   - Navigate to http://localhost:3000
   - Test 15+ URLs from the checklist
   - Verify demo data displays
   - Test all 4 user flows

---

**Status**: Complete reference ready for implementation ✅
