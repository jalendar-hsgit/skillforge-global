# SKILLFORGE GLOBAL - QUICK START GUIDE FOR TESTING

## 🚀 GET STARTED IN 5 MINUTES

### Terminal 1: Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```
✅ Look for: "Uvicorn running on http://0.0.0.0:8001"

### Terminal 2: Start Frontend
```bash
npm run dev
```
✅ Look for: "ready - started server on 0.0.0.0:3000"

### Terminal 3: Open Browser
```
http://localhost:3000
```

---

## 🎯 TEST IN 10 MINUTES

### Test 1: Student Buys Product (5 minutes)
```
1. Click "Sign Up" → Register as Student
2. Email: test-student@example.com | Password: Test123
3. Navigate to "Marketplace"
4. Add "Python Fundamentals" to cart ($19.99)
5. Proceed to checkout
6. Pay with: 4242 4242 4242 4242 (Stripe test card)
   Expiry: 12/34 | CVC: 123
7. Confirm order ✅
```

### Test 2: Seller Creates Product (3 minutes)
```
1. Sign up new account as "Seller"
2. Go to "Seller Dashboard"
3. Click "Create Product"
4. Title: "Test Product" | Price: $29.99
5. Upload any file
6. Submit for approval
7. Product shows as PENDING_APPROVAL ✅
```

### Test 3: Admin Approves Product (2 minutes)
```
1. Log out, login as admin@skillforge.com
2. Go to Admin > Products
3. Find pending product
4. Click "Approve"
5. Product status changes to PUBLISHED ✅
```

---

## 📊 DATABASE CHECK

### View Current Data
```bash
cd backend
python -c "
import sqlite3
conn = sqlite3.connect('app/data/skillforge.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
users = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM digital_products')
products = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM product_purchases')
purchases = cursor.fetchone()[0]
print(f'Users: {users} | Products: {products} | Purchases: {purchases}')
conn.close()
"
```

### Seed Demo Data
```bash
cd backend
python seed_all_demo_data.py
```

---

## 🔑 DEFAULT TEST ACCOUNTS

### Admin
```
Email: admin@skillforge.com
Password: (check seed_admin_users.py)
Role: ADMIN
```

### Test Mentors
```
Sarah Chen (sarah@skillforge.com)
David Kumar (david@skillforge.com)
Emily Rodriguez (emily@skillforge.com)
James Patterson (james@skillforge.com)
```

### Test Products (Already in DB)
```
1. Python Fundamentals - $19.99 (Sarah)
2. React Templates - $29.99 (David)
3. ML Training Guide - $49.99 (Emily)
```

---

## 🛒 COMPLETE PURCHASE FLOW

```
Customer Registration
   ↓
Browse Products: GET /api/v1x/marketplace/products
   ↓
Add to Cart: POST /api/v1x/marketplace/cart/items
   ↓
View Cart: GET /api/v1x/marketplace/cart
   ↓
Checkout: POST /api/v1x/marketplace/checkout
   ↓
Stripe Payment: POST /api/v1x/payments/charge
   ↓
Order Confirmation: Created in database
   ↓
Email Notification: Sent (if SMTP configured)
   ↓
Product Download: GET /api/v1x/marketplace/product-files/{id}
```

---

## 💰 REVENUE FLOW

```
Customer pays $19.99
   ↓
Stripe charges card $19.99
   ↓
Platform takes 30% = $5.99
   ↓
Seller gets 70% = $13.99
   ↓
Seller balance updated
   ↓
When balance > $100: Can request payout
   ↓
Admin approves payout
   ↓
Seller receives payment to Stripe Connect account
```

---

## 📱 KEY ENDPOINTS FOR TESTING

### Authentication
```
POST   /api/v1x/auth/register          - Create new user
POST   /api/v1x/auth/login             - Login user
POST   /api/v1x/auth/logout            - Logout user
POST   /api/v1x/auth/refresh-token     - Refresh JWT
```

### Marketplace (Student)
```
GET    /api/v1x/marketplace/products   - List products
GET    /api/v1x/marketplace/products/{id} - Get product detail
POST   /api/v1x/marketplace/cart/items - Add to cart
GET    /api/v1x/marketplace/cart       - View cart
POST   /api/v1x/marketplace/checkout   - Place order
GET    /api/v1x/marketplace/orders     - View orders
```

### Seller
```
POST   /api/v1x/seller/register        - Register as seller
PUT    /api/v1x/seller/profile         - Update profile
POST   /api/v1x/seller/products        - Create product
GET    /api/v1x/seller/products        - List seller products
POST   /api/v1x/seller/products/{id}/upload - Upload file
GET    /api/v1x/seller/analytics/sales - View sales
GET    /api/v1x/seller/analytics/earnings - View earnings
POST   /api/v1x/seller/payouts/request - Request payout
```

### Mentor
```
POST   /api/v1x/mentors/register       - Register as mentor
PUT    /api/v1x/mentors/{id}/profile   - Update profile
POST   /api/v1x/mentors/availability   - Set availability
GET    /api/v1x/mentors/sessions       - View sessions
PUT    /api/v1x/mentors/sessions/{id}/confirm - Confirm session
GET    /api/v1x/mentors/analytics/earnings - View earnings
```

### Admin
```
GET    /api/v1x/admin/analytics/dashboard - View dashboard
GET    /api/v1x/admin/products         - List all products
PUT    /api/v1x/admin/products/{id}/approve - Approve product
GET    /api/v1x/admin/sellers          - List sellers
PUT    /api/v1x/admin/sellers/{id}/verify - Verify seller
GET    /api/v1x/admin/payouts          - View payouts
PUT    /api/v1x/admin/payouts/{id}/approve - Approve payout
```

### Payments
```
POST   /api/v1x/payments/charge        - Process payment
GET    /api/v1x/payments/methods       - List payment methods
POST   /api/v1x/payments/methods       - Add payment method
```

---

## 🧪 QUICK API TESTS WITH CURL

### Test Backend Health
```bash
curl http://localhost:8001/api/v1x/health
```

### Get All Products
```bash
curl http://localhost:8001/api/v1x/marketplace/products
```

### Get User (with token)
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8001/api/v1x/users/me
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Backend server running (http://localhost:8001)
- [ ] Frontend server running (http://localhost:3000)
- [ ] Can access login page
- [ ] Can register new student account
- [ ] Can login with new account
- [ ] Can see marketplace products (3+ products)
- [ ] Can add product to cart
- [ ] Can proceed to checkout
- [ ] Can enter payment info
- [ ] Payment succeeds with Stripe test card
- [ ] Order appears in order history
- [ ] Can download purchased product
- [ ] Can login as seller
- [ ] Can create new product (pending approval)
- [ ] Can login as admin
- [ ] Can approve product
- [ ] Admin dashboard shows correct data

---

## 🐛 TROUBLESHOOTING

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Install dependencies
cd backend
pip install -r requirements.txt

# Try running with verbose output
python -m uvicorn app.main:app --reload --log-level debug
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 16+

# Install dependencies
npm install

# Clear cache
npm cache clean --force
npm install

# Try running
npm run dev
```

### Can't connect to backend
```bash
# Check if backend is actually running
curl http://localhost:8001/docs

# Check if ports are in use
# Windows: netstat -ano | findstr :8001
# Mac/Linux: lsof -i :8001
```

### Database errors
```bash
# Reset database
cd backend
rm app/data/skillforge.db*
python init_db.py
python seed_all_demo_data.py
```

### Payment processing fails
- Verify using Stripe test card: `4242 4242 4242 4242`
- Check backend logs for Stripe error details
- Verify Stripe API keys are set in environment

---

## 📈 TESTING PROGRESSION

### Day 1 - Basic Flow (2 hours)
1. ✅ Start servers (5 min)
2. ✅ Student signup & login (15 min)
3. ✅ Browse marketplace (10 min)
4. ✅ Add to cart & checkout (15 min)
5. ✅ Make test payment (15 min)
6. ✅ Verify order (10 min)

### Day 2 - All Roles (3 hours)
1. ✅ Test seller workflow (45 min)
2. ✅ Test mentor workflow (45 min)
3. ✅ Test admin controls (45 min)
4. ✅ Verify database state (15 min)

### Day 3 - Edge Cases (2 hours)
1. ✅ Test refunds
2. ✅ Test payout requests
3. ✅ Test admin payouts
4. ✅ Test error handling
5. ✅ Test role-based access control

### Day 4 - Load Testing (2 hours)
1. ✅ Multiple concurrent users
2. ✅ High volume purchases
3. ✅ Analytics accuracy
4. ✅ Database performance

### Day 5 - Production Prep (2 hours)
1. ✅ Final bug fixes
2. ✅ Security audit
3. ✅ Performance optimization
4. ✅ Production deployment

---

## 📞 SUPPORT

### Documentation Files
- `SYSTEM_VERIFICATION_COMPLETE.md` - Full system status
- `COMPLETE_TESTING_GUIDE.md` - Detailed test steps
- `PENDING_IMPLEMENTATION_CHECKLIST.md` - Implementation status
- `FRONTEND_URLS_COMPLETE.md` - All frontend routes
- `API_ROUTES_COMPLETE.md` - All API endpoints

### Key Files
- Backend: `backend/app/main.py`
- Frontend: `src/pages/`
- Database: `backend/app/data/skillforge.db`
- Tests: `backend/tests/`

---

## 🎉 EXPECTED RESULTS

After 5 minutes of setup:
```
✅ Backend running
✅ Frontend running  
✅ Can access marketplace
✅ Can register user
✅ Can login
✅ Can buy product with Stripe test card
✅ Order confirmed
✅ System is 100% OPERATIONAL
```

---

## STATUS: 🚀 READY FOR TESTING

**All systems operational. Begin testing now.**

Start with Terminal 1 (Backend), Terminal 2 (Frontend), then open http://localhost:3000
