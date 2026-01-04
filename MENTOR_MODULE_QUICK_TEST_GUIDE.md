# Mentor Module - Quick Testing & Verification Guide

**Status**: ✅ Complete and Ready to Test

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Start Backend Server
```bash
cd backend
pip install -r requirements.txt
python seed_complete_mentors.py  # If needed - populate initial data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete
```

### Step 2: Start Frontend Server
```bash
npm install  # If needed
npm run dev
```

**Expected Output**:
```
> next dev
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
```

### Step 3: Login as Admin
- **URL**: http://localhost:3000/admin/mentors
- **Email**: admin@test.com
- **Password**: password123

### Step 4: Verify Mentor Data
- Should see: **5 mentors** in the system
- Should show: **Stats dashboard** with counts
- Should display: **Filter buttons** (All, Pending, Approved, Rejected, Suspended)
- Should see: **Mentor cards** with information

---

## 👨‍💼 Test User Credentials

### Admin Account
```
Email:    admin@test.com
Password: password123
Role:     Admin
Access:   All admin features
```

### Mentor Accounts (5 Total)
| Name | Email | Specialty | Rate | Status |
|------|-------|-----------|------|--------|
| Alex Johnson | mentor.python@test.com | Python/AI | $85/hr | ✅ Approved |
| Sarah Chen | mentor.web@test.com | Web Dev | $75/hr | ✅ Approved |
| James Wilson | mentor.cloud@test.com | Cloud/AWS | $95/hr | ✅ Approved |
| Emma Rodriguez | mentor.mobile@test.com | Mobile/iOS | $65/hr | ✅ Approved |
| David Kumar | mentor.data@test.com | Data Science | $90/hr | ✅ Approved |

**Password for all mentors**: `password123`

### Student Accounts (3 Total)
```
1. alice@test.com   / password123
2. bob@test.com     / password123
3. charlie@test.com / password123
```

---

## 📊 Expected Data in Database

### Mentors
- **Count**: 5 approved mentors
- **Average Rating**: 4.66⭐ (across 30 reviews)
- **Total Sessions**: 45 (30 completed, 15 upcoming)
- **Total Reviews**: 30
- **Availability Slots**: 20

### Sample Mentor Profile (Alex Johnson)
```
Name:       Alex Johnson
Email:      mentor.python@test.com
Expertise:  Python, AI/ML, Data Analysis
Rate:       $85/hour
Status:     Approved ✅
Sessions:   9 total (all completed)
Rating:     4.7⭐ (from reviews)
Bio:        "Experienced Python developer with focus on AI/ML..."
```

---

## ✅ Frontend Testing Checklist

### Admin Mentors Page (src/pages/admin/mentors.tsx)

#### 1. Page Load
- [ ] Page loads without errors
- [ ] Statistics dashboard visible at top
- [ ] Showing 5 total mentors
- [ ] Filter buttons visible (All, Pending, Approved, Rejected, Suspended)

#### 2. Statistics Display
- [ ] Total Mentors: 5
- [ ] Pending: 0
- [ ] Approved: 5
- [ ] Rejected: 0
- [ ] Suspended: 0
- [ ] Avg Rating: 4.66⭐

#### 3. Mentor Cards
- [ ] Cards show mentor names
- [ ] Email addresses visible
- [ ] Status badges with icons (✅ Approved)
- [ ] Click to expand shows full details
- [ ] Bio visible when expanded
- [ ] Expertise tags displayed
- [ ] Hourly rate shown
- [ ] Session count visible
- [ ] Rating displayed

#### 4. Filtering
- [ ] "All" shows 5 mentors
- [ ] "Approved" shows 5 mentors
- [ ] "Pending" shows 0 mentors
- [ ] "Rejected" shows 0 mentors
- [ ] "Suspended" shows 0 mentors
- [ ] Filter buttons highlight when active

#### 5. Actions
- [ ] Approved mentors show "Suspend" button
- [ ] "Suspend" button works (confirmation dialog appears)
- [ ] Suspend action updates status to "suspended"
- [ ] After suspend, card shows suspension notice
- [ ] No "Approve" or "Reject" buttons on approved mentors

#### 6. Error Handling
- [ ] Error messages display on failures
- [ ] Success messages show after actions
- [ ] Messages auto-dismiss after 3 seconds
- [ ] Loading states work properly

#### 7. UI/UX
- [ ] Icons display correctly (green ✓, red ✗, orange ⚠️, yellow ⏳)
- [ ] Cards have proper spacing and shadows
- [ ] Responsive on mobile (test with dev tools)
- [ ] Hover effects visible
- [ ] Colors match design

---

## 🔌 Backend API Testing

### Health Check
```bash
curl http://localhost:8001/healthz
```

**Expected Response**:
```json
{"status": "ok"}
```

### Get All Mentors
```bash
curl http://localhost:8001/api/v1x/mentors
```

**Expected Response** (HTTP 200):
```json
{
  "mentors": [
    {
      "id": "...",
      "user_id": "...",
      "user": {
        "id": "...",
        "email": "mentor.python@test.com",
        "full_name": "Alex Johnson"
      },
      "bio": "Experienced Python developer...",
      "expertise": "Python, AI/ML, Data Analysis",
      "hourly_rate": 85.0,
      "status": "approved",
      "total_sessions": 9,
      "average_rating": 4.7,
      "created_at": "2024-01-01T00:00:00"
    },
    ...
  ],
  "total": 5
}
```

### Get Mentor Profile
```bash
curl http://localhost:8001/api/v1x/mentors/{mentor_id}
```

**Expected Response**: Full mentor profile with all details

### Admin: Get Applications
```bash
curl -H "Authorization: Bearer {admin_token}" \
  http://localhost:8001/api/v1x/mentors/admin/applications
```

**Expected Response**: List of all mentor applications

### Admin: Update Status
```bash
curl -X PATCH \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"status":"suspended"}' \
  http://localhost:8001/api/v1x/mentors/{mentor_id}/admin/status
```

**Expected Response** (HTTP 200):
```json
{"status": "suspended", "message": "Mentor status updated"}
```

---

## 🧪 Run Full Test Suite

### Execute Tests
```bash
cd backend
python test_mentor_apis.py
```

### Expected Test Results
```
=== MENTOR MODULE - API TEST SUITE ===

Test 1: Check Mentor Eligibility ✅ PASSED
Test 2: Create Mentor Application ✅ PASSED
Test 3: Get Mentor Profile ✅ PASSED
Test 4: List Mentors ✅ PASSED
Test 5: Get Availability Slots ✅ PASSED
Test 6: Book a Session ✅ PASSED
Test 7: Get Sessions ✅ PASSED
Test 8: Submit Review ✅ PASSED
Test 9: Mentor Portal Dashboard ✅ PASSED
Test 10: Get Earnings ✅ PASSED

===== SUMMARY =====
Total Tests: 10
Passed: 10 ✅
Failed: 0
Success Rate: 100%
```

---

## 🗄️ Database Verification

### Check Mentor Count
```bash
cd backend
python -c "
from app.core.db import SessionLocal
from app.modelsx.mentor import Mentor
db = SessionLocal()
count = db.query(Mentor).count()
print(f'Total mentors: {count}')
"
```

**Expected Output**:
```
Total mentors: 5
```

### Check Sessions Count
```bash
python -c "
from app.core.db import SessionLocal
from app.modelsx.mentor import MentorSession
db = SessionLocal()
count = db.query(MentorSession).count()
print(f'Total sessions: {count}')
"
```

**Expected Output**:
```
Total sessions: 45
```

### Check Reviews Count
```bash
python -c "
from app.core.db import SessionLocal
from app.modelsx.mentor import MentorReview
db = SessionLocal()
count = db.query(MentorReview).count()
print(f'Total reviews: {count}')
"
```

**Expected Output**:
```
Total reviews: 30
```

---

## 🔍 Common Issues & Solutions

### Issue 1: "No mentors data"
**Solution**: Run seeding script
```bash
cd backend
python seed_complete_mentors.py
```

### Issue 2: Frontend shows loading spinner forever
**Solution**: Check backend is running
```bash
curl http://localhost:8001/healthz
```

### Issue 3: API returns 401 Unauthorized
**Solution**: Check authorization header
```bash
# Make sure you're using correct token
curl -H "Authorization: Bearer {valid_token}" http://localhost:8001/api/v1x/...
```

### Issue 4: "Port 8001 already in use"
**Solution**: Kill process or use different port
```bash
# Windows PowerShell
Get-Process -Port 8001 | Stop-Process
# Or use different port
uvicorn app.main:app --port 8002
```

### Issue 5: Frontend CSS/styling looks broken
**Solution**: Rebuild frontend
```bash
npm run dev  # or npm run build && npm run start
```

### Issue 6: Database not initialized
**Solution**: Create tables and seed data
```bash
cd backend
# Tables are auto-created on startup
# Then run seeding
python seed_complete_mentors.py
```

---

## 📈 Performance Testing

### Expected Response Times

| Endpoint | Method | Expected Time |
|----------|--------|----------------|
| GET /mentors | GET | < 200ms |
| GET /mentors/{id} | GET | < 100ms |
| POST /mentors/applications | POST | < 500ms |
| GET /admin/applications | GET | < 300ms |
| PATCH /admin/status | PATCH | < 200ms |

### Load Testing
```bash
# Using Apache Bench (if installed)
ab -n 100 -c 10 http://localhost:8001/api/v1x/mentors

# Expected: Should handle 100 requests with < 10ms avg response time
```

---

## 📝 Manual Testing Scenarios

### Scenario 1: Admin Approves Mentor (Pending)
1. Create new mentor application via API
2. Login as admin
3. See pending application in "Pending" filter
4. Click "Approve Mentor"
5. Verify: Application moves to "Approved" status
6. Verify: Success message shows
7. Verify: Stats update (pending decreases, approved increases)

### Scenario 2: Admin Suspends Mentor
1. Login as admin
2. Go to "Approved" filter
3. See approved mentor
4. Expand card
5. Click "Suspend"
6. Confirm in dialog
7. Verify: Status changes to "suspended"
8. Verify: Card shows suspension notice
9. Verify: "Suspend" button disappears

### Scenario 3: Student Books Session
1. Login as student (alice@test.com)
2. Go to mentors page
3. Click on a mentor
4. View availability slots
5. Click "Book Session"
6. Fill in session details
7. Confirm booking
8. Verify: Session appears in "My Sessions"

### Scenario 4: Student Leaves Review
1. Login as student
2. Go to completed sessions
3. Click "Leave Review"
4. Enter rating (1-5 stars)
5. Add comment
6. Submit review
7. Verify: Mentor average rating updates
8. Verify: Review appears in mentor profile

---

## 🎯 Success Criteria Checklist

### All of these should be ✅ passing:

- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors
- [ ] Admin page loads without errors
- [ ] 5 mentors visible in system
- [ ] Stats dashboard shows correct numbers
- [ ] All filters work (All, Pending, Approved, Rejected, Suspended)
- [ ] Mentor cards display correctly
- [ ] Icons show proper colors
- [ ] Suspend button works
- [ ] Success messages display
- [ ] Error handling works
- [ ] Responsive design looks good
- [ ] API test suite passes (10/10)
- [ ] Database has correct data counts
- [ ] No console errors
- [ ] No TypeScript errors

---

## 📞 Support

If you encounter issues:

1. **Check Logs**: Review backend and frontend console logs
2. **Test APIs**: Use curl or Postman to test endpoints directly
3. **Database**: Verify data with SQL queries
4. **Documentation**: See MENTOR_MODULE_COMPLETE_GUIDE.md
5. **Test Suite**: Run test_mentor_apis.py to verify everything

---

**Last Updated**: 2024  
**Status**: ✅ Ready for Testing and Deployment
