# Quick Migration Guide - Apply Reusable Components to Dashboard Pages

## TL;DR - 3 Steps to Fix Any Dashboard Page

### Step 1: Add Imports
```tsx
import DashboardStatCard from '@/components/DashboardStatCard'
import DashboardSectionHeader from '@/components/DashboardSectionHeader'
import DashboardListItem from '@/components/DashboardListItem'
```

### Step 2: Replace Stat Cards
**Before**:
```tsx
<div className="bg-gradient-to-br from-forgePurple/20 to-forgePurple/10 border border-forgePurple/30 rounded-xl p-6">
  <p className="text-sm text-techGray-400 mb-2">Label</p>
  <p className="text-3xl font-bold text-forgePurple">Value</p>
</div>
```

**After**:
```tsx
<DashboardStatCard label="Label" value="Value" color="purple" />
```

### Step 3: Replace List Items & Headers
**Before**:
```tsx
<h2 className="text-2xl font-bold text-white mb-4">Title</h2>
<div className="bg-white/5 border border-white/10 rounded-lg p-6 hover:border-forgePurple/50 transition">
  Content
</div>
```

**After**:
```tsx
<DashboardSectionHeader title="Title" />
<DashboardListItem hoverColor="purple">
  Content
</DashboardListItem>
```

---

## Page-by-Page Migration

### ✅ COMPLETED
- ✅ `index.tsx` (Overview)
- ✅ `earnings.tsx` (Earnings)

### ⏳ TODO
- [ ] `sessions.tsx` (Sessions)
- [ ] `students.tsx` (Students)
- [ ] `payouts.tsx` (Payouts)
- [ ] `reviews.tsx` (Reviews)
- [ ] `analytics.tsx` (Analytics)
- [ ] `profile.tsx` (Profile)

---

## Color Mapping Guide

### DashboardStatCard Colors
| Color | Use For | Hex |
|-------|---------|-----|
| `purple` | Primary stats, total values, earnings | #A78BFA |
| `blue` | Secondary stats, sessions, counts | #0EA5E9 |
| `electric` | Highlighted stats, ratings, performance | #00D9FF |
| `green` | Success stats, completed items, active | #10B981 |

### Examples by Page

**Overview Page**:
```tsx
<DashboardStatCard label="Total Earnings" value="$1,234.56" color="purple" />
<DashboardStatCard label="Total Sessions" value="42" color="blue" />
<DashboardStatCard label="Average Rating" value="4.8 ⭐" color="electric" />
<DashboardStatCard label="Total Students" value="12" color="green" />
```

**Earnings Page**:
```tsx
<DashboardStatCard label="Total Earnings" value="$5,678.90" color="electric" />
<DashboardStatCard label="Sessions Count" value="156" color="green" />
<DashboardStatCard label="Average Per Session" value="$36.40" color="blue" />
```

**Sessions Page**:
```tsx
<DashboardStatCard label="Total Sessions" value="42" color="purple" />
<DashboardStatCard label="Completed" value="38" color="green" />
<DashboardStatCard label="Pending" value="4" color="electric" />
```

**Students Page**:
```tsx
<DashboardStatCard label="Total Students" value="12" color="purple" />
<DashboardStatCard label="Active" value="10" color="green" />
<DashboardStatCard label="Total Revenue" value="$2,450.00" color="electric" />
```

---

## Common Pattern - Sessions List Example

### Before (Duplicate Code)
```tsx
<div>
  <h2 className="text-2xl font-bold text-white mb-4">Upcoming Sessions</h2>
  <div className="space-y-4">
    {sessions.map((session) => (
      <div
        key={session.id}
        className="bg-white/5 border border-white/10 rounded-lg p-6 hover:border-forgePurple/50 transition"
      >
        <h3 className="text-lg font-semibold text-white">{session.topic}</h3>
        <p className="text-sm text-techGray-400 mt-2">
          {new Date(session.date).toLocaleDateString()}
        </p>
      </div>
    ))}
  </div>
</div>
```

### After (Reusable Components)
```tsx
<div>
  <DashboardSectionHeader title="Upcoming Sessions" />
  <div className="space-y-4">
    {sessions.map((session) => (
      <DashboardListItem key={session.id} hoverColor="purple">
        <h3 className="text-lg font-semibold text-white">{session.topic}</h3>
        <p className="text-sm text-techGray-400 mt-2">
          {new Date(session.date).toLocaleDateString()}
        </p>
      </DashboardListItem>
    ))}
  </div>
</div>
```

**Lines Saved**: 11 lines per instance × 10 pages = 110+ lines total!

---

## Component Props Reference

### DashboardStatCard

```tsx
interface DashboardStatCardProps {
  label: string
  value: string | number
  subtitle?: string
  color: 'purple' | 'blue' | 'electric' | 'green'
  icon?: string
}
```

**Examples**:
```tsx
// With all props
<DashboardStatCard
  label="Monthly Revenue"
  value="$1,234.56"
  subtitle="+12% from last month"
  color="purple"
  icon="💰"
/>

// Minimal
<DashboardStatCard label="Count" value={42} color="blue" />
```

---

### DashboardListItem

```tsx
interface DashboardListItemProps {
  children: React.ReactNode
  hoverColor?: 'purple' | 'blue' | 'electric'
  onClick?: () => void
  className?: string
}
```

**Examples**:
```tsx
// Basic usage
<DashboardListItem hoverColor="purple">
  <h3>Item Title</h3>
  <p>Description</p>
</DashboardListItem>

// With click handler
<DashboardListItem 
  hoverColor="blue" 
  onClick={() => handleClick()}
>
  Click me
</DashboardListItem>

// With additional classes
<DashboardListItem 
  hoverColor="electric"
  className="p-4"
>
  Custom padding
</DashboardListItem>
```

---

### DashboardSectionHeader

```tsx
interface DashboardSectionHeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
}
```

**Examples**:
```tsx
// Basic
<DashboardSectionHeader title="Upcoming Sessions" />

// With subtitle
<DashboardSectionHeader 
  title="Recent Reviews"
  subtitle="Last 30 days"
/>

// With action button
<DashboardSectionHeader 
  title="All Sessions"
  subtitle="8 total"
  action={
    <button className="px-4 py-2 bg-forgePurple text-white rounded">
      View All
    </button>
  }
/>
```

---

## Finding What to Replace

### Search for Duplicate Patterns

**Stat Cards** - Look for:
```
className="bg-gradient-to-br from-*
className="text-3xl font-bold text-*
className="text-sm text-techGray-400"
```

**List Items** - Look for:
```
className="bg-white/5 border border-white/10
className="rounded-lg p-6
className="hover:border-
```

**Section Headers** - Look for:
```
className="text-2xl font-bold text-white mb-4"
className="h2" or <h2
```

---

## Checklist for Each Page

- [ ] Add imports for 3 components
- [ ] Find all stat card divs
- [ ] Replace with `<DashboardStatCard />`
- [ ] Find all section header h2s
- [ ] Replace with `<DashboardSectionHeader />`
- [ ] Find all list item divs
- [ ] Replace with `<DashboardListItem />`
- [ ] Check responsive grid classes
- [ ] Verify spacing (space-y-8 for sections)
- [ ] Test in browser
- [ ] Check mobile view

---

## Validation

After migration, ensure:
- ✅ No undefined colors (only purple, blue, electric, green)
- ✅ No hardcoded inline styles
- ✅ Components have proper indentation
- ✅ TypeScript doesn't complain about props
- ✅ Components render correctly in browser
- ✅ Styling matches other pages

---

## Questions?

Refer to:
- Completed examples: `index.tsx`, `earnings.tsx`
- Component files: `src/components/Dashboard*.tsx`
- Full guide: `FRONTEND_CLEANUP_COMPLETE.md`

---

## Estimated Time

Per page:
- Find and replace stat cards: 2 minutes
- Find and replace section headers: 1 minute
- Find and replace list items: 3 minutes
- Testing: 2 minutes
- **Total per page: ~8 minutes**

For all 6 remaining pages: **~48 minutes**
