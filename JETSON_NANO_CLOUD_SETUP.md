# Jetson Nano Cloud Setup Guide

## 🌐 Cloud-Connected Setup (No Offline Mode)

This guide sets up VU Legal AID on Jetson Nano to use **OpenAI cloud services** instead of offline Ollama. This setup requires internet connection and uses OpenAI API for all AI processing.

---

## 📋 Prerequisites

- **Jetson Nano** with JetPack 4.6+ or 5.0+
- **Internet connection** (required)
- **OpenAI API Key** (required)
- **32GB+ microSD card**
- **5V 4A power supply**

---

## 🚀 Quick Setup

### Automated Setup Script

```bash
# 1. Clone or transfer project to Jetson Nano
cd ~/Preventive_legal

# 2. Run the automated setup script
cd backend/scripts
bash setup_jetson_nano_cloud.sh
```

The script will:
- ✅ Install all system dependencies
- ✅ Set up Python virtual environment
- ✅ Install Python packages (without Ollama dependencies)
- ✅ Configure `.env` for cloud mode
- ✅ Set up frontend
- ✅ Create systemd service
- ✅ Create startup script

---

## 📝 Manual Setup

### Step 1: System Preparation

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    build-essential \
    python3-pip \
    python3-venv \
    git \
    curl \
    nodejs \
    npm \
    nginx
```

### Step 2: Configure Swap (Recommended)

```bash
# Create 4GB swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Step 3: Set Up Backend

```bash
cd ~/Preventive_legal/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (without Ollama)
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-multipart
pip install openai langchain langchain-openai langchain-community
pip install redis pinecone-client python-dotenv
pip install python-jose[cryptography] passlib[bcrypt]
pip install PyPDF2 pdfplumber
# ... (see requirements.txt, skip torch/ollama)
```

### Step 4: Configure Environment

Create `backend/.env`:

```bash
# Application
APP_NAME=VU Legal AID
APP_ENV=production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# OpenAI (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here

# Disable offline mode
USE_OFFLINE_MODE=false
FORCE_EDGE_MODE=false

# Pinecone (Optional - for RAG)
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=legal-aid-index

# Redis (Optional - for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://jetson-ip:3000
```

### Step 5: Set Up Frontend

```bash
cd ~/Preventive_legal/frontend

# Install dependencies
npm install

# Create .env
cat > .env <<EOF
VITE_API_URL=http://jetson-ip:8000
VITE_FALLBACK_API_URL=http://localhost:8000
VITE_ENABLE_OFFLINE_MODE=false
EOF
```

---

## 🎯 Running the Application

### Option 1: Using Startup Script

```bash
# Start everything
./start-cloud.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd ~/Preventive_legal/backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd ~/Preventive_legal/frontend
npm run dev -- --host 0.0.0.0 --port 3000
```

### Option 3: Systemd Service

```bash
# Start service
sudo systemctl start vu-legal-aid-cloud

# Enable auto-start on boot
sudo systemctl enable vu-legal-aid-cloud

# Check status
sudo systemctl status vu-legal-aid-cloud

# View logs
journalctl -u vu-legal-aid-cloud -f
```

---

## 🌐 Access the Application

- **Frontend**: `http://jetson-ip:3000`
- **Backend API**: `http://jetson-ip:8000`
- **API Documentation**: `http://jetson-ip:8000/docs`

Find your IP:
```bash
hostname -I
```

---

## ⚙️ Configuration Differences

### Cloud Mode vs Offline Mode

| Feature | Cloud Mode | Offline Mode |
|---------|-----------|--------------|
| **AI Model** | OpenAI GPT | Ollama (local) |
| **Internet** | ✅ Required | ❌ Not required |
| **Setup** | Simpler | More complex |
| **Cost** | API usage | Free |
| **Speed** | Fast (cloud) | Slower (local) |
| **Quality** | Best | Good |
| **Ollama** | ❌ Not needed | ✅ Required |

### Environment Variables

**Cloud Mode:**
```bash
USE_OFFLINE_MODE=false
FORCE_EDGE_MODE=false
OPENAI_API_KEY=your-key  # Required
```

**Offline Mode:**
```bash
USE_OFFLINE_MODE=true
FORCE_EDGE_MODE=true
OLLAMA_MODEL=qwen:0.5b
# OPENAI_API_KEY not required
```

---

## 🔧 Troubleshooting

### Issue: OpenAI API Errors

**Symptoms**: `401 Unauthorized` or `Invalid API Key`

**Solutions:**
```bash
# 1. Verify API key in .env
cd backend
cat .env | grep OPENAI_API_KEY

# 2. Test API key
python3 << EOF
import os
from dotenv import load_dotenv
load_dotenv()
import httpx

api_key = os.getenv('OPENAI_API_KEY')
response = httpx.get(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=5.0
)
print(f"Status: {response.status_code}")
EOF

# 3. Check internet connection
ping -c 3 api.openai.com
```

### Issue: Slow Response Times

**Solutions:**
```bash
# 1. Check internet speed
speedtest-cli

# 2. Check system resources
htop
free -h

# 3. Verify OpenAI API status
curl https://status.openai.com
```

### Issue: Frontend Can't Connect to Backend

**Solutions:**
```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check CORS settings in backend/.env
cat backend/.env | grep ALLOWED_ORIGINS

# 3. Check firewall
sudo ufw allow 8000
sudo ufw allow 3000
```

### Issue: Out of Memory

**Solutions:**
```bash
# 1. Increase swap
sudo fallocate -l 6G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. Close unnecessary processes
htop  # Press F9 to kill processes
```

---

## 📊 Performance Expectations

### Cloud Mode (OpenAI):
- **Query Processing**: 2-5 seconds
- **Voice Transcription**: 3-8 seconds (if using OpenAI Whisper)
- **Memory Usage**: ~1-2GB
- **Internet Required**: ✅ Yes

### Comparison:
- **Faster** than offline mode (no local model inference)
- **Better quality** responses (GPT-4/GPT-3.5)
- **Requires internet** connection
- **API costs** apply

---

## 🔄 Switching Between Modes

### From Cloud to Offline:

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Download model
ollama pull qwen:0.5b

# 3. Update .env
cd backend
nano .env
# Change:
# USE_OFFLINE_MODE=true
# FORCE_EDGE_MODE=true
# Remove or comment OPENAI_API_KEY

# 4. Restart backend
sudo systemctl restart vu-legal-aid-cloud
```

### From Offline to Cloud:

```bash
# 1. Update .env
cd backend
nano .env
# Change:
# USE_OFFLINE_MODE=false
# FORCE_EDGE_MODE=false
# Add OPENAI_API_KEY=your-key

# 2. Restart backend
sudo systemctl restart vu-legal-aid-cloud
```

---

## 🎯 Production Deployment

### Using Nginx (Recommended)

```bash
# Configure Nginx
sudo nano /etc/nginx/sites-available/vu-legal-aid
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /home/jetson/Preventive_legal/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/vu-legal-aid /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📝 Summary

**Cloud Mode Setup:**
- ✅ No Ollama installation needed
- ✅ No local model downloads
- ✅ Simpler setup
- ✅ Better AI quality
- ⚠️ Requires internet
- ⚠️ API costs apply

**Quick Start:**
```bash
bash backend/scripts/setup_jetson_nano_cloud.sh
./start-cloud.sh
```

**Access:**
- Frontend: `http://jetson-ip:3000`
- API Docs: `http://jetson-ip:8000/docs`

---

## 🔗 Related Documentation

- **Offline Setup**: See `JETSON_NANO_4GB_SETUP.md`
- **Cloud Deployment**: See `CLOUD_DEPLOYMENT_GUIDE.md`
- **Quick Reference**: See `JETSON_NANO_QUICK_REFERENCE.md`

