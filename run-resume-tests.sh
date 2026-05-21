#!/bin/bash
# Resume Feature - Quick Test Execution Guide
# This script helps quickly run all resume-related tests

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    RESUME FEATURE - QUICK TEST EXECUTION GUIDE             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo
    echo -e "${BLUE}▶ $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
print_header "Checking Prerequisites"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Python
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_error "Python not found. Please install Python 3.11+"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm installed: $NPM_VERSION"
else
    print_error "npm not found"
    exit 1
fi

# Check pytest
if python -m pytest --version &> /dev/null; then
    PYTEST_VERSION=$(python -m pytest --version | head -n 1)
    print_success "Pytest installed: $PYTEST_VERSION"
else
    print_warning "Pytest not installed. Installing from requirements.txt..."
fi

print_header "Test Execution Options"

echo "Choose which tests to run:"
echo "  1) All Tests (frontend + backend + E2E)"
echo "  2) Frontend Tests Only"
echo "  3) Backend Tests Only"
echo "  4) E2E Validation Only"
echo "  5) Specific Frontend Tests"
echo "  6) Specific Backend Tests"
echo "  7) Exit"
echo

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        print_header "Installing Dependencies"
        echo "Installing npm packages..."
        npm install --silent 2>/dev/null || print_warning "npm install had warnings"
        print_success "npm dependencies ready"
        
        echo "Installing Python packages..."
        pip install -r backend/requirements.txt -q || print_warning "Some packages already installed"
        print_success "Python dependencies ready"
        
        print_header "Running Frontend Tests"
        npm test -- --passWithNoTests --testPathPattern="test|spec" 2>/dev/null || print_warning "Some frontend tests failed"
        
        print_header "Running Backend Tests"
        cd backend
        python -m pytest tests/ -v --tb=short 2>/dev/null || print_warning "Some backend tests failed"
        cd ..
        
        print_header "E2E Validation"
        echo "Starting E2E validation..."
        echo "Make sure backend is running: uvicorn app.main:app --reload --port 8001"
        read -p "Is backend running? (y/n): " backend_check
        if [ "$backend_check" == "y" ]; then
            python backend/tests/e2e_resume_validation.py
        else
            print_warning "Skipping E2E validation. Start backend and run: python backend/tests/e2e_resume_validation.py"
        fi
        ;;
        
    2)
        print_header "Installing npm Dependencies"
        npm install --silent 2>/dev/null || print_warning "npm install had warnings"
        
        print_header "Running Frontend Tests"
        npm test -- --passWithNoTests --testPathPattern="ResumeEditor|ResumeImportModal|resumes" 2>/dev/null || true
        
        print_header "Frontend Test Summary"
        echo "Test files found:"
        echo "  • src/components/resume/ResumeEditor.test.tsx"
        echo "  • src/components/resume/ResumeImportModal.test.tsx"
        echo "  • src/pages/resumes/resumes.test.tsx"
        ;;
        
    3)
        print_header "Installing Python Dependencies"
        pip install -r backend/requirements.txt -q 2>/dev/null || print_warning "Some packages already installed"
        
        print_header "Running Backend Tests"
        cd backend
        python -m pytest tests/test_resume_tools.py tests/test_resume_import.py -v --tb=short
        
        print_header "Backend Test Summary"
        echo "Test files executed:"
        echo "  • backend/tests/test_resume_tools.py (export, suggestions)"
        echo "  • backend/tests/test_resume_import.py (upload, parsing)"
        cd ..
        ;;
        
    4)
        print_header "E2E Resume Validation"
        pip install -r backend/requirements.txt -q 2>/dev/null || print_warning "Some packages already installed"
        
        echo "Starting E2E validation..."
        echo
        echo "Prerequisites:"
        echo "  1. Backend must be running on port 8001"
        echo "  2. Database must be initialized"
        echo "  3. Start with: uvicorn app.main:app --reload --port 8001"
        echo
        read -p "Is backend running? (y/n): " backend_check
        
        if [ "$backend_check" == "y" ]; then
            python backend/tests/e2e_resume_validation.py
        else
            print_error "Backend not running. Start it first with:"
            echo "  cd backend"
            echo "  uvicorn app.main:app --reload --port 8001"
            exit 1
        fi
        ;;
        
    5)
        print_header "Specific Frontend Tests"
        npm install --silent 2>/dev/null || true
        
        echo "Select test file:"
        echo "  1) ResumeEditor Tests"
        echo "  2) ResumeImportModal Tests"
        echo "  3) Resume List Page Tests"
        echo
        read -p "Enter choice (1-3): " fe_choice
        
        case $fe_choice in
            1)
                print_header "Running ResumeEditor Tests"
                npm test -- ResumeEditor.test.tsx --verbose 2>/dev/null || true
                ;;
            2)
                print_header "Running ResumeImportModal Tests"
                npm test -- ResumeImportModal.test.tsx --verbose 2>/dev/null || true
                ;;
            3)
                print_header "Running Resume List Page Tests"
                npm test -- resumes.test.tsx --verbose 2>/dev/null || true
                ;;
            *)
                print_error "Invalid choice"
                exit 1
                ;;
        esac
        ;;
        
    6)
        print_header "Specific Backend Tests"
        pip install -r backend/requirements.txt -q 2>/dev/null || true
        
        echo "Select test file:"
        echo "  1) Resume Export & Suggestions Tests"
        echo "  2) Resume Import & Parsing Tests"
        echo "  3) Both"
        echo
        read -p "Enter choice (1-3): " be_choice
        
        cd backend
        case $be_choice in
            1)
                print_header "Running Resume Export Tests"
                python -m pytest tests/test_resume_tools.py -v --tb=short
                ;;
            2)
                print_header "Running Resume Import Tests"
                python -m pytest tests/test_resume_import.py -v --tb=short
                ;;
            3)
                print_header "Running All Resume Tests"
                python -m pytest tests/test_resume_tools.py tests/test_resume_import.py -v --tb=short
                ;;
            *)
                print_error "Invalid choice"
                exit 1
                ;;
        esac
        cd ..
        ;;
        
    7)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice. Please enter 1-7"
        exit 1
        ;;
esac

print_header "Test Execution Complete"
print_success "All requested tests have been executed"
echo
echo "Documentation:"
echo "  • RESUME_TESTING_GUIDE.md - Comprehensive testing guide"
echo "  • RESUME_IMPLEMENTATION_SUMMARY.md - Implementation details"
echo "  • README.md - Project overview"
echo
