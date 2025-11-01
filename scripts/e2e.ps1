param(
  [string]$AppUrl = "http://localhost:3000",
  [string]$ApiUrl = "http://127.0.0.1:8001",
  [switch]$Headed
)

Write-Host "Starting E2E test environment..." -ForegroundColor Cyan

# Use a dedicated sqlite file for tests
$env:DATABASE_URL = "sqlite:///./app/data/test_e2e.db"
$env:NEXT_PUBLIC_API_BASE = $ApiUrl
$env:PORT = "3000"

# Kill any existing processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start backend (prefer python -m uvicorn for reliability)
$backendStart = {
  Set-Location backend
  $cmd = "python"
  $args = @("-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8001")
  Start-Process -FilePath $cmd -ArgumentList $args -PassThru
}
$backend = & $backendStart

# Wait for backend up
$backendReady = $false
for ($i=0; $i -lt 30; $i++) {
  try { Invoke-WebRequest -Uri "$ApiUrl/healthz" -TimeoutSec 1 -UseBasicParsing | Out-Null; $backendReady=$true; break } catch { Start-Sleep -Milliseconds 500 }
}
if (-not $backendReady) { Write-Host "Backend failed to start" -ForegroundColor Red; exit 1 }

# Start frontend
$frontend = Start-Process -FilePath "npm" -ArgumentList "run","dev" -PassThru

# Wait for frontend up
$frontendReady = $false
for ($i=0; $i -lt 40; $i++) {
  try { Invoke-WebRequest -Uri $AppUrl -TimeoutSec 1 -UseBasicParsing | Out-Null; $frontendReady=$true; break } catch { Start-Sleep -Milliseconds 500 }
}
if (-not $frontendReady) { Write-Host "Frontend failed to start" -ForegroundColor Red; Stop-Process -Id $backend.Id -Force; exit 1 }

# Run Playwright tests
try {
  if ($Headed) { npx playwright test --headed } else { npx playwright test }
  $result = $LASTEXITCODE
} finally {
  # Teardown
  if ($frontend) { Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue }
  if ($backend) { Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue }
}

exit $result
