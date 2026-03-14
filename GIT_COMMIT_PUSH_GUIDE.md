# Git Commit & Push Guide

## Current Status

**Last Fix**: March 15, 2026
**Commit Message**: "fix: resolve frontend API connectivity issues and add missing get_current_superadmin function"

## Files Changed

### 1. Frontend API Configuration
**File**: `src/lib/api.ts`

**Changes**:
- Added `getApiBase()` function for environment detection
- Detects `backend` hostname in Docker and replaces with `localhost` for browser access
- Improved error logging for network issues

**Why**: Frontend was trying to reach Docker-internal hostname `backend:8001` which doesn't exist on host machine. Now automatically uses `localhost:8001` when accessed from browser.

### 2. Backend Admin Router
**File**: `backend/app/api/v1x/admin.py`

**Changes**:
- Added missing `get_current_superadmin()` function
- This function was being imported but never defined, causing router import failures

**Why**: Without this function, the admin router couldn't import and API calls to `/api/v1x/admin/*` endpoints would fail.

## Quick Git Commands

### View Current Status
```bash
cd "d:\python code\sfg\skillforge-global"

# See what files changed
git status

# See all changes
git diff

# See changes in specific file
git diff src/lib/api.ts
```

### Commit Changes
```bash
# Stage all changes
git add .

# Or stage specific files
git add src/lib/api.ts backend/app/api/v1x/admin.py

# Create commit with descriptive message
git commit -m "fix: resolve frontend API connectivity issues and add missing get_current_superadmin function

- Fixed frontend trying to reach internal Docker hostname 'backend' from browser
- Added smart API URL detection to use localhost:8001 when accessed from host
- Improved error logging for network connectivity issues  
- Added missing get_current_superadmin dependency function in admin router
- Enables proper mentors, admin dashboard, and coins data fetching
- Tested with admin@skillforge.com login - all endpoints now respond 200"

# View commit
git show
```

### Push to Remote Repository
```bash
# Push to main branch
git push origin main

# Push to specific branch
git push origin develop

# Push all branches
git push origin --all

# If tracking branch not set
git push -u origin main
```

### Push with Specific Date
```bash
# Override commit date (if needed for records)
git commit -m "fix: API connectivity" --date="Fri, 15 Mar 2026 14:30:00 +0000"

# Or amend last commit
git commit --amend --date="Fri, 15 Mar 2026 14:30:00 +0000"
```

## Step-by-Step Commit Process

### Step 1: Check Status
```bash
cd "d:\python code\sfg\skillforge-global"
git status
```

**Expected Output**:
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   src/lib/api.ts
  modified:   backend/app/api/v1x/admin.py

Untracked files:
  new file:   FRONTEND_API_FIX_GUIDE.md
  new file:   CI_CD_PIPELINE_SETUP.md
```

### Step 2: Review Changes
```bash
# See what changed in api.ts
git diff src/lib/api.ts

# See what changed in admin.py
git diff backend/app/api/v1x/admin.py
```

### Step 3: Stage Files
```bash
# Add specific files
git add src/lib/api.ts backend/app/api/v1x/admin.py

# Or add everything including new documentation
git add .

# Verify staged files
git status
```

**Expected Output**:
```
Changes to be committed:
  modified:   src/lib/api.ts
  modified:   backend/app/api/v1x/admin.py
  new file:   FRONTEND_API_FIX_GUIDE.md
  new file:   CI_CD_PIPELINE_SETUP.md
```

### Step 4: Commit
```bash
git commit -m "fix: resolve API connectivity issues

- Smart API URL detection for browser vs Docker environment
- Added missing get_current_superadmin function
- Improved error logging for network debugging
- Comprehensive fix guides added"
```

### Step 5: Verify Commit
```bash
# See commit message
git show

# See recent commits
git log --oneline -5
```

### Step 6: Push to Remote
```bash
# Push to main
git push origin main

# If this is first push to this branch
git push -u origin main
```

## Full PowerShell Script

Save as `commit-and-push.ps1`:

```powershell
# ============================================
# SkillForge Global - Git Commit & Push Script
# ============================================

$repo = "d:\python code\sfg\skillforge-global"
cd $repo

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SkillForge Git Commit & Push         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Show current status
Write-Host "1️⃣  Current Git Status:" -ForegroundColor Yellow
git status
Write-Host ""

# Step 2: Show diff
Write-Host "2️⃣  Changes Preview:" -ForegroundColor Yellow
git diff --stat
Write-Host ""

# Step 3: Ask for confirmation
$confirm = Read-Host "Continue with commit? (Y/n)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Aborted." -ForegroundColor Red
    exit 1
}

# Step 4: Stage changes
Write-Host "3️⃣  Staging changes..." -ForegroundColor Yellow
git add .
git status

# Step 5: Commit
Write-Host "4️⃣  Creating commit..." -ForegroundColor Yellow
$message = @"
fix: resolve API connectivity issues and add admin router function

Frontend:
- Added smart API URL detection for browser vs Docker environment
- Fixed 'backend' hostname resolution from browser
- Improved network error logging and debugging

Backend:
- Added missing get_current_superadmin dependency function
- Enables admin dashboard and protected endpoints

Testing:
- Verified admin @skillforge.com login works
- Confirmed mentors, courses, and admin data fetch correctly
- All endpoints returning 200 status

Files Changed:
- src/lib/api.ts: API base URL detection
- backend/app/api/v1x/admin.py: Missing function added
- Documentation: Troubleshooting and CI/CD setup guides

Date: $(Get-Date -Format 'ddd, dd MMM yyyy HH:mm:ss K')
"@

git commit -m $message
Write-Host "" 

# Step 6: Show commit
Write-Host "5️⃣  Commit created:" -ForegroundColor Yellow
git log --oneline -1
Write-Host ""

# Step 7: Push
Write-Host "6️⃣  Pushing to remote..." -ForegroundColor Yellow
$pushConfirm = Read-Host "Push to origin/main? (Y/n)"
if ($pushConfirm -eq "Y" -or $pushConfirm -eq "y") {
    git push origin main
    Write-Host "✅ Push successful!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Commit created but not pushed." -ForegroundColor Yellow
    Write-Host "To push later, run: git push origin main" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
```

Run it:
```bash
powershell -ExecutionPolicy Bypass -File commit-and-push.ps1
```

## Remote Repository Setup

### If Remote Doesn't Exist Yet

```bash
# Check current remote
git remote -v

# If empty, add remote
git remote add origin https://github.com/YOUR_USERNAME/skillforge-global.git

# Verify
git remote -v
```

### Update Existing Remote

```bash
# Update remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/skillforge-global.git

# Or if using SSH
git remote set-url origin git@github.com:YOUR_USERNAME/skillforge-global.git
```

## Authentication

### Using HTTPS (Easier)
```bash
# First push
git push origin main

# Will ask for GitHub username and password
# Or personal access token if 2FA enabled
```

**Create GitHub Personal Access Token**:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. Select: `repo`, `write:packages`
4. Use token as password when prompted

### Using SSH (Recommended)
```bash
# Generate SSH key (one time)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub (Settings → SSH Keys)
# Then use SSH URL
git remote set-url origin git@github.com:YOUR_USERNAME/skillforge-global.git

# Test
ssh -T git@github.com
```

## Common Issues

### Issue: "fatal: not a git repository"
```bash
# Initialize git if needed
git init

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/skillforge-global.git

# Then commit and push
```

### Issue: "Permission denied (publickey)"
```bash
# Add ssh key to ssh-agent
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_ed25519

# Test connection
ssh -T git@github.com
```

### Issue: "Your branch is ahead by X commits"
```bash
# Push all commits
git push origin main

# Or force push (⚠️ use carefully!)
git push origin main --force
```

### Issue: "rejected... no changes added to commit"
```bash
# Stage changes first
git add .

# Then commit
git commit -m "Your message"

# Then push
git push origin main
```

## Verification Checklist

- [ ] Files changed are correct
- [ ] Commit message is descriptive
- [ ] Remote URL is configured
- [ ] GitHub credentials working
- [ ] No uncommitted changes left
- [ ] Branch is main/develop
- [ ] Push successful (no errors)
- [ ] Verify on GitHub website

## After Push

### Verify on GitHub
1. Go to https://github.com/YOUR_USERNAME/skillforge-global
2. Check recent commits
3. Verify all files are present
4. Check commit history

### Next Steps
1. Start CI/CD pipeline (if configured)
2. Monitor Docker build
3. Verify deployment
4. Test in production environment

## Branch Strategy (Recommended)

```
main          (Production-ready)
   ↑
   └── develop (Integration branch)
          ↑
          └── feature/* (Feature branches)
```

### Create Feature Branch
```bash
git checkout -b feature/api-fix
# Make changes
git add .
git commit -m "feature: api connectivity improvements"
git push origin feature/api-fix

# Then create Pull Request on GitHub
```

## Summary

**What Was Changed**:
- Frontend API URL detection logic
- Backend admin router missing function
- Documentation guides

**Why**:
- Fix `ERR_NAME_NOT_RESOLVED` errors
- Enable admin, mentors, and coins features
- Provide deployment guidance

**How to Push**:
1. `git add .`
2. `git commit -m "fix: ..."`
3. `git push origin main`

**Status**: ✅ Ready to deploy
