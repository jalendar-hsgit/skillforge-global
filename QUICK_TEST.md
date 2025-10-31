# Quick Test Reference Card

## 🚀 Start Servers

```powershell
# Backend (Terminal 1)
cd backend
python -m uvicorn app.main:app --reload --port 8001

# Frontend (Terminal 2)
cd ..
npm run dev
```

## 🔗 Key URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8001/docs | Interactive API docs |
| Health Check | http://localhost:8001/healthz | Server status |
| Pricing | http://localhost:3000/pricing | Subscription plans |
| Login | http://localhost:3000/login | User authentication |
| Dashboard | http://localhost:3000/dashboard | User dashboard |
| Mentors | http://localhost:3000/mentors | Browse mentors |

## 🧪 Quick Tests

### 1. Health Check (30 seconds)
```bash
curl http://localhost:8001/healthz
# Expected: {"ok":true}
```

### 2. View Plans (1 minute)
1. Go to http://localhost:3000/pricing
2. See Free, Pro, Enterprise plans
3. Toggle Monthly/Annual

### 3. Create Account (2 minutes)
1. Go to http://localhost:3000/signup
2. Email: `test@example.com`
3. Password: `password123`
4. Submit → Should redirect to dashboard

### 4. API Test (2 minutes)
1. Go to http://localhost:8001/docs
2. Try GET `/healthz`
3. Try GET `/api/v1x/subscriptions/plans`
4. See 3 plans returned

### 5. Subscribe Test (3 minutes)
1. Click "Upgrade" on Pro plan
2. Use test card: `4242 4242 4242 4242`
3. Expiry: `12/25`, CVC: `123`
4. Submit → Success message

## 🧾 Test Cards (Stripe)

| Card Number | Result |
|-------------|--------|
| 4242 4242 4242 4242 | ✅ Success |
| 4000 0000 0000 0002 | ❌ Declined |
| 4000 0025 0000 3155 | 🔐 Requires authentication |

## 📋 Test Checklist (15 minutes)

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Health endpoint returns OK
- [ ] Can view pricing page
- [ ] Can create account
- [ ] Can login
- [ ] Dashboard loads after login
- [ ] Can view courses/paths
- [ ] API docs accessible
- [ ] Subscription plans load
- [ ] Test subscribe flow (test mode)
- [ ] Can logout

## 🔍 Debug Commands

```powershell
# Check if servers running
netstat -ano | findstr :3000
netstat -ano | findstr :8001

# Test backend directly
curl http://localhost:8001/healthz
curl http://localhost:8001/api/v1/courses

# View logs
# Check terminal where servers are running

# Database query
cd backend/app/data
sqlite3 app.db "SELECT * FROM users;"
```

## ⚡ Common Test Scenarios

### Scenario A: New User Journey (5 min)
1. Signup → Login → Browse Courses → View Pricing → Subscribe

### Scenario B: Mentor Flow (10 min)
1. Complete course → Apply as mentor → Get approved → Accept booking

### Scenario C: Payment Flow (3 min)
1. Add test card → Subscribe → See Pro badge → Cancel subscription

### Scenario D: Chat & Video (5 min)
1. Book session → Open chat → Send message → Start video call

## 🎯 Priority Tests

**P0 (Must Work):**
- Backend health check
- Frontend loads
- User signup/login
- View courses

**P1 (Critical Features):**
- Subscription plans display
- Subscribe with test card
- Mentor listing
- API endpoints respond

**P2 (Nice to Have):**
- Video calls work
- File upload works
- Real-time chat
- Payout requests

## 📞 Support

**Issues?**
1. Check both servers are running
2. Clear browser cache/cookies
3. Check console for errors (F12)
4. Restart servers
5. Check `MANUAL_TESTING.md` for detailed troubleshooting

---

**Full Guide:** See `MANUAL_TESTING.md` for complete testing procedures.
