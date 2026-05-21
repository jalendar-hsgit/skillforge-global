@echo off
REM Test API endpoints
echo Testing API endpoints...

REM Test using curl if available
where curl >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Using curl...
    curl -s -o /dev/null -w "Healthz: %%{http_code}\n" http://localhost:8001/healthz
    curl -s -o /dev/null -w "Courses: %%{http_code}\n" http://localhost:8001/api/v1/courses
    curl -s -o /dev/null -w "Mentors: %%{http_code}\n" http://localhost:8001/api/v1x/mentors
) else (
    echo Curl not found, trying with PowerShell...
    powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { (Invoke-WebRequest -Uri 'http://localhost:8001/healthz' -UseBasicParsing -TimeoutSec 5).StatusCode | %% { Write-Host 'Healthz: ' $_ } } catch { }"
    powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { (Invoke-WebRequest -Uri 'http://localhost:8001/api/v1/courses' -UseBasicParsing -TimeoutSec 5).StatusCode | %% { Write-Host 'Courses: ' $_ } } catch { }"
    powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { (Invoke-WebRequest -Uri 'http://localhost:8001/api/v1x/mentors' -UseBasicParsing -TimeoutSec 5).StatusCode | %% { Write-Host 'Mentors: ' $_ } } catch { }"
)

pause
