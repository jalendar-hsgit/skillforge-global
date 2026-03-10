#!/bin/bash

# SkillForge Backend Deployment Script
# Usage: ./scripts/deploy-backend.sh [dev|prod] [--rollback]

set -e  # Exit on error

ENVIRONMENT=${1:-prod}
ROLLBACK=${2:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== SkillForge Backend Deployment ===${NC}"
echo "Environment: $ENVIRONMENT"
echo "Rollback: $ROLLBACK"

# Step 1: Pre-deployment checks
echo -e "\n${YELLOW}[1/8]${NC} Pre-deployment checks..."

if [ "$ENVIRONMENT" == "prod" ]; then
    # Check if .env.production exists
    if [ ! -f "backend/.env.production" ]; then
        echo -e "${RED}ERROR: backend/.env.production not found${NC}"
        exit 1
    fi
    
    # Verify git is clean
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}WARNING: Uncommitted changes detected${NC}"
        echo "Commit all changes before deploying to production"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo -e "${GREEN}✓ Pre-deployment checks passed${NC}"

# Step 2: Install dependencies
echo -e "\n${YELLOW}[2/8]${NC} Installing Python dependencies..."

cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate || source venv/Scripts/activate  # Windows support
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Run tests
echo -e "\n${YELLOW}[3/8]${NC} Running tests..."

if [ -d "tests" ]; then
    pytest tests/ -v --tb=short || {
        echo -e "${RED}Tests failed. Aborting deployment.${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠ No tests directory found${NC}"
fi

# Step 4: Database initialization (if needed)
echo -e "\n${YELLOW}[4/8]${NC} Database initialization..."

if [ "$ENVIRONMENT" == "prod" ] && [ "$ROLLBACK" != "--rollback" ]; then
    # For production, typically use RDS - skip local init
    echo "Skipping database initialization (using RDS)"
else
    # For dev, initialize SQLite
    if [ -f "init_db.py" ]; then
        python init_db.py
        echo -e "${GREEN}✓ Database initialized${NC}"
    fi
fi

# Step 5: Build and optimize
echo -e "\n${YELLOW}[5/8]${NC} Building application..."

# Compile Python files
python -m py_compile app/main.py
echo -e "${GREEN}✓ Syntax validation passed${NC}"

# Step 6: AWS deployment
echo -e "\n${YELLOW}[6/8]${NC} Deploying to AWS..."

if [ "$ENVIRONMENT" == "prod" ]; then
    # Get AWS instance details
    EC2_INSTANCE=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=skillforge-backend" "Name=instance-state-name,Values=running" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    
    if [ -z "$EC2_INSTANCE" ] || [ "$EC2_INSTANCE" == "None" ]; then
        echo -e "${RED}ERROR: EC2 instance not found or not running${NC}"
        exit 1
    fi
    
    echo "Target EC2: $EC2_INSTANCE"
    
    # Get SSH key path from environment or config
    SSH_KEY=${SKILLFORGE_SSH_KEY:-~/.ssh/skillforge-prod.pem}
    
    if [ ! -f "$SSH_KEY" ]; then
        echo -e "${RED}ERROR: SSH key not found at $SSH_KEY${NC}"
        exit 1
    fi
    
    # Deploy via SSH
    echo "Deploying code to EC2..."
    
    # Method 1: Using git on remote server (recommended)
    ssh -i "$SSH_KEY" ec2-user@"$EC2_INSTANCE" << 'REMOTESCRIPT'
        cd /opt/skillforge
        source venv/bin/activate
        git pull origin main
        pip install -r backend/requirements.txt
        
        # Restart service
        sudo systemctl restart skillforge
        sleep 5
        sudo systemctl status skillforge
REMOTESCRIPT
    
    STATUS=$?
    if [ $STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Code deployed successfully${NC}"
    else
        echo -e "${RED}Deployment failed with status $STATUS${NC}"
        exit 1
    fi
    
    # Verify deployment
    echo "Verifying deployment..."
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://"$EC2_INSTANCE":8001/api/v1/health)
    
    if [ "$HEALTH_CHECK" == "200" ]; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}Health check failed (HTTP $HEALTH_CHECK)${NC}"
        exit 1
    fi
else
    # For development, just restart local service
    echo "Development deployment - restarting local service"
    # This depends on your local setup
fi

# Step 7: Database backup
echo -e "\n${YELLOW}[7/8]${NC} Creating database backup..."

if [ "$ENVIRONMENT" == "prod" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    aws rds create-db-snapshot \
        --db-instance-identifier skillforge-prod-db \
        --db-snapshot-identifier skillforge-backup-$TIMESTAMP \
        --tags "Key=Environment,Value=production" "Key=Type,Value=pre-deployment"
    
    echo -e "${GREEN}✓ Database backup created (skillforge-backup-$TIMESTAMP)${NC}"
fi

# Step 8: Post-deployment verification
echo -e "\n${YELLOW}[8/8]${NC} Post-deployment verification..."

# Check logs for errors
if [ "$ENVIRONMENT" == "prod" ]; then
    echo "Checking CloudWatch logs for errors..."
    
    aws logs filter-log-events \
        --log-group-name /skillforge/backend \
        --start-time $(($(date +%s) - 300))000 \
        --filter-pattern "[ERROR]" \
        --query 'events[*].message' \
        --output text | head -10
    
    echo -e "${GREEN}✓ Log check complete${NC}"
fi

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "Backend URL: $([ "$ENVIRONMENT" == "prod" ] && echo 'https://api.skillforge.com' || echo 'http://localhost:8001')"
echo -e "Health Check: $([ "$ENVIRONMENT" == "prod" ] && echo 'https://api.skillforge.com/api/v1/health' || echo 'http://localhost:8001/api/v1/health')"

# Cleanup
cd ..

exit 0
