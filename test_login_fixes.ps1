# Login Security & Redirect - Quick Test

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  LOGIN SECURITY & REDIRECT FIX - VERIFICATION TESTS          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$FRONTEND_URL = "http://localhost:3000"
$BACKEND_URL = "http://localhost:8001"

Write-Host "🔍 TESTING LOGIN FIXES`n" -ForegroundColor Yellow

# Test 1: Login Redirect
Write-Host "TEST 1: Login Redirect" -ForegroundColor Green
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "1. Open browser DevTools (F12)" -ForegroundColor White
Write-Host "2. Go to: $FRONTEND_URL/login" -ForegroundColor White
Write-Host "3. Enter credentials and click 'Log In'" -ForegroundColor White
Write-Host "4. ✅ EXPECTED: Immediate redirect to /admin or /dashboard" -ForegroundColor Green
Write-Host "5. ✅ EXPECTED: URL changes without page refresh feel`n" -ForegroundColor Green

# Test 2: Role-Based Redirect
Write-Host "TEST 2: Role-Based Redirect" -ForegroundColor Green
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "Admin users → Redirect to: /admin" -ForegroundColor White
Write-Host "Regular users → Redirect to: /dashboard" -ForegroundColor White
Write-Host "With ?redirect param → Redirect to: specified URL`n" -ForegroundColor White

# Test 3: Redirect Query Parameter
Write-Host "TEST 3: Redirect Query Parameter" -ForegroundColor Green
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "1. Go to: $FRONTEND_URL/login?redirect=/admin/users" -ForegroundColor White
Write-Host "2. Login successfully" -ForegroundColor White
Write-Host "3. ✅ EXPECTED: Redirect to /admin/users (not /admin or /dashboard)`n" -ForegroundColor Green

# Test 4: Security - DevTools Visibility
Write-Host "TEST 4: Password Visibility in DevTools (SECURITY CHECK)" -ForegroundColor Green
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "⚠️  IMPORTANT: This is EXPECTED BEHAVIOR" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White
Write-Host "1. Open DevTools → Network tab" -ForegroundColor White
Write-Host "2. Login with credentials" -ForegroundColor White
Write-Host "3. Click on the login request" -ForegroundColor White
Write-Host "4. ℹ️  You WILL see password in Request Payload" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "Why this is ACCEPTABLE:" -ForegroundColor Yellow
Write-Host "  • This is standard browser behavior (all websites work this way)" -ForegroundColor DarkGray
Write-Host "  • DevTools only shows YOUR requests to YOUR browser" -ForegroundColor DarkGray
Write-Host "  • Other users cannot see your requests" -ForegroundColor DarkGray
Write-Host "  • Password is encrypted in transit with HTTPS (production)" -ForegroundColor DarkGray
Write-Host "  • Password is hashed on server (never stored plain text)" -ForegroundColor DarkGray
Write-Host "  • HTTP-only cookies prevent JavaScript access" -ForegroundColor DarkGray
Write-Host "" -ForegroundColor White
Write-Host "Real Security Measures in Place:" -ForegroundColor Green
Write-Host "  ✅ HTTPS in production (encrypts transmission)" -ForegroundColor White
Write-Host "  ✅ Bcrypt password hashing (server-side)" -ForegroundColor White
Write-Host "  ✅ HTTP-only secure cookies (prevents XSS)" -ForegroundColor White
Write-Host "  ✅ SameSite=Lax (prevents CSRF)" -ForegroundColor White
Write-Host "  ✅ Rate limiting (10 attempts/5min)" -ForegroundColor White
Write-Host "  ✅ No passwords in server logs`n" -ForegroundColor White

# Test 5: Error Handling
Write-Host "TEST 5: Error Handling" -ForegroundColor Green
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "1. Try login with wrong password" -ForegroundColor White
Write-Host "2. ✅ EXPECTED: Error message displays" -ForegroundColor Green
Write-Host "3. ✅ EXPECTED: Can retry login" -ForegroundColor Green
Write-Host "4. ✅ EXPECTED: No redirect on error`n" -ForegroundColor Green

# Test 6: Loading State
Write-Host "TEST 6: Loading State" -ForegroundColor Green
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "1. Click 'Log In' button" -ForegroundColor White
Write-Host "2. ✅ EXPECTED: Button shows 'Logging in...'" -ForegroundColor Green
Write-Host "3. ✅ EXPECTED: Button is disabled during login" -ForegroundColor Green
Write-Host "4. ✅ EXPECTED: Button stays disabled during redirect`n" -ForegroundColor Green

Write-Host "`n📊 AUTOMATED API TEST`n" -ForegroundColor Yellow

$testLogin = Read-Host "Do you want to run automated login test? (y/n)"

if ($testLogin -eq 'y') {
    Write-Host "`n🔐 Testing Login API..." -ForegroundColor Cyan
    
    $email = Read-Host "Enter test email (default: admin@skillforge.test)"
    if ([string]::IsNullOrWhiteSpace($email)) { $email = "admin@skillforge.test" }
    
    $password = Read-Host "Enter test password (default: Admin123!)" -AsSecureString
    if ($password.Length -eq 0) {
        $passwordText = "Admin123!"
    } else {
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
        $passwordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    }
    
    $body = @{
        email = $email
        password = $passwordText
    } | ConvertTo-Json
    
    try {
        Write-Host "`nSending login request..." -ForegroundColor White
        
        $response = Invoke-WebRequest -Uri "$FRONTEND_URL/api/session/login" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -SessionVariable session
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Login successful! (Status: $($response.StatusCode))" -ForegroundColor Green
            
            # Test /me endpoint
            Write-Host "`nFetching user info..." -ForegroundColor White
            $meResponse = Invoke-WebRequest -Uri "$FRONTEND_URL/api/session/me" `
                -WebSession $session
            
            $userData = $meResponse.Content | ConvertFrom-Json
            
            Write-Host "`n👤 User Information:" -ForegroundColor Cyan
            Write-Host "   Email: $($userData.email)" -ForegroundColor White
            Write-Host "   Role: $($userData.role)" -ForegroundColor White
            
            Write-Host "`n🎯 Expected Redirect:" -ForegroundColor Cyan
            if ($userData.role -eq 'ADMIN' -or $userData.role -eq 'SUPERADMIN') {
                Write-Host "   → $FRONTEND_URL/admin" -ForegroundColor Yellow
            } else {
                Write-Host "   → $FRONTEND_URL/dashboard" -ForegroundColor Yellow
            }
        }
        
    } catch {
        Write-Host "`n❌ Login failed!" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode.value__
            Write-Host "Status Code: $statusCode" -ForegroundColor Red
            
            if ($statusCode -eq 401) {
                Write-Host "  → Invalid credentials" -ForegroundColor Yellow
            } elseif ($statusCode -eq 429) {
                Write-Host "  → Rate limit exceeded (too many attempts)" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host "`n`n📚 Documentation" -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "For detailed security information, see:" -ForegroundColor White
Write-Host "  📄 SECURITY_FIXES.md - Complete security analysis" -ForegroundColor Cyan
Write-Host "  📄 TESTING_QUICK_START.md - Full testing guide`n" -ForegroundColor Cyan

Write-Host "✨ Test Complete!`n" -ForegroundColor Green
