# SkillForge Global UI System

> **Consistent, stable, rich UI components for all pages**

## Overview

This document describes the new UI design system implemented across SkillForge Global. All new pages should use these components for consistency, maintainability, and a professional appearance.

## Design Principles

- **Glass Morphism**: Subtle transparency with backdrop blur for modern aesthetic
- **Gradient Accents**: Purple-to-blue gradients (`forgePurple` → `neuralBlue`)
- **Responsive First**: Mobile-optimized with proper breakpoints (sm, md, lg)
- **Hover Effects**: Smooth transitions with scale transforms
- **Consistent Spacing**: Standardized padding, margins, and gaps
- **Accessible**: Proper color contrast and keyboard navigation

## Color System

```typescript
// Primary Colors
forgePurple: #7C3AED (RGB: 124, 58, 237)
neuralBlue: #2563EB (RGB: 37, 99, 235)
aiElectric: #3B82F6 (RGB: 59, 130, 246)

// Backgrounds
deepTech: #0A0A0F (Main background)
white/5: Semi-transparent overlays
white/10: Card backgrounds

// Text
white: Primary text
white/60: Secondary text (techGray)
white/40: Disabled text

// Status Colors
green: Success (#10B981)
blue: Info (#3B82F6)
yellow: Warning (#F59E0B)
red: Error/Danger (#EF4444)
orange: Accent (#F97316)
pink: Accent (#EC4899)
```

---

## Core Components

### 1. Layout Component

**Location**: `src/components/Layout.tsx`

The main application shell with navigation, header, and footer.

```tsx
import Layout from '@/components/Layout'

<Layout maxWidth="7xl" showFooter={true}>
  {/* Page content */}
</Layout>
```

**Props**:
- `maxWidth`: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl' | 'full' (default: '7xl')
- `showFooter`: boolean (default: true)
- `children`: React.ReactNode

**Features**:
- Sticky header with glass morphism effect
- Responsive navigation with mobile hamburger menu
- Active route highlighting
- User authentication state display
- Coin badge for logged-in users

---

### 2. PageLayout Components

**Location**: `src/components/PageLayout.tsx`

Utility components for consistent page structure.

#### PageHeader

Page title section with optional breadcrumbs and actions.

```tsx
import { PageHeader } from '@/components/PageLayout'

<PageHeader
  icon="📊"
  title="Dashboard"
  subtitle="Track your learning progress"
  breadcrumbs={[
    { label: 'Home', href: '/' },
    { label: 'Dashboard' }
  ]}
  actions={
    <Button variant="primary">Action</Button>
  }
/>
```

**Props**:
- `icon`: string (emoji recommended)
- `title`: string (required)
- `subtitle`: string (optional)
- `breadcrumbs`: Array<{ label: string, href?: string }> (optional)
- `actions`: React.ReactNode (optional)

#### PageContainer

Wrapper with background variants.

```tsx
import { PageContainer } from '@/components/PageLayout'

<PageContainer variant="glass">
  {/* Content */}
</PageContainer>
```

**Props**:
- `variant`: 'default' | 'card' | 'glass' (default: 'default')
- `children`: React.ReactNode

**Variants**:
- `default`: No background
- `card`: Semi-transparent with border
- `glass`: Premium glass morphism effect

#### PageSection

Section with optional header.

```tsx
import { PageSection } from '@/components/PageLayout'

<PageSection
  icon="📈"
  title="Your Progress"
  subtitle="Last 30 days"
  headerAction={<Button>View All</Button>}
>
  {/* Section content */}
</PageSection>
```

**Props**:
- `icon`: string (optional)
- `title`: string (optional)
- `subtitle`: string (optional)
- `headerAction`: React.ReactNode (optional)
- `children`: React.ReactNode

#### PageGrid

Responsive grid layout.

```tsx
import { PageGrid } from '@/components/PageLayout'

<PageGrid cols={3} gap="md">
  <Card1 />
  <Card2 />
  <Card3 />
</PageGrid>
```

**Props**:
- `cols`: 1 | 2 | 3 | 4 (default: 1)
- `gap`: 'sm' | 'md' | 'lg' (default: 'md')
- `children`: React.ReactNode

**Responsive Behavior**:
- `cols={4}`: 2 cols on mobile, 4 on desktop
- `cols={3}`: 1 col on mobile, 2 on tablet, 3 on desktop
- `cols={2}`: 1 col on mobile, 2 on tablet+

#### EmptyState

Display when no content is available.

```tsx
import { EmptyState } from '@/components/PageLayout'

<EmptyState
  icon="📚"
  title="No courses found"
  description="Start learning by browsing our course catalog."
  action={<Button variant="primary">Browse Courses</Button>}
/>
```

**Props**:
- `icon`: string (required)
- `title`: string (required)
- `description`: string (optional)
- `action`: React.ReactNode (optional)

#### LoadingState

Display while content loads.

```tsx
import { LoadingState } from '@/components/PageLayout'

<LoadingState message="Loading dashboard..." />
```

**Props**:
- `message`: string (optional, default: "Loading...")

#### ErrorState

Display error messages.

```tsx
import { ErrorState } from '@/components/PageLayout'

<ErrorState
  icon="❌"
  title="Failed to Load"
  message="Could not fetch course data. Please try again."
  action={<Button onClick={retry}>Retry</Button>}
/>
```

**Props**:
- `icon`: string (required)
- `title`: string (required)
- `message`: string (optional)
- `action`: React.ReactNode (optional)

---

### 3. Card Components

**Location**: `src/components/Cards.tsx`

Rich card components for displaying data.

#### StatCard

Display key metrics and statistics.

```tsx
import { StatCard } from '@/components/Cards'

<StatCard
  icon="📚"
  label="Courses Completed"
  value="12"
  trend={{ value: 20, direction: 'up' }}
  href="/courses"
  color="purple"
/>
```

**Props**:
- `icon`: string (required, emoji recommended)
- `label`: string (required)
- `value`: string | number (required)
- `trend`: { value: number, direction: 'up' | 'down' } (optional)
- `href`: string (optional, makes card clickable)
- `color`: 'purple' | 'blue' | 'green' | 'orange' | 'pink' (default: 'purple')

**Colors**:
- `purple`: Purple gradient (default)
- `blue`: Blue gradient
- `green`: Green gradient
- `orange`: Orange gradient
- `pink`: Pink gradient

#### FeatureCard

Showcase features or services.

```tsx
import { FeatureCard } from '@/components/Cards'

<FeatureCard
  icon="👨‍🏫"
  title="Book a Mentor"
  description="Get personalized guidance from industry experts."
  href="/mentors"
  badge="Popular"
/>
```

**Props**:
- `icon`: string (required)
- `title`: string (required)
- `description`: string (required)
- `href`: string (optional)
- `badge`: string (optional)

#### ProgressCard

Show learning progress with visual progress bar.

```tsx
import { ProgressCard } from '@/components/Cards'

<ProgressCard
  icon="🐍"
  title="Python AI Engineer"
  subtitle="Master machine learning"
  progress={75}
  href="/paths/python-ai"
  stats={[
    { label: 'Videos', value: '45/60' },
    { label: 'Quizzes', value: '8/10' }
  ]}
/>
```

**Props**:
- `icon`: string (required)
- `title`: string (required)
- `subtitle`: string (optional)
- `progress`: number (0-100, required)
- `href`: string (optional)
- `stats`: Array<{ label: string, value: string }> (optional)

#### AlertCard

Display important notifications.

```tsx
import { AlertCard } from '@/components/Cards'

<AlertCard
  variant="success"
  title="Success!"
  message="Your subscription has been upgraded."
  action={<Button variant="primary">View Dashboard</Button>}
  onDismiss={() => console.log('Dismissed')}
/>
```

**Props**:
- `variant`: 'info' | 'success' | 'warning' | 'error' (required)
- `title`: string (required)
- `message`: string (optional)
- `action`: React.ReactNode (optional)
- `onDismiss`: () => void (optional)

**Variants**:
- `info`: Blue background
- `success`: Green background
- `warning`: Yellow/orange background
- `error`: Red background

#### ActionCard

Call-to-action card with prominent button.

```tsx
import { ActionCard } from '@/components/Cards'

<ActionCard
  icon="🎓"
  title="Start Learning"
  description="Choose from 50+ career paths."
  buttonText="Browse Courses"
  buttonHref="/paths"
  variant="gradient"
/>
```

**Props**:
- `icon`: string (required)
- `title`: string (required)
- `description`: string (required)
- `buttonText`: string (required)
- `buttonHref`: string (required)
- `variant`: 'default' | 'gradient' (default: 'default')

**Variants**:
- `default`: Secondary button style
- `gradient`: Primary gradient button

---

### 4. Button Component

**Location**: `src/components/Button.tsx`

Standard button with variants and sizes.

```tsx
import { Button } from '@/components/Button'

<Button variant="primary" size="md" loading={false}>
  Click Me
</Button>
```

**Props**:
- `variant`: 'primary' | 'secondary' | 'ghost' (default: 'primary')
- `size`: 'sm' | 'md' | 'lg' (default: 'md')
- `loading`: boolean (default: false)
- `disabled`: boolean
- `onClick`: () => void
- All standard HTML button attributes

**Variants**:
- `primary`: Gradient background (purple → blue)
- `secondary`: Border with hover effect
- `ghost`: Transparent with hover background

**Sizes**:
- `sm`: Small (h-10, px-4)
- `md`: Medium (h-12, px-6)
- `lg`: Large (h-14, px-7)

---

## Complete Page Example

See `src/pages/dashboard/index.tsx` for a complete implementation using all components.

Key patterns demonstrated:
1. Layout wrapper with maxWidth
2. PageHeader with breadcrumbs and actions
3. AlertCard for subscription status
4. PageSection with StatCard grid for metrics
5. ProgressCard for current learning path
6. PageGrid with multiple ProgressCards
7. EmptyState when no content
8. ActionCard for CTAs

---

## UI Showcase

Visit `/ui-showcase` to see all components in action with live examples.

The showcase page (`src/pages/ui-showcase.tsx`) includes:
- Alert cards (all 4 variants)
- Stat cards (all 5 colors)
- Progress cards
- Feature cards
- Action cards
- Empty state
- Loading state
- Container variants
- Grid system examples
- Button variants

---

## Migration Guide

### Converting Existing Pages

**Before**:
```tsx
<Layout>
  <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
    <h1 className="text-3xl font-bold">My Page</h1>
    
    <div className="grid grid-cols-4 gap-4 mt-8">
      <div className="rounded-xl border border-white/10 bg-white/[0.06] p-4">
        <div className="text-sm text-white/60">Videos</div>
        <div className="text-2xl font-bold">12</div>
      </div>
      {/* More manual cards... */}
    </div>
  </section>
</Layout>
```

**After**:
```tsx
<Layout maxWidth="7xl">
  <PageHeader
    icon="📚"
    title="My Page"
    subtitle="Page description"
  />
  
  <PageSection icon="📊" title="Statistics">
    <PageGrid cols={4} gap="md">
      <StatCard icon="📚" label="Videos" value="12" color="purple" />
      {/* More stat cards... */}
    </PageGrid>
  </PageSection>
</Layout>
```

### Benefits of Migration

1. **Reduced Code**: Less boilerplate, more readability
2. **Consistency**: All pages look and feel the same
3. **Maintainability**: Change design in one place
4. **Responsiveness**: Built-in mobile optimization
5. **Accessibility**: Proper semantic HTML and ARIA
6. **Type Safety**: Full TypeScript support

---

## Best Practices

### Do's ✅

- **Use PageHeader for all pages** - Consistent page titles and breadcrumbs
- **Wrap content in PageSection** - Proper spacing and organization
- **Use PageGrid for layouts** - Responsive by default
- **Choose appropriate card types** - StatCard for metrics, ProgressCard for progress, etc.
- **Keep icons consistent** - Use emojis for simplicity
- **Use color variants meaningfully** - Purple for primary, green for success, etc.

### Don'ts ❌

- **Don't create custom card styles** - Use existing card components
- **Don't use inline styles** - Use Tailwind classes
- **Don't hardcode dimensions** - Use responsive utilities
- **Don't mix different design patterns** - Stick to the system
- **Don't skip empty/loading states** - Always provide feedback

---

## Component Hierarchy

```
Layout (Application Shell)
├── PageHeader (Title, Breadcrumbs, Actions)
├── AlertCard (Notifications, Banners)
├── PageSection (Logical Content Sections)
│   ├── PageGrid (Responsive Layouts)
│   │   ├── StatCard (Metrics)
│   │   ├── FeatureCard (Features)
│   │   ├── ProgressCard (Progress)
│   │   ├── ActionCard (CTAs)
│   │   └── Custom Content
│   ├── PageContainer (Background Variants)
│   ├── EmptyState (No Content)
│   ├── LoadingState (Loading)
│   └── ErrorState (Errors)
└── Footer (Optional)
```

---

## Responsive Breakpoints

```css
sm: 640px   /* Small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Small desktops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large desktops */
```

All components are mobile-first and automatically adapt to screen size.

---

## Next Steps

1. **Review UI Showcase**: Visit `/ui-showcase` to see all components
2. **Update Dashboard**: Already completed as reference implementation
3. **Migrate Remaining Pages**: Apply new components to:
   - `/paths` (Course paths listing)
   - `/paths/[slug]` (Individual path pages)
   - `/mentors` (Mentor browsing)
   - `/mentors/dashboard` (Mentor dashboard)
   - `/mentors/earnings` (Earnings page)
   - `/pricing` (Pricing page)
   - `/login` & `/signup` (Auth pages)
   - Admin pages
4. **Create Page-Specific Components**: Build on base components for unique needs
5. **Test Responsiveness**: Verify all pages work on mobile, tablet, desktop

---

## Questions & Support

For questions about the UI system:
1. Check this document first
2. Review `/ui-showcase` for examples
3. Look at `dashboard/index.tsx` for complete implementation
4. Inspect component source code in `src/components/`

**Happy building! 🚀**
