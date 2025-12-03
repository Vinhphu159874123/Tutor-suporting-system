#!/bin/bash

# Production Deployment Script for HCMUT Tutor Support System

set -e  # Exit on error

echo "🚀 Starting production deployment..."

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo -e "${RED}❌ Error: .env.prod file not found${NC}"
    echo "Please copy .env.prod.template to .env.prod and configure it"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env.prod | xargs)

echo -e "${GREEN}✓${NC} Environment variables loaded"

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker and Docker Compose are installed"

# Ask for deployment mode
echo ""
echo "Select deployment mode:"
echo "1) Production (real HCMUT services)"
echo "2) Production with Mock services (for testing)"
read -p "Enter choice [1-2]: " mode_choice

COMPOSE_PROFILE=""
if [ "$mode_choice" = "2" ]; then
    COMPOSE_PROFILE="--profile mock"
    echo -e "${YELLOW}ℹ${NC} Using mock HCMUT services"
fi

# Build images
echo ""
echo "📦 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo -e "${GREEN}✓${NC} Images built successfully"

# Check if services are already running
if [ "$(docker-compose -f docker-compose.prod.yml ps -q)" ]; then
    echo ""
    echo -e "${YELLOW}⚠${NC} Services are already running"
    read -p "Do you want to restart them? [y/N]: " restart_choice
    if [[ $restart_choice =~ ^[Yy]$ ]]; then
        echo "🔄 Stopping existing services..."
        docker-compose -f docker-compose.prod.yml down
    else
        echo "Deployment cancelled"
        exit 0
    fi
fi

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml $COMPOSE_PROFILE up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check backend health
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✓${NC} Backend is healthy"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Waiting for backend... ($retry_count/$max_retries)"
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check logs with: docker-compose -f docker-compose.prod.yml logs backend"
    exit 1
fi

# Check frontend health
if curl -f http://localhost:80/health &> /dev/null; then
    echo -e "${GREEN}✓${NC} Frontend is healthy"
else
    echo -e "${YELLOW}⚠${NC} Frontend health check failed (might still be starting)"
fi

# Check Redis health
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓${NC} Redis is healthy"
else
    echo -e "${YELLOW}⚠${NC} Redis health check failed"
fi

# Display service URLs
echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""
echo "📍 Service URLs:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Default Admin Credentials:"
echo "   Email: admin@hcmut.edu.vn"
echo "   Password: admin123"
echo "   ${YELLOW}⚠ Please change this password immediately!${NC}"
echo ""
echo "📊 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "📚 For more information, see DEPLOYMENT.md"
