# Marketplace URLs - Quick Reference Card

## Seller Dashboard
```
Homepage        → http://localhost:3000/marketplace/seller
Products List   → http://localhost:3000/marketplace/seller/products        ✅ FIXED
Create Product  → http://localhost:3000/marketplace/seller/create-product
Edit Product    → http://localhost:3000/marketplace/seller/create-product?productId=ID
My Orders       → http://localhost:3000/marketplace/seller/orders
Analytics       → http://localhost:3000/marketplace/seller/analytics
```

## Admin Dashboard
```
Marketplace     → http://localhost:3000/admin/marketplace
  ├─ Products    (tab=products or default)
  ├─ Sellers     (tab=sellers)
  └─ Dashboard   metrics
```

## Customer Marketplace
```
Browse Products → http://localhost:3000/marketplace
Shopping Cart   → http://localhost:3000/marketplace/cart
Checkout        → http://localhost:3000/marketplace/checkout
My Orders       → http://localhost:3000/marketplace/orders
```

## Mentor Features
```
Sessions        → http://localhost:3000/mentor/sessions
Availability    → http://localhost:3000/mentor/availability
Verification    → http://localhost:3000/mentor/verification
```

## Jobs & Applications
```
Job Tracker     → http://localhost:3000/jobs
```

## Admin System Pages
```
Main Dashboard  → http://localhost:3000/admin
Analytics       → http://localhost:3000/admin/analytics
Users           → http://localhost:3000/admin/users
Courses         → http://localhost:3000/admin/courses
Mentors         → http://localhost:3000/admin/mentors
Payouts         → http://localhost:3000/admin/payouts
Revenue         → http://localhost:3000/admin/revenue
Audit Log       → http://localhost:3000/admin/audit-log
Sessions        → http://localhost:3000/admin/sessions
Settings        → http://localhost:3000/admin/settings
```

## Test Credentials

### Seller (Mentor)
```
Email:    mentor.sarah@skillforge.com
Password: mentor123
Role:     MENTOR (can sell products)
```

### Admin
```
Email:    admin@skillforge.com
Password: admin123
Role:     ADMIN
```

### Regular User
```
Email:    john.doe@example.com
Password: user123
Role:     USER
```

## API Endpoint Base
```
Backend API: http://localhost:8001
Marketplace: /api/v1x/marketplace/...
Admin:       /api/v1x/marketplace/admin/marketplace/...
```

## Current Status

✅ **WORKING**
- Seller products page now displays products correctly
- Admin marketplace dashboard functional
- Product creation working
- All endpoints responding with correct data

📝 **FIXED TODAY**
- Frontend API path issue (was using `/api/v1x/admin/marketplace/...`)
- Seller products response parsing (was looking for `.products` instead of `.items`)
- Admin dashboard endpoints returning 404 errors

---
See [COMPLETE_MARKETPLACE_URLS.md](COMPLETE_MARKETPLACE_URLS.md) for detailed documentation.
