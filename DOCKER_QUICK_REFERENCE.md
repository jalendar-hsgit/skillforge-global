# DOCKER & DEPLOYMENT QUICK REFERENCE

## QUICK START

```bash
# Navigate to project
cd skillforge-global

# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Rebuild everything
docker-compose up -d --build
```

## ESSENTIAL COMMANDS

### Status & Monitoring
```bash
# Check all containers
docker ps

# Check specific container
docker inspect skillforge-backend

# View container logs
docker logs skillforge-backend
docker logs -f skillforge-backend          # Follow logs
docker logs --tail 50 skillforge-backend   # Last 50 lines

# Check resource usage
docker stats

# View network
docker network ls
docker network inspect skillforge-network
```

### Building
```bash
# Build all images
docker-compose build

# Build without cache (fresh build)
docker-compose build --no-cache

# Build specific service
docker-compose build skillforge-backend

# See build time
time docker-compose build
```

### Starting & Stopping
```bash
# Start all
docker-compose up -d

# Start specific service
docker-compose up -d skillforge-backend

# Stop all
docker-compose down

# Stop and remove volumes (DELETES DATABASE!)
docker-compose down -v

# Restart all
docker-compose restart

# Restart specific
docker-compose restart skillforge-backend
```

### Accessing Services
```bash
# Get shell in backend
docker exec -it skillforge-backend bash

# Run Python command in backend
docker exec skillforge-backend python -c "print('hello')"

# Access PostgreSQL
docker exec -it skillforge-postgres psql -U admin -d skillforge

# Test Redis
docker exec skillforge-redis redis-cli ping

# Check API
curl http://localhost:8001/healthz
curl http://localhost:8001/api/v1/courses
```

## TROUBLESHOOTING

### Container Won't Start
```bash
# Check logs
docker logs skillforge-backend

# Rebuild
docker-compose build --no-cache skillforge-backend

# Restart
docker-compose restart skillforge-backend

# Nuclear option: remove and restart
docker-compose down
docker system prune -a
docker-compose up -d
```

### Can't Connect to Database
```bash
# Test from backend
docker exec skillforge-backend psql -h postgres -U admin -d skillforge -c "SELECT 1"

# Check database logs
docker logs skillforge-postgres

# Restart database
docker-compose restart skillforge-postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Port Already in Use
```bash
# Find what's using port 8001
netstat -ano | findstr :8001  # Windows
lsof -i :8001                 # Mac/Linux

# Kill process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                  # Mac/Linux
```

### Build Taking Too Long
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Add to .env
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1

# Clean and rebuild
docker system prune -a

# Check build context
du -sh .
```

## FILE LOCATIONS

```
Project Root
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── init_db.py
│   └── seed_all_demo_data.py
├── src/
│   ├── pages/
│   ├── components/
│   └── lib/
├── public/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .dockerignore
├── package.json
└── .github/
    └── workflows/
        └── build-and-test.yml
```

## PORT MAPPING

| Service | Internal | External | Purpose |
|---------|----------|----------|---------|
| Frontend | 3000 | 3000 | Web app |
| Backend | 8001 | 8001 | REST API |
| PostgreSQL | 5432 | 5432 | Database |
| Redis | 6379 | 6379 | Cache |
| Adminer | 8080 | 8080 | DB web client |
| pgAdmin | 80 | 5050 | Advanced DB tool |

## COMMON TASKS

### Add Python Package
```bash
# Edit backend/requirements.txt
vim backend/requirements.txt

# Rebuild backend
docker-compose build --no-cache skillforge-backend
docker-compose up -d skillforge-backend
```

### Add NPM Package
```bash
# From host machine
npm install package-name

# Rebuild frontend
docker-compose build skillforge-frontend
docker-compose up -d skillforge-frontend
```

### View Database
```bash
# Option 1: Adminer (web)
# Go to http://localhost:8080

# Option 2: pgAdmin (web)
# Go to http://localhost:5050

# Option 3: Command line
docker exec -it skillforge-postgres psql -U admin -d skillforge

# View tables
\dt

# Query data
SELECT * FROM courses;
SELECT COUNT(*) FROM mentors;
```

### Check API Health
```bash
# Health check
curl http://localhost:8001/healthz

# List courses
curl http://localhost:8001/api/v1/courses

# List mentors
curl http://localhost:8001/api/v1x/mentors

# With JSON formatting
curl -s http://localhost:8001/api/v1/courses | python -m json.tool
```

## DEPLOYMENT CHECKLIST

- [ ] Code pushed to GitHub
- [ ] GitHub Actions workflow triggers
- [ ] Tests pass
- [ ] Images built successfully
- [ ] Images pushed to registry
- [ ] Deploy to server
- [ ] Pull latest images
- [ ] Run docker-compose up -d
- [ ] Check health endpoints
- [ ] Verify API responses
- [ ] Test from browser

## MONITORING

### Real-time Stats
```bash
watch -n 1 docker stats
```

### Recent Activity
```bash
docker events --since 10m
```

### Image Size
```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

## CLEANUP

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Complete cleanup
docker system prune -a
```

## IMPORTANT NOTES

⚠️ **WARNING: Destructive Commands**
```bash
docker-compose down -v      # Deletes database!
docker system prune -a      # Removes all images!
```

✅ **Safe Operations**
```bash
docker-compose restart      # Keeps data
docker logs                 # Read-only
docker-compose ps          # View only
```

## FILES REFERENCE

- **Docker-compose**: `docker-compose.yml`
- **Backend Docker**: `Dockerfile.backend`
- **Frontend Docker**: `Dockerfile.frontend`
- **Build ignores**: `.dockerignore`
- **CI/CD workflow**: `.github/workflows/build-and-test.yml`
- **Full guide**: `DOCKER_GUIDE.md`
- **Optimization**: `CICD_OPTIMIZATION_GUIDE.md`

## NEXT STEPS

1. **[x] Understand Docker architecture** - See DOCKER_GUIDE.md
2. **[x] Optimize build times** - See CICD_OPTIMIZATION_GUIDE.md
3. **[ ] Set up GitHub Actions** - Commit `.github/workflows/build-and-test.yml`
4. **[ ] Test locally**: `docker-compose up -d --build`
5. **[ ] Choose deployment** - DigitalOcean, Render, or VPS
6. **[ ] Set up monitoring** - Use Docker stats or cloud dashboards

## RESOURCES

- Docker Docs: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose/
- GitHub Actions: https://github.com/features/actions
- DigitalOcean: https://www.digitalocean.com
- Render: https://render.com
