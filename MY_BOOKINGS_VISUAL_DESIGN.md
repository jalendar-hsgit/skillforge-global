# MY-BOOKINGS PAGE - VISUAL DESIGN GUIDE

## Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│                        BACKGROUND: deepTech-950             │
│                                                              │
│  ╔═══════════════════════════════════════════════════════╗ │
│  ║ My Mentor Sessions                                   ║ │
│  ║ View and manage all your booked mentor sessions      ║ │
│  │                                                       │ │
│  │ [📚 Book New Session]  [📚 Browse Mentors]          │ │
│  ╚═══════════════════════════════════════════════════════╝ │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │   SESSION CARD 1     │  │   SESSION CARD 2     │        │
│  │ [sarah Chen ⭐ 4.5]  │  │   [David Kumar ⭐ ]  │        │
│  │ [PENDING]            │  │   [CONFIRMED]        │        │
│  │                      │  │                      │        │
│  │ Topic: Python AI     │  │ Topic: Web Dev       │        │
│  │ Date: Feb 2, 2026    │  │ Date: Feb 5, 2026    │        │
│  │ Time: 03:30 AM       │  │ Time: 10:00 AM       │        │
│  │ Duration: 60 min     │  │ Duration: 90 min     │        │
│  │ Price: $75           │  │ Price: $65           │        │
│  │ Payment: PENDING     │  │ Payment: COMPLETED   │        │
│  │                      │  │                      │        │
│  │ [Join Meeting] ✓     │  │ [Join Meeting] ✓     │        │
│  │ [View Details]       │  │ [View Details]       │        │
│  │ [Leave Feedback]     │  │ [Leave Feedback]     │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  ┌──────────────────────┐                                   │
│  │   SESSION CARD 3     │                                   │
│  │ [Emily Rodriguez ⭐] │                                   │
│  │   [COMPLETED]        │                                   │
│  └──────────────────────┘                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Status Badges
```
┌──────────────┬────────────────────────────────────────────┐
│   Status     │ Style                                      │
├──────────────┼────────────────────────────────────────────┤
│ PENDING      │ 🟨 bg-yellow-500/20 text-yellow-300       │
│ CONFIRMED    │ 🟢 bg-green-500/20 text-green-300         │
│ COMPLETED    │ 🔵 bg-blue-500/20 text-blue-300           │
│ CANCELLED    │ 🔴 bg-red-500/20 text-red-300             │
└──────────────┴────────────────────────────────────────────┘
```

### Icon Colors
```
📖 Topic        → forgePurple-400
📅 Date/Time    → aiElectric-400  
⏱️  Duration     → neuralBlue-400
💵 Price        → green-400
💳 Payment      → neuralBlue-300
⭐ Rating       → aiElectric-300
```

### Text Hierarchy
```
H1: "My Mentor Sessions"
    - forgePurple-400 → neuralBlue-400 → aiElectric-400 (gradient)
    - font-display font-black text-4xl md:text-5xl

H3: Mentor Name
    - text-white text-lg font-bold

P: Description / Labels
    - Label: text-techGray-400 text-xs uppercase tracking-wide
    - Value: text-white text-sm font-medium
    - Secondary: text-techGray-300

P: Empty State Text
    - Heading: text-white text-xl font-bold
    - Description: text-techGray-300
```

## Card Component Details

```
╔══════════════════════════════════════╗
║  bg-glass backdrop-blur-xl           ║
║  border border-white/10              ║
║  shadow-glass                        ║
║  hover:shadow-lg                     ║
║  hover:shadow-forgePurple-500/20     ║
║  transition-all                      ║
║                                      ║
║  ┌────────────────────────────────┐  ║
║  │ Sarah Chen     [PENDING]        │  ║
║  │ ⭐ 4.5                           │  ║
║  │ ──────────────────────────────  │  ║
║  │ 📖 TOPIC: Python AI             │  ║
║  │ 📅 SCHEDULED: Feb 2, 2026       │  ║
║  │ 🕐 TIME: 03:30 AM               │  ║
║  │ ⏱️  DURATION: 60 minutes         │  ║
║  │ 💵 PRICE: $75                   │  ║
║  │ 💳 PAYMENT: PENDING             │  ║
║  │ ──────────────────────────────  │  ║
║  │                                 │  ║
║  │ [💬 Join Meeting] [View Details] │  ║
║  │ [Leave Feedback]               │  ║
║  └────────────────────────────────┘  ║
╚══════════════════════════════════════╝
```

## Responsive Behavior

### Desktop (1024px+)
- 3-column grid layout
- Full card width: 100% of grid column
- Large text: 4xl header
- Spacious padding and gaps

### Tablet (768px - 1023px)
- 2-column grid layout
- Medium text: 3xl header
- Moderate padding

### Mobile (< 768px)
- 1-column layout (full width)
- Small text: text-2xl header
- Compact padding
- Touch-friendly button sizing

## Button Styles

### Primary Button (Book New Session)
```
bg-gradient-to-r from-forgePurple-600 to-aiElectric-600
text-white
px-8 py-3
rounded-lg
shadow-lg shadow-forgePurple-500/30
hover:shadow-forgePurple-500/50
transition-all
```

### Join Meeting Button
```
bg-gradient-to-r from-green-600 to-green-500
text-white
hover:shadow-lg hover:shadow-green-500/30
```

### View Details / Leave Feedback (Outline)
```
Border-based styling
text-white
Hover effects for interactivity
```

## Empty State

```
┌─────────────────────────────────────┐
│   No Sessions Booked                │
│                                     │
│   📅 (large icon)                   │
│                                     │
│   You haven't booked any mentor    │
│   sessions yet. Start by browsing  │
│   mentors and scheduling your      │
│   first session!                    │
│                                     │
│   [🔍 Browse Mentors]              │
└─────────────────────────────────────┘
```

Colors:
- Background: bg-glass backdrop-blur-xl border border-white/10
- Icon: text-forgePurple-400
- Heading: text-white text-xl font-bold
- Description: text-techGray-300
- Button: variant="primary"

## Error State

```
┌─────────────────────────────────────┐
│ ⚠️  Failed to load bookings          │
│     (Status: 500) - Unknown error    │
└─────────────────────────────────────┘
```

Colors:
- Background: bg-red-500/20 border border-red-500/50
- Icon: text-red-400
- Text: text-red-300
- Glassmorphism: backdrop-blur-xl shadow-glass

## Loading State

```
     ◐  (spinning indicator)
```

- Ring: border-4 border-forgePurple-400/30
- Top: border-t-forgePurple-400
- Animation: animate-spin

## Dashboard Integration

The "My Bookings" button on dashboard/index.tsx:

```
[📚 My Bookings]

bg-gradient-to-r from-forgePurple-600 to-aiElectric-600
text-white
px-8 py-3
rounded-lg
shadow-lg shadow-forgePurple-500/30
hover:shadow-forgePurple-500/50
transition-all
hover:scale-105
```

Positioned before "View My Profile" button for easy access.

## Next Steps

1. **Session Detail Page** (`/my-bookings/[id]`)
   - Use same card styling
   - Show full session details
   - Add mentor profile card
   - Action buttons: Cancel, Reschedule, Join Meeting

2. **Leave Feedback Modal**
   - Use glass styling
   - Star rating input
   - Feedback text area
   - Submit button with gradient

3. **Meeting Join Experience**
   - Redirect to meeting URL
   - Show "Meeting Joined" confirmation
   - Meeting details during session

---

This design maintains visual consistency with the SkillForge Global platform's modern, tech-forward aesthetic using glassmorphism effects, gradient text, and themed color accents.
