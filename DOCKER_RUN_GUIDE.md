# SkillForge Local Docker Deployment - Manual Steps

## Status: Build Complete ✅ 

Docker images have been successfully built. Here's how to run them locally:

---

## 🚀 Quick Start (3 commands)

Open **Windows PowerShell** or **Git Bash** and run:

```bash
cd "d:\python code\sfg\skillforge-global"

docker-compose up -d

docker-compose ps
```

That's it! All services will start in background mode.

---

## Detailed Startup Steps

### Step 1: Open Terminal
- **Windows:** Open PowerShell or Command Prompt
- **Navigate to project:**
```bash
cd "d:\python code\sfg\skillforge-global"
```

### Step 2: Start Services
```bash
docker-compose up -d
```

**Expected Output:**
```
[+] Running 7/7
 ✓ Container skillforge-postgres   Started
 ✓ Container skillforge-redis      Started
 ✓ Container skillforge-backend    Started
 ✓ Container skillforge-frontend   Started
 ✓ Container skillforge-adminer    Started
 ✓ Container skillforge-pgadmin    Started
```

### Step 3: Verify All Running
```bash
docker-compose ps
```

**Expected Output:**
```
NAME                    STATUS      PORTS
skillforge-postgres     Up 2 min    5432/tcp
skillforge-redis        Up 2 min    6379/tcp
skillforge-backend      Up 1 min    0.0.0.0:8001->8001/tcp
skillforge-frontend     Up 1 min    0.0.0.0:3000->3000/tcp
skillforge-adminer      Up 1 min    0.0.0.0:8080->8080/tcp
skillforge-pgadmin      Up 1 min    0.0.0.0:5050->80/tcp
```

---

## 🌐 Access Your Application

Once all services are running, access them at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | SkillForge Web App |
| **Backend API** | http://localhost:8001 | REST API |
| **Backend Health** | http://localhost:8001/api/v1/health | API Status |
| **Database UI** | http://localhost:8080 | Adminer (Simple DB UI) |
| **Advanced DB UI** | http://localhost:5050 | pgAdmin (Advanced DB UI) |

---

## 👤 Demo Account

Use these credentials to login at http://localhost:3000:

```
Email:    john.doe@example.com
Password: password
```

---

## 📊 Useful Commands

### View All Container Logs
```bash
docker-compose logs -f
```

### View Specific Service Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Check Container Status
```bash
docker-compose ps
```

### Stop All Services (Keep Data)
```bash
docker-compose stop
```

### Restart All Services
```bash
docker-compose restart
```

### Stop and Remove All (Keep Data)
```bash
docker-compose down
```

### Complete Reset (Delete Everything)
```bash
docker-compose down -v
```

### Restart Backend Only
```bash
docker-compose restart backend
```

### Restart Frontend Only
```bash
docker-compose restart frontend
```

---

## 🔍 Testing the API

### Test Backend Health
```bash
curl http://localhost:8001/api/v1/health
```

Expected response:
```json
{"status":"healthy"}
```

### Test Courses API
```bash
curl http://localhost:8001/api/v1x/marketplace/courses
```

### Test User Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"john.doe@example.com",
    "password":"password"
  }'
```

---

## 🗄️ Database Access

### Using Adminer (Simple Interface)
1. Visit: http://localhost:8080
2. Select database:
   - **System:** PostgreSQL
   - **Server:** postgres
   - **Username:** admin
   - **Password:** skillforge_dev_password
   - **Database:** skillforge
3. Click Login

### Using pgAdmin (Advanced Interface)
1. Visit: http://localhost:5050
2. Login:
   - **Email:** admin@skillforge.com
   - **Password:** admin
3. Add server → New → Server
4. Configure:
   - **Name:** skillforge
   - **Host:** postgres
   - **Port:** 5432
   - **Username:** admin
   - **Password:** skillforge_dev_password

### Using Command Line
```bash
# Connect directly to PostgreSQL
docker-compose exec postgres psql -U admin -d skillforge

# List tables
\dt

# Query users
SELECT * FROM users;

# Exit
\q
```

---

## 📈 What's Running

### Services
1. **PostgreSQL 15** (Port 5432)
   - Database for application data
   - Persistent storage in `postgres_data` volume

2. **Redis 7** (Port 6379)
   - In-memory cache
   - Session storage

3. **FastAPI Backend** (Port 8001)
   - REST API endpoints
   - Automatic database initialization
   - Demo data seeding
   - Live reload enabled

4. **Next.js Frontend** (Port 3000)
   - React web application
   - Hot reload enabled
   - Connected to backend API

5. **Adminer** (Port 8080)
   - Simple web database UI
   - Quick database exploration

6. **pgAdmin** (Port 5050)
   - Advanced PostgreSQL management
   - Visual query builder

---

## ⚠️ Troubleshooting

### "Port already in use" Error
```bash
# Find what's using port 3000 (Windows)
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <process_id> /F

# Or change docker-compose ports in docker-compose.yml
# Change "3000:3000" to "3001:3000"
```

### "Cannot connect to database" Error
```bash
# Check postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Wait 10 seconds then test
docker-compose exec postgres psql -U admin -d skillforge -c "SELECT 1;"
```

### "Frontend won't load" Error
```bash
# Check frontend is running
docker-compose ps frontend

# View frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend

# Clear browser cache (Ctrl+Shift+Delete)
# Then refresh page
```

### "API returns 404" Error
```bash
# Check backend is running
docker-compose ps backend

# Test backend health
curl http://localhost:8001/api/v1/health

# View backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Docker Compose Version Issues
If you see warnings about version attribute, you're using an older docker-compose.  
The warning doesn't affect functionality but can be fixed by updating Docker Desktop.

---

## 📚 Development Workflow

### Daily Start
```bash
cd "d:\python code\sfg\skillforge-global"
docker-compose up -d
```

### Make Changes
- Edit files in `src/` directory for frontend (auto hot-reload)
- Edit files in `backend/app/` for backend (auto reload)
- View logs: `docker-compose logs -f`

### Run Tests
```bash
# Backend tests
docker-compose exec backend pytest tests/ -v

# Frontend tests
docker-compose exec frontend npm test
```

### Database Changes
```bash
# Access database
docker-compose exec postgres psql -U admin -d skillforge

# Run migrations or queries
# Edit files and they're immediately available

# Clear data and reseed
docker-compose restart backend
```

### End of Day
```bash
# Keep data, stop containers
docker-compose stop

# Next day just start again
docker-compose up -d
```

---

## 🎯 First Time Setup Checklist

- [ ] Started Docker Desktop   
- [ ] Opened PowerShell/Terminal
- [ ] Navigated to project: `cd "d:\python code\sfg\skillforge-global"`
- [ ] Started services: `docker-compose up -d`
- [ ] Verified all running: `docker-compose ps`
- [ ] Visited http://localhost:3000
- [ ] Logged in with demo account (john.doe@example.com / password)
- [ ] Tested marketplace features
- [ ] Checked backend API: http://localhost:8001/api/v1/health
- [ ] Viewed database: http://localhost:8080

---

## 📺 Monitoring

### Real-time Monitoring
```bash
# Watch all container stats
docker stats

# Or specific container
docker stats skillforge-backend
```

### Quick Status Check
```bash
docker-compose ps
```

### Check Image Sizes
```bash
docker images | Select-String skillforge
```

---

## 🔄 Complete Reset

If you want to start completely fresh:

```bash
# Stop everything and remove all data
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Verify
docker-compose ps
```

---

## ✅ You're All Set!

Your local Docker deployment is ready. 

**Next steps:**
1. Run: `docker-compose up -d`
2. Visit: http://localhost:3000
3. Login with: john.doe@example.com / password
4. Explore the marketplace
5. View logs: `docker-compose logs -f`

---

For detailed guides, see:
- `LOCAL_DOCKER_DEPLOYMENT.md` - Complete reference
- `DOCKER_BUILD_FIX_SUMMARY.md` - Build fixes applied
- `FRONTEND_BUILD_FIX.md` - Frontend fixes applied

**Enjoy! 🚀**
