# ✅ GITLAB CI/CD DEPLOYMENT CHECKLIST

**Project**: SkillForge Global  
**Username**: prasadreddy147  
**Deployment**: GitLab CI/CD → Vercel + Railway  
**Start Date**: January 5, 2026  
**Status**: 🟢 READY TO DEPLOY

---

## 📋 COMPLETE SETUP CHECKLIST

### PHASE 1: ACCOUNT CREATION ⏱️ 15 minutes

#### Vercel Account Setup
```
☐ Go to https://vercel.com/signup
☐ Click "Sign up with GitHub"
☐ Authorize access to GitHub
☐ Enter/confirm username: prasadreddy147
☐ Create account (free tier)
⏱️ Estimated: 3 minutes
```

**Verification**:
- [ ] You can log into https://vercel.com/dashboard
- [ ] See "Welcome to Vercel"

---

#### Railway Account Setup
```
☐ Go to https://railway.app/login
☐ Click "Continue with GitHub"
☐ Authorize access to GitHub  
☐ Confirm username: prasadreddy147
☐ Create account (free tier)
⏱️ Estimated: 3 minutes
```

**Verification**:
- [ ] You can log into https://railway.app/dashboard
- [ ] See Railway dashboard

---

#### GitHub Integration - Vercel
```
☐ Go to https://vercel.com/integrations/github
☐ Click "Install"
☐ Select "All repositories" (or only "prasad.r1342-project")
☐ Click "Install & Authorize"
☐ Grant permissions when prompted
⏱️ Estimated: 3 minutes
```

**Verification**:
- [ ] Vercel shows your GitHub repos in dashboard
- [ ] Can see prasad.r1342-project listed

---

#### GitHub Integration - Railway
```
☐ Go to https://railway.app/integrations
☐ Find "GitHub" 
☐ Click "Connect"
☐ Select repos (all or specific)
☐ Click "Install & Authorize"
☐ Grant permissions when prompted
⏱️ Estimated: 3 minutes
```

**Verification**:
- [ ] Railway dashboard shows GitHub integration active
- [ ] Can see your repos in Railway

---

### PHASE 2: CREDENTIAL GENERATION ⏱️ 10 minutes

#### Step 1: Vercel Organization ID
```
☐ Go to https://vercel.com/settings
☐ Look at "Team" section  
☐ Find "Team ID" (starts with team_)
☐ Copy the full ID: ___________________________
☐ Save to secure location (you'll need it later)
⏱️ Estimated: 1 minute
```

**Credential Format**:
```
VERCEL_ORG_ID = team_abc123def456...
```

---

#### Step 2: Vercel Project ID
```
☐ Go to https://vercel.com/dashboard
☐ Click "prasad.r1342-project" (your project)
☐ Click "Settings" → "General"
☐ Find "Project ID" (starts with prj_)
☐ Copy the full ID: ___________________________
⏱️ Estimated: 1 minute
```

**Credential Format**:
```
VERCEL_PROJECT_ID = prj_xyz789abc123...
```

---

#### Step 3: Vercel Token (IMPORTANT - SAVE IMMEDIATELY!)
```
☐ Go to https://vercel.com/account/tokens
☐ Click "Create Token"
☐ Name it: "GitLab-CI-CD"
☐ Expiration: "No Expiration" (or 90 days)
☐ Scope: "All"
☐ Click "Create"
☐ ⚠️ COPY IMMEDIATELY - you won't see it again!
☐ Paste here: ___________________________
⏱️ Estimated: 1 minute
⚠️ CRITICAL: Save this somewhere safe!
```

**Credential Format**:
```
VERCEL_TOKEN = [long string of characters]
```

---

#### Step 4: Railway Token (IMPORTANT - SAVE IMMEDIATELY!)
```
☐ Go to https://railway.app/account/tokens
☐ Click "Create New Token"
☐ Name it: "GitLab-CI-CD"
☐ Click "Create"
☐ ⚠️ COPY IMMEDIATELY - you won't see it again!
☐ Paste here: ___________________________
⏱️ Estimated: 1 minute
⚠️ CRITICAL: Save this somewhere safe!
```

**Credential Format**:
```
RAILWAY_TOKEN = [long string of characters]
```

---

#### Step 5: Railway Project ID
```
☐ Go to https://railway.app/dashboard
☐ Click your project
☐ Click "Settings"
☐ Find "Project ID"
☐ Copy the full ID: ___________________________
⏱️ Estimated: 1 minute
```

**Credential Format**:
```
RAILWAY_PROJECT_ID = abc123def456...
```

---

#### Step 6: Railway Database URL (if using PostgreSQL)
```
☐ Go to https://railway.app/dashboard
☐ Click "PostgreSQL" service
☐ Click "PostgreSQL" → "Connect"
☐ Copy the "PostgreSQL" connection URL
☐ Paste here: ___________________________
⏱️ Estimated: 1 minute
```

**Credential Format**:
```
DATABASE_URL = postgresql://user:pass@host:5432/db
```

---

### PHASE 3: GITLAB CI/CD VARIABLES ⏱️ 10 minutes

#### Navigate to GitLab Settings
```
☐ Go to https://gitlab.com/prasad.r1342/prasad.r1342-project
☐ Click "Settings" (left sidebar, bottom)
☐ Click "CI/CD"
☐ Click "Variables" section
☐ You should see "Add variable" button
⏱️ Estimated: 1 minute
```

---

#### Add Variable 1: VERCEL_TOKEN
```
☐ Click "Add variable"
☐ Key: VERCEL_TOKEN
☐ Value: [paste from Phase 2, Step 3]
☐ Check "Protect variable" ✓
☐ Check "Mask variable" ✓
☐ Environment scope: "All"
☐ Click "Add variable"
⏱️ Estimated: 1 minute

Verification: Green checkmark appears
```

---

#### Add Variable 2: VERCEL_ORG_ID
```
☐ Click "Add variable"
☐ Key: VERCEL_ORG_ID
☐ Value: [paste from Phase 2, Step 1]
☐ Check "Protect variable" ✓
☐ Check "Mask variable" ✓
☐ Environment scope: "All"
☐ Click "Add variable"
⏱️ Estimated: 1 minute

Verification: Variable appears in list
```

---

#### Add Variable 3: VERCEL_PROJECT_ID
```
☐ Click "Add variable"
☐ Key: VERCEL_PROJECT_ID
☐ Value: [paste from Phase 2, Step 2]
☐ Check "Protect variable" ✓
☐ Check "Mask variable" ✓
☐ Environment scope: "All"
☐ Click "Add variable"
⏱️ Estimated: 1 minute

Verification: Variable appears in list
```

---

#### Add Variable 4: RAILWAY_TOKEN
```
☐ Click "Add variable"
☐ Key: RAILWAY_TOKEN
☐ Value: [paste from Phase 2, Step 4]
☐ Check "Protect variable" ✓
☐ Check "Mask variable" ✓
☐ Environment scope: "All"
☐ Click "Add variable"
⏱️ Estimated: 1 minute

Verification: Variable appears in list
```

---

#### Add Variable 5: RAILWAY_PROJECT_ID
```
☐ Click "Add variable"
☐ Key: RAILWAY_PROJECT_ID
☐ Value: [paste from Phase 2, Step 5]
☐ Check "Protect variable" ✓
☐ Check "Mask variable" ✓
☐ Environment scope: "All"
☐ Click "Add variable"
⏱️ Estimated: 1 minute

Verification: Variable appears in list
```

---

#### Add Variable 6: DATABASE_URL (Optional)
```
☐ Click "Add variable"
☐ Key: DATABASE_URL
☐ Value: [paste from Phase 2, Step 6]
☐ Check "Protect variable" ✓
☐ Check "Mask variable" ✓
☐ Environment scope: "All"
☐ Click "Add variable"
⏱️ Estimated: 1 minute

Verification: Variable appears in list
```

---

**Summary after Phase 3**:
```
✓ VERCEL_TOKEN         - Added
✓ VERCEL_ORG_ID        - Added
✓ VERCEL_PROJECT_ID    - Added
✓ RAILWAY_TOKEN        - Added
✓ RAILWAY_PROJECT_ID   - Added
✓ DATABASE_URL         - Added (optional)

All variables should be visible at:
https://gitlab.com/prasad.r1342/prasad.r1342-project/settings/ci_cd
```

---

### PHASE 4: FIRST DEPLOYMENT ⏱️ 15 minutes

#### Prepare Code
```bash
cd "d:\python code\sfg\skillforge-global"

☐ Check current branch
git branch -a

☐ Switch to main (if not already)
git checkout main

☐ Make sure you're up to date
git pull origin main
```

---

#### Trigger Pipeline
```bash
☐ Make a small change (e.g., update README)
# ... edit a file ...

☐ Stage changes
git add .

☐ Commit with deployment message
git commit -m "deploy: Enable GitLab CI/CD with Vercel + Railway"

☐ Push to trigger pipeline
git push origin main

⏱️ Estimated: 1 minute
```

**Verification**:
- [ ] Command shows "Enumerating objects..."
- [ ] No errors in terminal
- [ ] Shows commit hash (e.g., "abc123d")

---

#### Watch Pipeline Execute
```
☐ Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
☐ Click the "latest" pipeline (your recent push)
☐ Watch the stages in order:

Stage 1: TEST (6-8 minutes)
  ☐ frontend_test
    Status: ⏳ Running or ✅ Passed
    Time: 3 min
  
  ☐ backend_test  
    Status: ⏳ Running or ✅ Passed
    Time: 3 min

Stage 2: DEPLOY (8-10 minutes)
  ☐ deploy_vercel
    Status: ⏳ Running or ✅ Passed
    Time: 4 min
    
  ☐ deploy_railway
    Status: ⏳ Running or ✅ Passed
    Time: 5 min
    
  ☐ health_check
    Status: ⏳ Running or ✅ Passed
    Time: 2 min

⏱️ Total estimated: 14-18 minutes
```

---

### PHASE 5: VERIFICATION ⏱️ 10 minutes

#### Check Vercel Deployment
```
☐ Go to: https://vercel.com/dashboard
☐ Click "prasad.r1342-project"
☐ Look for your latest deployment
  Should show: "READY" (green checkmark)
  
☐ Status should show one of:
  ✅ "READY" - Fully deployed
  ⏳ "BUILDING" - Still deploying
  ❌ "FAILED" - Something went wrong
  
☐ Click "Visit" to see your live frontend
☐ Should load at: https://prasadreddy147.vercel.app

⏱️ Estimated: 2 minutes
```

**Verification Checklist**:
- [ ] Deployment shows "READY" status
- [ ] Click "Visit" opens the site
- [ ] Frontend loads without errors
- [ ] See SkillForge branding/content

---

#### Check Railway Deployment
```
☐ Go to: https://railway.app/dashboard
☐ Click your project
☐ Look at "Recent Deployments"
☐ Latest should show: ✅ "Success"

☐ Status options:
  ✅ "Success" - Fully deployed
  ⏳ "Deploying" - Still deploying
  ❌ "Failed" - Something went wrong

☐ Click deployment to see logs
☐ Look for: "listening on port"

⏱️ Estimated: 2 minutes
```

**Verification Checklist**:
- [ ] Deployment shows "Success" status
- [ ] No error messages in logs
- [ ] Shows "listening on port" or similar
- [ ] PostgreSQL service is running

---

#### Test API Connectivity
```bash
# Test frontend
☐ Open: https://prasadreddy147.vercel.app
☐ Check page loads
☐ Open DevTools (F12)
☐ Go to Network tab
☐ Check API calls go to Railway backend

# Test backend health (if configured)
☐ Open: https://prasadreddy147-backend.up.railway.app/health
☐ Should show: 200 OK status
☐ Or similar health endpoint response

⏱️ Estimated: 3 minutes
```

**Verification Checklist**:
- [ ] Frontend loads without 404 errors
- [ ] DevTools shows Network requests
- [ ] API calls go to Railway backend
- [ ] Status codes are 200/201 (success)

---

#### Check GitLab Pipeline Summary
```
Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

Your pipeline should show:
┌─────────────────────────────────────┐
│ Pipeline #[number]                  │
│ Status: ✅ PASSED                   │
│                                     │
│ Test Stage:       ✅ PASSED         │
│ Deploy Stage:     ✅ PASSED         │
│                                     │
│ Duration: 16-20 minutes             │
│ Branch: main                        │
└─────────────────────────────────────┘

⏱️ Estimated: 1 minute
```

**Verification Checklist**:
- [ ] Overall status shows ✅ "PASSED"
- [ ] Test stage shows ✅ "PASSED"
- [ ] Deploy stage shows ✅ "PASSED"
- [ ] All jobs show green checkmarks

---

## 🎯 FINAL VERIFICATION

### All Deployments Live?
```
✅ Frontend:
   URL: https://prasadreddy147.vercel.app
   Status: ✅ READY
   Provider: Vercel

✅ Backend:
   URL: https://prasadreddy147-backend.up.railway.app
   Status: ✅ Success
   Provider: Railway

✅ CI/CD:
   Pipeline: ✅ PASSED
   Status: All jobs successful
   Provider: GitLab
```

---

## 🔄 NEXT DEPLOYMENTS

After first successful deployment, future deployments are automatic!

### Every Code Change:
```bash
# 1. Make changes
# ... edit files ...

# 2. Commit and push
git add .
git commit -m "feat: Your feature"
git push origin main

# 3. Wait 16-20 minutes
# Pipeline runs automatically
# Tests pass: ✅
# Deploy happens: ✅
# Site updates: ✅

# 4. Your changes are LIVE!
# No manual work needed!
```

---

## 📊 MONITORING AFTER DEPLOYMENT

### Daily Checks (Optional)
```
☐ Check GitLab pipelines for any failures
  https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

☐ Check Vercel dashboard for deployments
  https://vercel.com/dashboard

☐ Check Railway dashboard for issues
  https://railway.app/dashboard

☐ Test frontend loads: https://prasadreddy147.vercel.app
☐ Test backend health (if available)
```

### Weekly Checks (Optional)
```
☐ Review deployment history
☐ Check for any error logs
☐ Monitor database usage (Railway)
☐ Monitor bandwidth usage (Vercel)
☐ Review any error tracking (Sentry, if configured)
```

---

## 🆘 TROUBLESHOOTING

### Pipeline Won't Run?
```
Problem: Pushed code but no pipeline started
Solution:
  1. Check: .gitlab-ci.yml exists in repo
  2. Check: File is on main branch
  3. Try: git push origin main --force
  4. Wait: 30 seconds for pipeline to appear
```

### Tests Failing?
```
Problem: Test stage shows ❌ FAILED
Solution:
  1. Click failed job name
  2. Scroll to bottom of logs
  3. Look for error message
  4. Common issues:
     - Missing dependencies (npm install)
     - Syntax errors in code
     - Test failures (logic errors)
     - Database connection issues
```

### Deployment Failing?
```
Problem: Deploy stage shows ❌ FAILED
Solution:
  1. Check Variables in Settings → CI/CD
     - VERCEL_TOKEN should exist
     - RAILWAY_TOKEN should exist
  2. Verify tokens are correct:
     - Go to https://vercel.com/account/tokens
     - Go to https://railway.app/account/tokens
     - Create new ones if needed
  3. Check logs for specific error message
  4. Common issues:
     - Invalid token format
     - Token has wrong permissions
     - Vercel/Railway account issues
```

### Site Not Updating?
```
Problem: Changed code but site still shows old version
Solution:
  1. Verify pipeline completed successfully (✅)
  2. Hard refresh browser: Ctrl+Shift+R
  3. Check Vercel dashboard for latest deployment
  4. Wait 30 seconds (CDN propagation)
  5. Try different browser/incognito mode
```

---

## ✨ SUCCESS INDICATORS

### You'll Know It's Working When:

```
✅ You push code to main
✅ GitLab pipeline starts automatically
✅ Tests run automatically (no action needed)
✅ If tests pass, deployment runs automatically
✅ Vercel shows "READY" status
✅ Railway shows "Success" status
✅ Your changes appear at https://prasadreddy147.vercel.app
✅ Everything happens in 16-20 minutes
✅ No manual deployment needed
```

---

## 📞 SUPPORT

### Official Documentation
- **Vercel**: https://vercel.com/docs
- **Railway**: https://docs.railway.app
- **GitLab CI/CD**: https://docs.gitlab.com/ee/ci/

### Status Pages
- **Vercel Status**: https://status.vercel.com
- **Railway Status**: https://status.railway.app
- **GitLab Status**: https://www.gitlab.com/gitlab-status

### Chat Support
- **Railway Discord**: https://discord.gg/railway
- **Vercel Discussions**: https://github.com/vercel/vercel/discussions

---

## 🎉 CONGRATULATIONS!

Once you complete all 5 phases and see green ✅ checkmarks:

```
🌍 Your frontend is live at:
   https://prasadreddy147.vercel.app

🔧 Your backend is live at:
   https://prasadreddy147-backend.up.railway.app

🚀 Your CI/CD is automated:
   https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

💰 All free tier (no costs!)

📊 Auto-scaling and globally distributed

✅ PRODUCTION READY!
```

---

## 📋 FINAL CHECKLIST

```
Phase 1: Accounts Created
  ✅ Vercel account
  ✅ Railway account
  ✅ GitHub integration (both)

Phase 2: Credentials Saved
  ✅ VERCEL_ORG_ID saved
  ✅ VERCEL_PROJECT_ID saved
  ✅ VERCEL_TOKEN saved (securely!)
  ✅ RAILWAY_TOKEN saved (securely!)
  ✅ RAILWAY_PROJECT_ID saved
  ✅ DATABASE_URL saved

Phase 3: GitLab Variables Added
  ✅ All 6 variables added
  ✅ All marked as Protected
  ✅ All marked as Masked

Phase 4: First Deployment Triggered
  ✅ Code pushed to main
  ✅ Pipeline started
  ✅ Tests ran
  ✅ Deployment ran

Phase 5: Verified Live
  ✅ Vercel shows READY
  ✅ Railway shows Success
  ✅ Frontend loads
  ✅ Backend responds
  ✅ Pipeline shows PASSED

BONUS:
  ✅ Second push triggered auto-deploy
  ✅ No manual work needed
  ✅ Life is good! 🎉
```

---

**Status**: ✅ READY FOR DEPLOYMENT

**Start With**: Phase 1 (Create Accounts)

**Time to Live**: 60 minutes total

**Good luck!** 🚀

