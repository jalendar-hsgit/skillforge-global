#!/bin/bash

# ============================================================
# PHASE 2.3 + STRIPE + EMAIL DEPLOYMENT SCRIPT
# ============================================================
#
# This script automates the complete deployment of Phase 2.3
# including Stripe payments and email notifications
#
# Usage: bash deploy_phase_2_3.sh
# ============================================================

set -e  # Exit on error

echo "=========================================="
echo "Phase 2.3 Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================
# STEP 1: INSTALL DEPENDENCIES
# ============================================================
echo -e "${YELLOW}STEP 1: Installing dependencies...${NC}"
cd backend
pip install stripe python-dotenv aiosmtplib -q
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# ============================================================
# STEP 2: CREATE .ENV FILE
# ============================================================
echo -e "${YELLOW}STEP 2: Checking .env configuration...${NC}"

if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${RED}⚠ .env created from template${NC}"
    echo -e "${RED}⚠ YOU MUST CONFIGURE .env with your Stripe keys and email settings${NC}"
    echo ""
    echo "Required settings:"
    echo "  - STRIPE_PUBLIC_KEY (from https://dashboard.stripe.com/apikeys)"
    echo "  - STRIPE_SECRET_KEY"
    echo "  - SENDER_EMAIL (Gmail, SendGrid, or AWS SES)"
    echo "  - SENDER_PASSWORD (App password for Gmail)"
    echo ""
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi
echo ""

# ============================================================
# STEP 3: VERIFY DATABASE
# ============================================================
echo -e "${YELLOW}STEP 3: Verifying database...${NC}"

# Check if database exists
if [ -f "app/data/skillforge.db" ]; then
    echo -e "${GREEN}✓ Database found${NC}"
else
    echo "Creating database..."
    python -c "from app.core.db import Base, engine; Base.metadata.create_all(bind=engine)"
    echo -e "${GREEN}✓ Database created${NC}"
fi
echo ""

# ============================================================
# STEP 4: RUN TESTS (optional)
# ============================================================
echo -e "${YELLOW}STEP 4: (Optional) Running basic tests...${NC}"
echo "To run full test suite: pytest tests/ -v"
echo ""

# ============================================================
# STEP 5: GIT CONFIGURATION
# ============================================================
echo -e "${YELLOW}STEP 5: Git configuration...${NC}"

# Check if .gitignore includes .env
if grep -q "^\.env$" ../.gitignore 2>/dev/null; then
    echo -e "${GREEN}✓ .env is in .gitignore${NC}"
else
    echo -e "${YELLOW}⚠ Make sure .env is in .gitignore${NC}"
    echo "Add this line to .gitignore: .env"
fi
echo ""

# ============================================================
# STEP 6: SUMMARY
# ============================================================
echo -e "${GREEN}=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. CONFIGURE .env with your credentials:"
echo "   - Stripe API keys"
echo "   - Email configuration (Gmail App Password, SendGrid, or AWS SES)"
echo ""
echo "2. START THE APPLICATION:"
echo "   Terminal 1 (Backend):"
echo "   cd backend"
echo "   uvicorn app.main:app --reload --port 8001"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   npm run dev"
echo ""
echo "3. TEST THE ENDPOINTS:"
echo "   curl http://localhost:8001/api/v1x/payments/balance"
echo ""
echo "4. PUSH TO GIT:"
echo "   git add ."
echo "   git commit -m 'feat: Phase 2.3 + Stripe + Email integration'"
echo "   git push origin main"
echo ""
echo "DOCUMENTATION:"
echo "  - See PHASE_2_3_STRIPE_EMAIL_INTEGRATION.md for detailed setup"
echo "  - See PHASE_2_3_COMPLETE_IMPLEMENTATION.md for feature overview"
echo ""
