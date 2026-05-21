# 🌐 Frontend URLs - Complete Reference

**Base URL**: `http://localhost:3000` (development)

---

## 📑 Table of Contents
1. [Public Pages](#public-pages)
2. [Authentication Pages](#authentication-pages)
3. [Marketplace](#marketplace)
4. [Mentor Features](#mentor-features)
5. [Admin Pages](#admin-pages)
6. [User Profile](#user-profile)
7. [Learning & Courses](#learning--courses)
8. [Community & Social](#community--social)
9. [Miscellaneous](#miscellaneous)

---

## 🌍 Public Pages

| URL | Purpose | Auth Required |
|-----|---------|----------------|
| `/` | Home page | ❌ No |
| `/trending` | Trending courses/content | ❌ No |
| `/teams` | Teams/organizations | ❌ No |
| `/subscribe` | Subscription plans | ❌ No |
| `/terms` | Terms of service | ❌ No |
| `/wishlist` | Wishlist (public view) | ❌ No |
| `/status` | System status page | ❌ No |
| `/ui-showcase` | UI component showcase | ❌ No |

---

## 🔐 Authentication Pages

| URL | Purpose | Status |
|-----|---------|--------|
| `/signup` | User registration | Public |
| `/login` | User login | Public |
| `/unauthorized` | Access denied page | Auth required |

---

## 🛍️ Marketplace

### Product Browsing (Public)
| URL | Purpose |
|-----|---------|
| `/marketplace` | Product listing with search/filter |
| `/marketplace/search?q=python` | Search results |

### Shopping (Auth Required - USER role)
| URL | Purpose | Auth |
|-----|---------|------|
| `/marketplace/cart` | Shopping cart | ✅ Yes |
| `/marketplace/checkout` | Payment form (Stripe) | ✅ Yes |
| `/marketplace/order-confirmation/{id}` | Order confirmation | ✅ Yes |
| `/marketplace/orders` | Order history | ✅ Yes |

### Seller Features (Auth Required - MENTOR role)
| URL | Purpose | Auth | Role |
|-----|---------|------|------|
| `/marketplace/seller` | Seller dashboard overview | ✅ Yes | MENTOR |
| `/marketplace/seller/create-product` | Create new product | ✅ Yes | MENTOR |
| `/marketplace/seller/products` | Manage products | ✅ Yes | MENTOR |
| `/marketplace/seller/orders` | View seller orders | ✅ Yes | MENTOR |
| `/marketplace/seller/analytics` | Sales analytics | ✅ Yes | MENTOR |

**Note**: All seller routes require MENTOR role. Accessing without role redirects to `/unauthorized`

---

## 👨‍🏫 Mentor Features

### Mentor Dashboard (Auth Required - MENTOR role)
| URL | Purpose | Auth |
|-----|---------|------|
| `/mentors/dashboard` | Overview/stats | ✅ Yes |
| `/mentors/dashboard/earnings` | Earnings summary | ✅ Yes |
| `/mentors/dashboard/analytics` | Performance analytics | ✅ Yes |
| `/mentors/dashboard/sessions` | Scheduled sessions | ✅ Yes |
| `/mentors/dashboard/students` | Student list | ✅ Yes |
| `/mentors/dashboard/payouts` | Payout history | ✅ Yes |
| `/mentors/dashboard/reviews` | Student reviews | ✅ Yes |
| `/mentors/dashboard/profile` | Mentor profile | ✅ Yes |

### Mentor Sessions
| URL | Purpose |
|-----|---------|
| `/mentors/{id}` | Mentor profile (public) |
| `/mentors/{id}/book` | Book a session |
| `/mentor/` | Current mentor dashboard |
| `/mentor/dashboard` | Mentor home |

---

## 👨‍💼 Admin Pages

**Note**: All admin routes require ADMIN or SUPERADMIN role

| URL | Purpose | Auth | Role |
|-----|---------|------|------|
| `/admin` | Admin main dashboard | ✅ Yes | ADMIN/SUPERADMIN |
| `/admin/dashboard` | Admin dashboard (alt) | ✅ Yes | ADMIN/SUPERADMIN |
| `/admin/marketplace` | Marketplace management | ✅ Yes | ADMIN/SUPERADMIN |
| `/admin/users` | User management | ✅ Yes | ADMIN/SUPERADMIN |
| `/admin/analytics` | Platform analytics | ✅ Yes | ADMIN/SUPERADMIN |
| `/admin/payouts` | Payout management | ✅ Yes | ADMIN/SUPERADMIN |

### Admin Marketplace Sub-pages
| URL | Purpose |
|-----|---------|
| `/admin/marketplace` (Tab 1) | Dashboard/metrics |
| `/admin/marketplace` (Tab 2) | Product approval |
| `/admin/marketplace` (Tab 3) | Seller management |

---

## 👤 User Profile

### My Profile (Auth Required)
| URL | Purpose | Auth |
|-----|---------|------|
| `/profile` | View my profile | ✅ Yes |
| `/profile/edit` | Edit my profile | ✅ Yes |
| `/settings` | Account settings | ✅ Yes |
| `/users/{id}` | View other user's profile | ❌ No |
| `/dashboard` | User dashboard | ✅ Yes |

---

## 🎓 Learning & Courses

| URL | Purpose | Auth |
|-----|---------|------|
| `/courses` | Course listing | ❌ No |
| `/courses/{id}` | Course details | ❌ No |
| `/courses/{id}/enroll` | Enroll in course | ✅ Yes |
| `/learning-paths/{id}` | Learning path | ✅ Yes |
| `/code-snippets` | Code snippet library | ❌ No |
| `/code-snippets/{id}` | View snippet | ❌ No |
| `/challenges` | Coding challenges | ❌ No |
| `/challenges/{id}` | Challenge details | ✅ Yes |
| `/watch/{id}` | Watch video/content | ❌ No |

---

## 👥 Community & Social

| URL | Purpose | Auth |
|-----|---------|------|
| `/social` | Social feed | ✅ Yes |
| `/social/following` | Following list | ✅ Yes |

---

## 🎯 Miscellaneous

| URL | Purpose | Auth |
|-----|---------|------|
| `/test-api` | API testing page | ❌ No |

---

## 🔒 Protected Routes & Middleware

**Routes requiring authentication** (will redirect to login if not authenticated):
```
/marketplace/seller/*
/marketplace/cart
/marketplace/checkout
/dashboard
/mentor/*
/mentors/dashboard/*
/admin/*
/profile
/settings
/social/*
/learning-paths/*
```

**Routes requiring MENTOR role** (will redirect to `/unauthorized` if not mentor):
```
/marketplace/seller/*
/mentors/dashboard/*
/mentor/*
```

**Routes requiring ADMIN role** (will redirect to `/unauthorized` if not admin):
```
/admin/*
```

### Middleware File
Location: `src/middleware.ts`

Protected routes configuration:
- PROTECTED_ROUTES: Routes that require authentication
- SELLER_ROUTES: Routes that require MENTOR role
- ADMIN_ROUTES: Routes that require ADMIN/SUPERADMIN role

---

## 📱 Dynamic Routes

### Route Parameters

| Pattern | Description | Example |
|---------|-------------|---------|
| `/users/[id]` | View user profile | `/users/5` |
| `/courses/[id]` | View course | `/courses/1` |
| `/challenges/[id]` | View challenge | `/challenges/3` |
| `/snippets/[id]` | View snippet | `/snippets/42` |
| `/learning-paths/[id]` | View learning path | `/learning-paths/2` |
| `/watch/[id]` | Watch content | `/watch/video-1` |
| `/mentors/[id]` | View mentor profile | `/mentors/3` |
| `/mentors/[id]/book` | Book mentor session | `/mentors/3/book` |

---

## 🔗 Common Navigation Links

### Authenticated User (USER role)
- Home: `/`
- Profile: `/profile`
- Settings: `/settings`
- Dashboard: `/dashboard`
- Courses: `/courses`
- Marketplace: `/marketplace`
- Cart: `/marketplace/cart`
- My Orders: `/marketplace/orders`
- Social: `/social`

### Mentor (MENTOR role) - All USER links PLUS:
- Mentor Dashboard: `/mentors/dashboard`
- Seller Dashboard: `/marketplace/seller`
- Create Product: `/marketplace/seller/create-product`
- My Products: `/marketplace/seller/products`
- Seller Orders: `/marketplace/seller/orders`
- Sales Analytics: `/marketplace/seller/analytics`

### Admin (ADMIN/SUPERADMIN role) - All MENTOR links PLUS:
- Admin Dashboard: `/admin`
- User Management: `/admin/users`
- Analytics: `/admin/analytics`
- Marketplace Admin: `/admin/marketplace`
- Payout Management: `/admin/payouts`

---

## 🧪 API Routes (Backend Proxies)

These routes are Next.js API endpoints that forward to the FastAPI backend:

```
/api/session/*              → Session/auth endpoints
/api/v1/*                   → V1 API endpoints
/api/v1x/*                  → V1X (extended) API endpoints
```

Examples:
```
GET  /api/session/me                                    → Current user info
POST /api/session/v1x/marketplace/cart/add              → Add to cart
GET  /api/session/v1x/marketplace/cart                  → Get cart
POST /api/session/v1x/marketplace/checkout              → Create order
GET  /api/session/v1x/seller/analytics                  → Seller analytics
GET  /api/v1x/marketplace/courses                       → List courses
POST /api/coins/balance                                 → Get coin balance
```

---

## 🔍 Query Parameters

### Marketplace
```
/marketplace?search=python         → Search for "python"
/marketplace?category=ml           → Filter by ML category
/marketplace?price_max=50          → Max price filter
/marketplace?sort=price            → Sort by price
```

### Search
```
/marketplace/search?q=python       → Search results for "python"
```

---

## 📊 Dashboard Components

### Mentor Dashboard Layout
```
/mentors/dashboard
├─ Sidebar/BottomNav with links:
│  ├─ Overview → /mentors/dashboard
│  ├─ Earnings → /mentors/dashboard/earnings
│  ├─ Analytics → /mentors/dashboard/analytics
│  ├─ Sessions → /mentors/dashboard/sessions
│  ├─ Students → /mentors/dashboard/students
│  ├─ Payouts → /mentors/dashboard/payouts
│  ├─ Reviews → /mentors/dashboard/reviews
│  └─ Profile → /mentors/dashboard/profile
└─ Main content area
   ├─ Breadcrumb: Home / Section / Page
   ├─ Page title
   ├─ Loading skeletons (while fetching)
   └─ Content
```

### Admin Marketplace Layout
```
/admin/marketplace
├─ 3 Tabs:
│  ├─ Dashboard: Platform metrics
│  ├─ Products: Product approval/management
│  └─ Sellers: Seller management/verification
└─ Content for selected tab
```

---

## ⚡ Quick Access URLs

**Fastest way to get to common pages:**

```bash
# As Student
http://localhost:3000/                    # Home
http://localhost:3000/marketplace         # Browse products
http://localhost:3000/marketplace/cart    # Shopping cart
http://localhost:3000/profile             # My profile

# As Mentor
http://localhost:3000/mentors/dashboard   # Mentor dashboard
http://localhost:3000/marketplace/seller  # Seller dashboard
http://localhost:3000/marketplace/seller/create-product  # Create product

# As Admin
http://localhost:3000/admin               # Admin dashboard
http://localhost:3000/admin/marketplace   # Manage marketplace
http://localhost:3000/admin/payouts       # Manage payouts
```

---

## 🚨 Error Pages

| Code | URL | Meaning |
|------|-----|---------|
| 404 | `/404` or invalid URL | Page not found |
| 403 | `/unauthorized` | Access denied (wrong role) |
| 401 | `/login` | Not authenticated |

---

## 📝 Notes

1. **Environment Variable**: Frontend API base is configured in `src/lib/api.ts`
   - Default: `http://localhost:8001`
   - Can be overridden with `NEXT_PUBLIC_API_BASE` env var

2. **Authentication**: Uses JWT tokens stored in localStorage
   - Middleware checks tokens on protected routes
   - Automatic redirect to login if expired

3. **Development Mode**:
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:8001`

4. **Role-Based Access**:
   - USER: Default role, access to marketplace as buyer
   - MENTOR: Can create products and mentor sessions
   - ADMIN: Can moderate marketplace and users
   - SUPERADMIN: Full system access

---

## 🔗 Related Files

- Frontend routes: `src/middleware.ts`
- API configuration: `src/lib/api.ts`
- Routes constants: `src/lib/routes.ts` (if exists)
- Component pages: `src/pages/`
- Layout components: `src/components/`

---

**Last Updated**: January 27, 2026  
**Status**: ✅ Complete and verified
