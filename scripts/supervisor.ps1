param(
  [int]$FrontendPort = 3000,
  [int]$BackendPort = 8001,
  [string]$RepoRoot = "D:\python code\sfg\skillforge-global"
)
$ErrorActionPreference = 'SilentlyContinue'

function Test-HttpOk($url){ try { $r = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 3 -ErrorAction Stop; return $true } catch { return $false } }
function Test-Health($url){ try { $r = Invoke-RestMethod -Uri $url -TimeoutSec 3; return [bool]$r.ok } catch { return $false } }

function Start-Backend{
  param([string]$Path)
  Write-Host "Starting backend..."
  $cmd = "& '" + (Join-Path $Path "venv\Scripts\python.exe") + "' -m uvicorn app.main:app --host 0.0.0.0 --port $BackendPort --reload"
  Start-Process -FilePath powershell -ArgumentList '-NoProfile','-Command', $cmd | Out-Null
}

function Start-Frontend{
  param([string]$Path)
  Write-Host "Starting frontend..."
  $cmd = "$env:NEXT_PUBLIC_API_BASE='http://127.0.0.1:$BackendPort'; cd '$Path'; npm run dev"
  Start-Process -FilePath powershell -ArgumentList '-NoProfile','-Command', $cmd | Out-Null
}

function Wait-Servers{
  param([string]$Base, [string]$Api)
  $b = $false; for($i=0;$i -lt 60;$i++){ if(Test-Health "$Api/healthz"){ $b=$true; break } Start-Sleep -Milliseconds 500 }
  $f = $false; for($i=0;$i -lt 120;$i++){ if(Test-HttpOk "$Base/api/session/me"){ $f=$true; break } Start-Sleep -Milliseconds 500 }
  Write-Host "Backend ready: $b ; Frontend ready: $f"
  return ($b -and $f)
}

function Run-Smoke{
  param([string]$Base)
  $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
  $EMAIL = "uitest+" + [Guid]::NewGuid().ToString("N").Substring(0,6) + "@example.com"; $PASSWORD = "TestPass123!"
  $signupBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json
  try { Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/signup" -Method Post -ContentType 'application/json' -Body $signupBody -ErrorAction SilentlyContinue | Out-Null } catch {}
  $loginResp = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/login" -Method Post -ContentType 'application/json' -Body $signupBody -WebSession $session -ErrorAction Stop
  Write-Host ("Login:" + $loginResp.StatusCode)
  $createBody = @{ full_name = 'Jane Smith'; email = 'jane@example.com'; phone = '555-1234' } | ConvertTo-Json
  $create = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes" -Method Post -ContentType 'application/json' -Body $createBody -WebSession $session -ErrorAction Stop
  $resumeId = ($create.Content | ConvertFrom-Json).id
  Write-Host ("Created:" + $resumeId)
  $get = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes?id=$resumeId" -WebSession $session -ErrorAction Stop
  Write-Host ("Get:" + $get.StatusCode)
  $patchBody = @{ full_name = 'Jane Doe' } | ConvertTo-Json
  $patch = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes?id=$resumeId" -Method PATCH -ContentType 'application/json' -Body $patchBody -WebSession $session -ErrorAction Stop
  Write-Host ("Patch:" + $patch.StatusCode)
  $dupBody = @{ action = 'duplicate' } | ConvertTo-Json
  $dup = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes?id=$resumeId" -Method POST -ContentType 'application/json' -Body $dupBody -WebSession $session -ErrorAction Stop
  Write-Host ("Duplicate:" + $dup.StatusCode)
  $aiBody = @{ title = 'Software Engineer'; years_of_experience = 3 } | ConvertTo-Json
  $ai = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resume-ai/professional-summary" -Method Post -ContentType 'application/json' -Body $aiBody -WebSession $session -ErrorAction Stop
  $aiJson = $ai.Content | ConvertFrom-Json
  Write-Host ("AI:" + $ai.StatusCode + ' ' + ($aiJson.summary.Substring(0,[Math]::Min(64,$aiJson.summary.Length))))
  $del = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes?id=$resumeId" -Method DELETE -WebSession $session -ErrorAction Stop
  Write-Host ("Delete:" + $del.StatusCode)
}

# Kill ports
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { try { Stop-Process -Id $_.OwningProcess -Force } catch {} }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { try { Stop-Process -Id $_.OwningProcess -Force } catch {} }

# Start both
Start-Backend -Path (Join-Path $RepoRoot 'backend')
Start-Sleep -Seconds 3
Start-Frontend -Path $RepoRoot

$Base = "http://127.0.0.1:$FrontendPort"
$Api = "http://127.0.0.1:$BackendPort"

# Supervisor loop: ensure ready, run tests, then keep monitoring
$attempt=0
while($true){
  $attempt++
  if(Wait-Servers -Base $Base -Api $Api){
    try {
      Run-Smoke -Base $Base
      Write-Host "Smoke test completed (attempt $attempt)."
      Start-Sleep -Seconds 15
    } catch {
      Write-Host "Smoke test failed (attempt $attempt): $($_.Exception.Message)"
      Start-Sleep -Seconds 5
    }
  } else {
    Write-Host "Servers not ready (attempt $attempt), restarting..."
    Start-Backend -Path (Join-Path $RepoRoot 'backend')
    Start-Sleep -Seconds 3
    Start-Frontend -Path $RepoRoot
  }
}