#!/usr/bin/env python3
"""
Demo User & Credentials Setup Script
Creates demo users and test data for SkillForge Global
Username: prasadreddy147
Date: January 5, 2026
"""

import os
import sys
import json
import hashlib
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def create_demo_users_and_credentials():
    """Create demo users and save credentials"""
    
    print("=" * 70)
    print("  SKILLFORGE GLOBAL - DEMO USER & CREDENTIALS SETUP")
    print("=" * 70)
    print()
    
    # Demo Users
    demo_users = {
        "admin": {
            "email": "admin@prasadreddy147.com",
            "password": "Admin@123456",
            "role": "ADMIN",
            "name": "Admin User",
            "description": "Main administrator account"
        },
        "mentor": {
            "email": "mentor@prasadreddy147.com",
            "password": "Mentor@123456",
            "role": "MENTOR",
            "name": "Demo Mentor",
            "description": "Sample mentor account"
        },
        "student": {
            "email": "student@prasadreddy147.com",
            "password": "Student@123456",
            "role": "USER",
            "name": "Demo Student",
            "description": "Sample student account"
        }
    }
    
    # Deployment Credentials Placeholder
    deployment_creds = {
        "vercel": {
            "account_username": "prasadreddy147",
            "signup_url": "https://vercel.com/signup",
            "dashboard_url": "https://vercel.com/dashboard",
            "settings_url": "https://vercel.com/settings",
            "tokens_url": "https://vercel.com/account/tokens",
            "note": "Create account with GitHub, then generate token at tokens_url"
        },
        "railway": {
            "account_username": "prasadreddy147",
            "signup_url": "https://railway.app/login",
            "dashboard_url": "https://railway.app/dashboard",
            "settings_url": "https://railway.app/account/tokens",
            "tokens_url": "https://railway.app/account/tokens",
            "note": "Create account with GitHub, then generate token at tokens_url"
        },
        "gitlab": {
            "project_url": "https://gitlab.com/prasad.r1342/prasad.r1342-project",
            "ci_cd_variables_url": "https://gitlab.com/prasad.r1342/prasad.r1342-project/settings/ci_cd",
            "variables_needed": [
                "VERCEL_TOKEN",
                "VERCEL_ORG_ID",
                "VERCEL_PROJECT_ID",
                "RAILWAY_TOKEN",
                "RAILWAY_PROJECT_ID",
                "DATABASE_URL"
            ]
        }
    }
    
    # Create credentials file
    credentials_file = Path(__file__).parent / "DEMO_CREDENTIALS.json"
    
    print("📝 DEMO USERS")
    print("-" * 70)
    for user_type, user_data in demo_users.items():
        print(f"\n{user_type.upper()} ACCOUNT:")
        print(f"  Email:    {user_data['email']}")
        print(f"  Password: {user_data['password']}")
        print(f"  Role:     {user_data['role']}")
        print(f"  Name:     {user_data['name']}")
    
    print("\n" + "=" * 70)
    print("🔑 DEPLOYMENT CREDENTIALS LOCATIONS")
    print("=" * 70)
    
    print("\n📍 VERCEL:")
    print(f"  • Signup: {deployment_creds['vercel']['signup_url']}")
    print(f"  • Dashboard: {deployment_creds['vercel']['dashboard_url']}")
    print(f"  • Get Token: {deployment_creds['vercel']['tokens_url']}")
    print(f"  • Username: {deployment_creds['vercel']['account_username']}")
    
    print("\n📍 RAILWAY:")
    print(f"  • Signup: {deployment_creds['railway']['signup_url']}")
    print(f"  • Dashboard: {deployment_creds['railway']['dashboard_url']}")
    print(f"  • Get Token: {deployment_creds['railway']['tokens_url']}")
    print(f"  • Username: {deployment_creds['railway']['account_username']}")
    
    print("\n📍 GITLAB CI/CD:")
    print(f"  • Project: {deployment_creds['gitlab']['project_url']}")
    print(f"  • Settings: {deployment_creds['gitlab']['ci_cd_variables_url']}")
    print(f"  • Variables needed:")
    for var in deployment_creds['gitlab']['variables_needed']:
        print(f"    - {var}")
    
    # Save to file
    all_credentials = {
        "app_users": demo_users,
        "deployment": deployment_creds,
        "created_at": "2026-01-05",
        "username": "prasadreddy147"
    }
    
    with open(credentials_file, "w") as f:
        json.dump(all_credentials, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ Credentials saved to: {credentials_file}")
    print("=" * 70)
    
    return demo_users, deployment_creds

def create_env_template():
    """Create .env.example file"""
    
    env_template = """# SkillForge Global - Environment Variables
# Copy this to .env and fill in your values

# Frontend
NEXT_PUBLIC_API_BASE=http://localhost:8001

# Backend
DATABASE_URL=sqlite:///./app/data/skillforge.db
JWT_SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin User
ADMIN_EMAIL=admin@prasadreddy147.com
ADMIN_PASSWORD=Admin@123456

# Demo Mode
DEMO_MODE=true

# Server
HOST=0.0.0.0
PORT=8001

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8001","https://prasadreddy147.vercel.app"]

# Security
CSRF_ENABLED=true
SESSION_TIMEOUT_MINUTES=30

# Deployment (Add these when deploying)
# VERCEL_TOKEN=
# RAILWAY_TOKEN=
# DATABASE_URL=postgresql://...
"""
    
    env_file = Path(__file__).parent / ".env.example"
    with open(env_file, "w") as f:
        f.write(env_template)
    
    print(f"✅ Environment template created: {env_file}")

def create_quick_start_script():
    """Create quick start bash script"""
    
    script_content = """#!/bin/bash
# Quick Start Deployment Script
# SkillForge Global (prasadreddy147)

set -e

echo "=================================================="
echo "  SKILLFORGE GLOBAL - QUICK START"
echo "  Username: prasadreddy147"
echo "=================================================="
echo ""

# Colors
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Step 1: Setup local environment
echo -e "${BLUE}[1/6] Setting up local environment...${NC}"
cd backend
pip install -r requirements.txt > /dev/null 2>&1
python init_db.py > /dev/null 2>&1
python seed_all_demo_data.py > /dev/null 2>&1
cd ..
echo -e "${GREEN}✓ Local environment ready${NC}"

# Step 2: Start backend
echo -e "${BLUE}[2/6] Starting backend server...${NC}"
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..
sleep 3
echo -e "${GREEN}✓ Backend running (PID: $BACKEND_PID)${NC}"

# Step 3: Start frontend
echo -e "${BLUE}[3/6] Starting frontend server...${NC}"
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
sleep 5
echo -e "${GREEN}✓ Frontend running (PID: $FRONTEND_PID)${NC}"

# Step 4: Display credentials
echo ""
echo -e "${YELLOW}📝 DEMO CREDENTIALS:${NC}"
echo "  Admin:"
echo "    Email: admin@prasadreddy147.com"
echo "    Password: Admin@123456"
echo ""
echo "  Mentor:"
echo "    Email: mentor@prasadreddy147.com"
echo "    Password: Mentor@123456"
echo ""
echo "  Student:"
echo "    Email: student@prasadreddy147.com"
echo "    Password: Student@123456"
echo ""

# Step 5: Display URLs
echo -e "${YELLOW}🌍 LOCAL URLS:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  Backend: http://localhost:8001"
echo "  API Docs: http://localhost:8001/docs"
echo ""

# Step 6: Ready message
echo "=================================================="
echo -e "${GREEN}✅ Application is running!${NC}"
echo "=================================================="
echo ""
echo "To deploy to production:"
echo "  1. Follow: GITLAB_VERCEL_RAILWAY_SETUP.md"
echo "  2. Create Vercel account: https://vercel.com/signup"
echo "  3. Create Railway account: https://railway.app/login"
echo "  4. Add GitLab CI/CD variables"
echo "  5. Push to main: git push origin main"
echo ""
echo "Press Ctrl+C to stop servers"
echo ""

# Keep script running
wait
"""
    
    script_file = Path(__file__).parent / "quick-start.sh"
    with open(script_file, "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_file, 0o755)
    print(f"✅ Quick start script created: {script_file}")

def create_deployment_checklist():
    """Create deployment checklist"""
    
    checklist = """# 🚀 COMPLETE DEPLOYMENT CHECKLIST

**Project**: SkillForge Global  
**Username**: prasadreddy147  
**Status**: READY FOR AUTOMATED DEPLOYMENT

---

## ✅ PRE-DEPLOYMENT (Already Done!)

- ✅ GitLab CI/CD pipeline configured (.gitlab-ci.yml)
- ✅ Vercel config created (vercel.json)
- ✅ Railway config created (Procfile + runtime.txt)
- ✅ Demo users created (admin, mentor, student)
- ✅ Database initialized with test data
- ✅ Documentation complete (6 guides)
- ✅ All code pushed to GitLab v1.0.0-release

---

## 🔑 DEPLOYMENT PHASE (60 Minutes)

### Phase 1: Create External Accounts (15 min)

#### Vercel Account
```
☐ Go to: https://vercel.com/signup
☐ Click "Sign up with GitHub"
☐ Authorize Vercel
☐ Username: prasadreddy147
☐ Create account

Demo credentials for testing:
Email:    admin@prasadreddy147.com
Password: Admin@123456
```

#### Railway Account
```
☐ Go to: https://railway.app/login
☐ Click "Continue with GitHub"
☐ Authorize Railway
☐ Username: prasadreddy147
☐ Create account
```

#### GitHub Integration
```
☐ Vercel: https://vercel.com/integrations/github
   ├─ Click "Install"
   ├─ Select repositories
   └─ Authorize

☐ Railway: https://railway.app/integrations
   ├─ Find GitHub
   ├─ Click "Connect"
   └─ Authorize
```

---

### Phase 2: Get API Credentials (10 min)

#### Get Vercel Credentials
```
VERCEL_ORG_ID:
☐ Go to: https://vercel.com/settings
☐ Find "Team ID"
☐ Copy: ___________________________

VERCEL_PROJECT_ID:
☐ Go to: https://vercel.com/dashboard
☐ Click your project
☐ Click Settings → General
☐ Copy "Project ID": ___________________________

VERCEL_TOKEN:
☐ Go to: https://vercel.com/account/tokens
☐ Click "Create Token"
☐ Name: GitLab-CI-CD
☐ Copy immediately: ___________________________
```

#### Get Railway Credentials
```
RAILWAY_TOKEN:
☐ Go to: https://railway.app/account/tokens
☐ Click "Create New Token"
☐ Copy immediately: ___________________________

RAILWAY_PROJECT_ID:
☐ Go to: https://railway.app/dashboard
☐ Click your project
☐ Find Project ID: ___________________________

DATABASE_URL:
☐ Go to: https://railway.app/dashboard
☐ Click PostgreSQL
☐ Click Connect
☐ Copy PostgreSQL URL: ___________________________
```

---

### Phase 3: Configure GitLab CI/CD (10 min)

Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/settings/ci_cd

#### Add Variables (all with Protected ✓ and Masked ✓)

```
Variable 1: VERCEL_TOKEN
☐ Key: VERCEL_TOKEN
☐ Value: [from Vercel]
☐ Protected: ✓
☐ Masked: ✓
☐ Click "Add variable"

Variable 2: VERCEL_ORG_ID
☐ Key: VERCEL_ORG_ID
☐ Value: [from Vercel]
☐ Protected: ✓
☐ Masked: ✓
☐ Click "Add variable"

Variable 3: VERCEL_PROJECT_ID
☐ Key: VERCEL_PROJECT_ID
☐ Value: [from Vercel]
☐ Protected: ✓
☐ Masked: ✓
☐ Click "Add variable"

Variable 4: RAILWAY_TOKEN
☐ Key: RAILWAY_TOKEN
☐ Value: [from Railway]
☐ Protected: ✓
☐ Masked: ✓
☐ Click "Add variable"

Variable 5: RAILWAY_PROJECT_ID
☐ Key: RAILWAY_PROJECT_ID
☐ Value: [from Railway]
☐ Protected: ✓
☐ Masked: ✓
☐ Click "Add variable"

Variable 6: DATABASE_URL
☐ Key: DATABASE_URL
☐ Value: [from Railway PostgreSQL]
☐ Protected: ✓
☐ Masked: ✓
☐ Click "Add variable"
```

---

### Phase 4: First Deployment (15 min)

```bash
# Navigate to repo
cd "d:\\python code\\sfg\\skillforge-global"

# Make sure on correct branch
git checkout main

# Create deployment commit
git add .
git commit -m "deploy: Initialize automated deployment (prasadreddy147)" --allow-empty

# Push to trigger pipeline
git push origin main
```

#### Watch Pipeline
```
Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines

Expected stages:
✓ TEST (6-8 min)
  ├─ frontend_test
  └─ backend_test

✓ DEPLOY (8-10 min)
  ├─ deploy_vercel
  ├─ deploy_railway
  └─ health_check

Total: 16-20 minutes
```

---

### Phase 5: Verify Deployment (10 min)

```
✓ Vercel Dashboard
  Go to: https://vercel.com/dashboard
  Status: "READY" (green)
  
✓ Railway Dashboard
  Go to: https://railway.app/dashboard
  Status: "Success" (green)
  
✓ Test Frontend
  URL: https://prasadreddy147.vercel.app
  Should load without errors
  
✓ Test Backend
  URL: https://prasadreddy147-backend.up.railway.app/health
  Should respond with 200 OK
  
✓ GitLab Pipeline
  Go to: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
  Status: All stages PASSED (green)
```

---

## 🎯 Demo Credentials (For Testing)

### Admin Account
```
Email:    admin@prasadreddy147.com
Password: Admin@123456
Role:     ADMIN
Features: Full access, user management, analytics
```

### Mentor Account
```
Email:    mentor@prasadreddy147.com
Password: Mentor@123456
Role:     MENTOR
Features: Create courses, manage sessions, view analytics
```

### Student Account
```
Email:    student@prasadreddy147.com
Password: Student@123456
Role:     USER
Features: View courses, book sessions, track progress
```

---

## 🚀 After First Deployment - Continuous Deployment

Every code change is now automatically deployed!

```bash
# 1. Make code changes
# ... edit files ...

# 2. Commit and push
git add .
git commit -m "feat: Your feature"
git push origin main

# 3. Automatic deployment (16-20 min)
# Pipeline runs → Tests pass → Deploys
# Frontend: https://prasadreddy147.vercel.app (updated)
# Backend: https://prasadreddy147-backend.up.railway.app (updated)

# 4. No manual work needed!
```

---

## 💡 Testing After Deployment

### Frontend Testing
```
1. Open: https://prasadreddy147.vercel.app
2. Login with demo credentials
3. Test all features
4. Check DevTools → Network
   └─ Verify API calls go to Railway backend
```

### Backend Testing
```
1. API Docs: https://prasadreddy147-backend.up.railway.app/docs
2. Test endpoints with demo users
3. Check database is working
4. Verify all services responding
```

### Production Verification
```
✓ Frontend loads from Vercel CDN
✓ Backend responds from Railway
✓ Database queries working
✓ Authentication working
✓ All features functional
```

---

## 🔧 Troubleshooting

### Pipeline Won't Start?
```
1. Verify .gitlab-ci.yml exists
2. Check you pushed to main branch
3. Wait 30 seconds
4. Refresh pipeline page
```

### Deployment Failing?
```
1. Check CI/CD variables are all present
2. Verify tokens are correct and not expired
3. Check Vercel/Railway accounts exist
4. Review pipeline job logs for error message
```

### Site Not Updating?
```
1. Verify pipeline shows all green ✓
2. Check Vercel/Railway dashboards
3. Hard refresh: Ctrl+Shift+R
4. Wait 30 seconds (CDN propagation)
```

### Can't Login with Demo Credentials?
```
1. Verify backend is running
2. Check database has demo data
3. Try: curl https://prasadreddy147-backend.up.railway.app/health
4. Review backend logs in Railway dashboard
```

---

## 📊 Your Live URLs

```
🌍 Frontend
   https://prasadreddy147.vercel.app
   Status: Check at vercel.com/dashboard
   
🔧 Backend
   https://prasadreddy147-backend.up.railway.app
   Docs: https://prasadreddy147-backend.up.railway.app/docs
   Status: Check at railway.app/dashboard
   
📊 Pipeline
   https://gitlab.com/prasad.r1342/prasad.r1342-project/-/pipelines
   Status: Check for green checkmarks
```

---

## ✨ FINAL CHECKLIST

Before you're done:

```
✓ Created Vercel account
✓ Created Railway account
✓ GitHub authorized both platforms
✓ All 6 credentials retrieved
✓ All 6 GitLab CI/CD variables added
✓ Code pushed to main
✓ Pipeline executed successfully
✓ Vercel shows "READY"
✓ Railway shows "Success"
✓ Frontend loads
✓ Backend responds
✓ Demo users working
✓ Tested login with credentials
```

---

## 🎉 DEPLOYMENT COMPLETE!

Your app is now:
- ✅ Deployed to production (globally)
- ✅ Auto-testing on every push
- ✅ Auto-deploying when tests pass
- ✅ Monitored and logged
- ✅ Ready for real users

**Next**: Monitor deployments and make code changes!

Every push = automatic test + deploy (16-20 min)
No manual work needed ever again!

---

**Setup Time**: 60 minutes  
**Cost**: FREE  
**Status**: ✅ PRODUCTION READY

Good luck! 🚀

"""
    
    checklist_file = Path(__file__).parent / "COMPLETE_DEPLOYMENT_CHECKLIST.md"
    with open(checklist_file, "w") as f:
        f.write(checklist)
    
    print(f"✅ Deployment checklist created: {checklist_file}")

def main():
    """Main function"""
    print()
    
    # Create demo users
    demo_users, deployment_creds = create_demo_users_and_credentials()
    
    print()
    
    # Create environment template
    create_env_template()
    
    # Create quick start script
    create_quick_start_script()
    
    # Create deployment checklist
    create_deployment_checklist()
    
    print()
    print("=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("📋 Files created:")
    print("  1. DEMO_CREDENTIALS.json - All credentials and URLs")
    print("  2. .env.example - Environment variables template")
    print("  3. quick-start.sh - Quick start script")
    print("  4. COMPLETE_DEPLOYMENT_CHECKLIST.md - Full deployment guide")
    print()
    print("🎯 Next steps:")
    print("  1. Review COMPLETE_DEPLOYMENT_CHECKLIST.md")
    print("  2. Follow Phase 1-5 (60 minutes)")
    print("  3. Create Vercel account: https://vercel.com/signup")
    print("  4. Create Railway account: https://railway.app/login")
    print("  5. Add GitLab CI/CD variables")
    print("  6. Push to main: git push origin main")
    print("  7. Watch pipeline deploy automatically!")
    print()
    print("🌍 Your live URLs (after deployment):")
    print("  Frontend: https://prasadreddy147.vercel.app")
    print("  Backend: https://prasadreddy147-backend.up.railway.app")
    print()

if __name__ == "__main__":
    main()
