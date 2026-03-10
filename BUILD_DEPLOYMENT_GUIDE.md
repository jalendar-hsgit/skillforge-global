# SkillForge Global - Complete Build & Deployment Guide

**Last Updated:** March 10, 2026  
**Project Status:** Production Ready - Full Stack Payment & Marketplace System  
**Version:** 1.0.0

---

## 📋 Quick Start (Choose Your Path)

### Option A: Local Development (Recommended for Testing)

```bash
# 1. Copy environment template
cp .env.example .env.local

# 2. Start everything with Docker
docker-compose up -d

# 3. Access the application
Frontend:  http://localhost:3000
Backend:   http://localhost:8001
Database:  localhost:5432 (Adminer at http://localhost:8080)

# 4. View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Option B: AWS Production Deployment

```bash
# 1. Read complete deployment guide
cat DEPLOYMENT_GUIDE_AWS.md

# 2. Configure AWS
aws configure  # Set your access keys

# 3. Deploy backend
chmod +x scripts/deploy-backend.sh
./scripts/deploy-backend.sh prod

# 4. Deploy frontend
chmod +x scripts/deploy-frontend.sh
./scripts/deploy-frontend.sh prod s3

# 5. Verify deployment
curl https://api.skillforge.com/api/v1/health
curl https://skillforge.com
```

### Option C: Manual Local Build

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload

# Frontend (in new terminal)
npm install
npm run dev

# Visit http://localhost:3000
```

---

## 🏗️ Project Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    SkillForge Global                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐           │
│  │  Frontend Layer  │         │  Backend Layer   │           │
│  │                  │         │                  │           │
│  │  Next.js/React   │◄───────►│  FastAPI/Python  │           │
│  │  TypeScript      │  REST   │  SQLAlchemy ORM  │           │
│  │  Tailwind CSS    │  JSON   │  Pydantic        │           │
│  │                  │         │                  │           │
│  │ • Marketplace    │         │ • Auth Routes    │           │
│  │ • Cart/Checkout  │         │ • Payment Routes │           │
│  │ • Admin Panel    │         │ • Marketplace    │           │
│  │ • User Profile   │         │ • Admin API      │           │
│  └──────────────────┘         └──────────────────┘           │
│         │                             │                       │
│         │                             ▼                       │
│         │                    ┌──────────────────┐             │
│         │                    │  Data Layer      │             │
│         └───────────────────►│                  │             │
│                              │  SQLite (Dev)    │             │
│                              │  PostgreSQL (Prod)             │
│                              │                  │             │
│                              │ • Users          │             │
│                              │ • Courses        │             │
│                              │ • Orders         │             │
│                              │ • Payments       │             │
│                              │ • Mentors        │             │
│                              │ • Products       │             │
│                              └──────────────────┘             │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           External Integrations                           │ │
│  │  • Stripe (Payment Processing)                            │ │
│  │  • JWT (Authentication)                                   │ │
│  │  • CORS (Cross-origin Requests)                          │ │
│  │  • CloudWatch (Monitoring)                               │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Next.js | 14.x | React framework |
| | TypeScript | 5.x | Type safety |
| | Tailwind CSS | 3.x | Styling |
| | Stripe.js | Latest | Payment UI |
| **Backend** | FastAPI | 0.104+ | REST API |
| | Python | 3.11+ | Language |
| | SQLAlchemy | 2.x | ORM |
| | Pydantic | 2.x | Data validation |
| | Uvicorn | 0.24+ | ASGI server |
| **Database** | SQLite | Latest | Development |
| | PostgreSQL | 14+ | Production |
| **Deployment** | Docker | 24.x | Containerization |
| | AWS | Various | Cloud infrastructure |
| **Testing** | Pytest | 7.x | Backend tests |
| | Jest | 29.x | Frontend tests |

---

## 📦 Build Process Matrix

### Build Type Comparison

| Build Type | Environment | Command | Time | Output |
|-----------|-------------|---------|------|--------|
| **Docker Local** | Development | `docker-compose up` | 3-5 min | Running containers |
| **Local Dev** | Development | Manual setup | 10-15 min | Running servers |
| **Production Build** | Production | `npm run build` + `deploy-*` | 5-10 min | Optimized artifacts |
| **Docker Production** | Production | Docker build | 8-12 min | Production image |

---

## 🚀 Deployment Strategies

### Strategy 1: Docker + AWS ECS (Recommended)

**Pros:**
- Consistent environments
- Easy horizontal scaling
- Automatic health checks
- Built-in load balancing

**Steps:**
```bash
# 1. Build Docker images
docker build -f Dockerfile.backend -t skillforge-backend:latest .
docker build -f Dockerfile.frontend -t skillforge-frontend:latest .

# 2. Push to AWS ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag skillforge-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:latest

# 3. Deploy via ECS/Fargate
aws ecs create-service --cluster skillforge --service-name backend --task-definition skillforge-backend:1
```

### Strategy 2: EC2 + Auto Scaling (Traditional)

**Pros:**
- More control
- Cheaper for consistent load
- Full SSH access
- Custom configurations

**Steps:**
```bash
# 1. Launch EC2 instance
aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 --instance-type t3.medium

# 2. Configure instance
ssh -i key.pem ec2-user@instance-ip
git clone repo && cd repo
./scripts/deploy-backend.sh prod

# 3. Set up auto-scaling
aws autoscaling create-auto-scaling-group --auto-scaling-group-name skillforge-asg
```

### Strategy 3: Vercel + AWS Lambda (Serverless)

**Pros:**
- Zero server management
- Auto-scaling
- Pay per use
- Fast deployments

**Steps:**
```bash
# Frontend to Vercel
npm install -g vercel
vercel --prod

# Backend to Lambda (optional)
serverless deploy
```

---

## 📊 Complete Build Checklist

### Pre-Build Phase
- [ ] **Code Quality**
  - [ ] All tests pass: `pytest backend/tests/ -v`
  - [ ] Frontend builds: `npm run build`
  - [ ] No ESLint errors: `npm run lint`
  - [ ] Git commits clean: `git status`

- [ ] **Security**
  - [ ] Environment variables configured
  - [ ] Database credentials secure
  - [ ] Stripe keys verified (production vs test)
  - [ ] SSL certificates ready
  - [ ] Security audit completed

- [ ] **Dependencies**
  - [ ] `pip install -r backend/requirements.txt`
  - [ ] `npm ci` (instead of install)
  - [ ] All versions pinned
  - [ ] No security vulnerabilities

### Build Phase

#### Backend Build
```bash
cd backend

# 1. Activate virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python init_db.py

# 4. Run tests
pytest tests/ -v --cov=app

# 5. Compile/optimize
python -m py_compile app/main.py

# 6. Build Docker image (if using containers)
docker build -f ../Dockerfile.backend -t skillforge-backend:latest ..
```

#### Frontend Build
```bash
# 1. Install dependencies
npm ci

# 2. Run linter
npm run lint

# 3. Build application
npm run build

# 4. Test production build locally
npm run start

# 5. Build Docker image (if using containers)
docker build -f Dockerfile.frontend -t skillforge-frontend:latest .
```

### Post-Build Phase

- [ ] **Verification**
  - [ ] Docker images built successfully
  - [ ] All tests passing
  - [ ] Build artifacts generated
  - [ ] File sizes within limits
  - [ ] No console warnings/errors

- [ ] **Performance**
  - [ ] Frontend bundle size < 500KB
  - [ ] API response time < 500ms
  - [ ] Database queries optimized
  - [ ] Images optimized

- [ ] **Security**
  - [ ] Dependencies scanned: `npm audit`, `pip audit`
  - [ ] Secrets not in code
  - [ ] HTTPS configured
  - [ ] CORS properly configured

### Deployment Phase

- [ ] **AWS Infrastructure**
  - [ ] EC2 instance running
  - [ ] RDS database initialized
  - [ ] Security groups configured
  - [ ] IAM roles assigned
  - [ ] CloudWatch monitoring enabled

- [ ] **Application Deployment**
  - [ ] Backend deployed and running
  - [ ] Frontend deployed and accessible
  - [ ] Database migrations completed
  - [ ] Health checks passing

- [ ] **Post-Deployment Testing**
  - [ ] Frontend loads (http://localhost:3000)
  - [ ] Can register user
  - [ ] Can login
  - [ ] Can view marketplace
  - [ ] Can add to cart
  - [ ] Can complete payment (test)
  - [ ] Admin panel accessible
  - [ ] No 404 errors
  - [ ] API responding

---

## 🐳 Docker Build & Run Commands

### Building Images Locally

```bash
# Backend image
docker build -f Dockerfile.backend -t skillforge-backend:1.0.0 .

# Frontend image
docker build -f Dockerfile.frontend -t skillforge-frontend:1.0.0 .

# Verify images
docker images | grep skillforge
```

### Running with Docker Compose (Development)

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend
docker-compose up -d frontend

# View logs
docker-compose logs -f backend --tail=100
docker-compose logs -f frontend --tail=100

# Run commands in container
docker-compose exec backend python init_db.py
docker-compose exec backend python seed_all_demo_data.py

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Running Standalone Containers

```bash
# Backend
docker run -d \
  -e DATABASE_URL=postgresql://user:pass@localhost/skillforge \
  -e STRIPE_SECRET_KEY=sk_test_... \
  -p 8001:8001 \
  skillforge-backend:1.0.0

# Frontend
docker run -d \
  -e NEXT_PUBLIC_API_BASE=http://localhost:8001 \
  -p 3000:3000 \
  skillforge-frontend:1.0.0
```

### Pushing to AWS ECR

```bash
# Create ECR repositories
aws ecr create-repository --repository-name skillforge-backend
aws ecr create-repository --repository-name skillforge-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag images
docker tag skillforge-backend:1.0.0 $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:1.0.0
docker tag skillforge-frontend:1.0.0 $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/skillforge-frontend:1.0.0

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:1.0.0
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/skillforge-frontend:1.0.0

# Verify
aws ecr list-images --repository-name skillforge-backend
```

---

## 📈 Performance Optimization

### Backend Optimization

```python
# 1. Connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
)

# 2. Query optimization
from sqlalchemy.orm import joinedload
courses = db.query(Course).options(joinedload(Course.author)).all()

# 3. Caching
from functools import lru_cache
@lru_cache(maxsize=128)
def get_course_categories():
    return db.query(distinct(Course.category)).all()

# 4. Async support
from fastapi import BackgroundTasks
@app.post("/orders")
async def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_payment, order) 
    return {"status": "processing"}

# 5. Pagination
@app.get("/courses")
async def list_courses(skip: int = 0, limit: int = 10):
    return db.query(Course).offset(skip).limit(limit).all()
```

### Frontend Optimization

```javascript
// 1. Code splitting
import dynamic from 'next/dynamic';
const Marketplace = dynamic(() => import('../pages/marketplace'), {
  loading: () => <p>Loading...</p>,
});

// 2. Image optimization
import Image from 'next/image';
<Image src="/course.jpg" alt="Course" width={400} height={300} />

// 3. Lazy loading
const IntersectionObserver = require('intersection-observer');
<Suspense fallback={<div>Loading...</div>}>
  <CourseList />
</Suspense>

// 4. Caching
const cacheConfig = {
  revalidate: 3600,  // ISR: revalidate every hour
};

// 5. Bundle analysis
npm install -D @next/bundle-analyzer
```

---

## 🔒 Security Checklist

Before going live, ensure:

```
Security Verification Checklist
================================

[ ] Authentication
    [ ] JWT tokens implemented
    [ ] Password hashing (bcrypt)
    [ ] Session management
    [ ] Rate limiting enabled

[ ] Data Security
    [ ] Environment variables not in code
    [ ] Database credentials encrypted
    [ ] API keys secured (Stripe, etc)
    [ ] SSL/TLS enabled
    [ ] HTTPS redirects

[ ] API Security
    [ ] CORS properly configured
    [ ] Input validation on all endpoints
    [ ] SQL injection prevention (SQLAlchemy parameterization)
    [ ] XSS protection (CSP headers)
    [ ] CSRF tokens implemented

[ ] Infrastructure
    [ ] Security groups restricted
    [ ] IAM roles least-privilege
    [ ] CloudWatch logging enabled
    [ ] Backup strategy implemented
    [ ] DDoS protection (CloudFront)

[ ] Compliance
    [ ] GDPR compliant (if EU users)
    [ ] PCI DSS (payment processing)
    [ ] Data retention policies
    [ ] Privacy policy published
    [ ] Terms of service agreed

[ ] Monitoring
    [ ] Error tracking enabled
    [ ] Performance monitoring
    [ ] Security alerts configured
    [ ] Log aggregation setup
```

---

## 📞 Support & Resources

### Documentation
- [AWS Deployment Guide](./DEPLOYMENT_GUIDE_AWS.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Stripe Docs](https://stripe.com/docs)

### Commands Reference

```bash
# Development
npm run dev              # Start frontend dev server
python uvicorn ...      # Start backend dev server
docker-compose up       # Start all services

# Building
npm run build          # Build Next.js
python -m build        # Build Python package
docker build ...       # Build Docker image

# Deployment
./scripts/deploy-backend.sh prod    # Deploy backend to AWS
./scripts/deploy-frontend.sh prod s3  # Deploy frontend to S3
aws cloudfront create-invalidation  # Invalidate CDN

# Maintenance
docker system prune    # Clean up Docker resources
git log --oneline      # View commit history
pytest backend/tests/  # Run tests
```

### Contact & Escalation
- **Technical Issues**: Check CloudWatch logs and application logs
- **Database Issues**: Use pgAdmin (port 5050) for inspection
- **Payment Issues**: Check Stripe dashboard for webhook events
- **Performance Issues**: Use CloudWatch metrics and X-Ray tracing

---

## ✅ Final Deployment Verification

After deployment, run this checklist:

```bash
# 1. API Health
curl https://api.skillforge.com/api/v1/health

# 2. Frontend Accessible  
curl -I https://skillforge.com

# 3. Database Connected
# (SSH into EC2 and check logs)
sudo journalctl -u skillforge -n 20

# 4. Payment Test
# Test a transaction in Stripe test mode

# 5. Email Verification
# Trigger an order and verify email sent

# 6. Admin Access
# Login to admin panel and verify metrics

# 7. Monitor Logs
aws logs tail /skillforge/backend -f

# 8. Alert Configuration
aws cloudwatch describe-alarms
```

**If all checks pass, deployment is successful! 🎉**

---

## 📅 Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Database Backup | Daily | `aws rds create-db-snapshot ...` |
| Log Analysis | Daily | `aws logs filter-log-events ...` |
| Security Updates | Weekly | `pip audit`, `npm audit` |
| Performance Review | Weekly | CloudWatch dashboard |
| Library Updates | Monthly | `pip list --outdated`, `npm outdated` |
| Full System Backup | Monthly | `aws s3 sync ...` |
| Disaster Recovery Test | Quarterly | Test from backup |

---

**Document Version:** 1.0.0  
**Last Updated:** March 10, 2026  
**Next Review Date:** June 10, 2026

For changes or updates to this guide, submit a pull request to the main repository. 

