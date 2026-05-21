# API Endpoint Test Script
# Run this to quickly verify all endpoints are working

Write-Host "`n=== SkillForge Global - API Endpoint Tests ===" -ForegroundColor Cyan
Write-Host "Testing backend at http://localhost:8001`n" -ForegroundColor Gray

$passed = 0
$failed = 0

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Url,
        [string]$Description,
        [int]$ExpectedStatus = 200,
        [bool]$RequiresAuth = $false
    )
    
    Write-Host "Testing: $Description" -ForegroundColor Yellow
    Write-Host "  $Method $Url" -ForegroundColor Gray
    
    try {
        $headers = @{}
        if ($RequiresAuth -and $global:AuthToken) {
            $headers["Cookie"] = "token=$global:AuthToken"
        }
        
        $response = Invoke-WebRequest -Uri $Url -Method $Method -Headers $headers -UseBasicParsing -ErrorAction Stop
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  ✓ PASS (Status: $($response.StatusCode))" -ForegroundColor Green
            $script:passed++
            return $true
        } else {
            Write-Host "  ✗ FAIL (Expected: $ExpectedStatus, Got: $($response.StatusCode))" -ForegroundColor Red
            $script:failed++
            return $false
        }
    } catch {
        Write-Host "  ✗ FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $script:failed++
        return $false
    }
}

# Core Endpoints
Write-Host "`n--- Core Endpoints ---" -ForegroundColor Cyan
Test-Endpoint "GET" "http://localhost:8001/healthz" "Health Check"
Test-Endpoint "GET" "http://localhost:8001/docs" "API Documentation" 200
Test-Endpoint "GET" "http://localhost:8001/openapi.json" "OpenAPI Schema"

# Courses
Write-Host "`n--- Courses ---" -ForegroundColor Cyan
Test-Endpoint "GET" "http://localhost:8001/api/v1/courses" "List All Courses"
Test-Endpoint "GET" "http://localhost:8001/api/v1/paths" "List Learning Paths"

# Subscription Endpoints
Write-Host "`n--- Subscriptions ---" -ForegroundColor Cyan
Test-Endpoint "GET" "http://localhost:8001/api/v1x/subscriptions/plans" "Subscription Plans"

# Try to create a test user and get auth token
Write-Host "`n--- Authentication ---" -ForegroundColor Cyan
$testEmail = "apitest_$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
$testPassword = "TestPass123!"

try {
    Write-Host "Creating test user..." -ForegroundColor Yellow
    $signupBody = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $signupResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/signup" `
        -Method POST `
        -Body $signupBody `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "  ✓ Signup successful" -ForegroundColor Green
    $script:passed++
    
    # Try to login
    Write-Host "Logging in..." -ForegroundColor Yellow
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/login" `
        -Method POST `
        -Body $signupBody `
        -ContentType "application/json" `
        -UseBasicParsing `
        -SessionVariable session `
        -ErrorAction Stop
    
    # Extract token from Set-Cookie header
    $setCookie = $loginResponse.Headers['Set-Cookie']
    if ($setCookie -match 'token=([^;]+)') {
        $global:AuthToken = $matches[1]
        Write-Host "  ✓ Login successful (Token: $($global:AuthToken.Substring(0, 20))...)" -ForegroundColor Green
        $script:passed++
        
        # Test authenticated endpoint
        Test-Endpoint "GET" "http://localhost:8001/api/v1/auth/me" "Get Current User" 200 $true
        Test-Endpoint "GET" "http://localhost:8001/api/v1x/subscriptions/current" "Current Subscription" 200 $true
    } else {
        Write-Host "  ✗ Failed to extract auth token" -ForegroundColor Red
        $script:failed++
    }
    
} catch {
    Write-Host "  ✗ Auth test failed: $($_.Exception.Message)" -ForegroundColor Red
    $script:failed += 2
}

# Stripe Connect Endpoints
Write-Host "`n--- Stripe Connect ---" -ForegroundColor Cyan
Test-Endpoint "GET" "http://localhost:8001/api/v1x/connect/status" "Connect Status" -RequiresAuth $true

# Mentor Payouts
Write-Host "`n--- Mentor Payouts ---" -ForegroundColor Cyan
Test-Endpoint "GET" "http://localhost:8001/api/v1x/mentors/payouts/summary" "Payout Summary" -RequiresAuth $true

# Frontend
Write-Host "`n--- Frontend ---" -ForegroundColor Cyan
Test-Endpoint "GET" "http://localhost:3000" "Frontend Home" 200

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "Total:  $($passed + $failed)`n"

if ($failed -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ Some tests failed. Check the output above." -ForegroundColor Red
    exit 1
}
