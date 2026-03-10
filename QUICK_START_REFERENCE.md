# SkillForge Global - Quick Reference Guide

## 🚀 Start Here (Pick One)

### 1️⃣ Quick Local Start (5 minutes)
```bash
docker-compose up -d
# Visit: http://localhost:3000
# API: http://localhost:8001
```

### 2️⃣ Deploy to AWS Production
```bash
aws configure
./scripts/deploy-backend.sh prod
./scripts/deploy-frontend.sh prod s3
# Verify: https://api.skillforge.com/api/v1/health
```

### 3️⃣ Manual Local Setup
```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python init_db.py
uvicorn app.main:app --reload

# Frontend (new terminal)
npm install && npm run dev
```

---

## 📋 Essential Commands

### 🐳 Docker Commands
```bash
# Start all services
docker-compose up -d

# View specific logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Run database seeding
docker-compose exec backend python seed_all_demo_data.py

# Remove all data (clean slate)
docker-compose down -v
```

### 🔄 Development Servers
```bash
# Backend (from backend/ directory)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Frontend (from root)
npm run dev

# Both together
npm run dev  # Runs both via package.json script
```

### 🧪 Testing
```bash
# Backend tests
pytest backend/tests/ -v
pytest backend/tests/test_payments.py -v  # Specific test
pytest --cov=app backend/tests/           # With coverage

# Frontend tests
npm test                    # Jest
npm run cypress             # E2E tests
```

### 📦 Building
```bash
# Frontend production build
npm run build
npm start              # Run production build locally

# Backend (Python doesn't require build)
python -m py_compile app/main.py  # Syntax check

# Docker images
docker build -f Dockerfile.backend -t skillforge-backend:latest .
docker build -f Dockerfile.frontend -t skillforge-frontend:latest .
```

### 🌍 Deployment
```bash
# AWS EC2 deployment
./scripts/deploy-backend.sh prod
./scripts/deploy-frontend.sh prod s3

# Verify deployment
curl https://api.skillforge.com/api/v1/health
curl https://skillforge.com

# View live logs
aws logs tail /skillforge/backend -f

# Rollback (if needed)
./scripts/deploy-backend.sh prod --rollback
```

### 💾 Database Operations
```bash
# Initialize database
python backend/init_db.py

# Seed demo data
python backend/seed_all_demo_data.py

# Access database (SQLite local)
sqlite3 backend/app/data/skillforge.db

# Access database (PostgreSQL)
psql -h localhost -U admin -d skillforge

# Backup RDS
aws rds create-db-snapshot \
  --db-instance-identifier skillforge-prod-db \
  --db-snapshot-identifier skillforge-backup-$(date +%Y%m%d)
```

### 🔧 Git Operations
```bash
# Check status
git status

# Commit changes
git add -A
git commit -m "Feature: description of changes"

# View history
git log --oneline -10

# Create feature branch
git checkout -b feature/new-feature

# Push to production
git push origin main

# Deploy after push
./scripts/deploy-backend.sh prod
```

### 🔍 Debugging & Logs
```bash
# Backend logs (local)
tail -f /var/log/skillforge/app.log

# Backend logs (Docker)
docker-compose logs -f backend

# Backend logs (AWS)
aws logs tail /skillforge/backend --follow

# Frontend console logs
# Open browser DevTools: F12 or Cmd+Option+I

# API testing
curl http://localhost:8001/api/v1/health
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@skillforge.com","password":"password"}'

# Check port usage
lsof -i :8001      # MacOS/Linux
netstat -ano | findstr :8001  # Windows
```

---

## 🎯 Common Tasks

### Add New Course
```bash
# Via database
sqlite3 backend/app/data/skillforge.db
INSERT INTO courses (path, title, description, price, is_paid, difficulty_level) 
VALUES ('new-course', 'New Course', 'Description', 99.99, true, 'Intermediate');

# Via API
curl -X POST http://localhost:8001/api/v1x/admin/courses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "new-course",
    "title": "New Course",
    "description": "Description",
    "price": 99.99,
    "is_paid": true
  }'
```

### Create Test Payment
```bash
# Use Stripe test card in frontend:
# Card: 4242 4242 4242 4242
# Exp: 12/25
# CVC: 123
# Stripe test mode: Active by default

# Verify in Stripe dashboard
# https://dashboard.stripe.com (test mode)
```

### Monitor Performance
```bash
# AWS CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Average

# Database performance
EXPLAIN ANALYZE SELECT * FROM marketplace_courses;

# Frontend performance
npm run build  # Check bundle size
npm run analyze  # Bundle analysis
```

### Fix Common Issues

**"No courses found" on marketplace**
```bash
# Check if courses exist
sqlite3 backend/app/data/skillforge.db "SELECT COUNT(*) FROM marketplace_courses;"

# Check API endpoint
curl http://localhost:8001/api/v1x/marketplace/courses

# Restart frontend and clear cache
docker-compose restart frontend
# Or: Clear browser cache (Ctrl+Shift+Delete)
```

**Database connection error**
```bash
# Check database is running
docker-compose ps

# Start database
docker-compose up -d postgres

# Verify connection
docker-compose exec postgres psql -U admin -d skillforge -c "SELECT 1;"
```

**Payment not working**
```bash
# Check Stripe keys
grep STRIPE_ backend/.env.production

# Verify webhook
aws logs tail /skillforge/webhooks -f

# Test payment flow
curl http://localhost:8001/api/v1x/test-payment \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Frontend won't load**
```bash
# Check build
ls -la .next/

# Rebuild
npm run build
npm start

# Check API connection
curl http://localhost:8001/api/v1/health
```

---

## 📊 Project Structure

```
skillforge-global/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── api/
│   │   │   ├── v1/                 # Legacy endpoints
│   │   │   └── v1x/                # Current: payments, marketplace, admin
│   │   ├── modelsx/                # Database models (40+)
│   │   ├── schemas/                # Validation schemas
│   │   ├── services/               # Business logic
│   │   └── data/
│   │       └── skillforge.db       # SQLite (development)
│   ├── tests/                      # Test suite
│   ├── init_db.py                  # Database initialization
│   ├── seed_all_demo_data.py       # Demo data seeding
│   └── requirements.txt            # Python dependencies
│
├── src/                            # Next.js frontend
│   ├── pages/
│   │   ├── marketplace/            # Course marketplace
│   │   ├── admin/                  # Admin dashboard
│   │   ├── auth/                   # Authentication pages
│   │   └── api/                    # API routes (optional)
│   ├── components/                 # React components
│   ├── hooks/                      # Custom hooks
│   ├── lib/                        # Utilities
│   │   ├── api.ts                  # API client
│   │   └── stripe.ts               # Stripe integration
│   └── public/                     # Static assets
│
├── scripts/
│   ├── deploy-backend.sh           # Backend deployment
│   └── deploy-frontend.sh          # Frontend deployment
│
├── docker-compose.yml              # Local development
├── Dockerfile.backend              # Backend container
├── Dockerfile.frontend             # Frontend container
├── BUILD_DEPLOYMENT_GUIDE.md       # This file + more
├── DEPLOYMENT_GUIDE_AWS.md         # Complete AWS guide
├── package.json                    # Frontend dependencies
└── .env.local                      # Environment variables (dev)
```

---

## 🌐 URLs Reference

### Local Development
```
Frontend:     http://localhost:3000
Backend API:  http://localhost:8001
Database:     localhost:5432 (Adminer: http://localhost:8080)
PgAdmin:      http://localhost:5050
Logs:         docker-compose logs -f
```

### Production (AWS)
```
Frontend:     https://skillforge.com
Backend API:  https://api.skillforge.com
Status Page:  https://status.skillforge.com
Admin Panel:  https://admin.skillforge.com
```

### Key API Endpoints
```
GET    /api/v1/health                           # Health check
POST   /api/v1/auth/register                    # Sign up
POST   /api/v1/auth/login                       # Sign in
GET    /api/v1x/marketplace/courses             # List courses
GET    /api/v1x/marketplace/courses/{id}        # Course details
POST   /api/v1x/marketplace/cart                # Add to cart
POST   /api/v1x/payments/create-intent          # Create payment
POST   /api/v1x/payments/stripe-webhook         # Stripe webhook
GET    /api/v1x/admin/dashboard                 # Admin metrics
POST   /api/v1x/admin/courses                   # Add course (admin)
```

---

## 💰 Cost Estimation

### AWS Monthly (Production)
- EC2: $40 (t3.medium)
- RDS: $80 (db.t3.small)
- CloudFront/S3: $95 (CDN + storage)
- Misc (ALB, CloudWatch, DNS): $40
- **Total: ~$255/month**

### Optional Optimizations
- Use Reserved Instances: -40% savings
- Use Spot Instances: -70% savings  
- Use VPC endpoints: Additional cost reduction
- Consolidate databases: -$40/month

---

## 🆘 Need Help?

### Logs & Debugging
```bash
# Backend errors
docker-compose logs backend | grep ERROR

# Frontend errors  
docker-compose logs frontend | grep ERROR

# Database errors
docker-compose logs postgres

# All services
docker-compose logs -f
```

### Status Check
```bash
# All services running?
docker-compose ps

# All tests passing?
pytest backend/tests/ -q

# Frontend builds?
npm run build

# No linting errors?
npm run lint
```

### Support Resources
- 📖 [AWS Deployment Guide](./DEPLOYMENT_GUIDE_AWS.md)
- 📖 [Complete Build & Deploy Guide](./BUILD_DEPLOYMENT_GUIDE.md)
- 🔗 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🔗 [Next.js Documentation](https://nextjs.org/docs)
- 🔗 [Stripe Documentation](https://stripe.com/docs)

---

## ✅ Pre-Deployment Checklist

Before going live:

```
Code Quality
[ ] All tests pass: pytest backend/tests/ && npm test
[ ] Linting clean: npm run lint
[ ] Build succeeds: npm run build
[ ] No console errors (F12)

Security
[ ] Secrets not in code
[ ] Environment variables set
[ ] SSL/HTTPS enabled
[ ] CORS configured
[ ] Database credentials secure

Performance  
[ ] API < 500ms response time
[ ] Frontend bundle < 500KB
[ ] Database queries optimized
[ ] Images optimized

Functionality
[ ] Can register user
[ ] Can login
[ ] Can view courses
[ ] Can add to cart
[ ] Can complete payment
[ ] Can view orders
[ ] Admin panel works
[ ] Webhooks configured

Infrastructure
[ ] AWS resources created
[ ] Databases initialized
[ ] Backups configured
[ ] Monitoring enabled
[ ] Alerts configured
```

---

**Quick Links:** [Build Guide](./BUILD_DEPLOYMENT_GUIDE.md) | [AWS Deploy](./DEPLOYMENT_GUIDE_AWS.md) | [GitHub](https://github.com/YOUR_ORG/skillforge-global)

**Version:** 1.0.0 | **Updated:** March 10, 2026
