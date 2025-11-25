#!/bin/bash
# Cloud-Connected Setup Script for Jetson Nano
# This script sets up VU Legal AID to use OpenAI (cloud) instead of offline Ollama
# No offline mode - requires internet connection

set -e  # Exit on error

echo "=========================================="
echo "VU Legal AID - Jetson Nano Cloud Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Error: Don't run as root. Run as regular user.${NC}"
    exit 1
fi

# Check internet connection
echo "Checking internet connection..."
if ! ping -c 1 8.8.8.8 &> /dev/null; then
    echo -e "${RED}Error: No internet connection. This setup requires internet.${NC}"
    exit 1
fi
echo -e "${GREEN}Internet connection OK${NC}"

echo ""
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
    libffi-dev \
    nginx

echo ""
echo "Step 3: Configure swap space (4GB) for better performance..."
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
echo "Step 5: Set up Python virtual environment..."
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_DIR"

if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
    read -p "Recreate virtual environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}Virtual environment recreated!${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created!${NC}"
fi

echo ""
echo "Step 6: Install Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel

echo "Installing backend dependencies (this may take 10-15 minutes)..."
cd backend

# Install dependencies without torch (not needed for cloud mode)
echo "Installing core dependencies..."
pip install fastapi uvicorn[standard] python-multipart pydantic pydantic-settings

echo "Installing AI and ML dependencies..."
pip install openai langchain langchain-openai langchain-community langchain-text-splitters tiktoken

echo "Installing database and cache dependencies..."
pip install redis hiredis langcache httpx

echo "Installing authentication dependencies..."
pip install python-jose[cryptography] passlib[bcrypt]

echo "Installing file processing dependencies..."
pip install PyPDF2 pdfplumber Pillow python-docx

echo "Installing AWS dependencies..."
pip install boto3 botocore

echo "Installing vector database clients..."
pip install pinecone-client weaviate-client

echo "Installing utilities..."
pip install python-dotenv python-dateutil pytz structlog slowapi fastapi-cors

echo "Installing testing dependencies..."
pip install pytest pytest-asyncio pytest-cov

echo "Installing SQLAlchemy (for future database support)..."
pip install sqlalchemy[asyncio] asyncpg alembic psycopg2-binary pgvector

echo ""
echo -e "${GREEN}All dependencies installed!${NC}"

echo ""
echo "Step 7: Configure .env file..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}.env file already exists${NC}"
    read -p "Overwrite with cloud configuration? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
    else
        CREATE_ENV=true
    fi
else
    CREATE_ENV=true
fi

if [ "$CREATE_ENV" = true ]; then
    echo ""
    echo -e "${BLUE}=== Configuration Setup ===${NC}"
    echo ""
    
    # Get OpenAI API Key
    read -p "Enter your OpenAI API Key: " OPENAI_KEY
    if [ -z "$OPENAI_KEY" ]; then
        echo -e "${YELLOW}Warning: OpenAI API Key not provided. You can add it later in .env${NC}"
    fi
    
    # Get Pinecone API Key (optional)
    read -p "Enter your Pinecone API Key (optional, press Enter to skip): " PINECONE_KEY
    
    # Get Pinecone Environment (optional)
    if [ -n "$PINECONE_KEY" ]; then
        read -p "Enter Pinecone Environment (e.g., us-east-1): " PINECONE_ENV
        PINECONE_ENV=${PINECONE_ENV:-us-east-1}
        
        read -p "Enter Pinecone Index Name (e.g., legal-aid-index): " PINECONE_INDEX
        PINECONE_INDEX=${PINECONE_INDEX:-legal-aid-index}
    fi
    
    # Get Redis configuration (optional)
    read -p "Enter Redis Host (optional, default: localhost): " REDIS_HOST
    REDIS_HOST=${REDIS_HOST:-localhost}
    
    read -p "Enter Redis Port (optional, default: 6379): " REDIS_PORT
    REDIS_PORT=${REDIS_PORT:-6379}
    
    read -p "Enter Redis Password (optional, press Enter to skip): " REDIS_PASSWORD
    
    # Get LangCache API Key (optional)
    read -p "Enter LangCache API Key (optional, press Enter to skip): " LANGCACHE_KEY
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Get Jetson Nano IP
    JETSON_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "Creating .env file with cloud configuration..."
    cat > .env <<EOF
# Application
APP_NAME=VU Legal AID
APP_ENV=production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# OpenAI (REQUIRED for cloud mode)
OPENAI_API_KEY=${OPENAI_KEY}

# Ollama (NOT USED in cloud mode - disabled)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
USE_OFFLINE_MODE=false
FORCE_EDGE_MODE=false

# Pinecone (Optional - for RAG)
PINECONE_API_KEY=${PINECONE_KEY}
PINECONE_ENVIRONMENT=${PINECONE_ENV}
PINECONE_INDEX_NAME=${PINECONE_INDEX}

# Redis (Optional - for caching)
REDIS_HOST=${REDIS_HOST}
REDIS_PORT=${REDIS_PORT}
REDIS_USERNAME=default
REDIS_PASSWORD=${REDIS_PASSWORD}

# LangCache (Optional)
LANGCACHE_API_KEY=${LANGCACHE_KEY}

# Database (Optional - currently disabled)
# DATABASE_URL=postgresql://user:pass@localhost/dbname

# JWT
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://${JETSON_IP}:3000,http://${JETSON_IP}:5173
EOF
    
    echo -e "${GREEN}.env file created!${NC}"
    echo ""
    echo -e "${YELLOW}Note: You can edit .env later to add/update API keys${NC}"
fi

echo ""
echo "Step 8: Test OpenAI connection..."
if [ -n "$OPENAI_KEY" ]; then
    echo "Testing OpenAI API connection..."
    source venv/bin/activate
    python3 << EOF
import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    import httpx
    try:
        response = httpx.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0
        )
        if response.status_code == 200:
            print("✅ OpenAI API connection successful!")
        else:
            print(f"⚠️ OpenAI API returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not connect to OpenAI: {e}")
else:
    print("⚠️ OpenAI API key not set in .env")
EOF
else
    echo -e "${YELLOW}Skipping OpenAI test (API key not provided)${NC}"
fi

echo ""
echo "Step 9: Set up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    echo -e "${GREEN}Frontend dependencies installed!${NC}"
else
    echo -e "${YELLOW}Frontend dependencies already installed${NC}"
fi

# Create frontend .env
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env <<EOF
# Backend API URL (pointing to local backend on Jetson Nano)
VITE_API_URL=http://${JETSON_IP}:8000
VITE_FALLBACK_API_URL=http://localhost:8000
VITE_ENABLE_OFFLINE_MODE=false
EOF
    echo -e "${GREEN}Frontend .env created!${NC}"
else
    echo -e "${YELLOW}Frontend .env already exists${NC}"
fi

echo ""
echo "Step 10: Create systemd service for backend..."
cd ../backend

# Create systemd service
sudo tee /etc/systemd/system/vu-legal-aid-cloud.service > /dev/null <<EOF
[Unit]
Description=VU Legal AID Backend (Cloud Mode)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo -e "${GREEN}Systemd service created!${NC}"
echo -e "${YELLOW}Note: Service is not started automatically. Start it with:${NC}"
echo "  sudo systemctl start vu-legal-aid-cloud"
echo "  sudo systemctl enable vu-legal-aid-cloud"

echo ""
echo "Step 11: Create startup script..."
cd "$PROJECT_DIR"

cat > start-cloud.sh <<'EOF'
#!/bin/bash
# Start VU Legal AID in cloud mode

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "Starting VU Legal AID (Cloud Mode)..."

# Activate virtual environment
source venv/bin/activate

# Start backend
cd backend
echo "Starting backend server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running!"
else
    echo "⚠️ Backend may not be ready yet"
fi

# Start frontend
cd ../frontend
echo "Starting frontend server..."
npm run dev -- --host 0.0.0.0 --port 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "VU Legal AID is running!"
echo "=========================================="
echo ""
echo "Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "Logs:"
echo "  Backend: tail -f $PROJECT_DIR/backend.log"
echo "  Frontend: tail -f $PROJECT_DIR/frontend.log"
echo ""
echo "To stop:"
echo "  pkill -f uvicorn"
echo "  pkill -f 'npm run dev'"
echo ""
EOF

chmod +x start-cloud.sh
echo -e "${GREEN}Startup script created: start-cloud.sh${NC}"

echo ""
echo "Step 12: Set max performance mode (optional)..."
read -p "Set Jetson Nano to max performance mode? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo nvpmodel -m 0
    sudo jetson_clocks
    echo -e "${GREEN}Max performance mode enabled!${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo "  ✅ Cloud mode enabled (OpenAI)"
echo "  ✅ Offline mode disabled"
echo "  ✅ Ollama not required"
echo "  ✅ Internet connection required"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Verify .env configuration:"
echo "   cd backend"
echo "   nano .env"
echo "   # Make sure OPENAI_API_KEY is set"
echo ""
echo "2. Start the application:"
echo "   ./start-cloud.sh"
echo ""
echo "   Or manually:"
echo "   # Terminal 1 - Backend"
echo "   cd backend"
echo "   source ../venv/bin/activate"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "   # Terminal 2 - Frontend"
echo "   cd frontend"
echo "   npm run dev -- --host 0.0.0.0 --port 3000"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "   Backend API: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "4. (Optional) Use systemd service:"
echo "   sudo systemctl start vu-legal-aid-cloud"
echo "   sudo systemctl enable vu-legal-aid-cloud"
echo ""
echo -e "${YELLOW}Important Notes:${NC}"
echo "  • This setup requires internet connection"
echo "  • OpenAI API key is required"
echo "  • No offline/Ollama functionality"
echo "  • All AI processing uses OpenAI cloud"
echo ""
echo -e "${GREEN}Ready to run!${NC}"

