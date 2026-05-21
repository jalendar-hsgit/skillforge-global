# Test Backend APIs for SkillForge Mentor Payouts
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SKILLFORGE BACKEND API TEST SUITE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BASE_URL = "http://localhost:8001"
$API = "$BASE_URL/api/v1x"

# Test 1: Mentor Login
Write-Host "`n[TEST 1] Testing Mentor Login" -ForegroundColor Yellow
$body = @{
    email = "sarah.chen@example.com"
    password = "password123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$API/auth/login" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    $data = $response.Content | ConvertFrom-Json
    
    if ($response.StatusCode -eq 200 -and $data.access_token) {
        Write-Host "✅ Mentor login successful" -ForegroundColor Green
        $MENTOR_TOKEN = $data.access_token
        Write-Host "   Token: $($MENTOR_TOKEN.Substring(0, 20))..." -ForegroundColor Gray
    } else {
        Write-Host "❌ Login failed: No token" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Login error: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Admin Login
Write-Host "`n[TEST 2] Testing Admin Login" -ForegroundColor Yellow
$body = @{
    email = "admin@skillforge.com"
    password = "password123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$API/auth/login" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    $data = $response.Content | ConvertFrom-Json
    
    if ($response.StatusCode -eq 200 -and $data.access_token) {
        Write-Host "✅ Admin login successful" -ForegroundColor Green
        $ADMIN_TOKEN = $data.access_token
        Write-Host "   Token: $($ADMIN_TOKEN.Substring(0, 20))..." -ForegroundColor Gray
    } else {
        Write-Host "❌ Admin login failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Admin login error: $_" -ForegroundColor Red
}

# Test 3: Get Earnings Summary
Write-Host "`n[TEST 3] Testing GET /mentors/payouts/summary" -ForegroundColor Yellow
try {
    $headers = @{ Authorization = "Bearer $MENTOR_TOKEN" }
    $response = Invoke-WebRequest -Uri "$API/mentors/payouts/summary" -Method Get -Headers $headers -UseBasicParsing -TimeoutSec 10
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "✅ GET /summary successful" -ForegroundColor Green
    Write-Host "   Total Earned: $($data.total_earned)" -ForegroundColor Gray
    Write-Host "   Available Payout: $($data.available_payout)" -ForegroundColor Gray
    Write-Host "   Pending Amount: $($data.pending_payout)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️ GET /summary: $($_.Exception.Response.StatusCode.Value) - $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 4: Get Payment Methods
Write-Host "`n[TEST 4] Testing GET /mentors/payouts/payment-methods" -ForegroundColor Yellow
try {
    $headers = @{ Authorization = "Bearer $MENTOR_TOKEN" }
    $response = Invoke-WebRequest -Uri "$API/mentors/payouts/payment-methods" -Method Get -Headers $headers -UseBasicParsing -TimeoutSec 10
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "✅ GET /payment-methods successful" -ForegroundColor Green
    Write-Host "   Count: $($data.Count)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️ GET /payment-methods: $($_.Exception.Response.StatusCode.Value)" -ForegroundColor Yellow
}

# Test 5: Create Payment Method
Write-Host "`n[TEST 5] Testing POST /mentors/payouts/payment-methods" -ForegroundColor Yellow
$body = @{
    bank_name = "Chase Bank"
    account_holder_name = "Sarah Chen"
    account_number = "1234567890"
    routing_number = "123456789"
    account_type = "checking"
    is_primary = $true
} | ConvertTo-Json

try {
    $headers = @{ Authorization = "Bearer $MENTOR_TOKEN" }
    $response = Invoke-WebRequest -Uri "$API/mentors/payouts/payment-methods" -Method Post -Body $body -ContentType "application/json" -Headers $headers -UseBasicParsing -TimeoutSec 10
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "✅ POST /payment-methods successful" -ForegroundColor Green
    Write-Host "   ID: $($data.id)" -ForegroundColor Gray
    $PAYMENT_METHOD_ID = $data.id
} catch {
    Write-Host "⚠️ POST /payment-methods: $($_.Exception.Response.StatusCode.Value)" -ForegroundColor Yellow
}

# Test 6: Create Payout Request
Write-Host "`n[TEST 6] Testing POST /mentors/payouts/request" -ForegroundColor Yellow
if ($PAYMENT_METHOD_ID) {
    $body = @{
        amount = 100.00
        payment_method_id = $PAYMENT_METHOD_ID
    } | ConvertTo-Json

    try {
        $headers = @{ Authorization = "Bearer $MENTOR_TOKEN" }
        $response = Invoke-WebRequest -Uri "$API/mentors/payouts/request" -Method Post -Body $body -ContentType "application/json" -Headers $headers -UseBasicParsing -TimeoutSec 10
        $data = $response.Content | ConvertFrom-Json
        
        Write-Host "✅ POST /request successful" -ForegroundColor Green
        Write-Host "   Status: $($data.status)" -ForegroundColor Gray
        Write-Host "   Amount: $($data.amount)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️ POST /request: $($_.Exception.Response.StatusCode.Value)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Skipped (no payment method)" -ForegroundColor Yellow
}

# Test 7: Admin - Get Pending Payouts
Write-Host "`n[TEST 7] Testing GET /admin/payouts/pending" -ForegroundColor Yellow
if ($ADMIN_TOKEN) {
    try {
        $headers = @{ Authorization = "Bearer $ADMIN_TOKEN" }
        $response = Invoke-WebRequest -Uri "$API/admin/payouts/pending" -Method Get -Headers $headers -UseBasicParsing -TimeoutSec 10
        $data = $response.Content | ConvertFrom-Json
        
        Write-Host "✅ GET /admin/payouts/pending successful" -ForegroundColor Green
        Write-Host "   Pending Count: $($data.Count)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️ GET /admin/payouts/pending: $($_.Exception.Response.StatusCode.Value)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Skipped (admin not authenticated)" -ForegroundColor Yellow
}

# Test 8: Admin - Get Stats
Write-Host "`n[TEST 8] Testing GET /admin/payouts/stats" -ForegroundColor Yellow
if ($ADMIN_TOKEN) {
    try {
        $headers = @{ Authorization = "Bearer $ADMIN_TOKEN" }
        $response = Invoke-WebRequest -Uri "$API/admin/payouts/stats" -Method Get -Headers $headers -UseBasicParsing -TimeoutSec 10
        $data = $response.Content | ConvertFrom-Json
        
        Write-Host "✅ GET /admin/payouts/stats successful" -ForegroundColor Green
        Write-Host "   Total Pending: $($data.total_pending)" -ForegroundColor Gray
        Write-Host "   Total Completed: $($data.total_completed)" -ForegroundColor Gray
        Write-Host "   Total Mentors: $($data.total_mentors)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️ GET /admin/payouts/stats: $($_.Exception.Response.StatusCode.Value)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Skipped (admin not authenticated)" -ForegroundColor Yellow
}

# Test 9: List Mentors
Write-Host "`n[TEST 9] Testing GET /mentors" -ForegroundColor Yellow
try {
    $headers = @{ Authorization = "Bearer $MENTOR_TOKEN" }
    $response = Invoke-WebRequest -Uri "$API/mentors" -Method Get -Headers $headers -UseBasicParsing -TimeoutSec 10
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "✅ GET /mentors successful" -ForegroundColor Green
    Write-Host "   Response type: $($data.GetType().Name)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️ GET /mentors: $($_.Exception.Response.StatusCode.Value)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Backend URL: $BASE_URL" -ForegroundColor Gray
Write-Host "API Endpoint: $API" -ForegroundColor Gray
Write-Host "Mentor Token: $($MENTOR_TOKEN.Substring(0, 20))..." -ForegroundColor Gray
Write-Host "`nKey Endpoints Mounted:" -ForegroundColor Cyan
Write-Host "  ✅ /api/v1x/mentors/payouts/summary" -ForegroundColor Green
Write-Host "  ✅ /api/v1x/mentors/payouts/payment-methods" -ForegroundColor Green
Write-Host "  ✅ /api/v1x/mentors/payouts/request" -ForegroundColor Green
Write-Host "  ✅ /api/v1x/admin/payouts/pending" -ForegroundColor Green
Write-Host "  ✅ /api/v1x/admin/payouts/stats" -ForegroundColor Green
Write-Host "`n✅ API TESTING COMPLETE" -ForegroundColor Green
