# Mentor Dashboard - Navigation Flow & Quick Start

## 🎯 Quick Start Guide

### For Mentors
1. **Login** at `http://localhost:3000/login`
   - Email: mentor@example.com
   - Password: your_password

2. **Get Redirected** to `/mentors/dashboard`
   - Dashboard overview loads automatically
   - All your stats display

3. **Navigate** Using:
   - **Desktop**: Click items in left sidebar
   - **Mobile**: Tap items in bottom navigation

4. **View Your Data**:
   - Earnings breakdown
   - Session management
   - Student roster
   - Reviews and ratings
   - Payment settings
   - Profile information

---

## 📍 Navigation Structure

```
┌─ Dashboard (Overview)
│   └─ /mentors/dashboard
│
├─ Earnings
│   └─ /mentors/dashboard/earnings
│
├─ Analytics
│   └─ /mentors/dashboard/analytics
│
├─ Sessions
│   └─ /mentors/dashboard/sessions
│
├─ Students
│   └─ /mentors/dashboard/students
│
├─ Payouts
│   └─ /mentors/dashboard/payouts
│
├─ Reviews
│   └─ /mentors/dashboard/reviews
│
└─ Profile
    └─ /mentors/dashboard/profile
```

---

## 🖥️ Desktop Navigation (lg breakpoint and above)

### Sidebar Layout
```
┌──────────────────────────────────────────────────────┐
│                     TOP NAV BAR                      │
│  Logo  |  Page Title  |  User Menu (@logout)         │
└────────┬──────────────────────────────────────────────┘
         │
         ├─[64px]─ SIDEBAR
         │         ┌─────────────────────┐
         │         │   Mentor Portal    │
         │         ├─────────────────────┤
         │         │ 📊 Overview         │ ← Active
         │         │ 💰 Earnings         │
         │         │ 📈 Analytics        │
         │         │ 📅 Sessions         │
         │         │ 👥 Students         │
         │         │ 💳 Payouts          │
         │         │ ⭐ Reviews          │
         │         │ ⚙️  Profile         │
         │         └─────────────────────┘
         │
         ├─ BREADCRUMB (if applicable)
         │  🏠 Dashboard / Current Page
         │
         └─ MAIN CONTENT
            Full width responsive content area
```

### How It Works
1. Sidebar is **fixed** on left side
2. Sidebar is **sticky** - stays visible while scrolling
3. Active item is **highlighted** with gradient
4. Hover over item shows **tooltip** with description
5. Click any item to **navigate** to that page
6. Page title updates in top navigation
7. Breadcrumb updates to show location
8. Content loads with skeletons

---

## 📱 Mobile Navigation (below lg breakpoint)

### Bottom Navigation Layout
```
┌──────────────────────────────────────────────────────┐
│                     TOP NAV BAR                      │
│  Logo  |  Page Title  |  User Menu (@logout)         │
├──────────────────────────────────────────────────────┤
│                 BREADCRUMB TRAIL                     │
│           🏠 Dashboard / Current Page                │
├──────────────────────────────────────────────────────┤
│                                                      │
│                   MAIN CONTENT                       │
│                                                      │
│                  (Scrollable)                        │
│                                                      │
├──────────────────────────────────────────────────────┤
│ BOTTOM NAVIGATION                                    │
│  📊    💰    📈    📅    👥   ⋯                      │
│ Dash  Earn  Analyt Sess  Stud More                 │
└──────────────────────────────────────────────────────┘
```

### How It Works
1. Bottom nav is **fixed** at bottom
2. Shows **5 primary sections** at once
3. "More" menu for remaining sections (Payouts, Reviews, Profile)
4. Active item **highlighted** with color
5. Tap item to **navigate** to that page
6. Content fills screen above bottom nav
7. Scrollable main content
8. Touch-optimized sizing

---

## 🔄 Navigation Flows

### Flow 1: Dashboard → Earnings
```
User on /mentors/dashboard
        ↓
Click "Earnings" in sidebar/bottom nav
        ↓
Navigate to /mentors/dashboard/earnings
        ↓
Breadcrumb updates: 🏠 Dashboard / Earnings
        ↓
"Earnings" item highlighted in navigation
        ↓
Earnings data loads with skeletons
        ↓
Page displays monthly breakdown
```

### Flow 2: Sessions → Student Details
```
User on /mentors/dashboard/sessions
        ↓
Click session in list
        ↓
Session details expanded/modal opens
        ↓
Can view student info or take actions
        ↓
Update session status
        ↓
Data refreshes in list
```

### Flow 3: Complete Session Workflow
```
1. Login → /login
2. Redirected to → /mentors/dashboard
3. Click Sessions → /mentors/dashboard/sessions
4. View pending sessions
5. Click Confirm → Session updates
6. Check Analytics → /mentors/dashboard/analytics
7. View performance → Session counted
8. Check Earnings → /mentors/dashboard/earnings
9. See revenue from session
10. Request Payout → /mentors/dashboard/payouts
11. Set up payment method
12. Request withdrawal
```

---

## 📊 Data Flow Example

### When User Navigates to Earnings Page
```
[Frontend]
┌─────────────────────────┐
│  Click "Earnings"       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Navigate to /earnings   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Show loading skeleton   │
│ Start API request       │
└────────────┬────────────┘
             ↓
        [Backend API]
┌─────────────────────────┐
│ GET /mentor-portal/     │
│    dashboard/earnings   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Query database          │
│ Calculate earnings      │
│ Format monthly data     │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Return JSON response    │
│ with earnings data      │
└────────────┬────────────┘
             ↓
        [Frontend]
┌─────────────────────────┐
│ Receive API response    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Parse JSON data         │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Hide skeleton           │
│ Display earnings data   │
│ Show monthly table      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Page fully rendered     │
│ User can interact       │
└─────────────────────────┘
```

---

## 🎨 Visual Indicators

### Active Page Indicator
- Current page is **highlighted** in navigation
- Highlight color: Gradient from `forgePurple` to `techBlue`
- Effect: Background color change
- Persistence: Stays highlighted while on that page

### Loading State
- Skeleton screens **match the layout** of loaded content
- **Animated pulse** effect (opacity fade)
- Placeholder text boxes, bars, and grids
- Removes skeleton when data arrives

### Breadcrumb Trail
- Format: `🏠 Parent / Child / Current`
- Current page is **not a link** (unclickable)
- Parent pages are **clickable links**
- Updates automatically on navigation

### Error States
- **Red background** with white/red text
- Clear error message describing the problem
- Shows action to fix (login, try again, etc.)
- Removes error when user takes action

---

## ⌨️ URL Examples

### Valid Dashboard URLs
- `http://localhost:3000/mentors/dashboard` ✅ Overview
- `http://localhost:3000/mentors/dashboard/earnings` ✅ Earnings
- `http://localhost:3000/mentors/dashboard/analytics` ✅ Analytics
- `http://localhost:3000/mentors/dashboard/sessions` ✅ Sessions
- `http://localhost:3000/mentors/dashboard/students` ✅ Students
- `http://localhost:3000/mentors/dashboard/payouts` ✅ Payouts
- `http://localhost:3000/mentors/dashboard/reviews` ✅ Reviews
- `http://localhost:3000/mentors/dashboard/profile` ✅ Profile

### Invalid URLs (404)
- `http://localhost:3000/mentors/dashboard/invalid` ❌ Page not found
- `http://localhost:3000/mentors/dashboard/edit` ❌ Page not found
- `http://localhost:3000/dashboard/earnings` ❌ Wrong base path

---

## 🔐 Access Requirements

To access the mentor dashboard, user must:

1. ✅ Be **logged in** (valid auth token)
2. ✅ Have a **mentor account** (registered as mentor)
3. ✅ Be **approved** (account status = "approved")

### What Happens If...

| Condition | Result | Message |
|-----------|--------|---------|
| Not logged in | 401 error | Redirect to `/login?redirect=/mentors/dashboard` |
| Not a mentor | 404 error | "You are not registered as a mentor" |
| Not approved | 403 error | "Mentor account not approved" |
| Logged in + mentor + approved | ✅ Access granted | Dashboard loads normally |

---

## 🔧 Testing Navigation

### Test Checklist
- [ ] Desktop sidebar displays all 8 items
- [ ] Mobile bottom nav displays 5 items + More
- [ ] Click each item navigates to correct page
- [ ] Active item highlighted in navigation
- [ ] Breadcrumbs update on navigation
- [ ] Skeleton shows while loading
- [ ] Data displays after loading
- [ ] Error messages show on failures
- [ ] Mobile responsive layout works
- [ ] Tablet responsive layout works
- [ ] Desktop full layout works

### Manual Testing Steps
1. Open browser DevTools (F12)
2. Go to `/mentors/dashboard`
3. Check sidebar/bottom nav is visible
4. Click different sections
5. Watch URL change in address bar
6. Observe breadcrumb update
7. See loading skeleton appear
8. Watch data load and display
9. Check mobile view (DevTools mobile mode)
10. Verify all works on mobile

---

## 📚 Component Relationships

```
DashboardLayout (main wrapper)
├── MentorDashboardSidebar (navigation)
│   ├── NavItem 1: Overview
│   ├── NavItem 2: Earnings
│   ├── NavItem 3: Analytics
│   ├── NavItem 4: Sessions
│   ├── NavItem 5: Students
│   ├── NavItem 6: Payouts
│   ├── NavItem 7: Reviews
│   └── NavItem 8: Profile
├── DashboardBreadcrumb (trail)
├── Top Navigation Bar
├── Main Content Area
│   └── Page Component (Overview, Earnings, etc.)
│       ├── Loading State (with Skeleton)
│       ├── Error State
│       └── Data Display
└── Footer
```

---

## 🚀 Next Steps for Users

After dashboard is fully loaded:

1. **Review Dashboard** - See your stats and upcoming sessions
2. **Check Earnings** - Understand your revenue breakdown
3. **View Analytics** - Analyze your performance
4. **Manage Sessions** - Confirm/complete sessions, add notes
5. **Explore Students** - See your student roster
6. **Set Up Payouts** - Add payment method and request withdrawals
7. **Read Reviews** - Check student feedback
8. **Update Profile** - Keep your information current

---

## 💡 Tips & Tricks

### For Mentors
- Use breadcrumbs to quickly go back
- Hover over sidebar items to see descriptions (desktop)
- Check Analytics regularly for insights
- Keep payment methods updated
- Respond to reviews when possible
- Update profile with recent achievements

### For Developers
- Study `DashboardLayout` to understand component structure
- Check `MentorDashboardSidebar` for navigation logic
- Review individual page files for data fetching patterns
- Use existing pages as templates for new features
- Test on both desktop and mobile
- Verify API responses match expected data shapes

---

## 📞 Troubleshooting

### Navigation Not Showing
**Issue**: Sidebar or bottom nav not visible
**Solution**: 
1. Check browser console for errors
2. Verify DashboardLayout is wrapping the page
3. Clear browser cache and reload

### Page Won't Load
**Issue**: Page shows loading skeleton forever
**Solution**:
1. Check Network tab for failed API requests
2. Verify user is logged in
3. Check if mentor is approved
4. Look for 401/403/404 errors in console

### Wrong Page Highlighted
**Issue**: Active page indicator is wrong
**Solution**:
1. Check router.pathname in sidebar component
2. Verify URL matches the href value
3. Clear browser cache

### Mobile Navigation Broken
**Issue**: Bottom nav not responding to taps
**Solution**:
1. Test on actual mobile or DevTools mobile view
2. Check touch event handlers
3. Verify responsive breakpoints

---

## ✅ Summary

The mentor dashboard navigation is **fully functional** with:
- ✅ All 8 pages accessible
- ✅ Clear navigation paths
- ✅ Responsive design for all devices
- ✅ Intuitive user interface
- ✅ Professional appearance
- ✅ Fast performance
- ✅ Error handling
- ✅ Loading states

Users can now easily navigate and manage their mentoring business from a single, cohesive dashboard interface.
