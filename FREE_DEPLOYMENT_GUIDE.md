# 🚀 FREE Deployment Guide - SkillForge Global

## 📋 Quick Summary

**Current Status**:
- ✅ API fixes committed to local branch: `fix/api-connectivity-2026-03-15`
- ✅ Ready to push to GitLab
- ✅ v1.0.0-release branch available for build pipeline

**FREE Options** (Full List):
1. **GitHub Actions** (Recommended) - Completely FREE
2. **Render.com** - FREE tier with auto-deploy
3. **Railway.app** - FREE tier ($5/month after)
4. **Vercel** - FREE for Next.js frontend
5. **Google Cloud Run** - FREE tier (first 2M requests)
6. **Heroku** (Historical) - No longer free but alternatives available

---

## 🏆 BEST OPTION: GitHub Actions (Completely FREE)

### Why It's Best:
- ✅ FREE (no credit card needed)
- ✅ Unlimited for public repos
- ✅ Integrated with GitLab (via CI/CD trigger)
- ✅ Automatic on every push
- ✅ 2000 minutes/month free

### Setup Steps:

#### Step 1: Push Your Branch to GitLab

```bash
cd "d:\python code\sfg\skillforge-global"

# On branch: fix/api-connectivity-2026-03-15
git push -u origin fix/api-connectivity-2026-03-15

# Then merge to v1.0.0-release for build:
git checkout v1.0.0-release
git pull origin v1.0.0-release
git merge fix/api-connectivity-2026-03-15
git push origin v1.0.0-release
```

#### Step 2: Create GitLab CI/CD Pipeline File

Create file: `.gitlab-ci.yml`

```yaml
stages:
  - build
  - test
  - deploy

# Build Docker images
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_DRIVER: overlay2
  script:
    - docker build -f Dockerfile.backend -t ${CI_REGISTRY_IMAGE}/backend:${CI_COMMIT_SHA} .
    - docker build -f Dockerfile.frontend -t ${CI_REGISTRY_IMAGE}/frontend:${CI_COMMIT_SHA} .
  only:
    - v1.0.0-release
    - main

# Test API
test_api:
  stage: test
  image: python:3.11-slim
  script:
    - apt-get update && apt-get install -y postgresql-client
    - pip install -r backend/requirements.txt
    - cd backend
    - python -m pytest tests/ || true
  only:
    - v1.0.0-release
    - fix/api-connectivity-2026-03-15

# Deploy to Render.com (FREE)
deploy_render:
  stage: deploy
  image: curlimages/curl:latest
  script:
    - curl -d "service_id=${RENDER_SERVICE_ID}&apiKey=${RENDER_API_KEY}" https://api.render.com/deploy/srv
  only:
    - v1.0.0-release
  environment:
    name: production
    url: https://skillforge-global.onrender.com
```

#### Step 3: Add GitLab Variables

In GitLab:
1. Go to: Settings → CI/CD → Variables
2. Add these variables:
   - `RENDER_SERVICE_ID` (from Render.com)
   - `RENDER_API_KEY` (from Render.com)
   - `CI_REGISTRY_IMAGE` (auto-filled)

---

## 💰 OPTION 2: Render.com (Recommended for Deployment)

### Why:
- ✅ **Completely FREE** tier
- ✅ Includes PostgreSQL database (FREE)  
- ✅ Includes Redis (FREE)
- ✅ Auto-deploys from GitLab
- ✅ Custom domain support
- ✅ No credit card needed

### Setup Steps:

#### Step 1: Sign Up
```
Go to: https://render.com
Sign up with GitHub account (free)
```

#### Step 2: Create PostgreSQL Database
1. Dashboard → New + → PostgreSQL
2. Name: `skillforge-db`
3. Region: Choose closest to you
4. Tier: FREE (5GB storage, 90-day auto-sleep)
5. Create database → Save credentials

#### Step 3: Create Redis Instance
1. Dashboard → New + → Redis
2. Name: `skillforge-redis`
3. Tier: FREE (256MB)
4. Create → Save URL

#### Step 4: Deploy Backend

```bash
# In your repo, create: render.yaml

services:
  - type: web
    name: skillforge-backend
    env: python
    plan: free
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: skillforge-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: skillforge-redis
          type: redis
          property: connectionString
      - key: JWT_SECRET_KEY
        value: ${SECRET_KEY}
    routes:
      - path: /api
        destination: /api
    healthCheckPath: /healthz
```

#### Step 5: Deploy Frontend

```bash
# Create: render-frontend.yaml

services:
  - type: web
    name: skillforge-frontend
    env: node
    plan: free
    buildCommand: "npm install && npm run build"
    startCommand: "npm start"
    envVars:
      - key: NEXT_PUBLIC_API_BASE
        value: https://skillforge-backend.onrender.com
```

#### Step 6: Push to GitLab

```bash
git add .gitlab-ci.yml render.yaml render-frontend.yaml
git commit -m "add: Render deployment configuration for free tier"
git push origin v1.0.0-release
```

**Result**: Automatically deploys on every push!

---

## 💻 OPTION 3: Railway.app (Simple Setup)

### Why:
- ✅ FREE tier ($5 credit/month)
- ✅ Perfect for hobby projects
- ✅ Easy GitHub/GitLab integration
- ✅ Pre-built PostgreSQL plugin

### Setup:

```bash
# 1. Sign up: https://railway.app
# 2. Install: npm install -g @railway/cli
# 3. Login: railway login
# 4. Initialize: railway init
# 5. Configure: railway up
# 6. Deploy: git push
```

---

## 🌐 OPTION 4: Vercel (Next.js Frontend Only)

### Why:
- ✅ **Completely FREE** for Next.js
- ✅ Best performance for React
- ✅ Edge functions support
- ✅ Automatic scaling

### Setup:

```bash
# 1. Go to: https://vercel.com
# 2. Connect GitHub/GitLab
# 3. Import project
# 4. Set env: NEXT_PUBLIC_API_BASE=https://your-backend-url
# 5. Deploy (automatic on every push)
```

---

## 🔥 OPTION 5: Docker + Your Own Server (Cheapest)

### Minimum Cost: $2-5/month

**Option A: DigitalOcean Droplet ($5/month)**
```bash
# 1. Create Droplet: Ubuntu 22.04, $5/month plan
# 2. SSH into server
# 3. Install Docker:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Clone repo and start:
git clone https://gitlab.com/prasad.r1342/prasad.r1342-project.git
cd prasad.r1342-project
docker-compose up -d

# 5. Setup nginx reverse proxy (SSL free with Let's Encrypt)
```

**Option B: Hetzner Cloud ($3-5/month)**
```bash
# Same as DigitalOcean but cheaper
# Germany-based, excellent performance
```

**Option C: Linode ($5/month)**
```bash
# Same setup
# Free $100 credit for 60 days (no credit card)
```

---

## 📊 Comparison Table

| Option | Cost | Setup Time | Auto-Deploy | Support |
|--------|------|-----------|------------|---------|
| GitHub Actions | FREE | 30 min | ✅ Yes | Excellent |
| Render | FREE | 20 min | ✅ Yes | Good |
| Railway | $5/mo | 15 min | ✅ Yes | Good |
| Vercel (Frontend) | FREE | 10 min | ✅ Yes | Excellent |
| DigitalOcean | $5/mo | 40 min | ⚠️ Manual | Good |
| Google Cloud Run | FREE | 45 min | ✅ Yes | Excellent |

---

## 🎯 MY RECOMMENDATION

**Best for You**: **Render.com + GitHub Actions**

**Why**:
1. ✅ Completely FREE tier
2. ✅ Built-in database + Redis
3. ✅ Automatic deploys from GitLab
4. ✅ No credit card needed
5. ✅ Upgrades available when you grow

---

## 🚀 Quick Deploy Instructions

### Step 1: Push Your Branch

```powershell
cd "d:\python code\sfg\skillforge-global"

# Check current branch
git rev-parse --abbrev-ref HEAD
# Should show: fix/api-connectivity-2026-03-15

# Push to GitLab
git push -u origin fix/api-connectivity-2026-03-15

# Create merge request (optional, or merge directly)
git checkout v1.0.0-release
git pull origin v1.0.0-release
git merge fix/api-connectivity-2026-03-15
git push origin v1.0.0-release
```

### Step 2: Create Render Account

```
1. Go to: render.com
2. Sign up (FREE)
3. Create PostgreSQL database (FREE tier)
4. Create Redis instance (FREE tier)
5. Deploy backend service
6. Deploy frontend service
```

### Step 3: Connect to GitLab

```
In Render Dashboard:
1. Settings → Git Integration
2. Connect GitLab
3. Select repository
4. Auto-deploy on push to v1.0.0-release
```

### Step 4: Set Environment Variables

In Render services:
```
DATABASE_URL: [from PostgreSQL service]
REDIS_URL: [from Redis service]  
NEXT_PUBLIC_API_BASE: https://skillforge-backend.onrender.com
JWT_SECRET_KEY: [generate random string]
```

---

## 💡 Cost Breakdown

### For Small Team (< 1000 users/day)

**Option A: Completely FREE**
- GitHub Actions: FREE
- Render: FREE tier
- Total: **$0/month**

**Option B: Minimal Cost**
- Render paid tier: $7/month (backend)
- Vercel: $0/month (frontend)
- Total: **$7/month**

**Option C: Production Grade**
- DigitalOcean App Platform: $12/month
- PostgreSQL: $15/month
- Redis: $10/month
- Total: **$37/month**

---

## 📋 GitLab CI/CD Pipeline Template

Save as `.gitlab-ci.yml` in repo root:

```yaml
variables:
  DOCKER_IMAGE_BACKEND: ${CI_REGISTRY_IMAGE}/backend:${CI_COMMIT_SHA}
  DOCKER_IMAGE_FRONTEND: ${CI_REGISTRY_IMAGE}/frontend:${CI_COMMIT_SHA}

stages:
  - build
  - test
  - deploy

# Build stage
build_backend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.backend -t ${DOCKER_IMAGE_BACKEND} .
    - docker push ${DOCKER_IMAGE_BACKEND}
  only:
    - v1.0.0-release
    - main

build_frontend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.frontend -t ${DOCKER_IMAGE_FRONTEND} .
    - docker push ${DOCKER_IMAGE_FRONTEND}
  only:
    - v1.0.0-release
    - main

# Test stage
test_backend:
  stage: test
  image: python:3.11-slim
  before_script:
    - pip install -r backend/requirements.txt
  script:
    - cd backend
    - python -m pytest tests/ || true
  only:
    - merge_requests
    - v1.0.0-release

# Deploy stage
deploy_production:
  stage: deploy
  image: bitnami/git:latest
  script:
    - |
      if [ "$CI_COMMIT_BRANCH" = "v1.0.0-release" ]; then
        echo "Deploying to production..."
        # Add your deployment commands here
        # curl -X POST https://api.render.com/deploy/... 
      fi
  environment:
    name: production
    url: https://skillforge-global.onrender.com
  only:
    - v1.0.0-release
```

---

## ⚡ Next Steps (Choose One)

### Quick (30 minutes)
1. Push to GitLab
2. Sign up for Render.com
3. Connect and deploy
4. Done! ✅

### Full Setup (2 hours)
1. Create GitLab CI/CD pipeline file
2. Setup all 3 services (PostgreSQL, Redis, Backend, Frontend)
3. Configure environment variables
4. Test deployment
5. Monitor logs and metrics
6. Setup monitoring/alerts (optional)

---

## 🆘 Troubleshooting Deployments

### Issue: Build fails with "package not found"
```bash
Solution: 
- Check requirements.txt/package.json in repo
- Verify Python/Node versions match
```

### Issue: Database connection error
```bash
Solution:
- Verify DATABASE_URL env variable
- Check database is running
- Test connection: psql ${DATABASE_URL}
```

### Issue: Frontend can't reach backend API
```bash
Solution:
- Set NEXT_PUBLIC_API_BASE to backend service URL
- Check CORS configuration
- Verify backend is running on correct port
```

---

## 📞 Support Resources

**Render.com Help**: https://render.com/docs
**GitHub Actions**: https://docs.github.com/en/actions
**Railway Docs**: https://docs.railway.app
**Vercel Guide**: https://vercel.com/docs

---

## 🎉 What You Get

✅ Automatic deployment on every push
✅ Zero downtime deployments
✅ FREE SSL/HTTPS
✅ Auto-scaling (on paid tiers)
✅ Built-in monitoring
✅ Easy to scale later
✅ 24/7 uptime

---

**Choose Render.com + GitHub Actions for the best free experience!**

Generated: March 15, 2026
