# 🚀 GITLAB CI/CD + VERCEL + RAILWAY SETUP GUIDE

**Username**: prasadreddy147  
**Total Setup Time**: 60 minutes  
**Cost**: FREE (all free tiers)

---

## 📋 QUICK CHECKLIST

```
Phase 1: Account Creation (15 min)
  ☐ Create Vercel account
  ☐ Create Railway account
  ☐ Connect GitHub to both

Phase 2: Generate Credentials (10 min)
  ☐ Vercel: Organization ID
  ☐ Vercel: Project ID
  ☐ Railway: Token
  ☐ Railway: Project ID

Phase 3: GitLab Configuration (10 min)
  ☐ Add CI/CD Variables to GitLab
  ☐ Configure 4 secrets

Phase 4: Deploy (15 min)
  ☐ Push to main branch
  ☐ Watch GitLab CI/CD pipeline
  ☐ Verify Vercel deployment
  ☐ Verify Railway deployment

Phase 5: Verify (10 min)
  ☐ Test frontend at https://prasadreddy147.vercel.app
  ☐ Test backend API
  ☐ Check health endpoints
```

---

## PHASE 1: CREATE ACCOUNTS (15 MINUTES)

### Step 1A: Create Vercel Account

1. Go to: https://vercel.com/signup
2. Choose **Sign up with GitHub**
3. Authorize Vercel to access your GitHub
4. Enter username: `prasadreddy147`
5. Click **Create Team** (or use personal account)
6. **Save**: You now have a Vercel account

### Step 1B: Create Railway Account

1. Go to: https://railway.app/login
2. Choose **Continue with GitHub**
3. Authorize Railway to access your GitHub
4. Enter username: `prasadreddy147` (if prompted)
5. Create new project
6. **Save**: You now have a Railway account

### Step 1C: Connect Both to Your GitHub

**Vercel**:
1. Go to: https://vercel.com/integrations/github
2. Click **Install**
3. Select: **All repositories** (or select only "prasad.r1342-project")
4. Click **Install & Authorize**

**Railway**:
1. Go to: https://railway.app/integrations
2. Click **GitHub**
3. Click **Connect**
4. Select: **All repositories** or your specific repo
5. Click **Install & Authorize**

---

## PHASE 2: GENERATE CREDENTIALS (10 MINUTES)

### Step 2A: Get Vercel Credentials

#### Get Vercel Organization ID:
1. Go to: https://vercel.com/settings
2. Look for **Team** section
3. Find the **Team ID** (format: `team_xxx...`)
4. **Copy and Save**: `VERCEL_ORG_ID`

#### Get Vercel Project ID:
1. Go to: https://vercel.com/dashboard
2. Click your project: **prasad.r1342-project**
3. Click **Settings** → **General**
4. Find **Project ID** (format: `prj_xxx...`)
5. **Copy and Save**: `VERCEL_PROJECT_ID`

#### Get Vercel Token:
1. Go to: https://vercel.com/account/tokens
2. Click **Create Token**
3. Name: `GitLab-CI-CD`
4. Expiration: **No Expiration** (or 90 days)
5. Scope: **All**
6. Click **Create**
7. **Copy Immediately** (you won't see it again): `VERCEL_TOKEN`

### Step 2B: Get Railway Credentials

#### Get Railway Token:
1. Go to: https://railway.app/account/tokens
2. Click **Create New Token**
3. Name: `GitLab-CI-CD`
4. Click **Create**
5. **Copy Immediately**: `RAILWAY_TOKEN`

#### Get Railway Project ID:
1. Go to: https://railway.app/dashboard
2. Click your project
3. Click **Settings**
4. Find **Project ID** (format: `xxx...`)
5. **Copy and Save**: `RAILWAY_PROJECT_ID`

#### Get Railway Database URL:
1. Go to: https://railway.app/dashboard
2. Click **PostgreSQL** service
3. Click **PostgreSQL** → **Connect**
4. Copy the **PostgreSQL URL**
5. **Save**: `DATABASE_URL`

---

## PHASE 3: ADD GITLAB CI/CD VARIABLES (10 MINUTES)

### Step 3A: Navigate to GitLab CI/CD Settings

1. Go to your GitLab project: https://gitlab.com/prasad.r1342/prasad.r1342-project
2. Click **Settings** (left sidebar)
3. Click **CI/CD** → **Variables**
4. Click **Add variable** (blue button)

### Step 3B: Add 4 Required Variables

#### Variable 1: VERCEL_TOKEN
```
Key:              VERCEL_TOKEN
Value:            [paste from Step 2A]
Protect:          ✓ (check)
Mask input:       ✓ (check)
Environment:      All
```
Click **Add variable**

#### Variable 2: VERCEL_ORG_ID
```
Key:              VERCEL_ORG_ID
Value:            [paste from Step 2A]
Protect:          ✓ (check)
Mask input:       ✓ (check)
Environment:      All
```
Click **Add variable**

#### Variable 3: VERCEL_PROJECT_ID
```
Key:              VERCEL_PROJECT_ID
Value:            [paste from Step 2A]
Protect:          ✓ (check)
Mask input:       ✓ (check)
Environment:      All
```
Click **Add variable**

#### Variable 4: RAILWAY_TOKEN
```
Key:              RAILWAY_TOKEN
Value:            [paste from Step 2B]
Protect:          ✓ (check)
Mask input:       ✓ (check)
Environment:      All
```
Click **Add variable**

#### Variable 5: RAILWAY_PROJECT_ID
```
Key:              RAILWAY_PROJECT_ID
Value:            [paste from Step 2B]
Protect:          ✓ (check)
Mask input:       ✓ (check)
Environment:      All
```
Click **Add variable**

#### Variable 6: DATABASE_URL (Optional, for Railway PostgreSQL)
```
Key:              DATABASE_URL
Value:            [paste from Step 2B]
Protect:          ✓ (check)
Mask input:       ✓ (check)
Environment:      All
```
Click **Add variable**

**Result**: All 5-6 variables added to GitLab ✅

---

## PHASE 4: DEPLOY (15 MINUTES)

### Step 4A: Push Code to Trigger Pipeline

1. Open terminal in your repo:
```bash
cd "d:\python code\sfg\skillforge-global"

# Make sure you're on main or v1.0.0-release branch
git checkout main

# Create a test commit
git add .
git commit -m "deploy: Configure GitLab CI/CD with Vercel + Railway" --allow-empty

# Push to trigger pipeline
git push origin main
```

2. **Watch the pipeline**:
   - Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
   - Click the **latest pipeline**
   - Watch the stages:
     - ✅ **test** (frontend_test, backend_test)
     - ✅ **deploy** (deploy_vercel, deploy_railway, health_check)

### Step 4B: Monitor Pipeline Execution

**Frontend Test** (~3 min):
- Builds Next.js app
- Runs tests (if any)
- Should show ✅ success

**Backend Test** (~3 min):
- Installs Python deps
- Runs pytest (if any)
- Should show ✅ success

**Deploy Vercel** (~4 min):
- Installs Vercel CLI
- Deploys to Vercel
- Should show ✅ success

**Deploy Railway** (~5 min):
- Installs Railway CLI
- Deploys to Railway
- Should show ✅ success

**Health Check** (~2 min):
- Checks if frontend is responding
- Checks if backend is responding
- May show warnings if not ready yet (OK)

---

## PHASE 5: VERIFY DEPLOYMENT (10 MINUTES)

### Step 5A: Check Vercel Deployment

1. Go to: https://vercel.com/dashboard
2. Click **prasad.r1342-project**
3. Look for the latest deployment (should be "READY" in green)
4. Click **Visit** button to open your site

**Expected**:
- Site loads at: `https://prasadreddy147.vercel.app`
- Shows your SkillForge frontend
- No errors in console

### Step 5B: Check Railway Deployment

1. Go to: https://railway.app/dashboard
2. Click your project
3. Look at **Recent Deployments**
4. Latest should show ✅ **Success**

**Expected**:
- Backend running at Railway
- Environment variables configured
- PostgreSQL connected

### Step 5C: Test API Connectivity

Open terminal and run:
```bash
# Test frontend
curl -s https://prasadreddy147.vercel.app | head -20

# Test backend health (if available)
curl -s https://prasadreddy147-backend.up.railway.app/health
```

Or use browser DevTools:
1. Open https://prasadreddy147.vercel.app
2. Open **DevTools** (F12)
3. Go to **Network** tab
4. Check that API calls go to Railway backend
5. Should see requests returning data

---

## ✅ DEPLOYMENT COMPLETE!

### What You Now Have:

```
🌍 Frontend:
   URL: https://prasadreddy147.vercel.app
   Hosted: Vercel Global CDN
   Auto-deploys: On push to main
   
🔧 Backend:
   URL: https://prasadreddy147-backend.up.railway.app
   Hosted: Railway (auto-scaling)
   Database: PostgreSQL (Railway)
   Auto-deploys: On push to main

🚀 CI/CD:
   Provider: GitLab CI/CD
   Testing: Automatic on every push
   Deployment: Automatic on main branch
   Pipeline: 16-20 min total

📊 Monitoring:
   Frontend: Vercel analytics (automatic)
   Backend: Railway metrics (automatic)
   Logs: Available in both platforms
```

### How It Works Now:

```
1. You make code changes
2. Push to main branch:
   git push origin main

3. GitLab CI/CD automatically:
   ✓ Runs tests (frontend + backend)
   ✓ Deploys to Vercel (if tests pass)
   ✓ Deploys to Railway (if tests pass)
   ✓ Runs health checks

4. Your changes go live automatically
   No manual deployment needed!
```

---

## 🔄 CONTINUOUS DEPLOYMENT WORKFLOW

### For Every Code Change:

```bash
# 1. Make changes to your code
# ... edit files ...

# 2. Commit and push
git add .
git commit -m "feat: Add new feature"
git push origin main

# 3. Watch the pipeline
# Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
# Wait 16-20 minutes
# Check ✅ all stages passed

# 4. View live changes
# Frontend: https://prasadreddy147.vercel.app
# Backend: https://prasadreddy147-backend.up.railway.app
```

---

## 🆘 TROUBLESHOOTING

### Pipeline Failed?

1. **Check logs**:
   - Go to GitLab pipeline
   - Click failed job
   - Scroll to bottom for error messages

2. **Common issues**:
   - `VERCEL_TOKEN not found` → Add missing CI/CD variable
   - `RAILWAY_TOKEN not found` → Add missing CI/CD variable
   - `Build failed` → Check frontend/backend build logs
   - `Deploy failed` → Check Vercel/Railway account status

### Vercel Deployment Not Showing?

1. Go to: https://vercel.com/dashboard
2. Click **prasad.r1342-project**
3. Check **Deployments** tab
4. If stuck, manually trigger:
   - Click **Deployments**
   - Click **Redeploy** on latest build

### Railway Not Updating?

1. Go to: https://railway.app/dashboard
2. Click project
3. Check **Recent Deployments**
4. If stuck:
   - Click **Deployments** tab
   - Click **Redeploy**

### Can't Connect to Database?

1. Check **DATABASE_URL** in GitLab variables
2. Verify PostgreSQL service in Railway
3. Check Railway **Environment** variables match

---

## 📞 SUPPORT RESOURCES

**Vercel**:
- Docs: https://vercel.com/docs
- Status: https://status.vercel.com
- Support: https://vercel.com/support

**Railway**:
- Docs: https://docs.railway.app
- Status: https://status.railway.app
- Support: https://discord.gg/railway

**GitLab CI/CD**:
- Docs: https://docs.gitlab.com/ee/ci/
- Examples: https://docs.gitlab.com/ee/ci/examples/

---

## 🎯 NEXT STEPS

### Week 1: Monitor & Test
- [ ] Monitor all deployments
- [ ] Test all features work
- [ ] Check error logs
- [ ] Monitor uptime

### Week 2: Optimize
- [ ] Review Vercel metrics
- [ ] Review Railway metrics
- [ ] Add custom domain (optional)
- [ ] Setup alerts (optional)

### Week 3+: Scale
- [ ] Monitor database usage
- [ ] Optimize slow endpoints
- [ ] Scale as needed
- [ ] Enhance monitoring

---

## 📈 COST TRACKING

Current Free Tier Usage:
```
Vercel          FREE  (includes 100GB bandwidth)
Railway         FREE  ($5 credit/month, you have plenty)
PostgreSQL      FREE  (5GB on free tier)
GitLab CI/CD    FREE  (400 min/month included)
───────────────────────────────────────
TOTAL:          FREE  ✅
```

When you outgrow free tier (~$20-30/month):
- Vercel: Still free for hobby (or $20/mo for pro)
- Railway: $5/month base, then usage-based
- Total: ~$20-40/month for production

---

## ✨ YOU'RE DONE!

**Deployment is complete and automated!** 🎉

From now on:
- Every push to `main` = automatic test + deploy
- No manual deployment needed
- Frontend updates automatically
- Backend updates automatically
- Both stay in sync automatically

**Your URLs**:
- Frontend: https://prasadreddy147.vercel.app
- Backend: https://prasadreddy147-backend.up.railway.app

Enjoy your production deployment! 🚀

