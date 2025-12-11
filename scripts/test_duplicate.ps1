#!/usr/bin/env pwsh

# Test script to diagnose duplicate endpoint
param(
    [string]$ApiBase = "http://127.0.0.1:3003",
    [string]$Token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxOTUiLCJleHAiOjk5OTk5OTk5OTl9.F0qZ6PblLqbM3j6Y7Jz3bPfnN_0q1X_7Y_9Z_0a_1b",
    [int]$ResumeId = 263
)

Write-Host "=== Testing v1x Proxy Duplicate Endpoint ===" -ForegroundColor Cyan
Write-Host "API Base: $ApiBase" 
Write-Host "Resume ID: $ResumeId"
Write-Host ""

# Test 1: Health check on v1x proxy
Write-Host "Test 1: Health check (GET /api/session/v1x/coins_db/balance)" -ForegroundColor Yellow
try {
    $res = Invoke-WebRequest -Uri "$ApiBase/api/session/v1x/coins_db/balance" `
        -Method GET `
        -Headers @{"Cookie" = "token=$Token"} `
        -SkipHttpErrorCheck
    Write-Host "Status: $($res.StatusCode)"
    if ($res.Headers['x-debug-target']) {
        Write-Host "Target: $($res.Headers['x-debug-target'])"
    }
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Get resume (should work)
Write-Host "Test 2: Get resume (GET /api/session/v1x/resumes/$ResumeId)" -ForegroundColor Yellow
try {
    $res = Invoke-WebRequest -Uri "$ApiBase/api/session/v1x/resumes/$ResumeId" `
        -Method GET `
        -Headers @{"Cookie" = "token=$Token"} `
        -SkipHttpErrorCheck
    Write-Host "Status: $($res.StatusCode)"
    if ($res.Headers['x-debug-target']) {
        Write-Host "Target: $($res.Headers['x-debug-target'])"
    }
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Duplicate resume (the problematic call)
Write-Host "Test 3: Duplicate resume (POST /api/session/v1x/resumes/$ResumeId/duplicate)" -ForegroundColor Yellow
try {
    $res = Invoke-WebRequest -Uri "$ApiBase/api/session/v1x/resumes/$ResumeId/duplicate" `
        -Method POST `
        -Headers @{"Cookie" = "token=$Token"; "Content-Type" = "application/json"} `
        -Body "{}" `
        -SkipHttpErrorCheck
    Write-Host "Status: $($res.StatusCode)"
    if ($res.Headers['x-debug-target']) {
        Write-Host "Target: $($res.Headers['x-debug-target'])"
    }
    Write-Host "Response length: $($res.Content.Length)"
    if ($res.StatusCode -eq 200 -or $res.StatusCode -eq 201) {
        Write-Host "Response: $($res.Content | ConvertFrom-Json | ConvertTo-Json)"
    } else {
        Write-Host "Response: $($res.Content)"
    }
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Test the catch-all with a simple arbitrary path
Write-Host "Test 4: Test catch-all with arbitrary path (GET /api/session/v1x/test/path)" -ForegroundColor Yellow
try {
    $res = Invoke-WebRequest -Uri "$ApiBase/api/session/v1x/test/path" `
        -Method GET `
        -Headers @{"Cookie" = "token=$Token"} `
        -SkipHttpErrorCheck
    Write-Host "Status: $($res.StatusCode)"
    if ($res.Headers['x-debug-target']) {
        Write-Host "Target: $($res.Headers['x-debug-target'])"
    }
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== Test complete ===" -ForegroundColor Cyan
