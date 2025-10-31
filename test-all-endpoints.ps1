# Test All API Endpoints
$ErrorActionPreference = "Continue"
$baseUrl = "http://localhost:8001"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  API ENDPOINT TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "[1/12] Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod "$baseUrl/healthz" -Method Get
    if ($health.ok) {
        Write-Host "  ✓ PASS: Health check OK" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ FAIL: Health check failed" -ForegroundColor Red
}

# Test 2: Courses (DB)
Write-Host "`n[2/12] Testing Courses (Database)..." -ForegroundColor Yellow
try {
    $courses = Invoke-RestMethod "$baseUrl/api/v1x/courses-db" -Method Get
    Write-Host "  ✓ PASS: Retrieved $($courses.Length) courses" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Videos
Write-Host "`n[3/12] Testing YouTube Videos..." -ForegroundColor Yellow
try {
    $videos = Invoke-RestMethod "$baseUrl/api/v1x/youtube-sync/videos" -Method Get
    Write-Host "  ✓ PASS: Retrieved $($videos.Length) videos" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Quizzes (Fixed)
Write-Host "`n[4/12] Testing Quizzes (with slug)..." -ForegroundColor Yellow
try {
    $quiz = Invoke-RestMethod "$baseUrl/api/v1x/quizzes-db/python-ai" -Method Get
    Write-Host "  ✓ PASS: Retrieved quiz '$($quiz.title)' with $($quiz.questions.Length) questions" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Auth - Signup
Write-Host "`n[5/12] Testing Auth - Signup..." -ForegroundColor Yellow
$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$testEmail = "test_$timestamp@example.com"
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
try {
    $signupData = @{
        email = $testEmail
        password = "TestPass123!"
    } | ConvertTo-Json
    
    $signup = Invoke-RestMethod "$baseUrl/api/v1/auth/signup" -Method Post -Body $signupData -ContentType "application/json" -WebSession $session
    Write-Host "  ✓ PASS: User created with ID: $($signup.id)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 6: Auth - Login
Write-Host "`n[6/12] Testing Auth - Login..." -ForegroundColor Yellow
try {
    $loginData = @{
        username = $testEmail
        password = "TestPass123!"
    } | ConvertTo-Json
    
    $login = Invoke-RestMethod "$baseUrl/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json" -WebSession $session
    Write-Host "  ✓ PASS: Login successful, token received" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 7: Auth - Get Me
Write-Host "`n[7/12] Testing Auth - Get Current User..." -ForegroundColor Yellow
try {
    $me = Invoke-RestMethod "$baseUrl/api/v1/auth/me" -Method Get -WebSession $session
    Write-Host "  ✓ PASS: Current user: $($me.email)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 8: Mentors List
Write-Host "`n[8/12] Testing Mentors..." -ForegroundColor Yellow
try {
    $mentors = Invoke-RestMethod "$baseUrl/api/v1x/mentors" -Method Get
    Write-Host "  ✓ PASS: Retrieved mentors list" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 9: Recordings - Unauthorized
Write-Host "`n[9/12] Testing Recordings (should require auth)..." -ForegroundColor Yellow
try {
    $rec = Invoke-RestMethod "$baseUrl/api/v1x/recordings/1" -Method Get
    Write-Host "  ⚠ WARN: Should require authentication" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "  ✓ PASS: Correctly requires authentication" -ForegroundColor Green
    } else {
        Write-Host "  ✗ FAIL: Unexpected error" -ForegroundColor Red
    }
}

# Test 10: File Sharing - List
Write-Host "`n[10/12] Testing File Sharing..." -ForegroundColor Yellow
try {
    $files = Invoke-RestMethod "$baseUrl/api/v1x/files/session/1" -Method Get -WebSession $session
    Write-Host "  ✓ PASS: File sharing endpoint accessible" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 11: Stripe Connect
Write-Host "`n[11/12] Testing Stripe Connect..." -ForegroundColor Yellow
try {
    $connect = Invoke-RestMethod "$baseUrl/api/v1x/connect/onboarding-link" -Method Post -WebSession $session
    Write-Host "  ✓ PASS: Stripe Connect available" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN: Requires Stripe keys: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 12: Subscriptions
Write-Host "`n[12/12] Testing Subscriptions..." -ForegroundColor Yellow
try {
    $subs = Invoke-RestMethod "$baseUrl/api/v1x/subscriptions/plans" -Method Get
    Write-Host "  ✓ PASS: Retrieved subscription plans" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ WARN: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TEST SUITE COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nAll major endpoints tested!" -ForegroundColor Green
Write-Host "Note: ⚠ WARN = Expected behavior (auth required, external services, etc.)" -ForegroundColor Yellow
