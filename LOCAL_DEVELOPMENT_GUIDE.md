# LOCAL DEVELOPMENT WORKFLOW GUIDE

## Quick Start (TL;DR)

```bash
# First time setup
git clone <repo>
cd skillforge-global
docker-compose up -d --build

# Wait ~3-5 minutes for containers to initialize
# Then open browser:
http://localhost:3000    # Frontend
http://localhost:8001    # Backend API
http://localhost:8080    # Adminer (SQL viewer)
http://localhost:5050    # pgAdmin (SQL GUI)

# Done! Start coding
```

---

## 1. INITIAL SETUP

### Minimum Requirements
- **OS**: Windows 10/11, Mac, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 10GB free
- **Software**: Docker Desktop (https://www.docker.com/products/docker-desktop)

### Installation Steps

**1.1 Install Docker Desktop**
```bash
# Windows: Download from https://www.docker.com/products/docker-desktop
# Run installer, accept defaults
# Restart computer

# Verify installation:
docker --version
# Output: Docker version 24.0.0, build abcd1234
```

**1.2 Clone Repository**
```bash
git clone https://github.com/yourusername/skillforge-global.git
cd skillforge-global
```

**1.3 Create .env File (Optional - has defaults)**
```bash
# Copy example (if exists)
cp .env.example .env

# Or create manually in root directory:
# skillforge-global/.env

POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
POSTGRES_DB=skillforge

JWT_SECRET_KEY=your-very-secret-key-here-min-32-chars
STRIPE_SECRET_KEY=sk_test_REPLACE_ME (get from Stripe)
STRIPE_PUBLIC_KEY=pk_test_xxxxx

REDIS_PASSWORD=
DATABASE_URL=postgresql://admin:admin123@postgres:5432/skillforge
REDIS_URL=redis://redis:6379
```

**1.4 Start Docker Containers**
```bash
# Navigate to project root
cd skillforge-global

# Start all services (build + run)
docker-compose up -d --build

# This takes 3-5 minutes first time (downloads images, installs deps)
# Subsequent starts take 30-60 seconds

# Watch the startup process
docker-compose logs -f backend

# Once you see "Application startup complete", backend is ready
# Press Ctrl+C to exit logs
```

---

## 2. VERIFY SETUP

### Check All Services Running

```bash
# List containers
docker-compose ps

# Output should show:
# NAME                    STATUS         PORTS
# skillforge-frontend     Up (healthy)   0.0.0.0:3000->3000/tcp
# skillforge-backend      Up (healthy)   0.0.0.0:8001->8001/tcp
# skillforge-postgres     Up (healthy)   0.0.0.0:5432->5432/tcp
# skillforge-redis        Up (healthy)   0.0.0.0:6379->6379/tcp
# skillforge-adminer      Up (healthy)   0.0.0.0:8080->8080/tcp
# skillforge-pgadmin      Up (healthy)   0.0.0.0:5050->5050/tcp
```

### Test API Endpoints

```bash
# In PowerShell or Terminal:

# Test backend health
curl http://localhost:8001/healthz
# Response: {"ok": true, "status": "healthy"}

# Test courses endpoint
curl http://localhost:8001/api/v1/courses
# Response: [{"id": 1, "title": "Python Fundamentals", ...}]

# Test mentors endpoint
curl http://localhost:8001/api/v1/mentors
# Response: [{"id": 1, "user_id": 2, "bio": "Expert in...", ...}]

# If you get 200 responses → SUCCESS ✓
# If you get 404 → Backend not fully loaded yet (wait 2 min)
# If you get connection refused → Containers not running
```

### Open Web Interfaces

```
Frontend:    http://localhost:3000        (Next.js app)
Backend API: http://localhost:8001        (FastAPI docs)
Backend API: http://localhost:8001/docs   (Swagger UI)
DB Client:   http://localhost:8080        (Adminer SQL client)
DB GUI:      http://localhost:5050        (pgAdmin - password: admin)
```

---

## 3. COMMON WORKFLOWS

### Workflow A: Frontend Changes

```bash
# 1. Make JavaScript/React changes
# Edit: src/components/YourComponent.tsx
# Edit: src/pages/dashboard.tsx

# 2. Changes auto-reload (hot module replacement)
# File saved → webpack rebuilds → browser refreshes
# No restart needed! ✓

# 3. Browser immediately shows changes
# Open DevTools (F12) to see hot reload messages

# Example: Change a button color
# src/components/Button.tsx line 15:
#   - className="bg-blue-600"
#   + className="bg-green-600"
# 
# Save file → Browser updates within 1 second
```

### Workflow B: Backend API Changes

```bash
# 1. Make Python/FastAPI changes
# Edit: backend/app/api/v1/courses.py
# Edit: backend/app/schemas/course.py

# 2. Backend auto-reloads (uvicorn with --reload)
# File saved → Python reloads module → API available
# No container restart needed! ✓

# Example: Add new endpoint
# backend/app/api/v1/courses.py:

@router.get("/featured")
async def get_featured_courses(db: Session = Depends(get_db)):
    """Get featured courses (CTRL+S to trigger reload)"""
    return db.query(Course).filter(Course.featured==True).all()

# Save → Check for errors: docker-compose logs -f backend
# Test: curl http://localhost:8001/api/v1/courses/featured
```

### Workflow C: Database Changes

#### Adding a New Column

```bash
# Problem: Database schema changed but container still running
# Solution: Database auto-creates on startup, so:

# 1. Update model in backend/app/modelsx/course.py
from sqlalchemy import Column, String, Boolean

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(2000))  # NEW LINE
    featured = Column(Boolean, default=False)  # NEW LINE

# 2. Restart backend only
docker-compose restart skillforge-backend

# 3. Watch logs for table updates
docker-compose logs -f backend | grep -i "creating\|alter\|migration"

# 4. If errors → Delete container and volume, restart
docker-compose down
docker volume rm skillforge-global_postgres_data  # WARNING: Deletes DB!
docker-compose up -d --build
```

#### Resetting Database

```bash
# Useful when "something broke, restart from scratch"

# 1. Stop all containers
docker-compose down

# 2. Delete database volume (DELETES ALL DATA!)
docker volume rm skillforge-global_postgres_data

# 3. Restart
docker-compose up -d --build

# 4. Wait for seeding complete
docker-compose logs -f backend | grep -i "seed\|complete"

# Result: Fresh database with demo data ✓
```

### Workflow D: Install New Backend Dependency

```bash
# 1. Add to requirements.txt
# backend/requirements.txt
echo "numpy==1.24.3" >> backend/requirements.txt

# 2. Rebuild backend container
docker-compose build --no-cache skillforge-backend

# 3. Restart backend
docker-compose up -d skillforge-backend

# 4. Verify installation
docker-compose exec skillforge-backend pip show numpy
# Output: Name: numpy, Version: 1.24.3

# OR test import in Python
docker-compose exec skillforge-backend python -c "import numpy; print('OK')"
```

### Workflow E: Install New Frontend Dependency

```bash
# 1. Add to package.json (from project root, NOT docker)
npm install @shadcn/ui

# 2. Rebuild frontend container
docker-compose build --no-cache skillforge-frontend

# 3. Restart frontend
docker-compose up -d skillforge-frontend

# 4. Verify installation
docker-compose exec skillforge-frontend npm list @shadcn/ui
# Output: @shadcn/ui@0.6.3

# Alternative (if npm causes issues):
rm package-lock.json
docker-compose build --no-cache skillforge-frontend
docker-compose up -d skillforge-frontend
```

### Workflow F: Debugging Backend Errors

```bash
# Problem: API returning 500 error

# 1. Check backend logs
docker-compose logs skillforge-backend -f --tail 50

# Looking for:
# - Traceback (Python error)
# - ImportError (missing module)
# - ConnectionError (database down)

# 2. Test endpoint directly in container
docker-compose exec skillforge-backend python -c "
from app.main import app
from app.database import get_db
print('Imports working!')
"

# 3. Check database connection
docker-compose exec skillforge-backend python -c "
from app.database import SessionLocal
db = SessionLocal()
result = db.execute('SELECT 1')
print('Database connected!')
"

# 4. Check Redis connection
docker-compose exec skillforge-backend python -c "
import redis
r = redis.Redis(host='redis', port=6379)
print(r.ping())  # Output: True = connected
"

# 5. Restart just the backend
docker-compose restart skillforge-backend
docker-compose logs -f skillforge-backend

# 6. If issue persists, check container health
docker-compose ps skillforge-backend
# Status should be 'Up' not 'Restarting'
```

### Workflow G: Debugging Frontend Errors

```bash
# Problem: Frontend shows blank page or error

# 1. Check browser console (F12 → Console tab)
# Look for:
# - CORS errors (API not accessible)
# - 404 errors (missing resources)
# - Connection refused (backend down)

# 2. Check frontend logs
docker-compose logs skillforge-frontend -f --tail 50

# Looking for:
# - Failed to load module
# - Build errors
# - Connection refused

# 3. Test API from frontend container
docker-compose exec skillforge-frontend curl http://backend:8001/healthz
# Response: {"ok": true, "status": "healthy"}

# 4. Check environment variables
docker-compose exec skillforge-frontend env | grep NEXT_PUBLIC

# Should show:
# NEXT_PUBLIC_API_BASE=http://backend:8001

# 5. Rebuild frontend
docker-compose build --no-cache skillforge-frontend
docker-compose up -d skillforge-frontend

# 6. Clear browser cache
# Press Ctrl+Shift+Delete → Clear cache → Reload page
# OR
# In DevTools (F12) → Application → Clear site data
```

---

## 4. DATA MANAGEMENT

### View Database in GUI

```bash
# Option 1: Adminer (simpler)
# Open: http://localhost:8080
# Login:
#   System: PostgreSQL
#   Server: postgres
#   Username: admin
#   Password: admin123
#   Database: skillforge
# Click Login → Browse tables

# Option 2: pgAdmin (more powerful)
# Open: http://localhost:5050
# Login: admin@admin.com / admin
# Register Server → New → Server
#   Name: Local PostgreSQL
#   Connection:
#     Host: postgres
#     Port: 5432
#     Username: admin
#     Password: admin123
# Save → Browse tables
```

### Query Database from Command Line

```bash
# Connect to psql
docker-compose exec skillforge-postgres psql -U admin -d skillforge

# Once inside (prompt shows "skillforge=#"):

# List all tables
\dt

# View courses
SELECT * FROM courses;

# View users
SELECT id, email, role FROM users LIMIT 10;

# View mentor sessions
SELECT * FROM mentor_sessions
WHERE status='pending'
ORDER BY scheduled_at DESC;

# Count rows
SELECT COUNT(*) FROM courses;

# Exit psql
\q
```

### Export Database Backup

```bash
# Backup entire database
docker-compose exec skillforge-postgres pg_dump -U admin skillforge > backup_$(date +%Y%m%d).sql

# Result: backup_20240115.sql file created (size: ~5-50 MB)

# Restore from backup
docker-compose exec -T skillforge-postgres psql -U admin skillforge < backup_20240115.sql

# Verify restore
docker-compose exec skillforge-postgres psql -U admin -d skillforge -c "SELECT COUNT(*) FROM courses;"
```

---

## 5. TROUBLESHOOTING COMMON ISSUES

### Issue 1: "Cannot connect to Docker daemon"

```bash
# Solution 1: Start Docker Desktop
# Open Docker Desktop application manually

# Solution 2: Check status
docker ps

# If error: "Cannot connect to Docker daemon"
# → Docker Desktop not running
# → Start it from Start Menu (Windows) or Applications (Mac/Linux)

# Solution 3: Restart Docker
# Power off: docker-compose down
# Restart Docker Desktop (close and reopen)
# Restart: docker-compose up -d
```

### Issue 2: "Port xxxxx is already allocated"

```bash
# Problem: Another service using the port

# Solution 1: Check what's using port
# Windows PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess

# Solution 2: Stop conflicting service
# Linux/Mac:
sudo lsof -i :3000
sudo kill -9 <PID>

# Solution 3: Change port mapping
# Edit docker-compose.yml
#   ports:
#     - "3000:3000"  ← Change first 3000 to 4000
#     - "4000:3000"  ← New mapping

docker-compose up -d --build
# Now access on http://localhost:4000

# Solution 4: Use different port in compose file
nano docker-compose.yml
# services:
#   frontend:
#     ports:
#       - "3001:3000"  # Host:Container
```

### Issue 3: "Out of memory" or "No space left on device"

```bash
# Problem: Docker running out of disk/memory

# Solution 1: Check disk space
df -h  # Linux/Mac
wmic logicaldisk get name,size,freespace  # Windows

# Solution 2: Clean up unused images/containers
docker-compose down -v  # Remove containers and volumes

# Solution 3: Prune Docker system
docker system prune -a --volumes
# WARNING: Deletes unused images, containers, volumes, networks

# Solution 4: Increase Docker resources
# Docker Desktop → Settings → Resources
# Memory: increase to 8GB or higher
# Disk: increase to 50GB or higher
```

### Issue 4: "Backend not responding after restart"

```bash
# Problem: Backend containers runs but API fails

# Step 1: Check logs
docker-compose logs skillforge-backend -f --tail 100

# Common errors:
# "ModuleNotFoundError: No module named 'xyz'"
#   → Solution: pip install missing package
#   → Rebuild: docker-compose build skillforge-backend

# "psycopg2.OperationalError: could not connect to server"
#   → Solution: Wait for PostgreSQL to start
#   → Check: docker-compose ps (should show postgres healthy)

# "KeyError in database"
#   → Solution: Tables not created
#   → Restart: docker-compose restart skillforge-backend

# Step 2: Restart backend only
docker-compose restart skillforge-backend
docker-compose logs -f skillforge-backend

# Step 3: Test after restart
sleep 5
curl http://localhost:8001/healthz

# Step 4: If still failing, rebuild
docker-compose build --no-cache skillforge-backend
docker-compose up -d skillforge-backend
```

### Issue 5: "Frontend shows blank page"

```bash
# Check browser console (F12 → Console)

# Error: "Failed to fetch from http://backend:8001"
#   → Backend not running
#   → Solution: docker-compose ps (verify backend healthy)
#   → Solution: Restart backend

# Error: "CORS error: No 'Access-Control-Allow-Origin' header"
#   → Backend CORS not configured properly
#   → Solution: Check backend/app/core/config.py
#   → Solution: Restart backend

# Error: "Module not found: Cannot find module 'xxxxx'"
#   → Frontend dependency missing
#   → Solution: npm install xxxxx
#   → Solution: docker-compose build skillforge-frontend

# Blank page (no errors):
#   → Clear browser cache (Ctrl+Shift+Delete)
#   → Reload (Ctrl+F5)
#   → Check if frontend container running (docker-compose ps)
```

### Issue 6: "Database migrations failing"

```bash
# Problem: "Column 'xxx' does not exist" or schema errors

# Solution 1: Check model definition
# backend/app/modelsx/course.py
# Ensure Column definitions match database

# Solution 2: Force recreate tables
docker-compose exec skillforge-backend python -c "
from app.database import engine
from app.models.base import Base

# Drop all tables
Base.metadata.drop_all(engine)

# Recreate all tables
Base.metadata.create_all(engine)

print('Tables recreated!')
"

# Solution 3: Reset database completely
docker-compose down -v
docker-compose up -d --build
docker-compose exec skillforge-backend python backend/seed_all_demo_data.py
```

---

## 6. OPTIMIZATION TIPS

### Faster Development

```bash
# 1. Use hot reload (already enabled)
# Edit code → Instant reload (no restart needed)

# 2. Use .hot-spots.json for IDE fast navigation
# Jump to frequently edited files

# 3. Keep logs separate
docker-compose logs -f backend > backend.log &
docker-compose logs -f frontend > frontend.log &
# Leaves terminal free for commands

# 4. Monitor performance
# Terminal 1: docker stats
# See real-time CPU/memory usage
```

### Faster Builds

```bash
# 1. Use --no-cache only when necessary
docker-compose build skillforge-backend

# 2. Regular build (uses cache): 30-60 seconds
# No-cache build (fresh): 3-5 minutes

# 3. Build specific service only
docker-compose build skillforge-backend
# Don't rebuild unchanged frontend

# 4. Check build cache status
docker system df
# Shows cache size and opportunities

# 5. Pre-build before big changes
docker-compose build
# Build everything while working
```

---

## 7. DEVELOPMENT BEST PRACTICES

### Before Starting Work

```bash
# 1. Update code from git
git pull origin main

# 2. Update dependencies
docker-compose build --no-cache

# 3. Restart services
docker-compose restart

# 4. Verify setup
curl http://localhost:8001/healthz
curl http://localhost:8001/api/v1/courses

# 5. Check database
docker-compose exec skillforge-postgres psql -U admin -c "SELECT COUNT(*) FROM courses;"
```

### While Developing

```bash
# 1. Keep multiple terminals open
# Terminal 1: docker-compose logs -f backend
# Terminal 2: docker-compose logs -f frontend
# Terminal 3: Regular commands

# 2. Use hot reload
# Save file → Browser/API updates automatically
# No manual restart needed

# 3. Test frequently
# After each change: curl or browser test
# Don't accumulate multiple changes

# 4. Commit often
git add .
git commit -m "Feature: Add course filtering"
git push origin feature/course-filter
```

### Before Committing

```bash
# 1. Run tests
docker-compose exec skillforge-backend pytest backend/tests/

# 2. Check code quality
docker-compose exec skillforge-backend flake8 backend/app/

# 3. Format code
docker-compose exec skillforge-backend black backend/app/

# 4. Run linter on frontend
docker-compose exec skillforge-frontend npm run lint

# 5. Fix formatting
docker-compose exec skillforge-frontend npm run lint:fix

# 6. Build production version
docker-compose build --no-cache skillforge-backend
docker-compose build --no-cache skillforge-frontend

# 7. Test in production mode
docker-compose -f docker-compose.prod.yml up -d  (if available)
```

---

## 8. USEFUL ALIASES (Save Time)

### Add to ~/.bashrc or ~/.zshrc (Mac/Linux)

```bash
# Quick commands
alias sfg-start="docker-compose up -d --build"
alias sfg-stop="docker-compose down"
alias sfg-logs-back="docker-compose logs -f backend"
alias sfg-logs-front="docker-compose logs -f frontend"
alias sfg-logs="docker-compose logs -f"
alias sfg-ps="docker-compose ps"
alias sfg-rebuild="docker-compose build --no-cache && docker-compose up -d"
alias sfg-clean="docker system prune -a --volumes"
alias sfg-reset="docker-compose down -v && docker-compose up -d --build"

# Example usage:
# $ sfg-logs-back
# $ sfg-stop
```

### Add to PowerShell Profile (Windows)

```powershell
# Open PowerShell profile
notepad $PROFILE

# Add functions
function sfg-start { docker-compose up -d --build }
function sfg-stop { docker-compose down }
function sfg-logs-back { docker-compose logs -f backend }
function sfg-logs-front { docker-compose logs -f frontend }
function sfg-ps { docker-compose ps }
function sfg-rebuild { docker-compose build --no-cache; docker-compose up -d }
function sfg-clean { docker system prune -a --volumes }
function sfg-reset { docker-compose down -v; docker-compose up -d --build }

# Save and reload profile
. $PROFILE
```

---

## QUICK REFERENCE

| Task | Command |
|------|---------|
| Start all services | `docker-compose up -d --build` |
| Stop all services | `docker-compose down` |
| View logs | `docker-compose logs -f <service>` |
| Rebuild service | `docker-compose build --no-cache <service>` |
| Restart service | `docker-compose restart <service>` |
| Execute command in container | `docker-compose exec <service> <command>` |
| View database | http://localhost:8080 (Adminer) |
| API documentation | http://localhost:8001/docs (Swagger) |
| Check health | `curl http://localhost:8001/healthz` |
| Reset database | `docker-compose down -v && docker-compose up -d --build` |
| Full cleanup | `docker system prune -a --volumes` |

---

**Next:** Read [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed architecture, or [CICD_OPTIMIZATION_GUIDE.md](CICD_OPTIMIZATION_GUIDE.md) for deployment info.
