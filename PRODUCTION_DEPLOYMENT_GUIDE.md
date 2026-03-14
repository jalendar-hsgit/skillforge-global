# PRODUCTION DEPLOYMENT GUIDE

## Overview

This guide walks you through deploying the Skillforge application to production on a real server accessible to the world. Once deployed, your app will be available at your own domain (e.g., skillforge.com).

---

## PART 1: PRE-DEPLOYMENT CHECKLIST

### 1.1 Code Readiness

- [ ] All features tested locally: `docker-compose up -d` works
- [ ] No sensitive data in code (`.env` not committed)
- [ ] All tests passing: `docker-compose exec backend pytest`
- [ ] Linting passed: `docker-compose exec backend flake8`
- [ ] Frontend builds without warnings: `npm run build`
- [ ] Git history clean: `git log --oneline | head -10` shows meaningful commits
- [ ] Latest code pushed to GitHub: `git push origin main`

### 1.2 Database Setup

- [ ] Demo data seeding works: `python backend/seed_all_demo_data.py` completes
- [ ] Database backups automated (backup script created)
- [ ] Migrations tested locally (if applicable)
- [ ] Schema validated: All tables exist with correct columns

### 1.3 Environment Configuration

- [ ] `.env` file created with production values:
  ```
  POSTGRES_USER=<strong_username>
  POSTGRES_PASSWORD=<strong_password>  # 20+ chars, random
  JWT_SECRET_KEY=<random_32_chars>
  STRIPE_SECRET_KEY=sk_prod_xxxxx
  STRIPE_PUBLIC_KEY=pk_prod_xxxxx
  DATABASE_URL=postgresql://user:pass@host:5432/skillforge
  REDIS_URL=redis://host:6379
  ENVIRONMENT=production
  ```
- [ ] All secrets generated (no "test" or "demo" values)
- [ ] .gitignore includes .env (verified)

### 1.4 Security Review

- [ ] CORS properly configured for production domain
- [ ] SSL/TLS certificates planned (Let's Encrypt free)
- [ ] Database password hashed and strong
- [ ] API rate limiting configured
- [ ] Admin endpoints protected with role checks
- [ ] User input validation on all endpoints
- [ ] No debug logging in production code

---

## PART 2: CHOOSE DEPLOYMENT PLATFORM

### Platform Comparison

| Platform | Cost | Setup Time | Difficulty | Auto-Deploy | Recommended For |
|----------|------|-----------|-----------|-------------|-----------------|
| **Render.com** | $12-25/mo | 10 min | EASY | ✅ Yes | First-timers, Small teams |
| **DigitalOcean VPS** | $3-5/mo | 30 min | MEDIUM | ❌ Manual | Cost-conscious, Learning |
| **DigitalOcean App Platform** | $12-25/mo | 15 min | EASY | ✅ Yes | Balanced choice |
| **AWS (ECS/Fargate)** | $20-100/mo | 60 min | HARD | ✅ Yes | Enterprise, Complex |
| **Heroku** | $25-50/mo | 5 min | VERY EASY | ✅ Yes | Simple apps (expensive) |

---

## PART 3: DEPLOYMENT OPTION A - RENDER.COM (RECOMMENDED FOR BEGINNERS)

### Why Render?
- Easiest setup (10 minutes)
- Free SSL certificates
- Automatic deployments from GitHub
- Good for learning
- $15/month for full stack

### A1. Sign Up

```bash
# 1. Go to https://render.com
# 2. Click "Sign up" → Choose "GitHub" authentication
# 3. Authorize Render to access your GitHub account
# 4. Verify email
```

### A2. Create PostgreSQL Database

```bash
# On Render dashboard:
# 1. Click "New +" → Select "PostgreSQL"
# 2. Fill in:
#    - Name: skillforge-db
#    - Database: skillforge
#    - User: admin
#    - Region: Choose closest to your users
#    - PostgreSQL Version: 15
# 3. Click "Create Database"
# 4. Wait 5-10 minutes for creation
# 5. Copy connection string from dashboard
#    (looks like: postgresql://admin:password@... )
# 6. Note this for later
```

### A3. Create Backend Web Service

```bash
# On Render dashboard:
# 1. Click "New +" → Select "Web Service"
# 2. Configure:
#    Name: skillforge-backend
#    Repository: your-github-repo/skillforge-global (if public)
#    OR paste GitHub repo URL
#    
#    Branch to deploy: main
#    Runtime: Python 3
#    Build Command: pip install -r backend/requirements.txt
#    Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
#    
#    Region: Same as database
#    Plan: Starter (free tier - auto-sleeps after 15 min inactivity)
#          Paid ($7/mo) - always running
#    
# 3. Click "Advanced" and add environment variables:
#    DATABASE_URL=postgresql://admin:PASSWORD@... (from database step)
#    REDIS_URL=redis://... (deploy Redis below first, or use Upstash)
#    JWT_SECRET_KEY=your-random-secret
#    STRIPE_SECRET_KEY=sk_prod_xxxxx
#    STRIPE_PUBLIC_KEY=pk_prod_xxxxx
#    ENVIRONMENT=production
#    
# 4. Click "Create Web Service"
# 5. Watch deployment in logs (should complete in 5-10 min)
```

### A4. Deploy Redis Cache

```bash
# On Render dashboard:
# 1. Click "New +" → Select "Redis"
# 2. Configure:
#    Name: skillforge-redis
#    Region: Same as backend
#    Plan: Starter ($5/mo) or Starter+ ($10/mo)
# 3. Click "Create Redis"
# 4. Copy connection string
# 5. Update backend environment variable: REDIS_URL=...
```

### A5. Create Frontend Web Service

```bash
# On Render dashboard:
# 1. Click "New +" → Select "Static Site" (for Next.js)
# 2. Configure:
#    Name: skillforge-frontend
#    Repository: your-github-repo/skillforge-global
#    Branch: main
#    Build Command: npm ci && npm run build && npm run export
#    
#    (Alternative for Next.js with dynamic features:)
#    Build Command: npm ci && npm run build
#    Start Command: npm run start
#    Use this if you need dynamic rendering
#    
#    Publish Directory: out (if using export) or .next (if using start)
#    
# 3. Add environment variable:
#    NEXT_PUBLIC_API_BASE=https://skillforge-backend.onrender.com
#    (replace with your actual backend URL from dashboard)
#    
# 4. Click "Create Static Site"
# 5. Watch deployment (should complete in 5-10 min)
```

### A6. Connect Domain (Optional)

```bash
# On Render dashboard for frontend service:
# 1. Click "Settings"
# 2. Under "Custom Domains"
#    Add your domain: www.yoursite.com
# 3. Render generates SSL certificate automatically (Let's Encrypt)
# 4. Update your domain registrar DNS records:
#    CNAME: www.yoursite.com → skillforge-frontend.onrender.com
# 5. Wait 24 hours for DNS propagation
```

### A7. Test Deployment

```bash
# Test backend API
curl https://skillforge-backend.onrender.com/healthz
# Response: {"ok": true, "status": "healthy"}

# Test frontend
open https://skillforge-frontend.onrender.com
# Should load the app and connect to backend API
```

---

## PART 4: DEPLOYMENT OPTION B - DIGITALOCEAN VPS (BUDGET OPTION)

### Why DigitalOcean?
- Cheapest: $3-5/month for basic VPS
- Full control
- Can run other services
- Learning platform

### B1. Create Droplet

```bash
# 1. Go to https://www.digitalocean.com
# 2. Sign up (get $10 credit for new users)
# 3. Click "Create" → "Droplet"
# 
# Choose:
#    OS: Ubuntu 22.04 LTS
#    Size: Basic $4/mo (1GB RAM, 25GB SSD) - minimum
#           Better: $6/mo (2GB RAM, 50GB SSD)
#    Region: Choose closest to users
#    Authentication: SSH key (more secure than password)
#    
# 4. Click "Create Droplet"
# 5. Wait 2-3 minutes for creation
# 6. Note your IP address: XXX.XXX.XXX.XXX
```

### B2. Connect and Setup

```bash
# SSH into your server
ssh root@XXX.XXX.XXX.XXX

# Update system
apt update
apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version       # Should show Docker version
docker-compose --version  # Should show Compose version
```

### B3. Deploy Application

```bash
# Still SSH'd into server

# Clone repository
cd /opt
sudo git clone https://github.com/your-username/skillforge-global.git
cd skillforge-global

# Create .env file with production values
sudo nano .env
# Add:
POSTGRES_USER=admin
POSTGRES_PASSWORD=<generate_strong_password>
JWT_SECRET_KEY=<generate_random_32_chars>
STRIPE_SECRET_KEY=sk_prod_xxxxx
DATABASE_URL=postgresql://admin:password@postgres:5432/skillforge
REDIS_URL=redis://redis:6379
ENVIRONMENT=production

# Save: Ctrl+O, Enter, Ctrl+X

# Start services
sudo docker-compose up -d --build

# Wait 5-10 minutes for build/startup
sudo docker-compose logs -f backend

# Verify running
sudo docker-compose ps
# All services should show "Up"

# Test API
curl http://localhost:8001/healthz
```

### B4. Setup Reverse Proxy (Nginx)

```bash
# SSH into server

# Install Nginx
sudo apt install nginx -y

# Create config file
sudo nano /etc/nginx/sites-available/skillforge

# Add config:
upstream backend {
    server localhost:8001;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name example.com www.example.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Save file: Ctrl+O, Enter, Ctrl+X

# Enable site
sudo ln -s /etc/nginx/sites-available/skillforge /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t
# Output: "configuration ok"

# Restart Nginx
sudo systemctl restart nginx
```

### B5. Setup SSL Certificate (Let's Encrypt)

```bash
# SSH into server

# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Issue certificate
sudo certbot certonly --noninteractive --nginx \
    -d example.com -d www.example.com \
    -m admin@example.com --agree-tos

# Auto-renew certificates
sudo certbot renew --dry-run

# Certbot auto-renews daily (set up automatically)
```

### B6. Update Nginx for HTTPS

```bash
# SSH into server

# Edit nginx config
sudo nano /etc/nginx/sites-available/skillforge

# Update to:
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Save: Ctrl+O, Enter, Ctrl+X

# Restart
sudo systemctl restart nginx

# Test
curl https://example.com
```

### B7. Setup Monitoring and Auto-Restart

```bash
# SSH into server

# Create systemd service for auto-start
sudo nano /etc/systemd/system/skillforge.service

# Add:
[Unit]
Description=Skillforge App
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/skillforge-global
ExecStart=/usr/local/bin/docker-compose up -d
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target

# Save and enable
sudo systemctl daemon-reload
sudo systemctl enable skillforge.service
sudo systemctl start skillforge.service

# Verify
sudo systemctl status skillforge.service
```

---

## PART 5: DEPLOYMENT OPTION C - DIGITALOCEAN APP PLATFORM

### Setup (Easiest Managed Option)

```bash
# 1. Go to https://www.digitalocean.com/products/app-platform
# 2. Click "Create App"
# 3. Connect GitHub repository
# 4. Configure services:
#
#    Backend (Web Service):
#    - Docker build: Dockerfile.backend
#    - HTTP Port: 8001
#    - Environment: POSTGRES_URL, JWT_SECRET_KEY, etc.
#
#    Frontend (Web Service):
#    - Docker build: Dockerfile.frontend
#    - Environment: NEXT_PUBLIC_API_BASE=http://backend-service:8001
#
#    Database: PostgreSQL 15
#    Redis: Cache service
#
# 5. Click "Deploy" → Wait 10-15 minutes
# 6. Automatic deployments on git push!
```

---

## PART 6: POST-DEPLOYMENT TASKS

### 6.1 Monitor Application

```bash
# Setup health checks
# For each service, configure:
# - Health check endpoint: /healthz
# - Check frequency: every 30 seconds
# - Restart if unhealthy

# Monitor logs
# For Render: View in dashboard
# For DigitalOcean: docker-compose logs -f

# Setup alerts (optional but recommended)
# - Email on service down
# - Slack notifications
# - SMS on critical errors
```

### 6.2 Backup Strategy

```bash
# Automated database backups every 6 hours
# Keep 30 days of backups

# For Render: Built-in (via dashboard)
# For DigitalOcean: Use DigitalOcean backups ($2-3/mo)

# Manual backup (run weekly)
docker-compose exec postgres pg_dump \
    -U admin skillforge > \
    backup_$(date +%Y%m%d_%H%M%S).sql

# Store backups off-site (AWS S3, DigitalOcean Spaces)
```

### 6.3 Setup Logging

```bash
# Centralized logging (for debugging)
# Option 1: Papertrail (free tier available)
# Option 2: LogRocket (for frontend errors)
# Option 3: ELK Stack (self-hosted)

# Add to backend/main.py:
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 6.4 Performance Optimization

```bash
# 1. Enable database query caching
# Redis connected ✓

# 2. Implement API caching
@app.get("/api/v1/courses")
@cache_decorator(ttl=3600)  # Cache for 1 hour
async def get_courses():
    ...

# 3. Enable CDN (Cloudflare Free)
# - Improves page load speed
# - Provides DDoS protection
# - Free SSL

# 4. Compress responses
# In nginx.conf:
gzip on;
gzip_types text/plain text/css application/json;
```

### 6.5 Setup CI/CD for Continuous Deployment

```bash
# GitHub Actions already configured
# Push to GitHub → Auto-deploys to production

# For Render: Automatic on commit
# For DigitalOcean: Setup webhook

# Workflows:
# 1. Lint code
# 2. Run tests
# 3. Build Docker images
# 4. Push to registry
# 5. Trigger deployment
```

---

## PART 7: TROUBLESHOOTING DEPLOYMENT

### Issue: "502 Bad Gateway"

```bash
# Problem: Backend not responding

# Cause 1: Container crashed
docker-compose ps
# Check if backend status shows "unhealthy"

# Cause 2: Out of memory
docker stats  # Monitor resource usage

# Cause 3: Database connection failed
docker-compose logs backend | grep -i "database\|connection"

# Fix:
docker-compose restart skillforge-backend
```

### Issue: "Application startup complete" but API returns 404

```bash
# Problem: Routes not loading

# Check logs
docker-compose logs backend | tail -50

# Look for: "Including router..."
# If missing, admin.py might have import error

# Fix: Check admin.py has get_current_superadmin function
grep -n "get_current_superadmin" backend/app/api/v1x/admin.py
```

### Issue: Frontend shows "Cannot reach backend"

```bash
# Problem: Frontend can't connect to API

# Cause 1: Wrong API URL
# Check frontend .env or hardcoded URL
NEXT_PUBLIC_API_BASE=http://backend:8001  # Local
NEXT_PUBLIC_API_BASE=https://api.example.com  # Production

# Cause 2: CORS error
# Check backend/app/core/config.py
# Ensure frontend domain in ALLOWED_ORIGINS

# Fix:
docker-compose build --no-cache frontend
docker-compose restart frontend
```

### Issue: Database migrations fail on deploy

```bash
# Problem: New column/table not created

# Check model files updated
git diff HEAD~1 backend/app/modelsx/

# Ensure import in main.py
grep "from.*modelsx" backend/app/main.py

# Force table recreation
docker-compose exec postgres drop table course;
docker-compose restart backend  # Recreates table
```

---

## PART 8: MAINTENANCE SCHEDULE

### Daily
- [ ] Check uptime/status page
- [ ] Review error logs
- [ ] Verify backups running

### Weekly
- [ ] Review performance metrics
- [ ] Check disk space usage
- [ ] Test recovery from backup

### Monthly
- [ ] Security updates (OS, packages)
- [ ] SSL certificate renewal (auto)
- [ ] Database optimization (VACUUM, ANALYZE)
- [ ] Review and update monitoring

### Quarterly
- [ ] Load testing
- [ ] Security audit
- [ ] Disaster recovery drill
- [ ] Cost optimization review

---

## PART 9: COST BREAKDOWN

### Option A: Render.com (Recommended First Choice)

```
Services           Monthly Cost
─────────────────────────────
Backend (Web)      $7 (auto-scales to $115+)
Frontend (Static)  $0 (free tier)
PostgreSQL DB      $7
Redis              $5
─────────────────────────────
Total              $19/month

Plus costs if scaling (auto-scales with traffic)
```

### Option B: DigitalOcean VPS (Budget Choice)

```
Services           Monthly Cost
─────────────────────────────
VPS (2GB/$6)       $6
PostgreSQL         Included
Redis              Included
DNS                Free
SSL                Free
─────────────────────────────
Total              $6/month

Plus: Backups $0.50/mo, Monitoring $0.50/mo
Estimated: $7-10/month
```

### Option C: DigitalOcean App Platform (Balanced)

```
Services           Monthly Cost
─────────────────────────────
Backend Web        $12
Frontend Web       $12
PostgreSQL DB      $15
Redis              $5
─────────────────────────────
Total              $44/month

Auto-scaling handled, easier than VPS
```

---

## FINAL DEPLOYMENT CHECKLIST

- [ ] Code committed to GitHub
- [ ] .env configured with production secrets
- [ ] Database created and seeded
- [ ] Domain name obtained (or using default URL)
- [ ] SSL certificate obtained (auto via platform)
- [ ] Backend deployed and API responding 200 OK
- [ ] Frontend deployed and loads without errors
- [ ] Database backups configured
- [ ] Monitoring/alerts set up
- [ ] Admin user created in production DB
- [ ] Load testing completed (traffic simulated)
- [ ] Incident response plan documented
- [ ] Team access to production systems set up

---

## QUICK DEPLOYMENT COMMAND REFERENCE

```bash
# Render (Automatic on push to main)
git push origin main
# Watch dashboard for auto-deployment

# DigitalOcean VPS Manual
ssh root@XXX.XXX.XXX.XXX
cd /opt/skillforge-global
sudo git pull origin main
sudo docker-compose build --no-cache
sudo docker-compose up -d

# DigitalOcean App (Automatic on push)
git push origin main
# Watch app dashboard for deployment
```

---

## NEXT STEPS AFTER DEPLOYMENT

1. **Test thoroughly**: Every feature accessible to users
2. **Setup monitoring**: Alerts on errors/downtime
3. **Plan maintenance**: Schedule updates, backups
4. **Document processes**: Runbooks for common issues
5. **Iterate**: Track user feedback, deploy improvements
6. **Scale**: Monitor growth, upgrade as needed

---

## SUPPORT & RESOURCES

- **Render docs**: https://render.com/docs
- **DigitalOcean docs**: https://docs.digitalocean.com
- **Docker docs**: https://docs.docker.com
- **Let's Encrypt**: https://letsencrypt.org
- **Cloudflare CDN**: https://dash.cloudflare.com

---

**Estimated time to deploy**: 30 minutes (Render) to 2 hours (DigitalOcean VPS)

**Estimated monthly cost**: $6-20 (depending on traffic and platform choice)

**Go live and celebrate! 🎉**
