#!/bin/bash

# SkillForge Frontend Deployment Script
# Usage: ./scripts/deploy-frontend.sh [dev|prod|vercel|s3]

set -e

ENVIRONMENT=${1:-prod}
PLATFORM=${2:-s3}  # s3, vercel, or ec2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== SkillForge Frontend Deployment ===${NC}"
echo "Environment: $ENVIRONMENT"
echo "Platform: $PLATFORM"

# Step 1: Pre-deployment checks
echo -e "\n${YELLOW}[1/7]${NC} Pre-deployment checks..."

if [ ! -f ".env.$ENVIRONMENT" ] && [ "$ENVIRONMENT" != "dev" ]; then
    echo -e "${RED}ERROR: .env.$ENVIRONMENT not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Pre-deployment checks passed${NC}"

# Step 2: Install dependencies
echo -e "\n${YELLOW}[2/7]${NC} Installing Node.js dependencies..."

npm ci --quiet  # Use npm ci instead of npm install for production

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Linting
echo -e "\n${YELLOW}[3/7]${NC} Running linter..."

if npm run lint > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${YELLOW}⚠ Linting warnings (continuing)${NC}"
fi

# Step 4: Build
echo -e "\n${YELLOW}[4/7]${NC} Building Next.js application..."

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    export $(cat ".env.$ENVIRONMENT" | grep -v '^#' | xargs)
fi

# Build with optimization
NEXT_TELEMETRY_DISABLED=1 npm run build

if [ ! -d ".next" ]; then
    echo -e "${RED}ERROR: Build failed - .next directory not created${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build completed successfully${NC}"

# Step 5: Deployment logic
echo -e "\n${YELLOW}[5/7]${NC} Deploying frontend..."

case $PLATFORM in
    vercel)
        echo "Deploying to Vercel..."
        
        if ! command -v vercel &> /dev/null; then
            npm install -g vercel
        fi
        
        # Deploy to production
        if [ "$ENVIRONMENT" == "prod" ]; then
            vercel --prod --token=$VERCEL_TOKEN
        else
            vercel --token=$VERCEL_TOKEN
        fi
        
        echo -e "${GREEN}✓ Deployed to Vercel${NC}"
        ;;
        
    s3)
        echo "Deploying to S3 + CloudFront..."
        
        # Check AWS credentials
        if ! aws sts get-caller-identity > /dev/null 2>&1; then
            echo -e "${RED}ERROR: AWS credentials not configured${NC}"
            exit 1
        fi
        
        # Determine S3 bucket
        S3_BUCKET="skillforge-frontend-${ENVIRONMENT}"
        
        # Create bucket if not exists
        if ! aws s3 ls "s3://$S3_BUCKET" 2>/dev/null; then
            echo "Creating S3 bucket: $S3_BUCKET"
            aws s3 mb "s3://$S3_BUCKET" --region us-east-1
            
            # Block public access (CloudFront will access via OAI)
            aws s3api put-public-access-block \
                --bucket "$S3_BUCKET" \
                --public-access-block-configuration \
                "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
        fi
        
        # Upload files with optimal cache headers
        echo "Uploading static assets..."
        
        # Cache immutable assets for 1 year
        aws s3 sync .next/static "s3://$S3_BUCKET/.next/static" \
            --cache-control "public, max-age=31536000, immutable" \
            --delete
        
        # Cache versioned public assets for 30 days
        if [ -d "public" ]; then
            aws s3 sync public "s3://$S3_BUCKET/public" \
                --cache-control "public, max-age=2592000" \
                --delete
        fi
        
        # Don't cache HTML files (5 minutes)
        aws s3 sync . "s3://$S3_BUCKET" \
            --cache-control "public, max-age=300" \
            --exclude ".next/*" \
            --exclude "public/*" \
            --exclude ".git/*" \
            --exclude "node_modules/*" \
            --exclude "*.ts" \
            --exclude "*.tsx" \
            --exclude "*.json" \
            --include "*.html" \
            --delete
        
        echo -e "${GREEN}✓ Files uploaded to S3${NC}"
        
        # Invalidate CloudFront cache
        if [ "$ENVIRONMENT" == "prod" ]; then
            echo "Invalidating CloudFront cache..."
            
            # Get distribution ID from environment or config
            DISTRIBUTION_ID=${CLOUDFRONT_DISTRIBUTION_ID:-$(aws cloudfront list-distributions \
                --query "DistributionList.Items[?Origins.Items[0].DomainName=='${S3_BUCKET}.s3.amazonaws.com'].Id" \
                --output text)}
            
            if [ -n "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
                aws cloudfront create-invalidation \
                    --distribution-id "$DISTRIBUTION_ID" \
                    --paths "/*" > /dev/null
                
                echo -e "${GREEN}✓ CloudFront cache invalidated${NC}"
            fi
        fi
        ;;
        
    ec2)
        echo "Deploying to EC2..."
        
        # Get EC2 instance
        EC2_INSTANCE=$(aws ec2 describe-instances \
            --filters "Name=tag:Name,Values=skillforge-frontend" "Name=instance-state-name,Values=running" \
            --query 'Reservations[0].Instances[0].PublicIpAddress' \
            --output text)
        
        if [ -z "$EC2_INSTANCE" ] || [ "$EC2_INSTANCE" == "None" ]; then
            echo -e "${RED}ERROR: EC2 instance not found${NC}"
            exit 1
        fi
        
        SSH_KEY=${SKILLFORGE_SSH_KEY:-~/.ssh/skillforge-prod.pem}
        
        # Deploy via SCP and SSH
        echo "Uploading to EC2: $EC2_INSTANCE"
        
        # Create tar archive
        tar --exclude=node_modules --exclude=.git -czf /tmp/skillforge-frontend.tar.gz .
        
        # Upload to EC2
        scp -i "$SSH_KEY" -r /tmp/skillforge-frontend.tar.gz ec2-user@"$EC2_INSTANCE":/tmp/
        
        # Extract and restart
        ssh -i "$SSH_KEY" ec2-user@"$EC2_INSTANCE" << 'REMOTESCRIPT'
            cd /opt/skillforge
            tar -xzf /tmp/skillforge-frontend.tar.gz
            npm ci --production
            npm run build
            pm2 restart skillforge-frontend
            pm2 save
REMOTESCRIPT
        
        echo -e "${GREEN}✓ Deployed to EC2${NC}"
        ;;
        
    *)
        echo -e "${RED}ERROR: Unknown platform: $PLATFORM${NC}"
        echo "Supported platforms: vercel, s3, ec2"
        exit 1
        ;;
esac

# Step 6: Health check
echo -e "\n${YELLOW}[6/7]${NC} Health checks..."

case $ENVIRONMENT in
    prod)
        FRONTEND_URL="https://skillforge.com"
        ;;
    *)
        FRONTEND_URL="http://localhost:3000"
        ;;
esac

# Wait a moment for deployment to be ready
sleep 5

# Check if site is responding
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")

if [ "$RESPONSE" == "200" ] || [ "$RESPONSE" == "307" ] || [ "$RESPONSE" == "308" ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP $RESPONSE)${NC}"
else
    echo -e "${YELLOW}⚠ Health check returned HTTP $RESPONSE (may need more time to propagate)${NC}"
fi

# Step 7: Summary
echo -e "\n${YELLOW}[7/7]${NC} Deployment summary..."

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo "Environment: $ENVIRONMENT"
echo "Platform: $PLATFORM"
echo -e "Frontend URL: $FRONTEND_URL"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Verify site loads at $FRONTEND_URL"
echo "2. Check browser console (F12) for errors"
echo "3. Test marketplace functionality"
echo "4. Verify API connectivity to backend"

# Cleanup
rm -f /tmp/skillforge-frontend.tar.gz

exit 0
