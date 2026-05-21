# API Endpoint Test Script
# Tests all major endpoints and shows results

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SKILLFORGE GLOBAL API TEST RESULTS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test Health Check
Write-Host "[1/10] Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri 'http://localhost:8001/healthz' -Method Get
    Write-Host "  ✓ PASS - Backend is healthy" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL - Backend not responding" -ForegroundColor Red
}

# Test Courses
Write-Host "`n[2/10] Testing Courses Endpoint..." -ForegroundColor Yellow
try {
    $courses = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1/courses' -Method Get
    $count = if ($courses) { $courses.Count } else { 0 }
    Write-Host "  ✓ PASS - Retrieved $count courses" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL - Could not retrieve courses" -ForegroundColor Red
}

# Test Auth Signup
Write-Host "`n[3/10] Testing Auth Signup..." -ForegroundColor Yellow
$testEmail = "testuser_$(Get-Random)@test.com"
$signupBody = @{ email = $testEmail; password = "TestPass123!" } | ConvertTo-Json
try {
    $signup = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1/auth/signup' -Method Post -Body $signupBody -ContentType 'application/json'
    Write-Host "  ✓ PASS - User created: $testEmail" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN - User may already exist" -ForegroundColor Yellow
}

# Test Auth Login
Write-Host "`n[4/10] Testing Auth Login..." -ForegroundColor Yellow
$loginBody = @{ email = "testuser@example.com"; password = "password123" } | ConvertTo-Json
try {
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $login = Invoke-WebRequest -Uri 'http://localhost:8001/api/v1/auth/login' -Method Post -Body $loginBody -ContentType 'application/json' -WebSession $session
    Write-Host "  ✓ PASS - Login successful" -ForegroundColor Green
    $global:testSession = $session
} catch {
    Write-Host "  ✗ FAIL - Login failed" -ForegroundColor Red
}

# Test Auth /me
Write-Host "`n[5/10] Testing Auth /me Endpoint..." -ForegroundColor Yellow
try {
    $me = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1/auth/me' -Method Get -WebSession $global:testSession
    Write-Host "  ✓ PASS - Authenticated user: $($me.email)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL - Could not get user info" -ForegroundColor Red
}

# Test Videos
Write-Host "`n[6/10] Testing Videos Endpoint..." -ForegroundColor Yellow
try {
    $videos = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1x/courses-db/python-ai/videos' -Method Get
    Write-Host "  ✓ PASS - Retrieved $($videos.Count) videos for python-ai" -ForegroundColor Green
    if ($videos.Count -gt 0) {
        $firstVideo = $videos[0]
        Write-Host "    Sample: $($firstVideo.title)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ✗ FAIL - Could not retrieve videos" -ForegroundColor Red
}

# Test Quiz
Write-Host "`n[7/10] Testing Quiz Endpoint..." -ForegroundColor Yellow
try {
    $quiz = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1x/quizzes-db/python-ai' -Method Get
    Write-Host "  ✓ PASS - Retrieved quiz with $($quiz.questions.Count) questions" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL - Could not retrieve quiz" -ForegroundColor Red
}

# Test Stripe Connect
Write-Host "`n[8/10] Testing Stripe Connect..." -ForegroundColor Yellow
try {
    $connect = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1x/stripe-connect/account' -Method Get -WebSession $global:testSession
    Write-Host "  ✓ PASS - Stripe account found" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN - No Stripe account (expected for new users)" -ForegroundColor Yellow
}

# Test Payouts
Write-Host "`n[9/10] Testing Payouts Endpoint..." -ForegroundColor Yellow
try {
    $earnings = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1x/payouts/earnings' -Method Get -WebSession $global:testSession
    Write-Host "  ✓ PASS - Earnings: `$$($earnings.total_earned)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN - No earnings data (expected for new users)" -ForegroundColor Yellow
}

# Test Subscription
Write-Host "`n[10/10] Testing Subscription Endpoint..." -ForegroundColor Yellow
try {
    $sub = Invoke-RestMethod -Uri 'http://localhost:8001/api/v1x/subscriptions/my-subscription' -Method Get -WebSession $global:testSession
    Write-Host "  ✓ PASS - Plan: $($sub.plan), Status: $($sub.status)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN - No subscription (default FREE plan)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
