# 🧪 Testing Coding Practice Integration

## Quick Test Commands

### 1. Start Backend Server
```powershell
cd "d:\python code\sfg\skillforge-global\backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Seed Coding Practice Data
```powershell
cd "d:\python code\sfg\skillforge-global\backend"
python seed_premium_practice.py
```

### 3. Start Frontend Server
```powershell
cd "d:\python code\sfg\skillforge-global"
npm run dev
```

---

## 🔍 Manual Testing Checklist

### Dashboard Integration
- [ ] Visit http://localhost:3000/dashboard
- [ ] Verify "Coding Practice Arena" banner is visible
- [ ] Check 4 stat cards (Languages, Challenges, Cloud Labs, IDE)
- [ ] Click "Start Coding" button → redirects to /practice
- [ ] Scroll to "Quick Actions" section
- [ ] Verify "Coding Practice" card is first (gradient style)

### Navigation
- [ ] Check top navigation bar
- [ ] Verify "Coding Practice" link appears between "Career Paths" and "Marketplace"
- [ ] Click link → navigates to /practice page

### Coding Practice Page
- [ ] Visit http://localhost:3000/practice
- [ ] Verify stats overview (4 cards at top)
- [ ] Check quick action buttons work
- [ ] Test category filter dropdown
- [ ] Test difficulty filter dropdown
- [ ] Verify challenge cards display correctly
- [ ] Check difficulty badges are color-coded
- [ ] Verify "Recent Submissions" section shows

### API Endpoints
```powershell
# Test dashboard overview (requires auth token)
curl http://localhost:8001/api/v1x/student/dashboard/overview -H "Cookie: token=YOUR_TOKEN"

# List challenges
curl http://localhost:8001/api/v1x/coding-practice/challenges

# Get categories
curl http://localhost:8001/api/v1x/coding-practice/categories

# Get languages
curl http://localhost:8001/api/v1x/coding-practice/languages

# Get user stats (requires auth)
curl http://localhost:8001/api/v1x/coding-practice/my-stats -H "Cookie: token=YOUR_TOKEN"

# Get submissions (requires auth)
curl http://localhost:8001/api/v1x/coding-practice/my-submissions -H "Cookie: token=YOUR_TOKEN"
```

---

## 🐛 Common Issues & Fixes

### Backend Won't Start
**Error:** `ModuleNotFoundError`
```powershell
pip install -r backend/requirements.txt
```

### Frontend Won't Start
**Error:** `Module not found`
```powershell
npm install
```

### Database Tables Missing
**Error:** `no such table: coding_challenges`
```powershell
# Run seed script to create and populate tables
python backend/seed_premium_practice.py
```

### API Returns Empty coding_practice Stats
**Solution:** This is normal if tables don't exist yet or user has no submissions.
The API gracefully returns zeros:
```json
{
  "coding_practice": {
    "total_submissions": 0,
    "perfect_solutions": 0,
    "challenges_attempted": 0,
    "coins_earned": 0,
    "avg_score": 0.0,
    "active_sessions": 0,
    "success_rate": 0.0
  }
}
```

---

## 📊 Expected Results

### After Fresh Seed
- 8 premium courses in database
- 5 coding challenges created
- 4 simulator environments
- 3 cloud lab scenarios

### Dashboard Banner Should Show
```
💻 Coding Practice Arena
Master programming with hands-on challenges

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   15+    │ │   100+   │ │   AWS    │ │ Real-time│
│Languages │ │Challenges│ │Cloud Labs│ │   IDE    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

[Start Coding →]
```

### Practice Page Should Show
- Stats cards (if user has submissions, else zeros)
- 3 quick action buttons
- Category filter (12 options)
- Difficulty filter (5 options)
- Challenge grid (filtered results)
- Recent submissions (if any exist)

---

## 🎯 User Flow Test

### Complete Journey
1. **Login** → http://localhost:3000/login
2. **See Dashboard** → Prominent coding practice banner
3. **Click Banner CTA** → Navigates to /practice
4. **Browse Challenges** → Use filters to find challenges
5. **Click Challenge** → Opens challenge detail (when implemented)
6. **Complete Challenge** → Submit solution
7. **Return to Dashboard** → See updated stats

---

## 🔐 Authentication Notes

Most endpoints require authentication:
- Use `Cookie: token=JWT_TOKEN` header
- Token is set after login at `/api/v1/auth/login`
- Token stored as HTTP-only cookie

**Get a token:**
```powershell
# Login and capture token
$response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"user@example.com","password":"password123"}' `
  -SessionVariable session

# Use session for authenticated requests
$dashboard = Invoke-WebRequest -Uri "http://localhost:8001/api/v1x/student/dashboard/overview" `
  -WebSession $session
```

---

## ✅ Success Criteria

Integration is working if:
- ✅ Backend starts without errors
- ✅ Frontend builds successfully
- ✅ Dashboard shows coding practice banner
- ✅ Navigation has "Coding Practice" link
- ✅ /practice page loads and displays UI
- ✅ API returns coding_practice section in dashboard
- ✅ Filters work (category/difficulty)
- ✅ No console errors in browser
- ✅ Mobile responsive (test different screen sizes)

---

## 📱 Mobile Testing

### Chrome DevTools
1. Open http://localhost:3000/practice
2. Press F12 → Toggle device toolbar
3. Test viewports:
   - iPhone SE (375px)
   - iPad (768px)
   - Desktop (1920px)

### Expected Behavior
- Stats cards: 4 → 2 → 1 columns
- Challenge grid: 3 → 2 → 1 columns
- Banner: Vertical stack on mobile
- Buttons: Full width on mobile

---

## 🎨 Visual Regression

### Colors to Verify
- Banner gradient: Purple → Blue
- Success badges: Green
- Warning badges: Yellow
- Error badges: Red
- Premium tags: Yellow border
- Difficulty badges: Match difficulty color

### Interactions to Test
- Hover effects on cards
- Button hover states
- Dropdown animations
- Link underlines
- Active states

---

## 📝 Performance Checks

### Load Times
- Dashboard should load < 1s
- Practice page should load < 1.5s
- API responses < 500ms

### Optimization
- Images lazy loaded
- Components memoized
- API calls minimized
- Filters debounced

---

## 🚀 Ready for Production?

Before deploying:
- [ ] All tests pass
- [ ] No console errors
- [ ] Mobile responsive confirmed
- [ ] API endpoints secured
- [ ] Error handling tested
- [ ] Loading states implemented
- [ ] Analytics tracking added
- [ ] SEO metadata added
- [ ] Performance optimized
- [ ] Accessibility verified (WCAG AA)

---

## 📞 Support

If issues persist:
1. Check `backend/CODING_PRACTICE_DASHBOARD.md` for full docs
2. Review `backend/COURSE_PRACTICE_IMPROVEMENTS.md` for implementation details
3. See `backend/QUICK_START_IMPROVEMENTS.md` for setup guide
4. Check browser console for errors
5. Check backend logs for API errors

---

**Status:** ✅ Ready for Testing  
**Last Updated:** December 2024  
**Version:** 1.0.0
