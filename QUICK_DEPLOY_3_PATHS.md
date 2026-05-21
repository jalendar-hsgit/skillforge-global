# 🚀 ULTIMATE QUICK START - GitLab Push + FREE Deployment

## ⚡ 5-Minute Setup (Choose ONE Path)

---

## 🎯 PATH A: Push to GitLab Only (5 minutes)

**Goal**: Get code on GitLab for v1.0.0-release build pipeline

### PowerShell Commands (Copy & Paste All):

```powershell
cd "d:\python code\sfg\skillforge-global"

Write-Host "=== STEP 1: Verify Branch ===" -ForegroundColor Green
git rev-parse --abbrev-ref HEAD
# Expected: fix/api-connectivity-2026-03-15

Write-Host "`n=== STEP 2: Push Feature Branch ===" -ForegroundColor Green  
git push -u origin fix/api-connectivity-2026-03-15

Write-Host "`n=== STEP 3: Switch to Build Branch ===" -ForegroundColor Green
git checkout v1.0.0-release
git pull origin v1.0.0-release

Write-Host "`n=== STEP 4: Merge Feature Branch ===" -ForegroundColor Green
git merge fix/api-connectivity-2026-03-15 -m "Merge: API connectivity fixes (2026-03-15)"

Write-Host "`n=== STEP 5: Push to GitLab ===" -ForegroundColor Green
git push origin v1.0.0-release

Write-Host "`n✅ SUCCESS! Code on GitLab:" -ForegroundColor Green
Write-Host "  🔗 https://gitlab.com/prasad.r1342/prasad.r1342-project/-/tree/v1.0.0-release"
```

**Status**: ✅ Code pushed, ready for CI/CD pipeline!

---

## 🎯 PATH B: Push to GitLab + Deploy to Render (20 minutes)

### Step 1: Push to GitLab (Use commands from PATH A above)

```powershell
# Run all commands from PATH A first
```

### Step 2: Create Render Account (1 minute)

1. Go to: **https://render.com**
2. Click **"Sign Up"**
3. Connect with GitHub/GitLab
4. Confirm email
5. You're in! 🎉

### Step 3: Create PostgreSQL Database (2 minutes)

In Render Dashboard:

```
1. Click "New +" → "PostgreSQL"
2. Name: skillforge-db
3. Database: skillforge_app
4. Region: Pick closest to your location
5. Tier: FREE (5GB, auto-suspend)
6. CREATE DATABASE
7. 📝 Save these credentials:
   - Host: [saved-db-host]
   - Port: 5432
   - User: [saved-user]
   - Password: [saved-password]
   - Database: skillforge_app
```

### Step 4: Create Redis Instance (2 minutes)

In Render Dashboard:

```
1. Click "New +" → "Redis"
2. Name: skillforge-redis
3. Region: Same as database
4. Tier: FREE (256MB)
5. CREATE REDIS
6. 📝 Save the connection string
```

### Step 5: Deploy Backend (3 minutes)

In Render Dashboard:

```
1. Click "New +" → "Web Service"
2. Connect to GitHub/GitLab
3. Select: prasad.r1342-project
4. Name: skillforge-backend
5. Runtime: Python 3.11
6. Build command: cd backend && pip install -r requirements.txt
7. Start command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
8. Plan: FREE
9. Add environment variables:
   DATABASE_URL=postgresql://[user]:[pass]@[host]:5432/skillforge_app
   REDIS_URL=redis://[redis-connection]
   JWT_SECRET_KEY=[generate-random-string]
10. CREATE WEB SERVICE
11. Wait 5-10 minutes for deployment
12. 📝 Save the URL: https://skillforge-backend-xxx.onrender.com
```

### Step 6: Deploy Frontend (3 minutes)

In Render Dashboard:

```
1. Click "New +" → "Web Service"
2. Connect to GitHub/GitLab
3. Select: prasad.r1342-project
4. Name: skillforge-frontend
5. Runtime: Node.js
6. Build command: npm install && npm run build
7. Start command: npm start
8. Plan: FREE
9. Add environment variables:
   NEXT_PUBLIC_API_BASE=https://skillforge-backend-xxx.onrender.com
10. CREATE WEB SERVICE
11. Wait 5-10 minutes
12. 📝 Note the frontend URL
```

### Step 7: Test Deployment (1 minute)

```
1. Open your frontend URL in browser
2. Login: admin@skillforge.com / admin123
3. Check admin dashboard loads
4. Verify no console errors
5. Done! ✅
```

**Cost**: $0/month (FREE tier)  
**Status**: ✅ Live on the internet!

---

## 🎯 PATH C: Push + Deploy to Vercel (Next.js Only)

**For frontend only** (faster if you just want frontend deployed)

### Step 1: Push to GitLab (Use commands from PATH A)

### Step 2: Deploy Frontend to Vercel

```bash
# 1. Go to: https://vercel.com
# 2. Click "Add New" → "Project"
# 3. Import Git Repository
# 4. Select prasad.r1342-project
# 5. Configure:
#    Root Dir: . (current)
#    Build: npm run build
#    Install: npm install
# 6. Environment Variables:
#    NEXT_PUBLIC_API_BASE=https://your-backend-url
# 7. DEPLOY
```

**Cost**: $0/month (completely FREE)  
**Status**: ✅ Frontend deployed!

---

## 📋 Complete Setup Checklist

### GitLab Push
- [ ] Branch created: `fix/api-connectivity-2026-03-15`
- [ ] Changes committed locally
- [ ] Feature branch pushed to GitLab
- [ ] Merged to `v1.0.0-release`
- [ ] v1.0.0-release pushed to GitLab

### Render Deployment (if PATH B)
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Redis instance created
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Environment variables configured
- [ ] Tested in browser

### URLs (Save These)
```
🔗 GitLab Repo: https://gitlab.com/prasad.r1342/prasad.r1342-project
🔗 v1.0.0-release: https://gitlab.com/prasad.r1342/prasad.r1342-project/-/tree/v1.0.0-release
🔗 Backend Live: https://skillforge-backend-[id].onrender.com
🔗 Frontend Live: https://skillforge-frontend-[id].onrender.com
```

---

## 🔑 Important Notes

### Login Credentials (Same in all environments)

```
Admin:
  Email: admin@skillforge.com
  Password: admin123

Superadmin:
  Email: superadmin@skillforge.com
  Password: admin123
```

### Environment Variables Reference

```
BACKEND:
- DATABASE_URL: PostgreSQL connection string
- REDIS_URL: Redis connection string
- JWT_SECRET_KEY: Generate random 32-char string
- NEXT_PUBLIC_API_BASE: Leave blank in backend

FRONTEND:
- NEXT_PUBLIC_API_BASE: https://your-backend-url.onrender.com
```

### Database Connection String Format

```
PostgreSQL (Render):
postgresql://[username]:[password]@[host]:[port]/[database]

Example:
postgresql://admin:abc123@dpg-xyz.onrender.com:5432/skillforge_app

Redis (Render):
redis://:password@[host]:[port]
```

---

## 🎯 Quick Decision Tree

**I want to...**

| Goal | Time | Path | Cost |
|------|------|------|------|
| Push code to GitLab for build | 5 min | PATH A | FREE |
| Push code + get live demo | 20 min | PATH B | FREE |
| Deploy frontend only, fast | 10 min | PATH C | FREE |
| Deploy everything properly | 1 hour | PATH B + monitoring | FREE |
| Production-grade setup | 2 hours | AWS/GCP guide | Varies |

---

## ⚡ One-Command Deploy (PowerShell)

**If using PATH A (GitLab only)**:

```powershell
cd "d:\python code\sfg\skillforge-global"; `
git checkout fix/api-connectivity-2026-03-15; `
git push -u origin fix/api-connectivity-2026-03-15; `
git checkout v1.0.0-release; `
git pull origin v1.0.0-release; `
git merge fix/api-connectivity-2026-03-15 -m "merge: api fixes"; `
git push origin v1.0.0-release; `
Write-Host "`n✅ Pushed to GitLab v1.0.0-release!" -ForegroundColor Green
```

---

## 🆘 Common Issues & Solutions

### "Connection refused" on Render

**Solution**:
```
1. Check PostgreSQL database is running (Dashboard → Activity)
2. Verify DATABASE_URL environment variable
3. Check firewall allows connections
4. Restart service: Dashboard → [service] → Restart
```

### "NEXT_PUBLIC_API_BASE not set"

**Solution**:
```
1. Frontend needs env variable: NEXT_PUBLIC_API_BASE
2. Must include https:// or http://
3. Value: https://your-backend.onrender.com
```

### "Frontend can't reach backend API"

**Solution**:
```
1. Check backend is running: curl https://your-backend-url/healthz
2. Verify NEXT_PUBLIC_API_BASE is correct
3. Check CORS is enabled in backend
4. Browser console (F12) → Network → See actual error
```

---

## 📊 Free Tier Limits

| Service | Limit | Notes |
|---------|-------|-------|
| Render Backend | 1 free web service | Can upgrade later |
| Render DB | 5 GB storage | Auto-suspend after 15 min inactivity |
| Render Redis | 256 MB | Enough for most apps |
| GitHub Actions | 2000 min/month | Per account |
| Vercel | Unlimited deployments | Free tier only |

---

## 🚀 Next Steps After Deployment

1. **Share the live URL**: Send frontend URL to team
2. **Monitor logs**: Click "Logs" in Render dashboard
3. **Upgrade when needed**: Render → Upgrade to paid plan
4. **Add monitoring**: See CI_CD_PIPELINE_SETUP.md for options
5. **Setup domain**: Connect custom domain in Render settings

---

## 📞 Quick Support

**GitLab Issues**:
→ Check GITLAB_PUSH_COMMANDS.md

**Render Issues**:
→ Go to Render → [Your Service] → Logs

**Deployment Issues**:
→ Check FREE_DEPLOYMENT_GUIDE.md

**API Issues**:
→ Check START_HERE_API_FIX_COMPLETE.md

---

## ✅ Success = Done!

When you see this, you're done:

```
✅ Code on GitLab: https://gitlab.com/prasad.r1342/prasad.r1342-project
✅ Backend Live: https://skillforge-backend-xyz.onrender.com/healthz → 200
✅ Frontend Live: https://skillforge-frontend-xyz.onrender.com → Loads
✅ Login Works: admin@skillforge.com / admin123 → Logged in
```

---

**Choose your path above and follow the steps!**  
**You've got this! 🎉**

Generated: March 15, 2026
