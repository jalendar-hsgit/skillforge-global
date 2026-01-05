# 🚀 GITLAB CI/CD DEPLOYMENT - QUICK REFERENCE

**Username**: prasadreddy147  
**Status**: ✅ Ready for Configuration

---

## 📊 DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────┐
│         You Push Code to GitLab             │
└──────────────────────┬──────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
    ┌──────────────┐       ┌──────────────┐
    │  TEST STAGE  │       │ DEPLOY STAGE │
    ├──────────────┤       ├──────────────┤
    │ Frontend     │       │ Vercel       │
    │ Backend      │       │ Railway      │
    │ Security     │       │ Health Check │
    └──────────────┘       └──────────────┘
           │                       │
           └───────────┬───────────┘
                       │
         ┌─────────────────────────┐
         │ LIVE IN PRODUCTION      │
         │ 🌍 prasadreddy147 ✅    │
         └─────────────────────────┘
```

---

## ✅ SETUP CHECKLIST (60 MINUTES TOTAL)

### Phase 1: Accounts (15 min)
```bash
# VERCEL
→ https://vercel.com/signup
→ Sign up with GitHub
→ Username: prasadreddy147

# RAILWAY
→ https://railway.app/login
→ Sign in with GitHub
→ Username: prasadreddy147

# Connect both to GitHub (authorize them)
```

### Phase 2: Get Credentials (10 min)

**Vercel** (https://vercel.com/account):
```
VERCEL_ORG_ID         = [Team ID from settings]
VERCEL_PROJECT_ID     = [Project ID from project settings]
VERCEL_TOKEN          = [Create from account/tokens]
```

**Railway** (https://railway.app/account):
```
RAILWAY_TOKEN         = [Create from account/tokens]
RAILWAY_PROJECT_ID    = [Project ID from dashboard]
DATABASE_URL          = [PostgreSQL connection string]
```

### Phase 3: Configure GitLab (10 min)

Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/settings/ci_cd

**Add 6 Variables**:
```
☐ VERCEL_TOKEN        [from Vercel]
☐ VERCEL_ORG_ID       [from Vercel]
☐ VERCEL_PROJECT_ID   [from Vercel]
☐ RAILWAY_TOKEN       [from Railway]
☐ RAILWAY_PROJECT_ID  [from Railway]
☐ DATABASE_URL        [from Railway PostgreSQL]
```

Mark all as **Protected** ✓ and **Masked** ✓

### Phase 4: Deploy (15 min)

```bash
cd "d:\python code\sfg\skillforge-global"
git add .
git commit -m "deploy: Configure GitLab CI/CD"
git push origin main
```

Watch pipeline at:
https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

### Phase 5: Verify (10 min)

```bash
# Frontend
https://prasadreddy147.vercel.app

# Backend
https://prasadreddy147-backend.up.railway.app/health

# Pipeline Status
https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
```

---

## 🔐 CREDENTIAL SOURCES

| Credential | Source | Find At | Copy As |
|-----------|--------|---------|---------|
| VERCEL_TOKEN | Create new | vercel.com/account/tokens | Full token |
| VERCEL_ORG_ID | Your account | vercel.com/settings | Team ID |
| VERCEL_PROJECT_ID | Project settings | vercel.com/[project]/settings | Project ID |
| RAILWAY_TOKEN | Create new | railway.app/account/tokens | Full token |
| RAILWAY_PROJECT_ID | Dashboard | railway.app/dashboard | Project ID |
| DATABASE_URL | PostgreSQL | railway.app/dashboard → PostgreSQL | Full URL |

---

## 📱 PIPELINE STAGES

### Stage 1: TEST (6 minutes)

```yaml
✓ frontend_test
  - npm ci
  - npm run build
  - npm test (if configured)

✓ backend_test
  - pip install -r requirements.txt
  - pytest tests/ (if configured)
```

**Status**: Green ✅ = Tests passed, proceed to deploy

### Stage 2: DEPLOY (10 minutes)

```yaml
✓ deploy_vercel
  - Deploy to: vercel.com
  - URL: https://prasadreddy147.vercel.app
  - Time: 4 min

✓ deploy_railway
  - Deploy to: railway.app
  - URL: https://prasadreddy147-backend.up.railway.app
  - Time: 5 min

✓ health_check
  - Verify frontend is up
  - Verify backend is up
  - Time: 2 min (allows 30s warmup)
```

**Status**: Green ✅ = Deployment successful, site is live

---

## 🔄 DEPLOYMENT WORKFLOW

### Every Time You Push to `main`:

```bash
# 1. Make changes
# ... edit code ...

# 2. Commit
git add .
git commit -m "feat: Your feature"

# 3. Push
git push origin main

# 4. Pipeline runs AUTOMATICALLY
#    - Tests run (pass/fail)
#    - If pass: deploys to Vercel + Railway
#    - If fail: nothing deployed, you get notification

# 5. Check status
# https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

# 6. After 16-20 min: your changes are LIVE
# Frontend: https://prasadreddy147.vercel.app
# Backend: https://prasadreddy147-backend.up.railway.app
```

---

## 📊 PIPELINE CONFIGURATION

Location: [.gitlab-ci.yml](.gitlab-ci.yml)

```yaml
stages:
  - test       # Run tests
  - deploy     # Deploy to production

# Tests run on:
  - Push to main, v1.0.0-release, develop
  - Merge requests

# Deployment runs on:
  - Push to main or v1.0.0-release (ONLY after tests pass)
  - Success from test stage
```

---

## 💰 COST ESTIMATE

| Service | Free Tier | Cost |
|---------|-----------|------|
| Vercel | 100GB/month | FREE ✅ |
| Railway | $5/month credit | FREE ✅ |
| PostgreSQL | 5GB | FREE ✅ |
| GitLab CI/CD | 400 min/month | FREE ✅ |
| **TOTAL** | **All free** | **$0** ✅ |

When you need paid tier (~Month 3):
```
Vercel:   FREE (still) or $20/month (pro)
Railway:  $5-15/month (usage-based)
Total:    ~$20-30/month for production
```

---

## 🆘 QUICK TROUBLESHOOTING

### Pipeline Won't Start?
```
1. Check main branch has changes
2. Go to Settings → CI/CD
3. Ensure runner is enabled
4. Try: git push origin main --force (last resort)
```

### Tests Failing?
```
1. Check console output in GitLab pipeline
2. Scroll to failed job
3. Look for error message at bottom
4. Common: missing deps, syntax errors
```

### Deployment Failing?
```
1. Check CI/CD Variables are added (Settings → CI/CD)
2. Verify token format (no quotes, no spaces)
3. Check Vercel/Railway accounts have project
4. Try deploying manually:
   - vercel --prod --token=$VERCEL_TOKEN
   - railway up --detach
```

### Site Not Updating?
```
1. Check pipeline status: green ✅ or red ❌?
2. Check Vercel dashboard for deployments
3. Check Railway dashboard for deployments
4. Hard refresh browser: Ctrl+Shift+R
5. Try manual redeploy in Vercel/Railway UI
```

---

## 🚀 AFTER DEPLOYMENT SETUP

### First Push Test
```bash
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "test: Verify GitLab CI/CD works"
git push origin main

# Watch pipeline at:
# https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

# Should take 16-20 minutes total
```

### Monitor Deployments
```
Vercel Dashboard:
→ vercel.com/dashboard
→ Watch "Deployments" tab for updates

Railway Dashboard:
→ railway.app/dashboard
→ Watch "Recent Deployments" for updates

GitLab Pipelines:
→ gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
→ Check each stage for progress
```

### Test Connectivity
```bash
# Frontend
curl -I https://prasadreddy147.vercel.app
# Should return: HTTP/1.1 200 OK

# Backend
curl -I https://prasadreddy147-backend.up.railway.app
# Should return: HTTP/1.1 200 OK (or relevant status)
```

---

## 📚 DOCUMENTATION

- **Full Guide**: [GITLAB_VERCEL_RAILWAY_SETUP.md](GITLAB_VERCEL_RAILWAY_SETUP.md)
- **Pipeline Config**: [.gitlab-ci.yml](.gitlab-ci.yml)
- **Vercel Config**: [vercel.json](vercel.json)
- **Railway Config**: [Procfile](Procfile)

---

## 🎯 YOUR DEPLOYMENT URLS

Once deployed, your app is live at:

```
🌍 FRONTEND
URL: https://prasadreddy147.vercel.app
Provider: Vercel (Global CDN)
Status: Check at vercel.com/dashboard

🔧 BACKEND  
URL: https://prasadreddy147-backend.up.railway.app
Provider: Railway (Auto-scaling)
Status: Check at railway.app/dashboard

📊 CI/CD STATUS
URL: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
Provider: GitLab CI/CD
```

---

## ✨ SETUP COMPLETE WHEN:

```
✅ Vercel account created
✅ Railway account created
✅ All 6 CI/CD variables added to GitLab
✅ First push to main triggers pipeline
✅ Pipeline runs tests
✅ Pipeline deploys to Vercel
✅ Pipeline deploys to Railway
✅ Frontend loads at prasadreddy147.vercel.app
✅ Backend responds at prasadreddy147-backend.up.railway.app
✅ Every push auto-deploys (no manual work)
```

---

## 🎉 NEXT ACTIONS

### Right Now:
1. Open [GITLAB_VERCEL_RAILWAY_SETUP.md](GITLAB_VERCEL_RAILWAY_SETUP.md)
2. Follow Phase 1-5 step by step
3. Total time: 60 minutes

### After Deployment:
1. Monitor first few deployments
2. Test all features work
3. Setup monitoring (optional)
4. Add custom domain (optional)

### Going Forward:
```bash
git push origin main
# → Tests run (automatic)
# → Deploys (automatic if tests pass)
# → Live (no manual intervention)
```

---

**Status**: ✅ **READY FOR CONFIGURATION**

Next Step: **Read** [GITLAB_VERCEL_RAILWAY_SETUP.md](GITLAB_VERCEL_RAILWAY_SETUP.md)

