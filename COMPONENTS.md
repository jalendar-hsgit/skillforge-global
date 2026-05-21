# UI Components Quick Reference

**One-page cheat sheet for the SkillForge Global UI system**

---

## 📦 Imports

```tsx
// Layout
import Layout from '@/components/Layout'

// Page utilities
import { 
  PageHeader, PageContainer, PageSection, PageGrid,
  EmptyState, LoadingState, ErrorState 
} from '@/components/PageLayout'

// Cards
import { 
  StatCard, FeatureCard, ProgressCard,
  AlertCard, ActionCard 
} from '@/components/Cards'

// Button
import { Button } from '@/components/Button'
```

---

## 🎨 Layout

```tsx
<Layout maxWidth="7xl" showFooter={true}>
  {/* Content */}
</Layout>
```

**maxWidth**: `'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl' | 'full'`

---

## 📄 PageHeader

```tsx
<PageHeader
  icon="📊"
  title="Dashboard"
  subtitle="Track your progress"
  breadcrumbs={[
    { label: 'Home', href: '/' },
    { label: 'Dashboard' }
  ]}
  actions={<Button>Action</Button>}
/>
```

---

## 📦 PageContainer

```tsx
<PageContainer variant="glass">
  {/* Content */}
</PageContainer>
```

**variant**: `'default' | 'card' | 'glass'`

---

## 📑 PageSection

```tsx
<PageSection 
  icon="📈" 
  title="Stats" 
  subtitle="Last 30 days"
  headerAction={<Button>View All</Button>}
>
  {/* Content */}
</PageSection>
```

---

## 🎯 PageGrid

```tsx
<PageGrid cols={3} gap="md">
  <Item1 />
  <Item2 />
  <Item3 />
</PageGrid>
```

**cols**: `1 | 2 | 3 | 4`  
**gap**: `'sm' | 'md' | 'lg'`

---

## 📊 StatCard

```tsx
<StatCard
  icon="📚"
  label="Courses"
  value="12"
  trend={{ value: 20, direction: 'up' }}
  href="/courses"
  color="purple"
/>
```

**color**: `'purple' | 'blue' | 'green' | 'orange' | 'pink'`  
**trend**: Optional `{ value: number, direction: 'up' | 'down' }`

---

## ✨ FeatureCard

```tsx
<FeatureCard
  icon="👨‍🏫"
  title="Book a Mentor"
  description="Get personalized guidance"
  href="/mentors"
  badge="Popular"
/>
```

---

## 📈 ProgressCard

```tsx
<ProgressCard
  icon="🐍"
  title="Python AI"
  subtitle="Machine learning"
  progress={75}
  href="/paths/python-ai"
  stats={[
    { label: 'Videos', value: '45/60' },
    { label: 'Quizzes', value: '8/10' }
  ]}
/>
```

**progress**: `0-100` (percentage)

---

## 🔔 AlertCard

```tsx
<AlertCard
  variant="success"
  title="Success!"
  message="Operation completed"
  action={<Button>View</Button>}
  onDismiss={() => {}}
/>
```

**variant**: `'info' | 'success' | 'warning' | 'error'`

---

## 🚀 ActionCard

```tsx
<ActionCard
  icon="🎓"
  title="Start Learning"
  description="Choose from 50+ paths"
  buttonText="Browse"
  buttonHref="/paths"
  variant="gradient"
/>
```

**variant**: `'default' | 'gradient'`

---

## 📭 EmptyState

```tsx
<EmptyState
  icon="📚"
  title="No courses"
  description="Start by browsing"
  action={<Button>Browse</Button>}
/>
```

---

## ⏳ LoadingState

```tsx
<LoadingState message="Loading..." />
```

---

## ❌ ErrorState

```tsx
<ErrorState
  icon="❌"
  title="Error"
  message="Failed to load"
  action={<Button onClick={retry}>Retry</Button>}
/>
```

---

## 🔘 Button

```tsx
<Button 
  variant="primary" 
  size="md" 
  loading={false}
  disabled={false}
>
  Click Me
</Button>
```

**variant**: `'primary' | 'secondary' | 'ghost'`  
**size**: `'sm' | 'md' | 'lg'`

---

## 🎨 Color Palette

```tsx
// Gradients
from-forgePurple to-neuralBlue  // Primary gradient
from-forgePurple/20 to-neuralBlue/20  // Subtle gradient

// Backgrounds
bg-white/5   // Light overlay
bg-white/10  // Card background
border-white/10  // Border

// Text
text-white  // Primary
text-white/60  // Secondary
text-white/40  // Disabled

// Status
text-green-400  // Success
text-blue-400   // Info
text-yellow-400 // Warning
text-red-400    // Error
```

---

## 📱 Responsive Classes

```tsx
// Mobile-first approach
className="grid-cols-1 md:grid-cols-2 lg:grid-cols-4"
className="text-sm md:text-base lg:text-lg"
className="px-4 md:px-6 lg:px-8"
```

---

## 🎯 Common Patterns

### Stats Grid
```tsx
<PageSection icon="📊" title="Stats">
  <PageGrid cols={4} gap="md">
    <StatCard icon="📚" label="Videos" value="12" color="purple" />
    <StatCard icon="🎯" label="Quizzes" value="8" color="blue" />
    <StatCard icon="🏆" label="Score" value="87%" color="green" />
    <StatCard icon="🔥" label="Streak" value="15" color="orange" />
  </PageGrid>
</PageSection>
```

### Progress List
```tsx
<PageSection icon="📚" title="Your Paths">
  <PageGrid cols={2} gap="md">
    <ProgressCard
      icon="🐍"
      title="Python AI"
      progress={75}
      href="/paths/python-ai"
      stats={[{ label: 'Videos', value: '45/60' }]}
    />
    {/* More progress cards */}
  </PageGrid>
</PageSection>
```

### Empty State
```tsx
{items.length === 0 ? (
  <EmptyState
    icon="📚"
    title="No items"
    description="Get started by adding one"
    action={<Button onClick={add}>Add Item</Button>}
  />
) : (
  <PageGrid cols={3}>
    {items.map(item => <ItemCard key={item.id} {...item} />)}
  </PageGrid>
)}
```

### Loading State
```tsx
{loading ? (
  <LoadingState message="Loading dashboard..." />
) : (
  <PageSection>
    {/* Content */}
  </PageSection>
)}
```

---

## ✅ Quick Checklist

Before pushing changes:

- [ ] Used Layout wrapper
- [ ] Added PageHeader
- [ ] Wrapped sections in PageSection
- [ ] Used PageGrid for layouts
- [ ] Replaced custom cards with Card components
- [ ] Added EmptyState where needed
- [ ] Added LoadingState during fetch
- [ ] Used Button component consistently
- [ ] Tested on mobile
- [ ] Tested on desktop
- [ ] No TypeScript errors
- [ ] No ESLint errors

---

## 📚 Full Documentation

See `UI_SYSTEM.md` for complete details and examples.

Visit `/ui-showcase` to see all components live.

Reference `src/pages/dashboard/index.tsx` for complete implementation.
