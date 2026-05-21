# CI/CD Pipeline Guide for SkillForge Global

## Executive Summary

This guide provides step-by-step instructions for setting up a free, production-ready CI/CD pipeline for SkillForge Global.

## Free & Open-Source Options Comparison

### 1. **GitHub Actions (RECOMMENDED)**
| Feature | Status |
|---------|--------|
| Cost | FREE - 2,000 free minutes/month per repo |
| Setup Time | 5 minutes |
| Best For | GitHub-hosted repos, teams already on GitHub |
| Integrations | Native Docker, Kubernetes, AWS, Azure, GCP |
| Learning Curve | Easy - YAML-based |
| Reliability | 99.9% uptime (Microsoft-backed) |

**Why Choose GitHub Actions**:
- Already integrated with GitHub
- No additional setup needed
- Generous free tier (2,000 min/month = ~60 deployments)
- Excellent documentation
- Works perfectly with Docker

---

### 2. **GitLab CI/CD (Alternative)**
| Feature | Status |
|---------|--------|
| Cost | FREE - 400 free minutes/month |
| Setup Time | 10 minutes |
| Best For | GitLab-hosted repos |
| Integrations | Docker, Kubernetes native |
| Learning Curve | Medium - More complex than GitHub |
| Container Registry | Included (50GB free) |

**When to Use**: If repo is on GitLab instead of GitHub

---

### 3. **Gitea + Drone CI (Self-Hosted)**
| Feature | Status |
|---------|--------|
| Cost | FREE (self-hosted) |
| Setup Time | 30 minutes |
| Best For | Complete control, private servers |
| Integrations | Unlimited |
| Learning Curve | Hard - Requires DevOps knowledge |
| Infrastructure | Your own servers |

**When to Use**: Enterprise compliance requirements

---

## RECOMMENDED: GitHub Actions Pipeline

### Prerequisites
- [ ] GitHub account
- [ ] Repository on GitHub
- [ ] Docker Hub account (for image registry)
- [ ] AWS/GCP account (optional, for deployment)

### Step 1: Create GitHub Actions Workflow

**File**: `.github/workflows/deploy.yml`

```yaml
name: Build and Deploy SkillForge

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
      - 'src/**'
      - 'docker-compose.yml'
      - '.github/workflows/deploy.yml'
  pull_request:
    branches: [ main, develop ]

env:
  REGISTRY: docker.io
  GITHUB_REGISTRY: ghcr.io
  BACKEND_IMAGE: ${{ secrets.DOCKER_USERNAME }}/skillforge-backend
  FRONTEND_IMAGE: ${{ secrets.DOCKER_USERNAME }}/skillforge-frontend

jobs:
  # ═══════════════════════════════════════════════════════════
  # 1. LINT & TEST BACKEND
  # ═══════════════════════════════════════════════════════════
  lint-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install pylint black flake8
      
      - name: Lint with pylint
        run: |
          pylint backend/app --disable=C,R --fail-under=8.0 || true
      
      - name: Check code format with black
        run: black --check backend/app || true
      
      - name: Run flake8
        run: flake8 backend/app --max-line-length=120 --ignore=E203,W503 || true

  # ═══════════════════════════════════════════════════════════
  # 2. LINT & BUILD FRONTEND
  # ═══════════════════════════════════════════════════════════
  lint-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run ESLint
        run: npm run lint || true
      
      - name: Build Next.js
        run: npm run build

  # ═══════════════════════════════════════════════════════════
  # 3. BUILD DOCKER IMAGES
  # ═══════════════════════════════════════════════════════════
  build-images:
    needs: [lint-backend, lint-frontend]
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.GITHUB_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: |
            ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}
            ${{ env.GITHUB_REGISTRY }}/${{ github.repository }}-backend
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:buildcache,mode=max
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.frontend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:buildcache,mode=max

  # ═══════════════════════════════════════════════════════════
  # 4. DEPLOY TO PRODUCTION
  # ═══════════════════════════════════════════════════════════
  deploy:
    needs: build-images
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H ${{ secrets.DEPLOY_HOST }} >> ~/.ssh/known_hosts
      
      - name: Deploy via SSH
        run: |
          ssh -i ~/.ssh/deploy_key ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} << 'EOF'
            cd /app/skillforge-global
            
            # Pull latest code
            git pull origin main
            
            # Pull latest Docker images
            docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }} docker.io
            docker-compose pull
            
            # Stop and restart services
            docker-compose down
            docker-compose up -d
            
            # Run migrations
            docker-compose exec -T backend python init_db.py
            docker-compose exec -T backend python seed_all_demo_data.py
            
            # Health checks
            sleep 10
            curl http://localhost:8001/healthz || exit 1
            curl http://localhost:3000 || exit 1
            
            echo "Deployment successful!"
          EOF
```

### Step 2: GitHub Secrets Configuration

Navigate to: **Settings → Secrets and variables → Actions**

Add these secrets:

```
DOCKER_USERNAME        = your-docker-username
DOCKER_PASSWORD        = your-docker-token (not password!)
DEPLOY_HOST            = your-server.com
DEPLOY_USER            = deploy-user
DEPLOY_KEY             = your-private-ssh-key
DATABASE_PASSWORD      = strong-password-here
STRIPE_SECRET_KEY      = sk_live_xxxxxx
STRIPE_PUBLISHABLE_KEY = pk_live_xxxxxx
```

### Step 3: Docker Hub Setup

1. Go to https://hub.docker.com
2. Create repositories:
   - `yourusername/skillforge-backend`
   - `yourusername/skillforge-frontend`

3. Generate access token:
   - Account Settings → Security → New Access Token
   - Copy the token (it's your `DOCKER_PASSWORD`)

### Step 4: Deploy Server Setup

```bash
# On your server
ssh user@your-server.com

# Create deploy directory
sudo mkdir -p /app/skillforge-global
sudo chown $USER:$USER /app/skillforge-global

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com | sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repo
cd /app/skillforge-global
git clone https://github.com/YOUR_USERNAME/skillforge-global .

# Create .env file
cat > .env << 'EOF'
DB_PASSWORD=your-secure-password-here
JWT_SECRET_KEY=your-jwt-secret-here
STRIPE_SECRET_KEY=your-stripe-key-here
STRIPE_PUBLISHABLE_KEY=your-stripe-pub-key-here
ENVIRONMENT=production
EOF

# Initial deployment
docker-compose pull
docker-compose up -d
```

## Alternative: GitLab CI/CD

**File**: `.gitlab-ci.yml`

```yaml
stages:
  - lint
  - build
  - deploy

lint-backend:
  stage: lint
  image: python:3.11
  script:
    - pip install -r backend/requirements.txt pylint
    - pylint backend/app --disable=C,R --fail-under=8.0 || true
  only:
    - merge_requests
    - main

lint-frontend:
  stage: lint
  image: node:18
  script:
    - npm ci
    - npm run lint || true
  only:
    - merge_requests
    - main

build-backend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.backend -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
  only:
    - main

build-frontend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.frontend -t $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA
  only:
    - main

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache openssh-client
    - mkdir -p ~/.ssh
    - echo "$DEPLOY_KEY" > ~/.ssh/deploy_key
    - chmod 600 ~/.ssh/deploy_key
    - ssh-keyscan -H $DEPLOY_HOST >> ~/.ssh/known_hosts
    - ssh -i ~/.ssh/deploy_key $DEPLOY_USER@$DEPLOY_HOST "cd /app/skillforge-global && git pull && docker-compose pull && docker-compose up -d"
  only:
    - main
  when: manual
```

## Monitoring & Logging

### Option 1: Free Tier Services

```bash
# Sentry (Error Tracking) - Free tier included
pip install sentry-sdk

# LogRocket (Frontend Monitoring) - 1GB/month free
npm install @logrocket/browser

# Grafana Cloud (Metrics) - Free tier
# InfluxDB Cloud (Time Series DB) - Free tier
```

### Option 2: Self-Hosted Monitoring

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Pipeline Workflow

```
┌──────────────┐
│  Push Code   │
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│  Run Linters       │
│  - ESLint          │
│  - Pylint          │
│  - Black/Flake8    │
└────┬───────────────┘
     │
     ├─ FAIL ──────► Notify Developer (Stop)
     │
     ├─ PASS ──────┐
     │             │
     │             ▼
     │      ┌──────────────────┐
     │      │  Build Images    │
     │      │  - Backend       │
     │      │  - Frontend      │
     │      └────┬─────────────┘
     │           │
     │           ├─ FAIL ──────► Review Logs (Stop)
     │           │
     │           ├─ PASS ──────┐
     │           │             │
     └───────────┼─────────────┼── If PR: Stop Here
                 │             │
                 │       ┌─────▼──────────────┐
                 │       │  Push to Registry  │
                 │       │  - Docker Hub      │
                 │       │  - GitHub Registry │
                 │       └────┬───────────────┘
                 │            │
                 │            ├─ FAIL ──────► Review Credentials (Stop)
                 │            │
                 │            ├─ PASS ──────┐
                 │            │             │
                 └────────────┼─────────────┼── If main branch: Continue
                              │             │
                              │       ┌─────▼──────────────┐
                              │       │  Deploy to Prod    │
                              │       │  - SSH to server   │
                              │       │  - docker-compose  │
                              │       └────┬───────────────┘
                              │            │
                              │      ┌─────▼──────────┐
                              │      │  Health Checks │
                              │      │  - Backend     │
                              │      │  - Frontend    │
                              │      │  - Database    │
                              │      └────┬───────────┘
                              │           │
                              │      ┌────▼──────────────┐
                              │      │  ✅ LIVE!         │
                              │      │  Notify Slack     │
                              │      └───────────────────┘
                              │
                              └──► 📊 Collect Metrics
```

## Cost Breakdown (Monthly)

| Service | Free Tier | Cost |
|---------|-----------|------|
| GitHub Actions | 2,000 min | $0 |
| Docker Hub | 1 private repo | $7 (optional) |
| Server (AWS/DigitalOcean) | - | $5-20 |
| Database | PostgreSQL (self-hosted) | $0 |
| Cache | Redis (self-hosted) | $0 |
| Domain | - | $1-5 |
| **TOTAL** | **With Free Tier** | **$0-25** |

## Recommended Free Deployment Options

### Option 1: DigitalOcean Apps ($0-12/month)
- Managed containers
- GitHub integration
- Auto-deploy on push
- Free SSL

```yaml
name: skillforge-global
services:
  - name: backend
    github:
      repo: YOUR_USERNAME/skillforge-global
      branch: main
    dockerfile_path: Dockerfile.backend
    envs:
      - key: DATABASE_URL
        value: ${db.connection_string}
  
  - name: frontend
    github:
      repo: YOUR_USERNAME/skillforge-global
      branch: main
    dockerfile_path: Dockerfile.frontend
    http_port: 3000
```

### Option 2: Railway App ($5/month credit, then pay-as-you-go)
- GitHub integration
- Built-in PostgreSQL
- Auto-deploy
- Free SSL

```toml
# railway.toml
[build]
builder = "dockerfile"
dockerfile = "Dockerfile.backend"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port 8001"
```

### Option 3: Heroku Alternative (Render.com)
- Free tier for hobby projects
- GitHub integration
- PostgreSQL database
- Auto-deploy

## Setup Quick Start (GitHub Actions + DigitalOcean)

```bash
# 1. Create GitHub Actions workflow
mkdir -p .github/workflows
# (Copy the deploy.yml content from above)

# 2. Add secrets to GitHub
# Settings → Secrets → Add secrets

# 3. Create DigitalOcean account
# https://digitalocean.com

# 4. Create App Platform project
# Connect GitHub repo
# Configure dockerfile paths
# Deploy!

# 5. Monitor deployment
# https://cloud.digitalocean.com/apps
```

## Troubleshooting CI/CD

### Build Fails: Docker Login Error
```
# Check credentials
docker login -u ${{ secrets.DOCKER_USERNAME }}

# Generate new token on Docker Hub
# Account → Security → New Access Token
```

### Deployment Fails: SSH Connection
```bash
# On local machine
ssh-keygen -t ed25519 -f ./deploy_key -N ""

# Copy public key to server
ssh-copy-id -i ./deploy_key.pub user@server.com

# Add private key as GitHub secret (deploy_key content)
```

### Pipeline Hangs: Resource Limits
```yaml
# Increase timeout
timeout: 1800  # 30 minutes

# Use larger runner
runs-on: ubuntu-latest-xl
```

## Next Actions

- [ ] Create `.github/workflows/deploy.yml`
- [ ] Add GitHub Secrets
- [ ] Push to trigger workflow
- [ ] Monitor build/deployment
- [ ] Celebrate! 🚀
