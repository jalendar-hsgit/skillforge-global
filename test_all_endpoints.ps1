# SkillForge Global - Complete E2E Test Suite
# Tests all endpoints and features from scratch

Write-Host "`n🚀 SkillForge Global - Complete System Test`n" -ForegroundColor Cyan
Write-Host "=" * 70

$BACKEND = "http://localhost:8001"
$FRONTEND = "http://localhost:3000"
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    try {
        & $Test
        Write-Host "✅ $Name" -ForegroundColor Green
        $script:testsPassed++
    } catch {
        Write-Host "❌ $Name - $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
    }
}

# 1. INFRASTRUCTURE
Write-Host "`n📡 Testing Infrastructure..." -ForegroundColor Yellow

Test-Endpoint "Backend Health Check" {
    $r = Invoke-RestMethod -Uri "$BACKEND/healthz"
    if (-not $r.ok) { throw "Health check failed" }
}

Test-Endpoint "Frontend Loading" {
    $r = Invoke-WebRequest -Uri $FRONTEND -UseBasicParsing
    if ($r.StatusCode -ne 200) { throw "Frontend not responding" }
}

Test-Endpoint "OpenAPI Docs Available" {
    $docs = Invoke-RestMethod -Uri "$BACKEND/openapi.json"
    if (-not $docs.paths) { throw "OpenAPI schema missing" }
}

# 2. AUTHENTICATION
Write-Host "`n🔐 Testing Authentication..." -ForegroundColor Yellow

$testEmail = "fulltest_$(Get-Date -Format 'yyyyMMddHHmmss')@test.com"
$testPassword = "Test123!"

Test-Endpoint "User Signup" {
    $body = @{
        email = $testEmail
        password = $testPassword
        name = "Full Test User"
    } | ConvertTo-Json
    
    $r = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/auth/signup" -ContentType 'application/json' -Body $body
    if (-not $r.created) { throw "Signup failed" }
}

Test-Endpoint "User Login" {
    $body = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $r = Invoke-WebRequest -Method Post -Uri "$BACKEND/api/v1/auth/login" -ContentType 'application/json' -Body $body -SessionVariable 'global:testSession'
    if ($r.StatusCode -ne 200) { throw "Login failed" }
    $global:testSession = $testSession
}

Test-Endpoint "Get Current User (/me)" {
    $user = Invoke-RestMethod -Uri "$BACKEND/api/v1/auth/me" -WebSession $global:testSession
    if ($user.email -ne $testEmail) { throw "User email mismatch" }
}

# 3. COURSES
Write-Host "`n📚 Testing Courses..." -ForegroundColor Yellow

Test-Endpoint "List All Courses" {
    $courses = Invoke-RestMethod -Uri "$BACKEND/api/v1/courses"
    if ($courses.Count -lt 1) { throw "No courses found" }
}

Test-Endpoint "Get Course by Slug" {
    $course = Invoke-RestMethod -Uri "$BACKEND/api/v1/courses/python-ai"
    if (-not $course.title) { throw "Course not found" }
}

# 4. QUIZZES - STATIC
Write-Host "`n📝 Testing Static Quizzes..." -ForegroundColor Yellow

Test-Endpoint "Get Quiz by Path" {
    $quiz = Invoke-RestMethod -Uri "$BACKEND/api/v1/quizzes?path=python-ai" -WebSession $global:testSession
    if ($quiz.questions.Count -lt 1) { throw "No questions found" }
}

Test-Endpoint "Submit Quiz" {
    # Get quiz first
    $quiz = Invoke-RestMethod -Uri "$BACKEND/api/v1/quizzes?path=python-ai" -WebSession $global:testSession
    
    # Submit with some answers
    $answers = @()
    for ($i = 0; $i -lt [Math]::Min(5, $quiz.questions.Count); $i++) {
        $answers += @{
            id = $quiz.questions[$i].id
            answerIndex = 0
        }
    }
    
    $body = @{
        path = "python-ai"
        answers = $answers
    } | ConvertTo-Json -Depth 3
    
    $result = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/quizzes/submit" -ContentType 'application/json' -Body $body -WebSession $global:testSession
    if ($null -eq $result.score) { throw "No score returned" }
}

Test-Endpoint "Quiz Status" {
    $status = Invoke-RestMethod -Uri "$BACKEND/api/v1/quizzes/status?path=python-ai" -WebSession $global:testSession
    if ($null -eq $status.passed) { throw "Status not returned" }
}

# 5. QUIZZES - AI GENERATION
Write-Host "`n🤖 Testing AI Quiz Generation..." -ForegroundColor Yellow

Test-Endpoint "Generate AI Quiz" {
    $body = @{
        topic = "JavaScript Arrays"
        difficulty = "medium"
        num_questions = 2
        options_per_question = 3
    } | ConvertTo-Json
    
    $quiz = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/quizzes/generate" -ContentType 'application/json' -Body $body -WebSession $global:testSession
    if ($quiz.questions.Count -ne 2) { throw "Wrong number of questions" }
    $global:generatedQuizId = $quiz.id
}

Test-Endpoint "Submit AI Quiz" {
    $body = @{
        topic = "test"
        difficulty = "easy"
        num_questions = 1
        options_per_question = 2
    } | ConvertTo-Json
    
    $quiz = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/quizzes/generate" -ContentType 'application/json' -Body $body -WebSession $global:testSession
    
    $submitBody = @{
        path = "ai-test"
        questions = $quiz.questions
        answers = @(@{
            id = $quiz.questions[0].id
            answerIndex = 0
        })
    } | ConvertTo-Json -Depth 3
    
    $result = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/quizzes/submit-ai" -ContentType 'application/json' -Body $submitBody -WebSession $global:testSession
    if ($null -eq $result.score) { throw "No score returned" }
}

Test-Endpoint "List Saved Quizzes" {
    $saved = Invoke-RestMethod -Uri "$BACKEND/api/v1/quizzes/saved" -WebSession $global:testSession
    # May be empty, just check it returns array
    if ($null -eq $saved) { throw "Saved endpoint failed" }
}

Test-Endpoint "Start Quiz Session" {
    $session = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/quizzes/session/start?path=test-path" -WebSession $global:testSession
    if ($null -eq $session.session_id) { throw "Session not created" }
}

Test-Endpoint "Rate Limiting Works" {
    $successCount = 0
    $rateLimited = $false
    
    $body = @{
        topic = "rate-test"
        difficulty = "easy"
        num_questions = 1
        options_per_question = 2
    } | ConvertTo-Json
    
    for ($i = 1; $i -le 11; $i++) {
        try {
            Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/quizzes/generate" -ContentType 'application/json' -Body $body -WebSession $global:testSession -ErrorAction Stop | Out-Null
            $successCount++
        } catch {
            if ($_.Exception.Response.StatusCode -eq 429) {
                $rateLimited = $true
                break
            }
        }
    }
    
    if (-not $rateLimited) { throw "Rate limit not enforced after $successCount requests" }
}

# 6. PROGRESS TRACKING
Write-Host "`n📊 Testing Progress..." -ForegroundColor Yellow

Test-Endpoint "Get User Progress" {
    $progress = Invoke-RestMethod -Uri "$BACKEND/api/v1/progress" -WebSession $global:testSession
    # Returns array of progress items
    if ($null -eq $progress) { throw "Progress endpoint failed" }
}

# 7. PATHS
Write-Host "`n🛤️  Testing Learning Paths..." -ForegroundColor Yellow

Test-Endpoint "List All Paths" {
    $paths = Invoke-RestMethod -Uri "$BACKEND/api/v1/paths"
    if ($paths.Count -lt 1) { throw "No paths found" }
}

# 8. ACHIEVEMENTS
Write-Host "`n🏆 Testing Achievements..." -ForegroundColor Yellow

Test-Endpoint "Get User Achievements" {
    $achievements = Invoke-RestMethod -Uri "$BACKEND/api/v1/achievements/me" -WebSession $global:testSession
    # Returns array
    if ($null -eq $achievements) { throw "Achievements endpoint failed" }
}

Test-Endpoint "Unlock Achievement" {
    $body = @{
        key = "test-achievement-$(Get-Date -Format 'HHmmss')"
        title = "Test Achievement"
        description = "Testing achievement unlock"
        points = 10
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/achievements/unlock" -ContentType 'application/json' -Body $body -WebSession $global:testSession
        if ($null -eq $result) { throw "No result returned" }
    } catch {
        # 409 Conflict is OK (already unlocked)
        if ($_.Exception.Response.StatusCode -ne 409) { throw }
    }
}

# 9. DASHBOARD
Write-Host "`n📊 Testing Dashboard..." -ForegroundColor Yellow

Test-Endpoint "Dashboard Endpoint" {
    $dashboard = Invoke-RestMethod -Uri "$BACKEND/api/v1/dashboard" -WebSession $global:testSession
    if ($null -eq $dashboard) { throw "Dashboard endpoint failed" }
}

# 10. NEWSLETTER
Write-Host "`n📧 Testing Newsletter..." -ForegroundColor Yellow

Test-Endpoint "Newsletter Subscribe" {
    $body = @{
        email = "newsletter_$(Get-Date -Format 'yyyyMMddHHmmss')@test.com"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Method Post -Uri "$BACKEND/api/v1/subscribe" -ContentType 'application/json' -Body $body
    if (-not $result.subscribed) { throw "Subscribe failed" }
}

# 11. FRONTEND PAGES
Write-Host "`n🌐 Testing Frontend Pages..." -ForegroundColor Yellow

$pages = @(
    "/",
    "/login",
    "/signup",
    "/paths",
    "/pricing",
    "/quiz/python-basics",
    "/dashboard"
)

foreach ($page in $pages) {
    Test-Endpoint "Page: $page" {
        $r = Invoke-WebRequest -Uri "$FRONTEND$page" -UseBasicParsing -TimeoutSec 10
        if ($r.StatusCode -ne 200) { throw "Page returned $($r.StatusCode)" }
    }
}

# 12. NEXT.JS API PROXIES
Write-Host "`n🔄 Testing Next.js API Proxies..." -ForegroundColor Yellow

Test-Endpoint "Proxy: /api/quizzes/generate" {
    $body = @{
        topic = "Proxy Test"
        difficulty = "easy"
        num_questions = 1
        options_per_question = 2
    } | ConvertTo-Json
    
    $r = Invoke-RestMethod -Method Post -Uri "$FRONTEND/api/quizzes/generate" -ContentType 'application/json' -Body $body -WebSession $global:testSession
    if ($null -eq $r.id) { throw "Proxy failed" }
}

Test-Endpoint "Proxy: /api/quizzes/saved" {
    $r = Invoke-RestMethod -Uri "$FRONTEND/api/quizzes/saved" -WebSession $global:testSession
    if ($null -eq $r) { throw "Proxy failed" }
}

# SUMMARY
Write-Host "`n" + ("=" * 70)
Write-Host "`n📊 Test Summary" -ForegroundColor Cyan
Write-Host "  ✅ Passed: $testsPassed" -ForegroundColor Green
Write-Host "  ❌ Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host "  Total:  $($testsPassed + $testsFailed)`n"

if ($testsFailed -eq 0) {
    Write-Host "🎉 All tests passed! System is fully operational.`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Some tests failed. Review errors above.`n" -ForegroundColor Yellow
    exit 1
}
