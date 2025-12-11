Param(
  [int]$Port = 3000,
  [string]$Host = "127.0.0.1"
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $root) { $root = (Get-Location).Path }
Set-Location (Join-Path $root "..")

Write-Host "=== SkillForge Frontend (Production) ===" -ForegroundColor Cyan
Write-Host "Root: $(Get-Location)" -ForegroundColor DarkGray

# Free the port if something is listening
$conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($conn) {
  try {
    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction Stop
    Write-Host "Killed process on port $Port (PID $($conn.OwningProcess))" -ForegroundColor Yellow
  } catch {
    Write-Host "Could not kill PID $($conn.OwningProcess): $($_.Exception.Message)" -ForegroundColor Red
  }
}

$env:NEXT_PUBLIC_API_BASE = "http://$Host:8001"
$env:NODE_OPTIONS = "--max_old_space_size=4096"

# Build if missing
if (-not (Test-Path ".next/BUILD_ID")) {
  Write-Host "No build found, building..." -ForegroundColor Yellow
  npm run build
}

Write-Host "Starting Next.js: host=$Host port=$Port" -ForegroundColor Green

# Start Next.js bound to explicit host/port
& node "node_modules/next/dist/bin/next" start -H $Host -p $Port
