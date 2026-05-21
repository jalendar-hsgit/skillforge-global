# Login Redirect Debugging Script
# Run this to test the login flow step by step

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          LOGIN REDIRECT DEBUG HELPER                         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$FRONTEND = "http://localhost:3000"
$BACKEND = "http://localhost:8001"

Write-Host "🔍 DEBUGGING LOGIN REDIRECT ISSUE`n" -ForegroundColor Yellow

# Step 1: Check servers
Write-Host "Step 1: Checking if servers are running..." -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray

try {
    $frontendCheck = Invoke-WebRequest -Uri $FRONTEND -Method Head -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Frontend running at $FRONTEND" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend NOT running at $FRONTEND" -ForegroundColor Red
    Write-Host "   Start with: npm run dev`n" -ForegroundColor Yellow
    exit
}

try {
    $backendCheck = Invoke-WebRequest -Uri "$BACKEND/docs" -Method Head -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend running at $BACKEND`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend NOT running at $BACKEND" -ForegroundColor Red
    Write-Host "   Start with: uvicorn app.main:app --reload --port 8001`n" -ForegroundColor Yellow
    exit
}

# Step 2: Get credentials
Write-Host "Step 2: Enter login credentials" -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$email = Read-Host "Email (default: admin@skillforge.test)"
if ([string]::IsNullOrWhiteSpace($email)) { $email = "admin@skillforge.test" }

$passwordSecure = Read-Host "Password (default: Admin123!)" -AsSecureString
if ($passwordSecure.Length -eq 0) {
    $password = "Admin123!"
} else {
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($passwordSecure)
    $password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

Write-Host ""

# Step 3: Test login
Write-Host "Step 3: Testing login flow..." -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$body = @{
    email = $email
    password = $password
} | ConvertTo-Json

try {
    Write-Host "📤 Sending POST to /api/session/login..." -ForegroundColor White
    
    $loginResponse = Invoke-WebRequest `
        -Uri "$FRONTEND/api/session/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -SessionVariable session `
        -ErrorAction Stop
    
    Write-Host "✅ Login successful! Status: $($loginResponse.StatusCode)" -ForegroundColor Green
    
    # Parse response
    $loginData = $loginResponse.Content | ConvertFrom-Json
    Write-Host "   Response: $($loginResponse.Content)" -ForegroundColor DarkGray
    
    # Check cookies
    if ($session.Cookies.GetCookies($FRONTEND)) {
        Write-Host "🍪 Cookies received:" -ForegroundColor Cyan
        $session.Cookies.GetCookies($FRONTEND) | ForEach-Object {
            Write-Host "   $($_.Name) = $($_.Value.Substring(0, [Math]::Min(20, $_.Value.Length)))..." -ForegroundColor DarkGray
        }
    }
    
    Write-Host ""
    
    # Step 4: Test /me endpoint
    Write-Host "Step 4: Testing /api/session/me endpoint..." -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    Write-Host "📤 Sending GET to /api/session/me..." -ForegroundColor White
    
    $meResponse = Invoke-WebRequest `
        -Uri "$FRONTEND/api/session/me" `
        -Method GET `
        -WebSession $session `
        -ErrorAction Stop
    
    Write-Host "✅ Me endpoint successful! Status: $($meResponse.StatusCode)" -ForegroundColor Green
    
    $userData = $meResponse.Content | ConvertFrom-Json
    Write-Host "   User ID: $($userData.id)" -ForegroundColor DarkGray
    Write-Host "   Email: $($userData.email)" -ForegroundColor DarkGray
    Write-Host "   Role: $($userData.role)" -ForegroundColor Cyan
    
    Write-Host ""
    
    # Step 5: Determine redirect
    Write-Host "Step 5: Determining redirect URL..." -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    $redirectUrl = "/dashboard"
    if ($userData.role -eq "ADMIN" -or $userData.role -eq "SUPERADMIN") {
        $redirectUrl = "/admin"
    }
    
    Write-Host "🎯 Redirect URL: $FRONTEND$redirectUrl" -ForegroundColor Yellow
    Write-Host ""
    
    # Step 6: Summary
    Write-Host "Step 6: Summary" -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "✅ Login: WORKING" -ForegroundColor Green
    Write-Host "✅ Cookie: WORKING" -ForegroundColor Green
    Write-Host "✅ /me endpoint: WORKING" -ForegroundColor Green
    Write-Host "✅ Redirect URL: $redirectUrl" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🎉 LOGIN FLOW IS WORKING!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Open browser to: $FRONTEND/login" -ForegroundColor White
    Write-Host "2. Open DevTools (F12) → Console tab" -ForegroundColor White
    Write-Host "3. Login with your credentials" -ForegroundColor White
    Write-Host "4. Check console logs for any errors" -ForegroundColor White
    Write-Host "5. Page should redirect to: $redirectUrl`n" -ForegroundColor White
    
    # Offer to open browser
    $openBrowser = Read-Host "Open login page in browser? (y/n)"
    if ($openBrowser -eq 'y') {
        Start-Process "$FRONTEND/login"
        Write-Host "✅ Browser opened. Check for redirect after login.`n" -ForegroundColor Green
    }
    
    # Offer to open test page
    $openTest = Read-Host "Open test page (test_login_redirect.html)? (y/n)"
    if ($openTest -eq 'y') {
        $testPath = Join-Path (Get-Location) "test_login_redirect.html"
        Start-Process $testPath
        Write-Host "✅ Test page opened. Use it to debug the redirect flow.`n" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ ERROR occurred!" -ForegroundColor Red
    Write-Host ""
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        if ($statusCode -eq 401) {
            Write-Host "❌ Invalid credentials" -ForegroundColor Red
            Write-Host "   → Check email and password" -ForegroundColor Yellow
        } elseif ($statusCode -eq 429) {
            Write-Host "❌ Rate limit exceeded" -ForegroundColor Red
            Write-Host "   → Too many login attempts. Wait 5 minutes." -ForegroundColor Yellow
        } else {
            Write-Host "❌ HTTP Error: $statusCode" -ForegroundColor Red
        }
    } else {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Verify admin user exists in database" -ForegroundColor White
    Write-Host "2. Check backend logs for errors" -ForegroundColor White
    Write-Host "3. Verify password is correct" -ForegroundColor White
    Write-Host "4. Try creating new admin user:`n" -ForegroundColor White
    
    Write-Host "   cd backend" -ForegroundColor DarkGray
    Write-Host "   python -c `"from app.core.db import SessionLocal; from app.models.user import User, UserRole; from app.core.security import get_password_hash; db = SessionLocal(); admin = User(email='admin@skillforge.test', hashed_password=get_password_hash('Admin123!'), full_name='Admin User', role=UserRole.ADMIN); db.add(admin); db.commit(); print('Admin created')`"`n" -ForegroundColor DarkGray
}

Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   - SECURITY_FIXES.md - Security & redirect documentation" -ForegroundColor White
Write-Host "   - test_login_redirect.html - Interactive test page`n" -ForegroundColor White
