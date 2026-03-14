# SkillForge Local Docker Setup Script (Windows PowerShell)
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup-docker.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "SkillForge Local Docker Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ProjectDir = Get-Location
Write-Host "Project directory: $ProjectDir" -ForegroundColor Gray

Write-Host "[1] Checking Docker installation..." -ForegroundColor Yellow
try {
    $DockerVersion = docker --version
    Write-Host "✅ Docker found: $DockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2] Checking Docker Compose..." -ForegroundColor Yellow
try {
    $DockerComposeVersion = docker-compose --version
    Write-Host "✅ Docker Compose found: $DockerComposeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3] Verifying environment files..." -ForegroundColor Yellow
$EnvFiles = @("backend\.env.production", ".env")
foreach ($File in $EnvFiles) {
    $FilePath = Join-Path $ProjectDir $File
    if (Test-Path $FilePath) {
        Write-Host "✅ $File exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $File not found" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[4] Checking for existing containers..." -ForegroundColor Yellow
try {
    $Running = docker-compose ps -q 2>$null | Measure-Object -Line
    if ($Running.Lines -gt 0) {
        Write-Host "⚠️  Found $($Running.Lines) running containers" -ForegroundColor Yellow
        Write-Host "Stopping existing services..." -ForegroundColor Yellow
        docker-compose down | Out-Null
        Start-Sleep -Seconds 2
    }
    Write-Host "✅ Ready to start fresh" -ForegroundColor Green
} catch {
    Write-Host "✅ No existing containers found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5] Building Docker images..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Gray
docker-compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[6] Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "[7] Waiting for services to be healthy (may take 30-60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "[8] Verifying all services..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "✅ LOCAL DOCKER DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your application:" -ForegroundColor Cyan
Write-Host "  🌐 Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  🔌 Backend:   http://localhost:8001" -ForegroundColor White
Write-Host "  💾 Database:  http://localhost:8080 (Adminer)" -ForegroundColor White
Write-Host "  📊 pgAdmin:   http://localhost:5050" -ForegroundColor White
Write-Host ""
Write-Host "Demo account:" -ForegroundColor Cyan
Write-Host "  Email:    john.doe@example.com" -ForegroundColor White
Write-Host "  Password: password" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f backend    # View backend logs" -ForegroundColor White
Write-Host "  docker-compose logs -f frontend   # View frontend logs" -ForegroundColor White
Write-Host "  docker-compose ps                 # Check service status" -ForegroundColor White
Write-Host "  docker-compose down              # Stop all services" -ForegroundColor White
Write-Host ""
Write-Host "📖 Full guide: LOCAL_DOCKER_DEPLOYMENT.md" -ForegroundColor Cyan
Write-Host ""
