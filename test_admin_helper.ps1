# SkillForge Admin Testing Helper
# Quick commands to test admin features

Write-Host "`n╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║" -ForegroundColor Cyan -NoNewline
Write-Host "               SKILLFORGE ADMIN - QUICK TEST HELPER                           " -ForegroundColor Yellow -NoNewline
Write-Host "║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$BACKEND_URL = "http://localhost:8001"
$FRONTEND_URL = "http://localhost:3000"

function Show-Menu {
    Write-Host "`n📋 QUICK ACTIONS:" -ForegroundColor Green
    Write-Host "  1. Open Frontend Admin Dashboard" -ForegroundColor White
    Write-Host "  2. Open Backend API Docs (Swagger)" -ForegroundColor White
    Write-Host "  3. Run Complete Test Suite" -ForegroundColor White
    Write-Host "  4. Create Admin User" -ForegroundColor White
    Write-Host "  5. Test Admin Login" -ForegroundColor White
    Write-Host "  6. Show All URLs" -ForegroundColor White
    Write-Host "  7. Check Server Status" -ForegroundColor White
    Write-Host "  8. View Documentation" -ForegroundColor White
    Write-Host "  Q. Quit`n" -ForegroundColor White
}

function Open-AdminDashboard {
    Write-Host "`n🚀 Opening Admin Dashboard..." -ForegroundColor Cyan
    Start-Process "$FRONTEND_URL/admin"
}

function Open-ApiDocs {
    Write-Host "`n📚 Opening API Documentation..." -ForegroundColor Cyan
    Start-Process "$BACKEND_URL/docs"
}

function Run-TestSuite {
    Write-Host "`n🧪 Running Complete Test Suite...`n" -ForegroundColor Cyan
    python backend/test_admin_complete.py
}

function Create-AdminUser {
    Write-Host "`n👤 Creating Admin User..." -ForegroundColor Cyan
    Write-Host "This will create an admin user in the database.`n" -ForegroundColor Yellow
    
    $email = Read-Host "Enter admin email (default: admin@skillforge.test)"
    if ([string]::IsNullOrWhiteSpace($email)) { $email = "admin@skillforge.test" }
    
    $password = Read-Host "Enter admin password (default: Admin123!)"
    if ([string]::IsNullOrWhiteSpace($password)) { $password = "Admin123!" }
    
    $name = Read-Host "Enter admin name (default: Admin User)"
    if ([string]::IsNullOrWhiteSpace($name)) { $name = "Admin User" }
    
    $pythonScript = @"
from app.core.db import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

# Check if user exists
existing = db.query(User).filter(User.email == '$email').first()
if existing:
    print('❌ User already exists with this email')
    exit(1)

# Create admin user
admin = User(
    email='$email',
    hashed_password=get_password_hash('$password'),
    full_name='$name',
    role=UserRole.ADMIN
)
db.add(admin)
db.commit()
print('✅ Admin user created successfully!')
print(f'   Email: $email')
print(f'   Password: $password')
"@
    
    Set-Location backend
    $pythonScript | python
    Set-Location ..
}

function Test-AdminLogin {
    Write-Host "`n🔐 Testing Admin Login..." -ForegroundColor Cyan
    
    $email = Read-Host "Enter admin email"
    $password = Read-Host "Enter admin password"
    
    $body = @{
        email = $email
        password = $password
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/v1/auth/login" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -SessionVariable session
        
        Write-Host "`n✅ Login successful!" -ForegroundColor Green
        Write-Host "Response: $($response.StatusCode)" -ForegroundColor White
        
        # Test /me endpoint
        $meResponse = Invoke-WebRequest -Uri "$BACKEND_URL/api/v1/auth/me" `
            -WebSession $session
        
        $userData = $meResponse.Content | ConvertFrom-Json
        Write-Host "`n👤 User Info:" -ForegroundColor Cyan
        Write-Host "   Email: $($userData.email)" -ForegroundColor White
        Write-Host "   Name: $($userData.full_name)" -ForegroundColor White
        Write-Host "   Role: $($userData.role)" -ForegroundColor White
        
    } catch {
        Write-Host "`n❌ Login failed!" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-AllUrls {
    Write-Host "`n📱 FRONTEND URLs ($FRONTEND_URL):" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    $frontendUrls = @(
        @("/admin", "Admin Dashboard"),
        @("/admin/analytics", "Analytics Dashboard"),
        @("/admin/user-analytics", "User Analytics (DAU/WAU/MAU)"),
        @("/admin/revenue", "Revenue Dashboard"),
        @("/admin/marketplace", "Marketplace Admin"),
        @("/admin/notifications", "Email & Notifications"),
        @("/admin/users", "User Management"),
        @("/admin/mentors", "Mentor Management"),
        @("/admin/sessions", "Session Management"),
        @("/admin/courses-enhanced", "Course Management"),
        @("/admin/logs", "Audit Logs"),
        @("/admin/settings", "Platform Settings")
    )
    
    foreach ($url in $frontendUrls) {
        Write-Host "  $FRONTEND_URL$($url[0])" -ForegroundColor White -NoNewline
        Write-Host " - $($url[1])" -ForegroundColor DarkGray
    }
    
    Write-Host "`n🔌 BACKEND API Endpoints ($BACKEND_URL):" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "  See ADMIN_URLS_COMPLETE.md for full list of 53 endpoints" -ForegroundColor White
    Write-Host "  API Docs: $BACKEND_URL/docs" -ForegroundColor Yellow
}

function Check-ServerStatus {
    Write-Host "`n🔍 Checking Server Status...`n" -ForegroundColor Cyan
    
    # Check backend
    Write-Host "Backend ($BACKEND_URL):" -ForegroundColor White -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "$BACKEND_URL/docs" -TimeoutSec 2
        Write-Host " ✅ Running" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Not running" -ForegroundColor Red
        Write-Host "   Start with: uvicorn app.main:app --reload --port 8001" -ForegroundColor Yellow
    }
    
    # Check frontend
    Write-Host "Frontend ($FRONTEND_URL):" -ForegroundColor White -NoNewline
    try {
        $response = Invoke-WebRequest -Uri $FRONTEND_URL -TimeoutSec 2
        Write-Host " ✅ Running" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Not running" -ForegroundColor Red
        Write-Host "   Start with: npm run dev" -ForegroundColor Yellow
    }
}

function Show-Documentation {
    Write-Host "`n📚 Documentation Files:" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    $docs = @(
        @("ADMIN_URLS_COMPLETE.md", "Complete URL reference (53 endpoints)"),
        @("ADMIN_IMPLEMENTATION_SUMMARY.md", "Technical implementation details"),
        @("NEXT_IMPLEMENTATIONS.md", "Roadmap and priorities"),
        @("EMAIL_NOTIFICATIONS_SUMMARY.md", "Email system documentation"),
        @("EMAIL_TESTING_GUIDE.md", "Email testing instructions"),
        @("backend/test_admin_complete.py", "Automated test suite")
    )
    
    foreach ($doc in $docs) {
        Write-Host "  $($doc[0])" -ForegroundColor Yellow
        Write-Host "    └─ $($doc[1])" -ForegroundColor DarkGray
    }
    
    Write-Host "`n💡 Quick Tips:" -ForegroundColor Cyan
    Write-Host "  • All admin pages require ADMIN or SUPERADMIN role" -ForegroundColor White
    Write-Host "  • Complete audit logging on all actions" -ForegroundColor White
    Write-Host "  • 14 frontend pages + 53 backend endpoints implemented" -ForegroundColor White
    Write-Host "  • CSV export available on multiple pages" -ForegroundColor White
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "`nSelect an option"
    
    switch ($choice) {
        "1" { Open-AdminDashboard }
        "2" { Open-ApiDocs }
        "3" { Run-TestSuite }
        "4" { Create-AdminUser }
        "5" { Test-AdminLogin }
        "6" { Show-AllUrls }
        "7" { Check-ServerStatus }
        "8" { Show-Documentation }
        "Q" { 
            Write-Host "`n👋 Goodbye!" -ForegroundColor Cyan
            break
        }
        default { Write-Host "`n❌ Invalid option. Please try again." -ForegroundColor Red }
    }
    
    if ($choice -ne "Q") {
        Write-Host "`nPress any key to continue..." -ForegroundColor DarkGray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
} while ($choice -ne "Q")
