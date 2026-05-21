# AWS Deployment Checklist

**Project:** SkillForge Global  
**Date Started:** _______________  
**Deployment Environment:** [ ] Development [ ] Production  
**AWS Region:** us-east-1

---

## PHASE 1: AWS Account Setup (30 min)

### 1.1 AWS Account & IAM
- [ ] AWS account created
- [ ] Email verified
- [ ] Payment method added
- [ ] IAM user "skillforge-admin" created
- [ ] Access keys generated
- [ ] Access keys saved securely
- [ ] AWS CLI installed: `aws --version`
- [ ] AWS CLI configured: `aws configure`
- [ ] Credentials verified: `aws sts get-caller-identity`

**Credentials Saved To:** ________________

### 1.2 SSH Keys
- [ ] SSH key pair generated: `skillforge-prod-key`
- [ ] Private key saved: `~/.ssh/skillforge-prod-key.pem`
- [ ] SSH key permissions set: `chmod 400`
- [ ] SSH key pair generated: `skillforge-dev-key`
- [ ] SSH key backup created

**Location:** ________________

---

## PHASE 2: VPC & Networking (45 min)

### 2.1 VPC Creation
- [ ] VPC created: `skillforge-vpc` (10.0.0.0/16)
- [ ] VPC ID: `_____________________`
- [ ] DNS hostnames enabled

### 2.2 Subnets
- [ ] Public Subnet 1A created (10.0.1.0/24)
  - SubnetID: `_____________________`
- [ ] Public Subnet 1B created (10.0.2.0/24)
  - SubnetID: `_____________________`
- [ ] Private Subnet 1A created (10.0.3.0/24)
  - SubnetID: `_____________________`
- [ ] Private Subnet 1B created (10.0.4.0/24)
  - SubnetID: `_____________________`

### 2.3 Internet Gateway
- [ ] IGW created: `skillforge-igw`
  - IGW ID: `_____________________`
- [ ] IGW attached to VPC

### 2.4 Route Tables
- [ ] Public route table created
  - RTB ID: `_____________________`
  - Route added: 0.0.0.0/0 → IGW
- [ ] Public subnets associated with public RTB
- [ ] Private route table created
  - RTB ID: `_____________________`
- [ ] Private subnets associated with private RTB

### 2.5 Security Groups
- [ ] ALB Security Group created
  - SG ID: `_____________________`
  - Port 80 (HTTP) from 0.0.0.0/0
  - Port 443 (HTTPS) from 0.0.0.0/0
- [ ] Backend Security Group created
  - SG ID: `_____________________`
  - Port 8001 from ALB SG
  - Port 22 from YOUR_IP/32
- [ ] RDS Security Group created
  - SG ID: `_____________________`
  - Port 5432 from Backend SG

---

## PHASE 3: Database Setup (45 min)

### 3.1 RDS Subnet Group
- [ ] DB Subnet Group created: `skillforge-db-subnet`
- [ ] Subnets included: Private 1A + 1B

### 3.2 Production RDS
- [ ] RDS instance created: `skillforge-prod-db`
- [ ] Engine: PostgreSQL 15.3
- [ ] Instance type: db.t3.small
- [ ] Master username: admin
- [ ] Master password: (saved securely)
- [ ] Database name: skillforge
- [ ] Backup retention: 30 days
- [ ] Multi-AZ enabled
- [ ] Encryption enabled
- [ ] Status: Available ✓
- [ ] Endpoint: `_____________________`

### 3.3 Development RDS
- [ ] RDS instance created: `skillforge-dev-db`
- [ ] Engine: PostgreSQL 15.3
- [ ] Instance type: db.t3.micro
- [ ] Status: Available ✓
- [ ] Endpoint: `_____________________`

---

## PHASE 4: EC2 Setup (1 hour)

### 4.1 EC2 Keys
- [ ] Prod key created: `skillforge-prod-key`
- [ ] Dev key created: `skillforge-dev-key`
- [ ] Both keys saved securely

### 4.2 Production EC2
- [ ] Latest Ubuntu 22.04 AMI ID found
  - AMI: `_____________________`
- [ ] Instance launched: `skillforge-backend-prod`
- [ ] Instance type: t3.medium
- [ ] VPC: skillforge-vpc
- [ ] Subnet: Private 1A
- [ ] Public IP assigned
- [ ] Instance ID: `_____________________`
- [ ] Public IP: `_____________________`
- [ ] Private IP: `_____________________`
- [ ] Status: running ✓
- [ ] Can SSH into instance

**SSH Command:**
```bash
ssh -i ~/.ssh/skillforge-prod-key.pem ubuntu@YOUR_PUBLIC_IP
```

### 4.3 Development EC2
- [ ] Instance launched: `skillforge-backend-dev`
- [ ] Instance type: t3.small
- [ ] Instance ID: `_____________________`
- [ ] Status: running ✓

---

## PHASE 5: Load Balancer (30 min)

### 5.1 Application Load Balancer
- [ ] ALB created: `skillforge-alb`
- [ ] Subnets: Public 1A + 1B
- [ ] Security Group: ALB SG
- [ ] Scheme: internet-facing
- [ ] ALB ARN: `_____________________`
- [ ] ALB DNS: `_____________________`

### 5.2 Target Groups
- [ ] Target Group created: `skillforge-backend-tg`
- [ ] Protocol: HTTP
- [ ] Port: 8001
- [ ] Health check path: /api/v1/health
- [ ] Target Group ARN: `_____________________`
- [ ] Prod instance registered (i-prod0123:8001)
- [ ] Dev instance registered (optional)

### 5.3 Listeners
- [ ] HTTP listener (80) created → redirect to HTTPS
- [ ] HTTPS listener (443) created
  - Certificate ARN: `_____________________`

---

## PHASE 6: S3 & CloudFront (30 min)

### 6.1 S3 Bucket
- [ ] Bucket created: `skillforge-frontend-prod`
- [ ] Versioning enabled
- [ ] Public access blocked
- [ ] Bucket name: `_____________________`

### 6.2 CloudFront
- [ ] Origin Access Identity (OAI) created
  - OAI ID: `_____________________`
- [ ] S3 bucket policy updated for OAI
- [ ] CloudFront distribution created
- [ ] Distribution ID: `_____________________`
- [ ] Distribution domain: `_____________________`
- [ ] Default root object: index.html
- [ ] Status: Deployed ✓

---

## PHASE 7: SSL & DNS (30 min)

### 7.1 SSL Certificate
- [ ] Certificate requested from ACM
- [ ] Domains: skillforge.com, api.skillforge.com, www.skillforge.com
- [ ] Validation method: DNS
- [ ] Certificate ARN: `_____________________`
- [ ] DNS validation records created
  - [ ] skillforge.com verified
  - [ ] api.skillforge.com verified
  - [ ] www.skillforge.com verified
- [ ] Status: Issued ✓

### 7.2 Route 53
- [ ] Hosted Zone created: skillforge.com
- [ ] Zone ID: `_____________________`
- [ ] Name Servers:
  - `_____________________`
  - `_____________________`
  - `_____________________`
  - `_____________________`
- [ ] Auto-nameservers updated at domain registrar
- [ ] Alias record created: api.skillforge.com → ALB
- [ ] Alias record created: skillforge.com → CloudFront
- [ ] Alias record created: www.skillforge.com → CloudFront
- [ ] DNS propagation verified (`nslookup skillforge.com`)

---

## PHASE 8: Application Deployment (1.5 hours)

### 8.1 SSH & System Setup
- [ ] Connected to prod EC2 via SSH
- [ ] System updated: `sudo apt update && sudo apt upgrade -y`
- [ ] Dependencies installed (Python, Git, Nginx, etc.)
- [ ] Log directory created: `/var/log/skillforge`

**On EC2, execute:**
```bash
cd /opt/skillforge
sudo chown ubuntu:ubuntu .
git clone https://github.com/YOUR_ORG/skillforge-global.git .
```

### 8.2 Python Environment
- [ ] Virtual environment created
- [ ] Package: `python3 -m venv venv`
- [ ] Activated: `source venv/bin/activate`
- [ ] Pip upgraded
- [ ] Dependencies installed: `pip install -r backend/requirements.txt`

### 8.3 Environment Configuration
- [ ] `.env.production` file created in backend/
- [ ] DATABASE_URL set to RDS endpoint
- [ ] STRIPE keys added (production keys)
- [ ] JWT_SECRET_KEY set (random, 32+ chars)
- [ ] ENVIRONMENT=production
- [ ] ALLOWED_ORIGINS configured

### 8.4 Database Initialization
- [ ] Database connection tested
- [ ] Tables created: `python init_db.py`
- [ ] Demo data seeded (optional): `python seed_all_demo_data.py`
- [ ] Database verified:
  ```bash
  psql -h RDS_ENDPOINT -U admin -d skillforge -c "SELECT COUNT(*) FROM marketplace_courses;"
  ```

### 8.5 Gunicorn & Systemd
- [ ] Systemd service file created: `/etc/systemd/system/skillforge.service`
- [ ] Service enabled: `sudo systemctl enable skillforge`
- [ ] Service started: `sudo systemctl start skillforge`
- [ ] Service status verified: `sudo systemctl status skillforge`
- [ ] Port 8001 listening: `sudo netstat -tlnp | grep 8001`

### 8.6 Nginx Configuration
- [ ] Nginx config created: `/etc/nginx/conf.d/skillforge.conf`
- [ ] Nginx validated: `sudo nginx -t`
- [ ] Nginx enabled: `sudo systemctl enable nginx`
- [ ] Nginx restarted: `sudo systemctl restart nginx`
- [ ] Reverse proxy working: `curl http://localhost/api/v1/health`

### 8.7 Frontend Deployment
- [ ] Frontend built locally: `npm run build`
- [ ] Build verified: `ls -la .next/`
- [ ] Static files uploaded to S3:
  ```bash
  aws s3 sync .next/static s3://skillforge-frontend-prod/.next/static
  aws s3 sync . s3://skillforge-frontend-prod --exclude "*" --include "*.html"
  ```
- [ ] CloudFront cache invalidated: `aws cloudfront create-invalidation`

---

## PHASE 9: Verification & Testing (30 min)

### 9.1 Backend API Testing
- [ ] Health check: `curl https://api.skillforge.com/api/v1/health`
  - Status: `_____________________`
- [ ] Register endpoint tested
- [ ] Login endpoint tested
- [ ] Marketplace courses endpoint: `curl https://api.skillforge.com/api/v1x/marketplace/courses`
  - Count: `_____________________`
- [ ] Admin dashboard accessible

### 9.2 Frontend Testing
- [ ] Website loads: https://skillforge.com
  - Status: `_____________________`
- [ ] Navigation works
- [ ] Courses visible on marketplace
- [ ] User registration works
- [ ] User login works
- [ ] Add to cart works
- [ ] Payment flow works (test transaction)
  - Test card: 4242 4242 4242 4242
  - Transaction ID: `_____________________`

### 9.3 Database Testing
- [ ] Can connect to RDS from EC2
- [ ] Can query tables
- [ ] Backups are scheduled
- [ ] Multi-AZ failover tested (optional)

### 9.4 Monitoring
- [ ] CloudWatch agent installed
- [ ] Logs visible in CloudWatch
- [ ] Metrics collecting:
  - CPU Utilization
  - Memory Utilization
  - Network
- [ ] ALB health checks passing
- [ ] RDS metrics visible

### 9.5 Security Verification
- [ ] SSL certificate valid (green lock)
- [ ] HTTP redirects to HTTPS
- [ ] Secrets not in code/logs
- [ ] Database not publicly accessible
- [ ] EC2 only accessible from ALB/SSH
- [ ] CORS properly configured

---

## Settings & Credentials Storage

Create a secure document (encrypted or password protected):

```
PROJECT: SkillForge Global - AWS Deployment
DATE: ________________

ACCOUNT DETAILS
- AWS Account ID: ___________________
- IAM Admin User: skillforge-admin
- Root Account Email: ___________________

SSH KEYS
- Prod Key: ~/.ssh/skillforge-prod-key.pem
- Dev Key: ~/.ssh/skillforge-dev-key.pem

RDS DATABASES
- Prod: skillforge-prod-db.*.rds.amazonaws.com
- Prod User: admin
- Prod Password: [SECURED]
- Dev: skillforge-dev-db.*.rds.amazonaws.com
- Dev User: admin
- Dev Password: [SECURED]

EC2 INSTANCES
- Prod ID: ___________________
- Prod Public IP: ___________________
- Dev ID: ___________________
- Dev Public IP: ___________________

STRIPE KEYS (Production)
- Publishable: pk_live_...
- Secret: sk_live_... [SECURED]
- Webhook Secret: whsec_...

CERTIFICATES
- ACM Certificate ARN: ___________________

DOMAAINS
- Main: skillforge.com (Route 53 Zone: _______)
- API: api.skillforge.com
- Frontend S3: skillforge-frontend-prod
- CloudFront: d111111abcdef8.cloudfront.net
```

---

## Post-Deployment Tasks

### Week 1
- [ ] Monitor application for errors
- [ ] Test payment processing thoroughly
- [ ] Load test (simulate traffic)
- [ ] Security audit
- [ ] Backup test (verify restore works)

### Week 2-4
- [ ] User acceptance testing (UAT)
- [ ] Performance optimization
- [ ] Documentation complete
- [ ] Team training on ops
- [ ] Go-live preparation

### Production Launch
- [ ] Final verification checklist
- [ ] Monitoring alerts active
- [ ] On-call engineer scheduled
- [ ] Rollback plan documented
- [ ] Customer notifications ready

---

## Notes & Issues

```
Date: _______  Issue: ______________________
Solution: ___________________________________

Date: _______  Issue: ______________________
Solution: ___________________________________
```

---

## Sign-Off

- [ ] Deployment completed
- [ ] All tests passing
- [ ] Production ready
- [ ] Team acknowledged

**Deployed By:** _________________________ **Date:** _____________

**Verified By:** _________________________ **Date:** _____________

**Approved By:** _________________________ **Date:** _____________
