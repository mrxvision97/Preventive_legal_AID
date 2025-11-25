#!/bin/bash
# Setup script for Jetson Nano 4GB
# Creates virtual environment and installs all required packages (latest versions)

set -e  # Exit on error

echo "=========================================="
echo "Jetson Nano 4GB Setup Script"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get the directory where script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "\n${GREEN}[1/6] Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    libffi-dev \
    git \
    curl \
    wget

echo -e "\n${GREEN}[2/6] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Removing old one...${NC}"
    rm -rf venv
fi

python3 -m venv venv
echo -e "${GREEN}Virtual environment created successfully${NC}"

echo -e "\n${GREEN}[3/6] Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "\n${GREEN}[4/6] Upgrading pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel

echo -e "\n${GREEN}[5/6] Installing Python packages (latest versions)...${NC}"
echo "This may take several minutes on Jetson Nano..."

# Core FastAPI and Server
pip install --no-cache-dir fastapi uvicorn[standard] python-multipart
pip install --no-cache-dir pydantic pydantic-settings

# AI Services
pip install --no-cache-dir openai

# HTTP Client
pip install --no-cache-dir httpx

# Redis (lightweight)
pip install --no-cache-dir redis

# Image Processing
pip install --no-cache-dir Pillow

# Optional: Tesseract OCR (if system Tesseract is installed)
if command -v tesseract &> /dev/null; then
    echo -e "${YELLOW}Installing Tesseract Python wrapper...${NC}"
    pip install --no-cache-dir pytesseract || echo -e "${YELLOW}Tesseract wrapper installation skipped${NC}"
else
    echo -e "${YELLOW}Tesseract not found. Install with: sudo apt-get install tesseract-ocr${NC}"
fi

# Utilities
pip install --no-cache-dir python-dotenv structlog python-dateutil pytz

# Rate Limiting
pip install --no-cache-dir slowapi

# CORS
pip install --no-cache-dir fastapi-cors

echo -e "\n${GREEN}[6/6] Verifying installation...${NC}"

# Test imports
python3 -c "import fastapi; print('✓ FastAPI')" || echo -e "${RED}✗ FastAPI failed${NC}"
python3 -c "import openai; print('✓ OpenAI')" || echo -e "${RED}✗ OpenAI failed${NC}"
python3 -c "import redis; print('✓ Redis')" || echo -e "${RED}✗ Redis failed${NC}"
python3 -c "from PIL import Image; print('✓ Pillow')" || echo -e "${RED}✗ Pillow failed${NC}"
python3 -c "import httpx; print('✓ httpx')" || echo -e "${RED}✗ httpx failed${NC}"
python3 -c "import structlog; print('✓ structlog')" || echo -e "${RED}✗ structlog failed${NC}"

echo -e "\n${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Create .env file:"
echo "   nano .env"
echo ""
echo "2. Add your API keys to .env:"
echo "   OPENAI_API_KEY=sk-your-key-here"
echo ""
echo "3. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "4. Run the server:"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo -e "${GREEN}Virtual environment is ready in: $(pwd)/venv${NC}"

