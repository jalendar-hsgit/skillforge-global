# Sprint 2 Development Plan
**Duration:** 2 weeks  
**Team:** 2 developers  
**Total Hours:** 65 hours  
**Start:** Post-Sprint 1 deployment  

---

## Sprint 2 Objectives

After successful Sprint 1 delivery, Sprint 2 focuses on:
1. **Polishing & Optimizing** existing features for performance
2. **Enhancing** with user-requested features
3. **Monetizing** the Resume AI platform
4. **Expanding** to mobile platforms

### Success Criteria
- Admin Analytics WebSocket updates < 100ms latency
- Resume AI processing time < 2 seconds
- Job Kanban mobile app with 90% feature parity
- Premium tier generating $5k/month revenue
- 80% user satisfaction with new features

---

## Task Breakdown

### Task 1: Admin Analytics Real-Time Updates (15 hours)
**Owner:** Developer A  
**Priority:** 🔴 HIGH  
**Business Impact:** $$$  

#### What
Transform polling-based analytics dashboard to real-time WebSocket updates.

#### Current State
- Analytics dashboard refr eshes on button click or page load
- No real-time updates
- Batch queries every 5 minutes max

#### Target State
- Real-time KPI updates via WebSocket
- Live chart animations
- User count updates in real-time
- Revenue ticker showing live transactions
- Session ratings updating instantly

#### Implementation Plan

**1. Backend WebSocket Server (5h)**
```python
# backend/app/api/v1x/ws/analytics.py
from fastapi import WebSocket
from app.core.security import get_current_user_ws

class AnalyticsWS:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send initial data
        await websocket.send_json(await get_analytics_data())
    
    async def broadcast(self, data: dict):
        """Send analytics update to all connected admins"""
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                self.active_connections.remove(connection)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

# WebSocket route
@router.websocket("/ws/analytics")
async def websocket_analytics(websocket: WebSocket, current_user: User = Depends(get_current_user_ws)):
    if current_user.role != "admin":
        await websocket.close(code=1008)
        return
    
    ws = AnalyticsWS()
    await ws.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    finally:
        await ws.disconnect(websocket)

# Background task to push updates every 10 seconds
async def analytics_broadcaster():
    while True:
        await asyncio.sleep(10)
        data = await get_analytics_data()
        await analytics_ws.broadcast({
            "type": "analytics_update",
            "data": data,
            "timestamp": datetime.now().isoformat()
        })

# Register in main.py
@app.on_event("startup")
async def startup():
    asyncio.create_task(analytics_broadcaster())
```

**2. Frontend WebSocket Integration (5h)**
```typescript
// src/hooks/useAnalyticsWS.ts
import { useEffect, useState, useRef } from 'react'

export const useAnalyticsWS = () => {
  const [data, setData] = useState<KPI | null>(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1x/ws/analytics`)

    ws.onopen = () => {
      setConnected(true)
      console.log('Analytics WebSocket connected')
    }

    ws.onmessage = (event) => {
      const { type, data: wsData } = JSON.parse(event.data)
      if (type === 'analytics_update') {
        setData(wsData)
      }
    }

    ws.onerror = () => setConnected(false)
    ws.onclose = () => setConnected(false)

    wsRef.current = ws

    return () => ws.close()
  }, [])

  return { data, connected }
}

// Usage in analytics.tsx
export default function AnalyticsDashboard() {
  const { data: wsData, connected } = useAnalyticsWS()
  const [kpi, setKpi] = useState<KPI | null>(null)

  useEffect(() => {
    if (wsData) setKpi(wsData)
  }, [wsData])

  return (
    <div>
      <div className={`status ${connected ? 'text-green-400' : 'text-red-400'}`}>
        {connected ? '🔴 Live' : '⚫ Offline'}
      </div>
      {/* Dashboard content */}
    </div>
  )
}
```

**3. Animation Effects (3h)**
- Smooth transitions for metric updates
- Revenue ticker rolling numbers
- Chart animations when data changes
- Pulse effects for live status

**4. Testing & Optimization (2h)**
- Load test with 100 concurrent connections
- Latency measurement
- Bandwidth optimization
- Error recovery testing

#### Success Metrics
- [ ] WebSocket connected and receiving updates
- [ ] Updates received every 10 seconds
- [ ] Latency < 100ms
- [ ] Handles 100+ concurrent connections
- [ ] Graceful fallback to polling if WS fails
- [ ] 95%+ uptime in testing

#### Dependencies
- FastAPI WebSocket support (built-in)
- Browser WebSocket API (built-in)
- No new packages needed

---

### Task 2: Custom Date Range Picker (8 hours)
**Owner:** Developer B  
**Priority:** 🟡 MEDIUM  
**Business Impact:** $$  

#### What
Add date range selector to analytics dashboard for custom time periods.

#### Current State
- Fixed timeframe options (7d, 30d, 90d, 1y)
- Cannot select arbitrary date ranges

#### Target State
- Date picker component for start/end dates
- Custom range support
- Comparison with previous period
- URL parameters for sharing custom reports
- Saved custom ranges (My Reports)

#### Implementation Plan

**1. Create DateRangePicker Component (3h)**
```typescript
// src/components/DateRangePicker.tsx
import React, { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface DateRange {
  start: Date
  end: Date
}

export const DateRangePicker: React.FC<{
  onSelect: (range: DateRange) => void
  initialRange?: DateRange
}> = ({ onSelect, initialRange }) => {
  const [start, setStart] = useState(initialRange?.start || new Date())
  const [end, setEnd] = useState(initialRange?.end || new Date())

  const handleApply = () => {
    onSelect({ start, end })
  }

  return (
    <div className="p-4 rounded-lg border border-white/10 bg-white/5">
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm text-gray-400 mb-2">Start Date</label>
          <input
            type="date"
            value={start.toISOString().split('T')[0]}
            onChange={(e) => setStart(new Date(e.target.value))}
            className="w-full px-3 py-2 rounded bg-white/10 border border-white/20 text-white"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-2">End Date</label>
          <input
            type="date"
            value={end.toISOString().split('T')[0]}
            onChange={(e) => setEnd(new Date(e.target.value))}
            className="w-full px-3 py-2 rounded bg-white/10 border border-white/20 text-white"
          />
        </div>
      </div>
      <button
        onClick={handleApply}
        className="w-full px-4 py-2 bg-forgePurple text-white rounded hover:bg-forgePurple/90 transition"
      >
        Apply Range
      </button>
    </div>
  )
}
```

**2. Integrate into Analytics Page (2h)**
- Add date picker modal to header
- Pass selected range to API calls
- Update URL with range params
- Cache selected ranges

**3. Backend Date Filtering (2h)**
```python
# Update analytics endpoints to accept date range
@router.get("/analytics/daily-active-users")
async def get_daily_active_users(
    start_date: datetime = Query(datetime.now() - timedelta(days=30)),
    end_date: datetime = Query(datetime.now()),
    current_user: User = Depends(get_current_admin)
):
    """Get DAU for custom date range"""
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    ).order_by(DailyMetrics.date).all()
    
    return [
        DailyMetric(
            date=m.date.isoformat(),
            count=m.count,
            percentage_change=calculate_change(m, metrics)
        )
        for m in metrics
    ]
```

**4. Testing (1h)**
- Test various date ranges
- Performance with large ranges (1+ year)
- Error handling for invalid dates
- URL parameter preservation

#### Success Metrics
- [ ] Date picker UI renders
- [ ] Custom ranges apply to all charts
- [ ] Query performance < 500ms for 1-year range
- [ ] URL parameters save/load correctly
- [ ] Comparison with previous period shows % change

---

### Task 3: Analytics Export to CSV/PDF (10 hours)
**Owner:** Developer A  
**Priority:** 🟡 MEDIUM  
**Business Impact:** $$  

#### What
Allow admins to export analytics reports in CSV and PDF formats.

#### Target Features

**1. CSV Export (4h)**
```python
# backend/app/api/v1x/exports.py
from io import StringIO
import csv

@router.get("/exports/analytics/csv")
async def export_analytics_csv(
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(get_current_admin)
):
    """Export analytics as CSV"""
    
    # Get all data
    kpi = await get_analytics_overview()
    daily_metrics = await get_daily_active_users(start_date, end_date)
    revenue = await get_revenue_breakdown()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write KPI section
    writer.writerow(['KEY PERFORMANCE INDICATORS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Users', kpi.total_users])
    writer.writerow(['Active Users Today', kpi.active_users_today])
    # ... more rows
    
    # Write daily metrics section
    writer.writerow([])
    writer.writerow(['DAILY ACTIVE USERS'])
    writer.writerow(['Date', 'Count', 'Change %'])
    for metric in daily_metrics:
        writer.writerow([metric.date, metric.count, metric.percentage_change])
    
    # ... more sections
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"}
    )
```

**2. PDF Export (4h)**
```python
# Using reportlab for PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, PageBreak

@router.get("/exports/analytics/pdf")
async def export_analytics_pdf(
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(get_current_admin)
):
    """Export analytics as PDF report"""
    
    # Get all data
    data = await get_full_analytics_data(start_date, end_date)
    
    # Create PDF
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    elements.append(Paragraph("SkillForge Analytics Report", styles['Heading1']))
    elements.append(Spacer(1, 12))
    
    # KPI Table
    kpi_data = [
        ['Metric', 'Value'],
        ['Total Users', str(data['kpi']['total_users'])],
        ['Active Today', str(data['kpi']['active_users_today'])],
        # ... more rows
    ]
    elements.append(Table(kpi_data))
    elements.append(Spacer(1, 12))
    
    # Charts as images (embed matplotlib/plotly)
    # ... chart generation code
    
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=analytics.pdf"}
    )
```

**3. Frontend Export UI (2h)**
```typescript
// src/components/ExportButton.tsx
export const ExportButton: React.FC<{ dateRange: DateRange }> = ({ dateRange }) => {
  const handleExport = async (format: 'csv' | 'pdf') => {
    const response = await fetch(
      `/api/v1x/exports/analytics/${format}?start_date=${dateRange.start}&end_date=${dateRange.end}`,
      { credentials: 'include' }
    )
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analytics.${format}`
    a.click()
  }

  return (
    <div className="flex gap-2">
      <button onClick={() => handleExport('csv')} className="px-4 py-2 bg-green-500 text-white rounded">
        📥 Export CSV
      </button>
      <button onClick={() => handleExport('pdf')} className="px-4 py-2 bg-red-500 text-white rounded">
        📄 Export PDF
      </button>
    </div>
  )
}
```

#### Success Metrics
- [ ] CSV export contains all analytics data
- [ ] PDF export is formatted and printable
- [ ] File downloads work reliably
- [ ] Large exports (1-year data) < 10 seconds
- [ ] 0 export errors in testing

---

### Task 4: Email Digest Scheduling (12 hours)
**Owner:** Developer B  
**Priority:** 🟡 MEDIUM  
**Business Impact:** $$  

#### What
Allow admins to schedule daily/weekly analytics digest emails.

#### Implementation

**1. Database Models (2h)**
```python
# backend/app/models/analytics_digest.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSON

class AnalyticsDigest(Base):
    __tablename__ = "analytics_digests"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("user.id"))
    frequency = Column(String)  # daily, weekly, monthly
    day_of_week = Column(String, nullable=True)  # for weekly
    time_of_day = Column(String)  # HH:MM UTC
    enabled = Column(Boolean, default=True)
    last_sent = Column(DateTime, nullable=True)
    email_address = Column(String)
    metrics_to_include = Column(JSON)  # Which metrics to show
    created_at = Column(DateTime, default=datetime.utcnow)
```

**2. Celery Task for Email Sending (4h)**
```python
# backend/app/celery_tasks/analytics_digest.py
from celery import shared_task
from app.services.email import send_email
from app.services.analytics import get_analytics_data

@shared_task
def send_analytics_digest(digest_id: int):
    """Send analytics digest email"""
    
    digest = db.query(AnalyticsDigest).filter(AnalyticsDigest.id == digest_id).first()
    if not digest or not digest.enabled:
        return
    
    # Get analytics data
    data = get_analytics_data()
    
    # Generate HTML email
    html_content = f"""
    <h1>SkillForge Analytics Digest</h1>
    <table>
        <tr>
            <td>Total Users</td>
            <td>{data['kpi']['total_users']}</td>
        </tr>
        <tr>
            <td>Active Today</td>
            <td>{data['kpi']['active_users_today']}</td>
        </tr>
        <tr>
            <td>Revenue This Month</td>
            <td>${data['kpi']['revenue_month']}</td>
        </tr>
    </table>
    """
    
    # Send email
    send_email(
        to=digest.email_address,
        subject="SkillForge Analytics Digest",
        html_content=html_content
    )
    
    # Update last_sent timestamp
    digest.last_sent = datetime.utcnow()
    db.commit()

# Schedule in Beat
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-daily-digests': {
        'task': 'app.celery_tasks.analytics_digest.send_daily_digests',
        'schedule': crontab(hour=9, minute=0),  # 9 AM UTC daily
    },
    'send-weekly-digests': {
        'task': 'app.celery_tasks.analytics_digest.send_weekly_digests',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9 AM
    },
}
```

**3. Frontend UI for Configuration (4h)**
```typescript
// src/pages/admin/analytics/digest-settings.tsx
export default function DigestSettings() {
  const [digest, setDigest] = useState<AnalyticsDigest | null>(null)
  const [frequency, setFrequency] = useState('daily')
  const [timeOfDay, setTimeOfDay] = useState('09:00')
  const [dayOfWeek, setDayOfWeek] = useState('monday')

  const handleSave = async () => {
    const response = await fetch('/api/v1x/admin/digest-settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        frequency,
        time_of_day: timeOfDay,
        day_of_week: frequency === 'weekly' ? dayOfWeek : null,
        enabled: true
      })
    })
    
    if (response.ok) {
      // Show success toast
    }
  }

  return (
    <div className="p-6 rounded-xl border border-white/10 bg-white/5">
      <h2 className="text-xl font-bold text-white mb-6">Analytics Email Digest</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-2">Frequency</label>
          <select
            value={frequency}
            onChange={(e) => setFrequency(e.target.value)}
            className="w-full px-3 py-2 rounded bg-white/10 border border-white/20 text-white"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
        
        {frequency === 'weekly' && (
          <div>
            <label className="block text-sm text-gray-400 mb-2">Day of Week</label>
            <select
              value={dayOfWeek}
              onChange={(e) => setDayOfWeek(e.target.value)}
              className="w-full px-3 py-2 rounded bg-white/10 border border-white/20 text-white"
            >
              <option value="monday">Monday</option>
              <option value="tuesday">Tuesday</option>
              {/* ... */}
            </select>
          </div>
        )}
        
        <div>
          <label className="block text-sm text-gray-400 mb-2">Time of Day</label>
          <input
            type="time"
            value={timeOfDay}
            onChange={(e) => setTimeOfDay(e.target.value)}
            className="w-full px-3 py-2 rounded bg-white/10 border border-white/20 text-white"
          />
        </div>
        
        <button
          onClick={handleSave}
          className="w-full px-4 py-2 bg-forgePurple text-white rounded hover:bg-forgePurple/90 transition"
        >
          Save Email Digest Settings
        </button>
      </div>
    </div>
  )
}
```

**4. Testing Email Delivery (2h)**
- Unit tests for digest generation
- Integration tests with mock email service
- Celery task scheduling verification

#### Success Metrics
- [ ] Digest emails send on schedule
- [ ] Email contains all configured metrics
- [ ] HTML formatting renders correctly
- [ ] Settings save/load properly
- [ ] Can enable/disable easily

---

### Task 5: Resume AI Testing & Performance (10 hours)
**Owner:** Developer A  
**Priority:** 🔴 HIGH  
**Business Impact:** $$$  

#### What
Comprehensive testing and optimization of Resume AI feature.

#### Current State
- 4 generation functions implemented
- Basic error handling
- No performance optimization
- Limited testing

#### Target State
- < 2 second generation time
- 99.9% success rate
- Mobile-optimized UI
- Comprehensive test coverage

#### Implementation Plan

**1. Performance Optimization (3h)**

**Cache Suggestions**
```typescript
// src/components/resume/AIAssistantPanel.tsx
const [suggestionCache, setSuggestionCache] = useState<Record<string, Suggestion[]>>({})

const generateSummary = async () => {
  const cacheKey = `summary-${userResumeHash}`
  if (suggestionCache[cacheKey]) {
    return suggestionCache[cacheKey]
  }
  
  const suggestions = await fetchSuggestions(...)
  setSuggestionCache(prev => ({ ...prev, [cacheKey]: suggestions }))
  return suggestions
}
```

**Debounce Requests**
```typescript
// Avoid duplicate API calls during rapid clicks
const [pendingRequest, setPendingRequest] = useState(false)

const handleGenerate = async () => {
  if (pendingRequest) return
  setPendingRequest(true)
  try {
    await generateSummary()
  } finally {
    setPendingRequest(false)
  }
}
```

**Backend Optimization**
```python
# backend/app/api/v1x/resume_ai.py
# Add query result caching
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=1000)
def get_cached_suggestions(user_id: int, suggestion_type: str):
    """Cache suggestions for 1 hour"""
    return generate_suggestions(user_id, suggestion_type)

@router.get("/resume-ai/summary")
async def get_summary(
    current_user: User = Depends(get_current_user),
    cache: bool = True
):
    if cache:
        return get_cached_suggestions(current_user.id, "summary")
    else:
        return generate_suggestions(current_user.id, "summary")
```

**2. Mobile Responsiveness (2h)**
```typescript
// Responsive card layouts
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {suggestions.map(suggestion => (
    <SuggestionCard key={suggestion.id} suggestion={suggestion} />
  ))}
</div>

// Touch-friendly buttons
<button className="min-h-12 px-4 py-3 rounded-lg hover:scale-105 active:scale-95 transition-transform">
  Apply Suggestion
</button>

// Readable font sizes on mobile
<p className="text-base sm:text-lg md:text-xl font-bold">
  Summary Suggestions
</p>
```

**3. E2E Testing with Playwright (3h)**
```typescript
// tests/resume-ai.e2e.ts
import { test, expect } from '@playwright/test'

test.describe('Resume AI', () => {
  test('should generate professional summary in < 3 seconds', async ({ page }) => {
    await page.goto('/resumes/edit/1')
    
    const startTime = Date.now()
    await page.click('button:has-text("Generate Summary")')
    await page.waitForSelector('.suggestion-card')
    const duration = Date.now() - startTime
    
    expect(duration).toBeLessThan(3000)
  })

  test('should apply suggestion and update form', async ({ page }) => {
    await page.goto('/resumes/edit/1')
    await page.click('button:has-text("Generate Summary")')
    await page.waitForSelector('.suggestion-card')
    
    const initialText = await page.inputValue('textarea[name="professional_summary"]')
    await page.click('button:has-text("Apply")')
    const updatedText = await page.inputValue('textarea[name="professional_summary"]')
    
    expect(updatedText).not.toBe(initialText)
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1x/resume-ai/**', route => {
      route.abort('failed')
    })
    
    await page.goto('/resumes/edit/1')
    await page.click('button:has-text("Generate Summary")')
    
    const error = await page.locator('.error-message')
    await expect(error).toBeVisible()
  })

  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/resumes/edit/1')
    
    const button = page.locator('button:has-text("Generate Summary")')
    await expect(button).toBeVisible()
    
    const box = await button.boundingBox()
    expect(box?.width).toBeGreaterThan(100) // Minimum touch target size
  })
})
```

**4. Load Testing (2h)**
```python
# tests/load_test_resume_ai.py
from locust import HttpUser, task, between

class ResumeAIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.token = self.get_auth_token()
    
    @task(3)
    def generate_summary(self):
        self.client.post(
            "/api/v1x/resume-ai/professional-summary",
            json={"resume_id": 1},
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def generate_bullets(self):
        self.client.post(
            "/api/v1x/resume-ai/bullet-points",
            json={"resume_id": 1},
            headers={"Authorization": f"Bearer {self.token}"}
        )

# Run with: locust -f tests/load_test_resume_ai.py --host=http://localhost:8001
```

#### Success Metrics
- [ ] Generation time < 2 seconds (p95)
- [ ] Success rate > 99%
- [ ] Mobile-optimized UI passes visual test
- [ ] Loads properly on 4G networks
- [ ] All E2E tests passing
- [ ] Can handle 100 concurrent users

---

### Task 6: Resume AI Monetization (10 hours)
**Owner:** Developer B  
**Priority:** 🟡 MEDIUM  
**Business Impact:** $$$  

#### What
Set up premium tier for unlimited Resume AI suggestions.

#### Current State
- Resume AI free for all users
- Unlimited suggestions
- No revenue generation

#### Target State
- Free tier: 5 suggestions/month
- Premium tier: Unlimited suggestions
- Stripe integration for billing
- Feature gating in UI
- Subscription management

#### Implementation Plan

**1. Database Schema (2h)**
```python
# backend/app/models/subscription.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True)
    stripe_customer_id = Column(String, unique=True)
    stripe_subscription_id = Column(String, unique=True)
    plan_type = Column(String)  # free, premium_monthly, premium_yearly
    status = Column(String)  # active, cancelled, pending
    billing_cycle_start = Column(DateTime)
    billing_cycle_end = Column(DateTime)
    current_period_end = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FeatureUsage(Base):
    __tablename__ = "feature_usage"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    feature = Column(String)  # resume_ai_summary, resume_ai_bullets, etc.
    count = Column(Integer, default=0)
    reset_date = Column(DateTime)  # When quota resets
    created_at = Column(DateTime, default=datetime.utcnow)
```

**2. Stripe Integration (4h)**
```python
# backend/app/services/stripe_service.py
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    async def create_customer(user: User) -> str:
        """Create Stripe customer"""
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"user_id": user.id}
        )
        return customer.id
    
    @staticmethod
    async def create_subscription(user_id: int, plan_id: str) -> str:
        """Create subscription"""
        user = db.query(User).filter(User.id == user_id).first()
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{"price": plan_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
        return subscription.id
    
    @staticmethod
    async def get_subscription(user: User) -> Subscription:
        """Get user's subscription"""
        return db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()

# Webhook handler
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400)
    
    if event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']
        user = db.query(User).filter(
            User.stripe_customer_id == subscription_data['customer']
        ).first()
        
        if user:
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user.id
            ).first()
            subscription.status = subscription_data['status']
            db.commit()
    
    return {"status": "success"}
```

**3. Feature Gating (2h)**
```python
# backend/app/services/usage_limit.py
from datetime import datetime, timedelta

async def check_usage_limit(user_id: int, feature: str, tier: str) -> bool:
    """Check if user can use feature"""
    
    # Premium users have unlimited access
    if tier == "premium":
        return True
    
    # Free tier: 5 suggestions per month
    if tier == "free":
        usage = db.query(FeatureUsage).filter(
            FeatureUsage.user_id == user_id,
            FeatureUsage.feature == feature,
            FeatureUsage.reset_date > datetime.utcnow() - timedelta(days=30)
        ).first()
        
        if usage and usage.count >= 5:
            return False
    
    return True

# Apply in endpoint
@router.post("/resume-ai/professional-summary")
async def generate_summary(
    current_user: User = Depends(get_current_user)
):
    # Check usage limit
    can_generate = await check_usage_limit(
        current_user.id,
        "resume_ai_summary",
        current_user.subscription.plan_type
    )
    
    if not can_generate:
        raise HTTPException(
            status_code=429,
            detail="Monthly limit reached. Upgrade to Premium for unlimited suggestions."
        )
    
    # ... generate summary
    
    # Track usage
    usage = db.query(FeatureUsage).filter(
        FeatureUsage.user_id == current_user.id,
        FeatureUsage.feature == "resume_ai_summary"
    ).first()
    
    if usage:
        usage.count += 1
    else:
        usage = FeatureUsage(
            user_id=current_user.id,
            feature="resume_ai_summary",
            count=1,
            reset_date=datetime.utcnow()
        )
        db.add(usage)
    
    db.commit()
```

**4. Frontend Billing UI (2h)**
```typescript
// src/pages/account/subscription.tsx
export default function SubscriptionManagement() {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSubscription()
  }, [])

  const fetchSubscription = async () => {
    const res = await fetch('/api/v1x/subscriptions/me', { credentials: 'include' })
    const data = await res.json()
    setSubscription(data)
    setLoading(false)
  }

  const handleUpgrade = async () => {
    const res = await fetch('/api/v1x/subscriptions/create-checkout', {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify({ plan_id: 'premium_monthly' })
    })
    const { checkout_url } = await res.json()
    window.location.href = checkout_url
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-white mb-8">Subscription</h1>
      
      {subscription?.plan_type === 'free' ? (
        <div className="p-6 rounded-xl border border-forgePurple/50 bg-forgePurple/10">
          <h2 className="text-xl font-bold text-white mb-4">Upgrade to Premium</h2>
          <p className="text-gray-300 mb-6">
            Get unlimited Resume AI suggestions, priority support, and more.
          </p>
          <button
            onClick={handleUpgrade}
            className="px-6 py-3 bg-forgePurple text-white rounded-lg hover:bg-forgePurple/90 transition"
          >
            Upgrade to Premium - $9.99/month
          </button>
        </div>
      ) : (
        <div className="p-6 rounded-xl border border-green-500/50 bg-green-500/10">
          <p className="text-green-300">✅ You have Premium access</p>
          <p className="text-gray-400 mt-2">
            Renews on {new Date(subscription?.billing_cycle_end).toLocaleDateString()}
          </p>
        </div>
      )}
    </div>
  )
}
```

#### Success Metrics
- [ ] Stripe integration working
- [ ] Subscriptions create successfully
- [ ] Feature limits enforced
- [ ] UI clearly shows upgrade path
- [ ] Webhook handlers processing payments

---

## Timeline

### Week 1
- **Mon-Tue:** Task 1 (WebSocket) - Developer A
- **Wed:** Task 2 (Date Picker) - Developer B
- **Thu-Fri:** Task 3 (CSV/PDF Export) - Developer A

### Week 2
- **Mon-Tue:** Task 4 (Email Digests) - Developer B
- **Wed-Fri:** Task 5 (Resume AI Testing) - Developer A + B
- **Parallel:** Task 6 (Monetization) - Developer B

## Risk Mitigation

### Technical Risks
- **WebSocket Connection Loss** → Fallback to polling
- **Payment Processing Failure** → Manual invoice system
- **Email Delivery** → Resend queue with retries

### Mitigation Strategies
- Daily backups
- Error monitoring via Sentry
- Staged rollout (staging → prod)
- Rollback plan for each feature

## Success Criteria

### Code Quality
- [ ] 100% of new code has tests
- [ ] No critical security issues
- [ ] Performance benchmarks met
- [ ] Code review approved

### User Experience
- [ ] Mobile fully responsive
- [ ] < 2 second load times
- [ ] Clear error messages
- [ ] Intuitive UI

### Business Impact
- [ ] Revenue tracking enabled
- [ ] Feature adoption monitored
- [ ] User feedback collected
- [ ] Demo-ready by end of sprint

---

## Next Steps

1. **Prepare Sprint 2 kickoff** - Review requirements with team
2. **Set up development environment** - All tools ready
3. **Create feature branches** - Organized code management
4. **Schedule daily standups** - Track progress closely
5. **Plan Sprint 3** - Based on Sprint 2 learnings

---

*Sprint 2 Development Plan - SkillForge Global*  
*Ready for execution post-Sprint 1 deployment*
