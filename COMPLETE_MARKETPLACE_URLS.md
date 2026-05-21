# Complete Marketplace & Related Frontend URLs

## Base URL
`http://localhost:3000`

---

## MARKETPLACE - CUSTOMER BROWSING

### Main Marketplace Pages
| Page | URL | Purpose |
|------|-----|---------|
| Marketplace Home | `/marketplace` | Browse all products, featured items, trending |
| Product Cart | `/marketplace/cart` | View shopping cart, manage items |
| Checkout | `/marketplace/checkout` | Complete purchase, payment processing |
| My Orders | `/marketplace/orders` | View customer's completed orders |

---

## MARKETPLACE - SELLER DASHBOARD

### Seller Product Management
| Page | URL | Purpose |
|------|-----|---------|
| **Seller Dashboard** | `/marketplace/seller` | Seller home, overview stats |
| **Seller Products** | `/marketplace/seller/products` | List all seller's products |
| **Create Product** | `/marketplace/seller/create-product` | Create new digital product |
| **Edit Product** | `/marketplace/seller/create-product?productId={id}` | Edit existing product |
| **Seller Orders** | `/marketplace/seller/orders` | View orders from customers |
| **Seller Analytics** | `/marketplace/seller/analytics` | Sales stats, revenue, performance |

### Seller Account
- Login required: YES
- Role required: MENTOR (has seller capability)
- Access: Seller can only see their own products/orders

**Test User**: `mentor.sarah@skillforge.com` / `mentor123`

---

## ADMIN MARKETPLACE MANAGEMENT

### Admin Marketplace Overview
| Page | URL | Purpose |
|------|-----|---------|
| **Admin Home** | `/admin` | Main admin dashboard |
| **Marketplace Dashboard** | `/admin/marketplace` | Marketplace metrics & management |
| **Marketplace Products** | `/admin/marketplace?tab=products` | View all products, approve/suspend |
| **Marketplace Sellers** | `/admin/marketplace?tab=sellers` | View all sellers, verify, manage |

### Other Admin Pages (System-Wide)
| Page | URL | Purpose |
|------|-----|---------|
| Analytics | `/admin/analytics` | Platform-wide analytics |
| Users | `/admin/users` | User management |
| Courses | `/admin/courses` | Course management |
| Mentors | `/admin/mentors` | Mentor management |
| Payouts | `/admin/payouts` | Payment/payout management |
| Revenue | `/admin/revenue` | Revenue tracking |
| Audit Log | `/admin/audit-log` | Activity logging |
| Sessions | `/admin/sessions` | User session management |
| Settings | `/admin/settings` | System settings |

### Admin Account
- Login required: YES
- Role required: ADMIN or SUPERADMIN
- Access: Full system access

**Test User**: `admin@skillforge.com` / `admin123`
**Test User (Superadmin)**: `superadmin@skillforge.com` / `super123`

---

## MENTOR MANAGEMENT

### Mentor Portal
| Page | URL | Purpose |
|------|-----|---------|
| **Mentor Sessions** | `/mentor/sessions` | Schedule & manage mentoring sessions |
| **Mentor Availability** | `/mentor/availability` | Set available hours for mentoring |
| **Mentor Verification** | `/mentor/verification` | Complete mentor verification process |

### Mentor Account
- Login required: YES
- Role required: MENTOR
- Access: Mentor-specific features

**Test Users**:
- `mentor.sarah@skillforge.com` / `mentor123`
- `mentor.david@skillforge.com` / `mentor123`
- `mentor.emily@skillforge.com` / `mentor123`
- `mentor.james@skillforge.com` / `mentor123`

---

## JOB TRACKING

### Job Applications
| Page | URL | Purpose |
|------|-----|---------|
| **Job Applications** | `/jobs` | Track job applications & interviews |

### Job Tracking Account
- Login required: YES
- Role required: USER (any user can track jobs)

---

## AUTHENTICATION

### Auth Pages
| Page | URL | Purpose |
|------|-----|---------|
| Login | `/login` | User login |
| Signup | `/signup` | User registration |
| Logout | `POST /api/v1/auth/logout` | Logout endpoint |

---

## API ENDPOINTS USED BY FRONTEND

### Marketplace API Endpoints
```
GET  /api/v1x/marketplace/seller/products              - Get seller's products
POST /api/v1x/marketplace/seller/products              - Create product
GET  /api/v1x/marketplace/seller/products/{id}         - Get product details
PUT  /api/v1x/marketplace/seller/products/{id}         - Update product
DELETE /api/v1x/marketplace/seller/products/{id}       - Delete product

GET  /api/v1x/marketplace/admin/marketplace/dashboard  - Admin dashboard metrics
GET  /api/v1x/marketplace/admin/marketplace/products   - All products (admin)
PUT  /api/v1x/marketplace/admin/marketplace/products/{id}/approve   - Approve product
PUT  /api/v1x/marketplace/admin/marketplace/products/{id}/suspend   - Suspend product
GET  /api/v1x/marketplace/admin/marketplace/sellers    - All sellers (admin)
PUT  /api/v1x/marketplace/admin/marketplace/sellers/{id}/verify     - Verify seller

GET  /api/v1x/marketplace/orders                       - Customer orders
GET  /api/v1x/marketplace/seller/orders                - Seller orders
POST /api/v1x/marketplace/cart                         - Cart operations
```

---

## USER ROLES & PERMISSIONS

### Role Hierarchy
```
SUPERADMIN
  ├─ Full system access
  ├─ Access: /admin/*
  └─ Test: superadmin@skillforge.com

ADMIN
  ├─ Admin features
  ├─ Access: /admin/*
  └─ Test: admin@skillforge.com

MENTOR
  ├─ Seller dashboard (via /marketplace/seller/*)
  ├─ Mentor features (via /mentor/*)
  ├─ Job tracking (via /jobs)
  └─ Test: mentor.sarah@skillforge.com, mentor.david@skillforge.com, etc.

USER
  ├─ Marketplace browsing (via /marketplace)
  ├─ Job tracking (via /jobs)
  └─ Test: john.doe@example.com, jane.smith@example.com, etc.
```

---

## PRODUCT WORKFLOW IN SYSTEM

### Creation Flow
1. **Seller creates product** → `/marketplace/seller/create-product`
2. **API**: POST `/api/v1x/marketplace/seller/products`
3. **Product saved** with status: `draft`
4. **Admin reviews** at `/admin/marketplace?tab=products`
5. **Admin approves** → PUT `/api/v1x/marketplace/admin/marketplace/products/{id}/approve`
6. **Status changes** to: `published`
7. **Product appears** in `/marketplace` for customers

### Seller Management
- View products: `/marketplace/seller/products`
- Edit product: `/marketplace/seller/create-product?productId={id}`
- Delete product: via product listing page
- View sales: `/marketplace/seller/analytics`
- View orders: `/marketplace/seller/orders`

### Admin Management
- View all products: `/admin/marketplace?tab=products`
- Approve product: Dashboard action button
- Suspend product: Dashboard action button (requires reason)
- View sellers: `/admin/marketplace?tab=sellers`
- Verify seller: Dashboard action button

---

## QUICK NAVIGATION REFERENCE

### For Testing Seller Features
1. Login: `mentor.sarah@skillforge.com`
2. Go to: `/marketplace/seller/products`
3. See: "Advanced Python Programming" ($99.99) and "Python Cheat Sheet" ($9.99)
4. Click: Create Product button to add new product

### For Testing Admin Features
1. Login: `admin@skillforge.com`
2. Go to: `/admin/marketplace`
3. See: Dashboard with all products and sellers
4. Tab to "products" or "sellers" for detailed management

### For Marketplace Features
1. Browse: `/marketplace` (no login needed)
2. View products by category
3. Add to cart, checkout
4. View orders at: `/marketplace/orders`

### For Mentoring Features
1. Login as mentor
2. Schedule sessions: `/mentor/sessions`
3. Set availability: `/mentor/availability`
4. Complete verification: `/mentor/verification`

### For Job Tracking
1. Login as any user
2. Go to: `/jobs`
3. Track job applications and interviews

---

## RECENT FIXES

**Issue**: Seller products not displaying on `/marketplace/seller/products`
**Cause**: Frontend was looking for `data.products` but API returns `data.items`
**Fix**: Updated `/src/pages/marketplace/seller/products.tsx` to handle both response formats
**Status**: ✅ FIXED

**Issue**: Admin marketplace endpoints returning 404
**Cause**: Frontend using wrong API paths (missing `/marketplace` prefix)
**Fix**: Updated all admin marketplace endpoints to use correct paths
**Status**: ✅ FIXED

---

## TROUBLESHOOTING

### Products Not Showing in Seller Dashboard
- Clear browser cache: `Ctrl+Shift+Delete`
- Ensure logged in as mentor with products
- Check browser console for errors
- Verify backend is running: `http://localhost:8001/api/v1x/marketplace/seller/products`

### Admin Marketplace Not Loading
- Ensure logged in as admin
- Verify role is ADMIN or SUPERADMIN
- Check if products exist in database
- Test admin endpoint: `http://localhost:8001/api/v1x/marketplace/admin/marketplace/dashboard`

### Can't Create Products
- Must be logged in as MENTOR
- Must have seller account created
- Verify backend is receiving POST requests
- Check product creation form for validation errors

---

**Last Updated**: January 28, 2026
**Status**: All marketplace URLs documented and tested ✅
