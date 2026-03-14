#!/usr/bin/env pwsh
# API Fix - Quick Command Reference
# Run these commands to verify everything works

Write-Host "=== SkillForge Global - API Fix Verification ===" -ForegroundColor Green

# 1. Check containers
Write-Host "`n1. Checking Docker containers..." -ForegroundColor Cyan
docker ps --filter "name=skillforge" --format "table {{.Names}}\t{{.Status}}"

# 2. Test backend health
Write-Host "`n2. Testing backend health..." -ForegroundColor Cyan
try {
    $health = Invoke-WebRequest -Uri 'http://localhost:8001/healthz' -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend healthy (HTTP 200)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding" -ForegroundColor Red
}

# 3. Test courses endpoint
Write-Host "`n3. Testing courses API..." -ForegroundColor Cyan
try {
    $courses = (Invoke-WebRequest -Uri 'http://localhost:8001/api/v1/courses' -UseBasicParsing -TimeoutSec 5).Content | ConvertFrom-Json
    $courseCount = if ($courses -is [array]) { $courses.Count } else { 1 }
    Write-Host "✅ Courses API working ($courseCount courses found)" -ForegroundColor Green
} catch {
    Write-Host "❌ Courses API failed" -ForegroundColor Red
}

# 4. Test mentors endpoint
Write-Host "`n4. Testing mentors API..." -ForegroundColor Cyan
try {
    $mentors = (Invoke-WebRequest -Uri 'http://localhost:8001/api/v1x/mentors' -UseBasicParsing -TimeoutSec 5).Content | ConvertFrom-Json
    $mentorCount = if ($mentors -is [array]) { $mentors.Count } else { 1 }
    Write-Host "✅ Mentors API working ($mentorCount mentors found)" -ForegroundColor Green
} catch {
    Write-Host "❌ Mentors API failed" -ForegroundColor Red
}

# 5. Summary
Write-Host "`n5. Summary:" -ForegroundColor Cyan
Write-Host "✅ All checks complete!" -ForegroundColor Green
Write-Host "`nTo test in browser:"
Write-Host "  1. Open: http://localhost:3000"
Write-Host "  2. Login with: admin@skillforge.com / admin123"
Write-Host "  3. Press F12 and check Console for errors"
Write-Host "  4. Verify mentors and admin data loading"
