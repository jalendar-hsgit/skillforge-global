# 🗺️ MARKETPLACE NAVIGATION & URL GUIDE

**Complete Guide to All Marketplace Frontend URLs and Navigation Paths**

---

## 📍 MAIN MARKETPLACE URLs

### Customer Access (Buyers)
```
🏠 Homepage
├─ http://localhost:3000/
└─ View landing page

📚 Marketplace (Browse All Courses)
├─ http://localhost:3000/marketplace
├─ Features:
│  ├─ View all courses
│  ├─ Filter by category
│  ├─ Search for courses
│  ├─ Free only filter
│  ├─ Add to cart
│  └─ View cart count
└─ Access: Public (no auth required)

🛒 Shopping Cart
├─ http://localhost:3000/marketplace/cart
├─ Features:
│  ├─ View cart items
│  ├─ Update quantities
│  ├─ Remove items
│  ├─ See total price
│  └─ Proceed to checkout
└─ Access: Authenticated only (login required)

💳 Checkout Page
├─ http://localhost:3000/marketplace/checkout
├─ Features:
│  ├─ Review order
│  ├─ Enter payment info
│  ├─ Apply coupon
│  ├─ Confirm purchase
│  └─ Get order confirmation
└─ Access: Authenticated only

📦 My Orders / Order History
├─ http://localhost:3000/marketplace/orders
├─ Features:
│  ├─ View all purchases
│  ├─ Track order status
│  ├─ Download invoices
│  ├─ Access purchased courses
│  └─ Request refunds
└─ Access: Authenticated only

📄 Order Details
├─ http://localhost:3000/marketplace/orders/{order_id}
├─ Example: http://localhost:3000/marketplace/orders/ORD-123-456
├─ Features:
│  ├─ Full order information
│  ├─ Payment status
│  ├─ Delivery status
│  ├─ Invoice details
│  └─ Support contact
└─ Access: Authenticated (own orders only)
```

---

## 🎓 COURSE & PRODUCT DETAILS

### View Course Details
```
Course Detail Page
├─ URL: http://localhost:3000/courses/{course_path}
├─ Examples:
│  ├─ http://localhost:3000/courses/python-fundamentals
│  ├─ http://localhost:3000/courses/web-development
│  ├─ http://localhost:3000/courses/react-basics
│  ├─ http://localhost:3000/courses/machine-learning-basics
│  └─ http://localhost:3000/courses/devops-essentials
│
├─ Information Shown:
│  ├─ Course title
│  ├─ Full description
│  ├─ Price (if paid)
│  ├─ Category
│  ├─ Video count
│  ├─ Instructor info
│  ├─ Student reviews
│  ├─ Prerequisites
│  ├─ Learning outcomes
│  └─ "Add to Cart" button
│
├─ Navigation:
│  ├─ From: /marketplace (click course card)
│  ├─ From: Search results
│  ├─ From: Category filter results
│  └─ From: Direct URL
│
└─ Access: Public (no auth required)

Digital Products Detail Page
├─ URL: http://localhost:3000/marketplace/digital-products/{product_id}
├─ Examples:
│  ├─ http://localhost:3000/marketplace/digital-products/1
│  ├─ http://localhost:3000/marketplace/digital-products/2
│  └─ http://localhost:3000/marketplace/digital-products/3
│
├─ Information Shown:
│  ├─ Product name
│  ├─ Detailed description
│  ├─ Price
│  ├─ Product type (template, guide, cheatsheet, etc.)
│  ├─ Category
│  ├─ Seller info
│  ├─ Reviews & ratings
│  ├─ Download count
│  ├─ File previews
│  └─ "Buy Now" button
│
├─ Navigation:
│  ├─ From: Digital Products browse page
│  ├─ From: Search results
│  ├─ From: Seller storefront
│  └─ From: Direct URL
│
└─ Access: Public (no auth required)

Digital Products Browse
├─ URL: http://localhost:3000/marketplace/digital-products
├─ Features:
│  ├─ View all published products
│  ├─ Sort by popularity/newest/price/rating
│  ├─ Filter by category
│  ├─ Search products
│  ├─ View seller ratings
│  └─ Quick buy buttons
└─ Access: Public (no auth required)
```

---

## 👨‍💼 SELLER DASHBOARD & MANAGEMENT

### Seller Home
```
Seller Dashboard
├─ URL: http://localhost:3000/marketplace/seller
├─ Access: Seller role only (must be logged in as seller)
├─ Features:
│  ├─ Sales overview
│  ├─ Revenue summary
│  ├─ Recent orders
│  ├─ Quick stats
│  └─ Navigation menu
└─ Requires: Seller account approval
```

### Manage Products
```
Seller Product List
├─ URL: http://localhost:3000/marketplace/seller/products
├─ Features:
│  ├─ View all my products
│  ├─ Filter by status (draft/published/archived)
│  ├─ Edit products
│  ├─ Delete products
│  ├─ See sales count
│  ├─ Check earnings
│  └─ "Create New Product" button
├─ Access: Seller only
└─ Quick Actions:
   ├─ Edit → http://localhost:3000/marketplace/seller/products/{product_id}/edit
   ├─ View → http://localhost:3000/marketplace/digital-products/{product_id}
   ├─ Analytics → View sales/ratings
   └─ Delete → Remove product

Create New Product
├─ URL: http://localhost:3000/marketplace/seller/products/create
├─ OR: http://localhost:3000/marketplace/seller/create-product
├─ Form Fields:
│  ├─ Product name
│  ├─ Description
│  ├─ Category
│  ├─ Product type (template/guide/cheatsheet/course)
│  ├─ Price
│  ├─ File upload
│  ├─ Thumbnail image
│  ├─ Preview content
│  └─ Save as draft or publish
├─ Access: Seller only
└─ After creation:
   ├─ Status: DRAFT (unpublished)
   ├─ Awaiting approval (if required)
   └─ Then PUBLISHED (visible to customers)

Edit Product
├─ URL: http://localhost:3000/marketplace/seller/products/{product_id}/edit
├─ Example: http://localhost:3000/marketplace/seller/products/5/edit
├─ Editable Fields:
│  ├─ Title
│  ├─ Description
│  ├─ Category
│  ├─ Price
│  ├─ Thumbnail
│  └─ Status (draft/published/archived)
├─ Access: Seller (own products only)
└─ After Edit:
   ├─ Changes saved
   ├─ If published: Visible immediately to customers
   └─ If draft: Private until published
```

### View Orders & Analytics
```
Seller Orders
├─ URL: http://localhost:3000/marketplace/seller/orders
├─ Features:
│  ├─ View all customer orders
│  ├─ Order status tracking
│  ├─ Customer info
│  ├─ Payment status
│  ├─ Delivery tracking
│  ├─ Invoice generation
│  └─ Message customer
├─ Filter by:
│  ├─ Status (pending/completed/shipped)
│  ├─ Date range
│  ├─ Product
│  └─ Customer
└─ Access: Seller only

Order Details
├─ URL: http://localhost:3000/marketplace/seller/orders/{order_id}
├─ Example: http://localhost:3000/marketplace/seller/orders/123
├─ Shows:
│  ├─ Customer name & email
│  ├─ Product purchased
│  ├─ Order date & time
│  ├─ Payment amount
│  ├─ Delivery status
│  ├─ Tracking number
│  └─ Communication log
└─ Access: Seller (own orders only)

Seller Analytics
├─ URL: http://localhost:3000/marketplace/seller/analytics
├─ Metrics Shown:
│  ├─ Total sales (count & revenue)
│  ├─ Best selling products
│  ├─ Revenue graph (daily/weekly/monthly)
│  ├─ Customer satisfaction
│  ├─ Average rating
│  ├─ Return rate
│  ├─ Popular categories
│  └─ Traffic sources
├─ Filters:
│  ├─ Date range
│  ├─ Product
│  ├─ Category
│  └─ Custom reports
└─ Access: Seller only

Seller Settings/Profile
├─ URL: http://localhost:3000/marketplace/seller/settings
├─ OR: http://localhost:3000/marketplace/seller/profile
├─ Manage:
│  ├─ Store name
│  ├─ Store description
│  ├─ Store logo/banner
│  ├─ Bank details (for payouts)
│  ├─ Contact info
│  ├─ Return policy
│  ├─ Shipping info
│  └─ Notification preferences
└─ Access: Seller only
```

---

## 🛡️ ADMIN DASHBOARD & MANAGEMENT

### Admin Home
```
Admin Dashboard
├─ URL: http://localhost:3000/admin
├─ OR: http://localhost:3000/admin/dashboard
├─ Access: Admin/Superadmin role only
├─ Features:
│  ├─ System overview
│  ├─ Key metrics
│  ├─ Recent activity
│  ├─ Quick actions
│  └─ Navigation menu
└─ Requires: Admin account
```

### Manage Products
```
Admin Products List
├─ URL: http://localhost:3000/admin/products
├─ Features:
│  ├─ View ALL products (all sellers)
│  ├─ Approve/reject pending products
│  ├─ Suspend/archive products
│  ├─ Edit product details
│  ├─ Filter by seller
│  ├─ Filter by status
│  ├─ Search
│  └─ Bulk actions
├─ Statuses Managed:
│  ├─ DRAFT → Review and approve
│  ├─ PENDING_APPROVAL → Approve or reject
│  ├─ PUBLISHED → Monitor
│  ├─ SUSPENDED → Review violations
│  └─ ARCHIVED → Historical records
└─ Access: Admin/Superadmin only

Product Approval
├─ URL: http://localhost:3000/admin/products/pending
├─ Shows:
│  ├─ List of pending products
│  ├─ Product details
│  ├─ Seller info
│  ├─ Quality check results
│  ├─ Customer reports (if any)
│  └─ Approve/Reject buttons
├─ Actions:
│  ├─ ✅ Approve → Product becomes PUBLISHED
│  ├─ ❌ Reject with reason → Seller notified
│  └─ ⏸️ Request changes → Seller revises
└─ Access: Admin/Superadmin only

Product Details (Admin View)
├─ URL: http://localhost:3000/admin/products/{product_id}
├─ Shows EVERYTHING:
│  ├─ Full product details
│  ├─ Seller information
│  ├─ Sales metrics
│  ├─ Customer reviews
│  ├─ Complaints/reports
│  ├─ File integrity
│  ├─ Quality flags
│  └─ Edit/suspend options
└─ Access: Admin/Superadmin only
```

### Manage Sellers
```
Sellers List
├─ URL: http://localhost:3000/admin/sellers
├─ Features:
│  ├─ View all sellers
│  ├─ Check seller stats
│  ├─ Approve new sellers
│  ├─ Suspend bad sellers
│  ├─ Review seller ratings
│  ├─ View seller revenue
│  └─ Send messages
├─ Filters:
│  ├─ Status (pending/approved/suspended)
│  ├─ Category
│  ├─ Rating
│  └─ Join date
└─ Access: Admin/Superadmin only

Seller Details (Admin)
├─ URL: http://localhost:3000/admin/sellers/{seller_id}
├─ Shows:
│  ├─ Seller profile
│  ├─ All products they've created
│  ├─ Sales history
│  ├─ Revenue earned
│  ├─ Customer complaints
│  ├─ Rating & reviews
│  ├─ Payout history
│  └─ Approval/suspension options
└─ Access: Admin/Superadmin only

Seller Approval
├─ URL: http://localhost:3000/admin/sellers/pending
├─ Features:
│  ├─ Pending seller applications
│  ├─ Verify seller credentials
│  ├─ Check background
│  ├─ Approve/reject sellers
│  ├─ Request more info
│  └─ Bulk actions
└─ Access: Admin/Superadmin only
```

### Manage Courses
```
Courses Management
├─ URL: http://localhost:3000/admin/courses
├─ Features:
│  ├─ View all courses
│  ├─ Create courses (admin-created)
│  ├─ Edit course details
│  ├─ Manage pricing
│  ├─ Set categories
│  ├─ Upload content
│  ├─ Manage students
│  └─ View analytics
├─ Status Options:
│  ├─ DRAFT → Preparing
│  ├─ PUBLISHED → Available to students
│  ├─ ARCHIVED → No longer available
│  └─ SUSPENDED → Temporarily unavailable
└─ Access: Admin/Superadmin only

Course Details (Admin)
├─ URL: http://localhost:3000/admin/courses/{course_id}
├─ Shows:
│  ├─ Full course details
│  ├─ Module breakdown
│  ├─ Student enrollment
│  ├─ Revenue earned
│  ├─ Completion rates
│  ├─ Reviews & ratings
│  └─ Edit options
└─ Access: Admin/Superadmin only
```

### Manage Orders
```
Orders Management
├─ URL: http://localhost:3000/admin/orders
├─ Features:
│  ├─ View ALL orders (all customers)
│  ├─ Track order status
│  ├─ Manage refunds
│  ├─ Resolve disputes
│  ├─ View revenue
│  ├─ Generate reports
│  └─ Customer support
├─ Filter by:
│  ├─ Status (pending/completed/failed/refunded)
│  ├─ Date range
│  ├─ Product
│  ├─ Seller
│  ├─ Customer
│  └─ Amount range
└─ Access: Admin/Superadmin only

Order Details (Admin)
├─ URL: http://localhost:3000/admin/orders/{order_id}
├─ Shows:
│  ├─ Customer info
│  ├─ Products ordered
│  ├─ Payment details
│  ├─ Shipping info
│  ├─ Transaction history
│  ├─ Support tickets
│  └─ Refund/action buttons
└─ Access: Admin/Superadmin only
```

### Analytics & Reports
```
Admin Analytics
├─ URL: http://localhost:3000/admin/analytics
├─ Dashboards:
│  ├─ Sales overview
│  ├─ Revenue reports
│  ├─ User metrics
│  ├─ Seller performance
│  ├─ Product performance
│  ├─ Category analysis
│  ├─ Customer satisfaction
│  └─ Traffic analysis
├─ Export Options:
│  ├─ PDF reports
│  ├─ Excel sheets
│  ├─ CSV data
│  └─ Custom date ranges
└─ Access: Admin/Superadmin only

User Management
├─ URL: http://localhost:3000/admin/users
├─ Features:
│  ├─ View all users
│  ├─ Manage roles (USER/MENTOR/ADMIN)
│  ├─ Suspend users
│  ├─ Ban users
│  ├─ View user activity
│  ├─ See purchase history
│  └─ Handle complaints
└─ Access: Admin/Superadmin only

Settings & Configuration
├─ URL: http://localhost:3000/admin/settings
├─ OR: http://localhost:3000/admin/configuration
├─ Configure:
│  ├─ Platform fees
│  ├─ Commission rates
│  ├─ Payment methods
│  ├─ Shipping settings
│  ├─ Tax rates
│  ├─ Category management
│  ├─ Feature toggles
│  └─ Email templates
└─ Access: Superadmin only
```

---

## 🔐 AUTHENTICATION & USER FLOW

### Login & Registration
```
Login Page
├─ URL: http://localhost:3000/auth/login
├─ With redirect:
│  ├─ http://localhost:3000/auth/login?redirect=/marketplace
│  ├─ http://localhost:3000/auth/login?redirect=/marketplace/cart
│  └─ http://localhost:3000/auth/login?redirect=/marketplace/seller
├─ Login Options:
│  ├─ Email + password
│  └─ Social login (if configured)
└─ After login: Redirects to intended page

Register Page
├─ URL: http://localhost:3000/auth/register
├─ Account Type:
│  ├─ Buyer (regular user)
│  ├─ Seller (seller account)
│  └─ Agency (bulk seller)
├─ After registration:
│  ├─ Verify email
│  ├─ Redirect to dashboard
│  └─ If seller: Await approval
└─ Public page (no auth required)

Forgot Password
├─ URL: http://localhost:3000/auth/forgot-password
├─ Reset Email
├─ New Password Setup
└─ Redirect to login

Profile / Account
├─ URL: http://localhost:3000/account
├─ OR: http://localhost:3000/profile
├─ Manage:
│  ├─ Name & email
│  ├─ Avatar
│  ├─ Bio
│  ├─ Skills
│  ├─ Password
│  ├─ Notifications
│  └─ Privacy settings
└─ Access: Authenticated users only
```

---

## 📊 HOW TO NAVIGATE & CHECK DETAILS

### For Customers (Buyers)
```
STEP 1: Browse Products
├─ Go to: http://localhost:3000/marketplace
├─ See:
│  └─ Grid of all courses
├─ Filter:
│  ├─ By category (dropdown)
│  ├─ By search (search bar)
│  ├─ Free only (checkbox)
│  └─ Sort (newest/popular)
└─ Result: List of matching courses

STEP 2: View Course Details
├─ Click: "View Details" or course card
├─ URL Changes to: /courses/{course_path}
├─ See:
│  ├─ Full description
│  ├─ Price
│  ├─ Category
│  ├─ Videos count
│  ├─ Instructor
│  ├─ Reviews
│  └─ "Add to Cart" button
└─ Decision: Add to cart or continue browsing

STEP 3: Add to Cart
├─ Click: "Add to Cart" button
├─ If NOT logged in:
│  └─ Redirect to: /auth/login?redirect=/marketplace
├─ If logged in:
│  ├─ Item added to cart
│  ├─ Cart count updates (top right)
│  └─ Get confirmation message
└─ Cart now has: 1 item

STEP 4: View Cart
├─ Click: Cart icon (top right)
├─ URL: http://localhost:3000/marketplace/cart
├─ See:
│  ├─ All items in cart
│  ├─ Item prices
│  ├─ Total price
│  ├─ Quantity controls
│  ├─ Remove buttons
│  └─ "Proceed to Checkout" button
└─ Can: Update quantities or remove items

STEP 5: Checkout
├─ Click: "Proceed to Checkout"
├─ URL: http://localhost:3000/marketplace/checkout
├─ Review:
│  ├─ Order summary
│  ├─ Items to be purchased
│  ├─ Pricing breakdown
│  ├─ Shipping address
│  ├─ Billing address
│  └─ Payment method
├─ Enter:
│  ├─ Payment card details
│  ├─ Apply coupon (if have)
│  └─ Confirm order
└─ Result: Order created, get confirmation

STEP 6: Track Order
├─ Go to: http://localhost:3000/marketplace/orders
├─ See:
│  ├─ All my purchases
│  ├─ Order status (pending/completed)
│  ├─ Order dates
│  ├─ Amount paid
│  └─ Access to purchased courses
├─ Click: Order details for full info
└─ Access: My courses from here
```

### For Sellers
```
STEP 1: Login as Seller
├─ Account type: Must be seller account
├─ Go to: http://localhost:3000/auth/login
├─ After approval: Access seller features
└─ Redirect to: /marketplace/seller

STEP 2: View Dashboard
├─ URL: http://localhost:3000/marketplace/seller
├─ See:
│  ├─ Sales overview
│  ├─ Revenue summary
│  ├─ Recent orders
│  ├─ Quick stats
│  └─ Menu navigation
└─ Quick access to all seller features

STEP 3: Create Product
├─ Go to: http://localhost:3000/marketplace/seller/products
├─ Click: "Create New Product" or "+"
├─ URL: http://localhost:3000/marketplace/seller/create-product
├─ Fill Form:
│  ├─ Product name
│  ├─ Description (detailed)
│  ├─ Category
│  ├─ Product type
│  ├─ Price
│  ├─ Upload file
│  ├─ Upload thumbnail
│  └─ Add preview content
├─ Choose:
│  ├─ Save as DRAFT (private)
│  └─ Publish (visible to customers)
└─ Result: Product created (awaits approval if required)

STEP 4: Manage Products
├─ URL: http://localhost:3000/marketplace/seller/products
├─ See:
│  ├─ All my products
│  ├─ Status (draft/published/archived)
│  ├─ Sales count per product
│  ├─ Earnings per product
│  └─ Rating per product
├─ Actions:
│  ├─ Edit: /products/{id}/edit
│  ├─ View: /digital-products/{id}
│  ├─ Delete
│  └─ Archive
└─ Can: Edit pricing, description, anything

STEP 5: View Orders
├─ URL: http://localhost:3000/marketplace/seller/orders
├─ See:
│  ├─ All customer orders
│  ├─ Order date
│  ├─ Product sold
│  ├─ Customer name
│  ├─ Amount received
│  ├─ Payment status
│  └─ Delivery status
├─ Click: Order details for full info
├─ Can:
│  ├─ Message customer
│  ├─ Update status
│  ├─ Download invoice
│  └─ Confirm delivery
└─ Track: When payment clears

STEP 6: View Analytics
├─ URL: http://localhost:3000/marketplace/seller/analytics
├─ See:
│  ├─ Total sales
│  ├─ Revenue graphs
│  ├─ Best sellers
│  ├─ Customer ratings
│  ├─ Return rates
│  └─ Traffic sources
├─ Filter: By date, product, category
└─ Export: Reports as PDF/CSV

STEP 7: Manage Settings
├─ URL: http://localhost:3000/marketplace/seller/settings
├─ Update:
│  ├─ Store name
│  ├─ Store description
│  ├─ Bank details (for payouts)
│  ├─ Policies
│  ├─ Contact info
│  └─ Logo/branding
└─ Save: Changes are applied
```

### For Admins
```
STEP 1: Login as Admin
├─ Account type: Must be ADMIN or SUPERADMIN
├─ Go to: http://localhost:3000/auth/login
├─ After login: Access admin features
└─ Redirect to: /admin/dashboard

STEP 2: View Admin Dashboard
├─ URL: http://localhost:3000/admin or /admin/dashboard
├─ See:
│  ├─ System overview
│  ├─ Key metrics
│  ├─ Recent activity
│  ├─ Admin menu
│  └─ Quick actions
└─ Navigate: To specific admin areas

STEP 3: Manage Products (All)
├─ URL: http://localhost:3000/admin/products
├─ See:
│  ├─ ALL products (all sellers)
│  ├─ Status (draft/pending/published/suspended)
│  ├─ Seller info
│  ├─ Sales metrics
│  └─ Quality flags
├─ Actions:
│  ├─ Approve pending products
│  ├─ Reject products
│  ├─ Suspend products
│  ├─ Edit product details
│  └─ View full details
└─ Filter: By seller, status, category

STEP 4: Approve Products
├─ URL: http://localhost:3000/admin/products/pending
├─ See:
│  ├─ Products awaiting approval
│  ├─ Quality check results
│  ├─ Customer reports
│  ├─ Seller ratings
│  └─ Approve/Reject buttons
├─ Decision:
│  ├─ ✅ APPROVE → Becomes PUBLISHED
│  ├─ ❌ REJECT → Seller notified
│  └─ ⏸️ REQUEST CHANGES → Seller revises
└─ Result: Product status updated

STEP 5: Manage Sellers
├─ URL: http://localhost:3000/admin/sellers
├─ See:
│  ├─ All sellers
│  ├─ Approval status
│  ├─ Seller ratings
│  ├─ Revenue metrics
│  └─ Compliance status
├─ Actions:
│  ├─ Approve new sellers
│  ├─ Suspend bad sellers
│  ├─ View seller details
│  ├─ See all their products
│  └─ Monitor performance
└─ Filter: By status, rating, category

STEP 6: View Analytics
├─ URL: http://localhost:3000/admin/analytics
├─ Reports:
│  ├─ Sales reports
│  ├─ Revenue reports
│  ├─ User metrics
│  ├─ Seller performance
│  ├─ Product performance
│  ├─ Category analysis
│  └─ Customer satisfaction
├─ Export: As PDF, Excel, CSV
└─ Filter: By date, category, metric

STEP 7: User Management
├─ URL: http://localhost:3000/admin/users
├─ See:
│  ├─ All users
│  ├─ User roles
│  ├─ Activity logs
│  ├─ Purchase history
│  └─ Complaints
├─ Actions:
│  ├─ Change roles
│  ├─ Suspend users
│  ├─ Ban users
│  └─ Handle disputes
└─ Monitor: User behavior

STEP 8: Settings & Configuration
├─ URL: http://localhost:3000/admin/settings
├─ Configure:
│  ├─ Platform fees (%)
│  ├─ Commission rates
│  ├─ Payment methods
│  ├─ Shipping options
│  ├─ Tax rates
│  ├─ Categories
│  ├─ Feature toggles
│  └─ Email templates
└─ Superadmin only
```

---

## 🎯 QUICK LINKS - BOOKMARK THESE

### Customer Links
```
| Feature | URL | Purpose |
|---------|-----|---------|
| Browse Courses | /marketplace | Browse all courses |
| Search | /marketplace?search=X | Find specific course |
| By Category | /marketplace?category=X | Filter by topic |
| Course Details | /courses/course-path | View full details |
| Digital Products | /marketplace/digital-products | Browse products |
| Shopping Cart | /marketplace/cart | View cart items |
| Checkout | /marketplace/checkout | Purchase |
| My Orders | /marketplace/orders | View purchases |
| Account | /account | Edit profile |
| Login | /auth/login | Sign in |
| Register | /auth/register | Create account |
```

### Seller Links
```
| Feature | URL | Purpose |
|---------|-----|---------|
| Seller Dashboard | /marketplace/seller | Home page |
| My Products | /marketplace/seller/products | Manage products |
| Create Product | /marketplace/seller/create-product | New product |
| Edit Product | /marketplace/seller/products/{id}/edit | Modify product |
| My Orders | /marketplace/seller/orders | See sales |
| Order Details | /marketplace/seller/orders/{id} | Full info |
| Analytics | /marketplace/seller/analytics | View metrics |
| Settings | /marketplace/seller/settings | Store config |
| Account | /account | Edit profile |
```

### Admin Links
```
| Feature | URL | Purpose |
|---------|-----|---------|
| Admin Dashboard | /admin | Home page |
| All Products | /admin/products | Manage all products |
| Pending Products | /admin/products/pending | Approve products |
| All Sellers | /admin/sellers | Manage sellers |
| Pending Sellers | /admin/sellers/pending | Approve sellers |
| All Orders | /admin/orders | View all orders |
| All Users | /admin/users | User management |
| Analytics | /admin/analytics | View reports |
| Courses | /admin/courses | Manage courses |
| Settings | /admin/settings | Platform config |
```

---

## 🔄 URL PATTERNS EXPLAINED

### Path Patterns
```
/marketplace           → Customer browsing area
/marketplace/seller    → Seller dashboard area
/marketplace/admin     → NOT USED (use /admin instead)
/admin                 → Admin dashboard area
/courses/{path}        → Individual course detail
/digital-products/{id} → Individual product detail
/auth/*                → Authentication pages
/account               → User account settings
```

### Query Parameters
```
?search=keyword        → Search in results
?category=Name         → Filter by category
?free_only=true        → Show only free items
?sort_by=popularity    → Sort results
?page=2                → Pagination
?filter=status         → Various filters
```

### URL Examples
```
Courses with filter:
http://localhost:3000/marketplace?category=Web%20Development&free_only=true

Product detail:
http://localhost:3000/courses/python-fundamentals

Digital product:
http://localhost:3000/marketplace/digital-products/5

Seller products:
http://localhost:3000/marketplace/seller/products?sort=sales

Admin approval:
http://localhost:3000/admin/products/pending?status=waiting
```

---

## ✅ SUMMARY TABLE

| Role | Browse | Add Cart | Checkout | View Orders | Admin | Analytics |
|------|--------|----------|----------|-------------|-------|-----------|
| **Customer** | ✅ /marketplace | ✅ /cart | ✅ /checkout | ✅ /orders | ❌ | ❌ |
| **Seller** | ✅ Browse own | ✅ See sales | ❌ | ✅ /seller/orders | ❌ | ✅ /seller/analytics |
| **Admin** | ✅ All products | ❌ | ❌ | ✅ All orders | ✅ /admin | ✅ /admin/analytics |
| **Superadmin** | ✅ All | ❌ | ❌ | ✅ All | ✅ All | ✅ Full config |

---

**This guide shows EVERY marketplace URL and how to navigate!** 🗺️
