# 🚀 SkillForge Global - Quick Start Guide

**Status:** ✅ Ready to Test  
**Date:** January 4, 2026  
**Running on:** http://localhost:3001

---

## 🎯 CURRENT STATE

### ✅ JUST COMPLETED
- **Social Activity Feed** - `/community/activity-feed`
- **Contests System** - `/contests` & `/contests/[id]`
- **AI Hints System** - `/ai-hints`

### 🔧 LAST FIXES APPLIED
1. Fixed `useMe` hook import in contests detail page
2. Added `Card` component import in ai-hints page
3. Fixed all Link component nesting issues
4. Build compiled successfully ✅

### 📊 STATUS
- **Build:** ✅ Passing
- **Dev Server:** ✅ Running (port 3001)
- **Backend:** ✅ Running (port 8001)
- **Database:** ✅ Connected (SQLite)

---

## 🌐 ACCESS POINTS

### New Features (Test These First)

| Feature | URL | Status |
|---------|-----|--------|
| Activity Feed | http://localhost:3001/community/activity-feed | ✅ Ready |
| Contests List | http://localhost:3001/contests | ✅ Ready |
| Contest Detail | http://localhost:3001/contests/1 | ✅ Ready |
| AI Hints | http://localhost:3001/ai-hints | ✅ Ready |

### Core Features (Already Working)

| Feature | URL | Status |
|---------|-----|--------|
| Home | http://localhost:3001 | ✅ Ready |
| Dashboard | http://localhost:3001/dashboard | ✅ Ready |
| Marketplace | http://localhost:3001/marketplace | ✅ Ready |
| Mentors | http://localhost:3001/mentors | ✅ Ready |
| Forums | http://localhost:3001/community/forums | ✅ Ready |
| Practice | http://localhost:3001/practice | ✅ Ready |

---

## 🧪 QUICK TEST CHECKLIST

### Activity Feed
```
1. Visit /community/activity-feed
2. See list of activities from followed users
3. Click filter buttons (All, Challenges, Courses, etc.)
4. Click heart icon to like activity
5. Click user name to view profile
6. Check dark mode works
```

### Contests
```
1. Visit /contests
2. See grid of contests with cards
3. Click status filter (Active, Upcoming, Ended)
4. Click category dropdown
5. Click contest card → goes to /contests/[id]
6. On detail: see Overview, Leaderboard, Rules tabs
7. See leaderboard with rankings
8. Click Register if eligible
9. Check dark mode
```

### AI Hints
```
1. Visit /ai-hints
2. See coin balance (top right, yellow badge)
3. See list of available hints
4. Click filter tabs (All, Explanations, Approach, Code)
5. Click hint to expand and see full content
6. Click "View Hint" button (costs coins)
7. Check coin balance decreased
8. Rate hint as helpful/unhelpful
9. Check dark mode
```

---

## 📁 KEY FILES CREATED

### Frontend Pages
```
src/pages/community/activity-feed.tsx      (253 lines)
src/pages/contests/index.tsx               (260 lines)
src/pages/contests/[id].tsx                (409 lines)
src/pages/ai-hints.tsx                     (487 lines)
```

### API Endpoints (Backend)
```
GET  /api/v1x/feed
POST /api/v1x/feed/{id}/like
DELETE /api/v1x/feed/{id}/like

GET  /api/v1x/contests
GET  /api/v1x/contests/{id}
GET  /api/v1x/contests/{id}/leaderboard
POST /api/v1x/contests/{id}/register

GET  /api/v1x/hints
POST /api/v1x/hints/{id}/use
POST /api/v1x/hints/{id}/rate
```

---

## 🚀 START/STOP SERVERS

### Check if Running
```powershell
# Check if frontend dev server is running
Get-Process node | Where-Object {$_.ProcessName -eq "node"}

# Check if backend is running
Get-Process python | Where-Object {$_.ProcessName -match "uvicorn"}
```

### Start Frontend
```bash
cd d:\python code\sfg\skillforge-global
npm run dev
# Runs on http://localhost:3001
```

### Start Backend
```bash
cd d:\python code\sfg\skillforge-global\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Check Backend Health
```bash
curl http://localhost:8001/api/v1x/health
# or open in browser: http://localhost:8001/docs
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Port 3001 is already in use"
```bash
# Kill process on port 3001
npx kill-port 3001
npm run dev
```

### Issue: API calls failing (404/500)
```bash
# Check backend is running
curl http://localhost:8001/api/v1x/contests

# If not running, start it
python -m uvicorn app.main:app --reload --port 8001
```

### Issue: Component not found error
```bash
# Clear Next.js cache
rm -r .next
npm run build
npm run dev
```

### Issue: "Token is invalid" on login
```bash
# Clear localStorage and login again
# In browser console:
localStorage.clear()
# Then go to /login
```

---

## 📚 DOCUMENTATION LINKS

- **Full Development Tracking:** [DEVELOPMENT_TRACKING.md](./DEVELOPMENT_TRACKING.md)
- **Three Features Summary:** [THREE_FEATURES_IMPLEMENTATION.md](./THREE_FEATURES_IMPLEMENTATION.md)
- **Architecture Guide:** Check `docs/` folder

---

## 🎯 NEXT STEPS

### Immediate (Today)
1. ✅ Fix runtime errors → DONE
2. ⏳ Test all 3 features in browser
3. ⏳ Fix any bugs found
4. ⏳ Verify API endpoints work

### After Testing
1. Complete Marketplace seller pages
2. Implement GitHub Integration
3. Build Referral Program
4. Add Certificates

---

## 💾 DATABASE

### Reset Database (if needed)
```bash
cd backend
python init_db.py
python seed_all_demo_data.py
```

### Demo Data Includes
- 7 test users
- 4 mentors
- 5 courses
- 5 contests (ready to test!)
- 3 marketplace products
- 8 mentor sessions
- 20 availability slots

---

## 📞 HELPFUL COMMANDS

### Frontend
```bash
npm run dev              # Start dev server
npm run build            # Build for production
npm run lint             # Run ESLint
npm run format           # Format with Prettier
npm run test             # Run Jest tests
```

### Backend
```bash
python init_db.py                              # Create tables
python seed_all_demo_data.py                   # Add demo data
python -m uvicorn app.main:app --reload       # Dev server
pytest backend/tests/ -v                       # Run tests
```

---

## 🔗 IMPORTANT LINKS

| Resource | URL |
|----------|-----|
| Frontend Dev | http://localhost:3001 |
| Backend API | http://localhost:8001 |
| API Docs | http://localhost:8001/docs |
| Database File | backend/app/data/skillforge.db |
| ENV Config | .env.local |

---

## ⚠️ KNOWN LIMITATIONS

- Activity feed pagination not implemented yet
- Contest leaderboard not real-time
- AI hints search not implemented
- Limited error handling on some pages
- No loading spinners in some places
- Mobile UI needs more testing

---

## ✨ SUCCESS INDICATORS

If everything is working, you should see:

✅ **Activity Feed Page**
- List of activities loads
- Filter buttons work
- Like button toggles

✅ **Contests Pages**
- Contest list displays with cards
- Status filter works
- Can click into contest detail
- Leaderboard shows rankings

✅ **AI Hints Page**
- Coin balance displays
- Hints list loads
- Can expand hints
- Filter tabs work

✅ **Dark Mode**
- Toggle dark mode in settings
- All new pages render correctly

✅ **Mobile**
- Squeeze window to <768px
- Layout responds correctly
- No layout breaks

---

## 📊 FILE STRUCTURE OVERVIEW

```
src/
├── pages/
│   ├── community/activity-feed.tsx      ← NEW
│   ├── contests/
│   │   ├── index.tsx                    ← NEW
│   │   └── [id].tsx                     ← NEW
│   └── ai-hints.tsx                     ← NEW
│
├── components/
│   ├── Layout.tsx                       (wrapper for all pages)
│   ├── Card.tsx                         (used in hints)
│   └── SectionHeading.tsx               (used in hints)
│
└── hooks/
    └── useMe.ts                         (get current user)

backend/
├── app/
│   ├── api/v1x/
│   │   ├── social.py                    (activity feed API)
│   │   ├── contests.py                  (contests API)
│   │   └── ai_hints.py                  (hints API)
│   └── modelsx/
│       ├── social.py                    (feed models)
│       ├── contests.py                  (contest models)
│       └── ai_hints.py                  (hint models)
│
└── data/
    └── skillforge.db                    (SQLite database)
```

---

## 🎓 KEY CONCEPTS

### Components
- **Layout** - Wraps all pages with navigation
- **Card** - Generic card container component
- **SectionHeading** - Large section titles

### Hooks
- **useMe()** - Returns current user: `{ me, loading }`
- **useState()** - Local state management
- **useEffect()** - Side effects & API calls

### API Pattern
```typescript
const token = localStorage.getItem('token');
const res = await fetch(
  `${API_BASE}/api/v1x/endpoint`,
  {
    headers: { Authorization: `Bearer ${token}` }
  }
);
```

---

## 🎉 YOU'RE ALL SET!

Everything is ready to test. Start by visiting the new features:

1. **http://localhost:3001/community/activity-feed** - Social Feed
2. **http://localhost:3001/contests** - Contests
3. **http://localhost:3001/ai-hints** - AI Hints

Report any issues you find and we'll fix them!

---

**Created:** January 4, 2026  
**Status:** ✅ Ready for Testing  
**Questions?** Check DEVELOPMENT_TRACKING.md for details
