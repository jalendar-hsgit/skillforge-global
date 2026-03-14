# DOCKER ARCHITECTURE - VISUAL DIAGRAMS

## 1. LOCAL DEVELOPMENT ARCHITECTURE

```
Your Machine (Host)
=============================================================================
┌─────────────────────────────────────────────────────────────────────────┐
│                      DOCKER DESKTOP / DAEMON                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │              skillforge-network (Bridge Network)                  │  │
│  │                                                                   │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │ │
│  │  │  skillforge      │  │  skillforge      │  │  skillforge     │ │ │
│  │  │  frontend        │  │  backend         │  │  postgres       │ │ │
│  │  │  (Next.js)       │  │  (FastAPI)       │  │  (Database)     │ │ │
│  │  │                  │  │                  │  │                 │ │ │
│  │  │ Port: 3000       │  │ Port: 8001       │  │ Port: 5432      │ │ │
│  │  │ Hostname: front. │  │ Hostname: backend│  │ Hostname: post. │ │ │
│  │  │                  │  │                  │  │                 │ │ │
│  │  │ ENV:             │  │ ENV:             │  │ ENV:            │ │ │
│  │  │ NEXT_PUBLIC_API_ │  │ DATABASE_URL:    │  │ POSTGRES_DB:    │ │ │
│  │  │ BASE: http://    │  │ postgresql://... │  │ skillforge      │ │ │
│  │  │ backend:8001     │  │                  │  │                 │ │ │
│  │  │                  │  │ REDIS_URL:       │  │                 │ │ │
│  │  │ Volumes:         │  │ redis://redis:63│  │ Volumes:        │ │ │
│  │  │ ./src → /app/src │  │ 79               │  │ postgres_data   │ │ │
│  │  │ ./public → /app/ │  │                  │  │ → /var/lib/     │ │ │
│  │  │ public          │  │ Volumes:         │  │ postgresql/data │ │ │
│  │  │                  │  │ ./backend/app    │  │                 │ │ │
│  │  └──────────────────┘  │ → /app/app       │  └─────────────────┘ │ │
│  │      │                 │                  │        │              │ │
│  │      │ HTTP calls      │ SQL queries      │        │              │ │
│  │      └─────────────────►  DB queries      │        │              │ │
│  │                         │ (internal:5432) │        │              │ │
│  │                         └─────────────────────────►│              │ │
│  │                                                    │              │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │ │
│  │  │  skillforge      │  │  skillforge      │  │  skillforge     │ │ │
│  │  │  redis           │  │  adminer         │  │  pgadmin        │ │ │
│  │  │  (Cache)         │  │  (Web DB Client) │  │  (Web DB GUI)   │ │ │
│  │  │                  │  │                  │  │                 │ │ │
│  │  │ Port: 6379       │  │ Port: 8080       │  │ Port: 5050      │ │ │
│  │  │ Hostname: redis  │  │ Hostname: adminer│  │ Hostname: pgadm.│ │ │
│  │  └──────────────────┘  └──────────────────┘  └─────────────────┘ │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Port Mapping (Exposed to Host):                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ localhost:3000   →  skillforge-frontend:3000                   │  │
│  │ localhost:8001   →  skillforge-backend:8001                    │  │
│  │ localhost:5432   →  skillforge-postgres:5432                   │  │
│  │ localhost:6379   →  skillforge-redis:6379                      │  │
│  │ localhost:8080   →  skillforge-adminer:8080                    │  │
│  │ localhost:5050   →  skillforge-pgadmin:80                      │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
         ▲
         │ Browser access
         │
    You: http://localhost:3000
```

---

## 2. REQUEST FLOW FROM BROWSER

```
USER BROWSER
─────────────

    ↓ User visits http://localhost:3000
    
┌──────────────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js) Container                                     │
│ ─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Receives HTTP request on localhost:3000                       │
│  │                                                              │
│  ├─ Serves HTML/CSS/JS (index.tsx, components, etc.)          │
│  │                                                              │
│  └─ On page load:                                              │
│     const API_BASE = "http://backend:8001"                     │
│     fetch(API_BASE + "/api/v1/courses")                        │
│                                                                  │
│     ↓↓↓                                                          │
│                                                                  │
│     Docker translates "backend" hostname                        │
│     to backend container IP (e.g., 172.19.0.3:8001)           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
              ↓ HTTP GET /api/v1/courses
              
┌──────────────────────────────────────────────────────────────────┐
│ BACKEND (FastAPI) Container                                      │
│ ─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Receives request on port 8001                                 │
│  │                                                              │
│  ├─ Route: /api/v1/courses                                     │
│  │  def list_courses():                                         │
│  │      courses = db.query(Course).all()                       │
│  │                                                              │
│  └─ Queries database                                            │
│     ↓↓↓                                                          │
│                                                                  │
│     DATABASE_URL = "postgresql://admin:pass@postgres:5432/..."│
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
              ↓ SQL SELECT * FROM courses
              
┌──────────────────────────────────────────────────────────────────┐
│ DATABASE (PostgreSQL) Container                                  │
│ ─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Executes SQL query on port 5432                               │
│  │                                                              │
│  ├─ SELECT * FROM courses;                                    │
│  │  ┌────┬──────────────────┬─────────┐                       │
│  │  │ id │ title            │ price   │                       │
│  │  ├────┼──────────────────┼─────────┤                       │
│  │  │ 1  │ Python Fund.     │ $49.99  │                       │
│  │  │ 2  │ Web Dev Boot.    │ $99.99  │                       │
│  │  │ 3  │ React + Next     │ $149.99 │                       │
│  │  └────┴──────────────────┴─────────┘                       │
│  │                                                              │
│  └─ Returns results to Backend                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
              ↑ JSON response
              
Response travels back through Backend → Frontend → Browser
      
┌──────────────────────────────────────────────────────────────────┐
│ BROWSER receives JSON                                             │
│ ─────────────────────────────────────────────────────────────────│
│                                                                  │
│  [                                                               │
│    {"id": 1, "title": "Python Fund.", "price": 49.99},        │
│    {"id": 2, "title": "Web Dev Boot.", "price": 99.99},       │
│    ...                                                          │
│  ]                                                               │
│                                                                  │
│  React renders components:                                      │
│  {courses.map(course => (                                      │
│    <CourseCard key={course.id} {...course} />                 │
│  ))}                                                            │
│                                                                  │
│  User sees 3 courses displayed ✓                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. SERVICES DEPENDENCY GRAPH

```
        ┌─────────────────────────┐
        │   docker-compose up     │
        │       -d --build        │
        └────────────┬────────────┘
                     │
          Start services in order:
                     │
        ┌────────────▼────────────┐
        │   1. PostgreSQL         │
        │   (Waits for)           │
        │   Health: pg_isready    │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   2. Redis              │
        │   (Waits for)           │
        │   Health: redis-cli     │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   3. Backend (FastAPI)  │
        │   (Waits for)           │
        │   Health: /healthz      │
        │                         │
        │   On startup:           │
        │   - init_db.py          │
        │   - seed_data.py        │
        │   - uvicorn server      │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   4. Frontend (Next.js) │
        │   (Waits for Backend)   │
        │   Health: GET /         │
        │                         │
        │   On startup:           │
        │   - npm run dev         │
        │   - Connects to Backend │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   5. Adminer            │
        │   (Waits for DB)        │
        │   Web UI: 8080          │
        └─────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │   6. pgAdmin            │
        │   (Waits for DB)        │
        │   Web UI: 5050          │
        └─────────────────────────┘

All services now running ✓
All health checks passing ✓
Ready for development ✓
```

---

## 4. CI/CD PIPELINE FLOW

```
Developer
    │
    ├─ Writes code
    │
    ├─ git commit -m "Fix bug XYZ"
    │
    └─ git push origin main
            │
            ▼
    ┌──────────────────────────────────┐
    │   GitHub Receives Push           │
    │   (Webhook triggered)            │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │   GitHub Actions Triggered       │
    │   .github/workflows/build-and... │
    │   test.yml is executed           │
    └────────────┬─────────────────────┘
                 │
    ┌────────────┴──────────────────────┐
    │                                   │
    ▼                                   ▼
┌─────────────────────┐          ┌────────────────────┐
│  Lint Backend       │          │  Lint Frontend     │
│  - Python style     │          │  - JavaScript style│
│  - Code formatting  │          │  - ESLint checks   │
│  - Type hints       │          │  - Prettier format │
│  Pass? ✓            │          │  Pass? ✓           │
└──────────┬──────────┘          └────────┬───────────┘
           │                              │
           └──────────────┬───────────────┘
                          │
           All linting passed? Continue...
                          │
                          ▼
           ┌──────────────────────────────┐
           │   Build Backend Image        │
           │                              │
           │   docker build \             │
           │   -f Dockerfile.backend \    │
           │   -t ghcr.io/.../backend:... │
           │   .                          │
           │                              │
           │   Result: 300MB image        │
           │   Push to ghcr.io ✓          │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   Build Frontend Image       │
           │                              │
           │   docker build \             │
           │   -f Dockerfile.frontend \   │
           │   -t ghcr.io/.../frontend:..│
           │   .                          │
           │                              │
           │   Result: 450MB image        │
           │   Push to ghcr.io ✓          │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   All Tests Passed ✓         │
           │   Images built successfully  │
           │   Images pushed to registry  │
           │                              │
           │   GitHub Actions Summary:    │
           │   ✓ Lint backend             │
           │   ✓ Lint frontend            │
           │   ✓ Build backend            │
           │   ✓ Build frontend           │
           │   ✓ Push images              │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │   Ready for Deployment!      │
           │                              │
           │   Images available at:       │
           │   ghcr.io/youruser/backend:..│
           │   ghcr.io/youruser/frontend:.│
           │                              │
           │   Option 1: Deploy to Render │
           │   Option 2: Deploy to VPS    │
           │   Option 3: Manual trigger   │
           └──────────────────────────────┘
```

---

## 5. DEPLOYMENT ARCHITECTURE (Production)

```
PRODUCTION SERVER (e.g., DigitalOcean VPS)
════════════════════════════════════════════════════════════════

┌────────────────────────────────────────────────────────────────┐
│                      Docker Daemon                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           skillforge-network (Bridge)                   │  │
│  │                                                          │  │
│  │  ┌─────────────────┐  ┌─────────────────┐              │  │
│  │  │ Nginx (Reverse  │  │ Backend         │              │  │
│  │  │ Proxy)          │  │ (FastAPI)       │              │  │
│  │  │                 │  │                 │              │  │
│  │  │ Port: 80 (HTTP) │  │ Port: 8001      │              │  │
│  │  │ Port: 443 (HTTPS│  │ (internal only) │              │  │
│  │  │                 │  │                 │              │  │
│  │  └────────┬────────┘  └────────┬────────┘              │  │
│  │           │                    │                       │  │
│  │           │ SSL cert           │ SQL queries           │  │
│  │           │ (Let's Encrypt)    │                       │  │
│  │           │                    │                       │  │
│  │  ┌────────▼────────┐  ┌────────▼────────┐              │  │
│  │  │ Frontend        │  │ PostgreSQL      │              │  │
│  │  │ (Static build)  │  │ (Persistent)    │              │  │
│  │  │                 │  │                 │              │  │
│  │  │ Served via      │  │ Port: 5432      │              │  │
│  │  │ Nginx           │  │ (internal only) │              │  │
│  │  └─────────────────┘  └─────────────────┘              │  │
│  │                                                          │  │
│  │  ┌─────────────────┐  ┌─────────────────┐              │  │
│  │  │ Redis           │  │ Backup storage  │              │  │
│  │  │ (Cache)         │  │ (Persistent)    │              │  │
│  │  │                 │  │                 │              │  │
│  │  │ Port: 6379      │  │ S3 / Backups    │              │  │
│  │  │ (internal only) │  │ (external)      │              │  │
│  │  └─────────────────┘  └─────────────────┘              │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  External Port Mapping:                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Domain: yourdomain.com (Port 80/443 via Nginx)          │  │
│  │ └─ Routes HTTP traffic to Frontend (static dist)        │  │
│  │ └─ Routes /api/* to Backend (8001)                      │  │
│  │ └─ SSL/HTTPS encrypted                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ External Traffic
         │
┌────────▼────────────────────────────────────────────────────────┐
│              USERS (Internet)                                   │
│                                                                 │
│  Browser: https://yourdomain.com                              │
│  └─ Nginx handles SSL                                          │
│  └─ Serves frontend HTML/CSS/JS                               │
│  └─ Proxies /api/* to FastAPI backend                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. BUILD PIPELINE COMPARISON

```
BEFORE OPTIMIZATION          →        AFTER OPTIMIZATION
────────────────────────────           ──────────────────────────

Backend Build:                         Backend Build:
├─ Copy all files        70s           ├─ .dockerignore removes
│  (node_modules, git,                 │  unnecessary files      30s
│   docs, tests, etc.)                 │
│                                      ├─ Copy requirements     5s
├─ Install deps         180s           │
│ (npm i, all packages)                ├─ Install deps (cached) 20s
│                                      │  (reuses layer)
├─ Build                 60s           │
│                                      ├─ Copy code             10s
├─ Copy code             30s           │
                                       ├─ Build                 10s
TOTAL: ~340s (5-6 min)   
                                       TOTAL: ~75s (1-2 min) ✓

Frontend Build:                        Frontend Build:
├─ Copy all files        80s           ├─ .dockerignore filters 40s
│                                      │
├─ npm install          200s           ├─ npm ci (faster)       60s
│ (downloads all deps)                 │  (uses cache layer)
│                                      │
├─ Copy code             40s           ├─ Copy code             20s
│                                      │
├─ Build                 50s           ├─ Build (dev mode)      5s
                                       │
TOTAL: ~370s (6+ min)                  TOTAL: ~125s (2 min) ✓

────────────────────────────           ──────────────────────────

TOTAL TIME:                            TOTAL TIME:
Cold start: 710s (12 min)              Cold start: 200s (3 min)
With cache: 400s (7 min)               With cache: 80s (1 min)

IMPROVEMENT: 60% faster ✓✓✓
```

---

## 7. ENVIRONMENT VARIABLES FLOW

```
docker-compose.yml
    │
    ├─ environment:              .env file (optional)
    │  DATABASE_URL: postgres...  ├─ DB_PASSWORD=****
    │  REDIS_URL: redis://...     ├─ STRIPE_SECRET_KEY=****
    │  STRIPE_SECRET_KEY: ****    └─ JWT_SECRET_KEY=****
    │  JWT_SECRET_KEY: ****
    │
    └─ Injected into containers:
    
    Frontend Container:
    ├─ NEXT_PUBLIC_API_BASE=http://backend:8001
    ├─ NEXT_PUBLIC_STRIPE_KEY=pk_test_xxxxx
    └─ NODE_ENV=development
    
    Backend Container:
    ├─ DATABASE_URL=postgresql://admin:pass@postgres:5432/skillforge
    ├─ REDIS_URL=redis://redis:6379
    ├─ STRIPE_SECRET_KEY=sk_test_xxxxx
    └─ JWT_SECRET_KEY=your_secret
    
    These are available as:
    - Python: os.getenv('DATABASE_URL')
    - Node: process.env.NEXT_PUBLIC_API_BASE
```

---

## 8. VOLUME PERSISTENCE

```
HOST MACHINE                          DOCKER CONTAINER

backend/app/                          /app/app/
├─ models/                ———bound(cache)——► /app/app/models/
├─ api/                   ———bound(cache)——► /app/app/api/
├─ core/                  ———bound(cache)——► /app/app/core/
└─ main.py               ———bound(cache)——► /app/app/main.py

Changes instantly reflected ✓ (live reload)

Data Persistence:
────────────────

postgres_data/                        /var/lib/postgresql/data/
├─ pg_wal/               ———volume———► (database files)
├─ base/                 ———volume———► (tables, indexes)
└─ (more directories)    ———volume———► (persistent!)

Even if container restarts, data persists ✓
Data survives: docker-compose restart ✓
Data deleted: docker-compose down -v ❌ (DANGER!)
```

---

## 9. HEALTH CHECK FLOW

```
docker-compose up -d
    │
    ├─ Start PostgreSQL
    │  ├─ Wait 5 seconds (start-period)
    │  ├─ Run healthcheck: pg_isready -U admin
    │  ├─ If success → Status: HEALTHY ✓
    │  └─ If fail → Retry (max 5 times)
    │     ├─ Check every 10 seconds
    │     ├─ Timeout: 5 seconds each
    │     └─ After 5 fails → Status: UNHEALTHY ❌
    │
    ├─ Start Redis
    │  ├─ Wait 5 seconds
    │  ├─ Run healthcheck: redis-cli ping
    │  └─ Same retry logic
    │
    ├─ Start Backend (ONLY if postgres + redis HEALTHY)
    │  ├─ Wait 5 seconds
    │  ├─ Run healthcheck: curl http://localhost:8001/healthz
    │  └─ Same retry logic
    │  │  Run initialization:
    │  │  ├─ python init_db.py (create tables)
    │  │  ├─ python seed_all_demo_data.py (populate data)
    │  │  └─ uvicorn app.main:app (start server)
    │  │
    │  └─ Wait for healthz endpoint to return {"ok": true}
    │
    └─ Start Frontend (ONLY if backend HEALTHY)
       ├─ Wait 5 seconds
       ├─ Run healthcheck: wget http://localhost:3000/
       └─ Same retry logic
       └─ npm run dev (start development server)

All services healthy ✓
Can now access: http://localhost:3000
```

---

This comprehensive visual guide helps understand:
- How services communicate
- Request flow through the stack
- Build pipeline optimization
- Deployment architecture
- Volume persistence
- Health checks and dependencies

Use these diagrams to explain the system to teammates or reference during troubleshooting!
