# FRONTEND URLS - COMPLETE WITH MENTOR BOOKING + DATA FLOW

## 🌐 ALL FRONTEND URLS - Including Mentor Features for Students

**Base URL**: `http://localhost:3000`

---

## 📍 PUBLIC PAGES (No Auth)

```
GET     /                                    Home page
GET     /trending                            Trending courses/products
GET     /teams                               Teams/organizations
GET     /subscribe                           Subscription plans
GET     /status                              System status
GET     /ui-showcase                         UI components
```

---

## 🔐 AUTHENTICATION (Public)

```
GET     /login                               Login form
GET     /signup                              Registration form
GET     /unauthorized                        Access denied
```

---

## 🛍️ MARKETPLACE - PRODUCTS & SHOPPING

### Browse Products (Public)
```
GET     /marketplace                         Product listing + search/filter
GET     /marketplace/search?q=python         Search results
GET     /marketplace/[productId]             Product detail page
```

### Shopping Cart (Auth Required - User Role)
```
GET     /marketplace/cart                    Shopping cart view
POST    /marketplace/cart                    Add item to cart
DELETE  /marketplace/cart/[itemId]           Remove from cart
GET     /marketplace/checkout                Checkout/payment form
POST    /marketplace/checkout                Place order
GET     /marketplace/order-confirmation      Order confirmation
GET     /marketplace/orders                  View order history
GET     /marketplace/orders/[orderId]        Order detail
```

---

## 👨‍🏫 MENTOR FEATURES - FOR STUDENTS/BUYERS

### Browse & Book Mentors (Public/Auth)
```
GET     /mentors                             Mentor listing/search
GET     /mentors?expertise=python            Filter by expertise
GET     /mentors?rate_min=50&rate_max=100   Filter by rate
GET     /mentors/[mentorId]                  Mentor profile (public view)
GET     /mentors/[mentorId]/book             Book mentor session form
POST    /mentors/[mentorId]/book             Create booking
GET     /mentors/[mentorId]/reviews          Mentor reviews
GET     /mentors/[mentorId]/availability     View availability
```

### My Mentor Sessions (Auth Required - User Role)
```
GET     /dashboard/mentor-sessions           My booked sessions
GET     /dashboard/mentor-sessions/[id]      Session details
PUT     /dashboard/mentor-sessions/[id]      Reschedule session
DELETE  /dashboard/mentor-sessions/[id]      Cancel session
POST    /dashboard/mentor-sessions/[id]/feedback  Leave feedback
```

---

## 💼 SELLER DASHBOARD & MANAGEMENT (Auth Required - Mentor Role)

### Seller Overview & Management
```
GET     /marketplace/seller                  Seller dashboard (overview)
GET     /marketplace/seller/analytics        Sales analytics
GET     /marketplace/seller/earnings         Earnings summary
GET     /marketplace/seller/payouts          Payout history
GET     /marketplace/seller/reviews          Customer reviews
```

### Product Management
```
GET     /marketplace/seller/products         List seller products
GET     /marketplace/seller/products/[id]    Product detail (edit)
POST    /marketplace/seller/create-product   Create product form
POST    /marketplace/seller/products         Create new product
PUT     /marketplace/seller/products/[id]    Update product
DELETE  /marketplace/seller/products/[id]    Delete product
POST    /marketplace/seller/products/[id]/upload  Upload file
GET     /marketplace/seller/products/[id]/stats   Product stats
```

### Sales & Orders
```
GET     /marketplace/seller/orders           Sales/orders list
GET     /marketplace/seller/orders/[id]      Order detail
PUT     /marketplace/seller/orders/[id]      Update order status
GET     /marketplace/seller/customers        Customer list
GET     /marketplace/seller/customers/[id]   Customer detail
```

---

## 👨‍🏫 MENTOR DASHBOARD (Auth Required - Mentor Role)

### Mentor Overview
```
GET     /mentors/dashboard                   Mentor dashboard overview
GET     /mentors/dashboard/earnings          Total earnings
GET     /mentors/dashboard/sessions          Scheduled sessions
GET     /mentors/dashboard/analytics         Performance analytics
GET     /mentors/dashboard/students          Student list
GET     /mentors/dashboard/reviews           Student reviews
GET     /mentors/dashboard/payouts           Payout history
PUT     /mentors/dashboard/profile           Edit mentor profile
POST    /mentors/dashboard/availability      Set availability
GET     /mentors/dashboard/availability      View availability
```

### Session Management
```
GET     /mentors/dashboard/sessions          List all sessions
GET     /mentors/dashboard/sessions/[id]     Session detail
PUT     /mentors/dashboard/sessions/[id]     Confirm/update session
POST    /mentors/dashboard/sessions/[id]/feedback  Send feedback
DELETE  /mentors/dashboard/sessions/[id]     Cancel session
```

---

## 👤 USER PROFILE & SETTINGS

### My Profile (Auth Required)
```
GET     /profile                             View my profile
PUT     /profile                             Edit my profile
GET     /profile/[userId]                    View other user's profile
GET     /settings                            Account settings
PUT     /settings                            Update settings
GET     /settings/notifications              Notification preferences
GET     /settings/privacy                    Privacy settings
```

### Dashboard
```
GET     /dashboard                           User dashboard/home
GET     /dashboard/overview                  Dashboard overview
```

---

## 🔐 ADMIN PAGES (Auth Required - Admin Role)

### Admin Overview
```
GET     /admin                               Admin main dashboard
GET     /admin/dashboard                     Admin dashboard (alt)
```

### Marketplace Management
```
GET     /admin/marketplace                   Marketplace overview
GET     /admin/marketplace/products          All products
PUT     /admin/marketplace/products/[id]/approve      Approve product
PUT     /admin/marketplace/products/[id]/reject       Reject product
DELETE  /admin/marketplace/products/[id]    Delete product
GET     /admin/marketplace/sellers           Seller management
GET     /admin/marketplace/sellers/[id]     Seller detail
PUT     /admin/marketplace/sellers/[id]/verify       Verify seller
PUT     /admin/marketplace/sellers/[id]/suspend      Suspend seller
GET     /admin/marketplace/orders            All orders
GET     /admin/marketplace/orders/[id]      Order detail
```

### User Management
```
GET     /admin/users                         User management
GET     /admin/users/[id]                    User detail
PUT     /admin/users/[id]                    Edit user
DELETE  /admin/users/[id]                    Delete user
PUT     /admin/users/[id]/role               Change user role
POST    /admin/users/[id]/suspend            Suspend user
```

### Analytics & Reports
```
GET     /admin/analytics                     Platform analytics
GET     /admin/analytics/overview            Analytics overview
GET     /admin/analytics/sales               Sales metrics
GET     /admin/analytics/users               User metrics
GET     /admin/analytics/mentors             Mentor metrics
GET     /admin/analytics/revenue             Revenue report
GET     /admin/analytics/trending            Trending products
```

### Payout Management
```
GET     /admin/payouts                       Payout requests
GET     /admin/payouts/[id]                  Payout detail
PUT     /admin/payouts/[id]/approve          Approve payout
PUT     /admin/payouts/[id]/reject           Reject payout
POST    /admin/payouts/[id]/process          Process payout
GET     /admin/payouts/history               Payout history
```

### System Settings
```
GET     /admin/settings                      Admin settings
PUT     /admin/settings                      Update settings
GET     /admin/settings/commission           Commission rates
PUT     /admin/settings/commission           Update commission
GET     /admin/audit-logs                    Audit logs
GET     /admin/system-health                 System health
```

---

## 🎓 LEARNING & COURSES

```
GET     /courses                             Course listing
GET     /courses/[courseId]                  Course detail
POST    /courses/[courseId]/enroll           Enroll in course
GET     /learning-paths                      Learning paths
GET     /learning-paths/[pathId]             Learning path detail
GET     /code-snippets                       Code snippets
GET     /code-snippets/[snippetId]           Snippet detail
GET     /challenges                          Code challenges
GET     /challenges/[challengeId]            Challenge detail
GET     /watch/[contentId]                   Watch video
```

---

## 👥 COMMUNITY & SOCIAL

```
GET     /social                              Social feed
GET     /social/following                    Following list
GET     /forum                               Discussion forum
GET     /forum/[topicId]                     Topic detail
```

---

## 🔒 PROTECTED ROUTES & MIDDLEWARE

### Authentication Required (Redirect to /login if not auth)
```
/marketplace/seller/*
/marketplace/cart
/marketplace/checkout
/marketplace/orders*
/dashboard/*
/mentors/dashboard/*
/mentor/*
/profile
/settings
/social/*
/learning-paths/*
```

### Mentor Role Required (Redirect to /unauthorized)
```
/marketplace/seller/*
/mentors/dashboard/*
/mentor/*
/marketplace/seller/create-product
/marketplace/seller/products*
/marketplace/seller/orders
/marketplace/seller/analytics
```

### Admin Role Required (Redirect to /unauthorized)
```
/admin/*
```

---

## 📊 COMPLETE DATA FLOW DIAGRAM

```
USER FLOWS:

┌─────────────────────────────────────────────────────────────┐
│ 1. STUDENT/BUYER FLOW                                       │
├─────────────────────────────────────────────────────────────┤
│ /login → /dashboard → /marketplace                          │
│   ↓                        ↓           ↓                     │
│   Register          Browse Products   Search Products        │
│   ↓                        ↓           ↓                     │
│   /signup           /marketplace/[id] /marketplace?q=python │
│   ↓                        ↓                                 │
│   Create Account    Add to Cart (/marketplace/cart)         │
│                     ↓                                        │
│                     Checkout (/marketplace/checkout)         │
│                     ↓                                        │
│                     Payment (Stripe)                         │
│                     ↓                                        │
│                     Order Confirmation                       │
│                     ↓                                        │
│                     /marketplace/orders (View History)       │
│                     ↓                                        │
│                     Download Product                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. MENTOR BOOKING FLOW (Student)                            │
├─────────────────────────────────────────────────────────────┤
│ /mentors (Browse all mentors)                               │
│   ↓                                                          │
│ Filter: /mentors?expertise=python&rate_min=50&rate_max=100  │
│   ↓                                                          │
│ /mentors/[mentorId] (View mentor profile)                   │
│   ↓                                                          │
│ /mentors/[mentorId]/availability (Check slots)              │
│   ↓                                                          │
│ /mentors/[mentorId]/book (Book session)                     │
│   ↓                                                          │
│ /dashboard/mentor-sessions (View my sessions)               │
│   ↓                                                          │
│ Session occurs → /dashboard/mentor-sessions/[id]/feedback   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. SELLER/MENTOR PRODUCT SALES FLOW                         │
├─────────────────────────────────────────────────────────────┤
│ /marketplace/seller (Dashboard overview)                    │
│   ↓                                                          │
│ /marketplace/seller/create-product (Create product)         │
│   ↓                                                          │
│ Upload File & Set Price                                     │
│   ↓                                                          │
│ Submit for Approval → PENDING status                        │
│   ↓                                                          │
│ /marketplace/seller/products (Manage products)              │
│   ↓                                                          │
│ Admin Approves → PUBLISHED status                           │
│   ↓                                                          │
│ Product appears on /marketplace                             │
│   ↓                                                          │
│ /marketplace/seller/orders (View sales)                     │
│   ↓                                                          │
│ /marketplace/seller/analytics (Track sales)                 │
│   ↓                                                          │
│ /marketplace/seller/earnings (View earnings)                │
│   ↓                                                          │
│ /marketplace/seller/payouts (Request payout)                │
│   ↓                                                          │
│ Admin Approves Payout → Sent to Seller Account              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4. ADMIN MANAGEMENT FLOW                                    │
├─────────────────────────────────────────────────────────────┤
│ /admin (Dashboard - overview metrics)                       │
│   ├─ Total Revenue, Total Users, Total Products            │
│   ├─ Pending Approvals, Top Sellers, Top Products          │
│   └─ Sales Trends                                           │
│   ↓                                                          │
│ /admin/marketplace (Product approval)                       │
│   ↓                                                          │
│ Review: /admin/marketplace/products                         │
│   ├─ Approve Product → PUBLISHED                           │
│   └─ Reject Product → REJECTED                             │
│   ↓                                                          │
│ /admin/marketplace/sellers (Seller verification)            │
│   ↓                                                          │
│ Verify Seller → Can Request Payouts                         │
│   ↓                                                          │
│ /admin/payouts (Approve payout requests)                    │
│   ├─ Approve → APPROVED                                    │
│   ├─ Process → Send to Stripe                              │
│   └─ View History                                           │
│   ↓                                                          │
│ /admin/analytics (View platform metrics)                    │
│   ├─ Revenue Reports, User Growth                          │
│   ├─ Mentor Performance, Sales Trends                      │
│   └─ Export Reports                                         │
│   ↓                                                          │
│ /admin/users (User management)                              │
│   ├─ View all users, Edit profiles                         │
│   ├─ Change roles, Suspend users                           │
│   └─ View activity logs                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 THEME & STYLING STRUCTURE

```
Frontend Styling:
├─ Color Scheme
│  ├─ Primary:     #007BFF (Blue) - Main actions
│  ├─ Success:     #28A745 (Green) - Approved, Complete
│  ├─ Warning:     #FFC107 (Yellow) - Pending, Review
│  ├─ Danger:      #DC3545 (Red) - Rejected, Error
│  ├─ Info:        #17A2B8 (Cyan) - Information
│  ├─ Light:       #F8F9FA (Gray Light) - Backgrounds
│  └─ Dark:        #212529 (Gray Dark) - Text
│
├─ Components
│  ├─ Navbar:      Sticky top, Logo + Nav Links + User Menu
│  ├─ Sidebar:     Left navigation for admin/mentor/seller
│  ├─ Card:        Product card, Order card, User card
│  ├─ Modal:       Confirm actions, view details
│  ├─ Table:       Product list, User list, Order list
│  ├─ Form:        Search, filters, input forms
│  ├─ Badge:       Status badges (PENDING, APPROVED, etc)
│  ├─ Button:      Primary, Secondary, Success, Danger
│  └─ Alert:       Success, Error, Warning messages
│
├─ Pages Layout
│  ├─ Public Pages:   Header + Hero + Content + Footer
│  ├─ Auth Pages:     Centered form + Logo + Links
│  ├─ Dashboard:      Sidebar + Top Bar + Cards/Charts
│  ├─ List Pages:     Sidebar + Filters + Table + Pagination
│  ├─ Detail Pages:   Sidebar + Header + Content + Actions
│  └─ Forms:          Sidebar + Form Fields + Buttons
│
└─ Responsive Design
   ├─ Desktop:   Full layout, sidebar visible
   ├─ Tablet:    Collapsed sidebar, grid layout
   └─ Mobile:    Full-width, hamburger menu
```

---

## 📱 DEMO DATA ACCESS ENDPOINTS (Backend API)

```
GET     /api/v1x/marketplace/products              All products
GET     /api/v1x/marketplace/products?seller_id=1  Seller's products
GET     /api/v1x/mentors                           All mentors
GET     /api/v1x/mentors/[id]/availability        Mentor slots
GET     /api/v1x/seller/products                   My products (seller)
GET     /api/v1x/seller/analytics/sales           My sales
GET     /api/v1x/admin/analytics/dashboard        Admin metrics
GET     /api/v1x/admin/products?status=pending    Pending products
GET     /api/v1x/admin/sellers                     All sellers
GET     /api/v1x/admin/payouts?status=pending     Pending payouts
```

---

## ✅ URL TESTING CHECKLIST

- [ ] `/login` - Login form loads
- [ ] `/signup` - Registration form loads
- [ ] `/marketplace` - Shows 3+ products
- [ ] `/marketplace/[productId]` - Product detail shows
- [ ] `/mentors` - Shows 4+ mentors
- [ ] `/mentors/[id]` - Mentor profile loads
- [ ] `/mentors/[id]/book` - Booking form works
- [ ] `/marketplace/seller/create-product` - Form loads (mentor role)
- [ ] `/marketplace/seller/products` - Lists products (mentor role)
- [ ] `/marketplace/seller/analytics` - Shows sales (mentor role)
- [ ] `/admin` - Dashboard loads (admin role)
- [ ] `/admin/marketplace` - Product approval visible
- [ ] `/admin/payouts` - Payout list visible
- [ ] `/marketplace/checkout` - Checkout form works
- [ ] `/marketplace/orders` - Order history visible

---

## 🎯 NEXT STEPS

1. **Seed Demo Data**: Run `python backend/seed_all_demo_data.py`
2. **Start Servers**: Backend + Frontend
3. **Test URLs**: Follow checklist above
4. **Report Issues**: If any URL returns 404 or blank data
