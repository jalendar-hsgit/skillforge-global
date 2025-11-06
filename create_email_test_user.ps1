# Create Test User for Email Testing
# Usage: .\create_email_test_user.ps1 [email] [name]

param(
    [string]$Email = "",
    [string]$Name = ""
)

$baseUrl = "http://localhost:8001"

# If no email provided, prompt for it
if ([string]::IsNullOrWhiteSpace($Email)) {
    Write-Host "`nCreate Test User for Email Testing" -ForegroundColor Cyan
    Write-Host "====================================`n" -ForegroundColor Cyan
    
    Write-Host "Enter email address (or press Enter for default):"
    $inputEmail = Read-Host "Email"
    
    if ([string]::IsNullOrWhiteSpace($inputEmail)) {
        $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
        $Email = "test$timestamp@skillforge.test"
        Write-Host "Using default: $Email" -ForegroundColor Gray
    } else {
        $Email = $inputEmail
    }
}

# If no name provided, prompt for it
if ([string]::IsNullOrWhiteSpace($Name)) {
    Write-Host "Enter full name (or press Enter for default):"
    $inputName = Read-Host "Name"
    
    if ([string]::IsNullOrWhiteSpace($inputName)) {
        $Name = "Test User"
        Write-Host "Using default: $Name" -ForegroundColor Gray
    } else {
        $Name = $inputName
    }
}

$password = "Test123!"

Write-Host "`nCreating user..." -ForegroundColor Yellow

# Create user
$userData = @{
    email = $Email
    password = $password
    full_name = $Name
} | ConvertTo-Json

try {
    $signupResult = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/auth/signup" -ContentType 'application/json' -Body $userData -ErrorAction Stop
    
    if ($signupResult.created) {
        Write-Host "`n✅ User Created Successfully!" -ForegroundColor Green
        Write-Host "================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "📧 Email:    $Email" -ForegroundColor Cyan
        Write-Host "🔑 Password: $password" -ForegroundColor Cyan
        Write-Host "👤 Name:     $Name" -ForegroundColor Cyan
        Write-Host "🪙 Coins:    100 (welcome bonus)" -ForegroundColor Cyan
        Write-Host ""
        
        # Try to login and verify coins
        Write-Host "Verifying account..." -ForegroundColor Yellow
        $loginData = @{
            email = $Email
            password = $password
        } | ConvertTo-Json
        
        $loginResult = Invoke-WebRequest -Method Post -Uri "$baseUrl/api/v1/auth/login" -ContentType 'application/json' -Body $loginData -SessionVariable 'session' -ErrorAction Stop
        
        if ($loginResult.StatusCode -eq 200) {
            # Check coin balance
            $balance = Invoke-RestMethod -Uri "$baseUrl/api/v1x/coins_db/balance" -WebSession $session -ErrorAction Stop
            
            Write-Host "✅ Login verified" -ForegroundColor Green
            Write-Host "✅ Coin balance: $($balance.balance) coins" -ForegroundColor Green
            
            if ($balance.balance -eq 100) {
                Write-Host "✅ Welcome bonus awarded correctly!" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Unexpected coin balance (expected 100)" -ForegroundColor Yellow
            }
        }
        
        Write-Host ""
        Write-Host "📋 Email Status:" -ForegroundColor Cyan
        Write-Host "   Check backend logs for email sending status" -ForegroundColor Gray
        Write-Host "   Look for: 'Welcome email sent to $Email'" -ForegroundColor Gray
        Write-Host "   Or: 'SMTP credentials not configured'" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "🔧 To Enable Email Sending:" -ForegroundColor Yellow
        Write-Host "   1. Edit backend/.env" -ForegroundColor Gray
        Write-Host "   2. Add email provider config:" -ForegroundColor Gray
        Write-Host "      EMAIL_PROVIDER=sendgrid" -ForegroundColor Gray
        Write-Host "      SENDGRID_API_KEY=your_key" -ForegroundColor Gray
        Write-Host "   3. Restart backend" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "🧪 Test Login:" -ForegroundColor Cyan
        Write-Host "   Email: $Email" -ForegroundColor Gray
        Write-Host "   Password: $password" -ForegroundColor Gray
        Write-Host "   URL: http://localhost:3000/login" -ForegroundColor Gray
        Write-Host ""
        
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorMessage = $_.Exception.Message
    
    if ($statusCode -eq 400 -and $errorMessage -match "Email already exists") {
        Write-Host "`n❌ User already exists with email: $Email" -ForegroundColor Red
        Write-Host "   Try using a different email address" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 Quick login with existing user:" -ForegroundColor Cyan
        Write-Host "   Email: $Email" -ForegroundColor Gray
        Write-Host "   Password: $password" -ForegroundColor Gray
    } elseif ($statusCode -eq 429) {
        Write-Host "`n⏱️  Rate Limited" -ForegroundColor Yellow
        Write-Host "   Too many signups from this IP" -ForegroundColor Gray
        Write-Host "   Wait a few minutes and try again" -ForegroundColor Gray
    } else {
        Write-Host "`n❌ Error creating user" -ForegroundColor Red
        Write-Host "   Status: $statusCode" -ForegroundColor Gray
        Write-Host "   Message: $errorMessage" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "================================`n" -ForegroundColor Cyan
