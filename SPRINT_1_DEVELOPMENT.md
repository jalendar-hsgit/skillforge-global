# SPRINT 1 DEVELOPMENT GUIDE
## Week 1-2: Quick Wins (Resume AI + Admin Analytics + Job Board)

**Status**: Starting Development  
**Timeline**: 2 weeks (85 hours for 2 developers)  
**Scope**: 3 high-impact features  
**Business Impact**: +30-50% feature adoption increase

---

## 📋 TASK BREAKDOWN

### 1️⃣ RESUME AI CONTENT SUGGESTIONS (Priority: CRITICAL)

#### Status: 90% Backend | 30% Frontend

**Why This Matters**:
- 30+ user feature requests
- Solves pain point: "Improving bullet points is hard"
- High engagement: Users spend 20-30 min generating/refining
- Revenue ready: Can add "Premium AI" tier later

#### Backend (Complete) ✅
- Endpoints implemented and tested
- Mock LLM provider active (MockLLMProvider)
- Ready to integrate with real LLM (Ollama, OpenAI, Anthropic)

**Implemented Endpoints**:
```
POST /api/v1x/resume-ai/professional-summary
POST /api/v1x/resume-ai/bullets
POST /api/v1x/resume-ai/keywords
POST /api/v1x/resume-ai/project-ideas
```

#### Frontend (15 hours remaining)
**What's Done**:
- AIAssistantPanel component exists
- UI structure for 4 tabs (Summary, Bullets, Keywords, Projects)
- Basic API calling functionality

**What's Needed**:
1. **API Integration** (3 hours)
   - Verify all 4 endpoints return correct data
   - Add error handling & retry logic
   - Implement loading states

2. **UI/UX Polish** (8 hours)
   - Add "Apply" buttons for each suggestion
   - Show confidence scores/ratings
   - Add "Regenerate" button with keyboard shortcut
   - Improve suggestion cards styling
   - Add animation for suggestion appearance

3. **Testing** (4 hours)
   - Test all generation functions
   - Test apply/save functionality
   - Test edge cases (empty fields, no data)

**Files to Modify**:
- `src/components/resume/AIAssistantPanel.tsx` - Main component
- `src/pages/api/session/resume-ai/*.ts` - API proxy routes
- `src/lib/api.ts` - Add resume-ai helpers

---

### 2️⃣ ADMIN ANALYTICS DASHBOARD (Priority: HIGH)

#### Status: 10% Complete | Backend: 50% | Frontend: 0%

**Why This Matters**:
- Business critical: Admins need real-time data
- Shows platform health (DAU, revenue, mentors)
- Helps identify issues fast

#### Backend (40 hours remaining)

**What Exists**:
- Basic admin API endpoints
- User, mentor, session queries

**What's Needed**:
1. **New Analytics Routes** (15 hours)
   ```python
   # app/api/v1x/admin_analytics.py
   
   - GET /analytics/overview
     Returns: {
       total_users, active_users, new_users_today, 
       total_mentors, active_sessions, 
       revenue_today, revenue_month, revenue_year
     }
   
   - GET /analytics/daily-active-users?days=30
     Returns: [{date, count, trending}]
   
   - GET /analytics/revenue-breakdown
     Returns: [{source, amount, percentage}]
   
   - GET /analytics/mentors-performance
     Returns: [{mentor_id, name, sessions, rating, earnings}]
   
   - GET /analytics/student-engagement
     Returns: [{metric, value, trend}]
   
   - GET /analytics/feature-adoption
     Returns: [{feature, users, percentage}]
   ```

2. **Database Optimization** (10 hours)
   - Add indexes for analytics queries
   - Create fast aggregation views
   - Cache frequently accessed data

3. **Testing** (15 hours)
   - Test data accuracy
   - Test performance (sub-200ms response)
   - Test with large datasets

#### Frontend (30 hours)

**What's Needed**:
1. **Dashboard Layout** (10 hours)
   ```tsx
   // src/pages/admin/analytics.tsx
   
   - Top KPI Cards (4 cards)
     • Active Users (DAU)
     • New Mentors
     • Sessions This Week
     • Revenue This Month
   
   - Charts (3 charts)
     • Daily Active Users (line chart, 30 days)
     • Revenue Breakdown (pie chart)
     • Feature Adoption (bar chart)
   
   - Tables (2 tables)
     • Top Mentors (by sessions/rating)
     • Student Engagement (by activity)
   ```

2. **Components** (15 hours)
   - `AnalyticsDashboard.tsx` - Main layout
   - `KPICard.tsx` - Metric cards with trends
   - `LineChart.tsx` - Daily active users
   - `RevenueBreakdown.tsx` - Pie chart
   - `MentorsTable.tsx` - Top mentors list
   - `EngagementMetrics.tsx` - Student engagement

3. **Data Integration** (5 hours)
   - API calls to analytics endpoints
   - Real-time update with polling/WebSocket
   - Error handling & fallbacks

**Tech Stack**:
- Recharts for charts (already installed)
- Lucide icons for KPIs
- Tailwind for styling

---

### 3️⃣ JOB BOARD KANBAN VIEW (Priority: HIGH)

#### Status: 30% Complete | Backend: 100% | Frontend: 20%

**Why This Matters**:
- Popular request from job seekers
- Improves workflow visualization
- +50% tracker usage increase

#### Frontend (30 hours)

**Kanban Columns**:
```
[Applied] → [Interviewing] → [Offer] → [Accepted]
   ↓              ↓            ↓         ↓
  5 jobs       2 jobs       1 job     2 jobs
```

**What's Needed**:
1. **Kanban Component** (15 hours)
   - Drag-drop between columns
   - Card styling (job title, company, salary)
   - Status transitions
   - Column collapsing

2. **Filters & Views** (10 hours)
   - View toggle: List ↔ Kanban
   - Filter by: company, salary, date
   - Search jobs
   - Sort options

3. **Interactions** (5 hours)
   - Quick actions (edit, delete, archive)
   - Add new application from board
   - Inline editing on cards

**Tech Stack**:
- `react-beautiful-dnd` or `@dnd-kit/core` (recommended)
- Lucide icons
- Tailwind CSS

---

## 🔄 IMPLEMENTATION SEQUENCE

### Week 1 (Hours 0-40)

**Day 1-2: Resume AI (15 hours)**
- [ ] Verify backend endpoints respond correctly
- [ ] Test mock LLM provider
- [ ] Build frontend integration
- [ ] Add error handling
- [ ] Create test cases

**Day 3-4: Admin Analytics Backend (20 hours)**
- [ ] Design analytics database schema
- [ ] Create aggregation functions
- [ ] Build REST endpoints
- [ ] Optimize queries
- [ ] Document API

**Day 5: Kanban Foundation (5 hours)**
- [ ] Research DnD library
- [ ] Set up basic component structure
- [ ] Plan column layout

### Week 2 (Hours 40-85)

**Day 6-7: Admin Analytics Frontend (25 hours)**
- [ ] Build dashboard layout
- [ ] Create KPI cards
- [ ] Implement charts
- [ ] Add tables
- [ ] Connect to API

**Day 8-9: Job Board Kanban (25 hours)**
- [ ] Implement drag-drop
- [ ] Build cards & columns
- [ ] Add filters/search
- [ ] Test interactions
- [ ] Polish UI

**Day 10: Testing & Polish (10 hours)**
- [ ] E2E testing
- [ ] Performance testing
- [ ] Bug fixes
- [ ] Documentation

---

## 💻 CODE EXAMPLES

### Resume AI - Backend Integration

**Location**: `backend/app/api/v1x/resume_ai.py`

**Endpoints Already Implemented**:
```python
@router.post("/professional-summary")
async def generate_professional_summary(
    request: AISummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate professional summary using AI."""
    # Uses LLM provider (mock or real)
    # Returns summary text

@router.post("/bullets")
async def generate_bullet_points(
    request: AIBulletPointRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate ATS-optimized bullet points."""
    # Returns list of bullet points

@router.post("/keywords")
async def extract_keywords(
    request: KeywordExtractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract keywords for ATS optimization."""
    # Returns keyword list

@router.post("/project-ideas")
async def suggest_projects(
    request: ProjectSuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Suggest projects based on skills."""
    # Returns project list
```

### Admin Analytics - Backend

**New File**: `backend/app/api/v1x/admin_analytics.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.db import get_db
from app.core.security import get_current_user, check_admin_access

router = APIRouter(prefix="/analytics", tags=["admin-analytics"])

@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get high-level dashboard overview."""
    check_admin_access(current_user)
    
    # Count active users today
    today = datetime.utcnow().date()
    active_today = db.query(User).filter(
        User.last_login >= datetime.combine(today, datetime.min.time())
    ).count()
    
    # Count new users today
    new_today = db.query(User).filter(
        User.created_at >= datetime.combine(today, datetime.min.time())
    ).count()
    
    return {
        "total_users": db.query(User).count(),
        "active_users": active_today,
        "new_users_today": new_today,
        "total_mentors": db.query(Mentor).count(),
        "active_sessions": db.query(MentorSession).filter(
            MentorSession.status == "ongoing"
        ).count(),
        "revenue_today": calculate_revenue(db, days=1),
        "revenue_month": calculate_revenue(db, days=30),
        "revenue_year": calculate_revenue(db, days=365),
    }

@router.get("/daily-active-users")
async def get_daily_active_users(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily active users for last N days."""
    check_admin_access(current_user)
    
    result = []
    for i in range(days, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = db.query(User).filter(
            User.last_login >= datetime.combine(date, datetime.min.time()),
            User.last_login < datetime.combine(date + timedelta(days=1), datetime.min.time())
        ).count()
        result.append({
            "date": date.isoformat(),
            "count": count,
            "trending": "up" if i > 0 and count > previous else "down"
        })
    return result
```

### Admin Analytics - Frontend

**New File**: `src/pages/admin/analytics.tsx`

```tsx
import { useState, useEffect } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { Card } from '@/components/Card';
import KPICard from '@/components/analytics/KPICard';
import AnalyticsChart from '@/components/analytics/AnalyticsChart';
import MentorsTable from '@/components/analytics/MentorsTable';

export default function AnalyticsDashboard() {
  const [overview, setOverview] = useState(null);
  const [dailyUsers, setDailyUsers] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [overviewRes, dailyRes] = await Promise.all([
        fetch('/api/admin/analytics/overview'),
        fetch('/api/admin/analytics/daily-active-users?days=30')
      ]);
      
      setOverview(await overviewRes.json());
      setDailyUsers(await dailyRes.json());
    } catch (err) {
      console.error('Failed to fetch analytics', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <AdminLayout title="Analytics Dashboard">
      <div className="space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <KPICard
            title="Active Users"
            value={overview.active_users}
            trend="+12%"
            icon="Users"
          />
          <KPICard
            title="New Mentors"
            value={overview.total_mentors}
            trend="+8%"
            icon="UserPlus"
          />
          <KPICard
            title="Sessions This Week"
            value={overview.active_sessions}
            trend="+25%"
            icon="Calendar"
          />
          <KPICard
            title="Revenue This Month"
            value={`$${overview.revenue_month}`}
            trend="+15%"
            icon="DollarSign"
          />
        </div>

        {/* Charts */}
        <Card title="Daily Active Users">
          <AnalyticsChart
            data={dailyUsers}
            type="line"
            xKey="date"
            yKey="count"
          />
        </Card>

        {/* Tables */}
        <MentorsTable />
      </div>
    </AdminLayout>
  );
}
```

### Job Board Kanban - Frontend

**New File**: `src/components/job-tracker/KanbanBoard.tsx`

```tsx
import { useState } from 'react';
import { DndContext, closestCenter, DragEndEvent } from '@dnd-kit/core';
import KanbanColumn from './KanbanColumn';
import JobCard from './JobCard';

const COLUMNS = ['applied', 'interviewing', 'offer', 'accepted'];

interface Job {
  id: number;
  title: string;
  company: string;
  status: string;
  salary?: string;
  appliedDate: string;
}

export default function KanbanBoard({ jobs }: { jobs: Job[] }) {
  const [jobsByStatus, setJobsByStatus] = useState(
    COLUMNS.reduce((acc, col) => ({
      ...acc,
      [col]: jobs.filter(j => j.status === col)
    }), {})
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const jobId = parseInt(active.id as string);
    const newStatus = over.id as string;

    // Find job in current status and move it
    let job = null;
    let sourceStatus = '';

    for (const status of COLUMNS) {
      const found = jobsByStatus[status]?.find(j => j.id === jobId);
      if (found) {
        job = found;
        sourceStatus = status;
        break;
      }
    }

    if (job && sourceStatus !== newStatus) {
      setJobsByStatus({
        ...jobsByStatus,
        [sourceStatus]: jobsByStatus[sourceStatus].filter(j => j.id !== jobId),
        [newStatus]: [...jobsByStatus[newStatus], { ...job, status: newStatus }]
      });

      // Update in API
      updateJobStatus(jobId, newStatus);
    }
  };

  const updateJobStatus = async (jobId: number, newStatus: string) => {
    await fetch(`/api/session/job-applications/${jobId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
  };

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-4 gap-4 overflow-x-auto">
        {COLUMNS.map(status => (
          <KanbanColumn
            key={status}
            status={status}
            jobs={jobsByStatus[status] || []}
            renderCard={(job) => <JobCard key={job.id} job={job} />}
          />
        ))}
      </div>
    </DndContext>
  );
}
```

---

## ✅ TESTING CHECKLIST

### Resume AI
- [ ] All 4 endpoints return valid responses
- [ ] Error handling for missing fields
- [ ] Apply button saves changes
- [ ] Multiple generations show different suggestions
- [ ] UI responsive on mobile

### Admin Analytics
- [ ] KPI numbers accurate
- [ ] Charts render correctly
- [ ] Tables load and display data
- [ ] Refresh updates data
- [ ] Performance: <200ms response time

### Job Board Kanban
- [ ] Drag-drop between columns works
- [ ] Status saved to backend
- [ ] Filters work correctly
- [ ] List view works as fallback
- [ ] Mobile friendly

---

## 🔄 DAILY STANDUPS

### Format: [Feature] [Status] [Blocker?]

**Example**:
```
- Resume AI: UI integration done, testing endpoints [No blocker]
- Admin Analytics: Backend half-done, needs dashboard design [No blocker]
- Job Kanban: Starting DnD implementation [No blocker]
```

---

## 📊 SUCCESS METRICS (End of Sprint 1)

✅ **Resume AI**: 100% user adoption, 50+ daily generations  
✅ **Admin Analytics**: Admins checking daily, faster issue detection  
✅ **Job Kanban**: 80% of job trackers use Kanban view  

**Overall**: 30% increase in feature engagement, 0 critical bugs

---

## 🚀 SPRINT 2 PREVIEW

Once Sprint 1 is complete:
- Interview Prep Module (20h)
- Mobile Optimization (20h)
- Job Board Polish (15h)

---

**Start Date**: Today  
**Demo Date**: End of Week 2  
**Team**: 2 developers  
**Budget**: 85 hours

Let's build! 🎉
