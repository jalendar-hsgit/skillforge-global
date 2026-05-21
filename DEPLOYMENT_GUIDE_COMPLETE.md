# 🚀 Complete Deployment Guide - SkillForge Global

**Status**: ✅ Production-Ready  
**Last Updated**: January 5, 2026  
**Infrastructure**: Vercel (Frontend) + Railway (Backend) + PostgreSQL

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Vercel Frontend Setup](#vercel-frontend-setup)
3. [Railway Backend Setup](#railway-backend-setup)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## Quick Start

**Total Setup Time**: ~45 minutes (no coding required)

### Prerequisites
- GitHub account (already have ✅)
- Vercel account (free)
- Railway account (free)
- Slack workspace (optional, for alerts)

### 1️⃣ Deploy Frontend to Vercel (5 min)

```bash
# Step 1: Visit https://vercel.com
# Step 2: Click "Add New Project"
# Step 3: Import your GitHub repo (prasad.r1342/prasad.r1342-project)
# Step 4: Select "Next.js" framework
# Step 5: Add environment variables:
#   NEXT_PUBLIC_API_BASE = https://your-backend-url.railway.app
# Step 6: Click "Deploy"
```

**Result**: Your frontend is live at `https://your-project.vercel.app`

### 2️⃣ Deploy Backend to Railway (10 min)

```bash
# Step 1: Visit https://railway.app
# Step 2: Click "New Project"
# Step 3: Select "Deploy from GitHub"
# Step 4: Select your repo
# Step 5: Select `/backend` folder as root
# Step 6: Add environment variables (see section below)
# Step 7: Select PostgreSQL addon (free tier)
# Step 8: Deploy
```

**Result**: Your backend is live at `https://your-project.railway.app`

### 3️⃣ Connect Frontend to Backend (2 min)

In Vercel dashboard:
```
Project Settings → Environment Variables → Add:
NEXT_PUBLIC_API_BASE = https://your-project.railway.app
```

### 4️⃣ Verify Deployment (3 min)

```bash
# Test frontend
curl https://your-project.vercel.app

# Test backend
curl https://your-project.railway.app/health

# Test connection
curl https://your-project.vercel.app/api/session/me
```

---

## Vercel Frontend Setup

### Configuration File

✅ **Already created**: `vercel.json`

Key settings:
- **Framework**: Next.js 14
- **Build Command**: `npm run build`
- **Dev Command**: `npm run dev`
- **API Rewrites**: Proxies API calls to Railway backend

### Environment Variables

**In Vercel Dashboard** → Project Settings → Environment Variables

| Variable | Value | Type |
|----------|-------|------|
| `NEXT_PUBLIC_API_BASE` | `https://api.railway.app` | Public |
| `NEXT_PUBLIC_STRIPE_KEY` | `pk_test_...` | Public |
| `NEXT_PUBLIC_GA_ID` | Google Analytics ID | Public |

### Deployment Triggers

- **Automatic**: Push to `main` or `v1.0.0-release` branch
- **Manual**: In Vercel dashboard → Click "Redeploy"

### Custom Domain

1. Vercel → Settings → Domains
2. Add your domain (e.g., `skillforge.com`)
3. Update DNS records (CNAME/A records)
4. Wait 24-48 hours for propagation

---

## Railway Backend Setup

### Procfile Configuration

✅ **Already created**: `Procfile`

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables

**In Railway Dashboard** → Project → Variables

```env
DATABASE_URL=postgresql://user:pass@host:5432/skillforge
JWT_SECRET=your-secret-key-min-32-characters
ALLOWED_ORIGINS=https://your-project.vercel.app
STRIPE_SECRET_KEY=sk_test_...
AWS_S3_BUCKET=skillforge-uploads
```

### Database Setup

1. Railway → Add Service → PostgreSQL
2. PostgreSQL automatically added to project
3. Railway injects `DATABASE_URL` automatically
4. Tables auto-create on first run

**Backup Strategy**:
```bash
# Automated: Railway daily backups (7-day retention)
# Manual: Export from Railway dashboard → Backups
```

### Python Runtime

✅ **Already created**: `backend/runtime.txt`

```
3.11.7
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

Two workflows automatically configured:

#### 1️⃣ **test.yml** - Runs on every push/PR

**Triggers**:
- Push to `main`, `v1.0.0-release`, `develop`
- Pull requests to any branch

**Jobs**:
- ✅ Frontend Tests (Next.js build, ESLint)
- ✅ Backend Tests (pytest, Python 3.9 & 3.11)
- ✅ Code Quality (pylint, flake8, mypy)
- ✅ Security Scan (Trivy vulnerability scan)

**Duration**: ~8-10 minutes

**Fails if**:
- Build fails
- Tests fail
- Type errors detected
- Security vulnerabilities found

#### 2️⃣ **deploy.yml** - Runs after tests pass

**Triggers**:
- Tests succeed on `main` or `v1.0.0-release`

**Steps**:
1. Deploy frontend to Vercel
2. Deploy backend to Railway
3. Wait 30 seconds for deployment
4. Health check both services
5. Notify Slack if success/failure

**Duration**: ~5-10 minutes

### Required Secrets

Add these to GitHub → Settings → Secrets → Actions

```
VERCEL_TOKEN              # From vercel.com/tokens
VERCEL_ORG_ID             # From Vercel project
VERCEL_PROJECT_ID         # From Vercel project
RAILWAY_TOKEN             # From railway.app/settings
RAILWAY_PROJECT_ID        # From Railway project
RAILWAY_DATABASE_URL      # From Railway PostgreSQL
JWT_SECRET                # Generate: openssl rand -hex 32
STRIPE_SECRET_KEY         # From Stripe dashboard
SLACK_WEBHOOK             # From Slack (optional)
```

### How to Add Secrets

```bash
# Via GitHub CLI
gh secret set VERCEL_TOKEN --body "your-token"

# Or manually:
# GitHub → Settings → Secrets → Actions → New repository secret
```

---

## Environment Configuration

### Frontend (.env.local)

**Development**:
```env
NEXT_PUBLIC_API_BASE=http://localhost:8001
NEXT_PUBLIC_ENVIRONMENT=development
```

**Production** (set in Vercel):
```env
NEXT_PUBLIC_API_BASE=https://api.railway.app
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_STRIPE_KEY=pk_live_...
```

### Backend (Railway)

**Auto-injected by Railway**:
```
PORT=8000 (or assigned value)
DATABASE_URL=postgresql://...
```

**You must set**:
```
JWT_SECRET
ALLOWED_ORIGINS
STRIPE_SECRET_KEY
```

---

## Monitoring & Alerts

### 1. Uptime Monitoring

**Option A: Railway Built-in** (Free)
- Railway → Project → Insights
- Shows CPU, memory, response time

**Option B: Axiom** (Recommended)
```bash
# 1. Sign up at https://axiom.co
# 2. Create organization
# 3. Create dataset
# 4. Add to Railway env:
#    AXIOM_ORG_ID=...
#    AXIOM_TOKEN=...
```

**Option C: Better Stack** (Free)
```
https://betterstack.com
- Add monitoring endpoint
- Get alerts if down
```

### 2. Error Tracking

**Sentry Setup** (Recommended for backend):

```bash
# 1. Sign up at https://sentry.io
# 2. Create project (Python)
# 3. Get DSN
# 4. Add to Railway:
#    SENTRY_DSN=https://...@sentry.io/...
```

**Backend integration** (in `app/main.py`):
```python
import sentry_sdk
sentry_sdk.init(dsn=settings.SENTRY_DSN)
```

### 3. Slack Notifications

✅ **Already configured** in `deploy.yml`

**Setup**:
```bash
# 1. Create Slack app: https://api.slack.com/apps
# 2. Enable "Incoming Webhooks"
# 3. Create webhook for #deployments channel
# 4. Add to GitHub Secrets:
#    SLACK_WEBHOOK=https://hooks.slack.com/...
```

**Notifications sent for**:
- ✅ Frontend deployed
- ✅ Backend deployed
- ✅ All systems healthy
- ❌ Deployment failed

### 4. Performance Monitoring

**Vercel Analytics** (Built-in):
- Vercel → Project → Analytics
- Shows Web Vitals, response times
- Real User Monitoring (RUM)

**Railway Metrics**:
- Railway → Project → Metrics
- CPU, memory, network usage
- Deployment history

---

## Troubleshooting

### Frontend Issues

#### Build fails with "Memory exceeded"
```bash
# Increase build timeout in vercel.json
"buildCommand": "npm run build -- --maxOldSpaceSize=4096"
```

#### API calls return 502
```bash
# Check if backend is running:
curl https://your-backend.railway.app/health

# Verify API_BASE is correct:
# Vercel → Project Settings → Environment Variables
```

#### Static files not loading
```bash
# Ensure public folder exists:
ls -la src/public/

# Check publicPath in next.config.js
```

### Backend Issues

#### Database connection failed
```bash
# Check DATABASE_URL in Railway:
# Railway → Project → Variables
# Verify PostgreSQL service is running

# Test connection:
psql $DATABASE_URL -c "SELECT 1"
```

#### Port already in use
```bash
# Railway auto-assigns PORT env var
# Update Procfile to use $PORT
# Already done: "uvicorn app.main:app --port $PORT"
```

#### Migrations failed
```bash
# If using Alembic:
# Railway → Services → Python → Command
# alembic upgrade head && uvicorn app.main:app --port $PORT

# For SQLAlchemy auto-create:
# Already enabled in app/main.py
```

### Deployment Pipeline Issues

#### Tests failing locally but passing on GitHub
```bash
# Check Python version:
python --version  # Should be 3.11.x

# Recreate environment:
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### Secrets not accessible in Actions
```bash
# Verify secrets in:
# GitHub → Settings → Secrets → Actions

# Use correct name:
${{ secrets.SECRET_NAME }}  # Case sensitive!
```

---

## Rollback Procedures

### Frontend Rollback

**Option 1: Via Vercel Dashboard**
```
Vercel → Project → Deployments → Click previous deployment → Promote to Production
```

**Option 2: Revert GitHub commit**
```bash
git revert HEAD --no-edit
git push origin main
# Vercel auto-deploys
```

**Duration**: 2-5 minutes

### Backend Rollback

**Option 1: Via Railway Dashboard**
```
Railway → Project → Deployments → Select previous → Promote to Production
```

**Option 2: Revert Git**
```bash
git revert HEAD --no-edit
git push origin v1.0.0-release
# GitHub Actions auto-deploys
```

**Duration**: 5-10 minutes

### Database Rollback

**If data corrupted**:
```
Railway → Backups → Restore from previous backup
# Wait 5-10 minutes
```

**If schema broken**:
```bash
# 1. Restore from backup
# 2. Apply migrations that failed
# 3. Test locally first
# 4. Deploy
```

---

## Post-Deployment Checklist

After first deployment:

- [ ] Frontend loads at `your-domain.vercel.app`
- [ ] Backend responds at `your-backend.railway.app/health`
- [ ] Login works end-to-end
- [ ] API calls succeed
- [ ] Database connection works
- [ ] Static assets load
- [ ] CORS headers correct
- [ ] SSL certificate valid
- [ ] Monitoring active
- [ ] Slack alerts working

---

## Scaling & Optimization

### Frontend Optimization

**Vercel Features**:
- ISR (Incremental Static Regeneration)
- Edge Functions (global distribution)
- Image Optimization (automatic)

**Enable ISR**:
```typescript
// pages/some-page.tsx
export const revalidate = 3600  // Revalidate every hour
```

### Backend Optimization

**Railway Features**:
- Horizontal scaling (add more instances)
- Database replicas (paid)
- Redis caching (optional)

**Enable caching**:
```bash
# Add Redis to Railway project
# Set REDIS_URL env var
# Use in FastAPI
```

---

## Cost Estimation

| Service | Free Tier | Paid Tier | Recommendation |
|---------|-----------|-----------|-----------------|
| **Vercel** | 100GB/month | Pay-as-you-go | Free tier sufficient |
| **Railway** | $5 free/month | $0.002/CPU hour | $10-20/month for prod |
| **PostgreSQL** | 5GB | Scalable | Free tier at start |
| **Slack** | Free | $12.50/user/month | Free for basic alerts |
| **Sentry** | Free tier | $29+/month | Free tier sufficient |
| **Total** | **FREE** | **~$15-30/month** | **Start free** |

---

## Support & Documentation

### Official Docs
- Vercel: https://vercel.com/docs
- Railway: https://railway.app/docs
- Next.js: https://nextjs.org/docs
- FastAPI: https://fastapi.tiangolo.com

### Helpful Links
- [Vercel Status](https://status.vercel.com)
- [Railway Status](https://status.railway.app)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

### Getting Help
1. Check troubleshooting section above
2. Review service status pages
3. Contact support:
   - Vercel: support@vercel.com
   - Railway: support@railway.app

---

## Next Steps

1. ✅ Create Vercel account
2. ✅ Create Railway account
3. ✅ Deploy frontend (5 min)
4. ✅ Deploy backend (10 min)
5. ✅ Configure secrets (5 min)
6. ✅ Test deployment (5 min)
7. ✅ Setup monitoring (10 min)
8. ✅ Add custom domain (optional)

**Total Time**: ~40-50 minutes

**Result**: Production-ready app with CI/CD, monitoring, and auto-scaling!

---

**Last Updated**: January 5, 2026  
**Status**: ✅ Production Ready  
**Deployment Target**: Vercel + Railway
