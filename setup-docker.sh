#!/bin/bash

# SkillForge Local Docker Setup Script
# This script automates the local Docker build and deployment

set -e

echo "======================================"
echo "SkillForge Local Docker Setup"
echo "======================================"
echo ""

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "[1] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

echo ""
echo "[2] Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi
echo "✅ Docker Compose found: $(docker-compose --version)"

echo ""
echo "[3] Verifying environment files..."
if [ ! -f "backend/.env.production" ]; then
    echo "❌ backend/.env.production not found"
    exit 1
fi
echo "✅ backend/.env.production exists"

if [ ! -f ".env" ]; then
    echo "❌ .env not found"
    exit 1
fi
echo "✅ .env file exists"

echo ""
echo "[4] Checking for existing containers..."
RUNNING=$(docker-compose ps -q 2>/dev/null | wc -l)
if [ "$RUNNING" -gt 0 ]; then
    echo "⚠️  Found $RUNNING running containers"
    echo "Stopping existing services..."
    docker-compose down
    sleep 2
fi
echo "✅ Ready to start fresh"

echo ""
echo "[5] Building Docker images..."
echo "This may take 5-10 minutes on first build..."
docker-compose build --no-cache

echo ""
echo "[6] Starting services..."
docker-compose up -d

echo ""
echo "[7] Waiting for services to be healthy..."
sleep 5

echo ""
echo "[8] Verifying all services..."
docker-compose ps

echo ""
echo "======================================"
echo "✅ LOCAL DOCKER DEPLOYMENT COMPLETE!"
echo "======================================"
echo ""
echo "Access your application:"
echo "  🌐 Frontend:  http://localhost:3000"
echo "  🔌 Backend:   http://localhost:8001"
echo "  💾 Database:  http://localhost:8080 (Adminer)"
echo "  📊 pgAdmin:   http://localhost:5050"
echo ""
echo "Demo account:"
echo "  Email:    john.doe@example.com"
echo "  Password: password"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f backend    # View backend logs"
echo "  docker-compose logs -f frontend   # View frontend logs"
echo "  docker-compose ps                 # Check service status"
echo "  docker-compose down              # Stop all services"
echo ""
echo "📖 Full guide: LOCAL_DOCKER_DEPLOYMENT.md"
echo ""
