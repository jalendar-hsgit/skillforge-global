# PowerShell E2E Marketplace Test Script
# Usage: Run in PowerShell with ExecutionPolicy Bypass
# cd 'D:\python code\sfg\skillforge-global\scripts'
# powershell -ExecutionPolicy Bypass -File .\test-marketplace.ps1

$base = "http://127.0.0.1:8001"
$testEmail = "testuser$(Get-Random)-e2e@skillforge.com"
$testPassword = "TestE2E123!"

Write-Host "Step 1: Health check..."
Invoke-WebRequest -UseBasicParsing "$base/healthz" | Select-Object -ExpandProperty Content

Write-Host "Step 2: Signup..."
$signupBody = @{ email = $testEmail; password = $testPassword; full_name = "Test User" } | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing -Uri "$base/api/v1/auth/signup" -Method POST -Body $signupBody -ContentType "application/json"

Write-Host "Step 3: Login..."
$loginBody = @{ email = $testEmail; password = $testPassword } | ConvertTo-Json
$loginResp = Invoke-WebRequest -UseBasicParsing -Uri "$base/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$cookie = $loginResp.Headers["Set-Cookie"]
Write-Host "Cookie: $cookie"

Write-Host "Step 4: Browse courses..."
$coursesResp = Invoke-WebRequest -UseBasicParsing -Uri "$base/api/v1x/marketplace/courses" -Headers @{ Cookie = $cookie }
$courses = ($coursesResp.Content | ConvertFrom-Json)
$paidCourse = $courses | Where-Object { $_.is_paid -eq $true }
if (-not $paidCourse) { Write-Error "No paid course found!"; exit 1 }
Write-Host "Found paid course: $($paidCourse.title) (ID: $($paidCourse.id))"

Write-Host "Step 5: Add to cart..."
$addBody = @{ course_id = $paidCourse.id } | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing -Uri "$base/api/v1x/marketplace/cart/add" -Method POST -Body $addBody -ContentType "application/json" -Headers @{ Cookie = $cookie }

Write-Host "Step 6: View cart..."
Invoke-WebRequest -UseBasicParsing -Uri "$base/api/v1x/marketplace/cart" -Headers @{ Cookie = $cookie } | Select-Object -ExpandProperty Content

Write-Host "Step 7: Checkout with coins..."
$checkoutBody = @{ payment_method = "coins" } | ConvertTo-Json
$orderResp = Invoke-WebRequest -UseBasicParsing -Uri "$base/api/v1x/marketplace/checkout" -Method POST -Body $checkoutBody -ContentType "application/json" -Headers @{ Cookie = $cookie }
$order = ($orderResp.Content | ConvertFrom-Json)
Write-Host "Order status: $($order.status) | Amount: $($order.amount)"

Write-Host "Step 8: Verify orders..."
Invoke-WebRequest -UseBasicParsing -Uri "$base/api/v1x/marketplace/orders" -Headers @{ Cookie = $cookie } | Select-Object -ExpandProperty Content

Write-Host "E2E test complete."
