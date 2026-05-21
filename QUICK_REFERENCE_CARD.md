# � QUICK REFERENCE CARD - ALL CREDENTIALS & URLS

**Print this page or bookmark for quick access**  
**Updated**: January 27, 2026

---

## 🚀 START HERE

### Development Environment
```
Frontend:    http://localhost:3001
Backend:     http://localhost:8001
API Docs:    http://localhost:8001/docs
Database:    backend/app/data/skillforge.db
```

---

## 👤 LOGIN CREDENTIALS - QUICK ACCESS

### Copy-Paste Ready Login Table

| Account Type | Email | Password | Next Step |
|---|---|---|---|
| **Student** | john.doe@example.com | john123 | → Dashboard |
| **Admin** | admin@skillforge.com | admin123 | → Admin Panel |
| **Superadmin** | superadmin@skillforge.com | super123 | → Full Access |
| **Mentor** | mentor.sarah@skillforge.com | mentor123 | → Mentor Dashboard |
| **Seller** | mentor.sarah@skillforge.com | mentor123 | → Marketplace |

---

## 🔑 ALL USER IDS & EMAILS

### Admin Accounts
```
ID 1: superadmin@skillforge.com [super123]       SUPERADMIN
ID 2: admin@skillforge.com [admin123]            ADMIN
```

### Student Accounts
```
ID 3: john.doe@example.com [john123]             Student
ID 4: jane.smith@example.com [jane123]           Student
ID 5: bob.wilson@example.com [bob123]            Student
ID 6: alice.johnson@example.com [alice123]       Student
ID 7: charlie.brown@example.com [charlie123]     Student
```

### Mentor/Seller Accounts
```
ID 8:  mentor.sarah@skillforge.com [mentor123]   $75/hr
ID 9:  mentor.david@skillforge.com [mentor123]   $65/hr
ID 10: mentor.emily@skillforge.com [mentor123]   $85/hr
ID 11: mentor.james@skillforge.com [mentor123]   $70/hr
```

---

## 🔴 NOT STARTED (9 Features) 0%

- AI Hints System (10-15h)
- GitHub Integration (6-8h)
- Referral Program (4-6h)
- Live Coding (12-15h)
- Video Conferencing (8-10h)
- Mobile App (40+h)
- Advanced Recommendations (10-12h)
- Badge System (4-6h)
- Analytics Export (3-4h)

---

## ⚡ NEXT 8 HOURS (Quick Wins)

### Rank 1: Leaderboard Page (3h) - HIGH IMPACT
```
Frontend: Create src/pages/leaderboard.tsx
Backend: GET /api/v1x/leaderboard (exists)
Impact: Users love competition
```

### Rank 2: Achievement Display (2h) - HIGH IMPACT
```
Frontend: Create src/components/AchievementBadge.tsx
Backend: Achievement system exists
Impact: Increases engagement 30%+
```

### Rank 3: Fix Coding Challenges (1h) - CRITICAL
```
Debug: /api/v1x/coding-practice (500 error)
File: backend/app/api/v1x/coding_practice.py
Impact: Unblocks feature implementation
```

### Rank 4: Coin History (1h) - QUICK WIN
```
Frontend: Update src/components/Navbar.tsx
Backend: GET /api/v1x/coins/history
Impact: 1-2 hour implementation
```

### Rank 5: User Following (4h) - HIGH VALUE
```
Frontend: Create src/pages/social/
Backend: Ready (no changes needed)
Impact: Social engagement
```

**Total: 11 hours for 5 major features**

---

## 📂 FILE STRUCTURE & API STATUS

### Working APIs (Test Now)
```
✅ GET /healthz
✅ GET /api/v1/courses (25 courses)
✅ GET /api/v1/auth/me
✅ POST /api/v1/auth/login (username or email)
✅ POST /api/v1/auth/signup
✅ GET /api/v1x/resumes (235 resumes)
✅ GET /api/v1x/mentors (4 mentors)
✅ GET /api/v1x/mentor-portal/sessions (21 sessions)
```

### Ready But Not Implemented (Build UI)
```
✅ GET /api/v1x/leaderboard
✅ GET /api/v1x/achievements
✅ GET /api/v1x/coins/balance
✅ GET /api/v1x/coins/transactions
✅ GET /api/v1x/user-social/followers
✅ GET /api/v1x/forums/categories
✅ GET /api/v1x/solutions
✅ GET /api/v1x/contests
```

### Broken (Debug & Fix)
```
❌ GET /api/v1x/coding-practice/challenges (500 error)
   - Issue: Foreign key or model relationship
   - 38 challenges in DB
   - 1-2 hours to fix
```

---

## 🎯 PRIORITY MATRIX

```
        Impact
         ↑
    4    │  Leaderboard     Achievements   Forums
    3    │     (3h)            (2h)        (6h)
    2    │  User Follow   Coin History   Challenges
    1    │     (4h)           (1h)        (debug)
    0    └─────────────────────────────────────→ Time (hours)
         0    2h    4h    6h    8h    10h   12h
```

**Recommended Order**:
1. Leaderboard (3h)
2. Achievements (2h)
3. Fix Challenges (1h)
4. Coin History (1h)
5. User Following (4h)
6. Forums (6h)
7. Solutions (4h)
8. Coding Practice (8h)

---

## 🚀 START NOW

### Terminal 1: Backend
```powershell
cd "d:\python code\sfg\skillforge-global\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Terminal 2: Frontend
```powershell
cd "d:\python code\sfg\skillforge-global"
npm run dev
```

### Test APIs
```powershell
# Health check
curl http://localhost:8001/healthz

# Leaderboard (API ready, needs UI)
curl http://localhost:8001/api/v1x/leaderboard

# List mentors
curl http://localhost:8001/api/v1x/mentors

# Get achievements
curl http://localhost:8001/api/v1x/achievements
```

---

## 📊 IMPLEMENTATION METRICS

| Metric | Value | Status |
|--------|-------|--------|
| **Total Features** | 55+ | ✅ Complete/Partial |
| **Fully Complete** | 47 | ✅ 85% |
| **In Progress** | 8 | 🟡 50% |
| **Not Started** | 9 | 🔴 0% |
| **Database Tables** | 121 | ✅ Ready |
| **Tables with Data** | 32 | ✅ Seeded |
| **Empty Tables (Ready)** | 89 | ✅ Ready |
| **API Endpoints** | 150+ | ✅ Implemented |
| **Working Frontend Pages** | 25+ | ✅ Live |

---

## 🧪 TESTING CHECKLIST

Before implementing each feature:

- [ ] Backend API endpoint exists
- [ ] API returns correct data format
- [ ] API properly authenticated
- [ ] Database tables are ready
- [ ] Sample data exists in database
- [ ] No foreign key conflicts
- [ ] Error handling implemented
- [ ] Rate limiting applied

---

## 📚 KEY FILES TO KNOW

```
Frontend:
├── src/pages/dashboard.tsx         (main dashboard)
├── src/pages/[slug].tsx            (course/path page)
├── src/pages/admin/                (all admin pages)
├── src/components/Navbar.tsx       (header)
├── src/lib/api.ts                  (API helper)
└── src/hooks/useMe.ts              (auth hook)

Backend:
├── backend/app/main.py             (app entry)
├── backend/app/api/v1/auth.py      (auth routes)
├── backend/app/api/v1x/admin.py    (admin routes)
├── backend/app/modelsx/            (database models)
├── backend/app/schemas/            (request schemas)
└── backend/app/core/               (config, security)

Database:
├── 121 tables total
├── 32 with live data
└── 89 ready for features
```

---

## 💡 IMPLEMENTATION TIPS

1. **Test API First**
   - Always test backend API before UI
   - Use Postman or curl
   - Verify response format

2. **Use Sample Data**
   - 32 tables have 1,900+ records
   - Test with real data
   - No fake data needed

3. **Component Reuse**
   - Use existing components
   - Lucide icons everywhere
   - Tailwind for styling

4. **Error Handling**
   - Catch API errors
   - Show user messages
   - Log to console

5. **Performance**
   - Lazy load components
   - Pagination for lists
   - Cache API responses

---

## 🎓 NEXT STEPS

### Hour 0-1: Setup
- [ ] Start backend: `uvicorn app.main:app --reload`
- [ ] Start frontend: `npm run dev`
- [ ] Open http://localhost:3000
- [ ] Login with admin/admin123

### Hour 1-2: Test & Debug
- [ ] Test existing APIs
- [ ] Fix coding challenges 500 error
- [ ] Verify database connections
- [ ] Check console for errors

### Hour 2-8: Build First Feature
- [ ] Pick leaderboard (3h) or achievements (2h)
- [ ] Create frontend page
- [ ] Connect to backend API
- [ ] Add styling with Tailwind
- [ ] Test end-to-end

### Hour 8+: Iterate
- [ ] Deploy feature
- [ ] Get user feedback
- [ ] Build next feature
- [ ] Repeat

---

**Last Updated**: Dec 30, 2025
**Velocity**: 5-8 hours/day
**Timeline**: 8-10 weeks for full feature set
**Ready to Build**: YES ✅
