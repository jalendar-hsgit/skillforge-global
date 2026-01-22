# Test Video Progress & Badges Features
# Usage: .\test_progress_badges.ps1

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 50)
Write-Host "VIDEO PROGRESS & BADGES TEST SUITE" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 50)
Write-Host ""

# Step 1: Login and get token
Write-Host "[1/7] Logging in..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"email":"john.doe@example.com","password":"password123"}' `
        -ErrorAction Stop
    
    $TOKEN = $loginResponse.access_token
    Write-Host "✓ Login successful" -ForegroundColor Green
    Write-Host "  Token: $($TOKEN.Substring(0,20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Test Progress API - Create Progress Record
Write-Host "[2/7] Testing Progress API (POST progress)..." -ForegroundColor Yellow
try {
    $progressResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/progress-db" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{"Authorization" = "Bearer $TOKEN"} `
        -Body '{"video_id":1,"progress_percent":25}' `
        -ErrorAction Stop
    
    Write-Host "✓ Progress update successful" -ForegroundColor Green
    Write-Host "  Response: $($progressResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Progress update failed: $_" -ForegroundColor Red
}

Write-Host ""

# Step 3: Test Progress API - Get Progress
Write-Host "[3/7] Testing Progress API (GET progress)..." -ForegroundColor Yellow
try {
    $progressList = Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/progress-db" `
        -Method GET `
        -ContentType "application/json" `
        -Headers @{"Authorization" = "Bearer $TOKEN"} `
        -ErrorAction Stop
    
    Write-Host "✓ Progress retrieval successful" -ForegroundColor Green
    Write-Host "  Found $($progressList.Count) progress records" -ForegroundColor Gray
    if ($progressList -and $progressList[0]) {
        Write-Host "  Sample: video_id=$($progressList[0].video_id), progress=$($progressList[0].progress_percent)%" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Progress retrieval failed: $_" -ForegroundColor Red
}

Write-Host ""

# Step 4: Test Badge System - Get All Badges
Write-Host "[4/7] Testing Badge System (GET all badges)..." -ForegroundColor Yellow
try {
    $badges = Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/badges" `
        -Method GET `
        -ContentType "application/json" `
        -Headers @{"Authorization" = "Bearer $TOKEN"} `
        -ErrorAction Stop
    
    Write-Host "✓ Badge retrieval successful" -ForegroundColor Green
    Write-Host "  Found $($badges.Count) badges in system" -ForegroundColor Gray
    if ($badges -and $badges[0]) {
        Write-Host "  Sample: $($badges[0].name) ($($badges[0].rarity))" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Badge retrieval failed: $_" -ForegroundColor Red
}

Write-Host ""

# Step 5: Test User Earned Badges
Write-Host "[5/7] Testing User Earned Badges..." -ForegroundColor Yellow
try {
    $earnedBadges = Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/badges/user/earned" `
        -Method GET `
        -ContentType "application/json" `
        -Headers @{"Authorization" = "Bearer $TOKEN"} `
        -ErrorAction Stop
    
    Write-Host "✓ User earned badges retrieval successful" -ForegroundColor Green
    Write-Host "  User has $($earnedBadges.Count) earned badges" -ForegroundColor Gray
    if ($earnedBadges -and $earnedBadges[0]) {
        Write-Host "  Sample: $($earnedBadges[0].badge.name) earned on $($earnedBadges[0].first_earned_at)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ User earned badges failed: $_" -ForegroundColor Red
}

Write-Host ""

# Step 6: Test Badge Stats
Write-Host "[6/7] Testing Badge Stats..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/badges/user/stats" `
        -Method GET `
        -ContentType "application/json" `
        -Headers @{"Authorization" = "Bearer $TOKEN"} `
        -ErrorAction Stop
    
    Write-Host "✓ Badge stats retrieval successful" -ForegroundColor Green
    Write-Host "  Total earned: $($stats.total_earned_badges)" -ForegroundColor Gray
    Write-Host "  Total points: $($stats.total_points)" -ForegroundColor Gray
    Write-Host "  In progress: $($stats.in_progress_count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Badge stats failed: $_" -ForegroundColor Red
}

Write-Host ""

# Step 7: Test Core Endpoints (Regression)
Write-Host "[7/7] Regression Testing (existing endpoints)..." -ForegroundColor Yellow
try {
    # Test courses endpoint
    $courses = Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/courses" `
        -Method GET `
        -Headers @{"Authorization" = "Bearer $TOKEN"} `
        -ErrorAction Stop
    Write-Host "✓ Courses endpoint working - $($courses.Count) courses" -ForegroundColor Green
    
    # Test mentors endpoint
    $mentors = Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/mentors" `
        -Method GET `
        -Headers @{"Authorization" = "Bearer $TOKEN"} `
        -ErrorAction Stop
    Write-Host "✓ Mentors endpoint working - $($mentors.Count) mentors" -ForegroundColor Green
} catch {
    Write-Host "✗ Regression test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 50)
Write-Host "TEST SUITE COMPLETE" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 50)
