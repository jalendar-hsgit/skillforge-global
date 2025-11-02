@echo off
echo ========================================
echo Starting SkillForge Global Frontend
echo ========================================
echo.

cd /d "%~dp0"

echo Installing/updating dependencies...
call npm install

echo.
echo Starting frontend dev server...
echo Will be available at http://localhost:3000 (or 3001 if 3000 is taken)
echo Press Ctrl+C to stop
echo.

call npm run dev
