# 🎯 SkillForge Admin - Testing Quick Start

## 📋 Prerequisites Checklist

- [ ] Backend running: `uvicorn app.main:app --reload --port 8001`
- [ ] Frontend running: `npm run dev`
- [ ] Admin user created in database
- [ ] Database has some test data (users, sessions, courses)

---

## 🚀 Fastest Way to Test (3 Steps)

### Step 1: Run the Helper Script
```powershell
.\test_admin_helper.ps1
```

**This interactive menu lets you:**
- Create admin user
- Test login
- Open admin dashboard
- Check server status
- View all URLs

### Step 2: Login as Admin
1. Go to: http://localhost:3000/login
2. Email: `admin@skillforge.test`
3. Password: `Admin123!`

### Step 3: Access Admin Dashboard
http://localhost:3000/admin

**You'll see 11 quick links to all admin features!**

---

## 📱 All Admin Pages (Click to Test)

### Core Features
1. **Dashboard** → http://localhost:3000/admin
2. **Users** → http://localhost:3000/admin/users
3. **Mentors** → http://localhost:3000/admin/mentors
4. **Sessions** → http://localhost:3000/admin/sessions
5. **Audit Logs** → http://localhost:3000/admin/logs
6. **Settings** → http://localhost:3000/admin/settings

### Analytics & Insights
7. **Analytics** → http://localhost:3000/admin/analytics
8. **User Analytics** → http://localhost:3000/admin/user-analytics
9. **Revenue** → http://localhost:3000/admin/revenue

### Content & Commerce
10. **Courses** → http://localhost:3000/admin/courses-enhanced
11. **Marketplace** → http://localhost:3000/admin/marketplace
12. **Notifications** → http://localhost:3000/admin/notifications

---

## 🔌 API Testing (Use Postman or curl)

### Quick API Tests

#### 1. Login (Get Auth Cookie)
```powershell
$body = @{
    email = "admin@skillforge.test"
    password = "Admin123!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -SessionVariable session

# Save session for subsequent requests
```

#### 2. Get Dashboard Stats
```powershell
Invoke-WebRequest -Uri "http://localhost:8001/api/v1x/admin/dashboard/stats" `
    -WebSession $session | 
    Select-Object -ExpandProperty Content |
    ConvertFrom-Json
```

#### 3. List Users
```powershell
Invoke-WebRequest -Uri "http://localhost:8001/api/v1x/admin/users" `
    -WebSession $session |
    Select-Object -ExpandProperty Content |
    ConvertFrom-Json
```

---

## 🧪 Automated Testing

### Run Complete Test Suite
```powershell
cd backend
python test_admin_complete.py
```

**This tests all 53 endpoints automatically!**

### What Gets Tested
- ✅ Authentication (login, signup, /me)
- ✅ Dashboard stats
- ✅ User management (CRUD)
- ✅ Mentor management
- ✅ Session management
- ✅ Audit logs
- ✅ Platform settings
- ✅ Analytics dashboard
- ✅ Course management
- ✅ Revenue dashboard
- ✅ Marketplace admin
- ✅ User analytics (DAU/WAU/MAU)
- ✅ Email & notifications
- ✅ Rate limiting

---

## 📊 Feature Testing Checklist

### Analytics Dashboard
- [ ] Access page: `/admin/analytics`
- [ ] View session completion rates
- [ ] See top mentors leaderboard
- [ ] Check user growth metrics

### User Analytics
- [ ] Access page: `/admin/user-analytics`
- [ ] View DAU/WAU/MAU on Overview tab
- [ ] Check retention cohorts on Cohorts tab
- [ ] Review user segmentation on Activity tab
- [ ] Identify at-risk users on Churn Risk tab

### Revenue Dashboard
- [ ] Access page: `/admin/revenue`
- [ ] View revenue overview cards
- [ ] Check subscription metrics (MRR)
- [ ] Review top earning mentors
- [ ] Export transaction history to CSV

### Marketplace Admin
- [ ] Access page: `/admin/marketplace`
- [ ] View marketplace statistics
- [ ] Review all orders
- [ ] Create new coupon
- [ ] Toggle coupon active status
- [ ] Process a refund

### Course Management
- [ ] Access page: `/admin/courses-enhanced`
- [ ] Create new course
- [ ] Edit existing course
- [ ] Delete a course
- [ ] Bulk delete multiple courses
- [ ] Toggle featured status
- [ ] Export courses to CSV

### Email & Notifications
- [ ] Access page: `/admin/notifications`
- [ ] Create email template
- [ ] Send broadcast email (all users)
- [ ] Send to specific segment (students/mentors)
- [ ] View notification history
- [ ] Check notification statistics

### User Management
- [ ] Access page: `/admin/users`
- [ ] Search for users
- [ ] Filter by role
- [ ] Change user role
- [ ] Suspend a user
- [ ] Delete a user

### Mentor Management
- [ ] Access page: `/admin/mentors`
- [ ] View pending applications
- [ ] Approve a mentor
- [ ] Reject a mentor
- [ ] View mentor details

### Session Management
- [ ] Access page: `/admin/sessions`
- [ ] View all sessions
- [ ] Filter sessions by status
- [ ] View session statistics
- [ ] Cancel a session

### Audit Logs
- [ ] Access page: `/admin/logs`
- [ ] View recent activity
- [ ] Filter by action type
- [ ] Filter by admin
- [ ] See all details (IP, user agent, timestamp)

### Platform Settings
- [ ] Access page: `/admin/settings`
- [ ] Toggle maintenance mode
- [ ] Toggle registration
- [ ] Set featured course limit
- [ ] Update mentor approval requirement

---

## 🎯 Quick Verification Tests

### Test 1: Basic Access (2 minutes)
1. Login as admin
2. Access dashboard
3. Click each quick link
4. Verify all pages load

### Test 2: CRUD Operations (5 minutes)
1. Create a course
2. Edit the course
3. Toggle featured status
4. Delete the course
5. Verify in audit logs

### Test 3: Analytics (3 minutes)
1. Open Analytics page
2. Check all metrics display
3. Open User Analytics page
4. Check DAU/WAU/MAU
5. Review churn risk users

### Test 4: Notifications (5 minutes)
1. Create email template
2. Send test broadcast
3. Check history
4. View statistics
5. Delete template

### Test 5: Complete Flow (10 minutes)
1. Create user → User Management
2. Approve as mentor → Mentor Management
3. Create course → Course Management
4. Send welcome email → Notifications
5. View all actions → Audit Logs

---

## 🔍 Common Issues & Solutions

### Issue: "403 Forbidden" on admin pages
**Solution:** User doesn't have admin role. Update in database:
```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'your@email.com';
```

### Issue: "No data to display"
**Solution:** Create test data using seed scripts or signup/create manually

### Issue: "Email not sending"
**Solution:** Email service not configured. See `EMAIL_TESTING_GUIDE.md`

### Issue: "Template not found" error
**Solution:** Templates stored in memory, restart clears them. Implement DB storage for persistence.

### Issue: Pages load but no stats
**Solution:** Database is empty. Create users, sessions, courses for meaningful stats.

---

## 📈 Expected Results

### Dashboard Stats (if data exists)
- Total users: 67+
- Total mentors: 10+
- Total sessions: 50+
- Total revenue: $1000+

### User Analytics
- DAU: 5-20 users
- WAU: 20-50 users
- MAU: 50-100 users
- Growth rate: varies

### Revenue Overview
- Session revenue: $500+
- Subscription revenue: $300+
- Platform revenue (30%): calculated
- Mentor payouts (70%): calculated

---

## 🎉 Success Criteria

✅ **All 12 admin pages load without errors**  
✅ **Can create, read, update, delete across all features**  
✅ **Audit logs capture all admin actions**  
✅ **Statistics display correctly (if data exists)**  
✅ **CSV exports work on applicable pages**  
✅ **Email system ready (even if not configured)**  
✅ **Authentication works (login/logout)**  
✅ **Role-based access enforced**

---

## 📞 Need Help?

### Documentation Files
- `ADMIN_URLS_COMPLETE.md` - All URLs and endpoints
- `ADMIN_IMPLEMENTATION_SUMMARY.md` - Technical details
- `EMAIL_NOTIFICATIONS_SUMMARY.md` - Email system docs

### Testing Tools
- `test_admin_complete.py` - Automated test suite
- `test_admin_helper.ps1` - Interactive testing menu

### API Documentation
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

---

## 🚀 Quick Commands Reference

```powershell
# Start servers
cd backend; uvicorn app.main:app --reload --port 8001
npm run dev

# Run tests
.\test_admin_helper.ps1
python backend/test_admin_complete.py

# Create admin user
# Use option 4 in test_admin_helper.ps1

# Open admin dashboard
start http://localhost:3000/admin

# Open API docs
start http://localhost:8001/docs
```

---

**Happy Testing! 🎯**

All 14 frontend pages and 53 backend endpoints are ready for your testing!
