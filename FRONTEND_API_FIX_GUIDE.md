# SkillForge Global - API Connectivity Fix & Deployment Guide

## IMMEDIATE ACTION: Forum Connectivity Issue

### Problem
```
GET http://backend:8001/api/v1x/admin/dashboard/stats net::ERR_NAME_NOT_RESOLVED
```

The frontend is trying to reach `http://backend:8001` but that hostname doesn't exist on your host machine.

### Root Cause
- **Docker Container**: Hostname `backend` resolves fine inside Docker network
- **Host Browser**: Hostname `backend` doesn't exist, must use `localhost:8001`
- **The Fix**: Frontend needs to detect environment and use correct API URL

### Solution Applied
Updated `src/lib/api.ts` to automatically detect and fix the API URL:

```typescript
function getApiBase(): string {
  const envBase = process.env.NEXT_PUBLIC_API_BASE?.trim();
  
  // If running in browser, replace internal Docker hostname with localhost
  if (typeof window !== "undefined" && envBase.includes("backend:8001")) {
    return envBase.replace("backend:8001", "localhost:8001");
  }
  
  return envBase || "http://localhost:8001";
}
```

## Step 1: Rebuild & Restart Services

### Full Clean Rebuild
```bash
# Stop all containers
docker-compose down -v

# Rebuild everything
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Wait 15-20 seconds for full initialization
Start-Sleep -Seconds 20
```

### Quick Restart (if containers already built)
```bash
docker-compose down
docker-compose up -d
```

## Step 2: Verify Services Are Running

```bash
# Check all containers
docker ps --filter "name=skillforge"

# Expected output:
# skillforge-postgres    Up and healthy
# skillforge-redis       Up and healthy  
# skillforge-backend     Up and healthy
# skillforge-frontend    Up and healthy
```

### Individual Health Checks

```bash
# Check backend
curl -s http://localhost:8001/healthz

# Check frontend
curl -s http://localhost:3000 | head -20

# Check database
docker exec skillforge-postgres psql -U admin -d skillforge -c "SELECT 1"

# Check Redis
docker exec skillforge-redis redis-cli ping
```

## Step 3: Test API Endpoints

### Test Courses
```bash
$ProgressPreference = 'SilentlyContinue'
(Invoke-WebRequest -Uri 'http://localhost:8001/api/v1/courses' -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -First 2
```

**Expected**: Returns ~5-27 courses

### Test Mentors
```bash
(Invoke-WebRequest -Uri 'http://localhost:8001/api/v1x/mentors' -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -First 2
```

**Expected**: Returns ~4 mentors (Sarah Chen, David Kumar, Emily Rodriguez, James Patterson)

### Test Admin Dashboard
```bash
# First login to get token
$login = @{
    email = "admin@skillforge.com"
    password = "admin123"
} | ConvertTo-Json

$token = (Invoke-WebRequest -Uri 'http://localhost:8001/api/v1/auth/login' -Method POST -Body $login -Headers @{'Content-Type'='application/json'} -UseBasicParsing).Content | ConvertFrom-Json

# Get admin stats (requires token)
$headers = @{'Authorization' = "Bearer $($token.access_token)"; 'Content-Type' = 'application/json'}
(Invoke-WebRequest -Uri 'http://localhost:8001/api/v1x/admin/dashboard/stats' -Headers $headers -UseBasicParsing).Content | ConvertFrom-Json
```

**Expected**: Returns admin dashboard statistics

## Step 4: Test in Browser

### Login Flow
1. Open: http://localhost:3000
2. Login with:
   - Email: `admin@skillforge.com`
   - Password: `admin123`
3. Navigate to admin dashboard

### Should See
- ✅ Courses loading
- ✅ Mentors loading  
- ✅ Admin stats visible
- ✅ Coins balance displaying
- ✅ No console errors starting with `ERR_NAME_NOT_RESOLVED`

## Step 5: Check Browser Console

### Open Dev Tools
- Press `F12` or `Ctrl+Shift+I`
- Go to **Console** tab

### Should NOT See
```
GET http://backend:8001/api/v1x/admin/dashboard/stats net::ERR_NAME_NOT_RESOLVED
GET http://backend:8001/api/v1x/mentors/search? net::ERR_NAME_NOT_RESOLVED
```

### Should See (OK)
```
[HMR] connected
GET http://localhost:8001/api/v1x/admin/dashboard/stats 200 OK
GET http://localhost:8001/api/v1x/mentors/search 200 OK
```

## Step 6: View Network Traffic

### In Dev Tools
1. Go to **Network** tab
2. Refresh page
3. Look for API calls starting with:
   - `admin/dashboard/stats` ✅ (200 status)
   - `mentors/search` ✅ (200 status)
   - `coins_db/balance` ✅ (200 status)

### If You See Red Errors
- Right-click → Copy as cURL
- Test directly in terminal: `curl [copied command]`
- This will show the exact error

## Changes Made

### 1. Frontend API Configuration
**File**: `src/lib/api.ts`

```typescript
// BEFORE: Tried to use backend hostname
const RAW_BASE = process.env.NEXT_PUBLIC_API_BASE?.trim() || "http://localhost:8001";

// AFTER: Detects environment and adjusts URL
function getApiBase(): string {
  const envBase = process.env.NEXT_PUBLIC_API_BASE?.trim();
  
  if (typeof window !== "undefined" && envBase?.includes("backend:8001")) {
    return envBase.replace("backend:8001", "localhost:8001");
  }
  
  return envBase || "http://localhost:8001";
}

const RAW_BASE = getApiBase();
```

### 2. Backend Admin Router Fix
**File**: `backend/app/api/v1x/admin.py`

Added missing function that was causing import errors:

```python
async def get_current_superadmin(
    current_user: User = Depends(require_superadmin)
) -> User:
    """Dependency to get current superadmin user - requires superadmin role only"""
    return current_user
```

## Troubleshooting

### Issue: Still seeing ERR_NAME_NOT_RESOLVED

**Solution 1**: Hard refresh browser
```
Ctrl+Shift+R  (Windows)
Cmd+Shift+R   (Mac)
```

**Solution 2**: Clear browser cache
- Press F12 → Dev Tools
- Right-click refresh icon → "Empty cache and hard reload"

**Solution 3**: Check frontend Docker rebuild
```bash
# Rebuild frontend specifically
docker-compose build --no-cache skillforge-frontend

# Restart just frontend
docker-compose restart skillforge-frontend

# Wait a few seconds, then refresh browser
```

### Issue: Still 404 or 500 Errors

```bash
# Check backend logs for errors
docker logs skillforge-backend --tail 50

# Check frontend logs
docker logs skillforge-frontend --tail 50

# Look for stack traces or "ERROR" messages
```

### Issue: Database Connection Failed

```bash
# Verify database is healthy
docker exec skillforge-postgres pg_isready -U admin -h localhost

# Check database exists
docker exec skillforge-postgres psql -U admin -l

# Verify tables created
docker exec skillforge-postgres psql -U admin -d skillforge -c "\dt" | head -20
```

### Issue: Mentors Not Showing

```bash
# Query database directly
docker exec skillforge-postgres psql -U admin -d skillforge -c "SELECT COUNT(*) FROM mentors;"

# Should return: count = 4
```

## Git Commit

**Last Commit**: "fix: resolve frontend API connectivity issues and add missing get_current_superadmin function"

**Files Changed**:
- `src/lib/api.ts` - Smart API URL detection
- `backend/app/api/v1x/admin.py` - Added get_current_superadmin

**Date**: March 15, 2026

**To Push to Remote**:
```bash
git add .
git commit -m "fix: API connectivity and admin router issues"
git push origin main
```

## Development Credentials

```
SuperAdmin:
  Email: superadmin@skillforge.com
  Password: admin123

Admin:
  Email: admin@skillforge.com
  Password: admin123

Regular Users:
  Email: john.doe@example.com
  Password: password123
  (Same password for all demo users)
```

## Environment URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3000 | Browser |
| Backend API | http://localhost:8001 | Terminal |
| Database (Adminer) | http://localhost:8080 | Browser |
| Database (pgAdmin) | http://localhost:5050 | Browser |
| Redis | localhost:6379 | CLI |

## Architecture

```
┌─────────────────────────────────────┐
│     Browser (Your Machine)          │
│  http://localhost:3000              │
│  ✓ Frontend (Next.js)               │
│    Calls: http://localhost:8001     │
└──────────────┬──────────────────────┘
               │
        HTTP Request │ Response
               │
        ┌──────▼──────────────────────┐
        │   Docker Network            │
        │   skillforge-network        │
        │                             │
        │  ┌──────────────────────┐   │
        │  │ skillforge-backend   │   │
        │  │ port: 8001           │   │
        │  │                      │   │
        │  │ ┌────────────────┐   │   │
        │  │ │ FastAPI Server │   │   │
        │  │ └────────────────┘   │   │
        │  └──────────┬───────────┘   │
        │             │                │
        │        Database             │
        │        Redis                │
        │                             │
        └─────────────────────────────┘
```

**Key Point**: 
- Inside Docker: Frontend uses `http://backend:8001` ✓
- From Host Machine: Frontend uses `http://localhost:8001` ✓
- Smart detection handles both cases automatically ✓

## Next Steps

1. **Restart Services** (Step 1)
2. **Verify Health** (Step 2)
3. **Test Endpoints** (Step 3)
4. **Test in Browser** (Step 4)
5. **Check Console** (Step 5)
6. **Push to Repo** when verified working

## Support

If issues persist:

1. **Collect logs**:
   ```bash
   docker logs skillforge-backend > backend.log
   docker logs skillforge-frontend > frontend.log
   ```

2. **Share logs** with development team

3. **Check Docker** is running:
   ```bash
   docker --version
   docker-compose --version
   ```
