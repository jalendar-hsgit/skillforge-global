# QUICK COMMAND REFERENCE - SKILLFORGE GLOBAL
**For:** Copy-paste commands for quick execution  
**Version:** 1.0  
**Last Updated:** December 30, 2025

---

## 🚀 START HERE - First Things First

### Verify Build Works (5 minutes)
```bash
# Navigate to project root
cd "d:\python code\sfg\skillforge-global"

# Run production build
npm run build

# Expected: ✓ Compiled successfully after ~30 seconds
# Check for: "✓ Generating static pages"
```

### Start Both Servers (5 minutes)

**Terminal 1: Frontend**
```bash
cd "d:\python code\sfg\skillforge-global"
npm run dev

# Expected output: 
# - ▲ Next.js 14.2.33
# - ready - started server on 0.0.0.0:3000
```

**Terminal 2: Backend**
```bash
cd "d:\python code\sfg\skillforge-global\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Expected output:
# - INFO:     Application startup complete
# - Uvicorn running on http://0.0.0.0:8001
```

**Terminal 3: Test (after both are running)**
```bash
# Quick connectivity test
curl http://localhost:3001

# Should NOT show error - frontend is up
curl http://localhost:8001/docs

# Should show Swagger UI - backend is up
```

---

## 🧪 TEST THE SYSTEM (20 minutes)

### Quick 5-Endpoint Smoke Test
```bash
# Test 1: Login and save token
$token = ((curl -X POST http://localhost:8001/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"john.doe@example.com","password":"john123"}' | ConvertFrom-Json).access_token)

echo "Token saved: $token"

# Test 2: Get courses (requires token)
curl -X GET http://localhost:8001/api/v1/courses `
  -H "Authorization: Bearer $token"

# Test 3: Get mentors
curl -X GET http://localhost:8001/api/v1x/mentors `
  -H "Authorization: Bearer $token"

# Test 4: Get quizzes
curl -X GET http://localhost:8001/api/v1x/quizzes `
  -H "Authorization: Bearer $token"

# Test 5: Admin dashboard (use admin token)
$adminToken = ((curl -X POST http://localhost:8001/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@skillforge.com","password":"admin123"}' | ConvertFrom-Json).access_token)

curl -X GET http://localhost:8001/api/v1x/admin/dashboard `
  -H "Authorization: Bearer $adminToken"
```

### Database Health Check
```bash
# Connect to database
cd "d:\python code\sfg\skillforge-global"
sqlite3 backend/app/data/skillforge.db

# Then run these commands:
SELECT COUNT(*) as table_count FROM sqlite_master WHERE type='table';
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as course_count FROM courses;
SELECT COUNT(*) as mentor_count FROM mentors;
SELECT COUNT(*) as quiz_count FROM quizzes;

# Exit SQLite
.quit
```

---

## 🔑 TEST CREDENTIALS

### Test Users (Copy-Paste)
```json
{
  "regular_user": {
    "email": "john.doe@example.com",
    "password": "john123"
  },
  "mentor": {
    "email": "mentor.sarah@skillforge.com",
    "password": "mentor123"
  },
  "admin": {
    "email": "admin@skillforge.com",
    "password": "admin123"
  },
  "superadmin": {
    "email": "superadmin@skillforge.com",
    "password": "superadmin123"
  }
}
```

### Get JWT Token for Testing
```bash
# For regular user
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"john123"}'

# For admin
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@skillforge.com","password":"admin123"}'

# Save the access_token from response and use as:
# -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 20 CRITICAL ENDPOINT TESTS (Use in Postman or curl)

### 1. Health Check
```bash
curl http://localhost:8001/docs
```

### 2. Signup
```bash
curl -X POST http://localhost:8001/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"Test123!","password_confirm":"Test123!"}'
```

### 3. Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"john123"}'
```

### 4. Get Current User
```bash
curl http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get Courses
```bash
curl http://localhost:8001/api/v1/courses \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Get Single Course
```bash
curl http://localhost:8001/api/v1/courses/python-fundamentals \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Get Quizzes
```bash
curl "http://localhost:8001/api/v1x/quizzes?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Get Mentors
```bash
curl "http://localhost:8001/api/v1x/mentors?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 9. Create Quiz Session
```bash
curl -X POST http://localhost:8001/api/v1x/quizzes/1/sessions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quiz_id": 1}'
```

### 10. Get Mentor Sessions
```bash
curl "http://localhost:8001/api/v1x/mentor-sessions?status=PENDING" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 11. Get Resumes
```bash
curl http://localhost:8001/api/v1x/resumes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 12. Create Resume
```bash
curl -X POST http://localhost:8001/api/v1x/resumes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Resume",
    "content": {
      "personal": {"name": "John", "email": "john@test.com"},
      "summary": "Experienced developer"
    }
  }'
```

### 13. Get Job Applications
```bash
curl "http://localhost:8001/api/v1x/job-applications?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 14. Create Job Application
```bash
curl -X POST http://localhost:8001/api/v1x/job-applications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "position_title": "Backend Developer",
    "application_date": "2025-12-30"
  }'
```

### 15. Admin Dashboard
```bash
curl http://localhost:8001/api/v1x/admin/dashboard \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 16. Get Users (Admin)
```bash
curl "http://localhost:8001/api/v1x/admin/users?skip=0&limit=10" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 17. Get Coins Balance
```bash
curl http://localhost:8001/api/v1x/coins/balance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 18. Get Leaderboard
```bash
curl "http://localhost:8001/api/v1x/leaderboard?period=monthly" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 19. Get Notifications
```bash
curl "http://localhost:8001/api/v1x/notifications?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 20. Database Health Check
```bash
cd "d:\python code\sfg\skillforge-global"
sqlite3 backend/app/data/skillforge.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';"
```

---

## 🔧 COMMON DEVELOPMENT COMMANDS

### Frontend Development
```bash
cd "d:\python code\sfg\skillforge-global"

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Type check
npm run lint

# Format code
npm run format
```

### Backend Development
```bash
cd "d:\python code\sfg\skillforge-global\backend"

# Install dependencies
pip install -r requirements.txt

# Run dev server with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Run production server
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Check dependencies
pip list

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Database Commands
```bash
cd "d:\python code\sfg\skillforge-global"

# Connect to database
sqlite3 backend/app/data/skillforge.db

# Inside SQLite:
# List all tables
.tables

# Show table schema
.schema users

# Count records
SELECT COUNT(*) FROM users;

# Backup database
cp backend/app/data/skillforge.db backend/app/data/skillforge_backup_$(date +%s).db

# Exit SQLite
.quit
```

---

## 🚀 DEPLOYMENT QUICK COMMANDS

### Before Production Deployment
```bash
# 1. Verify build
npm run build

# 2. Backup database
cp backend/app/data/skillforge.db backend/app/data/skillforge_backup.db

# 3. Create production env files
# Create backend/.env with production values
# Create .env.local with production API_BASE

# 4. Install production dependencies
pip install -r backend/requirements.txt
npm install --production

# 5. Test production build
npm run build
npm run start
```

### Deploy to VPS (Example)
```bash
# 1. SSH into VPS
ssh user@your-vps.com

# 2. Clone repository
git clone https://github.com/yourname/skillforge-global.git
cd skillforge-global

# 3. Setup backend
cd backend
pip install -r requirements.txt
nohup gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001 &

# 4. Setup frontend
cd ..
npm install
npm run build
nohup npm run start &

# 5. Setup Nginx (see NEXT_IMPLEMENTATION_PLAN.md for full config)
sudo systemctl start nginx
sudo systemctl enable nginx

# 6. Setup SSL (Let's Encrypt)
sudo certbot certonly --standalone -d skillforge.com
sudo systemctl restart nginx
```

### Deploy with Docker
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

---

## 🐛 DEBUGGING COMMANDS

### Check if Ports Are Available
```bash
# Windows PowerShell
netstat -ano | findstr :3001
netstat -ano | findstr :8001

# If port is in use, kill the process
taskkill /PID 12345 /F
```

### Check Node Processes
```bash
# List all Node processes
tasklist | findstr node

# Kill Node process
taskkill /F /IM node.exe
```

### View Logs
```bash
# Frontend dev logs (visible in terminal where npm run dev runs)
# Backend logs (visible in terminal where uvicorn runs)

# Production logs (if using PM2)
pm2 logs

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Check Database Integrity
```bash
cd "d:\python code\sfg\skillforge-global"
sqlite3 backend/app/data/skillforge.db

# Inside SQLite:
PRAGMA integrity_check;  # Run integrity check
.tables                  # List all tables
SELECT COUNT(*) FROM sqlite_master WHERE type='table';  # Count tables
SELECT COUNT(*) FROM users;  # Count users
.quit
```

---

## 📋 DAILY CHECKLIST

### Morning (Start of Day)
```bash
# 1. Verify code hasn't changed unexpectedly
git status

# 2. Pull latest changes
git pull origin main

# 3. Install any new dependencies
npm install
pip install -r backend/requirements.txt

# 4. Start servers
# Terminal 1: npm run dev
# Terminal 2: python -m uvicorn app.main:app --reload

# 5. Verify system is up
curl http://localhost:3001
curl http://localhost:8001/docs
```

### Before Pushing Code
```bash
# 1. Run type check
npm run lint

# 2. Run tests (if available)
npm run test

# 3. Verify build still works
npm run build

# 4. Check for TypeScript errors
npx tsc --noEmit

# 5. Commit and push
git add .
git commit -m "Your commit message"
git push origin main
```

---

## 🎯 TESTING WORKFLOW

### Full Test Suite (Recommended Before Deployment)
```bash
# 1. Start fresh
npm run build
rm -rf .next node_modules  # Windows: rmdir /s /q .next node_modules

# 2. Reinstall
npm install
npm run build

# 3. Test both servers start
npm run dev  # Terminal 1
python -m uvicorn app.main:app --reload  # Terminal 2

# 4. Run API tests
# Use IMMEDIATE_ACTION_PLAN.md for full test sequence

# 5. Check database
sqlite3 backend/app/data/skillforge.db "SELECT COUNT(*) FROM users;"

# 6. Verify build succeeds
npm run build
```

---

## 💾 BACKUP & RESTORE

### Backup Database
```bash
# Create backup with timestamp
cd "d:\python code\sfg\skillforge-global"
cp backend/app/data/skillforge.db "backend/app/data/skillforge_backup_$(date +%Y%m%d_%H%M%S).db"

# List backups
ls -la backend/app/data/skillforge_backup_*
```

### Restore from Backup
```bash
# Stop services first!
pm2 stop all

# Restore backup
cd "d:\python code\sfg\skillforge-global"
cp backend/app/data/skillforge_backup_YYYYMMDD_HHMMSS.db backend/app/data/skillforge.db

# Restart services
pm2 start all

# Verify
sqlite3 backend/app/data/skillforge.db "SELECT COUNT(*) FROM users;"
```

---

## 📞 QUICK REFERENCE LINKS

### Local Development
```
Frontend Dev:  http://localhost:3001
Frontend UI:   http://localhost:3001 (click around)
Backend API:   http://localhost:8001
API Docs:      http://localhost:8001/docs
Swagger UI:    http://localhost:8001/swagger
ReDoc:         http://localhost:8001/redoc
OpenAPI JSON:  http://localhost:8001/openapi.json
```

### Key Files
```
Frontend: 
- Next.js config: next.config.js
- Environment: .env.local
- API client: src/lib/api.ts
- Home page: src/pages/index.tsx

Backend:
- Entry point: backend/app/main.py
- Models: backend/app/models/, backend/app/modelsx/
- Routers: backend/app/api/v1x/
- Database: backend/app/data/skillforge.db
```

---

## ⚡ MOST IMPORTANT COMMANDS

If you only run 3 commands:

```bash
# 1. Verify build works
npm run build

# 2. Start both servers
npm run dev  # Terminal 1
python -m uvicorn app.main:app --reload  # Terminal 2

# 3. Run smoke tests
# See "20 CRITICAL ENDPOINT TESTS" section above
```

---

**Last Updated:** December 30, 2025  
**Next:** Go to IMMEDIATE_ACTION_PLAN.md for tasks
