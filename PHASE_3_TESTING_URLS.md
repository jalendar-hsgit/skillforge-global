# Phase 3 Complete Testing Guide - All URLs & Test Scenarios

**Status:** ✅ Phase 3A-3B Complete  
**Date:** January 21, 2026  
**Prerequisites:** Backend running on `http://localhost:8001` | Frontend on `http://localhost:3000`

---

## 📋 Demo Test Accounts

```
ADMIN USER
Email: admin@skillforge.com
Role: ADMIN
Password: (any - demo auth)

MENTOR USERS (4 available)
1. Email: mentor.sarah@skillforge.com (Sarah Chen - $75/hr Python/AI)
2. Email: mentor.david@skillforge.com (David Kumar - $65/hr Web Dev)
3. Email: mentor.emily@skillforge.com (Emily Rodriguez - $85/hr ML)
4. Email: mentor.james@skillforge.com (James Patterson - $70/hr DevOps)
Password: (any - demo auth)

STUDENT USERS (5 available)
1. Email: john.doe@example.com (John Doe)
2. Email: jane.smith@example.com (Jane Smith)
3. Email: bob.wilson@example.com (Bob Wilson)
4. Email: alice.johnson@example.com (Alice Johnson)
5. Email: charlie.brown@example.com (Charlie Brown)
Password: (any - demo auth)
```

---

## 🔐 AUTHENTICATION URLS

### Login
```
http://localhost:3000/auth/login
```

### Register
```
http://localhost:3000/auth/register
```

### Logout
- Click "Logout" button (top-right menu)

---

## 👨‍💼 ADMIN PAGES (Test as admin@skillforge.com)

### 1. Admin Dashboard
```
http://localhost:3000/admin
```
**Test:**
- View system stats (users, courses, sessions, applications)
- Check pending mentors count
- View revenue charts
- See pending items summary

### 2. Mentor Document Verification
```
http://localhost:3000/admin/mentor-verification
```
**Test:**
- See 8 uploaded mentor documents
- Filter by status (PENDING, APPROVED, REJECTED)
- View document thumbnails
- Approve/Reject documents with modal
- Check stats (pending count, etc.)

### 3. Analytics
```
http://localhost:3000/admin/analytics
```
**Test:**
- View user growth metrics
- See course popularity
- Check session booking trends
- Monitor revenue

### 4. Job Applications
```
http://localhost:3000/admin/job-applications
```
**Test:**
- View all user job applications
- Filter by status
- See application history

### 5. Admin Settings
```
http://localhost:3000/admin/settings
```
**Test:**
- Update platform settings
- Configure payment methods
- Set course pricing rules

---

## 🎓 MENTOR PAGES (Test as mentor.sarah@skillforge.com)

### 1. Mentor Dashboard
```
http://localhost:3000/mentor
```
**Test:**
- View profile and bio
- See expertise area
- Check hourly rate ($75/hr)
- View verification status
- See pending items count

### 2. Mentor Document Verification
```
http://localhost:3000/mentor/verification
```
**Test:**
- Upload new documents (drag & drop or file picker)
- See 8+ existing documents
- View document status (APPROVED, PENDING, REJECTED)
- Download/view documents
- Check approval status

### 3. Mentor Availability Management
```
http://localhost:3000/mentor/availability
```
**Test:**
- View weekly calendar (Mon-Sun)
- See 20 availability slots (5 days × 4 mentors)
- **Add slot:**
  - Click day (e.g., Monday)
  - Enter start time: 09:00
  - Enter end time: 10:00
  - Click "Add Slot"
- **Edit slot:**
  - Click "Edit" on any slot
  - Modify times
  - Save changes
- **Delete slot:**
  - Click "Delete" on any slot
  - Confirm deletion
- **Bulk add (Full Day):**
  - Click "Add Full Day"
  - Select Monday
  - Creates 9:00-17:00 block

### 4. Mentor Sessions Management
```
http://localhost:3000/mentor/sessions
```
**Test:**
- View 60 total sessions (mixed statuses)
- **Filter by status:**
  - All (60 total)
  - Upcoming (24 CONFIRMED)
  - Completed (12 COMPLETED)
  - Cancelled (0)
- **View session details:**
  - See student name
  - See topic (e.g., "Python Fundamentals")
  - See scheduled time
  - See duration (60 minutes)
  - See rating (5-star if completed)
- **Confirm session:**
  - Click "Confirm" on PENDING session
  - Confirm via modal
  - Status changes to CONFIRMED
- **Cancel session:**
  - Click "Cancel" on CONFIRMED session
  - Enter reason
  - Status changes to CANCELLED
- **View feedback:**
  - Click "View Feedback" on COMPLETED session
  - See student rating and comments
  - See feedback date
- **View meeting link:**
  - Click "Join Meeting" on CONFIRMED session
  - Generates/shows meeting URL

---

## 👨‍🎓 STUDENT PAGES (Test as john.doe@example.com)

### 1. Student Dashboard
```
http://localhost:3000/student
```
**Test:**
- View profile
- See enrolled courses
- View upcoming mentor sessions
- See job applications tracker

### 2. Book a Mentor Session - Select Mentor
```
http://localhost:3000/student/book-session
```
**Test:**
- See list of 4 mentors:
  1. Sarah Chen ($75/hr) - Python/AI
  2. David Kumar ($65/hr) - Web Dev
  3. Emily Rodriguez ($85/hr) - ML
  4. James Patterson ($70/hr) - DevOps
- Click "Book Session" on any mentor

### 3. Book a Mentor Session - Select Time & Duration
```
http://localhost:3000/student/book-session/1
(where 1 = mentor ID for Sarah Chen)
```
**Test:**
- See mentor profile card (name, rating, bio, expertise)
- View available time slots grouped by date:
  - See 5 upcoming days
  - See available hours (9am-5pm)
- **Select a time slot:**
  - Click on any 1-hour block
  - Slot highlights in blue
- **Choose duration:**
  - Select from dropdown: 30 min, 60 min, 90 min
- **Enter session details:**
  - Topic: "Learn Python Advanced"
  - Description: "Focus on decorators and generators"
- **View mentor rating:**
  - See 5-star rating (if mentor has feedback)
- **Click "Book Session"**
  - Success message appears
  - Redirects to student/sessions

### 4. Student Sessions
```
http://localhost:3000/student/sessions
```
**Test:**
- View all your booked sessions
- **Filter by status:**
  - Upcoming: CONFIRMED sessions (24 total)
  - Completed: COMPLETED sessions (12 total)
- **For each session see:**
  - Mentor name
  - Topic
  - Scheduled date/time
  - Duration (60 min)
  - Current status (PENDING, CONFIRMED, COMPLETED)
  - Price paid
- **For CONFIRMED sessions:**
  - Click "Join Meeting" → Opens Zoom/meet link
  - Click "Cancel" → Cancels booking
- **For COMPLETED sessions:**
  - Click "Add Feedback"
  - Rate session 1-5 stars
  - Add comment: "Great session!"
  - Submit feedback
  - Feedback appears on profile

### 5. View Feedback (After Session)
```
http://localhost:3000/student/sessions
(Scroll to COMPLETED section)
```
**Test:**
- Click "View Feedback" on completed session
- See mentor's response/notes
- See rating and feedback date

---

## 🛒 OTHER PAGES (General)

### Courses
```
http://localhost:3000/courses
```
**Test:**
- View 5 demo courses
- See course details and pricing
- Enroll in course

### Job Tracker
```
http://localhost:3000/job-applications
```
**Test:**
- View all job applications (5 defaults)
- See application status progression
- Add new application

### Marketplace
```
http://localhost:3000/marketplace
```
**Test:**
- View 3 marketplace products (guides, templates, cheat sheets)
- See seller ratings
- Purchase items

---

## 🔌 BACKEND API TESTING (PowerShell)

### Get Auth Token
```powershell
$response = curl -X POST "http://localhost:8001/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "john.doe@example.com",
    "password": "password123"
  }' | ConvertFrom-Json

$TOKEN = $response.access_token
Write-Host "Token: $TOKEN"
```

### List Mentor Availability
```powershell
curl -X GET "http://localhost:8001/api/v1x/mentors/1/availability" `
  -H "Authorization: Bearer $TOKEN"
```

### Get Available Slots for Booking
```powershell
curl -X GET "http://localhost:8001/api/v1x/mentors/1/available-slots?days_ahead=7" `
  -H "Authorization: Bearer $TOKEN"
```

### Book a Session
```powershell
curl -X POST "http://localhost:8001/api/v1x/mentors/sessions/book" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "mentor_id": 1,
    "availability_slot_id": 1,
    "duration_minutes": 60,
    "topic": "Python Basics",
    "description": "Learn Python fundamentals"
  }'
```

### Get My Sessions
```powershell
curl -X GET "http://localhost:8001/api/v1x/mentors/sessions/my-sessions" `
  -H "Authorization: Bearer $TOKEN"
```

### Confirm Session (Mentor)
```powershell
curl -X PUT "http://localhost:8001/api/v1x/mentors/sessions/1/confirm" `
  -H "Authorization: Bearer $TOKEN"
```

### Submit Session Feedback
```powershell
curl -X POST "http://localhost:8001/api/v1x/mentors/sessions/1/feedback" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "rating": 5,
    "feedback_text": "Excellent session! Very helpful.",
    "topics_covered": ["decorators", "generators"]
  }'
```

### Get Mentor Documents
```powershell
curl -X GET "http://localhost:8001/api/v1x/mentor-documents?mentor_id=1" `
  -H "Authorization: Bearer $TOKEN"
```

### Approve Mentor Document (Admin)
```powershell
curl -X PUT "http://localhost:8001/api/v1x/mentor-documents/1/approve" `
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 TEST CHECKLIST

### Authentication
- [ ] Login with admin account
- [ ] Login with mentor account
- [ ] Login with student account
- [ ] Logout and verify redirect
- [ ] Register new account (optional)

### Admin Features
- [ ] View admin dashboard stats
- [ ] View pending mentor documents
- [ ] Approve/reject a document
- [ ] View analytics charts

### Mentor Features
- [ ] View availability slots (20 slots visible)
- [ ] Add new availability slot
- [ ] Edit existing slot
- [ ] Delete slot
- [ ] Add full-day bulk slots
- [ ] View all sessions (60 total)
- [ ] Filter sessions by status
- [ ] Confirm a PENDING session
- [ ] Cancel a CONFIRMED session
- [ ] View feedback on COMPLETED session
- [ ] View/manage documents

### Student Features
- [ ] View mentor list (4 mentors)
- [ ] Click "Book Session" on mentor
- [ ] Select available time slot
- [ ] Choose session duration (30/60/90 min)
- [ ] Enter topic and description
- [ ] Submit booking
- [ ] View booked sessions in dashboard
- [ ] See CONFIRMED sessions in upcoming
- [ ] Click "Join Meeting" on session
- [ ] Submit feedback on COMPLETED session
- [ ] See 5-star rating on mentor profile

### Database Verification
- [ ] 20 availability slots visible
- [ ] 60 mentor sessions with mixed statuses
- [ ] 12 completed sessions with feedback
- [ ] 12 mentor reviews (5-star)
- [ ] 8 mentor documents verified

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Sessions not showing | Check database: `sqlite3 backend/app/data/skillforge.db "SELECT COUNT(*) FROM mentor_sessions"` |
| Auth token error | Re-login and get fresh token |
| API 404 error | Verify backend running on port 8001 |
| Page not found | Check frontend running on port 3000 and restart if needed |
| Availability slots showing 0 | Run `python backend/seed_all_demo_data.py` again |

---

## 🎯 Success Criteria

✅ **All 4 mentor pages accessible and functional**  
✅ **All student booking flows work end-to-end**  
✅ **Admin can approve/reject documents**  
✅ **60 demo sessions visible with correct statuses**  
✅ **20 availability slots per mentor visible**  
✅ **Feedback/ratings system works**  
✅ **Authentication/authorization enforced**  

---

**Last Updated:** January 21, 2026  
**Created by:** AI Assistant  
**Phase:** 3B Complete
