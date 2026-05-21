$Base='http://127.0.0.1:3003'
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$EMAIL = 'uitest+' + ([Guid]::NewGuid().ToString('N').Substring(0,6)) + '@example.com'
$PASSWORD='TestPass123!'
$body = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json

Write-Host "Starting smoke run against $Base"

try {
  $r = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/signup" -Method Post -ContentType 'application/json' -Body $body -WebSession $session -ErrorAction Stop
  Write-Host "Signup: $($r.StatusCode)"
} catch {
  Write-Host "Signup FAILED: $($_.Exception.Message)"
}

try {
  $r = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/login" -Method Post -ContentType 'application/json' -Body $body -WebSession $session -ErrorAction Stop
  Write-Host "Login: $($r.StatusCode)"
} catch {
  Write-Host "Login FAILED: $($_.Exception.Message)"
}

try {
  # Use required fields according to backend schema: title is required
  $createBody = @{ title = 'Software Engineer Resume'; template_id = 'modern'; full_name = 'Jane Smith'; email = 'jane@example.com'; phone = '555-1234' } | ConvertTo-Json
  $c = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes" -Method Post -ContentType 'application/json' -Body $createBody -WebSession $session -ErrorAction Stop
  $cContent = if ($c.Content -is [byte[]]) { [System.Text.Encoding]::UTF8.GetString($c.Content) } else { $c.Content }
  $id = (ConvertFrom-Json $cContent).id
  Write-Host "Created resume id: $id"
} catch {
  Write-Host "Create resume FAILED: $($_.Exception.Message)"
}

try {
  $get = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes?id=$id" -WebSession $session -ErrorAction Stop
  Write-Host "Get resume: $($get.StatusCode)"
} catch {
  Write-Host "Get resume FAILED: $($_.Exception.Message)"
}

try {
  $patchBody = @{ full_name = 'Jane Doe' } | ConvertTo-Json
  $patch = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes?id=$id" -Method PATCH -ContentType 'application/json' -Body $patchBody -WebSession $session -ErrorAction Stop
  Write-Host "Patch resume: $($patch.StatusCode)"
} catch {
  Write-Host "Patch resume FAILED: $($_.Exception.Message)"
}

# Frontend uses the v1x proxy for duplicate: POST /api/session/v1x/resumes/{id}/duplicate
  try {
    $dup = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/v1x/resumes/$id/duplicate" -Method POST -ContentType 'application/json' -WebSession $session -ErrorAction Stop -MaximumRedirection 10
    $dupContent = if ($dup.Content -is [byte[]]) { [System.Text.Encoding]::UTF8.GetString($dup.Content) } else { $dup.Content }
    Write-Host "Duplicate resume: $($dup.StatusCode) Content: $dupContent"
  } catch {
    $resp = $_.Exception.Response
    if ($resp -ne $null) {
      try {
        $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $body = $reader.ReadToEnd()
        $status = $resp.StatusCode
        Write-Host "Duplicate resume: $status Content: $body"
      } catch {
        Write-Host "Duplicate resume failed to read response body: $($_.Exception.Message)"
      }
    } else {
      Write-Host "Duplicate resume FAILED: $($_.Exception.Message)"
    }
  }

# Debug: call backend endpoint directly to check route availability and cookie forwarding
try {
  $cookieHeader = ($session.Cookies.GetCookies('http://127.0.0.1:3003') | ForEach-Object { $_.ToString() }) -join '; '
  $headers = @{ Cookie = $cookieHeader }
  $direct = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8001/api/v1x/resumes/$id/duplicate" -Method POST -Headers $headers -ErrorAction SilentlyContinue
  if ($direct) {
    $directBody = if ($direct.Content -is [byte[]]) { [System.Text.Encoding]::UTF8.GetString($direct.Content) } else { $direct.Content }
    Write-Host "Direct backend duplicate status: $($direct.StatusCode) Content: $directBody"
  } else {
    Write-Host "Direct backend duplicate: no response"
  }
} catch {
  Write-Host "Direct backend duplicate FAILED: $($_.Exception.Message)"
}

try {
  $aiBody = @{ title = 'Software Engineer'; years_of_experience = 3 } | ConvertTo-Json
  $ai = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resume-ai/professional-summary" -Method Post -ContentType 'application/json' -Body $aiBody -WebSession $session -ErrorAction Stop
  $aiJson = $ai.Content | ConvertFrom-Json
  Write-Host "AI summary status: $($ai.StatusCode) length: $($aiJson.summary.Length)"
} catch {
  Write-Host "AI call FAILED: $($_.Exception.Message)"
}

try {
  $del = Invoke-WebRequest -UseBasicParsing -Uri "$Base/api/session/resumes?id=$id" -Method DELETE -WebSession $session -ErrorAction Stop
  Write-Host "Delete resume: $($del.StatusCode)"
} catch {
  Write-Host "Delete resume FAILED: $($_.Exception.Message)"
}

Write-Host "Smoke run completed"