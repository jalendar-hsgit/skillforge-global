# SkillForge Global - Complete AWS Deployment Guide

**Last Updated:** March 10, 2026  
**Project Status:** Production Ready  
**Version:** 1.0.0-production

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Build Process](#local-build-process)
3. [AWS Infrastructure Setup](#aws-infrastructure-setup)
4. [Backend Deployment (FastAPI)](#backend-deployment-fastapi)
5. [Frontend Deployment (Next.js)](#frontend-deployment-nextjs)
6. [Database Setup (RDS/SQLite)](#database-setup)
7. [Stripe Integration](#stripe-integration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Scaling & Performance](#scaling--performance)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing locally: `pytest backend/tests/`
- [ ] Frontend builds without errors: `npm run build`
- [ ] No console errors in browser (F12)
- [ ] All git changes committed: `git status` is clean
- [ ] Code reviewed and approved
- [ ] Security audit completed

### Environment Variables
- [ ] Production `.env.production` files created (separate from dev)
- [ ] Database credentials secure
- [ ] Stripe keys for production obtained
- [ ] AWS credentials configured
- [ ] CORS settings configured for production domain

### AWS Account Requirements
- [ ] AWS account with billing enabled
- [ ] IAM user with appropriate permissions
- [ ] AWS CLI installed and configured: `aws configure`
- [ ] EC2, RDS, S3, CloudFront, Route53 access enabled

### External Resources
- [ ] Production Stripe account created (not test mode)
- [ ] Domain name registered (Route53 or external registrar)
- [ ] SSL/TLS certificate obtained (free via ACM)

---

## Local Build Process

### Prerequisites
```bash
# Node.js and npm
node --version  # v18+ required
npm --version   # v9+ required

# Python
python --version  # v3.10+ required
```

### Backend Build

```bash
cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create production database (optional - can use managed RDS)
python init_db.py

# 3. Seed demo data (optional - for testing only)
python seed_all_demo_data.py

# 4. Run tests
pytest tests/ -v

# 5. Check for syntax errors
python -m py_compile app/main.py

# 6. Generate requirements.txt with exact versions (if needed)
pip freeze > requirements.txt
```

**Backend Directory Structure:**
```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── api/
│   │   ├── v1/                 # Auth, legacy endpoints
│   │   └── v1x/                # Current version: marketplace, payments, admin
│   ├── modelsx/                # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic validation schemas
│   ├── services/               # Business logic (payments, etc.)
│   └── data/                   # SQLite database (local only)
├── init_db.py                  # Database initialization
├── seed_all_demo_data.py       # Demo data seeding
└── requirements.txt            # Python dependencies
```

### Frontend Build

```bash
cd src (repo root)

# 1. Install dependencies
npm install

# 2. Set production environment variables
cp .env.local .env.production
# Edit .env.production with production URLs

# 3. Build Next.js app
npm run build

# 4. Test production build locally
npm run start

# 5. Check build output
ls -la .next/
```

**Frontend Directory Structure:**
```
src/
├── pages/                      # Next.js pages
│   ├── marketplace/
│   │   ├── index.tsx          # Course listing
│   │   ├── cart.tsx           # Shopping cart
│   │   ├── checkout.tsx       # Payment page
│   │   └── orders.tsx         # Order history
│   ├── admin/                 # Admin dashboard
│   └── api/                   # Backend API routes (optional)
├── components/                # React components
├── hooks/                      # Custom React hooks
├── lib/                        # Utilities (API, Stripe, etc.)
└── public/                     # Static assets
```

### Build Output Verification

```bash
# Backend
ls -la backend/__pycache__     # Should have compiled Python files
python -c "from app.main import app; print('Backend OK')"

# Frontend
ls -la .next/                  # Should have compiled Next.js assets
npm run lint                   # Check for linting errors
```

---

## AWS Infrastructure Setup

### Step 1: Create AWS Resources

#### 1.1 EC2 Instance (Backend)

```bash
# Using AWS Console or CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name skillforge-prod-key \
  --security-groups skillforge-sg \
  --region us-east-1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=skillforge-backend}]'
```

**EC2 Configuration:**
- **Instance Type:** `t3.medium` (1 vCPU, 4GB RAM minimum)
- **OS:** Amazon Linux 2 or Ubuntu 22.04 LTS
- **Storage:** 20GB gp3 SSD
- **Security Group:** Allow inbound port 8001 (from ALB only)
- **IAM Role:** Attach policies for RDS access, CloudWatch logs, S3 (if needed)

#### 1.2 RDS Database (PostgreSQL)

```bash
aws rds create-db-instance \
  --db-instance-identifier skillforge-prod-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --storage-type gp3 \
  --backup-retention-period 30 \
  --publicly-accessible false \
  --db-name skillforge
```

**RDS Configuration:**
- **Engine:** PostgreSQL 14+
- **Instance Class:** `db.t3.small` (minimum for production)
- **Storage:** 20GB gp3 (auto-scaling enabled)
- **Backup:** Daily automated backups (30 days retention)
- **Multi-AZ:** Enabled for high availability
- **Security Group:** Only allow inbound from EC2 instance

#### 1.3 CloudFront Distribution (Frontend)

```bash
# Frontend hosted on S3 with CloudFront CDN
aws s3 mb s3://skillforge-frontend-prod

aws cloudfront create-distribution \
  --origin-domain-name skillforge-frontend-prod.s3.amazonaws.com \
  --default-root-object index.html
```

**CloudFront Configuration:**
- **Origin:** S3 bucket with OAI (Origin Access Identity)
- **Caching:** 
  - HTML: 300 seconds (TTL)
  - JS/CSS: 31536000 seconds (1 year)
  - Images: 2592000 seconds (30 days)
- **Compress:** Enable for JSON, JS, CSS
- **Security:** Redirect HTTP → HTTPS

#### 1.4 Application Load Balancer (ALB)

```bash
aws elbv2 create-load-balancer \
  --name skillforge-alb \
  --subnets subnet-xxxxxxxx subnet-xxxxxxxx \
  --security-groups sg-xxxxxxxx \
  --scheme internet-facing \
  --type application
```

**ALB Configuration:**
- **Ports:** 80 (HTTP), 443 (HTTPS)
- **Targets:** EC2 instance running FastAPI
- **Health Check:** Every 30 seconds to `/api/v1/health` endpoint
- **SSL Certificate:** ACM managed certificate

### Step 2: Set Up IAM Roles and Permissions

```bash
# Create IAM role for EC2 instances
aws iam create-role \
  --role-name SkillForgeBackendRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name SkillForgeBackendRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

aws iam attach-role-policy \
  --role-name SkillForgeBackendRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
```

### Step 3: Create VPC and Security Groups

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create security groups
aws ec2 create-security-group \
  --group-name skillforge-backend \
  --description "SkillForge Backend Security Group" \
  --vpc-id vpc-xxxxxxxx

# Allow backend port (8001) from ALB
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 8001 \
  --source-security-group-id sg-alb-xxxxxxxx
```

---

## Backend Deployment (FastAPI)

### Step 1: Prepare EC2 Instance

```bash
# SSH into EC2 instance
ssh -i /path/to/skillforge-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

# Update system
sudo yum update -y  # Amazon Linux
# OR
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install dependencies
sudo yum install -y python3.11 git nginx  # Amazon Linux
# OR
sudo apt install -y python3.11 python3-pip git nginx  # Ubuntu

# Install Python packages
python3 -m venv /opt/skillforge/venv
source /opt/skillforge/venv/bin/activate
pip install --upgrade pip
```

### Step 2: Clone and Setup Backend

```bash
# Clone repository
cd /opt/skillforge
git clone https://github.com/YOUR_REPO/skillforge-global.git .

# Install Python dependencies
pip install -r backend/requirements.txt

# Create production environment variables
cat > backend/.env.production << 'EOF'
DATABASE_URL=postgresql://admin:PASSWORD@skillforge-prod-db.xxxx.us-east-1.rds.amazonaws.com:5432/skillforge
STRIPE_SECRET_KEY=sk_live_YOUR_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLIC_KEY
JWT_SECRET_KEY=your-secure-random-key-min-32-chars
ALLOWED_ORIGINS=https://skillforge.com,https://www.skillforge.com
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

# Set permissions
chmod 600 backend/.env.production

# Initialize database (first time only)
cd backend
python init_db.py

# No need to seed demo data in production
```

### Step 3: Configure Gunicorn and Nginx

**Gunicorn Configuration** (`/opt/skillforge/gunicorn_config.py`):
```python
import multiprocessing

bind = "127.0.0.1:8001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 60
keepalive = 5

# Logging
accesslog = "/var/log/skillforge/access.log"
errorlog = "/var/log/skillforge/error.log"
loglevel = "info"

# Process naming
proc_name = "skillforge-backend"
```

**Nginx Configuration** (`/etc/nginx/conf.d/skillforge.conf`):
```nginx
upstream skillforge_backend {
    least_conn;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name YOUR_BACKEND_DOMAIN;

    client_max_body_size 10M;

    location / {
        proxy_pass http://skillforge_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://skillforge_backend/api/v1/health;
        access_log off;
    }
}
```

### Step 4: Create SystemD Service

**File:** `/etc/systemd/system/skillforge.service`
```ini
[Unit]
Description=SkillForge FastAPI Backend
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/opt/skillforge/backend
Environment="PATH=/opt/skillforge/venv/bin"
EnvironmentFile=/opt/skillforge/backend/.env.production
ExecStart=/opt/skillforge/venv/bin/gunicorn \
    --config /opt/skillforge/gunicorn_config.py \
    app.main:app

Restart=always
RestartSec=10

# Resource limits
MemoryMax=2G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
```

**Start the Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable skillforge
sudo systemctl start skillforge
sudo systemctl status skillforge

# Check logs
sudo journalctl -u skillforge -f
```

### Step 5: Database Migration (PostgreSQL)

```bash
# If migrating from SQLite to PostgreSQL
python << 'EOF'
import sqlite3
import psycopg2
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from app.modelsx import *  # Import all models

# Source: SQLite
sqlite_engine = create_engine('sqlite:///app/data/skillforge.db')

# Destination: PostgreSQL
pg_engine = create_engine('postgresql+psycopg2://admin:PASSWORD@RDS_ENDPOINT:5432/skillforge')

# Create tables in PostgreSQL
from app.models.user import User
Base = User.__class__.__bases__[0]  # Get declarative base
Base.metadata.create_all(pg_engine)

# Copy data (if needed)
print("Database migration complete!")
EOF
```

---

## Frontend Deployment (Next.js)

### Option 1: Deploy to Vercel (Recommended for Next.js)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
# - NEXT_PUBLIC_API_BASE=https://api.skillforge.com
# - NEXT_PUBLIC_STRIPE_KEY=pk_live_...
```

### Option 2: Deploy to S3 + CloudFront

```bash
# Build Next.js app (export static)
# Edit next.config.js to enable static export
npm run build

# Upload to S3
aws s3 sync .next/static s3://skillforge-frontend-prod/.next/static --cache-control "public, max-age=31536000, immutable"

aws s3 sync out s3://skillforge-frontend-prod --cache-control "public, max-age=300"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E12345EXAMPLE \
  --paths "/*"
```

**next.config.js for S3 Export:**
```javascript
module.exports = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE,
  },
  images: {
    unoptimized: true,
  },
};
```

### Option 3: Deploy to EC2 with PM2

```bash
# On EC2 instance
sudo npm install -g pm2

cd /opt/skillforge

# Create PM2 ecosystem config
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'skillforge-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/opt/skillforge',
    instances: 'max',
    exec_mode: 'cluster',
    watch: false,
    env: {
      NODE_ENV: 'production',
      NEXT_PUBLIC_API_BASE: 'https://api.skillforge.com',
    }
  }]
};
EOF

# Build and start
npm run build
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## Database Setup

### Option 1: AWS RDS PostgreSQL (Recommended)

```bash
# Create RDS instance (already done in infrastructure setup)

# Update backend database URL
export DATABASE_URL="postgresql://admin:${DB_PASSWORD}@skillforge-prod-db.c9akciq32.us-east-1.rds.amazonaws.com:5432/skillforge"

# Run migrations (if using Alembic)
alembic upgrade head

# Or create tables with SQLAlchemy
python << 'EOF'
from sqlalchemy import create_engine
from app.models import Base

engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(engine)
print("Tables created successfully!")
EOF
```

### Option 2: Keep SQLite (Optional for smaller deployments)

```bash
# Copy SQLite database to S3
aws s3 cp backend/app/data/skillforge.db s3://skillforge-backups/db-backup-$(date +%Y%m%d).db

# For deployment, include in Docker image or backup storage
```

### Database Backup Strategy

```bash
# Create automated RDS backups (already configured)
# Or set up backup scripts

# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier skillforge-prod-db \
  --db-snapshot-identifier skillforge-backup-$(date +%Y%m%d)

# Backup to S3
aws s3 sync /backups/skillforge s3://skillforge-backups/ --delete
```

---

## Stripe Integration

### Production Setup

```bash
# 1. Get production keys from Stripe Dashboard
# - Dashboard: https://dashboard.stripe.com
# - API Keys: Copy both Secret Key and Publishable Key

# 2. Update environment variables
cat > backend/.env.production << 'EOF'
STRIPE_SECRET_KEY=sk_live_YOUR_ACTUAL_SECRET_FROM_STRIPE_DASHBOARD
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_ACTUAL_PUBLIC_FROM_STRIPE_DASHBOARD
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
EOF

# 3. Configure webhook in Stripe Dashboard
# - Settings → Webhooks
# - Endpoint: https://api.skillforge.com/api/v1x/payments/stripe-webhook
# - Events: 
#   - payment_intent.succeeded
#   - payment_intent.payment_failed
#   - charge.refunded
#   - customer.subscription.updated

# 4. Update frontend Stripe key
cat > .env.production << 'EOF'
NEXT_PUBLIC_STRIPE_KEY=pk_live_YOUR_ACTUAL_PUBLIC_FROM_STRIPE_DASHBOARD
EOF
```

### Webhook Setup

```bash
# Test webhook URL
curl -X POST https://api.skillforge.com/api/v1x/payments/stripe-webhook \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: SIGNATURE_VALUE" \
  -d '{"type":"payment_intent.succeeded","data":{}}'

# Check webhook logs
aws logs tail /aws/lambda/skillforge-webhook-handler --follow
```

---

## Monitoring & Logging

### CloudWatch Setup

```bash
# Install CloudWatch agent on EC2
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/skillforge/*",
            "log_group_name": "/skillforge/backend",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "SkillForge",
    "metrics_collected": {
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MemoryUtilization"}
        ]
      },
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DiskUtilization"}
        ]
      }
    }
  }
}
EOF

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

### Application Logging

**Backend Logging Configuration** (`backend/logging.conf`):
```ini
[loggers]
keys=root,skillforge

[handlers]
keys=console,file

[formatters]
keys=detailed

[logger_root]
level=WARNING
handlers=console

[logger_skillforge]
level=INFO
handlers=console,file
qualname=app

[handler_console]
class=StreamHandler
level=INFO
formatter=detailed
args=(sys.stdout,)

[handler_file]
class=handlers.RotatingFileHandler
level=INFO
formatter=detailed
args=('/var/log/skillforge/app.log', 'a', 10485760, 5)

[formatter_detailed]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

### CloudWatch Dashboards

```bash
# Create custom dashboard
aws cloudwatch put-dashboard \
  --dashboard-name SkillForgeDashboard \
  --dashboard-body file://dashboard-config.json
```

---

## Scaling & Performance

### Auto Scaling Group (EC2)

```bash
# Create AMI from configured instance
aws ec2 create-image \
  --instance-id i-0123456789abcdef0 \
  --name skillforge-backend-ami

# Create launch template
aws ec2 create-launch-template \
  --launch-template-name skillforge-backend \
  --launch-template-data file://launch-template.json

# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name skillforge-asg \
  --launch-template LaunchTemplateName=skillforge-backend \
  --min-size 2 \
  --max-size 8 \
  --desired-capacity 3 \
  --load-balancer-names skillforge-alb

# Create scaling policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name skillforge-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://scaling-policy.json
```

### Database Connection Pooling

**Update backend config:**
```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Test connections before using
)
```

### CDN Configuration

```bash
# CloudFront cache optimization
aws cloudfront create-invalidation \
  --distribution-id E2FDTIHK47Z91H \
  --paths "/api/*" "/images/*"

# Set cache headers in Next.js
# next.config.js
module.exports = {
  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 5,
  },
};
```

---

## Complete Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Security audit complete
- [ ] Environment variables configured
- [ ] Database migrated
- [ ] AWS resources created
- [ ] Domain DNS configured

### Deployment Steps
```bash
# 1. Backend deployment
./scripts/deploy-backend.sh prod

# 2. Frontend deployment
./scripts/deploy-frontend.sh prod

# 3. Database initialization
python backend/init_db.py --production

# 4. Health checks
curl https://api.skillforge.com/api/v1/health
curl https://skillforge.com/health

# 5. Smoke tests
pytest integration_tests/

# 6. Monitoring verification
aws cloudwatch get-metric-statistics --namespace SkillForge

# 7. Log verification
aws logs tail /skillforge/backend --follow
```

### Post-Deployment
- [ ] All endpoints responding (200 OK)
- [ ] Database seeders run (if needed)
- [ ] Payment processing tested (test Stripe transaction)
- [ ] Email notifications working
- [ ] Error monitoring active
- [ ] Performance metrics within thresholds
- [ ] User can register, login, purchase course
- [ ] Admin dashboard accessible

---

## Troubleshooting

### Backend Issues

```bash
# 1. Check service status
sudo systemctl status skillforge

# 2. View logs
sudo journalctl -u skillforge -n 100 -f

# 3. Check database connection
python << 'EOF'
from app.database import SessionLocal
db = SessionLocal()
db.execute("SELECT 1")
print("Database connected!")
EOF

# 4. Test API endpoint
curl -i http://localhost:8001/api/v1/health

# 5. Check port binding
sudo netstat -tlnp | grep 8001
```

### Frontend Issues

```bash
# 1. Check build output
ls -la .next/

# 2. View application logs
pm2 logs skillforge-frontend

# 3. Check environment variables
echo $NEXT_PUBLIC_API_BASE

# 4. Test API connectivity
curl https://api.skillforge.com/api/v1/health
```

### Database Issues

```bash
# Check RDS instance
aws rds describe-db-instances --db-instance-identifier skillforge-prod-db

# Test connection
psql -h <RDS_ENDPOINT> -U admin -d skillforge -c "SELECT COUNT(*) FROM users;"

# Check disk space
aws rds describe-db-instances --query 'DBInstances[0].AllocatedStorage'
```

### Performance Issues

```bash
# Check CPU usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Average

# Check memory usage (with CloudWatch agent)
aws cloudwatch get-metric-statistics \
  --namespace SkillForge \
  --metric-name MemoryUtilization \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Average
```

---

## Rollback Procedure

```bash
# If deployment issues occur:

# 1. Check previous version
git log --oneline | head -5

# 2. Rollback code
git revert HEAD
git push

# 3. Redeploy previous version
./scripts/deploy-backend.sh prod --rollback

# 4. Verify service
curl https://api.skillforge.com/api/v1/health

# 5. Check logs
aws logs tail /skillforge/backend --follow
```

---

## Cost Estimation (Monthly AWS Spend)

| Service | Instance/Size | Cost/Month |
|---------|---------------|-----------|
| **EC2** | t3.medium (always on) | $40 |
| **RDS** | db.t3.small PostgreSQL | $80 |
| **ALB** | Application Load Balancer | $20 |
| **CloudFront** | ~1TB/month | $85 |
| **S3** | Storage (~10GB) + requests | $10 |
| **CloudWatch** | Logs + monitoring | $10 |
| **Data Transfer** | Across AZs, out of AWS | $15 |
| **Route53** | DNS queries | $5 |
| **Total Estimate** | | **~$260/month** |

*Costs can be optimized with Reserved Instances (-40%) or Spot Instances (-70%)*

---

## Support & Documentation

- **AWS Documentation:** https://docs.aws.amazon.com/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Next.js Documentation:** https://nextjs.org/docs
- **Stripe Documentation:** https://stripe.com/docs
- **SkillForge Repo:** https://github.com/YOUR_REPO/skillforge-global

