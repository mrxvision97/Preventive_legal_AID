#!/bin/bash
# Quick Setup Script for Jetson Nano 4GB
# Run this script after initial JetPack installation

set -e  # Exit on error

echo "=========================================="
echo "VU Legal AID - Jetson Nano 4GB Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Jetson Nano
if [ ! -f "/proc/device-tree/model" ] || ! grep -qi "jetson" /proc/device-tree/model; then
    echo -e "${YELLOW}Warning: This script is designed for Jetson Nano${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root for system operations
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Error: Don't run as root. Run as regular user.${NC}"
    exit 1
fi

echo "Step 1: Update system packages..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "Step 2: Install essential build tools..."
sudo apt install -y \
    build-essential \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    vim \
    htop \
    libasound2-dev \
    portaudio19-dev \
    python3-pyaudio \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libssl-dev \
    libffi-dev

echo ""
echo "Step 3: Configure swap space (4GB)..."
if [ -f /swapfile ]; then
    echo -e "${YELLOW}Swap file already exists. Skipping...${NC}"
else
    echo "Creating 4GB swap file..."
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo -e "${GREEN}Swap configured successfully!${NC}"
fi

# Verify swap
echo ""
echo "Current swap status:"
free -h

echo ""
echo "Step 4: Install Node.js 18.x..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${YELLOW}Node.js already installed: $NODE_VERSION${NC}"
else
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    echo -e "${GREEN}Node.js installed: $(node --version)${NC}"
fi

echo ""
echo "Step 5: Install Ollama..."
if command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama already installed: $(ollama --version)${NC}"
else
    curl -fsSL https://ollama.ai/install.sh | sh
    echo -e "${GREEN}Ollama installed successfully!${NC}"
fi

echo ""
echo "Step 6: Set up Ollama service..."
if systemctl is-active --quiet ollama; then
    echo -e "${YELLOW}Ollama service already running${NC}"
else
    # Create systemd service
    sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ollama
    sudo systemctl start ollama
    echo -e "${GREEN}Ollama service configured and started!${NC}"
fi

# Wait for Ollama to be ready
echo ""
echo "Waiting for Ollama to be ready..."
sleep 5
for i in {1..10}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}Ollama is ready!${NC}"
        break
    fi
    echo "Waiting... ($i/10)"
    sleep 2
done

echo ""
echo "Step 7: Download qwen:0.5b model (optimized for 4GB RAM)..."
if ollama list | grep -q "qwen:0.5b"; then
    echo -e "${YELLOW}Model qwen:0.5b already downloaded${NC}"
else
    echo "Downloading qwen:0.5b (~300MB, this may take a few minutes)..."
    ollama pull qwen:0.5b
    echo -e "${GREEN}Model downloaded successfully!${NC}"
fi

echo ""
echo "Step 8: Create Python virtual environment..."
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_DIR"

if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created!${NC}"
fi

echo ""
echo "Step 9: Install Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel

echo "Installing backend dependencies (this may take 10-15 minutes)..."
cd backend
pip install -r requirements.txt

echo ""
echo "Step 10: Create .env file..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}.env file already exists${NC}"
    echo "Please verify it has the correct settings for Jetson Nano:"
    echo "  OLLAMA_MODEL=qwen:0.5b"
    echo "  USE_OFFLINE_MODE=true"
    echo "  FORCE_EDGE_MODE=true"
else
    echo "Creating .env file with Jetson Nano settings..."
    cat > .env <<EOF
# Application
APP_NAME=VU Legal AID
APP_ENV=production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Ollama (Offline Mode) - CRITICAL for Jetson Nano
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen:0.5b
USE_OFFLINE_MODE=true
FORCE_EDGE_MODE=true

# OpenAI (Optional - leave empty for offline only)
OPENAI_API_KEY=

# Redis (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=

# Pinecone (Optional)
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=legal-aid-index

# LangCache (Optional)
LANGCACHE_API_KEY=

# JWT
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
EOF
    echo -e "${GREEN}.env file created!${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start backend server:"
echo "   cd backend"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "3. Find your IP address:"
echo "   hostname -I"
echo ""
echo "4. Access the application:"
echo "   http://<your-ip>:8000/docs"
echo ""
echo "5. (Optional) Set max performance mode:"
echo "   sudo nvpmodel -m 0"
echo "   sudo jetson_clocks"
echo ""
echo -e "${GREEN}Ready to run!${NC}"

