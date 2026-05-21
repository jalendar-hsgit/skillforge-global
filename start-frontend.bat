@echo off
echo ========================================
echo Starting SkillForge Global Frontend
echo ========================================
echo.

cd /d "%~dp0"

echo Installing/updating dependencies...
call npm install

echo.
echo Starting frontend production server...
echo Binding to 127.0.0.1:3000 for Windows reliability
echo Press Ctrl+C to stop
echo.

set NEXT_PUBLIC_API_BASE=http://127.0.0.1:8001
REM Ensure a fresh build exists
call npm run build

REM Start Next.js directly via node with explicit host/port
node node_modules\next\dist\bin\next start -H 127.0.0.1 -p 3000
