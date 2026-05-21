# Next.js Dev Mode Watchpack Error - Workaround

## Issue

Next.js 14.2.33 has a watchpack TypeError that prevents `npm run dev` from starting:

```
TypeError [ERR_INVALID_ARG_TYPE]: The "to" argument must be of type string. Received undefined
    at Object.relative (node:path:554:5)
    at Watchpack.<anonymous> (.../setup-dev-bundler.js:381:55)
```

## Root Cause

This is a known bug in Next.js 14.2.33 where the file watcher receives `undefined` paths, likely due to:
- Complex directory structures with spaces in path names (`d:\python code\sfg\...`)
- Interaction between Windows paths and Next.js watchpack
- File watching across mixed content (Python backend + Node.js frontend)

## Attempted Fixes (All Failed)

✗ Webpack watchOptions configuration  
✗ Polling mode (`WATCHPACK_POLLING=true`)  
✗ Ignoring specific directories  
✗ Snapshot configuration  
✗ Environment variables

## **Working Solution: Use Production Mode**

### Option 1: Production Build (Recommended for Testing)

```powershell
# Build once
npm run build

# Start production server
npm start
```

**Pros:**
- Stable, no watchpack errors
- Fast page loads
- Works reliably for E2E tests

**Cons:**
- Need to rebuild after code changes
- No hot reload

### Option 2: Upgrade Next.js (Future Fix)

```powershell
# Upgrade to latest Next.js (when ready)
npm install next@latest react@latest react-dom@latest
```

### Option 3: Development with Manual Rebuild

```powershell
# Terminal 1: Watch for changes and auto-rebuild
while ($true) { 
  npm run build
  Start-Sleep -Seconds 30
}

# Terminal 2: Run production server
npm start
```

## Current Workflow

**For E2E Testing:**
```powershell
# 1. Build frontend
npm run build

# 2. Start backend (Terminal 1)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 3. Start frontend (Terminal 2)
npm start

# 4. Run E2E tests (Terminal 3)
$env:SKIP_WEBSERVER="1"
npx playwright test e2e/mentor-session-actions.spec.ts
```

**For Backend Testing (Recommended):**
```powershell
cd backend
$env:PYTHONIOENCODING="utf-8"
$env:AUTO_RUN="1"
python test_mentor_api.py
```

## Upgrade Path

When upgrading Next.js to fix this issue:

1. Check Next.js release notes for watchpack fixes
2. Test with `npm install next@14.3.0` (or latest)
3. Run `npm run dev` to verify fix
4. Update this document if resolved

## Related Issues

- Next.js GitHub: Similar watchpack errors in 14.2.x
- Related to: Windows path handling, file watching in monorepos
- Workaround documented: Use production mode for stability
