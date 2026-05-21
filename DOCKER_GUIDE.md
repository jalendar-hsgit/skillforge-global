# DOCKER ARCHITECTURE & CONNECTIVITY GUIDE

## 1. DOCKER-COMPOSE STRUCTURE & SERVICES

### Services Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILLFORGE DOCKER NETWORK                   │
│                   (skillforge-network bridge)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐  │
│  │  FRONTEND        │  │   BACKEND        │  │  DATABASE   │  │
│  │  (Next.js)       │  │   (FastAPI)      │  │ (PostgreSQL)│  │
│  │  Port 3000       │  │   Port 8001      │  │  Port 5432  │  │
│  │  ┌────────────────┼──┼────────────────┐  │             │  │
│  │  │ Connects to    │  │ Connects to    │  │             │  │
│  │  │ backend:8001   │  │ postgres:5432  │  │             │  │
│  │  │                │  │ redis:6379     │  │             │  │
│  │  └────────────────┼──┼────────────────┘  │             │  │
│  └──────────────────┘  └──────────────────┘  └─────────────┘  │
│           ▲                    ▲                      ▲         │
│           │                    │                      │         │
│      HTTP API calls        DB queries           Persistent      │
│      CORS enabled          Redis cache          volumes         │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐  │
│  │  CACHE           │  │   TOOLS          │  │   TOOLS     │  │
│  │  (Redis)         │  │   (Adminer)      │  │  (pgAdmin)  │  │
│  │  Port 6379       │  │   Port 8080      │  │  Port 5050  │  │
│  │                  │  │  (Web DB client) │  │ (Advanced DB│  │
│  │  Session store   │  │                  │  │   Manager)  │  │
│  │  Queue storage   │  │                  │  │             │  │
│  └──────────────────┘  └──────────────────┘  └─────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ▲ localhost port mapping (external access)
         │
      Your machine
```

## 2. SERVICE DETAILS

### PostgreSQL (Database)
- **Image**: postgres:15-alpine
- **Container**: skillforge-postgres
- **Port**: 5432 (exposed)
- **Hostname in network**: postgres
- **Database**: skillforge
- **User**: admin
- **Password**: skillforge_dev_password
- **Volumes**: postgres_data (persistent storage)
- **Healthcheck**: pg_isready -U admin (checks every 10s)

### Redis (Cache)
- **Image**: redis:7-alpine
- **Container**: skillforge-redis
- **Port**: 6379 (exposed)
- **Hostname in network**: redis
- **Healthcheck**: redis-cli ping (checks every 10s)

### Backend (FastAPI)
- **Dockerfile**: Dockerfile.backend (multi-stage build)
- **Container**: skillforge-backend
- **Port**: 8001 (exposed)
- **Hostname in network**: backend
- **Environment**:
  - DATABASE_URL: postgresql://admin:pass@postgres:5432/skillforge
  - REDIS_URL: redis://redis:6379
  - ALLOWED_ORIGINS: http://localhost:3000, http://backend:8001
- **Startup**: init_db.py → seed_data.py → uvicorn
- **Healthcheck**: curl http://localhost:8001/healthz
- **Volumes**: ./backend:/app:cached (live reload)

### Frontend (Next.js)
- **Dockerfile**: Dockerfile.frontend
- **Container**: skillforge-frontend
- **Port**: 3000 (exposed)
- **Hostname in network**: frontend
- **Environment**:
  - NEXT_PUBLIC_API_BASE: http://backend:8001 (inside Docker network)
  - NEXT_PUBLIC_API_BASE: http://localhost:8001 (from browser)
- **Startup**: npm run dev
- **Healthcheck**: wget to http://localhost:3000
- **Volumes**: ./src, ./public (live reload)

### Adminer (DB Web Client)
- **Image**: adminer:latest
- **Container**: skillforge-adminer
- **Port**: 8080 (exposed)
- **URL**: http://localhost:8080
- **Connect to**: postgres:5432

### pgAdmin (Advanced DB Manager)
- **Image**: dpage/pgadmin4:latest
- **Container**: skillforge-pgadmin
- **Port**: 5050 (exposed)
- **URL**: http://localhost:5050
- **Email**: admin@skillforge.com
- **Password**: admin

## 3. NETWORK CONNECTIVITY MAP

### Internal Service-to-Service (Docker Network)
```
Frontend → Backend
URL: http://backend:8001
Port: 8001
CORS: Allowed from http://localhost:3000

Backend → PostgreSQL
URL: postgresql://admin:pass@postgres:5432/skillforge
Port: 5432
Auth: Required

Backend → Redis
URL: redis://redis:6379
Port: 6379
Auth: Not required

Adminer → PostgreSQL
URL: postgres:5432
Port: 5432
Auth: Required
```

### External Access (From Your Machine)
```
Browser → Frontend
URL: http://localhost:3000
Port: 3000

Browser/API Client → Backend
URL: http://localhost:8001/api/v1/*
Port: 8001

Database Tools → PostgreSQL
URL: localhost:5432
Port: 5432
Auth: admin/skillforge_dev_password

Adminer Web Client
URL: http://localhost:8080
Port: 8080

pgAdmin Web Client
URL: http://localhost:5050
Port: 5050
Email: admin@skillforge.com
Pass: admin
```

## 4. DOCKER COMPOSE COMMANDS & TROUBLESHOOTING

### Basic Commands
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d skillforge-backend

# Stop all services
docker-compose down

# Stop and remove volumes (resets database!)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Rebuild and start
docker-compose up -d --build

# View logs
docker-compose logs -f                    # All services
docker-compose logs -f skillforge-backend # Specific service
docker-compose logs --tail 100 skillforge-backend  # Last 100 lines

# Check service status
docker-compose ps
docker-compose ps --services

# Execute command in running container
docker exec -it skillforge-backend bash
docker exec skillforge-postgres psql -U admin -d skillforge
docker exec skillforge-redis redis-cli ping
```

### Troubleshooting Commands

#### Check Service Health
```bash
# Check all container status
docker ps --filter "name=skillforge" --format "{{.Names}}\t{{.Status}}"

# Check specific container health
docker inspect skillforge-backend --format "{{.State.Status}}"

# Get exit code of stopped container
docker inspect skillforge-backend --format "{{.State.ExitCode}}"
```

#### Check Connectivity
```bash
# Test database connection from backend
docker exec skillforge-backend psql -h postgres -U admin -d skillforge -c "SELECT 1"

# Test Redis connection from backend
docker exec skillforge-backend redis-cli -h redis ping

# Test backend API from localhost
curl http://localhost:8001/healthz
curl http://localhost:8001/api/v1/courses

# Test inter-container connectivity (from backend)
docker exec skillforge-backend curl -I http://backend:8001/healthz
docker exec skillforge-backend curl -I http://postgres:5432
```

#### Database Debugging
```bash
# Access PostgreSQL directly
docker exec -it skillforge-postgres psql -U admin -d skillforge

# View all tables
\dt

# Check table row counts
SELECT tablename, (SELECT COUNT(*) FROM tablename) as rows 
FROM pg_tables WHERE schemaname='public';

# View courses table
SELECT COUNT(*) FROM courses;

# View mentors table
SELECT COUNT(*) FROM mentors;

# Exit psql
\q
```

#### Check Network
```bash
# List Docker networks
docker network ls

# Inspect skillforge network
docker network inspect skillforge-network

# Test network connectivity between containers
docker exec skillforge-backend ping -c 1 postgres
docker exec skillforge-backend ping -c 1 redis
docker exec skillforge-backend ping -c 1 frontend
```

#### View Logs
```bash
# Real-time logs with color
docker-compose logs -f --timestamps

# Logs from last 30 minutes
docker-compose logs --since 30m

# Search for errors
docker logs skillforge-backend 2>&1 | grep -i error

# Save logs to file
docker logs skillforge-backend > backend_logs.txt 2>&1
```

### Common Issues & Fixes

#### Port Already in Use
```bash
# Find what's using port 8001
netstat -ano | findstr :8001  # Windows
lsof -i :8001                  # Mac/Linux

# Kill process using port
taskkill /PID <PID> /F  # Windows
kill -9 <PID>           # Mac/Linux
```

#### Container Won't Start
```bash
# Check logs
docker logs skillforge-backend

# Rebuild without cache
docker-compose build --no-cache skillforge-backend

# Remove old image and rebuild
docker rmi skillforge-global-backend
docker-compose build skillforge-backend
```

#### Database Connection Errors
```bash
# Check if database is healthy
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Check database logs
docker logs skillforge-postgres

# Reset database (WARNING: deletes data!)
docker-compose down -v
docker-compose up -d
```

#### Network Issues
```bash
# Recreate network
docker-compose down
docker network rm skillforge-network
docker-compose up -d

# Check DNS resolution
docker exec skillforge-backend nslookup postgres
docker exec skillforge-backend nslookup redis
```

## 5. FILE MAPPING

### Host ↔ Container Volumes
```
Host                              Container
─────────────────────────────────────────────
./backend/app                  ↔  /app/app
./backend/init_db.py           ↔  /app/init_db.py
./src                          ↔  /app/src (frontend)
./public                       ↔  /app/public (frontend)
postgres_data (managed)        ↔  /var/lib/postgresql/data
```

### Why Volumes Matter
- **Live Reload**: Changes to code reflect immediately
- **Data Persistence**: Database survives container restarts
- **Development**: No need to rebuild images for code changes

## 6. CORS & API ACCESS

### CORS Configuration
Backend allows requests from:
- http://localhost:3000 (frontend local)
- http://localhost:8001 (API server)
- Environment-based: ALLOWED_ORIGINS

### API Base URL Context
```javascript
// Inside React/Next.js container
const API_BASE = "http://backend:8001"  // Uses Docker hostname

// From browser (localhost)
const API_BASE = "http://localhost:8001"  // Uses mapped port

// env variable overrides
process.env.NEXT_PUBLIC_API_BASE
```

## 7. HEALTH CHECKS

Each service has health checks:
```yaml
PostgreSQL: pg_isready -U admin
Redis:      redis-cli ping
Backend:    curl http://localhost:8001/healthz
Frontend:   wget http://localhost:3000
```

Dependencies wait for health:
- Frontend waits for Backend healthy
- Backend waits for PostgreSQL + Redis healthy

---

## NEXT SECTION: BUILD TIME OPTIMIZATION →
