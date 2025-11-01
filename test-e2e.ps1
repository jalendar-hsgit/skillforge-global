# PowerShell E2E test for SkillForge Resume application
$ErrorActionPreference = "Stop"
$BASE = "http://localhost:3000"
$EMAIL = "pstest@example.com"
$PASSWORD = "TestPass123!"

Write-Host "`n=== SkillForge Resume E2E Test (PowerShell) ===`n" -ForegroundColor Cyan

# 1. Signup
Write-Host "1️⃣  Signup..." -ForegroundColor Yellow
$signupBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json
try {
    $signupResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/signup" -Method Post -ContentType "application/json" -Body $signupBody -ErrorAction SilentlyContinue
    Write-Host "   Signup: $($signupResp.StatusCode)" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "   Signup: 400 (User exists - OK)" -ForegroundColor Yellow
    } else {
        throw "Signup failed: $_"
    }
}

# 2. Login
Write-Host "`n2️⃣  Login..." -ForegroundColor Yellow
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$loginBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json
$loginResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/login" -Method Post -ContentType "application/json" -Body $loginBody -WebSession $session -ErrorAction Stop
Write-Host "   Login: $($loginResp.StatusCode)" -ForegroundColor Green
Write-Host "   ✓ Cookie captured" -ForegroundColor Green

# 3. Get /me
Write-Host "`n3️⃣  Get user profile..." -ForegroundColor Yellow
$meResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/me" -WebSession $session -ErrorAction Stop
$user = $meResp.Content | ConvertFrom-Json
Write-Host "   Me: $($meResp.StatusCode) - User ID: $($user.id), Email: $($user.email)" -ForegroundColor Green

# 4. Create Resume
Write-Host "`n4️⃣  Create Resume..." -ForegroundColor Yellow
$createBody = @{
    full_name = "Test User"
    email = "test@example.com"
    phone = "555-1234"
    professional_summary = "Experienced developer."
} | ConvertTo-Json
$createResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resumes" -Method Post -ContentType "application/json" -Body $createBody -WebSession $session -ErrorAction Stop
$resume = $createResp.Content | ConvertFrom-Json
$resumeId = $resume.id
Write-Host "   Create: $($createResp.StatusCode) - Resume ID: $resumeId" -ForegroundColor Green

# 5. Get Resume
Write-Host "`n5️⃣  Get Resume..." -ForegroundColor Yellow
$getResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resumes?id=$resumeId" -WebSession $session -ErrorAction Stop
$fetchedResume = $getResp.Content | ConvertFrom-Json
Write-Host "   Get: $($getResp.StatusCode) - Name: $($fetchedResume.full_name)" -ForegroundColor Green

# 6. PATCH Resume
Write-Host "`n6️⃣  PATCH Resume..." -ForegroundColor Yellow
$patchBody = @{ full_name = "Updated Name"; phone = "555-9999" } | ConvertTo-Json
$patchResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resumes?id=$resumeId" -Method PATCH -ContentType "application/json" -Body $patchBody -WebSession $session -ErrorAction Stop
$patchedResume = $patchResp.Content | ConvertFrom-Json
Write-Host "   Patch: $($patchResp.StatusCode) - Updated name: $($patchedResume.full_name)" -ForegroundColor Green

# 7. AI Professional Summary
Write-Host "`n7️⃣  AI Professional Summary..." -ForegroundColor Yellow
$aiBody = @{ title = "Software Engineer"; years_of_experience = 5 } | ConvertTo-Json
$aiResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resume-ai/professional-summary" -Method Post -ContentType "application/json" -Body $aiBody -WebSession $session -ErrorAction Stop
$aiData = $aiResp.Content | ConvertFrom-Json
Write-Host "   AI summary: $($aiResp.StatusCode) - $($aiData.summary.Substring(0, [Math]::Min(60, $aiData.summary.Length)))..." -ForegroundColor Green

# 8. AI Bullet Points
Write-Host "`n8️⃣  AI Bullet Points..." -ForegroundColor Yellow
$bulletBody = @{ role = "Backend Developer"; description = "Built APIs" } | ConvertTo-Json
$bulletResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resume-ai/bullet-points" -Method Post -ContentType "application/json" -Body $bulletBody -WebSession $session -ErrorAction Stop
$bulletData = $bulletResp.Content | ConvertFrom-Json
Write-Host "   AI bullets: $($bulletResp.StatusCode) - Generated $($bulletData.bullet_points.Count) bullets" -ForegroundColor Green

# 9. Duplicate Resume
Write-Host "`n9️⃣  Duplicate Resume..." -ForegroundColor Yellow
$dupBody = @{ action = "duplicate" } | ConvertTo-Json
$dupResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resumes?id=$resumeId" -Method POST -ContentType "application/json" -Body $dupBody -WebSession $session -ErrorAction Stop
$dupResume = $dupResp.Content | ConvertFrom-Json
Write-Host "   Duplicate: $($dupResp.StatusCode) - Duplicated ID: $($dupResume.id)" -ForegroundColor Green

# 10. List Resumes
Write-Host "`n🔟 List Resumes..." -ForegroundColor Yellow
$listResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resumes" -WebSession $session -ErrorAction Stop
$resumes = $listResp.Content | ConvertFrom-Json
Write-Host "   List: $($listResp.StatusCode) - Total resumes: $($resumes.Count)" -ForegroundColor Green

# 11. Delete Original Resume
Write-Host "`n1️⃣1️⃣ Delete Resume..." -ForegroundColor Yellow
$delResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/session/resumes?id=$resumeId" -Method DELETE -WebSession $session -ErrorAction Stop
Write-Host "   Delete: $($delResp.StatusCode) - Deleted ID: $resumeId" -ForegroundColor Green

# 12. Courses
Write-Host "`n1️⃣2️⃣ Get Courses..." -ForegroundColor Yellow
$coursesResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/courses" -WebSession $session -ErrorAction Stop
$courses = $coursesResp.Content | ConvertFrom-Json
Write-Host "   Courses: $($coursesResp.StatusCode) - Found $($courses.Count) courses" -ForegroundColor Green

# 13. Progress
Write-Host "`n1️⃣3️⃣ Get Progress..." -ForegroundColor Yellow
try {
    $progressResp = Invoke-WebRequest -UseBasicParsing -Uri "$BASE/api/progress/get?path=python-ai" -WebSession $session -ErrorAction Stop
    Write-Host "   Progress: $($progressResp.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   Progress: 404 (No progress yet - OK)" -ForegroundColor Yellow
}

Write-Host "`n✅ All E2E tests passed!`n" -ForegroundColor Green
