# UI Migration Checklist

Track progress of migrating pages to the new UI system.

## ✅ Completed

- [x] **UI Component Library** - Created PageLayout, Cards, updated Layout
- [x] **UI Showcase Page** (`/ui-showcase`) - Live demo of all components
- [x] **Dashboard** (`/dashboard`) - Reference implementation
- [x] **Documentation** (`UI_SYSTEM.md`) - Complete guide

## 🔄 In Progress

- [ ] None currently

## ⏳ Pending Pages

### High Priority (User-Facing)

- [ ] **Home Page** (`/`)
  - Update hero section with new components
  - Use FeatureCard for features
  - Apply new button styles
  
- [ ] **Paths Listing** (`/paths`)
  - Convert path cards to FeatureCard
  - Use PageHeader with breadcrumbs
  - Apply PageGrid layout
  
- [ ] **Individual Path** (`/paths/[slug]`)
  - Use ProgressCard for video list
  - Add StatCard for path stats
  - Improve mobile layout
  
- [ ] **Login** (`/login`)
  - Simplify with PageContainer variant="glass"
  - Update button styles
  - Add AlertCard for errors
  
- [ ] **Signup** (`/signup`)
  - Match login page styling
  - Use consistent button variants
  - Improve form layout
  
- [ ] **Pricing** (`/pricing`)
  - Convert plan cards to ActionCard or custom PricingCard
  - Use PageSection for organization
  - Add StatCard for feature comparisons

### Medium Priority (Mentor Features)

- [ ] **Mentor Browse** (`/mentors`)
  - Create MentorCard based on FeatureCard
  - Use PageGrid for mentor listing
  - Add filters with PageSection
  
- [ ] **Mentor Dashboard** (`/mentors/dashboard`)
  - Similar to main dashboard structure
  - StatCard for mentor metrics
  - ProgressCard for upcoming sessions
  
- [ ] **Mentor Earnings** (`/mentors/earnings`)
  - StatCard for earnings stats
  - Custom table or list layout
  - ActionCard for payout requests
  
- [ ] **Mentor Settings** (`/mentors/settings`)
  - PageContainer for forms
  - AlertCard for notifications
  - Consistent button usage

### Lower Priority (Secondary Pages)

- [ ] **AI Assistant** (`/ai`)
  - Update chat interface styling
  - Use PageContainer variants
  - Improve message bubbles
  
- [ ] **Quiz Pages** (`/quiz/[slug]`)
  - Card-based question layout
  - StatCard for quiz results
  - ProgressCard for quiz progress
  
- [ ] **FAQ** (`/faq`)
  - Use PageSection for categories
  - Improve accordion styling
  - Add EmptyState if needed
  
- [ ] **Contact** (`/contact`)
  - PageContainer for form
  - AlertCard for success/error
  - Improve form styling
  
- [ ] **Company/About** (`/company`)
  - Use FeatureCard for team/values
  - PageSection for organization
  - Update content layout
  
- [ ] **Careers** (`/careers`)
  - ActionCard for job listings
  - PageGrid for opportunities
  - Improve CTAs
  
- [ ] **Privacy** (`/privacy`)
  - PageContainer for content
  - Better typography hierarchy
  - Add table of contents
  
- [ ] **Terms** (`/terms`)
  - Match privacy page styling
  - PageContainer for content
  - Improve readability
  
- [ ] **Security** (`/security`)
  - StatCard for security metrics
  - FeatureCard for security features
  - Update layout

### Admin Pages

- [ ] **Admin Courses** (`/admin/courses`)
  - Use PageGrid for course management
  - StatCard for course stats
  - ActionCard for admin actions
  - Add EmptyState when no courses

## 🎨 Custom Components Needed

These page-specific components should be built using our base components:

- [ ] **MentorCard** - Extend FeatureCard
  - Add mentor avatar
  - Show expertise tags
  - Display rating/reviews
  - Include availability indicator
  
- [ ] **CourseCard** - Extend FeatureCard
  - Add thumbnail image
  - Show difficulty level
  - Display progress if enrolled
  - Include duration/video count
  
- [ ] **PricingCard** - Extend ActionCard
  - Add pricing tiers
  - Feature list
  - Highlight "popular" plan
  - CTA button styling
  
- [ ] **SessionCard** - Custom component
  - Mentor info
  - Session date/time
  - Status indicator
  - Action buttons (join/cancel/reschedule)
  
- [ ] **QuizQuestionCard** - Custom component
  - Question text
  - Answer options
  - Submit button
  - Feedback display

## 📝 Migration Steps (Per Page)

1. **Backup**: Copy current file if major changes
2. **Imports**: Add PageLayout and Cards imports
3. **Layout**: Wrap in `<Layout maxWidth="7xl">`
4. **Header**: Replace custom header with `<PageHeader>`
5. **Sections**: Wrap content groups in `<PageSection>`
6. **Grids**: Replace manual grids with `<PageGrid>`
7. **Cards**: Replace custom cards with appropriate Card components
8. **States**: Add EmptyState, LoadingState, ErrorState where needed
9. **Buttons**: Update all buttons to use Button component
10. **Test**: Verify responsive behavior on mobile/tablet/desktop
11. **Review**: Check accessibility and visual consistency

## 🔍 Testing Checklist (Per Page)

- [ ] Mobile view (320px, 375px, 428px)
- [ ] Tablet view (768px, 1024px)
- [ ] Desktop view (1280px, 1920px)
- [ ] Dark mode appearance
- [ ] Loading states
- [ ] Empty states
- [ ] Error states
- [ ] Button hover effects
- [ ] Link navigation
- [ ] Keyboard navigation
- [ ] Screen reader compatibility

## 🎯 Success Criteria

- All pages use Layout component
- Consistent PageHeader across pages
- No custom card styles (use Card components)
- Responsive on all screen sizes
- Proper empty/loading/error states
- Consistent button styling
- Proper semantic HTML
- TypeScript strict mode passing
- No ESLint errors
- Visual consistency verified

## 📊 Progress Tracking

**Total Pages**: 25
**Completed**: 2 (8%)
**In Progress**: 0 (0%)
**Remaining**: 23 (92%)

Update this checklist as you migrate each page!

---

## Quick Reference

**Start Migration**:
```bash
# Open file
code src/pages/[page-name].tsx

# Check UI Showcase for examples
http://localhost:3000/ui-showcase

# Reference Dashboard implementation
code src/pages/dashboard/index.tsx
```

**Component Imports**:
```tsx
import Layout from '@/components/Layout'
import { PageHeader, PageContainer, PageSection, PageGrid, 
         EmptyState, LoadingState, ErrorState } from '@/components/PageLayout'
import { StatCard, FeatureCard, ProgressCard, 
         AlertCard, ActionCard } from '@/components/Cards'
import { Button } from '@/components/Button'
```

**Typical Page Structure**:
```tsx
<Layout maxWidth="7xl">
  <PageHeader icon="🎯" title="Page Title" subtitle="Description" />
  
  <PageSection icon="📊" title="Section Title">
    <PageGrid cols={3} gap="md">
      {/* Cards here */}
    </PageGrid>
  </PageSection>
</Layout>
```
