# IMPLEMENTATION ROADMAP - Next 8 Weeks

**Start Date**: January 1, 2026  
**Sprint Duration**: 2 weeks per sprint  
**Team Size**: 2+ developers  
**Focus**: Core feature completion + polish

---

## SPRINT 1 (Week 1-2): Resume AI + Admin Analytics

### User Stories
**As a user, I want AI-powered bullet point suggestions so I can write better resume content**
**As an admin, I want to see analytics dashboards to understand platform health**

### Backend Tasks

#### Resume AI Content Engine
**File**: `backend/app/services/ai_resume_service.py` (NEW)
**Estimated**: 20 hours

```python
class AIResumeService:
    """AI-powered resume content suggestions using Claude/GPT-4"""
    
    @staticmethod
    def generate_bullet_points(job_title: str, company: str, description: str) -> List[str]:
        """
        Generate 3-5 professional bullet points from job description
        Format: [Action verb] [Task] [Metric/Impact]
        """
        # Call Claude API
        # Return array of bullet points
        pass
    
    @staticmethod
    def improve_summary(current_summary: str) -> str:
        """Rewrite summary with better keywords and impact"""
        pass
    
    @staticmethod
    def extract_metrics(description: str) -> List[str]:
        """Extract quantifiable achievements from text"""
        pass
    
    @staticmethod
    def suggest_keywords(job_description: str) -> List[str]:
        """Extract important keywords from job description"""
        pass
```

**New Endpoints**:
- `POST /resumes/{id}/ai/bullet-points` - Generate bullet points
- `POST /resumes/{id}/ai/improve-summary` - Improve summary
- `POST /resumes/{id}/ai/extract-metrics` - Extract metrics
- `POST /resumes/{id}/ai/suggest-keywords` - Job-specific keywords

**Database Changes**: None (AI calls are stateless)

**Testing**: Unit tests for each AI method + mock API responses

#### Admin Analytics Backend
**File**: `backend/app/services/analytics_service.py` (ENHANCE)
**Estimated**: 15 hours

```python
class AnalyticsService:
    """Platform-wide analytics and metrics"""
    
    @staticmethod
    def get_user_metrics(start_date: date, end_date: date) -> Dict:
        """User acquisition, growth, retention"""
        return {
            "total_users": int,
            "new_users": int,
            "active_users_7d": int,
            "active_users_30d": int,
            "churned_users": int,
            "retention_rate": float,  # 7 day, 30 day, 90 day
            "growth_rate": float
        }
    
    @staticmethod
    def get_revenue_metrics(start_date: date, end_date: date) -> Dict:
        """Revenue by source"""
        return {
            "total_revenue": float,
            "mentor_session_revenue": float,
            "marketplace_revenue": float,
            "subscription_revenue": float,
            "revenue_by_day": List[Dict],  # For charting
            "revenue_by_source": Dict
        }
    
    @staticmethod
    def get_engagement_metrics() -> Dict:
        """User engagement statistics"""
        return {
            "avg_session_duration": float,
            "avg_actions_per_user": int,
            "feature_usage": Dict,  # Which features used most
            "course_completion_rate": float,
            "practice_problem_attempts": int
        }
    
    @staticmethod
    def get_mentor_metrics() -> Dict:
        """Mentor system health"""
        return {
            "total_mentors": int,
            "pending_applications": int,
            "active_mentors": int,
            "avg_rating": float,
            "sessions_this_month": int,
            "mentor_satisfaction": float
        }
```

**New Endpoints**:
- `GET /admin/analytics/users` - User metrics
- `GET /admin/analytics/revenue` - Revenue breakdown
- `GET /admin/analytics/engagement` - Engagement metrics
- `GET /admin/analytics/mentors` - Mentor metrics
- `GET /admin/analytics/timeline` - Time series data for charts

**Database**: Add indexes on `created_at`, `user_id`, `status` for fast analytics queries

### Frontend Tasks

#### Resume AI UI Component
**File**: `src/components/ResumeSuggestions.tsx` (NEW)
**Estimated**: 15 hours

```tsx
interface ResumeSuggestionsProps {
  resumeId: number;
  section: 'work_experience' | 'summary' | 'skills';
  currentContent: string;
}

export function ResumeSuggestions({ resumeId, section, currentContent }: ResumeSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Load suggestions on demand
  // Show "Improve with AI" button
  // Display suggestions in popup/sidebar
  // Allow user to insert, edit, or dismiss
  // Track AI suggestion usage
}
```

**Changes to Resume Editor**:
- Add "Improve with AI" button next to each section
- Show suggestion panel on right side
- Inline suggestion indicators
- Track which suggestions were accepted

#### Admin Analytics Dashboard
**File**: `src/pages/admin/analytics-new.tsx` (NEW)
**Estimated**: 20 hours

```tsx
// Components to build:
- UserGrowthChart (line chart)
- RevenueBreakdown (pie chart)
- EngagementMetrics (cards)
- MentorMetrics (cards + mini chart)
- TimelineSelector (date range picker)
- MetricCard (reusable card)
- ExportButton (export data as CSV)

// Features:
- Real-time metrics refresh (30 sec interval)
- Date range selection (7d, 30d, 90d, custom)
- Metric drill-down (click to see details)
- Export to CSV
- Share dashboard link
```

**Charts Library**: Use `react-chartjs-2` or `recharts`

**WebSocket Integration**: Optional for real-time updates

### Testing
- [ ] Unit tests for AI service (mock API)
- [ ] Analytics query tests
- [ ] Component snapshot tests
- [ ] Integration test: End-to-end AI suggestion flow

### Deployment
- [ ] Set Claude API keys in environment
- [ ] Analytics database indexes created
- [ ] Admin page accessible (role check)
- [ ] Frontend build passes lint

---

## SPRINT 2 (Week 3-4): Job Board + Interview Prep

### User Stories
**As a user, I want to see my job applications in a Kanban board to manage my pipeline visually**
**As a user, I want interview preparation resources to prepare for upcoming interviews**

### Backend Tasks

#### Job Board Data Formatting
**File**: `backend/app/api/v1x/job_applications.py` (ENHANCE)
**Estimated**: 5 hours

Add endpoint to return applications grouped by status:
```python
@router.get("/board")
def get_applications_board(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return applications grouped by status for board view"""
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()
    
    board = {
        "applied": [],
        "screening": [],
        "interviewing": [],
        "offered": [],
        "rejected": [],
        "accepted": []
    }
    
    for app in applications:
        board[app.status.value].append(app)
    
    return board
```

#### Interview Prep Service
**File**: `backend/app/services/interview_service.py` (NEW)
**Estimated**: 20 hours

```python
class InterviewPrepService:
    """Interview preparation resources and tracking"""
    
    @staticmethod
    def get_prep_resources(job_id: int, resume_id: int) -> Dict:
        """Get interview prep resources based on job and resume"""
        return {
            "common_questions": List[str],  # For this role/company
            "technical_topics": List[str],  # Topics to study
            "company_info": Dict,  # About the company
            "interview_tips": List[str],  # General advice
            "mock_interviews": List[Dict]  # Available simulations
        }
    
    @staticmethod
    def create_interview_event(application_id: int, datetime: datetime) -> Dict:
        """Create interview event and set reminders"""
        # Create calendar event
        # Set 1-day before reminder
        # Set 1-hour before reminder
        # Return confirmation
        pass
    
    @staticmethod
    def score_mock_interview(
        interview_id: int,
        answers: List[str],
        video_url: str = None
    ) -> Dict:
        """Score mock interview performance"""
        return {
            "overall_score": float,  # 0-100
            "communication_score": float,
            "technical_score": float,
            "feedback": List[str],  # AI-generated feedback
            "strengths": List[str],
            "improvement_areas": List[str]
        }
```

**New Endpoints**:
- `GET /job-applications/{app_id}/interview-prep` - Get prep resources
- `POST /job-applications/{app_id}/schedule-interview` - Create interview
- `GET /interviews/{id}` - Get interview details
- `POST /interviews/{id}/mock-score` - Score mock interview

### Frontend Tasks

#### Job Board View
**File**: `src/pages/jobs/board.tsx` (NEW)
**Estimated**: 20 hours

```tsx
// Kanban board with columns:
// - Applied (blue)
// - Screening (yellow)
// - Interviewing (purple)
// - Offered (green)
// - Rejected (red)
// - Accepted (emerald)

// Features:
// - Drag-drop cards between columns
// - Card shows: Company, Position, Salary, Date
// - Click card to see full details
// - Add/edit notes on card
// - Color-code by priority
// - Filter by company/location/salary
// - Sort by date/priority
// - Bulk actions (delete, export)

export function JobBoard() {
  const [board, setBoard] = useState<Board>(null);
  const [dragging, setDragging] = useState(null);
  
  const handleDragEnd = async (source, destination, draggableId) => {
    // Update application status on drag-drop
    // Optimistic update
    // Error handling
  };
  
  return (
    <div className="grid grid-cols-6 gap-4">
      {statuses.map(status => (
        <Column
          key={status}
          status={status}
          applications={board[status]}
          onDragEnd={handleDragEnd}
        />
      ))}
    </div>
  );
}
```

**Dependencies**: `react-beautiful-dnd` or `dnd-kit`

#### Interview Prep Panel
**File**: `src/components/InterviewPrep.tsx` (NEW)
**Estimated**: 15 hours

```tsx
// Panel showing:
// - Interview date/time
// - Company background
// - Role requirements
// - Common interview questions
// - Study resources
// - Mock interview options
// - Preparation checklist

// Features:
// - Download prep guide as PDF
// - Watch company videos
// - Practice with mock interviewer (AI)
// - Schedule practice sessions
// - Get personalized tips
```

### Testing
- [ ] Kanban board drag-drop tests
- [ ] Interview scheduling validation
- [ ] Mock interview scoring algorithm

### Deployment
- [ ] Job board page accessible
- [ ] Interview prep page accessible
- [ ] No 404 errors

---

## SPRINT 3 (Week 5-6): Payment Integration

### User Stories
**As a mentor, I want to receive payment for sessions so I can earn income**
**As a user, I want to pay mentors securely for sessions**

### Backend Tasks

#### Stripe Connect Integration
**File**: `backend/app/services/payment_service.py` (NEW)
**Estimated**: 40 hours

```python
class StripeService:
    """Stripe payment processing"""
    
    @staticmethod
    def create_mentor_stripe_account(mentor_id: int, email: str) -> str:
        """Create Stripe Connect account for mentor"""
        # Create connected account
        # Return account link for mentor onboarding
        pass
    
    @staticmethod
    def process_session_payment(
        session_id: int,
        amount: float,
        student_user_id: int,
        mentor_user_id: int
    ) -> Dict:
        """Process payment for completed session"""
        # Charge student's payment method
        # Hold funds in escrow (or transfer to mentor minus platform fee)
        # Create transaction record
        # Send confirmation emails
        pass
    
    @staticmethod
    def release_payment(session_id: int, amount: float, mentor_id: int) -> Dict:
        """Release escrow payment to mentor's account"""
        # Transfer funds to mentor's Stripe account
        # Deduct platform fees
        # Create payout record
        pass
    
    @staticmethod
    def handle_refund(session_id: int, reason: str) -> Dict:
        """Process refund for session"""
        # Refund student
        # Don't pay mentor
        # Log refund reason
        pass
    
    @staticmethod
    def get_mentor_earnings(mentor_id: int, start_date: date, end_date: date) -> Dict:
        """Get mentor earnings summary"""
        return {
            "total_earned": float,
            "platform_fees": float,
            "pending_payout": float,
            "completed_payout": float,
            "transactions": List[Dict]
        }
```

**New Database Tables**:
- `stripe_account` - Mentor Stripe account mapping
- `payment_transaction` - Payment records
- `payout_history` - Payout tracking

**New Endpoints**:
- `POST /mentors/{id}/stripe-onboarding` - Start onboarding
- `POST /payments/session/{id}` - Process session payment
- `GET /mentors/{id}/earnings` - Get earnings
- `POST /payments/{id}/refund` - Refund payment

**Environment Variables**:
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`

#### Payment Models
**File**: `backend/app/modelsx/payment.py` (NEW)

```python
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    mentor_session_id = Column(Integer, ForeignKey("mentor_sessions.id"))
    student_user_id = Column(Integer, ForeignKey("user.id"))
    mentor_user_id = Column(Integer, ForeignKey("user.id"))
    amount = Column(Float)  # In USD
    platform_fee = Column(Float)  # 10-20%
    mentor_payout = Column(Float)  # Amount mentor receives
    status = Column(Enum(PaymentStatus))  # pending, completed, refunded
    stripe_payment_id = Column(String)  # Stripe charge ID
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class StripeAccount(Base):
    __tablename__ = "stripe_accounts"
    
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"))
    stripe_account_id = Column(String, unique=True)
    onboarding_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Frontend Tasks

#### Mentor Onboarding Flow
**File**: `src/pages/mentors/stripe-onboarding.tsx` (NEW)
**Estimated**: 15 hours

```tsx
// 1. Check if mentor already has Stripe account
// 2. If not, show "Connect Stripe" button
// 3. Redirect to Stripe Connect onboarding
// 4. Handle callback and confirmation
// 5. Show success message

export default function StripeOnboarding() {
  const router = useRouter();
  const [status, setStatus] = useState('checking');
  
  useEffect(() => {
    checkStripeStatus();
  }, []);
  
  const handleConnectStripe = async () => {
    const response = await fetch('/api/session/mentors/stripe-onboarding', {
      method: 'POST',
      credentials: 'include'
    });
    const { onboarding_url } = await response.json();
    window.location.href = onboarding_url;
  };
  
  return (
    <div>
      {status === 'checking' && <Spinner />}
      {status === 'needs_setup' && (
        <button onClick={handleConnectStripe}>Connect Stripe Account</button>
      )}
      {status === 'complete' && <p>Payment setup complete!</p>}
    </div>
  );
}
```

#### Student Payment UI
**File**: `src/components/SessionPayment.tsx` (NEW)
**Estimated**: 15 hours

```tsx
// Payment form for session booking
// Shows:
// - Mentor hourly rate
// - Session duration
// - Total cost
// - Payment method (card)
// - Book button

// Uses Stripe.js for PCI compliance
```

### Testing
- [ ] Stripe test API integration
- [ ] Payment flow end-to-end
- [ ] Refund processing
- [ ] Webhook handling

### Deployment
- [ ] Stripe Live keys in production
- [ ] Webhook endpoints configured
- [ ] SSL certificate verified

---

## SPRINT 4 (Week 7-8): Performance + Polish

### User Stories
**As a user, I want the application to load fast for better experience**
**As a user, I want the UI to work well on mobile devices**

### Backend Tasks

#### Database Optimization
**Estimated**: 15 hours

```sql
-- Add indexes on frequently queried columns
CREATE INDEX idx_resume_user_id ON resumes(user_id);
CREATE INDEX idx_mentor_session_user_id ON mentor_sessions(student_user_id);
CREATE INDEX idx_mentor_session_created ON mentor_sessions(created_at);
CREATE INDEX idx_job_app_user_status ON job_applications(user_id, status);
CREATE INDEX idx_user_created ON user(created_at);

-- Query optimization:
-- Use JOINs instead of loading related objects
-- Use pagination
-- Use select() to load only needed columns
-- Enable query caching with Redis
```

**Caching Strategy**:
- Cache user profiles (Redis, 1 hour)
- Cache mentor listings (Redis, 30 min)
- Cache course listings (Redis, 1 hour)
- Cache analytics data (Redis, 5 min)

#### API Performance
**Estimated**: 10 hours

- Add response compression
- Implement request batching
- Optimize image serving
- Add CDN integration (CloudFlare)

### Frontend Tasks

#### Mobile Responsiveness
**Estimated**: 20 hours

- Update Resume Editor for mobile
- Update Job Board for mobile
- Responsive Admin Dashboard
- Mobile navigation/menu
- Touch-friendly buttons
- Mobile-optimized charts

#### Performance Optimization
**Estimated**: 15 hours

```tsx
// Code splitting
// Image optimization (next/image)
// Lazy loading components
// Remove unused dependencies
// Minify/uglify production builds
// Add service worker for offline mode
```

### Testing
- [ ] Lighthouse performance score >80
- [ ] Mobile responsiveness on all pages
- [ ] Load testing with k6
- [ ] Performance monitoring setup

### Deployment
- [ ] Production database PostgreSQL
- [ ] CloudFlare CDN enabled
- [ ] Redis cache configured
- [ ] Sentry error tracking enabled

---

## RESOURCE ALLOCATION

### Team Structure
```
Team Lead / Architect
├── Backend Developer 1 (AI, Payments)
├── Backend Developer 2 (Analytics, Job Board)
├── Frontend Developer 1 (Dashboard, Analytics UI)
└── Frontend Developer 2 (Resume Editor, Job Board)
```

### Time Budget
```
Sprint 1: 85 hours (Resume AI + Analytics)
Sprint 2: 70 hours (Job Board + Interview Prep)
Sprint 3: 70 hours (Payment Integration)
Sprint 4: 60 hours (Performance + Polish)
─────────────────────────────────
Total: 285 hours (~7 weeks with 2-3 developers)
```

### Risk Mitigation
- **Payment Integration**: Partner with Stripe support
- **AI APIs**: Use Claude API with backup (OpenAI)
- **Video Integration**: Plan for Q2 2026 (complex)
- **Database Migration**: Test extensively, plan rollback

---

## SUCCESS METRICS

### User Engagement
- Resume editor daily active users
- Average time in editor
- AI suggestions acceptance rate
- Job board adoption rate

### Performance
- Page load time < 2 seconds
- API response time < 500ms
- 99.9% uptime
- Zero critical errors

### Business
- Mentor session completion rate > 95%
- Payment success rate > 98%
- Refund rate < 2%
- User satisfaction score > 4.5/5

---

## DEPENDENCIES & BLOCKERS

### External
- Stripe API access
- Claude/OpenAI API keys
- AWS account for S3 (future)
- CloudFlare account

### Internal
- Database password reset procedure
- Environment variable management
- Deployment pipeline setup

### Technical Debt
- [ ] Migrate SQLite to PostgreSQL
- [ ] Set up Docker containers
- [ ] Implement CI/CD pipeline
- [ ] Add comprehensive logging

---

## COMMUNICATION PLAN

### Weekly Standup
- **When**: Monday 10 AM, Friday 4 PM
- **Duration**: 15 minutes
- **Format**: What done, what next, blockers

### Sprint Reviews
- **When**: End of each 2-week sprint
- **Duration**: 30 minutes
- **Format**: Demo + metrics + planning next sprint

### Stakeholder Updates
- **When**: Bi-weekly
- **Format**: Executive summary + metrics

---

**Document Version**: 1.0  
**Last Updated**: December 31, 2025  
**Next Review**: January 5, 2026
