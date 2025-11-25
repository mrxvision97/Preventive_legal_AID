#!/bin/bash
# Frontend setup script for Jetson Nano (Ubuntu 18.04 + Node.js 16)

set -e

echo "=========================================="
echo "Frontend Setup for Jetson Nano"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get the directory where script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "\n${GREEN}[1/6] Checking Node.js version...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js not found. Installing Node.js 16...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ] || [ "$NODE_VERSION" -ge 18 ]; then
        echo -e "${YELLOW}Node.js version is not 16.x. Installing Node.js 16...${NC}"
        curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
        sudo apt-get install -y nodejs
    else
        echo -e "${GREEN}Node.js $(node --version) detected ✓${NC}"
    fi
fi

echo -e "\n${GREEN}[2/6] Checking npm version...${NC}"
npm --version || echo -e "${YELLOW}npm not found, will be installed with Node.js${NC}"

echo -e "\n${GREEN}[3/6] Cleaning old dependencies...${NC}"
if [ -d "node_modules" ]; then
    rm -rf node_modules
    echo -e "${GREEN}Removed node_modules${NC}"
fi
if [ -f "package-lock.json" ]; then
    rm -f package-lock.json
    echo -e "${GREEN}Removed package-lock.json${NC}"
fi

echo -e "\n${GREEN}[4/6] Installing dependencies (this may take 10-15 minutes)...${NC}"
# Increase memory limit for installation
export NODE_OPTIONS="--max-old-space-size=2048"
npm install

echo -e "\n${GREEN}[5/6] Creating .env file...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Frontend port (optional, defaults to 3000)
PORT=3000

# Disable source maps in production for smaller builds
GENERATE_SOURCEMAP=false
EOF
    echo -e "${GREEN}.env file created${NC}"
else
    echo -e "${YELLOW}.env file already exists, skipping...${NC}"
fi

echo -e "\n${GREEN}[6/6] Verifying installation...${NC}"
if [ -d "node_modules" ] && [ -f "node_modules/.bin/react-scripts" ]; then
    echo -e "${GREEN}✓ Create React App installed successfully${NC}"
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}✗ Installation verification failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Start development server:"
echo "   npm start"
echo ""
echo "2. Or build for production:"
echo "   npm run build"
echo ""
echo "3. Serve production build:"
echo "   npx serve -s build -l 3000"
echo ""
echo -e "${GREEN}Frontend is ready for Jetson Nano!${NC}"

