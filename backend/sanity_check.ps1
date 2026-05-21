$outFile = "sanity_results.txt"
if (Test-Path $outFile) { Remove-Item $outFile -Force }

Add-Content -Path $outFile -Value "Sanity check started: $(Get-Date)"
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$loginBody = @{email='superadmin@skillforge.com'; password='super123'} | ConvertTo-Json
Add-Content -Path $outFile -Value "Logging in as superadmin..."
try {
    $login = Invoke-RestMethod -Uri 'http://127.0.0.1:8001/api/v1/auth/login' -Method POST -ContentType 'application/json' -Body $loginBody -WebSession $session -ErrorAction Stop
    Add-Content -Path $outFile -Value "LOGIN: SUCCESS: $($login | ConvertTo-Json -Compress)"
} catch {
    Add-Content -Path $outFile -Value "LOGIN: FAILED: $($_.Exception.Message)"
}

$endpoints = @(
  '/api/v1/auth/me',
  '/api/v1/courses',
  '/api/v1x/courses-db',
  '/api/quizzes/list',
  '/api/v1x/quizzes-db',
  '/api/v1x/coins_db/balance',
  '/api/v1x/mentors/all',
  '/api/v1x/mentor-portal/sessions',
  '/api/v1x/subscriptions/plans',
  '/api/session/resumes',
  '/api/v1x/job-applications',
  '/api/v1x/cover-letters',
  '/api/v1x/marketplace/courses',
  '/api/v1x/youtube-sync/status',
  '/api/v1x/chat/files',
  '/api/v1x/student-dashboard/stats',
  '/api/v1x/admin/users',
  '/api/v1x/admin/notifications/templates',
  '/api/v1x/admin/analytics'
)

foreach ($ep in $endpoints) {
    $url = "http://127.0.0.1:8001" + $ep
    Add-Content -Path $outFile -Value "\nCALL: $url"
    try {
        $res = Invoke-WebRequest -Uri $url -Method GET -WebSession $session -UseBasicParsing -ErrorAction Stop
        $status = $res.StatusCode
        $len = $res.Content.Length
        Add-Content -Path $outFile -Value "  STATUS: $status LENGTH: $len"
        try {
            $j = $res.Content | ConvertFrom-Json
            if ($j -is [System.Array]) { Add-Content -Path $outFile -Value "  JSON: Array count=$($j.Count)" }
            else { $props = $j | Get-Member -MemberType NoteProperty | Select -Expand Name; Add-Content -Path $outFile -Value "  JSON keys: $($props -join ', ')" }
        } catch {
            Add-Content -Path $outFile -Value "  (response not JSON or too large)"
        }
    } catch {
        Add-Content -Path $outFile -Value "  ERROR: $($_.Exception.Message)"
    }
}
Add-Content -Path $outFile -Value "Sanity check finished: $(Get-Date)"
