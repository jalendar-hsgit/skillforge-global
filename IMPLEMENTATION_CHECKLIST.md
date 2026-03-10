# IMPLEMENTATION CHECKLIST - VERIFY & TEST

## 🎯 QUICK VERIFICATION (15 MINUTES)

### Phase 1: Setup (3 minutes)
```
☐ Seed database: python backend/seed_all_demo_data.py
☐ Start backend: cd backend && python -m uvicorn app.main:app --reload
☐ Start frontend: npm run dev (from project root)
☐ Open browser: http://localhost:3000
```

### Phase 2: Test Student Mentor Booking (4 minutes)
```
☐ /mentors page loads (should see 4 mentors)
  ✓ Sarah Chen ($75/hr, 4.8★)
  ✓ David Kumar ($65/hr, 4.7★)
  ✓ Emily Rodriguez ($85/hr, 4.9★)
  ✓ James Patterson ($70/hr, 4.6★)

☐ Filter mentors by expertise (python, web-dev, ml)
☐ View mentor profile (/mentors/1)
  ✓ Shows bio, expertise, rate, reviews
☐ Check availability (/mentors/1/availability)
  ✓ Shows available time slots
☐ Book session (/mentors/1/book)
  ✓ Select date & time
  ✓ Enter topic & notes
  ✓ See booking summary
  ✓ Submit booking
☐ View booked sessions (/dashboard/mentor-sessions)
  ✓ Session shows with status PENDING_CONFIRMATION
```

### Phase 3: Test Seller Features (4 minutes)
```
☐ Login as seller (mentor account)
☐ /marketplace/seller dashboard loads
☐ /marketplace/seller/products
  ✓ Shows 3 demo products
  ✓ Products: Python, Web Dev, ML courses
☐ /marketplace/seller/analytics
  ✓ Shows sales data (chart or table)
☐ /marketplace/seller/earnings
  ✓ Shows earnings summary
  ✓ Shows pending & paid amounts
☐ /marketplace/seller/payouts
  ✓ Shows payout history
☐ /marketplace/seller/create-product
  ✓ Form loads (to create new product)
```

### Phase 4: Test Admin Features (4 minutes)
```
☐ Login as admin (admin@skillforge.com)
☐ /admin dashboard loads
  ✓ Shows 4 metric cards (revenue, users, products, pending)
☐ /admin/marketplace/products
  ✓ Shows product list
  ✓ Filter by pending status
☐ /admin/marketplace/products/[id]/approve
  ✓ Approve/Reject buttons visible
☐ /admin/marketplace/sellers
  ✓ Shows seller list (mentors)
☐ /admin/payouts
  ✓ Shows payout requests
  ✓ Approve/Process buttons visible
☐ /admin/analytics
  ✓ Shows sales, revenue, trending products
☐ /admin/users
  ✓ Shows user list
  ✓ Can view user details
```

---

## 📋 DETAILED IMPLEMENTATION TASKS

### Task 1: Mentor Booking Feature Implementation

**Frontend Components to Create/Update**:
```
✓ Components needed:
  ☐ /pages/mentors/index.tsx (browse mentors)
  ☐ /pages/mentors/[id].tsx (mentor profile)
  ☐ /pages/mentors/[id]/book.tsx (booking form)
  ☐ /pages/mentors/[id]/availability.tsx (calendar)
  ☐ /pages/mentors/[id]/reviews.tsx (reviews list)
  ☐ /pages/dashboard/mentor-sessions.tsx (my sessions)
  ☐ /pages/dashboard/mentor-sessions/[id]/feedback.tsx (feedback)

✓ Components to modify:
  ☐ /src/lib/api.ts (add mentor API methods)
  ☐ /src/components/MentorCard.tsx (display mentor)
  ☐ /src/components/SessionCard.tsx (display session)

✓ Styling:
  ☐ Create /styles/mentors.css
  ☐ Add mentor card styles
  ☐ Add booking form styles
  ☐ Add calendar styles
  ☐ Ensure responsive design
```

**API Integration**:
```
✓ Endpoints to test:
  ☐ GET /api/v1x/mentors (should return 4 mentors)
  ☐ GET /api/v1x/mentors/[id] (mentor profile)
  ☐ GET /api/v1x/mentors/[id]/availability (time slots)
  ☐ GET /api/v1x/mentors/[id]/reviews (mentor reviews)
  ☐ POST /api/v1x/mentors/[id]/book (create booking)
  ☐ GET /api/v1x/dashboard/mentor-sessions (my sessions)
  ☐ POST /api/v1x/dashboard/mentor-sessions/[id]/feedback (feedback)

✓ Test with curl:
  curl http://localhost:8001/api/v1x/mentors
  curl http://localhost:8001/api/v1x/mentors/1
  curl http://localhost:8001/api/v1x/mentors/1/availability
```

**Demo Data Validation**:
```
✓ Database verification:
  ☐ SELECT COUNT(*) FROM mentors; → Should be 4
  ☐ SELECT * FROM mentors; → Shows all 4 with rates
  ☐ SELECT * FROM mentor_availability; → 20+ slots
  ☐ SELECT * FROM mentor_sessions; → 8 sessions

✓ Frontend verification:
  ☐ /mentors page shows 4 mentor cards
  ☐ Each card shows name, expertise, rate, rating
  ☐ Filter works by expertise, rate, rating
  ☐ Mentor profile shows full details
  ☐ Availability calendar displays
  ☐ Can book session
```

### Task 2: Seller Features Implementation

**Frontend Components**:
```
✓ Create/Update pages:
  ☐ /pages/marketplace/seller/index.tsx (dashboard)
  ☐ /pages/marketplace/seller/products.tsx (list products)
  ☐ /pages/marketplace/seller/create-product.tsx (create form)
  ☐ /pages/marketplace/seller/orders.tsx (sales)
  ☐ /pages/marketplace/seller/analytics.tsx (charts)
  ☐ /pages/marketplace/seller/earnings.tsx (earnings)
  ☐ /pages/marketplace/seller/payouts.tsx (payout history)

✓ Styling:
  ☐ Create /styles/seller.css
  ☐ Dashboard card styles
  ☐ Product list table styles
  ☐ Analytics chart styles
```

**API Integration**:
```
✓ Endpoints to test:
  ☐ GET /api/v1x/seller/products (returns 3 products)
  ☐ GET /api/v1x/seller/analytics/sales (sales data)
  ☐ GET /api/v1x/seller/analytics/earnings (earnings)
  ☐ GET /api/v1x/seller/payouts (payout history)

✓ Test with auth:
  # First get token by logging in as seller
  curl -X POST http://localhost:8001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"seller@email.com","password":"password"}'
  
  # Then use token in request
  curl -H "Authorization: Bearer {TOKEN}" \
    http://localhost:8001/api/v1x/seller/products
```

**Demo Data Validation**:
```
✓ Database verification:
  ☐ SELECT COUNT(*) FROM digital_products; → Should be 3
  ☐ SELECT * FROM digital_products; → Shows 3 products
  ☐ SELECT * FROM orders; → Shows sales data

✓ Frontend verification:
  ☐ Seller dashboard loads
  ☐ Products list shows 3 items
  ☐ Analytics shows sales chart
  ☐ Earnings shows totals
  ☐ Payouts shows history
```

### Task 3: Admin Features Implementation

**Frontend Components**:
```
✓ Create/Update pages:
  ☐ /pages/admin/index.tsx (dashboard)
  ☐ /pages/admin/marketplace.tsx (product approval)
  ☐ /pages/admin/payouts.tsx (payout management)
  ☐ /pages/admin/users.tsx (user management)
  ☐ /pages/admin/analytics.tsx (platform analytics)
  ☐ /pages/admin/settings.tsx (system settings)

✓ Components:
  ☐ AdminDashboard with metric cards
  ☐ ProductApprovalTable with approve/reject buttons
  ☐ PayoutManagement with approve/process buttons
  ☐ UserManagement with role/suspend options
  ☐ AnalyticsDashboard with charts

✓ Styling:
  ☐ Create /styles/admin.css
  ☐ Metric card styles (4 cards layout)
  ☐ Table styles with action buttons
  ☐ Chart container styles
```

**API Integration**:
```
✓ Endpoints to test:
  ☐ GET /api/v1x/admin/analytics/dashboard (metrics)
  ☐ GET /api/v1x/admin/products?status=pending (products)
  ☐ POST /api/v1x/admin/products/[id]/approve (approve)
  ☐ POST /api/v1x/admin/products/[id]/reject (reject)
  ☐ GET /api/v1x/admin/sellers (sellers)
  ☐ POST /api/v1x/admin/marketplace/sellers/[id]/verify (verify)
  ☐ GET /api/v1x/admin/payouts?status=pending (payouts)
  ☐ POST /api/v1x/admin/payouts/[id]/approve (approve)
  ☐ POST /api/v1x/admin/payouts/[id]/process (process)

✓ Test with admin auth:
  curl -X POST http://localhost:8001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@skillforge.com","password":"password"}'
```

**Demo Data Validation**:
```
✓ Database verification:
  ☐ SELECT * FROM users WHERE role='ADMIN'; → 2 admins
  ☐ SELECT COUNT(*) FROM digital_products; → 3 products
  ☐ SELECT * FROM payouts; → Shows payout requests
  ☐ SELECT COUNT(*) FROM users; → 11 users total

✓ Frontend verification:
  ☐ Admin dashboard shows metrics
  ☐ Product approval page shows 3 products
  ☐ Can approve/reject products
  ☐ Seller list shows mentors
  ☐ Can verify sellers
  ☐ Payout page shows requests
  ☐ Can approve/process payouts
```

### Task 4: Theme & Styling Implementation

**CSS System**:
```
✓ Create files:
  ☐ /styles/theme.css (color vars, spacing)
  ☐ /styles/components.css (buttons, cards, tables)
  ☐ /styles/layouts.css (navbar, sidebar, grid)
  ☐ /styles/responsive.css (mobile, tablet, desktop)

✓ Theme variables:
  ☐ Primary colors (7 colors)
  ☐ Status badges (7 badge colors)
  ☐ Spacing scale (5 sizes)
  ☐ Typography scale (5 sizes)
  ☐ Shadow/border styles

✓ Components styled:
  ☐ Buttons (primary, success, danger, etc)
  ☐ Cards (mentor, product, session)
  ☐ Tables (products, orders, payouts)
  ☐ Forms (inputs, selects, textareas)
  ☐ Badges (pending, approved, rejected)
  ☐ Modals (confirm dialogs)
  ☐ Navigation (navbar, sidebar)

✓ Responsive design:
  ☐ Desktop: Full layout with sidebar
  ☐ Tablet: Collapsible sidebar
  ☐ Mobile: Hamburger menu, single column
```

**Color Verification**:
```
✓ Test colors in browser:
  ☐ Primary buttons are blue (#007BFF)
  ☐ Success badges are green (#28A745)
  ☐ Warning badges are amber (#FFC107)
  ☐ Danger badges are red (#DC3545)
  ☐ Text is dark (#212529)
  ☐ Backgrounds are light (#F8F9FA)
```

---

## 🧪 TESTING SCENARIOS

### Scenario 1: Student Books Mentor
```
1. Login as: john.doe@example.com / password
2. Go to /mentors
3. See 4 mentors displayed
4. Click on Sarah Chen profile
5. View /mentors/1 with full details
6. Check /mentors/1/availability
7. Go to /mentors/1/book
8. Select date: 2026-02-03
9. Select time: 09:00
10. Enter topic: "Python Web Development"
11. Click "Confirm Booking"
12. Check /dashboard/mentor-sessions
13. Session should show PENDING_CONFIRMATION status
```

**Expected Result**: ✓ Session created, mentor notified, student can see booking

### Scenario 2: Seller Creates & Sells Product
```
1. Login as seller: Use mentor account (has role=MENTOR)
2. Go to /marketplace/seller
3. See dashboard with 3 products
4. Go to /marketplace/seller/products
5. See product list with Python, Web Dev, ML courses
6. Click on product to view details
7. Go to /marketplace/seller/analytics
8. See sales chart
9. Go to /marketplace/seller/earnings
10. See earnings breakdown by product
11. Go to /marketplace/seller/payouts
12. See payout history
13. Request payout via API: POST /api/v1x/seller/request-payout
```

**Expected Result**: ✓ Seller can see all products, sales, earnings, and payouts

### Scenario 3: Admin Approves Product & Payout
```
1. Login as admin: admin@skillforge.com / password
2. Go to /admin
3. See dashboard with 4 metrics
4. Click pending approvals (should show pending products)
5. Go to /admin/marketplace/products
6. See product list with status column
7. Click product to approve
8. Click "Approve" button
9. Product status changes to PUBLISHED
10. Go to /admin/payouts
11. See payout requests
12. Click payout to review
13. Click "Approve" button (status → APPROVED)
14. Click "Process to Bank" (status → PROCESSED)
```

**Expected Result**: ✓ Admin can approve products and process payouts

---

## 🔍 ERROR CHECKING GUIDE

### If Pages Show 404
```
1. Check URL spelling (case-sensitive)
2. Check file exists: /pages/[path].tsx
3. Check route registered in backend
4. Check token/auth headers if required
5. Restart both servers
```

### If No Demo Data Shows
```
1. Run seed again: python seed_all_demo_data.py
2. Check database: sqlite3 backend/app/data/skillforge.db
3. Verify mentors: SELECT COUNT(*) FROM mentors; → 4
4. Verify products: SELECT COUNT(*) FROM digital_products; → 3
5. Check API response: curl http://localhost:8001/api/v1x/mentors
6. Check browser console for errors
```

### If Styling Broken
```
1. Check CSS file imported in _app.tsx
2. Verify color variable names match
3. Check browser DevTools for CSS errors
4. Clear cache: Ctrl+Shift+Delete
5. Restart frontend: npm run dev
```

### If API Returns Error
```
1. Check auth token in headers
2. Verify user role (admin needs role=ADMIN)
3. Check API endpoint exists in backend
4. Check request body format
5. Review backend logs for error message
```

---

## ✅ SIGN-OFF CHECKLIST

### Backend Ready
- [ ] Database seeded (11 users, 4 mentors, 3 products)
- [ ] All API endpoints returning data
- [ ] Auth working (login returns token)
- [ ] Mentor endpoints returning 4 mentors
- [ ] Seller endpoints returning products & analytics
- [ ] Admin endpoints returning metrics & manageable items
- [ ] No 500 errors in logs

### Frontend Ready
- [ ] All 90+ pages accessible
- [ ] No 404 errors on key pages
- [ ] Demo data displays (mentors, products, users)
- [ ] Forms submit correctly
- [ ] Navigation works
- [ ] Responsive design verified
- [ ] No console errors

### Features Working
- [ ] Student can browse & book mentors
- [ ] Seller can view products & earnings
- [ ] Admin can approve products & payouts
- [ ] Theme colors applied correctly
- [ ] All status badges show correct colors
- [ ] Charts/analytics display data

---

**Status**: Ready for implementation and testing! ✅

Follow the checklist above to verify all components are working correctly.
