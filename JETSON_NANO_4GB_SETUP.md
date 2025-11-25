# Jetson Nano 4GB - Complete Setup Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Initial System Setup](#initial-system-setup)
3. [Install Dependencies](#install-dependencies)
4. [Install Ollama & Models](#install-ollama--models)
5. [Project Setup](#project-setup)
6. [Environment Configuration](#environment-configuration)
7. [Run the Application](#run-the-application)
8. [Performance Optimizations](#performance-optimizations)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

---

## System Requirements

### Hardware
- **Jetson Nano 4GB** (Developer Kit)
- **32GB+ microSD card** (Class 10 or better, recommended: 64GB+)
- **5V 4A power supply** (official or compatible)
- **Ethernet cable** or WiFi adapter (for initial setup)
- **USB keyboard and mouse** (for initial setup)
- **HDMI monitor** or SSH access

### Software
- **JetPack 4.6+** or **JetPack 5.0+** (Ubuntu 18.04/20.04)
- **Python 3.8+** (usually pre-installed)
- **Node.js 18+** (for frontend, optional if serving static files)

---

## Initial System Setup

### 1. Flash JetPack Image

If starting fresh, flash the latest JetPack image to your microSD card:

```bash
# Download JetPack from NVIDIA Developer site
# Use balenaEtcher or similar tool to flash to SD card
# Boot Jetson Nano with the flashed SD card
```

### 2. Initial Boot & Configuration

```bash
# Connect via SSH or directly
# Default username: jetson (or your configured username)

# Update system packages
sudo apt update
sudo apt upgrade -y

# Install essential build tools
sudo apt install -y \
    build-essential \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    vim \
    htop
```

### 3. Configure Swap Space (CRITICAL for 4GB RAM)

Jetson Nano 4GB has limited RAM. Adding swap is essential:

```bash
# Check current swap
free -h

# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify swap is active
free -h
# You should see ~4GB swap
```

### 4. Set Jetson Clocks (Optional - for better performance)

```bash
# Set max performance mode
sudo nvpmodel -m 0  # Max performance
sudo jetson_clocks  # Max clocks

# Make it persistent (optional)
sudo systemctl enable nvpmodel
```

### 5. Install Node.js (for frontend development)

```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should be v18.x or higher
npm --version
```

---

## Install Dependencies

### 1. Install System Dependencies

```bash
# Audio libraries (for voice features)
sudo apt install -y \
    libasound2-dev \
    portaudio19-dev \
    python3-pyaudio \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev

# Image processing libraries
sudo apt install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev

# SSL libraries
sudo apt install -y \
    libssl-dev \
    libffi-dev
```

### 2. Create Python Virtual Environment

```bash
# Navigate to your project directory
cd ~/Preventive_legal  # or your project path

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

---

## Install Ollama & Models

### 1. Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service (if not auto-started)
ollama serve &
# Or run in background
nohup ollama serve > /dev/null 2>&1 &

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### 2. Download Optimized Model for 4GB RAM

**IMPORTANT**: For Jetson Nano 4GB, use `qwen:0.5b` - it's the fastest and uses least memory:

```bash
# Download the recommended model (fastest, ~300MB)
ollama pull qwen:0.5b

# Verify model is downloaded
ollama list
# Should show: qwen:0.5b

# Test the model
ollama run qwen:0.5b "Hello, test response"
```

**Why qwen:0.5b?**
- ✅ Smallest model (~300MB)
- ✅ Fastest inference (3-10 seconds)
- ✅ Lowest memory usage (~500MB RAM)
- ✅ Supports multiple languages
- ✅ Optimized for edge devices

### 3. Set Up Ollama Service (Auto-start)

```bash
# Create systemd service for Ollama
sudo nano /etc/systemd/system/ollama.service
```

Add this content:

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=jetson
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Check status
sudo systemctl status ollama
```

---

## Project Setup

### 1. Clone or Transfer Project

```bash
# If using git
git clone https://github.com/mrxvision97/Preventive_legal_AID.git
cd Preventive_legal_AID

# Or transfer files via SCP/SFTP
```

### 2. Install Python Dependencies

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Note: Some packages may take time to compile on ARM
# If you encounter errors, install dependencies one by one
```

**Common Issues & Fixes:**

```bash
# If torch installation fails, install CPU-only version
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# If psutil fails, install system dependencies first
sudo apt install -y python3-dev
pip install psutil

# If build fails due to memory, increase swap or install in smaller batches
```

### 3. Install Frontend Dependencies (Optional)

If you want to build the frontend on Jetson Nano:

```bash
cd ../frontend
npm install

# Build for production
npm run build
```

**Note**: For production, you might want to build the frontend on a more powerful machine and transfer the `dist` folder.

---

## Environment Configuration

### 1. Create Backend `.env` File

```bash
cd backend
cp .env.example .env  # If .env.example exists
# Or create new .env file
nano .env
```

Add this configuration:

```bash
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

# OpenAI (Optional - for online features)
OPENAI_API_KEY=your_key_here  # Leave empty if offline only

# Redis (Optional - for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=

# Pinecone (Optional - for RAG)
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=legal-aid-index

# LangCache (Optional)
LANGCACHE_API_KEY=your_key_here

# Database (Optional - currently commented out)
# DATABASE_URL=postgresql://user:pass@localhost/dbname

# JWT
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://jetson-nano-ip:3000
```

### 2. Verify Configuration

```bash
# Test Ollama connection
python3 -c "
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:11434/api/tags')
        print('Ollama status:', r.status_code)
        print('Models:', r.json())

asyncio.run(test())
"
```

---

## Run the Application

### 1. Start Ollama (if not running as service)

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve &
# Or use systemd service
sudo systemctl start ollama
```

### 2. Start Backend Server

```bash
cd backend
source ../venv/bin/activate  # Activate venv

# Run development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or run in background
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

### 3. Access the Application

```bash
# Find Jetson Nano IP address
hostname -I

# Access from browser:
# http://jetson-nano-ip:8000
# Or locally: http://localhost:8000

# API docs:
# http://jetson-nano-ip:8000/docs
```

### 4. Serve Frontend (Option 1: Static Files)

If you built the frontend on another machine:

```bash
# Copy dist folder to Jetson Nano
# Then serve with nginx or Python

# Using Python (simple)
cd frontend/dist
python3 -m http.server 3000

# Or configure nginx (recommended for production)
```

### 5. Serve Frontend (Option 2: Development Server)

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 3000
```

---

## Performance Optimizations

### 1. Memory Management

The system automatically optimizes for 4GB RAM, but you can fine-tune:

```bash
# Monitor memory usage
watch -n 1 free -h

# Monitor GPU usage
sudo tegrastats
```

### 2. Model Settings (Already Optimized)

The application automatically:
- Uses `qwen:0.5b` model (fastest)
- Limits tokens to 800 (edge) / 1200 (laptop)
- Uses minimal context window (1024 tokens)
- Skips RAG context in offline mode
- Uses `tiny` Whisper model for voice

### 3. System Optimizations

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable snapd  # If installed

# Limit background processes
# Edit /etc/systemd/system.conf
# Set: DefaultTasksMax=50
```

### 4. Application Optimizations

The code already includes:
- ✅ Minimal prompts (ultra-short)
- ✅ Reduced token limits
- ✅ Smaller context windows
- ✅ Optimized Ollama settings (top_k, top_p)
- ✅ Fast connection timeouts
- ✅ RAG context skipped in offline mode

---

## Troubleshooting

### Issue: Out of Memory (OOM)

**Symptoms**: Application crashes, "Killed" messages

**Solutions**:
```bash
# 1. Increase swap (if not done)
sudo fallocate -l 6G /swapfile  # 6GB instead of 4GB
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. Use only qwen:0.5b model
export OLLAMA_MODEL=qwen:0.5b

# 3. Close unnecessary applications
# Check memory usage
free -h
htop
```

### Issue: Slow Inference (>30 seconds)

**Solutions**:
```bash
# 1. Verify correct model is used
ollama list
# Should show: qwen:0.5b

# 2. Check Ollama is using correct model
curl http://localhost:11434/api/tags

# 3. Restart Ollama
sudo systemctl restart ollama

# 4. Check system load
top
# If CPU is 100%, wait for other processes to finish
```

### Issue: Ollama Not Starting

**Solutions**:
```bash
# 1. Check if port 11434 is in use
sudo netstat -tulpn | grep 11434

# 2. Kill existing Ollama process
pkill ollama

# 3. Start Ollama manually
ollama serve

# 4. Check logs
journalctl -u ollama -n 50
```

### Issue: Module Not Found Errors

**Solutions**:
```bash
# 1. Ensure virtual environment is activated
source venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 3. Check Python path
which python
# Should point to venv/bin/python
```

### Issue: Frontend Not Loading

**Solutions**:
```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check CORS settings in .env
ALLOWED_ORIGINS=http://jetson-nano-ip:3000

# 3. Check firewall
sudo ufw allow 8000
sudo ufw allow 3000
```

### Issue: Voice Features Not Working

**Solutions**:
```bash
# 1. Install audio dependencies
sudo apt install -y portaudio19-dev python3-pyaudio

# 2. Install espeak for TTS
sudo apt install -y espeak espeak-data

# 3. Test audio
python3 -c "import pyaudio; print('Audio OK')"
```

---

## Production Deployment

### 1. Create Systemd Service for Backend

```bash
sudo nano /etc/systemd/system/vu-legal-aid.service
```

Add:

```ini
[Unit]
Description=VU Legal AID Backend
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=jetson
WorkingDirectory=/home/jetson/Preventive_legal/backend
Environment="PATH=/home/jetson/Preventive_legal/venv/bin"
ExecStart=/home/jetson/Preventive_legal/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vu-legal-aid
sudo systemctl start vu-legal-aid

# Check status
sudo systemctl status vu-legal-aid
```

### 2. Configure Nginx (Optional - for frontend)

```bash
sudo apt install -y nginx

sudo nano /etc/nginx/sites-available/vu-legal-aid
```

Add:

```nginx
server {
    listen 80;
    server_name jetson-nano-ip;

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

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/vu-legal-aid /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Monitor Resources

```bash
# Create monitoring script
nano ~/monitor.sh
```

Add:

```bash
#!/bin/bash
while true; do
    clear
    echo "=== System Resources ==="
    free -h
    echo ""
    echo "=== GPU Usage ==="
    sudo tegrastats --interval 1000 --logfile /tmp/tegrastats.log &
    sleep 2
    tail -n 1 /tmp/tegrastats.log
    pkill tegrastats
    echo ""
    echo "=== Ollama Status ==="
    curl -s http://localhost:11434/api/tags | jq '.models[].name' 2>/dev/null || echo "Ollama not responding"
    sleep 5
done
```

Make executable:

```bash
chmod +x ~/monitor.sh
```

### 4. Auto-start on Boot

Services are already configured to auto-start:
- ✅ Ollama (systemd service)
- ✅ Backend (systemd service)
- ✅ Frontend (via nginx or systemd)

---

## Expected Performance

### Jetson Nano 4GB with qwen:0.5b:

- **Query Processing**: 5-15 seconds
- **Voice Transcription**: 5-15 seconds (tiny model)
- **TTS Generation**: 1-3 seconds
- **Memory Usage**: ~2-3GB (with swap)
- **CPU Usage**: 50-80% during inference

### Optimization Tips:

1. **Use qwen:0.5b** (already configured) ✅
2. **4GB+ swap** (already configured) ✅
3. **Max performance mode** (jetson_clocks) ✅
4. **Close unnecessary apps** during use
5. **Monitor resources** with `tegrastats`

---

## Quick Start Checklist

- [ ] JetPack installed and updated
- [ ] Swap space configured (4GB+)
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] Ollama installed and running
- [ ] `qwen:0.5b` model downloaded
- [ ] `.env` file configured
- [ ] Backend server running
- [ ] Frontend built and served
- [ ] Application accessible via browser
- [ ] Test query works (5-15 seconds response)

---

## Support & Resources

- **Jetson Nano Documentation**: https://developer.nvidia.com/embedded/jetson-nano
- **Ollama Documentation**: https://ollama.ai/docs
- **Project Repository**: https://github.com/mrxvision97/Preventive_legal_AID

---

## Notes

- The application is optimized for **offline use** on Jetson Nano
- **qwen:0.5b** is the recommended model for 4GB RAM
- Swap space is **critical** - don't skip it
- Monitor memory usage regularly
- For best performance, use Ethernet instead of WiFi

---

**Ready to deploy!** 🚀

If you encounter any issues, check the Troubleshooting section or review the logs:
- Backend: `journalctl -u vu-legal-aid -n 50`
- Ollama: `journalctl -u ollama -n 50`

