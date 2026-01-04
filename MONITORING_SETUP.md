# 📊 Monitoring & Alerting Setup - SkillForge Global

**Status**: ✅ Ready to Configure  
**Integrations**: 5+ monitoring providers  
**Setup Time**: 30 minutes

---

## Table of Contents

1. [Quick Setup (5 min)](#quick-setup)
2. [Uptime Monitoring](#uptime-monitoring)
3. [Error Tracking](#error-tracking)
4. [Performance Monitoring](#performance-monitoring)
5. [Alert Channels](#alert-channels)
6. [Dashboards](#dashboards)
7. [Logging](#logging)

---

## Quick Setup

### Option A: Best Stack (Recommended - 5 min)

1. **Go to** https://betterstack.com
2. **Sign up** (free tier)
3. **Create monitor**:
   - Name: "SkillForge Frontend"
   - URL: `https://your-project.vercel.app`
   - Check interval: 5 minutes
   - Incident escalation: Email/Slack
4. **Create another**:
   - Name: "SkillForge Backend"
   - URL: `https://your-backend.railway.app/health`
5. **Add to Slack** → Integrations → Slack

### Option B: Full Stack (15 min)

Combines Best Stack + Sentry + Railway metrics

---

## Uptime Monitoring

### 1. Better Stack (Recommended)

**What**: Uptime monitoring + incident management  
**Cost**: Free tier or $29/month  
**Features**: 
- Status page
- Incident management
- SMS/Email/Slack alerts
- Response time tracking

**Setup**:
```bash
# 1. Sign up at https://betterstack.com
# 2. Create monitors:
#    - Frontend: https://your-project.vercel.app
#    - Backend: https://your-backend.railway.app/health
# 3. Set check interval to 5 minutes
# 4. Enable Slack integration (see alert channels)
# 5. Create status page (optional)
```

**Status Page URL**: `https://your-company.betterstack.com`

### 2. Railway Native Monitoring

**Built-in** (no setup required):
- Railway → Project → Metrics
- Shows CPU, memory, network usage
- Deployment history

**Alerts**:
```
Railway → Project → Alerts
Add thresholds:
- CPU > 80%
- Memory > 90%
- Restart detected
```

### 3. Vercel Analytics

**Built-in** (no setup required):
- Vercel → Project → Analytics
- Web Vitals (Core Web Vitals)
- Real User Monitoring (RUM)
- Function execution time

---

## Error Tracking

### 1. Sentry (Recommended for Backend)

**What**: Real-time error tracking + alerting  
**Cost**: Free tier (5,000 errors/month) or $99+/month  

**Setup**:

```bash
# 1. Sign up at https://sentry.io
# 2. Create organization
# 3. Create project → Select "Python"
# 4. Copy DSN (looks like: https://xxx@sentry.io/123456)
# 5. Add to Railway env vars:
#    SENTRY_DSN=https://xxx@sentry.io/123456
```

**Backend Integration** (already ready):

```python
# Add to app/main.py (if not already)
import sentry_sdk
from fastapi import FastAPI

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0
)

app = FastAPI()
```

**View Errors**:
- Sentry → Issues → All issues
- Filter by release, environment, user
- Get stack traces, session info
- Create alerts

**Alert Rules**:
```
Sentry → Project → Alerts → Create Alert Rule
Trigger when:
- New error is introduced
- Error rate > 10%
- Critical error occurs

Send to: Email, Slack, PagerDuty
```

### 2. Rollbar (Alternative)

**What**: Exception monitoring + deployment tracking  
**Cost**: Free tier or $49+/month  

**Setup**: Similar to Sentry, good for Python

---

## Performance Monitoring

### 1. Lighthouse CI (Free, runs on GitHub Actions)

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: ./lighthouserc.json
```

**Create `lighthouserc.json`**:
```json
{
  "ci": {
    "collect": {
      "url": ["https://your-project.vercel.app"],
      "numberOfRuns": 3
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### 2. New Relic (Paid, but comprehensive)

**What**: Full-stack observability  
**Cost**: Free tier or $100+/month  

**Features**:
- Frontend performance
- Backend performance
- Database monitoring
- Synthetics

### 3. DataDog (Enterprise)

**What**: Enterprise-grade monitoring  
**Cost**: $15-50+/month  

---

## Alert Channels

### 1. Slack Integration

**Setup for Better Stack**:
```bash
# 1. Go to https://api.slack.com/apps
# 2. Create New App → From scratch
# 3. Name: "SkillForge Monitoring"
# 4. Workspace: Your workspace
# 5. OAuth & Permissions → Add scopes:
#    - chat:write
#    - chat:write.public
# 6. Install app to workspace
# 7. Copy Bot Token (xoxb-...)
# 8. Create channel #monitoring
# 9. Invite bot to channel
# 10. Back to Better Stack:
#     → Integrations → Slack
#     → Paste Bot Token
#     → Select #monitoring channel
```

**Test**:
```bash
# Trigger a test alert in Better Stack
# You should see message in Slack
```

### 2. Email Alerts

**Better Stack**:
- Automatically enabled
- Uses your account email

**Sentry**:
- Sentry → Alerts → Your email

### 3. SMS Alerts (Premium)

**Better Stack**:
- Settings → SMS
- Add phone number
- Select alerts to notify

**Cost**: $0.50-1.00 per SMS

### 4. PagerDuty Integration

**For escalation**:
```bash
# 1. Sign up at https://pagerduty.com
# 2. Create service
# 3. Connect to Better Stack/Sentry
# 4. On-call schedule + escalation
```

### 5. Webhook to Custom Service

**Example Python webhook receiver**:
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/alert")
async def receive_alert(request: Request):
    data = await request.json()
    # Send to Discord, custom app, etc.
    return {"status": "received"}
```

**Configure in Better Stack**:
- Integrations → Webhook
- URL: `https://your-backend.railway.app/webhook/alert`

---

## Dashboards

### 1. Better Stack Status Page

Public status page for users:

```bash
# 1. Better Stack → Status Pages
# 2. Create new status page
# 3. Add your monitors
# 4. Customize branding
# 5. Share: https://status.skillforge.com
```

**Features**:
- Real-time status
- Incident history
- Component status
- Email notifications

### 2. Custom Grafana Dashboard

**Self-hosted** (advanced):

```bash
# 1. Add Grafana to Docker Compose
# 2. Configure data sources:
#    - Prometheus (Railway metrics)
#    - PostgreSQL
# 3. Create custom dashboards
```

### 3. Railway Metrics Dashboard

Built into Railway:
- Railway → Project → Metrics
- CPU, memory, network, disk
- Deployment history
- Service health

---

## Logging

### 1. Structured Logging Setup

**Frontend** (Next.js):

```typescript
// lib/logger.ts
export const logger = {
  info: (msg: string, data?: any) => {
    console.log(`[INFO] ${msg}`, data)
  },
  error: (msg: string, error?: any) => {
    console.error(`[ERROR] ${msg}`, error)
  },
  warn: (msg: string, data?: any) => {
    console.warn(`[WARN] ${msg}`, data)
  }
}
```

**Backend** (FastAPI):

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### 2. Centralized Logging (Advanced)

**Option A: ELK Stack** (Self-hosted)
- Elasticsearch
- Logstash
- Kibana

**Option B: LogIO** (Cloud)
```bash
# 1. Sign up at https://logio.io
# 2. Create log stream
# 3. Ship logs:
#    LOGIO_TOKEN=xxx in environment
# 4. View dashboard
```

**Option C: Railway Logs** (Simple)
```
Railway → Project → Logs
Stream real-time logs from deployment
```

---

## Implementation Checklist

### Phase 1: Basic (30 min)
- [ ] Create Better Stack account
- [ ] Add uptime monitoring (frontend + backend)
- [ ] Setup Slack webhook
- [ ] Test alert notification

### Phase 2: Error Tracking (20 min)
- [ ] Create Sentry account
- [ ] Get DSN
- [ ] Add SENTRY_DSN to Railway
- [ ] Deploy
- [ ] Test error tracking

### Phase 3: Performance (20 min)
- [ ] Setup Lighthouse CI
- [ ] Configure lighthouse.yml
- [ ] Enable Vercel analytics
- [ ] Monitor Web Vitals

### Phase 4: Advanced (Optional, 30 min)
- [ ] Create Better Stack status page
- [ ] Setup PagerDuty escalation
- [ ] Configure advanced Sentry rules
- [ ] Setup custom dashboards

---

## Monitoring Commands

### Check Backend Health

```bash
# From terminal
curl https://your-backend.railway.app/health

# Expected response:
# {"status": "healthy"}
```

### View Railway Logs

```bash
# Via Railway CLI
railway logs

# In dashboard:
# Railway → Project → Logs
```

### Check Error Rate

```bash
# Sentry
# Sentry → Issues → Graph
# Shows errors over time

# Railway
# Railway → Metrics → Error rate
```

### View Performance

```bash
# Vercel
# Vercel → Analytics → Web Vitals
# Shows Core Web Vitals trends

# Lighthouse
# GitHub Actions → Lighthouse CI
# Shows performance scores
```

---

## Alert Examples

### Good Alert (Act On It)
- ❌ Uptime: Site down for 10 min
- ✅ Action: Restart, check logs, investigate

### Bad Alert (Ignore It)
- ❌ Uptime: CPU at 45% (doesn't indicate problem)
- ❌ Error: One random error (might be user issue)

### Alert Tuning

**Start conservative**:
- High severity: Only for critical issues
- Low severity: For trends and warnings
- Escalation: Page team only for critical

**Adjust over time**:
- Track false positives
- Increase thresholds if too noisy
- Decrease thresholds if issues missed

---

## Cost Breakdown

| Tool | Free | Paid | Recommendation |
|------|------|------|-----------------|
| Better Stack | ✅ (10 monitors) | $29/mo | Free tier sufficient |
| Sentry | ✅ (5K errors) | $99/mo | Free tier for start |
| Lighthouse CI | ✅ | N/A | Free (CI/CD) |
| Slack | ✅ | $12.50/user | Free for alerts |
| PagerDuty | - | $40+/mo | Optional |
| **Total** | **FREE** | **~$60-70/mo** | **Start with free** |

---

## Next Steps

1. **Day 1**: Setup Better Stack + Slack
2. **Day 2**: Setup Sentry for backend errors
3. **Day 3**: Configure advanced alerts
4. **Week 1**: Review monitoring, tune thresholds
5. **Month 1**: Add advanced features (PagerDuty, custom dashboards)

---

## Quick Links

- Better Stack: https://betterstack.com
- Sentry: https://sentry.io
- Railway Metrics: Dashboard → Metrics
- Vercel Analytics: Dashboard → Analytics
- GitHub Actions: Settings → Actions

---

**Questions?** Check the troubleshooting section in DEPLOYMENT_GUIDE_COMPLETE.md

**Status**: ✅ Ready to monitor!
