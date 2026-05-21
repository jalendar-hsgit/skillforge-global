# ============================================================
# PHASE 2.3 + STRIPE + EMAIL DEPLOYMENT SCRIPT (PowerShell)
# ============================================================
#
# This script automates the complete deployment of Phase 2.3
# including Stripe payments and email notifications
#
# Usage: .\deploy_phase_2_3.ps1
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phase 2.3 Deployment Script (PowerShell)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 1: INSTALL DEPENDENCIES
# ============================================================
Write-Host "STEP 1: Installing dependencies..." -ForegroundColor Yellow
cd backend
pip install stripe python-dotenv aiosmtplib -q
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# ============================================================
# STEP 2: CREATE .ENV FILE
# ============================================================
Write-Host "STEP 2: Checking .env configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from template..."
    Copy-Item ".env.example" ".env"
    Write-Host "⚠ .env created from template" -ForegroundColor Red
    Write-Host "⚠ YOU MUST CONFIGURE .env with your Stripe keys and email settings" -ForegroundColor Red
    Write-Host ""
    Write-Host "Required settings:"
    Write-Host "  - STRIPE_PUBLIC_KEY (from https://dashboard.stripe.com/apikeys)"
    Write-Host "  - STRIPE_SECRET_KEY"
    Write-Host "  - SENDER_EMAIL (Gmail, SendGrid, or AWS SES)"
    Write-Host "  - SENDER_PASSWORD (App password for Gmail)"
    Write-Host ""
} else {
    Write-Host "✓ .env file found" -ForegroundColor Green
}
Write-Host ""

# ============================================================
# STEP 3: VERIFY DATABASE
# ============================================================
Write-Host "STEP 3: Verifying database..." -ForegroundColor Yellow

$dbPath = "app\data\skillforge.db"
if (Test-Path $dbPath) {
    Write-Host "✓ Database found" -ForegroundColor Green
} else {
    Write-Host "Creating database..."
    python -c "from app.core.db import Base, engine; Base.metadata.create_all(bind=engine)"
    Write-Host "✓ Database created" -ForegroundColor Green
}
Write-Host ""

# ============================================================
# STEP 4: GIT CONFIGURATION
# ============================================================
Write-Host "STEP 4: Git configuration..." -ForegroundColor Yellow

$gitignorePath = "..\\.gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath
    if ($gitignoreContent -match "^\.env$") {
        Write-Host "✓ .env is in .gitignore" -ForegroundColor Green
    } else {
        Write-Host "⚠ Make sure .env is in .gitignore" -ForegroundColor Yellow
        Write-Host "Add this line to .gitignore: .env"
    }
} else {
    Write-Host "⚠ .gitignore not found" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================
# STEP 5: SUMMARY
# ============================================================
Write-Host "==========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. CONFIGURE .env with your credentials:"
Write-Host "   - Stripe API keys"
Write-Host "   - Email configuration (Gmail App Password, SendGrid, or AWS SES)"
Write-Host ""
Write-Host "2. START THE APPLICATION:" -ForegroundColor Yellow
Write-Host "   Terminal 1 (Backend):"
Write-Host "   cd backend"
Write-Host "   uvicorn app.main:app --reload --port 8001"
Write-Host ""
Write-Host "   Terminal 2 (Frontend):"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "3. TEST THE ENDPOINTS:" -ForegroundColor Yellow
Write-Host "   curl http://localhost:8001/api/v1x/payments/balance"
Write-Host ""
Write-Host "4. PUSH TO GIT:" -ForegroundColor Yellow
Write-Host "   git add ."
Write-Host "   git commit -m 'feat: Phase 2.3 + Stripe + Email integration'"
Write-Host "   git push origin main"
Write-Host ""
Write-Host "DOCUMENTATION:" -ForegroundColor Cyan
Write-Host "  - See PHASE_2_3_STRIPE_EMAIL_INTEGRATION.md for detailed setup"
Write-Host "  - See PHASE_2_3_COMPLETE_IMPLEMENTATION.md for feature overview"
Write-Host ""
