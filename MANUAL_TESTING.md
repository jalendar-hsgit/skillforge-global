# Manual Testing Guide - SkillForge Global

## Setup & Prerequisites

### 1. Start Both Servers

**Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Frontend:**
```powershell
npm run dev
```

**Verify Servers:**
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8001/docs
- Backend Health: http://localhost:8001/healthz

---

## Test Scenarios

### 🔐 Authentication Flow

#### Test 1: User Signup
1. Navigate to http://localhost:3000/signup
2. Fill in:
   - Email: `test@example.com`
   - Password: `password123`
3. Click "Sign Up"
4. **Expected**: Redirected to dashboard, cookie set, user logged in
5. **Verify**: Check browser DevTools > Application > Cookies for `token`

#### Test 2: User Login
1. Navigate to http://localhost:3000/logout (if logged in)
2. Go to http://localhost:3000/login
3. Enter credentials from Test 1
4. Click "Log In"
5. **Expected**: Redirected to dashboard
6. **Verify**: Token cookie present

#### Test 3: Protected Routes
1. Open incognito/private window
2. Try to access http://localhost:3000/dashboard
3. **Expected**: Redirected to /login
4. Login and verify access granted

---

### 📚 Courses & Learning Paths

#### Test 4: Browse Courses
1. Navigate to http://localhost:3000/paths
2. **Expected**: See list of available learning paths
3. Click on a path (e.g., "Python AI Engineer")
4. **Expected**: See course details, modules, videos

#### Test 5: Watch Video & Track Progress
1. From course detail page, click on a video module
2. **Expected**: Video player opens (YouTube embed)
3. Watch for a few seconds
4. Navigate away and return
5. **Expected**: Progress should be saved (if progress tracking is wired up)

#### Test 6: Take Quiz
1. From a course page, find a quiz module
2. Click to start quiz
3. Answer questions
4. Submit quiz
5. **Expected**: See score, pass/fail status
6. **Verify**: Check dashboard for quiz completion

---

### 💳 Subscription & Pricing

#### Test 7: View Pricing Plans
1. Navigate to http://localhost:3000/pricing
2. **Expected**: See three plans:
   - **Free**: $0/month
   - **Pro**: $29/month
   - **Enterprise**: $99/month
3. Toggle between Monthly/Annual billing
4. **Verify**: Annual prices show discount (~17% off)

#### Test 8: Subscribe to Pro Plan (Test Mode)
1. Click "Upgrade" on Pro plan
2. **Expected**: Redirected to http://localhost:3000/subscribe
3. **Setup Test Stripe Key** (if not already done):
   - Add `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...` to `.env.local`
4. Enter test card:
   - Card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/25`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)
5. Click "Subscribe"
6. **Expected**: Success message, redirected to dashboard
7. **Verify**: Dashboard shows "Pro" plan badge

#### Test 9: Check Current Subscription
1. Login as subscribed user
2. Visit http://localhost:8001/api/v1x/subscriptions/current (in browser or Postman)
3. **Expected**: JSON response with:
   ```json
   {
     "plan": "pro",
     "status": "active",
     "is_active": true,
     "is_premium": true
   }
   ```

#### Test 10: Cancel Subscription
1. From dashboard, click "Manage Subscription"
2. Click "Cancel Subscription"
3. Choose "Cancel at period end"
4. **Expected**: Confirmation, subscription marked for cancellation
5. **Verify**: API shows `cancel_at_period_end: true`

---

### 👥 Mentor System

#### Test 11: Become a Mentor - Check Eligibility
1. Login as user with completed courses
2. Visit http://localhost:3000/mentors/become
3. **Expected**: Eligibility check runs
   - Need: 1+ completed path, 80%+ quiz average
4. If not eligible: Complete courses/quizzes first

#### Test 12: Submit Mentor Application
1. Fill out application form:
   - Bio: "Experienced Python developer..."
   - Expertise: "python-ai,web-dev"
   - Hourly Rate: $50
2. Submit application
3. **Expected**: Application pending approval
4. **Manual Approval** (via API or DB):
   ```sql
   UPDATE mentors SET status = 'approved' WHERE user_id = <your_user_id>;
   ```

#### Test 13: Browse Available Mentors
1. Visit http://localhost:3000/mentors
2. **Expected**: List of approved mentors
3. Filter by expertise
4. View mentor profile
5. **Expected**: See bio, rating, hourly rate, availability

#### Test 14: Book a Mentor Session
1. From mentor profile, click "Book Session"
2. Fill in:
   - Topic: "Help with ML project"
   - Date/Time: Future date
   - Duration: 60 minutes
3. Enter payment method (test card)
4. Confirm booking
5. **Expected**: 
   - Payment intent created
   - Session status: "pending" or "confirmed"
   - Email notification sent (if configured)

#### Test 15: Mentor Dashboard
1. Login as a mentor
2. Visit http://localhost:3000/mentors/dashboard
3. **Expected**: See:
   - Upcoming sessions
   - Session requests (pending)
   - Total sessions count
   - Average rating
4. Accept/decline session requests

---

### 💬 Chat & Communication

#### Test 16: Real-time Chat
1. Login as student with booked session
2. Navigate to session detail or chat page
3. **Expected**: WebSocket connection established
4. Send a text message
5. **Verify**: 
   - Message appears instantly
   - Stored in database
6. Open session in mentor's browser
7. **Expected**: Mentor sees message in real-time

#### Test 17: File Sharing in Chat
1. In chat interface, click "Attach File" or file upload button
2. Select file (image, PDF, document)
3. Upload file
4. **Expected**:
   - Progress indicator during upload
   - File appears in chat with download link
   - File stored in `backend/uploads/`
5. Click to download file
6. **Expected**: File downloads successfully

#### Test 18: Video Call
1. In active chat session, click "Start Video Call"
2. Allow camera/microphone permissions
3. **Expected**:
   - Local video preview appears
   - WebRTC connection established
4. On mentor's side, accept call
5. **Expected**:
   - Two-way video/audio stream
   - Controls for mute, camera on/off, end call
6. Test controls:
   - Mute/unmute audio
   - Turn camera on/off
   - End call

---

### 💰 Mentor Payouts

#### Test 19: View Earnings Summary
1. Login as mentor with completed sessions
2. Visit http://localhost:3000/mentors/earnings
3. **Expected**: Dashboard showing:
   - Total earnings
   - Available balance
   - Pending payouts
   - Completed sessions list

#### Test 20: Request Payout
1. From earnings page, click "Request Payout"
2. Enter amount (must be ≤ available balance)
3. Confirm request
4. **Expected**:
   - Payout status: "pending"
   - Displayed in payout history
5. **Admin Approval** (via API):
   ```bash
   # Mark payout as completed
   PATCH /api/v1x/mentors/payouts/{payout_id}
   { "status": "completed" }
   ```

---

### 🔗 Stripe Connect (Mentor Onboarding)

#### Test 21: Setup Stripe Connect Account
1. Login as approved mentor
2. Visit http://localhost:3000/mentors/settings
3. Click "Connect Stripe Account"
4. **Expected**: API call to `/api/v1x/connect/create-account`
5. **Verify**: Account ID created

#### Test 22: Complete Stripe Onboarding
1. Click "Complete Onboarding"
2. **Expected**: Redirected to Stripe Connect onboarding flow
   - Test mode: Use test business info
   - Provide bank details
   - Complete verification
3. After completion, redirected back to settings
4. **Expected**: Status shows:
   - `onboarding_complete: true`
   - `payouts_enabled: true`

#### Test 23: View Stripe Dashboard
1. From settings, click "View Stripe Dashboard"
2. **Expected**: Redirected to Stripe Express Dashboard
3. View transactions, payouts, tax forms

---

### 🔍 API Testing (via Swagger UI)

#### Test 24: Interactive API Testing
1. Navigate to http://localhost:8001/docs
2. **Test Health Endpoint:**
   - Click GET `/healthz`
   - Click "Try it out" > "Execute"
   - **Expected**: `{"ok": true}`

3. **Test Auth Endpoints:**
   - POST `/api/v1/auth/signup` - Create user
   - POST `/api/v1/auth/login` - Get JWT token
   - GET `/api/v1/auth/me` - Verify token (click 🔒 Authorize first)

4. **Test Subscription Endpoints:**
   - GET `/api/v1x/subscriptions/plans` - List plans
   - GET `/api/v1x/subscriptions/current` - Current user's subscription

5. **Test Courses:**
   - GET `/api/v1/courses` - List all courses
   - GET `/api/v1/courses/{path}` - Get specific course

---

### 🎯 Feature Gating by Plan

#### Test 25: Free Plan Limits
1. Login as Free plan user
2. Try to:
   - Book mentor session > 30 minutes
   - Share files in chat
   - Record session
3. **Expected**: Blocked with upgrade prompt

#### Test 26: Pro Plan Features
1. Upgrade to Pro plan
2. **Expected**: Access to:
   - Sessions up to 120 minutes
   - File sharing enabled
   - Session recording enabled
   - Unlimited monthly sessions

---

### 🛠️ Admin Functions

#### Test 27: Manage Courses (Admin)
1. Login with admin credentials (or add `ADMIN_KEY` header)
2. Visit http://localhost:3000/admin/courses
3. **Expected**: CRUD interface for courses
4. Create new course
5. Edit existing course
6. Delete course
7. **Verify**: Changes reflected on courses list

#### Test 28: Approve Mentor Applications
1. Access admin panel or use API directly:
   ```bash
   GET /api/v1x/mentors?status=pending
   ```
2. Review pending applications
3. Approve/reject applications:
   ```bash
   PATCH /api/v1x/mentors/{mentor_id}
   { "status": "approved" }
   ```

---

## 🧪 Testing Checklist

### Authentication ✅
- [ ] Signup with new email
- [ ] Login with existing account
- [ ] Logout and session cleared
- [ ] Protected routes redirect to login
- [ ] Token persists across page refreshes

### Courses ✅
- [ ] Browse all courses
- [ ] View course details
- [ ] Watch videos
- [ ] Progress tracked
- [ ] Complete quizzes
- [ ] View quiz results

### Subscriptions ✅
- [ ] View pricing page
- [ ] See all plan tiers
- [ ] Monthly/Annual toggle works
- [ ] Subscribe to Pro (test mode)
- [ ] View current subscription
- [ ] Cancel subscription
- [ ] Downgrade to Free

### Mentors ✅
- [ ] Check eligibility
- [ ] Submit application
- [ ] Application approved
- [ ] Browse mentors
- [ ] View mentor profile
- [ ] Book session
- [ ] Pay for session (test mode)
- [ ] View mentor dashboard

### Chat & Communication ✅
- [ ] Send text messages
- [ ] Real-time message delivery
- [ ] Upload files
- [ ] Download shared files
- [ ] Start video call
- [ ] Accept video call
- [ ] Mute/unmute controls
- [ ] Camera on/off
- [ ] End call

### Payouts ✅
- [ ] View earnings summary
- [ ] See completed sessions
- [ ] Request payout
- [ ] View payout history
- [ ] Payout marked completed (admin)

### Stripe Connect ✅
- [ ] Create Connect account
- [ ] Start onboarding flow
- [ ] Complete onboarding (test mode)
- [ ] Verify account status
- [ ] Access Express dashboard

### Feature Gating ✅
- [ ] Free plan blocked from premium features
- [ ] Pro plan has full access
- [ ] Enterprise features work

---

## 🐛 Common Issues & Troubleshooting

### Issue: "Cannot connect to backend"
**Solution:**
```powershell
# Check backend is running
curl http://localhost:8001/healthz

# Restart backend
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

### Issue: "Token expired" or "Unauthorized"
**Solution:**
1. Logout and login again
2. Clear cookies
3. Check JWT_SECRET is set in backend

### Issue: "Stripe test card declined"
**Solution:**
- Use `4242 4242 4242 4242` (always succeeds)
- Ensure Stripe test keys are configured
- Check network tab for API errors

### Issue: "WebSocket connection failed"
**Solution:**
1. Verify backend has Socket.IO mounted at `/ws`
2. Check CORS settings include frontend origin
3. Restart both servers

### Issue: "File upload fails"
**Solution:**
1. Check `backend/uploads/` directory exists
2. Verify file size < 10MB
3. Check backend logs for errors

---

## 📊 Test Data Setup

### Create Test Users

**Via API (Swagger UI):**
```json
POST /api/v1/auth/signup
{
  "email": "student@test.com",
  "password": "password123"
}
```

**Create Mentor User:**
```json
POST /api/v1/auth/signup
{
  "email": "mentor@test.com", 
  "password": "password123"
}
```

### Seed Test Courses

```bash
cd backend
python seed_courses.py
```

### Setup Test Stripe Keys

**.env.local (Frontend):**
```env
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51...
```

**backend/.env:**
```env
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 🎬 End-to-End Test Scenario

**Complete User Journey:**

1. ✅ Sign up as new user
2. ✅ Browse courses and start learning
3. ✅ Complete quizzes (get 80%+ average)
4. ✅ Become a mentor (apply + get approved)
5. ✅ Setup Stripe Connect for payouts
6. ✅ Upgrade to Pro subscription
7. ✅ Book a session with another mentor
8. ✅ Conduct session with video call + file sharing
9. ✅ Receive a session booking as mentor
10. ✅ Complete session and see earnings
11. ✅ Request payout
12. ✅ Check payout status in Stripe dashboard

---

## 📝 Notes

- **Test Mode**: Always use Stripe test keys and test cards
- **Database**: SQLite DB at `backend/app/data/app.db`
- **Logs**: Check terminal output for backend errors
- **Browser DevTools**: Monitor Network tab for API calls
- **Cookies**: JWT token stored in HTTP-only cookie named `token`

---

## 🚀 Quick Test Commands

**Health Check All Services:**
```powershell
# Backend
curl http://localhost:8001/healthz

# Frontend
curl http://localhost:3000

# API Plans
curl http://localhost:8001/api/v1x/subscriptions/plans

# Courses
curl http://localhost:8001/api/v1/courses
```

**Check Database:**
```bash
cd backend/app/data
sqlite3 app.db

.tables
SELECT * FROM users;
SELECT * FROM subscriptions;
SELECT * FROM mentors;
```

---

Happy Testing! 🎉
