#!/usr/bin/env pwsh
# Simple test - just hit the endpoint and show status

$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxOTUiLCJleHAiOjk5OTk5OTk5OTl9.F0qZ6PblLqbM3j6Y7Jz3bPfnN_0q1X_7Y_9Z_0a_1b"
$url = "http://127.0.0.1:3003/api/session/v1x/resumes/263/duplicate"

Write-Host "Testing $url" -ForegroundColor Cyan

$result = & {
  $ErrorActionPreference = 'SilentlyContinue'
  $response = $null
  $statusCode = $null
  
  try {
    $response = Invoke-WebRequest -Uri $url -Method POST -Headers @{"Cookie"="token=$token"} -Body "{}" -SkipHttpErrorCheck
    $statusCode = $response.StatusCode
  } catch {
    $statusCode = $_.Exception.Response.StatusCode.Value
  }
  
  return @{ statusCode = $statusCode; response = $response }
}

$result.statusCode
