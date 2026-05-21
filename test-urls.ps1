# URL Testing Script for SkillForge Global
Write-Host "`n=== Testing Application URLs ===`n" -ForegroundColor Cyan

$frontendBase = "http://localhost:3001"
$backendBase = "http://localhost:8001"

function Test-Url {
    param(
        [string]$Url,
        [string]$Description
    )
    
    try {
        Write-Host "Testing: $Description" -ForegroundColor Yellow
        Write-Host "  URL: $Url"
        
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ⚠ Warning - Status: $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "  ✗ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    Write-Host ""
}

# Test Frontend URLs
Write-Host "`n--- Frontend URLs ---`n" -ForegroundColor Magenta

$frontendResults = @{
    "Home Page" = Test-Url "$frontendBase/" "Home Page"
    "Login Page" = Test-Url "$frontendBase/login" "Login Page"
    "Signup Page" = Test-Url "$frontendBase/signup" "Signup Page"
    "Dashboard" = Test-Url "$frontendBase/dashboard" "Dashboard (may redirect if not logged in)"
    "Paths/Careers" = Test-Url "$frontendBase/paths" "Career Paths Page"
    "Pricing" = Test-Url "$frontendBase/pricing" "Pricing Page"
}

# Test Backend URLs
Write-Host "`n--- Backend URLs ---`n" -ForegroundColor Magenta

$backendResults = @{
    "Health Check" = Test-Url "$backendBase/healthz" "Backend Health Check"
    "API Docs" = Test-Url "$backendBase/docs" "API Documentation (Swagger)"
}

# Summary
Write-Host "`n=== Test Summary ===`n" -ForegroundColor Cyan

$frontendPassed = ($frontendResults.Values | Where-Object { $_ -eq $true }).Count
$frontendTotal = $frontendResults.Count
$backendPassed = ($backendResults.Values | Where-Object { $_ -eq $true }).Count
$backendTotal = $backendResults.Count

Write-Host "Frontend: $frontendPassed/$frontendTotal tests passed" -ForegroundColor $(if ($frontendPassed -eq $frontendTotal) { "Green" } else { "Yellow" })
Write-Host "Backend:  $backendPassed/$backendTotal tests passed" -ForegroundColor $(if ($backendPassed -eq $backendTotal) { "Green" } else { "Yellow" })

$totalPassed = $frontendPassed + $backendPassed
$totalTests = $frontendTotal + $backendTotal

Write-Host "`nOverall: $totalPassed/$totalTests tests passed" -ForegroundColor $(if ($totalPassed -eq $totalTests) { "Green" } elseif ($totalPassed -gt 0) { "Yellow" } else { "Red" })

Write-Host "`n=== Key Application URLs ===`n" -ForegroundColor Cyan
Write-Host "Frontend:       $frontendBase" -ForegroundColor White
Write-Host "Backend API:    $backendBase" -ForegroundColor White
Write-Host "API Docs:       $backendBase/docs" -ForegroundColor White
Write-Host "Resume Editor:  $frontendBase/resumes/new" -ForegroundColor White
Write-Host ""
