# Local Docker Build & Deploy Guide

**Environment:** Local Development  
**Date:** March 12, 2026  
**Estimated Time:** 10-15 minutes

---

## 📋 prerequisites

### System Requirements
- **Docker Desktop:** Latest version installed ([Download here](https://www.docker.com/products/docker-desktop))
- **Docker Compose:** Included with Docker Desktop v20.10+
- **Git:** For cloning repository
- **Disk Space:** 10GB free (for images and volumes)
- **RAM:** 4GB minimum (8GB recommended)

### Verify Installation
```bash
# Check Docker
docker --version
# Output: Docker version 24.x.x or higher

# Check Docker Compose
docker-compose --version
# Output: Docker Compose version 2.x.x or higher

# Check both working
docker run hello-world
```

---

## 🚀 QUICK START (3 Steps)

### Step 1: Navigate to Project Directory
```bash
cd d:\python code\sfg\skillforge-global
# Or wherever your project is

# Verify you see docker-compose.yml
ls docker-compose.yml
```

### Step 2: Start All Services
```bash
# Start in background mode
docker-compose up -d

# Or start in foreground (see all logs)
docker-compose up

# Press Ctrl+C to stop (if foreground mode)
```

### Step 3: Access the Application
```
Frontend:  http://localhost:3000
Backend:   http://localhost:8001
Database:  localhost:5432
Adminer:   http://localhost:8080 (Database UI)
```

**That's it! Your application is running! 🎉**

---

## 📦 COMPLETE DOCKER SETUP PROCESS

### Phase 1: Prepare Environment (2 minutes)

**Task 1.1: Navigate to Project**
```bash
cd d:\python code\sfg\skillforge-global
```

**Task 1.2: Check Docker is Running**
```bash
# Windows PowerShell
docker ps

# Should show: (empty or running containers, no errors)
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

**Task 1.3: Create Environment Files (if needed)**
```bash
# Create .env.local for frontend
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_BASE=http://localhost:8001
NEXT_PUBLIC_STRIPE_KEY=pk_test_51234567890abcdefg
EOF

# Create backend environment (docker-compose handles this)
# But you can create for reference:
cat > backend/.env.local << 'EOF'
DATABASE_URL=postgresql://admin:skillforge_dev_password@postgres:5432/skillforge
STRIPE_SECRET_KEY=sk_test_your_test_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key_here
JWT_SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8001
ENVIRONMENT=development
LOG_LEVEL=DEBUG
EOF
```

---

### Phase 2: Build Docker Images (5-10 minutes)

**Task 2.1: Build Backend Image**
```bash
# Build backend image
docker build -f Dockerfile.backend -t skillforge-backend:latest .

# After build, verify:
docker images | grep skillforge-backend

# Output should show:
# REPOSITORY              TAG       IMAGE ID      CREATED      SIZE
# skillforge-backend      latest    abc123def456  2 minutes    450MB
```

**Task 2.2: Build Frontend Image**
```bash
# Build frontend image
docker build -f Dockerfile.frontend -t skillforge-frontend:latest .

# Verify:
docker images | grep skillforge-frontend

# Output should show both images
```

**Task 2.3: Verify Both Images Built**
```bash
# List all SkillForge images
docker images | grep skillforge

# Should show:
skillforge-backend    latest    ...    450MB
skillforge-frontend   latest    ...    350MB
```

---

### Phase 3: Start Services with Docker Compose (3 minutes)

**Task 3.1: Start All Services**
```bash
# Start containers in background
docker-compose up -d

# Output:
# [+] Running 7/7
#  ⠿ Network skillforge-global_skillforge-network  Created
#  ⠿ Container skillforge-postgres               Started
#  ⠿ Container skillforge-redis                  Started
#  ⠿ Container skillforge-backend                Started
#  ⠿ Container skillforge-frontend               Started
#  ⠿ Container skillforge-adminer                Started
#  ⠿ Container skillforge-pgadmin                Started
```

**Task 3.2: Verify All Containers Running**
```bash
# Check status
docker-compose ps

# Should show all containers in "running" state:
NAME                    COMMAND              STATUS      PORTS
skillforge-postgres     postgres             Up 1 min    5432/tcp
skillforge-redis        redis-server         Up 1 min    6379/tcp
skillforge-backend      uvicorn app.main    Up 1 min    8001/tcp
skillforge-frontend     npm start            Up 1 min    3000/tcp
skillforge-adminer      adminer              Up 1 min    8080/tcp
skillforge-pgadmin      /entrypoint.sh       Up 1 min    5050/tcp
```

**If any container failed:**
```bash
# Check logs for specific container
docker-compose logs backend

# Or see full logs
docker-compose logs

# Try restarting
docker-compose restart
```

---

### Phase 4: Access & Test Services (2 minutes)

**Task 4.1: Test Backend API**
```bash
# Option 1: Using PowerShell curl
curl http://localhost:8001/api/v1/health

# Should return: 200 OK with response like:
# {"status":"healthy"}

# Option 2: Using browser
# Visit: http://localhost:8001/api/v1/health
```

**Task 4.2: Test Frontend**
```bash
# Visit in browser
http://localhost:3000

# Should see:
# - SkillForge logo
# - Navigation menu
# - Marketplace courses
# - Login/Register buttons
```

**Task 4.3: Test Database Admin UIs**
```bash
# Adminer (simple database UI)
http://localhost:8080

# Login details:
# System: PostgreSQL
# Server: postgres
# Username: admin
# Password: skillforge_dev_password (from docker-compose.yml)
# Database: skillforge

# pgAdmin (advanced database UI)
http://localhost:5050

# Login details:
# Email: admin@skillforge.com
# Password: admin (from docker-compose.yml)
```

---

### Phase 5: Initialize Database (3 minutes)

**Task 5.1: Seed Demo Data**
```bash
# Run seed script inside backend container
docker-compose exec backend python seed_all_demo_data.py

# Output should show:
# Creating demo users...
# Creating demo mentors...
# Creating demo courses...
# Creating demo jobs...
# Creating demo products...
# Creating demo sessions...
# Seed complete!

# Check what was created:
docker-compose exec backend python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.modelsx.course import Course

engine = create_engine('postgresql://admin:skillforge_dev_password@postgres:5432/skillforge')
Session = sessionmaker(bind=engine)
session = Session()

courses = session.query(Course).all()
print(f'Total courses: {len(courses)}')
for course in courses:
    print(f'  - {course.title}')
"
```

**Expected Output:**
```
Total courses: 5
  - Python Fundamentals
  - Web Development Bootcamp
  - Advanced React & Next.js
  - Machine Learning Masterclass
  - DevOps Essentials
```

**Task 5.2: Verify Database**
```bash
# Connect to PostgreSQL directly
docker-compose exec postgres psql -U admin -d skillforge -c "SELECT COUNT(*) as total_users FROM users;"

# Should show: 7 users (2 admins + 5 regular users)

# Check courses
docker-compose exec postgres psql -U admin -d skillforge -c "SELECT title, price FROM marketplace_courses LIMIT 5;"

# Should show 5 courses with prices
```

---

## 🧪 TEST THE APPLICATION

### Test User Registration
```bash
# Register new user
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"testuser@skillforge.com",
    "password":"TestPassword123!",
    "name":"Test User"
  }'

# Should return 201 Created with user details
```

### Test Login
```bash
# Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"testuser@skillforge.com",
    "password":"TestPassword123!"
  }'

# Should return access token
```

### Test Marketplace API
```bash
# Get courses
curl http://localhost:8001/api/v1x/marketplace/courses

# Should return array of 5 courses

# Get specific course
curl http://localhost:8001/api/v1x/marketplace/courses/1

# Should return course details with title, price, etc.
```

### Test Using Browser
```
1. Visit http://localhost:3000
2. Click "Register" or "Login"
3. Create account or login with demo user:
   - Email: john.doe@example.com
   - Password: password (demo account)
4. Navigate to "Marketplace"
5. Should see 5 courses
6. Add course to cart
7. Test checkout (use Stripe test card: 4242 4242 4242 4242)
```

---

## 📊 USEFUL DOCKER COMMANDS

### View Container Status
```bash
# See all running containers
docker-compose ps

# See all containers (including stopped)
docker-compose ps -a

# Get detailed container info
docker-compose logs                    # All logs
docker-compose logs backend            # Backend logs only
docker-compose logs frontend           # Frontend logs only
docker-compose logs postgres           # Database logs
docker-compose logs -f backend         # Follow backend logs in real-time
docker-compose logs -f --tail=100      # Last 100 lines, follow changes
```

### Stop/Start Services
```bash
# Stop all containers
docker-compose down

# Stop specific container
docker-compose stop backend

# Start specific container
docker-compose start backend

# Restart all
docker-compose restart

# Restart specific
docker-compose restart backend

# Remove all containers (keeps data)
docker-compose down

# Remove all containers AND volumes (deletes all data)
docker-compose down -v
```

### Execute Commands in Containers
```bash
# Run commands in backend
docker-compose exec backend python seed_all_demo_data.py
docker-compose exec backend bash

# Run commands in frontend
docker-compose exec frontend npm list
docker-compose exec frontend bash

# Run database commands
docker-compose exec postgres psql -U admin -d skillforge -c "SELECT * FROM users LIMIT 5;"
```

### View Real-Time Logs
```bash
# All services at once
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last N lines
docker-compose logs --tail=50

# Specific time range
docker-compose logs --since 2024-03-11T12:00:00
```

### Database Operations
```bash
# Access PostgreSQL directly
docker-compose exec postgres psql -U admin -d skillforge

# Common queries:
# \dt                                    (list tables)
# SELECT * FROM users;                   (show users)
# SELECT COUNT(*) FROM marketplace_courses;  (count courses)
# \q                                     (exit)

# Dump database
docker-compose exec postgres pg_dump -U admin skillforge > backup.sql

# Restore database
docker-compose exec -T postgres psql -U admin skillforge < backup.sql
```

---

## 🔧 TROUBLESHOOTING LOCAL DOCKER

### "Port already in use" Error
```bash
# Find what's using the port (Windows PowerShell)
netstat -ano | findstr :3000
netstat -ano | findstr :8001
netstat -ano | findstr :5432

# Kill the process using port (Windows)
taskkill /PID 12345 /F

# Or change docker-compose port mapping:
# Edit docker-compose.yml, change "3000:3000" to "3001:3000"
```

### "Cannot connect to database" Error
```bash
# Make sure postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Wait 10 seconds for startup
docker-compose logs postgres | grep "listening on"
```

### "Frontend won't load" Error
```bash
# Check frontend is running
docker-compose ps frontend

# Check frontend logs
docker-compose logs frontend

# Make sure backend is running
curl http://localhost:8001/api/v1/health

# Clear browser cache (Ctrl+Shift+Delete)
# Then refresh page
```

### "API returns 404" Error
```bash
# Make sure backend is running
docker-compose logs backend

# Check if service is listening
curl http://localhost:8001/api/v1/health

# Restart backend
docker-compose restart backend

# Wait for startup
sleep 5

# Try again
curl http://localhost:8001/api/v1/health
```

### Container keeps restarting
```bash
# Check logs for reason
docker-compose logs backend

# Common issues:
# - Missing environment variables
# - Port already in use
# - Database connection failed
# - Disk space full

# Rebuild image
docker-compose down
docker build -f Dockerfile.backend -t skillforge-backend:latest .
docker-compose up -d
```

### Out of Disk Space
```bash
# Clean up Docker
docker system prune -a      # Remove all unused images/containers
docker volume prune         # Remove unused volumes
docker container prune      # Remove stopped containers

# Check disk usage
docker system df

# See image sizes
docker images --format "{{.Repository}}\t{{.Size}}"
```

---

## 📝 DEVELOPMENT WORKFLOW

### Daily Development Cycle

**Morning: Start Services**
```bash
cd d:\python code\sfg\skillforge-global
docker-compose up -d
# Check all running
docker-compose ps
```

**During Development: Make Changes**
```bash
# Edit backend code (will auto-reload in container)
# Edit src/pages/marketplace/index.tsx (will hot reload)

# View real-time logs
docker-compose logs -f backend
```

**Testing: Run Tests**
```bash
# Backend tests
docker-compose exec backend pytest tests/ -v

# Frontend tests
docker-compose exec frontend npm test
```

**Check Data: View Database**
```bash
# Visit Adminer
http://localhost:8080

# Or use psql
docker-compose exec postgres psql -U admin -d skillforge
```

**End of Day: Stop Services**
```bash
# Keep data (containers stopped but volumes persist)
docker-compose stop

# Or completely remove (data stays in volumes)
docker-compose down

# Next day: restart
docker-compose up -d
```

---

## 🔄 RESET & REBUILD

### Reset Everything (Clean Slate)
```bash
# Stop everything and remove volumes
docker-compose down -v

# Rebuild images from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Seed data
docker-compose exec backend python seed_all_demo_data.py
```

### Just Update Backend Code
```bash
# If you modified backend code:
docker-compose exec backend pip install -r requirements.txt
docker-compose restart backend

# Or rebuild container:
docker-compose build backend
docker-compose up -d backend
```

### Just Update Frontend Code
```bash
# If you modified frontend code (hot reload usually handles it):
# Usually no action needed - Next.js rebuilds automatically

# If needed, rebuild:
docker-compose build frontend
docker-compose up -d frontend
```

---

## 📊 DOCKER-COMPOSE.YML OVERVIEW

The `docker-compose.yml` file defines 7 services:

```yaml
Services:
├── postgres         # PostgreSQL database (port 5432)
├── redis            # Redis cache (port 6379)
├── backend          # FastAPI backend (port 8001)
│                    # auto-runs: python init_db.py + seed_all_demo_data.py
├── frontend         # Next.js frontend (port 3000)
├── adminer          # Database UI (port 8080)
├── pgadmin          # Advanced DB UI (port 5050)
└── [optional]       # Elasticsearch, monitoring, etc.

Volumes:
├── postgres_data    # Persistent database storage
├── ./backend        # Backend code (hot reload)
├── ./src            # Frontend code (hot reload)
└── ./public         # Static files

Networks:
└── skillforge-network  # Internal Docker network
```

---

## ✅ VERIFICATION CHECKLIST

After starting Docker, verify everything:

```bash
# ✓ All containers running
docker-compose ps
# All should show "Up" status

# ✓ Backend API responding
curl http://localhost:8001/api/v1/health
# Should return: {"status":"healthy"}

# ✓ Frontend loads
# Visit http://localhost:3000 in browser
# Should see website

# ✓ Database has data
curl http://localhost:8001/api/v1x/marketplace/courses
# Should return array with 5 courses

# ✓ Can access database
http://localhost:8080
# Should load Adminer admin panel

# ✓ Advanced DB UI
http://localhost:5050
# Should load pgAdmin
```

**If all checks pass: ✅ You're ready to develop!**

---

## 🛑 STOP & CLEANUP

### Stop Services (Keep Data)
```bash
# Stop all containers (data persists)
docker-compose stop

# Next time, start with:
docker-compose start
# or
docker-compose up -d
```

### Clean Up Everything
```bash
# Remove containers, networks (keep volumes)
docker-compose down

# Remove containers AND data volumes
docker-compose down -v

# Remove all unused Docker resources
docker system prune -a
```

---

## 📈 MONITORING & PERFORMANCE

### Monitor Resource Usage
```bash
# Real-time resource stats for all containers
docker stats

# Or specific container:
docker stats skillforge-backend

# Shows:
# CONTAINER          CPU %     MEM USAGE / LIMIT
# skillforge-backend 2.5%      250MB / 1GB
# skillforge-frontend 1.2%    180MB / 1GB
```

### Check Container Health
```bash
# See if containers are healthy
docker-compose ps

# Check specific container
docker-compose exec backend curl http://localhost:8001/api/v1/health

# View container health status
docker ps --format "{{.Names}}\t{{.Status}}"
```

### View Recent Logs
```bash
# Last 50 lines
docker-compose logs --tail=50

# Last 30 minutes of logs
docker-compose logs --since 30m

# Between timestamps
docker-compose logs --since 2024-03-12T10:00:00 --until 2024-03-12T11:00:00
```

---

## 🎯 COMMON DEVELOPMENT TASKS

### Add a New Course via API
```bash
# Create new course
curl -X POST http://localhost:8001/api/v1x/admin/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "path": "new-course",
    "title": "New Course",
    "description": "Course description",
    "difficulty_level": "Intermediate",
    "is_paid": true,
    "price": 99.99
  }'
```

### Test Payment (Use Stripe Test Card)
```
Card Number: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123
```

### Debug Backend Issues
```bash
# Get full traceback
docker-compose logs backend | tail -100

# Run shell in container
docker-compose exec backend bash

# Then run Python directly:
python
>>> from app.main import app
>>> # test code here
```

### Profile Performance
```bash
# Time an API call
time curl http://localhost:8001/api/v1x/marketplace/courses

# Monitor database during load
docker-compose exec postgres psql -U admin -d skillforge
# Then in psql:
# SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

---

## 📚 QUICK REFERENCE

```bash
# START
docker-compose up -d

# STOP
docker-compose down

# LOGS
docker-compose logs -f

# DATABASE ACCESS
http://localhost:8080              # Adminer
http://localhost:5050              # pgAdmin

# APPLICATION
http://localhost:3000              # Frontend
http://localhost:8001/api/v1/health # Backend health

# COMMON COMMANDS
docker-compose ps                  # Status
docker-compose logs backend        # Backend logs
docker-compose exec backend bash   # Backend shell
docker-compose restart backend     # Restart service
docker-compose down -v             # Clean everything
```

---

## 🎉 CONGRATULATIONS!

Your local Docker development environment is ready!

**You can now:**
- ✅ Develop locally with hot reload
- ✅ Test backend API
- ✅ Test frontend
- ✅ Access database with UI
- ✅ Run tests
- ✅ Deploy to AWS when ready

**Next Steps:**
1. Start docker: `docker-compose up -d`
2. Visit http://localhost:3000
3. Register/login
4. Test marketplace
5. Test payments (use test card)
6. View backend logs: `docker-compose logs -f backend`

---

**Happy developing! 🚀**

For AWS deployment, see: [AWS_SETUP_STEP_BY_STEP.md](AWS_SETUP_STEP_BY_STEP.md)
