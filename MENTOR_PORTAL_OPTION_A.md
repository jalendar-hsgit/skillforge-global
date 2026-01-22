# Option A Implementation: Mentor Portal Development

**Status:** Ready to Build  
**Scope:** 5 hours  
**Priority:** HIGH - Core mentor functionality

---

## 1. MENTOR PORTAL MISSING FEATURES

### 1.1 Backend Requirements

#### Missing Endpoints

```
GET  /api/v1x/mentor-portal/dashboard
     - Return: earnings_this_month, total_earnings, sessions_completed, 
       rating, students_count, pending_sessions, upcoming_sessions
     
GET  /api/v1x/mentor-portal/earnings
     - Params: ?period=month|year|all&from_date=&to_date=
     - Return: Array of earnings records with timestamps
     
POST /api/v1x/mentor-portal/request-payout
     - Body: amount, payment_method, notes
     - Return: Payout request record with status
     
GET  /api/v1x/mentor-portal/payouts
     - Return: List of payout requests with statuses
     
GET  /api/v1x/mentor-portal/performance
     - Return: completion_rate, avg_rating, response_time, 
       student_feedback_summary
     
PUT  /api/v1x/mentor-portal/profile
     - Body: bio, expertise, hourly_rate, max_students, bio_url
     - Return: Updated mentor profile
     
GET  /api/v1x/mentor-portal/sessions
     - Params: ?status=upcoming|completed|cancelled
     - Return: List of mentor sessions
     
PATCH /api/v1x/mentor-portal/availability/{id}
     - Body: day_of_week, start_time, end_time
     - Return: Updated availability slot
     
GET  /api/v1x/mentor-portal/students
     - Return: List of students with details
     
GET  /api/v1x/mentor-portal/reviews
     - Return: List of reviews with student info
```

### 1.2 Data Models Needed

**MentorEarnings (New Model):**
```python
class MentorEarnings(Base):
    id: int (PK)
    mentor_id: int (FK)
    order_id: int (FK)
    session_id: int (FK)
    amount: Decimal
    currency: str = "USD"
    transaction_type: str (course, session, product)
    status: str (completed, pending, refunded)
    created_at: datetime
    
    mentor: Relationship
    order: Relationship
    session: Relationship
```

**PayoutRequest (New Model):**
```python
class PayoutRequest(Base):
    id: int (PK)
    mentor_id: int (FK)
    amount: Decimal
    payment_method: str (stripe, bank_transfer, paypal)
    status: str (pending, processing, completed, failed)
    requested_at: datetime
    processed_at: datetime
    notes: str
    failure_reason: str
    
    mentor: Relationship
```

**MentorPerformance (View Model - Computed):**
```python
@dataclass
class MentorPerformance:
    total_sessions: int
    completed_sessions: int
    completion_rate: float
    avg_rating: float
    total_students: int
    response_time_minutes: int
    total_earnings: Decimal
    avg_session_rating: float
    feedback_count: int
```

---

## 2. FRONTEND PAGES NEEDED

### 2.1 Mentor Dashboard (`src/pages/mentor/dashboard.tsx`)

**Components:**
- Earnings card with monthly/yearly toggle
- Quick stats (sessions completed, rating, students)
- Recent sessions table
- Earnings chart
- Upcoming sessions preview
- Top students by session count
- Recent reviews

**Features:**
- Period selector (today, week, month, year, all)
- Export earnings CSV
- Download payout history
- View detailed analytics
- Quick action buttons

### 2.2 Earnings Page (`src/pages/mentor/earnings.tsx`)

**Components:**
- Earnings table (date, type, amount, status)
- Filters (date range, type, status)
- Pagination
- Summary cards (total, pending, completed)
- Earnings chart
- Export button

**Features:**
- Transaction history
- Filter by date range
- Filter by transaction type
- Download as CSV/PDF
- Refund tracking

### 2.3 Payouts Page (`src/pages/mentor/payouts.tsx`)

**Components:**
- Payout history table
- Request payout form
- Payout status tracking
- Bank account management
- Tax information form

**Features:**
- Request payout (button)
- View pending payouts
- View completed payouts
- Payment method selection
- Minimum payout amount check
- Payout frequency display

### 2.4 Profile Management (`src/pages/mentor/profile-edit.tsx`)

**Components:**
- Profile info form (bio, expertise)
- Rate settings
- Availability bulk editor
- Student limits
- Certificate upload
- Social links

**Features:**
- Edit profile information
- Change hourly rate
- Bulk availability upload (CSV)
- Upload certifications
- Preview public profile

### 2.5 Students Page (`src/pages/mentor/students.tsx`)

**Components:**
- Students list with filters
- Student detail modal
- Email student button
- Session history per student
- Rating and feedback

**Features:**
- View all students
- Filter by date joined
- View student history
- Send message
- View feedback given

### 2.6 Reviews Page (`src/pages/mentor/reviews.tsx`)

**Components:**
- Reviews list with ratings
- Filter by rating
- Sort by date
- Student avatar/name
- Review text with context
- Response option

**Features:**
- View all reviews
- Filter by rating (5, 4, 3, 2, 1 stars)
- Sort by date/rating
- Respond to reviews
- Pin favorite reviews

---

## 3. API LAYER

### 3.1 New File: `src/lib/mentorPortalApi.ts`

```typescript
// Mentor Portal API Functions

export interface EarningsRecord {
  id: number;
  date: string;
  type: 'course' | 'session' | 'product';
  description: string;
  amount: number;
  currency: string;
  status: 'completed' | 'pending' | 'refunded';
}

export interface PayoutRequest {
  id: number;
  amount: number;
  payment_method: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  requested_at: string;
  processed_at?: string;
  notes?: string;
}

export interface MentorDashboard {
  earnings_this_month: number;
  total_earnings: number;
  sessions_completed: number;
  avg_rating: number;
  students_count: number;
  pending_sessions: number;
  upcoming_sessions: Array<{
    id: number;
    student_name: string;
    topic: string;
    scheduled_at: string;
    duration_minutes: number;
  }>;
}

export interface MentorPerformance {
  completion_rate: number;
  avg_rating: number;
  response_time_minutes: number;
  student_feedback_summary: string;
}

// Functions
export async function getMentorDashboard(): Promise<MentorDashboard>
export async function getEarnings(period: 'month' | 'year' | 'all'): Promise<EarningsRecord[]>
export async function requestPayout(amount: number, method: string): Promise<PayoutRequest>
export async function getPayouts(): Promise<PayoutRequest[]>
export async function getPerformance(): Promise<MentorPerformance>
export async function updateMentorProfile(data: any): Promise<any>
export async function getMentorSessions(status?: string): Promise<any[]>
export async function updateAvailability(id: number, data: any): Promise<any>
export async function getStudents(): Promise<any[]>
export async function getReviews(): Promise<any[]>
```

---

## 4. STYLING

### 4.1 New File: `src/styles/mentor-dashboard.module.css`

```css
.container { }
.header { }
.statsGrid { }
.statCard { }
.statValue { }
.statLabel { }
.chartContainer { }
.tableContainer { }
.formContainer { }
.buttonGroup { }
/* etc. */
```

---

## 5. BACKEND IMPLEMENTATION CHECKLIST

### Phase 1: Database & Models (1.5 hours)
- [ ] Create MentorEarnings model
- [ ] Create PayoutRequest model
- [ ] Add migrations (or update Base.metadata.create_all)
- [ ] Add relationships to Mentor model
- [ ] Create performance view/computed property

### Phase 2: API Endpoints (2 hours)
- [ ] GET /mentor-portal/dashboard
- [ ] GET /mentor-portal/earnings
- [ ] POST /mentor-portal/request-payout
- [ ] GET /mentor-portal/payouts
- [ ] GET /mentor-portal/performance
- [ ] PUT /mentor-portal/profile
- [ ] GET /mentor-portal/sessions
- [ ] PATCH /mentor-portal/availability/{id}
- [ ] GET /mentor-portal/students
- [ ] GET /mentor-portal/reviews

### Phase 3: Authentication & Authorization (0.5 hours)
- [ ] Add mentor-only middleware
- [ ] Verify mentor status (APPROVED)
- [ ] Add role checks

---

## 6. FRONTEND IMPLEMENTATION CHECKLIST

### Phase 1: API Integration Layer (0.5 hours)
- [ ] Create mentorPortalApi.ts
- [ ] Add all fetch functions
- [ ] Add TypeScript interfaces
- [ ] Add error handling

### Phase 2: Pages (2 hours)
- [ ] Create mentor/dashboard.tsx
- [ ] Create mentor/earnings.tsx
- [ ] Create mentor/payouts.tsx
- [ ] Create mentor/profile-edit.tsx
- [ ] Create mentor/students.tsx
- [ ] Create mentor/reviews.tsx

### Phase 3: Styling (1 hour)
- [ ] Create mentor-dashboard.module.css
- [ ] Create mentor-earnings.module.css
- [ ] Create mentor-payouts.module.css
- [ ] Create mentor-profile.module.css
- [ ] Responsive design
- [ ] Dark mode support

### Phase 4: Integration (1 hour)
- [ ] Add navigation links
- [ ] Wire up all functions
- [ ] Add loading states
- [ ] Add error handling
- [ ] Test all flows

---

## 7. QUICK STATS CARDS TO SHOW

**Dashboard Cards:**
1. Total Earnings (month/year)
2. Pending Earnings
3. Sessions Completed (this month)
4. Average Rating (with count)
5. Active Students
6. Upcoming Sessions
7. Payout Balance Available
8. Next Payout Date

---

## 8. CHARTS TO IMPLEMENT

1. **Earnings Chart** - Line/bar chart of earnings over time
2. **Session Chart** - Sessions completed over time
3. **Rating Chart** - Rating distribution (1-5 stars)
4. **Revenue by Type** - Pie chart (courses vs sessions vs products)

**Library Recommendation:** `recharts` (already available in Next.js)

---

## 9. TABLES TO IMPLEMENT

1. **Recent Sessions** - Date, student, topic, duration, price, status
2. **Earnings History** - Date, type, amount, status, action
3. **Payouts** - Amount, method, status, date, action
4. **Students** - Name, sessions, avg rating, joined date
5. **Reviews** - Rating, text, student, date, response

---

## 10. FORMS TO IMPLEMENT

1. **Request Payout Form**
   - Amount input (must be > minimum)
   - Payment method dropdown
   - Notes textarea
   - Terms checkbox
   - Submit button

2. **Update Profile Form**
   - Bio textarea
   - Expertise tags
   - Hourly rate input
   - Max students input
   - Social links
   - Bio/website URL

3. **Availability Bulk Upload**
   - CSV file upload
   - Template download
   - Validation display
   - Confirm import

---

## 11. VALIDATION RULES

**Payout Request:**
- Minimum amount: $10
- Balance must be available
- Payment method required
- At most 1 pending payout per mentor

**Profile Update:**
- Bio: 20-500 characters
- Hourly rate: $5-$500
- Max students: 1-100
- Expertise: At least 1, max 10

**Availability:**
- Start time < end time
- At most 1 slot per day
- Advance booking minimum

---

## 12. ERROR HANDLING

**Common Errors:**
- Insufficient balance for payout
- Mentor not verified
- Invalid availability slot
- Duplicate payout request
- Rate limit exceeded

---

## 13. TIME BREAKDOWN

| Phase | Task | Hours |
|-------|------|-------|
| 1 | Backend setup & models | 1.5 |
| 2 | API endpoints | 2.0 |
| 3 | Frontend API layer | 0.5 |
| 4 | Create pages & components | 2.0 |
| 5 | Styling & responsive | 1.0 |
| 6 | Integration & testing | 1.0 |
| **Total** | | **8.0** |

*Note: Extra 3 hours available if we skip some features*

---

## 14. FEATURE PRIORITY

**MUST HAVE (Week 1):**
1. Dashboard with stats
2. Earnings tracking
3. Payout requests
4. Session list

**SHOULD HAVE (Week 2):**
5. Profile editing
6. Student list
7. Reviews view
8. Performance metrics

**NICE TO HAVE (Week 3):**
9. Charts & analytics
10. Bulk availability upload
11. Tax forms
12. Email notifications

---

## 15. QUICK START COMMAND

To start development:

```bash
# Backend: Add new models to modelsx/mentor.py
# Then update main.py to import and create tables

# Frontend: Create new pages
# Create new API layer
# Create new styles

# Run tests:
npm run dev  # Frontend
uvicorn app.main:app --reload  # Backend (port 8001)
```

---

## READY TO BUILD?

- ✅ Backend structure: Ready
- ✅ Frontend structure: Ready
- ✅ Database design: Ready
- ✅ API design: Ready
- ✅ UI components: Ready

**Start with Phase 1 (Backend Models & API) - most critical path**
