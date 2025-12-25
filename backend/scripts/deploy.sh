#!/bin/bash
# Deployment script for Navio Academic Advisor API to Fly.io

set -e  # Exit on error

echo "🚀 Deploying Navio API to Fly.io..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo -e "${RED}Error: Fly CLI is not installed${NC}"
    echo "Install it from: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Check if logged in to Fly.io
if ! fly auth whoami &> /dev/null; then
    echo -e "${BLUE}Not logged in to Fly.io. Please login:${NC}"
    fly auth login
fi

# Change to backend directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}Running pre-deployment checks...${NC}"

# Run tests
echo "Running tests..."
if ! pytest; then
    echo -e "${RED}Tests failed. Aborting deployment.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Tests passed${NC}"

# Check if app exists
APP_NAME="navio-api"
if fly apps list | grep -q "$APP_NAME"; then
    echo -e "${BLUE}App $APP_NAME exists. Deploying update...${NC}"
    fly deploy
else
    echo -e "${BLUE}App $APP_NAME does not exist. Creating new app...${NC}"
    echo ""
    echo "After creation, you'll need to set secrets:"
    echo "  fly secrets set DATABASE_URL='postgresql://...'"
    echo "  fly secrets set OPENAI_API_KEY='sk-...'"
    echo "  fly secrets set ANTHROPIC_API_KEY='sk-ant-...'"
    echo "  fly secrets set FRONTEND_URL='https://your-app.vercel.app'"
    echo "  fly secrets set AUTH_SECRET_KEY='your-secure-random-key'"
    echo ""
    fly launch --copy-config --yes
fi

echo -e "${GREEN}✓ Deployment complete!${NC}"

# Show app status
echo -e "${BLUE}App status:${NC}"
fly status

# Show recent logs
echo -e "${BLUE}Recent logs:${NC}"
fly logs --lines=50

echo ""
echo -e "${GREEN}Deployment successful! 🎉${NC}"
echo "App URL: https://$APP_NAME.fly.dev"
echo "Health check: https://$APP_NAME.fly.dev/health"
echo "Metrics: https://$APP_NAME.fly.dev/metrics"
echo "API Docs: https://$APP_NAME.fly.dev/docs"
