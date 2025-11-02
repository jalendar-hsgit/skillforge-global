@echo off
echo ========================================
echo Starting SkillForge Global Backend
echo ========================================
echo.

cd /d "%~dp0backend"

echo Installing/updating dependencies...
pip install -q -r requirements.txt
pip install -q python-dateutil APScheduler==3.10.4

echo.
echo Starting backend server on http://localhost:8001
echo Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
