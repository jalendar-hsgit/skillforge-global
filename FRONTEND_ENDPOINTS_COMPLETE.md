# Complete Frontend Endpoints Documentation
**SkillForge Global - Next.js Application**

Base URL: `http://localhost:3000/`

---

## Table of Contents
1. [Authentication Pages](#authentication-pages)
2. [Home & Core Pages](#home--core-pages)
3. [User Profile Pages](#user-profile-pages)
4. [Mentorship Pages](#mentorship-pages)
5. [Courses & Learning](#courses--learning)
6. [Practice & Coding](#practice--coding)
7. [Resumes & Career](#resumes--career)
8. [Job Tracking](#job-tracking)
9. [Marketplace](#marketplace)
10. [Community & Social](#community--social)
11. [Admin Pages](#admin-pages)
12. [Settings & Preferences](#settings--preferences)
13. [Miscellaneous Pages](#miscellaneous-pages)

---

## Authentication Pages

### 1. Login
**URL:** `http://localhost:3000/login`
**File:** `src/pages/login.tsx`
**Purpose:** User login page
**Access:** Public (unauthenticated)
**Features:**
- Email/password login
- "Forgot password" link
- "Sign up" link
- OAuth integration (GitHub, Google)

### 2. Sign Up
**URL:** `http://localhost:3000/signup`
**File:** `src/pages/signup.tsx`
**Purpose:** Create new account
**Access:** Public
**Features:**
- Registration form
- Email verification
- Password validation
- Login redirect link

### 3. Forgot Password
**URL:** `http://localhost:3000/forgot-password`
**File:** `src/pages/forgot-password.tsx`
**Purpose:** Password reset request
**Access:** Public
**Features:**
- Email input
- Reset link sender
- Resend option

### 4. Reset Password
**URL:** `http://localhost:3000/reset-password`
**File:** `src/pages/reset-password.tsx`
**Purpose:** Password reset form
**Access:** Public (with reset token)
**Features:**
- New password input
- Token validation
- Success confirmation

### 5. OAuth Callback
**URL:** `http://localhost:3000/oauth-callback`
**File:** `src/pages/oauth-callback.tsx`
**Purpose:** OAuth provider redirect
**Access:** Public
**Features:**
- Handles OAuth responses
- Session creation

### 6. GitHub Callback
**URL:** `http://localhost:3000/github-callback`
**File:** `src/pages/github-callback.tsx`
**Purpose:** GitHub OAuth redirect
**Access:** Public
**Features:**
- GitHub account linking

### 7. Logout
**URL:** `http://localhost:3000/logout`
**File:** `src/pages/logout.tsx`
**Purpose:** User logout
**Access:** Protected (authenticated)
**Features:**
- Session termination
- Redirect to home

---

## Home & Core Pages

### 1. Home/Index
**URL:** `http://localhost:3000/`
**File:** `src/pages/index.tsx`
**Purpose:** Landing/home page
**Access:** Public
**Features:**
- Navigation overview
- Featured courses
- Call-to-action buttons
- Hero section

### 2. Dashboard
**URL:** `http://localhost:3000/dashboard`
**File:** `src/pages/dashboard/index.tsx`
**Purpose:** Main user dashboard
**Access:** Protected
**Features:**
- User stats
- Progress tracking
- Recent activities
- Quick action buttons

### 3. Dashboard Analytics
**URL:** `http://localhost:3000/dashboard-analytics`
**File:** `src/pages/dashboard-analytics.tsx`
**Purpose:** Detailed analytics view
**Access:** Protected
**Features:**
- Performance metrics
- Charts and graphs
- Data visualization
- Export options

### 4. Customize Dashboard
**URL:** `http://localhost:3000/customize-dashboard`
**File:** `src/pages/customize-dashboard.tsx`
**Purpose:** Dashboard layout customization
**Access:** Protected
**Features:**
- Widget arrangement
- Theme selection
- Save preferences

### 5. Feed
**URL:** `http://localhost:3000/feed`
**File:** `src/pages/feed.tsx`
**Purpose:** Activity/news feed
**Access:** Protected
**Features:**
- User activity stream
- Course updates
- Social interactions
- Notifications

---

## User Profile Pages

### 1. Profile Index
**URL:** `http://localhost:3000/profile`
**File:** `src/pages/profile/index.tsx`
**Purpose:** Current user profile
**Access:** Protected
**Features:**
- User information
- Skills list
- Achievements
- Connections

### 2. Profile Edit
**URL:** `http://localhost:3000/profile/edit`
**File:** `src/pages/profile/edit.tsx`
**Purpose:** Edit user profile
**Access:** Protected
**Features:**
- Update name, bio
- Add/remove skills
- Profile picture upload
- Social links

### 3. Profile Settings
**URL:** `http://localhost:3000/profile/settings`
**File:** `src/pages/profile/settings.tsx`
**Purpose:** Account settings
**Access:** Protected
**Features:**
- Privacy settings
- Notification preferences
- Email settings
- Account options

### 4. View User Profile
**URL:** `http://localhost:3000/profile/[userId]`
**File:** `src/pages/profile/[userId].tsx`
**Purpose:** View another user's profile
**Access:** Public
**Parameters:**
- `userId`: User ID to view
**Features:**
- Public profile view
- Send message button
- Connect option

---

## Mentorship Pages

### 1. Mentors List
**URL:** `http://localhost:3000/mentors`
**File:** `src/pages/mentors/index.tsx`
**Purpose:** Browse available mentors
**Access:** Public
**Features:**
- Mentor cards
- Filter by expertise
- Rating display
- Hourly rates

### 2. Mentor Profile
**URL:** `http://localhost:3000/mentors/[id]`
**File:** `src/pages/mentors/[id].tsx`
**Purpose:** Individual mentor profile
**Access:** Public
**Parameters:**
- `id`: Mentor ID
**Features:**
- Full profile information
- Reviews/ratings
- Availability schedule
- Book session button

### 3. Book Mentor Session
**URL:** `http://localhost:3000/mentors/[id]/book`
**File:** `src/pages/mentors/[id]/book.tsx`
**Purpose:** Schedule mentorship session
**Access:** Protected
**Parameters:**
- `id`: Mentor ID
**Features:**
- Calendar picker
- Time slot selection
- Payment processing
- Confirmation

### 4. Become a Mentor
**URL:** `http://localhost:3000/mentors/become`
**File:** `src/pages/mentors/become.tsx`
**Purpose:** Mentor application form
**Access:** Protected
**Features:**
- Application form
- Expertise input
- Rate setting
- Submit application

### 5. Mentor Settings
**URL:** `http://localhost:3000/mentors/settings`
**File:** `src/pages/mentors/settings.tsx`
**Purpose:** Mentor configuration
**Access:** Protected (mentors only)
**Features:**
- Availability management
- Rate adjustment
- Profile customization
- Bio/expertise update

### 6. My Sessions
**URL:** `http://localhost:3000/mentors/my-sessions`
**File:** `src/pages/mentors/my-sessions.tsx`
**Purpose:** View scheduled sessions
**Access:** Protected
**Features:**
- Upcoming sessions
- Past sessions
- Session details
- Rescheduling options

### 7. Earnings
**URL:** `http://localhost:3000/mentors/earnings`
**File:** `src/pages/mentors/earnings.tsx`
**Purpose:** Mentor earnings summary
**Access:** Protected (mentors only)
**Features:**
- Total earnings
- Monthly breakdown
- Session earnings
- Payment history

### 8. Session Details
**URL:** `http://localhost:3000/mentors/sessions/[id]`
**File:** `src/pages/mentors/sessions/[id].tsx`
**Purpose:** Individual session details
**Access:** Protected
**Parameters:**
- `id`: Session ID
**Features:**
- Session info
- Video call link
- Notes section
- Feedback option

### Mentor Dashboard

#### Dashboard Index
**URL:** `http://localhost:3000/mentors/dashboard`
**File:** `src/pages/mentors/dashboard/index.tsx`
**Purpose:** Mentor dashboard home
**Access:** Protected (mentors only)
**Features:**
- Overview metrics
- Quick actions
- Recent activity

#### Dashboard Profile
**URL:** `http://localhost:3000/mentors/dashboard/profile`
**File:** `src/pages/mentors/dashboard/profile.tsx`
**Purpose:** Manage mentor profile
**Features:**
- Profile editing
- Photo upload
- Bio management

#### Dashboard Sessions
**URL:** `http://localhost:3000/mentors/dashboard/sessions`
**File:** `src/pages/mentors/dashboard/sessions.tsx`
**Purpose:** Manage all sessions
**Features:**
- Session list
- Status filtering
- Bulk actions

#### Dashboard Students
**URL:** `http://localhost:3000/mentors/dashboard/students`
**File:** `src/pages/mentors/dashboard/students.tsx`
**Purpose:** View all mentee profiles
**Features:**
- Student list
- Interaction history
- Notes section

#### Dashboard Earnings
**URL:** `http://localhost:3000/mentors/dashboard/earnings`
**File:** `src/pages/mentors/dashboard/earnings.tsx`
**Purpose:** Earnings management
**Features:**
- Earnings summary
- Payment history
- Withdrawal options

#### Dashboard Payouts
**URL:** `http://localhost:3000/mentors/dashboard/payouts`
**File:** `src/pages/mentors/dashboard/payouts.tsx`
**Purpose:** Payout management
**Features:**
- Bank account linking
- Payout schedule
- Transaction history

#### Dashboard Analytics
**URL:** `http://localhost:3000/mentors/dashboard/analytics`
**File:** `src/pages/mentors/dashboard/analytics.tsx`
**Purpose:** Mentor analytics
**Features:**
- Performance metrics
- Session trends
- Rating analytics

#### Dashboard Reviews
**URL:** `http://localhost:3000/mentors/dashboard/reviews`
**File:** `src/pages/mentors/dashboard/reviews.tsx`
**Purpose:** View student reviews
**Features:**
- Review list
- Rating breakdown
- Response to reviews

#### Dashboard Verification
**URL:** `http://localhost:3000/mentors/dashboard/verification`
**File:** `src/pages/mentors/dashboard/verification.tsx`
**Purpose:** Mentor verification status
**Features:**
- Verification status
- Document upload
- Status updates

---

## Courses & Learning

### 1. Learning Paths
**URL:** `http://localhost:3000/learning-paths`
**File:** `src/pages/learning-paths.tsx`
**Purpose:** Browse learning paths
**Access:** Public
**Features:**
- Path cards
- Difficulty levels
- Enrollment button
- Progress tracking

### 2. Learning Path Detail
**URL:** `http://localhost:3000/learning-paths/[id]`
**File:** `src/pages/learning-paths/[id].tsx`
**Purpose:** Specific learning path
**Access:** Public
**Parameters:**
- `id`: Path ID
**Features:**
- Curriculum overview
- Course sequence
- Enroll button
- Completion percentage

### 3. Learning Paths Alternative
**URL:** `http://localhost:3000/paths`
**File:** `src/pages/paths.tsx`
**Purpose:** Alternative paths view
**Access:** Public
**Features:**
- Path browsing
- Filtering options

### 4. Learning Paths Detail Alternative
**URL:** `http://localhost:3000/paths/[slug]`
**File:** `src/pages/paths/[slug].tsx`
**Purpose:** Path by slug
**Access:** Public
**Parameters:**
- `slug`: Path slug
**Features:**
- Full path details
- Module breakdown

---

## Practice & Coding

### 1. Practice Index
**URL:** `http://localhost:3000/practice`
**File:** `src/pages/practice/index.tsx`
**Purpose:** Coding practice hub
**Access:** Public
**Features:**
- Problem list
- Difficulty filter
- Search functionality
- Solutions link

### 2. Practice Problem
**URL:** `http://localhost:3000/practice/[slug]`
**File:** `src/pages/practice/[slug].tsx`
**Purpose:** Individual coding problem
**Access:** Public
**Parameters:**
- `slug`: Problem slug
**Features:**
- Problem statement
- Code editor
- Compiler/runner
- Sample test cases
- Solution submission

### 3. Practice Submissions
**URL:** `http://localhost:3000/practice/submissions`
**File:** `src/pages/practice/submissions.tsx`
**Purpose:** View all submissions
**Access:** Protected
**Features:**
- Submission history
- Status tracking
- Code review option

### 4. Code Simulator
**URL:** `http://localhost:3000/practice/simulator/[type]`
**File:** `src/pages/practice/simulator/[type].tsx`
**Purpose:** Language-specific simulator
**Access:** Public
**Parameters:**
- `type`: Language type (python, javascript, java, etc.)
**Features:**
- Code editor
- Real-time compilation
- Output display
- Examples

### 5. Code Snippets
**URL:** `http://localhost:3000/code-snippets`
**File:** `src/pages/code-snippets/index.tsx`
**Purpose:** Browse code snippets
**Access:** Public
**Features:**
- Snippet search
- Language filter
- Copy to clipboard
- Share options

### 6. Quiz (Practice)
**URL:** `http://localhost:3000/quiz/[slug]`
**File:** `src/pages/quiz/[slug].tsx`
**Purpose:** Quiz by slug
**Access:** Public
**Parameters:**
- `slug`: Quiz slug
**Features:**
- Quiz questions
- Answer submission
- Score calculation

### 7. Interactive Quiz
**URL:** `http://localhost:3000/quiz/interactive-[slug]`
**File:** `src/pages/quiz/interactive-[slug].tsx`
**Purpose:** Interactive quiz mode
**Parameters:**
- `slug`: Quiz slug
**Features:**
- Real-time feedback
- Progress tracking
- Instant answers

### 8. Quiz Stream
**URL:** `http://localhost:3000/quiz/stream`
**File:** `src/pages/quiz/stream.tsx`
**Purpose:** Quiz streaming/live quiz
**Features:**
- Live quiz session
- Real-time questions

### 9. Quiz Results
**URL:** `http://localhost:3000/quizzes/[id]/results`
**File:** `src/pages/quizzes/[id]/results.tsx`
**Purpose:** Quiz result details
**Access:** Protected
**Parameters:**
- `id`: Quiz ID
**Features:**
- Score display
- Answer review
- Performance analysis

### 10. AI Hints
**URL:** `http://localhost:3000/ai-hints`
**File:** `src/pages/ai-hints.tsx`
**Purpose:** AI-powered hints for problems
**Access:** Protected
**Features:**
- Problem solving hints
- Step-by-step guidance
- Code suggestions

### 11. Hint Preferences
**URL:** `http://localhost:3000/hint-preferences`
**File:** `src/pages/hint-preferences.tsx`
**Purpose:** Customize hint settings
**Access:** Protected
**Features:**
- Difficulty level preference
- Language preference
- Hint frequency

### 12. Leaderboard
**URL:** `http://localhost:3000/leaderboard`
**File:** `src/pages/leaderboard/index.tsx`
**Purpose:** Coding leaderboard
**Access:** Public
**Features:**
- User rankings
- Points/scores
- Filters by time period
- Monthly challenges

### 13. Achievements
**URL:** `http://localhost:3000/achievements`
**File:** `src/pages/achievements.tsx`
**Purpose:** User achievements/badges
**Access:** Public
**Features:**
- Achievement list
- Progress tracking
- Badge display
- Unlock conditions

---

## Resumes & Career

### 1. Resumes Index
**URL:** `http://localhost:3000/resumes`
**File:** `src/pages/resumes/index.tsx`
**Purpose:** User's resumes list
**Access:** Protected
**Features:**
- Resume list
- Create new
- Edit/delete options
- Download options

### 2. New Resume
**URL:** `http://localhost:3000/resumes/new`
**File:** `src/pages/resumes/new.tsx`
**Purpose:** Create new resume
**Access:** Protected
**Features:**
- Resume builder
- Template selection
- Field input
- Real-time preview

### 3. Edit Resume
**URL:** `http://localhost:3000/resumes/[id]/edit`
**File:** `src/pages/resumes/[id]/edit.tsx`
**Purpose:** Edit existing resume
**Access:** Protected
**Parameters:**
- `id`: Resume ID
**Features:**
- Full editing
- Section management
- Formatting tools

### 4. Resume Preview
**URL:** `http://localhost:3000/resumes/[id]/preview`
**File:** `src/pages/resumes/[id]/preview.tsx`
**Purpose:** Preview resume
**Access:** Protected
**Parameters:**
- `id`: Resume ID
**Features:**
- Formatted view
- Print option
- Download PDF

### 5. Resume Export
**URL:** `http://localhost:3000/resumes/[id]/export`
**File:** `src/pages/resumes/[id]/export.tsx`
**Purpose:** Export resume
**Access:** Protected
**Parameters:**
- `id`: Resume ID
**Features:**
- PDF export
- DOCX export
- Format selection

### 6. ATS Score
**URL:** `http://localhost:3000/resumes/[id]/ats-score`
**File:** `src/pages/resumes/[id]/ats-score.tsx`
**Purpose:** ATS compatibility score
**Access:** Protected
**Parameters:**
- `id`: Resume ID
**Features:**
- Score calculation
- Improvement suggestions
- Detailed report

### 7. Sharing
**URL:** `http://localhost:3000/resumes/[id]/sharing`
**File:** `src/pages/resumes/[id]/sharing.tsx`
**Purpose:** Share resume publicly
**Access:** Protected
**Parameters:**
- `id`: Resume ID
**Features:**
- Public link generation
- QR code
- Share options

### 8. Versions
**URL:** `http://localhost:3000/resumes/[id]/versions`
**File:** `src/pages/resumes/[id]/versions.tsx`
**Purpose:** Resume version history
**Access:** Protected
**Parameters:**
- `id`: Resume ID
**Features:**
- Version list
- Restore option
- Comparison

### 9. Resume Templates
**URL:** `http://localhost:3000/resumes/templates`
**File:** `src/pages/resumes/templates.tsx`
**Purpose:** Browse resume templates
**Access:** Public
**Features:**
- Template gallery
- Preview options
- Use template button

### 10. Resume Compare
**URL:** `http://localhost:3000/resumes/compare`
**File:** `src/pages/resumes/compare.tsx`
**Purpose:** Compare multiple resumes
**Access:** Protected
**Features:**
- Side-by-side comparison
- Difference highlighting

### 11. Resume Import
**URL:** `http://localhost:3000/resumes/import`
**File:** `src/pages/resumes/import.tsx`
**Purpose:** Import resume
**Access:** Protected
**Features:**
- File upload
- Auto-parsing
- Field mapping

### 12. Resume Diagnostics
**URL:** `http://localhost:3000/resumes/diagnostics`
**File:** `src/pages/resumes/diagnostics.tsx`
**Purpose:** Resume analysis
**Access:** Protected
**Features:**
- Grammar check
- Content analysis
- Improvement tips

---

## Job Tracking

### 1. Jobs
**URL:** `http://localhost:3000/jobs`
**File:** `src/pages/jobs/index.tsx`
**Purpose:** Job listings
**Access:** Public
**Features:**
- Job search
- Filters
- Apply button
- Save jobs

### 2. Job Tracker
**URL:** `http://localhost:3000/job-tracker/add`
**File:** `src/pages/job-tracker/add.tsx`
**Purpose:** Add job application
**Access:** Protected
**Features:**
- Application form
- Company input
- Position details
- Submission date

### 3. Job Analytics
**URL:** `http://localhost:3000/job-tracker/analytics`
**File:** `src/pages/job-tracker/analytics.tsx`
**Purpose:** Job application analytics
**Access:** Protected
**Features:**
- Application stats
- Response rate
- Pipeline visualization
- Conversion metrics

---

## Marketplace

### 1. Marketplace Index
**URL:** `http://localhost:3000/marketplace`
**File:** `src/pages/marketplace/index.tsx`
**Purpose:** Digital products marketplace
**Access:** Public
**Features:**
- Product listing
- Search and filter
- Add to cart
- Product details link

### 2. Marketplace Cart
**URL:** `http://localhost:3000/marketplace/cart`
**File:** `src/pages/marketplace/cart.tsx`
**Purpose:** Shopping cart
**Access:** Protected
**Features:**
- Cart items
- Quantity adjustment
- Remove items
- Checkout button

### 3. Marketplace Orders
**URL:** `http://localhost:3000/marketplace/orders`
**File:** `src/pages/marketplace/orders.tsx`
**Purpose:** Purchase history
**Access:** Protected
**Features:**
- Order list
- Order details
- Download products
- Leave reviews

### Seller Pages

#### Seller Dashboard
**URL:** `http://localhost:3000/marketplace/seller`
**File:** `src/pages/marketplace/seller/index.tsx`
**Purpose:** Seller dashboard home
**Access:** Protected (sellers only)
**Features:**
- Sales overview
- Quick actions
- Recent orders

#### Create Product
**URL:** `http://localhost:3000/marketplace/seller/create-product`
**File:** `src/pages/marketplace/seller/create-product.tsx`
**Purpose:** Add new product
**Access:** Protected (sellers only)
**Features:**
- Product form
- File upload
- Pricing input
- Publishing

#### Seller Products
**URL:** `http://localhost:3000/marketplace/seller/products`
**File:** `src/pages/marketplace/seller/products.tsx`
**Purpose:** Manage products
**Access:** Protected (sellers only)
**Features:**
- Product list
- Edit/delete options
- Stock management
- Publish/unpublish

#### Seller Orders
**URL:** `http://localhost:3000/marketplace/seller/orders`
**File:** `src/pages/marketplace/seller/orders.tsx`
**Purpose:** Sales orders
**Access:** Protected (sellers only)
**Features:**
- Order list
- Order details
- Fulfillment tracking
- Customer communication

#### Seller Analytics
**URL:** `http://localhost:3000/marketplace/seller/analytics`
**File:** `src/pages/marketplace/seller/analytics.tsx`
**Purpose:** Sales analytics
**Access:** Protected (sellers only)
**Features:**
- Revenue charts
- Sales trends
- Customer analytics
- Performance metrics

---

## Community & Social

### 1. Activity Feed
**URL:** `http://localhost:3000/community/activity-feed`
**File:** `src/pages/community/activity-feed.tsx`
**Purpose:** Community activity
**Access:** Public
**Features:**
- Activity stream
- Filtering options
- Comment/like actions

### 2. Forums
**URL:** `http://localhost:3000/community/forums`
**File:** `src/pages/community/forums/index.tsx`
**Purpose:** Discussion forums
**Access:** Public
**Features:**
- Forum categories
- Thread list
- Create topic button

### 3. Forum Topic
**URL:** `http://localhost:3000/community/forums/topic/[topicId]`
**File:** `src/pages/community/forums/topic/[topicId].tsx`
**Purpose:** Individual forum topic
**Access:** Public
**Parameters:**
- `topicId`: Topic ID
**Features:**
- Thread discussion
- Reply posting
- Voting system

### 4. Social Index
**URL:** `http://localhost:3000/social`
**File:** `src/pages/social/index.tsx`
**Purpose:** Social features
**Access:** Protected
**Features:**
- User suggestions
- Follow options
- Social feed

### 5. Social Feed
**URL:** `http://localhost:3000/social/feed`
**File:** `src/pages/social/feed/index.tsx`
**Purpose:** Personalized feed
**Access:** Protected
**Features:**
- Following activity
- Post interactions
- Share options

### 6. Following
**URL:** `http://localhost:3000/social/following`
**File:** `src/pages/social/following.tsx`
**Purpose:** Manage follows
**Access:** Protected
**Features:**
- Following list
- Unfollow option
- View profiles

### 7. Messages
**URL:** `http://localhost:3000/messages`
**File:** `src/pages/messages/index.tsx`
**Purpose:** Direct messaging
**Access:** Protected
**Features:**
- Conversation list
- Send messages
- Message history

### 8. Notifications
**URL:** `http://localhost:3000/notifications`
**File:** `src/pages/notifications/index.tsx`
**Purpose:** Notification center
**Access:** Protected
**Features:**
- Notification list
- Mark as read
- Delete options
- Filter by type

---

## Admin Pages

### 1. Admin Dashboard
**URL:** `http://localhost:3000/admin`
**File:** `src/pages/admin/index.tsx`
**Purpose:** Admin control panel
**Access:** Protected (admins only)
**Features:**
- System overview
- User management
- Content management
- Analytics

---

## Settings & Preferences

### 1. Security
**URL:** `http://localhost:3000/security`
**File:** `src/pages/security.tsx`
**Purpose:** Security settings
**Access:** Protected
**Features:**
- Password management
- Two-factor authentication
- Session management
- Login history

### 2. PWA Settings
**URL:** `http://localhost:3000/pwa-settings`
**File:** `src/pages/pwa-settings.tsx`
**Purpose:** Progressive Web App settings
**Access:** Protected
**Features:**
- Install options
- Offline mode
- Notifications

---

## Miscellaneous Pages

### 1. Contact
**URL:** `http://localhost:3000/contact`
**File:** `src/pages/contact.tsx`
**Purpose:** Contact form
**Access:** Public
**Features:**
- Contact form
- Support options
- Email submission

### 2. Pricing
**URL:** `http://localhost:3000/pricing`
**File:** `src/pages/pricing.tsx`
**Purpose:** Pricing page
**Access:** Public
**Features:**
- Plan comparison
- Feature list
- CTA buttons

### 3. Pricing New
**URL:** `http://localhost:3000/pricing-new`
**File:** `src/pages/pricing-new.tsx`
**Purpose:** Updated pricing page
**Access:** Public

### 4. Premium
**URL:** `http://localhost:3000/premium`
**File:** `src/pages/premium.tsx`
**Purpose:** Premium features
**Access:** Public
**Features:**
- Premium benefits
- Subscribe button
- Feature highlights

### 5. Subscribe
**URL:** `http://localhost:3000/subscribe`
**File:** `src/pages/subscribe.tsx`
**Purpose:** Subscription page
**Access:** Public
**Features:**
- Plan selection
- Payment processing
- Confirmation

### 6. Compare Plans
**URL:** `http://localhost:3000/compare-plans`
**File:** `src/pages/compare-plans.tsx`
**Purpose:** Plan comparison
**Access:** Public
**Features:**
- Side-by-side comparison
- Feature highlights
- Choose button

### 7. Privacy
**URL:** `http://localhost:3000/privacy`
**File:** `src/pages/privacy.tsx`
**Purpose:** Privacy policy
**Access:** Public

### 8. Terms
**URL:** `http://localhost:3000/terms`
**File:** `src/pages/terms.tsx`
**Purpose:** Terms of service
**Access:** Public

### 9. FAQ
**URL:** `http://localhost:3000/faq`
**File:** `src/pages/faq.tsx`
**Purpose:** Frequently asked questions
**Access:** Public
**Features:**
- Question list
- Answer expandable
- Search functionality

### 10. Company
**URL:** `http://localhost:3000/company`
**File:** `src/pages/company.tsx`
**Purpose:** Company information
**Access:** Public
**Features:**
- About company
- Team info
- Company values

### 11. Careers
**URL:** `http://localhost:3000/careers`
**File:** `src/pages/careers.tsx`
**Purpose:** Job listings (company)
**Access:** Public
**Features:**
- Open positions
- Apply button
- Job details

### 12. Referral Program
**URL:** `http://localhost:3000/referral_program`
**File:** `src/pages/referral_program.tsx`
**Purpose:** Referral rewards
**Access:** Protected
**Features:**
- Referral link
- Earnings tracking
- Referral history

### 13. Trending
**URL:** `http://localhost:3000/trending`
**File:** `src/pages/trending.tsx`
**Purpose:** Trending content
**Access:** Public
**Features:**
- Trending courses
- Popular problems
- Trending topics

### 14. Recommendations
**URL:** `http://localhost:3000/recommendations`
**File:** `src/pages/recommendations.tsx`
**Purpose:** Personalized recommendations
**Access:** Protected
**Features:**
- Recommended courses
- Suggested problems
- Personalized content

### 15. Teams
**URL:** `http://localhost:3000/teams`
**File:** `src/pages/teams.tsx`
**Purpose:** Team collaboration
**Access:** Protected
**Features:**
- Team list
- Create team
- Team management

### 16. Contests
**URL:** `http://localhost:3000/contests`
**File:** `src/pages/contests/index.tsx`
**Purpose:** Coding contests
**Access:** Public
**Features:**
- Contest list
- Register for contest
- Contest details

### 17. Watch/Video
**URL:** `http://localhost:3000/watch/[id]`
**File:** `src/pages/watch/[id].tsx`
**Purpose:** Video player page
**Access:** Public
**Parameters:**
- `id`: Video ID
**Features:**
- Video playback
- Comments
- Related videos

### 18. Coins
**URL:** `http://localhost:3000/coins`
**File:** `src/pages/coins.tsx`
**Purpose:** Coin/currency system
**Access:** Protected
**Features:**
- Coin balance
- Coin history
- Coin shop

### 19. Coins Database
**URL:** `http://localhost:3000/coins/[id]`
**File:** `src/pages/coins/[id].tsx`
**Purpose:** Coin management
**Access:** Protected
**Parameters:**
- `id`: Coin transaction ID

### 20. UI Showcase
**URL:** `http://localhost:3000/ui-showcase`
**File:** `src/pages/ui-showcase.tsx`
**Purpose:** Design system showcase
**Access:** Public
**Features:**
- Component library
- Design patterns
- Examples

### 21. Status
**URL:** `http://localhost:3000/status`
**File:** `src/pages/status.tsx`
**Purpose:** System status page
**Access:** Public
**Features:**
- Service status
- Incident history
- System health

### 22. GitHub Integration
**URL:** `http://localhost:3000/github-integration`
**File:** `src/pages/github-integration.tsx`
**Purpose:** GitHub account linking
**Access:** Protected
**Features:**
- Link GitHub
- Authorize app
- Repository sync

### 23. AI
**URL:** `http://localhost:3000/ai`
**File:** `src/pages/ai.tsx`
**Purpose:** AI features hub
**Access:** Protected
**Features:**
- AI tools
- AI assistance
- Feature overview

---

## Error Pages

### 404 Not Found
**URL:** Any undefined route
**File:** `src/pages/404.tsx`
**Purpose:** Page not found
**Features:**
- Error message
- Home link
- Search option

### 500 Server Error
**URL:** Server error condition
**File:** `src/pages/500.tsx`
**Purpose:** Server error
**Features:**
- Error message
- Support contact
- Home link

### Unauthorized
**URL:** `http://localhost:3000/unauthorized`
**File:** `src/pages/unauthorized.tsx`
**Purpose:** Access denied
**Features:**
- Error message
- Login option
- Home link

---

## Quick Navigation Guide

### By User Type

#### **Unauthenticated User (Public)**
- Home: `/`
- Login: `/login`
- Sign Up: `/signup`
- Browse Mentors: `/mentors`
- Browse Courses: `/learning-paths`, `/paths`
- Browse Jobs: `/jobs`
- Practice Problems: `/practice`
- Marketplace: `/marketplace`
- Community: `/community/forums`, `/community/activity-feed`
- Information: `/pricing`, `/privacy`, `/terms`, `/faq`, `/company`, `/contact`

#### **Authenticated Student**
- Dashboard: `/dashboard`
- My Profile: `/profile`
- Edit Profile: `/profile/edit`
- My Courses: `/learning-paths`
- Practice: `/practice`
- My Resumes: `/resumes`
- Job Tracker: `/job-tracker`
- Mentorship: `/mentors/my-sessions`
- Marketplace: `/marketplace/cart`, `/marketplace/orders`
- Messages: `/messages`
- Notifications: `/notifications`
- Social: `/social`, `/social/feed`, `/social/following`

#### **Authenticated Mentor**
- Dashboard: `/mentors/dashboard`
- Profile Settings: `/mentors/dashboard/profile`
- Sessions: `/mentors/dashboard/sessions`
- Students: `/mentors/dashboard/students`
- Earnings: `/mentors/dashboard/earnings`
- Payouts: `/mentors/dashboard/payouts`
- Analytics: `/mentors/dashboard/analytics`
- Reviews: `/mentors/dashboard/reviews`
- Verification: `/mentors/dashboard/verification`
- Availability: `/mentors/settings`

#### **Marketplace Seller**
- Seller Dashboard: `/marketplace/seller`
- Create Product: `/marketplace/seller/create-product`
- My Products: `/marketplace/seller/products`
- Sales Orders: `/marketplace/seller/orders`
- Analytics: `/marketplace/seller/analytics`

#### **Admin**
- Admin Panel: `/admin`
- Dashboard: `/dashboard`

---

## Access Control Summary

| Page Type | Public | Authenticated | Admin | Mentor |
|-----------|--------|---------------|-------|--------|
| Login/Signup | ✅ | ❌ | ❌ | ❌ |
| Dashboard | ❌ | ✅ | ✅ | ✅ |
| Profile | ❌ | ✅ | ✅ | ✅ |
| Mentors Browse | ✅ | ✅ | ✅ | ✅ |
| Mentor Dashboard | ❌ | ❌ | ❌ | ✅ |
| Courses | ✅ | ✅ | ✅ | ✅ |
| Practice | ✅ | ✅ | ✅ | ✅ |
| Resumes | ❌ | ✅ | ✅ | ✅ |
| Job Tracker | ❌ | ✅ | ✅ | ✅ |
| Marketplace | ✅ | ✅ | ✅ | ✅ |
| Seller Pages | ❌ | ✅ | ✅ | ✅ |
| Admin Panel | ❌ | ❌ | ✅ | ❌ |
| Community | ✅ | ✅ | ✅ | ✅ |
| Messages | ❌ | ✅ | ✅ | ✅ |

---

## Dynamic Routes Explanation

### Route Parameters

**`[id]` or `[slug]`** - Represents a dynamic segment

**Examples:**
- `/mentors/[id]` → `/mentors/123` (where 123 is mentor ID)
- `/resumes/[id]/edit` → `/resumes/456/edit` (where 456 is resume ID)
- `/paths/[slug]` → `/paths/python-basics` (where python-basics is the path slug)

---

## How to Access the Application

### Step 1: Start the Frontend Dev Server
```bash
npm run dev
```
Server runs on: `http://localhost:3000`

### Step 2: Create Account or Login
- Navigate to `/login` or `/signup`
- Enter credentials

### Step 3: Navigate Using
- Top navigation bar
- Sidebar menu
- Direct URL access
- Internal links

### Step 4: Explore Features
- Click on menu items
- Use search/filter functionality
- Access user-specific sections from dashboard

---

## Common Navigation Patterns

### From Home Page
1. Click "Get Started" → `/signup`
2. Click "Browse Courses" → `/learning-paths`
3. Click "Find Mentors" → `/mentors`
4. Click "Practice" → `/practice`

### From Dashboard
1. Access via `/dashboard`
2. Quick action buttons for common features
3. Activity feed and notifications
4. Personalized recommendations

### From Profile
1. `/profile` - View own profile
2. `/profile/edit` - Edit profile information
3. `/profile/settings` - Change settings
4. `/profile/[userId]` - View other users

---

## Notes

- All routes starting with `/api/` are API endpoints, not UI pages
- Protected pages automatically redirect to `/login` if not authenticated
- Role-based access control enforces permissions on protected pages
- Dynamic routes require parameters in the URL
- Trailing slashes are optional

---

**Last Updated:** January 5, 2026
**Application:** SkillForge Global
**Framework:** Next.js 14.2.33
**Base URL:** http://localhost:3000/
