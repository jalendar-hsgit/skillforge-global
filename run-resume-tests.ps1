# Resume Feature - Quick Test Execution Guide for Windows PowerShell
# Run with: .\run-resume-tests.ps1

param(
    [string]$TestType = "interactive"
)

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "▶ $Message" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

Clear-Host
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    RESUME FEATURE - QUICK TEST EXECUTION GUIDE (Windows)   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Header "Checking Prerequisites"

# Check Node.js
try {
    $nodeVersion = & node --version 2>$null
    Write-Success "Node.js installed: $nodeVersion"
} catch {
    Write-Error-Custom "Node.js not found. Please install Node.js 18+"
    exit 1
}

# Check Python
try {
    $pythonVersion = & python --version 2>$null
    Write-Success "Python installed: $pythonVersion"
} catch {
    Write-Error-Custom "Python not found. Please install Python 3.11+"
    exit 1
}

# Check npm
try {
    $npmVersion = & npm --version 2>$null
    Write-Success "npm installed: $npmVersion"
} catch {
    Write-Error-Custom "npm not found"
    exit 1
}

# Menu
Write-Header "Test Execution Options"
Write-Host "Choose which tests to run:" -ForegroundColor White
Write-Host "  1) All Tests (frontend + backend + E2E)" -ForegroundColor White
Write-Host "  2) Frontend Tests Only" -ForegroundColor White
Write-Host "  3) Backend Tests Only" -ForegroundColor White
Write-Host "  4) E2E Validation Only" -ForegroundColor White
Write-Host "  5) Specific Frontend Tests" -ForegroundColor White
Write-Host "  6) Specific Backend Tests" -ForegroundColor White
Write-Host "  7) Exit" -ForegroundColor White
Write-Host ""

if ($TestType -eq "interactive") {
    $choice = Read-Host "Enter your choice (1-7)"
} else {
    $choice = $TestType
}

switch ($choice) {
    "1" {
        Write-Header "Installing Dependencies"
        Write-Host "Installing npm packages..."
        & npm install | Out-Null
        Write-Success "npm dependencies ready"
        
        Write-Host "Installing Python packages..."
        & pip install -r backend/requirements.txt -q
        Write-Success "Python dependencies ready"
        
        Write-Header "Running Frontend Tests"
        & npm test -- --passWithNoTests 2>$null
        
        Write-Header "Running Backend Tests"
        Push-Location backend
        & python -m pytest tests/ -v --tb=short
        Pop-Location
        
        Write-Header "E2E Validation"
        Write-Host "Starting E2E validation..."
        Write-Host "Make sure backend is running: uvicorn app.main:app --reload --port 8001"
        $backendCheck = Read-Host "Is backend running? (y/n)"
        
        if ($backendCheck -eq "y") {
            & python backend/tests/e2e_resume_validation.py
        } else {
            Write-Warning-Custom "Skipping E2E validation. Start backend and run: python backend/tests/e2e_resume_validation.py"
        }
    }
    
    "2" {
        Write-Header "Installing npm Dependencies"
        & npm install | Out-Null
        
        Write-Header "Running Frontend Tests"
        Write-Host "Running ResumeEditor.test.tsx, ResumeImportModal.test.tsx, resumes.test.tsx"
        & npm test -- --passWithNoTests 2>$null
        
        Write-Header "Frontend Test Summary"
        Write-Host "Test files found:" -ForegroundColor White
        Write-Host "  • src/components/resume/ResumeEditor.test.tsx" -ForegroundColor White
        Write-Host "  • src/components/resume/ResumeImportModal.test.tsx" -ForegroundColor White
        Write-Host "  • src/pages/resumes/resumes.test.tsx" -ForegroundColor White
    }
    
    "3" {
        Write-Header "Installing Python Dependencies"
        & pip install -r backend/requirements.txt -q
        
        Write-Header "Running Backend Tests"
        Push-Location backend
        & python -m pytest tests/test_resume_tools.py tests/test_resume_import.py -v --tb=short
        
        Write-Header "Backend Test Summary"
        Write-Host "Test files executed:" -ForegroundColor White
        Write-Host "  • backend/tests/test_resume_tools.py (export, suggestions)" -ForegroundColor White
        Write-Host "  • backend/tests/test_resume_import.py (upload, parsing)" -ForegroundColor White
        Pop-Location
    }
    
    "4" {
        Write-Header "E2E Resume Validation"
        & pip install -r backend/requirements.txt -q
        
        Write-Host "Starting E2E validation..."
        Write-Host ""
        Write-Host "Prerequisites:" -ForegroundColor White
        Write-Host "  1. Backend must be running on port 8001" -ForegroundColor White
        Write-Host "  2. Database must be initialized" -ForegroundColor White
        Write-Host "  3. Start with: uvicorn app.main:app --reload --port 8001" -ForegroundColor White
        Write-Host ""
        
        $backendCheck = Read-Host "Is backend running? (y/n)"
        
        if ($backendCheck -eq "y") {
            & python backend/tests/e2e_resume_validation.py
        } else {
            Write-Error-Custom "Backend not running. Start it first with:"
            Write-Host "  cd backend" -ForegroundColor Yellow
            Write-Host "  uvicorn app.main:app --reload --port 8001" -ForegroundColor Yellow
            exit 1
        }
    }
    
    "5" {
        Write-Header "Specific Frontend Tests"
        & npm install | Out-Null
        
        Write-Host "Select test file:" -ForegroundColor White
        Write-Host "  1) ResumeEditor Tests" -ForegroundColor White
        Write-Host "  2) ResumeImportModal Tests" -ForegroundColor White
        Write-Host "  3) Resume List Page Tests" -ForegroundColor White
        Write-Host ""
        
        $feChoice = Read-Host "Enter choice (1-3)"
        
        switch ($feChoice) {
            "1" {
                Write-Header "Running ResumeEditor Tests"
                & npm test -- ResumeEditor.test.tsx --verbose 2>$null
            }
            "2" {
                Write-Header "Running ResumeImportModal Tests"
                & npm test -- ResumeImportModal.test.tsx --verbose 2>$null
            }
            "3" {
                Write-Header "Running Resume List Page Tests"
                & npm test -- resumes.test.tsx --verbose 2>$null
            }
            default {
                Write-Error-Custom "Invalid choice"
                exit 1
            }
        }
    }
    
    "6" {
        Write-Header "Specific Backend Tests"
        & pip install -r backend/requirements.txt -q
        
        Write-Host "Select test file:" -ForegroundColor White
        Write-Host "  1) Resume Export & Suggestions Tests" -ForegroundColor White
        Write-Host "  2) Resume Import & Parsing Tests" -ForegroundColor White
        Write-Host "  3) Both" -ForegroundColor White
        Write-Host ""
        
        $beChoice = Read-Host "Enter choice (1-3)"
        
        Push-Location backend
        switch ($beChoice) {
            "1" {
                Write-Header "Running Resume Export Tests"
                & python -m pytest tests/test_resume_tools.py -v --tb=short
            }
            "2" {
                Write-Header "Running Resume Import Tests"
                & python -m pytest tests/test_resume_import.py -v --tb=short
            }
            "3" {
                Write-Header "Running All Resume Tests"
                & python -m pytest tests/test_resume_tools.py tests/test_resume_import.py -v --tb=short
            }
            default {
                Write-Error-Custom "Invalid choice"
                exit 1
            }
        }
        Pop-Location
    }
    
    "7" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Error-Custom "Invalid choice. Please enter 1-7"
        exit 1
    }
}

Write-Header "Test Execution Complete"
Write-Success "All requested tests have been executed"
Write-Host ""
Write-Host "Documentation:" -ForegroundColor White
Write-Host "  • RESUME_TESTING_GUIDE.md - Comprehensive testing guide" -ForegroundColor White
Write-Host "  • RESUME_IMPLEMENTATION_SUMMARY.md - Implementation details" -ForegroundColor White
Write-Host "  • README.md - Project overview" -ForegroundColor White
Write-Host ""
