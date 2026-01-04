# PHASE 1: DASHBOARD TESTING - EXECUTION GUIDE

**Start Time**: January 1, 2026  
**Duration**: 2 hours  
**Goal**: Verify all 8 dashboard pages load correctly and handle errors properly

---

## ✅ PRE-TEST CHECKLIST

Before you start, ensure:
- [x] Dev server running on port 3002
- [ ] Browser console open (F12)
- [ ] API backend running on port 8001
- [ ] Logged in as mentor user
- [ ] Network tab open (for API calls)

---

## 🧪 TESTING SCHEDULE (2 Hours)

### 0:00-0:15 (15 min) - Setup & Dashboard Home
```
□ Open http://localhost:3002/mentors/dashboard
□ Check for console errors
□ Verify all 4 stat cards load
□ Check navigation sidebar
□ Test mobile view (DevTools)
□ Note any issues
```

### 0:15-0:30 (15 min) - Analytics Page
```
□ Navigate to /mentors/dashboard/analytics
□ Verify data loads (Total Sessions, Rating)
□ Check charts render
□ Test status breakdown displays
□ Check responsive design
□ Note any issues
```

### 0:30-0:45 (15 min) - Students & Reviews
```
□ Go to /mentors/dashboard/students
□ Verify 3 stat cards display
□ Check student table loads
□ Hover effects work
□ Go to /mentors/dashboard/reviews
□ Check review list displays
□ Star ratings render correctly
```

### 0:45-1:00 (15 min) - Sessions & Payouts
```
□ Go to /mentors/dashboard/sessions
□ Check session list loads
□ Filter buttons work
□ Action buttons functional
□ Go to /mentors/dashboard/payouts
□ Check balance stats display
□ Payment methods list shows
```

### 1:00-1:15 (15 min) - Profile & Earnings
```
□ Go to /mentors/dashboard/profile
□ Form loads with data
□ Expertise array handles correctly
□ Go to /mentors/dashboard/earnings
□ Charts display
□ Stats show
```

### 1:15-2:00 (45 min) - Full Error Testing
```
□ Test each page with DevTools Network tab
□ Trigger API errors intentionally
□ Check error messages display
□ Verify fallback UI works
□ Document all findings
```

---

## 🔍 DETAILED TEST CASES

### Test Case 1: Dashboard Home Load
```
STEPS:
1. Navigate to http://localhost:3002/mentors/dashboard
2. Wait 2 seconds for page load
3. Check browser console (F12)
4. Look for stat cards: Overview, Sessions, Rating, Earnings

PASS CRITERIA:
✓ Page loads in < 2 seconds
✓ No red errors in console
✓ All 4 stat cards visible
✓ Data displayed correctly
✓ Responsive on mobile (375px)

FAILURE: Document in Issues list
```

### Test Case 2: Analytics Data Load
```
STEPS:
1. Navigate to /mentors/dashboard/analytics
2. Wait for data load
3. Check Network tab for API call
4. Verify stat cards display

PASS CRITERIA:
✓ Total Sessions card shows number
✓ Average Rating shows "4.5 ⭐"
✓ Status breakdown displays
✓ Chart renders without errors

FAILURE: Note API response status
```

### Test Case 3: Error Handling
```
STEPS:
1. Open DevTools Network tab
2. Simulate API error (Right-click → Block request)
3. Refresh page
4. Check error message displays

PASS CRITERIA:
✓ Error message appears
✓ Not a blank/white page
✓ User can navigate elsewhere
✓ Retry option available

FAILURE: Screenshot the error
```

### Test Case 4: Mobile Responsiveness
```
STEPS:
1. Open DevTools (F12)
2. Toggle device toolbar
3. Select iPhone SE (375x667)
4. Navigate to each page
5. Check layout adjusts

PASS CRITERIA:
✓ All text readable
✓ No horizontal scroll
✓ Buttons are tappable (44px+)
✓ Sidebar converts to bottom nav

FAILURE: Note which page breaks
```

### Test Case 5: Session List Actions
```
STEPS:
1. Go to /mentors/dashboard/sessions
2. Click filter button (e.g., "confirmed")
3. List updates
4. Click session row
5. Check modal/detail opens

PASS CRITERIA:
✓ Filters work
✓ List updates
✓ Modal opens
✓ Action buttons functional

FAILURE: Note which action fails
```

---

## 📋 COMPREHENSIVE CHECKLIST

### Dashboard Home (`/mentors/dashboard`)
- [ ] Page loads in < 2 seconds
- [ ] 4 stat cards render with correct colors
- [ ] Stats display actual numbers
- [ ] Responsive grid (3 cols → 1 col on mobile)
- [ ] Sidebar visible on desktop
- [ ] Bottom nav visible on mobile
- [ ] No console errors
- [ ] Navigation links work

### Analytics (`/mentors/dashboard/analytics`)
- [ ] Page loads without error
- [ ] Total Sessions stat card displays
- [ ] Average Rating stat card displays
- [ ] Sessions by Status section shows
- [ ] Rating Distribution chart renders
- [ ] Colors match theme (blue, green, purple)
- [ ] Mobile responsive
- [ ] API calls successful (Network tab)

### Students (`/mentors/dashboard/students`)
- [ ] Page loads quickly
- [ ] 3 stat cards render (blue, green, purple)
- [ ] Student table displays all columns
- [ ] Hover effects work (bg color change)
- [ ] Student count accurate
- [ ] Session count accurate
- [ ] Revenue total calculates correctly
- [ ] Mobile scrolls horizontally (table)

### Reviews (`/mentors/dashboard/reviews`)
- [ ] Page loads
- [ ] 3 stat cards display
- [ ] Review list shows items
- [ ] Star ratings render (⭐ emoji)
- [ ] Review comments display
- [ ] Average rating calculated
- [ ] 5-star percentage shown
- [ ] No text overflow

### Sessions (`/mentors/dashboard/sessions`)
- [ ] Session list displays
- [ ] Filter buttons work (all, pending, confirmed, etc.)
- [ ] Session cards show data
- [ ] Action buttons appear (Confirm, Cancel, Complete)
- [ ] Click action → modal opens
- [ ] Modal can be closed
- [ ] No console errors
- [ ] Responsive layout

### Payouts (`/mentors/dashboard/payouts`)
- [ ] 3 balance stat cards display
- [ ] Payment methods list shows
- [ ] Add payment method form available
- [ ] Request payout button works
- [ ] Payout history displays
- [ ] Status badges show correct colors
- [ ] Modal forms functional
- [ ] No errors on form submit

### Profile (`/mentors/dashboard/profile`)
- [ ] Page loads with form
- [ ] Bio field populated
- [ ] Expertise array converts to string
- [ ] Hourly rate field shows number
- [ ] Save button clickable
- [ ] Success message appears on save
- [ ] Form validation works
- [ ] Mobile keyboard friendly

### Earnings (`/mentors/dashboard/earnings`)
- [ ] Page loads
- [ ] Stat cards display
- [ ] Charts render (if present)
- [ ] Revenue data accurate
- [ ] Period selector works
- [ ] Responsive on mobile
- [ ] No JavaScript errors

---

## 🐛 COMMON ISSUES TO WATCH FOR

### Issue 1: Data Undefined Error
```
ERROR: Cannot read properties of undefined
CAUSE: API returns null/empty
FIX: Check optional chaining (?.) used
EXAMPLE: data?.total_sessions || 0
```

### Issue 2: Array.join() Error
```
ERROR: Cannot read properties of undefined (reading 'join')
CAUSE: Array expected, got string or undefined
FIX: Check type before .join()
EXAMPLE: 
const expertise = Array.isArray(data.expertise) 
  ? data.expertise 
  : (typeof data.expertise === 'string' ? [data.expertise] : [])
setExpertiseInput(expertise.join(', '))
```

### Issue 3: Layout Breaks Mobile
```
ERROR: Horizontal scroll appears
CAUSE: Fixed width elements
FIX: Check Tailwind responsive classes
EXAMPLE: md:grid-cols-3 (not grid-cols-3)
```

### Issue 4: API Call Fails
```
ERROR: 401 Unauthorized, 404 Not Found
CAUSE: Wrong endpoint, missing auth
FIX: Check Network tab, API port 8001
SOLUTION: Restart backend server
```

### Issue 5: Component Import Missing
```
ERROR: Cannot find module '@/components/X'
CAUSE: Import path wrong or file missing
FIX: Check file exists in src/components/
SOLUTION: Add import statement
```

---

## 📊 ERROR REPORTING TEMPLATE

When you find an issue, document it as:

```
## Issue #1: [Title]
**Severity**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low

**Page**: /mentors/dashboard/[page]
**Browser**: Chrome/Firefox/Safari + Version
**OS**: Windows/Mac/Linux

**Steps to Reproduce**:
1. Go to page
2. Do action
3. See error

**Expected**:
What should happen

**Actual**:
What actually happens

**Error Message**:
```
[Console error text]
```

**Screenshot**:
[Paste screenshot if helpful]

**Status**: ⏳ Open / 🔄 In Progress / ✅ Fixed
```

---

## 🚀 HOW TO RUN TESTS

### Command Line Testing
```bash
# Start dev server
npm run dev

# In another terminal, run tests
npm run test

# For specific file
npm run test -- dashboard
```

### Manual Testing Steps
```
1. Open http://localhost:3002
2. Press F12 to open DevTools
3. Go to each dashboard page
4. Check Console tab for errors (red text)
5. Check Network tab for API calls
6. Test mobile view (Ctrl+Shift+M)
7. Document findings in Issues.md
```

---

## ✅ SIGN-OFF CHECKLIST

When complete, verify:

- [ ] All 8 pages tested
- [ ] No console errors on any page
- [ ] Responsive design verified (desktop, tablet, mobile)
- [ ] All data loads correctly
- [ ] Error states handled
- [ ] Navigation works
- [ ] Buttons functional
- [ ] Forms validate
- [ ] Issues documented
- [ ] Time logged (2 hours)

---

## 📝 ISSUES FOUND

**Keep track here as you test:**

```
## Dashboard Testing Issues

### ✅ Fixed
- [x] analytics.tsx - data.total_sessions undefined (FIXED: Added optional chaining)
- [x] profile.tsx - expertise.join() error (FIXED: Type checking added)

### 🔴 Found During Testing
- [ ] [Issue description]
- [ ] [Issue description]
- [ ] [Issue description]

### 📋 Deferred to Phase 2
- [ ] [Nice-to-have improvement]
- [ ] [Enhancement for later]
```

---

## 🎯 SUCCESS METRICS

**Phase 1 Complete When**:
- ✅ All 8 dashboard pages load without errors
- ✅ Responsive design works (tested at 375px, 768px, 1024px+)
- ✅ All data displays correctly
- ✅ Error states handled gracefully
- ✅ No TypeScript errors
- ✅ No console warnings (except expected)
- ✅ Issues documented
- ✅ Time spent: 2 hours

---

## 📚 QUICK REFERENCE

**Testing tools in browser**:
- `F12` = Open DevTools
- `Ctrl+Shift+M` = Toggle mobile view
- `Ctrl+Shift+J` = Open Console tab
- `Ctrl+Shift+E` = Open Network tab

**Common test URLs**:
- Home: http://localhost:3002/mentors/dashboard
- Analytics: http://localhost:3002/mentors/dashboard/analytics
- Students: http://localhost:3002/mentors/dashboard/students
- Reviews: http://localhost:3002/mentors/dashboard/reviews
- Sessions: http://localhost:3002/mentors/dashboard/sessions
- Payouts: http://localhost:3002/mentors/dashboard/payouts
- Profile: http://localhost:3002/mentors/dashboard/profile
- Earnings: http://localhost:3002/mentors/dashboard/earnings

---

## ⏱️ TIME TRACKING

```
Start Time:  [Record when you begin]
End Time:    [Record when complete]
Total Time:  2 hours
Issues Found: [Count]
Issues Fixed: [Count]
Status:      ✅ COMPLETE / ⏳ IN PROGRESS / ❌ BLOCKED
```

---

**Created**: January 1, 2026  
**Phase**: 1 of 4  
**Duration**: 2 hours  
**Next Phase**: Mentor features (10 hours)

🚀 **READY TO TEST? START NOW!**
