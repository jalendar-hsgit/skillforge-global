# Start the backend detached and log output to run_server.log
# For PowerShell 5.1 (Windows) - run this from the repository root or from backend\
# Usage (PowerShell):
#   cd 'D:\python code\sfg\skillforge-global\backend'
#   $env:ADMIN_KEY = 'test-admin-key'
#   .\run_server_detached.ps1

# Ensure an ADMIN_KEY exists
if (-not $env:ADMIN_KEY) { $env:ADMIN_KEY = 'test-admin-key' }

$py = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
$log = Join-Path $PSScriptRoot 'run_server.log'

# Use cmd.exe to run the python script and redirect stdout/stderr to a log file
$cmd = "`"$py`" run_server.py > `"$log`" 2>&1"
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -NoNewWindow -WindowStyle Hidden -PassThru | Out-Null
Write-Output "Started detached backend; logs will be written to: $log"
