param(
  [string]$DatabaseUrl = "sqlite:///./app/data/test_local.ps1.db"
)

$env:DATABASE_URL = $DatabaseUrl
$env:JWT_SECRET = "local-secret"
$env:FRONTEND_ORIGIN = "http://localhost:3000"

cd "$PSScriptRoot/../backend"
python -m pytest tests_e2e -q
