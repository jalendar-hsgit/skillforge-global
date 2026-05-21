# Mentor Dashboard Navigation - Visual Guide

## Complete Page Layout

```
╔═════════════════════════════════════════════════════════════════════════════╗
║ TOP NAVIGATION BAR (Fixed - Always Visible)                                ║
║ ├─ [🔷 SkillForge]  /  Dashboard Title    [User Email] [Mentor] [Avatar ▼] ║
║ └─ On Hover Avatar: ┌─────────────────────┐                                ║
║                     │ Dashboard           │                                ║
║                     │ Earnings            │                                ║
║                     │ Analytics           │                                ║
║                     ├─────────────────────┤                                ║
║                     │ Logout (Red)        │                                ║
║                     └─────────────────────┘                                ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  ┌─────────────────────┐  ┌─────────────────────────────────────────────┐ ║
║  │  SIDEBAR (Desktop)  │  │  MAIN CONTENT AREA                          │ ║
║  │                     │  │                                             │ ║
║  │  🏠 Overview        │  │  Breadcrumbs: Overview                      │ ║
║  │  📊 Earnings        │  │                                             │ ║
║  │  📈 Analytics       │  │  Earnings                                   │ ║
║  │  📅 Sessions        │  │  └─ Subtitle: Welcome back, Mentor!        │ ║
║  │  👥 Students        │  │                                             │ ║
║  │  💸 Payouts         │  ├─────────────────────────────────────────────┤ ║
║  │  ⭐ Reviews         │  │                                             │ ║
║  │  👤 Profile         │  │  [Date Range Filter] [Export CSV]           │ ║
║  │  • • •              │  │                                             │ ║
║  │                     │  │  ┌─────────┬─────────┬─────────┬─────────┐ ║
║  │ (Hover for tooltips)│  │  │ Total   │ This    │ Last    │ Pending │ ║
║  │                     │  │  │ Earnings│ Month   │ Month   │ Payout  │ ║
║  └─────────────────────┘  │  └─────────┴─────────┴─────────┴─────────┘ ║
║                           │                                             │ ║
║  MOBILE BOTTOM NAV        │  [Monthly Breakdown Chart]                  │ ║
║  [Overview] [More...]     │                                             │ ║
║                           │  [Top Students List]                        │ ║
║                           │                                             │ ║
║                           ├─────────────────────────────────────────────┤ ║
║                           │  © 2025 SkillForge. All rights reserved.   │ ║
║                           └─────────────────────────────────────────────┘ ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## Responsive Breakpoints

### Desktop (1920px+)
```
┌─────────────────────────────────────────────────────────────────┐
│ Logo Title [SkillForge / Dashboard] User Menu                   │
├──────────┬───────────────────────────────────────────────────────┤
│ Sidebar  │  Content with full width                             │
│ (Visible)│  • Tables with all columns                            │
│          │  • Multi-column layouts                               │
│          │  • Wide charts and graphs                             │
└──────────┴───────────────────────────────────────────────────────┘
```

### Tablet (1024px)
```
┌─────────────────────────────────────────────────────────────────┐
│ Logo [Title Hidden] User Menu                                   │
├─────────────────────────────────────────────────────────────────┤
│  Content with medium width                                      │
│  • Tables with 2-3 columns                                       │
│  • Single column on small sections                               │
│                                                                  │
│  [Bottom Navigation: Overview | Earnings | Analytics | More]    │
└─────────────────────────────────────────────────────────────────┘
```

### Mobile (640px)
```
┌───────────────────────────────────────┐
│ Logo  [User Avatar Dropdown]          │
├───────────────────────────────────────┤
│                                       │
│  Content (Full Width - Single Column)│
│  • Stack all data vertically         │
│  • Touch-friendly buttons             │
│  • Readable font sizes               │
│                                       │
│  [Bottom Navigation Bar - Sticky]    │
│  [Overview] [Earnings] [More]        │
│                                       │
└───────────────────────────────────────┘
```

---

## Navigation Flow

### Entry Points
```
Login Page
    ↓
    ├─→ /mentors/dashboard (Overview)
    │       ↓
    │       ├─→ /mentors/dashboard/earnings
    │       ├─→ /mentors/dashboard/analytics
    │       ├─→ /mentors/dashboard/sessions
    │       ├─→ /mentors/dashboard/students
    │       ├─→ /mentors/dashboard/payouts
    │       ├─→ /mentors/dashboard/reviews
    │       └─→ /mentors/dashboard/profile
    │
    └─→ Avatar Menu
            ├─→ Dashboard
            ├─→ Earnings
            ├─→ Analytics
            └─→ Logout → Login Page
```

---

## Component Hierarchy

```
DashboardLayout
├── Top Navigation Bar (Fixed)
│   ├── Logo (Link to /)
│   ├── Page Title (Center, Desktop only)
│   └── User Profile Section
│       ├── Email Display
│       ├── Role Display
│       └── Avatar Button
│           └── Dropdown Menu
│               ├── Dashboard Link
│               ├── Earnings Link
│               ├── Analytics Link
│               └── Logout Button
│
├── Main Content Area
│   ├── Sidebar (Desktop) / Bottom Nav (Mobile)
│   │   └── MentorDashboardSidebar Component
│   │
│   ├── Sticky Header Section
│   │   ├── Breadcrumb Navigation
│   │   └── Page Title & Subtitle
│   │
│   ├── Content Container
│   │   └── Page-specific content
│   │       (earnings data, analytics charts, etc.)
│   │
│   └── Footer
│       └── Copyright info
```

---

## Color Scheme

### Color Variables Used
```css
deepNavy: #0F172A          /* Primary background */
black: #000000             /* Dark accents */
white: rgba(255,255,255,1) /* Primary text */
white/10: rgba(255,255,255,0.1) /* Borders, subtle backgrounds */
white/5: rgba(255,255,255,0.05) /* Very subtle elements */

techGray: #888888           /* Secondary text */
techBlue: #0091FF           /* Primary accent */
forgePurple: #8B5CF6        /* Secondary accent */

Gradients:
- from-techBlue to-forgePurple /* Avatar, buttons */
- from-deepNavy via-black to-deepNavy /* Page background */
- from-deepNavy/95 to-deepNavy/50 /* Navigation background */
```

### Interactive States
```
Default Button:  bg-techBlue
Hover Button:    bg-techBlue/80 (semi-transparent)
Disabled:        opacity-50

Link Default:    text-white
Link Hover:      text-white with bg-white/10

Border:          border-white/10
Hover Border:    border-techBlue/50 or border-white/20
```

---

## Z-Index Stack (Top to Bottom)

```
z-50 ← Top Navigation + User Dropdown Menu (always on top)
z-40 ← Sticky Header (breadcrumbs, title)
z-30 ← Sidebar Navigation
z-20 ← Modal/Dialog (when present)
z-10 ← Floating elements
z-0  ← Main content
```

---

## Accessibility Features

- ✅ **Semantic HTML**: Proper heading hierarchy (h1, h2, etc.)
- ✅ **Keyboard Navigation**: All interactive elements accessible via Tab
- ✅ **Color Contrast**: WCAG AA compliant (white text on dark background)
- ✅ **ARIA Labels**: Added to icon-only buttons
- ✅ **Focus States**: Visible focus indicators on all interactive elements
- ✅ **Mobile Touch**: 48px+ minimum touch target size

---

## Performance Optimizations

- ✅ **Lazy Loading**: Sidebar icons lazy-loaded
- ✅ **CSS Optimization**: Tailwind CSS purged for unused styles
- ✅ **Image Optimization**: Logo component optimized
- ✅ **Hook Efficiency**: useMe hook cached at app level
- ✅ **Zero Additional API Calls**: Uses existing authentication

---

## Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome/Edge | ✅ Full | Latest 2 versions |
| Firefox | ✅ Full | Latest 2 versions |
| Safari | ✅ Full | Latest 2 versions |
| Mobile Safari | ✅ Full | iOS 13+ |
| Chrome Mobile | ✅ Full | Latest 2 versions |

---

## Testing Scenarios

### Desktop User Flow
1. Open `http://localhost:3002/mentors/dashboard`
2. See top navigation with user profile
3. Click on avatar → Dropdown appears
4. Click "Earnings" → Navigate to earnings page
5. Check breadcrumbs updated
6. Click logout → Redirected to login

### Mobile User Flow
1. Open same URL on mobile device
2. See logo and avatar (title hidden)
3. Avatar dropdown positioned for mobile
4. Bottom navigation shows main sections
5. Content stacks vertically
6. All buttons touch-friendly (48px)

### Responsive Resize
1. Open dashboard on desktop
2. Slowly resize browser to tablet size
3. Sidebar hidden, bottom nav appears
4. Page title hides at 1024px
5. Continue resizing to mobile
6. Bottom nav becomes sticky
7. Content goes full width

---

## Known Limitations & Future Enhancements

### Current
- ✅ Basic navigation structure
- ✅ User profile display
- ✅ Logout functionality
- ✅ Responsive design

### Future Enhancements
- [ ] Dark/Light mode toggle
- [ ] Notification badge on avatar
- [ ] Search functionality in navbar
- [ ] Quick action buttons (e.g., New Session)
- [ ] Keyboard shortcuts (e.g., G=Dashboard, E=Earnings)
- [ ] Mobile slide-out menu option

---

**Last Updated**: December 31, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
