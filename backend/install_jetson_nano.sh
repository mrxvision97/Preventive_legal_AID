#!/bin/bash
# Quick installation script for Jetson Nano
# Usage: bash install_jetson_nano.sh

set -e  # Exit on error

echo "=========================================="
echo "Jetson Nano Installation Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo -e "${YELLOW}Warning: This script is designed for Jetson Nano. Continue anyway? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Update system
echo -e "\n${GREEN}[1/8] Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Install system dependencies
echo -e "\n${GREEN}[2/8] Installing system dependencies...${NC}"
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    libffi-dev

# Step 3: Install Tesseract (optional)
echo -e "\n${GREEN}[3/8] Installing Tesseract OCR (optional)...${NC}"
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin || echo -e "${YELLOW}Tesseract installation skipped${NC}"

# Step 4: Create virtual environment
echo -e "\n${GREEN}[4/8] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Step 5: Activate virtual environment
echo -e "\n${GREEN}[5/8] Activating virtual environment...${NC}"
source venv/bin/activate

# Step 6: Upgrade pip
echo -e "\n${GREEN}[6/8] Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Step 7: Install Python packages
echo -e "\n${GREEN}[7/8] Installing Python packages (this may take a while)...${NC}"
if [ -f "requirements-jetson-nano.txt" ]; then
    pip install --no-cache-dir -r requirements-jetson-nano.txt
else
    echo -e "${RED}Error: requirements-jetson-nano.txt not found!${NC}"
    exit 1
fi

# Step 8: Verify installation
echo -e "\n${GREEN}[8/8] Verifying installation...${NC}"
python -c "import fastapi; print('✓ FastAPI installed')" || echo -e "${RED}✗ FastAPI installation failed${NC}"
python -c "import openai; print('✓ OpenAI installed')" || echo -e "${RED}✗ OpenAI installation failed${NC}"
python -c "import redis; print('✓ Redis installed')" || echo -e "${RED}✗ Redis installation failed${NC}"
python -c "from PIL import Image; print('✓ Pillow installed')" || echo -e "${RED}✗ Pillow installation failed${NC}"

echo -e "\n${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Create .env file in backend/ directory"
echo "2. Add your OPENAI_API_KEY to .env"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo -e "${GREEN}For detailed instructions, see: JETSON_NANO_INSTALL.md${NC}"

