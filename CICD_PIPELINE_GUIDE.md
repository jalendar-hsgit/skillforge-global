# 🔄 CI/CD Pipeline Guide - GitHub Actions

**Status**: ✅ Fully Configured  
**Workflows**: 2 (test.yml, deploy.yml)  
**Triggers**: Automatic on push/PR  

---

## Pipeline Overview

```
Git Push
  ↓
[TEST WORKFLOW] (test.yml)
  ├─ Frontend Tests (npm)
  ├─ Backend Tests (pytest)
  ├─ Code Quality (lint/type-check)
  └─ Security Scan
    ↓
[If Tests Pass → DEPLOY WORKFLOW] (deploy.yml)
  ├─ Deploy Frontend (Vercel)
  ├─ Deploy Backend (Railway)
  ├─ Health Checks
  └─ Notifications
```

---

## Test Workflow (test.yml)

**Trigger**: Every push or PR to main/develop/v1.0.0-release

### Jobs

#### 1. Frontend Tests
- **Node versions**: 18.x, 20.x
- **Steps**:
  1. Checkout code
  2. Install npm dependencies
  3. Run ESLint
  4. Build Next.js
  5. Run test suite
  6. Upload coverage to Codecov

**Duration**: 3-5 minutes

**Fail if**:
- Build fails
- Linter errors
- Tests fail

#### 2. Backend Tests
- **Python versions**: 3.9, 3.11
- **Database**: PostgreSQL (auto-started)
- **Steps**:
  1. Checkout code
  2. Install Python dependencies
  3. Start PostgreSQL service
  4. Run pytest
  5. Generate coverage report
  6. Run security scan (bandit)

**Duration**: 4-8 minutes

**Fail if**:
- Test fails
- Coverage below threshold
- Security issues found

#### 3. Code Quality
- **Tools**: pylint, flake8, mypy
- **Checks**: Python only
- **Won't fail** (informational)

**Duration**: 1-2 minutes

#### 4. Security Scan
- **Tool**: Trivy
- **Scans**: Entire repo for vulnerabilities
- **Results**: Uploaded to GitHub Security tab

**Duration**: 2-3 minutes

### View Test Results

```
GitHub → Actions tab → Latest workflow
→ Click workflow name
→ See all job results
```

---

## Deploy Workflow (deploy.yml)

**Trigger**: After test.yml succeeds + manual push

### Prerequisites

Tests must pass:
```
Test workflow ✅ → Deploy workflow ▶️ → Success ✅
```

### Deployment Steps

#### 1. Deploy Frontend

```yaml
- name: Deploy to Vercel
  run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

**What happens**:
1. Installs Vercel CLI
2. Builds Next.js project
3. Pushes to Vercel CDN
4. Updates DNS/caching
5. Returns production URL

**Duration**: 2-4 minutes

#### 2. Deploy Backend

```yaml
- name: Deploy to Railway
  run: railway up --detach
```

**What happens**:
1. Connects to Railway
2. Builds Python app
3. Creates new release
4. Runs migrations (if any)
5. Starts service
6. Returns API URL

**Duration**: 3-5 minutes

#### 3. Health Checks

```yaml
- name: Check frontend health
  run: curl -f https://skillforge-global.vercel.app/api/session/me
```

**What it does**:
- Waits 30 seconds for services to start
- Calls frontend API endpoint
- Calls backend health endpoint
- Verifies both respond

**Duration**: 1 minute

#### 4. Slack Notification

Sends message to #deployments:
```
✅ Frontend deployed to Vercel
✅ Backend deployed to Railway
✅ All systems healthy
```

---

## Workflow Files

### test.yml (Runs on every push/PR)

```yaml
name: Tests & Linting
on:
  push:
    branches: [main, v1.0.0-release, develop]
  pull_request:
    branches: [main, v1.0.0-release, develop]

jobs:
  frontend-tests: ...
  backend-tests: ...
  code-quality: ...
  security-scan: ...
```

### deploy.yml (Runs after tests pass)

```yaml
name: Deploy to Vercel & Railway
on:
  push:
    branches: [main, v1.0.0-release]
  workflow_run:
    workflows: ["Tests & Linting"]
    types: [completed]

jobs:
  deploy-frontend: ...
  deploy-backend: ...
  health-check: ...
  notifications: ...
```

---

## Common Scenarios

### Scenario 1: Push to main

```
1. You push code to main
2. GitHub triggers test.yml automatically
3. Tests run (8-10 min)
4. If all pass → deploy.yml runs (5-10 min)
5. Slack notification sent
6. Site is live!
Total: 15-20 minutes
```

### Scenario 2: Create Pull Request

```
1. You open PR against main
2. GitHub runs test.yml
3. Shows status on PR (passing/failing)
4. NO deployment (only on merge)
5. Reviewers check results
6. Merge if good
7. Deployment happens
```

### Scenario 3: Test Fails

```
1. Test fails in CI
2. GitHub shows ❌ on PR
3. Deployment does NOT happen
4. Fix code locally
5. Push again
6. Tests run again
7. If pass → deploy
```

---

## Monitoring Workflows

### Live View

```
GitHub → Actions tab
→ Click workflow name to see live progress
→ See logs for each step
```

### Check Status

```bash
# Via GitHub CLI
gh workflow list
gh workflow view test.yml --shell

# Or in GitHub UI
Settings → Actions → Workflows
```

### View Logs

```
Actions → Workflow run → Job → Step → View logs
```

**Common logs to check**:
- Build output
- Test results
- Deployment status

---

## Troubleshooting

### Tests Fail on GitHub but Pass Locally

**Causes**:
- Different Python/Node version
- Missing environment variables
- Different database setup

**Fix**:
```bash
# Ensure local matches CI:
python --version  # Match workflow
node --version    # Match workflow
pip install -r requirements.txt  # Fresh install
npm install  # Fresh install
npm test     # Run exact same test
pytest       # Run exact same test
```

### Deploy Fails with Secret Error

**Error**: `secret not found`

**Fix**:
1. Check secret name spelling (case-sensitive)
2. Verify secret exists in Settings → Secrets
3. Verify workflow file has correct name: `${{ secrets.NAME }}`

### Deployment Takes Too Long

**Normal times**:
- Frontend: 2-4 min
- Backend: 3-5 min
- Health check: 1 min
- **Total**: 6-10 min

**If slower**:
- Check service logs
- Verify no large builds
- Check database migrations

### GitHub Actions Quota Exceeded

**Limits**:
- Free tier: 2,000 minutes/month
- With SkillForge: ~100 minutes/month
- You have plenty!

**If exceeded**:
- Optimize workflow (cache dependencies)
- Reduce test matrix (remove Python 3.9?)
- Remove slow jobs

---

## Customization

### Add a New Job

```yaml
jobs:
  existing-job: ...
  
  new-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Do something
        run: echo "Hello!"
```

### Add Environment Variable

```yaml
env:
  MY_VAR: "value"

# Or per job:
jobs:
  my-job:
    env:
      JOB_VAR: "job-value"
```

### Change Trigger Conditions

```yaml
# Currently: Trigger on push/PR to main, v1.0.0-release, develop
# Change to:
on:
  push:
    branches:
      - main
      - production
    paths:
      - 'src/**'  # Only if src/ changes
```

### Parallel vs Sequential

**Parallel** (current):
```yaml
jobs:
  frontend-tests: ...
  backend-tests: ...
  # Both run at same time
```

**Sequential**:
```yaml
jobs:
  frontend-tests: ...
  backend-tests:
    needs: frontend-tests  # Wait for frontend
```

---

## Performance Tips

### Caching

Already enabled:
```yaml
cache: 'npm'  # Caches node_modules
cache: 'pip'  # Caches Python packages
```

**Result**: First run 5 min, subsequent runs 2 min

### Matrix Optimization

Current:
```yaml
matrix:
  node-version: [18.x, 20.x]  # Tests 2 versions
  python-version: ['3.9', '3.11']  # Tests 2 versions
```

**To speed up**:
```yaml
# Only test latest version on PR
# Test all versions only on main push
if: github.ref == 'refs/heads/main'
```

---

## Notifications

### Slack Alerts (Configured)

Sent automatically on:
- ✅ Deployment success
- ❌ Deployment failure
- ⚠️ Health check warning

### Email Alerts

Go to: GitHub → Settings → Notifications
- Email when workflow fails
- Email when workflow succeeds

---

## Cost Analysis

**GitHub Actions Minutes**:
- Frontend tests: ~3 min
- Backend tests: ~4 min
- Code quality: ~1 min
- Security scan: ~2 min
- Deployment: ~8 min
- **Per run**: ~18 minutes

**Monthly usage**:
- ~3 pushes/day = 90 pushes/month
- 90 × 18 min = 1,620 minutes
- Free tier: 2,000 minutes
- **Cost**: FREE ✅

---

## Best Practices

✅ **Do**:
- Run tests before pushing
- Keep workflows focused
- Use caching
- Fail fast (test front, then back)
- Monitor workflow durations

❌ **Don't**:
- Test multiple versions if not needed
- Run expensive jobs on every push
- Ignore workflow failures
- Keep failed branches around
- Use hardcoded values (use secrets)

---

## Quick Reference

### View Workflow Status
```
GitHub.com → Actions tab
```

### Retrigger Workflow
```
Actions → Click workflow → Re-run all jobs
```

### Skip Workflow
```bash
# In commit message:
git commit -m "fix: Something [skip ci]"
```

### Debug Workflow
```yaml
- name: Debug
  run: env | sort  # Show all variables
```

---

## Maintenance

### Update Actions Versions

Periodically update to latest:
```yaml
uses: actions/checkout@v4  # Latest
uses: actions/setup-node@v4  # Latest
```

Check: https://github.com/actions

### Clean Up Old Runs

GitHub → Actions → Click workflow → Workflow runs → Delete old runs

### Monitor Workflow Health

Dashboard:
- GitHub → Insights → Actions
- See runs over time
- Identify trends

---

## Next Steps

1. ✅ Push to main branch
2. ✅ Watch Actions tab
3. ✅ See tests run
4. ✅ See deployment happen
5. ✅ Check site is live
6. ✅ Celebrate! 🎉

---

**Status**: ✅ Pipeline Ready!

**Questions?** See DEPLOYMENT_GUIDE_COMPLETE.md

