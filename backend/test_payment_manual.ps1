# MANUAL API TESTING SCRIPT - PAYMENT FLOW
# Run from PowerShell: Run this script against the backend running on http://localhost:8001

$BASE_URL = "http://localhost:8001"
$API_PATH = "/api/v1x"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Payment Flow Testing Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 1: GET JWT TOKEN (Create/Login user)
# ============================================================
Write-Host "STEP 1: Creating test user and getting JWT token..." -ForegroundColor Yellow

$loginBody = @{
    email = "test-payment@example.com"
    password = "TestPassword123!"
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "$BASE_URL$API_PATH/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody `
    -SkipHttpErrorCheck

if ($loginResponse.StatusCode -eq 200) {
    $loginData = $loginResponse.Content | ConvertFrom-Json
    $JWT_TOKEN = $loginData.data.access_token
    Write-Host "✅ Got JWT token: $JWT_TOKEN" -ForegroundColor Green
} else {
    # Try login if user exists
    $loginBody2 = @{
        email = "test-payment@example.com"
        password = "TestPassword123!"
    } | ConvertTo-Json
    
    $loginResponse2 = Invoke-WebRequest -Uri "$BASE_URL$API_PATH/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody2 `
        -SkipHttpErrorCheck
    
    if ($loginResponse2.StatusCode -eq 200) {
        $loginData2 = $loginResponse2.Content | ConvertFrom-Json
        $JWT_TOKEN = $loginData2.data.access_token
        Write-Host "✅ Logged in and got JWT token: $JWT_TOKEN" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to get JWT token" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# ============================================================
# STEP 2: GET COURSES (Find a paid course)
# ============================================================
Write-Host "STEP 2: Fetching available courses..." -ForegroundColor Yellow

$coursesResponse = Invoke-WebRequest -Uri "$BASE_URL$API_PATH/courses-db/list" `
    -Method GET `
    -Headers @{Authorization = "Bearer $JWT_TOKEN"} `
    -SkipHttpErrorCheck

if ($coursesResponse.StatusCode -eq 200) {
    $coursesData = $coursesResponse.Content | ConvertFrom-Json
    $paidCourse = $coursesData.data | Where-Object { $_.is_paid -eq $true } | Select-Object -First 1
    
    if ($paidCourse) {
        $COURSE_ID = $paidCourse.id
        Write-Host "✅ Found paid course: $($paidCourse.title) (ID: $COURSE_ID)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No paid courses found. Using demo course ID 1" -ForegroundColor Yellow
        $COURSE_ID = 1
    }
} else {
    Write-Host "⚠️  Could not fetch courses. Using demo course ID 1" -ForegroundColor Yellow
    $COURSE_ID = 1
}

Write-Host ""

# ============================================================
# STEP 3: CREATE ORDER
# ============================================================
Write-Host "STEP 3: Creating order..." -ForegroundColor Yellow

$orderBody = @{
    course_id = $COURSE_ID
    payment_method = "stripe"
} | ConvertTo-Json

$orderResponse = Invoke-WebRequest -Uri "$BASE_URL$API_PATH/orders/create" `
    -Method POST `
    -ContentType "application/json" `
    -Body $orderBody `
    -Headers @{Authorization = "Bearer $JWT_TOKEN"} `
    -SkipHttpErrorCheck

if ($orderResponse.StatusCode -eq 200) {
    $orderData = $orderResponse.Content | ConvertFrom-Json
    $ORDER_ID = $orderData.data.id
    $ORDER_NUMBER = $orderData.data.order_number
    $ORDER_AMOUNT = $orderData.data.amount
    
    Write-Host "✅ Order created successfully:" -ForegroundColor Green
    Write-Host "   Order ID: $ORDER_ID" -ForegroundColor Green
    Write-Host "   Order Number: $ORDER_NUMBER" -ForegroundColor Green
    Write-Host "   Amount: `$$ORDER_AMOUNT" -ForegroundColor Green
} else {
    $errorData = $orderResponse.Content | ConvertFrom-Json
    Write-Host "❌ Failed to create order: $($errorData.detail)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================
# STEP 4: CREATE PAYMENT INTENT
# ============================================================
Write-Host "STEP 4: Creating payment intent..." -ForegroundColor Yellow

$intentBody = @{
    order_id = $ORDER_ID
} | ConvertTo-Json

$intentResponse = Invoke-WebRequest -Uri "$BASE_URL$API_PATH/orders/create-payment-intent" `
    -Method POST `
    -ContentType "application/json" `
    -Body $intentBody `
    -Headers @{Authorization = "Bearer $JWT_TOKEN"} `
    -SkipHttpErrorCheck

if ($intentResponse.StatusCode -eq 200) {
    $intentData = $intentResponse.Content | ConvertFrom-Json
    $PAYMENT_INTENT_ID = $intentData.data.payment_intent_id
    $CLIENT_SECRET = $intentData.data.client_secret
    
    Write-Host "✅ Payment intent created successfully:" -ForegroundColor Green
    Write-Host "   Payment Intent ID: $PAYMENT_INTENT_ID" -ForegroundColor Green
    Write-Host "   Client Secret: $CLIENT_SECRET" -ForegroundColor Green
} else {
    $errorData = $intentResponse.Content | ConvertFrom-Json
    Write-Host "❌ Failed to create payment intent: $($errorData.detail)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================
# STEP 5: GET ORDER STATUS
# ============================================================
Write-Host "STEP 5: Checking order status..." -ForegroundColor Yellow

$statusResponse = Invoke-WebRequest -Uri "$BASE_URL$API_PATH/orders/$ORDER_ID" `
    -Method GET `
    -Headers @{Authorization = "Bearer $JWT_TOKEN"} `
    -SkipHttpErrorCheck

if ($statusResponse.StatusCode -eq 200) {
    $statusData = $statusResponse.Content | ConvertFrom-Json
    Write-Host "✅ Order status retrieved:" -ForegroundColor Green
    Write-Host "   Status: $($statusData.data.status)" -ForegroundColor Green
    Write-Host "   Payment Status: $($statusData.data.payment_status)" -ForegroundColor Green
    Write-Host "   Amount: `$$($statusData.data.amount)" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to get order status" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# STEP 6: GET MY ORDERS
# ============================================================
Write-Host "STEP 6: Retrieving my orders..." -ForegroundColor Yellow

$ordersResponse = Invoke-WebRequest -Uri "$BASE_URL$API_PATH/orders/my-orders" `
    -Method GET `
    -Headers @{Authorization = "Bearer $JWT_TOKEN"} `
    -SkipHttpErrorCheck

if ($ordersResponse.StatusCode -eq 200) {
    $ordersData = $ordersResponse.Content | ConvertFrom-Json
    $totalOrders = $ordersData.data.total
    
    Write-Host "✅ Orders retrieved:" -ForegroundColor Green
    Write-Host "   Total Orders: $totalOrders" -ForegroundColor Green
    
    if ($ordersData.data.orders.Count -gt 0) {
        Write-Host "   Recent Orders:" -ForegroundColor Green
        $ordersData.data.orders | ForEach-Object {
            Write-Host "     - Order #$($_.order_number): `$$($_.amount) (Status: $($_.payment_status))"
        }
    }
} else {
    Write-Host "❌ Failed to retrieve orders" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# SUMMARY
# ============================================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ PAYMENT FLOW TESTING COMPLETE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  JWT Token: $JWT_TOKEN" -ForegroundColor Gray
Write-Host "  Course ID: $COURSE_ID" -ForegroundColor Gray
Write-Host "  Order ID: $ORDER_ID" -ForegroundColor Gray
Write-Host "  Order Number: $ORDER_NUMBER" -ForegroundColor Gray
Write-Host "  Payment Intent ID: $PAYMENT_INTENT_ID" -ForegroundColor Gray
Write-Host "  Client Secret: $CLIENT_SECRET" -ForegroundColor Gray

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to frontend and use client_secret to complete payment" -ForegroundColor White
Write-Host "2. Use Stripe test card: 4242 4242 4242 4242" -ForegroundColor White
Write-Host "3. Set expiry: 12/25 and CVC: 123" -ForegroundColor White
Write-Host "4. After payment, order status should be 'completed'" -ForegroundColor White
Write-Host ""
