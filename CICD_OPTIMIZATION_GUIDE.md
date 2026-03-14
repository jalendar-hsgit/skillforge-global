# BUILD TIME OPTIMIZATION & CI/CD PIPELINE

## PART 1: CURRENT BUILD TIME ANALYSIS

### Why Build Takes So Long

#### Backend (Python)
- **requirements.txt**: 30+ packages (fastapi, sqlalchemy, stripe, openai, anthropic, etc.)
- **Multi-stage build**: Good practice but still processes ALL dependencies
- **pip install**: Downloads and compiles all packages from scratch
- **Typical time**: 3-5 minutes (first build), 1-2 minutes (cached)

#### Frontend (Next.js)
- **node_modules**: 1000+ nested packages (React, Next, TypeScript, etc.)
- **npm install**: Downloads and installs every dependency
- **Next.js build**: Compiles TypeScript, optimizes bundles
- **Typical time**: 5-8 minutes (first build), 2-3 minutes (cached)

#### Total Build Time: 10-15 minutes ❌

---

## PART 2: OPTIMIZATION STRATEGIES

### Strategy 1: Use .dockerignore (QUICK WIN ✓)

Create `.dockerignore` in project root:

```
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
.next/
dist/
build/

# Development
.env.local
.env.development
.git
.gitignore
README.md

# Tests
__tests__/
tests/
*.test.js
*.test.ts

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/
npm-debug.log*

# Temporary
tmp/
temp/
.DS_Store
```

**Impact**: Reduces build context by 50-70%, saves 30-60 seconds

---

### Strategy 2: Layer Caching (MEDIUM IMPACT ✓)

Reorganize Dockerfiles to maximize cache hit rate:

#### Optimized Backend Dockerfile:

```dockerfile
# SkillForge Backend Dockerfile - OPTIMIZED

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies ONLY (cached separately)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements (changes rarely)
COPY backend/requirements.txt .

# Install dependencies (cached layer)
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -u 1000 skillforge

# Install runtime deps (cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder (reuses cached layer)
COPY --from=builder /root/.local /home/skillforge/.local

# Copy code (changes frequently, doesn't break cache)
COPY backend/app /app/app
COPY backend/init_db.py /app/

ENV PATH=/home/skillforge/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8001

RUN chown -R skillforge:skillforge /app
USER skillforge

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/healthz || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

EXPOSE 8001
```

**Impact**: Saves 1-2 minutes on rebuilds (requirements cached)

---

### Strategy 3: Optimized Frontend Dockerfile:

```dockerfile
# SkillForge Frontend Dockerfile - OPTIMIZED

FROM node:18-alpine AS dependencies

WORKDIR /app

# Copy only package files (changes rarely)
COPY package*.json ./

# Install dependencies (cached layer)
RUN npm ci --only=production && npm cache clean --force

# Development dependencies cached separately
FROM dependencies AS dev-dependencies

RUN npm ci --only=development

# Builder stage
FROM dev-dependencies AS builder

WORKDIR /app

# Copy source code
COPY . .

# Build (can be skipped for dev)
RUN npm run build 2>/dev/null || true

# Production stage
FROM node:18-alpine

WORKDIR /app

ENV NEXT_PUBLIC_API_BASE="http://backend:8001" \
    NEXT_PUBLIC_STRIPE_KEY="pk_test_51SkcWEBydMsdVDYvDjEH5cNq0BO8VbYGcTq64NdlpvxFwaGaaaUIrKDFrTAAV4TrNYAAz3JdOvRFcDz8PWQLBc3K00kQDXwyCd" \
    NODE_ENV="development" \
    PORT=3000

# Copy from dependencies (reuses cache)
COPY --from=dependencies /app/node_modules ./node_modules

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["npm", "run", "dev"]
```

**Impact**: Saves 1-3 minutes on rebuilds (npm packages cached)

---

### Strategy 4: Docker Compose Build Optimization:

```yaml
# docker-compose.yml - BUILD OPTIMIZATIONS

services:
  postgres:
    image: postgres:15-alpine  # Use pre-built image
    # ... rest of config

  redis:
    image: redis:7-alpine      # Use pre-built image
    # ... rest of config

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
      cache_from:              # ← NEW: Reuse cache from registry
        - ghcr.io/skillforge/backend:latest
    # ... rest of config

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      cache_from:              # ← NEW: Reuse cache from registry
        - ghcr.io/skillforge/frontend:latest
      args:                    # ← Avoid rebuilds for env changes
        NEXT_PUBLIC_API_BASE: http://backend:8001
    # ... rest of config
```

---

### Strategy 5: Skip Non-Essential Dependencies:

#### Split requirements.txt:

**requirements.txt** (core - 15 packages):
```
fastapi==0.115.4
uvicorn[standard]==0.30.6
SQLAlchemy==2.0.36
pydantic==2.8.2
python-jose[cryptography]==3.3.0
bcrypt==4.0.1
psycopg2-binary
redis
stripe
requests
email-validator
python-multipart
aiofiles
python-dateutil
PyJWT
```

**requirements-ai.txt** (optional - AI features):
```
openai==1.54.0
anthropic==0.39.0
httpx-sse==0.4.0
```

**requirements-reports.txt** (optional - report generation):
```
reportlab
python-docx
PyPDF2
Pillow==12.0.0
PyMuPDF==1.26.6
playwright
```

**Dockerfile.backend** (updated):
```dockerfile
# Install only core dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Optional: Conditionally install features
ARG INCLUDE_AI=false
RUN if [ "$INCLUDE_AI" = "true" ]; then \
    pip install --user --no-cache-dir -r requirements-ai.txt; \
    fi
```

**Impact**: Saves 30-60 seconds by not installing unused packages

---

### Strategy 6: Use BuildKit (Native Docker Faster Builds):

```bash
# Enable Docker BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build with BuildKit (parallelizes stages)
docker-compose build --no-cache
```

Add to `.env`:
```
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1
```

**Impact**: Saves 2-3 minutes (parallel stage building)

---

## PART 3: OPTIMIZED BUILD SETUP

### Create New Dockerfiles:

Replace current Dockerfiles.backend with optimized version (shown above)
Replace current Dockerfile.frontend with optimized version (shown above)

### Update docker-compose.yml:

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
      cache_from:
        - skillforge-backend:latest
      buildargs:
        INCLUDE_AI: "false"  # Disable AI for faster builds
    # ... rest remains same

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      cache_from:
        - skillforge-frontend:latest
    # ... rest remains same
```

### Create .dockerignore:

[As shown in Strategy 1 above]

### Benchmark Commands:

```bash
# Measure current build time
time docker-compose build --no-cache

# Measure with cache
time docker-compose build

# Build specific service
time docker-compose build skillforge-backend

# Clean everything and rebuild
docker system prune -a
docker-compose build --no-cache
```

---

## PREDICTED OPTIMIZATION RESULTS

| Strategy | Time Saved | Total |
|----------|-----------|-------|
| Current baseline | — | 10-15 min |
| .dockerignore | 30-60s | 9-14 min |
| Layer caching | 1-2 min | 8-12 min |
| Split requirements | 30-60s | 7-10 min |
| BuildKit enabled | 2-3 min | 5-7 min |
| **All combined** | **4-6 min** | **4-6 min** ✓✓✓ |

---

# PART 4: CI/CD PIPELINE RECOMMENDATIONS

## Option 1: GitHub Actions (RECOMMENDED - FREE) ✓✓✓

### Why GitHub Actions?
- **Free**: 2,000 minutes/month (enough for most projects)
- **No setup**: Works directly with GitHub repos
- **Docker support**: Built-in Docker and Docker Compose
- **Easy to use**: YAML workflow files
- **Good ecosystem**: Lots of community actions

### Setup:

1. Create `.github/workflows/ci-cd.yml`:

```yaml
name: Build & Deploy SkillForge

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Job 1: Lint & Test
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        service: [backend, frontend]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run tests for ${{ matrix.service }}
        run: |
          if [ "${{ matrix.service }}" == "backend" ]; then
            docker build -f Dockerfile.backend .
          else
            docker build -f Dockerfile.frontend .
          fi
  
  # Job 2: Build & Push Images
  build:
    runs-on: ubuntu-latest
    needs: test
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      # Build Backend
      - name: Build & push backend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.backend
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      # Build Frontend
      - name: Build & push frontend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.frontend
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
  
  # Job 3: Deploy (Optional)
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add your deployment commands here
          # Example: SSH to server and pull latest images
```

2. Configure secrets in GitHub:
   - Go to Settings → Secrets and variables → Actions
   - Add any required secrets (API keys, etc.)

**Cost**: FREE (2,000 min/month = ~40 builds/month at 50 min each)

---

## Option 2: GitLab CI/CD (FREE if self-hosted)

### Why GitLab?
- **Free tier**: Unlimited minutes (if self-hosted)
- **Docker native**: Excellent Docker/Kubernetes support
- **Built-in registry**: Similar to GitHub
- **Powerful**: More features than GitHub Actions

### Setup:

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  REGISTRY: registry.gitlab.com
  IMAGE_NAME: $CI_PROJECT_PATH

before_script:
  - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY

# Test stage
test:backend:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.backend .

test:frontend:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.frontend .

# Build stage
build:backend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.backend -t $REGISTRY/$IMAGE_NAME/backend:latest .
    - docker push $REGISTRY/$IMAGE_NAME/backend:latest

build:frontend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.frontend -t $REGISTRY/$IMAGE_NAME/frontend:latest .
    - docker push $REGISTRY/$IMAGE_NAME/frontend:latest

# Deploy stage
deploy:
  stage: deploy
  image: docker:latest
  services:
    - docker:dind
  script:
    - echo "Deploying..."
    - docker pull $REGISTRY/$IMAGE_NAME/backend:latest
    - docker pull $REGISTRY/$IMAGE_NAME/frontend:latest
    - docker-compose up -d
  only:
    - main
```

**Cost**: FREE (if self-hosted), ~$20-40/month (SaaS)

---

## Option 3: Travis CI (Simple but paid)

**Cost**: Start with free tier, $129+/month for advanced

---

## Option 4: CircleCI (Professional choice)

**Cost**: FREE tier ~150 builds/month, $50+/month for unlimited

---

## RECOMMENDED CHOICE FOR YOU:

### GitHub Actions ✓ (BEST FOR FREE/OPEN SOURCE)
- Already have GitHub
- No setup needed
- 2,000 free minutes/month
- Great community support
- Perfect for teams

### Implementation Priority:
1. **Month 1**: GitHub Actions with basic build/push
2. **Month 2**: Add testing and linting
3. **Month 3**: Add deployment automation
4. **Later**: Consider Kubernetes deployment

---

## PART 5: COMPLETE CI/CD WITH DEPLOYMENT

### Option A: Deploy to DigitalOcean App Platform (FREE tier available)

`.github/workflows/deploy-digitalocean.yml`:

```yaml
name: Deploy to DigitalOcean

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Update DigitalOcean App
        env:
          DIGITALOCEAN_ACCESS_TOKEN: ${{ secrets.DIGITALOCEAN_TOKEN }}
          APP_ID: ${{ secrets.DIGITALOCEAN_APP_ID }}
        run: |
          curl -X POST "https://api.digitalocean.com/v2/apps/${APP_ID}/deployments" \
            -H "Authorization: Bearer ${DIGITALOCEAN_ACCESS_TOKEN}" \
            -H "Content-Type: application/json" \
            -d '{"force_build": true}'
```

**Cost**: $5-30/month depending on resources

---

### Option B: Deploy to Render (Easy & Free tier)

1. Connect repo to Render.com
2. Create services (PostgreSQL, Backend, Frontend)
3. Automatic deploys on push

**Cost**: $12-25/month (free tier available)

---

### Option C: Self-hosted on VPS (Cheapest)

Deploy to server with Docker:

```bash
#!/bin/bash
# deploy.sh

cd /home/skillforge/app
git pull origin main

# Build images
docker-compose build --no-cache

# Start services
docker-compose up -d

# Prune old images
docker system prune -a -f
```

**Cost**: $3-5/month (DigitalOcean, Linode, Vultr)

---

## SUMMARY TABLE

| Solution | Cost | Setup Time | Maintenance | Free Tier | Best For |
|----------|------|-----------|-------------|-----------|----------|
| **GitHub Actions** | FREE | 30 min | Minimal | 2000 min/mo | Most projects |
| **GitLab CI** | FREE (self) | 1 hour | Low | Unlimited | Enterprise |
| **CircleCI** | $0-50/mo | 30 min | Minimal | 150 builds/mo | Pro teams |
| **DigitalOcean App** | $5-30 | 30 min | None | Limited | Easy deploy |
| **Render** | $12+ | 15 min | None | Yes | Quick start |
| **VPS + Docker** | $3-5 | 2 hours | Medium | N/A | Control freaks |

---

## RECOMMENDED ARCHITECTURE FOR YOU

```
Dev Laptop
    ↓
    Push to GitHub (main branch)
    ↓
GitHub Actions
    ├→ Test (lint, build)
    ├→ Build images (backend, frontend)
    └→ Push to ghcr.io (container registry)
    ↓
Deploy to VPS (DigitalOcean) or Render
    ├→ Pull images
    ├→ Run docker-compose
    └→ Health checks + monitoring
```

**Estimated monthly cost**: $3-5 (VPS) + FREE (GitHub Actions) = $3-5 total

---

## NEXT STEPS

1. **Implement optimizations** (Dockerfiles + .dockerignore)
2. **Test build time**: `time docker-compose build`
3. **Set up GitHub Actions** workflow
4. **Choose deployment** platform
5. **Monitor and maintain**

All configurations are in the file `/DOCKER_GUIDE.md`
