# Quick Deployment Script - SkillForge Global (PowerShell)
# Usage: .\deploy.ps1 [frontend|backend|both]

param(
    [string]$Target = "both"
)

Write-Host "🚀 SkillForge Global Deployment Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

function Deploy-Frontend {
    Write-Host ""
    Write-Host "📦 Deploying Frontend to Vercel..." -ForegroundColor Yellow
    Write-Host "------------------------------------" -ForegroundColor Yellow
    
    # Check if Vercel CLI is installed
    if (!(Get-Command vercel -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Red
        npm i -g vercel
    }
    
    # Build frontend
    Write-Host "Building frontend..." -ForegroundColor White
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        exit 1
    }
    
    # Deploy to Vercel
    Write-Host "Deploying to Vercel..." -ForegroundColor White
    vercel --prod
    
    Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
}

function Deploy-Backend {
    Write-Host ""
    Write-Host "📦 Backend Deployment Checklist..." -ForegroundColor Yellow
    Write-Host "------------------------------------" -ForegroundColor Yellow
    
    # Run tests
    Write-Host "Running backend tests..." -ForegroundColor White
    Set-Location backend
    python -m unittest discover -s tests -p "test_*.py" -v
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Tests failed! Aborting deployment." -ForegroundColor Red
        Set-Location ..
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Backend deployment options:" -ForegroundColor Cyan
    Write-Host "1. Render: Push to GitHub (auto-deploy if configured)" -ForegroundColor White
    Write-Host "2. Railway: railway up" -ForegroundColor White
    Write-Host "3. Fly.io: fly deploy" -ForegroundColor White
    Write-Host ""
    Write-Host "After deploying backend:" -ForegroundColor Cyan
    Write-Host "  1. Set environment variables in platform dashboard" -ForegroundColor White
    Write-Host "  2. Run: alembic upgrade head (via platform CLI)" -ForegroundColor White
    Write-Host "  3. Test: Invoke-WebRequest https://your-backend.com/healthz" -ForegroundColor White
    Write-Host ""
    
    Set-Location ..
}

switch ($Target.ToLower()) {
    "frontend" {
        Deploy-Frontend
    }
    "backend" {
        Deploy-Backend
    }
    "both" {
        Deploy-Backend
        Deploy-Frontend
    }
    default {
        Write-Host "❌ Invalid target: $Target" -ForegroundColor Red
        Write-Host "Usage: .\deploy.ps1 [frontend|backend|both]" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ Deployment process complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Verify deployment at production URLs" -ForegroundColor White
Write-Host "  2. Run smoke tests on production" -ForegroundColor White
Write-Host "  3. Monitor logs for 24 hours" -ForegroundColor White
Write-Host "  4. See DEPLOYMENT.md for detailed instructions" -ForegroundColor White
Write-Host ""
