# 🌐 COMPLETE FRONTEND URLS & USER CREDENTIALS

**Generated**: January 27, 2026  
**Environment**: Development (localhost)

---

## 📍 FRONTEND BASE URLs

### Main Application
```
Frontend URL:  http://localhost:3001
Backend API:   http://localhost:8001
API Docs:      http://localhost:8001/docs
Database:      backend/app/data/skillforge.db
```

---

## 🔐 ALL DEMO USERS & CREDENTIALS

### Admin/System Users

| ID | Email | Password | Role | Name | Status |
|---|---|---|---|---|---|
| 1 | superadmin@skillforge.com | super123 | SUPERADMIN | System SuperAdmin | ✅ Active |
| 2 | admin@skillforge.com | admin123 | ADMIN | System Admin | ✅ Active |

### Regular Users (Students)

| ID | Email | Password | Role | Name | Status |
|---|---|---|---|---|---|
| 3 | john.doe@example.com | john123 | USER | John Doe | ✅ Active |
| 4 | jane.smith@example.com | jane123 | USER | Jane Smith | ✅ Active |
| 5 | bob.wilson@example.com | bob123 | USER | Bob Wilson | ✅ Active |
| 6 | alice.johnson@example.com | alice123 | USER | Alice Johnson | ✅ Active |
| 7 | charlie.brown@example.com | charlie123 | USER | Charlie Brown | ✅ Active |

### Mentor Users (with User accounts)

| ID | Email | Password | Role | Mentor Name | Expertise | Rate/hr | Status |
|---|---|---|---|---|---|---|---|
| 8 | mentor.sarah@skillforge.com | mentor123 | MENTOR | Sarah Chen | Python AI, Web Dev | $75 | ✅ APPROVED |
| 9 | mentor.david@skillforge.com | mentor123 | MENTOR | David Kumar | Web Dev, JavaScript | $65 | ✅ APPROVED |
| 10 | mentor.emily@skillforge.com | mentor123 | MENTOR | Emily Rodriguez | Python AI, ML | $85 | ✅ APPROVED |
| 11 | mentor.james@skillforge.com | mentor123 | MENTOR | James Patterson | DevOps, Cloud | $70 | ✅ APPROVED |

---

## 🛍️ SELLER/MARKETPLACE USERS

Sellers in the marketplace system are mentors who also sell digital products.

### Active Sellers

| Seller ID | User ID | Email | Store Name | Products | Status |
|---|---|---|---|---|---|
| 1 | 8 | mentor.sarah@skillforge.com | Sarah's Resources | 2 | ✅ Active |
| 2 | 9 | mentor.david@skillforge.com | David's Templates | 1 | ✅ Active |
| 3 | 10 | mentor.emily@skillforge.com | Emily's Guides | - | ✅ Active |

### Seller Credentials (Same as Mentor Accounts)
- Email: `mentor.sarah@skillforge.com` | Password: `mentor123`
- Email: `mentor.david@skillforge.com` | Password: `mentor123`
- Email: `mentor.emily@skillforge.com` | Password: `mentor123`
- Email: `mentor.james@skillforge.com` | Password: `mentor123`

---

## 📋 COMPLETE FRONTEND ROUTES (All Pages)

### Authentication Routes
```
/login                    Login page
/signup                   Sign up page
/forgot-password          Password recovery
/reset-password           Password reset form
/security/change-password Change password
```

### Public Routes
```
/                         Home page
/paths                    Learning paths catalog
/paths/[slug]             Specific learning path (e.g., /paths/python-ai)
/watch/[id]               Video player (e.g., /watch/1)
/mentors                  Browse all mentors
/mentors/become           Become a mentor
/mentors/[id]             Mentor profile (e.g., /mentors/1)
/mentors/[id]/book        Book mentor session (e.g., /mentors/1/book)
/marketplace              Marketplace products
/marketplace/[id]         Product details (e.g., /marketplace/1)
/pricing                  Pricing page
/terms                    Terms of service
/privacy                  Privacy policy
/trending                 Trending content
/ui-showcase              Component showcase (dev only)
/status                   Status page
```

### Student/User Routes (Protected)
```
/dashboard                Student dashboard
/my-bookings              My booked mentor sessions
/my-bookings/[id]         Booking details (e.g., /my-bookings/1)
/student/sessions         Student's session history
/student/book-session     Browse and book mentor sessions
/student/book-session/[mentorId]  Book specific mentor (e.g., /student/book-session/1)
/paths/[slug]             Learning path content
/watch/[id]               Video player with progress
/courses                  My enrolled courses
/wishlist                 Wishlist / favorites
/cart                     Shopping cart
/orders                   My orders
/resumes                  My resumes
/resumes/new              Create new resume
/resumes/import           Import resume
/resumes/templates        Resume templates
/resumes/[id]             Resume details (e.g., /resumes/1)
/resumes/compare          Compare resumes
/profile                  My profile
/settings                 Account settings
/social/feed              Social feed
/social/following         Following list
/profile/[username]       User profile (e.g., /profile/john_doe)
/notifications            Notifications
```

### Mentor Routes (Protected)
```
/mentor/verification      Mentor verification setup
/mentor-bookings          My mentor bookings
/mentor-booking           Browse mentor bookings
/mentor-booking/[id]      Booking details (e.g., /mentor-booking/1)
/mentor/dashboard         Mentor dashboard (if exists)
```

### Team Routes (Protected)
```
/teams                    Teams list
/teams/[slug]             Specific team (e.g., /teams/python-devs)
```

### Admin Routes (Protected - ADMIN/SUPERADMIN only)
```
/admin                    Admin dashboard (if exists)
```

### Special Routes
```
/unauthorized             Unauthorized page
/test-api                 API testing page (dev only)
/subscribe                Subscription page
```

---

## 🔗 RECOMMENDED TEST USER PATHS

### Admin Testing (Superadmin)
```
1. Login: http://localhost:3001/login
   Email: superadmin@skillforge.com
   Password: super123
   
2. Access dashboard: http://localhost:3001/dashboard

3. Test admin features (if available)
```

### Student Testing (Regular User)
```
1. Login: http://localhost:3001/login
   Email: john.doe@example.com
   Password: john123
   
2. Dashboard: http://localhost:3001/dashboard

3. Browse mentors: http://localhost:3001/mentors

4. View learning paths: http://localhost:3001/paths

5. Book session: http://localhost:3001/student/book-session

6. My bookings: http://localhost:3001/my-bookings

7. Marketplace: http://localhost:3001/marketplace
```

### Mentor Testing (Mentor User)
```
1. Login: http://localhost:3001/login
   Email: mentor.sarah@skillforge.com
   Password: mentor123
   
2. Mentor verification: http://localhost:3001/mentor/verification

3. View my bookings: http://localhost:3001/mentor-bookings

4. Profile: http://localhost:3001/profile

5. Settings: http://localhost:3001/settings
```

### Seller Testing (Seller User)
```
1. Login as seller: http://localhost:3001/login
   Email: mentor.sarah@skillforge.com
   Password: mentor123
   
2. Go to marketplace: http://localhost:3001/marketplace

3. View products as seller

4. Check sales/orders (if available)
```

---

## 📊 QUICK REFERENCE TABLE

### All Test Accounts (Copy-Paste Ready)

```
USERNAME                          PASSWORD      ROLE        ACCOUNT TYPE
═══════════════════════════════════════════════════════════════════════════
superadmin@skillforge.com         super123      SUPERADMIN  System Admin
admin@skillforge.com              admin123      ADMIN       System Admin
john.doe@example.com              john123       USER        Student
jane.smith@example.com            jane123       USER        Student
bob.wilson@example.com            bob123        USER        Student
alice.johnson@example.com         alice123      USER        Student
charlie.brown@example.com         charlie123    USER        Student
mentor.sarah@skillforge.com       mentor123     MENTOR      Mentor + Seller
mentor.david@skillforge.com       mentor123     MENTOR      Mentor + Seller
mentor.emily@skillforge.com       mentor123     MENTOR      Mentor + Seller
mentor.james@skillforge.com       mentor123     MENTOR      Mentor + Seller
```

---

## 🎯 KEY USER GROUPS

### By User ID Range
- **IDs 1-2**: Admin/System users
- **IDs 3-7**: Regular students
- **IDs 8-11**: Mentor accounts

### By Role
- **SUPERADMIN**: ID 1 (superadmin@skillforge.com)
- **ADMIN**: ID 2 (admin@skillforge.com)
- **USER**: IDs 3-7 (regular students)
- **MENTOR**: IDs 8-11 (mentors)

### By Access Level
- **Full System Access**: ID 1 (superadmin)
- **Admin Access**: ID 2 (admin)
- **Teaching Access**: IDs 8-11 (mentors)
- **Learning Access**: IDs 3-7 (students)

---

## 🔄 COMMON WORKFLOWS

### Register New User
```
1. Go to: http://localhost:3001/signup
2. Enter email and password
3. Verify email (in dev, auto-verified)
4. Redirected to /login
5. Login with credentials
```

### Book a Mentor Session (As Student)
```
1. Login as: john.doe@example.com / john123
2. Go to: http://localhost:3001/mentors
3. Click mentor profile: http://localhost:3001/mentors/8
4. Click "Book Session": http://localhost:3001/mentors/8/book
5. Fill form (date, time, topic)
6. Submit and pay
7. View booked session: http://localhost:3001/my-bookings
```

### Become a Mentor
```
1. Login as regular user
2. Go to: http://localhost:3001/mentors/become
3. Fill mentor form
4. Wait for approval
5. Once approved, login shows mentor features
```

### Sell Digital Product (As Mentor)
```
1. Login as: mentor.sarah@skillforge.com / mentor123
2. Go to: http://localhost:3001/marketplace
3. Create/manage products (if feature available)
4. Monitor sales/earnings
```

### View Payments & Payouts
```
1. Login as mentor
2. Check dashboard for payout info
3. API: http://localhost:8001/api/v1x/mentors/payouts/history
```

---

## 🌍 API ENDPOINTS (Backend)

### Authentication API
```
POST   http://localhost:8001/api/v1/auth/login
POST   http://localhost:8001/api/v1/auth/register
POST   http://localhost:8001/api/v1/auth/logout
POST   http://localhost:8001/api/v1/auth/refresh-token
GET    http://localhost:8001/api/session/me
```

### User API
```
GET    http://localhost:8001/api/v1/users/me
PUT    http://localhost:8001/api/v1/users/me
GET    http://localhost:8001/api/v1/users/[id]
```

### Mentors API
```
GET    http://localhost:8001/api/v1x/mentors
GET    http://localhost:8001/api/v1x/mentors/[id]
POST   http://localhost:8001/api/v1x/mentors
GET    http://localhost:8001/api/v1x/mentors/sessions/my
POST   http://localhost:8001/api/v1x/mentors/sessions
GET    http://localhost:8001/api/v1x/mentors/payouts/history
```

### Courses API
```
GET    http://localhost:8001/api/v1x/courses
GET    http://localhost:8001/api/v1x/courses/[id]
POST   http://localhost:8001/api/v1x/courses/enroll
```

### Marketplace API
```
GET    http://localhost:8001/api/v1x/products
GET    http://localhost:8001/api/v1x/products/[id]
GET    http://localhost:8001/api/v1x/orders
POST   http://localhost:8001/api/v1x/orders
```

### Job Applications API
```
GET    http://localhost:8001/api/v1/job-applications
POST   http://localhost:8001/api/v1/job-applications
```

### Subscriptions API (New)
```
GET    http://localhost:8001/api/v1x/subscriptions/tiers
GET    http://localhost:8001/api/v1x/subscriptions/me
POST   http://localhost:8001/api/v1x/subscriptions/upgrade
```

### Analytics API (New)
```
GET    http://localhost:8001/api/v1x/analytics/users/overview
GET    http://localhost:8001/api/v1x/analytics/revenue/overview
GET    http://localhost:8001/api/v1x/analytics/system-health
```

---

## ⚙️ DEVELOPMENT NOTES

### Running the Application

**Terminal 1 - Frontend**:
```bash
cd d:\python code\sfg\skillforge-global
npm run dev
# Frontend runs on http://localhost:3001
```

**Terminal 2 - Backend**:
```bash
cd d:\python code\sfg\skillforge-global\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
# Backend runs on http://localhost:8001
```

### Seeding Demo Data
```bash
cd backend
python seed_all_demo_data.py
```

### Database
```bash
# View database (SQLite)
sqlite3 backend/app/data/skillforge.db

# List tables
.tables

# Query users
SELECT id, email, role FROM users;

# Query mentors
SELECT id, user_id, expertise, hourly_rate, status FROM mentors;
```

---

## 🔒 SECURITY NOTES

- ✅ All passwords are hashed in database
- ✅ Admin accounts have system-wide access
- ✅ Mentor accounts limited to mentoring features
- ✅ Student accounts limited to learning features
- ✅ Protected routes require authentication
- ✅ HttpOnly cookies used for token storage
- ✅ CORS configured for localhost:3000-3001

### Change Passwords Before Production
```bash
# Do NOT use demo passwords in production
# Change all passwords before deploying
```

---

## 📝 NOTES

1. **Mentor IDs 8-11** are both mentors AND sellers (marketplace)
2. **User ID 1** is superadmin with full system access
3. **Sessions data** includes 8 booked sessions from demo seed
4. **Marketplace products** include 3 demo products from sellers
5. **All test accounts** can be recreated by running `seed_all_demo_data.py`

---

## 📞 QUICK START COMMANDS

```bash
# 1. Start frontend
npm run dev

# 2. Start backend (in separate terminal)
cd backend && uvicorn app.main:app --reload

# 3. Seed demo data
python backend/seed_all_demo_data.py

# 4. Access application
http://localhost:3001

# 5. Login with
john.doe@example.com / john123
```

---

**Created**: January 27, 2026  
**Status**: ✅ Complete & Current
