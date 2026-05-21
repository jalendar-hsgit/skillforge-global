#!/usr/bin/env bash
# Quick Deployment Script - SkillForge Global
# Usage: ./deploy.sh [frontend|backend|both]

set -e

echo "🚀 SkillForge Global Deployment Script"
echo "======================================"

TARGET=${1:-both}

deploy_frontend() {
    echo ""
    echo "📦 Deploying Frontend to Vercel..."
    echo "------------------------------------"
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo "❌ Vercel CLI not found. Installing..."
        npm i -g vercel
    fi
    
    # Build frontend
    echo "Building frontend..."
    npm run build
    
    # Deploy to Vercel
    echo "Deploying to Vercel..."
    vercel --prod
    
    echo "✅ Frontend deployed successfully!"
}

deploy_backend() {
    echo ""
    echo "📦 Backend Deployment Checklist..."
    echo "------------------------------------"
    
    # Run tests
    echo "Running backend tests..."
    cd backend
    python -m unittest discover -s tests -p "test_*.py" -v
    
    if [ $? -ne 0 ]; then
        echo "❌ Tests failed! Aborting deployment."
        exit 1
    fi
    
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "Backend deployment options:"
    echo "1. Render: Push to GitHub (auto-deploy if configured)"
    echo "2. Railway: railway up"
    echo "3. Fly.io: fly deploy"
    echo ""
    echo "After deploying backend:"
    echo "  1. Set environment variables in platform dashboard"
    echo "  2. Run: alembic upgrade head (via platform CLI)"
    echo "  3. Test: curl https://your-backend.com/healthz"
    echo ""
    
    cd ..
}

case $TARGET in
    frontend)
        deploy_frontend
        ;;
    backend)
        deploy_backend
        ;;
    both)
        deploy_backend
        deploy_frontend
        ;;
    *)
        echo "❌ Invalid target: $TARGET"
        echo "Usage: ./deploy.sh [frontend|backend|both]"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "✅ Deployment process complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Verify deployment at production URLs"
echo "  2. Run smoke tests on production"
echo "  3. Monitor logs for 24 hours"
echo "  4. See DEPLOYMENT.md for detailed instructions"
echo ""
